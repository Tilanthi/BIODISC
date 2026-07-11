"""Truth-known benchmark generator for differential-expression methods.

This is BENCHMARK DATA WITH A KNOWN ANSWER, not discovery data. We control
which genes are truly differentially expressed so a DE method can be scored
against ground truth (AUROC). See package docstring.
"""
from dataclasses import dataclass, field
from typing import Set

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


def make_de_benchmark(
    n_genes: int = 500,
    n_samples: int = 40,
    n_de: int = 50,
    seed: int = 0,
    effect_size: float = 1.5,
) -> BenchmarkCase:
    """Generate a truth-known DE benchmark deterministically from ``seed``.

    Args:
        n_genes: number of genes (features).
        n_samples: total samples (split evenly between control/treatment).
        n_de: number of truly differentially expressed genes.
        seed: RNG seed (deterministic).
        effect_size: log2 fold-change added to the treatment group for DE genes.

    Returns:
        BenchmarkCase with known ``truth_de_indices``.
    """
    rng = np.random.default_rng(seed)

    if n_de > n_genes:
        raise ValueError(f"n_de ({n_de}) cannot exceed n_genes ({n_genes})")
    if n_samples < 4:
        raise ValueError("n_samples must be >= 4 (need >=2 per group)")

    # Baseline log2 expression ~ N(0, 1) for all genes/samples.
    expression = rng.normal(0.0, 1.0, size=(n_genes, n_samples))

    # Even, non-fabricated group assignment: first half control, second half
    # treatment. This is legitimate here because WE generate the data and the
    # group assignment is the controlled ground truth, not an inferred design.
    labels = np.zeros(n_samples, dtype=int)
    labels[n_samples // 2:] = 1

    # Choose which genes are truly DE, add the effect to the treatment group.
    de_idx = rng.choice(n_genes, size=n_de, replace=False)
    treatment_mask = labels == 1
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
    )
