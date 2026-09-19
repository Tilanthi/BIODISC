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
"""Calibration registry — provenance + staleness fingerprints for every invented constant.

Paper2Agent lesson (V9.1): every deviation from a calibrated value must be a
DETECTABLE mechanical state, not a judgment call. BIODISC's pipeline is full of
invented algorithms — the Gate-2 cosine threshold, the anomaly-miner effect
cutoff, the EV weights — and each constant was calibrated once, manually, or
never. This module makes that systematic:

* ``calibration_registry.json`` registers each constant with its live value,
  provenance (how/when it was derived), and a ``store_lines_at_calibration``
  fingerprint.
* :func:`validate_against_code` cross-checks every registered value against the
  LIVE code (module attributes and constructor/function defaults), so editing a
  constant without re-registering its provenance is flagged as a mismatch.
* :func:`staleness` flags entries whose calibration predates a doubling of the
  discovery store — the signal to re-derive the value on the now-larger data.

Run: ``python -m biodisc_core.fixed_pipeline.calibration_registry``
(writes ``calibration_report.json``).
"""
from __future__ import annotations

import importlib
import inspect
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

from .paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
REGISTRY_FILE = PROJECT_ROOT / "calibration_registry.json"
REPORT_FILE = PROJECT_ROOT / "calibration_report.json"
GENUINE_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"
CANDIDATE_STORE = PROJECT_ROOT / "autonomous_discoveries_candidates.jsonl"

_PACKAGE = "biodisc_core.fixed_pipeline"


def load_registry(path: Optional[Path] = None) -> dict:
    p = Path(path) if path is not None else REGISTRY_FILE
    return json.loads(p.read_text())


def _resolve_actual(entry: dict):
    """Resolve an entry's value from the LIVE code (never the registry)."""
    mod = importlib.import_module(f"{_PACKAGE}.{entry['module']}")
    kind = entry["kind"]
    if kind == "module_attr":
        return getattr(mod, entry["symbol"])
    if kind == "ctor_default":
        cls = getattr(mod, entry["params"]["class"])
        params = inspect.signature(cls.__init__).parameters
        return params[entry["params"]["param"]].default
    if kind == "fn_default":
        fn = getattr(mod, entry["params"]["fn"])
        params = inspect.signature(fn).parameters
        return params[entry["params"]["param"]].default
    raise ValueError(f"unknown registry entry kind: {kind!r} (id={entry.get('id')})")


def validate_against_code(registry: dict) -> List[dict]:
    """Cross-check registered values against the live code.

    Returns one ``{id, registered, actual, ok}`` per constant. A mismatch means
    someone edited the constant without re-registering provenance (or vice
    versa) — exactly the silent drift this registry exists to catch.
    """
    out: List[dict] = []
    for e in registry.get("constants", []):
        try:
            actual = _resolve_actual(e)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the report
            out.append({"id": e.get("id"), "registered": e.get("value"),
                        "actual": f"UNRESOLVABLE: {exc}", "ok": False})
            continue
        out.append({"id": e.get("id"), "registered": e.get("value"), "actual": actual,
                    "ok": actual == e.get("value")})
    return out


def _count_store_lines() -> int:
    n = 0
    for p in (GENUINE_STORE, CANDIDATE_STORE):
        if p.exists():
            n += sum(1 for line in p.read_text().splitlines() if line.strip())
    return n


def staleness(registry: dict, store_lines: Optional[int] = None) -> List[dict]:
    """Flag entries whose calibration predates a doubling of the store.

    An entry calibrated at N store lines goes stale when the store reaches
    ``stale_at_multiplier * N`` (default 2x) — the point where the data the
    constant was derived from is no longer representative.
    """
    if store_lines is None:
        store_lines = _count_store_lines()
    out: List[dict] = []
    for e in registry.get("constants", []):
        at = (e.get("provenance") or {}).get("store_lines_at_calibration") or 0
        m = e.get("stale_at_multiplier", 2.0)
        out.append({"id": e.get("id"), "at_calibration": at, "now": store_lines,
                    "stale": bool(store_lines >= m * max(at, 1))})
    return out


def run(write: bool = True, registry_path: Optional[Path] = None) -> dict:
    reg = load_registry(registry_path)
    mismatches = [r for r in validate_against_code(reg) if not r["ok"]]
    stale = [s for s in staleness(reg) if s["stale"]]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_constants": len(reg.get("constants", [])),
        "mismatches": mismatches,
        "stale_entries": stale,
        "note": ("mismatches = code edited without re-registered provenance (fix "
                 "immediately); stale = store doubled since calibration "
                 "(re-derive the value on the larger data)."),
    }
    if write:
        REPORT_FILE.write_text(json.dumps(report, indent=2))
        logger.info("calibration report -> %s (mismatches=%d, stale=%d)",
                    REPORT_FILE, len(mismatches), len(stale))
    return report


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        description="Cross-check the calibration registry against live code.")
    p.add_argument("--no-write", action="store_true")
    args = p.parse_args(argv)
    report = run(write=not args.no_write)
    print(json.dumps(report, indent=2))
    if report["mismatches"]:
        return 1
    return 0


__all__ = ["load_registry", "validate_against_code", "staleness", "run", "main",
           "REGISTRY_FILE", "REPORT_FILE"]


if __name__ == "__main__":
    raise SystemExit(main())
