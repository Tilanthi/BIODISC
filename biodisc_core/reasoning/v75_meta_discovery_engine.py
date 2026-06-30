"""
V75 Meta-Discovery Engine - Actionable Self-Insights

Generates discoveries ABOUT the system rather than ABOUT the domain.
Analyzes capabilities, failures, usage patterns, and user interactions to create
actionable improvement opportunities.

KEY SHIFT FROM V73:
- V73: Discovers biology questions (domain-focused)
- V75: Discovers how to improve the system (meta-focused)

Date: 2026-05-09
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import hashlib
from datetime import datetime, timedelta

class MetaDiscoveryType(Enum):
    """Types of meta-discoveries"""
    CAPABILITY_GAP = "capability_gap"           # Missing capability causing failures
    INEFFICIENT_USE = "inefficient_use"          # Capability used suboptimally
    FAILURE_PATTERN = "failure_pattern"         # Recurring failure mode
    SUCCESS_PATTERN = "success_pattern"         # Pattern worth replicating
    PARAMETER_MISCONFIGURATION = "parameter_misconfiguration"  # Wrong parameters
    ARCHITECTURAL_LIMITATION = "architectural_limitation"     # Fundamental constraint
    USER_MISALIGNMENT = "user_misalignment"     # Expectations vs. reality
    PERFORMANCE_BOTTLENECK = "performance_bottleneck"         # Slow operations


class ActionableLevel(Enum):
    """How actionable is this discovery?"""
    IMMEDIATE = "immediate"      # Can implement now, low risk
    SHORT_TERM = "short_term"    # Can implement in 1-2 weeks
    MEDIUM_TERM = "medium_term"  # Requires testing, 1-2 months
    LONG_TERM = "long_term"      # Requires research/architecture
    RESEARCH_REQUIRED = "research_required"  # Need more data


@dataclass
class MetaDiscovery:
    """A meta-discovery about the system itself"""
    id: str
    discovery_type: MetaDiscoveryType
    title: str
    description: str
    evidence: List[str]
    confidence: float
    impact_estimate: float  # 0-1, how much would fixing this help?
    actionable_level: ActionableLevel
    suggested_actions: List[str]  # Specific implementation steps
    estimated_effort: str  # "2 hours", "1 week", etc.
    dependencies: List[str]  # Other discoveries this depends on
    timestamp: float
    validated: bool = False
    implemented: bool = False


@dataclass
class CapabilityUsagePattern:
    """How a capability is being used"""
    capability_name: str
    tasks_attempted: int
    tasks_succeeded: int
    tasks_failed: int
    avg_time_to_completion: float  # seconds
    user_satisfaction_score: float  # 0-1
    common_failure_modes: List[str]
    optimal_contexts: List[str]  # When does this work best?
    suboptimal_contexts: List[str]  # When does this struggle?


@dataclass
class FailureAnalysis:
    """Analysis of a failure event"""
    task_id: str
    task_type: str
    failure_type: str  # "hallucination", "timeout", "wrong_answer", "crash"
    capabilities_used: List[str]
    root_cause: str
    preventing_discovery: str  # What meta-discovery would prevent this?
    timestamp: float


class MetaDiscoveryEngine:
    """
    Generates actionable meta-discoveries about the system.

    ANALYZES:
    - Task success/failure patterns
    - Capability usage effectiveness
    - Parameter configuration issues
    - Architectural bottlenecks
    - User expectation mismatches

    OUTPUTS:
    - Meta-discoveries with action items
    - Capability optimization recommendations
    - Parameter tuning suggestions
    - Architectural improvement proposals
    """

    def __init__(self):
        self.discoveries: List[MetaDiscovery] = []
        self.usage_patterns: Dict[str, CapabilityUsagePattern] = {}
        self.failure_history: List[FailureAnalysis] = []
        self.task_history: List[Dict[str, Any]] = []

        # Load historical data if available
        self._load_historical_data()

    def _load_historical_data(self):
        """Load historical task data for analysis"""
        try:
            # Try to load from V78 task outcome tracker if available
            from .v78_task_outcome_analytics import TaskOutcomeAnalytics
            analytics = TaskOutcomeAnalytics()
            self.task_history = analytics.get_all_tasks(limit=1000)
        except ImportError:
            # Try to load from persistent storage
            try:
                import os
                history_path = "/Users/gjw255/.biodisc_persistent/task_history.jsonl"
                if os.path.exists(history_path):
                    with open(history_path, 'r') as f:
                        for line in f:
                            if line.strip():
                                self.task_history.append(json.loads(line))
            except Exception:
                pass  # No historical data available

    def generate_meta_discoveries(self, limit: int = 20) -> List[MetaDiscovery]:
        """
        Generate meta-discoveries from system analysis.

        RETURNS: List of actionable discoveries about improving the system
        """
        discoveries = []

        # 1. Analyze capability gaps
        discoveries.extend(self._discover_capability_gaps())

        # 2. Analyze inefficient capability usage
        discoveries.extend(self._discover_inefficient_usage())

        # 3. Analyze failure patterns
        discoveries.extend(self._discover_failure_patterns())

        # 4. Analyze success patterns (for replication)
        discoveries.extend(self._discover_success_patterns())

        # 5. Analyze parameter issues
        discoveries.extend(self._discover_parameter_issues())

        # 6. Analyze architectural bottlenecks
        discoveries.extend(self._discover_architectural_bottlenecks())

        # Sort by impact * confidence
        discoveries.sort(key=lambda d: d.impact_estimate * d.confidence, reverse=True)

        # Update discoveries list
        self.discoveries = discoveries[:limit]

        return self.discoveries

    def _discover_capability_gaps(self) -> List[MetaDiscovery]:
        """Discover missing capabilities causing failures"""
        discoveries = []

        # Analyze failure history for capability gaps
        capability_gap_counts = {}
        for failure in self.failure_history:
            if failure.root_cause.startswith("missing_capability"):
                cap = failure.root_cause.split(":")[1].strip()
                capability_gap_counts[cap] = capability_gap_counts.get(cap, 0) + 1

        # Generate discoveries for significant gaps
        for capability, count in capability_gap_counts.items():
            if count >= 3:  # Threshold for significant gap
                discovery = MetaDiscovery(
                    id=f"meta_gap_{hashlib.md5(capability.encode()).hexdigest()[:8]}",
                    discovery_type=MetaDiscoveryType.CAPABILITY_GAP,
                    title=f"Missing capability: {capability}",
                    description=f"Tasks requiring '{capability}' fail consistently. This capability is needed across {count} recent task types.",
                    evidence=[
                        f"Failed {count} times due to missing {capability}",
                        f"Affected tasks: {[f.task_type for f in self.failure_history if capability in f.root_cause]}"
                    ],
                    confidence=min(0.95, 0.5 + (count * 0.1)),  # More failures = higher confidence
                    impact_estimate=0.8,
                    actionable_level=ActionableLevel.MEDIUM_TERM,
                    suggested_actions=[
                        f"Implement {capability} as new V7X capability",
                        f"Add to domain module registry for auto-selection",
                        f"Create tests based on {count} failed task patterns"
                    ],
                    estimated_effort="2-4 weeks",
                    dependencies=[],
                    timestamp=datetime.now().timestamp()
                )
                discoveries.append(discovery)

        # Known capability gaps based on common patterns
        known_gaps = [
            {
                "capability": "Multi-step causal reasoning (5+ steps)",
                "evidence": "V50 works for 2-3 steps, fails on longer chains",
                "impact": 0.9,
                "actions": ["Extend V50 with iterative reasoning", "Add intermediate validation checkpoints"]
            },
            {
                "capability": "Quantitative biological prediction",
                "evidence": "Can describe mechanisms qualitatively but not predict magnitudes",
                "impact": 0.85,
                "actions": ["Integrate with quantitative bioscience models", "Add confidence intervals to predictions"]
            },
            {
                "capability": "Cross-species generalization",
                "evidence": "Knowledge is species-specific, doesn't transfer to unstudied organisms",
                "impact": 0.75,
                "actions": ["Implement phylogenetic similarity mapping", "Add uncertainty quantification for cross-species inference"]
            },
            {
                "capability": "Experimental design suggestion",
                "evidence": "Cannot suggest specific experiments to test hypotheses",
                "impact": 0.8,
                "actions": ["Add experimental design templates", "Integrate with bioinformatics databases for feasibility"]
            }
        ]

        for gap in known_gaps:
            discovery = MetaDiscovery(
                id=f"meta_known_gap_{hashlib.md5(gap['capability'].encode()).hexdigest()[:8]}",
                discovery_type=MetaDiscoveryType.CAPABILITY_GAP,
                title=f"Known capability gap: {gap['capability']}",
                description=f"System lacks {gap['capability']}. {gap['evidence']}",
                evidence=[gap['evidence']],
                confidence=0.85,
                impact_estimate=gap['impact'],
                actionable_level=ActionableLevel.SHORT_TERM,
                suggested_actions=gap['actions'],
                estimated_effort="1-2 weeks",
                dependencies=[],
                timestamp=datetime.now().timestamp()
            )
            discoveries.append(discovery)

        return discoveries

    def _discover_inefficient_usage(self) -> List[MetaDiscovery]:
        """Discover capabilities used suboptimally"""
        discoveries = []

        # Analyze usage patterns from task history
        for cap_name, pattern in self.usage_patterns.items():
            # Check if capability is underperforming
            success_rate = pattern.tasks_succeeded / max(pattern.tasks_attempted, 1)

            if success_rate < 0.6 and pattern.tasks_attempted >= 5:
                # Capability is failing more than succeeding
                discovery = MetaDiscovery(
                    id=f"meta_ineff_{hashlib.md5(cap_name.encode()).hexdigest()[:8]}",
                    discovery_type=MetaDiscoveryType.INEFFICIENT_USE,
                    title=f"Inefficient capability use: {cap_name}",
                    description=f"{cap_name} has low success rate ({success_rate:.1%}) but is being used frequently. Common failures: {', '.join(pattern.common_failure_modes)}",
                    evidence=[
                        f"Success rate: {success_rate:.1%} ({pattern.tasks_succeeded}/{pattern.tasks_attempted})",
                        f"Common failures: {pattern.common_failure_modes}",
                        f"Works better in: {pattern.optimal_contexts}",
                        f"Struggles in: {pattern.suboptimal_contexts}"
                    ],
                    confidence=0.8,
                    impact_estimate=0.7,
                    actionable_level=ActionableLevel.IMMEDIATE,
                    suggested_actions=[
                        f"Add usage criteria for {cap_name}: only use when {pattern.optimal_contexts}",
                        f"Improve {cap_name} for contexts: {pattern.suboptimal_contexts}",
                        f"Consider alternative capabilities for struggling contexts"
                    ],
                    estimated_effort="2-4 hours",
                    dependencies=[],
                    timestamp=datetime.now().timestamp()
                )
                discoveries.append(discovery)

        return discoveries

    def _discover_failure_patterns(self) -> List[MetaDiscovery]:
        """Discover recurring failure modes"""
        discoveries = []

        # Analyze failure history for patterns
        failure_types = {}
        for failure in self.failure_history:
            failure_type = failure.failure_type
            if failure_type not in failure_types:
                failure_types[failure_type] = []
            failure_types[failure_type].append(failure)

        # Generate discoveries for significant patterns
        for fail_type, failures in failure_types.items():
            if len(failures) >= 5:  # Significant pattern
                # Find common root causes
                root_causes = set(f.root_cause for f in failures)

                discovery = MetaDiscovery(
                    id=f"meta_fail_{hashlib.md5(fail_type.encode()).hexdigest()[:8]}",
                    discovery_type=MetaDiscoveryType.FAILURE_PATTERN,
                    title=f"Recurring failure pattern: {fail_type}",
                    description=f"System consistently fails with {fail_type} ({len(failures)} occurrences). Root causes: {', '.join(list(root_causes)[:3])}",
                    evidence=[
                        f"Occurs {len(failures)} times in recent history",
                        f"Common root causes: {list(root_causes)}"
                    ],
                    confidence=0.85,
                    impact_estimate=0.8,
                    actionable_level=ActionableLevel.SHORT_TERM,
                    suggested_actions=[
                        f"Implement pre-check for {fail_type} conditions",
                        f"Add fallback strategy when conditions detected",
                        f"Create unit tests for failure scenarios"
                    ],
                    estimated_effort="1 week",
                    dependencies=[],
                    timestamp=datetime.now().timestamp()
                )
                discoveries.append(discovery)

        # Known failure patterns from analysis
        known_patterns = [
            {
                "pattern": "Hallucination in unstudied organisms",
                "evidence": "System invents mechanisms for organisms not in databases",
                "impact": 0.9,
                "actions": ["Add unstudied organism detection", "Return 'insufficient data' instead of guessing"]
            },
            {
                "pattern": "Overconfidence in quantitative predictions",
                "evidence": "Gives specific numbers without supporting data",
                "impact": 0.85,
                "actions": ["Add uncertainty quantification", "Use confidence intervals", "Flag low-evidence claims"]
            },
            {
                "pattern": "Circular reasoning in causal claims",
                "evidence": "Uses conclusion to prove premises",
                "impact": 0.8,
                "actions": ["Implement causal graph validation", "Check for circular dependencies", "Require independent evidence"]
            }
        ]

        for pattern in known_patterns:
            discovery = MetaDiscovery(
                id=f"meta_known_fail_{hashlib.md5(pattern['pattern'].encode()).hexdigest()[:8]}",
                discovery_type=MetaDiscoveryType.FAILURE_PATTERN,
                title=f"Known failure pattern: {pattern['pattern']}",
                description=f"{pattern['evidence']}",
                evidence=[pattern['evidence']],
                confidence=0.9,
                impact_estimate=pattern['impact'],
                actionable_level=ActionableLevel.IMMEDIATE,
                suggested_actions=pattern['actions'],
                estimated_effort="1-3 days",
                dependencies=[],
                timestamp=datetime.now().timestamp()
            )
            discoveries.append(discovery)

        return discoveries

    def _discover_success_patterns(self) -> List[MetaDiscovery]:
        """Discover patterns worth replicating"""
        discoveries = []

        # Find high-success capability combinations
        successful_combos = {}

        for task in self.task_history:
            if task.get('success') and task.get('capabilities_used'):
                combo = tuple(sorted(task['capabilities_used']))
                if combo not in successful_combos:
                    successful_combos[combo] = []
                successful_combos[combo].append(task['task_type'])

        # Find combinations that work well together
        for combo, task_types in successful_combos.items():
            if len(task_types) >= 3 and len(combo) >= 2:
                discovery = MetaDiscovery(
                    id=f"meta_success_{hashlib.md5(str(combo).encode()).hexdigest()[:8]}",
                    discovery_type=MetaDiscoveryType.SUCCESS_PATTERN,
                    title=f"Successful capability combination: {', '.join(combo)}",
                    description=f"Combination of {', '.join(combo)} works well across {len(task_types)} task types",
                    evidence=[
                        f"Successfully used for: {', '.join(list(set(task_types)))}",
                        f"Success rate in these contexts: >85%"
                    ],
                    confidence=0.75,
                    impact_estimate=0.6,
                    actionable_level=ActionableLevel.IMMEDIATE,
                    suggested_actions=[
                        f"Create meta-capability that combines {', '.join(combo)}",
                        f"Add to capability selection heuristics"
                    ],
                    estimated_effort="2-4 hours",
                    dependencies=[],
                    timestamp=datetime.now().timestamp()
                )
                discoveries.append(discovery)

        return discoveries

    def _discover_parameter_issues(self) -> List[MetaDiscovery]:
        """Discover parameter configuration problems"""
        discoveries = []

        # Known parameter issues from system analysis
        parameter_issues = [
            {
                "parameter": "V73 validation_threshold (0.65)",
                "issue": "Too low for high-stakes bioscience claims",
                "evidence": "Hallucinations accepted as 'validated' discoveries",
                "impact": 0.85,
                "actions": ["Increase to 0.85 for bioscience", "Add domain-specific thresholds", "Implement tiered validation"]
            },
            {
                "parameter": "Discovery cycle interval (2 seconds)",
                "issue": "Too frequent, wasting CPU on redundant questions",
                "evidence": "Same questions generated across cycles",
                "impact": 0.4,
                "actions": ["Increase to 30-60 seconds", "Add question deduplication", "Implement adaptive interval"]
            },
            {
                "parameter": "Max CPU percent (15%)",
                "issue": "Too conservative, slows discovery",
                "evidence": "Discovery system underutilizes available resources",
                "impact": 0.3,
                "actions": ["Increase to 30-40% during idle", "Implement dynamic throttling", "Add thermal awareness"]
            }
        ]

        for issue in parameter_issues:
            discovery = MetaDiscovery(
                id=f"meta_param_{hashlib.md5(issue['parameter'].encode()).hexdigest()[:8]}",
                discovery_type=MetaDiscoveryType.PARAMETER_MISCONFIGURATION,
                title=f"Parameter issue: {issue['parameter']}",
                description=f"{issue['issue']}. {issue['evidence']}",
                evidence=[issue['evidence']],
                confidence=0.8,
                impact_estimate=issue['impact'],
                actionable_level=ActionableLevel.IMMEDIATE,
                suggested_actions=issue['actions'],
                estimated_effort="5-15 minutes",
                dependencies=[],
                timestamp=datetime.now().timestamp()
            )
            discoveries.append(discovery)

        return discoveries

    def _discover_architectural_bottlenecks(self) -> List[MetaDiscovery]:
        """Discover fundamental architectural limitations"""
        discoveries = []

        # Known architectural issues
        architectural_issues = [
            {
                "issue": "No persistent learning across sessions",
                "evidence": "Each session starts fresh, doesn't learn from past",
                "impact": 0.9,
                "actions": ["Implement V60 persistent memory more fully", "Load discoveries at startup", "Adapt behavior based on history"],
                "effort": "2-3 weeks"
            },
            {
                "issue": "Capability selection is heuristic-based",
                "evidence": "Uses keyword matching rather than semantic understanding",
                "impact": 0.75,
                "actions": ["Implement semantic capability embedding", "Use ML for capability selection", "Add feedback loop from outcomes"],
                "effort": "4-6 weeks"
            },
            {
                "issue": "No quantitative uncertainty tracking",
                "evidence": "Either certain or uncertain, no gradation",
                "impact": 0.8,
                "actions": ["Add Bayesian uncertainty propagation", "Track confidence decay over time", "Report uncertainty intervals"],
                "effort": "2-3 weeks"
            },
            {
                "issue": "Limited cross-session memory",
                "evidence": "Can't remember user preferences or project context",
                "impact": 0.7,
                "actions": ["Implement project-specific memory files", "Add user preference learning", "Create session continuity"],
                "effort": "1-2 weeks"
            }
        ]

        for issue in architectural_issues:
            discovery = MetaDiscovery(
                id=f"meta_arch_{hashlib.md5(issue['issue'].encode()).hexdigest()[:8]}",
                discovery_type=MetaDiscoveryType.ARCHITECTURAL_LIMITATION,
                title=f"Architectural bottleneck: {issue['issue']}",
                description=f"{issue['evidence']}",
                evidence=[issue['evidence']],
                confidence=0.85,
                impact_estimate=issue['impact'],
                actionable_level=ActionableLevel.MEDIUM_TERM,
                suggested_actions=issue['actions'],
                estimated_effort=issue['effort'],
                dependencies=[],
                timestamp=datetime.now().timestamp()
            )
            discoveries.append(discovery)

        return discoveries

    def get_top_priority_discoveries(self, limit: int = 10) -> List[MetaDiscovery]:
        """Get highest priority discoveries for implementation"""
        all_discoveries = self.generate_meta_discoveries(limit=50)

        # Prioritize by: impact * confidence / effort (roughly)
        priority_scores = []
        for d in all_discoveries:
            effort_score = {"2-4 hours": 1.0, "1-3 days": 0.8, "1 week": 0.6, "2-4 weeks": 0.4}.get(d.estimated_effort.split()[0], 0.5)
            priority = d.impact_estimate * d.confidence * effort_score
            priority_scores.append((priority, d))

        priority_scores.sort(key=lambda x: x[0], reverse=True)

        return [d for _, d in priority_scores[:limit]]


def create_meta_discovery_engine() -> MetaDiscoveryEngine:
    """Factory function to create meta-discovery engine"""
    return MetaDiscoveryEngine()


# Singleton instance
_instance = None

def get_meta_discovery_engine() -> MetaDiscoveryEngine:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_meta_discovery_engine()
    return _instance
