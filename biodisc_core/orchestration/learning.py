"""
Orchestrator Learning System for BIODISC

Implements closed-loop learning from orchestration outcomes:
- Track orchestration outcomes
- Compare predicted vs actual performance
- Update coordination strategies
- Adapt capability selection
- Detect and avoid anti-patterns

Uses reinforcement learning principles to improve orchestration over time.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from enum import Enum
import time
import numpy as np
from collections import defaultdict, deque


class LearningSignal(Enum):
    """Types of learning signals."""
    POSITIVE = "positive"          # Good outcome, reinforce
    NEGATIVE = "negative"          # Bad outcome, penalize
    NEUTRAL = "neutral"            # No strong signal


@dataclass
class OrchestrationOutcome:
    """Outcome of an orchestration."""
    orchestration_id: str
    query: str
    capabilities_used: List[str]
    coordination_pattern: str
    start_time: float
    end_time: float
    success: bool
    user_satisfaction: Optional[float] = None
    quality_score: Optional[float] = None
    resource_efficiency: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningExample:
    """A learning example for the orchestrator."""
    context_features: Dict[str, float]
    action_taken: str
    reward: float
    outcome: OrchestrationOutcome


@dataclass
class PolicyUpdate:
    """An update to orchestration policy."""
    policy_type: str
    parameter_name: str
    old_value: Any
    new_value: Any
    confidence: float
    reason: str


class RewardCalculator:
    """Calculate rewards for orchestration outcomes."""

    def __init__(self):
        self.weights = {
            "success": 1.0,
            "speed": 0.3,
            "efficiency": 0.2,
            "satisfaction": 0.5,
            "quality": 0.4
        }

    def calculate_reward(self, outcome: OrchestrationOutcome) -> float:
        """
        Calculate reward for an orchestration outcome.

        Reward combines multiple factors:
        - Success/failure
        - Execution time
        - Resource efficiency
        - User satisfaction
        - Quality score
        """
        reward = 0.0

        # Success/failure (primary factor)
        if outcome.success:
            reward += self.weights["success"]
        else:
            reward -= self.weights["success"] * 2

        # Speed (faster is better)
        duration = outcome.end_time - outcome.start_time
        if duration < 10:
            reward += self.weights["speed"]
        elif duration < 30:
            reward += self.weights["speed"] * 0.5

        # Resource efficiency
        if outcome.resource_efficiency:
            reward += outcome.resource_efficiency * self.weights["efficiency"]

        # User satisfaction (if available)
        if outcome.user_satisfaction is not None:
            reward += (outcome.user_satisfaction - 0.5) * 2 * self.weights["satisfaction"]

        # Quality score
        if outcome.quality_score is not None:
            reward += (outcome.quality_score - 0.5) * 2 * self.weights["quality"]

        # Penalize errors
        reward -= len(outcome.errors) * 0.1

        return reward

    def get_learning_signal(self, reward: float) -> LearningSignal:
        """Get learning signal type from reward."""
        if reward > 0.5:
            return LearningSignal.POSITIVE
        elif reward < -0.5:
            return LearningSignal.NEGATIVE
        else:
            return LearningSignal.NEUTRAL


class FeatureExtractor:
    """Extract features from orchestration context."""

    def extract_features(
        self,
        query: str,
        available_capabilities: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Extract features from orchestration context.

        Features include:
        - Query complexity indicators
        - Domain specificity
        - Resource constraints
        - Capability availability
        """
        features = {}

        # Query complexity
        query_lower = query.lower()
        features["query_length"] = len(query) / 1000.0  # Normalize
        features["has_mechanism"] = 1.0 if "mechanism" in query_lower else 0.0
        features["has_pathway"] = 1.0 if "pathway" in query_lower else 0.0
        features["has_relationship"] = 1.0 if "relationship" in query_lower else 0.0
        features["has_comparison"] = 1.0 if "compare" in query_lower else 0.0

        # Domain indicators
        domains = ["protein", "gene", "cell", "molecular", "biochemical"]
        for domain in domains:
            features[f"domain_{domain}"] = 1.0 if domain in query_lower else 0.0

        # Capability count
        features["num_capabilities"] = len(available_capabilities) / 20.0  # Normalize

        # Constraint indicators
        if constraints:
            features["has_time_constraint"] = 1.0 if "time" in constraints else 0.0
            features["has_memory_constraint"] = 1.0 if "memory" in constraints else 0.0
            features["constraint_severity"] = constraints.get("severity", 0.0)
        else:
            features["has_time_constraint"] = 0.0
            features["has_memory_constraint"] = 0.0
            features["constraint_severity"] = 0.0

        return features


