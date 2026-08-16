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
"""Phase 3 — evolution controller for discovery programs.

Same AlphaEvolve loop as EvolutionController (sample -> propose diff -> apply ->
gate -> score -> archive + co-evolved meta-prompts), but the program contract is
``discover(...)`` and the fitness is REPLICATION (replication.py), not the DE
AUROC. Reuses ProgramDatabase/IslandModel, MetaPromptArchive, evaluation
cascade, and diff_applier unchanged. After evolution, publish_best() runs the
publication gate and writes provenance (subject to the human checkpoint).
"""
import logging
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import BenchmarkCase

from .diff_applier import apply_diffs_or_full, DiffApplyError, DiffParseError
from .discovery import (
    compile_discover_program, validate_discover_source, run_discover_program,
    get_seed_discovery_program,
)
from .meta_prompt import MetaPromptArchive
from .program_db import ArchivedProgram, ProgramDatabase
from .publication import (
    PublicationGate, GateDecision, GenealogyNode, ProvenanceRecord,
    DEFAULT_PUBLICATION_LOG, publish_discovery,
)
from .replication import ReplicationScore, replication_fitness
from .seeds import get_seed_program

logger = logging.getLogger(__name__)

Proposer = callable  # (system, user) -> str

DISCOVERY_SYSTEM = """\
You are an evolutionary coding agent improving a biological DISCOVERY program.
The program commits to quantitative claims about differentially-expressed genes.

CONTRACT (a valid program MUST satisfy):
- define `def discover(expression, labels, gene_symbols=None)`
- expression: np.ndarray (n_genes, n_samples); labels: np.ndarray of {0,1}
- return a list of claim dicts, each with keys: gene_index (int), direction
  (+1/-1), effect_size (float), ci_low, ci_high (95% CI bounds), p_value
- you may `import numpy as np` and `from scipy import stats` inside the function

FITNESS = REPLICATION. Claims made on the discovery cohort must REPLICATE on an
INDEPENDENT cohort (same direction + significant). Optimize for claims that
generalize. Do NOT overfit the cohort; do NOT hard-code gene indices.

OUTPUT FORMAT — return ONLY search-and-replace diffs:
<<< SEARCH
exact lines to replace (verbatim)
===
replacement lines
>>> REPLACE
Multiple blocks allowed. For a full rewrite, emit the entire new `def discover`.
No commentary or markdown fences.
"""


def build_discovery_prompt(parent, inspirations, generation, rng, meta_prompt=None):
    hints = [
        "Make a surgical change.",
        "Improve the confidence interval (analytical or bootstrap).",
        "Make claim selection more robust (rank by a blend of effect and significance).",
        "Reduce false positives via a stricter or better-calibrated threshold.",
        "Improve numerical stability.",
    ]
    style = rng.choice(hints)
    lines = [f"=== GENERATION {generation} ===",
             f"Goal: improve REPLICATION (currently rate={parent.replicate_concordance:.3f}, "
             f"precision={parent.auroc:.3f}, aggregate={parent.aggregate:.3f}).",
             f"Strategy hint: {style}"]
    if meta_prompt is not None:
        lines.append(f"Co-evolved guidance: {meta_prompt.text}")
    lines += ["", "=== CURRENT PROGRAM (parent) ===", parent.source.strip("\n")]
    if inspirations:
        lines += ["", "=== INSPIRATIONS ==="]
        for i, ins in enumerate(inspirations):
            lines.append(f"--- inspiration {i+1} (agg {ins.aggregate:.3f}) ---")
            lines.append(ins.source.strip("\n"))
    lines += ["", "Emit your improvement as diff blocks now."]
    return DISCOVERY_SYSTEM, "\n".join(lines)


@dataclass
class DiscoveryAttempt:
    generation: int
    accepted: bool
    aggregate: Optional[float]
    replication_rate: Optional[float]
    precision: Optional[float]
    error: Optional[str] = None


