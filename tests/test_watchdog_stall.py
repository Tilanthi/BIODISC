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
"""Watchdog kill-rule regression tests (the 2.7-minute kill-death spiral).

Regression (2026-08-13..16, 1734 process starts, 0 completed cycles): the
watchdog killed a freshly restarted discovery process at the next 60 s check
because ``last_activity`` staleness (>30 min) predated the restart — and only
completion events (record_rejection / record_cycle) could refresh that
timestamp, none of which a killed process can reach. The rule now: a process
younger than WATCHDOG_GRACE is never killed, no matter how stale the status
file is, so a restart always gets a full shot at producing its first
heartbeat.
"""
import time

import discovery_watchdog


class _FakeProc:
    """Minimal psutil-like process stand-in."""

    def __init__(self, pid, age_s):
        self.pid = pid
        self._age = age_s
        self.terminated = False

    def create_time(self):
        return time.time() - self._age

    def terminate(self):
        self.terminated = True

    def is_running(self):
        return not self.terminated


def _setup(monkeypatch, proc, last_activity_age, last_discovery_age=None):
    monkeypatch.setattr(discovery_watchdog, "get_discovery_process", lambda: proc)
    status = {"last_activity": time.time() - last_activity_age}
    monkeypatch.setattr(discovery_watchdog.discovery_status, "read_status",
                        lambda: status)
    monkeypatch.setattr(discovery_watchdog.discovery_status, "is_user_active",
                        lambda: False)
    monkeypatch.setattr(discovery_watchdog.discovery_status,
                        "seconds_since_validated_discovery",
                        lambda: 669 * 3600)
    monkeypatch.setattr(discovery_watchdog, "get_last_discovery_time",
                        lambda: (time.time() - last_discovery_age
                                 if last_discovery_age is not None else None))
    started = []

    def _fake_start():
        started.append(1)
        return None

    monkeypatch.setattr(discovery_watchdog, "start_discovery_system", _fake_start)
    return started


def test_fresh_process_with_stale_status_is_not_killed(monkeypatch):
    """The exact death-spiral scenario: stale last_activity + just-restarted loop.

    Old behaviour: killed at the next 60 s check, before gene-symbol
    validation could finish. Expected: grace wins, process survives.
    """
    proc = _FakeProc(pid=55532, age_s=60)               # started 1 min ago
    started = _setup(monkeypatch, proc, last_activity_age=3600)  # status 1 h stale
    discovery_watchdog.check_and_restart()
    assert not proc.terminated
    assert started == []  # ...and no spurious duplicate start


def test_old_process_with_stale_status_is_killed(monkeypatch):
    """True-hang recovery still works: old process, idle past the threshold."""
    proc = _FakeProc(pid=1, age_s=2 * 3600)             # up for 2 h
    started = _setup(monkeypatch, proc, last_activity_age=3600)  # idle 1 h > 30 min
    discovery_watchdog.check_and_restart()
    assert proc.terminated
    assert started == [1]  # kill is always followed by a restart


def test_old_process_with_fresh_status_is_not_killed(monkeypatch):
    """A busy old process (heartbeating) is never touched."""
    proc = _FakeProc(pid=1, age_s=2 * 3600)
    started = _setup(monkeypatch, proc, last_activity_age=30)  # active 30 s ago
    discovery_watchdog.check_and_restart()
    assert not proc.terminated
    assert started == []


def test_user_active_threshold_still_tolerant(monkeypatch):
    """While the user is active the loop yields; 1 h idle must not be punished."""
    proc = _FakeProc(pid=1, age_s=2 * 3600)
    started = _setup(monkeypatch, proc, last_activity_age=3600)
    monkeypatch.setattr(discovery_watchdog.discovery_status, "is_user_active",
                        lambda: True)
    discovery_watchdog.check_and_restart()
    assert not proc.terminated
    assert started == []


def test_grace_is_at_least_a_full_first_cycle_budget():
    """The grace must comfortably exceed process boot + first dataset attempt."""
    assert discovery_watchdog.WATCHDOG_GRACE >= 10 * 60
