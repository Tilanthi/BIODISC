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
"""Tests for the two changes in this pull request.

FIX 1 - batching: gene-symbol validation made one HTTP request per symbol.
        It now makes ONE request for the whole catalogue, and the verdicts it
        produces are the same verdicts.

FIX 2 - silent loss: a non-200 response from HGNC returned None with no log
        line anywhere, and the caller drops an unverified symbol, so genes left
        the analysis without a trace. The verdict is deliberately UNCHANGED -
        an unverifiable symbol is still UNKNOWN, not INVALID - what changes is
        that it is now said out loud.

Everything here is offline: no test in this file touches the network. The
live-API equivalence check is `test_live_equivalence.py`, which is skipped
unless BIODISC_HGNC_LIVE=1 is set deliberately.
"""
import json
import logging
import time

import pytest

from biodisc_core.fixed_pipeline import gene_symbol_validation as gsv
from biodisc_core.fixed_pipeline.gene_symbol_validation import (
    GeneSymbolValidator, ValidationResult)


# Symbols chosen so that every one of them reaches the network layer: none is
# in the curated known-real list, none matches a probe-ID rule, and none trips
# a fake-pattern heuristic. A symbol that never reaches HGNC would prove
# nothing about HGNC access.
CATALOGUE = {
    "MTOR": "HGNC:3942",
    "BEST1": "HGNC:1257",
    "CRADD": "HGNC:2340",
    "RCAN2": "HGNC:3041",
    "XIST": "HGNC:12810",
    # HGNC's own spelling of this one is mixed-case, and the live per-symbol
    # endpoint answers for any capitalisation of it. The catalogue must too.
    "C1orf21": "HGNC:15494",
    "MIR1273E": "HGNC:50833",   # status "Entry Withdrawn": fetch/symbol still finds it
}
NOT_IN_CATALOGUE = ["TRP53", "GM10801", "TP53///TP63", "NOTAGENE1"]


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content=b"x"):
        self.status_code = status_code
        self._payload = payload
        self.content = content

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON in this response")
        return self._payload


def catalogue_payload(mapping=None, num_found=None):
    docs = [{"symbol": s, "hgnc_id": i} for s, i in (mapping or CATALOGUE).items()]
    return {"response": {"numFound": num_found if num_found is not None else len(docs),
                         "docs": docs}}


def per_symbol_payload(symbol):
    """What fetch/symbol/<symbol> returns - case-insensitive, like the real one."""
    hgnc_id = (mapping_upper := {k.upper(): v for k, v in CATALOGUE.items()}).get(symbol.upper())
    if hgnc_id:
        return {"response": {"numFound": 1,
                             "docs": [{"hgnc_id": hgnc_id, "name": f"name of {symbol}"}]}}
    assert mapping_upper is not None
    return {"response": {"numFound": 0, "docs": []}}


class RecordingSession:
    """Stands in for the module's requests.Session and records every call."""

    def __init__(self, catalogue_response=None, per_symbol=True):
        self.calls = []
        self._catalogue_response = catalogue_response
        self._per_symbol = per_symbol

    def get(self, url, **kwargs):
        self.calls.append(url)
        if url == gsv.HGNC_CATALOGUE_URL:
            if self._catalogue_response is not None:
                return self._catalogue_response
            return FakeResponse(200, catalogue_payload())
        symbol = url.rsplit("/fetch/symbol/", 1)[-1]
        if not self._per_symbol:
            return FakeResponse(503, None)
        return FakeResponse(200, per_symbol_payload(symbol))

    @property
    def catalogue_calls(self):
        return [u for u in self.calls if u == gsv.HGNC_CATALOGUE_URL]

    @property
    def per_symbol_calls(self):
        return [u for u in self.calls if "/fetch/symbol/" in u]


@pytest.fixture(autouse=True)
def _isolated_hgnc(tmp_path, monkeypatch):
    """Module-level catalogue state and the on-disk cache are per-process; give
    every test its own, or a test would silently inherit another's catalogue."""
    monkeypatch.setenv("BIODISC_HGNC_CATALOGUE", str(tmp_path / "catalogue.json"))
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE", None)
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE_TRIED", False)
    monkeypatch.setattr(gsv, "_HGNC_STATUS_COUNTS", {})
    monkeypatch.setattr(gsv, "_HGNC_LAST_REQUEST", 0.0)
    yield


def install(monkeypatch, session):
    monkeypatch.setattr(gsv, "_HGNC_SESSION", session)
    return session


# ---------------------------------------------------------------------------
# FIX 1 - one request instead of one per symbol
# ---------------------------------------------------------------------------

