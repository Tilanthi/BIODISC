"""Tests for question<->dataset relevance pinning.

Verifies that a question is served its biologically-matching dataset first
(mouse-liver -> mus_musculus liver dataset, breast -> breast, leukemia ->
bone-marrow/PB), eliminating the incoherent pairings the loose rotation
produced (e.g. a breast-cancer question on a mouse high-fat-diet liver dataset).
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.specific_questions import (  # noqa: E402
    rank_datasets_for_question, select_datasets_for_question,
)
from biodisc_core.fixed_pipeline.real_datasets import REAL_GEO_DATASETS  # noqa: E402


def _ids(ranked):
    return [ds["id"] for _, ds in ranked]


def test_mouse_liver_question_pins_to_mouse_liver_dataset():
    q = ("Which lipid-metabolism genes are differentially expressed in mouse "
         "liver under high-fat vs standard diet?")
    ranked = rank_datasets_for_question(q, REAL_GEO_DATASETS)
    assert ranked[0][0] > 0, "should have a positive match"
    assert ranked[0][1]["id"] == "GSE15822", f"mouse-liver question should pin to GSE15822, got {_ids(ranked)}"


def test_breast_cancer_question_pins_to_breast_dataset():
    q = ("How does BRCA1 mutation status affect response to PARP inhibitors in "
         "triple-negative breast cancer?")
    ranked = rank_datasets_for_question(q, REAL_GEO_DATASETS)
    assert ranked[0][0] > 0
    assert ranked[0][1]["id"] == "GSE2034", f"breast-cancer question should pin to GSE2034, got {_ids(ranked)}"


def test_leukemia_question_pins_to_leukemia_dataset():
    q = ("How do gene expression profiles differ between bone marrow and "
         "peripheral blood leukemia samples?")
    ranked = rank_datasets_for_question(q, REAL_GEO_DATASETS)
    assert ranked[0][0] > 0
    assert ranked[0][1]["id"] == "GSE13159", f"leukemia question should pin to GSE13159, got {_ids(ranked)}"


def test_unmatched_question_scores_zero_everywhere():
    # No entity overlap with any verified dataset -> all zero (caller rotates).
    q = "How does quantum tunneling affect photosynthetic efficiency?"
    ranked = rank_datasets_for_question(q, REAL_GEO_DATASETS)
    assert all(score == 0 for score, _ in ranked)


def test_ranking_is_deterministic():
    q = "mouse liver high-fat diet"
    a = _ids(rank_datasets_for_question(q, REAL_GEO_DATASETS))
    b = _ids(rank_datasets_for_question(q, REAL_GEO_DATASETS))
    assert a == b


def test_select_returns_matched_dataset_first():
    q = ("Which lipid-metabolism genes are differentially expressed in mouse "
         "liver under high-fat vs standard diet?")
    selected = select_datasets_for_question(q, REAL_GEO_DATASETS)
    assert [d["id"] for d in selected] == ["GSE15822"]


def test_select_returns_empty_when_no_dataset_matches():
    """A question with no biological relation to any verified dataset must be
    SKIPPED (return []), not rotated onto a random dataset — otherwise it yields
    an incoherent candidate the entity-sparse validator can't catch
    (e.g. glioblastoma on a breast-cancer dataset)."""
    q = "Does STAT3 activation differ between IL-6 treated and untreated glioblastoma cells?"
    assert select_datasets_for_question(q, REAL_GEO_DATASETS) == []


def test_select_returns_empty_for_entity_less_question():
    q = "How does quantum tunneling affect photosynthetic efficiency?"
    assert select_datasets_for_question(q, REAL_GEO_DATASETS) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
