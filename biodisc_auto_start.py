#!/usr/bin/env python3
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
"""
Auto-start Autonomous Discovery for BIODISC.

Ensures the CANONICAL always-on discovery path is running:
    discovery_watchdog.py -> .fixed_autonomous_discovery.py
(the fixed real-data pipeline, whose every write passes the machine-verification
chokepoint). Can be imported and called at session start.

Usage:
    from biodisc_auto_start import ensure_autonomous_discovery
    ensure_autonomous_discovery()  # Starts the watchdog if not already running

HISTORY: this module previously generated and launched the legacy V73 loop
(`.autonomous_discovery_auto.py`), which wrote to autonomous_discoveries.jsonl
directly, bypassing the verification chokepoint. That legacy loop is retired
(ASTRA §11: never run a legacy loop alongside the new one). This module now
delegates to the single canonical watchdog.
"""
import os
import sys
from pathlib import Path

# Add BIODISC to path
biodisc_path = Path(__file__).resolve().parent
sys.path.insert(0, str(biodisc_path))

PID_FILE = biodisc_path / ".autonomous_discovery.pid"
WATCHDOG = biodisc_path / "discovery_watchdog.py"


def _process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def ensure_autonomous_discovery():
    """Start the canonical discovery watchdog if it is not already running.

    The watchdog itself guards against duplicate discovery processes, so calling
    this when discovery is already running is a safe no-op. Returns True if a
    watchdog process is running after the call.
    """
    # If a PID file references a live process, assume discovery is already supervised.
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            if _process_alive(pid):
                print(f"✓ Autonomous discovery already running (PID {pid})")
                return True
            PID_FILE.unlink(missing_ok=True)
        except (OSError, ValueError):
            PID_FILE.unlink(missing_ok=True)

    if not WATCHDOG.exists():
        print(f"✗ Canonical watchdog not found: {WATCHDOG}")
        return False

    try:
        import subprocess
        log_dir = biodisc_path / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = open(log_dir / "discovery_watchdog.log", 'a')
        process = subprocess.Popen(
            [sys.executable, str(WATCHDOG)],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=str(biodisc_path),
        )

        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))

        import time
        time.sleep(2)

        if process.poll() is None:
            print(f"✓ Canonical discovery watchdog started (PID {process.pid})")
            print("  -> .fixed_autonomous_discovery.py (writes verified through the chokepoint)")
            return True
        else:
            print("✗ Failed to start discovery watchdog")
            PID_FILE.unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"Error starting autonomous discovery: {e}")
        return False


def stop_autonomous_discovery():
    """Stop the supervised discovery process referenced by the PID file."""
    if PID_FILE.exists():
        try:
            import signal
            import time
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            PID_FILE.unlink(missing_ok=True)
            print("✓ Autonomous discovery stopped")
            return True
        except Exception as e:
            print(f"Error stopping: {e}")
            return False
    else:
        return False


def get_autonomous_discovery_status():
    """Get status of the supervised discovery process."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            if _process_alive(pid):
                return {"running": True, "pid": pid}
            PID_FILE.unlink(missing_ok=True)
        except (OSError, ValueError):
            PID_FILE.unlink(missing_ok=True)
    return {"running": False, "pid": None}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--stop', action='store_true', help='Stop autonomous discovery')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()

    if args.stop:
        stop_autonomous_discovery()
    elif args.status:
        status = get_autonomous_discovery_status()
        if status["running"]:
            print(f"✓ Running (PID {status['pid']})")
        else:
            print("✗ Not running")
    else:
        ensure_autonomous_discovery()
