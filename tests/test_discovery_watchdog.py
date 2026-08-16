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
"""Tests for the discovery watchdog's hang decision, and for the liveness
signal the loop uses to prove it is working rather than stuck.

The property under test is a pair, and both halves have to hold at once:

  A. a cycle that spends longer than the stall threshold doing legitimate work
     is NOT killed;
  B. a cycle that is genuinely producing nothing IS still killed.

Every "not killed" test below is paired with a "still killed" test, because a
fix that only satisfies A is indistinguishable from switching the watchdog off.

Background: the watchdog restarts the loop only once the activity clock is
already stale, so the replacement process was born stale and was killed on the
next 60 s tick — about 30 s into STEP 2.5's ~1,750 sequential HGNC lookups.
Measured over the three rotated fixed_discovery.log files committed in this
repo: 1,734 process starts, 0 completed cycles, median process lifetime 49 s.

No test here touches the network.
"""
import json
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import discovery_watchdog as wd  # noqa: E402
from biodisc_core.fixed_pipeline import discovery_status  # noqa: E402
from biodisc_core.fixed_pipeline import gene_symbol_validation as gsv  # noqa: E402
from biodisc_core.fixed_pipeline.gene_symbol_validation import (  # noqa: E402
    GeneSymbolValidation,
    GeneSymbolValidator,
    ValidationResult,
)

HOUR = 3600.0
THRESHOLD = wd.STALL_THRESHOLD  # 30 min


@pytest.fixture
def status_file(tmp_path, monkeypatch):
    """Point the status store at a temp file, isolated from the real one.

    conftest already redirects BIODISC_DISCOVERY_STATUS for every test; this
    fixture names the path so a test can read it back, and resets the heartbeat
    throttle so tests do not inherit each other's timing."""
    f = tmp_path / "discovery_status.json"
    monkeypatch.setenv("BIODISC_DISCOVERY_STATUS", str(f))
    monkeypatch.setattr(discovery_status, "_last_progress_write", 0.0, raising=False)
    return f


def _write_status(path: Path, **kw):
    path.write_text(json.dumps(kw))


class _FakeProc:
    """Stands in for a psutil.Process for the discovery loop."""

    def __init__(self, start_time):
        self.pid = 4242
        self._start = start_time
        self.terminated = False
        self.killed = False

    def create_time(self):
        return self._start

    def terminate(self):
        self.terminated = True

    def is_running(self):
        return not self.killed

    def kill(self):
        self.killed = True


# ---------------------------------------------------------------------------
# _loop_looks_hung: the decision itself
# ---------------------------------------------------------------------------

def test_freshly_started_loop_is_not_judged_by_its_predecessors_silence(status_file):
    """A. The livelock. The activity clock is an hour stale — it was stale when
    the watchdog did the restarting — but the process running now is 30 s old
    and has not yet had a chance to record anything."""
    _write_status(status_file, last_activity=time.time() - HOUR)
    assert wd._loop_looks_hung(THRESHOLD, proc_start=time.time() - 30) is False


def test_long_running_legitimate_work_is_not_killed(status_file):
    """A. A process 25 min into STEP 2.5 that has heartbeated 10 s ago is
    working, not hung."""
    _write_status(status_file, last_activity=time.time() - 10)
    assert wd._loop_looks_hung(THRESHOLD, proc_start=time.time() - 25 * 60) is False


def test_loop_that_reports_nothing_for_a_full_threshold_is_still_hung(status_file):
    """B. The other half. Old process, no activity of its own: still hung."""
    _write_status(status_file, last_activity=time.time() - HOUR)
    assert wd._loop_looks_hung(THRESHOLD, proc_start=time.time() - 2 * HOUR) is True


def test_process_that_never_recorded_anything_is_still_hung(status_file):
    """B. No status file at all + an old process is a hang, not a fresh start."""
    assert not status_file.exists()
    assert wd._loop_looks_hung(THRESHOLD, proc_start=time.time() - 2 * HOUR) is True


def test_no_process_start_time_falls_back_to_the_old_behaviour(status_file):
    """If psutil cannot give us a start time we must not silently stop
    supervising: with proc_start=None the check is exactly as before."""
    _write_status(status_file, last_activity=time.time() - HOUR)
    assert wd._loop_looks_hung(THRESHOLD, proc_start=None) is True
    _write_status(status_file, last_activity=time.time() - 5)
    assert wd._loop_looks_hung(THRESHOLD, proc_start=None) is False


# ---------------------------------------------------------------------------
# check_and_restart: the decision as the watchdog actually reaches it
# ---------------------------------------------------------------------------

