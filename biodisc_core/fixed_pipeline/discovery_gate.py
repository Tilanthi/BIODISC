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
from dataclasses import dataclass, field
from typing import List, Tuple

TIER_GENUINE = "genuine"                    # validated + peer-reviewed + replicated
TIER_CANDIDATE = "candidate_unconfirmed"    # validated but NOT replicated
TIER_REJECTED = "rejected"                  # failed validation / peer review

# Gate-2's similarity threshold (must mirror literature_gate's default; kept as a
# literal so this module stays import-light and stdlib-only).
_GATE2_THRESHOLD = 0.55
_NOVELTY_MARGIN = 0.05   # within this of the threshold => thin margin
_WEAK_FRACTION = 0.5     # replication fraction below this => weak


@dataclass
class FlagDecision:
    tier: str
    is_genuine: bool
    reason: str
    # V9.1 limitations taxonomy: machine-readable epistemic qualifiers on the
    # GENUINE tier. Status: 'verified' | 'verified_with_limitations' (genuine
    # tier only; candidates/rejected carry their tier as status). Readers must
    # treat a MISSING status as 'verified' (pre-V9.1 records).
    limitations: List[str] = field(default_factory=list)
    status: str = ""


def _limitations_of(report: dict) -> List[str]:
    """Machine-checkable limitations of a genuine-tier finding (V9.1).

    Deliberately conservative — each limitation must be derivable from recorded
    evidence in the report, never asserted from judgment:
      * internal_replication_only — replicated on the held-out SPLIT of the same
        dataset, not an independent cohort (weaker than the gold standard).
      * weak_replication_fraction — under half the tested genes replicated.
      * novelty_margin_thin — Gate-2 similarity within 0.05 of the known
        threshold: a small retrieval change would flip novel->known.
    """
    out: List[str] = []
    rep = report.get("replication") or {}
    if rep.get("replicated"):
        if rep.get("method") == "internal_held_out_split_nominal_p":
            out.append("internal_replication_only")
        try:
            if float(rep.get("replication_fraction", 1.0)) < _WEAK_FRACTION:
                out.append("weak_replication_fraction")
        except (TypeError, ValueError):
            pass
    lit = (report.get("comprehensive_validation_statistics") or {}).get(
        "literature_novelty") or {}
    sim = lit.get("max_similarity")
    if isinstance(sim, (int, float)) and sim >= (_GATE2_THRESHOLD - _NOVELTY_MARGIN):
        out.append("novelty_margin_thin")
    return out


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
        return FlagDecision(TIER_REJECTED, False, "peer review rejected",
                            status=TIER_REJECTED)

    if not _validation_passed(report):
        return FlagDecision(TIER_REJECTED, False, "validation gate failed",
                            status=TIER_REJECTED)

    if replicated:
        peer_ok = (peer_decision in (None, "ACCEPT", "ACCEPTED"))
        if peer_ok:
            limitations = _limitations_of(report)
            status = "verified_with_limitations" if limitations else "verified"
            return FlagDecision(TIER_GENUINE, True,
                                "validated + peer-reviewed + replicated",
                                limitations=limitations, status=status)
        return FlagDecision(TIER_CANDIDATE, False,
                            "replicated but not peer-accepted — not flagged genuine",
                            status=TIER_CANDIDATE)

    # Single-dataset default: validated but NOT replicated -> NOT genuine.
    return FlagDecision(
        TIER_CANDIDATE, False,
        "validated but not replicated (single dataset) — not flagged genuine",
        status=TIER_CANDIDATE,
    )


def stamp_report(report: dict) -> Tuple[dict, FlagDecision]:
    """Return a copy of ``report`` with the flagging decision stamped on it."""
    decision = evaluate_for_flagging(report)
    out = dict(report)
    out["flagging"] = {
        "tier": decision.tier,
        "is_genuine": decision.is_genuine,
        "reason": decision.reason,
        # V9.1 taxonomy: status + machine-readable limitations (absent on
        # pre-V9.1 records; readers treat missing status as 'verified').
        "status": decision.status,
        "limitations": decision.limitations,
    }
    out["is_genuine"] = decision.is_genuine
    return out, decision
