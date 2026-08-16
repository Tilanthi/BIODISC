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
BIODISC WORKING Autonomous Discovery System

FINAL SOLUTION: This version implements the complete fix for genuine discovery.

CRITICAL INSIGHT: The problem was NOT the architecture - it was the routing logic.
Questions like "How/Why" were sent to insight generation WITHOUT computational analysis.
The insight generator expected computational results but received question metadata.

SOLUTION IMPLEMENTED:
1. ALL questions now route through computational analysis first
2. Computational analysis generates genuine findings
3. Only THEN does insight generation interpret results
4. Discoveries have proper computational backing

Date: 2026-07-01
Version: 4.0 - WORKING Genuine Discovery System
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
        logging.FileHandler(log_dir / "autonomous_discovery_working.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WorkingAutonomousDiscovery:
    """
    WORKING autonomous discovery system that makes genuine biological discoveries.

    KEY FIX: Proper integration of computational analysis with question routing.
    """

    def __init__(self):
        self.discovery_system = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 1000
        self.last_progress_time = None
        self.last_discovery_count = 0
        self.cycle_count = 0

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start working autonomous discovery"""
        logger.info("🧬 BIODISC WORKING Autonomous Discovery v4.0")
        logger.info("=" * 70)
        logger.info("CRITICAL FIX APPLIED:")
        logger.info("✅ ALL questions now get computational analysis first")
        logger.info("✅ Proper integration of computational pipeline")
        logger.info("✅ Genuine discoveries with statistical backing")
        logger.info("=" * 70)

        self.running = True

        while self.running and self.restart_count < self.max_restarts:
            try:
                logger.info(f"🔄 Starting working discovery (attempt #{self.restart_count + 1})")
                self._start_working_discovery_system()
                self._monitor_working_system()

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

    def _start_working_discovery_system(self):
        """Start the WORKING discovery system"""
        from biodisc_core.reasoning.v73_autonomous_discovery_working import (
            get_working_autonomous_discovery_system,
            WorkingAutonomousDiscoveryConfig
        )

        # Create working configuration
        config = WorkingAutonomousDiscoveryConfig(
            max_cpu_percent=15.0,
            max_hours_per_week=168.0,
            idle_timeout_minutes=0,  # CRITICAL: No idle wait for testing
            min_confidence_to_store=0.70,  # Higher confidence for genuine discoveries
            min_evidence_count=2,  # Require multiple evidence sources
            bioscience_mode=True,
            questions_per_cycle=8,
            cycle_interval_seconds=10,  # Allow time for proper analysis
            log_all_discoveries=True,
            discovery_log_path=str(project_root / 'autonomous_discoveries.jsonl')
        )

        self.discovery_system = get_working_autonomous_discovery_system(config)
        self.discovery_system.start()

        self.last_progress_time = datetime.now()
        logger.info("✅ WORKING discovery system started")

    def _monitor_working_system(self):
        """Monitor working system"""
        logger.info("📊 Starting WORKING system health monitoring...")

        while self.running:
            try:
                time.sleep(30)

                if not self.discovery_system:
                    logger.warning("Discovery system not available, restarting...")
                    break

                status = self.discovery_system.get_status()

                current_discovery_count = status.get('total_discoveries', 0)

                if current_discovery_count > self.last_discovery_count:
                    new_discoveries = current_discovery_count - self.last_discovery_count
                    logger.info(f"🧬 Progress: {new_discoveries} new discoveries (total: {current_discovery_count})")
                    self.last_discovery_count = current_discovery_count
                    self.last_progress_time = datetime.now()

                time_since_progress = (datetime.now() - self.last_progress_time).total_seconds()

                if time_since_progress > 600:  # 10 minutes
                    logger.warning(f"⚠️ System stalled: no progress for {time_since_progress:.0f} seconds")
                    break

                if not status.get('running', False):
                    logger.warning("⚠️ Discovery system not running, restarting...")
                    break

                if self.cycle_count % 10 == 0:
                    logger.info(f"📊 Status: {current_discovery_count} discoveries, running: {status.get('running', False)}")

                self.cycle_count += 1

            except Exception as e:
                logger.error(f"Error monitoring system: {e}", exc_info=True)
                if "connection" in str(e).lower() or "broken" in str(e).lower():
                    logger.warning("Connection error detected, restarting...")
                    break

    def update_activity(self):
        """Update activity time"""
        if self.discovery_system:
            try:
                self.discovery_system.update_activity()
            except Exception as e:
                logger.error(f"Error updating activity: {e}")


def main():
    """Main entry point"""
    logger.info("🧬 BIODISC WORKING Autonomous Discovery v4.0")
    logger.info("=" * 70)

    discovery = WorkingAutonomousDiscovery()

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