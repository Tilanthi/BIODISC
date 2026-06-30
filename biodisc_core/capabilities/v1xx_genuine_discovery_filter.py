"""
V74 Genuine Discovery Filter - Screen Trivial Questions, Prioritize Genuine Contributions

CRITICAL PRINCIPLE: BIODISC should act as a true autonomous research scientist, focusing
on genuine discovery contributions rather than trivial definitional questions.

GENUINE DISCOVERY CONTRIBUTIONS REQUIRE:
1. Novel Computational Analysis: New analysis methods, novel applications of existing methods
2. Published Data Integration: Using data from archives, repositories, peer-reviewed sources
3. Genuine Synthesis: New insights from combining existing knowledge in novel ways
4. Original Insights: Discoveries that BIODISC itself generates through reasoning

FILTERS OUT:
- Trivial definition questions ("What is Feedback?", "What is Natural?")
- Literature lookup questions that can be answered by existing knowledge
- Questions requiring no synthesis, computation, or novel reasoning
- Questions that don't advance scientific understanding

PRIORITIZES:
- Questions requiring computational analysis
- Questions needing multi-domain synthesis
- Questions about mechanisms, causality, and quantitative relationships
- Questions that test hypotheses or generate new insights
- Meta-discovery questions that improve discovery capabilities

Date: 2026-06-28
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import re
from datetime import datetime


class ContributionType(Enum):
    """Types of genuine discovery contributions"""
    COMPUTATIONAL_ANALYSIS = "computational_analysis"  # New computational methods or analyses
    PUBLISHED_DATA_INTEGRATION = "published_data_integration"  # Using published datasets
    NOVEL_SYNTHESIS = "novel_synthesis"  # New insights from combining knowledge
    ORIGINAL_INSIGHT = "original_insight"  # Reasoning-generated discoveries
    HYPOTHESIS_GENERATION = "hypothesis_generation"  # Testable new hypotheses
    META_DISCOVERY = "meta_discovery"  # Improving discovery capabilities


class QuestionQuality(Enum):
    """Quality assessment of questions"""
    GENUINE_DISCOVERY = "genuine_discovery"  # Requires genuine contribution
    SYNTHESIS_REQUIRED = "synthesis_required"  # Needs multi-domain synthesis
    COMPUTATIONAL_REQUIRED = "computational_required"  # Needs computational analysis
    LITERATURE_LOOKUP = "literature_lookup"  # Can be answered from existing knowledge
    TRIVIAL_DEFINITION = "trivial_definition"  # Simple definition question
    INSUFFICIENT_CONTEXT = "insufficient_context"  # Not enough context to assess


@dataclass
class GenuineContributionCriteria:
    """Criteria for assessing genuine discovery contributions"""
    # Computational Analysis Criteria
    requires_computation: bool = False
    requires_novel_methods: bool = False
    requires_quantitative_analysis: bool = False

    # Data Source Criteria
    requires_published_data: bool = False
    acceptable_data_sources: List[str] = field(default_factory=lambda: [
        "peer_reviewed",
        "preprint",
        "data_archive",
        "repository",
        "database",
        "published_dataset"
    ])

    # Synthesis Criteria
    requires_cross_domain_synthesis: bool = False
    requires_multi_level_analysis: bool = False
    requires_causal_reasoning: bool = False

    # Insight Criteria
    requires_hypothesis_generation: bool = False
    requires_novel_connections: bool = False
    requires_testable_prediction: bool = False

    # Meta-Discovery Criteria
    is_meta_discovery: bool = False
    improves_capabilities: bool = False


@dataclass
class QuestionAssessment:
    """Assessment of a question's discovery potential"""
    question: str
    quality: QuestionQuality
    contribution_type: Optional[ContributionType]
    confidence: float

    # Detailed assessment
    reasons: List[str] = field(default_factory=list)
    potential_discovery: Optional[str] = None  # What might be discovered
    required_capabilities: List[str] = field(default_factory=list)
    suggested_data_sources: List[str] = field(default_factory=list)
    computational_needs: List[str] = field(default_factory=list)

    # Filtering decision
    is_genuine_contribution: bool = False
    should_filter_out: bool = False

    # Priority for exploration
    discovery_priority: float = 0.0  # 0-1, higher = more valuable
    estimated_scientific_value: float = 0.0  # 0-1


