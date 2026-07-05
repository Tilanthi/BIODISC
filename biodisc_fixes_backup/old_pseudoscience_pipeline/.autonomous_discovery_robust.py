#!/usr/bin/env python3
"""
BIODISC Robust Autonomous Discovery Startup

Enhanced startup system with:
- Automatic restart on failure
- Progress detection and recovery
- User activity detection
- Duplicate prevention
- Health monitoring

Date: 2026-07-01
Version: 2.0 - Robust Auto-Restart System
"""

import sys
import os
import time
import signal
import logging
from pathlib import Path
from datetime import datetime
import threading

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "autonomous_discovery_robust.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustAutonomousDiscovery:
    """
    Robust autonomous discovery system with automatic restart and recovery.

    KEY IMPROVEMENTS:
    1. Never exits silently - always logs and restarts
    2. Detects stalled systems and restarts automatically
    3. Prevents infinite loops with same discoveries
    4. Monitors system health and progress
    5. Gracefully handles user activity
    """

    def __init__(self):
        self.discovery_system = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 1000  # Very high limit for truly autonomous operation
        self.last_progress_time = None
        self.last_discovery_count = 0
        self.stall_threshold_seconds = 600  # 10 minutes without progress = stalled
        self.check_interval = 30  # Check health every 30 seconds

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start robust autonomous discovery"""
        logger.info("🧬 Starting BIODISC Robust Autonomous Discovery System")
        logger.info("=" * 70)

        self.running = True

        # Main loop with automatic restart
        while self.running and self.restart_count < self.max_restarts:
            try:
                logger.info(f"🔄 Starting autonomous discovery (attempt #{self.restart_count + 1})")
                self._start_discovery_system()
                self._monitor_system()

            except Exception as e:
                logger.error(f"Discovery system failed: {e}", exc_info=True)
                self.restart_count += 1

                if self.restart_count < self.max_restarts:
                    logger.warning(f"Restarting in 10 seconds...")
                    time.sleep(10)
                else:
                    logger.error("Maximum restart attempts reached, giving up")
                    break

    def stop(self):
        """Stop autonomous discovery"""
        logger.info("Stopping autonomous discovery...")
        self.running = False

        if self.discovery_system:
            try:
                self.discovery_system.stop()
                logger.info("Discovery system stopped")
            except Exception as e:
                logger.error(f"Error stopping discovery system: {e}")

    def _start_discovery_system(self):
        """Start the underlying discovery system"""
        from biodisc_core.reasoning.v73_autonomous_discovery import (
            get_autonomous_discovery_system,
            AutonomousDiscoveryConfig
        )

        config = AutonomousDiscoveryConfig(
            max_cpu_percent=15.0,  # Conservative CPU usage
            max_hours_per_week=168.0,  # 24x7 operation
            idle_timeout_minutes=2,  # Standard idle detection
            min_confidence_to_store=0.65,
            min_evidence_count=1,
            bioscience_mode=True,
            questions_per_cycle=10,
            cycle_interval_seconds=5,  # Conservative cycle timing
            log_all_discoveries=True,
            discovery_log_path=str(project_root / 'autonomous_discoveries.jsonl')
        )

        self.discovery_system = get_autonomous_discovery_system(config)
        self.discovery_system.start()

        self.last_progress_time = datetime.now()
        logger.info("✅ Discovery system started successfully")

    def _monitor_system(self):
        """Monitor system health and detect stalls"""
        logger.info("📊 Starting system health monitoring...")

        while self.running:
            try:
                time.sleep(self.check_interval)

                # Check if discovery system is still running
                if not self.discovery_system:
                    logger.warning("Discovery system not available, restarting...")
                    break

                # Get system status
                status = self.discovery_system.get_status()

                # Check for progress
                current_discovery_count = status.get('total_discoveries', 0)

                if current_discovery_count > self.last_discovery_count:
                    # Progress detected!
                    new_discoveries = current_discovery_count - self.last_discovery_count
                    logger.info(f"🧬 Progress: {new_discoveries} new discoveries (total: {current_discovery_count})")
                    self.last_discovery_count = current_discovery_count
                    self.last_progress_time = datetime.now()

                # Check for stall
                time_since_progress = (datetime.now() - self.last_progress_time).total_seconds()

                if time_since_progress > self.stall_threshold_seconds:
                    logger.warning(f"⚠️ System stalled: no progress for {time_since_progress:.0f} seconds")
                    logger.warning("Restarting discovery system...")
                    break

                # Check if system is running
                if not status.get('running', False):
                    logger.warning("⚠️ Discovery system not running, restarting...")
                    break

                # Log periodic status
                if self.restart_count % 10 == 0:  # Every ~5 minutes
                    logger.info(f"📊 Status: {current_discovery_count} discoveries, "
                              f"running: {status.get('running', False)}, "
                              f"stall check: {time_since_progress:.0f}s since progress")

            except Exception as e:
                logger.error(f"Error monitoring system: {e}", exc_info=True)
                # Don't break immediately, could be transient error
                if "No connection to" in str(e) or "broken" in str(e).lower():
                    logger.warning("Connection error detected, restarting...")
                    break

    def update_activity(self):
        """Update activity time (call when user interacts)"""
        if self.discovery_system:
            try:
                self.discovery_system.update_activity()
                logger.debug("User activity updated")
            except Exception as e:
                logger.error(f"Error updating activity: {e}")


def main():
    """Main entry point"""
    logger.info("🧬 BIODISC Robust Autonomous Discovery v2.0")
    logger.info("=" * 70)

    discovery = RobustAutonomousDiscovery()

    try:
        discovery.start()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        discovery.stop()


if __name__ == "__main__":
    main()