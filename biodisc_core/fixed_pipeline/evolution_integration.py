"""Supervised integration of the AlphaEvolve-style evolution system.

This is the "switch on" for BIODISC's already-built evolutionary method-discovery
loop (``biodisc_core/evolution/``) — previously orphaned. It exposes that loop as
a recognized, on-demand capability of the canonical discovery system.

HONEST SCOPE (do not overstate):
  * The evolution loop optimises DIFFERENTIAL-EXPRESSION *methods* (code that
    emits quantitative claims) against BENCHMARK truth-known data — a signal with
    objective ground truth. That is exactly the trustworthy automated evaluator
    AlphaEvolve requires.
  * Fitness = REPLICATION on an independent cohort + precision (AUROC). Validation
    is a hard gate, never a fitness component (we do not train the model to fool
    the validator). See ``evolution/replication.py``.
  * Outputs are METHODS, not biological discoveries. Promoted methods carry full
    genealogy and pass a publication gate; they are written to the evolution
    Phase-3 provenance log (``evolution/publication.py``), NOT to the discovery
    store — so they never masquerade as findings.
  * This is a SUPERVISED, on-demand capability (human triggers it; human approves
    publication). It is intentionally NOT part of the always-on real-data loop,
    which runs the fixed pipeline against real GEO data through the chokepoint.

REMAINING WORK (not done here): the real-cohort evaluator hook
(``score_de_method_on_real``) is still a stub. Evolving directly on real cohort
data requires that hook + a trustworthy per-cohort ground-truth proxy. Until then,
evolution runs on benchmarks only — no claim of biological truth, only of better
methods.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Optional

from biodisc_core.evolution.discovery_controller import DiscoveryEvolutionController
from biodisc_core.evolution.llm_ensemble import LLMEnsemble
from biodisc_core.evolution.replication import make_replication_pair

logger = logging.getLogger(__name__)


@dataclass
class EvolutionRunResult:
    ran: bool
    reason: str = ""
    seed_aggregate: Optional[float] = None
    best_aggregate: Optional[float] = None
    best_replication: Optional[float] = None
    best_precision: Optional[float] = None
    accepted: int = 0
    rejected: int = 0
    genealogy_size: int = 0
    publication_decision: str = ""
    publication_written: bool = False
    error: Optional[str] = field(default=None, repr=False)


def run_method_evolution(
    generations: int = 3,
    attempts_per_generation: int = 2,
    n_genes: int = 300,
    n_samples: int = 30,
    n_de: int = 30,
    effect_size: float = 1.2,
    noise: str = "gaussian",
    seed: int = 3,
    model: Optional[str] = None,
    publish: bool = False,
) -> EvolutionRunResult:
    """Run one supervised method-evolution episode on benchmark truth-known data.

    ``publish=False`` (default) is a DRY RUN: the publication gate is evaluated
    but nothing is written. ``publish=True`` exercises human approval and writes
    the provenance record ONLY if the gate is met.
    """
    logger.info("🧬 supervised method-evolution episode starting (benchmark ground truth)")
    try:
        pair = make_replication_pair(
            n_genes=n_genes, n_samples=n_samples, n_de=n_de,
            seed=seed, effect_size=effect_size, noise=noise,
        )
        ensemble = LLMEnsemble(models=[model] if model else None)
        rng = random.Random(7)
        ctrl = DiscoveryEvolutionController(pair, ensemble.propose, rng=rng)

        logger.info("seed aggregate=%.3f (replication=%.3f precision=%.3f)",
                    ctrl.seed_score.aggregate, ctrl.seed_score.replication_rate,
                    ctrl.seed_score.precision)

        best = ctrl.run(generations=generations, attempts_per_generation=attempts_per_generation)
        accepted = sum(1 for a in ctrl.attempts if a.accepted)

        record, score, decision, _ = ctrl.publish_best(human_approved=publish)

        logger.info("evolution complete: best aggregate=%.3f (replication=%.3f precision=%.3f); "
                    "publication=%s written=%s",
                    best.aggregate, best.replicate_concordance, best.auroc,
                    decision.decision, record.written)

        return EvolutionRunResult(
            ran=True,
            reason="method-evolution episode completed on benchmark data",
            seed_aggregate=round(ctrl.seed_score.aggregate, 4),
            best_aggregate=round(best.aggregate, 4),
            best_replication=round(best.replicate_concordance, 4),
            best_precision=round(best.auroc, 4),
            accepted=accepted,
            rejected=len(ctrl.attempts) - accepted,
            genealogy_size=len(ctrl.db.all_programs()),
            publication_decision=str(decision.decision),
            publication_written=bool(record.written),
        )
    except Exception as e:  # noqa: BLE001 - supervised run must report, not crash the caller
        logger.error("method-evolution episode failed: %s", e)
        return EvolutionRunResult(ran=False, reason="episode failed", error=f"{type(e).__name__}: {e}")


__all__ = ["run_method_evolution", "EvolutionRunResult"]


if __name__ == "__main__":
    import argparse
    import json
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(description="Supervised method-evolution (AlphaEvolve-style) on benchmarks.")
    p.add_argument("--generations", type=int, default=3)
    p.add_argument("--attempts", type=int, default=2)
    p.add_argument("--publish", action="store_true", help="human-approved publish of an eligible evolved method")
    p.add_argument("--model", default=None)
    args = p.parse_args()

    result = run_method_evolution(
        generations=args.generations, attempts_per_generation=args.attempts,
        publish=args.publish, model=args.model,
    )
    print(json.dumps(result.__dict__, indent=2))
    sys.exit(0 if result.ran else 1)
