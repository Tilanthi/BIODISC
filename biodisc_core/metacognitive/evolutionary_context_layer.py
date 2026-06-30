"""
Evolutionary Context Layer for MCE

Adds deep-time evolutionary/origins perspective as default context for biological questions.

CAPABILITIES:
- Automatically frame biological questions with evolutionary perspective
- Apply "origins-first" heuristic to biological problems
- Trace mechanisms back to early cellular evolution
- Consider selective advantages and ancestral states

Date: 2026-04-26
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import re

from .meta_context_engine import (
    TemporalScale, CognitiveFrame, ContextLayer, ContextMetadata
)


class EvolutionaryFrame(Enum):
    """Types of evolutionary framing"""
    ORIGINS_FIRST = "origins_first"  # Start from physical/chemical origins
    ANCESTRAL_RECONSTRUCTION = "ancestral_reconstruction"  # Reconstruct ancestral states
    SELECTIVE_ADVANTAGE = "selective_advantage"  # Focus on what was selected for
    COMPARATIVE_PHYLOGENETIC = "comparative_phylogenetic"  # Compare across lineages
    DEVELOPMENTAL_CONSISTENCY = "developmental_consistency"  # Deep homology


@dataclass
class EvolutionaryQuestion:
    """
    A biological question reframed with evolutionary perspective.

    ORIGINAL: "How does bacterial cell cycle regulation work?"
    EVOLUTIONARY: "How did bacterial cell cycle regulation evolve from
                   physical foundations, and what selective advantages
                   favored increasing molecular complexity?"
    """
    original_question: str
    evolutionary_frame: EvolutionaryFrame
    reframed_question: str
    key_questions_to_add: List[str]
    expected_insights: List[str]


class EvolutionaryContextLayer:
    """
    Adds evolutionary/origins perspective to biological questions.

    KEY HEURISTICS (learned from expert feedback):
    1. Physical constraints existed before molecular regulation
    2. Molecular systems evolved to fine-tune physical processes
    3. Selective advantages favor increasing complexity when precision matters
    4. Ancestral states reveal what is fundamental vs derived
    5. LUCA implications constrain early evolution scenarios

    USAGE:
        layer = EvolutionaryContextLayer()
        framed = layer.apply_origins_frame("How does bacterial cell cycle work?")
        # Returns evolutionary-reframed question and context
    """

    def __init__(self):
        self.biological_indicators = [
            'cell', 'organism', 'gene', 'protein', 'dna', 'rna',
            'regulation', 'metabolism', 'division', 'replication',
            'bacteri', 'evolution', 'development', 'signaling'
        ]

        self.evolutionary_keywords = [
            'evolution', 'origins', 'ancestral', 'luca', 'phylogeny',
            'selective advantage', 'adaptation', 'homology', 'deep time'
        ]

    def is_biological_question(self, question: str) -> bool:
        """Check if question is biological in nature"""
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in self.biological_indicators)

    def has_evolutionary_context(self, text: str) -> bool:
        """Check if text already includes evolutionary perspective"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.evolutionary_keywords)

    def apply_origins_frame(self, question: str) -> EvolutionaryQuestion:
        """
        Apply origins-first framing to biological question.

        PRINCIPLE: "Physical chemistry provides general, low-affinity, inefficient
        processes; molecular biology provides specific, high-affinity, efficient processes"

        QUESTIONS TO ADD:
        - What physical constraints existed before molecular regulation?
        - What selective advantages favored increasing molecular complexity?
        - What does this reveal about LUCA and early cellular evolution?
        - Is this mechanism universal (found in all life) or derived?
        """
        if not self.is_biological_question(question):
            return EvolutionaryQuestion(
                original_question=question,
                evolutionary_frame=EvolutionaryFrame.ORIGINS_FIRST,
                reframed_question=question,
                key_questions_to_add=[],
                expected_insights=[]
            )

        # Check if already has evolutionary context
        if self.has_evolutionary_context(question):
            return EvolutionaryQuestion(
                original_question=question,
                evolutionary_frame=EvolutionaryFrame.ORIGINS_FIRST,
                reframed_question=question,
                key_questions_to_add=[],
                expected_insights=["Evolutionary context already present"]
            )

        # Reframe with origins perspective
        key_questions = [
            "What physical-chemical constraints provided the foundation?",
            "How did molecular regulation evolve to fine-tune these processes?",
            "What selective advantages favored increasing complexity?",
            "What does this reveal about early cellular evolution (LUCA)?",
            "Is this mechanism universal or lineage-specific?"
        ]

        # Generate reframed question
        if "how does" in question.lower():
            reframed = question.replace("How does", "How did") + " evolve from physical foundations,"
            reframed += " and what selective advantages favored increasing molecular complexity?"
        elif "how do" in question.lower():
            reframed = question.replace("How do", "How did") + " evolve from physical foundations,"
            reframed += " and what selective advantages favored increasing molecular complexity?"
        elif "what is" in question.lower() or "what are" in question.lower():
            reframed = question + " From an evolutionary perspective, what physical constraints"
            reframed += " existed before this mechanism, and how did it evolve?"
        else:
            reframed = question + " (Consider: evolutionary origins, selective advantages, "
            reframed += "and physical foundations)"

        expected_insights = [

        expected_insights = [
            "Physical-chemical mechanisms as ancestral condition",
            "Molecular regulation as derived overlay",
            "Precision vs robustness trade-offs in evolution",
            "Environmental coupling as ancient feature"
        ]

        return EvolutionaryQuestion(
            original_question=question,
            evolutionary_frame=EvolutionaryFrame.ORIGINS_FIRST,
            reframed_question=reframamed,
            key_questions_to_add=key_questions,
            expected_insights=expected_insights
        )

    def enhance_context_layer(
        self,
        base_layer: ContextLayer,
        question: str
    ) -> ContextLayer:
        """
        Enhance an existing MCE context layer with evolutionary perspective.

        This integrates with the Meta-Context Engine by adding evolutionary
        temporal scale and cognitive frame.
        """
        evolutionary_q = self.apply_origins_frame(question)

        if evolutionary_q.reframed_question == question:
            # No enhancement needed
            return base_layer

        # Create enhanced context layer
        enhanced = ContextLayer(
            layer_id=f"{base_layer.layer_id}_evolutionary",
            temporal_scale=TemporalScale.ERA,  # Deep-time perspective
            perceptual_granularity=base_layer.perceptual_granularity,
            cognitive_frame=CognitiveFrame.NARRATIVE,  # Historical narrative
            activation=base_layer.activation + 0.1,  # Slightly boost activation
            contents={
                **base_layer.contents,
                'evolutionary_frame': evolutionary_q.evolutionary_frame.value,
                'key_questions': evolutionary_q.key_questions_to_add,
                'expected_insights': evolutionary_q.expected_insights,
                'origins_principle': "Physical chemistry provides general, low-affinity, "
                                    "inefficient processes; molecular biology provides "
                                    "specific, high-affinity, efficient processes"
            },
            metadata=ContextMetadata(
                created_at=base_layer.metadata.created_at,
                last_accessed=base_layer.metadata.last_accessed,
                access_count=base_layer.metadata.access_count,
                effectiveness_score=0.8,  # High effectiveness for evolutionary framing
                stability_score=0.7,
                novelty_score=0.6,
                emotional_valence=0.0,
                associated_minds=base_layer.metadata.associated_minds + ['causal', 'historical']
            )
        )

        return enhanced

    def get_evolutionary_context_prompt(self, question: str) -> str:
        """
        Generate a prompt that includes evolutionary context.

        This can be prepended to questions to ensure evolutionary perspective.
        """
        evolutionary_q = self.apply_origins_frame(question)

        if evolutionary_q.reframed_question == question:
            return ""

        prompt = """EVOLUTIONARY CONTEXT TO CONSIDER:

When addressing this biological question, consider:

1. PHYSICAL FOUNDATIONS: What physical-chemical constraints existed before
   molecular regulation? (DNA topology, membrane physics, thermodynamics,
   macromolecular crowding, polyelectrolyte effects)

2. EVOLUTIONARY TRAJECTORY: How did molecular systems evolve to fine-tune
   these physical processes? What selective advantages favored increasing
   complexity?

3. ANCESTRAL STATES: What does this reveal about LUCA and early cellular
   evolution? Is this mechanism universal or lineage-specific?

4. PRECISION VS ROBUSTNESS: Physical chemistry provides robust, general
   mechanisms. Molecular regulation provides precise, specific control.
   How does this trade-off manifest?

REFRAMED QUESTION: {reframed}

Original question: {original}
""".format(
    reframed=evolutionary_q.reframed_question,
    original=evolutionary_q.original_question
)

        return prompt


class PhysicsBiologyIntegrator:
    """
    Template for integrating physical and biological explanations.

    PRINCIPLE: "Physical chemistry provides general, low-affinity, inefficient
    processes; molecular biology provides specific, high-affinity, efficient processes"

    This provides the standard narrative structure for physics-biology integration
    that worked well in the bacterial cell cycle review.
    """

    def __init__(self):
        self.physical_mechanisms = [
            "DNA topology and supercoiling",
            "Membrane physics (lateral/transverse asymmetry)",
            "Macromolecular crowding and entropic forces",
            "Thermodynamic constraints",
            "Polyelectrolyte effects and reptation",
            "Liquid crystalline phases",
            "Turgor pressure and mechanical stress"
        ]

        self.molecular_systems = [
            "Regulatory proteins and feedback loops",
            "Signal transduction pathways",
            "Gene regulatory networks",
            "Checkpoint systems",
            "Targeted degradation machinery"
        ]

    def generate_integrated_explanation(
        self,
        biological_process: str,
        physical_constraint: Optional[str] = None,
        molecular_regulator: Optional[str] = None
    ) -> str:
        """
        Generate explanation integrating physics and biology.

        STRUCTURE:
        1. Physical constraints create foundational context
        2. Molecular systems evolve to fine-tune physical processes
        3. Evolutionary narrative: from physical defaults to molecular precision
        4. Hierarchical relationships: when does molecular override physical?
        """
        if not physical_constraint:
            physical_constraint = "physical-chemical constraints"
        if not molecular_regulator:
            molecular_regulator = "molecular regulation"

        explanation = f"""
## {biological_process}: Physics-Biology Integration

### Physical Foundation
{physical_constraint} provide the robust, general mechanisms that create
permissive conditions for {biological_process.lower()}. These processes operate
even in minimal cells and represent the ancestral condition.

### Molecular Refinement
{molecular_regulator} evolved to fine-tune these physical processes, providing
specificity, high-affinity interactions, and efficient control. This represents
a derived overlay on the physical foundation.

### Evolutionary Narrative
Early cells likely relied primarily on physical-chemical mechanisms for
{biological_process.lower()}. As molecular complexity increased through evolution,
regulatory systems emerged that could override physical constraints during
critical transitions (checkpoints, stress responses) while working within
physical constraints during normal homeostasis.

### Hierarchical Relationships
- **Type A (Override)**: Molecular regulation dominates during critical transitions
- **Type B (Bidirectional)**: Physical and molecular systems continuously coupled
- **Type C (Default)**: Physical processes provide baseline behavior

This framework explains how {biological_process.lower()} can be both robust
(physical foundation) and precise (molecular refinement).
"""

        return explanation


def create_evolutionary_context_layer() -> EvolutionaryContextLayer:
    """Factory function to create evolutionary context layer"""
    return EvolutionaryContextLayer()


def create_physics_biology_integrator() -> PhysicsBiologyIntegrator:
    """Factory function to create physics-biology integrator"""
    return PhysicsBiologyIntegrator()
