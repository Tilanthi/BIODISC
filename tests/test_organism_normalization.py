"""Regression test for organism normalization in dataset-question validation.

Bug: extract_entities() returned raw keys ('mouse', 'mus musculus'), so a
mouse-liver question on a mus-musculus dataset was rejected as an organism
mismatch — killing the GSE15822 (mouse) dataset entirely. Fix: compare on
canonical NCBITaxon IDs.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.dataset_question_validation.ontology_mapper import OntologyMapper  # noqa: E402
from biodisc_core.fixed_pipeline.dataset_question_validation.biological_relevance import (  # noqa: E402
    BiologicalRelevanceValidator,
)


def test_organism_common_name_matches_latin_name():
    m = OntologyMapper()
    assert m.normalize_organisms({"mouse"}) == m.normalize_organisms({"mus musculus"})
    assert m.normalize_organisms({"human"}) == m.normalize_organisms({"homo sapiens"})
    assert m.normalize_organisms({"rat"}) == m.normalize_organisms({"rattus norvegicus"})


def test_mouse_question_on_mus_musculus_dataset_is_relevant():
    v = BiologicalRelevanceValidator()
    r = v.validate_relevance(
        "Which lipid-metabolism genes are differentially expressed in mouse liver "
        "under high-fat vs standard diet?",
        {"title": "High-fat vs standard diet liver transcriptome",
         "organism": "mus musculus", "tissue": "liver"},
    )
    assert r.is_relevant, f"mouse/mus musculus should match: {r.reason}"
    assert r.score >= 5.0


def test_genuine_organism_mismatch_still_rejected():
    v = BiologicalRelevanceValidator()
    r = v.validate_relevance(
        "mouse liver diet", {"organism": "homo sapiens", "tissue": "liver"})
    assert not r.is_relevant
    assert "mismatch" in r.reason.lower()


def test_tissue_synonyms_match_after_normalization():
    m = OntologyMapper()
    assert m.normalize_tissues({"breast"}) == m.normalize_tissues({"mammary"})


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
