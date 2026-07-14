"""Tests for per-candidate verdict logging (the discovery funnel)."""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.verdict_log import (  # noqa: E402
    log_verdict, verdict_summary, print_funnel,
)


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