class DiscoveryEvolutionController:
    def __init__(
        self,
        pair: Tuple[BenchmarkCase, BenchmarkCase],
        proposer,
        db: Optional[ProgramDatabase] = None,
        rng: Optional[random.Random] = None,
        meta_archive: Optional[MetaPromptArchive] = None,
        gate: Optional[PublicationGate] = None,
    ):
        self.pair = pair
        self.proposer = proposer
        self.rng = rng or random.Random(0)
        self.db = db or ProgramDatabase(complexity_per_bucket=40)
        self.meta_archive = meta_archive or MetaPromptArchive(rng=self.rng)
        self.gate = gate or PublicationGate()
        self.attempts: List[DiscoveryAttempt] = []
        self.seed_score = self._seed_archive()

    def _evaluate(self, source: str) -> ReplicationScore:
        fn = compile_discover_program(source)
        return replication_fitness(fn, self.pair)

    def _seed_archive(self) -> ReplicationScore:
        src = get_seed_discovery_program()
        score = self._evaluate(src)
        if hasattr(self.db, "seed_all"):
            self.db.seed_all(src, score.to_method_score(), generation=0)
        else:
            self.db.add(src, score.to_method_score(), generation=0, parent_id=None)
        logger.info(f"seed discovery: replication={score.replication_rate:.3f} "
                    f"precision={score.precision:.3f} agg={score.aggregate:.3f}")
        return score

    def step(self, generation: int) -> DiscoveryAttempt:
        parent, inspirations = self.db.sample()
        meta = self.meta_archive.sample()
        system, user = build_discovery_prompt(parent, inspirations, generation, self.rng, meta)

        try:
            raw = self.proposer(system, user)
        except Exception as exc:
            return self._log(generation, False, err=f"proposer: {exc}")
        try:
            child = apply_diffs_or_full(parent.source, raw, entry_name="discover")
        except (DiffParseError, DiffApplyError) as exc:
            return self._log(generation, False, err=f"diff: {exc}")
        if not validate_discover_source(child):
            return self._log(generation, False, err="invalid source")
        try:
            score = self._evaluate(child)
        except Exception as exc:
            return self._log(generation, False, err=f"eval: {exc}")

        accepted = score.aggregate > 0.0
        if accepted:
            self.db.add(child, score.to_method_score(), generation, parent_id=parent.program_id)
            self.meta_archive.record(meta.id, score.aggregate)
        return self._log(generation, accepted, score=score)

    def _log(self, generation, accepted, score=None, err=None) -> DiscoveryAttempt:
        a = DiscoveryAttempt(
            generation=generation, accepted=accepted,
            aggregate=score.aggregate if score else None,
            replication_rate=score.replication_rate if score else None,
            precision=score.precision if score else None,
            error=err,
        )
        self.attempts.append(a)
        return a

    def run(self, generations: int, attempts_per_generation: int = 1) -> ArchivedProgram:
        for g in range(1, generations + 1):
            for _ in range(attempts_per_generation):
                self.step(g)
            best = self.db.best()
            logger.info(f"discovery gen {g}: best aggregate={best.aggregate:.3f}")
        return self.db.best()

    def publish_best(self, human_approved: bool = False,
                     log_path: str = DEFAULT_PUBLICATION_LOG
                     ) -> Tuple[ProvenanceRecord, ReplicationScore, GateDecision, ArchivedProgram]:
        """Run the gate on the best program and publish with full provenance.

        human_approved defaults False -> dry run (nothing written).
        """
        best = self.db.best()
        fn = compile_discover_program(best.source)
        score = self._evaluate(best.source)
        decision = self.gate.evaluate(score)

        cohort_a = self.pair[0]
        claims = [c.__dict__ for c in run_discover_program(
            fn, cohort_a.expression, cohort_a.labels, dataset_id="cohort_a").claims]
        genealogy = [GenealogyNode(p.program_id, p.parent_id, p.aggregate, p.generation)
                     for p in self.db.all_programs()]

        record = publish_discovery(
            discovery_program_id=best.program_id,
            discovery_program_source=best.source,
            method_program_id=None,  # could link a Phase-1 evolved method if composed
            cohort_id="replication_pair",
            score=score, decision=decision, claims=claims, genealogy=genealogy,
            human_approved=human_approved, log_path=log_path,
        )
        return record, score, decision, best
