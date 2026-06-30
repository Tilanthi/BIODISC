"""
Hierarchical Orchestration System for BIODISC

Implements three-tier orchestration:
- Strategic Layer: High-level goal decomposition and objective setting
- Tactical Layer: Resource allocation and capability selection
- Operational Layer: Individual task execution and monitoring

This architecture enables BIODISC to handle complex biological research tasks
with appropriate abstraction at each level.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import time
from abc import ABC, abstractmethod


class OrchestrationTier(Enum):
    """Orchestration tiers in the hierarchy."""
    STRATEGIC = "strategic"      # Goal decomposition, objective setting
    TACTICAL = "tactical"        # Resource allocation, capability selection
    OPERATIONAL = "operational"  # Task execution, monitoring


class TaskComplexity(Enum):
    """Complexity levels for tasks."""
    TRIVIAL = "trivial"          # Single capability, deterministic
    SIMPLE = "simple"            # Few capabilities, low uncertainty
    MODERATE = "moderate"        # Multiple capabilities, some uncertainty
    COMPLEX = "complex"          # Many capabilities, high uncertainty
    EXPERT = "expert"            # Requires multi-stage reasoning


@dataclass
class StrategicObjective:
    """High-level objective at the strategic tier."""
    objective_id: str
    description: str
    domain: str  # e.g., "molecular_biology", "genomics"
    priority: float  # 0.0 to 1.0
    success_criteria: Dict[str, Any]
    constraints: Dict[str, Any] = field(default_factory=dict)
    sub_objectives: List[str] = field(default_factory=list)


@dataclass
class TacticalPlan:
    """Execution plan at the tactical tier."""
    plan_id: str
    objective_id: str
    capabilities_required: List[str]
    execution_order: List[str]
    resource_allocation: Dict[str, float]
    estimated_duration: float
    fallback_strategies: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class OperationalTask:
    """Individual task at the operational tier."""
    task_id: str
    plan_id: str
    capability_name: str
    parameters: Dict[str, Any]
    timeout: float = 30.0
    retry_limit: int = 3
    dependencies: List[str] = field(default_factory=list)


@dataclass
class OrchestrationContext:
    """Context passed through orchestration tiers."""
    query: str
    domain: Optional[str] = None
    complexity: TaskComplexity = TaskComplexity.MODERATE
    uncertainty: float = 0.5
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StrategicOrchestrator:
    """
    Strategic Tier: High-level goal decomposition

    Responsibilities:
    - Understand user intent and high-level objectives
    - Decompose complex queries into sub-objectives
    - Set success criteria and priorities
    - Identify domain-specific constraints
    """

    def __init__(self):
        self.objective_history: List[StrategicObjective] = []
        self.domain_patterns: Dict[str, List[str]] = {
            "molecular_biology": ["protein", "rna", "dna", "binding", "structure"],
            "genomics": ["gene", "sequence", "variation", "expression", "regulation"],
            "cell_biology": ["cell", "organelle", "division", "signaling", "transport"],
            "biochemistry": ["enzyme", "metabolism", "pathway", "catalysis", "reaction"],
            "bioinformatics": ["alignment", "phylogeny", "annotation", "database"],
        }

    def analyze_query(self, query: str, context: OrchestrationContext) -> StrategicObjective:
        """
        Analyze query and create strategic objective.

        Args:
            query: User's query
            context: Orchestration context

        Returns:
            StrategicObjective with decomposed goals
        """
        # Identify domain
        domain = self._identify_domain(query, context)

        # Determine complexity
        complexity = self._assess_complexity(query, domain)

        # Create objective
        objective = StrategicObjective(
            objective_id=f"obj_{int(time.time() * 1000)}",
            description=query,
            domain=domain,
            priority=self._calculate_priority(query, context),
            success_criteria=self._define_success_criteria(query, domain),
            constraints=self._identify_constraints(query, context)
        )

        # Decompose if complex
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            objective.sub_objectives = self._decompose_objective(objective)

        self.objective_history.append(objective)
        return objective

    def _identify_domain(self, query: str, context: OrchestrationContext) -> str:
        """Identify biological domain from query."""
        query_lower = query.lower()

        if context.domain:
            return context.domain

        # Domain keyword matching
        for domain, keywords in self.domain_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain

        return "general_biology"

    def _assess_complexity(self, query: str, domain: str) -> TaskComplexity:
        """Assess task complexity."""
        query_lower = query.lower()

        # Complexity indicators
        complex_indicators = [
            "compare", "relationship", "mechanism", "pathway",
            "integration", "synthesis", "comprehensive", "multi"
        ]

        simple_indicators = [
            "what is", "define", "list", "identify"
        ]

        complex_count = sum(1 for indicator in complex_indicators if indicator in query_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in query_lower)

        if complex_count >= 2:
            return TaskComplexity.COMPLEX
        elif complex_count == 1:
            return TaskComplexity.MODERATE
        elif simple_count >= 1:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE

    def _calculate_priority(self, query: str, context: OrchestrationContext) -> float:
        """Calculate objective priority."""
        base_priority = 0.5

        # Adjust based on user preferences
        if context.user_preferences.get("urgency") == "high":
            base_priority += 0.3

        # Adjust based on query characteristics
        urgent_keywords = ["urgent", "important", "critical", "immediately"]
        if any(keyword in query.lower() for keyword in urgent_keywords):
            base_priority += 0.2

        return min(1.0, base_priority)

    def _define_success_criteria(self, query: str, domain: str) -> Dict[str, Any]:
        """Define success criteria for the objective."""
        return {
            "accuracy_threshold": 0.8,
            "completeness": "all_subquestions_answered",
            "domain_relevance": domain,
            "evidence_quality": "peer_reviewed_preferred"
        }

    def _identify_constraints(self, query: str, context: OrchestrationContext) -> Dict[str, Any]:
        """Identify constraints for the objective."""
        constraints = {}

        # Time constraints
        if context.resource_constraints.get("max_duration"):
            constraints["max_duration"] = context.resource_constraints["max_duration"]

        # Scope constraints
        if "in humans only" in query.lower():
            constraints["organism"] = "human"
        elif "in eukaryotes" in query.lower():
            constraints["organism_type"] = "eukaryote"

        return constraints

    def _decompose_objective(self, objective: StrategicObjective) -> List[str]:
        """Decompose complex objective into sub-objectives."""
        # Simple decomposition based on query structure
        sub_objectives = []

        # Common decomposition patterns
        description = objective.description.lower()

        if "compare" in description or "versus" in description:
            sub_objectives = [
                f"Analyze first aspect of {objective.description}",
                f"Analyze second aspect of {objective.description}",
                f"Synthesize comparison"
            ]

        elif "mechanism" in description and "regulation" in description:
            sub_objectives = [
                f"Identify components of {objective.description}",
                f"Determine regulatory relationships",
                f"Characterize feedback mechanisms"
            ]

        else:
            # Generic decomposition
            sub_objectives = [
                f"Gather information about {objective.description}",
                f"Analyze patterns and relationships",
                f"Synthesize findings"
            ]

        return sub_objectives


class TacticalOrchestrator:
    """
    Tactical Tier: Resource allocation and capability selection

    Responsibilities:
    - Select appropriate capabilities for each objective
    - Plan execution order and dependencies
    - Allocate resources (time, memory, compute)
    - Define fallback strategies
    """

    def __init__(self):
        self.capability_registry: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[TacticalPlan] = []

    def create_execution_plan(
        self,
        objective: StrategicObjective,
        available_capabilities: List[str],
        context: OrchestrationContext
    ) -> TacticalPlan:
        """
        Create execution plan for strategic objective.

        Args:
            objective: Strategic objective to achieve
            available_capabilities: List of available capability names
            context: Orchestration context

        Returns:
            TacticalPlan with capability selection and execution order
        """
        # Select capabilities
        capabilities = self._select_capabilities(objective, available_capabilities, context)

        # Determine execution order
        execution_order = self._plan_execution_order(capabilities, objective)

        # Allocate resources
        resource_allocation = self._allocate_resources(capabilities, context)

        # Define fallbacks
        fallbacks = self._define_fallback_strategies(capabilities, available_capabilities)

        plan = TacticalPlan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            objective_id=objective.objective_id,
            capabilities_required=capabilities,
            execution_order=execution_order,
            resource_allocation=resource_allocation,
            estimated_duration=self._estimate_duration(capabilities),
            fallback_strategies=fallbacks
        )

        self.execution_history.append(plan)
        return plan

    def _select_capabilities(
        self,
        objective: StrategicObjective,
        available: List[str],
        context: OrchestrationContext
    ) -> List[str]:
        """Select capabilities for objective."""
        selected = []

        # Domain-specific capabilities
        domain_capabilities = {
            "molecular_biology": ["protein_structure", "molecular_interactions"],
            "genomics": ["sequence_analysis", "gene_regulation"],
            "cell_biology": ["cellular_processes", "organelle_function"],
            "biochemistry": ["metabolic_pathways", "enzymology"],
            "bioinformatics": ["sequence_alignment", "phylogenetic_analysis"],
        }

        # Add domain capabilities
        if objective.domain in domain_capabilities:
            for cap in domain_capabilities[objective.domain]:
                if cap in available:
                    selected.append(cap)

        # Add reasoning capabilities based on complexity
        if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            reasoning_caps = ["causal_reasoning", "abstraction", "synthesis"]
            for cap in reasoning_caps:
                if cap in available:
                    selected.append(cap)

        # Add information retrieval
        if "knowledge_retrieval" in available:
            selected.append("knowledge_retrieval")

        # Remove duplicates while preserving order
        seen = set()
        selected = [x for x in selected if not (x in seen or seen.add(x))]

        return selected if selected else ["general_reasoning"]  # Fallback

    def _plan_execution_order(
        self,
        capabilities: List[str],
        objective: StrategicObjective
    ) -> List[str]:
        """Plan execution order considering dependencies."""
        # Define dependency graph
        dependencies = {
            "causal_reasoning": ["knowledge_retrieval"],
            "abstraction": ["knowledge_retrieval"],
            "synthesis": ["knowledge_retrieval", "causal_reasoning"],
            "protein_structure": ["knowledge_retrieval"],
            "molecular_interactions": ["protein_structure"],
        }

        # Topological sort
        ordered = []
        remaining = capabilities.copy()

        while remaining:
            # Find capabilities with no unsatisfied dependencies
            ready = [
                cap for cap in remaining
                if all(dep in ordered for dep in dependencies.get(cap, []))
            ]

            if not ready:
                # Circular dependency or missing dependency - break arbitrarily
                ready = [remaining[0]]

            # Add first ready capability
            ordered.append(ready[0])
            remaining.remove(ready[0])

        return ordered

    def _allocate_resources(
        self,
        capabilities: List[str],
        context: OrchestrationContext
    ) -> Dict[str, float]:
        """Allocate resources to capabilities."""
        allocation = {}

        # Base allocation
        for cap in capabilities:
            allocation[cap] = {
                "memory_mb": 512,
                "timeout_seconds": 30.0,
                "priority": 0.5
            }

        # Adjust based on capability type
        if "causal_reasoning" in capabilities:
            allocation["causal_reasoning"]["timeout_seconds"] = 60.0
            allocation["causal_reasoning"]["memory_mb"] = 1024

        if "synthesis" in capabilities:
            allocation["synthesis"]["timeout_seconds"] = 45.0

        # Apply user constraints
        if context.resource_constraints.get("max_duration"):
            total_time = sum(alloc[cap]["timeout_seconds"] for cap in capabilities)
            max_time = context.resource_constraints["max_duration"]

            if total_time > max_time:
                scale_factor = max_time / total_time
                for cap in capabilities:
                    allocation[cap]["timeout_seconds"] *= scale_factor

        return allocation

    def _define_fallback_strategies(
        self,
        capabilities: List[str],
        available: List[str]
    ) -> Dict[str, List[str]]:
        """Define fallback strategies for each capability."""
        fallbacks = {
            "causal_reasoning": ["correlation_analysis", "statistical_testing"],
            "abstraction": ["pattern_matching", "taxonomy_lookup"],
            "synthesis": ["summarization", "template_based_generation"],
            "protein_structure": ["homology_modeling", "structure_prediction"],
        }

        strategies = {}
        for cap in capabilities:
            if cap in fallbacks:
                # Find available fallbacks
                available_fallbacks = [
                    fb for fb in fallbacks[cap]
                    if fb in available
                ]
                if available_fallbacks:
                    strategies[cap] = available_fallbacks

        return strategies

    def _estimate_duration(self, capabilities: List[str]) -> float:
        """Estimate total execution duration."""
        # Base durations for capability types
        durations = {
            "knowledge_retrieval": 2.0,
            "causal_reasoning": 15.0,
            "abstraction": 10.0,
            "synthesis": 12.0,
            "protein_structure": 8.0,
            "molecular_interactions": 6.0,
            "sequence_analysis": 5.0,
        }

        total = sum(durations.get(cap, 5.0) for cap in capabilities)
        return total


class OperationalOrchestrator:
    """
    Operational Tier: Task execution and monitoring

    Responsibilities:
    - Execute individual tasks
    - Monitor task progress and results
    - Handle retries and fallbacks
    - Aggregate results
    """

    def __init__(self):
        self.task_registry: Dict[str, Callable] = {}
        self.execution_log: List[Dict[str, Any]] = []

    def register_capability(self, name: str, executor: Callable) -> None:
        """Register a capability executor."""
        self.task_registry[name] = executor

    def execute_plan(
        self,
        plan: TacticalPlan,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """
        Execute tactical plan.

        Args:
            plan: Tactical execution plan
            context: Orchestration context

        Returns:
            Aggregated results from all tasks
        """
        results = {}
        execution_metadata = {
            "start_time": time.time(),
            "capabilities_executed": [],
            "capabilities_failed": [],
            "fallbacks_used": []
        }

        # Execute capabilities in order
        for capability_name in plan.execution_order:
            task_result = self._execute_capability(
                capability_name,
                plan,
                context
            )

            results[capability_name] = task_result

            if task_result.get("success"):
                execution_metadata["capabilities_executed"].append(capability_name)
            else:
                execution_metadata["capabilities_failed"].append(capability_name)

                # Try fallback
                if capability_name in plan.fallback_strategies:
                    fallback_result = self._try_fallback(
                        capability_name,
                        plan.fallback_strategies[capability_name],
                        plan,
                        context
                    )
                    if fallback_result.get("success"):
                        results[f"{capability_name}_fallback"] = fallback_result
                        execution_metadata["fallbacks_used"].append(capability_name)

        execution_metadata["end_time"] = time.time()
        execution_metadata["duration"] = execution_metadata["end_time"] - execution_metadata["start_time"]

        return {
            "results": results,
            "metadata": execution_metadata,
            "plan_id": plan.plan_id
        }

    def _execute_capability(
        self,
        capability_name: str,
        plan: TacticalPlan,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute a single capability."""
        if capability_name not in self.task_registry:
            return {
                "success": False,
                "error": f"Capability {capability_name} not registered",
                "result": None
            }

        try:
            executor = self.task_registry[capability_name]
            parameters = {
                "query": context.query,
                "domain": context.domain,
                "timeout": plan.resource_allocation[capability_name]["timeout_seconds"]
            }

            result = executor(**parameters)

            self.execution_log.append({
                "capability": capability_name,
                "success": True,
                "timestamp": time.time()
            })

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            self.execution_log.append({
                "capability": capability_name,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            })

            return {
                "success": False,
                "error": str(e),
                "result": None
            }

    def _try_fallback(
        self,
        failed_capability: str,
        fallback_names: List[str],
        plan: TacticalPlan,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Try fallback capabilities."""
        for fallback_name in fallback_names:
            if fallback_name in self.task_registry:
                try:
                    executor = self.task_registry[fallback_name]
                    result = executor(query=context.query)

                    return {
                        "success": True,
                        "result": result,
                        "fallback_for": failed_capability
                    }
                except Exception:
                    continue

        return {
            "success": False,
            "error": "All fallbacks failed"
        }


class HierarchicalOrchestrator:
    """
    Main orchestrator combining all three tiers.

    Provides unified interface for hierarchical orchestration of
    complex biological research tasks.
    """

    def __init__(self):
        self.strategic = StrategicOrchestrator()
        self.tactical = TacticalOrchestrator()
        self.operational = OperationalOrchestrator()
        self.orchestration_history: List[Dict[str, Any]] = []

    def orchestrate(
        self,
        query: str,
        available_capabilities: List[str],
        context: Optional[OrchestrationContext] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate complex query using hierarchical approach.

        Args:
            query: User's query
            available_capabilities: List of available capability names
            context: Orchestration context (optional)

        Returns:
            Complete orchestration result with all tier outputs
        """
        if context is None:
            context = OrchestrationContext(query=query)

        orchestration_start = time.time()

        # Strategic tier: Analyze and decompose
        strategic_result = self.strategic.analyze_query(query, context)

        # Tactical tier: Plan execution
        tactical_plan = self.tactical.create_execution_plan(
            strategic_result,
            available_capabilities,
            context
        )

        # Operational tier: Execute plan
        operational_result = self.operational.execute_plan(tactical_plan, context)

        orchestration_duration = time.time() - orchestration_start

        # Record orchestration
        orchestration_record = {
            "query": query,
            "strategic_objective": strategic_result,
            "tactical_plan_id": tactical_plan.plan_id,
            "operational_result": operational_result,
            "duration": orchestration_duration,
            "timestamp": time.time()
        }

        self.orchestration_history.append(orchestration_record)

        return {
            "strategic": strategic_result,
            "tactical": tactical_plan,
            "operational": operational_result,
            "duration": orchestration_duration,
            "explanation": self._generate_explanation(
                strategic_result,
                tactical_plan,
                operational_result
            )
        }

    def _generate_explanation(
        self,
        strategic: StrategicObjective,
        tactical: TacticalPlan,
        operational: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation of orchestration."""
        explanation = f"""
Orchestration Summary:

Strategic Tier:
- Domain: {strategic.domain}
- Complexity: {strategic.priority}
- Sub-objectives: {len(strategic.sub_objectives)}

Tactical Tier:
- Capabilities selected: {', '.join(tactical.capabilities_required)}
- Estimated duration: {tactical.estimated_duration:.1f}s
- Fallback strategies: {len(tactical.fallback_strategies)}

Operational Tier:
- Capabilities executed: {len(operational['metadata']['capabilities_executed'])}
- Capabilities failed: {len(operational['metadata']['capabilities_failed'])}
- Fallbacks used: {len(operational['metadata']['fallbacks_used'])}
- Actual duration: {operational['metadata']['duration']:.1f}s
"""
        return explanation

    def register_capability(self, name: str, executor: Callable) -> None:
        """Register a capability executor."""
        self.operational.register_capability(name, executor)

    def get_orchestration_history(self) -> List[Dict[str, Any]]:
        """Get history of orchestrations."""
        return self.orchestration_history

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics across all orchestrations."""
        if not self.orchestration_history:
            return {}

        total_duration = sum(record["duration"] for record in self.orchestration_history)
        avg_duration = total_duration / len(self.orchestration_history)

        successful_orchestrations = sum(
            1 for record in self.orchestration_history
            if len(record["operational"]["metadata"]["capabilities_failed"]) == 0
        )

        return {
            "total_orchestrations": len(self.orchestration_history),
            "average_duration": avg_duration,
            "success_rate": successful_orchestrations / len(self.orchestration_history),
            "total_duration": total_duration
        }


def create_hierarchical_orchestrator() -> HierarchicalOrchestrator:
    """Factory function to create hierarchical orchestrator."""
    return HierarchicalOrchestrator()
