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
"""Liveness + persistence for the gene-symbol validation crawl.

The 2.7-minute kill spiral landed here: validating a 2000-symbol GEO matrix is
minutes-to-hours of serial HGNC HTTP with (a) no heartbeat, so the watchdog
saw "loop idle", and (b) in-memory-only caches, so every kill+restart
re-crawled the same symbols from zero. These tests pin both fixes: the crawl
heartbeats while it runs, and its cache survives the process.
"""
import json

from biodisc_core.fixed_pipeline import discovery_status
from biodisc_core.fixed_pipeline import gene_symbol_validation as gsv


def _offline_validator(monkeypatch, tmp_path, hgnc_results=None):
    """Validator with the network replaced by a controllable stub."""
    monkeypatch.setattr(gsv, "CACHE_PATH", tmp_path / "gsv_cache.json")
    monkeypatch.setattr(discovery_status, "STATUS_FILE",
                        tmp_path / "status.json")
    hgnc_results = hgnc_results or {}

    def _fake_hgnc(self, symbol, timeout=10):
        res = hgnc_results.get(symbol)
        if res is None:
            return None  # API unavailable -> UNKNOWN
        return gsv.GeneSymbolValidation(
            symbol=symbol, result=res, source="HGNC", gene_id=symbol)

    monkeypatch.setattr(gsv.GeneSymbolValidator, "_query_hgnc", _fake_hgnc)
    return gsv.create_gene_symbol_validator()


def test_crawl_heartbeats_while_validating(monkeypatch, tmp_path):
    """record_activity fires during the crawl — the watchdog's idle check
    must see liveness, not a minutes-long silent network loop."""
    v = _offline_validator(monkeypatch, tmp_path)
    beats = []
    monkeypatch.setattr(discovery_status, "record_activity",
                        lambda note="": beats.append(note))
    # 30 symbols that all miss cache/known-list/probe/fake paths -> HGNC stub
    symbols = [f"ABC{i}" for i in range(30)]
    monkeypatch.setattr(v, "_last_progress_flush", 0.0)  # force first flush
    v.validate_gene_symbols(symbols, reject_on_invalid=False)
    assert beats, "no heartbeat fired during gene-symbol validation"
    assert any("gene_symbol_validation" in b for b in beats)


def test_cache_survives_process_restart(monkeypatch, tmp_path):
    """A second validator instance (i.e. process restart) must NOT re-ask
    HGNC about symbols the first one already resolved."""
    hgnc_calls = []

    def _fake_hgnc(self, symbol, timeout=10):
        hgnc_calls.append(symbol)
        return gsv.GeneSymbolValidation(
            symbol=symbol, result=gsv.ValidationResult.VALID,
            source="HGNC", gene_id=symbol)

    monkeypatch.setattr(gsv, "CACHE_PATH", tmp_path / "gsv_cache.json")
    monkeypatch.setattr(discovery_status, "STATUS_FILE",
                        tmp_path / "status.json")
    monkeypatch.setattr(gsv.GeneSymbolValidator, "_query_hgnc", _fake_hgnc)

    v1 = gsv.create_gene_symbol_validator()
    v1.validate_gene_symbols(["ZZZ1", "ZZZ2"], reject_on_invalid=False)
    n_first = len(hgnc_calls)
    assert n_first == 2

    v2 = gsv.create_gene_symbol_validator()  # fresh process, disk cache only
    results, ok = v2.validate_gene_symbols(["ZZZ1", "ZZZ2"],
                                           reject_on_invalid=False)
    assert len(hgnc_calls) == n_first  # zero new network calls
    assert ok
    assert all(r.result == gsv.ValidationResult.VALID for r in results)


def test_unknown_results_are_not_persisted_as_facts(monkeypatch, tmp_path):
    """A transient API outage (UNKNOWN) must not be frozen into the cache —
    only confirmed valid/invalid verdicts are persisted."""
    v = _offline_validator(monkeypatch, tmp_path,
                           hgnc_results={})  # everything -> UNKNOWN
    v.validate_gene_symbols(["QQQ1"], reject_on_invalid=False)
    disk = json.loads(gsv.CACHE_PATH.read_text())
    assert "QQQ1" not in disk.get("valid", [])
    assert "QQQ1" not in disk.get("invalid", [])