def test_many_symbols_cost_exactly_one_http_request(monkeypatch):
    session = install(monkeypatch, RecordingSession())
    symbols = list(CATALOGUE) + NOT_IN_CATALOGUE
    validator = GeneSymbolValidator()

    results, _ = validator.validate_gene_symbols(symbols * 3, reject_on_invalid=False)

    assert len(session.catalogue_calls) == 1, "catalogue must be fetched once per process"
    assert session.per_symbol_calls == [], "no per-symbol request may remain"
    assert len(results) == len(symbols) * 3


def test_catalogue_verdicts_equal_per_symbol_verdicts(monkeypatch):
    """The whole point. Same symbols, both code paths, verdict by verdict."""
    symbols = list(CATALOGUE) + NOT_IN_CATALOGUE + ["Mtor", "best1", "Trp53"]

    # Path A: the per-symbol endpoint (what this PR replaces). The catalogue
    # fetch fails, so the validator falls back to exactly the old behaviour.
    install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(500, None)))
    old, _ = GeneSymbolValidator().validate_gene_symbols(symbols, reject_on_invalid=False)

    # Path B: the catalogue.
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE", None)
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE_TRIED", False)
    session_b = install(monkeypatch, RecordingSession())
    new, _ = GeneSymbolValidator().validate_gene_symbols(symbols, reject_on_invalid=False)

    assert [r.result for r in new] == [r.result for r in old]
    assert [r.symbol for r in new] == [r.symbol for r in old]
    assert len(session_b.per_symbol_calls) == 0
    # and the verdicts are not all the same value, or the comparison is empty
    assert {r.result for r in new} == {ValidationResult.VALID, ValidationResult.INVALID}


def test_catalogue_lookup_is_case_insensitive_like_fetch_symbol(monkeypatch):
    """fetch/symbol/<S> is case-insensitive against the live API (MTOR and Mtor
    both return numFound=1). The catalogue must behave the same way: this is
    the reason non-human symbols validate at all, and changing it would change
    which symbols survive - not this PR's decision to make."""
    install(monkeypatch, RecordingSession())
    validator = GeneSymbolValidator()

    for spelling in ("MTOR", "Mtor", "mtor", "mToR"):
        result = validator._validate_single_symbol(spelling)
        assert result.result == ValidationResult.VALID, spelling
        assert result.gene_id == "HGNC:3942"

    # ... and symbols HGNC itself spells in mixed case (361 of them, e.g.
    # C1orf21) must resolve however the platform annotation spells them.
    for spelling in ("C1orf21", "C1ORF21", "c1orf21"):
        result = validator._validate_single_symbol(spelling)
        assert result.result == ValidationResult.VALID, spelling
        assert result.gene_id == "HGNC:15494"


def test_catalogue_is_cached_on_disk_and_reused_cold(monkeypatch, tmp_path):
    session = install(monkeypatch, RecordingSession())
    GeneSymbolValidator().validate_gene_symbols(["MTOR"], reject_on_invalid=False)
    assert len(session.catalogue_calls) == 1
    cache = tmp_path / "catalogue.json"
    assert json.loads(cache.read_text())["MTOR"] == "HGNC:3942"

    # A brand-new process: module state reset, disk cache still there.
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE", None)
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE_TRIED", False)
    session2 = install(monkeypatch, RecordingSession())
    results, _ = GeneSymbolValidator().validate_gene_symbols(["MTOR"], reject_on_invalid=False)

    assert session2.calls == [], "a restart must not refetch a fresh catalogue"
    assert results[0].result == ValidationResult.VALID


def test_expired_disk_cache_is_refetched(monkeypatch, tmp_path):
    cache = tmp_path / "catalogue.json"
    cache.write_text(json.dumps({"STALE": "HGNC:0"}))
    old = time.time() - gsv.HGNC_CATALOGUE_TTL_SECONDS - 60
    import os
    os.utime(cache, (old, old))

    session = install(monkeypatch, RecordingSession())
    results, _ = GeneSymbolValidator().validate_gene_symbols(["MTOR"], reject_on_invalid=False)

    assert len(session.catalogue_calls) == 1
    assert results[0].result == ValidationResult.VALID


def test_corrupt_disk_cache_is_survivable(monkeypatch, tmp_path):
    (tmp_path / "catalogue.json").write_text("{not json")
    session = install(monkeypatch, RecordingSession())
    results, _ = GeneSymbolValidator().validate_gene_symbols(["MTOR"], reject_on_invalid=False)
    assert len(session.catalogue_calls) == 1
    assert results[0].result == ValidationResult.VALID


def test_truncated_catalogue_is_refused_and_falls_back(monkeypatch):
    """A catalogue missing rows would mark real genes INVALID. Refuse it."""
    truncated = FakeResponse(200, catalogue_payload(num_found=99999))
    session = install(monkeypatch, RecordingSession(catalogue_response=truncated))

    results, _ = GeneSymbolValidator().validate_gene_symbols(
        ["MTOR", "TRP53"], reject_on_invalid=False)

    assert len(session.per_symbol_calls) == 2, "must fall back, not use a partial catalogue"
    assert results[0].result == ValidationResult.VALID
    assert results[1].result == ValidationResult.INVALID


