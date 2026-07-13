"""
Repro/verification for the two validation-gate root causes that zeroed
discovery throughput (RC1: Layer 2 unreachable threshold; RC2: Layer 5
saturation blacklist vs. its own question pool).

Run before the fix  -> both assertions FAIL (reproduces the bug).
Run after  the fix  -> both assertions PASS.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from biodisc_core.fixed_pipeline.dataset_question_validation.biological_relevance import (
    BiologicalRelevanceValidator,
)
from biodisc_core.fixed_pipeline.template_detection import create_template_detector


def test_layer2_relevant_pair_with_sparse_metadata_passes():
    """RC1: a relevant question + sparse-metadata dataset must pass Layer 2.

    Real verified datasets often carry organism='Unknown' and a generic title,
    so no organism/tissue/disease entity match is possible. The scorer then
    awards 5.0 (relevant) + 0.5 (specificity) = 5.5. The gate must not reject
    a relevant pair for lacking metadata it was never given.
    """
    v = BiologicalRelevanceValidator()
    question = (
        "How does PD-L1 expression change after IFN-gamma exposure in melanoma cells?"
    )
    sparse_dataset = {
        "title": "Dataset from NCBI Gene Expression Omnibus",
        "organism": "Unknown",
    }
    result = v.validate_relevance(question, sparse_dataset)
    assert result.is_relevant, (
        f"RC1 NOT FIXED: relevant pair rejected at score {result.score}/10 "
        f"(reason: {result.reason}). MIN_SCORE is above the 5.5 a relevant pair "
        f"earns from sparse metadata."
    )
    print(f"  [RC1] Layer 2 PASS (score {result.score}/10): {result.reason}")


def test_layer2_genuine_mismatch_still_rejected():
    """Guard: lowering the threshold must not let a true organism mismatch through."""
    v = BiologicalRelevanceValidator()
    question = "How does STAT3 activation differ in human glioblastoma cells?"
    mismatched_dataset = {
        "title": "Mouse glioblastoma expression study",
        "organism": "mouse",
    }
    result = v.validate_relevance(question, mismatched_dataset)
    assert not result.is_relevant, (
        f"Layer 2 let a human/mouse organism mismatch through (score {result.score}/10)"
    )
    print(f"  [guard] organism mismatch correctly rejected: {result.reason}")


def test_layer5_specific_question_in_busy_field_passes():
    """RC2: a specific, mechanistic question must not be auto-rejected just
    because its field is well-studied. Field activity != specific novelty."""
    detector = create_template_detector()
    question = (
        "How does BRCA1 mutation status affect response to PARP inhibitors "
        "in triple-negative breast cancer?"
    )
    is_valid, classification, novelty = detector.validate_question(question)
    assert is_valid, (
        f"RC2 NOT FIXED: specific question rejected as 'saturated field' "
        f"(novelty {novelty.novelty_score}/10, type {classification.question_type})."
    )
    print(
        f"  [RC2] Layer 5 PASS (novelty {novelty.novelty_score}/10, "
        f"type {classification.question_type.value})"
    )


def test_layer5_generic_template_still_rejected():
    """Guard: genuinely vague questions must still be rejected."""
    detector = create_template_detector()
    question = "What genes are important in cancer?"
    is_valid, classification, novelty = detector.validate_question(question)
    assert not is_valid, (
        f"Layer 5 let a generic template question through (novelty {novelty.novelty_score}/10)"
    )
    print(
        f"  [guard] generic template correctly rejected (novelty {novelty.novelty_score}/10)"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("GATE FIX VERIFICATION (expect FAIL before fix, PASS after)")
    print("=" * 70)
    tests = [
        test_layer2_relevant_pair_with_sparse_metadata_passes,
        test_layer2_genuine_mismatch_still_rejected,
        test_layer5_specific_question_in_busy_field_passes,
        test_layer5_generic_template_still_rejected,
    ]
    failed = 0
    for t in tests:
        print(f"\n{t.__name__}")
        try:
            t()
            print("  -> PASS")
        except AssertionError as e:
            failed += 1
            print(f"  -> FAIL: {e}")
    print("\n" + "=" * 70)
    print(f"{len(tests) - failed}/{len(tests)} checks passed")
    print("=" * 70)
    sys.exit(1 if failed else 0)
