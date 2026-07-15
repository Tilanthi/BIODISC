"""RSI miner — mine discovery failures into gated, *measured* fixes.

This is the recursive-self-improvement loop from "Unleashing the Beast" (§6),
translated to BIODISC's domain. The discovery verdict log
(``discovery_verdicts.jsonl``) is our "surprise ledger": one structured record
per candidate recording where it died (the gate / reason / outcome). This module:

  1. MINES the verdict log, clustering rejected candidates into recurring failure
     themes (significance_failed, duplicate_profile, organism_mismatch,
     literature_known, no_datasets, …) with per-day recurrence rates.
  2. PROPOSES a concrete, human-gated fix per theme (a gate change, an ontology
     expansion, a question/dataset-pinning tweak) — written to a ranked queue.
  3. MEASURES whether an applied fix actually reduced its failure class: it splits
     the verdict log at the fix's apply-date, counts theme-matching failures
     before vs after, and computes a per-day recurrence drop → an effectiveness
     score 0–100. This is the part that makes it a loop and not a suggestion box.
  4. ROLLS the effectiveness up into a single number that a capability index is
     designed to ingest — *even when it lowers the headline* (the Beast design
     property worth copying: instruments that ingest inputs which can reduce
     their own headline number).

Honesty properties, by construction:
  * Propose-only. It never edits core code, gates, prompts, or the chokepoint.
    Applying a fix is a human-gated act; the miner only records that an id/theme
    was applied (``rsi_proposals_applied.jsonl``) so its effect can be measured.
  * Every number is computed from the fleet's own recorded artifacts. A system
    that stopped logging its failures would look healthier on these instruments
    for worse behavior — so the miner surfaces verdict coverage as an explicit
    honesty check.
  * "Improving, not solved." Effectiveness reports the recurrence drop, not
    elimination; a class that merely got rarer scores below 100, and a class that
    did not drop scores 0.

Dependency-free: Python standard library only.
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERDICT_LOG = PROJECT_ROOT / "discovery_verdicts.jsonl"
PROPOSALS_MD = PROJECT_ROOT / "rsi_proposals.md"
APPLIED_JSONL = PROJECT_ROOT / "rsi_proposals_applied.jsonl"
MEASUREMENTS_MD = PROJECT_ROOT / "rsi_measurements.md"
EFFECTIVENESS_TXT = PROJECT_ROOT / "rsi_effectiveness.txt"

# Each theme: (name, keyword phrases matched against the verdict reason, a
# concrete proposed fix, whether applying it needs human approval). Anything that
# touches verification gates, the chokepoint, or data provenance is approval-gated
# by default. Order matters only for readability; matching is independent (a
# verdict with multiple failure reasons contributes to each theme it matches).
THEME_TAXONOMY: List[Tuple[str, List[str], str, bool]] = [
    ("significance_failed",
     ["significance failed", "no genes", "best fdr", "fdr significance"],
     "Review DE parameters (effect-size floor, FDR threshold, min-read filter); "
     "many matched question/dataset pairs still yield too few significant genes.",
     True),
    ("duplicate_profile",
     ["duplicate", "identical statistical profile", "template pattern"],
     "Broaden question/dataset diversity or perturb DE so repeated pairs yield "
     "distinct statistical profiles (the small dataset pool is the deeper cause).",
     True),
    ("organism_mismatch",
     ["organism mismatch"],
     "Expand the organism normalization map (common-name <-> Latin synonyms).",
     True),
    ("tissue_mismatch",
     ["tissue mismatch"],
     "Expand the tissue ontology map, or add a dataset matching this tissue.",
     True),
    ("disease_mismatch",
     ["disease mismatch"],
     "Expand the disease ontology map (e.g. distinguish cancer subtypes).",
     True),
    ("dataset_question_mismatch",
     ["dataset-question", "dataset question"],
     "Tighten question<->dataset pinning, or add the matching dataset.",
     True),
    ("literature_known",
     ["literature known", "entailed by pubmed", "entailed by literature"],
     "Reframe the question toward a less-established, more context-conditional angle.",
     False),
    ("probe_gene_failed",
     ["probe id", "probe-gene", "probe id detected"],
     "Improve GPL probe->gene mapping coverage for the dataset's platform.",
     True),
    ("no_datasets",
     ["no_datasets"],
     "Add a verified dataset matching this question's biology, or expand the "
     "ontology maps so the question finds a match.",
     False),
    ("generation_failed",
     ["generation_failed", "generation failed"],
     "Root-cause the pre-validation failure (download timeout, gene-symbol "
     "validation, DE setup); treat as a reliability fix.",
     True),
    ("exception",
     ["exception:", "traceback"],
     "Root-cause the exception class; treat as a reliability fix.",
     True),
    ("abandoned_mid_validation",
     ["abandoned_mid_validation"],
     "Reliability: a validation cycle started but never wrote a final verdict — "
     "the process was likely killed mid-validation. Reduce mid-cycle kills "
     "(bound downloads, lengthen watchdog patience, avoid SIGKILL mid-cycle).",
     True),
    ("template_question",
     ["template question"],
     "Retire the generic template question or make it more specific.",
     False),
]

_THEME_FIX = {name: (fix, appr) for name, _kws, fix, appr in THEME_TAXONOMY}


# --------------------------------------------------------------------------- IO

def _parse_epoch(ts) -> Optional[float]:
    """Parse an ISO-8601 or epoch timestamp to seconds. None if unparseable."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return float(ts)
    s = str(ts).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _themes_of(reason: str) -> List[str]:
    """Themes matched by a verdict reason (lowercased substring match)."""
    r = (reason or "").lower()
    hits = [name for name, kws, _f, _a in THEME_TAXONOMY if any(k in r for k in kws)]
    return hits or ["unclassified"]


