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
BIODISC Autonomous Discovery Guardian - Robust Auto-Restart System

This guardian ensures BIODISC autonomous discovery ALWAYS runs unless:
1. User is actively interacting with the system
2. System is explicitly disabled
3. Resource limits are exceeded

ARCHITECTURAL IMPROVEMENTS:
1. Automatic restart on failure/crash
2. Duplicate discovery prevention
3. Progress detection and recovery
4. Health monitoring and alerts
5. Graceful shutdown on user activity

Date: 2026-07-01
Version: 1.0 - Guardian System
"""

import sys
import os
import time
import json
import logging
import psutil
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib
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
        logging.FileHandler(log_dir / "autonomous_guardian.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GuardianConfig:
    """Guardian configuration"""
    # Process monitoring
    check_interval_seconds: int = 30  # Check process health every 30 seconds
    max_restart_attempts: int = 100  # Maximum restart attempts before giving up
    restart_delay_seconds: int = 10  # Delay between restart attempts

    # Duplicate prevention
    discovery_cache_size: int = 1000  # Store recent discovery hashes
    duplicate_check_window_hours: int = 24  # Check for duplicates in last 24 hours

    # Health monitoring
    max_cycles_without_discovery: int = 20  # Alert after 20 cycles without discovery
    cycle_timeout_seconds: int = 300  # Alert if cycle takes longer than 5 minutes
    inactivity_timeout_seconds: int = 600  # Alert if no activity for 10 minutes

    # Resource limits
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0

    # User activity detection
    user_activity_timeout_seconds: int = 120  # Consider active if user interaction within 2 minutes


@dataclass
class DiscoveryRecord:
    """Record of a discovery for duplicate prevention"""
    question_hash: str
    discovery_hash: str
    timestamp: datetime
    cycle_number: int
    confidence: float
    validated: bool


class AutonomousDiscoveryGuardian:
    """
    Guardian system for autonomous discovery with robust auto-restart and duplicate prevention.

    KEY FEATURES:
    1. Monitors autonomous discovery process health
    2. Automatically restarts failed processes
    3. Prevents duplicate discoveries
    4. Detects and alerts on stalled systems
    5. Respects user activity and resource limits
    """

    def __init__(self, config: GuardianConfig = None):
        self.config = config or GuardianConfig()
        self.discovery_process: Optional[Any] = None
        self.discovery_records: List[DiscoveryRecord] = []
        self.last_activity_time = datetime.now()
        self.last_cycle_time = datetime.now()
        self.cycle_count = 0
        self.discovery_count = 0
        self.restart_count = 0
        self.running = False
        self.lock = threading.Lock()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down guardian...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start the guardian system"""
        logger.info("🧬 Starting BIODISC Autonomous Discovery Guardian...")
        self.running = True

        # Start monitoring loop
        self._monitoring_loop()

    def stop(self):
        """Stop the guardian system"""
        logger.info("Stopping BIODISC Autonomous Discovery Guardian...")
        self.running = False

        if self.discovery_process:
            logger.info("Stopping autonomous discovery process...")
            try:
                self.discovery_process.terminate()
                self.discovery_process.wait(timeout=10)
            except Exception as e:
                logger.error(f"Error stopping discovery process: {e}")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Guardian monitoring loop started")

        while self.running:
            try:
                # Check if user is active
                if self._is_user_active():
                    logger.debug("User active, ensuring discovery is paused...")
                    self._ensure_discovery_paused()
                else:
                    logger.debug("User idle, ensuring discovery is running...")
                    self._ensure_discovery_running()

                # Check process health
                if self.discovery_process:
                    self._check_process_health()

                # Clean old discovery records
                self._cleanup_old_records()

                # Sleep before next check
                time.sleep(self.config.check_interval_seconds)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(5)  # Brief pause before retry

    def _is_user_active(self) -> bool:
        """Check if user has been active recently"""
        idle_time = (datetime.now() - self.last_activity_time).total_seconds()
        return idle_time < self.config.user_activity_timeout_seconds

    def _update_activity(self):
        """Update last activity time (call when user interacts)"""
        with self.lock:
            self.last_activity_time = datetime.now()

    def _ensure_discovery_running(self):
        """Ensure autonomous discovery process is running"""
        if not self.discovery_process or not self._is_process_alive():
            logger.warning("Autonomous discovery process not running, starting...")
            self._start_discovery_process()
        elif self._is_process_stalled():
            logger.warning("Discovery process appears stalled, restarting...")
            self._restart_discovery_process()

    def _ensure_discovery_paused(self):
        """Ensure discovery is paused during user activity"""
        if self.discovery_process and self._is_process_alive():
            # Process should handle pausing automatically via activity detection
            # We just update activity time to signal user presence
            self._update_activity()

    def _is_process_alive(self) -> bool:
        """Check if discovery process is still alive"""
        if not self.discovery_process:
            return False

        try:
            # Check if process is still running
            return self.discovery_process.poll() is None
        except Exception as e:
            logger.error(f"Error checking process status: {e}")
            return False

    def _is_process_stalled(self) -> bool:
        """Check if process has stalled (no progress for too long)"""
        if not self.discovery_process or not self._is_process_alive():
            return False

        # Check if last cycle was too long ago
        cycle_idle_time = (datetime.now() - self.last_cycle_time).total_seconds()
        if cycle_idle_time > self.config.inactivity_timeout_seconds:
            logger.warning(f"Process stalled: no activity for {cycle_idle_time:.0f} seconds")
            return True

        # Check if too many cycles without discoveries
        if self.cycle_count > 0 and self.discovery_count == 0:
            if self.cycle_count >= self.config.max_cycles_without_discovery:
                logger.warning(f"Process stalled: {self.cycle_count} cycles without discoveries")
                return True

        return False

    def _start_discovery_process(self):
        """Start the autonomous discovery process"""
        try:
            logger.info("Starting autonomous discovery process...")

            # Import and start autonomous discovery
            from biodisc_core.reasoning.v73_autonomous_discovery import (
                get_autonomous_discovery_system,
                AutonomousDiscoveryConfig
            )

            config = AutonomousDiscoveryConfig(
                max_cpu_percent=self.config.max_cpu_percent,
                max_hours_per_week=168.0,  # 24x7
                idle_timeout_minutes=2,  # Standard idle timeout
                min_confidence_to_store=0.65,
                min_evidence_count=1,
                bioscience_mode=True,
                questions_per_cycle=10,
                cycle_interval_seconds=5,  # Conservative cycle interval
                log_all_discoveries=True,
                discovery_log_path=str(project_root / 'autonomous_discoveries.jsonl')
            )

            self.discovery_system = get_autonomous_discovery_system(config)

            # Start in background thread
            import threading
            discovery_thread = threading.Thread(
                target=self.discovery_system.start,
                daemon=True,
                name="AutonomousDiscovery"
            )
            discovery_thread.start()

            # Create fake process object for compatibility
            class FakeProcess:
                def __init__(self):
                    self.alive = True
                    self.thread = discovery_thread

                def poll(self):
                    return None if self.alive and self.thread.is_alive() else 0

                def terminate(self):
                    self.alive = False
                    try:
                        self.discovery_system.stop()
                    except:
                        pass

                def wait(self, timeout=None):
                    if self.thread.is_alive():
                        self.thread.join(timeout=timeout)

            self.discovery_process = FakeProcess()
            self.discovery_process.discovery_system = self.discovery_system
            self.discovery_process.thread = discovery_thread

            self.last_cycle_time = datetime.now()
            self.restart_count += 1

            logger.info(f"✅ Autonomous discovery started (restart #{self.restart_count})")

        except Exception as e:
            logger.error(f"Failed to start autonomous discovery: {e}", exc_info=True)

    def _restart_discovery_process(self):
        """Restart the discovery process"""
        logger.info("Restarting autonomous discovery process...")

        if self.discovery_process:
            try:
                self.discovery_process.terminate()
                time.sleep(2)  # Brief pause for cleanup
            except Exception as e:
                logger.error(f"Error terminating old process: {e}")

        self.discovery_process = None
        self._start_discovery_process()

    def _check_process_health(self):
        """Monitor process health and progress"""
        try:
            if not self.discovery_process:
                return

            # Get status from discovery system
            if hasattr(self.discovery_process, 'discovery_system'):
                status = self.discovery_process.discovery_system.get_status()

                # Update cycle count
                if 'total_discoveries' in status:
                    new_discovery_count = status['total_discoveries']
                    if new_discovery_count > self.discovery_count:
                        logger.info(f"🧬 New discovery! Total: {new_discovery_count}")
                        self.discovery_count = new_discovery_count
                        self.last_cycle_time = datetime.now()

                self.cycle_count += 1

        except Exception as e:
            logger.error(f"Error checking process health: {e}")

    def _cleanup_old_records(self):
        """Remove discovery records older than the duplicate check window"""
        cutoff_time = datetime.now() - timedelta(hours=self.config.duplicate_check_window_hours)

        with self.lock:
            original_count = len(self.discovery_records)
            self.discovery_records = [
                record for record in self.discovery_records
                if record.timestamp > cutoff_time
            ]

            removed = original_count - len(self.discovery_records)
            if removed > 0:
                logger.debug(f"Cleaned up {removed} old discovery records")

    def _hash_question(self, question: str) -> str:
        """Create hash of question for duplicate detection"""
        return hashlib.md5(question.encode()).hexdigest()

    def _hash_discovery(self, discovery: str) -> str:
        """Create hash of discovery content for duplicate detection"""
        return hashlib.md5(discovery.encode()).hexdigest()

    def is_duplicate_discovery(self, question: str, discovery_content: str) -> bool:
        """Check if this is a duplicate discovery"""
        question_hash = self._hash_question(question)
        discovery_hash = self._hash_discovery(discovery_content)

        with self.lock:
            for record in self.discovery_records:
                if record.question_hash == question_hash and record.discovery_hash == discovery_hash:
                    logger.info(f"Duplicate discovery detected: {question[:50]}...")
                    return True

        return False

    def record_discovery(self, question: str, discovery_content: str, confidence: float, validated: bool):
        """Record a discovery for duplicate prevention"""
        question_hash = self._hash_question(question)
        discovery_hash = self._hash_discovery(discovery_content)

        with self.lock:
            record = DiscoveryRecord(
                question_hash=question_hash,
                discovery_hash=discovery_hash,
                timestamp=datetime.now(),
                cycle_number=self.cycle_count,
                confidence=confidence,
                validated=validated
            )

            self.discovery_records.append(record)

            # Keep cache size manageable
            if len(self.discovery_records) > self.config.discovery_cache_size:
                self.discovery_records = self.discovery_records[-self.config.discovery_cache_size:]

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive guardian status"""
        return {
            'guardian_running': self.running,
            'discovery_process_alive': self._is_process_alive() if self.discovery_process else False,
            'restart_count': self.restart_count,
            'cycle_count': self.cycle_count,
            'discovery_count': self.discovery_count,
            'discovery_records_count': len(self.discovery_records),
            'last_activity': self.last_activity_time.isoformat(),
            'last_cycle': self.last_cycle_time.isoformat(),
            'user_active': self._is_user_active()
        }


def main():
    """Main entry point for guardian system"""
    logger.info("🧬 BIODISC Autonomous Discovery Guardian v1.0")
    logger.info("=" * 60)

    # Create and start guardian
    guardian = AutonomousDiscoveryGuardian()

    try:
        guardian.start()
    except KeyboardInterrupt:
        logger.info("Guardian stopped by user")
    except Exception as e:
        logger.error(f"Guardian error: {e}", exc_info=True)
    finally:
        guardian.stop()


if __name__ == "__main__":
    main()