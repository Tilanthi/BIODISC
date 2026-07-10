"""Template pattern detection system."""
import logging
from typing import Dict, List, Tuple
from .question_classifier import QuestionClassifier, QuestionType, QuestionClassification
from .novelty_estimator import NoveltyEstimator, NoveltyEstimate

logger = logging.getLogger(__name__)

class TemplateDetector:
    """Complete template detection and novelty estimation system."""

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.novelty_estimator = NoveltyEstimator()
        self.rejections = 0

        # Minimum novelty threshold
        self.MIN_NOVELTY_SCORE = 5.0  # Questions with novelty < 5.0 are rejected

        logger.info("🔍 TemplateDetector initialized")
        logger.info(f"   Minimum novelty score: {self.MIN_NOVELTY_SCORE}/10")

    def validate_question(
        self,
        question: str
    ) -> Tuple[bool, QuestionClassification, NoveltyEstimate]:
        """
        Validate question as template vs. specific.

        Args:
            question: Research question

        Returns:
            (is_valid, classification, novelty_estimate)
        """

        # Classify question
        classification = self.classifier.classify_question(question)

        # Estimate novelty
        novelty = self.novelty_estimator.estimate_novelty(question, classification)

        # Make decision
        is_valid = novelty.novelty_score >= self.MIN_NOVELTY_SCORE

        if not is_valid:
            self.rejections += 1
            logger.warning(f"❌ TEMPLATE QUESTION REJECTED: {question[:60]}...")
            logger.warning(f"   Novelty: {novelty.novelty_score}/10 (minimum: {self.MIN_NOVELTY_SCORE})")
        else:
            logger.info(f"✅ SPECIFIC QUESTION ACCEPTED: {question[:60]}...")
            logger.info(f"   Novelty: {novelty.novelty_score}/10")

        return is_valid, classification, novelty

    def get_statistics(self) -> Dict:
        """Get detection statistics."""
        stats = self.classifier.get_statistics()
        stats.update(self.novelty_estimator.get_statistics())
        stats['rejections'] = self.rejections
        return stats

def create_template_detector() -> TemplateDetector:
    """Factory function to create template detector."""
    return TemplateDetector()
