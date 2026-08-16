# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the value-of-compute gate (offline: literature_gate=None)."""
import pytest

from biodisc_core.fixed_pipeline.value_of_compute import (
    score_question, fund_candidates, extract_named_genes)


def test_confirmatory_question_is_low_surprise():
    s = score_question(
        "Which genes are differentially expressed between breast cancer tumors and normal breast tissue?",
        None, None)
    assert s.surprise < 0.25, s           # textbook tumor-vs-normal -> low surprise
    assert s.importance > 0.1             # touches cancer biology
    assert s.ev >= 0.0


def test_contrarian_question_is_high_surprise():
    s = score_question(
        "Does CYP2E1 decrease in mouse fatty liver, reversing the textbook direction?",
        {"samples": 96}, None)
    assert s.surprise > 0.4, s            # explicit contrarian direction + reversal word
    assert s.cost > 1.0                   # 96 samples -> log cost > 1
    assert s.ev > 0.0


def test_reversal_wording_alone_raises_surprise():
    s = score_question(
        "Is the relationship between diet and the gene the OPPOSITE of what is reported?", None, None)
    assert s.surprise > 0.3, s


def test_hub_gene_scores_higher_importance_than_obscure_gene():
    s_hub = score_question("Does TP53 loss drive progression?", None, None)
    s_obscure = score_question("Does WDR33 change here?", None, None)
    assert s_hub.importance > s_obscure.importance, (s_hub, s_obscure)


def test_pathway_term_raises_importance():
    s = score_question("How does the mTOR pathway respond?", None, None)
    assert s.importance > 0.4, s


def test_novelty_neutral_without_gate():
    # No literature_gate -> neutral 0.5, never blocks
    s = score_question("anything", None, None)
    assert s.novelty == 0.5


def test_fund_candidates_returns_top_k_plus_exploration_and_never_drops_all():
    questions = [
        "Which genes differ between tumor and normal?",          # low surprise
        "Does CYP2E1 decrease in fatty liver (reversal)?",       # high surprise
        "Does TP53 increase in cancer (contrarian)?",            # high surprise
        "How does X alter Y?",                                    # low
        "Which genes differ between A and B?",                    # low
        "Does MMP2 reverse direction across species?",            # high surprise
        "Generic question one about something?",
        "Generic question two about something?",
        "Generic question three about something?",
        "Generic question four about something?",
    ]
    scored = [score_question(q, None, None) for q in questions]
    funded = fund_candidates(scored, top_k=3, exploration_frac=0.5)
    funded_qs = {s.question for s in funded}
    # the three highest-surprise questions must be in the funded top-k
    assert "Does CYP2E1 decrease in fatty liver (reversal)?" in funded_qs
    assert "Does TP53 increase in cancer (contrarian)?" in funded_qs
    assert "Does MMP2 reverse direction across species?" in funded_qs
    # exploration slice funds some of the remainder too (eureka insurance)
    assert len(funded) >= 3
    # nothing funded twice
    assert len(funded) == len(funded_qs)
    # every scored candidate got a reason
    assert all(s.reason for s in scored)


def test_fund_candidates_exploration_is_bounded():
    scored = [score_question(f"Generic question number {i}?", None, None) for i in range(20)]
    funded = fund_candidates(scored, top_k=3, exploration_frac=0.2)
    # top_k=3 + ~20% of 17 remainder (~3) -> ~6; never more than all
    assert 3 <= len(funded) <= len(scored)


# ---- extract_named_genes (used by the Layer 7 binding gate) ----

def test_extract_named_genes_finds_symbols():
    assert extract_named_genes("Whereas MYC typically increases in prostate cancer...") == ["MYC"]
    assert extract_named_genes("Does CYP2E1 decrease in mouse fatty liver?") == ["CYP2E1"]
    both = extract_named_genes("Does TP53 and BRCA1 loss drive progression?")
    assert "TP53" in both and "BRCA1" in both


def test_extract_named_genes_exploratory_has_none():
    assert extract_named_genes("Which genes differ between tumor and normal?") == []


def test_extract_named_genes_excludes_non_gene_acronyms_and_hyphens():
    g = extract_named_genes("DNA-repair genes at FDR threshold (GSE2034, ILMN_1)")
    assert "DNA" not in g and "FDR" not in g
    assert g == []  # nothing real named -> exploratory; accessions excluded too


# ---- Layer 7 question-result binding gate ----

@pytest.fixture(scope="module")
def orchestrator():
    from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import create_fixed_discovery_orchestrator
    return create_fixed_discovery_orchestrator()


def test_binding_rejects_unbound_named_gene(orchestrator):
    # the documented failure: question names MTOR, result has a generic signature
    de = {"top_upregulated": [{"gene_symbol": "ANLN"}, {"gene_symbol": "MAD2L1"}],
          "top_downregulated": []}
    b = orchestrator._check_question_result_binding(
        "Whereas MTOR typically increases in liver, does it paradoxically decrease?", de)
    assert b["named"] == ["MTOR"]
    assert b["bound"] is False


def test_binding_passes_when_named_gene_present(orchestrator):
    de = {"top_upregulated": [{"gene_symbol": "MTOR"}], "top_downregulated": []}
    b = orchestrator._check_question_result_binding(
        "Whereas MTOR typically increases in liver, does it paradoxically decrease?", de)
    assert b["bound"] is True


def test_binding_passes_for_exploratory_question(orchestrator):
    b = orchestrator._check_question_result_binding(
        "Which genes differ between tumor and normal?", {"top_upregulated": []})
    assert b["named"] == []
    assert b["bound"] is True


def test_build_claim_text_leads_with_directional_result(orchestrator):
    # rebuild item 4: Gate-2 must assess the specific RESULT claim, not the question text
    report = {
        "question": "Whereas MTOR typically increases in liver, does it paradoxically decrease?",
        "gene_hypothesis": {"gene": "MTOR", "observed_direction": "down"},
        "differential_expression": {"top_upregulated": [{"gene_symbol": "ANLN"}]},
        "dataset": {"organism": "Homo sapiens", "data_type": "gene_expression"},
    }
    claim = orchestrator._build_claim_text(report)
    assert claim.startswith("MTOR is downregulated")


def test_build_claim_text_no_direction_without_hypothesis(orchestrator):
    report = {"question": "Which genes differ between tumor and normal?",
              "differential_expression": {}}
    claim = orchestrator._build_claim_text(report)
    assert "is downregulated" not in claim and "is upregulated" not in claim


