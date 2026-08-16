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
"""Autonomous-discovery runtime status + heartbeat (Phase B supervision).

A small, dependency-free store the discovery loop writes and the watchdog reads,
so the loop can't silently starve. Records: last cycle, last VALIDATED
discovery, a rejection breakdown, and a heartbeat the assistant touches to signal
"the user is active — yield."

Heartbeat model: the loop runs by default (filling idle time). It yields only
when the heartbeat is fresh (a user task is in progress). The assistant touches
the heartbeat via a Claude Code hook (see plan); without that hook the loop runs
continuously — the safe default.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_FILE = PROJECT_ROOT / "discovery_status.json"
HEARTBEAT_FILE = Path.home() / ".biodisc" / "user_heartbeat"
USER_ACTIVE_WINDOW = 300.0  # seconds — heartbeat fresher than this means user active

# Progress heartbeat: how often a long-running operation may refresh
# ``last_activity``. The loop calls progress_heartbeat() from inside operations
# that take longer than the watchdog's stall threshold (STEP 2.5 gene-symbol
# validation is ~1,750 sequential HGNC lookups); writing the status file on
# every symbol would be thousands of writes per cycle, so writes are throttled
# to one per this many seconds. See progress_heartbeat() for why this does NOT
# weaken hang detection.
HEARTBEAT_MIN_INTERVAL = 30.0
_last_progress_write = 0.0


def _status_path() -> Path:
    """The status file to use, honouring BIODISC_DISCOVERY_STATUS.

    Same escape hatch as BIODISC_VERDICT_LOG: the test suite must be able to
    exercise the loop without overwriting the production runtime state. Read at
    call time, not import time, so a fixture can set it.
    """
    override = os.environ.get("BIODISC_DISCOVERY_STATUS")
    return Path(override) if override else STATUS_FILE


def _read() -> dict:
    path = _status_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def _write(d: dict) -> None:
    """Write the status file atomically.

    The watchdog polls this file from another process while the loop writes it.
    A plain write_text() is not atomic, so a reader could observe a truncated
    file, fail to parse it, and conclude the loop had no recorded activity —
    i.e. exactly the false "hung" verdict this module exists to prevent.
    Write to a temp file in the same directory and os.replace() it, which is
    atomic on POSIX.
    """
    path = _status_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    try:
        tmp.write_text(json.dumps(d, indent=2))
        os.replace(tmp, path)
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def record_cycle(n_discoveries: int) -> None:
    d = _read()
    now = time.time()
    d["last_cycle_time"] = now
    d["last_cycle_iso"] = datetime.fromtimestamp(now).isoformat()
    d["last_cycle_discoveries"] = n_discoveries
    d["last_activity"] = now
    _write(d)


def record_validated_discovery(discovery_id: str = "") -> None:
    d = _read()
    now = time.time()
    d["last_validated_discovery_time"] = now
    d["last_validated_discovery_iso"] = datetime.fromtimestamp(now).isoformat()
    d["validated_count"] = d.get("validated_count", 0) + 1
    d["last_validated_discovery_id"] = discovery_id
    d["last_activity"] = now
    _write(d)


def record_rejection(reason: str) -> None:
    d = _read()
    breakdown = d.get("rejections", {})
    breakdown[reason] = breakdown.get(reason, 0) + 1
    d["rejections"] = breakdown
    d["last_activity"] = time.time()
    _write(d)


def progress_heartbeat(min_interval: float = None) -> bool:
    """Record that the loop is alive AND advancing. Returns True if written.

    Call this from inside operations that legitimately run longer than the
    watchdog's stall threshold, once per unit of work completed (e.g. once per
    validated gene symbol). Writes are throttled to one per ``min_interval``
    seconds, so calling it thousands of times per cycle costs one file write
    per 30 s.

    Why this does not weaken hang detection
    ---------------------------------------
    This is deliberately NOT a background ticker. It advances only when the
    caller completes a unit of work, so a process blocked in a syscall, spinning
    on a dead socket, or deadlocked emits nothing and still goes stale — the
    watchdog still kills it. What it fixes is the opposite error: a loop doing
    exactly the work it was told to do, silently, being killed for the silence.

    Never raises: a status-file problem must not abort a discovery cycle.
    """
    global _last_progress_write
    interval = HEARTBEAT_MIN_INTERVAL if min_interval is None else min_interval
    now = time.time()
    if (now - _last_progress_write) < interval:
        return False
    # Set before writing so a persistently failing write cannot turn into a
    # hot loop of failing writes.
    _last_progress_write = now
    try:
        d = _read()
        d["last_activity"] = now
        d["last_progress_iso"] = datetime.fromtimestamp(now).isoformat()
        _write(d)
        return True
    except Exception:
        return False


def read_status() -> dict:
    return _read()


def touch_heartbeat() -> None:
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_FILE.touch()


def is_user_active(window: float = USER_ACTIVE_WINDOW) -> bool:
    """True if the assistant signalled user activity within ``window`` seconds."""
    try:
        if not HEARTBEAT_FILE.exists():
            return False
        return (time.time() - HEARTBEAT_FILE.stat().st_mtime) < window
    except Exception:
        return False


def seconds_since_validated_discovery():
    """Seconds since the last validated discovery, or None if never."""
    t = _read().get("last_validated_discovery_time")
    return None if t is None else time.time() - t


def seconds_since_activity():
    """Seconds since the loop last recorded ANY activity, or None if never.

    "Activity" is a completed cycle, a recorded rejection, a validated
    discovery, or a progress heartbeat from inside a long operation. This is
    the quantity the watchdog actually acts on, so it is the one its log line
    should quote.
    """
    t = _read().get("last_activity")
    return None if t is None else time.time() - t