class GenuineDiscoveryFilter:
    """
    Filter and prioritize questions based on genuine discovery contribution potential.

    PRINCIPLES:
    1. Filter out trivial questions that don't require genuine contribution
    2. Prioritize questions requiring computational analysis
    3. Prioritize questions using published data sources
    4. Prioritize questions requiring novel synthesis
    5. Prioritize meta-discovery that improves capabilities
    """

    def __init__(self):
        # Trivial definition patterns
        self.definition_patterns = [
            r'^What is [A-Z][a-z]+\?$',
            r'^What are [A-Z][a-z]+\?$',
            r'^Define [A-Z][a-z]+\.',
            r'^Explain what [A-Z][a-z]+ means\.$',
            r'^What does [A-Z][a-z]+ mean\?$',
        ]

        # Literature lookup patterns (can be answered from existing knowledge)
        self.literature_lookup_patterns = [
            r'^What is the function of [A-Z][a-z]+\?$',
            r'^Where is [A-Z][a-z]+ found\?$',
            r'^What is the structure of [A-Z][a-z]+\?$',
            r'^Who discovered [A-Z][a-z]+\?$',
            r'^When was [A-Z][a-z]+ discovered\?$',
        ]

        # Genuine discovery patterns (require contribution)
        self.genuine_discovery_patterns = [
            r'How does .* influence .*$',  # Mechanism questions
            r'What determines .*',  # Causality questions (more flexible)
            r'Why do .*',  # Explanation questions
            r'How do .*',  # Mechanism questions (added)
            r'Can we improve .*$',  # Improvement questions
            r'What is the relationship between .* and .*$',  # Relationship questions
            r'How can .* be optimized',  # Optimization questions
            r'What mechanisms regulate .*$',  # Mechanism questions
            r'What would happen if .*$',  # Counterfactual questions
            r'How does .* affect .*$',  # Causality questions
            r'What are the quantitative .*',  # Quantitative questions
            r'How can we measure .*$',  # Measurement questions
            r'What predicts .*$',  # Predictive questions
            r'How does .* vary with .*$',  # Relationship questions
        ]

        # Meta-discovery patterns
        self.meta_discovery_patterns = [
            r'How can we improve .* discovery',
            r'What limits .* analysis',
            r'How can .* be optimized',
            r'What would make .* more efficient',
            r'Can we develop .* method',
        ]

        # Computational analysis keywords
        self.computational_keywords = [
            'quantitative', 'computational', 'algorithm', 'model', 'simulate',
            'analyze', 'predict', 'optimize', 'calculate', 'measure', 'estimate',
            'correlation', 'distribution', 'pattern', 'network', 'trajectory',
            'dynamics', 'kinetics', 'thermodynamics', 'statistical', 'probabilistic'
        ]

        # Cross-domain synthesis keywords
        self.synthesis_keywords = [
            'integration', 'combine', 'synthesis', 'interdisciplinary', 'multi-domain',
            'connection', 'relationship', 'interaction', 'coupling', 'feedback',
            'emergent', 'systems', 'network', 'complex', 'holistic'
        ]

        # Data source indicators
        self.data_source_keywords = [
            'data', 'dataset', 'experiment', 'measurement', 'observation',
            'published', 'repository', 'archive', 'database', 'literature',
            'study', 'research', 'findings', 'evidence', 'results'
        ]

    def assess_question(self, question: str, context: Optional[str] = None) -> QuestionAssessment:
        """
        Assess a question's genuine discovery contribution potential.

        Args:
            question: The question to assess
            context: Optional context for the question

        Returns:
            QuestionAssessment with detailed analysis
        """
        # Initialize assessment
        assessment = QuestionAssessment(
            question=question,
            quality=QuestionQuality.INSUFFICIENT_CONTEXT,
            contribution_type=None,
            confidence=0.5,
            is_genuine_contribution=False,
            should_filter_out=False,
            discovery_priority=0.0,
            estimated_scientific_value=0.0
        )

        # Check if it's a trivial definition question
        if self._is_trivial_definition(question):
            assessment.quality = QuestionQuality.TRIVIAL_DEFINITION
            assessment.should_filter_out = True
            assessment.reasons.append("Trivial definition question - can be answered by existing knowledge")
            assessment.confidence = 0.95
            return assessment

        # Check if it's a literature lookup question
        if self._is_literature_lookup(question):
            assessment.quality = QuestionQuality.LITERATURE_LOOKUP
            assessment.should_filter_out = True
            assessment.reasons.append("Literature lookup question - no genuine contribution required")
            assessment.confidence = 0.90
            return assessment

        # Check if it's a genuine discovery question
        if self._is_genuine_discovery(question):
            assessment.quality = QuestionQuality.GENUINE_DISCOVERY
            assessment.is_genuine_contribution = True
            assessment.should_filter_out = False

            # Determine contribution type
            assessment.contribution_type = self._determine_contribution_type(question, context)
            assessment.reasons.extend(self._generate_reasons(question, assessment.contribution_type))
            assessment.required_capabilities = self._identify_required_capabilities(question)
            assessment.computational_needs = self._identify_computational_needs(question)

            # Calculate priority
            assessment.discovery_priority = self._calculate_discovery_priority(question, assessment.contribution_type)
            assessment.estimated_scientific_value = self._estimate_scientific_value(question, assessment.contribution_type)
            assessment.confidence = 0.85

            return assessment

        # Check if it's a synthesis question
        if self._is_synthesis_question(question):
            assessment.quality = QuestionQuality.SYNTHESIS_REQUIRED
            assessment.is_genuine_contribution = True
            assessment.should_filter_out = False
            assessment.contribution_type = ContributionType.NOVEL_SYNTHESIS
            assessment.reasons.append("Requires cross-domain synthesis - genuine contribution")
            assessment.required_capabilities = ['cross_domain_synthesis', 'knowledge_integration']
            assessment.discovery_priority = 0.7
            assessment.estimated_scientific_value = 0.75
            assessment.confidence = 0.80
            return assessment

        # Check if it's a computational question
        if self._is_computational_question(question):
            assessment.quality = QuestionQuality.COMPUTATIONAL_REQUIRED
            assessment.is_genuine_contribution = True
            assessment.should_filter_out = False
            assessment.contribution_type = ContributionType.COMPUTATIONAL_ANALYSIS
            assessment.reasons.append("Requires computational analysis - genuine contribution")
            assessment.required_capabilities = ['computational_analysis', 'quantitative_methods']
            assessment.computational_needs = self._identify_computational_needs(question)
            assessment.discovery_priority = 0.8
            assessment.estimated_scientific_value = 0.80
            assessment.confidence = 0.85
            return assessment

        # If it's not a trivial definition or literature lookup, but also doesn't match genuine patterns,
        # mark as insufficient context (better to filter out uncertain questions)
        assessment.reasons.append("Insufficient context to determine if genuine contribution")
        assessment.should_filter_out = True  # Better to filter out uncertain questions
        return assessment

        # Check if it's a synthesis question
        if self._is_synthesis_question(question):
            assessment.quality = QuestionQuality.SYNTHESIS_REQUIRED
            assessment.is_genuine_contribution = True
            assessment.should_filter_out = False
            assessment.contribution_type = ContributionType.NOVEL_SYNTHESIS
            assessment.reasons.append("Requires cross-domain synthesis - genuine contribution")
            assessment.required_capabilities = ['cross_domain_synthesis', 'knowledge_integration']
            assessment.discovery_priority = 0.7
            assessment.estimated_scientific_value = 0.75
            assessment.confidence = 0.80
            return assessment

        # Check if it's a computational question
        if self._is_computational_question(question):
            assessment.quality = QuestionQuality.COMPUTATIONAL_REQUIRED
            assessment.is_genuine_contribution = True
            assessment.should_filter_out = False
            assessment.contribution_type = ContributionType.COMPUTATIONAL_ANALYSIS
            assessment.reasons.append("Requires computational analysis - genuine contribution")
            assessment.required_capabilities = ['computational_analysis', 'quantitative_methods']
            assessment.computational_needs = self._identify_computational_needs(question)
            assessment.discovery_priority = 0.8
            assessment.estimated_scientific_value = 0.80
            assessment.confidence = 0.85
            return assessment

        # If no clear pattern, mark as insufficient context
        assessment.reasons.append("Insufficient context to determine if genuine contribution")
        assessment.should_filter_out = True  # Better to filter out uncertain questions
        return assessment

    def _is_trivial_definition(self, question: str) -> bool:
        """Check if question is a trivial definition request"""
        question_lower = question.lower().strip()

        # Direct pattern matching
        for pattern in self.definition_patterns:
            if re.match(pattern, question_lower, re.IGNORECASE):
                return True

        # Simple "What is X?" pattern with single biological term
        if re.match(r'^what is [a-z]+$', question_lower):
            return True

        return False

    def _is_literature_lookup(self, question: str) -> bool:
        """Check if question can be answered by literature lookup"""
        question_lower = question.lower().strip()

        # Direct pattern matching
        for pattern in self.literature_lookup_patterns:
            if re.match(pattern, question_lower, re.IGNORECASE):
                return True

        return False

    def _is_genuine_discovery(self, question: str) -> bool:
        """Check if question requires genuine discovery contribution"""
        question_lower = question.lower().strip()

        # Direct pattern matching for genuine discovery
        for pattern in self.genuine_discovery_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return True

        return False

    def _is_synthesis_question(self, question: str) -> bool:
        """Check if question requires cross-domain synthesis"""
        question_lower = question.lower()

        # Check for synthesis keywords
        synthesis_count = sum(1 for keyword in self.synthesis_keywords if keyword in question_lower)

        # Also check for words indicating relationship between domains
        relationship_indicators = ['relationship between', 'interaction', 'connection', 'integration', 'combine']

        for indicator in relationship_indicators:
            if indicator in question_lower:
                return True

        return synthesis_count >= 2

    def _is_computational_question(self, question: str) -> bool:
        """Check if question requires computational analysis"""
        question_lower = question.lower()

        # Check for computational keywords
        computational_count = sum(1 for keyword in self.computational_keywords if keyword in question_lower)

        # Check for quantitative/analytical indicators
        quantitative_indicators = ['how much', 'how many', 'quantitative', 'calculate', 'measure', 'estimate', 'predict']

        for indicator in quantitative_indicators:
            if indicator in question_lower:
                return True

        return computational_count >= 2

    def _determine_contribution_type(self, question: str, context: Optional[str] = None) -> ContributionType:
        """Determine the type of contribution required"""
        question_lower = question.lower()

        # Check for meta-discovery
        if any(re.search(pattern, question_lower) for pattern in self.meta_discovery_patterns):
            return ContributionType.META_DISCOVERY

        # Check for computational analysis
        if self._is_computational_question(question):
            return ContributionType.COMPUTATIONAL_ANALYSIS

        # Check for data integration
        if any(keyword in question_lower for keyword in self.data_source_keywords):
            return ContributionType.PUBLISHED_DATA_INTEGRATION

        # Check for hypothesis generation
        if any(word in question_lower for word in ['hypothesis', 'predict', 'would happen if', 'consequence']):
            return ContributionType.HYPOTHESIS_GENERATION

        # Default to novel synthesis
        return ContributionType.NOVEL_SYNTHESIS

    def _generate_reasons(self, question: str, contribution_type: ContributionType) -> List[str]:
        """Generate reasons for the assessment"""
        reasons = []

        if contribution_type == ContributionType.COMPUTATIONAL_ANALYSIS:
            reasons.append("Requires novel computational analysis")
            reasons.append("Cannot be answered by literature lookup alone")

        elif contribution_type == ContributionType.PUBLISHED_DATA_INTEGRATION:
            reasons.append("Requires integration of published data")
            reasons.append("Needs data source validation and analysis")

        elif contribution_type == ContributionType.NOVEL_SYNTHESIS:
            reasons.append("Requires synthesis of multiple domains")
            reasons.append("Genuinely new insight from existing knowledge")

        elif contribution_type == ContributionType.HYPOTHESIS_GENERATION:
            reasons.append("Generates testable hypotheses")
            reasons.append("Advances scientific understanding")

        elif contribution_type == ContributionType.META_DISCOVERY:
            reasons.append("Improves discovery capabilities")
            reasons.append("Meta-contribution to scientific methodology")

        return reasons

    def _identify_required_capabilities(self, question: str) -> List[str]:
        """Identify required capabilities for the question"""
        capabilities = []
        question_lower = question.lower()

        if any(word in question_lower for word in ['quantitative', 'calculate', 'measure']):
            capabilities.append('quantitative_analysis')

        if any(word in question_lower for word in ['predict', 'model', 'simulate']):
            capabilities.append('predictive_modeling')

        if any(word in question_lower for word in ['caus', 'mechanism', 'why']):
            capabilities.append('causal_reasoning')

        if any(word in question_lower for word in ['optimize', 'improve', 'enhance']):
            capabilities.append('optimization')

        if any(word in question_lower for word in ['relationship', 'interaction', 'network']):
            capabilities.append('network_analysis')

        if any(word in question_lower for word in ['data', 'experiment', 'measurement']):
            capabilities.append('data_integration')

        return capabilities

    def _identify_computational_needs(self, question: str) -> List[str]:
        """Identify computational needs for the question"""
        needs = []
        question_lower = question.lower()

        if any(word in question_lower for word in ['quantitative', 'measure', 'calculate', 'estimate']):
            needs.append('quantitative_analysis')

        if any(word in question_lower for word in ['predict', 'forecast', 'project']):
            needs.append('predictive_modeling')

        if any(word in question_lower for word in ['optimize', 'maximize', 'minimize']):
            needs.append('optimization_algorithms')

        if any(word in question_lower for word in ['pattern', 'cluster', 'classify']):
            needs.append('pattern_recognition')

        if any(word in question_lower for word in ['network', 'interaction', 'connectivity']):
            needs.append('network_analysis')

        if any(word in question_lower for word in ['simulate', 'model']):
            needs.append('simulation')

        if any(word in question_lower for word in ['statistical', 'probability', 'distribution']):
            needs.append('statistical_analysis')

        return needs

    def _calculate_discovery_priority(self, question: str, contribution_type: ContributionType) -> float:
        """Calculate priority for exploration (0-1)"""
        base_priority = 0.5

        # Meta-discovery gets highest priority
        if contribution_type == ContributionType.META_DISCOVERY:
            base_priority = 0.9

        # Computational analysis gets high priority
        elif contribution_type == ContributionType.COMPUTATIONAL_ANALYSIS:
            base_priority = 0.8

        # Data integration gets medium-high priority
        elif contribution_type == ContributionType.PUBLISHED_DATA_INTEGRATION:
            base_priority = 0.75

        # Hypothesis generation gets medium-high priority
        elif contribution_type == ContributionType.HYPOTHESIS_GENERATION:
            base_priority = 0.7

        # Novel synthesis gets medium priority
        elif contribution_type == ContributionType.NOVEL_SYNTHESIS:
            base_priority = 0.6

        return base_priority

    def _estimate_scientific_value(self, question: str, contribution_type: ContributionType) -> float:
        """Estimate scientific value (0-1)"""
        base_value = 0.5

        # Higher value for contributions that advance understanding
        if contribution_type in [
            ContributionType.META_DISCOVERY,
            ContributionType.COMPUTATIONAL_ANALYSIS,
            ContributionType.HYPOTHESIS_GENERATION
        ]:
            base_value = 0.85

        elif contribution_type == ContributionType.PUBLISHED_DATA_INTEGRATION:
            base_value = 0.80

        elif contribution_type == ContributionType.NOVEL_SYNTHESIS:
            base_value = 0.70

        return base_value

    def filter_questions(self, questions: List[str]) -> Tuple[List[str], List[QuestionAssessment]]:
        """
        Filter a list of questions, returning only genuine discovery contributions.

        Args:
            questions: List of questions to filter

        Returns:
            Tuple of (filtered_questions, assessments)
        """
        genuine_questions = []
        assessments = []

        for question in questions:
            assessment = self.assess_question(question)

            assessments.append(assessment)

            # Keep only genuine contributions
            if assessment.is_genuine_contribution and not assessment.should_filter_out:
                genuine_questions.append(question)

        return genuine_questions, assessments

    def get_filter_statistics(self, assessments: List[QuestionAssessment]) -> Dict[str, Any]:
        """Get statistics on filtering results"""
        stats = {
            'total_questions': len(assessments),
            'genuine_discoveries': sum(1 for a in assessments if a.quality == QuestionQuality.GENUINE_DISCOVERY),
            'synthesis_required': sum(1 for a in assessments if a.quality == QuestionQuality.SYNTHESIS_REQUIRED),
            'computational_required': sum(1 for a in assessments if a.quality == QuestionQuality.COMPUTATIONAL_REQUIRED),
            'literature_lookup': sum(1 for a in assessments if a.quality == QuestionQuality.LITERATURE_LOOKUP),
            'trivial_definitions': sum(1 for a in assessments if a.quality == QuestionQuality.TRIVIAL_DEFINITION),
            'filtered_out': sum(1 for a in assessments if a.should_filter_out),
            'kept': sum(1 for a in assessments if not a.should_filter_out),
            'average_priority': sum(a.discovery_priority for a in assessments) / len(assessments) if assessments else 0,
            'average_scientific_value': sum(a.estimated_scientific_value for a in assessments) / len(assessments) if assessments else 0
        }

        return stats


