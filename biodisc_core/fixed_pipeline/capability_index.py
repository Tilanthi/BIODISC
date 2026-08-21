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
"""BIODISC capability index — one dated number for "are we getting better at discovery?"

The Beast's CI-score design property, applied to BIODISC: a composite computed from
the fleet's own recorded artifacts that is DESIGNED to ingest inputs which can lower
its own headline. The load-bearing dimension is REPLICATION — the actual discovery
criterion — which today is 0% (no finding has reached the genuine/replicated tier),
so the index is honestly low. As replication, gate-pass rate, and RSI effectiveness
improve, it rises; a regression in any of them drops it.

This is a compass needle, not a benchmark. 100 means "the formula's components are
saturated," not "solved biology." Trend over level; read the breakdown, not just the
composite. Dependency-free (stdlib only).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

from .paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
INDEX_FILE = PROJECT_ROOT / "capability_index.json"
EFFECTIVENESS_FILE = PROJECT_ROOT / "rsi_effectiveness.txt"
GENUINE_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"
CANDIDATE_STORE = PROJECT_ROOT / "autonomous_discoveries_candidates.jsonl"
VERDICT_LOG = PROJECT_ROOT / "discovery_verdicts.jsonl"


def kill_recovery_rates(verdict_log: Optional[Path] = None) -> dict:
    """Paired kill-rate + recovery-rate (Item-Bank Schema v0.2).

    Kill-rate = fraction of candidates rejected (specificity — high is good).
    Recovery-rate = fraction that survived to the shortlist (sensitivity —
    stored + quarantined). The PAIR is what matters: kill-rate alone rewards
    refusing everything (perfect kill, zero recovery = safe but meaningless).
    """
    log = verdict_log or VERDICT_LOG
    rejected = stored = quarantined = in_progress = 0
    if log.exists():
        with open(log) as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    r = json.loads(s)
                except Exception:
                    continue
                outcome = r.get("outcome", "")
                if outcome == "rejected":
                    rejected += 1
                elif outcome == "stored":
                    stored += 1
                elif outcome == "quarantined":
                    quarantined += 1
                elif outcome == "in_progress":
                    in_progress += 1
    total = max(1, rejected + stored + quarantined)
    return {
        "kill_rate": round(rejected / total, 4),
        "recovery_rate": round((stored + quarantined) / total, 4),
        "decided": rejected + stored + quarantined,
        "in_progress": in_progress,
        "note": ("kill-rate + recovery-rate reported as a PAIR. Kill-rate alone "
                 "rewards refusing everything (perfect specificity, zero sensitivity)."),
    }


def contrarian_success_rate(verdict_log: Optional[Path] = None) -> dict:
    """The rebuild's true success metric (rebuild item 5).

    Of funded gene-naming (contrarian) questions that ran the gene-specific test,
    how many were BOTH supported by the data (the named gene moved in the claimed
    direction) AND novel (that specific directional claim is absent from PubMed).
    That intersection is a genuine surprise candidate — the thing the whole
    rebuild is trying to produce. ``supported_novel_rate`` is the trend to watch:
    if it stays at 0 the primitive is still the bottleneck (or the bets keep
    failing/being known); if it climbs, the pipeline is producing real novelty.

    Reads the verdict log; entries without ``gene_hypothesis_supports`` (exploratory
    questions, or pre-V8.0.27 runs) are skipped. Forward-looking — populates only
    once the loop runs V8.0.27+ code.
    """
    log = verdict_log or VERDICT_LOG
    tested = supported = supported_novel = supported_known = 0
    if log.exists():
        with open(log) as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    r = json.loads(s)
                except Exception:
                    continue
                sup = r.get("gene_hypothesis_supports")
                if sup is None:
                    continue
                tested += 1
                if sup is True:
                    supported += 1
                    g2 = r.get("gate2_status")
                    if g2 == "novel":
                        supported_novel += 1
                    elif g2 == "known":
                        supported_known += 1
    return {
        "contrarian_tested": tested,
        "supported": supported,
        "supported_and_novel": supported_novel,
        "supported_but_known": supported_known,
        "supported_novel_rate": round(supported_novel / tested, 4) if tested else 0.0,
        "note": ("genuine-surprise candidates = contrarian claim supported AND novel. "
                 "0 until the loop runs V8.0.27+ and funds gene-naming questions."),
    }


def _count_store(path: Path, tier: Optional[str] = None) -> int:
    """Count store entries (optionally by flagging tier). Authoritative — the
    stores are chokepoint-gated, unlike the verdict log whose 'stored' outcome
    has proven an unreliable genuine signal."""
    if not path.exists():
        return 0
    n = 0
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if tier is None or (d.get("flagging") or {}).get("tier") == tier:
            n += 1
    return n

def funded_attempt_stats(verdict_log: Optional[Path] = None) -> dict:
    """Split the verdict log into real discovery compute vs bookkeeping.

    The v1 gate_pass denominator was the whole log — 93% of it
    ``low_ev_deprioritized``: questions the value-of-compute gate considered
    and did NOT fund (zero compute), plus ``no_datasets`` pre-filter drops.
    Only dataset-bearing verdicts (a dataset was actually attempted) plus
    watchdog-killed mid-validation runs spent compute; those form the v2
    denominator.
    """
    log = verdict_log or VERDICT_LOG
    low_ev = no_data = funded_decided = 0
    if log.exists():
        with open(log) as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    r = json.loads(s)
                except Exception:
                    continue
                outcome = r.get("outcome", "")
                reason = r.get("reason") or ""
                if outcome == "rejected":
                    if reason.startswith("low_ev_deprioritized"):
                        low_ev += 1
                    elif reason == "no_datasets":
                        no_data += 1
                if r.get("dataset_id") and outcome in ("rejected", "stored",
                                                       "quarantined"):
                    funded_decided += 1
    return {"funded_decided": funded_decided,
            "low_ev_deprioritized": low_ev,
            "no_datasets": no_data}


# Weights — replication is heaviest because it IS the discovery criterion.
W_REPLICATION = 0.5
W_GATE_PASS = 0.3
W_RSI = 0.2


def _read_effectiveness() -> Optional[float]:
    try:
        txt = EFFECTIVENESS_FILE.read_text().strip()
        return float(txt) if txt else None
    except Exception:
        return None


def compute_capability_index(verdict_summary: Optional[dict] = None,
                             effectiveness: Optional[float] = None,
                             genuine: Optional[int] = None,
                             quarantined: Optional[int] = None,
                             funded: Optional[int] = None) -> dict:
    """Compute a dated capability index. Designed to go DOWN on bad news.

    Dimensions (each 0-1 unless noted):
      replication_rate  (w=0.5): genuine / (genuine + quarantined) — the bridge
                                  from candidate to finding. THE headline driver.
      gate_pass_rate    (w=0.3): (genuine + quarantined) / FUNDED attempts — the
                                  fraction of real compute that survives all gates.
                                  v2 (2026-08-16): the denominator is funded
                                  attempts only (dataset-bearing verdicts +
                                  mid-validation kills). v1 used the whole
                                  verdict log, 93% of which was low-EV
                                  bookkeeping that never spent compute, pinning
                                  the dimension at ~0.002. v1 stays published as
                                  capability_index_v1 for reproducibility.
      rsi_effectiveness (w=0.2): 0-100 roll-up of whether applied fixes worked (or 0
                                  if none measurable). Whether the system is improving.

    ``genuine``/``quarantined`` default to the chokepoint-gated stores (authoritative);
    tests inject them directly for determinism. ``funded`` defaults to
    funded_attempt_stats() + abandoned mid-validation runs.
    """
    if verdict_summary is None:
        from biodisc_core.fixed_pipeline.verdict_log import verdict_summary as _vs
        verdict_summary = _vs()
    if effectiveness is None:
        effectiveness = _read_effectiveness()

    buckets = verdict_summary.get("buckets", {}) or {}
    # Authoritative counts come from the chokepoint-gated STORES, not the verdict
    # log (whose 'stored' outcome has proven an unreliable genuine signal).
    if genuine is None:
        genuine = _count_store(GENUINE_STORE, tier="genuine")
    if quarantined is None:
        quarantined = _count_store(CANDIDATE_STORE)
    stored = genuine
    total = max(1, verdict_summary.get("total_candidates", 0))
    stats = funded_attempt_stats()
    if funded is None:
        funded = stats["funded_decided"] + buckets.get("abandoned_mid_validation", 0)
    funded = max(1, funded)

    replication_rate = stored / max(1, stored + quarantined)  # 0 when no genuine findings
    gate_pass_rate = min(1.0, (stored + quarantined) / funded)   # v2: funded attempts
    gate_pass_rate_v1 = (stored + quarantined) / total            # legacy diluted view
    rsi = (effectiveness / 100.0) if effectiveness is not None else 0.0
    rsi_measured = effectiveness is not None

    composite = 100.0 * (
        W_REPLICATION * replication_rate
        + W_GATE_PASS * gate_pass_rate
        + W_RSI * rsi
    )
    composite_v1 = 100.0 * (
        W_REPLICATION * replication_rate
        + W_GATE_PASS * gate_pass_rate_v1
        + W_RSI * rsi
    )

    return {
        "capability_index": round(composite, 1),
        "capability_index_v1": round(composite_v1, 1),
        "metric_version": 2,
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dimensions": {
            "replication_rate": round(replication_rate, 3),
            "gate_pass_rate": round(gate_pass_rate, 3),
            "gate_pass_rate_v1_diluted": round(gate_pass_rate_v1, 3),
            "rsi_effectiveness": (round(effectiveness, 1) if effectiveness is not None else None),
        },
        "drivers": {
            "genuine": stored,
            "quarantined": quarantined,
            "total_candidates": verdict_summary.get("total_candidates", 0),
            "abandoned": buckets.get("abandoned_mid_validation", 0),
            "rsi_measured": rsi_measured,
        },
        "denominator_audit": {
            "funded_attempts": funded,
            "funded_decided": stats["funded_decided"],
            "low_ev_deprioritized": stats["low_ev_deprioritized"],
            "no_datasets": stats["no_datasets"],
            "verdict_log_total": verdict_summary.get("total_candidates", 0),
            "note": ("v2 gate denominator counts only attempts that spent real "
                     "discovery compute (dataset-bearing verdicts + mid-validation "
                     "kills). low_ev_deprioritized entries were considered by the "
                     "EV gate and never funded — bookkeeping, not attempts."),
        },
        "contrarian_success_rate": contrarian_success_rate(),
        "kill_recovery_rates": kill_recovery_rates(),
        "note": ("Compass needle, not a benchmark. 100 = formula saturation, not "
                 "'solved biology'. genuine/quarantined counted from the chokepoint-"
                 "gated stores (authoritative); replication_rate is the load-bearing "
                 "dimension. v2 (2026-08-16): funded-attempt gate denominator; "
                 "capability_index_v1 preserves the original diluted formula."),
    }


def run(write: bool = True) -> dict:
    idx = compute_capability_index()
    if write:
        INDEX_FILE.write_text(json.dumps(idx, indent=2))
        logger.info("capability_index = %s/100 -> %s", idx["capability_index"], INDEX_FILE)
    return idx


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Compute BIODISC capability index.")
    p.add_argument("--no-write", action="store_true")
    args = p.parse_args(argv)
    idx = run(write=not args.no_write)
    print(json.dumps(idx, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
