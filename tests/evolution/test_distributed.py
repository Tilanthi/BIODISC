"""P4.1 + P4.2 + P4.3 — distributed runner, task generality, distillation."""
import importlib.util
import time

import pytest

from biodisc_core.evolution.distributed import DistributedEvolutionRunner
from biodisc_core.evolution.tasks import (
    make_de_method_task, make_normalization_task,
)
from biodisc_core.evolution.distill import distill_program
from biodisc_core.evolution.seeds import get_seed_program
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


def _benchmark():
    return make_de_benchmark(n_genes=200, n_samples=24, n_de=20, seed=1,
                             effect_size=1.0, noise="gaussian")


# --- task generality (P4.2) ---

def test_de_method_task_seed_scores_positive():
    task = make_de_method_task(_benchmark())
    s = task.fitness_fn(task.seed_source)
    assert s.aggregate > 0.0


def test_normalization_task_seed_scores_positive():
    task = make_normalization_task(_benchmark())
    s = task.fitness_fn(task.seed_source)
    assert 0.0 <= s.aggregate <= 1.0


def test_normalization_task_rejects_invalid_source():
    task = make_normalization_task(_benchmark())
    assert task.fitness_fn("def normalize(e):\n    return oops  # syntax ok but NameError").aggregate == 0.0


# --- runner: thread-safety + completion (P4.1) ---

def test_runner_runs_concurrently_without_corruption():
    bench = _benchmark()
    task = make_de_method_task(bench)
    proposer = lambda s, u: get_seed_program()  # noqa: E731
    runner = DistributedEvolutionRunner(task, proposer, n_workers=4, seed=0)
    metrics = runner.run(total_steps=12, generation=1)
    assert metrics.steps == 12
    assert metrics.n_workers == 4
    assert runner.best() is not None
    assert runner.best().aggregate > 0.0


# --- runner: near-linear scaling with workers (Phase 4 exit test) ---

def _slow_proposer(delay):
    def _p(system, user):
        time.sleep(delay)            # simulate LLM round-trip (I/O-bound)
        return get_seed_program()
    return _p


def test_throughput_scales_with_workers():
    # Isolate the runner's I/O concurrency: an instant-fitness task so the only
    # per-step cost is the simulated LLM round-trip. Real GLM calls (~1-3s)
    # dominate the ~0.1s CPU eval, so I/O scaling is what matters in practice.
    from biodisc_core.evolution.distributed import EvolutionTask
    from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore

    trivial = EvolutionTask(
        name="trivial",
        seed_source="def score(e, l):\n    return e.sum(axis=1)\n",
        entry_name="score",
        system_prompt="x",
        fitness_fn=lambda src: DEMethodScore(auroc=0.5, replicate_concordance=0.5, aggregate=0.5),
    )
    r1 = DistributedEvolutionRunner(trivial, _slow_proposer(0.25), n_workers=1, seed=0)
    m1 = r1.run(total_steps=8, generation=1)
    r4 = DistributedEvolutionRunner(trivial, _slow_proposer(0.25), n_workers=4, seed=0)
    m4 = r4.run(total_steps=8, generation=1)

    speedup = m4.throughput / m1.throughput
    assert speedup > 2.5, (
        f"expected near-linear I/O scaling 1->4 workers: "
        f"1w={m1.throughput:.2f}/s 4w={m4.throughput:.2f}/s (speedup {speedup:.2f}x)"
    )


# --- normalizer task runs through the distributed runner (P4.2 end-to-end) ---

def test_normalizer_task_runs_on_distributed_runner():
    from biodisc_core.evolution.tasks import _SEED_NORMALIZER
    bench = _benchmark()
    task = make_normalization_task(bench)
    proposer = lambda s, u: _SEED_NORMALIZER  # noqa: E731
    runner = DistributedEvolutionRunner(task, proposer, n_workers=2, seed=0)
    metrics = runner.run(total_steps=4, generation=1)
    assert metrics.steps == 4
    assert runner.best().aggregate > 0.0


# --- distillation (P4.3) ---

def test_distill_writes_importable_module(tmp_path):
    src = get_seed_program()
    path = distill_program(src, "de_method_win", out_dir=str(tmp_path))
    assert path.endswith("de_method_win.py")
    spec = importlib.util.spec_from_file_location("de_method_win", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.score)
