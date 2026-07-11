"""Run real LLM-driven DISCOVERY evolution (Phase 3) and publish with provenance.

Evolves discovery programs (code emitting quantitative DE claims) toward
REPLICATION fitness, then runs the publication gate. By default the publish is a
DRY RUN (human_approved=False); pass --publish to exercise human approval and
write the provenance record to the Phase-3 log.

Usage:
    python -m biodisc_core.evolution.run_discovery_evolution --generations 3
"""
import argparse
import random
import sys

from biodisc_core.evolution.discovery_controller import DiscoveryEvolutionController
from biodisc_core.evolution.llm_ensemble import LLMEnsemble
from biodisc_core.evolution.replication import make_replication_pair


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Evolve discovery programs with an LLM.")
    p.add_argument("--generations", type=int, default=3)
    p.add_argument("--attempts", type=int, default=2)
    p.add_argument("--n-genes", type=int, default=300)
    p.add_argument("--n-samples", type=int, default=30)
    p.add_argument("--n-de", type=int, default=30)
    p.add_argument("--effect-size", type=float, default=1.2)
    p.add_argument("--noise", default="gaussian", choices=["gaussian", "heavy_tail", "heteroscedastic"])
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--model", default=None)
    p.add_argument("--publish", action="store_true",
                   help="exercise human approval: write the provenance record if eligible")
    args = p.parse_args(argv)

    pair = make_replication_pair(
        n_genes=args.n_genes, n_samples=args.n_samples, n_de=args.n_de,
        seed=args.seed, effect_size=args.effect_size, noise=args.noise,
    )
    ensemble = LLMEnsemble(models=[args.model] if args.model else None)
    rng = random.Random(7)
    ctrl = DiscoveryEvolutionController(pair, ensemble.propose, rng=rng)

    print(f"[discovery] model={ensemble.models} pair=noise:{args.noise} "
          f"effect:{args.effect_size} gens={args.generations} attempts/gen={args.attempts}")
    print(f"[discovery] seed replication_rate={ctrl.seed_score.replication_rate:.3f} "
          f"precision={ctrl.seed_score.precision:.3f} agg={ctrl.seed_score.aggregate:.3f}")

    best = ctrl.run(generations=args.generations, attempts_per_generation=args.attempts)

    accepted = sum(1 for a in ctrl.attempts if a.accepted)
    print("\n=== DISCOVERY EVOLUTION COMPLETE ===")
    print(f"attempts: {accepted} accepted, {len(ctrl.attempts)-accepted} rejected")
    print(f"best aggregate = {best.aggregate:.3f} "
          f"(replication={best.replicate_concordance:.3f}, precision={best.auroc:.3f})")
    print(f"genealogy: {len(ctrl.db.all_programs())} programs")

    record, score, decision, _ = ctrl.publish_best(human_approved=args.publish)
    print(f"\n=== PUBLICATION GATE ===")
    print(f"decision        = {decision.decision} ({decision.reason})")
    print(f"replication_rate= {score.replication_rate:.3f}  precision={score.precision:.3f}  "
          f"n_claims={score.n_claims}")
    print(f"human_approved  = {args.publish}  -> written={record.written}")
    if args.publish and record.written:
        from biodisc_core.evolution.publication import DEFAULT_PUBLICATION_LOG
        print(f"provenance written to {DEFAULT_PUBLICATION_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
