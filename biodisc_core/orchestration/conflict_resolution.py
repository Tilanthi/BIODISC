"""
Conflict Resolution System for BIODISC

Implements sophisticated conflict resolution strategies:
- Confidence weighting: Trust higher confidence outputs
- Expertise matching: Domain-specific priority
- Ensemble methods: Combine multiple outputs
- User preference learning: Adapt from feedback

This enables BIODISC to handle conflicting capability outputs intelligently.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import time
import numpy as np
from collections import defaultdict


class ConflictType(Enum):
    """Types of conflicts between capability outputs."""
    CONTRADICTORY = "contradictory"      # Direct contradiction (A vs not-A)
    INCOMPATIBLE = "incompatible"        # Mutually exclusive conclusions
    INCONSISTENT = "inconsistent"        # Different but potentially reconcilable
    UNCERTAIN = "uncertain"              # Low confidence in all outputs
    TEMPORAL = "temporal"                # Different time perspectives


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    CONFIDENCE_WEIGHTING = "confidence_weighting"
    EXPERTISE_MATCHING = "expertise_matching"
    ENSEMBLE_AVERAGE = "ensemble_average"
    VOTING = "voting"
    USER_PREFERENCE = "user_preference"
    META_REASONING = "meta_reasoning"
    DEFER_TO_EXPERT = "defer_to_expert"


@dataclass
class CapabilityOutput:
    """Output from a single capability."""
    capability_name: str
    result: Any
    confidence: float  # 0.0 to 1.0
    domain: str
    expertise_score: float  # 0.0 to 1.0
    reasoning_trace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conflict:
    """A detected conflict between capability outputs."""
    conflict_id: str
    conflict_type: ConflictType
    conflicting_outputs: List[CapabilityOutput]
    description: str
    severity: float  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResolutionResult:
    """Result of conflict resolution."""
    conflict_id: str
    strategy_used: ResolutionStrategy
    resolved_output: Any
    confidence: float
    explanation: str
    rejected_outputs: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExpertiseDatabase:
    """Database of capability expertise scores by domain."""

    def __init__(self):
        # Domain -> {capability -> expertise_score}
        self.expertise_scores: Dict[str, Dict[str, float]] = {
            "molecular_biology": {
                "protein_structure": 0.95,
                "molecular_interactions": 0.90,
                "biochemical_pathways": 0.85,
                "causal_reasoning": 0.70,
            },
            "genomics": {
                "sequence_analysis": 0.95,
                "gene_regulation": 0.90,
                "phylogenetic_analysis": 0.85,
                "causal_reasoning": 0.65,
            },
            "cell_biology": {
                "cellular_processes": 0.95,
                "organelle_function": 0.90,
                "signaling_pathways": 0.85,
                "causal_reasoning": 0.70,
            },
            "biochemistry": {
                "enzymology": 0.95,
                "metabolic_pathways": 0.90,
                "protein_structure": 0.85,
                "causal_reasoning": 0.70,
            },
            "general_biology": {
                "knowledge_retrieval": 0.90,
                "causal_reasoning": 0.75,
                "abstraction": 0.70,
                "synthesis": 0.65,
            },
        }

        # Historical performance data
        self.historical_performance: Dict[str, List[float]] = defaultdict(list)

    def get_expertise_score(self, capability: str, domain: str) -> float:
        """Get expertise score for capability in domain."""
        if domain in self.expertise_scores:
            return self.expertise_scores[domain].get(capability, 0.5)
        return 0.5

    def record_performance(self, capability: str, domain: str, score: float) -> None:
        """Record performance for capability in domain."""
        self.historical_performance[f"{capability}:{domain}"].append(score)

        # Update expertise score based on performance
        if len(self.historical_performance[f"{capability}:{domain}"]) > 5:
            avg_performance = np.mean(self.historical_performance[f"{capability}:{domain}"])
            if domain not in self.expertise_scores:
                self.expertise_scores[domain] = {}
            self.expertise_scores[domain][capability] = avg_performance


class UserPreferenceLearner:
    """Learn user preferences for conflict resolution."""

    def __init__(self):
        self.preference_history: List[Dict[str, Any]] = []
        self.preference_patterns: Dict[str, float] = {
            "prefer_high_confidence": 0.7,
            "prefer_domain_expert": 0.8,
            "prefer_explanation": 0.6,
            "prefer_detailed": 0.5,
        }

    def record_feedback(
        self,
        conflict_id: str,
        chosen_output: str,
        rejected_outputs: List[str],
        user_satisfaction: float
    ) -> None:
        """Record user feedback on resolution."""
        self.preference_history.append({
            "conflict_id": conflict_id,
            "chosen": chosen_output,
            "rejected": rejected_outputs,
            "satisfaction": user_satisfaction,
            "timestamp": time.time()
        })

        # Update preference patterns
        self._update_preferences(chosen_output, user_satisfaction)

    def _update_preferences(self, chosen_output: str, satisfaction: float) -> None:
        """Update preference patterns based on feedback."""
        if satisfaction > 0.7:
            # Reinforce current preferences
            for key in self.preference_patterns:
                self.preference_patterns[key] = min(1.0, self.preference_patterns[key] + 0.05)

    def get_preferred_strategy(self, context: Dict[str, Any]) -> ResolutionStrategy:
        """Get preferred resolution strategy based on learning."""
        if self.preference_patterns["prefer_domain_expert"] > 0.7:
            return ResolutionStrategy.EXPERTISE_MATCHING
        elif self.preference_patterns["prefer_high_confidence"] > 0.7:
            return ResolutionStrategy.CONFIDENCE_WEIGHTING
        else:
            return ResolutionStrategy.ENSEMBLE_AVERAGE


class ConflictDetector:
    """Detect conflicts between capability outputs."""

    def __init__(self):
        self.detection_rules: List[Callable] = [
            self._detect_contradiction,
            self._detect_incompatibility,
            self._detect_inconsistency,
            self._detect_uncertainty,
        ]

    def detect_conflicts(
        self,
        outputs: List[CapabilityOutput],
        domain: str
    ) -> List[Conflict]:
        """Detect conflicts between outputs."""
        conflicts = []

        # Check each detection rule
        for rule in self.detection_rules:
            detected = rule(outputs, domain)
            conflicts.extend(detected)

        return conflicts

    def _detect_contradiction(
        self,
        outputs: List[CapabilityOutput],
        domain: str
    ) -> List[Conflict]:
        """Detect direct contradictions."""
        conflicts = []

        # Check pairs of outputs
        for i, output1 in enumerate(outputs):
            for output2 in outputs[i+1:]:
                if self._are_contradictory(output1, output2):
                    conflicts.append(Conflict(
                        conflict_id=f"contradiction_{int(time.time()*1000)}_{i}_{len(outputs)}",
                        conflict_type=ConflictType.CONTRADICTORY,
                        conflicting_outputs=[output1, output2],
                        description=f"Contradiction between {output1.capability_name} and {output2.capability_name}",
                        severity=0.9
                    ))

        return conflicts

    def _are_contradictory(self, output1: CapabilityOutput, output2: CapabilityOutput) -> bool:
        """Check if two outputs are contradictory."""
        # Simplified check - in real system would use NLP
        result1 = str(output1.result).lower()
        result2 = str(output2.result).lower()

        # Check for explicit contradictions
        contradiction_pairs = [
            ("yes", "no"),
            ("true", "false"),
            ("increases", "decreases"),
            ("activates", "inhibits"),
            ("present", "absent"),
        ]

        for pos, neg in contradiction_pairs:
            if pos in result1 and neg in result2:
                return True
            if neg in result1 and pos in result2:
                return True

        return False

    def _detect_incompatibility(
        self,
        outputs: List[CapabilityOutput],
        domain: str
    ) -> List[Conflict]:
        """Detect incompatible outputs."""
        conflicts = []

        # Check for mutually exclusive conclusions
        # Simplified implementation
        for i, output1 in enumerate(outputs):
            for output2 in outputs[i+1:]:
                if self._are_incompatible(output1, output2):
                    conflicts.append(Conflict(
                        conflict_id=f"incompatible_{int(time.time()*1000)}_{i}_{len(outputs)}",
                        conflict_type=ConflictType.INCOMPATIBLE,
                        conflicting_outputs=[output1, output2],
                        description=f"Incompatible outputs from {output1.capability_name} and {output2.capability_name}",
                        severity=0.7
                    ))

        return conflicts

    def _are_incompatible(self, output1: CapabilityOutput, output2: CapabilityOutput) -> bool:
        """Check if outputs are incompatible."""
        # Simplified check
        result1 = str(output1.result).lower()
        result2 = str(output2.result).lower()

        # Check for incompatible values
        if "mechanism 1" in result1 and "mechanism 2" in result2:
            return True

        return False

    def _detect_inconsistency(
        self,
        outputs: List[CapabilityOutput],
        domain: str
    ) -> List[Conflict]:
        """Detect inconsistent outputs."""
        conflicts = []

        # Check for significant variations
        confidences = [out.confidence for out in outputs]
        if confidences and max(confidences) - min(confidences) > 0.5:
            conflicts.append(Conflict(
                conflict_id=f"inconsistent_{int(time.time()*1000)}",
                conflict_type=ConflictType.INCONSISTENT,
                conflicting_outputs=outputs,
                description="Significant variation in confidence levels",
                severity=0.5
            ))

        return conflicts

    def _detect_uncertainty(
        self,
        outputs: List[CapabilityOutput],
        domain: str
    ) -> List[Conflict]:
        """Detect high uncertainty across all outputs."""
        conflicts = []

        # Check if all outputs have low confidence
        if outputs and all(out.confidence < 0.5 for out in outputs):
            conflicts.append(Conflict(
                conflict_id=f"uncertain_{int(time.time()*1000)}",
                conflict_type=ConflictType.UNCERTAIN,
                conflicting_outputs=outputs,
                description="All outputs have low confidence",
                severity=0.6
            ))

        return conflicts


class ConflictResolver:
    """Resolve conflicts between capability outputs."""

    def __init__(self):
        self.expertise_db = ExpertiseDatabase()
        self.preference_learner = UserPreferenceLearner()
        self.resolution_history: List[ResolutionResult] = []

    def resolve(
        self,
        conflict: Conflict,
        domain: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ResolutionResult:
        """
        Resolve a conflict using appropriate strategy.

        Strategy selection is based on:
        - Conflict type and severity
        - User preferences (if provided)
        - Learned preference patterns
        """
        # Select resolution strategy
        strategy = self._select_strategy(conflict, user_preferences)

        # Execute strategy
        if strategy == ResolutionStrategy.CONFIDENCE_WEIGHTING:
            return self._resolve_by_confidence(conflict, domain)
        elif strategy == ResolutionStrategy.EXPERTISE_MATCHING:
            return self._resolve_by_expertise(conflict, domain)
        elif strategy == ResolutionStrategy.ENSEMBLE_AVERAGE:
            return self._resolve_by_ensemble(conflict, domain)
        elif strategy == ResolutionStrategy.VOTING:
            return self._resolve_by_voting(conflict, domain)
        else:
            # Fallback to confidence weighting
            return self._resolve_by_confidence(conflict, domain)

    def _select_strategy(
        self,
        conflict: Conflict,
        user_preferences: Optional[Dict[str, Any]]
    ) -> ResolutionStrategy:
        """Select appropriate resolution strategy."""
        # User preference takes priority
        if user_preferences and "strategy" in user_preferences:
            return ResolutionStrategy(user_preferences["strategy"])

        # Learned preferences
        context = {"conflict_type": conflict.conflict_type}
        strategy = self.preference_learner.get_preferred_strategy(context)

        # Override for specific conflict types
        if conflict.conflict_type == ConflictType.CONTRADICTORY:
            return ResolutionStrategy.EXPERTISE_MATCHING
        elif conflict.conflict_type == ConflictType.UNCERTAIN:
            return ResolutionStrategy.ENSEMBLE_AVERAGE

        return strategy

    def _resolve_by_confidence(
        self,
        conflict: Conflict,
        domain: str
    ) -> ResolutionResult:
        """
        Resolve by confidence weighting.

        Select output with highest confidence.
        """
        # Sort by confidence
        sorted_outputs = sorted(
            conflict.conflicting_outputs,
            key=lambda x: x.confidence,
            reverse=True
        )

        selected = sorted_outputs[0]
        rejected = [out.capability_name for out in sorted_outputs[1:]]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.CONFIDENCE_WEIGHTING,
            resolved_output=selected.result,
            confidence=selected.confidence,
            explanation=f"Selected {selected.capability_name} due to highest confidence ({selected.confidence:.2f})",
            rejected_outputs=rejected,
            metadata={
                "all_confidences": {out.capability_name: out.confidence for out in conflict.conflicting_outputs}
            }
        )

    def _resolve_by_expertise(
        self,
        conflict: Conflict,
        domain: str
    ) -> ResolutionResult:
        """
        Resolve by expertise matching.

        Select output from capability with highest domain expertise.
        """
        # Get expertise scores
        expertise_scores = {
            out.capability_name: self.expertise_db.get_expertise_score(out.capability_name, domain)
            for out in conflict.conflicting_outputs
        }

        # Sort by expertise
        sorted_outputs = sorted(
            conflict.conflicting_outputs,
            key=lambda x: expertise_scores[x.capability_name],
            reverse=True
        )

        selected = sorted_outputs[0]
        rejected = [out.capability_name for out in sorted_outputs[1:]]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.EXPERTISE_MATCHING,
            resolved_output=selected.result,
            confidence=expertise_scores[selected.capability_name],
            explanation=f"Selected {selected.capability_name} due to highest domain expertise ({expertise_scores[selected.capability_name]:.2f})",
            rejected_outputs=rejected,
            metadata={
                "expertise_scores": expertise_scores
            }
        )

    def _resolve_by_ensemble(
        self,
        conflict: Conflict,
        domain: str
    ) -> ResolutionResult:
        """
        Resolve by ensemble averaging.

        Combine outputs using confidence-weighted averaging.
        """
        # Calculate weighted average
        total_confidence = sum(out.confidence for out in conflict.conflicting_outputs)

        if total_confidence == 0:
            # Equal weights if all confidences are 0
            weights = [1.0 / len(conflict.conflicting_outputs)] * len(conflict.conflicting_outputs)
        else:
            weights = [out.confidence / total_confidence for out in conflict.conflicting_outputs]

        # For non-numeric outputs, select most common
        # For numeric, calculate weighted average
        if self._are_numeric_outputs(conflict.conflicting_outputs):
            numeric_results = [float(out.result) for out in conflict.conflicting_outputs]
            ensemble_result = sum(w * r for w, r in zip(weights, numeric_results))
            ensemble_confidence = total_confidence / len(conflict.conflicting_outputs)
        else:
            # Select highest confidence output
            sorted_outputs = sorted(
                conflict.conflicting_outputs,
                key=lambda x: x.confidence,
                reverse=True
            )
            ensemble_result = sorted_outputs[0].result
            ensemble_confidence = sorted_outputs[0].confidence

        rejected = [out.capability_name for out in conflict.conflicting_outputs]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.ENSEMBLE_AVERAGE,
            resolved_output=ensemble_result,
            confidence=ensemble_confidence,
            explanation=f"Ensemble combination using confidence-weighted averaging",
            rejected_outputs=rejected,
            metadata={
                "weights": dict(zip([out.capability_name for out in conflict.conflicting_outputs], weights))
            }
        )

    def _are_numeric_outputs(self, outputs: List[CapabilityOutput]) -> bool:
        """Check if outputs are numeric."""
        try:
            for out in outputs:
                float(out.result)
            return True
        except (ValueError, TypeError):
            return False

    def _resolve_by_voting(
        self,
        conflict: Conflict,
        domain: str
    ) -> ResolutionResult:
        """
        Resolve by majority voting.

        Select most common output.
        """
        # Count votes
        votes = defaultdict(int)
        for out in conflict.conflicting_outputs:
            votes[str(out.result)] += 1

        # Get most common
        most_common = max(votes.items(), key=lambda x: x[1])
        selected_output = next(
            out for out in conflict.conflicting_outputs
            if str(out.result) == most_common[0]
        )

        rejected = [out.capability_name for out in conflict.conflicting_outputs if out != selected_output]

        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.VOTING,
            resolved_output=selected_output.result,
            confidence=most_common[1] / len(conflict.conflicting_outputs),
            explanation=f"Selected output with {most_common[1]} votes out of {len(conflict.conflicting_outputs)}",
            rejected_outputs=rejected,
            metadata={
                "vote_counts": dict(votes)
            }
        )

    def provide_feedback(
        self,
        resolution: ResolutionResult,
        user_satisfaction: float
    ) -> None:
        """
        Provide feedback on resolution for learning.

        Args:
            resolution: The resolution that was provided
            user_satisfaction: User satisfaction score (0.0 to 1.0)
        """
        self.preference_learner.record_feedback(
            resolution.conflict_id,
            resolution.resolved_output,
            resolution.rejected_outputs,
            user_satisfaction
        )

        # Record in history
        self.resolution_history.append(resolution)


class ComprehensiveConflictResolver:
    """
    Main conflict resolution system.

    Provides unified interface for detecting and resolving conflicts
    between capability outputs.
    """

    def __init__(self):
        self.detector = ConflictDetector()
        self.resolver = ConflictResolver()
        self.resolution_cache: Dict[str, ResolutionResult] = {}

    def process_outputs(
        self,
        outputs: List[CapabilityOutput],
        domain: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process capability outputs and resolve any conflicts.

        Args:
            outputs: List of capability outputs
            domain: Biological domain
            user_preferences: Optional user preferences

        Returns:
            Dictionary with resolved outputs and metadata
        """
        # Detect conflicts
        conflicts = self.detector.detect_conflicts(outputs, domain)

        if not conflicts:
            # No conflicts - return original outputs
            return {
                "status": "no_conflicts",
                "outputs": outputs,
                "conflicts_detected": 0,
                "conflicts_resolved": 0
            }

        # Resolve each conflict
        resolutions = []
        for conflict in conflicts:
            # Check cache
            if conflict.conflict_id in self.resolution_cache:
                resolution = self.resolution_cache[conflict.conflict_id]
            else:
                resolution = self.resolver.resolve(conflict, domain, user_preferences)
                self.resolution_cache[conflict.conflict_id] = resolution

            resolutions.append(resolution)

        # Apply resolutions
        resolved_outputs = self._apply_resolutions(outputs, resolutions)

        return {
            "status": "conflicts_resolved",
            "outputs": resolved_outputs,
            "conflicts_detected": len(conflicts),
            "conflicts_resolved": len(resolutions),
            "resolutions": resolutions,
            "metadata": {
                "original_output_count": len(outputs),
                "resolved_output_count": len(resolved_outputs),
                "strategies_used": [r.strategy_used.value for r in resolutions]
            }
        }

    def _apply_resolutions(
        self,
        original_outputs: List[CapabilityOutput],
        resolutions: List[ResolutionResult]
    ) -> List[CapabilityOutput]:
        """Apply resolutions to create final outputs."""
        # Start with original outputs
        final_outputs = original_outputs.copy()

        # Apply each resolution
        for resolution in resolutions:
            # Remove rejected outputs
            final_outputs = [
                out for out in final_outputs
                if out.capability_name not in resolution.rejected_outputs
            ]

            # Add resolved output if not already present
            if not any(out.capability_name == f"resolved_{resolution.conflict_id}" for out in final_outputs):
                resolved_output = CapabilityOutput(
                    capability_name=f"resolved_{resolution.conflict_id}",
                    result=resolution.resolved_output,
                    confidence=resolution.confidence,
                    domain="",
                    expertise_score=0.0,
                    reasoning_trace=resolution.explanation
                )
                final_outputs.append(resolved_output)

        return final_outputs

    def provide_feedback(
        self,
        conflict_id: str,
        satisfaction: float
    ) -> None:
        """Provide feedback on a resolution."""
        if conflict_id in self.resolution_cache:
            self.resolver.provide_feedback(self.resolution_cache[conflict_id], satisfaction)

    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get statistics on conflicts and resolutions."""
        if not self.resolver.resolution_history:
            return {}

        strategy_counts = defaultdict(int)
        for resolution in self.resolver.resolution_history:
            strategy_counts[resolution.strategy_used.value] += 1

        return {
            "total_resolutions": len(self.resolver.resolution_history),
            "strategy_distribution": dict(strategy_counts),
            "cache_size": len(self.resolution_cache)
        }


def create_conflict_resolver() -> ComprehensiveConflictResolver:
    """Factory function to create conflict resolver."""
    return ComprehensiveConflictResolver()
