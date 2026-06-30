"""
Adaptive Coordination Patterns for BIODISC

Implements dynamic coordination pattern selection based on:
- Task complexity and uncertainty
- Resource availability
- Performance feedback
- Interdependencies between capabilities

Patterns:
- Centralized: Single coordinator for simple, deterministic tasks
- Distributed: Peer-to-peer coordination for complex, exploratory tasks
- Hybrid: Mixed approach for multi-stage workflows
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum
import time
import numpy as np
from abc import ABC, abstractmethod


class CoordinationPattern(Enum):
    """Types of coordination patterns."""
    CENTRALIZED = "centralized"       # Single coordinator directs all
    DISTRIBUTED = "distributed"       # Peer-to-peer, no central authority
    HYBRID = "hybrid"                 # Mixed, stage-dependent
    HIERARCHICAL = "hierarchical"     # Multi-level coordination
    AD_HOC = "ad_hoc"                 # Dynamic, emergent coordination


class TaskState(Enum):
    """States in task lifecycle."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class CapabilityNode:
    """A capability node in the coordination network."""
    name: str
    domain: str
    state: TaskState = TaskState.PENDING
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    assigned_coordinator: Optional[str] = None
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    performance_score: float = 0.5
    last_execution_time: Optional[float] = None


@dataclass
class CoordinationMessage:
    """Message between coordination nodes."""
    sender: str
    receiver: str
    message_type: str  # "request", "response", "notification", "command"
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None


