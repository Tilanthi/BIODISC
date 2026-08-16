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
"""Tests for the RSI miner (mine / propose / measure loop).

Synthetic verdicts only — no network, no real data. Verifies (1) failure-theme
clustering and (2) the before/after recurrence measure that makes the loop close.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.rsi_miner import (  # noqa: E402
    mine, measure, effectiveness_rollup, _themes_of,
)

# A realistic "now" shortly after the synthetic fix date (2026-07-15), so the
# before/after windows are comparable in length and per-day rates are meaningful.
NOW = datetime(2026, 7, 19, tzinfo=timezone.utc).timestamp()


def _v(reason, outcome="rejected", at="2026-07-14T00:00:00+00:00", question="q"):
    return {"outcome": outcome, "reason": reason, "logged_at": at, "question": question}


# --- clustering -------------------------------------------------------------

def test_significance_failures_cluster_into_one_theme():
    vs = [_v("SIGNIFICANCE FAILED: best fdr 1.0 exceeds 0.01", at="2026-07-14T0%d:00:00+00:00" % i)
          for i in range(1, 6)]
    patterns = {p.theme: p for p in mine(vs)}
    assert "significance_failed" in patterns
    assert patterns["significance_failed"].count == 5


def test_organism_mismatch_clusters_separately():
    vs = [_v("Organism mismatch: question mentions mouse but dataset is mus musculus",
             at="2026-07-14T01:00:00+00:00")]
    themes = {p.theme for p in mine(vs)}
    assert "organism_mismatch" in themes


def test_multi_reason_verdict_counts_each_theme():
    # A verdict rejected at two gates contributes to both themes.
    vs = [_v("SIGNIFICANCE FAILED: ...; LITERATURE KNOWN: claim entailed")]
    pmap = {p.theme: p for p in mine(vs)}
    assert pmap["significance_failed"].count == 1
    assert pmap["literature_known"].count == 1


def test_only_rejected_verdicts_are_mined():
    vs = [
        _v("SIGNIFICANCE FAILED", outcome="rejected"),
        _v("", outcome="quarantined"),  # passed validation — not a failure
        _v("", outcome="stored"),
    ]
    patterns = mine(vs)
    assert sum(p.count for p in patterns) == 1  # only the rejected one


def test_unclassified_reason_falls_through():
    assert _themes_of("some novel unknown problem") == ["unclassified"]


# --- the measure step (loop-closer) -----------------------------------------

def test_measure_fix_that_eliminates_class_is_high_effectiveness():
    # organism_mismatch happens 4x BEFORE the fix date, 0x after.
    vs = [_v("Organism mismatch: ...", at="2026-07-1%dT00:00:00+00:00" % i) for i in range(0, 4)]
    applied = [{"theme": "organism_mismatch", "applied_at": "2026-07-15T00:00:00+00:00"}]
    ms = measure(applied, vs, now_epoch=2_000_000_000.0)
    assert len(ms) == 1
    m = ms[0]
    assert m.before_count == 4 and m.after_count == 0
    assert m.effectiveness == 100.0


def test_measure_fix_that_does_not_help_is_low_effectiveness():
    # Failures continue at a similar rate after the "fix".
    vs = ([_v("Organism mismatch: ...", at="2026-07-1%dT00:00:00+00:00" % i) for i in range(0, 4)]
          + [_v("Organism mismatch: ...", at="2026-07-1%dT00:00:00+00:00" % i) for i in range(6, 9)])
    applied = [{"theme": "organism_mismatch", "applied_at": "2026-07-15T00:00:00+00:00"}]
    m = measure(applied, vs, now_epoch=NOW)[0]
    assert m.after_count == 3  # still recurring
    assert m.effectiveness is not None and m.effectiveness < 50.0  # genuinely low


def test_measure_no_prior_failures_is_unmeasurable():
    vs = [_v("Organism mismatch: ...", at="2026-07-20T00:00:00+00:00")]  # only after
    applied = [{"theme": "organism_mismatch", "applied_at": "2026-07-15T00:00:00+00:00"}]
    m = measure(applied, vs)[0]
    assert m.effectiveness is None  # nothing to measure the fix against


def test_rollup_is_before_count_weighted():
    # Two fixes: one eliminated a frequent class (100), one did nothing (0).
    vs = ([_v("Organism mismatch", at="2026-07-1%d" % i) for i in range(0, 4)]   # 4 before
          + [_v("Significance failed", at="2026-07-1%d" % i) for i in range(0, 2)]  # 2 before
          + [_v("Significance failed", at="2026-07-1%d" % i) for i in range(6, 8)])  # 2 after
    applied = [
        {"theme": "organism_mismatch", "applied_at": "2026-07-15T00:00:00+00:00"},
        {"theme": "significance_failed", "applied_at": "2026-07-15T00:00:00+00:00"},
    ]
    ms = measure(applied, vs, now_epoch=NOW)
    roll = effectiveness_rollup(ms)
    # weighted by before_count: (100*4 + 0*2)/(4+2) = 66.7
    assert roll is not None and 60 < roll < 70


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
