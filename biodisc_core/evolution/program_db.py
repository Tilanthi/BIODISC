"""MAP-Elites program database for evolutionary code search (AlphaEvolve).

Stores evolved DE programs in a 1-D MAP-Elites archive keyed by a behavioral
dimension (code complexity, bucketed). The archive keeps the best program per
bucket and samples parents + diverse inspirations for the next generation,
balancing exploitation (best per niche) with exploration (diversity across
niches). This is the mechanism that lets past ideas resurface.

A full MAP-Elites + island model (multi-dimension, migration) is Phase 2.
"""
import ast
import hashlib
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore


@dataclass
class ArchivedProgram:
    program_id: str           # sha1 of source
    source: str
    aggregate: float
    auroc: float
    replicate_concordance: float
    generation: int
    parent_id: Optional[str]
    complexity: int           # AST node count (behavior descriptor)
    bucket: int


def _complexity(source: str) -> int:
    """AST node count — a cheap behavioral descriptor for MAP-Elites niches."""
    try:
        return sum(1 for _ in ast.walk(ast.parse(source)))
    except SyntaxError:
        return 10**9


class ProgramDatabase:
    """1-D MAP-Elites archive over code-complexity buckets."""

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
        self._elites: List[Optional[ArchivedProgram]] = [None] * n_buckets
        self._seen_hashes: set = set()
        self._all: List[ArchivedProgram] = []  # genealogy log (every accepted program)
        self._rng = random.Random(seed)

    def _bucket_of(self, source: str) -> int:
        return min(_complexity(source) // self.complexity_per_bucket, self.n_buckets - 1)

    def add(
        self,
        source: str,
        score: DEMethodScore,
        generation: int,
        parent_id: Optional[str] = None,
    ) -> Optional[ArchivedProgram]:
        """Add a program; keep it if it is the best in its complexity bucket.

        Returns the ArchivedProgram if accepted, None if deduped/declined.
        """
        program_id = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
        if program_id in self._seen_hashes:
            return None  # exact duplicate source; skip

        bucket = self._bucket_of(source)
        archived = ArchivedProgram(
            program_id=program_id,
            source=source,
            aggregate=score.aggregate,
            auroc=score.auroc,
            replicate_concordance=score.replicate_concordance,
            generation=generation,
            parent_id=parent_id,
            complexity=_complexity(source),
            bucket=bucket,
        )

        incumbent = self._elites[bucket]
        if incumbent is None or archived.aggregate > incumbent.aggregate:
            self._elites[bucket] = archived
        self._seen_hashes.add(program_id)
        self._all.append(archived)
        return archived

    def occupied_buckets(self) -> List[int]:
        return [b for b, e in enumerate(self._elites) if e is not None]

    def sample(self) -> Tuple[ArchivedProgram, List[ArchivedProgram]]:
        """Return (parent, inspirations): a random elite + diverse others."""
        occupied = self.occupied_buckets()
        if not occupied:
            raise RuntimeError("cannot sample from an empty archive")
        parent_bucket = self._rng.choice(occupied)
        parent = self._elites[parent_bucket]
        assert parent is not None

        others = [self._elites[b] for b in occupied if b != parent_bucket]
        self._rng.shuffle(others)
        inspirations = others[: self.max_inspirations]
        return parent, inspirations

    def best(self) -> Optional[ArchivedProgram]:
        elites = [e for e in self._elites if e is not None]
        return max(elites, key=lambda e: e.aggregate) if elites else None

    def all_programs(self) -> List[ArchivedProgram]:
        """Full genealogy log (every accepted program, in insertion order)."""
        return list(self._all)

    def __len__(self) -> int:
        return len(self.occupied_buckets())
