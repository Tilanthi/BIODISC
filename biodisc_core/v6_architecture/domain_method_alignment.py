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
BIODISC V6.0 - Domain-Method Alignment Optimizer

Provides principled matching of methods to domains rather than uniform adoption
of any single architecture. Optimizes method selection based on domain characteristics
and research requirements.

Key Features:
- Domain characteristic profiling
- Method capability assessment
- Compatibility optimization
- Adaptive method configuration
- Multi-domain learning
- Performance-based method selection

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

logger = logging.getLogger(__name__)


class MethodType(Enum):
    """Types of AI/ML methods for biological discovery"""
    DEEP_LEARNING = 'deep_learning'
    CAUSAL_INFERENCE = 'causal_inference'
    STATISTICAL_ANALYSIS = 'statistical_analysis'
    NEUROSYMBOLIC = 'neurosymbolic'
    HYBRID_GENERATIVE = 'hybrid_generative'
    LITERATURE_MINING = 'literature_mining'
    NETWORK_ANALYSIS = 'network_analysis'
    MECHANISTIC_MODELING = 'mechanistic_modeling'


@dataclass
class DomainCharacteristics:
    """Characteristics of biological research domains"""
    data_richness: float  # 0.0-1.0
    theoretical_maturity: float  # 0.0-1.0
    complexity_level: str  # 'low', 'medium', 'high', 'very_high'
    experimental_accessibility: float  # 0.0-1.0
    computational_requirements: str  # 'low', 'medium', 'high'
    validation_difficulty: float  # 0.0-1.0


@dataclass
class MethodCapabilities:
    """Capabilities of analysis methods"""
    data_requirement: str  # 'low', 'medium', 'high'
    interpretability: float  # 0.0-1.0
    theoretical_handling: float  # 0.0-1.0
    pattern_discovery: float  # 0.0-1.0
    causal_capability: float  # 0.0-1.0
    computational_cost: str  # 'low', 'medium', 'high'
    validation_speed: str  # 'low', 'medium', 'high'


