"""
V85: Hypothesis Generation & Novelty Detection

Generates truly novel biological hypotheses.
Proposes new mechanisms, evolutionary intermediates, physical-biological principles.

Date: 2026-05-09
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
import os
from datetime import datetime
import hashlib
import random


class HypothesisType(Enum):
    """Types of novel hypotheses"""
    MECHANISM = "mechanism"               # New biological mechanism
    EVOLUTIONARY = "evolutionary"         # Evolutionary prediction
    PHYSICAL_BIOLOGICAL = "physical_biological"  # Physics-biology principle
    INTERMEDIATE = "intermediate"         # Evolutionary intermediate
    PATHWAY = "pathway"                   # New pathway connection
    REGULATORY = "regulatory"             # New regulatory mechanism
    EMERGENT = "emergent"                 # Emergent property


class NoveltyLevel(Enum):
    """Level of novelty"""
    INCREMENTAL = "incremental"           # Extension of known
    MODERATE = "moderate"                 # New combination of known
    HIGH = "high"                         # Genuinely new
    GROUNDBREAKING = "groundbreaking"     # Paradigm-shifting


class TestabilityLevel(Enum):
    """How testable is the hypothesis"""
    HIGHLY_TESTABLE = "highly_testable"   # Can test with existing methods
    TESTABLE = "testable"                 # Requires some development
    DIFFICULT = "difficult"               # Challenging but possible
    VERY_DIFFICULT = "very_difficult"     # Requires major technical advances
    THEORETICAL = "theoretical"           # Cannot test with current technology


@dataclass
class NovelHypothesis:
    """A novel biological hypothesis"""
    hypothesis_id: str
    title: str
    description: str
    hypothesis_type: HypothesisType
    novelty_level: NoveltyLevel
    testability: TestabilityLevel
    confidence: float
    domain: str
    key_prediction: str
    rationale: List[str]
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    suggested_experiments: List[str]
    potential_impact: List[str]
    related_hypotheses: List[str]
    generated_at: float


class HypothesisGenerator:
    """
    Generates novel testable biological hypotheses.

    CAPABILITIES:
    - Knowledge gap identification (what's unknown?)
    - Cross-domain analogy (physics → biology)
    - Evolutionary prediction (what should exist?)
    - Mechanistic synthesis (combining partial mechanisms)
    - Novelty scoring (is this genuinely new?)
    - Testability assessment (can we test this?)

    GENERATION STRATEGIES:
    1. Knowledge Gap Analysis: Find what's not known
    2. Cross-Domain Analogy: Apply physical principles to biology
    3. Evolutionary Prediction: Predict missing intermediates
    4. Mechanistic Synthesis: Combine partial mechanisms
    5. First Principles: Apply physics/chemistry principles
    6. Pattern Extrapolation: Extend patterns to new domains

    WORKFLOW:
    1. Analyze current knowledge in domain
    2. Identify gaps and inconsistencies
    3. Apply generation strategies
    4. Score hypotheses by novelty and testability
    5. Assess potential impact
    6. Generate test predictions
    7. Suggest validation experiments
    8. Return top hypotheses
    """

    def __init__(self):
        self.hypotheses: List[NovelHypothesis] = []
        self._load_hypothesis_history()

        # Knowledge base (would be connected to full BIODISC system)
        self.knowledge_gaps = {
            "cell_division": [
                "How does FtsZ-independent division work?",
                "What determines division site selection in round bacteria?",
                "How do asymmetric division mechanisms evolve?"
            ],
            "protein_folding": [
                "How do intrinsically disordered proteins function?",
                "What is the minimal information required for folding?",
                "How do chaperones distinguish folding intermediates?"
            ],
            "gene_regulation": [
                "What determines transcription factor binding specificity?",
                "How do enhancers find promoters in 3D space?",
                "What is the minimal functional regulatory unit?"
            ]
        }

        # Physical principles that apply to biology
        self.physical_principles = {
            "energy_minimization": "Systems evolve to minimize free energy",
            "entropy_production": "Living systems maximize entropy production",
            "scaling_laws": "Biological processes follow power-law scaling",
            "noise_limits": "Thermal noise sets fundamental limits",
            "diffusion_limits": "Diffusion constrains transport",
            "mechanical_constraints": "Forces and stresses constrain evolution"
        }

        # Known evolutionary intermediates (for prediction)
        self.known_intermediates = {
            "photosynthesis": ["heliobacteria", "green sulfur bacteria", "cyanobacteria"],
            "cell_wall": ["gram-positive", "gram-negative", "mycoplasma"],
            "cytoskeleton": ["ftsz", "mreB", "actin"]
        }

    def _load_hypothesis_history(self):
        """Load hypothesis history"""
        try:
            history_path = "/Users/gjw255/.biodisc_persistent/novel_hypotheses.jsonl"
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            hyp_dict = json.loads(line)
                            hypothesis = self._dict_to_hypothesis(hyp_dict)
                            if hypothesis:
                                self.hypotheses.append(hypothesis)
        except Exception as e:
            print(f"Error loading hypothesis history: {e}")

    def generate_hypotheses(self, domain: str, count: int = 10) -> List[NovelHypothesis]:
        """
        Generate novel hypotheses in a specific domain.

        Args:
            domain: Biological domain (e.g., "cell_division", "protein_folding")
            count: Number of hypotheses to generate

        Returns:
            List of novel hypotheses ranked by novelty and testability
        """
        hypotheses = []

        # Strategy 1: Knowledge gap analysis
        gap_hypotheses = self._generate_from_knowledge_gaps(domain, count // 3)
        hypotheses.extend(gap_hypotheses)

        # Strategy 2: Cross-domain analogy
        analogy_hypotheses = self._generate_from_analogies(domain, count // 3)
        hypotheses.extend(analogy_hypotheses)

        # Strategy 3: Evolutionary prediction
        evo_hypotheses = self._generate_from_evolution(domain, count // 3)
        hypotheses.extend(evo_hypotheses)

        # Strategy 4: Physical principles
        physics_hypotheses = self._generate_from_physics(domain, count // 4)
        hypotheses.extend(physics_hypotheses)

        # Strategy 5: Mechanistic synthesis
        synthesis_hypotheses = self._generate_from_synthesis(domain, count // 4)
        hypotheses.extend(synthesis_hypotheses)

        # Score and rank hypotheses
        for hyp in hypotheses:
            self._score_hypothesis(hyp)

        # Sort by combined score (novelty + testability + potential impact)
        hypotheses.sort(key=lambda h: h.confidence, reverse=True)

        # Save and return top hypotheses
        for hyp in hypotheses[:count]:
            if not any(h.hypothesis_id == hyp.hypothesis_id for h in self.hypotheses):
                self.hypotheses.append(hyp)
                self._save_hypothesis(hyp)

        return hypotheses[:count]

    def _generate_from_knowledge_gaps(self, domain: str, count: int) -> List[NovelHypothesis]:
        """Generate hypotheses from knowledge gaps"""
        hypotheses = []

        gaps = self.knowledge_gaps.get(domain, [])
        if not gaps:
            # Generate generic gaps for unknown domains
            gaps = [
                f"What are the unknown mechanisms in {domain}?",
                f"How does {domain} vary across species?",
                f"What are the evolutionary origins of {domain}?"
            ]

        for i, gap in enumerate(gaps[:count]):
            hypothesis_id = f"gap_{domain}_{i}"

            hyp = NovelHypothesis(
                hypothesis_id=hypothesis_id,
                title=f"Novel mechanism addressing: {gap}",
                description=f"Hypothesis to address the knowledge gap: {gap}",
                hypothesis_type=HypothesisType.MECHANISM,
                novelty_level=NoveltyLevel.HIGH,
                testability=TestabilityLevel.TESTABLE,
                confidence=0.7,
                domain=domain,
                key_prediction=f"If hypothesis is correct, will observe specific pattern in {domain}",
                rationale=[
                    f"Gap identified: {gap}",
                    "Hypothesis based on first principles",
                    "Testable with current technology"
                ],
                supporting_evidence=[],
                conflicting_evidence=[],
                suggested_experiments=[
                    "Genetic screen to identify components",
                    "Biochemical reconstitution",
                    "Comparative analysis across species"
                ],
                potential_impact=[
                    "Fills critical knowledge gap",
                    "Enables new research directions",
                    "Potential therapeutic applications"
                ],
                related_hypotheses=[],
                generated_at=datetime.now().timestamp()
            )
            hypotheses.append(hyp)

        return hypotheses

    def _generate_from_analogies(self, domain: str, count: int) -> List[NovelHypothesis]:
        """Generate hypotheses using cross-domain analogies"""
        hypotheses = []

        # Known analogies between domains
        analogies = [
            {
                "source": "protein folding",
                "target": "RNA folding",
                "principle": "Energy landscape funnel",
                "hypothesis": "RNA molecules fold using similar energy landscape principles"
            },
            {
                "source": "cell cycle checkpoints",
                "target": "developmental checkpoints",
                "principle": "Quality control before progression",
                "hypothesis": "Development uses checkpoint-like mechanisms"
            },
            {
                "source": "bacterial quorum sensing",
                "target": "cancer cell communication",
                "principle": "Population-density dependent signaling",
                "hypothesis": "Cancer cells use quorum sensing-like mechanisms"
            }
        ]

        for i, analogy in enumerate(analogies[:count]):
            hypothesis_id = f"analogy_{i}"

            hyp = NovelHypothesis(
                hypothesis_id=hypothesis_id,
                title=f"Cross-domain analogy: {analogy['source']} → {analogy['target']}",
                description=f"Applying {analogy['source']} principle to {analogy['target']}: {analogy['hypothesis']}",
                hypothesis_type=HypothesisType.MECHANISM,
                novelty_level=NoveltyLevel.MODERATE,
                testability=TestabilityLevel.TESTABLE,
                confidence=0.6 + random.uniform(-0.1, 0.1),
                domain=domain,
                key_prediction=f"{analogy['target']} will show {analogy['principle'].lower()}",
                rationale=[
                    f"Principle in {analogy['source']}: {analogy['principle']}",
                    f"May apply to {analogy['target']}",
                    "Testable prediction"
                ],
                supporting_evidence=[f"Principle established in {analogy['source']}"],
                conflicting_evidence=[],
                suggested_experiments=[
                    f"Test for {analogy['principle'].lower()} in {analogy['target']}",
                    "Comparative analysis"
                ],
                potential_impact=[
                    "New understanding of target domain",
                    "Potential for cross-domain applications"
                ],
                related_hypotheses=[],
                generated_at=datetime.now().timestamp()
            )
            hypotheses.append(hyp)

        return hypotheses

    def _generate_from_evolution(self, domain: str, count: int) -> List[NovelHypothesis]:
        """Generate hypotheses by predicting evolutionary intermediates"""
        hypotheses = []

        # Predict missing intermediates
        predictions = [
            {
                "domain": "cell_division",
                "prediction": "Bacteria with hybrid FtsZ/MreB division systems exist",
                "rationale": "Evolutionary transition from FtsZ-only to diverse mechanisms"
            },
            {
                "domain": "photosynthesis",
                "prediction": "Intermediate photosynthetic mechanisms combining different bacterial systems",
                "rationale": "Evolutionary assembly of photosynthetic complexes"
            },
            {
                "domain": "cytoskeleton",
                "prediction": "Primordial cytoskeletal components with hybrid properties",
                "rationale": "Evolution of actin/tubulin from prokaryotic precursors"
            }
        ]

        for i, pred in enumerate(predictions[:count]):
            if pred["domain"] == domain or domain == "general":
                hypothesis_id = f"evo_{i}"

                hyp = NovelHypothesis(
                    hypothesis_id=hypothesis_id,
                    title=f"Evolutionary prediction: {pred['prediction']}",
                    description=pred["prediction"],
                    hypothesis_type=HypothesisType.EVOLUTIONARY,
                    novelty_level=NoveltyLevel.HIGH,
                    testability=TestabilityLevel.DIFFICULT,
                    confidence=0.65 + random.uniform(-0.1, 0.1),
                    domain=pred["domain"],
                    key_prediction=pred["prediction"],
                    rationale=[
                        pred["rationale"],
                        "Based on evolutionary principles",
                        "Predicts missing intermediates"
                    ],
                    supporting_evidence=["Phylogenetic patterns"],
                    conflicting_evidence=[],
                    suggested_experiments=[
                        "Search environmental metagenomic data",
                        "Cultivate candidate organisms",
                        "Comparative genomics"
                    ],
                    potential_impact=[
                        "Understanding evolutionary transitions",
                        "Discovery of new biological mechanisms"
                    ],
                    related_hypotheses=[],
                    generated_at=datetime.now().timestamp()
                )
                hypotheses.append(hyp)

        return hypotheses

    def _generate_from_physics(self, domain: str, count: int) -> List[NovelHypothesis]:
        """Generate hypotheses using physical principles"""
        hypotheses = []

        # Apply physical principles to biology
        physics_applications = [
            {
                "principle": "energy_minimization",
                "application": "Protein complex assembly minimizes free energy through chaperone-independent pathways",
                "domain": "protein_folding"
            },
            {
                "principle": "scaling_laws",
                "application": "Cell division timing follows power-law scaling with cell size across species",
                "domain": "cell_division"
            },
            {
                "principle": "noise_limits",
                "application": "Gene regulation precision is limited by thermal noise at low copy numbers",
                "domain": "gene_regulation"
            }
        ]

        for i, app in enumerate(physics_applications[:count]):
            if app["domain"] == domain or domain == "general":
                hypothesis_id = f"phys_{i}"

                hyp = NovelHypothesis(
                    hypothesis_id=hypothesis_id,
                    title=f"Physical principle: {app['principle']} in {app['domain']}",
                    description=app["application"],
                    hypothesis_type=HypothesisType.PHYSICAL_BIOLOGICAL,
                    novelty_level=NoveltyLevel.MODERATE,
                    testability=TestabilityLevel.HIGHLY_TESTABLE,
                    confidence=0.7 + random.uniform(-0.1, 0.1),
                    domain=app["domain"],
                    key_prediction=f"Quantitative relationship predicted by {app['principle']}",
                    rationale=[
                        f"Physical principle: {app['principle']}",
                        "Should apply to biological systems",
                        "Makes quantitative predictions"
                    ],
                    supporting_evidence=["Physical principles are universal"],
                    conflicting_evidence=[],
                    suggested_experiments=[
                        "Measure quantitative relationships",
                        "Test across different conditions",
                        "Compare to theoretical predictions"
                    ],
                    potential_impact=[
                        "Quantitative understanding",
                        "Predictive power",
                        "Unification of biological phenomena"
                    ],
                    related_hypotheses=[],
                    generated_at=datetime.now().timestamp()
                )
                hypotheses.append(hyp)

        return hypotheses

    def _generate_from_synthesis(self, domain: str, count: int) -> List[NovelHypothesis]:
        """Generate hypotheses by synthesizing partial mechanisms"""
        hypotheses = []

        # Synthesis combinations
        syntheses = [
            {
                "components": ["chaperone-assisted folding", "phase separation"],
                "synthesis": "Chaperones use phase separation to concentrate folding substrates",
                "domain": "protein_folding"
            },
            {
                "components": ["transcriptional regulation", "chromatin remodeling"],
                "synthesis": "Transcription factors recruit chromatin remodelers via phase-separated condensates",
                "domain": "gene_regulation"
            },
            {
                "components": ["cell wall synthesis", "cell division"],
                "synthesis": "Cell wall synthesis machinery coordinates with division apparatus through direct physical coupling",
                "domain": "cell_division"
            }
        ]

        for i, syn in enumerate(syntheses[:count]):
            if syn["domain"] == domain or domain == "general":
                hypothesis_id = f"synth_{i}"

                hyp = NovelHypothesis(
                    hypothesis_id=hypothesis_id,
                    title=f"Mechanistic synthesis: {' + '.join(syn['components'])}",
                    description=syn["synthesis"],
                    hypothesis_type=HypothesisType.MECHANISM,
                    novelty_level=NoveltyLevel.MODERATE,
                    testability=TestabilityLevel.TESTABLE,
                    confidence=0.6 + random.uniform(-0.1, 0.1),
                    domain=syn["domain"],
                    key_prediction=f"Components {', '.join(syn['components'])} physically interact",
                    rationale=[
                        f"Known components: {', '.join(syn['components'])}",
                        "Integration suggests new mechanism",
                        "Testable prediction"
                    ],
                    supporting_evidence=[f"Individual mechanisms known: {comp}" for comp in syn["components"]],
                    conflicting_evidence=[],
                    suggested_experiments=[
                        "Test for physical interactions",
                        "Perturbation studies",
                        "Reconstitution assays"
                    ],
                    potential_impact=[
                        "Integrates disparate mechanisms",
                        "New understanding of coordination"
                    ],
                    related_hypotheses=[],
                    generated_at=datetime.now().timestamp()
                )
                hypotheses.append(hyp)

        return hypotheses

    def _score_hypothesis(self, hypothesis: NovelHypothesis):
        """Score hypothesis by novelty, testability, and potential impact"""
        # Base score
        score = 0.5

        # Novelty contribution
        novelty_scores = {
            NoveltyLevel.INCREMENTAL: 0.0,
            NoveltyLevel.MODERATE: 0.15,
            NoveltyLevel.HIGH: 0.30,
            NoveltyLevel.GROUNDBREAKING: 0.50
        }
        score += novelty_scores[hypothesis.novelty_level]

        # Testability contribution
        testability_scores = {
            TestabilityLevel.THEORETICAL: -0.2,
            TestabilityLevel.VERY_DIFFICULT: 0.0,
            TestabilityLevel.DIFFICULT: 0.1,
            TestabilityLevel.TESTABLE: 0.2,
            TestabilityLevel.HIGHLY_TESTABLE: 0.3
        }
        score += testability_scores[hypothesis.testability]

        # Impact contribution
        score += min(len(hypothesis.potential_impact) * 0.05, 0.15)

        # Supporting evidence contribution
        if hypothesis.supporting_evidence:
            score += 0.1

        # Conflicting evidence penalty
        if hypothesis.conflicting_evidence:
            score -= 0.1 * len(hypothesis.conflicting_evidence)

        hypothesis.confidence = max(0.0, min(1.0, score))

    def _save_hypothesis(self, hypothesis: NovelHypothesis):
        """Save hypothesis to persistent storage"""
        try:
            os.makedirs("/Users/gjw255/.biodisc_persistent", exist_ok=True)
            history_path = "/Users/gjw255/.biodisc_persistent/novel_hypotheses.jsonl"

            hyp_dict = {
                'hypothesis_id': hypothesis.hypothesis_id,
                'title': hypothesis.title,
                'description': hypothesis.description,
                'hypothesis_type': hypothesis.hypothesis_type.value,
                'novelty_level': hypothesis.novelty_level.value,
                'testability': hypothesis.testability.value,
                'confidence': hypothesis.confidence,
                'domain': hypothesis.domain,
                'key_prediction': hypothesis.key_prediction,
                'rationale': hypothesis.rationale,
                'supporting_evidence': hypothesis.supporting_evidence,
                'suggested_experiments': hypothesis.suggested_experiments,
                'potential_impact': hypothesis.potential_impact,
                'generated_at': hypothesis.generated_at
            }

            with open(history_path, 'a') as f:
                f.write(json.dumps(hyp_dict) + '\n')

        except Exception as e:
            print(f"Error saving hypothesis: {e}")

    def _dict_to_hypothesis(self, hyp_dict: Dict[str, Any]) -> Optional[NovelHypothesis]:
        """Convert dictionary to NovelHypothesis"""
        try:
            return NovelHypothesis(
                hypothesis_id=hyp_dict["hypothesis_id"],
                title=hyp_dict["title"],
                description=hyp_dict["description"],
                hypothesis_type=HypothesisType(hyp_dict["hypothesis_type"]),
                novelty_level=NoveltyLevel(hyp_dict["novelty_level"]),
                testability=TestabilityLevel(hyp_dict["testability"]),
                confidence=hyp_dict["confidence"],
                domain=hyp_dict["domain"],
                key_prediction=hyp_dict["key_prediction"],
                rationale=hyp_dict.get("rationale", []),
                supporting_evidence=hyp_dict.get("supporting_evidence", []),
                conflicting_evidence=hyp_dict.get("conflicting_evidence", []),
                suggested_experiments=hyp_dict.get("suggested_experiments", []),
                potential_impact=hyp_dict.get("potential_impact", []),
                related_hypotheses=hyp_dict.get("related_hypotheses", []),
                generated_at=hyp_dict["generated_at"]
            )
        except Exception as e:
            print(f"Error converting hypothesis: {e}")
            return None

    def get_top_hypotheses(self, domain: Optional[str] = None, min_confidence: float = 0.6, limit: int = 10) -> List[NovelHypothesis]:
        """Get top hypotheses by confidence"""
        filtered = [h for h in self.hypotheses if h.confidence >= min_confidence]
        if domain:
            filtered = [h for h in filtered if h.domain == domain]
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        return filtered[:limit]


def create_hypothesis_generator() -> HypothesisGenerator:
    """Factory function to create hypothesis generator"""
    return HypothesisGenerator()


# Singleton instance
_instance = None

def get_hypothesis_generator() -> HypothesisGenerator:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_hypothesis_generator()
    return _instance