class PolicyLearner:
    """Learn orchestration policies from experience."""

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate

        # Policy parameters
        self.coordination_preferences: Dict[str, float] = {
            "centralized": 0.33,
            "distributed": 0.33,
            "hybrid": 0.34
        }

        # Domain-pattern associations
        self.domain_coordination_map: Dict[str, str] = {}

        # Capability performance tracking
        self.capability_performance: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"success_rate": 0.5, "avg_reward": 0.0, "count": 0}
        )

        # Feature weights for context-based decisions
        self.feature_weights: Dict[str, float] = {
            "query_length": 0.1,
            "has_mechanism": 0.3,
            "has_pathway": 0.2,
            "has_relationship": 0.2,
            "num_capabilities": 0.1,
            "constraint_severity": 0.3
        }

    def update_policy(
        self,
        example: LearningExample
    ) -> List[PolicyUpdate]:
        """
        Update policy based on learning example.

        Returns list of policy updates made.
        """
        updates = []

        # Update coordination pattern preferences
        pattern = example.action_taken
        if pattern in self.coordination_preferences:
            old_preference = self.coordination_preferences[pattern]

            # Adjust based on reward
            adjustment = example.reward * self.learning_rate
            self.coordination_preferences[pattern] += adjustment

            # Normalize
            total = sum(self.coordination_preferences.values())
            if total > 0:
                for key in self.coordination_preferences:
                    self.coordination_preferences[key] /= total

            updates.append(PolicyUpdate(
                policy_type="coordination_preference",
                parameter_name=pattern,
                old_value=old_preference,
                new_value=self.coordination_preferences[pattern],
                confidence=min(1.0, example.outcome.quality_score or 0.5),
                reason=f"{'Positive' if example.reward > 0 else 'Negative'} outcome ({example.reward:.2f})"
            ))

        # Update capability performance tracking
        for cap in example.outcome.capabilities_used:
            perf = self.capability_performance[cap]
            n = perf["count"]

            # Update success rate
            if example.outcome.success:
                perf["success_rate"] = (perf["success_rate"] * n + 1.0) / (n + 1)
            else:
                perf["success_rate"] = (perf["success_rate"] * n) / (n + 1)

            # Update average reward
            perf["avg_reward"] = (perf["avg_reward"] * n + example.reward) / (n + 1)
            perf["count"] = n + 1

        # Update feature weights using simple gradient
        for feature, value in example.context_features.items():
            if feature in self.feature_weights:
                old_weight = self.feature_weights[feature]

                # Gradient: reward * feature_value
                gradient = example.reward * value * self.learning_rate
                self.feature_weights[feature] += gradient

                # Clip to reasonable range
                self.feature_weights[feature] = np.clip(
                    self.feature_weights[feature],
                    0.0,
                    1.0
                )

                if abs(gradient) > 0.01:
                    updates.append(PolicyUpdate(
                        policy_type="feature_weight",
                        parameter_name=feature,
                        old_value=old_weight,
                        new_value=self.feature_weights[feature],
                        confidence=abs(gradient),
                        reason=f"Feature sensitivity to reward"
                    ))

        return updates

    def select_coordination_pattern(
        self,
        context_features: Dict[str, float],
        available_patterns: List[str]
    ) -> str:
        """
        Select coordination pattern based on learned policy.

        Uses feature weights to score each pattern.
        """
        if not available_patterns:
            return "centralized"  # Default

        # Score each pattern
        pattern_scores = {}
        for pattern in available_patterns:
            if pattern not in self.coordination_preferences:
                continue

            # Base score from preference
            score = self.coordination_preferences[pattern]

            # Adjust based on features
            for feature, value in context_features.items():
                if feature in self.feature_weights:
                    # Feature influence on pattern selection
                    if feature == "constraint_severity" and pattern == "centralized":
                        # Centralized better under constraints
                        score += value * self.feature_weights[feature]
                    elif feature == "num_capabilities" and pattern == "distributed":
                        # Distributed better for many capabilities
                        score += value * self.feature_weights[feature]

            pattern_scores[pattern] = score

        # Select pattern with highest score
        if pattern_scores:
            return max(pattern_scores.items(), key=lambda x: x[1])[0]

        return available_patterns[0]

    def select_capabilities(
        self,
        available: List[str],
        context_features: Dict[str, float],
        max_capabilities: int = 10
    ) -> List[str]:
        """
        Select capabilities based on learned performance.

        Prioritizes capabilities with good historical performance.
        """
        # Score capabilities
        capability_scores = []
        for cap in available:
            perf = self.capability_performance[cap]

            # Base score from success rate
            score = perf["success_rate"]

            # Adjust for average reward
            score += perf["avg_reward"] * 0.5

            # Adjust for sample count (prefer more data)
            score += min(perf["count"] / 100.0, 0.2)

            # Context-specific adjustments
            if "has_mechanism" in context_features and "causal" in cap:
                score += context_features["has_mechanism"] * 0.3

            if "has_pathway" in context_features and "pathway" in cap:
                score += context_features["has_pathway"] * 0.3

            capability_scores.append((cap, score))

        # Sort by score and select top capabilities
        capability_scores.sort(key=lambda x: x[1], reverse=True)
        selected = [cap for cap, score in capability_scores[:max_capabilities]]

        return selected

    def get_policy_state(self) -> Dict[str, Any]:
        """Get current policy state."""
        return {
            "coordination_preferences": self.coordination_preferences.copy(),
            "capability_performance": {
                cap: dict(perf)
                for cap, perf in self.capability_performance.items()
            },
            "feature_weights": self.feature_weights.copy()
        }