class DomainMethodAlignmentOptimizer:
    """
    Optimizer for domain-method alignment in BIODISC discovery process.

    Performs:
    - Domain characteristic analysis
    - Method capability assessment
    - Compatibility calculation
    - Optimal method selection
    - Adaptive configuration
    - Performance learning
    """

    def __init__(self):
        self.domain_profiles = self._initialize_domain_profiles()
        self.method_capabilities = self._initialize_method_capabilities()
        self.performance_history = {}
        self.alignment_matrix = self._build_initial_alignment_matrix()

        # Thread safety
        self.lock = threading.Lock()

        logger.info("🎯 Domain-Method Alignment Optimizer initialized")

    def _initialize_domain_profiles(self) -> Dict[str, DomainCharacteristics]:
        """Initialize profiles for biological research domains"""
        return {
            'protein_folding': DomainCharacteristics(
                data_richness=0.9,
                theoretical_maturity=0.8,
                complexity_level='very_high',
                experimental_accessibility=0.7,
                computational_requirements='high',
                validation_difficulty=0.6
            ),
            'gene_expression': DomainCharacteristics(
                data_richness=0.95,
                theoretical_maturity=0.7,
                complexity_level='high',
                experimental_accessibility=0.8,
                computational_requirements='medium',
                validation_difficulty=0.4
            ),
            'cell_cycle': DomainCharacteristics(
                data_richness=0.85,
                theoretical_maturity=0.9,
                complexity_level='medium',
                experimental_accessibility=0.9,
                computational_requirements='low',
                validation_difficulty=0.3
            ),
            'epigenetics': DomainCharacteristics(
                data_richness=0.7,
                theoretical_maturity=0.6,
                complexity_level='high',
                experimental_accessibility=0.6,
                computational_requirements='medium',
                validation_difficulty=0.7
            ),
            'systems_biology': DomainCharacteristics(
                data_richness=0.5,
                theoretical_maturity=0.4,
                complexity_level='very_high',
                experimental_accessibility=0.4,
                computational_requirements='very_high',
                validation_difficulty=0.9
            ),
            'structural_biology': DomainCharacteristics(
                data_richness=0.8,
                theoretical_maturity=0.9,
                complexity_level='medium',
                experimental_accessibility=0.7,
                computational_requirements='medium',
                validation_difficulty=0.5
            ),
            'quantum_biology': DomainCharacteristics(
                data_richness=0.2,
                theoretical_maturity=0.3,
                complexity_level='very_high',
                experimental_accessibility=0.3,
                computational_requirements='very_high',
                validation_difficulty=0.95
            ),
            'synthetic_biology': DomainCharacteristics(
                data_richness=0.6,
                theoretical_maturity=0.5,
                complexity_level='high',
                experimental_accessibility=0.8,
                computational_requirements='medium',
                validation_difficulty=0.6
            ),
            'immunology': DomainCharacteristics(
                data_richness=0.8,
                theoretical_maturity=0.7,
                complexity_level='high',
                experimental_accessibility=0.7,
                computational_requirements='medium',
                validation_difficulty=0.5
            ),
            'neurobiology': DomainCharacteristics(
                data_richness=0.7,
                theoretical_maturity=0.6,
                complexity_level='very_high',
                experimental_accessibility=0.5,
                computational_requirements='high',
                validation_difficulty=0.8
            )
        }

    def _initialize_method_capabilities(self) -> Dict[MethodType, MethodCapabilities]:
        """Initialize capabilities for different analysis methods"""
        return {
            MethodType.DEEP_LEARNING: MethodCapabilities(
                data_requirement='high',
                interpretability=0.3,
                theoretical_handling=0.4,
                pattern_discovery=0.9,
                causal_capability=0.4,
                computational_cost='high',
                validation_speed='low'
            ),
            MethodType.CAUSAL_INFERENCE: MethodCapabilities(
                data_requirement='medium',
                interpretability=0.9,
                theoretical_handling=0.8,
                pattern_discovery=0.6,
                causal_capability=0.95,
                computational_cost='medium',
                validation_speed='medium'
            ),
            MethodType.STATISTICAL_ANALYSIS: MethodCapabilities(
                data_requirement='medium',
                interpretability=0.8,
                theoretical_handling=0.7,
                pattern_discovery=0.7,
                causal_capability=0.6,
                computational_cost='low',
                validation_speed='high'
            ),
            MethodType.NEUROSYMBOLIC: MethodCapabilities(
                data_requirement='low',
                interpretability=0.95,
                theoretical_handling=0.9,
                pattern_discovery=0.5,
                causal_capability=0.8,
                computational_cost='medium',
                validation_speed='medium'
            ),
            MethodType.HYBRID_GENERATIVE: MethodCapabilities(
                data_requirement='high',
                interpretability=0.5,
                theoretical_handling=0.6,
                pattern_discovery=0.95,
                causal_capability=0.7,
                computational_cost='very_high',
                validation_speed='low'
            ),
            MethodType.LITERATURE_MINING: MethodCapabilities(
                data_requirement='low',
                interpretability=0.7,
                theoretical_handling=0.5,
                pattern_discovery=0.8,
                causal_capability=0.4,
                computational_cost='low',
                validation_speed='high'
            ),
            MethodType.NETWORK_ANALYSIS: MethodCapabilities(
                data_requirement='medium',
                interpretability=0.6,
                theoretical_handling=0.6,
                pattern_discovery=0.8,
                causal_capability=0.7,
                computational_cost='medium',
                validation_speed='medium'
            ),
            MethodType.MECHANISTIC_MODELING: MethodCapabilities(
                data_requirement='medium',
                interpretability=0.9,
                theoretical_handling=0.95,
                pattern_discovery=0.5,
                causal_capability=0.9,
                computational_cost='high',
                validation_speed='low'
            )
        }

    def _build_initial_alignment_matrix(self) -> Dict[str, Dict[MethodType, float]]:
        """Build initial alignment scores between domains and methods"""
        alignment_matrix = {}

        for domain_name, domain_profile in self.domain_profiles.items():
            alignment_matrix[domain_name] = {}

            for method_type, method_caps in self.method_capabilities.items():
                alignment_score = self.calculate_domain_method_compatibility(
                    domain_profile, method_caps
                )
                alignment_matrix[domain_name][method_type] = alignment_score

        return alignment_matrix

    def optimize_method_selection(self, biological_domain: str,
                                research_question: str,
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Optimize method selection for a specific biological domain and question.

        Returns ranked list of optimal methods with configurations.
        """

        with self.lock:
            logger.info(f"🎯 Optimizing method selection for domain: {biological_domain}")

            # Get domain characteristics
            domain_profile = self.domain_profiles.get(
                biological_domain,
                self._get_default_domain_profile()
            )

            # Calculate compatibility scores for all methods
            method_rankings = []

            for method_type, method_caps in self.method_capabilities.items():
                compatibility_score = self.calculate_domain_method_compatibility(
                    domain_profile, method_caps
                )

                # Consider performance history
                performance_bonus = self.get_performance_bonus(
                    biological_domain, method_type
                )

                # Consider research question specifics
                context_adjustment = self.calculate_context_adjustment(
                    research_question, context, method_type
                )

                # Calculate final score
                final_score = (
                    0.7 * compatibility_score +
                    0.2 * performance_bonus +
                    0.1 * context_adjustment
                )

                if final_score >= 0.6:  # Only include methods with reasonable compatibility
                    method_rankings.append({
                        'method': method_type,
                        'compatibility': compatibility_score,
                        'performance_bonus': performance_bonus,
                        'context_adjustment': context_adjustment,
                        'final_score': final_score,
                        'configuration': self.suggest_method_configuration(
                            method_type, domain_profile
                        )
                    })

            # Sort by final score
            method_rankings.sort(key=lambda x: x['final_score'], reverse=True)

            logger.info(f"   Found {len(method_rankings)} optimal methods")
            for i, method in enumerate(method_rankings[:3], 1):
                logger.info(f"   {i}. {method['method'].value}: {method['final_score']:.2f}")

            return method_rankings

    def calculate_domain_method_compatibility(self, domain_profile: DomainCharacteristics,
                                            method_caps: MethodCapabilities) -> float:
        """
        Calculate compatibility score between domain and method.

        Considers:
        - Data requirement alignment
        - Complexity handling
        - Theoretical maturity match
        - Validation compatibility
        """

        compatibility = 0.5  # Base score

        # Data requirement alignment
        data_alignment = self.align_data_requirements(
            domain_profile.data_richness, method_caps.data_requirement
        )
        compatibility += 0.2 * data_alignment

        # Complexity handling
        complexity_match = self.assess_complexity_handling(
            domain_profile.complexity_level, method_caps
        )
        compatibility += 0.2 * complexity_match

        # Theoretical maturity match
        theoretical_match = self.assess_theoretical_match(
            domain_profile.theoretical_maturity, method_caps.theoretical_handling
        )
        compatibility += 0.2 * theoretical_match

        # Validation compatibility
        validation_match = self.assess_validation_compatibility(
            domain_profile.validation_difficulty, method_caps.validation_speed
        )
        compatibility += 0.2 * validation_match

        # Computational requirement match
        computational_match = self.assess_computational_match(
            domain_profile.computational_requirements, method_caps.computational_cost
        )
        compatibility += 0.2 * computational_match

        return max(0.0, min(1.0, compatibility))

    def align_data_requirements(self, data_richness: float,
                                method_requirement: str) -> float:
        """Calculate data requirement alignment"""
        requirement_levels = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        required_level = requirement_levels.get(method_requirement, 0.5)

        # Perfect alignment when domain richness matches requirement
        alignment = 1.0 - abs(data_richness - required_level)
        return max(0.0, alignment)

    def assess_complexity_handling(self, domain_complexity: str,
                                  method_caps: MethodCapabilities) -> float:
        """Assess method's ability to handle domain complexity"""
        complexity_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'very_high': 1.0}

        domain_score = complexity_scores.get(domain_complexity, 0.5)

        # Methods with higher interpretability handle complexity better
        complexity_handling = (method_caps.interpretability +
                             method_caps.theoretical_handling) / 2

        return 1.0 - abs(domain_score - complexity_handling)

    def assess_theoretical_match(self, domain_maturity: float,
                                method_theoretical_handling: float) -> float:
        """Assess match between domain theoretical maturity and method capabilities"""
        # High maturity domains benefit from methods with high theoretical handling
        if domain_maturity > 0.7:
            return method_theoretical_handling
        else:
            # Low maturity domains benefit more from pattern discovery
            return 1.0 - method_theoretical_handling * 0.5

    def assess_validation_compatibility(self, validation_difficulty: float,
                                      validation_speed: str) -> float:
        """Assess compatibility between validation difficulty and method validation speed"""
        speed_levels = {'low': 0.25, 'medium': 0.5, 'high': 0.75}
        speed_score = speed_levels.get(validation_speed, 0.5)

        # Easy validation can handle slower methods
        if validation_difficulty < 0.5:
            return 1.0 - speed_score * 0.3
        else:
            # Hard validation needs faster validation methods
            return speed_score

    def assess_computational_match(self, domain_requirement: str,
                                  method_cost: str) -> float:
        """Assess computational resource compatibility"""
        requirement_levels = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'very_high': 1.0}
        cost_levels = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'very_high': 1.0}

        domain_level = requirement_levels.get(domain_requirement, 0.5)
        method_level = cost_levels.get(method_cost, 0.5)

        # Prefer methods that don't exceed domain requirements
        if method_level <= domain_level:
            return 1.0
        else:
            return max(0.0, 1.0 - (method_level - domain_level))

    def get_performance_bonus(self, domain: str, method: MethodType) -> float:
        """Get performance bonus based on historical performance"""
        key = f"{domain}_{method.value}"

        if key in self.performance_history:
            performances = self.performance_history[key]
            recent_performance = np.mean(performances[-5:])  # Last 5 performances
            return recent_performance
        else:
            return 0.7  # Default moderate performance

    def calculate_context_adjustment(self, research_question: str,
                                    context: Dict[str, Any],
                                    method: MethodType) -> float:
        """Calculate adjustment based on specific research context"""
        adjustment = 0.7  # Base adjustment

        # Consider specific question characteristics
        question_lower = research_question.lower()

        # Adjust based on question type
        if any(word in question_lower for word in ['how', 'mechanism', 'pathway']):
            if method in [MethodType.CAUSAL_INFERENCE, MethodType.MECHANISTIC_MODELING]:
                adjustment += 0.2

        if any(word in question_lower for word in ['pattern', 'identify', 'discover']):
            if method in [MethodType.DEEP_LEARNING, MethodType.HYBRID_GENERATIVE]:
                adjustment += 0.2

        if any(word in question_lower for word in ['validate', 'confirm', 'test']):
            if method in [MethodType.STATISTICAL_ANALYSIS, MethodType.CAUSAL_INFERENCE]:
                adjustment += 0.2

        # Consider context factors
        if context.get('data_limited', False):
            if method in [MethodType.NEUROSYMBOLIC, MethodType.LITERATURE_MINING]:
                adjustment += 0.2

        if context.get('requires_interpretability', False):
            if method in [MethodType.NEUROSYMBOLIC, MethodType.CAUSAL_INFERENCE]:
                adjustment += 0.2

        return max(0.0, min(1.0, adjustment))

    def suggest_method_configuration(self, method: MethodType,
                                     domain_profile: DomainCharacteristics) -> Dict[str, Any]:
        """Suggest optimal configuration for a method in a specific domain"""

        configuration = {
            'method': method.value,
            'domain_specific_settings': True
        }

        # Domain-specific parameter suggestions
        if domain_profile.data_richness > 0.8:
            configuration['data_usage'] = 'maximum'
            configuration['ensemble_methods'] = True
        else:
            configuration['data_usage'] = 'conservative'
            configuration['data_augmentation'] = True

        if domain_profile.complexity_level in ['high', 'very_high']:
            configuration['depth'] = 'increased'
            configuration['regularization'] = 'strong'
        else:
            configuration['depth'] = 'standard'
            configuration['regularization'] = 'moderate'

        if domain_profile.validation_difficulty > 0.7:
            configuration['validation_strategy'] = 'conservative'
            configuration['cross_validation'] = 'enhanced'
        else:
            configuration['validation_strategy'] = 'standard'

        # Method-specific configurations
        if method == MethodType.DEEP_LEARNING:
            configuration.update({
                'architecture': 'transformer' if domain_profile.complexity_level == 'very_high' else 'feedforward',
                'learning_rate': 'adaptive',
                'batch_size': 'small' if domain_profile.data_richness < 0.5 else 'large'
            })

        elif method == MethodType.CAUSAL_INFERENCE:
            configuration.update({
                'causal_discovery_method': 'pc_algorithm' if domain_profile.complexity_level == 'medium' else 'ges',
                'confounding_handling': 'aggressive' if domain_profile.validation_difficulty > 0.7 else 'standard'
            })

        elif method == MethodType.NEUROSYMBOLIC:
            configuration.update({
                'logic_framework': 'prolog' if domain_profile.theoretical_maturity > 0.7 else 'first_order_logic',
                'symbolic_grounding': 'enhanced'
            })

        return configuration

    def record_method_performance(self, domain: str, method: MethodType,
                                performance_score: float):
        """Record performance of a method in a specific domain for learning"""
        key = f"{domain}_{method.value}"

        if key not in self.performance_history:
            self.performance_history[key] = []

        self.performance_history[key].append(performance_score)

        # Keep only recent performances
        if len(self.performance_history[key]) > 20:
            self.performance_history[key] = self.performance_history[key][-20:]

        logger.debug(f"📊 Recorded performance: {key} = {performance_score:.2f}")

    def get_method_recommendations(self, biological_domain: str,
                                  research_type: str = 'discovery') -> Dict[str, Any]:
        """Get method recommendations for a domain and research type"""
        context = {'research_type': research_type}
        dummy_question = f"Research question in {biological_domain}"

        optimal_methods = self.optimize_method_selection(
            biological_domain, dummy_question, context
        )

        return {
            'domain': biological_domain,
            'research_type': research_type,
            'recommended_methods': optimal_methods[:3],  # Top 3 recommendations
            'domain_profile': self.domain_profiles.get(biological_domain).__dict__,
            'recommendation_confidence': optimal_methods[0]['final_score'] if optimal_methods else 0.0
        }

    def _get_default_domain_profile(self) -> DomainCharacteristics:
        """Get default domain profile for unknown domains"""
        return DomainCharacteristics(
            data_richness=0.5,
            theoretical_maturity=0.5,
            complexity_level='medium',
            experimental_accessibility=0.5,
            computational_requirements='medium',
            validation_difficulty=0.5
        )

    def analyze_method_synergy(self, methods: List[MethodType]) -> Dict[str, Any]:
        """Analyze potential synergies between multiple methods"""
        synergy_analysis = {
            'synergy_score': 0.0,
            'complementary_strengths': [],
            'potential_conflicts': [],
            'integration_recommendations': []
        }

        # Check for complementary strengths
        if MethodType.DEEP_LEARNING in methods and MethodType.NEUROSYMBOLIC in methods:
            synergy_analysis['synergy_score'] += 0.3
            synergy_analysis['complementary_strengths'].append(
                'Deep learning pattern discovery + neurosymbolic validation'
            )

        if MethodType.CAUSAL_INFERENCE in methods and MethodType.LITERATURE_MINING in methods:
            synergy_analysis['synergy_score'] += 0.2
            synergy_analysis['complementary_strengths'].append(
                'Causal analysis + literature evidence integration'
            )

        if MethodType.HYBRID_GENERATIVE in methods:
            synergy_analysis['synergy_score'] += 0.2
            synergy_analysis['integration_recommendations'].append(
                'Hybrid generative can integrate insights from all other methods'
            )

        return synergy_analysis


