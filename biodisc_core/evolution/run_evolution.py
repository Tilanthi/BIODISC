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
from .program_db import ProgramDatabase, IslandModel, method_family


def _diversity_report(genealogy) -> str:
    """Summarize behavioral diversity of archived programs (Phase 2 metric)."""
    families = {method_family(p.source) for p in genealogy}
    cells = {(p.bucket, p.family) for p in genealogy}
    return (f"{len(genealogy)} programs, {len(families)} method families "
            f"({sorted(families)}), {len(cells)} (complexity,family) niches")


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
    parser.add_argument("--islands", type=int, default=3,
                        help="0 = single MAP-Elites archive; >0 = N islands with migration")
    parser.add_argument("--migration-interval", type=int, default=5)
    parser.add_argument("--cascade", action="store_true",
                        help="enable the evaluation cascade (cheap screen -> full)")
    parser.add_argument("--screen-floor", type=float, default=0.55)
    args = parser.parse_args(argv)

    case = make_de_benchmark(
        n_genes=args.n_genes, n_samples=args.n_samples, n_de=args.n_de,
        seed=args.seed, effect_size=args.effect_size, noise=args.noise,
    )

    models = [args.model] if args.model else None
    ensemble = LLMEnsemble(models=models, max_tokens=args.max_tokens)
    db = (
        IslandModel(n_islands=args.islands, migration_interval=args.migration_interval,
                    complexity_per_bucket=25)
        if args.islands > 0
        else ProgramDatabase(complexity_per_bucket=25)
    )
    print(f"[run_evolution] model={ensemble.last_model or ensemble.models} "
          f"benchmark=noise:{args.noise} n_samples:{args.n_samples} "
          f"effect:{args.effect_size}")
    print(f"[run_evolution] generations={args.generations} attempts/gen={args.attempts} "
          f"islands={args.islands or 'single'} cascade={args.cascade}")

    rng = random.Random(123)
    ctrl = EvolutionController(
        case, ensemble.propose, db=db, rng=rng,
        use_cascade=args.cascade, screen_floor=args.screen_floor,
    )
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
    print(f"diversity        = {_diversity_report(result.genealogy)}")
    best_meta = ctrl.meta_archive.best()
    if best_meta is not None:
        print(f"best meta-prompt = {best_meta.text!r} (mean agg {best_meta.mean_aggregate:.3f}, "
              f"n={best_meta.n_uses})")

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
