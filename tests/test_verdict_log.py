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
"""Tests for per-candidate verdict logging (the discovery funnel)."""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.verdict_log import (  # noqa: E402
    log_verdict, verdict_summary, print_funnel, read_verdicts_dedup,
)


def _write_jsonl(path, records):
    path.write_text("\n".join(__import__("json").dumps(r) for r in records) + "\n")


# --- coverage fix: provisional + final dedup, abandoned detection -----------

def test_provisional_and_final_collapse_to_one(tmp_path):
    lf = tmp_path / "v.jsonl"
    _write_jsonl(lf, [
        {"vtok": "t1", "outcome": "in_progress", "question": "q", "logged_at": "2026-07-15T01:00:00+00:00"},
        {"vtok": "t1", "outcome": "rejected", "reason": "SIGNIFICANCE FAILED", "logged_at": "2026-07-15T01:00:05+00:00"},
    ])
    out = read_verdicts_dedup(lf)
    assert len(out) == 1
    assert out[0]["outcome"] == "rejected"  # final wins


def test_orphaned_provisional_becomes_abandoned_failure(tmp_path):
    """The coverage fix: a cycle killed mid-validation (provisional, no final)
    surfaces as a counted failure instead of silently vanishing."""
    lf = tmp_path / "v.jsonl"
    _write_jsonl(lf, [
        {"vtok": "t2", "outcome": "in_progress", "question": "q", "logged_at": "2026-07-15T02:00:00+00:00"},
    ])
    out = read_verdicts_dedup(lf)
    assert len(out) == 1
    assert out[0]["outcome"] == "rejected"
    assert "abandoned_mid_validation" in out[0]["reason"]


def test_verdicts_without_vtok_pass_through_unchanged(tmp_path):
    lf = tmp_path / "v.jsonl"
    recs = [
        {"outcome": "rejected", "reason": "no_datasets"},          # coarse live-loop
        {"outcome": "quarantined", "discovery_id": "D1"},          # legacy/final
    ]
    _write_jsonl(lf, recs)
    out = read_verdicts_dedup(lf)
    assert len(out) == 2  # no vtok -> not merged


def test_summary_counts_abandoned_and_does_not_double_count(tmp_path):
    lf = tmp_path / "v.jsonl"
    _write_jsonl(lf, [
        {"vtok": "t1", "outcome": "in_progress", "logged_at": "2026-07-15T01:00:00+00:00"},
        {"vtok": "t1", "outcome": "rejected", "reason": "SIGNIFICANCE FAILED", "gate1_pass": False, "logged_at": "2026-07-15T01:00:05+00:00"},
        {"vtok": "t2", "outcome": "in_progress", "logged_at": "2026-07-15T02:00:00+00:00"},  # orphaned -> abandoned
    ])
    s = verdict_summary(lf)
    assert s["total_candidates"] == 2  # t1 collapsed, t2 abandoned -> 2 total
    assert s["abandoned"] == 1


def test_log_verdict_writes_one_jsonl_line(tmp_path):
    lf = tmp_path / "v.jsonl"
    log_verdict({"question": "q", "outcome": "rejected", "gate1_pass": False}, log_file=lf)
    log_verdict({"question": "q2", "outcome": "stored", "gate1_pass": True,
                 "gate2_status": "novel"}, log_file=lf)
    lines = lf.read_text().strip().splitlines()
    assert len(lines) == 2


def test_log_verdict_never_raises(tmp_path):
    """Logging must not break the pipeline even on bad inputs."""
    lf = tmp_path / "v.jsonl"
    log_verdict(None, log_file=lf)  # type: ignore[arg-type]
    # should not raise
    assert True


def test_funnel_buckets_bottleneck(tmp_path):
    lf = tmp_path / "v.jsonl"
    # 8 die at gate1, 1 dies gate2-known, 1 stored
    for _ in range(8):
        log_verdict({"outcome": "rejected", "gate1_pass": False}, log_file=lf)
    log_verdict({"outcome": "rejected", "gate1_pass": True, "gate2_status": "known"}, log_file=lf)
    log_verdict({"outcome": "stored", "gate1_pass": True, "gate2_status": "novel"}, log_file=lf)
    s = verdict_summary(lf)
    assert s["total_candidates"] == 10
    assert s["bottleneck"] == "died_gate1_significance"
    assert s["buckets"]["died_gate1_significance"] == 8
    assert s["stored"] == 1
    text = print_funnel(lf)
    assert "BOTTLENECK" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
