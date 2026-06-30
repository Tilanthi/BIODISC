"""
Capability Lifecycle Manager for BIODISC

Manages the complete lifecycle of capabilities:
- Registration: Discover and index capabilities
- Activation: Load and initialize based on need
- Deactivation: Release resources when idle
- Health monitoring: Track capability performance
- Lazy loading: Load capabilities on demand

This ensures efficient resource usage and optimal performance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum
import time
import importlib
import sys
import traceback
from collections import defaultdict
import weakref


class LifecycleState(Enum):
    """States in capability lifecycle."""
    REGISTERED = "registered"      # Known to system but not loaded
    LOADING = "loading"            # Currently being loaded
    ACTIVE = "active"              # Loaded and ready to use
    IDLE = "idle"                  # Active but not recently used
    SUSPENDED = "suspended"        # Temporarily deactivated
    DEACTIVATED = "deactivated"    # Unloaded, resources released
    ERROR = "error"                # Failed to load or execute


class HealthStatus(Enum):
    """Health status of capabilities."""
    HEALTHY = "healthy"            # Functioning normally
    DEGRADED = "degraded"          # Functioning with issues
    UNHEALTHY = "unhealthy"        # Not functioning properly
    UNKNOWN = "unknown"            # Status not yet determined


@dataclass
class CapabilityMetadata:
    """Metadata about a capability."""
    name: str
    module_path: str
    class_name: Optional[str] = None
    domain: str = "general"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    estimated_load_time: float = 1.0  # Seconds
    version: str = "1.0.0"


@dataclass
class CapabilityInstance:
    """An active capability instance."""
    metadata: CapabilityMetadata
    instance: Any
    state: LifecycleState
    last_used: float
    load_time: float
    health_status: HealthStatus = HealthStatus.UNKNOWN
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_execution_time: float = 0.0
    peak_memory_mb: float = 0.0


@dataclass
class LifecycleEvent:
    """Event in capability lifecycle."""
    capability_name: str
    event_type: str  # "registered", "activated", "deactivated", "error"
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Monitor health and performance of capabilities."""

    def __init__(self):
        self.health_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.performance_thresholds = {
            "max_failure_rate": 0.2,      # 20% max failure rate
            "max_avg_time": 30.0,         # 30 seconds max average time
            "min_success_rate": 0.8       # 80% min success rate
        }

    def check_health(
        self,
        capability_name: str,
        instance: CapabilityInstance
    ) -> HealthStatus:
        """
        Check health of a capability instance.

        Evaluates:
        - Success/failure rates
        - Execution time
        - Error patterns
        """
        if instance.execution_count == 0:
            return HealthStatus.UNKNOWN

        # Calculate metrics
        failure_rate = instance.failure_count / instance.execution_count
        success_rate = instance.success_count / instance.execution_count

        # Check against thresholds
        if failure_rate > self.performance_thresholds["max_failure_rate"]:
            return HealthStatus.UNHEALTHY

        if success_rate < self.performance_thresholds["min_success_rate"]:
            return HealthStatus.UNHEALTHY

        if instance.average_execution_time > self.performance_thresholds["max_avg_time"]:
            return HealthStatus.DEGRADED

        # Check recent performance trend
        recent_history = self.health_history[capability_name][-10:] if capability_name in self.health_history else []

        if recent_history:
            recent_failures = sum(1 for h in recent_history if not h.get("success", True))
            if recent_failures > len(recent_history) * 0.3:
                return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def record_execution(
        self,
        capability_name: str,
        success: bool,
        execution_time: float,
        memory_mb: float
    ) -> None:
        """Record execution for health monitoring."""
        self.health_history[capability_name].append({
            "timestamp": time.time(),
            "success": success,
            "execution_time": execution_time,
            "memory_mb": memory_mb
        })

    def get_health_report(self, capability_name: str) -> Dict[str, Any]:
        """Get health report for a capability."""
        if capability_name not in self.health_history:
            return {"status": "no_data"}

        history = self.health_history[capability_name]

        if not history:
            return {"status": "no_data"}

        # Calculate statistics
        total_executions = len(history)
        successful = sum(1 for h in history if h.get("success", True))
        failed = total_executions - successful

        execution_times = [h.get("execution_time", 0) for h in history]
        memory_usage = [h.get("memory_mb", 0) for h in history]

        return {
            "total_executions": total_executions,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "failure_rate": failed / total_executions if total_executions > 0 else 0,
            "average_execution_time": np.mean(execution_times) if execution_times else 0,
            "peak_memory_mb": max(memory_usage) if memory_usage else 0,
            "last_execution": history[-1]["timestamp"] if history else None
        }