def test_catalogue_http_error_falls_back_to_per_symbol(monkeypatch):
    session = install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(403, None)))
    results, _ = GeneSymbolValidator().validate_gene_symbols(
        ["MTOR", "TRP53"], reject_on_invalid=False)
    assert len(session.per_symbol_calls) == 2
    assert [r.result for r in results] == [ValidationResult.VALID, ValidationResult.INVALID]


def test_fallback_paces_under_the_published_rate_limit(monkeypatch):
    """HGNC publish a 10 requests/second ceiling and say they may IP-block above
    it. The fallback path must not be able to exceed it."""
    slept = []
    monkeypatch.setattr(gsv.time, "sleep", lambda s: slept.append(s))
    install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(500, None)))

    GeneSymbolValidator().validate_gene_symbols(
        ["MTOR", "BEST1", "CRADD", "RCAN2"], reject_on_invalid=False)

    assert len(slept) >= 3, "every per-symbol request after the first must be paced"
    assert all(s <= gsv.HGNC_MIN_REQUEST_INTERVAL for s in slept)
    assert gsv.HGNC_MIN_REQUEST_INTERVAL >= 0.1, "0.1s between requests == 10 req/s"


def test_one_session_is_reused_rather_than_a_new_connection_per_symbol(monkeypatch):
    """The old code called requests.get at module level, so every symbol paid a
    fresh DNS + TCP + TLS handshake."""
    calls = []
    monkeypatch.setattr(gsv.requests, "get",
                        lambda *a, **k: calls.append(a) or FakeResponse(500, None))
    install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(500, None)))

    GeneSymbolValidator().validate_gene_symbols(["MTOR", "BEST1"], reject_on_invalid=False)

    assert calls == [], "requests.get bypasses the Session; use gsv._HGNC_SESSION"


# ---------------------------------------------------------------------------
# FIX 2 - a dropped gene must never be silent
# ---------------------------------------------------------------------------

def test_non_200_is_logged_and_counted(monkeypatch, caplog):
    install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(500, None),
                                          per_symbol=False))
    with caplog.at_level(logging.WARNING, logger=gsv.logger.name):
        results, _ = GeneSymbolValidator().validate_gene_symbols(
            ["MTOR", "BEST1"], reject_on_invalid=False)

    text = caplog.text
    assert "HTTP 503" in text
    assert "DROPPED" in text
    assert gsv._HGNC_STATUS_COUNTS == {503: 2}
    # The VERDICT is deliberately unchanged: unverifiable is still UNKNOWN.
    assert [r.result for r in results] == [ValidationResult.UNKNOWN, ValidationResult.UNKNOWN]


def test_summary_says_unverified_symbols_are_dropped(monkeypatch, caplog):
    install(monkeypatch, RecordingSession(catalogue_response=FakeResponse(500, None),
                                          per_symbol=False))
    with caplog.at_level(logging.WARNING, logger=gsv.logger.name):
        GeneSymbolValidator().validate_gene_symbols(["MTOR", "BEST1"], reject_on_invalid=False)

    summary = [r.message % r.args if r.args else r.message
               for r in caplog.records if "Could not verify" in r.getMessage()]
    assert summary, "the run must end with a line about the unverified symbols"
    line = summary[-1]
    assert "2/2" in line and "DROPPED" in line
    assert "503" in line, "the summary must carry the HTTP statuses responsible"


def test_a_200_that_cannot_be_read_is_also_reported(monkeypatch, caplog):
    class Unreadable(RecordingSession):
        def get(self, url, **kwargs):
            self.calls.append(url)
            if url == gsv.HGNC_CATALOGUE_URL:
                return FakeResponse(500, None)
            return FakeResponse(200, {"something": "unexpected"})

    install(monkeypatch, Unreadable())
    with caplog.at_level(logging.WARNING, logger=gsv.logger.name):
        results, _ = GeneSymbolValidator().validate_gene_symbols(["MTOR"], reject_on_invalid=False)

    assert "could not be interpreted" in caplog.text
    assert "DROPPED" in caplog.text
    assert results[0].result == ValidationResult.UNKNOWN


def test_nothing_is_reported_when_nothing_was_lost(monkeypatch, caplog):
    """A checker that always fires tells you nothing. This one must stay quiet
    when every symbol was answered."""
    install(monkeypatch, RecordingSession())
    with caplog.at_level(logging.WARNING, logger=gsv.logger.name):
        GeneSymbolValidator().validate_gene_symbols(list(CATALOGUE), reject_on_invalid=False)

    assert "DROPPED" not in caplog.text
    assert "Could not verify" not in caplog.text
