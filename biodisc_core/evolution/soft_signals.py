"""Phase 3 — advisory soft signals (novelty, literature consistency).

WARNING — these are ADVISORY ONLY and are NEVER part of the evolutionary
fitness. The fitness anchor is REPLICATION (replication.py). Per the plan's
anti-pseudo-science rules, novelty and literature-consistency are LLM-graded
soft signals that can be reported on a published claim but must not drive
selection — otherwise the optimizer learns to game the LLM judge rather than
find replicable signal. is_anchor is always False by construction.
"""
import json
import re
from dataclasses import dataclass
from typing import Callable

Proposer = Callable[[str, str], str]

_SOFT_SYSTEM = (
    "You are a cautious scientific reviewer. Grade ONE biological claim on two "
    "0.0-1.0 scales: 'novelty' (how specific/non-textbook) and "
    "'literature_consistency' (plausibility vs established biology). "
    "Respond with compact JSON only: "
    '{"novelty": float, "literature_consistency": float, "rationale": str}.'
)


@dataclass
class SoftSignals:
    novelty: float
    literature_consistency: float
    rationale: str = ""
    is_anchor: bool = False  # always False — advisory only


def _extract_float(text: str, key: str) -> float:
    m = re.search(rf'"{key}"\s*:\s*([0-9]*\.?[0-9]+)', text)
    if not m:
        return 0.0
    try:
        return max(0.0, min(1.0, float(m.group(1))))
    except ValueError:
        return 0.0


def grade_soft_signals(claim_text: str, proposer: Proposer) -> SoftSignals:
    """Ask the LLM to grade a claim's novelty / literature consistency.

    Returns a SoftSignals with values clamped to [0,1]. On any failure returns
    zeros (never raises) — these signals are advisory and must not break the loop.
    """
    try:
        raw = proposer(_SOFT_SYSTEM, f"Claim: {claim_text}")
    except Exception:
        return SoftSignals(0.0, 0.0, "proposer unavailable")

    # Prefer a JSON parse; fall back to regex extraction.
    rationale = ""
    try:
        # grab the first {...} block
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            obj = json.loads(match.group(0))
            return SoftSignals(
                novelty=max(0.0, min(1.0, float(obj.get("novelty", 0.0)))),
                literature_consistency=max(0.0, min(1.0, float(obj.get("literature_consistency", 0.0)))),
                rationale=str(obj.get("rationale", "")),
            )
    except (ValueError, TypeError):
        pass

    return SoftSignals(
        novelty=_extract_float(raw, "novelty"),
        literature_consistency=_extract_float(raw, "literature_consistency"),
        rationale=raw[:200],
    )
