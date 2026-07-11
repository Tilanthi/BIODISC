"""Phase 3 — publication gate (graded autonomy) + provenance.

A discovery is only PUBLISHED after (a) the replication-anchored gate rules it
PUBLISH_ELIGIBLE and (b) explicit human approval. By default human approval is
NOT given, so publish_discovery() returns a dry-run record and writes nothing —
enforcing the human-in-the-loop checkpoint. When approved, records go to a
Phase-3 log kept SEPARATE from the legacy autonomous_discoveries.jsonl so the
running discovery loop is unaffected.

Every published record carries full provenance: the discovery-program source,
the evolved DE-method it embeds, the replication score, and the parent->child
genealogy — so any claim is auditable back to its diffs.
"""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from .replication import ReplicationScore

PUBLISH_ELIGIBLE = "PUBLISH_ELIGIBLE"
HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
REJECT = "REJECT"

# Default Phase-3 publication log (distinct from the legacy discovery loop).
DEFAULT_PUBLICATION_LOG = os.path.join(
    os.path.dirname(__file__), "runs", "published_discoveries.jsonl"
)


@dataclass
class GateDecision:
    decision: str
    reason: str


class PublicationGate:
    """Graded-autonomy gate over a replication score."""

    def __init__(self, min_replication: float = 0.7, min_precision: float = 0.5,
                 min_claims: int = 3, hold_replication_floor: float = 0.5):
        self.min_replication = min_replication
        self.min_precision = min_precision
        self.min_claims = min_claims
        self.hold_floor = hold_replication_floor

    def evaluate(self, score: ReplicationScore) -> GateDecision:
        if score.n_claims < self.min_claims:
            return GateDecision(REJECT, f"too few claims ({score.n_claims} < {self.min_claims})")
        if score.replication_rate >= self.min_replication and score.precision >= self.min_precision:
            return GateDecision(
                PUBLISH_ELIGIBLE,
                f"replication {score.replication_rate:.2f} >= {self.min_replication}, "
                f"precision {score.precision:.2f} >= {self.min_precision}",
            )
        if score.replication_rate >= self.hold_floor:
            return GateDecision(
                HOLD_FOR_REVIEW,
                f"replication {score.replication_rate:.2f} below publish threshold "
                f"{self.min_replication}",
            )
        return GateDecision(
            REJECT,
            f"replication {score.replication_rate:.2f} below hold floor {self.hold_floor}",
        )


@dataclass
class GenealogyNode:
    program_id: str
    parent_id: Optional[str]
    aggregate: float
    generation: int


@dataclass
class ProvenanceRecord:
    discovery_program_id: str
    discovery_program_source: str
    method_program_id: Optional[str]
    cohort_id: str
    replication_rate: float
    precision: float
    n_claims: int
    aggregate: float
    decision: str
    gate_reason: str
    human_approved: bool
    written: bool
    claims: List[dict]
    genealogy: List[dict] = field(default_factory=list)


def publish_discovery(
    *,
    discovery_program_id: str,
    discovery_program_source: str,
    method_program_id: Optional[str],
    cohort_id: str,
    score: ReplicationScore,
    decision: GateDecision,
    claims: List[dict],
    genealogy: List[GenealogyNode],
    human_approved: bool = False,
    log_path: str = DEFAULT_PUBLICATION_LOG,
) -> ProvenanceRecord:
    """Publish a discovery with full provenance, subject to the human checkpoint.

    Writes to ``log_path`` ONLY when decision == PUBLISH_ELIGIBLE AND
    human_approved. Otherwise returns a dry-run record (written=False).
    """
    eligible = decision.decision == PUBLISH_ELIGIBLE
    will_write = eligible and human_approved

    record = ProvenanceRecord(
        discovery_program_id=discovery_program_id,
        discovery_program_source=discovery_program_source,
        method_program_id=method_program_id,
        cohort_id=cohort_id,
        replication_rate=score.replication_rate,
        precision=score.precision,
        n_claims=score.n_claims,
        aggregate=score.aggregate,
        decision=decision.decision,
        gate_reason=decision.reason,
        human_approved=human_approved,
        written=will_write,
        claims=claims,
        genealogy=[asdict(g) for g in genealogy],
    )

    if will_write:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    return record
