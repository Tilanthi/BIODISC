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
"""Phase 4 — distributed asynchronous evolution controller (AlphaEvolve §2.5).

N worker threads share ONE program database + meta-prompt archive and each run
the sample -> propose -> apply -> evaluate -> add loop concurrently. Because the
proposer is an I/O-bound LLM call (the slow part) and the shared DB is touched
only briefly under a lock, workers run effectively in parallel during the
network wait — linear speedup in the number of workers (the Phase 4 exit test).

Thread-safety: a coarse ``_Locked`` proxy serializes only the quick DB/meta
operations; the long proposer call happens with no lock held. Each worker has
its own RNG (Python's Random is not thread-safe).

Generality: the runner is driven by an ``EvolutionTask`` (seed source, entry
name, system prompt, fitness fn) so it can target DE methods (Phase 1),
discovery programs (Phase 3), or pipeline components like a normalizer (P4.2).
"""
import functools
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore

from .diff_applier import apply_diffs_or_full, DiffApplyError, DiffParseError
from .meta_prompt import MetaPromptArchive
from .program import validate_program_source
from .program_db import ArchivedProgram, ProgramDatabase


class _Locked:
    """Coarse-lock proxy: serializes every method call on the wrapped object."""

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_lock", threading.RLock())

    def __getattr__(self, name):
        attr = getattr(self._obj, name)
        if callable(attr):
            lock = self._lock

            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                with lock:
                    return attr(*args, **kwargs)
            return wrapper
        return attr


@dataclass
class EvolutionTask:
    """A target for evolution. The runner is agnostic to which task it runs."""
    name: str
    seed_source: str
    entry_name: str                                   # 'score' | 'discover' | 'normalize'
    system_prompt: str
    fitness_fn: Callable[[str], DEMethodScore]        # source -> DEMethodScore (agg 0 if invalid)
    prompt_hints: Tuple[str, ...] = ()
    max_inspirations: int = 3


@dataclass
class RunMetrics:
    n_workers: int
    steps: int
    accepted: int
    rejected: int
    elapsed_seconds: float
    throughput: float            # steps per second
    best_aggregate: float

    @property
    def accept_rate(self) -> float:
        return self.accepted / self.steps if self.steps else 0.0


def _build_task_user_prompt(task, parent, inspirations, generation, rng, meta_prompt):
    hints = task.prompt_hints or ("Make a surgical change.",)
    lines = [
        f"=== GENERATION {generation} ===",
        f"Goal: improve aggregate fitness (currently {parent.aggregate:.3f}).",
        f"Strategy hint: {rng.choice(hints)}",
    ]
    if meta_prompt is not None:
        lines.append(f"Co-evolved guidance: {meta_prompt.text}")
    lines += ["", "=== CURRENT PROGRAM (parent) ===", parent.source.strip("\n")]
    if inspirations:
        lines += ["", "=== INSPIRATIONS ==="]
        for i, ins in enumerate(inspirations):
            lines.append(f"--- inspiration {i+1} (agg {ins.aggregate:.3f}) ---")
            lines.append(ins.source.strip("\n"))
    lines += ["", "Emit your improvement as diff blocks now."]
    return "\n".join(lines)


class DistributedEvolutionRunner:
    """Runs an EvolutionTask across N worker threads against a shared archive."""

    def __init__(
        self,
        task: EvolutionTask,
        proposer: Callable[[str, str], str],   # thread-safe (e.g. LLMEnsemble.propose)
        n_workers: int = 4,
        db: Optional[ProgramDatabase] = None,
        meta_archive: Optional[MetaPromptArchive] = None,
        seed: int = 0,
        use_meta: bool = True,
    ):
        self.task = task
        self.proposer = proposer
        self.n_workers = n_workers
        self.db = _Locked(db or ProgramDatabase(complexity_per_bucket=25))
        self.meta = _Locked(meta_archive or MetaPromptArchive(rng=random.Random(seed)))
        self.use_meta = use_meta
        self._master_seed = seed
        self._seed_archive()

    def _validate(self, source: str) -> bool:
        from .diff_applier import validate_program_entry
        return validate_program_entry(source, self.task.entry_name)

    def _seed_archive(self) -> DEMethodScore:
        score = self.task.fitness_fn(self.task.seed_source)
        if hasattr(self.db, "seed_all"):
            self.db.seed_all(self.task.seed_source, score, generation=0)
        else:
            self.db.add(self.task.seed_source, score, generation=0, parent_id=None)
        return score

    def _worker_step(self, worker_id: int, generation: int) -> bool:
        """One attempt. Returns True if accepted (scored > 0)."""
        rng = random.Random(self._master_seed + 1000 + worker_id + generation * 7919)
        try:
            parent, inspirations = self.db.sample()
        except Exception:
            return False
        meta = self.meta.sample() if self.use_meta else None
        user = _build_task_user_prompt(self.task, parent, inspirations, generation, rng, meta)

        try:
            raw = self.proposer(self.task.system_prompt, user)
        except Exception:
            return False
        try:
            child = apply_diffs_or_full(parent.source, raw, entry_name=self.task.entry_name)
        except (DiffParseError, DiffApplyError):
            return False
        if not self._validate(child):
            return False
        try:
            score = self.task.fitness_fn(child)
        except Exception:
            return False
        if score.aggregate > 0.0:
            self.db.add(child, score, generation, parent_id=parent.program_id)
            if meta is not None:
                self.meta.record(meta.id, score.aggregate)
            return True
        return False

    def run(self, total_steps: int, generation: int = 1) -> RunMetrics:
        """Run ``total_steps`` attempts across ``n_workers`` threads. Returns metrics."""
        start = time.perf_counter()
        accepted = 0
        steps_done = 0

        with ThreadPoolExecutor(max_workers=self.n_workers) as pool:
            futures = [
                pool.submit(self._worker_step, i % self.n_workers, generation)
                for i in range(total_steps)
            ]
            for fut in as_completed(futures):
                steps_done += 1
                if fut.result():
                    accepted += 1

        elapsed = time.perf_counter() - start
        best = self.db.best()
        return RunMetrics(
            n_workers=self.n_workers,
            steps=steps_done,
            accepted=accepted,
            rejected=steps_done - accepted,
            elapsed_seconds=elapsed,
            throughput=steps_done / elapsed if elapsed else 0.0,
            best_aggregate=best.aggregate if best else 0.0,
        )

    def best(self) -> Optional[ArchivedProgram]:
        return self.db.best()

    def all_programs(self) -> List[ArchivedProgram]:
        return self.db.all_programs()
