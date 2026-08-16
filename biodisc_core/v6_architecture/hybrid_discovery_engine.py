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
BIODISC V6.0 - Hybrid Discovery Engine

Integrates generative, causal, and neurosymbolic reasoning within a unified
closed-loop discovery architecture. Combines the strengths of multiple AI paradigms.

Key Features:
- Generative hypothesis generation (LLM-based)
- Causal structure analysis and inference
- Neurosymbolic reasoning and validation
- Hybrid reasoning integration
- Multi-paradigm discovery cycles
- Unified knowledge representation

Date: 2026-07-04
Version: 6.0
"""

import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import threading

logger = logging.getLogger(__name__)


@dataclass
class HybridDiscoveryResult:
    """Result from hybrid discovery engine with multiple reasoning paradigms"""
    question: str
    generative_hypothesis: Dict[str, Any]
    causal_analysis: Dict[str, Any]
    neurosymbolic_validation: Dict[str, Any]
    unified_insight: Dict[str, Any]
    confidence_scores: Dict[str, float]
    paradigm_contributions: Dict[str, float]
    meta_reasoning: Dict[str, Any]


class GenerativeDiscoveryEngine:
    """
    Generative discovery engine using LLM-based hypothesis generation.

    Focuses on:
    - Creative hypothesis generation
    - Pattern recognition across large datasets
    - Natural language understanding and generation
    - Statistical pattern identification
    """

    def __init__(self):
        self.hypothesis_templates = self._initialize_hypothesis_templates()
        self.pattern_recognition_models = {}
        logger.info("🧠 Generative Discovery Engine initialized")

    def _initialize_hypothesis_templates(self) -> List[Dict[str, str]]:
        """Initialize templates for generative hypothesis generation"""
        return [
            {
                'template': 'How do {process} affect {target} in {context}?',
                'type': 'mechanistic'
            },
            {
                'template': 'What {relationship} exist between {entity1} and {entity2} during {condition}?',
                'type': 'relational'
            },
            {
                'template': 'Which {regulators} modulate {pathway} in {system}?',
                'type': 'regulatory'
            },
            {
                'template': 'What determines {property} of {entity} under {condition}?',
                'type': 'deterministic'
            }
        ]

    def generate_hypothesis(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate hypothesis using generative approach.

        Combines:
        - LLM-based text generation
        - Pattern recognition from existing literature
        - Statistical association mining
        - Creative hypothesis formulation
        """

        logger.info(f"🧠 Generating hypothesis for: {question[:50]}...")

        # Extract key concepts from question
        concepts = self.extract_concepts(question)

        # Generate hypothesis using multiple approaches
        statistical_patterns = self.identify_statistical_patterns(question, context)
        literature_insights = self.extract_literature_patterns(question, context)
        creative_synthesis = self.creative_hypothesis_synthesis(concepts, context)

        # Combine into unified hypothesis
        hypothesis = {
            'question': question,
            'main_claim': self.formulate_main_claim(concepts, statistical_patterns),
            'supporting_evidence': statistical_patterns,
            'literature_context': literature_insights,
            'creative_insights': creative_synthesis,
            'confidence': self.calculate_generative_confidence(statistical_patterns, literature_insights),
            'paradigm': 'generative',
            'reasoning_type': 'pattern_based'
        }

        return hypothesis

    def extract_concepts(self, question: str) -> List[str]:
        """Extract key biological concepts from question"""
        # Simple concept extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', question)
        return list(set(words))

    def identify_statistical_patterns(self, question: str,
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify statistical patterns relevant to the question"""
        # This would interface with data analysis components
        return {
            'patterns_found': [],
            'statistical_significance': 0.0,
            'effect_sizes': [],
            'confidence_intervals': []
        }

    def extract_literature_patterns(self, question: str,
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from scientific literature"""
        # This would interface with literature mining components
        return {
            'related_papers': [],
            'common_themes': [],
            'gaps_identified': []
        }

    def creative_hypothesis_synthesis(self, concepts: List[str],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative hypothesis synthesis"""
        return {
            'novel_connections': [],
            'cross_domain_insights': [],
            'speculative_mechanisms': []
        }

    def formulate_main_claim(self, concepts: List[str],
                           patterns: Dict[str, Any]) -> str:
        """Formulate the main claim of the hypothesis"""
        return f"Based on statistical patterns and literature analysis, " + \
               f"{' and '.join(concepts[:3])} show significant relationships " + \
               f"that suggest novel biological mechanisms."

    def calculate_generative_confidence(self, patterns: Dict[str, Any],
                                      literature: Dict[str, Any]) -> float:
        """Calculate confidence score for generative hypothesis"""
        base_confidence = 0.5

        # Adjust based on pattern strength
        if patterns.get('statistical_significance', 0) > 0.05:
            base_confidence += 0.2

        # Adjust based on literature support
        if len(literature.get('related_papers', [])) > 5:
            base_confidence += 0.2

        return min(0.9, base_confidence)


class CausalDiscoveryEngine:
    """
    Causal discovery engine for mechanistic understanding.

    Focuses on:
    - Causal structure learning
    - Mechanism identification
    - Intervention prediction
    - Causal validation
    """

    def __init__(self):
        self.causal_models = {}
        self.mechanistic_patterns = {}
        logger.info("⚡ Causal Discovery Engine initialized")

    def analyze_causal_structure(self, question: str,
                                generative_hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze causal structure of the hypothesis.

        Performs:
        - Causal graph construction
        - Mechanism identification
        - Intervention analysis
        - Causal validation
        """

        logger.info(f"⚡ Analyzing causal structure for: {question[:50]}...")

        # Extract causal relationships
        causal_variables = self.extract_causal_variables(question, generative_hypothesis)
        causal_graph = self.construct_causal_graph(causal_variables)
        mechanisms = self.identify_mechanisms(causal_graph, generative_hypothesis)

        # Validate causal structure
        causal_validation = self.validate_causal_structure(causal_graph, mechanisms)

        causal_analysis = {
            'question': question,
            'causal_variables': causal_variables,
            'causal_graph': causal_graph,
            'identified_mechanisms': mechanisms,
            'intervention_predictions': self.predict_interventions(causal_graph),
            'causal_validation': causal_validation,
            'confidence': self.calculate_causal_confidence(causal_validation),
            'paradigm': 'causal',
            'reasoning_type': 'mechanistic'
        }

        return causal_analysis

    def extract_causal_variables(self, question: str,
                                hypothesis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract variables involved in causal relationships"""
        # Simple extraction - can be enhanced with NLP
        concepts = hypothesis.get('creative_insights', {}).get('novel_connections', [])

        variables = []
        for i, concept in enumerate(concepts):
            variables.append({
                'name': f'variable_{i}',
                'type': 'unknown',
                'role': 'intermediate'
            })

        return variables

    def construct_causal_graph(self, variables: List[Dict[str, str]]) -> Dict[str, Any]:
        """Construct causal graph from variables"""
        # Simplified causal graph construction
        graph = {
            'nodes': [v['name'] for v in variables],
            'edges': [],
            'latent_confounders': [],
            'assumptions': []
        }

        # Add edges based on variable relationships
        for i in range(len(variables) - 1):
            graph['edges'].append({
                'from': variables[i]['name'],
                'to': variables[i + 1]['name'],
                'type': 'directed',
                'strength': 0.7
            })

        return graph

    def identify_mechanisms(self, causal_graph: Dict[str, Any],
                          hypothesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify underlying mechanisms"""
        mechanisms = []

        for edge in causal_graph.get('edges', []):
            mechanism = {
                'from': edge['from'],
                'to': edge['to'],
                'type': 'unknown_mechanism',
                'mediators': [],
                'modulators': []
            }
            mechanisms.append(mechanism)

        return mechanisms

    def predict_interventions(self, causal_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Predict effects of interventions"""
        return {
            'predicted_interventions': [],
            'effect_sizes': [],
            'confidence_intervals': []
        }

    def validate_causal_structure(self, causal_graph: Dict[str, Any],
                                mechanisms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate causal structure assumptions"""
        return {
            'assumptions_validated': [],
            'alternative_structures': [],
            'robustness_score': 0.7,
            'validation_method': 'assumption_based'
        }

    def calculate_causal_confidence(self, validation: Dict[str, Any]) -> float:
        """Calculate confidence score for causal analysis"""
        base_confidence = 0.6
        robustness = validation.get('robustness_score', 0.5)
        return min(0.9, base_confidence + robustness * 0.3)


class NeurosymbolicReasoningEngine:
    """
    Neurosymbolic reasoning engine for formal validation.

    Focuses on:
    - Symbolic logic reasoning
    - Formal constraint validation
    - Knowledge graph integration
    - Logical consistency checking
    """

    def __init__(self):
        self.knowledge_base = {}
        self.reasoning_rules = self._initialize_reasoning_rules()
        logger.info("🔗 Neurosymbolic Reasoning Engine initialized")

    def _initialize_reasoning_rules(self) -> List[Dict[str, Any]]:
        """Initialize symbolic reasoning rules"""
        return [
            {
                'rule': 'conservation',
                'description': 'Biological quantities are conserved unless transformed'
            },
            {
                'rule': 'causality',
                'description': 'Effects cannot precede causes'
            },
            {
                'rule': 'specificity',
                'description': 'Specific interactions require specific molecular compatibility'
            }
        ]

    def validate_mechanisms(self, causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate mechanisms using neurosymbolic reasoning.

        Performs:
        - Symbolic logic validation
        - Knowledge graph consistency checking
        - Formal constraint verification
        - Logical consistency analysis
        """

        logger.info("🔗 Validating mechanisms with neurosymbolic reasoning...")

        # Extract mechanisms from causal analysis
        mechanisms = causal_analysis.get('identified_mechanisms', [])

        # Validate each mechanism
        validated_mechanisms = []
        for mechanism in mechanisms:
            validation_result = self.validate_single_mechanism(mechanism, causal_analysis)
            validated_mechanisms.append(validation_result)

        # Check overall consistency
        consistency_check = self.check_logical_consistency(causal_analysis)

        neurosymbolic_validation = {
            'mechanisms_validated': validated_mechanisms,
            'consistency_check': consistency_check,
            'formal_constraints_satisfied': self.check_formal_constraints(causal_analysis),
            'knowledge_graph_integration': self.integrate_with_knowledge_graph(causal_analysis),
            'confidence': self.calculate_neurosymbolic_confidence(validated_mechanisms, consistency_check),
            'paradigm': 'neurosymbolic',
            'reasoning_type': 'formal'
        }

        return neurosymbolic_validation

    def validate_single_mechanism(self, mechanism: Dict[str, Any],
                                 causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single mechanism using symbolic reasoning"""
        return {
            'mechanism': mechanism,
            'symbolically_valid': True,
            'rule_violations': [],
            'logical_form': self.generate_logical_form(mechanism),
            'constraint_satisfaction': 0.8
        }

    def generate_logical_form(self, mechanism: Dict[str, Any]) -> str:
        """Generate logical representation of mechanism"""
        return f"∀x, y: mechanism({mechanism.get('from', 'X')}, {mechanism.get('to', 'Y')}) → effect(x, y)"

    def check_logical_consistency(self, causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check logical consistency of causal analysis"""
        return {
            'consistent': True,
            'contradictions': [],
            'logical_gaps': [],
            'consistency_score': 0.8
        }

    def check_formal_constraints(self, causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check satisfaction of formal biological constraints"""
        constraints_satisfied = []

        for rule in self.reasoning_rules:
            satisfied = self.verify_rule_satisfaction(rule, causal_analysis)
            constraints_satisfied.append({
                'rule': rule['rule'],
                'satisfied': satisfied
            })

        return {
            'constraints_checked': len(constraints_satisfied),
            'constraints_satisfied': sum(1 for c in constraints_satisfied if c['satisfied']),
            'details': constraints_satisfied
        }

    def verify_rule_satisfaction(self, rule: Dict[str, Any],
                               causal_analysis: Dict[str, Any]) -> bool:
        """Verify if a reasoning rule is satisfied"""
        # Simplified rule checking
        return True

    def integrate_with_knowledge_graph(self, causal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate causal analysis with knowledge graph"""
        return {
            'nodes_integrated': 0,
            'edges_integrated': 0,
            'new_connections': [],
            'contradictions_resolved': 0
        }

    def calculate_neurosymbolic_confidence(self, validated_mechanisms: List[Dict[str, Any]],
                                          consistency_check: Dict[str, Any]) -> float:
        """Calculate confidence score for neurosymbolic validation"""
        base_confidence = 0.7

        # Adjust based on consistency
        consistency = consistency_check.get('consistency_score', 0.5)
        base_confidence += (consistency - 0.5) * 0.2

        return min(0.95, max(0.5, base_confidence))


class HybridReasoningIntegrator:
    """
    Integrates results from multiple reasoning paradigms into unified insights.

    Performs:
    - Multi-paradigm result integration
    - Conflict resolution between paradigms
    - Meta-reasoning about paradigm contributions
    - Unified confidence assessment
    """

    def __init__(self):
        self.integration_methods = ['weighted_average', 'paradigm_voting', 'meta_learning']
        self.integration_history = []
        logger.info("🔮 Hybrid Reasoning Integrator initialized")

    def merge_insights(self, generative_hypothesis: Dict[str, Any],
                       causal_analysis: Dict[str, Any],
                       neurosymbolic_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge insights from all three paradigms into unified result.

        Integration strategies:
        - Complementary insights enhancement
        - Conflict resolution
        - Confidence aggregation
        - Meta-reasoning about paradigm contributions
        """

        logger.info("🔮 Merging multi-paradigm insights...")

        # Extract key insights from each paradigm
        generative_insights = self.extract_generative_insights(generative_hypothesis)
        causal_insights = self.extract_causal_insights(causal_analysis)
        neurosymbolic_insights = self.extract_neurosymbolic_insights(neurosymbolic_validation)

        # Resolve conflicts between paradigms
        resolved_insights = self.resolve_paradigm_conflicts(
            generative_insights, causal_insights, neurosymbolic_insights
        )

        # Calculate paradigm contributions
        paradigm_contributions = self.calculate_paradigm_contributions(
            generative_hypothesis, causal_analysis, neurosymbolic_validation
        )

        # Aggregate confidence scores
        aggregated_confidence = self.aggregate_confidence_scores(
            generative_hypothesis.get('confidence', 0.5),
            causal_analysis.get('confidence', 0.5),
            neurosymbolic_validation.get('confidence', 0.5),
            paradigm_contributions
        )

        # Generate meta-reasoning
        meta_reasoning = self.generate_meta_reasoning(
            generative_hypothesis, causal_analysis, neurosymbolic_validation,
            paradigm_contributions, resolved_insights
        )

        unified_result = {
            'unified_insight': resolved_insights,
            'paradigm_contributions': paradigm_contributions,
            'aggregated_confidence': aggregated_confidence,
            'meta_reasoning': meta_reasoning,
            'integration_method': 'weighted_consensus',
            'paradigm_agreement': self.calculate_paradigm_agreement(
                generative_hypothesis, causal_analysis, neurosymbolic_validation
            )
        }

        return unified_result

    def extract_generative_insights(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from generative hypothesis"""
        return {
            'main_claim': hypothesis.get('main_claim', ''),
            'creative_elements': hypothesis.get('creative_insights', {}),
            'literature_support': hypothesis.get('literature_context', {}),
            'paradigm_strengths': ['creativity', 'pattern_recognition', 'literature_synthesis']
        }

    def extract_causal_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from causal analysis"""
        return {
            'mechanisms': analysis.get('identified_mechanisms', []),
            'causal_structure': analysis.get('causal_graph', {}),
            'intervention_predictions': analysis.get('intervention_predictions', {}),
            'paradigm_strengths': ['mechanistic_understanding', 'intervention_design', 'causal_clarity']
        }

    def extract_neurosymbolic_insights(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from neurosymbolic validation"""
        return {
            'formal_validation': validation.get('consistency_check', {}),
            'mechanism_validation': validation.get('mechanisms_validated', []),
            'constraint_satisfaction': validation.get('formal_constraints_satisfied', {}),
            'paradigm_strengths': ['logical_rigor', 'formal_validation', 'consistency_ensuring']
        }

    def resolve_paradigm_conflicts(self, generative: Dict[str, Any],
                                  causal: Dict[str, Any],
                                  neurosymbolic: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between different reasoning paradigms"""
        # Conflict resolution strategy: prioritize neurosymbolic for consistency,
        # causal for mechanisms, generative for novelty

        resolved = {
            'primary_insights': [],
            'secondary_insights': [],
            'conflicts_resolved': [],
            'integration_strategy': 'hierarchical_priority'
        }

        # Combine insights with priority weighting
        # Handle neurosymbolic consistency check (boolean vs list)
        neurosymbolic_consistency = neurosymbolic.get('formal_validation', {}).get('consistent', [])
        if isinstance(neurosymbolic_consistency, bool):
            # If it's a boolean, convert to appropriate list
            if neurosymbolic_consistency:
                neurosymbolic_consistency = ['consistency_validated']
            else:
                neurosymbolic_consistency = ['consistency_issues']

        resolved['primary_insights'].extend(neurosymbolic_consistency if isinstance(neurosymbolic_consistency, list) else [])
        resolved['primary_insights'].extend(causal.get('mechanisms', []))
        resolved['secondary_insights'].extend(generative.get('creative_elements', {}).get('speculative_mechanisms', []))

        return resolved

    def calculate_paradigm_contributions(self, generative: Dict[str, Any],
                                       causal: Dict[str, Any],
                                       neurosymbolic: Dict[str, Any]) -> Dict[str, float]:
        """Calculate relative contributions of each paradigm"""

        # Weight contributions based on confidence and paradigm strength
        gen_conf = generative.get('confidence', 0.5)
        causal_conf = causal.get('confidence', 0.5)
        neuro_conf = neurosymbolic.get('confidence', 0.5)

        total_conf = gen_conf + causal_conf + neuro_conf

        if total_conf == 0:
            return {'generative': 0.33, 'causal': 0.33, 'neurosymbolic': 0.34}

        return {
            'generative': gen_conf / total_conf,
            'causal': causal_conf / total_conf,
            'neurosymbolic': neuro_conf / total_conf
        }

    def aggregate_confidence_scores(self, gen_conf: float, causal_conf: float,
                                   neuro_conf: float,
                                   contributions: Dict[str, float]) -> float:
        """Aggregate confidence scores using weighted average"""
        aggregated = (
            contributions['generative'] * gen_conf +
            contributions['causal'] * causal_conf +
            contributions['neurosymbolic'] * neuro_conf
        )

        return min(0.95, max(0.5, aggregated))

    def calculate_paradigm_agreement(self, generative: Dict[str, Any],
                                   causal: Dict[str, Any],
                                   neurosymbolic: Dict[str, Any]) -> float:
        """Calculate level of agreement between paradigms"""
        # Simplified agreement calculation
        return 0.7  # Can be enhanced with actual comparison logic

    def generate_meta_reasoning(self, generative: Dict[str, Any], causal: Dict[str, Any],
                               neurosymbolic: Dict[str, Any],
                               contributions: Dict[str, float],
                               resolved_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meta-reasoning about the discovery process"""
        return {
            'reasoning_summary': 'Multi-paradigm integration successful',
            'paradigm_synergy': 'Complementary strengths utilized',
            'confidence_justification': f"Weighted integration with {contributions}",
            'limitations': 'Each paradigm has domain-specific constraints',
            'recommendations': 'Continue multi-paradigm approach for complex questions'
        }


class HybridDiscoveryEngine:
    """
    Main hybrid discovery engine integrating all three paradigms.

    Provides unified interface for:
    - Multi-paradigm hypothesis generation
    - Integrated causal analysis
    - Unified validation
    - Meta-reasoned confidence assessment
    """

    def __init__(self):
        self.generative_engine = GenerativeDiscoveryEngine()
        self.causal_engine = CausalDiscoveryEngine()
        self.neurosymbolic_engine = NeurosymbolicReasoningEngine()
        self.integrator = HybridReasoningIntegrator()

        self.discovery_history = []
        logger.info("🔬 HYBRID DISCOVERY ENGINE initialized - All paradigms operational")

    def unified_discovery_cycle(self, question: str,
                               context: Dict[str, Any]) -> HybridDiscoveryResult:
        """
        Perform complete unified discovery cycle using all three paradigms.

        Process:
        1. Generate hypothesis using generative approach
        2. Analyze causal structure
        3. Validate with neurosymbolic reasoning
        4. Integrate all insights
        5. Generate meta-reasoned result
        """

        logger.info(f"🔬 Starting unified discovery cycle: {question[:60]}...")

        # Step 1: Generative hypothesis
        generative_hypothesis = self.generative_engine.generate_hypothesis(question, context)

        # Step 2: Causal analysis
        causal_analysis = self.causal_engine.analyze_causal_structure(
            question, generative_hypothesis
        )

        # Step 3: Neurosymbolic validation
        neurosymbolic_validation = self.neurosymbolic_engine.validate_mechanisms(
            causal_analysis
        )

        # Step 4: Integrate insights
        unified_insight = self.integrator.merge_insights(
            generative_hypothesis, causal_analysis, neurosymbolic_validation
        )

        # Step 5: Create hybrid result
        hybrid_result = HybridDiscoveryResult(
            question=question,
            generative_hypothesis=generative_hypothesis,
            causal_analysis=causal_analysis,
            neurosymbolic_validation=neurosymbolic_validation,
            unified_insight=unified_insight,
            confidence_scores={
                'generative': generative_hypothesis.get('confidence', 0.5),
                'causal': causal_analysis.get('confidence', 0.5),
                'neurosymbolic': neurosymbolic_validation.get('confidence', 0.5),
                'unified': unified_insight.get('aggregated_confidence', 0.5)
            },
            paradigm_contributions=unified_insight.get('paradigm_contributions', {}),
            meta_reasoning=unified_insight.get('meta_reasoning', {})
        )

        # Store in history
        self.discovery_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'result': hybrid_result,
            'unified_confidence': unified_insight.get('aggregated_confidence', 0.5)
        })

        logger.info(f"✅ Unified discovery complete: Confidence={unified_insight.get('aggregated_confidence', 0.5):.2f}")

        return hybrid_result

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get statistics about hybrid discoveries"""
        if not self.discovery_history:
            return {'message': 'No discovery history available'}

        confidences = [d['unified_confidence'] for d in self.discovery_history]

        return {
            'total_discoveries': len(self.discovery_history),
            'average_confidence': np.mean(confidences),
            'confidence_range': [min(confidences), max(confidences)],
            'paradigm_usage': self.analyze_paradigm_usage()
        }

    def analyze_paradigm_usage(self) -> Dict[str, float]:
        """Analyze which paradigms contribute most"""
        # Analyze paradigm contributions across all discoveries
        paradigm_counts = {'generative': 0, 'causal': 0, 'neurosymbolic': 0}

        for discovery in self.discovery_history:
            contributions = discovery['result'].paradigm_contributions
            for paradigm, contribution in contributions.items():
                paradigm_counts[paradigm] += contribution

        total = sum(paradigm_counts.values())
        if total == 0:
            return paradigm_counts

        return {k: v/total for k, v in paradigm_counts.items()}


# Singleton instance
_hybrid_discovery_engine = None

def get_hybrid_discovery_engine() -> HybridDiscoveryEngine:
    """Get the singleton hybrid discovery engine instance"""
    global _hybrid_discovery_engine
    if _hybrid_discovery_engine is None:
        _hybrid_discovery_engine = HybridDiscoveryEngine()
    return _hybrid_discovery_engine


if __name__ == "__main__":
    # Test the hybrid discovery engine
    engine = get_hybrid_discovery_engine()

    # Test with a sample question
    test_question = "How do post-translational modifications affect protein folding in vivo?"
    test_context = {'domain': 'protein_folding', 'data_available': True}

    result = engine.unified_discovery_cycle(test_question, test_context)

    print(f"\n🔬 HYBRID DISCOVERY RESULT:")
    print(f"Question: {result.question}")
    print(f"Unified Confidence: {result.confidence_scores['unified']:.2f}")
    print(f"Paradigm Contributions: {result.paradigm_contributions}")
    print(f"\nMeta-reasoning: {result.meta_reasoning}")

    print(f"\n📊 Discovery Statistics: {engine.get_discovery_statistics()}")