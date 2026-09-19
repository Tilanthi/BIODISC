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
"""Tests for the limitations taxonomy (V9.1, Paper2Agent lesson #4).

Genuine-vs-candidate is 1 bit over a spectrum. A replicated finding whose only
replication is the internal held-out split, with a thin novelty margin, is NOT
the same epistemic object as an independent-cohort replicated finding with a
wide margin — but both currently print 'genuine'. The taxonomy adds a machine-
readable ``flagging.status`` ∈ {verified, verified_with_limitations} plus
``flagging.limitations`` reasons, WITHOUT changing tier assignment (the
candidate/genuine split and the write path are untouched).

Run: python -m pytest tests/test_discovery_gate_limitations.py -v
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.discovery_gate import (  # noqa: E402
    evaluate_for_flagging, stamp_report,
)


def _report(replication=None, gate2_sim=None, tier_stats=None):
    replication = replication or {"replicated": True,
                                  "method": "independent_cohort",
                                  "replication_fraction": 0.8}
    report = {
        "discovery_id": "T1",
        "question": "Does GENE1 change in this specific contrast?",
        "replication": replication,
        "comprehensive_validation_statistics": {},
    }
    if gate2_sim is not None:
        report["comprehensive_validation_statistics"]["literature_novelty"] = {
            "status": "novel", "max_similarity": gate2_sim}
    if tier_stats:
        report["comprehensive_validation_statistics"].update(tier_stats)
    return report


# ------------------------------------------------------------- limitation rules
def test_internal_replication_gets_limitation():
    decision = evaluate_for_flagging(_report(replication={
        "replicated": True, "method": "internal_held_out_split_nominal_p",
        "replication_fraction": 0.8}))
    assert decision.tier == "genuine"
    assert decision.status == "verified_with_limitations"
    assert "internal_replication_only" in decision.limitations


def test_independent_cohort_clean():
    decision = evaluate_for_flagging(_report(gate2_sim=0.10))
    assert decision.tier == "genuine"
    assert decision.status == "verified"
    assert decision.limitations == []


def test_thin_novelty_margin_flagged():
    """Gate-2 similarity within 0.05 of the 0.55 threshold = thin margin."""
    decision = evaluate_for_flagging(_report(gate2_sim=0.52))
    assert "novelty_margin_thin" in decision.limitations
    assert decision.status == "verified_with_limitations"


def test_wide_margin_not_flagged():
    decision = evaluate_for_flagging(_report(gate2_sim=0.30))
    assert "novelty_margin_thin" not in (decision.limitations or [])


def test_weak_fraction_flagged():
    decision = evaluate_for_flagging(_report(replication={
        "replicated": True, "method": "independent_cohort",
        "replication_fraction": 0.4}))
    assert "weak_replication_fraction" in decision.limitations


def test_multiple_limitations_accumulate():
    decision = evaluate_for_flagging(_report(
        replication={"replicated": True,
                     "method": "internal_held_out_split_nominal_p",
                     "replication_fraction": 0.45},
        gate2_sim=0.53))
    assert set(decision.limitations) >= {"internal_replication_only",
                                         "weak_replication_fraction",
                                         "novelty_margin_thin"}


# ------------------------------------------------------ tier behavior unchanged
def test_candidates_never_get_verified_status():
    """Limitations apply only to the genuine tier; candidates stay candidates."""
    decision = evaluate_for_flagging(_report(replication={"replicated": False}))
    assert decision.tier == "candidate_unconfirmed"
    assert decision.status == "candidate_unconfirmed"
    assert decision.limitations == []


def test_stamp_report_writes_status_and_limitations():
    report = _report(replication={"replicated": True,
                                  "method": "internal_held_out_split_nominal_p",
                                  "replication_fraction": 0.8})
    stamped, decision = stamp_report(report)
    assert stamped["flagging"]["status"] == "verified_with_limitations"
    assert "internal_replication_only" in stamped["flagging"]["limitations"]
    assert stamped["flagging"]["tier"] == "genuine"  # tier assignment unchanged


# --------------------------------------------------- capability index ingestion
def test_capability_index_counts_limitation_statuses(tmp_path, monkeypatch):
    from biodisc_core.fixed_pipeline import capability_index as ci
    store = tmp_path / "autonomous_discoveries.jsonl"
    rows = [
        {"flagging": {"tier": "genuine", "status": "verified"}},
        {"flagging": {"tier": "genuine", "status": "verified_with_limitations",
                      "limitations": ["internal_replication_only", "weak_replication_fraction"]}},
        {"flagging": {"tier": "genuine",
                      "limitations": ["internal_replication_only"]}},  # legacy: no status
    ]
    store.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    counts = ci.count_limitation_statuses(store)
    assert counts["verified"] == 2  # explicit + legacy (missing status = verified)
    assert counts["verified_with_limitations"] == 1
    assert counts["limitation_breakdown"]["internal_replication_only"] == 2
    assert counts["limitation_breakdown"]["weak_replication_fraction"] == 1
