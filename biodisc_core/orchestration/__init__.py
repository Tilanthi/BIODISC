"""
BIODISC Orchestration System

A comprehensive orchestration framework for AGI-inspired biological discovery.

Components:
- HierarchicalOrchestrator: Three-tier orchestration (strategic, tactical, operational)
- AdaptiveCoordinator: Dynamic coordination pattern selection
- ConflictResolver: Sophisticated conflict resolution between capabilities
- ResourceAwareOrchestrator: Resource-constrained orchestration
- CapabilityLifecycleManager: Lifecycle management for capabilities
- OrchestratorLearner: Closed-loop learning from outcomes
- IncrementalOrchestrator: Progressive refinement with early stopping
- PolicyDrivenOrchestrator: Declarative, customizable orchestration

Usage:
    from biodisc_core.orchestration import (
        create_unified_orchestrator,
        OrchestrationContext,
        CoordinationPattern,
        RefinementStage,
        QualityThreshold
    )

    orchestrator = create_unified_orchestrator()
    result = orchestrator.orchestrate(
        query="What causes protein misfolding?",
        capabilities=["knowledge_retrieval", "causal_reasoning", "synthesis"]
    )
"""

from .hierarchical import (
    HierarchicalOrchestrator,
    StrategicOrchestrator,
    TacticalOrchestrator,
    OperationalOrchestrator,
    OrchestrationContext,
    OrchestrationTier,
    TaskComplexity,
    StrategicObjective,
    TacticalPlan,
    OperationalTask,
    create_hierarchical_orchestrator
)

from .adaptive import (
    AdaptiveCoordinator,
    CentralizedCoordinator,
    DistributedCoordinator,
    HybridCoordinator,
    CoordinationPattern,
    TaskState,
    CapabilityNode,
    CoordinationMessage,
    CoordinationContext,
    create_adaptive_coordinator
)

from .conflict_resolution import (
    ComprehensiveConflictResolver,
    ConflictResolver,
    ConflictDetector,
    ConflictType,
    ResolutionStrategy,
    CapabilityOutput,
    Conflict,
    ResolutionResult,
    ExpertiseDatabase,
    UserPreferenceLearner,
    create_conflict_resolver
)

from .resource_aware import (
    ResourceAwareOrchestrator,
    ResourceMonitor,
    ResourceEstimator,
    AdaptiveResourceScaler,
    ResourceType,
    ResourceState,
    ResourceConstraint,
    ResourceRequirement,
    ResourceProfile,
    create_resource_aware_orchestrator
)

from .lifecycle import (
    CapabilityLifecycleManager,
    LifecycleState,
    HealthStatus,
    CapabilityMetadata,
    CapabilityInstance,
    LifecycleEvent,
    HealthChecker,
    create_lifecycle_manager
)

from .learning import (
    OrchestratorLearner,
    PolicyLearner,
    RewardCalculator,
    FeatureExtractor,
    AntiPatternDetector,
    LearningSignal,
    OrchestrationOutcome,
    LearningExample,
    PolicyUpdate,
    create_orchestrator_learner
)

from .incremental import (
    IncrementalOrchestrator,
    IncrementalExecutor,
    QualityEvaluator,
    RefinementStage,
    QualityThreshold,
    IncrementalResult,
    RefinementPlan,
    StreamingOrchestrator,
    create_incremental_orchestrator,
    create_refinement_plan
)

from .policy_driven import (
    PolicyDrivenOrchestrator,
    PolicyEngine,
    PolicyLoader,
    PolicyValidator,
    PolicyType,
    PolicyAction,
    PolicyRule,
    PolicySet,
    PolicyCondition,
    PolicyDecision,
    create_policy_driven_orchestrator
)


