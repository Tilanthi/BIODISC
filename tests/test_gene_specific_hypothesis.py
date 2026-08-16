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
"""Tests for the gene-specific hypothesis primitive."""
import numpy as np

from biodisc_core.fixed_pipeline.gene_specific_hypothesis import (
    claimed_direction, evaluate_gene_hypothesis as gene_hyp,
    evaluate_question_hypothesis as question_hyp)


def _expr():
    # 6 samples (3 per group) x 3 genes.
    # GENEA: high in group0, low in group1 -> DOWN in group1 vs group0.
    # GENEB: low in group0, high in group1 -> UP.
    # GENEC: unchanged.
    return np.array([
        [8.0, 2.0, 5.0],
        [8.0, 2.0, 5.0],
        [8.0, 2.0, 5.0],
        [2.0, 8.0, 5.0],
        [2.0, 8.0, 5.0],
        [2.0, 8.0, 5.0],
    ]), ["GENEA", "GENEB", "GENEC"], [0, 0, 0, 1, 1, 1]


def test_claimed_direction_contrarian():
    assert claimed_direction("Whereas MTOR typically increases in liver, does it paradoxically decrease?") == "down"
    assert claimed_direction("Does TP53 increase in cancer?") == "up"


def test_claimed_direction_relative_is_none():
    # "opposite direction" with no explicit up/down word -> inconclusive
    assert claimed_direction("Does TP53 change in the OPPOSITE direction to the textbook?") is None


def test_gene_hypothesis_supported_contrarian():
    expr, genes, labels = _expr()
    r = gene_hyp(expr, genes, labels, "GENEA", claimed_dir="down")
    assert r.present is True
    assert r.observed_direction == "down"
    assert r.significant is True
    assert r.supports_claim is True   # contrarian "decrease" confirmed -> surprise


def test_gene_hypothesis_not_supported_textbook_held():
    expr, genes, labels = _expr()
    r = gene_hyp(expr, genes, labels, "GENEA", claimed_dir="up")
    assert r.observed_direction == "down"
    assert r.supports_claim is False  # claimed up, observed down -> claim fails


def test_gene_hypothesis_gene_not_measured():
    expr, genes, labels = _expr()
    r = gene_hyp(expr, genes, labels, "NOTHERE", claimed_dir="down")
    assert r.present is False
    assert r.supports_claim is None


def test_gene_hypothesis_relative_claim_inconclusive():
    expr, genes, labels = _expr()
    r = gene_hyp(expr, genes, labels, "GENEA", claimed_dir=None)
    assert r.observed_direction == "down"
    assert r.supports_claim is None   # no baseline -> can't judge the relative claim


def test_question_hypothesis_extracts_and_tests():
    expr, genes, labels = _expr()
    r = question_hyp("Whereas GENEA typically increases here, does it paradoxically decrease?", expr, genes, labels)
    assert r is not None
    assert r.gene == "GENEA"
    assert r.claimed_direction == "down"
    assert r.supports_claim is True


def test_question_hypothesis_none_for_exploratory():
    expr, genes, labels = _expr()
    assert question_hyp("Which genes differ between tumor and normal?", expr, genes, labels) is None
