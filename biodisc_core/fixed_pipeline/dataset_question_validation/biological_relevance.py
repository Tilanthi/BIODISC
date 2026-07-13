"""Biological relevance validation for dataset-question pairs."""
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from .ontology_mapper import OntologyMapper

logger = logging.getLogger(__name__)

@dataclass
class RelevanceValidationResult:
    """Result of biological relevance validation."""

    is_relevant: bool
    score: float  # 0-10
    reason: str
    question_entities: Dict
    dataset_entities: Dict
    mismatches: list

class BiologicalRelevanceValidator:
    """Validate biological relevance of dataset-question pairs."""

    def __init__(self):
        self.mapper = OntologyMapper()
        self.validations = 0
        self.rejections = 0

        # Minimum relevance score. A genuinely relevant pair (no organism /
        # tissue / disease conflict) earns a 5.0 base; sparse dataset metadata
        # (organism='Unknown', generic title) cannot yield the entity-match
        # bonuses, so 6.0 was unreachable and every relevant pair was rejected.
        # 5.0 lets relevance clear the gate while real mismatches (which score
        # ~0-0.5 because is_relevant=False) still fail.
        self.MIN_SCORE = 5.0  # Relevant pair passes; mismatched pair fails

        logger.info("🎯 BiologicalRelevanceValidator initialized")
        logger.info(f"   Minimum relevance score: {self.MIN_SCORE}/10")

    def validate_relevance(
        self,
        question: str,
        dataset_metadata: Dict
    ) -> RelevanceValidationResult:
        """
        Validate if dataset is biologically relevant to question.

        Args:
            question: Research question text
            dataset_metadata: Dataset metadata (title, organism, tissue, etc.)

        Returns:
            RelevanceValidationResult with decision and details
        """

        logger.info("🎯 VALIDATING BIOLOGICAL RELEVANCE")
        logger.info(f"   Question: {question[:60]}...")

        self.validations += 1

        # Extract entities
        question_entities = self.mapper.extract_entities(question)

        # Extract from dataset metadata
        dataset_text = self._format_dataset_metadata(dataset_metadata)
        dataset_entities = self.mapper.extract_entities(dataset_text)

        logger.info(f"   Question entities: {question_entities}")
        logger.info(f"   Dataset entities: {dataset_entities}")

        # Check relevance
        is_relevant, mismatch_reason = self.mapper.check_relevance(
            question_entities, dataset_entities
        )

        # Calculate score
        score = self._calculate_relevance_score(
            question_entities, dataset_entities, is_relevant
        )

        # Collect mismatches
        mismatches = []
        if not is_relevant:
            mismatches.append(mismatch_reason)

        # Make decision
        final_decision = is_relevant and score >= self.MIN_SCORE

        # Honest reason: distinguish a genuine mismatch from a low-score pass.
        # check_relevance() returns the success phrase "Biological relevance
        # confirmed" as its reason even when is_relevant=True, so reusing it as
        # the rejection reason produced the misleading "REJECTED: Biological
        # relevance confirmed" log line.
        if not final_decision:
            self.rejections += 1
            if not is_relevant:
                reason = mismatch_reason  # genuine organism/tissue/disease conflict
            else:
                reason = (
                    f"Relevant but insufficient relevance signals "
                    f"(score {score:.1f}/10 < {self.MIN_SCORE}; add organism/"
                    f"tissue/disease metadata)"
                )
            logger.warning(f"❌ REJECTED: {reason} (score: {score}/10)")
        else:
            reason = "Biological relevance confirmed"
            logger.info(f"✅ ACCEPTED: {reason} (score: {score}/10)")

        return RelevanceValidationResult(
            is_relevant=final_decision,
            score=score,
            reason=reason,
            question_entities=question_entities,
            dataset_entities=dataset_entities,
            mismatches=mismatches
        )

    def _format_dataset_metadata(self, metadata: Dict) -> str:
        """Format dataset metadata into text for entity extraction."""

        parts = []

        if 'title' in metadata:
            parts.append(metadata['title'])
        if 'summary' in metadata:
            parts.append(metadata['summary'])
        if 'organism' in metadata:
            parts.append(metadata['organism'])
        if 'tissue' in metadata:
            parts.append(metadata['tissue'])
        if 'disease' in metadata:
            parts.append(metadata['disease'])

        return ' '.join(parts)

    def _calculate_relevance_score(
        self,
        q_entities: Dict,
        d_entities: Dict,
        is_relevant: bool
    ) -> float:
        """Calculate relevance score (0-10)."""

        score = 0.0

        # Start with base score
        if is_relevant:
            score += 5.0

        # Organism match (critical): +3 points
        q_orgs = q_entities.get('organisms', set())
        d_orgs = d_entities.get('organisms', set())
        if q_orgs and d_orgs and q_orgs.intersection(d_orgs):
            score += 3.0

        # Tissue match (important): +2 points
        q_tissues = q_entities.get('tissues', set())
        d_tissues = d_entities.get('tissues', set())
        if q_tissues and d_tissues and q_tissues.intersection(d_tissues):
            score += 2.0

        # Disease match (important): +2 points
        q_diseases = q_entities.get('diseases', set())
        d_diseases = d_entities.get('diseases', set())
        if q_diseases and d_diseases and q_diseases.intersection(d_diseases):
            score += 2.0

        # If any entities in question, bonus for specificity
        if q_orgs or q_tissues or q_diseases:
            score += 0.5

        return min(score, 10.0)

    def get_statistics(self) -> Dict:
        """Get validation statistics."""
        return {
            'validations_performed': self.validations,
            'rejections': self.rejections,
            'rejection_rate': f"{(self.rejections / max(self.validations, 1)) * 100:.2f}%"
        }
