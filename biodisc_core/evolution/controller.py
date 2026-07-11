"""Evolution controller — the AlphaEvolve loop for DE-method discovery.

Loop (single-process in Phase 1):
    sample(parent, inspirations) -> build_prompt -> proposer -> apply_diffs
    -> validate (compiles + defines score) -> evaluate (fitness h) -> archive

The 5-layer discovery validation becomes a HARD GATE here for methods: a
candidate must compile, define `score`, run, and return a strictly-positive
aggregate (broken/crashing programs score 0.0 and are rejected, never archived).
Fitness is measured ONLY on truth-known / held-out benchmark data — never on
validation-gate output — so the optimizer cannot learn to fool a validator.
"""
import logging
import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark, score_de_method
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import BenchmarkCase

from .program import compile_de_program, validate_program_source
from .program_db import ArchivedProgram, ProgramDatabase
from .prompt_sampler import build_evolution_prompt
from .meta_prompt import MetaPromptArchive
from .seeds import get_seed_program
from .diff_applier import apply_diffs_or_full, DiffParseError, DiffApplyError

logger = logging.getLogger(__name__)

Proposer = Callable[[str, str], str]  # (system, user) -> raw model text


@dataclass
class AttemptLog:
    generation: int
    parent_id: Optional[str]
    accepted: bool
    aggregate: Optional[float]
    error: Optional[str] = None


@dataclass
class EvolutionResult:
    best_source: str
    best_score: DEMethodScore
    seed_score: DEMethodScore
    genealogy: List[ArchivedProgram]
    attempts: List[AttemptLog] = field(default_factory=list)

    @property
    def improvement(self) -> float:
        return self.best_score.aggregate - self.seed_score.aggregate


class EvolutionController:
    """Runs evolutionary code search over DE programs against one benchmark."""

    def __init__(
        self,
        benchmark: BenchmarkCase,
        proposer: Proposer,
        db: Optional[ProgramDatabase] = None,
        rng: Optional[random.Random] = None,
        db_seed: int = 0,
        meta_archive: Optional[MetaPromptArchive] = None,
        use_cascade: bool = False,
        screen_floor: float = 0.55,
    ):
        self.benchmark = benchmark
        self.proposer = proposer
        self.rng = rng or random.Random(0)
        self.db = db or ProgramDatabase(seed=db_seed)
        self.meta_archive = meta_archive or MetaPromptArchive(rng=self.rng)
        self.use_cascade = use_cascade
        self.screen_floor = screen_floor
        self.attempts: List[AttemptLog] = []
        self.seed_score = self._seed_archive()

    def _evaluate(self, source: str) -> DEMethodScore:
        fn = compile_de_program(source)
        return score_de_method(fn, self.benchmark)

    def _evaluate_child(self, source: str) -> Optional[DEMethodScore]:
        """Evaluate a candidate; with the cascade enabled, cheap-screen first.

        Returns None when the candidate is pruned at the screen stage.
        """
        if not self.use_cascade:
            return self._evaluate(source)
        from .evaluation_cascade import cascade_evaluate
        return cascade_evaluate(source, self.benchmark, screen_floor=self.screen_floor)

    def _seed_archive(self) -> DEMethodScore:
        seed_source = get_seed_program()
        score = self._evaluate(seed_source)
        # Island models: seed every island so populations compete fairly;
        # single archives: add once.
        if hasattr(self.db, "seed_all"):
            self.db.seed_all(seed_source, score, generation=0)
        else:
            self.db.add(seed_source, score, generation=0, parent_id=None)
        logger.info(f"seed fitness: aggregate={score.aggregate:.3f} "
                    f"(auroc={score.auroc:.3f}, replicate={score.replicate_concordance:.3f})")
        return score

    def step(self, generation: int) -> AttemptLog:
        """One evolution attempt: sample -> propose -> apply -> gate -> score -> archive."""
        parent, inspirations = self.db.sample()
        meta_prompt = self.meta_archive.sample()
        system, user = build_evolution_prompt(
            parent, inspirations, generation, self.rng, meta_prompt=meta_prompt,
        )

        try:
            raw = self.proposer(system, user)
        except Exception as exc:  # proposer failure (e.g. API error) -> skip, don't crash
            log = AttemptLog(generation, parent.program_id, False, None, f"proposer: {exc}")
            self.attempts.append(log)
            return log

        try:
            child_source = apply_diffs_or_full(parent.source, raw)
        except (DiffParseError, DiffApplyError) as exc:
            log = AttemptLog(generation, parent.program_id, False, None, f"diff: {exc}")
            self.attempts.append(log)
            return log

        if not validate_program_source(child_source):
            log = AttemptLog(generation, parent.program_id, False, None, "invalid source")
            self.attempts.append(log)
            return log

        try:
            score = self._evaluate_child(child_source)
        except Exception as exc:
            log = AttemptLog(generation, parent.program_id, False, None, f"compile/eval: {exc}")
            self.attempts.append(log)
            return log

        if score is None:
            log = AttemptLog(generation, parent.program_id, False, None,
                             f"cascade pruned (screen < {self.screen_floor})")
            self.attempts.append(log)
            return log

        accepted = score.aggregate > 0.0
        if accepted:
            self.db.add(child_source, score, generation, parent_id=parent.program_id)
            # Credit this program's fitness back to the directive that guided it.
            self.meta_archive.record(meta_prompt.id, score.aggregate)
        log = AttemptLog(generation, parent.program_id, accepted, score.aggregate)
        self.attempts.append(log)
        return log

    def run(self, generations: int, attempts_per_generation: int = 1) -> EvolutionResult:
        for g in range(1, generations + 1):
            for _ in range(attempts_per_generation):
                self.step(g)
            best = self.db.best()
            logger.info(f"generation {g}: best aggregate={best.aggregate:.3f}")
        best = self.db.best()
        return EvolutionResult(
            best_source=best.source,
            best_score=DEMethodScore(
                auroc=best.auroc,
                replicate_concordance=best.replicate_concordance,
                aggregate=best.aggregate,
            ),
            seed_score=self.seed_score,
            genealogy=self.db.all_programs(),
            attempts=list(self.attempts),
        )
