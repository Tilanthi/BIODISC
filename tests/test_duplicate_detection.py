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
"""Tests for near-duplicate detection via DE-gene overlap (Lever 1).

The genuine store was inflating on the same contrast rediscovered with different
question phrasings (e.g. GSE15822 high-fat diet x5) because exact-hash and
question+dataset checks miss them. A gene-overlap check on the same dataset
catches them: two discoveries sharing most of their top DE genes are the same
finding re-derived.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.duplicate_detection import create_duplicate_detector  # noqa: E402


def _genes(syms):
    return [{"gene_symbol": s} for s in syms]


def test_near_duplicate_same_dataset_high_gene_overlap():
    det = create_duplicate_detector()
    d1 = {"question": "lipid-metabolism genes in mouse liver",
          "dataset_id": "GSE15822",
          "differential_expression": {"significant_genes_count": 153, "best_p_value": 0.001,
                                      "top_upregulated": _genes([f"G{i}" for i in range(10)])}}
    det.register_discovery(d1)
    # different question phrasing + different stats (so Check 3 doesn't fire), SAME dataset,
    # 8/10 genes overlap -> same finding re-derived
    d2 = {"question": "how does a high-fat diet alter hepatic expression",
          "dataset_id": "GSE15822",
          "differential_expression": {"significant_genes_count": 155, "best_p_value": 0.002,
                                      "top_upregulated": _genes([f"G{i}" for i in range(8)] + ["X", "Y"])}}
    is_dup, reason = det.check_duplicate(d2)
    assert is_dup, f"near-duplicate should be caught: {reason}"
    assert "overlap" in reason.lower()


def test_distinct_findings_not_flagged():
    det = create_duplicate_detector()
    det.register_discovery({"question": "Q1", "dataset_id": "GSE15822",
                            "differential_expression": {"significant_genes_count": 150, "best_p_value": 0.001,
                                                        "top_upregulated": _genes([f"G{i}" for i in range(10)])}})
    # different dataset, entirely different genes -> not a duplicate
    d2 = {"question": "Q2", "dataset_id": "GSE2034",
          "differential_expression": {"significant_genes_count": 200, "best_p_value": 0.0005,
                                      "top_upregulated": _genes([f"H{i}" for i in range(10)])}}
    assert not det.check_duplicate(d2)[0]


def test_same_dataset_low_overlap_not_flagged():
    det = create_duplicate_detector()
    det.register_discovery({"question": "Q1", "dataset_id": "GSE2034",
                            "differential_expression": {"significant_genes_count": 120, "best_p_value": 0.001,
                                                        "top_upregulated": _genes([f"G{i}" for i in range(10)])}})
    # same dataset but 0% gene overlap -> distinct finding on the same data
    d2 = {"question": "Q2", "dataset_id": "GSE2034",
          "differential_expression": {"significant_genes_count": 130, "best_p_value": 0.002,
                                      "top_upregulated": _genes([f"Z{i}" for i in range(10)])}}
    assert not det.check_duplicate(d2)[0]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