def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# ------------------------------------------------------------------- dataclasses

_HR = 1.0 / 24.0  # 1 hour in days — minimum window so a sub-day burst doesn't explode the rate


def _span_days(epochs: List[float], lo: Optional[float] = None,
               hi: Optional[float] = None) -> float:
    """Wall-clock span (days) covered by the events, floored at 1 hour."""
    if not epochs:
        return 0.0
    a = min(epochs) if lo is None else lo
    b = max(epochs) if hi is None else hi
    return max(_HR, (b - a) / 86400.0)


@dataclass
class Pattern:
    theme: str
    count: int
    per_day: float
    span_days: float
    proposed_fix: str
    needs_approval: bool
    samples: List[str] = field(default_factory=list)


@dataclass
class Measurement:
    theme: str
    applied_at: str
    before_count: int
    after_count: int
    before_per_day: float
    after_per_day: float
    effectiveness: Optional[float]  # 0-100, or None if unmeasurable
    reason: str


# ------------------------------------------------------------------------- MINE

def _per_day(epochs: List[float]) -> float:
    """Failures per day over the real span they cover (min 1-hour window)."""
    if not epochs:
        return 0.0
    return len(epochs) / _span_days(epochs)


def mine(verdicts: List[dict]) -> List[Pattern]:
    """Cluster rejected verdicts into recurring failure themes (most frequent first)."""
    counts: Counter = Counter()
    samples: defaultdict = defaultdict(list)
    epochs: defaultdict = defaultdict(list)
    for v in verdicts:
        if (v.get("outcome") or "") != "rejected":
            continue
        e = _parse_epoch(v.get("logged_at"))
        for theme in _themes_of(v.get("reason", "")):
            counts[theme] += 1
            if e is not None:
                epochs[theme].append(e)
            if len(samples[theme]) < 3:
                q = (v.get("question") or v.get("reason") or "")[:70]
                samples[theme].append(q)

    patterns = []
    for theme, cnt in counts.most_common():
        fix, appr = _THEME_FIX.get(theme, ("Investigate root cause.", True))
        eps = epochs[theme]
        patterns.append(Pattern(
            theme=theme, count=cnt,
            per_day=round(_per_day(eps), 3), span_days=round(_span_days(eps), 3),
            proposed_fix=fix, needs_approval=appr, samples=samples[theme],
        ))
    return patterns


# ---------------------------------------------------------------------- MEASURE