def test_check_and_restart_does_not_kill_a_young_process(status_file, monkeypatch):
    """A, end to end. This is the exact configuration that produced 1,734
    restarts and 0 completed cycles."""
    proc = _FakeProc(time.time() - 45)  # median observed lifetime was 49 s
    _write_status(status_file, last_activity=time.time() - 664 * HOUR)
    started = []
    monkeypatch.setattr(wd, "get_discovery_process", lambda: proc)
    monkeypatch.setattr(wd, "start_discovery_system", lambda: started.append(1))
    monkeypatch.setattr(wd, "_LAST_CHECK_TIME", time.time() - wd.CHECK_INTERVAL)
    monkeypatch.setattr(discovery_status, "is_user_active", lambda *a, **k: False)

    wd.check_and_restart()

    assert proc.terminated is False, "young process was killed - the livelock is back"
    assert started == []


def test_check_and_restart_still_kills_a_genuinely_stuck_process(status_file, monkeypatch):
    """B, end to end. Same silence, but the process has had two full hours of
    it. It must be restarted."""
    proc = _FakeProc(time.time() - 2 * HOUR)
    _write_status(status_file, last_activity=time.time() - 664 * HOUR)
    started = []
    monkeypatch.setattr(wd, "get_discovery_process", lambda: proc)
    monkeypatch.setattr(wd, "start_discovery_system", lambda: started.append(1))
    monkeypatch.setattr(wd, "_LAST_CHECK_TIME", time.time() - wd.CHECK_INTERVAL)
    monkeypatch.setattr(discovery_status, "is_user_active", lambda *a, **k: False)
    monkeypatch.setattr(wd.time, "sleep", lambda *_: None)

    wd.check_and_restart()

    assert proc.terminated is True, "a genuinely stuck loop was left running"
    assert started == [1]


# ---------------------------------------------------------------------------
# progress_heartbeat: the liveness signal
# ---------------------------------------------------------------------------

def test_progress_heartbeat_refreshes_last_activity(status_file):
    _write_status(status_file, last_activity=time.time() - HOUR)
    assert discovery_status.progress_heartbeat(min_interval=0) is True
    assert discovery_status.seconds_since_activity() < 5


def test_progress_heartbeat_is_throttled(status_file):
    assert discovery_status.progress_heartbeat(min_interval=0) is True
    for _ in range(500):
        assert discovery_status.progress_heartbeat() is False  # one write per 30 s


def test_progress_heartbeat_never_raises(monkeypatch, status_file):
    """Liveness reporting must not be able to abort a discovery cycle."""
    monkeypatch.setattr(discovery_status, "_write",
                        lambda *_: (_ for _ in ()).throw(OSError("disk full")))
    assert discovery_status.progress_heartbeat(min_interval=0) is False


def test_status_write_is_atomic(status_file):
    """The watchdog reads this file from another process while the loop writes
    it. A torn read parses as {} and looks exactly like 'no activity ever'."""
    discovery_status.record_rejection("test_reason")
    leftovers = list(status_file.parent.glob("discovery_status.json.tmp*"))
    assert leftovers == []
    assert json.loads(status_file.read_text())["rejections"]["test_reason"] == 1


# ---------------------------------------------------------------------------
# The long operation reports progress from the inside
# ---------------------------------------------------------------------------

def test_gene_symbol_validation_keeps_the_activity_clock_fresh(
        status_file, tmp_path, monkeypatch):
    """A, at the source. This is the operation that was being killed: it makes
    one network call per unknown symbol and, before this change, wrote nothing
    to the status store until it was finished.

    No network: _query_hgnc is replaced by a local stub.
    """
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(tmp_path / "hgnc.json"))
    _write_status(status_file, last_activity=time.time() - HOUR)
    monkeypatch.setattr(discovery_status, "_last_progress_write", 0.0, raising=False)

    validator = GeneSymbolValidator()
    monkeypatch.setattr(validator, "_query_hgnc", lambda symbol, timeout=10:
                        GeneSymbolValidation(symbol=symbol,
                                             result=ValidationResult.VALID,
                                             source="HGNC_API", gene_id="HGNC:1"))

    started_at = time.time()
    validator.validate_gene_symbols(
        [f"FAKEGENEX{i}" for i in range(200)], reject_on_invalid=False)

    last_activity = discovery_status.read_status().get("last_activity")
    assert last_activity is not None
    assert last_activity >= started_at, (
        "validation ran without reporting progress - the watchdog will read this "
        "as a hang and kill it, which is the bug")


