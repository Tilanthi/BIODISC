"""Evaluation cascade (AlphaEvolve §2.3).

Most LLM-proposed diffs are bad (broken, worse, or no-ops). Running the full
benchmark on every candidate wastes compute. The cascade:

    1. compile + validate (hard gate — rejects broken source)
    2. CHEAP SCREEN: score on a small fast sub-benchmark; if below a floor,
       reject immediately without paying for the full evaluation
    3. FULL evaluation: score_de_method on the real benchmark (which itself
       includes the held-out replicate)

Returns None when the candidate is pruned at the screen; otherwise the full
DEMethodScore. The screen benchmark is independent (different seed) so passing
it is weak evidence of generalization, not memorization.
"""
from typing import Optional

from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark, score_de_method
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import BenchmarkCase

from .program import compile_de_program

SCREEN_SEED_OFFSET = 5000


def make_screen_case(full_case: BenchmarkCase, n_genes_screen: int = 120) -> BenchmarkCase:
    """A smaller, independent benchmark for the cheap screen stage."""
    n_genes = min(n_genes_screen, full_case.n_genes)
    n_de = max(2, round(full_case.n_de * n_genes / full_case.n_genes))
    return make_de_benchmark(
        n_genes=n_genes,
        n_samples=full_case.n_samples,
        n_de=n_de,
        seed=full_case.seed + SCREEN_SEED_OFFSET,
        effect_size=full_case.effect_size,
        noise=full_case.noise,
    )


def cascade_evaluate(
    source: str,
    full_case: BenchmarkCase,
    screen_floor: float = 0.55,
    n_genes_screen: int = 120,
) -> Optional[DEMethodScore]:
    """Evaluate a candidate through the screen->full cascade.

    Returns None if the candidate is pruned at the screen (aggregate < floor),
    else the full DEMethodScore.
    """
    fn = compile_de_program(source)
    screen = score_de_method(fn, make_screen_case(full_case, n_genes_screen))
    if screen.aggregate < screen_floor:
        return None
    return score_de_method(fn, full_case)
