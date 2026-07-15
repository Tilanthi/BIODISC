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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_FILE = PROJECT_ROOT / "capability_index.json"
EFFECTIVENESS_FILE = PROJECT_ROOT / "rsi_effectiveness.txt"
GENUINE_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"
CANDIDATE_STORE = PROJECT_ROOT / "autonomous_discoveries_candidates.jsonl"


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
                             quarantined: Optional[int] = None) -> dict:
    """Compute a dated capability index. Designed to go DOWN on bad news.

    Dimensions (each 0-1 unless noted):
      replication_rate  (w=0.5): genuine / (genuine + quarantined) — the bridge
                                  from candidate to finding. Today 0. THE headline driver.
      gate_pass_rate    (w=0.3): (genuine + quarantined) / total candidates — the
                                  fraction that survive all gates (pipeline quality).
      rsi_effectiveness (w=0.2): 0-100 roll-up of whether applied fixes worked (or 0
                                  if none measurable). Whether the system is improving.

    ``genuine``/``quarantined`` default to the chokepoint-gated stores (authoritative);
    tests inject them directly for determinism.
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

    replication_rate = stored / max(1, stored + quarantined)  # 0 when no genuine findings
    gate_pass_rate = (stored + quarantined) / total
    rsi = (effectiveness / 100.0) if effectiveness is not None else 0.0
    rsi_measured = effectiveness is not None

    composite = 100.0 * (
        W_REPLICATION * replication_rate
        + W_GATE_PASS * gate_pass_rate
        + W_RSI * rsi
    )

    return {
        "capability_index": round(composite, 1),
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dimensions": {
            "replication_rate": round(replication_rate, 3),
            "gate_pass_rate": round(gate_pass_rate, 3),
            "rsi_effectiveness": (round(effectiveness, 1) if effectiveness is not None else None),
        },
        "drivers": {
            "genuine": stored,
            "quarantined": quarantined,
            "total_candidates": verdict_summary.get("total_candidates", 0),
            "abandoned": buckets.get("abandoned_mid_validation", 0),
            "rsi_measured": rsi_measured,
        },
        "note": ("Compass needle, not a benchmark. 100 = formula saturation, not "
                 "'solved biology'. genuine/quarantined counted from the chokepoint-"
                 "gated stores (authoritative); replication_rate is the load-bearing "
                 "dimension."),
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
