"""MAP-Elites program database + island model for evolutionary code search.

Phase 1 used a 1-D archive (complexity only). Phase 2 upgrades to:

* 2-D MAP-Elites — elites indexed by (complexity bucket, method family), so the
  archive preserves diversity along TWO behavioral axes (simple/complex ×
  ttest/rank/foldchange/...). Niches that a 1-D archive would collapse now
  survive, which is what feeds genuinely diverse inspirations to the LLM.
* IslandModel — several independent archives with periodic ring migration of
  elites, the standard way to maintain between-population diversity.

Both expose the same minimal interface (add / sample / best / all_programs) so
the EvolutionController can use either interchangeably. Full multi-dimension
MAP-Elites + richer islands can grow from here.
"""
import ast
import hashlib
import random
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore

Cell = Tuple[int, str]


@dataclass
class ArchivedProgram:
    program_id: str           # sha1 of source
    source: str
    aggregate: float
    auroc: float
    replicate_concordance: float
    generation: int
    parent_id: Optional[str]
    complexity: int           # AST node count (behavior descriptor 1)
    bucket: int               # complexity bucket (kept for backwards compat)
    family: str = "other"     # method family (behavior descriptor 2)


def _complexity(source: str) -> int:
    """AST node count — behavioral descriptor 1 (niche: simple vs complex)."""
    try:
        return sum(1 for _ in ast.walk(ast.parse(source)))
    except SyntaxError:
        return 10 ** 9


_FAMILY_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("ttest", re.compile(r"ttest_ind|ttest_1samp|ttest_rel|student", re.I)),
    ("rank", re.compile(r"mannwhitneyu|ranksums|rankdata|wilcoxon|kendall", re.I)),
    ("foldchange", re.compile(r"foldchange|log2fc|\.mean\s*\(|mean\s*\(", re.I)),
    ("bayes", re.compile(r"bayes|posterior|deseq|limma|moderated", re.I)),
]


def method_family(source: str) -> str:
    """Behavioral descriptor 2: which statistic family a program implements."""
    for name, pat in _FAMILY_PATTERNS:
        if pat.search(source):
            return name
    return "other"


