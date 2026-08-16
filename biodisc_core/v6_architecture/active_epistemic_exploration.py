#!/usr/bin/env python3
# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
BIODISC V6.0 - Active Epistemic Exploration Framework

Transforms discovery from reactive to active epistemic exploration through autonomous
experimental agenda generation and adaptive refinement based on results.

Key Features:
- Autonomous experimental agenda generation
- Epistemic gap identification and prioritization
- Adaptive exploration with surprise factor handling
- Information gain estimation
- Sequential experimental design
- Active learning strategies

Date: 2026-07-04
Version: 6.0
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import threading
from collections import defaultdict, deque
import heapq

logger = logging.getLogger(__name__)


class ExplorationPriority(Enum):
    """Priority levels for epistemic exploration"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    EXPLORATORY = 5


@dataclass
class EpistemicGap:
    """Represents a gap in current scientific knowledge"""
    gap_id: str
    target_question: str
    epistemic_value: float  # Expected information gain
    experimental_accessibility: float  # Ease of experimental validation
    conceptual_dependencies: List[str]
    domain: str
    estimated_difficulty: str  # 'low', 'medium', 'high', 'very_high'
    surprise_potential: float  # Potential for unexpected discoveries


@dataclass
class ExplorationExperiment:
    """Represents an experiment in the exploration agenda"""
    experiment_id: str
    question: str
    expected_gain: float
    feasibility: float
    dependencies: List[str]
    priority: ExplorationPriority
    estimated_duration: int  # minutes
    resource_requirements: Dict[str, Any]


class EpistemicGainCalculator:
    """Calculates expected epistemic gain from potential discoveries"""

    def __init__(self):
        self.gain_factors = {
            'novelty_weight': 0.3,
            'breadth_weight': 0.2,
            'depth_weight': 0.2,
            'connectivity_weight': 0.15,
            'validation_weight': 0.15
        }
        logger.info("📊 Epistemic Gain Calculator initialized")

    def calculate_information_gain(self, gap: EpistemicGap,
                                  current_knowledge_state: Dict[str, Any]) -> float:
        """
        Calculate expected information gain from addressing an epistemic gap.

        Considers:
        - Novelty of the question
        - Breadth of impact
        - Depth of understanding
        - Connectivity to existing knowledge
        - Ease of validation
        """

        # Novelty contribution
        novelty_score = self.assess_novelty(gap, current_knowledge_state)
        novelty_contribution = self.gain_factors['novelty_weight'] * novelty_score

        # Breadth contribution
        breadth_score = self.assess_breadth(gap, current_knowledge_state)
        breadth_contribution = self.gain_factors['breadth_weight'] * breadth_score

        # Depth contribution
        depth_score = self.assess_depth(gap, current_knowledge_state)
        depth_contribution = self.gain_factors['depth_weight'] * depth_score

        # Connectivity contribution
        connectivity_score = self.assess_connectivity(gap, current_knowledge_state)
        connectivity_contribution = self.gain_factors['connectivity_weight'] * connectivity_score

        # Validation contribution
        validation_score = gap.experimental_accessibility
        validation_contribution = self.gain_factors['validation_weight'] * validation_score

        total_gain = (novelty_contribution + breadth_contribution +
                     depth_contribution + connectivity_contribution +
                     validation_contribution)

        return max(0.0, min(1.0, total_gain))

    def assess_novelty(self, gap: EpistemicGap,
                      knowledge_state: Dict[str, Any]) -> float:
        """Assess novelty of addressing this gap"""
        # Check if similar questions exist in knowledge base
        existing_questions = knowledge_state.get('known_questions', [])

        # Simple novelty assessment (can be enhanced with semantic similarity)
        novelty = 1.0  # Start with maximum novelty

        for existing_question in existing_questions:
            similarity = self.calculate_question_similarity(
                gap.target_question, existing_question
            )
            novelty = min(novelty, 1.0 - similarity)

        return max(0.1, novelty)

    def calculate_question_similarity(self, question1: str, question2: str) -> float:
        """Calculate similarity between two questions"""
        # Simple word overlap similarity (can be enhanced with NLP)
        words1 = set(question1.lower().split())
        words2 = set(question2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def assess_breadth(self, gap: EpistemicGap,
                      knowledge_state: Dict[str, Any]) -> float:
        """Assess breadth of impact across domains"""
        domain_connections = knowledge_state.get('domain_connections', {})
        gap_domain = gap.domain

        # Domains that would be affected
        affected_domains = domain_connections.get(gap_domain, [])

        # More domain connections = higher breadth
        breadth = min(1.0, len(affected_domains) / 10.0)
        return max(0.2, breadth)

    def assess_depth(self, gap: EpistemicGap,
                    knowledge_state: Dict[str, Any]) -> float:
        """Assess depth of understanding this gap would provide"""
        # Deeper questions (more specific, mechanistic) provide more depth
        question_complexity = self.assess_question_complexity(gap.target_question)
        return question_complexity

    def assess_question_complexity(self, question: str) -> float:
        """Assess complexity of a question"""
        # Simple complexity metrics
        words = question.split()
        has_mechanism = any(word in question.lower() for word in
                           ['mechanism', 'how', 'process', 'pathway', 'regulate'])
        has_specificity = len(words) > 8  # Longer questions tend to be more specific

        complexity = 0.5  # Base complexity
        if has_mechanism:
            complexity += 0.3
        if has_specificity:
            complexity += 0.2

        return min(1.0, complexity)

    def assess_connectivity(self, gap: EpistemicGap,
                           knowledge_state: Dict[str, Any]) -> float:
        """Assess how well this gap connects to existing knowledge"""
        # Check if dependencies are satisfied
        dependencies_satisfied = sum(1 for dep in gap.conceptual_dependencies
                                   if dep in knowledge_state.get('established_concepts', []))

        if not gap.conceptual_dependencies:
            return 0.5  # No dependencies = moderate connectivity

        dependency_satisfaction = dependencies_satisfied / len(gap.conceptual_dependencies)
        return dependency_satisfaction


class ActiveEpistemicExplorer:
    """
    Active epistemic exploration system for autonomous scientific discovery.

    Performs:
    - Conceptual landscape mapping
    - Epistemic gap identification
    - Exploration agenda generation
    - Adaptive execution with surprise handling
    - Sequential experimental optimization
    """

    def __init__(self, exploration_budget: int = 100):
        self.exploration_budget = exploration_budget
        self.epistemic_gain_calculator = EpistemicGainCalculator()
        self.conceptual_landscape = ConceptualLandscapeMapper()
        self.exploration_history = []
        self.current_agenda = []
        self.agenda_version = 0

        # Active exploration state
        self.experiments_completed = 0
        self.surprise_discoveries_count = 0
        self.agenda_refinements = 0

        # Thread safety
        self.lock = threading.Lock()

        logger.info("🔭 Active Epistemic Explorer initialized")
        logger.info(f"   Exploration budget: {exploration_budget} experiments")

    def design_exploration_agenda(self, current_knowledge: Dict[str, Any],
                                user_constraints: Optional[Dict[str, Any]] = None) -> List[ExplorationExperiment]:
        """
        Design autonomous exploration agenda based on epistemic landscape.

        Process:
        1. Map current conceptual landscape
        2. Identify epistemic gaps
        3. Prioritize by information gain
        4. Generate experimental sequence
        5. Optimize for resource constraints
        """

        with self.lock:
            logger.info("🔭 Designing exploration agenda...")

            # Step 1: Map conceptual landscape
            landscape = self.conceptual_landscape.map_landscape(current_knowledge)

            # Step 2: Identify epistemic gaps
            epistemic_gaps = self.identify_epistemic_gaps(landscape, current_knowledge)

            # Step 3: Prioritize by information gain
            prioritized_gaps = self.prioritize_by_information_gain(
                epistemic_gaps, current_knowledge
            )

            # Step 4: Generate experimental sequence
            exploration_agenda = self.generate_experimental_sequence(
                prioritized_gaps, user_constraints
            )

            # Step 5: Optimize agenda
            optimized_agenda = self.optimize_agenda(exploration_agenda)

            self.current_agenda = optimized_agenda
            self.agenda_version += 1

            logger.info(f"✅ Exploration agenda generated: {len(optimized_agenda)} experiments")
            logger.info(f"   Agenda version: {self.agenda_version}")

            return optimized_agenda

    def identify_epistemic_gaps(self, landscape: Dict[str, Any],
                              knowledge_state: Dict[str, Any]) -> List[EpistemicGap]:
        """Identify gaps in current knowledge landscape"""

        gaps = []

        # Analyze current knowledge coverage
        known_areas = landscape.get('established_areas', [])
        unknown_areas = landscape.get('unexplored_areas', [])

        # Generate gap descriptions from unknown areas
        for area in unknown_areas[:50]:  # Limit to top 50 unknown areas
            gap = EpistemicGap(
                gap_id=f"gap_{area.get('id', '')}",
                target_question=self.formulate_gap_question(area),
                epistemic_value=area.get('potential_value', 0.5),
                experimental_accessibility=area.get('accessibility', 0.5),
                conceptual_dependencies=area.get('dependencies', []),
                domain=area.get('domain', 'unknown'),
                estimated_difficulty=area.get('difficulty', 'medium'),
                surprise_potential=area.get('surprise_potential', 0.5)
            )
            gaps.append(gap)

        logger.info(f"   Identified {len(gaps)} epistemic gaps")
        return gaps

    def formulate_gap_question(self, area: Dict[str, Any]) -> str:
        """Formulate a research question for an epistemic gap"""
        domain = area.get('domain', 'biology')
        focus = area.get('focus', 'mechanisms')

        return f"What are the key {focus} in {domain} that remain unexplored?"

    def prioritize_by_information_gain(self, gaps: List[EpistemicGap],
                                     knowledge_state: Dict[str, Any]) -> List[EpistemicGap]:
        """Prioritize gaps by expected information gain"""

        # Calculate information gain for each gap
        gaps_with_gain = []
        for gap in gaps:
            information_gain = self.epistemic_gain_calculator.calculate_information_gain(
                gap, knowledge_state
            )
            gap.epistemic_value = information_gain
            gaps_with_gain.append(gap)

        # Sort by information gain (descending)
        gaps_with_gain.sort(key=lambda g: g.epistemic_value, reverse=True)

        logger.info(f"   Prioritized {len(gaps_with_gain)} gaps by information gain")
        return gaps_with_gain

    def generate_experimental_sequence(self, prioritized_gaps: List[EpistemicGap],
                                     user_constraints: Optional[Dict[str, Any]]) -> List[ExplorationExperiment]:
        """Generate experimental sequence from prioritized gaps"""

        experiments = []

        for i, gap in enumerate(prioritized_gaps[:self.exploration_budget]):
            # Determine priority level
            if gap.epistemic_value > 0.8:
                priority = ExplorationPriority.CRITICAL
            elif gap.epistemic_value > 0.6:
                priority = ExplorationPriority.HIGH
            elif gap.epistemic_value > 0.4:
                priority = ExplorationPriority.MEDIUM
            else:
                priority = ExplorationPriority.LOW

            experiment = ExplorationExperiment(
                experiment_id=f"exp_{gap.gap_id}",
                question=gap.target_question,
                expected_gain=gap.epistemic_value,
                feasibility=gap.experimental_accessibility,
                dependencies=gap.conceptual_dependencies,
                priority=priority,
                estimated_duration=self.estimate_experiment_duration(gap),
                resource_requirements=self.estimate_resource_requirements(gap)
            )

            experiments.append(experiment)

        logger.info(f"   Generated {len(experiments)} experiments")
        return experiments

    def estimate_experiment_duration(self, gap: EpistemicGap) -> int:
        """Estimate experiment duration in minutes"""
        base_duration = 120  # 2 hours base

        # Adjust for difficulty
        difficulty_multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0,
            'very_high': 4.0
        }

        multiplier = difficulty_multipliers.get(gap.estimated_difficulty, 1.0)

        # Adjust for accessibility
        accessibility_factor = 1.0 / (gap.experimental_accessibility + 0.1)

        duration = base_duration * multiplier * accessibility_factor
        return int(duration)

    def estimate_resource_requirements(self, gap: EpistemicGap) -> Dict[str, Any]:
        """Estimate resource requirements for experiment"""
        return {
            'computational_resources': 'high' if gap.domain in ['quantum_biology', 'systems_biology'] else 'medium',
            'data_requirements': 'high' if gap.experimental_accessibility < 0.5 else 'low',
            'validation_effort': 'high' if gap.estimated_difficulty in ['high', 'very_high'] else 'medium',
            'estimated_cost': self.estimate_experiment_cost(gap)
        }

    def estimate_experiment_cost(self, gap: EpistemicGap) -> float:
        """Estimate computational/monetary cost of experiment"""
        base_cost = 1.0

        # Adjust for difficulty and accessibility
        difficulty_penalty = {'low': 0.5, 'medium': 1.0, 'high': 2.0, 'very_high': 4.0}
        difficulty_multiplier = difficulty_penalty.get(gap.estimated_difficulty, 1.0)

        accessibility_factor = 1.0 / (gap.experimental_accessibility + 0.1)

        total_cost = base_cost * difficulty_multiplier * accessibility_factor
        return total_cost

    def optimize_agenda(self, agenda: List[ExplorationExperiment]) -> List[ExplorationExperiment]:
        """Optimize exploration agenda for resource constraints and dependencies"""

        # Sort by priority and resource efficiency
        optimized = sorted(agenda, key=lambda exp: (
            -self.priority_value(exp.priority),
            exp.expected_gain / (exp.estimated_duration / 60.0)  # Gain per hour
        ))

        # Ensure dependency order
        ordered_agenda = self.order_by_dependencies(optimized)

        logger.info(f"   Optimized agenda: {len(ordered_agenda)} experiments")
        return ordered_agenda

    def priority_value(self, priority: ExplorationPriority) -> int:
        """Get numeric value for priority ordering"""
        return priority.value

    def order_by_dependencies(self, agenda: List[ExplorationExperiment]) -> List[ExplorationExperiment]:
        """Order experiments to respect dependencies"""
        # Simple topological sort based on dependencies
        ordered = []
        remaining = agenda.copy()
        resolved_dependencies = set()

        while remaining:
            # Find experiments with satisfied dependencies
            ready = [exp for exp in remaining
                    if all(dep in resolved_dependencies for dep in exp.dependencies)]

            if not ready:
                # If no ready experiments, pick the one with fewest dependencies
                ready = [min(remaining, key=lambda e: len(e.dependencies))]

            for exp in ready:
                ordered.append(exp)
                remaining.remove(exp)
                resolved_dependencies.add(exp.experiment_id)

        return ordered

    def execute_exploration_agenda(self, agenda: List[ExplorationExperiment],
                                  discovery_engine_func) -> List[Dict[str, Any]]:
        """
        Execute exploration agenda with adaptive refinement.

        Features:
        - Sequential execution
        - Surprise factor handling
        - Adaptive agenda refinement
        - Resource monitoring
        """

        logger.info(f"🔭 Executing exploration agenda: {len(agenda)} experiments")

        results = []
        self.experiments_completed = 0
        self.surprise_discoveries_count = 0

        for i, experiment in enumerate(agenda):
            logger.info(f"🧪 Experiment {i+1}/{len(agenda)}: {experiment.question[:50]}...")

            # Execute experiment
            result = self.execute_single_experiment(experiment, discovery_engine_func)
            results.append(result)

            # Check for surprise factor
            surprise_factor = self.calculate_surprise_factor(result, experiment)

            if surprise_factor > 0.8:
                logger.info(f"🎉 SURPRISE DISCOVERY! Factor: {surprise_factor:.2f}")
                self.surprise_discoveries_count += 1

                # Adaptively refine agenda with new insights
                self.refine_agenda_with_surprise(result, agenda[i+1:])

            self.experiments_completed += 1

            # Periodic agenda refinement
            if (i + 1) % 10 == 0:  # Every 10 experiments
                self.perform_periodic_refinement(results, agenda[i+1:])

        logger.info(f"✅ Exploration complete: {len(results)} experiments executed")
        logger.info(f"   Surprise discoveries: {self.surprise_discoveries_count}")
        logger.info(f"   Agenda refinements: {self.agenda_refinements}")

        return results

    def execute_single_experiment(self, experiment: ExplorationExperiment,
                                discovery_engine_func) -> Dict[str, Any]:
        """Execute a single exploration experiment"""

        try:
            # Call the actual discovery engine function
            result = discovery_engine_func(experiment.question)

            return {
                'experiment_id': experiment.experiment_id,
                'question': experiment.question,
                'result': result,
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'expected_gain': experiment.expected_gain
            }

        except Exception as e:
            logger.error(f"❌ Experiment execution error: {e}")
            return {
                'experiment_id': experiment.experiment_id,
                'question': experiment.question,
                'result': None,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def calculate_surprise_factor(self, result: Dict[str, Any],
                                  experiment: ExplorationExperiment) -> float:
        """Calculate surprise factor based on deviation from expectations"""

        if not result.get('success'):
            return 0.0

        # Factors contributing to surprise:
        # 1. Novelty much higher than expected
        # 2. Unexpected domain connections
        # 3. Mechanistic insights in unexpected areas
        # 4. Validation results contrary to expectations

        surprise = 0.5  # Base surprise

        result_data = result.get('result', {})

        # Check if novelty is significantly higher than expected
        actual_novelty = result_data.get('novelty_score', experiment.expected_gain)
        if actual_novelty > experiment.expected_gain + 0.2:
            surprise += 0.3

        # Check for unexpected domain connections
        discovered_domains = result_data.get('discovered_domains', [])
        if len(discovered_domains) > 2:
            surprise += 0.2

        return min(1.0, surprise)

    def refine_agenda_with_surprise(self, surprise_result: Dict[str, Any],
                                  remaining_agenda: List[ExplorationExperiment]):
        """Refine remaining agenda based on surprise discovery"""

        logger.info("🔄 Refining agenda with surprise discovery...")

        # Extract insights from surprise result
        result_data = surprise_result.get('result', {})
        new_insights = result_data.get('new_insights', [])

        # Update remaining experiments based on new insights
        for experiment in remaining_agenda:
            # Re-prioritize based on new information
            for insight in new_insights:
                if insight['relevant_to'] == experiment.experiment_id:
                    experiment.expected_gain *= 1.2  # Boost priority

        self.agenda_refinements += 1

    def perform_periodic_refinement(self, results_so_far: List[Dict[str, Any]],
                                   remaining_agenda: List[ExplorationExperiment]):
        """Perform periodic agenda refinement based on accumulated results"""

        logger.info("🔄 Performing periodic agenda refinement...")

        # Analyze patterns in results so far
        patterns = self.analyze_result_patterns(results_so_far)

        # Adjust remaining agenda based on patterns
        for experiment in remaining_agenda:
            for pattern in patterns:
                if pattern['affects'] == experiment.domain:
                    experiment.expected_gain *= pattern['adjustment_factor']

        self.agenda_refinements += 1

    def analyze_result_patterns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in exploration results"""

        if not results:
            return []

        patterns = []

        # Analyze success rates
        successful_results = [r for r in results if r.get('success', False)]
        success_rate = len(successful_results) / len(results)

        if success_rate > 0.8:
            patterns.append({
                'type': 'high_success',
                'affects': 'all',
                'adjustment_factor': 1.1
            })
        elif success_rate < 0.5:
            patterns.append({
                'type': 'low_success',
                'affects': 'all',
                'adjustment_factor': 0.9
            })

        # Analyze domain-specific patterns
        domain_results = defaultdict(list)
        for result in successful_results:
            result_data = result.get('result', {})
            domain = result_data.get('domain', 'unknown')
            domain_results[domain].append(result)

        for domain, domain_specific_results in domain_results.items():
            if len(domain_specific_results) >= 3:
                avg_novelty = np.mean([r.get('result', {}).get('novelty_score', 0.5)
                                      for r in domain_specific_results])

                if avg_novelty > 0.7:
                    patterns.append({
                        'type': 'high_novelty_domain',
                        'affects': domain,
                        'adjustment_factor': 1.15
                    })

        return patterns

    def get_exploration_statistics(self) -> Dict[str, Any]:
        """Get statistics about exploration performance"""
        return {
            'experiments_completed': self.experiments_completed,
            'surprise_discoveries': self.surprise_discoveries_count,
            'agenda_refinements': self.agenda_refinements,
            'current_agenda_size': len(self.current_agenda),
            'agenda_version': self.agenda_version
        }