def measure(applied_records: List[dict], verdicts: List[dict],
            now_epoch: Optional[float] = None) -> List[Measurement]:
    """For each applied fix, measure whether its failure class recurred less.

    Splits the verdict log at each fix's apply-date; counts theme-matching
    rejections before vs after; effectiveness = 100*(1 - after_rate/before_rate),
    clamped to [0, 100]. Returns None-effectiveness when there were no prior
    failures of that class (the fix targeted something that wasn't recurring).
    """
    now_epoch = now_epoch if now_epoch is not None else datetime.now(timezone.utc).timestamp()
    out: List[Measurement] = []
    for rec in applied_records:
        theme = rec.get("theme")
        cutoff = _parse_epoch(rec.get("applied_at"))
        if not theme or cutoff is None:
            continue
        b_epochs: List[float] = []
        a_epochs: List[float] = []
        for v in verdicts:
            if (v.get("outcome") or "") != "rejected":
                continue
            if theme not in _themes_of(v.get("reason", "")):
                continue
            e = _parse_epoch(v.get("logged_at"))
            if e is None:
                continue
            (a_epochs if e >= cutoff else b_epochs).append(e)

        before_rate = _per_day_rate(b_epochs, cutoff, before=True)
        after_rate = _per_day_rate(a_epochs, cutoff, before=False, now_epoch=now_epoch)

        if before_rate > 0:
            eff = max(0.0, min(100.0, 100.0 * (1.0 - after_rate / before_rate)))
            reason = (f"{before_rate:.2f}/day -> {after_rate:.2f}/day "
                      f"({len(b_epochs)} -> {len(a_epochs)} events)")
        elif not b_epochs:
            eff = None
            reason = "no prior failures of this class — effect unmeasurable"
        else:  # prior events but rate rounded to 0 over a long span
            eff = 100.0 if not a_epochs else 0.0
            reason = f"prior {len(b_epochs)} events; {len(a_epochs)} after"

        out.append(Measurement(
            theme=theme, applied_at=str(rec.get("applied_at")),
            before_count=len(b_epochs), after_count=len(a_epochs),
            before_per_day=round(before_rate, 3), after_per_day=round(after_rate, 3),
            effectiveness=eff, reason=reason,
        ))
    return out


def _per_day_rate(epochs: List[float], cutoff: float, *, before: bool,
                  now_epoch: Optional[float] = None) -> float:
    """Recurrence rate over the relevant window (before: up to cutoff; after: cutoff->now)."""
    if not epochs:
        return 0.0
    if before:
        return len(epochs) / _span_days(epochs, hi=cutoff)
    end = now_epoch if now_epoch is not None else max(epochs)
    return len(epochs) / _span_days(epochs, lo=cutoff, hi=end)


def effectiveness_rollup(measurements: List[Measurement]) -> Optional[float]:
    """Before-count-weighted mean effectiveness over measurable fixes, 0-100.

    Themes with more prior failures weigh more heavily. Returns None if no fix
    was measurable (so a caller can degrade gracefully rather than report 0).
    """
    num = den = 0.0
    for m in measurements:
        if m.effectiveness is None:
            continue
        w = max(1, m.before_count)
        num += m.effectiveness * w
        den += w
    return round(num / den, 1) if den > 0 else None


# ------------------------------------------------------------- output writers

def write_proposals_md(patterns: List[Pattern], path: Path,
                       coverage: Optional[Tuple[int, int]] = None) -> None:
    total = sum(p.count for p in patterns)
    lines = ["# RSI proposals — mined from discovery_verdicts.jsonl", ""]
    lines.append(f"_Candidate failures analyzed: {total}  "
                 f"(themes: {len(patterns)})_")
    if coverage:
        rej, tot = coverage
        lines.append(f"_Verdict coverage: {rej} rejected of {tot} logged "
                     f"({(100 * rej / max(1, tot)):.0f}%) — a system that stops "
                     f"logging failures would look healthier here for worse behavior._")
    lines.append("")
    lines.append("_Propose-only. Applying any [APPROVAL] fix is a human-gated act; "
                 "record it in rsi_proposals_applied.jsonl so its effect can be measured._")
    lines.append("")
    for i, p in enumerate(patterns, 1):
        gate = "[APPROVAL]" if p.needs_approval else "[auto-elig]"
        lines.append(f"## {i}. {p.theme}  {gate}")
        lines.append(f"- occurrences: **{p.count}**  ({p.per_day}/day over {p.span_days}d)")
        lines.append(f"- proposed fix: {p.proposed_fix}")
        if p.samples:
            lines.append("- samples:")
            for s in p.samples:
                lines.append(f"    - {s}")
        lines.append("")
    path.write_text("\n".join(lines))
    logger.info("wrote %d proposals -> %s", len(patterns), path)


