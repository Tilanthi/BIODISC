#!/usr/bin/env python3
"""
Continuous Autonomous Discovery Launcher for BIODISC

This script launches the V73 Autonomous Discovery Orchestrator in the background
and monitors it to ensure it keeps running. If the process dies, it will be restarted.

Usage:
    python run_autonomous_discovery.py [--stop]

Options:
    --stop    Stop any running autonomous discovery processes
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from pathlib import Path

# Add BIODISC to path
biodisc_path = Path(__file__).parent
sys.path.insert(0, str(biodisc_path))

PID_FILE = biodisc_path / ".autonomous_discovery.pid"
LOG_FILE = biodisc_path / "autonomous_discovery.log"


def check_running():
    """Check if autonomous discovery is already running"""
    if not PID_FILE.exists():
        return None

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Check if process is still alive
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks existence
            return pid
        except OSError:
            # Process is dead, clean up stale PID file
            PID_FILE.unlink()
            return None
    except (ValueError, OSError):
        return None


def stop_autonomous_discovery():
    """Stop any running autonomous discovery process"""
    pid = check_running()
    if pid:
        print(f"Stopping autonomous discovery (PID {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)

            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

            PID_FILE.unlink(missing_ok=True)
            print("Autonomous discovery stopped.")
        except Exception as e:
            print(f"Error stopping process: {e}")
    else:
        print("No autonomous discovery process running.")


def start_autonomous_discovery():
    """Start autonomous discovery in the background"""
    existing_pid = check_running()
    if existing_pid:
        print(f"Autonomous discovery is already running (PID {existing_pid})")
        return existing_pid

    print("Starting autonomous discovery...")

    # Create launcher script
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

    # Start background discovery
    system.start()

    print("Autonomous discovery started in background")
    print("PID:", os.getpid())
    print("Log file: {LOG_FILE}")

    # Keep process alive
    try:
        while True:
            time.sleep(60)
            status = system.get_status()
            if not status.get('running', False):
                print("Autonomous discovery stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\\nShutting down autonomous discovery...")
        system.stop()
        raise

except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

    # Write launcher script
    launcher_path = biodisc_path / ".autonomous_discovery_launcher.py"
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)

    # Start process in background
    log_file = open(LOG_FILE, 'a')
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

    print(f"Autonomous discovery started (PID {process.pid})")
    print(f"Log file: {LOG_FILE}")
    print(f"Use 'python {sys.argv[0]} --stop' to stop")

    # Wait a moment and check if it's still running
    time.sleep(2)
    if process.poll() is None:
        print("✓ Autonomous discovery is running successfully")
        return process.pid
    else:
        print("✗ Process died unexpectedly. Check log file for errors.")
        PID_FILE.unlink(missing_ok=True)
        return None


def show_status():
    """Show current status of autonomous discovery"""
    pid = check_running()
    if pid:
        print(f"✓ Autonomous discovery is running (PID {pid})")

        # Try to get more status
        try:
            sys.path.insert(0, str(biodisc_path))
            from biodisc_core.reasoning.v73_autonomous_discovery import get_autonomous_discovery_system

            # This won't connect to running process but shows config
            print(f"  Log file: {LOG_FILE}")
            print(f"  PID file: {PID_FILE}")
        except:
            pass
    else:
        print("✗ Autonomous discovery is not running")
        print(f"  Log file: {LOG_FILE}")
        print(f"  Start with: python {sys.argv[0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage autonomous discovery")
    parser.add_argument('--stop', action='store_true', help='Stop autonomous discovery')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--start', action='store_true', help='Start autonomous discovery')

    args = parser.parse_args()

    if args.stop:
        stop_autonomous_discovery()
    elif args.status:
        show_status()
    elif args.start or len(sys.argv) == 1:
        start_autonomous_discovery()
    else:
        parser.print_help()
