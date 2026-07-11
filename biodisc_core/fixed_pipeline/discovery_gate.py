"""Flagging gate for real-loop discoveries (Phase B quality integration).

The user's prime directive: a 'discovery' must be CHECKED before it is flagged
as representing genuine new scientific progress. This module is that check, and
it is where the AlphaEvolve work's replication anchor connects to the real loop.

Honest guarantee (enforced here): a discovery is flagged ``is_genuine = True``
ONLY if it has REPLICATED on independent data (``report['replication']['replicated']``)
AND passed peer review. The autonomous loop runs on a SINGLE dataset, so by
default it cannot establish replication — therefore real-loop discoveries are
saved as ``candidate_unconfirmed`` (is_genuine=False), never as confirmed
Eureka-level findings. This prevents false claims of new knowledge.

When a replication cohort is wired in future (second dataset / held-out split),
the loop sets ``report['replication'] = {'replicated': True, ...}`` and the gate
promotes the discovery to ``genuine`` automatically.
"""
from dataclasses import dataclass
from typing import Tuple

TIER_GENUINE = "genuine"                    # validated + peer-reviewed + replicated
TIER_CANDIDATE = "candidate_unconfirmed"    # validated but NOT replicated
TIER_REJECTED = "rejected"                  # failed validation / peer review


@dataclass
class FlagDecision:
    tier: str
    is_genuine: bool
    reason: str


def _validation_passed(report: dict) -> bool:
    """The orchestrator returns None on hard gate failure, so a present report
    has already cleared the 5-layer validation. Defensive sanity-check here."""
    val = report.get("comprehensive_validation_statistics")
    if not val:
        return True
    # If any layer recorded an explicit pass=False, treat as failed.
    for _layer, result in val.items():
        if isinstance(result, dict):
            for k, v in result.items():
                if k in ("passed", "success", "is_relevant", "question_valid",
                         "passes_significance_gate") and v is False:
                    return False
    return True


def evaluate_for_flagging(report: dict) -> FlagDecision:
    replication = report.get("replication") or {}
    replicated = bool(replication.get("replicated", False))

    peer = report.get("peer_review_result") or {}
    peer_decision = peer.get("decision")
    if peer_decision in ("REJECT", "REJECTED"):
        return FlagDecision(TIER_REJECTED, False, "peer review rejected")

    if not _validation_passed(report):
        return FlagDecision(TIER_REJECTED, False, "validation gate failed")

    if replicated:
        peer_ok = (peer_decision in (None, "ACCEPT", "ACCEPTED"))
        if peer_ok:
            return FlagDecision(TIER_GENUINE, True,
                                "validated + peer-reviewed + replicated")
        return FlagDecision(TIER_CANDIDATE, False,
                            "replicated but not peer-accepted — not flagged genuine")

    # Single-dataset default: validated but NOT replicated -> NOT genuine.
    return FlagDecision(
        TIER_CANDIDATE, False,
        "validated but not replicated (single dataset) — not flagged genuine",
    )


def stamp_report(report: dict) -> Tuple[dict, FlagDecision]:
    """Return a copy of ``report`` with the flagging decision stamped on it."""
    decision = evaluate_for_flagging(report)
    out = dict(report)
    out["flagging"] = {
        "tier": decision.tier,
        "is_genuine": decision.is_genuine,
        "reason": decision.reason,
    }
    out["is_genuine"] = decision.is_genuine
    return out, decision
