"""
Resource-Aware Orchestration for BIODISC

Implements orchestration that respects resource constraints:
- Memory budgets and management
- Computational costs and optimization
- Time constraints and scheduling
- Energy efficiency considerations

This enables BIODISC to operate effectively within resource limits.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import time
import psutil
import gc
import numpy as np


class ResourceType(Enum):
    """Types of resources that can be constrained."""
    MEMORY = "memory"          # RAM usage in MB
    COMPUTE = "compute"        # CPU/GPU utilization
    TIME = "time"              # Execution time in seconds
    ENERGY = "energy"          # Energy consumption (estimated)
    IO = "io"                  # I/O operations
    NETWORK = "network"        # Network bandwidth


class ResourceState(Enum):
    """States of resource utilization."""
    ABUNDANT = "abundant"      # Plenty of resources available
    ADEQUATE = "adequate"      # Sufficient resources
    CONSTRAINED = "constrained"  # Limited resources
    CRITICAL = "critical"      # Severely limited resources


@dataclass
class ResourceConstraint:
    """A constraint on a resource type."""
    resource_type: ResourceType
    limit: float  # Maximum allowed value
    priority: float  # 0.0 to 1.0, higher = more important
    flexible: bool = True  # Can constraint be relaxed?
    current_usage: float = 0.0


@dataclass
class ResourceRequirement:
    """Resource requirement for a capability."""
    capability_name: str
    memory_mb: float
    compute_units: float  # Normalized compute units
    estimated_time: float  # Seconds
    io_operations: int = 0
    network_mb: float = 0.0


@dataclass
class ResourceProfile:
    """Resource usage profile for a capability."""
    capability_name: str
    average_memory_mb: float
    peak_memory_mb: float
    average_time: float
    compute_intensity: float  # 0.0 to 1.0
    io_intensity: float  # 0.0 to 1.0
    sample_count: int = 0


class ResourceMonitor:
    """Monitor system resource usage."""

    def __init__(self):
        self.process = psutil.Process()
        self.monitoring_history: List[Dict[str, Any]] = []
        self.baseline_usage = self._get_baseline_usage()

    def _get_baseline_usage(self) -> Dict[str, float]:
        """Get baseline resource usage."""
        return {
            "memory_mb": self.process.memory_info().rss / 1024 / 1024,
            "cpu_percent": self.process.cpu_percent(),
        }

    def get_current_usage(self) -> Dict[ResourceType, float]:
        """Get current resource usage."""
        memory_info = self.process.memory_info()

        return {
            ResourceType.MEMORY: memory_info.rss / 1024 / 1024,  # MB
            ResourceType.COMPUTE: self.process.cpu_percent() / 100.0,
            ResourceType.TIME: 0.0,  # Time is tracked separately
            ResourceType.IO: 0.0,  # IO is estimated
            ResourceType.NETWORK: 0.0,  # Network is estimated
        }

    def get_resource_state(
        self,
        constraints: Dict[ResourceType, ResourceConstraint]
    ) -> ResourceState:
        """Determine overall resource state."""
        current_usage = self.get_current_usage()

        # Check each constraint
        utilization_levels = []
        for resource_type, constraint in constraints.items():
            if resource_type in current_usage:
                utilization = current_usage[resource_type] / constraint.limit
                utilization_levels.append(utilization)

        if not utilization_levels:
            return ResourceState.ADEQUATE

        avg_utilization = np.mean(utilization_levels)

        if avg_utilization < 0.5:
            return ResourceState.ABUNDANT
        elif avg_utilization < 0.8:
            return ResourceState.ADEQUATE
        elif avg_utilization < 0.95:
            return ResourceState.CONSTRAINED
        else:
            return ResourceState.CRITICAL

    def record_usage(self, operation: str, duration: float) -> None:
        """Record resource usage for an operation."""
        current = self.get_current_usage()

        self.monitoring_history.append({
            "operation": operation,
            "timestamp": time.time(),
            "duration": duration,
            "memory_mb": current[ResourceType.MEMORY],
            "compute": current[ResourceType.COMPUTE],
        })

    def get_memory_pressure(self) -> float:
        """Get current memory pressure (0.0 to 1.0)."""
        # Get system memory info
        system_memory = psutil.virtual_memory()

        # Memory pressure is based on both process and system usage
        process_memory = self.process.memory_info().rss
        system_pressure = system_memory.percent / 100.0

        return min(1.0, system_pressure)


class ResourceEstimator:
    """Estimate resource requirements for capabilities."""

    def __init__(self):
        # Historical data for resource requirements
        self.resource_profiles: Dict[str, ResourceProfile] = {
            "knowledge_retrieval": ResourceProfile(
                capability_name="knowledge_retrieval",
                average_memory_mb=100.0,
                peak_memory_mb=200.0,
                average_time=2.0,
                compute_intensity=0.2,
                io_intensity=0.8,
                sample_count=100
            ),
            "causal_reasoning": ResourceProfile(
                capability_name="causal_reasoning",
                average_memory_mb=512.0,
                peak_memory_mb=1024.0,
                average_time=15.0,
                compute_intensity=0.8,
                io_intensity=0.3,
                sample_count=50
            ),
            "abstraction": ResourceProfile(
                capability_name="abstraction",
                average_memory_mb=256.0,
                peak_memory_mb=512.0,
                average_time=10.0,
                compute_intensity=0.6,
                io_intensity=0.2,
                sample_count=75
            ),
            "synthesis": ResourceProfile(
                capability_name="synthesis",
                average_memory_mb=384.0,
                peak_memory_mb=768.0,
                average_time=12.0,
                compute_intensity=0.7,
                io_intensity=0.4,
                sample_count=60
            ),
            "protein_structure": ResourceProfile(
                capability_name="protein_structure",
                average_memory_mb=2048.0,
                peak_memory_mb=4096.0,
                average_time=30.0,
                compute_intensity=0.95,
                io_intensity=0.1,
                sample_count=20
            ),
        }

    def estimate_requirement(self, capability_name: str) -> ResourceRequirement:
        """Estimate resource requirement for a capability."""
        if capability_name in self.resource_profiles:
            profile = self.resource_profiles[capability_name]
            return ResourceRequirement(
                capability_name=capability_name,
                memory_mb=profile.average_memory_mb,
                compute_units=profile.compute_intensity,
                estimated_time=profile.average_time,
                io_operations=int(100 * profile.io_intensity),
                network_mb=0.0
            )

        # Default estimation
        return ResourceRequirement(
            capability_name=capability_name,
            memory_mb=256.0,
            compute_units=0.5,
            estimated_time=5.0,
            io_operations=10,
            network_mb=0.0
        )

    def record_actual_usage(
        self,
        capability_name: str,
        memory_mb: float,
        time_seconds: float,
        compute_intensity: float
    ) -> None:
        """Record actual resource usage for learning."""
        if capability_name not in self.resource_profiles:
            self.resource_profiles[capability_name] = ResourceProfile(
                capability_name=capability_name,
                average_memory_mb=memory_mb,
                peak_memory_mb=memory_mb,
                average_time=time_seconds,
                compute_intensity=compute_intensity,
                io_intensity=0.3,
                sample_count=1
            )
        else:
            # Update profile with new data
            profile = self.resource_profiles[capability_name]
            n = profile.sample_count

            # Update averages
            profile.average_memory_mb = (
                (profile.average_memory_mb * n + memory_mb) / (n + 1)
            )
            profile.peak_memory_mb = max(profile.peak_memory_mb, memory_mb)
            profile.average_time = (
                (profile.average_time * n + time_seconds) / (n + 1)
            )
            profile.compute_intensity = (
                (profile.compute_intensity * n + compute_intensity) / (n + 1)
            )
            profile.sample_count = n + 1


class ResourceAwareOrchestrator:
    """
    Orchestrator that respects resource constraints.

    Features:
    - Resource monitoring and estimation
    - Capability selection based on resource availability
    - Execution scaling based on constraints
    - Graceful degradation under resource pressure
    """

    def __init__(self):
        self.monitor = ResourceMonitor()
        self.estimator = ResourceEstimator()
        self.constraints: Dict[ResourceType, ResourceConstraint] = {}
        self.orchestration_history: List[Dict[str, Any]] = []

        # Set default constraints
        self._set_default_constraints()

    def _set_default_constraints(self) -> None:
        """Set default resource constraints."""
        self.constraints = {
            ResourceType.MEMORY: ResourceConstraint(
                resource_type=ResourceType.MEMORY,
                limit=8192.0,  # 8 GB
                priority=0.9,
                flexible=False
            ),
            ResourceType.TIME: ResourceConstraint(
                resource_type=ResourceType.TIME,
                limit=120.0,  # 2 minutes
                priority=0.8,
                flexible=True
            ),
            ResourceType.COMPUTE: ResourceConstraint(
                resource_type=ResourceType.COMPUTE,
                limit=0.8,  # 80% CPU
                priority=0.7,
                flexible=True
            ),
        }

    def set_constraint(self, constraint: ResourceConstraint) -> None:
        """Set a resource constraint."""
        self.constraints[constraint.resource_type] = constraint

    def orchestrate(
        self,
        capabilities: List[str],
        query: str,
        user_constraints: Optional[Dict[ResourceType, float]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate capabilities within resource constraints.

        Args:
            capabilities: List of available capabilities
            query: User query
            user_constraints: Optional user-specified constraints

        Returns:
            Orchestration result with resource usage metadata
        """
        # Apply user constraints
        if user_constraints:
            for resource_type, limit in user_constraints.items():
                if resource_type in self.constraints:
                    self.constraints[resource_type].limit = limit

        # Get current resource state
        resource_state = self.monitor.get_resource_state(self.constraints)

        # Select capabilities based on resources
        selected_capabilities = self._select_capabilities(
            capabilities,
            resource_state
        )

        # Estimate resource requirements
        requirements = [
            self.estimator.estimate_requirement(cap)
            for cap in selected_capabilities
        ]

        # Check feasibility
        feasible = self._check_feasibility(requirements)

        if not feasible:
            # Scale down or reduce capabilities
            selected_capabilities, requirements = self._scale_to_fit(
                selected_capabilities,
                requirements
            )

        # Execute capabilities
        execution_start = time.time()
        results = self._execute_capabilities(
            selected_capabilities,
            query,
            requirements
        )
        execution_time = time.time() - execution_start

        # Record resource usage
        self.monitor.record_usage("orchestration", execution_time)

        # Record orchestration
        orchestration_record = {
            "query": query,
            "selected_capabilities": selected_capabilities,
            "resource_state": resource_state.value,
            "execution_time": execution_time,
            "estimated_requirements": [req.__dict__ for req in requirements],
            "timestamp": time.time()
        }
        self.orchestration_history.append(orchestration_record)

        return {
            "results": results,
            "resource_state": resource_state.value,
            "execution_time": execution_time,
            "capabilities_executed": selected_capabilities,
            "resource_metadata": {
                "memory_used_mb": self.monitor.get_current_usage()[ResourceType.MEMORY],
                "constraints_respected": feasible,
                "scaling_applied": len(selected_capabilities) < len(capabilities)
            }
        }

    def _select_capabilities(
        self,
        available: List[str],
        resource_state: ResourceState
    ) -> List[str]:
        """Select capabilities based on resource availability."""
        # In constrained state, prioritize essential capabilities
        if resource_state in [ResourceState.CONSTRAINED, ResourceState.CRITICAL]:
            essential = ["knowledge_retrieval", "causal_reasoning"]
            selected = [cap for cap in essential if cap in available]

            # Add others if space permits
            if resource_state == ResourceState.CONSTRAINED:
                additional = [cap for cap in available if cap not in essential][:2]
                selected.extend(additional)

            return selected

        # In abundant state, select all capabilities
        return available

    def _check_feasibility(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if requirements fit within constraints."""
        # Sum requirements
        total_memory = sum(req.memory_mb for req in requirements)
        total_time = sum(req.estimated_time for req in requirements)
        total_compute = sum(req.compute_units for req in requirements) / len(requirements)

        # Check against constraints
        memory_ok = total_memory <= self.constraints[ResourceType.MEMORY].limit
        time_ok = total_time <= self.constraints[ResourceType.TIME].limit
        compute_ok = total_compute <= self.constraints[ResourceType.COMPUTE].limit

        return memory_ok and time_ok and compute_ok

    def _scale_to_fit(
        self,
        capabilities: List[str],
        requirements: List[ResourceRequirement]
    ) -> Tuple[List[str], List[ResourceRequirement]]:
        """Scale down capabilities to fit within constraints."""
        # Sort by priority (time and resource efficiency)
        priority_order = sorted(
            zip(capabilities, requirements),
            key=lambda x: x[1].estimated_time
        )

        scaled_capabilities = []
        scaled_requirements = []

        # Add capabilities until constraints are met
        for cap, req in priority_order:
            test_capabilities = scaled_capabilities + [cap]
            test_requirements = scaled_requirements + [req]

            if self._check_feasibility(test_requirements):
                scaled_capabilities.append(cap)
                scaled_requirements.append(req)
            else:
                break

        return scaled_capabilities, scaled_requirements

    def _execute_capabilities(
        self,
        capabilities: List[str],
        query: str,
        requirements: List[ResourceRequirement]
    ) -> Dict[str, Any]:
        """Execute capabilities with resource awareness."""
        results = {}

        for i, (capability, requirement) in enumerate(zip(capabilities, requirements)):
            # Monitor memory pressure
            memory_pressure = self.monitor.get_memory_pressure()

            if memory_pressure > 0.9:
                # Trigger garbage collection
                gc.collect()

            # Check if we have enough memory
            current_memory = self.monitor.get_current_usage()[ResourceType.MEMORY]
            available_memory = self.constraints[ResourceType.MEMORY].limit - current_memory

            if available_memory < requirement.memory_mb * 0.5:
                # Not enough memory - skip or use degraded version
                results[capability] = {
                    "success": False,
                    "reason": "insufficient_memory",
                    "result": None
                }
                continue

            # Execute capability
            try:
                start_time = time.time()

                # In real system, would call actual capability
                result = self._simulate_capability_execution(capability, query)

                execution_time = time.time() - start_time

                # Record actual usage
                self.estimator.record_actual_usage(
                    capability,
                    requirement.memory_mb * (0.8 + np.random.random() * 0.4),  # Variance
                    execution_time,
                    requirement.compute_units
                )

                results[capability] = {
                    "success": True,
                    "result": result
                }

            except Exception as e:
                results[capability] = {
                    "success": False,
                    "reason": str(e),
                    "result": None
                }

        return results

    def _simulate_capability_execution(self, capability: str, query: str) -> Any:
        """Simulate capability execution for testing."""
        # In real system, would call actual capability
        return f"Result from {capability} for query: {query[:50]}..."

    def get_resource_report(self) -> Dict[str, Any]:
        """Get comprehensive resource usage report."""
        current_usage = self.monitor.get_current_usage()
        resource_state = self.monitor.get_resource_state(self.constraints)

        return {
            "current_usage": {rt.value: usage for rt, usage in current_usage.items()},
            "resource_state": resource_state.value,
            "constraints": {
                rt.value: {
                    "limit": cons.limit,
                    "priority": cons.priority,
                    "flexible": cons.flexible
                }
                for rt, cons in self.constraints.items()
            },
            "monitoring_samples": len(self.monitor.monitoring_history),
            "orchestrations_performed": len(self.orchestration_history),
            "average_orchestration_time": np.mean([
                record["execution_time"]
                for record in self.orchestration_history
            ]) if self.orchestration_history else 0.0
        }

    def optimize_constraints(self) -> None:
        """Optimize constraints based on historical usage."""
        if not self.orchestration_history:
            return

        # Analyze historical usage
        memory_usage = [
            record["estimated_requirements"][0].get("memory_mb", 0)
            for record in self.orchestration_history
            if record["estimated_requirements"]
        ]

        if memory_usage:
            avg_memory = np.mean(memory_usage)
            max_memory = np.max(memory_usage)

            # Set memory limit to 2x average, but at least max
            recommended_limit = max(max_memory, avg_memory * 2)

            self.constraints[ResourceType.MEMORY].limit = recommended_limit


class AdaptiveResourceScaler:
    """
    Dynamically scale resource allocation based on conditions.

    Monitors system state and adjusts allocation accordingly.
    """

    def __init__(self, orchestrator: ResourceAwareOrchestrator):
        self.orchestrator = orchestrator
        self.scaling_history: List[Dict[str, Any]] = []

    def scale_execution(
        self,
        capabilities: List[str],
        query: str
    ) -> Dict[str, Any]:
        """
        Scale execution based on current conditions.

        Implements dynamic scaling strategies:
        - Parallel execution when resources abundant
        - Sequential execution when constrained
        - Degraded execution when critical
        """
        resource_state = self.orchestrator.monitor.get_resource_state(
            self.orchestrator.constraints
        )

        scaling_strategy = self._select_scaling_strategy(resource_state)

        start_time = time.time()

        if scaling_strategy == "parallel":
            result = self._execute_parallel(capabilities, query)
        elif scaling_strategy == "sequential":
            result = self._execute_sequential(capabilities, query)
        else:  # degraded
            result = self._execute_degraded(capabilities, query)

        execution_time = time.time() - start_time

        # Record scaling
        self.scaling_history.append({
            "strategy": scaling_strategy,
            "resource_state": resource_state.value,
            "execution_time": execution_time,
            "timestamp": time.time()
        })

        result["scaling_strategy"] = scaling_strategy
        result["resource_state"] = resource_state.value

        return result

    def _select_scaling_strategy(self, resource_state: ResourceState) -> str:
        """Select scaling strategy based on resource state."""
        if resource_state == ResourceState.ABUNDANT:
            return "parallel"
        elif resource_state == ResourceState.ADEQUATE:
            return "sequential"
        else:
            return "degraded"

    def _execute_parallel(
        self,
        capabilities: List[str],
        query: str
    ) -> Dict[str, Any]:
        """Execute capabilities in parallel."""
        # Simplified - in real system would use actual parallelization
        results = {}
        for cap in capabilities:
            results[cap] = self.orchestrator._simulate_capability_execution(cap, query)
        return {"results": results}

    def _execute_sequential(
        self,
        capabilities: List[str],
        query: str
    ) -> Dict[str, Any]:
        """Execute capabilities sequentially."""
        results = {}
        for cap in capabilities:
            results[cap] = self.orchestrator._simulate_capability_execution(cap, query)
        return {"results": results}

    def _execute_degraded(
        self,
        capabilities: List[str],
        query: str
    ) -> Dict[str, Any]:
        """Execute capabilities in degraded mode."""
        # Only execute essential capabilities
        essential = [cap for cap in capabilities if cap in ["knowledge_retrieval", "causal_reasoning"]]

        results = {}
        for cap in essential:
            results[cap] = self.orchestrator._simulate_capability_execution(cap, query)

        results["degraded_mode"] = True
        return {"results": results}


def create_resource_aware_orchestrator() -> ResourceAwareOrchestrator:
    """Factory function to create resource-aware orchestrator."""
    return ResourceAwareOrchestrator()