def test_heartbeat_does_not_fire_when_no_work_is_done(status_file, tmp_path, monkeypatch):
    """B, at the source. The heartbeat is driven by completed units of work, not
    by the clock, so an operation that processes nothing reports nothing and
    stays killable."""
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(tmp_path / "hgnc.json"))
    stale = time.time() - HOUR
    _write_status(status_file, last_activity=stale)
    monkeypatch.setattr(discovery_status, "_last_progress_write", 0.0, raising=False)

    GeneSymbolValidator().validate_gene_symbols([], reject_on_invalid=False)

    assert discovery_status.read_status()["last_activity"] == stale
    assert wd._loop_looks_hung(THRESHOLD, proc_start=time.time() - 2 * HOUR) is True


# ---------------------------------------------------------------------------
# HGNC verdict cache — the reason the operation is slow enough to matter
# ---------------------------------------------------------------------------

def test_hgnc_verdicts_survive_a_restart(tmp_path, monkeypatch, status_file):
    """Every restart re-walked ~1,750 symbols from cold against
    rest.genenames.org. Cache what the API said, not what the heuristics said."""
    cache = tmp_path / "hgnc.json"
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(cache))

    calls = []

    def fake_query(symbol, timeout=10):
        calls.append(symbol)
        return GeneSymbolValidation(symbol=symbol, result=ValidationResult.VALID,
                                    source="HGNC_API", gene_id="HGNC:99",
                                    gene_name="fake")

    v1 = GeneSymbolValidator()
    monkeypatch.setattr(v1, "_query_hgnc", fake_query)
    v1.validate_gene_symbols(["FAKEGENEX1", "FAKEGENEX2"], reject_on_invalid=False)
    assert len(calls) == 2
    assert cache.exists()

    # A brand-new validator == a restarted process.
    v2 = GeneSymbolValidator()
    monkeypatch.setattr(v2, "_query_hgnc", fake_query)
    results, _ = v2.validate_gene_symbols(["FAKEGENEX1", "FAKEGENEX2"],
                                          reject_on_invalid=False)
    assert len(calls) == 2, "restarted process went back to the network"
    assert [r.source for r in results] == ["HGNC_DISK_CACHE"] * 2
    assert all(r.result == ValidationResult.VALID for r in results)


def test_hgnc_cache_never_overrides_a_local_rule(tmp_path, monkeypatch, status_file):
    """The cache sits where the network call was: after the curated list, the
    probe-ID rules and the fake-pattern rules. A poisoned or stale cache entry
    must not be able to promote a probe ID to a valid gene."""
    cache = tmp_path / "hgnc.json"
    cache.write_text(json.dumps({
        "version": gsv._HGNC_CACHE_VERSION,
        "entries": {"1553367_a_at": {"r": "valid", "t": time.time()},
                    "ACTB": {"r": "invalid", "t": time.time()}},
    }))
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(cache))

    v = GeneSymbolValidator()
    monkeypatch.setattr(v, "_query_hgnc", lambda *a, **k: pytest.fail(
        "should not have reached the network"))

    probe = v._validate_single_symbol("1553367_a_at")
    assert probe.result == ValidationResult.INVALID
    assert probe.source == "AFFYMETRIX_PROBE"

    known = v._validate_single_symbol("ACTB")
    assert known.result == ValidationResult.VALID
    assert known.source == "KNOWN_LIST"


def test_hgnc_cache_entries_expire(tmp_path, monkeypatch, status_file):
    cache = tmp_path / "hgnc.json"
    cache.write_text(json.dumps({
        "version": gsv._HGNC_CACHE_VERSION,
        "entries": {"FAKEGENEX1": {"r": "valid",
                                   "t": time.time() - gsv.HGNC_CACHE_TTL_SECONDS - 1}},
    }))
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(cache))
    assert GeneSymbolValidator()._hgnc_disk_cache_lookup("FAKEGENEX1") is None


def test_unknown_is_never_cached(tmp_path, monkeypatch, status_file):
    """UNKNOWN means the database was unreachable. That is a fact about the
    network and must never be stored as a verdict about a gene."""
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(tmp_path / "hgnc.json"))
    v = GeneSymbolValidator()
    v._hgnc_disk_cache_store("FAKEGENEX1", ValidationResult.UNKNOWN)
    assert v._hgnc_disk_cache == {}
    assert v._save_hgnc_disk_cache() is False


def test_corrupt_cache_file_starts_cold_instead_of_failing(tmp_path, monkeypatch, status_file):
    cache = tmp_path / "hgnc.json"
    cache.write_text("{not json")
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(cache))
    assert GeneSymbolValidator()._hgnc_disk_cache == {}
