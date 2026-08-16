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
"""Tests for the breakthrough discovery package (the multi-modality rebuild)."""
from biodisc_core.breakthrough.candidate import DiscoveryCandidate, CandidatePool
from biodisc_core.breakthrough.convergence import ConvergenceScorer
from biodisc_core.breakthrough.bridge_engine import detect_bridges
from biodisc_core.breakthrough.contradiction_detector import extract_claims, detect_contradictions
from biodisc_core.breakthrough.anomaly_context import detect_anomaly_candidates
from biodisc_core.breakthrough.runner import run_breakthrough_discovery


# ---- candidate model + convergence (items 5) ----

def test_candidate_merges_by_gene():
    pool = CandidatePool()
    pool.add(DiscoveryCandidate(kind="cross_domain_bridge", claim="X", gene="TP53", methods=["bridge"]))
    pool.add(DiscoveryCandidate(kind="anomaly_in_context", claim="Y", gene="TP53", methods=["anomaly"]))
    assert len(pool) == 1  # merged by gene
    merged = pool.all()[0]
    assert set(merged.methods) == {"bridge", "anomaly"}


def test_convergence_high_potential_at_3_methods():
    pool = CandidatePool()
    pool.add(DiscoveryCandidate(kind="x", claim="test", gene="TP53",
                                methods=["bridge", "contradiction", "anomaly"],
                                importance=0.8, novelty=0.5, surprise=0.5))
    ranked = ConvergenceScorer(min_methods=3).score_pool(pool)
    assert ranked[0].convergence_score == 3
    assert ranked[0].high_potential is True


def test_convergence_below_threshold_not_high():
    pool = CandidatePool()
    pool.add(DiscoveryCandidate(kind="x", claim="test", gene="MYC",
                                methods=["bridge", "anomaly"], importance=0.5))
    ranked = ConvergenceScorer(min_methods=3).score_pool(pool)
    assert ranked[0].high_potential is False


# ---- bridge engine (item 1) ----

def test_bridge_engine_produces_candidates():
    bridges = detect_bridges(literature_gate=None)
    assert len(bridges) > 0
    assert all(b.kind == "cross_domain_bridge" for b in bridges)


def test_bridge_engine_includes_known_crispr():
    bridges = detect_bridges(literature_gate=None)
    # CRISPR (a known bridge: microbiology -> gene editing) should appear
    assert any("CRISPR" in b.evidence.get("mechanism", "").upper() for b in bridges), \
        "Expected CRISPR bridge as validation"


# ---- contradiction detector (item 3) ----

def test_extract_claims_finds_pattern():
    text = "The stomach is sterile and bacteria never survive there."
    claims = extract_claims(text)
    assert len(claims) > 0
    assert any("sterile" in c.lower() or "never" in c.lower() for c in claims)


def test_contradiction_historical_candidates():
    cands = detect_contradictions(include_historical=True)
    assert len(cands) > 0
    assert all(c.kind == "literature_contradiction" for c in cands)


# ---- anomaly-in-context (item 4) ----

def test_anomaly_context_wraps_miner():
    de = {"top_upregulated": [{"gene_symbol": "GENEA", "log2_fold_change": 0.5,
                               "p_value": 1e-5, "fdr_p_value": 1e-5, "regulation": "up"}]}
    prior = {"GENEA": {"GSE_OTHER": "down"}}
    cands = detect_anomaly_candidates(de, prior, dataset_id="GSE_THIS")
    assert len(cands) > 0
    assert cands[0].kind == "anomaly_in_context"
    assert cands[0].gene == "GENEA"


# ---- runner (integration) ----

def test_runner_collects_from_multiple_modalities():
    result = run_breakthrough_discovery(literature_gate=None)
    assert result["pool_size"] > 0
    assert len(result["all_ranked"]) > 0
    # bridge + contradiction should both contribute
    methods_seen = set()
    for c in result["all_ranked"]:
        methods_seen.update(c.methods)
    assert "bridge" in methods_seen
    assert "contradiction" in methods_seen
