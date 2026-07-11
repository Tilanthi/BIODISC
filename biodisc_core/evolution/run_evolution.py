"""Run real LLM-driven DE-method evolution (AlphaEvolve-style).

Uses the configured Anthropic-compatible gateway — here GLM via z.ai
(ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN), no Anthropic key required.
Override the model with BIODISC_EVOLUTION_MODEL.

Usage:
    python -m biodisc_core.evolution.run_evolution --generations 4 --attempts 2

Writes the best evolved program + genealogy JSON to
biodisc_core/evolution/runs/<timestamp>/.
"""
import argparse
import json
import os
import random
import sys
from datetime import datetime

from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark

from .controller import EvolutionController
from .llm_ensemble import LLMEnsemble


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evolve a DE method with an LLM.")
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--attempts", type=int, default=2, help="attempts per generation")
    parser.add_argument("--noise", default="heteroscedastic",
                        choices=["gaussian", "heavy_tail", "heteroscedastic"])
    parser.add_argument("--n-genes", type=int, default=400)
    parser.add_argument("--n-samples", type=int, default=24)
    parser.add_argument("--n-de", type=int, default=40)
    parser.add_argument("--effect-size", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--model", default=None, help="override model id")
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args(argv)

    case = make_de_benchmark(
        n_genes=args.n_genes, n_samples=args.n_samples, n_de=args.n_de,
        seed=args.seed, effect_size=args.effect_size, noise=args.noise,
    )

    models = [args.model] if args.model else None
    ensemble = LLMEnsemble(models=models, max_tokens=args.max_tokens)
    print(f"[run_evolution] model={ensemble.last_model or ensemble.models} "
          f"benchmark=noise:{args.noise} n_samples:{args.n_samples} "
          f"effect:{args.effect_size}")
    print(f"[run_evolution] generations={args.generations} attempts/gen={args.attempts}")

    rng = random.Random(123)
    ctrl = EvolutionController(case, ensemble.propose, rng=rng)
    print(f"[run_evolution] seed aggregate = {ctrl.seed_score.aggregate:.4f} "
          f"(auroc={ctrl.seed_score.auroc:.3f}, "
          f"replicate={ctrl.seed_score.replicate_concordance:.3f})")

    result = ctrl.run(generations=args.generations, attempts_per_generation=args.attempts)

    accepted = [a for a in result.attempts if a.accepted]
    rejected = [a for a in result.attempts if not a.accepted]
    print("\n=== EVOLUTION COMPLETE ===")
    print(f"attempts: {len(accepted)} accepted, {len(rejected)} rejected")
    print(f"seed aggregate   = {result.seed_score.aggregate:.4f}")
    print(f"best aggregate   = {result.best_score.aggregate:.4f} "
          f"(auroc={result.best_score.auroc:.3f}, "
          f"replicate={result.best_score.replicate_concordance:.3f})")
    print(f"improvement      = {result.improvement:+.4f}")
    print(f"genealogy: {len(result.genealogy)} archived programs")

    # Persist artifacts.
    stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(os.path.dirname(__file__), "runs", stamp)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "best_program.py"), "w") as f:
        f.write(result.best_source)
    with open(os.path.join(out_dir, "genealogy.json"), "w") as f:
        json.dump({
            "model": ensemble.models,
            "benchmark": {"noise": args.noise, "n_samples": args.n_samples,
                          "n_genes": args.n_genes, "n_de": args.n_de,
                          "effect_size": args.effect_size, "seed": args.seed},
            "seed_aggregate": result.seed_score.aggregate,
            "best_aggregate": result.best_score.aggregate,
            "improvement": result.improvement,
            "genealogy": [
                {"gen": g.generation, "id": g.program_id, "parent": g.parent_id,
                 "aggregate": g.aggregate, "auroc": g.auroc,
                 "replicate": g.replicate_concordance, "complexity": g.complexity,
                 "bucket": g.bucket}
                for g in result.genealogy
            ],
            "attempts": [a.__dict__ for a in result.attempts],
        }, f, indent=2)
    print(f"[run_evolution] artifacts written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
