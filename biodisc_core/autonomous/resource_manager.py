"""
Resource Management System

Manages CPU, memory, and time resources for autonomous operations.
Ensures autonomous operations stay within configured limits.
"""

import logging
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

from .config import (
    AutonomousConfig,
    ResourceStatus,
    ThrottleAction
)

logger = logging.getLogger(__name__)


@dataclass
class ResourceUsage:
    """Current resource usage snapshot"""
    cpu_percent: float
    memory_percent: float
    timestamp: datetime


class ResourceTracker:
    """Track resource usage over time"""

    def __init__(self, window_size: int = 60):
        """
        Initialize resource tracker.

        Args:
            window_size: Number of samples to keep for averaging
        """
        self.window_size = window_size
        self.cpu_history: deque = deque(maxlen=window_size)
        self.memory_history: deque = deque(maxlen=window_size)
        self.session_start = datetime.now()

    def record_usage(self, cpu_percent: float, memory_percent: float):
        """Record current resource usage"""
        self.cpu_history.append(cpu_percent)
        self.memory_history.append(memory_percent)

    def get_current_usage(self) -> ResourceUsage:
        """Get current resource usage"""
        try:
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_memory = psutil.virtual_memory().percent

            # Record for history
            self.record_usage(current_cpu, current_memory)

            return ResourceUsage(
                cpu_percent=current_cpu,
                memory_percent=current_memory,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return ResourceUsage(cpu_percent=0, memory_percent=0, timestamp=datetime.now())

    def get_average_usage(self) -> Dict[str, float]:
        """Get average resource usage over the window"""
        if not self.cpu_history:
            return {'cpu': 0.0, 'memory': 0.0}

        return {
            'cpu': sum(self.cpu_history) / len(self.cpu_history),
            'memory': sum(self.memory_history) / len(self.memory_history)
        }

    def get_weekly_hours(self) -> float:
        """Get total hours used this week"""
        duration = datetime.now() - self.session_start
        return duration.total_seconds() / 3600


class ResourceManager:
    """
    Monitor and manage resource usage for autonomous operations.

    Ensures autonomous operations stay within configured resource limits:
    - CPU usage percentage
    - Memory usage percentage
    - Weekly time budget
    """

    def __init__(self, config: AutonomousConfig):
        """
        Initialize resource manager.

        Args:
            config: Autonomous system configuration with resource limits
        """
        self.config = config
        self.tracker = ResourceTracker()

        # Throttling state
        self.current_throttle = ThrottleAction.NONE
        self.throttle_history: list = []

        # Resource limit tracking
        self.resource_violations: int = 0
        self.last_violation_time: Optional[datetime] = None

        logger.info("Resource Manager initialized")

    def check_resource_availability(self) -> ResourceStatus:
        """
        Check if sufficient resources available for autonomous operation.

        Returns:
            ResourceStatus with availability information
        """
        try:
            # Get current usage
            current = self.tracker.get_current_usage()
            weekly_hours = self.tracker.get_weekly_hours()

            # Check each resource
            cpu_available = current.cpu_percent < self.config.max_cpu_percent
            memory_available = current.memory_percent < self.config.max_memory_percent
            time_available = weekly_hours < self.config.max_hours_per_week

            status = ResourceStatus(
                cpu_available=cpu_available,
                memory_available=memory_available,
                time_available=time_available,
                current_cpu_percent=current.cpu_percent,
                current_memory_percent=current.memory_percent,
                weekly_hours_used=weekly_hours
            )

            # Log any resource pressure
            if not cpu_available:
                logger.warning(f"CPU limit: {current.cpu_percent:.1f}% > {self.config.max_cpu_percent}%")

            if not time_available:
                logger.warning(f"Time limit: {weekly_hours:.1f}h > {self.config.max_hours_per_week}h")

            return status

        except Exception as e:
            logger.error(f"Error checking resource availability: {e}")
            return ResourceStatus(
                cpu_available=False,
                memory_available=False,
                time_available=False
            )

    def throttle_if_needed(self) -> ThrottleAction:
        """
        Determine if throttling is needed based on resource pressure.

        Returns:
            ThrottleAction to take
        """
        status = self.check_resource_availability()

        # Check CPU pressure
        if not status.cpu_available:
            cpu_over = status.current_cpu_percent - self.config.max_cpu_percent

            if cpu_over > 10:
                # Major CPU overage
                logger.warning("Major CPU overage - pausing autonomous operations")
                self.current_throttle = ThrottleAction.PAUSE
            else:
                # Minor CPU overage
                logger.info("CPU pressure detected - reducing CPU intensity")
                self.current_throttle = ThrottleAction.REDUCE_CPU

        # Check time pressure
        elif not status.time_available:
            time_over = status.weekly_hours_used - self.config.max_hours_per_week

            if time_over > 1.0:
                # Major time overage
                logger.warning("Time budget exceeded - pausing")
                self.current_throttle = ThrottleAction.PAUSE
            else:
                # Minor time overage
                logger.info("Time budget pressure - reduce agent count")
                self.current_throttle = ThrottleAction.REDUCE_AGENTS

        else:
            # All resources OK
            self.current_throttle = ThrottleAction.NONE

        # Track throttling
        if self.current_throttle != ThrottleAction.NONE:
            self.throttle_history.append({
                'action': self.current_throttle,
                'timestamp': datetime.now(),
                'cpu_percent': status.current_cpu_percent,
                'weekly_hours': status.weekly_hours_used
            })

        return self.current_throttle

    def get_resource_report(self) -> Dict[str, Any]:
        """Get comprehensive resource usage report"""
        status = self.check_resource_availability()
        averages = self.tracker.get_average_usage()

        return {
            'current_usage': {
                'cpu_percent': status.current_cpu_percent,
                'memory_percent': status.current_memory_percent
            },
            'average_usage': averages,
            'limits': {
                'max_cpu_percent': self.config.max_cpu_percent,
                'max_memory_percent': self.config.max_memory_percent,
                'max_hours_per_week': self.config.max_hours_per_week
            },
            'availability': {
                'cpu_available': status.cpu_available,
                'memory_available': status.memory_available,
                'time_available': status.time_available
            },
            'weekly_hours_used': status.weekly_hours_used,
            'current_throttle': self.current_throttle,
            'throttle_count': len(self.throttle_history),
            'resource_violations': self.resource_violations
        }

    def reset_resource_tracking(self):
        """Reset resource tracking (e.g., for new week)"""
        self.tracker = ResourceTracker()
        self.resource_violations = 0
        self.last_violation_time = None
        logger.info("Resource tracking reset")

    def record_violation(self):
        """Record a resource limit violation"""
        self.resource_violations += 1
        self.last_violation_time = datetime.now()
        logger.warning(f"Resource violation recorded (total: {self.resource_violations})")