class UnifiedOrchestrator:
    """
    Unified orchestrator combining all orchestration systems.

    Provides a single interface to:
    - Hierarchical orchestration
    - Adaptive coordination
    - Conflict resolution
    - Resource awareness
    - Lifecycle management
    - Learning and adaptation
    - Incremental refinement
    - Policy-driven behavior
    """

    def __init__(
        self,
        enable_learning: bool = True,
        enable_incremental: bool = True,
        enable_policies: bool = True,
        policy_directory: Optional[str] = None
    ):
        # Core orchestration components
        self.hierarchical = create_hierarchical_orchestrator()
        self.adaptive = create_adaptive_coordinator()
        self.conflict_resolver = create_conflict_resolver()
        self.resource_aware = create_resource_aware_orchestrator()
        self.lifecycle = create_lifecycle_manager()

        # Optional components
        self.learner = create_orchestrator_learner() if enable_learning else None
        self.incremental = create_incremental_orchestrator() if enable_incremental else None
        self.policy_driven = create_policy_driven_orchestrator() if enable_policies else None

        # Load policies if specified
        if self.policy_driven and policy_directory:
            self.policy_driven.load_policies_from_directory(policy_directory)

        # Orchestration history
        self.orchestration_history: List[Dict[str, Any]] = []

    def orchestrate(
        self,
        query: str,
        capabilities: Optional[List[str]] = None,
        context: Optional[OrchestrationContext] = None,
        incremental: bool = False,
        quality_threshold: QualityThreshold = QualityThreshold.HIGH
    ) -> Dict[str, Any]:
        """
        Orchestrate a query using all orchestration systems.

        Args:
            query: User's query
            capabilities: Available capabilities (if None, uses all)
            context: Orchestration context (if None, creates default)
            incremental: Whether to use incremental refinement
            quality_threshold: Quality threshold for incremental

        Returns:
            Orchestration result with all system outputs
        """
        start_time = time.time()

        # Create context if not provided
        if context is None:
            context = OrchestrationContext(query=query)

        # Get available capabilities
        if capabilities is None:
            capabilities = self.lifecycle.get_active_capabilities()
            if not capabilities:
                # Activate default capabilities
                capabilities = [
                    "knowledge_retrieval",
                    "causal_reasoning",
                    "abstraction",
                    "synthesis"
                ]

        # Policy-driven capability selection if enabled
        if self.policy_driven:
            policy_result = self.policy_driven.orchestrate_with_policies(
                query,
                capabilities,
                ["centralized", "distributed", "hybrid"],
                {"query": query, "domain": context.domain}
            )

            if policy_result["policy_compliance"]:
                capabilities = policy_result["selected_capabilities"]

        # Incremental orchestration if requested
        if incremental and self.incremental:
            plan = create_refinement_plan(
                query=query,
                target_stage=RefinementStage.COMPREHENSIVE,
                quality_threshold=quality_threshold,
                max_time=120.0,
                early_stop=True
            )

            # Create iterator for incremental results
            incremental_results = []
            for result in self.incremental.orchestrate_incremental(
                query,
                plan,
                {"domain": context.domain}
            ):
                incremental_results.append(result)

            # Use final result
            final_result = incremental_results[-1] if incremental_results else None

            orchestration_result = {
                "incremental": True,
                "stages_completed": len(incremental_results),
                "final_quality": final_result.quality_score if final_result else 0.0,
                "results": [r.content for r in incremental_results],
                "progression": [r.stage.value for r in incremental_results]
            }

        else:
            # Standard orchestration using hierarchical approach
            hierarchical_result = self.hierarchical.orchestrate(
                query,
                capabilities,
                context
            )

            orchestration_result = {
                "incremental": False,
                "strategic": hierarchical_result["strategic"],
                "tactical": hierarchical_result["tactical"],
                "operational": hierarchical_result["operational"]
            }

        # Resource-aware execution
        resource_result = self.resource_aware.orchestrate(
            capabilities,
            query,
            context.resource_constraints
        )

        # Conflict resolution
        if "results" in orchestration_result:
            capability_outputs = [
                CapabilityOutput(
                    capability_name=cap,
                    result=result.get("result"),
                    confidence=result.get("confidence", 0.5),
                    domain=context.domain or "general",
                    expertise_score=0.7
                )
                for cap, result in orchestration_result["results"].items()
            ]

            conflict_result = self.conflict_resolver.process_outputs(
                capability_outputs,
                context.domain or "general"
            )

            orchestration_result["conflicts_resolved"] = conflict_result["conflicts_resolved"]

        # Learning from outcome
        if self.learner:
            outcome = OrchestrationOutcome(
                orchestration_id=f"orch_{int(time.time()*1000)}",
                query=query,
                capabilities_used=capabilities,
                coordination_pattern="adaptive",
                start_time=start_time,
                end_time=time.time(),
                success=True,
                quality_score=orchestration_result.get("final_quality", 0.8)
            )

            # Extract features
            features = self.learner.feature_extractor.extract_features(
                query,
                capabilities,
                context.resource_constraints
            )

            # Learn from outcome
            self.learner.learn_from_outcome(outcome, features)

        # Record orchestration
        orchestration_result["total_time"] = time.time() - start_time
        orchestration_result["resource_usage"] = resource_result["resource_metadata"]

        self.orchestration_history.append(orchestration_result)

        return orchestration_result

    def register_capability(
        self,
        name: str,
        executor: Any,
        domain: str = "general",
        description: str = ""
    ) -> None:
        """Register a capability with the orchestrator."""
        metadata = CapabilityMetadata(
            name=name,
            module_path="",
            domain=domain,
            description=description
        )

        self.lifecycle.register_capability(metadata)
        self.hierarchical.register_capability(name, executor)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all orchestration systems."""
        status = {
            "hierarchical": self.hierarchical.get_performance_metrics(),
            "adaptive": self.adaptive.get_performance_metrics(),
            "conflict_resolution": self.conflict_resolver.get_conflict_statistics(),
            "resource_aware": self.resource_aware.get_resource_report(),
            "lifecycle": self.lifecycle.get_system_status(),
            "orchestrations_performed": len(self.orchestration_history)
        }

        if self.learner:
            status["learning"] = self.learner.get_learning_summary()

        if self.incremental:
            status["incremental"] = self.incremental.get_refinement_statistics()

        if self.policy_driven:
            status["policy_driven"] = self.policy_driven.get_policy_report()

        return status

    def optimize(self) -> None:
        """Optimize all orchestration systems."""
        self.resource_aware.optimize_constraints()
        self.lifecycle.release_idle_capabilities()

        if self.learner:
            # Rebalance coordination preferences
            pass

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.lifecycle.cleanup()


def create_unified_orchestrator(
    enable_learning: bool = True,
    enable_incremental: bool = True,
    enable_policies: bool = True,
    policy_directory: Optional[str] = None
) -> UnifiedOrchestrator:
    """
    Factory function to create unified orchestrator.

    Args:
        enable_learning: Enable learning from outcomes
        enable_incremental: Enable incremental refinement
        enable_policies: Enable policy-driven orchestration
        policy_directory: Directory containing policy files

    Returns:
        Configured UnifiedOrchestrator instance
    """
    return UnifiedOrchestrator(
        enable_learning=enable_learning,
        enable_incremental=enable_incremental,
        enable_policies=enable_policies,
        policy_directory=policy_directory
    )


# Export main components
__all__ = [
    # Main orchestrator
    "create_unified_orchestrator",
    "UnifiedOrchestrator",
    "OrchestrationContext",

    # Hierarchical orchestration
    "HierarchicalOrchestrator",
    "TaskComplexity",
    "OrchestrationTier",

    # Adaptive coordination
    "AdaptiveCoordinator",
    "CoordinationPattern",

    # Conflict resolution
    "ConflictResolver",
    "ConflictType",
    "ResolutionStrategy",

    # Resource awareness
    "ResourceAwareOrchestrator",
    "ResourceType",
    "ResourceState",

    # Lifecycle management
    "CapabilityLifecycleManager",
    "LifecycleState",
    "HealthStatus",

    # Learning
    "OrchestratorLearner",
    "LearningSignal",

    # Incremental
    "IncrementalOrchestrator",
    "RefinementStage",
    "QualityThreshold",

    # Policy-driven
    "PolicyDrivenOrchestrator",
    "PolicyType",
    "PolicyAction",
]


# Add time import for the module
import time
from typing import List, Dict, Any, Optional, Union