class ProgramDatabase:
    """2-D MAP-Elites archive over (complexity bucket, method family)."""

    def __init__(
        self,
        n_buckets: int = 8,
        complexity_per_bucket: int = 25,
        max_inspirations: int = 3,
        seed: int = 0,
    ):
        self.n_buckets = n_buckets
        self.complexity_per_bucket = complexity_per_bucket
        self.max_inspirations = max_inspirations
        self._elites: dict = {}  # Cell -> ArchivedProgram
        self._seen_hashes: set = set()
        self._all: List[ArchivedProgram] = []
        self._rng = random.Random(seed)

    def _cell_of(self, source: str) -> Cell:
        bucket = min(_complexity(source) // self.complexity_per_bucket, self.n_buckets - 1)
        return (bucket, method_family(source))

    def add(
        self,
        source: str,
        score: DEMethodScore,
        generation: int,
        parent_id: Optional[str] = None,
    ) -> Optional[ArchivedProgram]:
        """Add a program; keep it if it is the best in its (complexity, family) cell."""
        program_id = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
        if program_id in self._seen_hashes:
            return None

        cell = self._cell_of(source)
        archived = ArchivedProgram(
            program_id=program_id,
            source=source,
            aggregate=score.aggregate,
            auroc=score.auroc,
            replicate_concordance=score.replicate_concordance,
            generation=generation,
            parent_id=parent_id,
            complexity=_complexity(source),
            bucket=cell[0],
            family=cell[1],
        )

        incumbent = self._elites.get(cell)
        if incumbent is None or archived.aggregate > incumbent.aggregate:
            self._elites[cell] = archived
        self._seen_hashes.add(program_id)
        self._all.append(archived)
        return archived

    def occupied_cells(self) -> List[Cell]:
        return list(self._elites.keys())

    # Backwards-compat alias.
    def occupied_buckets(self) -> List[Cell]:
        return self.occupied_cells()

    def sample(self) -> Tuple[ArchivedProgram, List[ArchivedProgram]]:
        """Return (parent, inspirations): a random elite + diverse others."""
        cells = self.occupied_cells()
        if not cells:
            raise RuntimeError("cannot sample from an empty archive")
        parent_cell = self._rng.choice(cells)
        parent = self._elites[parent_cell]

        others = [self._elites[c] for c in cells if c != parent_cell]
        self._rng.shuffle(others)
        return parent, others[: self.max_inspirations]

    def best(self) -> Optional[ArchivedProgram]:
        return max(self._elites.values(), key=lambda e: e.aggregate) if self._elites else None

    def all_programs(self) -> List[ArchivedProgram]:
        return list(self._all)

    def __len__(self) -> int:
        return len(self._elites)


class IslandModel:
    """Multiple ProgramDatabase islands with periodic ring migration of elites.

    Exposes the same interface as ProgramDatabase (add/sample/best/all_programs)
    so the controller can use it as a drop-in replacement. Programs are assigned
    to islands by a deterministic hash of their source (so the same program is
    never split across islands); every ``migration_interval`` adds, the best
    program of each island is copied to the next island (ring), spreading strong
    material while keeping populations distinct.
    """

    def __init__(
        self,
        n_islands: int = 3,
        migration_interval: int = 5,
        seed: int = 0,
        **db_kwargs,
    ):
        self.n_islands = n_islands
        self.migration_interval = migration_interval
        self.islands: List[ProgramDatabase] = [
            ProgramDatabase(seed=seed + i, **db_kwargs) for i in range(n_islands)
        ]
        self._rng = random.Random(seed + 1000)
        self._ops = 0

    def _island_index(self, source: str) -> int:
        h = int(hashlib.sha1(source.encode("utf-8")).hexdigest(), 16)
        return h % self.n_islands

    def add(self, source, score, generation, parent_id=None) -> Optional[ArchivedProgram]:
        self._ops += 1
        island = self.islands[self._island_index(source)]
        result = island.add(source, score, generation, parent_id)
        if self.migration_interval and self._ops % self.migration_interval == 0:
            self.migrate()
        return result

    def seed_all(self, source, score, generation) -> None:
        """Seed EVERY island with the same incumbent so populations compete fairly.

        Without this, hash-based assignment places the seed on only one island;
        the others start empty and cannot compete in short runs.
        """
        for isl in self.islands:
            isl.add(source, score, generation, parent_id=None)

    def migrate(self) -> int:
        """Copy each island's best into the next island (ring). Returns # copied."""
        bests = [isl.best() for isl in self.islands]
        copied = 0
        for i, island in enumerate(self.islands):
            donor = bests[(i - 1) % self.n_islands]
            if donor is None:
                continue
            added = island.add(
                donor.source,
                DEMethodScore(
                    auroc=donor.auroc,
                    replicate_concordance=donor.replicate_concordance,
                    aggregate=donor.aggregate,
                ),
                generation=donor.generation,
                parent_id=donor.program_id,
            )
            if added is not None:
                copied += 1
        return copied

    def sample(self) -> Tuple[ArchivedProgram, List[ArchivedProgram]]:
        occupied = [i for i, isl in enumerate(self.islands) if len(isl) > 0]
        if not occupied:
            raise RuntimeError("cannot sample from an empty island model")
        island = self.islands[self._rng.choice(occupied)]
        return island.sample()

    def best(self) -> Optional[ArchivedProgram]:
        bests = [isl.best() for isl in self.islands if isl.best() is not None]
        return max(bests, key=lambda e: e.aggregate) if bests else None

    def all_programs(self) -> List[ArchivedProgram]:
        return [p for isl in self.islands for p in isl.all_programs()]

    def maybe_migrate(self) -> None:
        """Hook the controller calls after each step (no-op gate happens in add)."""
        # Migration is triggered in add() by interval; this is a no-op placeholder
        # so callers can call it uniformly without breaking.
        return None

    def __len__(self) -> int:
        return sum(len(isl) for isl in self.islands)