# Singleton instance
_domain_method_optimizer = None

def get_domain_method_optimizer() -> DomainMethodAlignmentOptimizer:
    """Get the singleton domain-method optimizer instance"""
    global _domain_method_optimizer
    if _domain_method_optimizer is None:
        _domain_method_optimizer = DomainMethodAlignmentOptimizer()
    return _domain_method_optimizer


if __name__ == "__main__":
    # Test the domain-method alignment optimizer
    optimizer = get_domain_method_optimizer()

    # Test optimization for different domains
    test_domains = ['protein_folding', 'cell_cycle', 'quantum_biology']

    for domain in test_domains:
        print(f"\n🎯 Optimizing for domain: {domain}")
        recommendations = optimizer.get_method_recommendations(domain, 'discovery')

        print(f"Recommendation confidence: {recommendations['recommendation_confidence']:.2f}")
        print("Top 3 recommended methods:")
        for i, method in enumerate(recommendations['recommended_methods'], 1):
            print(f"  {i}. {method['method'].value}: {method['final_score']:.2f}")
            print(f"     Configuration: {list(method['configuration'].keys())}")

    # Test method synergy analysis
    print(f"\n🔗 Analyzing method synergy...")
    synergy = optimizer.analyze_method_synergy([
        MethodType.DEEP_LEARNING,
        MethodType.NEUROSYMBOLIC,
        MethodType.CAUSAL_INFERENCE
    ])

    print(f"Synergy score: {synergy['synergy_score']:.2f}")
    print(f"Complementary strengths: {synergy['complementary_strengths']}")
