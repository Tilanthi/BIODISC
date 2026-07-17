#!/usr/bin/env python3
"""
BIODISC Discovery Watchdog - Auto-Restart System

This watchdog ensures that the autonomous discovery system is ALWAYS running.
It automatically restarts the discovery system if:
- Process is not running
- Last discovery is too old (>15 minutes indicates system stopped)
- Computer woke from sleep
- Process crashed/stopped

This implements the ALWAYS RUNNING requirement from CLAUDE.md.
"""

import os
import sys
import time
import subprocess
import psutil
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timedelta

# Make biodisc_core importable so we can read the shared discovery status.
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from biodisc_core.fixed_pipeline import discovery_status

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_dir / "discovery_watchdog.log", maxBytes=10_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Discovery system configuration
DISCOVERY_SCRIPT = Path(__file__).parent / ".fixed_autonomous_discovery.py"
DISCOVERY_PROCESS_NAME = "fixed_autonomous_discovery.py"
MAX_IDLE_TIME = 900  # legacy fallback (discoveries-file timestamp), minutes->seconds
CHECK_INTERVAL = 60   # Check every minute
# Phase B: stall = no validated discovery AND no recent loop activity for this long.
# A healthy loop is active every few minutes; 30 min of silence means it is hung
# (the recurring blocking-IO stall). The watchdog escalates SIGTERM->SIGKILL, so
# this recovers a hung loop within ~30 min instead of the old 6 h. Downloads are
# also hard-bounded (geo_data_downloader._read_stream_bounded), so genuine hangs
# are now rare AND promptly recovered.
STALL_THRESHOLD = 30 * 60               # 30 minutes
STALL_THRESHOLD_USER_ACTIVE = 3 * 3600  # 3 hours (was 24 h) — still tolerant while active
_LAST_CHECK_TIME = time.time()  # for watchdog sleep/wake detection


def get_discovery_process():
    """Find the autonomous discovery process"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                # Check if this is our discovery process
                cmdline = proc.info['cmdline']
                if cmdline and any(DISCOVERY_PROCESS_NAME in str(cmd) for cmd in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    except Exception as e:
        logger.error(f"Error finding discovery process: {e}")
        return None


def get_last_discovery_time():
    """Get timestamp of last discovery made"""
    try:
        discovery_file = Path(__file__).parent / "autonomous_discoveries.jsonl"
        if not discovery_file.exists():
            return None

        # Get last line from file
        with open(discovery_file, 'r') as f:
            lines = f.readlines()
            if lines:
                import json
                last_discovery = json.loads(lines[-1])
                return last_discovery.get('timestamp', None)
        return None
    except Exception as e:
        logger.error(f"Error reading last discovery time: {e}")
        return None


def start_discovery_system():
    """Start the autonomous discovery system (single-process guarded)."""
    try:
        # Guard: never start a second discovery process.
        existing = get_discovery_process()
        if existing:
            logger.info(f"ℹ️  Discovery system already running (PID {existing.pid}) - not starting a duplicate")
            return existing

        logger.info("🚀 Starting autonomous discovery system...")
        process = subprocess.Popen(
            [sys.executable, str(DISCOVERY_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        logger.info(f"✅ Discovery system started (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"❌ Failed to start discovery system: {e}")
        return None


def _loop_looks_hung(threshold: float) -> bool:
    """True if the loop has had no recent activity (status or discoveries file)."""
    s = discovery_status.read_status()
    last_activity = s.get("last_activity")
    if last_activity and (time.time() - last_activity) < threshold:
        return False
    ldt = get_last_discovery_time()
    if ldt and (time.time() - ldt) < threshold:
        return False
    return True


def check_and_restart():
    """Check if discovery system needs restart; restart only on true hang."""
    global _LAST_CHECK_TIME

    # Watchdog sleep/wake: if we slept a long time, don't thrash this round.
    gap = time.time() - _LAST_CHECK_TIME
    _LAST_CHECK_TIME = time.time()
    if gap > CHECK_INTERVAL * 10:
        logger.warning(f"😴 Watchdog gap {gap/60:.1f} min (system sleep?) - skipping restart check this round")
        return None

    discovery_proc = get_discovery_process()
    if not discovery_proc:
        logger.warning("❌ Discovery process not running - starting...")
        return start_discovery_system()

    # Yield: while the user is active the loop intentionally pauses; don't penalize it.
    if discovery_status.is_user_active():
        threshold = STALL_THRESHOLD_USER_ACTIVE
    else:
        threshold = STALL_THRESHOLD

    if _loop_looks_hung(threshold):
        since = discovery_status.seconds_since_validated_discovery()
        if since is None:
            logger.warning(f"⚠️  No validated discovery ever recorded and loop idle "
                           f">{threshold/3600:.0f}h - restarting hung loop")
        else:
            logger.warning(f"⚠️  No validated discovery for {since/3600:.1f}h and loop idle "
                           f"- restarting hung loop")
        try:
            discovery_proc.terminate()
            time.sleep(5)
            if discovery_proc.is_running():
                discovery_proc.kill()
        except Exception:
            pass
        return start_discovery_system()

    logger.debug("✅ Discovery system alive with recent activity")
    return None


# How many check intervals between metric refreshes (~hourly at CHECK_INTERVAL=60s).
METRICS_EVERY = 60


def run_metrics():
    """Refresh the RSI miner + capability index. Non-fatal: a failure here must
    never stop the watchdog from keeping discovery alive."""
    try:
        from biodisc_core.fixed_pipeline.rsi_miner import run as rsi_run
        from biodisc_core.fixed_pipeline.capability_index import run as ci_run
        rsi_run()
        ci_run()
        logger.info("📊 hourly metrics refreshed (RSI miner + capability index)")
    except Exception as e:  # noqa: BLE001
        logger.warning("metrics refresh failed (non-fatal): %s", e)


def main():
    """Main watchdog loop"""
    logger.info("🐕 BIODISC Discovery Watchdog Started")
    logger.info("=" * 60)
    logger.info("Ensuring autonomous discovery system is ALWAYS running")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    logger.info(f"Max idle time: {MAX_IDLE_TIME/60} minutes")
    logger.info("=" * 60)

    # Initial check and start if needed
    logger.info("🔍 Initial system check...")
    if not get_discovery_process():
        logger.info("📡 Discovery system not running - starting now...")
        start_discovery_system()

    # Main monitoring loop
    ticks = 0
    while True:
        try:
            check_and_restart()
            ticks += 1
            if ticks % METRICS_EVERY == 0:
                run_metrics()  # hourly: turn the RSI loop + refresh the capability index
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("🛑 Watchdog stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Watchdog error: {e}")
            time.sleep(CHECK_INTERVAL)  # Continue monitoring despite errors


if __name__ == "__main__":
    main()
