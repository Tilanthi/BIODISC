"""
Autonomous Decision-Making System

Implements adaptive decision-making beyond predefined workflows.
Uses V93 metacognition and V60 swarm intelligence for intelligent goal selection.

This system enables BIODISC to move from reactive instruction execution
to genuine autonomous choice in what to explore and discover.
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .config import (
    AutonomousConfig,
    GoalType,
    AutonomousGoal
)

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGap:
    """Represents a gap in knowledge that could be explored"""
    question: str
    domain: str
    gap_type: str  # knowledge_gap, pattern_anomaly, cross_domain, etc.
    importance: float
    estimated_difficulty: float
    resource_requirements: Dict[str, Any]
    related_concepts: List[str] = None


class AutonomousDecisionMaker:
    """
    Generate autonomous goals using multiple cognitive systems.

    This decision-maker moves beyond reactive workflows to genuine
    adaptive decision-making by:
    - Analyzing knowledge gaps from V73 curiosity engine
    - Using V60 swarm consensus for goal ranking
    - Applying V93 metacognitive evaluation for goal quality
    - Considering resource availability and constraints
    """

    def __init__(self,
                 v73_curiosity=None,
                 v60_swarm=None,
                 v93_metacognition=None,
                 config: Optional[AutonomousConfig] = None):
        """
        Initialize the autonomous decision-maker.

        Args:
            v73_curiosity: V73 curiosity engine instance
            v60_swarm: V60 swarm intelligence instance
            v93_metacognition: V93 metacognition instance
            config: Autonomous system configuration
        """
        self.v73_curiosity = v73_curiosity
        self.v60_swarm = v60_swarm
        self.v93_metacognition = v93_metacognition
        self.config = config or AutonomousConfig()

        # Decision-making state
        self.goal_history: List[AutonomousGoal] = []
        self.knowledge_gap_cache: List[KnowledgeGap] = []

        logger.info("Autonomous Decision-Maker initialized")

    def generate_goals(self, meta_assessment: Dict[str, Any]) -> List[AutonomousGoal]:
        """
        Generate autonomous goals for exploration.

        This is the core method that enables adaptive decision-making.
        It analyzes the current state, identifies opportunities, and
        generates prioritized goals for autonomous exploration.

        Args:
            meta_assessment: Results from metacognitive assessment

        Returns:
            List of prioritized autonomous goals
        """
        try:
            # Step 1: Assess knowledge gaps
            knowledge_gaps = self._assess_knowledge_gaps(meta_assessment)

            if not knowledge_gaps:
                logger.debug("No knowledge gaps identified")
                return []

            # Step 2: Get swarm recommendations on gap importance
            if self.v60_swarm:
                knowledge_gaps = self._rank_gaps_by_swarm_consensus(knowledge_gaps)

            # Step 3: Evaluate goal quality using metacognition
            goal_candidates = []
            for gap in knowledge_gaps:
                goal_quality = self._evaluate_goal_quality(gap, meta_assessment)

                if goal_quality > self.config.min_discovery_confidence:
                    goal = self._create_goal_from_gap(gap, goal_quality)
                    goal_candidates.append(goal)

            # Step 4: Prioritize and select top goals
            prioritized_goals = self._prioritize_goals(goal_candidates)

            # Step 5: Apply resource constraints
            feasible_goals = self._apply_resource_constraints(prioritized_goals)

            logger.info(f"Generated {len(feasible_goals)} autonomous goals")
            return feasible_goals[:self.config.discoveries_per_cycle]

        except Exception as e:
            logger.error(f"Error generating autonomous goals: {e}")
            return []

    def _assess_knowledge_gaps(self, meta_assessment: Dict[str, Any]) -> List[KnowledgeGap]:
        """
        Assess current knowledge gaps using multiple sources.

        Args:
            meta_assessment: Metacognitive assessment results

        Returns:
            List of identified knowledge gaps
        """
        gaps = []

        # Get gaps from metacognitive assessment
        if 'knowledge_gaps' in meta_assessment:
            for gap_text in meta_assessment['knowledge_gaps']:
                gap = KnowledgeGap(
                    question=gap_text,
                    domain=self._infer_domain(gap_text),
                    gap_type=self._classify_gap_type(gap_text),
                    importance=self._estimate_importance(gap_text),
                    estimated_difficulty=self._estimate_difficulty(gap_text),
                    resource_requirements=self._estimate_resources(gap_text)
                )
                gaps.append(gap)

        # Use V73 curiosity engine if available
        if self.v73_curiosity and hasattr(self.v73_curiosity, 'get_curiosity_questions'):
            try:
                v73_questions = self.v73_curiosity.get_curiosity_questions(
                    num_questions=self.config.discoveries_per_cycle
                )
                for question_obj in v73_questions:
                    gap = KnowledgeGap(
                        question=question_obj.get('question', ''),
                        domain=question_obj.get('domain', 'general'),
                        gap_type=question_obj.get('type', 'knowledge_gap'),
                        importance=question_obj.get('importance', 0.5),
                        estimated_difficulty=question_obj.get('difficulty', 0.5),
                        resource_requirements={'estimated_time': 10, 'cpu_intensity': 0.3}
                    )
                    gaps.append(gap)
            except Exception as e:
                logger.error(f"Error getting V73 curiosity questions: {e}")

        # Cache gaps for future reference
        self.knowledge_gap_cache = gaps

        return gaps

    def _rank_gaps_by_swarm_consensus(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """
        Use V60 swarm intelligence to rank knowledge gaps by consensus.

        The swarm can identify which gaps are most promising through
        collective intelligence and pheromone-based coordination.

        Args:
            gaps: List of knowledge gaps to rank

        Returns:
            Ranked list of knowledge gaps
        """
        try:
            # Simulate swarm consensus ranking
            # In full implementation, this would use pheromone fields
            # and multi-agent voting

            ranked_gaps = []
            for gap in gaps:
                # Factors in swarm consensus:
                # - Multiple agents find it interesting
                # - Pheromone strength indicates collective interest
                # - Cross-domain connections increase value

                swarm_score = self._calculate_swarm_score(gap)
                gap.importance = (gap.importance + swarm_score) / 2

                ranked_gaps.append(gap)

            # Sort by swarm-adjusted importance
            ranked_gaps.sort(key=lambda g: g.importance, reverse=True)

            return ranked_gaps

        except Exception as e:
            logger.error(f"Error in swarm consensus ranking: {e}")
            return gaps

    def _calculate_swarm_score(self, gap: KnowledgeGap) -> float:
        """Calculate swarm consensus score for a gap"""
        # Simulated swarm scoring based on gap characteristics
        score = 0.5  # Base score

        # Cross-domain questions get higher swarm interest
        if gap.gap_type == 'cross_domain':
            score += 0.2

        # Questions with multiple related concepts attract more agents
        if len(gap.related_concepts or []) > 2:
            score += 0.1

        # Balance difficulty - not too easy, not too hard
        if 0.3 < gap.estimated_difficulty < 0.7:
            score += 0.15

        return min(score, 1.0)

    def _evaluate_goal_quality(self, gap: KnowledgeGap, meta_assessment: Dict) -> float:
        """
        Evaluate goal quality using metacognitive assessment.

        Uses V93 metacognition to evaluate if pursuing this gap would
        be valuable and feasible.

        Args:
            gap: Knowledge gap to evaluate
            meta_assessment: Current metacognitive state

        Returns:
            Quality score (0.0 to 1.0)
        """
        quality_score = gap.importance  # Base score from importance

        # Metacognitive factors
        if self.v93_metacognition:
            try:
                # Check if goal aligns with cognitive capabilities
                readiness = meta_assessment.get('readiness', True)
                if not readiness:
                    quality_score *= 0.7

                # Check for cognitive biases in goal selection
                bias_check = meta_assessment.get('bias_check', {})
                if bias_check.get('biases_detected'):
                    quality_score *= 0.8

                # Evaluate if goal would advance understanding
                advancement_potential = self._evaluate_advancement_potential(gap)
                quality_score = (quality_score + advancement_potential) / 2

            except Exception as e:
                logger.error(f"Error in metacognitive evaluation: {e}")

        # Resource feasibility
        if not self._is_resource_feasible(gap):
            quality_score *= 0.6

        return min(quality_score, 1.0)

    def _create_goal_from_gap(self, gap: KnowledgeGap, quality_score: float) -> AutonomousGoal:
        """
        Create an autonomous goal from a knowledge gap.

        Args:
            gap: Knowledge gap to convert
            quality_score: Quality evaluation score

        Returns:
            AutonomousGoal object
        """
        goal_id = self._generate_goal_id(gap)

        # Determine goal type based on gap characteristics
        goal_type = self._determine_goal_type(gap)

        # Estimate resource requirements
        resource_estimate = gap.resource_requirements or self._default_resource_estimate()

        # Determine exploration strategy
        strategy = self._select_exploration_strategy(gap, goal_type)

        goal = AutonomousGoal(
            goal_id=goal_id,
            goal_type=goal_type,
            description=gap.question,
            priority=quality_score,
            estimated_value=quality_score,
            resource_estimate=resource_estimate,
            exploration_strategy=strategy,
            related_domains=[gap.domain] if gap.domain else []
        )

        return goal

    def _determine_goal_type(self, gap: KnowledgeGap) -> GoalType:
        """
        Determine what type of autonomous operation to pursue.

        Args:
            gap: Knowledge gap to analyze

        Returns:
            Appropriate GoalType for the gap
        """
        # Cross-domain questions benefit from swarm exploration
        if gap.gap_type == 'cross_domain':
            return GoalType.SWARM_EXPLORATION

        # Meta-questions about discovery methods
        if gap.gap_type == 'meta_discovery':
            return GoalType.META_DISCOVERY

        # Complex questions requiring architecture improvements
        if gap.estimated_difficulty > 0.8:
            return GoalType.SELF_MODIFICATION

        # Default: regular discovery
        return GoalType.DISCOVERY

    def _select_exploration_strategy(self, gap: KnowledgeGap, goal_type: GoalType) -> str:
        """Select appropriate exploration strategy"""
        if goal_type == GoalType.SWARM_EXPLORATION:
            return "parallel_multi_agent"
        elif goal_type == GoalType.META_DISCOVERY:
            return "recursive_reflection"
        elif gap.estimated_difficulty > 0.7:
            return "deep_divide"
        else:
            return "adaptive"

    def _prioritize_goals(self, goals: List[AutonomousGoal]) -> List[AutonomousGoal]:
        """
        Prioritize goals by multiple factors.

        Args:
            goals: List of goals to prioritize

        Returns:
            Prioritized list of goals
        """
        # Sort by priority (estimated value)
        goals.sort(key=lambda g: (g.priority, g.estimated_value), reverse=True)

        return goals

    def _apply_resource_constraints(self, goals: List[AutonomousGoal]) -> List[AutonomousGoal]:
        """
        Filter goals based on resource constraints.

        Args:
            goals: List of goals to filter

        Returns:
            List of feasible goals within resource constraints
        """
        feasible = []

        total_estimated_time = 0
        total_estimated_cpu = 0

        for goal in goals:
            # Check if adding this goal would exceed resource limits
            estimated_time = goal.resource_estimate.get('estimated_time', 10)
            estimated_cpu = goal.resource_estimate.get('cpu_intensity', 0.3)

            if (total_estimated_time + estimated_time <= 60 and
                total_estimated_cpu + estimated_cpu <= self.config.max_cpu_percent):

                feasible.append(goal)
                total_estimated_time += estimated_time
                total_estimated_cpu += estimated_cpu

            else:
                # Resource limits reached, stop adding goals
                break

        return feasible

    # Helper methods

    def _infer_domain(self, question: str) -> str:
        """Infer domain from question content"""
        question_lower = question.lower()

        # Simple keyword-based domain inference
        domain_keywords = {
            'molecular_biology': ['protein', 'dna', 'rna', 'gene', 'molecular'],
            'cell_biology': ['cell', 'membrane', 'organelle', 'nucleus'],
            'biochemistry': ['enzyme', 'metabolism', 'pathway', 'reaction'],
            'genetics': ['genetic', 'mutation', 'inheritance', 'genotype'],
            'evolutionary_biology': ['evolution', 'selection', 'adaptation', 'phylogeny']
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return domain

        return 'general'

    def _classify_gap_type(self, question: str) -> str:
        """Classify the type of knowledge gap"""
        question_lower = question.lower()

        if 'how' in question_lower and 'work' in question_lower:
            return 'mechanism'
        elif 'why' in question_lower:
            return 'causal'
        elif 'relationship' in question_lower or 'connect' in question_lower:
            return 'cross_domain'
        elif 'improve' in question_lower or 'better' in question_lower:
            return 'meta_discovery'
        else:
            return 'knowledge_gap'

    def _estimate_importance(self, question: str) -> float:
        """Estimate importance of a knowledge gap"""
        # Base importance
        importance = 0.5

        # Factors that increase importance
        question_lower = question.lower()

        # Questions about fundamental mechanisms are important
        if any(word in question_lower for word in ['fundamental', 'basic', 'underlying']):
            importance += 0.2

        # Questions with practical applications
        if any(word in question_lower for word in ['disease', 'treatment', 'therapy']):
            importance += 0.15

        # Questions about unknown areas
        if any(word in question_lower for word in ['unknown', 'unclear', 'mystery']):
            importance += 0.1

        return min(importance, 1.0)

    def _estimate_difficulty(self, question: str) -> float:
        """Estimate difficulty of exploring a knowledge gap"""
        difficulty = 0.5

        # Complex questions are harder
        if 'how' in question.lower() and len(question.split()) > 15:
            difficulty += 0.2

        # Multi-part questions are harder
        if ' and ' in question.lower() or ' or ' in question.lower():
            difficulty += 0.15

        return min(difficulty, 1.0)

    def _estimate_resources(self, question: str) -> Dict[str, Any]:
        """Estimate resource requirements for exploring a gap"""
        difficulty = self._estimate_difficulty(question)

        return {
            'estimated_time': 10 + difficulty * 20,  # 10-30 minutes
            'cpu_intensity': 0.2 + difficulty * 0.3,  # 20-50% CPU
            'memory_requirement': 0.1 + difficulty * 0.2  # 10-30% memory
        }

    def _default_resource_estimate(self) -> Dict[str, Any]:
        """Default resource estimate"""
        return {
            'estimated_time': 15,
            'cpu_intensity': 0.3,
            'memory_requirement': 0.15
        }

    def _is_resource_feasible(self, gap: KnowledgeGap) -> bool:
        """Check if exploring gap is resource feasible"""
        # Simple feasibility check
        if gap.resource_requirements:
            cpu_req = gap.resource_requirements.get('cpu_intensity', 0.3)
            return cpu_req <= self.config.max_cpu_percent
        return True

    def _evaluate_advancement_potential(self, gap: KnowledgeGap) -> float:
        """Evaluate potential for advancing understanding"""
        # Questions about mechanisms have high advancement potential
        if gap.gap_type == 'mechanism':
            return 0.8

        # Cross-domain questions have high advancement potential
        if gap.gap_type == 'cross_domain':
            return 0.75

        # Meta-discovery has very high advancement potential
        if gap.gap_type == 'meta_discovery':
            return 0.9

        # Default moderate potential
        return 0.6

    def _generate_goal_id(self, gap: KnowledgeGap) -> str:
        """Generate unique goal ID"""
        hash_input = f"{gap.question}_{datetime.now().timestamp()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]