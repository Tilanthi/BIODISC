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
"""Tests for the held-out replication anchor (live-loop Gate for is_genuine).

Network-free: a mock analyze_fn returns a synthetic DE result so we can verify
the split + same-direction replication logic.
"""
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.replication_gate import (  # noqa: E402
    ReplicationGate, create_replication_gate, to_report_dict,
)
from biodisc_core.fixed_pipeline.differential_expression import (  # noqa: E402
    create_differential_expression_analyzer,
)


def _results(gene_symbols, sig_set, lfc_by_gene):
    return NS(results=[
        NS(gene_symbol=g, significant=(g in sig_set),
           p_value=1e-4 if g in sig_set else 0.5,
           fdr_p_value=1e-4 if g in sig_set else 0.5,
           log2_fold_change=lfc_by_gene.get(g, 0.0))
        for g in gene_symbols
    ])


def test_too_few_samples_is_not_replicated():
    gate = create_replication_gate()
    X = np.random.rand(5, 4)  # 4 samples
    labels = ["a", "a", "b", "b"]
    v = gate.assess(X, ["G1", "G2", "G3", "G4", "G5"], labels,
                    analyze_fn=lambda *a, **k: _results([], {}, {}), dataset_id="DS1")
    assert v.replicated is False
    assert "too few samples" in v.reason


def test_true_effect_replicates():
    """When genes truly differ by group, the held-out split confirms them."""
    rng = np.random.default_rng(7)
    n_genes, n_per, n_groups = 30, 10, 2
    # 6 genes have a real effect (shifted means by group)
    effect_genes = {f"G{i}" for i in range(6)}
    genes = [f"G{i}" for i in range(n_genes)]
    X = np.zeros((n_genes, n_per * n_groups))
    labels = []
    for g in range(n_groups):
        shift = 2.0 if g == 1 else 0.0
        for j in range(n_per):
            labels.append(g)
            X[:, g * n_per + j] = rng.normal(shift if True else 0, 1.0, n_genes) * 0.3
            for i in range(n_genes):
                base = rng.normal(0, 1)
                X[i, g * n_per + j] = base + (shift if i < 6 else 0.0)

    def analyze_fn(ex, syms, labs, q, ds):
        means_a = ex[:, [k for k, l in enumerate(labs) if l == labs[0]]].mean(axis=1)
        means_b = ex[:, [k for k, l in enumerate(labs) if l != labs[0]]].mean(axis=1)
        lfc = means_b - means_a
        # significant if effect size large
        sig = {genes[i] for i in range(n_genes) if abs(lfc[i]) > 0.8}
        return _results(syms, sig, {genes[i]: lfc[i] for i in range(n_genes)})

    gate = create_replication_gate(top_n=10, min_fraction=0.4, min_replicated=3)
    v = gate.assess(X, genes, labels, analyze_fn=analyze_fn, dataset_id="DS_TRUE")
    assert v.replicated is True
    assert v.n_replicated >= 3
    d = to_report_dict(v)
    assert d["replicated"] is True


def test_no_effect_does_not_replicate():
    rng = np.random.default_rng(11)
    n_genes, n_per, n_groups = 30, 10, 2
    genes = [f"G{i}" for i in range(n_genes)]
    X = rng.normal(0, 1, (n_genes, n_per * n_groups))
    labels = [g for g in range(n_groups) for _ in range(n_per)]

    def analyze_fn(ex, syms, labs, q, ds):
        # random ~3 false positives
        sig = set(rng.choice(genes, size=3, replace=False))
        lfc = rng.normal(0, 0.3, n_genes)
        return _results(syms, sig, {genes[i]: lfc[i] for i in range(n_genes)})

    gate = create_replication_gate(top_n=10, min_fraction=0.4, min_replicated=3)
    v = gate.assess(X, genes, labels, analyze_fn=analyze_fn, dataset_id="DS_NULL")
    assert v.replicated is False


def test_to_report_dict_shape():
    gate = create_replication_gate()
    v = gate.assess(np.zeros((3, 3)), ["G1"], ["a", "b", "a"],
                    analyze_fn=lambda *a, **k: _results([], {}, {}), dataset_id="X")
    d = to_report_dict(v)
    assert set(["replicated", "replication_fraction", "method", "reason"]).issubset(d.keys())


