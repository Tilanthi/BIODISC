#!/usr/bin/env python3
"""
BIODISC V6.0 - Epistemic Collapse Prevention System

Prevents recursive training on own discoveries and maintains conceptual diversity
to avoid epistemic drift and model collapse in the scientific discovery process.

Key Features:
- Continuous diversity monitoring with 0.7 threshold
- Self-reference detection and mitigation
- External anchor validation (30% requirement)
- Conceptual landscape mapping
- Automatic intervention when collapse risk detected
- Cross-pollination with external scientific sources

Date: 2026-07-04
Version: 6.0
"""

import logging
import json
import threading
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EpistemicHealthMetrics:
    """Metrics for assessing epistemic health"""
    conceptual_diversity_score: float
    self_reference_rate: float
    external_anchor_ratio: float
    novelty_distribution: Dict[str, float]
    domain_coverage: Dict[str, int]
    temporal_spread: float
    collapse_risk: str


class EpistemicCollapsePrevention:
    """
    System to prevent epistemic collapse in BIODISC discovery process.

    Monitors:
    - Conceptual diversity across discoveries
    - Self-reference rates
    - External validation and anchoring
    - Temporal distribution patterns
    - Domain coverage breadth

    Intervenes when:
    - Diversity score < 0.7
    - Self-reference rate > 0.4
    - External anchor ratio < 0.3
    """

    def __init__(self, diversity_threshold: float = 0.7,
                 self_reference_threshold: float = 0.4,
                 external_validation_ratio: float = 0.3):

        self.diversity_threshold = diversity_threshold
        self.self_reference_threshold = self_reference_threshold
        self.external_validation_ratio = external_validation_ratio

        self.discovery_history = []
        self.conceptual_landscape = defaultdict(list)
        self.domain_mapper = DomainConceptMapper()
        self.external_anchors = ExternalAnchorManager()

        # Intervention mechanisms
        self.intervention_history = []
        self.active_interventions = []

        # Thread safety
        self.lock = threading.Lock()

        # Monitoring state
        self.last_health_check = None
        self.collapse_risk_level = 'LOW'

        logger.info("🛡️  Epistemic Collapse Prevention System initialized")
        logger.info(f"   Diversity threshold: {diversity_threshold}")
        logger.info(f"   Self-reference threshold: {self_reference_threshold}")
        logger.info(f"   External validation ratio: {external_validation_ratio}")

    def check_epistemic_health(self, recent_discoveries: List[Dict[str, Any]],
                              force_check: bool = False) -> EpistemicHealthMetrics:
        """
        Comprehensive epistemic health assessment.

        Monitors:
        1. Conceptual diversity across discoveries
        2. Self-reference patterns
        3. External anchor presence
        4. Domain coverage
        5. Temporal distribution

        Triggers interventions if thresholds exceeded.
        """

        with self.lock:
            if not recent_discoveries and not force_check:
                return self.get_default_health_metrics()

            # Add discoveries to history
            for discovery in recent_discoveries:
                self.discovery_history.append(discovery)

            # Keep history manageable (last 500 discoveries)
            if len(self.discovery_history) > 500:
                self.discovery_history = self.discovery_history[-500:]

            # Calculate health metrics
            diversity_score = self.calculate_conceptual_diversity(recent_discoveries)
            self_reference_rate = self.detect_self_referential_cycles(recent_discoveries)
            external_validation = self.validate_external_anchors(recent_discoveries)
            domain_coverage = self.analyze_domain_coverage(recent_discoveries)
            temporal_spread = self.analyze_temporal_distribution(recent_discoveries)

            # Assess overall collapse risk
            collapse_risk = self.assess_collapse_risk(
                diversity_score, self_reference_rate, external_validation
            )

            metrics = EpistemicHealthMetrics(
                conceptual_diversity_score=diversity_score,
                self_reference_rate=self_reference_rate,
                external_anchor_ratio=external_validation,
                novelty_distribution=self.analyze_novelty_distribution(recent_discoveries),
                domain_coverage=domain_coverage,
                temporal_spread=temporal_spread,
                collapse_risk=collapse_risk
            )

            # Store health check results
            self.last_health_check = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'discovery_count': len(recent_discoveries)
            }

            # Trigger interventions if needed
            if collapse_risk in ['MEDIUM', 'HIGH', 'CRITICAL']:
                self.trigger_intervention(metrics, collapse_risk)

            logger.info(f"🛡️  Epistemic Health Check: {collapse_risk} risk")
            logger.info(f"   Diversity: {diversity_score:.2f}, Self-ref: {self_reference_rate:.2f}, External: {external_validation:.2f}")

            return metrics

    def calculate_conceptual_diversity(self, discoveries: List[Dict[str, Any]]) -> float:
        """
        Calculate conceptual diversity across discoveries.

        Uses multiple metrics:
        - Semantic similarity analysis
        - Domain keyword diversity
        - Conceptual category distribution
        - Methodological variety
        """

        if not discoveries:
            return 1.0  # No discoveries = maximum potential diversity

        # Extract conceptual features
        conceptual_features = []
        for discovery in discoveries:
            features = self.extract_conceptual_features(discovery)
            conceptual_features.append(features)

        # Calculate diversity using multiple approaches
        semantic_diversity = self.calculate_semantic_diversity(conceptual_features)
        domain_diversity = self.calculate_domain_diversity(conceptual_features)
        methodological_diversity = self.calculate_methodological_diversity(conceptual_features)

        # Weighted combination
        overall_diversity = (
            0.5 * semantic_diversity +
            0.3 * domain_diversity +
            0.2 * methodological_diversity
        )

        return overall_diversity

    def extract_conceptual_features(self, discovery: Dict[str, Any]) -> Dict[str, Any]:
        """Extract conceptual features from a discovery"""
        question = discovery.get('question', '')
        discovery_text = discovery.get('discovery', '')

        # Extract biological concepts
        concepts = self.extract_biological_concepts(question + ' ' + discovery_text)

        # Extract methodological terms
        methods = self.extract_methodological_terms(discovery_text)

        # Extract domain keywords
        domains = self.domain_mapper.identify_domains(question + ' ' + discovery_text)

        return {
            'concepts': concepts,
            'methods': methods,
            'domains': domains,
            'question_keywords': self.extract_keywords(question),
            'novelty_score': discovery.get('novelty_score', 0.0)
        }

    def extract_biological_concepts(self, text: str) -> List[str]:
        """Extract biological concepts from text"""
        # Common biological concept patterns
        concept_patterns = [
            r'\b(protein|enzyme|receptor|gene|pathway|mechanism|process)\s+\w+',
            r'\b\w+\s+(metabolism|synthesis|degradation|regulation|expression|signaling)',
            r'\b\w+\s+(folding|binding|interaction|transport|activation|inhibition)',
            r'\b(cellular|molecular|biological|biochemical)\s+\w+'
        ]

        concepts = []
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)

        return list(set(concepts))

    def extract_methodological_terms(self, text: str) -> List[str]:
        """Extract methodological terms from text"""
        method_keywords = [
            'experiment', 'analysis', 'measurement', 'assay', 'sequencing',
            'microarray', 'spectroscopy', 'crystallography', 'microscopy',
            'computational', 'statistical', 'bioinformatics', 'proteomics',
            'genomics', 'transcriptomics', 'metabolomics', 'biochemical'
        ]

        methods = []
        text_lower = text.lower()
        for method in method_keywords:
            if method in text_lower:
                methods.append(method)

        return list(set(methods))

    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        word_freq = Counter(words)

        # Return top 5 most frequent meaningful words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'been', 'being'}
        meaningful_words = [(w, c) for w, c in word_freq.items() if w.lower() not in stop_words and c > 1]

        return [w for w, c in sorted(meaningful_words, key=lambda x: x[1], reverse=True)[:5]]

    def calculate_semantic_diversity(self, features_list: List[Dict[str, Any]]) -> float:
        """Calculate semantic diversity using concept overlap analysis"""
        if not features_list or len(features_list) == 1:
            return 1.0

        all_concepts = set()
        for features in features_list:
            all_concepts.update(features['concepts'])

        if not all_concepts:
            return 0.5  # No concepts extracted = moderate diversity

        # Calculate pairwise concept overlap
        overlap_scores = []
        for i in range(len(features_list)):
            for j in range(i + 1, len(features_list)):
                concepts_i = set(features_list[i]['concepts'])
                concepts_j = set(features_list[j]['concepts'])

                if not concepts_i or not concepts_j:
                    continue

                overlap = len(concepts_i & concepts_j) / len(concepts_i | concepts_j)
                overlap_scores.append(overlap)

        if not overlap_scores:
            return 1.0

        average_overlap = np.mean(overlap_scores)
        diversity = 1.0 - average_overlap

        return max(0.0, min(1.0, diversity))

    def calculate_domain_diversity(self, features_list: List[Dict[str, Any]]) -> float:
        """Calculate domain diversity using entropy"""
        if not features_list:
            return 1.0

        # Count domain occurrences
        domain_counts = []
        for features in features_list:
            domains = features.get('domains', [])
            domain_counts.extend(domains if domains else ['unknown'])

        if not domain_counts:
            return 1.0

        # Calculate entropy-based diversity
        domain_counter = Counter(domain_counts)
        total = len(domain_counts)

        if total == 0:
            return 1.0

        entropy = 0.0
        for count in domain_counter.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        # Normalize by max possible entropy
        max_entropy = np.log2(len(domain_counter))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return normalized_entropy

    def calculate_methodological_diversity(self, features_list: List[Dict[str, Any]]) -> float:
        """Calculate methodological diversity"""
        if not features_list:
            return 1.0

        all_methods = set()
        for features in features_list:
            all_methods.update(features.get('methods', []))

        # Diversity based on unique method count
        total_features = len(features_list)
        unique_methods = len(all_methods)

        if total_features == 0:
            return 1.0

        # Normalize: more unique methods per discovery = higher diversity
        method_ratio = unique_methods / total_features
        normalized_diversity = min(1.0, method_ratio)

        return normalized_diversity

    def detect_self_referential_cycles(self, discoveries: List[Dict[str, Any]]) -> float:
        """
        Detect self-referential patterns in discoveries.

        Analyzes:
        - Citations to previous BIODISC discoveries
        - Reuse of own discovery patterns
        - Recursive conceptual patterns
        """

        if len(discoveries) < 3:
            return 0.0  # Not enough data for pattern detection

        self_reference_count = 0
        total_references = 0

        for discovery in discoveries:
            question = discovery.get('question', '')
            discovery_text = discovery.get('discovery', '')

            # Check for self-reference patterns
            if self.contains_self_reference(question, discovery_text):
                self_reference_count += 1
                total_references += 1
            else:
                total_references += 1

        if total_references == 0:
            return 0.0

        self_reference_rate = self_reference_count / total_references
        return self_reference_rate

    def contains_self_reference(self, question: str, discovery_text: str) -> bool:
        """Check if discovery contains self-referential patterns"""
        # Patterns indicating self-reference
        self_ref_patterns = [
            r'previous\s+(?:BIODISC|our|this\s+system)\s+discovery',
            r'as\s+(?:we\s+)?(?:previously\s+)?(?:showed|demonstrated|found)',
            r'building\s+on\s+(?:our\s+)?earlier\s+(?:work|findings|results)',
            r'according\s+to\s+(?:our|previous)\s+(?:analysis|study)',
            r'discovery.*\d+'  # Reference to discovery IDs
        ]

        combined_text = question + ' ' + discovery_text

        for pattern in self_ref_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True

        return False

    def validate_external_anchors(self, discoveries: List[Dict[str, Any]]) -> float:
        """
        Validate presence of external anchors in discoveries.

        External anchors include:
        - Citations to external scientific literature
        - References to established databases
        - Connections to external validation sources
        """

        if not discoveries:
            return 0.0

        externally_anchored_count = 0

        for discovery in discoveries:
            if self.has_external_anchors(discovery):
                externally_anchored_count += 1

        external_ratio = externally_anchored_count / len(discoveries)
        return external_ratio

    def has_external_anchors(self, discovery: Dict[str, Any]) -> bool:
        """Check if discovery has external anchors"""
        # Check for literature citations
        evidence = discovery.get('evidence', [])
        computational_backing = discovery.get('computational_backing', {})

        # Look for external database references
        for item in evidence:
            if any(term in str(item).lower() for term in ['pubmed', 'geo', 'string', 'kegg', 'uniprot']):
                return True

        # Check for external validation sources
        if computational_backing.get('data_source') in ['GEO', 'PubMed', 'NCBI', 'STRING', 'KEGG']:
            return True

        # Check for literature references in discovery text
        discovery_text = discovery.get('discovery', '')
        if re.search(r'\bPMID:\d+\b', discovery_text):
            return True

        return False

    def analyze_novelty_distribution(self, discoveries: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze distribution of novelty scores"""
        if not discoveries:
            return {}

        novelty_scores = [d.get('novelty_score', 0.0) for d in discoveries]

        return {
            'mean': np.mean(novelty_scores),
            'std': np.std(novelty_scores),
            'min': np.min(novelty_scores),
            'max': np.max(novelty_scores),
            'median': np.median(novelty_scores)
        }

    def analyze_domain_coverage(self, discoveries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze domain coverage across discoveries"""
        domain_counts = defaultdict(int)

        for discovery in discoveries:
            question = discovery.get('question', '')
            domains = self.domain_mapper.identify_domains(question)
            for domain in domains:
                domain_counts[domain] += 1

        return dict(domain_counts)

    def analyze_temporal_distribution(self, discoveries: List[Dict[str, Any]]) -> float:
        """Analyze temporal spread of discoveries"""
        if len(discoveries) < 2:
            return 1.0

        timestamps = [d.get('timestamp', time.time()) for d in discoveries
                     if isinstance(d.get('timestamp'), (int, float))]

        if len(timestamps) < 2:
            return 1.0

        time_span = max(timestamps) - min(timestamps)

        # Normalize: larger time span with many discoveries = better temporal spread
        expected_time_span = len(discoveries) * 300  # 5 minutes per discovery expected

        temporal_spread = min(1.0, time_span / expected_time_span)
        return temporal_spread

    def assess_collapse_risk(self, diversity_score: float,
                           self_reference_rate: float,
                           external_validation: float) -> str:
        """Assess overall collapse risk from multiple indicators"""

        risk_factors = 0

        # Check diversity threshold
        if diversity_score < self.diversity_threshold:
            risk_factors += 1
            if diversity_score < 0.5:
                risk_factors += 1  # Extra risk for very low diversity

        # Check self-reference threshold
        if self_reference_rate > self.self_reference_threshold:
            risk_factors += 1
            if self_reference_rate > 0.6:
                risk_factors += 1  # Extra risk for very high self-reference

        # Check external validation threshold
        if external_validation < self.external_validation_ratio:
            risk_factors += 1
            if external_validation < 0.1:
                risk_factors += 1  # Extra risk for very low external validation

        # Determine risk level
        if risk_factors >= 4:
            collapse_risk = 'CRITICAL'
        elif risk_factors >= 3:
            collapse_risk = 'HIGH'
        elif risk_factors >= 2:
            collapse_risk = 'MEDIUM'
        elif risk_factors >= 1:
            collapse_risk = 'LOW'
        else:
            collapse_risk = 'EXCELLENT'

        self.collapse_risk_level = collapse_risk
        return collapse_risk

    def trigger_intervention(self, metrics: EpistemicHealthMetrics, risk_level: str):
        """Trigger intervention to prevent epistemic collapse"""

        intervention_strategies = []

        if metrics.conceptual_diversity_score < self.diversity_threshold:
            intervention_strategies.append('diversity_enhancement')
            self.trigger_diversity_enhancement()

        if metrics.self_reference_rate > self.self_reference_threshold:
            intervention_strategies.append('external_pivot')
            self.force_external_pivot()

        if metrics.external_anchor_ratio < self.external_validation_ratio:
            intervention_strategies.append('external_anchor_injection')
            self.inject_external_anchors()

        intervention_record = {
            'timestamp': datetime.now().isoformat(),
            'risk_level': risk_level,
            'strategies': intervention_strategies,
            'metrics': metrics
        }

        self.intervention_history.append(intervention_record)
        logger.warning(f"🛡️  INTERVENTION TRIGGERED: {risk_level} risk - {intervention_strategies}")

    def trigger_diversity_enhancement(self):
        """Enhance conceptual diversity by broadening discovery focus"""
        logger.info("🌟 TRIGGERING DIVERSITY ENHANCEMENT")

        # Strategy: Broaden question generation to include diverse domains
        # and conceptual approaches

        intervention = {
            'type': 'diversity_enhancement',
            'action': 'broaden_discovery_scope',
            'parameters': {
                'domain_expansion_factor': 2.0,
                'conceptual_variety_boost': 1.5,
                'methodological_diversification': True
            },
            'timestamp': datetime.now().isoformat()
        }

        self.active_interventions.append(intervention)

        # Implementation: Expand question generation domains
        self.expand_question_domains()

    def force_external_pivot(self):
        """Force pivot to external knowledge sources"""
        logger.info("🔄 FORCING EXTERNAL PIVOT")

        intervention = {
            'type': 'external_pivot',
            'action': 'external_source_integration',
            'parameters': {
                'external_source_priority': 'HIGH',
                'internal_source_suppression': 0.3,
                'cross_validation_requirement': True
            },
            'timestamp': datetime.now().isoformat()
        }

        self.active_interventions.append(intervention)

        # Implementation: Prioritize external knowledge sources
        self.prioritize_external_sources()

    def inject_external_anchors(self):
        """Inject external validation anchors"""
        logger.info("⚓ INJECTING EXTERNAL ANCHORS")

        intervention = {
            'type': 'external_anchor_injection',
            'action': 'external_validation_enforcement',
            'parameters': {
                'minimum_external_sources': 3,
                'validation_diversity_requirement': True,
                'cross_domain_validation': True
            },
            'timestamp': datetime.now().isoformat()
        }

        self.active_interventions.append(intervention)

        # Implementation: Require external validation for next N discoveries
        self.enforce_external_validation()

    def expand_question_domains(self):
        """Expand question generation to include more diverse domains"""
        # This would interface with the question generation system
        expanded_domains = [
            'quantum_biology', 'synthetic_biology', 'bioinformatics',
            'computational_biology', 'systems_biology', 'neurobiology',
            'immunology', 'microbiology', 'evolutionary_biology'
        ]
        logger.info(f"   Expanding to domains: {expanded_domains}")

    def prioritize_external_sources(self):
        """Prioritize external knowledge sources"""
        # This would interface with literature mining system
        logger.info("   Prioritizing PubMed, GEO, and external databases")

    def enforce_external_validation(self):
        """Enforce external validation requirements"""
        # This would modify validation criteria
        logger.info("   Enforcing external validation for next discoveries")

    def get_default_health_metrics(self) -> EpistemicHealthMetrics:
        """Return default metrics when no data available"""
        return EpistemicHealthMetrics(
            conceptual_diversity_score=1.0,
            self_reference_rate=0.0,
            external_anchor_ratio=1.0,
            novelty_distribution={'mean': 0.8},
            domain_coverage={},
            temporal_spread=1.0,
            collapse_risk='EXCELLENT'
        )

    def get_intervention_history(self) -> List[Dict[str, Any]]:
        """Get history of interventions triggered"""
        return self.intervention_history

    def get_active_interventions(self) -> List[Dict[str, Any]]:
        """Get currently active interventions"""
        return self.active_interventions

    def clear_active_interventions(self):
        """Clear active interventions (when health improves)"""
        self.active_interventions = []
        logger.info("✅ Active interventions cleared")


class DomainConceptMapper:
    """Maps biological concepts to domains"""

    def __init__(self):
        self.domain_keywords = {
            'protein_folding': ['protein', 'folding', 'misfolding', 'chaperone', 'conformation'],
            'gene_expression': ['gene', 'expression', 'transcription', 'mRNA', 'regulation'],
            'metabolism': ['metabolism', 'metabolic', 'pathway', 'synthesis', 'degradation'],
            'cell_cycle': ['cell cycle', 'division', 'mitosis', 'meiosis', 'proliferation'],
            'epigenetics': ['epigenetic', 'methylation', 'histone', 'chromatin', 'modification'],
            'signaling': ['signaling', 'pathway', 'cascade', 'receptor', 'ligand'],
            'immunology': ['immune', 'antibody', 'antigen', 'lymphocyte', 'cytokine'],
            'neurobiology': ['neuron', 'synapse', 'neural', 'brain', 'nervous'],
            'microbiology': ['bacteria', 'virus', 'microbe', 'pathogen', 'infection'],
            'evolutionary_biology': ['evolution', 'selection', 'adaptation', 'phylogeny', 'speciation']
        }

    def identify_domains(self, text: str) -> List[str]:
        """Identify biological domains present in text"""
        text_lower = text.lower()
        identified_domains = []

        for domain, keywords in self.domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                identified_domains.append(domain)

        return identified_domains if identified_domains else ['general_biology']


class ExternalAnchorManager:
    """Manages external knowledge sources and anchors"""

    def __init__(self):
        self.external_sources = {
            'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/',
            'geo': 'https://www.ncbi.nlm.nih.gov/geo/',
            'string': 'https://string-db.org/',
            'kegg': 'https://www.genome.jp/kegg/',
            'uniprot': 'https://www.uniprot.org/'
        }
        self.anchor_cache = {}

    def validate_external_accessibility(self, source: str) -> bool:
        """Check if external source is accessible"""
        return source in self.external_sources

    def get_external_anchors(self, discovery: Dict[str, Any]) -> List[str]:
        """Get external anchors for a discovery"""
        anchors = []

        evidence = discovery.get('evidence', [])
        for item in evidence:
            for source in self.external_sources:
                if source.lower() in str(item).lower():
                    anchors.append(source)

        return anchors


# Singleton instance
_epistemic_collapse_prevention = None

def get_epistemic_collapse_prevention() -> EpistemicCollapsePrevention:
    """Get the singleton epistemic collapse prevention instance"""
    global _epistemic_collapse_prevention
    if _epistemic_collapse_prevention is None:
        _epistemic_collapse_prevention = EpistemicCollapsePrevention()
    return _epistemic_collapse_prevention


# Add import time at end
import time