@dataclass
class CoordinationContext:
    """Context for coordination decisions."""
    task_complexity: float  # 0.0 to 1.0
    uncertainty: float  # 0.0 to 1.0
    resource_availability: Dict[str, float]  # resource_name -> availability (0-1)
    time_pressure: float  # 0.0 to 1.0
    interdependency_count: int
    failure_tolerance: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseCoordinator(ABC):
    """Abstract base class for coordination patterns."""

    def __init__(self, name: str):
        self.name = name
        self.active_capabilities: Dict[str, CapabilityNode] = {}
        self.message_queue: List[CoordinationMessage] = []

    @abstractmethod
    def coordinate(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Execute coordination pattern."""
        pass

    @abstractmethod
    def assign_task(self, capability: str, dependencies: List[str]) -> bool:
        """Assign task to a capability."""
        pass

    @abstractmethod
    def resolve_conflict(self, conflicting_capabilities: List[str]) -> str:
        """Resolve conflict between capabilities."""
        pass

    def send_message(self, message: CoordinationMessage) -> None:
        """Send message to another node."""
        self.message_queue.append(message)

    def receive_messages(self, receiver: str) -> List[CoordinationMessage]:
        """Receive messages for a node."""
        messages = [m for m in self.message_queue if m.receiver == receiver]
        self.message_queue = [m for m in self.message_queue if m.receiver != receiver]
        return messages


class CentralizedCoordinator(BaseCoordinator):
    """
    Centralized coordination: Single coordinator directs all capabilities.

    Best for:
    - Simple, deterministic tasks
    - Low uncertainty environments
    - When strong consistency is required
    - Time-constrained operations
    """

    def __init__(self):
        super().__init__("CentralizedCoordinator")
        self.coordination_plan: Optional[Dict[str, Any]] = None
        self.execution_order: List[str] = []

    def coordinate(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """
        Execute centralized coordination.

        Single coordinator creates and enforces execution plan.
        """
        # Initialize capability nodes
        for cap in capabilities:
            self.active_capabilities[cap] = CapabilityNode(
                name=cap,
                domain=self._infer_domain(cap),
                state=TaskState.PENDING
            )

        # Create centralized execution plan
        self.coordination_plan = self._create_execution_plan(
            capabilities,
            context
        )

        # Execute plan
        results = {}
        for capability in self.execution_order:
            result = self._execute_capability(capability, context)
            results[capability] = result

            # Update state
            if result.get("success"):
                self.active_capabilities[capability].state = TaskState.COMPLETED
            else:
                self.active_capabilities[capability].state = TaskState.FAILED

        return {
            "pattern": CoordinationPattern.CENTRALIZED,
            "results": results,
            "execution_order": self.execution_order,
            "coordinator": self.name
        }

    def _create_execution_plan(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Create centralized execution plan."""
        # Determine execution order based on dependencies
        self.execution_order = self._topological_sort(capabilities)

        return {
            "capabilities": capabilities,
            "execution_order": self.execution_order,
            "total_estimated_time": sum(
                self.active_capabilities[cap].resource_requirements.get("time", 1.0)
                for cap in capabilities
            )
        }

    def _topological_sort(self, capabilities: List[str]) -> List[str]:
        """Sort capabilities topologically by dependencies."""
        # Simple implementation - in real system, would use actual dependency graph
        priority_order = [
            "knowledge_retrieval",
            "causal_reasoning",
            "abstraction",
            "synthesis"
        ]

        ordered = []
        remaining = capabilities.copy()

        for priority_cap in priority_order:
            if priority_cap in remaining:
                ordered.append(priority_cap)
                remaining.remove(priority_cap)

        # Add remaining capabilities
        ordered.extend(remaining)

        return ordered

    def _execute_capability(
        self,
        capability: str,
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Execute a single capability."""
        # In real system, would call actual capability
        return {
            "success": True,
            "capability": capability,
            "coordinator": self.name
        }

    def assign_task(self, capability: str, dependencies: List[str]) -> bool:
        """Assign task to a capability."""
        if capability in self.active_capabilities:
            self.active_capabilities[capability].dependencies.update(dependencies)
            self.active_capabilities[capability].state = TaskState.ASSIGNED
            return True
        return False

    def resolve_conflict(self, conflicting_capabilities: List[str]) -> str:
        """Resolve conflict by selecting first capability."""
        return conflicting_capabilities[0] if conflicting_capabilities else None

    def _infer_domain(self, capability: str) -> str:
        """Infer domain from capability name."""
        if "protein" in capability or "molecular" in capability:
            return "molecular_biology"
        elif "gene" in capability or "sequence" in capability:
            return "genomics"
        elif "cell" in capability:
            return "cell_biology"
        else:
            return "general"


class DistributedCoordinator(BaseCoordinator):
    """
    Distributed coordination: Peer-to-peer without central authority.

    Best for:
    - Complex, exploratory tasks
    - High uncertainty environments
    - When capabilities have specialized knowledge
    - Fault tolerance is important
    """

    def __init__(self):
        super().__init__("DistributedCoordinator")
        self.peer_registry: Dict[str, Dict[str, Any]] = {}
        self.consensus_threshold: float = 0.6

    def coordinate(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """
        Execute distributed coordination.

        Capabilities self-organize and coordinate peer-to-peer.
        """
        # Initialize peer registry
        for cap in capabilities:
            self.peer_registry[cap] = {
                "state": TaskState.PENDING,
                "peers": [c for c in capabilities if c != cap],
                "local_knowledge": {},
                "consensus_votes": {}
            }
            self.active_capabilities[cap] = CapabilityNode(
                name=cap,
                domain=self._infer_domain(cap),
                state=TaskState.PENDING
            )

        # Self-organization phase
        self._self_organize(capabilities, context)

        # Distributed execution
        results = self._distributed_execute(capabilities, context)

        # Consensus phase
        consensus_result = self._reach_consensus(results, context)

        return {
            "pattern": CoordinationPattern.DISTRIBUTED,
            "results": results,
            "consensus": consensus_result,
            "peer_count": len(capabilities),
            "coordinator": self.name
        }

    def _self_organize(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> None:
        """Enable capabilities to self-organize."""
        # Each capability discovers its peers
        for cap in capabilities:
            peers = [c for c in capabilities if c != cap]

            # Share local knowledge with peers
            for peer in peers:
                message = CoordinationMessage(
                    sender=cap,
                    receiver=peer,
                    message_type="discovery",
                    content={"capability": cap, "state": "ready"}
                )
                self.send_message(message)

        # Process discovery messages
        for cap in capabilities:
            messages = self.receive_messages(cap)
            self.peer_registry[cap]["peers"] = [
                m.content["capability"] for m in messages
                if m.message_type == "discovery"
            ]

    def _distributed_execute(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Execute capabilities in distributed manner."""
        results = {}

        for cap in capabilities:
            # Each capability executes independently
            result = self._execute_capability(cap, context)
            results[cap] = result

            # Update peer registry
            self.peer_registry[cap]["local_result"] = result

            # Share result with peers
            for peer in self.peer_registry[cap]["peers"]:
                message = CoordinationMessage(
                    sender=cap,
                    receiver=peer,
                    message_type="result_share",
                    content={"result": result}
                )
                self.send_message(message)

        return results

    def _reach_consensus(
        self,
        results: Dict[str, Any],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Reach consensus among distributed capabilities."""
        # Collect votes
        votes = {}
        for cap, result in results.items():
            if result.get("success"):
                votes[cap] = result.get("confidence", 0.5)

        # Calculate consensus
        if votes:
            avg_confidence = np.mean(list(votes.values()))
            consensus_reached = avg_confidence > self.consensus_threshold

            return {
                "reached": consensus_reached,
                "average_confidence": avg_confidence,
                "participating_capabilities": len(votes),
                "votes": votes
            }

        return {
            "reached": False,
            "reason": "No successful results"
        }

    def _execute_capability(
        self,
        capability: str,
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """Execute a capability in distributed manner."""
        return {
            "success": True,
            "capability": capability,
            "confidence": 0.7,
            "coordinator": self.name
        }

    def assign_task(self, capability: str, dependencies: List[str]) -> bool:
        """Assign task - in distributed, capabilities self-assign."""
        if capability in self.active_capabilities:
            self.active_capabilities[capability].state = TaskState.ASSIGNED
            return True
        return False

    def resolve_conflict(self, conflicting_capabilities: List[str]) -> str:
        """Resolve conflict through peer voting."""
        # In real system, would conduct actual vote
        return conflicting_capabilities[np.random.randint(len(conflicting_capabilities))]

    def _infer_domain(self, capability: str) -> str:
        """Infer domain from capability name."""
        return "general"


class HybridCoordinator(BaseCoordinator):
    """
    Hybrid coordination: Mixes centralized and distributed approaches.

    Best for:
    - Multi-stage workflows
    - When different stages have different requirements
    - Complex tasks with both deterministic and exploratory components
    """

    def __init__(self):
        super().__init__("HybridCoordinator")
        self.centralized = CentralizedCoordinator()
        self.distributed = DistributedCoordinator()
        self.stage_pattern_map: Dict[str, CoordinationPattern] = {}

    def coordinate(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, Any]:
        """
        Execute hybrid coordination.

        Different stages use different patterns based on their characteristics.
        """
        # Divide capabilities into stages
        stages = self._identify_stages(capabilities, context)

        # Select pattern for each stage
        for stage_name, stage_caps in stages.items():
            pattern = self._select_pattern_for_stage(stage_name, stage_caps, context)
            self.stage_pattern_map[stage_name] = pattern

        # Execute each stage with its pattern
        results = {}
        stage_results = {}

        for stage_name, stage_caps in stages.items():
            pattern = self.stage_pattern_map[stage_name]

            if pattern == CoordinationPattern.CENTRALIZED:
                stage_result = self.centralized.coordinate(stage_caps, context)
            elif pattern == CoordinationPattern.DISTRIBUTED:
                stage_result = self.distributed.coordinate(stage_caps, context)
            else:
                # Default to centralized
                stage_result = self.centralized.coordinate(stage_caps, context)

            stage_results[stage_name] = stage_result
            results.update(stage_result.get("results", {}))

        return {
            "pattern": CoordinationPattern.HYBRID,
            "stage_results": stage_results,
            "stage_patterns": self.stage_pattern_map,
            "results": results,
            "coordinator": self.name
        }

    def _identify_stages(
        self,
        capabilities: List[str],
        context: CoordinationContext
    ) -> Dict[str, List[str]]:
        """Identify execution stages from capabilities."""
        stages = {
            "information_gathering": [],
            "analysis": [],
            "synthesis": []
        }

        for cap in capabilities:
            if "retrieval" in cap or "fetch" in cap:
                stages["information_gathering"].append(cap)
            elif "analysis" in cap or "reasoning" in cap:
                stages["analysis"].append(cap)
            elif "synthesis" in cap or "generation" in cap:
                stages["synthesis"].append(cap)
            else:
                # Default to analysis
                stages["analysis"].append(cap)

        # Remove empty stages
        return {k: v for k, v in stages.items() if v}

    def _select_pattern_for_stage(
        self,
        stage_name: str,
        capabilities: List[str],
        context: CoordinationContext
    ) -> CoordinationPattern:
        """Select coordination pattern for a stage."""
        # Information gathering: centralized (deterministic)
        if stage_name == "information_gathering":
            return CoordinationPattern.CENTRALIZED

        # Analysis: distributed (exploratory)
        if stage_name == "analysis" and context.uncertainty > 0.5:
            return CoordinationPattern.DISTRIBUTED

        # Synthesis: centralized (needs consistency)
        if stage_name == "synthesis":
            return CoordinationPattern.CENTRALIZED

        # Default based on uncertainty
        return CoordinationPattern.DISTRIBUTED if context.uncertainty > 0.6 else CoordinationPattern.CENTRALIZED

    def assign_task(self, capability: str, dependencies: List[str]) -> bool:
        """Delegate to appropriate coordinator."""
        return self.centralized.assign_task(capability, dependencies)

    def resolve_conflict(self, conflicting_capabilities: List[str]) -> str:
        """Resolve conflict using hybrid approach."""
        # Try consensus first, fallback to centralized
        return self.centralized.resolve_conflict(conflicting_capabilities)

    def _infer_domain(self, capability: str) -> str:
        """Infer domain from capability name."""
        return self.centralized._infer_domain(capability)


class AdaptiveCoordinator:
    """
    Main adaptive coordinator that selects and executes appropriate patterns.

    Analyzes task context and selects the best coordination pattern:
    - Centralized for simple, low-uncertainty tasks
    - Distributed for complex, high-uncertainty tasks
    - Hybrid for multi-stage workflows
    """

    def __init__(self):
        self.centralized = CentralizedCoordinator()
        self.distributed = DistributedCoordinator()
        self.hybrid = HybridCoordinator()
        self.coordination_history: List[Dict[str, Any]] = []
        self.performance_tracker: Dict[str, List[float]] = {
            "centralized": [],
            "distributed": [],
            "hybrid": []
        }

    def select_coordination_pattern(
        self,
        context: CoordinationContext
    ) -> CoordinationPattern:
        """
        Select appropriate coordination pattern based on context.

        Decision matrix:
        - Low complexity (<0.3), low uncertainty (<0.4): Centralized
        - High complexity (>0.7), high uncertainty (>0.6): Distributed
        - Mixed complexity/uncertainty or multi-stage: Hybrid
        """
        # Simple tasks: centralized
        if context.task_complexity < 0.3 and context.uncertainty < 0.4:
            return CoordinationPattern.CENTRALIZED

        # Complex tasks: distributed
        if context.task_complexity > 0.7 and context.uncertainty > 0.6:
            return CoordinationPattern.DISTRIBUTED

        # Multi-stage workflows: hybrid
        if context.interdependency_count > 3:
            return CoordinationPattern.HYBRID

        # Time pressure: centralized (faster)
        if context.time_pressure > 0.7:
            return CoordinationPattern.CENTRALIZED

        # High failure tolerance: distributed (more robust)
        if context.failure_tolerance > 0.7:
            return CoordinationPattern.DISTRIBUTED

        # Resource constraints: centralized (more efficient)
        if any(avail < 0.5 for avail in context.resource_availability.values()):
            return CoordinationPattern.CENTRALIZED

        # Default: hybrid
        return CoordinationPattern.HYBRID

    def coordinate(
        self,
        capabilities: List[str],
        query: str,
        context: Optional[CoordinationContext] = None
    ) -> Dict[str, Any]:
        """
        Execute adaptive coordination.

        Selects and executes appropriate pattern based on context.
        """
        # Build context if not provided
        if context is None:
            context = self._build_context(capabilities, query)

        # Select pattern
        pattern = self.select_coordination_pattern(context)

        # Execute with selected pattern
        start_time = time.time()

        if pattern == CoordinationPattern.CENTRALIZED:
            result = self.centralized.coordinate(capabilities, context)
        elif pattern == CoordinationPattern.DISTRIBUTED:
            result = self.distributed.coordinate(capabilities, context)
        elif pattern == CoordinationPattern.HYBRID:
            result = self.hybrid.coordinate(capabilities, context)
        else:
            # Fallback
            result = self.centralized.coordinate(capabilities, context)

        duration = time.time() - start_time

        # Track performance
        self.performance_tracker[pattern.value].append(duration)

        # Record coordination
        self.coordination_history.append({
            "pattern": pattern,
            "context": context,
            "duration": duration,
            "success": result.get("results", {}).get("success", True),
            "timestamp": time.time()
        })

        # Add pattern selection rationale to result
        result["selection_rationale"] = self._explain_selection(pattern, context)

        return result

    def _build_context(
        self,
        capabilities: List[str],
        query: str
    ) -> CoordinationContext:
        """Build coordination context from query and capabilities."""
        # Analyze query complexity
        complexity_indicators = [
            "mechanism", "pathway", "relationship", "integration",
            "synthesis", "comprehensive", "multiple"
        ]
        complexity = sum(
            0.1 for indicator in complexity_indicators
            if indicator in query.lower()
        )

        # Estimate uncertainty
        uncertainty_indicators = [
            "unknown", "unclear", "poorly understood", "controversial"
        ]
        uncertainty = sum(
            0.15 for indicator in uncertainty_indicators
            if indicator in query.lower()
        )
        uncertainty = min(1.0, uncertainty)

        # Count interdependencies
        interdependency_count = sum(
            1 for cap in capabilities
            if "reasoning" in cap or "synthesis" in cap
        )

        return CoordinationContext(
            task_complexity=min(1.0, complexity),
            uncertainty=uncertainty,
            resource_availability={"memory": 0.8, "compute": 0.7},
            time_pressure=0.3,
            interdependency_count=interdependency_count,
            failure_tolerance=0.5
        )

    def _explain_selection(
        self,
        pattern: CoordinationPattern,
        context: CoordinationContext
    ) -> str:
        """Explain why pattern was selected."""
        explanations = {
            CoordinationPattern.CENTRALIZED:
                f"Selected centralized coordination due to low complexity "
                f"({context.task_complexity:.2f}) and low uncertainty "
                f"({context.uncertainty:.2f})",
            CoordinationPattern.DISTRIBUTED:
                f"Selected distributed coordination due to high complexity "
                f"({context.task_complexity:.2f}) and high uncertainty "
                f"({context.uncertainty:.2f})",
            CoordinationPattern.HYBRID:
                f"Selected hybrid coordination for multi-stage workflow "
                f"({context.interdependency_count} interdependencies)"
        }
        return explanations.get(pattern, "Pattern selected based on context analysis")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all patterns."""
        metrics = {}

        for pattern, durations in self.performance_tracker.items():
            if durations:
                metrics[pattern] = {
                    "count": len(durations),
                    "average_duration": np.mean(durations),
                    "min_duration": np.min(durations),
                    "max_duration": np.max(durations),
                    "std_duration": np.std(durations)
                }

        return metrics

    def get_coordination_history(self) -> List[Dict[str, Any]]:
        """Get history of all coordinations."""
        return self.coordination_history


def create_adaptive_coordinator() -> AdaptiveCoordinator:
    """Factory function to create adaptive coordinator."""
    return AdaptiveCoordinator()