class CapabilityLifecycleManager:
    """
    Manage complete lifecycle of capabilities.

    Features:
    - Registration and discovery
    - Lazy loading on demand
    - Automatic deactivation when idle
    - Health monitoring and recovery
    - Resource management
    """

    def __init__(
        self,
        idle_timeout: float = 300.0,  # 5 minutes
        health_check_interval: float = 60.0,  # 1 minute
        max_idle_capabilities: int = 10
    ):
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval
        self.max_idle_capabilities = max_idle_capabilities

        # Capability storage
        self.registered_capabilities: Dict[str, CapabilityMetadata] = {}
        self.active_capabilities: Dict[str, CapabilityInstance] = {}

        # Lifecycle tracking
        self.event_history: List[LifecycleEvent] = []
        self.health_checker = HealthChecker()

        # Weak references for cleanup
        self.weak_refs: Dict[str, weakref.ref] = {}

    def register_capability(self, metadata: CapabilityMetadata) -> bool:
        """
        Register a capability with the system.

        Args:
            metadata: Capability metadata

        Returns:
            True if registration successful
        """
        try:
            # Validate metadata
            if not metadata.name or not metadata.module_path:
                return False

            # Register
            self.registered_capabilities[metadata.name] = metadata

            # Record event
            self._record_event(
                metadata.name,
                "registered",
                {"module": metadata.module_path, "domain": metadata.domain}
            )

            return True

        except Exception as e:
            self._record_event(
                metadata.name,
                "error",
                {"error": str(e), "stage": "registration"}
            )
            return False

    def discover_capabilities(self, module_paths: List[str]) -> int:
        """
        Discover capabilities in specified modules.

        Args:
            module_paths: List of module paths to scan

        Returns:
            Number of capabilities discovered
        """
        discovered = 0

        for module_path in module_paths:
            try:
                # Import module
                module = importlib.import_module(module_path)

                # Find capability classes
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue

                    attr = getattr(module, attr_name)

                    # Check if it's a class
                    if not isinstance(attr, type):
                        continue

                    # Check for capability markers
                    if hasattr(attr, "__capability_name__"):
                        metadata = CapabilityMetadata(
                            name=getattr(attr, "__capability_name__"),
                            module_path=module_path,
                            class_name=attr_name,
                            domain=getattr(attr, "__capability_domain__", "general"),
                            description=getattr(attr, "__capability_description__", ""),
                            dependencies=getattr(attr, "__capability_dependencies__", []),
                        )

                        if self.register_capability(metadata):
                            discovered += 1

            except ImportError:
                continue
            except Exception:
                continue

        return discovered

    def activate_capability(self, name: str) -> Optional[Any]:
        """
        Activate a capability (lazy loading).

        Args:
            name: Capability name

        Returns:
            Capability instance or None if activation fails
        """
        # Check if already active
        if name in self.active_capabilities:
            instance = self.active_capabilities[name]
            instance.last_used = time.time()
            instance.state = LifecycleState.ACTIVE
            return instance.instance

        # Check if registered
        if name not in self.registered_capabilities:
            return None

        metadata = self.registered_capabilities[name]

        try:
            # Update state
            self._record_event(name, "loading", {})

            # Load module
            module = importlib.import_module(metadata.module_path)

            # Get class
            if metadata.class_name:
                capability_class = getattr(module, metadata.class_name)
            else:
                # Try to find a class with matching name
                capability_class = getattr(
                    module,
                    name.replace("_", " ").title().replace(" ", ""),
                    None
                )

            if capability_class is None:
                # Use module itself as capability
                capability_class = module

            # Create instance
            instance = capability_class()

            # Create capability instance record
            load_time = time.time()

            capability_instance = CapabilityInstance(
                metadata=metadata,
                instance=instance,
                state=LifecycleState.ACTIVE,
                last_used=load_time,
                load_time=load_time,
                health_status=HealthStatus.UNKNOWN
            )

            self.active_capabilities[name] = capability_instance

            # Record event
            self._record_event(
                name,
                "activated",
                {"load_time": load_time}
            )

            return instance

        except Exception as e:
            # Record error
            self._record_event(
                name,
                "error",
                {"error": str(e), "traceback": traceback.format_exc()}
            )
            return None

    def deactivate_capability(self, name: str) -> bool:
        """
        Deactivate a capability and release resources.

        Args:
            name: Capability name

        Returns:
            True if deactivation successful
        """
        if name not in self.active_capabilities:
            return False

        try:
            # Remove from active
            del self.active_capabilities[name]

            # Remove weak ref
            if name in self.weak_refs:
                del self.weak_refs[name]

            # Record event
            self._record_event(name, "deactivated", {})

            return True

        except Exception as e:
            self._record_event(
                name,
                "error",
                {"error": str(e), "stage": "deactivation"}
            )
            return False

    def get_capability(self, name: str) -> Optional[Any]:
        """
        Get capability instance, activating if necessary.

        Args:
            name: Capability name

        Returns:
            Capability instance or None
        """
        # Activate if not active
        if name not in self.active_capabilities:
            return self.activate_capability(name)

        # Update last used
        self.active_capabilities[name].last_used = time.time()

        return self.active_capabilities[name].instance

    def release_idle_capabilities(self) -> int:
        """
        Release capabilities that have been idle too long.

        Returns:
            Number of capabilities released
        """
        current_time = time.time()
        released = 0

        # Sort by last used time
        idle_capabilities = [
            (name, instance)
            for name, instance in self.active_capabilities.items()
            if current_time - instance.last_used > self.idle_timeout
        ]

        # If too many idle capabilities, release oldest
        if len(idle_capabilities) > self.max_idle_capabilities:
            # Sort by last used (oldest first)
            idle_capabilities.sort(key=lambda x: x[1].last_used)

            # Release excess
            excess = len(idle_capabilities) - self.max_idle_capabilities
            for name, _ in idle_capabilities[:excess]:
                if self.deactivate_capability(name):
                    released += 1

        return released

    def check_capability_health(self, name: str) -> HealthStatus:
        """
        Check health of a capability.

        Args:
            name: Capability name

        Returns:
            Health status
        """
        if name not in self.active_capabilities:
            return HealthStatus.UNKNOWN

        instance = self.active_capabilities[name]
        health = self.health_checker.check_health(name, instance)

        instance.health_status = health

        return health

    def record_capability_execution(
        self,
        name: str,
        success: bool,
        execution_time: float,
        memory_mb: float
    ) -> None:
        """
        Record capability execution for monitoring.

        Args:
            name: Capability name
            success: Whether execution succeeded
            execution_time: Execution time in seconds
            memory_mb: Memory usage in MB
        """
        if name in self.active_capabilities:
            instance = self.active_capabilities[name]

            # Update instance metrics
            instance.execution_count += 1
            instance.last_used = time.time()

            if success:
                instance.success_count += 1
            else:
                instance.failure_count += 1

            # Update average execution time
            n = instance.execution_count
            instance.average_execution_time = (
                (instance.average_execution_time * (n - 1) + execution_time) / n
            )

            # Update peak memory
            instance.peak_memory_mb = max(instance.peak_memory_mb, memory_mb)

        # Record in health checker
        self.health_checker.record_execution(name, success, execution_time, memory_mb)

    def get_active_capabilities(self) -> List[str]:
        """Get list of currently active capabilities."""
        return list(self.active_capabilities.keys())

    def get_capability_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a capability."""
        if name in self.active_capabilities:
            instance = self.active_capabilities[name]
            return {
                "name": name,
                "state": instance.state.value,
                "health": instance.health_status.value,
                "execution_count": instance.execution_count,
                "success_rate": (
                    instance.success_count / instance.execution_count
                    if instance.execution_count > 0 else 0
                ),
                "average_execution_time": instance.average_execution_time,
                "peak_memory_mb": instance.peak_memory_mb,
                "last_used": instance.last_used,
                "load_time": instance.load_time
            }
        elif name in self.registered_capabilities:
            metadata = self.registered_capabilities[name]
            return {
                "name": name,
                "state": "registered",
                "domain": metadata.domain,
                "description": metadata.description,
                "module": metadata.module_path
            }
        else:
            return None

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        active_count = len(self.active_capabilities)
        registered_count = len(self.registered_capabilities)

        # Calculate health distribution
        health_distribution = defaultdict(int)
        for instance in self.active_capabilities.values():
            health_distribution[instance.health_status.value] += 1

        return {
            "active_capabilities": active_count,
            "registered_capabilities": registered_count,
            "health_distribution": dict(health_distribution),
            "total_executions": sum(
                instance.execution_count
                for instance in self.active_capabilities.values()
            ),
            "idle_timeout": self.idle_timeout,
            "max_idle_capabilities": self.max_idle_capabilities
        }

    def cleanup(self) -> None:
        """Cleanup resources."""
        # Deactivate all capabilities
        for name in list(self.active_capabilities.keys()):
            self.deactivate_capability(name)

        # Clear event history
        self.event_history.clear()

    def _record_event(
        self,
        capability_name: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Record a lifecycle event."""
        event = LifecycleEvent(
            capability_name=capability_name,
            event_type=event_type,
            timestamp=time.time(),
            details=details
        )

        self.event_history.append(event)

        # Limit history size
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]

    def get_event_history(
        self,
        capability_name: Optional[str] = None,
        limit: int = 100
    ) -> List[LifecycleEvent]:
        """Get event history."""
        events = self.event_history

        if capability_name:
            events = [e for e in events if e.capability_name == capability_name]

        return events[-limit:]


def create_lifecycle_manager(
    idle_timeout: float = 300.0,
    health_check_interval: float = 60.0,
    max_idle_capabilities: int = 10
) -> CapabilityLifecycleManager:
    """Factory function to create lifecycle manager."""
    return CapabilityLifecycleManager(
        idle_timeout=idle_timeout,
        health_check_interval=health_check_interval,
        max_idle_capabilities=max_idle_capabilities
    )


import numpy as np  # For health statistics