class ConceptualLandscapeMapper:
    """Maps the current conceptual landscape of scientific knowledge"""

    def __init__(self):
        self.knowledge_nodes = defaultdict(dict)
        self.concept_connections = defaultdict(list)
        logger.info("🗺️  Conceptual Landscape Mapper initialized")

    def map_landscape(self, current_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Map the current conceptual landscape"""

        landscape = {
            'established_areas': [],
            'unexplored_areas': [],
            'knowledge_density': {},
            'conceptual_connections': {}
        }

        # Analyze current knowledge
        for discovery in current_knowledge.get('discoveries', []):
            area = self.identify_knowledge_area(discovery)
            landscape['established_areas'].append(area)

        # Generate unexplored areas
        landscape['unexplored_areas'] = self.generate_unexplored_areas(
            landscape['established_areas']
        )

        return landscape

    def identify_knowledge_area(self, discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Identify the knowledge area covered by a discovery"""
        return {
            'id': discovery.get('id', ''),
            'domain': discovery.get('domain', 'unknown'),
            'focus': discovery.get('focus', 'general'),
            'coverage': discovery.get('coverage', 0.5)
        }

    def generate_unexplored_areas(self, established_areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate unexplored areas based on gaps in established knowledge"""

        unexplored = []

        # Generate hypothetical unexplored areas
        domains = ['protein_folding', 'gene_expression', 'epigenetics', 'systems_biology',
                  'quantum_biology', 'synthetic_biology', 'neurobiology']

        for domain in domains:
            # Check if domain is well-covered
            domain_coverage = [area for area in established_areas if area.get('domain') == domain]

            if len(domain_coverage) < 5:  # Less than 5 discoveries in domain
                unexplored.append({
                    'id': f"{domain}_gap_{len(unexplored)}",
                    'domain': domain,
                    'focus': 'mechanisms',
                    'potential_value': 0.7,
                    'accessibility': 0.6,
                    'difficulty': 'medium',
                    'surprise_potential': 0.7,
                    'dependencies': []
                })

        return unexplored


# Singleton instance
_active_epistemic_explorer = None

def get_active_epistemic_explorer() -> ActiveEpistemicExplorer:
    """Get the singleton active epistemic explorer instance"""
    global _active_epistemic_explorer
    if _active_epistemic_explorer is None:
        _active_epistemic_explorer = ActiveEpistemicExplorer()
    return _active_epistemic_explorer


if __name__ == "__main__":
    # Test the active epistemic explorer
    explorer = get_active_epistemic_explorer()

    # Create mock current knowledge
    mock_knowledge = {
        'discoveries': [
            {'id': 'd1', 'domain': 'protein_folding', 'focus': 'chaperones', 'coverage': 0.7},
            {'id': 'd2', 'domain': 'gene_expression', 'focus': 'transcription', 'coverage': 0.6}
        ],
        'known_questions': [
            'How do chaperones assist protein folding?',
            'What regulates gene transcription?'
        ]
    }

    # Design exploration agenda
    print("🔭 Designing exploration agenda...")
    agenda = explorer.design_exploration_agenda(mock_knowledge)

    print(f"\n✅ Agenda created with {len(agenda)} experiments:")
    for i, experiment in enumerate(agenda[:5], 1):
        print(f"  {i}. Priority: {experiment.priority.value}, Gain: {experiment.expected_gain:.2f}")
        print(f"     Question: {experiment.question[:60]}...")

    print(f"\n📊 Exploration statistics: {explorer.get_exploration_statistics()}")