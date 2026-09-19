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
"""Tests for the calibration registry (V9.1, Paper2Agent lesson #2).

Every invented constant in the pipeline must carry provenance and a staleness
fingerprint, and the registry must be cross-checked against the LIVE code so
silent drift is impossible: if someone edits a constant without re-registering
its provenance, validate_against_code() must flag it.

Run: python -m pytest tests/test_calibration_registry.py -v
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline import calibration_registry as cr  # noqa: E402


def test_registry_loads_and_has_entries():
    reg = cr.load_registry()
    assert len(reg["constants"]) >= 10
    ids = {e["id"] for e in reg["constants"]}
    assert "anomaly_miner.EXTREME_LOG2FC" in ids
    assert "literature_gate.similarity_threshold" in ids


def test_every_entry_carries_provenance():
    reg = cr.load_registry()
    for e in reg["constants"]:
        assert e.get("provenance", {}).get("note"), f"{e['id']} missing provenance note"
        assert "store_lines_at_calibration" in e["provenance"], (
            f"{e['id']} missing store_lines_at_calibration fingerprint")


def test_registry_validates_against_live_code():
    reg = cr.load_registry()
    results = cr.validate_against_code(reg)
    assert results, "no constants were resolved at all"
    mismatches = [r for r in results if not r["ok"]]
    assert not mismatches, f"registry out of sync with code: {mismatches}"


def test_tamper_detected(monkeypatch):
    """A constant edited in code without re-registering must be flagged."""
    from biodisc_core.fixed_pipeline import anomaly_miner
    monkeypatch.setattr(anomaly_miner, "EXTREME_LOG2FC", 1.5, raising=True)
    reg = cr.load_registry()
    results = cr.validate_against_code(reg)
    bad = [r for r in results if r["id"] == "anomaly_miner.EXTREME_LOG2FC"]
    assert bad and bad[0]["ok"] is False
    assert bad[0]["actual"] == 1.5 and bad[0]["registered"] == 1.0


def test_ctor_and_fn_defaults_resolved():
    """Constructor/function default parameters are registry-tracked too."""
    reg = cr.load_registry()
    results = {r["id"]: r for r in cr.validate_against_code(reg)}
    assert results["replication_gate.min_fraction"]["actual"] == 0.40
    assert results["value_of_compute.exploration_frac"]["actual"] == 0.15


def test_staleness_doubles():
    reg = cr.load_registry()
    # at_calibration=104 for every entry (32 genuine + 72 candidate lines at
    # registration); stale once the store has doubled.
    st = cr.staleness(reg, store_lines=208)
    assert all(s["stale"] for s in st)
    st = cr.staleness(reg, store_lines=207)
    assert not any(s["stale"] for s in st)
    st = cr.staleness(reg, store_lines=0)
    assert not any(s["stale"] for s in st)


def test_run_writes_report(tmp_path, monkeypatch):
    monkeypatch.setattr(cr, "REPORT_FILE", tmp_path / "calibration_report.json")
    report = cr.run(write=True)
    saved = json.loads((tmp_path / "calibration_report.json").read_text())
    assert saved["n_constants"] == report["n_constants"]
    assert saved["mismatches"] == []
    assert "generated_at" in saved
