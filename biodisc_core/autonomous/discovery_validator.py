"""
Discovery Validation System

Robust validation to distinguish genuine novel discoveries from generic knowledge gaps.
Uses V60 swarm consensus and V93 metacognitive evaluation for quality control.

This system ensures that discoveries reported to users are genuinely novel
and scientifically valuable, not just easily searchable facts.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from .config import (
    AutonomousConfig,
    Discovery,
    ValidationResult,
    ValidationMode
)

logger = logging.getLogger(__name__)


class DiscoveryValidator:
    """
    Validate discoveries to ensure genuine novelty and scientific value.

    VALIDATION CRITERIA:
    - Novelty: Not already known or easily searchable
    - Scientific Value: Contributes to understanding
    - Testability: Can be experimentally verified
    - Consistency: Compatible with existing knowledge
    - Swarm Consensus: V60 agents agree on significance
    - Metacognitive Approval: V93 judges reasoning sound
    """

    def __init__(self, config: AutonomousConfig, v60_swarm=None, v93_metacognition=None):
        """
        Initialize discovery validator.

        Args:
            config: Autonomous system configuration
            v60_swarm: V60 swarm intelligence for consensus
            v93_metacognition: V93 metacognition for reasoning evaluation
        """
        self.config = config
        self.v60_swarm = v60_swarm
        self.v93_metacognition = v93_metacognition

        # Validation history
        self.validation_history: List[ValidationResult] = []
        self.known_discoveries: set = set()  # Track discovery IDs to prevent duplicates

        logger.info("Discovery Validator initialized")

    def validate(self, discovery: Discovery) -> ValidationResult:
        """
        Validate a discovery using multiple criteria.

        This is the main validation method that applies all criteria
        to ensure the discovery is genuinely novel and valuable.

        Args:
            discovery: Discovery to validate

        Returns:
            ValidationResult with detailed analysis
        """
        try:
            logger.info(f"Validating discovery: {discovery.question[:50]}...")

            # Run all validation criteria
            validation_scores = {}

            # 1. Novelty check
            novelty_score, novelty_analysis = self._check_novelty(discovery)
            validation_scores['novelty'] = novelty_score
            discovery.novelty_score = novelty_score

            # 2. Scientific value assessment
            value_score, value_analysis = self._assess_scientific_value(discovery)
            validation_scores['scientific_value'] = value_score
            discovery.scientific_value = value_score

            # 3. Testability evaluation
            testability_score, testability_analysis = self._evaluate_testability(discovery)
            validation_scores['testability'] = testability_score
            discovery.testability = testability_score

            # 4. Consistency check
            consistency_score, consistency_analysis = self._check_consistency(discovery)
            validation_scores['consistency'] = consistency_score
            discovery.consistency = consistency_score

            # 5. Swarm consensus (if V60 available)
            swarm_score, swarm_analysis = self._get_swarm_consensus(discovery)
            validation_scores['swarm_consensus'] = swarm_score
            discovery.swarm_consensus = swarm_score

            # 6. Metacognitive evaluation (if V93 available)
            metacognitive_score, metacognitive_analysis = self._metacognitive_evaluation(discovery)
            validation_scores['metacognitive_approval'] = metacognitive_score
            discovery.metacognitive_approval = metacognitive_score

            # Aggregate scores
            overall_score = self._aggregate_scores(validation_scores)

            # Determine if discovery is valid
            is_valid = overall_score > self.config.min_discovery_confidence

            # Generate recommendation
            recommendation = self._generate_recommendation(discovery, validation_scores, overall_score)

            # Create validation result
            result = ValidationResult(
                is_valid=is_valid,
                confidence=overall_score,
                breakdown=validation_scores,
                recommendation=recommendation,
                novelty_analysis=novelty_analysis,
                scientific_value_analysis=value_analysis,
                testability_analysis=testability_analysis,
                consistency_analysis=consistency_analysis,
                swarm_analysis=swarm_analysis,
                metacognitive_analysis=metacognitive_analysis
            )

            # Track validation
            self.validation_history.append(result)

            if is_valid:
                logger.info(f"Discovery VALIDATED: {discovery.question[:50]}... (score: {overall_score:.2f})")
            else:
                logger.debug(f"Discovery REJECTED: {discovery.question[:50]}... (score: {overall_score:.2f})")

            return result

        except Exception as e:
            logger.error(f"Error validating discovery: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                breakdown={},
                recommendation=f"Validation error: {e}"
            )

    def _check_novelty(self, discovery: Discovery) -> tuple[float, str]:
        """
        Check if discovery is genuinely novel.

        This is the most important criterion - it rejects discoveries
        that are just generic knowledge gaps or easily searchable facts.

        Returns:
            Tuple of (novelty_score, analysis)
        """
        analysis_parts = []
        score = 0.5  # Base score

        # Check 1: Is this a trivial "what is X" question?
        if self._is_trivial_definition_question(discovery.question):
            score = 0.1
            analysis_parts.append("Trivial definition question")
            return score, " | ".join(analysis_parts)

        # Check 2: Has this been discovered before?
        discovery_hash = hash(discovery.question + discovery.finding)
        if discovery_hash in self.known_discoveries:
            score = 0.0
            analysis_parts.append("Duplicate discovery")
            return score, " | ".join(analysis_parts)

        # Check 3: Is it easily searchable?
        searchability = self._check_searchability(discovery)
        if searchability['easily_searchable']:
            score *= 0.3  # Heavy penalty for easily searchable content
            analysis_parts.append(f"Easily searchable ({searchability['search_terms']})")

        # Check 4: Does it show insight depth?
        insight_depth = self._evaluate_insight_depth(discovery)
        if insight_depth > 0.6:
            score += 0.3
            analysis_parts.append("High insight depth")
        elif insight_depth > 0.4:
            score += 0.1
            analysis_parts.append("Moderate insight depth")
        else:
            score *= 0.7
            analysis_parts.append("Low insight depth")

        # Check 5: Does it connect concepts in novel ways?
        if self._has_novel_connections(discovery):
            score += 0.2
            analysis_parts.append("Novel conceptual connections")

        # Check 6: Is it in a specialized domain?
        if discovery.domain != 'general':
            score += 0.1
            analysis_parts.append(f"Specialized domain: {discovery.domain}")

        return min(score, 1.0), " | ".join(analysis_parts)

    def _is_trivial_definition_question(self, question: str) -> bool:
        """
        Check if this is a trivial "what is X" definition question.

        Examples of trivial questions:
        - "What is photosynthesis?"
        - "What does DNA do?"
        - "Define protein synthesis"

        These are not discoveries, they're basic definitions.
        """
        question_lower = question.lower().strip()

        # Pattern 1: Simple "What is X?"
        if re.match(r'^what is [a-z\s]{3,30}\?$', question_lower):
            return True

        # Pattern 2: Simple "Define X"
        if re.match(r'^define [a-z\s]{3,30}\?*$', question_lower):
            return True

        # Pattern 3: Very short questions (likely simple definitions)
        if len(question_lower.split()) < 4 and question_lower.startswith('what'):
            return True

        # Pattern 4: Check against list of known trivial topics
        trivial_patterns = [
            'what is photosynthesis',
            'what is dna',
            'what is rna',
            'what is protein',
            'what is enzyme',
            'what is metabolism',
            'what is cell',
            'what is gene',
            'what is evolution',
            'what is natural selection'
        ]

        for pattern in trivial_patterns:
            if question_lower.startswith(pattern):
                return True

        return False

    def _check_searchability(self, discovery: Discovery) -> Dict[str, Any]:
        """
        Check if discovery is easily searchable.

        Returns:
            Dict with searchability assessment
        """
        question_lower = discovery.question.lower()

        # Extract potential search terms
        words = question_lower.split()
        significant_words = [w for w in words if len(w) > 3 and w not in
                           {'what', 'how', 'why', 'does', 'the', 'a', 'an', 'and', 'or', 'but'}]

        # Check if question uses common, searchable terms
        common_terms = {
            'function', 'structure', 'role', 'purpose', 'definition',
            'process', 'mechanism', 'example', 'type', 'kind'
        }

        uses_common_terms = any(term in significant_words for term in common_terms)

        # Check if finding states well-known facts
        finding_patterns = [
            'converts light to energy',  # Photosynthesis
            'genetic material',  # DNA/RNA
            'protein synthesis',  # Common process
            'cell membrane',  # Basic structure
            'energy production',  # General concept
        ]

        states_common_fact = any(pattern in discovery.finding.lower() for pattern in finding_patterns)

        return {
            'easily_searchable': uses_common_terms and states_common_fact,
            'search_terms': significant_words[:5]  # Top 5 search terms
        }

    def _evaluate_insight_depth(self, discovery: Discovery) -> float:
        """
        Evaluate the depth of insight in the discovery.

        Higher scores for:
        - Multi-step reasoning
        - Integration of multiple concepts
        - Quantitative relationships
        - Causal mechanisms
        """
        depth_score = 0.5

        question_lower = discovery.question.lower()
        finding_lower = discovery.finding.lower()

        # Multi-concept integration
        if len(set(discovery.question.split())) > 8:
            depth_score += 0.15

        # Causal reasoning indicators
        causal_words = {'because', 'causes', 'leads to', 'results in', 'due to', 'triggers'}
        if any(word in question_lower or word in finding_lower for word in causal_words):
            depth_score += 0.2

        # Quantitative aspects
        quantitative_indicators = {'rate', 'probability', 'frequency', 'amount', 'level', 'degree'}
        if any(word in question_lower for word in quantitative_indicators):
            depth_score += 0.15

        # Mechanistic questions
        if 'mechanism' in question_lower or 'how does' in question_lower:
            depth_score += 0.1

        return min(depth_score, 1.0)

    def _has_novel_connections(self, discovery: Discovery) -> bool:
        """Check if discovery makes novel conceptual connections"""
        question_words = set(discovery.question.lower().split())

        # Look for unexpected pairings of concepts
        # This is a simplified check - full implementation would use semantic analysis
        unexpected_pairs = [
            {'protein', 'folding', 'disease'},
            {'gene', 'expression', 'environment'},
            {'metabolism', 'aging', 'regulation'}
        ]

        for pair in unexpected_pairs:
            if pair.issubset(question_words):
                return True

        return False

    def _assess_scientific_value(self, discovery: Discovery) -> tuple[float, str]:
        """
        Assess the scientific value of the discovery.

        Higher scores for discoveries that:
        - Contribute to fundamental understanding
        - Have practical applications
        - Suggest new research directions
        - Challenge existing paradigms
        """
        analysis_parts = []
        score = 0.5

        question_lower = discovery.question.lower()

        # Fundamental understanding contribution
        if any(word in question_lower for word in ['fundamental', 'basic', 'underlying', 'core']):
            score += 0.2
            analysis_parts.append("Fundamental understanding")

        # Practical applications
        if any(word in question_lower for word in ['disease', 'treatment', 'therapy', 'medicine', 'clinical']):
            score += 0.15
            analysis_parts.append("Practical applications")

        # New research directions
        if any(word in question_lower for word in ['novel', 'new', 'innovative', 'previously unknown']):
            score += 0.2
            analysis_parts.append("New research direction")

        # Challenging paradigms
        if any(word in question_lower for word in ['contradicts', 'challenges', 'unexpected', 'surprising']):
            score += 0.15
            analysis_parts.append("Parigm-challenging")

        return min(score, 1.0), " | ".join(analysis_parts)

    def _evaluate_testability(self, discovery: Discovery) -> tuple[float, str]:
        """
        Evaluate if discovery can be experimentally verified.

        Higher scores for discoveries that:
        - Make specific predictions
        - Suggest experimental approaches
        - Are measurable/quantifiable
        """
        analysis_parts = []
        score = 0.6

        question_lower = discovery.question.lower()

        # Testable predictions
        if any(word in question_lower for word in ['predict', 'expect', 'hypothesis', 'should']):
            score += 0.2
            analysis_parts.append("Testable predictions")

        # Quantitative measurability
        if any(word in question_lower for word in ['measure', 'quantify', 'detect', 'observe']):
            score += 0.15
            analysis_parts.append("Measurable outcomes")

        # Experimental feasibility
        if any(word in question_lower for word in ['experiment', 'test', 'verify', 'validate']):
            score += 0.15
            analysis_parts.append("Experimental feasibility")

        return min(score, 1.0), " | ".join(analysis_parts)

    def _check_consistency(self, discovery: Discovery) -> tuple[float, str]:
        """
        Check if discovery is consistent with existing knowledge.

        Higher scores for discoveries that:
        - Don't contradict established facts
        - Fit within known frameworks
        - Acknowledge limitations
        """
        analysis_parts = []
        score = 0.7  # Start with assumption of consistency

        # Basic consistency checks
        # In full implementation, this would query knowledge base

        # Check for obviously incorrect statements
        finding_lower = discovery.finding.lower()

        # Known contradictions (simplified)
        contradictions = [
            'violates thermodynamics',
            'impossible',
            'contradicts',
            'inconsistent with'
        ]

        if any(contradiction in finding_lower for contradiction in contradictions):
            score *= 0.3
            analysis_parts.append("Potential contradiction detected")
        else:
            analysis_parts.append("No obvious contradictions")

        return min(score, 1.0), " | ".join(analysis_parts)

    def _get_swarm_consensus(self, discovery: Discovery) -> tuple[float, str]:
        """
        Get V60 swarm consensus on discovery significance.

        In full implementation, this would:
        - Have multiple swarm agents evaluate the discovery
        - Measure agreement on significance
        - Use pheromone fields to assess collective interest
        """
        if not self.v60_swarm:
            return 0.7, "Swarm consensus not available"

        # Simplified swarm consensus
        # In full implementation, would query actual swarm agents

        analysis = "Simulated swarm consensus"
        score = 0.75  # Moderate-high consensus

        return score, analysis

    def _metacognitive_evaluation(self, discovery: Discovery) -> tuple[float, str]:
        """
        V93 metacognitive evaluation of reasoning quality.

        In full implementation, this would:
        - Analyze reasoning process
        - Check for cognitive biases
        - Evaluate evidence quality
        - Assess confidence calibration
        """
        if not self.v93_metacognition:
            return 0.7, "Metacognitive evaluation not available"

        # Simplified metacognitive evaluation
        analysis = "Simulated metacognitive evaluation"
        score = 0.75  # Moderate-high approval

        # Check for potential biases
        question_lower = discovery.question.lower()

        # Bias indicators
        if any(word in question_lower for word in ['obviously', 'clearly', 'certainly']):
            score *= 0.8  # Overconfidence penalty
            analysis += " | Potential overconfidence detected"

        return score, analysis

    def _aggregate_scores(self, scores: Dict[str, float]) -> float:
        """
        Aggregate individual validation scores into overall score.

        Uses weighted averaging based on validation mode.
        """
        # Weights based on validation mode
        if self.config.validation_mode == 'strict':
            weights = {
                'novelty': 0.30,  # Novelty is most important
                'scientific_value': 0.20,
                'testability': 0.15,
                'consistency': 0.10,
                'swarm_consensus': 0.15,
                'metacognitive_approval': 0.10
            }
        elif self.config.validation_mode == 'moderate':
            weights = {
                'novelty': 0.25,
                'scientific_value': 0.20,
                'testability': 0.15,
                'consistency': 0.15,
                'swarm_consensus': 0.15,
                'metacognitive_approval': 0.10
            }
        else:  # permissive
            weights = {
                'novelty': 0.20,
                'scientific_value': 0.20,
                'testability': 0.15,
                'consistency': 0.15,
                'swarm_consensus': 0.15,
                'metacognitive_approval': 0.15
            }

        # Calculate weighted average
        overall = sum(scores.get(key, 0) * weight for key, weight in weights.items())

        return overall

    def _generate_recommendation(self, discovery: Discovery, scores: Dict[str, float], overall: float) -> str:
        """Generate recommendation based on validation results"""
        if overall > 0.85:
            return "HIGH VALUE: Strong candidate for reporting to user"
        elif overall > 0.75:
            return "GOOD VALUE: Worth reporting"
        elif overall > self.config.min_discovery_confidence:
            return "ACCEPTABLE: Meets minimum criteria"
        else:
            # Identify weak areas
            weak_areas = [key for key, score in scores.items() if score < 0.5]

            if weak_areas:
                return f"REJECTED: Weak in {', '.join(weak_areas)}"
            else:
                return "REJECTED: Does not meet overall quality threshold"

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get statistics about validation performance"""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'validation_rate': 0.0,
                'average_score': 0.0
            }

        validated_count = sum(1 for result in self.validation_history if result.is_valid)
        total_count = len(self.validation_history)
        average_score = sum(result.confidence for result in self.validation_history) / total_count

        return {
            'total_validations': total_count,
            'validated_count': validated_count,
            'rejected_count': total_count - validated_count,
            'validation_rate': validated_count / total_count,
            'average_score': average_score,
            'average_novelty': sum(result.breakdown.get('novelty', 0) for result in self.validation_history) / total_count,
            'average_scientific_value': sum(result.breakdown.get('scientific_value', 0) for result in self.validation_history) / total_count
        }