class AntiPatternDetector:
    """Detect and avoid anti-patterns in orchestration."""

    def __init__(self, min_occurrences: int = 3):
        self.min_occurrences = min_occurrences

        # Track failed patterns
        self.failed_patterns: Dict[str, int] = defaultdict(int)

        # Track problematic capability combinations
        self.bad_combinations: Dict[Tuple[str, ...], int] = defaultdict(int)

        # Track patterns that lead to timeouts
        self.timeout_patterns: Dict[str, int] = defaultdict(int)

    def observe_outcome(self, outcome: OrchestrationOutcome) -> None:
        """Observe orchestration outcome for pattern detection."""
        # Check for failure patterns
        if not outcome.success:
            pattern_key = self._get_pattern_key(outcome)
            self.failed_patterns[pattern_key] += 1

            # Track capability combinations
            caps_tuple = tuple(sorted(outcome.capabilities_used))
            self.bad_combinations[caps_tuple] += 1

        # Check for timeouts
        duration = outcome.end_time - outcome.start_time
        if duration > 60:  # 1 minute
            pattern_key = self._get_pattern_key(outcome)
            self.timeout_patterns[pattern_key] += 1

    def _get_pattern_key(self, outcome: OrchestrationOutcome) -> str:
        """Get pattern key for outcome."""
        return f"{outcome.coordination_pattern}_{len(outcome.capabilities_used)}"

    def is_anti_pattern(
        self,
        coordination_pattern: str,
        capabilities: List[str]
    ) -> bool:
        """Check if this is a known anti-pattern."""
        # Check failed patterns
        pattern_key = f"{coordination_pattern}_{len(capabilities)}"
        if self.failed_patterns.get(pattern_key, 0) >= self.min_occurrences:
            return True

        # Check timeout patterns
        if self.timeout_patterns.get(pattern_key, 0) >= self.min_occurrences:
            return True

        # Check bad combinations
        caps_tuple = tuple(sorted(capabilities))
        if self.bad_combinations.get(caps_tuple, 0) >= self.min_occurrences:
            return True

        return False

    def get_anti_patterns(self) -> Dict[str, int]:
        """Get detected anti-patterns."""
        anti_patterns = {}

        for pattern, count in self.failed_patterns.items():
            if count >= self.min_occurrences:
                anti_patterns[f"failed_{pattern}"] = count

        for pattern, count in self.timeout_patterns.items():
            if count >= self.min_occurrences:
                anti_patterns[f"timeout_{pattern}"] = count

        for combo, count in self.bad_combinations.items():
            if count >= self.min_occurrences:
                anti_patterns[f"combo_{'_'.join(combo)}"] = count

        return anti_patterns