def test_replication_computes_with_the_real_de_analyzer():
    """Regression for the bug that kept replication at 0%.

    The replication gate passed group labels to the DE analyzer as a Python list,
    but the analyzer does ``np.where(group_labels == 0)`` which only does
    element-wise comparison on an ndarray. On a list, ``list == 0`` is scalar
    False -> ``np.where(False)`` -> 'nonzero on 0d' ValueError on EVERY split.
    The per-split guard caught it, so replication always degraded to
    'split DE failed' and no discovery ever reached the genuine tier.

    This test uses the REAL DE analyzer (not a mock) so it would have failed
    before the fix; after the fix it must COMPUTE a verdict, not degrade.
    """
    rng = np.random.default_rng(7)
    n_genes, n_per = 40, 30
    genes = [f"G{i}" for i in range(n_genes)]
    X = rng.normal(0, 1, (n_genes, n_per * 2))
    for j in range(n_per, n_per * 2):      # strong signal in first 6 genes, group 1
        X[:6, j] += 3.0
    labels = np.array([0] * n_per + [1] * n_per)

    analyzer = create_differential_expression_analyzer()
    gate = create_replication_gate(top_n=6, min_fraction=0.4, min_replicated=3)
    v = gate.assess(X, genes, labels,
                    analyze_fn=analyzer.perform_differential_expression_analysis,
                    dataset_id="DS_REGRESS")
    assert "split DE failed" not in v.reason, f"regression: replication degraded — {v.reason}"
    assert v.n_tested > 0  # it actually ran both split DEs and compared top genes


def test_replication_uses_top_by_pvalue_when_discovery_split_underpowered():
    """The discovery split has fewer samples than the full data, so requiring
    FDR-significance THERE dead-ends on 'no significant genes in discovery split'
    for nearly every real candidate. The gate must instead test the top-N genes
    by p-value for direction+significance replication in the held-out split."""
    genes = ["G1", "G2", "G3", "G4", "G5"]
    disc = NS(results=[
        NS(gene_symbol=g, significant=False, p_value=0.001 + i * 0.01,
           fdr_p_value=0.06, log2_fold_change=1.0)
        for i, g in enumerate(genes)])  # none FDR-significant, but ordered p-values
    held = NS(results=[
        NS(gene_symbol=g, significant=(g in {"G1", "G2", "G3"}),
           p_value=0.001, fdr_p_value=0.001 if g in {"G1", "G2", "G3"} else 0.5,
           log2_fold_change=1.0) for g in genes])  # G1-G3 replicate

    calls = {"n": 0}
    def analyze_fn(ex, syms, labs, q, ds):
        calls["n"] += 1
        return disc if calls["n"] == 1 else held

    gate = create_replication_gate(top_n=3, min_fraction=0.4, min_replicated=2)
    v = gate.assess(np.zeros((5, 8)), genes, np.array([0, 0, 0, 0, 1, 1, 1, 1]),
                    analyze_fn=analyze_fn, dataset_id="X_UNDERPOWERED")
    assert "no significant genes in discovery split" not in v.reason, v.reason
    assert v.replicated is True
    assert v.n_replicated >= 2


def test_replication_uses_nominal_p_not_fdr_in_held_out():
    """Field-standard replication bar: discover at FDR, replicate at NOMINAL p<0.05
    + same direction. Requiring FDR<0.05 in the underpowered held-out split blocked
    everything (1/15 observed live). Here the held-out top genes are nominal-p<0.05
    + same direction but NOT FDR-significant -> must replicate."""
    genes = ["G1", "G2", "G3", "G4", "G5"]
    disc = NS(results=[
        NS(gene_symbol=g, significant=False, p_value=0.001 + i * 0.01,
           fdr_p_value=0.06, log2_fold_change=1.0) for i, g in enumerate(genes)])
    held = NS(results=[  # G1-G3 nominal-p<0.05 + same direction, but NOT FDR-significant
        NS(gene_symbol=g, significant=False, p_value=0.02 if g in {"G1", "G2", "G3"} else 0.5,
           fdr_p_value=0.08, log2_fold_change=1.0) for g in genes])
    calls = {"n": 0}
    def analyze_fn(ex, syms, labs, q, ds):
        calls["n"] += 1
        return disc if calls["n"] == 1 else held

    gate = create_replication_gate(top_n=3, min_fraction=0.4, min_replicated=2)
    v = gate.assess(np.zeros((5, 8)), genes, np.array([0, 0, 0, 0, 1, 1, 1, 1]),
                    analyze_fn=analyze_fn, dataset_id="X_NOMINAL")
    assert v.replicated is True, v.reason
    assert v.n_replicated >= 2


def test_independent_cohort_replication():
    """An independent cohort (a different dataset of the same domain) confirms the
    discovery's top genes — stronger than the internal held-out split of one dataset."""
    discovery_top = [
        {"gene_symbol": "G1", "log2_fold_change": 1.0},
        {"gene_symbol": "G2", "log2_fold_change": 1.0},
        {"gene_symbol": "G3", "log2_fold_change": 1.0},
    ]
    cohort = NS(results=[
        NS(gene_symbol=g, p_value=0.01 if g in {"G1", "G2", "G3"} else 0.5,
           log2_fold_change=1.0) for g in ["G1", "G2", "G3", "G4"]])
    gate = create_replication_gate(min_replicated=2, min_fraction=0.4)
    v = gate.assess_independent_cohort(
        discovery_top, np.zeros((4, 4)), ["G1", "G2", "G3", "G4"],
        np.array([0, 0, 1, 1]), lambda *a, **k: cohort, cohort_id="GSE42568")
    assert v.method == "independent_cohort"
    assert v.replicated is True
    assert v.n_replicated == 3


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
