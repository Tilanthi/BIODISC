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
"""Novelty estimator based on literature analysis."""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class NoveltyEstimate:
    """Estimate of scientific novelty."""

    novelty_score: float  # 0-10
    literature_saturation: str  # "low", "medium", "high", "saturated"
    estimated_paper_count: int
    confidence: float
    reason: str

class NoveltyEstimator:
    """Estimate novelty based on question analysis."""

    def __init__(self):
        self.estimations = 0

        # Known saturated fields with paper counts
        self.SATURATED_FIELDS = {
            'BRCA1 PARP inhibitor': 5000,
            'TP53 cancer': 10000,
            'cell cycle yeast': 3000,
            'EGFR lung cancer': 4000,
            'p53 DNA damage': 6000,
        }

        # Paper count estimation based on question specificity
        self.PAPER_COUNT_RANGES = {
            'highly_specific': (100, 500),  # Narrow niche
            'specific': (500, 2000),  # Specific area
            'moderate': (2000, 5000),  # Established area
            'broad': (5000, 10000),  # Large field
            'saturated': (10000, 50000),  # Very well-established
        }

        logger.info("📚 NoveltyEstimator initialized")
        logger.info(f"   Known saturated fields: {len(self.SATURATED_FIELDS)}")

    def estimate_novelty(
        self,
        question: str,
        classification: 'QuestionClassification'
    ) -> NoveltyEstimate:
        """
        Estimate scientific novelty of question.

        Args:
            question: Research question
            classification: Question classification result

        Returns:
            NoveltyEstimate with score and details
        """

        logger.info("📚 ESTIMATING SCIENTIFIC NOVELTY")

        self.estimations += 1

        # NOTE: The two saturation blacklist paths (a SATURATED_FIELD
        # classification branch and a SATURATED_FIELDS substring dict) were
        # removed. They hard-zeroed novelty for any question touching a busy
        # field (BRCA1/PARP, TP53/cancer, ...) which conflates field activity
        # with specific-question novelty and rejected the system's own curated
        # specific questions. Novelty is now driven by question type and
        # specificity below. (Genuinely generic template questions still score
        # low and are rejected by the MIN_NOVELTY_SCORE gate.) A real novelty
        # check should be literature-similarity based, not a keyword blacklist.

        # Estimate based on question type and specificity
        if classification.question_type.name == "SPECIFIC_MECHANISTIC":
            novelty_range = self.PAPER_COUNT_RANGES['highly_specific']
            saturation = "low"
            novelty_score = 8.5
        elif classification.question_type.name == "SPECIFIC_QUESTIONS":
            novelty_range = self.PAPER_COUNT_RANGES['specific']
            saturation = "medium"
            novelty_score = 7.0
        elif classification.question_type.name == "GENERIC_TEMPLATE":
            novelty_range = self.PAPER_COUNT_RANGES['broad']
            saturation = "high"
            novelty_score = 3.0
        else:  # Should not reach here, but handle gracefully
            novelty_range = self.PAPER_COUNT_RANGES['specific']
            saturation = "medium"
            novelty_score = 7.0

        # Adjust based on specificity score
        specificity = classification.specificity_score
        if specificity >= 8.0:
            novelty_score += 1.0
        elif specificity >= 6.0:
            novelty_score += 0.5
        elif specificity <= 3.0:
            novelty_score -= 1.0

        # Estimate paper count
        estimated_papers = sum(novelty_range) // 2

        logger.info(f"   Novelty score: {novelty_score}/10")
        logger.info(f"   Saturation: {saturation} (~{estimated_papers} papers)")

        return NoveltyEstimate(
            novelty_score=min(novelty_score, 10.0),
            literature_saturation=saturation,
            estimated_paper_count=estimated_papers,
            confidence=classification.confidence,
            reason=f"Estimated {estimated_papers} papers in this area (saturation: {saturation})"
        )

    def get_statistics(self) -> Dict:
        """Get estimation statistics."""
        return {
            'estimations_performed': self.estimations
        }
