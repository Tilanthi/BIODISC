"""Question classifier for template vs. specific question detection."""
import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Classification of question type."""
    SPECIFIC_MECHANISTIC = "specific_mechanistic"  # Novel, specific
    SPECIFIC_QUESTIONS = "specific_questions"  # Novel but broad
    GENERIC_TEMPLATE = "generic_template"  # Template question
    SATURATED_FIELD = "saturated_field"  # Well-established field

@dataclass
class QuestionClassification:
    """Result of question classification."""

    question_type: QuestionType
    specificity_score: float  # 0-10 (higher = more specific)
    template_patterns: List[str]
    confidence: float
    reason: str

class QuestionClassifier:
    """Classify questions as template vs. specific."""

    def __init__(self):
        self.classifications = 0
        self.template_questions = 0

        # Template patterns (generic, non-specific)
        self.TEMPLATE_PATTERNS = [
            r'how does .* affect .*',
            r'how do .* affect .*',
            r'what is the role of .* in .*',
            r'what are the .* of .*',
            r'how does .* regulate .*',
            r'how do .* regulate .*',
            r'what genes .* in .*',
        ]

        # Specific indicators (mechanistic, novel)
        self.SPECIFIC_INDICATORS = [
            'mutation',
            'variant',
            'phosphorylation',
            'acetylation',
            'methylation',
            'binding',
            'interaction',
            'pathway',
            'signaling',
            'cascade',
            'feedback',
            'regulation',
            'regulate',
            'mechanism',
            'transcriptional',
            'silencing',
            'differentiation',
            'mediated',
        ]

        # Well-established saturated fields
        self.SATURATED_PATTERNS = [
            r'BRCA1.*PARP',
            r'TP53.*cancer',
            r'EGFR.*lung.*cancer',
            r'cell cycle.*yeast',
            r'p53.*DNA.*damage',
        ]

        logger.info("🔍 QuestionClassifier initialized")
        logger.info(f"   Template patterns: {len(self.TEMPLATE_PATTERNS)}")
        logger.info(f"   Specific indicators: {len(self.SPECIFIC_INDICATORS)}")
        logger.info(f"   Saturated patterns: {len(self.SATURATED_PATTERNS)}")

    def classify_question(self, question: str) -> QuestionClassification:
        """
        Classify question as template vs. specific.

        Args:
            question: Research question text

        Returns:
            QuestionClassification with type and details
        """

        logger.info(f"🔍 CLASSIFYING QUESTION: {question[:60]}...")

        self.classifications += 1

        question_lower = question.lower()

        # NOTE: The SATURATED_PATTERNS early-return was removed. It conflated
        # field activity with specific-question novelty: any question mentioning
        # a well-studied pair (BRCA1/PARP, TP53/cancer, ...) was force-classified
        # as SATURATED_FIELD regardless of how specific and mechanistic the
        # question was. That made Layer 5 reject the system's OWN curated
        # specific questions (specific_questions.py #1 is the BRCA1/PARP
        # question), zeroing discovery throughput. Classification now falls
        # through to the specificity-based logic below, which still rejects
        # genuinely generic template questions.

        # Check for template patterns
        matched_templates = []
        for pattern in self.TEMPLATE_PATTERNS:
            if re.search(pattern, question_lower, re.IGNORECASE):
                matched_templates.append(pattern)

        # Check for specific indicators
        matched_specific = []
        for indicator in self.SPECIFIC_INDICATORS:
            if indicator in question_lower:
                matched_specific.append(indicator)

        # Calculate specificity score
        specificity = self._calculate_specificity(
            matched_templates, matched_specific, question
        )

        # Determine question type
        if len(matched_templates) > 0 and len(matched_specific) == 0:
            # Template without specificity
            question_type = QuestionType.GENERIC_TEMPLATE
            confidence = 0.8
            reason = f"Generic template question (matched {len(matched_templates)} template patterns)"
        elif len(matched_specific) >= 2:
            # Multiple specific indicators
            question_type = QuestionType.SPECIFIC_MECHANISTIC
            confidence = 0.85
            reason = f"Specific mechanistic question ({len(matched_specific)} specific indicators)"
        elif len(matched_specific) >= 1:
            # Some specificity
            question_type = QuestionType.SPECIFIC_QUESTIONS
            confidence = 0.75
            reason = f"Specific but not highly mechanistic ({len(matched_specific)} specific indicators)"
        else:
            # Borderline
            question_type = QuestionType.SPECIFIC_QUESTIONS
            confidence = 0.6
            reason = "Moderately specific question"

        # Track templates
        if question_type in [QuestionType.GENERIC_TEMPLATE, QuestionType.SATURATED_FIELD]:
            self.template_questions += 1
            logger.warning(f"⚠️  TEMPLATE QUESTION DETECTED: {question_type.value}")
        else:
            logger.info(f"✅ SPECIFIC QUESTION: {question_type.value}")

        return QuestionClassification(
            question_type=question_type,
            specificity_score=specificity,
            template_patterns=matched_templates,
            confidence=confidence,
            reason=reason
        )

    def _calculate_specificity(
        self,
        templates: List[str],
        specific: List[str],
        question: str
    ) -> float:
        """Calculate specificity score (0-10)."""

        score = 5.0  # Base score

        # Penalize templates
        score -= len(templates) * 1.5

        # Bonus for specific indicators
        score += len(specific) * 0.8

        # Bonus for longer questions (more specific)
        word_count = len(question.split())
        if word_count > 15:
            score += 1.0
        elif word_count > 10:
            score += 0.5

        # Bonus for specific gene/protein names
        if re.search(r'\b[A-Z]{2,10}\d*\b', question):  # Gene symbols
            score += 0.5

        return max(0.0, min(score, 10.0))

    def get_statistics(self) -> Dict:
        """Get classification statistics."""
        return {
            'classifications_performed': self.classifications,
            'template_questions_detected': self.template_questions,
            'template_rate': f"{(self.template_questions / max(self.classifications, 1)) * 100:.2f}%"
        }
