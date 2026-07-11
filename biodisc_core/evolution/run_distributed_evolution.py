"""Run real LLM-driven DISTRIBUTED evolution (Phase 4).

Spins up N worker threads sharing one archive and runs an EvolutionTask
concurrently against the configured LLM gateway (GLM via z.ai here). Prints
throughput/accept metrics and the best aggregate, and optionally distills the
winner to evolution/distilled/.

Usage:
    python -m biodisc_core.evolution.run_distributed_evolution \
        --task de_method --workers 3 --steps 6
"""
import argparse
import sys

from biodisc_core.evolution.distributed import DistributedEvolutionRunner
from biodisc_core.evolution.tasks import make_de_method_task, make_normalization_task
from biodisc_core.evolution.llm_ensemble import LLMEnsemble
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Distributed LLM evolution.")
    p.add_argument("--task", choices=["de_method", "normalizer"], default="de_method")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--steps", type=int, default=6)
    p.add_argument("--noise", default="heteroscedastic",
                   choices=["gaussian", "heavy_tail", "heteroscedastic"])
    p.add_argument("--n-genes", type=int, default=300)
    p.add_argument("--n-samples", type=int, default=24)
    p.add_argument("--n-de", type=int, default=30)
    p.add_argument("--effect-size", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--model", default=None)
    p.add_argument("--distill", action="store_true", help="distill the winner to a module")
    args = p.parse_args(argv)

    bench = make_de_benchmark(
        n_genes=args.n_genes, n_samples=args.n_samples, n_de=args.n_de,
        seed=args.seed, effect_size=args.effect_size, noise=args.noise,
    )
    task = make_de_method_task(bench) if args.task == "de_method" else make_normalization_task(bench)
    ensemble = LLMEnsemble(models=[args.model] if args.model else None)

    runner = DistributedEvolutionRunner(task, ensemble.propose, n_workers=args.workers, seed=args.seed)
    seed_agg = task.fitness_fn(task.seed_source).aggregate
    print(f"[distributed] model={ensemble.models} task={args.task} workers={args.workers} "
          f"steps={args.steps} noise={args.noise}")
    print(f"[distributed] seed aggregate={seed_agg:.3f}")

    metrics = runner.run(total_steps=args.steps, generation=1)
    print("\n=== DISTRIBUTED RUN COMPLETE ===")
    print(f"steps={metrics.steps} accepted={metrics.accepted} rejected={metrics.rejected} "
          f"accept_rate={metrics.accept_rate:.2f}")
    print(f"elapsed={metrics.elapsed_seconds:.2f}s throughput={metrics.throughput:.2f} steps/s "
          f"(~{metrics.throughput/args.workers:.2f} steps/s per worker)")
    print(f"best aggregate={metrics.best_aggregate:.3f}  genealogy={len(runner.all_programs())} programs")

    if args.distill and runner.best() is not None:
        from biodisc_core.evolution.distill import distill_program
        path = distill_program(runner.best().source, f"{args.task}_win")
        print(f"[distributed] distilled winner -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
