"""Unified discovery candidate model — the lingua franca of the breakthrough package.

Every discovery modality (bridge engine, contradiction detector, anomaly-in-context,
re-mining) emits ``DiscoveryCandidate`` objects. They share a ``convergence_key``
so the ``ConvergenceScorer`` can merge candidates from *different* methods that
refer to the same underlying gene/claim — the multi-method-agreement signal that
distinguishes a likely breakthrough from a single-method artifact.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _normalize_key(text: str) -> str:
    """Normalize a claim/gene into a merge key (lowercase alnum, stopword-light)."""
    t = re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())
    words = [w for w in t.split() if len(w) > 2]
    # drop common biology filler so similar claims merge
    filler = {"the", "and", "for", "that", "this", "with", "from", "into", "are",
              "was", "were", "not", "but", "gene", "protein", "expression", "cells",
              "cell", "tissue", "human", "mouse", "rat", "may", "can", "could"}
    words = [w for w in words if w not in filler]
    return " ".join(sorted(words[:8]))


@dataclass
class DiscoveryCandidate:
    """A discovery candidate from any modality, consumable by the convergence scorer."""
    kind: str                          # 'cross_domain_bridge' | 'literature_contradiction' | 'anomaly_in_context' | 'remining_finding'
    claim: str                         # the specific, checkable claim
    gene: str = ""                     # the gene/entity at the center (if any)
    field_a: str = ""                  # for bridges: source field
    field_b: str = ""                  # for bridges: target field
    evidence: Dict[str, Any] = field(default_factory=dict)   # method-specific evidence
    methods: List[str] = field(default_factory=list)         # which methods flagged it
    novelty: float = 0.0               # 0-1 (literature-absence)
    importance: float = 0.0            # 0-1 (hub/network centrality)
    surprise: float = 0.0              # 0-1 (mechanistic-violation strength)
    convergence_score: int = 0         # # of independent methods agreeing (set by ConvergenceScorer)
    high_potential: bool = False       # convergence >= threshold (set by ConvergenceScorer)
    testable_with_existing_data: bool = False
    source_datasets: List[str] = field(default_factory=list)

    @property
    def ev(self) -> float:
        return round(self.novelty * self.importance * max(self.surprise, 0.1), 4)

    @property
    def convergence_key(self) -> str:
        """Key for merging candidates from different methods about the same thing.
        Prefers the gene (most precise); falls back to a normalized claim hash."""
        if self.gene:
            return f"gene:{self.gene.upper()}"
        return "claim:" + hashlib.md5(_normalize_key(self.claim).encode()).hexdigest()[:10]

    def merge(self, other: "DiscoveryCandidate") -> "DiscoveryCandidate":
        """Merge another candidate (same key) into this one — union the methods +
        evidence, take the max scores."""
        self.methods = sorted(set(self.methods) | set(other.methods))
        self.source_datasets = sorted(set(self.source_datasets) | set(other.source_datasets))
        self.evidence.update(other.evidence)
        self.novelty = max(self.novelty, other.novelty)
        self.importance = max(self.importance, other.importance)
        self.surprise = max(self.surprise, other.surprise)
        self.testable_with_existing_data = self.testable_with_existing_data or other.testable_with_existing_data
        return self

    def as_dict(self) -> dict:
        return {
            "kind": self.kind, "claim": self.claim, "gene": self.gene,
            "field_a": self.field_a, "field_b": self.field_b,
            "evidence": self.evidence, "methods": self.methods,
            "novelty": self.novelty, "importance": self.importance, "surprise": self.surprise,
            "ev": self.ev, "convergence_score": self.convergence_score,
            "high_potential": self.high_potential,
            "testable_with_existing_data": self.testable_with_existing_data,
            "source_datasets": self.source_datasets,
            "convergence_key": self.convergence_key,
        }


class CandidatePool:
    """Collects candidates from all modalities; merges by convergence_key."""

    def __init__(self):
        self._by_key: Dict[str, DiscoveryCandidate] = {}

    def add(self, candidate: DiscoveryCandidate) -> None:
        key = candidate.convergence_key
        if key in self._by_key:
            self._by_key[key].merge(candidate)
        else:
            self._by_key[key] = candidate

    def add_all(self, candidates: List[DiscoveryCandidate]) -> None:
        for c in candidates:
            self.add(c)

    def all(self) -> List[DiscoveryCandidate]:
        return list(self._by_key.values())

    def __len__(self) -> int:
        return len(self._by_key)
