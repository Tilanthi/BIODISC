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
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_FILE = PROJECT_ROOT / "discovery_status.json"
HEARTBEAT_FILE = Path.home() / ".biodisc" / "user_heartbeat"
USER_ACTIVE_WINDOW = 300.0  # seconds — heartbeat fresher than this means user active


def _read() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception:
            return {}
    return {}


def _write(d: dict) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(d, indent=2))


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
