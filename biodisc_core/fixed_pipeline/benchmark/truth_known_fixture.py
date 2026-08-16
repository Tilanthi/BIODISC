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
"""Truth-known benchmark generator for differential-expression methods.

This is BENCHMARK DATA WITH A KNOWN ANSWER, not discovery data. We control
which genes are truly differentially expressed so a DE method can be scored
against ground truth (AUROC). See package docstring.
"""
from dataclasses import dataclass, field
from typing import Iterable, Optional, Set

import numpy as np


@dataclass
class BenchmarkCase:
    """A truth-known differential-expression benchmark case."""
    expression: np.ndarray          # shape (n_genes, n_samples), log2-scale
    labels: np.ndarray              # shape (n_samples,), 0 = control, 1 = treatment
    truth_de_indices: Set[int]      # indices of truly differentially expressed genes
    n_genes: int
    n_samples: int
    n_de: int
    seed: int
    effect_size: float = 1.5        # log2 fold-change added to treatment group
    noise: str = "gaussian"         # noise regime: gaussian|heavy_tail|heteroscedastic


# Valid noise regimes for make_de_benchmark.
NOISE_GAUSSIAN = "gaussian"
NOISE_HEAVY_TAIL = "heavy_tail"          # Student-t (df=3) — outliers hurt t-test
NOISE_HETEROSCEDASTIC = "heteroscedastic"  # treatment group has ~3x variance
VALID_NOISES = (NOISE_GAUSSIAN, NOISE_HEAVY_TAIL, NOISE_HETEROSCEDASTIC)


def make_de_benchmark(
    n_genes: int = 500,
    n_samples: int = 40,
    n_de: int = 50,
    seed: int = 0,
    effect_size: float = 1.5,
    noise: str = NOISE_GAUSSIAN,
    truth_indices: Optional[Iterable[int]] = None,
) -> BenchmarkCase:
    """Generate a truth-known DE benchmark deterministically from ``seed``.

    Args:
        n_genes: number of genes (features).
        n_samples: total samples (split evenly between control/treatment).
        n_de: number of truly differentially expressed genes.
        seed: RNG seed (deterministic).
        effect_size: log2 fold-change added to the treatment group for DE genes.
        noise: noise regime. 'gaussian' (easy; t-test near-perfect),
            'heavy_tail' (Student-t df=3, outliers), or 'heteroscedastic'
            (treatment group ~3x variance). The non-gaussian regimes are HARD:
            naive Student's t-test is suboptimal, leaving headroom for evolution
            to discover more robust statistics (Welch, rank-based, moderated).
        truth_indices: optional fixed set of DE gene indices. When provided,
            the SAME truth is used (only expression noise depends on ``seed``).
            This lets two cohorts share ground truth with independent draws —
            the basis of replication-pair scoring (Phase 3). n_de is ignored.

    Returns:
        BenchmarkCase with known ``truth_de_indices``.
    """
    if noise not in VALID_NOISES:
        raise ValueError(f"noise must be one of {VALID_NOISES}, got {noise!r}")
    if n_samples < 4:
        raise ValueError("n_samples must be >= 4 (need >=2 per group)")

    rng = np.random.default_rng(seed)

    # Even, non-fabricated group assignment: first half control, second half
    # treatment. This is legitimate here because WE generate the data and the
    # group assignment is the controlled ground truth, not an inferred design.
    labels = np.zeros(n_samples, dtype=int)
    labels[n_samples // 2:] = 1
    control_mask = labels == 0
    treatment_mask = labels == 1

    expression = np.zeros((n_genes, n_samples), dtype=float)
    for mask in (control_mask, treatment_mask):
        n_grp = int(mask.sum())
        if noise == NOISE_GAUSSIAN:
            expression[:, mask] = rng.normal(0.0, 1.0, size=(n_genes, n_grp))
        elif noise == NOISE_HEAVY_TAIL:
            # Student-t df=3: heavy tails => outliers that inflate pooled variance
            expression[:, mask] = rng.standard_t(3, size=(n_genes, n_grp))
        else:  # heteroscedastic
            scale = 1.0 if mask is control_mask else (3.0 ** 0.5)
            expression[:, mask] = rng.normal(0.0, scale, size=(n_genes, n_grp))

    # Choose which genes are truly DE, add the effect to the treatment group.
    if truth_indices is not None:
        de_idx = np.array(sorted(set(int(i) for i in truth_indices)), dtype=int)
        if len(de_idx) == 0 or de_idx.max() >= n_genes or de_idx.min() < 0:
            raise ValueError("truth_indices must be non-empty and within [0, n_genes)")
        n_de = len(de_idx)
    else:
        if n_de > n_genes:
            raise ValueError(f"n_de ({n_de}) cannot exceed n_genes ({n_genes})")
        de_idx = rng.choice(n_genes, size=n_de, replace=False)
    expression[np.ix_(de_idx, treatment_mask)] += effect_size

    return BenchmarkCase(
        expression=expression,
        labels=labels,
        truth_de_indices=set(int(i) for i in de_idx),
        n_genes=n_genes,
        n_samples=n_samples,
        n_de=n_de,
        seed=seed,
        effect_size=effect_size,
        noise=noise,
    )
