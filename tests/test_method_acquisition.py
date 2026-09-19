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
"""Tests for the method-acquisition route + RSI confinement policy (V9.1).

Paper2Agent's hard rule — "Do not invent scientific algorithms to fill
repository gaps" — applied to BIODISC: scientific methods enter the pipeline
only through ACQUISITION WITH VERIFIED REFERENCE AGREEMENT (bound to
peer-reviewed source code), never by invention. The RSI miner stays confined to
plumbing. Admission is quarantined until every requirement carries evidence
(Paper2Agent converted only 74/100 papers even with heavy verification —
acquired methods get their own quarantine, like candidates).

Run: python -m pytest tests/test_method_acquisition.py -v
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.method_acquisition import admission, policy  # noqa: E402


def _method(**evidence):
    ev = {"reference_agreement": False, "store_fpr_check": False, "human_review": False}
    ev.update(evidence)
    return admission.AcquiredMethod(
        method_id="wgcna-coexpression", name="WGCNA co-expression modules",
        source_repo="https://github.com/cran/WGCNA", source_commit="abc123",
        source_paper="pmid:12345678", tools=["build_modules"],
        state="quarantined", evidence=ev)


# ------------------------------------------------------------------- admission
def test_admission_requires_all_evidence():
    m = _method()  # no evidence at all
    d = admission.evaluate_admission(m)
    assert d["state"] == "quarantined"
    assert set(d["unmet"]) == {"reference_agreement", "store_fpr_check", "human_review"}
    assert admission.is_admitted(m.method_id, methods=[m]) is False


def test_partial_evidence_still_quarantined():
    m = _method(reference_agreement=True)
    d = admission.evaluate_admission(m)
    assert d["state"] == "quarantined"
    assert "reference_agreement" not in d["unmet"]
    assert "store_fpr_check" in d["unmet"]


def test_full_evidence_admits():
    m = _method(reference_agreement=True, store_fpr_check=True, human_review=True)
    d = admission.evaluate_admission(m)
    assert d["state"] == "admitted"
    assert d["unmet"] == []
    assert admission.is_admitted(m.method_id, methods=[m]) is True


def test_rejected_only_explicit():
    m = _method(reference_agreement=True, store_fpr_check=True, human_review=True)
    m.state = "rejected"  # a human reject overrides evidence
    d = admission.evaluate_admission(m)
    assert d["state"] == "rejected"
    assert admission.is_admitted(m.method_id, methods=[m]) is False


def test_registry_roundtrip(tmp_path):
    p = tmp_path / "acquired_methods.json"
    m = _method(reference_agreement=True, store_fpr_check=True, human_review=True)
    admission.save_registry([m], p)
    loaded = admission.load_registry(p)
    assert loaded == [m]
    assert admission.is_admitted("wgcna-coexpression", methods=loaded) is True
    assert admission.is_admitted("not-registered", methods=loaded) is False


# ---------------------------------------------------------------------- policy
def test_classify_paths():
    scientific = [
        "biodisc_core/fixed_pipeline/differential_expression/__init__.py",
        "biodisc_core/fixed_pipeline/anomaly_miner.py",
        "biodisc_core/fixed_pipeline/replication_gate.py",
        "biodisc_core/fixed_pipeline/literature_gate.py",
        "biodisc_core/fixed_pipeline/fdr_significance_gate/significance_validator.py",
        "biodisc_core/fixed_pipeline/benchmark/truth_known_fixture.py",
    ]
    plumbing = [
        "biodisc_core/fixed_pipeline/FixedDiscoveryOrchestrator.py",
        "biodisc_core/fixed_pipeline/verdict_log.py",
        "biodisc_core/fixed_pipeline/geo_data_downloader.py",
        "discovery_watchdog.py",
        "tests/test_watchdog_stall.py",
    ]
    for p in scientific:
        assert policy.classify_path(p) == "scientific_algorithm", p
    for p in plumbing:
        assert policy.classify_path(p) == "plumbing", p


def test_theme_routes():
    # scientific themes route to acquisition
    assert policy.classify_proposal("significance_failed")["route"] == "method_acquisition"
    assert policy.classify_proposal("template_question")["route"] == "method_acquisition"
    # plumbing themes stay RSI-direct
    assert policy.classify_proposal("organism_mismatch")["route"] == "rsi_direct"
    assert policy.classify_proposal("probe_gene_failed")["route"] == "rsi_direct"
    assert policy.classify_proposal("abandoned_mid_validation")["route"] == "rsi_direct"
    # unknown themes default CONSERVATIVELY to acquisition
    assert policy.classify_proposal("brand_new_theme")["route"] == "method_acquisition"


def test_rsi_proposals_md_shows_routes(tmp_path):
    from biodisc_core.fixed_pipeline.rsi_miner import mine, write_proposals_md
    verdicts = [
        {"outcome": "rejected", "reason": "significance failed: no genes",
         "logged_at": "2026-09-19T10:00:00+00:00"},
        {"outcome": "rejected", "reason": "organism mismatch: mouse vs human",
         "logged_at": "2026-09-19T11:00:00+00:00"},
    ]
    patterns = mine(verdicts)
    out = tmp_path / "rsi_proposals.md"
    write_proposals_md(patterns, out)
    text = out.read_text()
    assert "method_acquisition" in text
    assert "rsi_direct" in text
    for p in patterns:
        assert p.route in ("method_acquisition", "rsi_direct")
        assert p.change_class in ("plumbing", "scientific_algorithm")
