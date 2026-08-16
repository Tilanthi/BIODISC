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
"""Test template pattern detection."""
import pytest
from biodisc_core.fixed_pipeline.template_detection import (
    create_template_detector,
    QuestionType,
    QuestionClassification
)

def test_specific_mechanistic_question():
    """Test classification of specific mechanistic question."""
    detector = create_template_detector()

    question = "How does BRCA1 phosphorylation at Ser1524 affect DNA repair pathway choice in triple-negative breast cancer?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Should be ACCEPTED - specific mechanistic question
    assert is_valid
    assert classification.question_type == QuestionType.SPECIFIC_MECHANISTIC
    assert novelty.novelty_score >= 7.0

def test_template_question():
    """A specific question in a busy field is NOT rejected by the keyword gate.

    The saturated-field keyword blacklist was deliberately removed (the V5.4
    field-activity-vs-novelty fix): broad field activity is not specific-question
    novelty, and the old blacklist was rejecting the system's own curated
    specific questions. This specific BRCA1/PARP question is correctly classified
    SPECIFIC and accepted here. Restating an already-known result is now caught
    by the REAL PubMed literature-novelty gate (orchestrator Layer 6), not a
    keyword heuristic.
    """
    detector = create_template_detector()

    question = "How does BRCA1 mutation affect response to PARP inhibitors?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Specific question in a busy field -> ACCEPTED by the keyword template gate.
    assert is_valid
    assert classification.question_type == QuestionType.SPECIFIC_QUESTIONS
    assert novelty.novelty_score >= 5.0

def test_saturated_field_detection():
    """The saturated-field keyword blacklist is gone (V5.4 fix).

    A specific question is now classified SPECIFIC with medium (not 'saturated')
    estimated literature saturation. Genuine textbook / already-known rejection
    is the job of the literature-novelty gate at the orchestrator level
    (FixedDiscoveryOrchestrator Layer 6), not this keyword estimator.
    """
    detector = create_template_detector()

    question = "How does BRCA1 mutation status affect response to PARP inhibitors in triple-negative breast cancer?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Specific question -> medium (not saturated) keyword saturation.
    assert is_valid
    assert classification.question_type == QuestionType.SPECIFIC_QUESTIONS
    assert novelty.literature_saturation in ("low", "medium")

def test_specific_questions_with_moderate_novelty():
    """Test acceptance of specific but not highly mechanistic question."""
    detector = create_template_detector()

    question = "What gene expression changes occur in metastatic colon cancer compared to primary tumors?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Should be ACCEPTED - specific question
    assert is_valid
    assert novelty.novelty_score >= 5.0

def test_generic_broad_question():
    """Test rejection of very generic broad question."""
    detector = create_template_detector()

    question = "How do genes affect cancer?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Should be REJECTED - too generic
    assert not is_valid
    assert classification.specificity_score < 5.0

def test_very_specific_niche_question():
    """Test acceptance of highly specific niche question."""
    detector = create_template_detector()

    question = "How does KDM5A-mediated H3K4 demethylation regulate transcriptional silencing of differentiation genes in acute myeloid leukemia?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Should be ACCEPTED - very specific niche
    assert is_valid
    assert novelty.novelty_score >= 8.0
    assert novelty.literature_saturation == "low"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
