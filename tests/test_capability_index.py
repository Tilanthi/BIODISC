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
"""Tests for the BIODISC capability index — the Beast design property: it ingests
inputs that can LOWER its headline, and replication (0% today) is the load-bearing
dimension."""
import sys
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.capability_index import compute_capability_index  # noqa: E402


def test_index_is_honestly_low_when_replication_is_zero():
    """0 genuine findings -> replication_rate 0 -> composite low, regardless of
    throughput. This is the whole point: throughput without replication is not capability."""
    idx = compute_capability_index(
        verdict_summary={"total_candidates": 100, "buckets": {}},
        effectiveness=20.0, genuine=0, quarantined=10)
    assert idx["dimensions"]["replication_rate"] == 0.0
    assert idx["capability_index"] < 30


def test_index_rises_when_replication_succeeds():
    idx = compute_capability_index(
        verdict_summary={"total_candidates": 100, "buckets": {}},
        effectiveness=20.0, genuine=5, quarantined=5)
    assert idx["dimensions"]["replication_rate"] == 0.5
    assert idx["capability_index"] > 25


def test_index_ingests_a_lowering_input():
    """The Beast property: a worse effectiveness reading must LOWER the composite,
    not be papered over."""
    high = compute_capability_index(
        {"total_candidates": 100, "buckets": {}}, effectiveness=80.0, genuine=0, quarantined=10)
    low = compute_capability_index(
        {"total_candidates": 100, "buckets": {}}, effectiveness=0.0, genuine=0, quarantined=10)
    assert high["capability_index"] > low["capability_index"]


def test_replication_dominates_throughput():
    """Lots of quarantined candidates but zero replication scores WORSE than few
    candidates with some replication — capability is about findings, not volume."""
    high_volume_no_replication = compute_capability_index(
        {"total_candidates": 1000, "buckets": {}}, effectiveness=50.0, genuine=0, quarantined=500)
    low_volume_some_replication = compute_capability_index(
        {"total_candidates": 10, "buckets": {}}, effectiveness=50.0, genuine=2, quarantined=2)
    assert low_volume_some_replication["capability_index"] > high_volume_no_replication["capability_index"]


# --- v2: funded-attempt denominator (2026-08-16) --------------------------
# The v1 gate_pass denominator was the whole verdict log — 93% of which was
# `low_ev_deprioritized`: questions the EV gate considered and did NOT fund.
# Zero discovery compute, pure bookkeeping, diluting the dimension to noise
# (0.002). v2 counts only funded attempts (verdicts attached to a dataset,
# plus watchdog-killed mid-validation runs). v1 stays published for
# reproducibility.


def test_gate_denominator_ignores_unfunded_bookkeeping():
    """10 findings out of 100 FUNDED attempts is a 0.1 gate rate — not 0.01
    just because 900 low-EV questions were (correctly) never funded."""
    idx = compute_capability_index(
        verdict_summary={"total_candidates": 1000, "buckets": {}},
        effectiveness=20.0, genuine=5, quarantined=5, funded=100)
    assert abs(idx["dimensions"]["gate_pass_rate"] - 0.1) < 1e-9
    # v1 stays reproducible with the diluted denominator
    assert abs(idx["capability_index_v1"] - idx["capability_index"]) > 0
    assert idx["denominator_audit"]["funded_attempts"] == 100
    assert idx["metric_version"] == 2


def test_funded_attempt_stats_separates_compute_from_bookkeeping(tmp_path):
    """low_ev_deprioritized / no_datasets never touched a dataset; only
    dataset-bearing verdicts count as funded."""
    from biodisc_core.fixed_pipeline.capability_index import funded_attempt_stats
    log = tmp_path / "verdicts.jsonl"
    rows = [
        {"outcome": "rejected", "reason": "low_ev_deprioritized: EV 0.01 < 0.05"},
        {"outcome": "rejected", "reason": "low_ev_deprioritized: EV 0.02 < 0.05"},
        {"outcome": "rejected", "reason": "no_datasets"},
        {"outcome": "rejected", "reason": "DUPLICATE: ...", "dataset_id": "GSE1"},
        {"outcome": "quarantined", "dataset_id": "GSE2"},
        {"outcome": "in_progress", "dataset_id": "GSE3"},  # live, not decided
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows))
    stats = funded_attempt_stats(log)
    assert stats["funded_decided"] == 2
    assert stats["low_ev_deprioritized"] == 2
    assert stats["no_datasets"] == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