def write_measurements_md(measurements: List[Measurement], rollup: Optional[float],
                          path: Path) -> None:
    lines = ["# RSI measurements — did the applied fixes work?", ""]
    if not measurements:
        lines.append("_No applied fixes recorded in rsi_proposals_applied.jsonl yet._")
    for m in measurements:
        eff = "n/a" if m.effectiveness is None else f"{m.effectiveness:.1f}/100"
        lines.append(f"## {m.theme}  (applied {m.applied_at})")
        lines.append(f"- before -> after: {m.before_count} -> {m.after_count} events  "
                     f"({m.before_per_day}/day -> {m.after_per_day}/day)")
        lines.append(f"- effectiveness: **{eff}**  ({m.reason})")
        lines.append("")
    if rollup is not None:
        lines.append(f"**RSI effectiveness roll-up: {rollup}/100** "
                     "_(before-count-weighted; improving, not solved)_")
    else:
        lines.append("_No measurable applied fixes yet (roll-up n/a)._")
    lines.append("")
    path.write_text("\n".join(lines))
    logger.info("wrote measurements -> %s (rollup=%s)", path, rollup)


def write_effectiveness_txt(rollup: Optional[float], path: Path) -> None:
    """Single roll-up value a capability index can ingest. Empty file = degrade."""
    path.write_text("" if rollup is None else f"{rollup:.1f}")


# ------------------------------------------------------------------------- CLI

def _coverage(verdicts: List[dict]) -> Tuple[int, int]:
    rej = sum(1 for v in verdicts if (v.get("outcome") or "") == "rejected")
    return rej, len(verdicts)


def run(verdict_path: Path = VERDICT_LOG, applied_path: Path = APPLIED_JSONL,
        write: bool = True) -> dict:
    """Mine + measure in one pass. Returns a summary dict."""
    # Read through the dedup reader so provisional+final verdict pairs collapse to
    # one record (and orphaned provisionals surface as `abandoned_mid_validation`).
    try:
        from biodisc_core.fixed_pipeline.verdict_log import read_verdicts_dedup
        verdicts = read_verdicts_dedup(verdict_path)
    except Exception:  # noqa: BLE001 - fall back to raw read if dedup unavailable
        verdicts = read_jsonl(verdict_path)
    patterns = mine(verdicts)
    applied = read_jsonl(applied_path)
    measurements = measure(applied, verdicts)
    rollup = effectiveness_rollup(measurements)
    if write:
        write_proposals_md(patterns, PROPOSALS_MD, coverage=_coverage(verdicts))
        write_measurements_md(measurements, rollup, MEASUREMENTS_MD)
        write_effectiveness_txt(rollup, EFFECTIVENESS_TXT)
    return {
        "verdicts": len(verdicts),
        "rejected": _coverage(verdicts)[0],
        "patterns": len(patterns),
        "applied_fixes": len(applied),
        "measurable_fixes": sum(1 for m in measurements if m.effectiveness is not None),
        "effectiveness_rollup": rollup,
        "top_themes": [(p.theme, p.count, p.per_day) for p in patterns[:5]],
    }


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Mine discovery verdicts into gated, measured fixes.")
    p.add_argument("--mine", action="store_true", help="mine verdict log -> rsi_proposals.md")
    p.add_argument("--measure", action="store_true", help="measure applied fixes -> rsi_measurements.md")
    p.add_argument("--verdict-log", default=str(VERDICT_LOG))
    p.add_argument("--applied", default=str(APPLIED_JSONL))
    args = p.parse_args(argv)

    try:
        from biodisc_core.fixed_pipeline.verdict_log import read_verdicts_dedup
        verdicts = read_verdicts_dedup(Path(args.verdict_log))
    except Exception:  # noqa: BLE001
        verdicts = read_jsonl(Path(args.verdict_log))
    if args.mine or not args.measure:
        patterns = mine(verdicts)
        write_proposals_md(patterns, PROPOSALS_MD, coverage=_coverage(verdicts))
        print(f"[mine] {len(patterns)} themes from {len(verdicts)} verdicts "
              f"({_coverage(verdicts)[0]} rejected). Top: "
              f"{[(t.theme, t.count) for t in patterns[:3]]}")
    if args.measure or not args.mine:
        applied = read_jsonl(Path(args.applied))
        measurements = measure(applied, verdicts)
        rollup = effectiveness_rollup(measurements)
        write_measurements_md(measurements, rollup, MEASUREMENTS_MD)
        write_effectiveness_txt(rollup, EFFECTIVENESS_TXT)
        print(f"[measure] {len(measurements)} applied fixes; rollup={rollup}")
    return 0


__all__ = [
    "mine", "measure", "effectiveness_rollup", "run", "main",
    "Pattern", "Measurement", "THEME_TAXONOMY",
]


if __name__ == "__main__":
    raise SystemExit(main())
