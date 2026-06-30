#!/usr/bin/env python3
"""
Auto-start Autonomous Discovery for BIODISC

This module ensures that autonomous discovery is always running when BIODISC is active.
It can be imported and called at session start.

Usage:
    from biodisc_auto_start import ensure_autonomous_discovery

    ensure_autonomous_discovery()  # Starts if not running
"""

import os
import sys
from pathlib import Path

# Add BIODISC to path
biodisc_path = Path(__file__).parent
sys.path.insert(0, str(biodisc_path))

PID_FILE = biodisc_path / ".autonomous_discovery.pid"


def ensure_autonomous_discovery():
    """
    Ensure autonomous discovery is running.

    This function checks if autonomous discovery is already running,
    and starts it if not. Safe to call multiple times.

    Returns:
        bool: True if autonomous discovery is running, False otherwise
    """
    # Check if already running
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is still alive
            os.kill(pid, 0)
            print(f"✓ Autonomous discovery already running (PID {pid})")
            return True
        except (OSError, ValueError):
            # Process is dead or PID file is invalid
            PID_FILE.unlink(missing_ok=True)

    # Not running, start it
    try:
        import subprocess

        launcher_script = f"""
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, '{biodisc_path}')

try:
    from biodisc_core.reasoning.v73_autonomous_discovery import get_autonomous_discovery_system, AutonomousDiscoveryConfig

    config = AutonomousDiscoveryConfig(
        max_cpu_percent=15.0,
        max_hours_per_week=168.0,  # 24x7 - run continuously when computer is on
        idle_timeout_minutes=1,  # Reduced from 2 for faster discovery
        min_confidence_to_store=0.65,  # 65% confidence - appropriate for bioscience
        min_evidence_count=1,  # 1 evidence source - more flexible for bioscience
        bioscience_mode=True,  # Enable bioscience-aware validation
        questions_per_cycle=10,  # Increased from 3 for faster discovery
        cycle_interval_seconds=2,  # Reduced for faster discovery cycles
        log_all_discoveries=True,
        discovery_log_path=str('{biodisc_path / "autonomous_discoveries.jsonl"}')
    )

    system = get_autonomous_discovery_system(config)
    system.start()

    print("✓ Autonomous discovery started in background")

    # Keep process alive
    try:
        while True:
            time.sleep(60)
            status = system.get_status()
            if not status.get('running', False):
                break
    except KeyboardInterrupt:
        system.stop()
        raise

except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""

        launcher_path = biodisc_path / ".autonomous_discovery_auto.py"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)

        # Start in background
        log_file = open(biodisc_path / "autonomous_discovery.log", 'a')
        process = subprocess.Popen(
            [sys.executable, str(launcher_path)],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=str(biodisc_path)
        )

        # Save PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))

        # Wait a moment to verify it started successfully
        import time
        time.sleep(2)

        if process.poll() is None:
            print(f"✓ Autonomous discovery started (PID {process.pid})")
            print("  Running continuously in background...")
            print("  Discoveries will be automatically stored to memory palace")
            return True
        else:
            print("✗ Failed to start autonomous discovery")
            PID_FILE.unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"Error starting autonomous discovery: {e}")
        return False


def stop_autonomous_discovery():
    """Stop autonomous discovery if running"""
    if PID_FILE.exists():
        try:
            import signal
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)
            import time
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
    """Get status of autonomous discovery"""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if alive
            return {"running": True, "pid": pid}
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
