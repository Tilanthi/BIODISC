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
    """Test rejection of generic template question."""
    detector = create_template_detector()

    question = "How does BRCA1 mutation affect response to PARP inhibitors?"  # Exact template from peer review
    is_valid, classification, novelty = detector.validate_question(question)

    # Should be REJECTED - template question in saturated field
    assert not is_valid
    assert classification.question_type in [
        QuestionType.GENERIC_TEMPLATE,
        QuestionType.SATURATED_FIELD
    ]
    assert novelty.novelty_score < 5.0

def test_saturated_field_detection():
    """Test detection of saturated field (BRCA1-PARP)."""
    detector = create_template_detector()

    question = "How does BRCA1 mutation status affect response to PARP inhibitors in triple-negative breast cancer?"
    is_valid, classification, novelty = detector.validate_question(question)

    # Should detect as saturated field
    assert not is_valid or novelty.literature_saturation in ["high", "saturated"]
    assert novelty.estimated_paper_count >= 4000  # BRCA1-PARP is very saturated

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