# Singleton instance
_instance = None


def get_genuine_discovery_filter() -> GenuineDiscoveryFilter:
    """Get singleton instance of the filter"""
    global _instance
    if _instance is None:
        _instance = GenuineDiscoveryFilter()
    return _instance


def create_genuine_discovery_filter() -> GenuineDiscoveryFilter:
    """Factory function to create a new filter instance"""
    return GenuineDiscoveryFilter()


# Utility functions for common use cases

def filter_autonomous_discovery_questions(questions: List[str]) -> List[str]:
    """
    Filter questions for autonomous discovery, keeping only genuine contributions.

    This is the main entry point for integrating V74 into the autonomous discovery system.
    """
    filter_instance = get_genuine_discovery_filter()
    genuine_questions, assessments = filter_instance.filter_questions(questions)

    # Log statistics
    stats = filter_instance.get_filter_statistics(assessments)

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Filtered {stats['total_questions']} questions: {stats['kept']} genuine contributions kept, {stats['filtered_out']} filtered out")
    logger.info(f"  - Trivial definitions filtered: {stats['trivial_definitions']}")
    logger.info(f"  - Literature lookup filtered: {stats['literature_lookup']}")
    logger.info(f"  - Genuine discoveries: {stats['genuine_discoveries']}")
    logger.info(f"  - Synthesis required: {stats['synthesis_required']}")
    logger.info(f"  - Computational required: {stats['computational_required']}")

    return genuine_questions


def assess_single_question(question: str) -> QuestionAssessment:
    """Assess a single question for genuine discovery potential"""
    filter_instance = get_genuine_discovery_filter()
    return filter_instance.assess_question(question)