class OrchestratorLearner:
    """
    Main learning system for orchestrator.

    Combines:
    - Reward calculation
    - Feature extraction
    - Policy learning
    - Anti-pattern detection
    """

    def __init__(self, learning_rate: float = 0.1):
        self.reward_calculator = RewardCalculator()
        self.feature_extractor = FeatureExtractor()
        self.policy_learner = PolicyLearner(learning_rate)
        self.anti_pattern_detector = AntiPatternDetector()

        # Learning history
        self.learning_examples: List[LearningExample] = []
        self.policy_updates: List[PolicyUpdate] = []

        # Performance tracking
        self.performance_history: deque = deque(maxlen=100)

    def observe_outcome(
        self,
        outcome: OrchestrationOutcome,
        context_features: Dict[str, float]
    ) -> LearningExample:
        """
        Observe orchestration outcome and create learning example.

        Args:
            outcome: Orchestration outcome
            context_features: Features of orchestration context

        Returns:
            Learning example created from outcome
        """
        # Calculate reward
        reward = self.reward_calculator.calculate_reward(outcome)

        # Create learning example
        example = LearningExample(
            context_features=context_features,
            action_taken=outcome.coordination_pattern,
            reward=reward,
            outcome=outcome
        )

        # Store example
        self.learning_examples.append(example)

        # Track performance
        self.performance_history.append({
            "timestamp": time.time(),
            "reward": reward,
            "success": outcome.success,
            "duration": outcome.end_time - outcome.start_time
        })

        # Update anti-pattern detector
        self.anti_pattern_detector.observe_outcome(outcome)

        return example

    def learn_from_outcome(
        self,
        outcome: OrchestrationOutcome,
        context_features: Dict[str, float]
    ) -> List[PolicyUpdate]:
        """
        Learn from orchestration outcome.

        Args:
            outcome: Orchestration outcome
            context_features: Features of orchestration context

        Returns:
            List of policy updates made
        """
        # Observe outcome
        example = self.observe_outcome(outcome, context_features)

        # Update policy
        updates = self.policy_learner.update_policy(example)

        # Store updates
        self.policy_updates.extend(updates)

        return updates

    def recommend_coordination(
        self,
        query: str,
        available_capabilities: List[str],
        available_patterns: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend coordination pattern and capabilities.

        Args:
            query: User query
            available_capabilities: Available capabilities
            available_patterns: Available coordination patterns
            constraints: Optional constraints

        Returns:
            Recommendation with pattern and capabilities
        """
        # Extract features
        context_features = self.feature_extractor.extract_features(
            query,
            available_capabilities,
            constraints
        )

        # Select coordination pattern
        pattern = self.policy_learner.select_coordination_pattern(
            context_features,
            available_patterns
        )

        # Select capabilities
        capabilities = self.policy_learner.select_capabilities(
            available_capabilities,
            context_features
        )

        # Check for anti-patterns
        is_anti_pattern = self.anti_pattern_detector.is_anti_pattern(
            pattern,
            capabilities
        )

        # Get recommendation confidence
        confidence = self._calculate_recommendation_confidence(
            pattern,
            capabilities,
            context_features
        )

        return {
            "coordination_pattern": pattern,
            "capabilities": capabilities,
            "is_anti_pattern": is_anti_pattern,
            "confidence": confidence,
            "context_features": context_features,
            "reasoning": self._generate_reasoning(
                pattern,
                capabilities,
                context_features
            )
        }

    def _calculate_recommendation_confidence(
        self,
        pattern: str,
        capabilities: List[str],
        context_features: Dict[str, float]
    ) -> float:
        """Calculate confidence in recommendation."""
        # Base confidence from pattern preference
        pattern_confidence = self.policy_learner.coordination_preferences.get(
            pattern,
            0.5
        )

        # Adjust based on capability performance data
        capability_data_count = sum(
            self.policy_learner.capability_performance[cap]["count"]
            for cap in capabilities
        )
        data_confidence = min(capability_data_count / 50.0, 1.0)

        # Combined confidence
        confidence = (pattern_confidence + data_confidence) / 2.0

        return confidence

    def _generate_reasoning(
        self,
        pattern: str,
        capabilities: List[str],
        context_features: Dict[str, float]
    ) -> str:
        """Generate explanation for recommendation."""
        reasoning_parts = []

        # Pattern reasoning
        pattern_pref = self.policy_learner.coordination_preferences.get(pattern, 0.0)
        reasoning_parts.append(
            f"Selected {pattern} coordination (preference: {pattern_pref:.2f})"
        )

        # Capability reasoning
        top_capabilities = capabilities[:3]
        reasoning_parts.append(
            f"Prioritized capabilities: {', '.join(top_capabilities)}"
        )

        # Context reasoning
        if context_features.get("constraint_severity", 0) > 0.5:
            reasoning_parts.append("Accounting for significant constraints")

        return "; ".join(reasoning_parts)

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress."""
        if not self.performance_history:
            return {"status": "no_data"}

        # Calculate statistics
        rewards = [h["reward"] for h in self.performance_history]
        success_rate = sum(h["success"] for h in self.performance_history) / len(self.performance_history)

        return {
            "total_examples": len(self.learning_examples),
            "policy_updates": len(self.policy_updates),
            "average_reward": np.mean(rewards),
            "reward_std": np.std(rewards),
            "success_rate": success_rate,
            "recent_performance": np.mean(rewards[-10:]) if len(rewards) >= 10 else np.mean(rewards),
            "anti_patterns_detected": len(self.anti_pattern_detector.get_anti_patterns())
        }

    def get_capability_insights(self) -> Dict[str, Dict[str, Any]]:
        """Get insights about capability performance."""
        insights = {}

        for cap, perf in self.policy_learner.capability_performance.items():
            if perf["count"] > 0:
                insights[cap] = {
                    "success_rate": perf["success_rate"],
                    "average_reward": perf["avg_reward"],
                    "usage_count": perf["count"],
                    "reliability": "high" if perf["success_rate"] > 0.8 else "medium" if perf["success_rate"] > 0.6 else "low"
                }

        return insights


def create_orchestrator_learner(learning_rate: float = 0.1) -> OrchestratorLearner:
    """Factory function to create orchestrator learner."""
    return OrchestratorLearner(learning_rate=learning_rate)
