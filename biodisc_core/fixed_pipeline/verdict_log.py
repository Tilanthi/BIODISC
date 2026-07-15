"""Structured per-candidate verdict logging — the discovery funnel.

ASTRA's #1 process lesson (MEASURE BEFORE BUILDING): before adding features,
diagnose where candidates actually die. The prerequisite is a structured
verdict log written INSIDE the search process — one JSONL line per candidate —
because the supervisor runs the search as a subprocess with stdout discarded,
so any verdict not explicitly written to disk is silently lost.

This module is that log. Every candidate (pass OR fail) gets one line carrying
enough to bucket the outcome:

    generated
      -> gate1 (fdr significance)  pass/fail + effect + p
        -> sub-gates (duplicate, dataset_question, probe_gene, template)
          -> gate2 (literature novelty)  novel / known / retrieval_failed
            -> replication  replicated / single_cohort
              -> stored (genuine) | quarantined (candidate) | rejected

Where the pile is largest is the bottleneck — and each bucket points to a
DIFFERENT fix. See :func:`verdict_summary`.
"""
import json
import logging
import os
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Repo root: biodisc_core/fixed_pipeline/verdict_log.py -> up 2 parents (= BIODISC).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERDICT_LOG = PROJECT_ROOT / "discovery_verdicts.jsonl"


def _verdict_log_path(log_file: Optional[Path] = None) -> Path:
    """Resolve the verdict-log path, honoring the BIODISC_VERDICT_LOG override.

    Tests set BIODISC_VERDICT_LOG to a tmp path (via conftest) so
    validate_discovery_comprehensive — which calls log_verdict unconditionally —
    does not pollute the production discovery_verdicts.jsonl with synthetic
    verdicts. Production reads default to VERDICT_LOG.
    """
    if log_file is not None:
        return log_file
    env = os.environ.get("BIODISC_VERDICT_LOG")
    return Path(env) if env else VERDICT_LOG


def log_verdict(verdict: dict, *, log_file: Optional[Path] = None) -> None:
    """Append one structured verdict line. Never raises (logging must not kill the pipeline).

    Expected keys (all optional, but the more present the better the funnel):
        question, dataset_id, claim,
        gate1_pass, gate1_min_fdr, gate1_n_sig,
        subgate_duplicate, subgate_dataset_question, subgate_probe_gene, subgate_template,
        gate2_status (novel|known|retrieval_failed), gate2_max_similarity, gate2_n_papers,
        replication_status (replicated|single_cohort|not_attempted),
        both_pass, outcome (stored|quarantined|rejected),
        reason
    """
    try:
        target = _verdict_log_path(log_file)
        target.parent.mkdir(parents=True, exist_ok=True)
        line = dict(verdict)
        line.setdefault("logged_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        with open(target, "a") as f:
            f.write(json.dumps(line) + "\n")
    except Exception as e:  # noqa: BLE001 - logging must never break discovery
        logger.warning("verdict logging failed (non-fatal): %s", e)


def _read_verdicts(log_file: Optional[Path] = None) -> list:
    target = log_file or VERDICT_LOG
    if not target.exists():
        return []
    out = []
    for line in target.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def read_verdicts_dedup(log_file: Optional[Path] = None) -> list:
    """One record per candidate, deduped by validation token (``vtok``).

    The orchestrator writes a PROVISIONAL verdict (outcome ``in_progress``) at the
    start of validation and the FINAL verdict (same ``vtok``) at the end. This
    returns one record per ``vtok``: the final if it exists, else the provisional
    rewritten as ``rejected`` / ``abandoned_mid_validation`` — so a cycle killed
    mid-validation (no final ever written) still shows up as a counted failure
    instead of silently vanishing. Records without a ``vtok`` (coarse live-loop
    verdicts, legacy entries) pass through unchanged.
    """
    raw = _read_verdicts(log_file)
    no_tok, by_tok = [], {}
    for v in raw:
        tok = v.get("vtok")
        if tok is None:
            no_tok.append(v)
        else:
            by_tok.setdefault(tok, []).append(v)

    out = list(no_tok)
    for tok, group in by_tok.items():
        group.sort(key=lambda g: g.get("logged_at") or "")
        finals = [g for g in group if (g.get("outcome") or "") != "in_progress"]
        if finals:
            out.append(finals[-1])
        else:
            abandoned = dict(group[-1])
            abandoned["outcome"] = "rejected"
            abandoned["reason"] = ("abandoned_mid_validation: no final verdict "
                                   "(process likely killed mid-validation)")
            out.append(abandoned)
    return out


def _outcome_bucket(v: dict) -> str:
    """Bucket a single verdict into where it died (or survived)."""
    outcome = v.get("outcome")
    if outcome in ("stored", "quarantined", "rejected"):
        # Rejected candidates: attribute to the first gate that failed.
        if outcome == "rejected":
            if "abandoned_mid_validation" in (v.get("reason") or ""):
                return "abandoned_mid_validation"
            if v.get("gate1_pass") is False:
                return "died_gate1_significance"
            if v.get("gate2_status") == "known":
                return "died_gate2_textbook_known"
            if v.get("gate2_status") == "retrieval_failed":
                return "died_gate2_retrieval_failed"
            for sg in ("subgate_duplicate", "subgate_dataset_question",
                       "subgate_probe_gene", "subgate_template"):
                if v.get(sg) is False:
                    return f"died_subgate_{sg.replace('subgate_', '')}"
            return "rejected_other"
        return outcome  # stored / quarantined
    if outcome == "in_progress":
        return "in_progress"  # only seen pre-dedup; dedup converts orphans to abandoned
    return "unknown_outcome"


def verdict_summary(log_file: Optional[Path] = None) -> dict:
    """Bucket all verdicts into a funnel distribution. The largest bucket is the bottleneck."""
    verdicts = read_verdicts_dedup(log_file)
    buckets = Counter(_outcome_bucket(v) for v in verdicts)
    total = len(verdicts)
    # Gate-2 retrieval-failure rate (infrastructure health, §7.4)
    g2 = [v for v in verdicts if v.get("gate2_status") is not None]
    retrieval_failed = sum(1 for v in g2 if v.get("gate2_status") == "retrieval_failed")
    return {
        "total_candidates": total,
        "buckets": dict(buckets),
        "bottleneck": buckets.most_common(1)[0][0] if buckets else None,
        "gate2_assessed": len(g2),
        "gate2_retrieval_failed": retrieval_failed,
        "stored": buckets.get("stored", 0),
        "quarantined": buckets.get("quarantined", 0),
        "abandoned": buckets.get("abandoned_mid_validation", 0),
    }


def print_funnel(log_file: Optional[Path] = None) -> str:
    """Render the funnel as a human-readable string for logging/CLI."""
    s = verdict_summary(log_file)
    lines = ["📊 DISCOVERY FUNNEL", "=" * 50]
    lines.append(f"total candidates: {s['total_candidates']}")
    for bucket, count in sorted(s["buckets"].items(), key=lambda kv: -kv[1]):
        pct = (100.0 * count / s["total_candidates"]) if s["total_candidates"] else 0.0
        marker = "  <-- BOTTLENECK" if bucket == s["bottleneck"] else ""
        lines.append(f"  {bucket:38s} {count:5d}  ({pct:5.1f}%){marker}")
    if s["gate2_assessed"]:
        lines.append(f"gate-2 retrieval failures: {s['gate2_retrieval_failed']}/{s['gate2_assessed']}")
    text = "\n".join(lines)
    logger.info(text)
    return text


__all__ = ["log_verdict", "verdict_summary", "print_funnel", "VERDICT_LOG"]
