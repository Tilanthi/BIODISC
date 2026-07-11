"""Phase 4 — concrete EvolutionTasks for the distributed runner.

P4.2 (bootstrapping analog): ``make_normalization_task`` targets a BIODISC
pipeline COMPONENT (a preprocessing normalizer) rather than a DE method — the
same loop, a different contract — mirroring how AlphaEvolve optimizes pieces of
its own infrastructure. ``make_de_method_task`` wraps the Phase-1 target so the
distributed runner is provably general.
"""
from typing import Callable

import numpy as np
from scipy import stats

from biodisc_core.fixed_pipeline.benchmark import score_de_method
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore, _auroc
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import BenchmarkCase

from .distributed import EvolutionTask
from .prompt_sampler import SYSTEM_PROMPT as _DE_SYSTEM
from .seeds import get_seed_program


def _compile_entry(source: str, entry_name: str) -> Callable:
    """Exec source and return the callable named ``entry_name``."""
    namespace: dict = {"np": np, "__name__": "evolution_task"}
    exec(compile(source, "<task_program>", "exec"), namespace)  # noqa: S102
    fn = namespace.get(entry_name)
    if not callable(fn):
        raise ValueError(f"source does not define callable `{entry_name}`")
    return fn


def _zero() -> DEMethodScore:
    return DEMethodScore(auroc=0.0, replicate_concordance=0.0, aggregate=0.0)


def make_de_method_task(benchmark: BenchmarkCase) -> EvolutionTask:
    """The Phase-1 target (a DE scoring method) as an EvolutionTask."""

    def fitness(source: str) -> DEMethodScore:
        try:
            from .program import compile_de_program
            fn = compile_de_program(source)
            return score_de_method(fn, benchmark)
        except Exception:
            return _zero()

    return EvolutionTask(
        name="de_method",
        seed_source=get_seed_program(),
        entry_name="score",
        system_prompt=_DE_SYSTEM,
        fitness_fn=fitness,
        prompt_hints=(
            "Try a more robust statistic (Welch, rank-based, moderated).",
            "Combine effect size and significance.",
            "Improve numerical stability.",
            "Make a minimal, surgical change.",
        ),
    )


# --- P4.2 bootstrap: evolve a pipeline COMPONENT (a normalizer) ---

NORMALIZER_SYSTEM = """\
You are an evolutionary coding agent improving a preprocessing NORMALIZER for
gene-expression data, a component of the analysis pipeline.

CONTRACT (a valid program MUST satisfy):
- define `def normalize(expression)`
- expression: np.ndarray shape (n_genes, n_samples)
- return an np.ndarray of the SAME shape, normalized
- you may `import numpy as np` inside the function

FITNESS = downstream DE quality. After your normalization, a fixed Student's
t-test ranks genes; the score is how well those rankings recover truly-DE genes.
Optimize the normalizer so downstream DE is more accurate. Do NOT hard-code gene
indices or peek at labels (the normalizer is unsupervised).

OUTPUT FORMAT — return ONLY search-and-replace diffs:
<<< SEARCH
exact lines to replace (verbatim)
===
replacement lines
>>> REPLACE
Multiple blocks allowed; full rewrites emit the entire `def normalize`.
"""

_SEED_NORMALIZER = '''\
import numpy as np


def normalize(expression):
    """Per-gene z-score (standardize each gene across samples). SEED."""
    mean = expression.mean(axis=1, keepdims=True)
    std = expression.std(axis=1, keepdims=True)
    std = np.where(std == 0, 1.0, std)
    return (expression - mean) / std
'''


def _ttest_abs_scores(expression, labels) -> np.ndarray:
    treat = labels == 1
    ctrl = labels == 0
    n = expression.shape[0]
    out = np.zeros(n)
    for i in range(n):
        t, _ = stats.ttest_ind(expression[i, treat], expression[i, ctrl])
        out[i] = abs(t) if t == t else 0.0
    return out


def make_normalization_task(benchmark: BenchmarkCase) -> EvolutionTask:
    """Bootstrap target: a normalizer scored by downstream DE AUROC.

    NOTE on headroom: on Gaussian benchmark data a fixed t-test is largely
    scale-invariant per gene, so per-gene linear normalization yields little
    AUROC change. The task exists to PROVE the distributed runner generalizes to
    a pipeline-component contract (entry_name='normalize'); finding a genuinely
    better normalizer requires heavy-tailed / count-distribution benchmarks.
    """

    def fitness(source: str) -> DEMethodScore:
        try:
            fn = _compile_entry(source, "normalize")
            normalized = np.asarray(fn(benchmark.expression), dtype=float)
            if normalized.shape != benchmark.expression.shape:
                return _zero()
            scores = _ttest_abs_scores(normalized, benchmark.labels)
            auroc = _auroc(scores, benchmark.truth_de_indices, benchmark.n_genes)
            # Single-benchmark score (no held-out for this bootstrap demo).
            return DEMethodScore(auroc=auroc, replicate_concordance=auroc, aggregate=auroc)
        except Exception:
            return _zero()

    return EvolutionTask(
        name="normalizer",
        seed_source=_SEED_NORMALIZER,
        entry_name="normalize",
        system_prompt=NORMALIZER_SYSTEM,
        fitness_fn=fitness,
        prompt_hints=(
            "Try a variance-stabilizing or non-linear transform.",
            "Try quantile or rank-based normalization.",
            "Robustly center genes (median / MAD).",
            "Make a surgical change.",
        ),
    )
