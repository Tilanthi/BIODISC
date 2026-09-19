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
"""Gate-2 truth-set calibration — the novelty gate is now itself measured.

Paper2Agent lesson (V9.1): verification machinery must be tested against a
known-answer set, not assumed. ``literature_gate.py``'s similarity threshold
(0.55) was engineering judgment — this module measures it.

Two-sided truth set (``gate2_truth_set.json`` + genuine store):

* **known side** — real textbook claims (TP53-in-cancer, SOD1-in-ALS, …) that
  MUST score ``known``. This is external ground truth: it catches an
  over-permissive gate waving textbook biology through as "novel" (the failure
  that would quietly re-surface established results as discoveries).
* **novel side** — seeded from the genuine store's own questions. These passed
  Gate-2 and replicated, so scoring them ``known`` means the threshold has
  drifted tight enough to kill verified findings. This is regression, not
  external truth (the store was itself gated by Gate-2); hand-authoring
  "novel" claims is deliberately avoided — we cannot verify a hand-written
  claim is absent from PubMed, only that the store's claims survived.

Accuracy is computed per side with ``retrieval_failed`` verdicts EXCLUDED from
both denominators (a network failure is infrastructure health, not gate
accuracy) and counted separately.

Run offline self-check: ``python -m biodisc_core.fixed_pipeline.gate2_calibration``
Run live (real PubMed):  ``python -m biodisc_core.fixed_pipeline.gate2_calibration --live``
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

from .paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
TRUTH_SET_FILE = PROJECT_ROOT / "gate2_truth_set.json"
REPORT_FILE = PROJECT_ROOT / "gate2_calibration_report.json"
GENUINE_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"


def load_truth_set(path: Optional[Path] = None) -> dict:
    p = Path(path) if path is not None else TRUTH_SET_FILE
    return json.loads(p.read_text())


def derive_novel_claims(store_path: Optional[Path] = None, cap: int = 12) -> List[str]:
    """Novel-side claims = the genuine store's own questions (most recent first).

    Genuine tier only — candidates never passed Gate-2's bar, so their
    questions are not known-novel ground truth.
    """
    p = Path(store_path) if store_path is not None else GENUINE_STORE
    out: List[str] = []
    if not p.exists():
        return out
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    for line in reversed(lines):  # most recent first
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        tier = (rec.get("flagging") or {}).get("tier")
        if tier != "genuine" and not rec.get("is_genuine"):
            continue
        q = (rec.get("question") or "").strip()
        if q:
            out.append(q)
        if len(out) >= cap:
            break
    return out


def evaluate(gate, known_claims: List[str], novel_claims: List[str]) -> dict:
    """Score the gate on both sides of the truth set.

    ``gate`` needs only ``assess(claim_text) -> verdict`` with ``.status`` and
    ``.max_similarity`` (the real LiteratureNoveltyGate or a test fake).
    ``retrieval_failed`` verdicts are excluded from the accuracy denominators
    and counted separately.
    """
    per_claim = []
    n_known = known_ok = n_novel = novel_ok = retrieval_failures = 0
    for claim in known_claims:
        v = gate.assess(claim)
        got = getattr(v, "status", "retrieval_failed")
        if got == "retrieval_failed":
            retrieval_failures += 1
        else:
            n_known += 1
            if got == "known":
                known_ok += 1
        per_claim.append({"claim": claim, "expected": "known", "got": got,
                          "max_similarity": getattr(v, "max_similarity", None)})
    for claim in novel_claims:
        v = gate.assess(claim)
        got = getattr(v, "status", "retrieval_failed")
        if got == "retrieval_failed":
            retrieval_failures += 1
        else:
            n_novel += 1
            if got == "novel":
                novel_ok += 1
        per_claim.append({"claim": claim, "expected": "novel", "got": got,
                          "max_similarity": getattr(v, "max_similarity", None)})
    return {
        "known_accuracy": round(known_ok / n_known, 4) if n_known else None,
        "novel_accuracy": round(novel_ok / n_novel, 4) if n_novel else None,
        "n_known": n_known,
        "n_novel": n_novel,
        "known_correct": known_ok,
        "novel_correct": novel_ok,
        "retrieval_failures": retrieval_failures,
        "per_claim": per_claim,
    }


def run(live: bool = False, write: bool = True,
        truth_set_path: Optional[Path] = None,
        store_path: Optional[Path] = None) -> dict:
    """Offline: fetcher-injected self-check (no network). Live: real PubMed."""
    ts = load_truth_set(truth_set_path)
    known = [kc["claim"] for kc in ts.get("known_claims", [])]
    novel = derive_novel_claims(store_path=store_path)

    if live:
        from biodisc_core.fixed_pipeline.literature_gate import create_literature_novelty_gate
        gate = create_literature_novelty_gate()
        mode = "live"
    else:
        gate = _OfflineSelfCheckGate()
        mode = "offline_selfcheck"

    res = evaluate(gate, known, novel)
    report = {
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "threshold": getattr(gate, "similarity_threshold", None),
        "summary": {k: res[k] for k in ("known_accuracy", "novel_accuracy",
                                        "n_known", "n_novel", "retrieval_failures")},
        "known_claims": known,
        "novel_claims": novel,
        "fetcher_injected": mode == "offline_selfcheck",
        **res,
    }
    if write:
        REPORT_FILE.write_text(json.dumps(report, indent=2))
        logger.info("gate2 calibration (%s) -> %s | known_acc=%s novel_acc=%s",
                    mode, REPORT_FILE, res["known_accuracy"], res["novel_accuracy"])
    return report


class _OfflineSelfCheckGate:
    """Offline self-check: exercises the truth-set plumbing with a deterministic
    fetcher-injected verdict, proving the report pipeline works without network.

    Verdicts: claims containing a digit or the word 'paradoxically' (the shape
    of store questions) -> novel; everything else -> known. This is NOT a
    measure of Gate-2 quality — it is a plumbing check; the quality measure is
    the live run.
    """

    similarity_threshold = 0.55

    def assess(self, claim_text: str, question=None, fetcher=None):
        from types import SimpleNamespace as NS
        is_novel_shaped = any(c.isdigit() for c in claim_text) or "paradoxically" in claim_text.lower()
        status = "novel" if is_novel_shaped else "known"
        return NS(status=status, max_similarity=0.5 if status == "known" else 0.1)


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        description="Calibrate Gate-2 (literature novelty) against its truth set.")
    p.add_argument("--live", action="store_true",
                   help="hit real PubMed (default: offline plumbing self-check)")
    p.add_argument("--no-write", action="store_true")
    args = p.parse_args(argv)
    report = run(live=args.live, write=not args.no_write)
    print(json.dumps({k: report[k] for k in
                      ("mode", "threshold", "summary")}, indent=2))
    return 0


__all__ = ["load_truth_set", "derive_novel_claims", "evaluate", "run", "main",
           "TRUTH_SET_FILE", "REPORT_FILE"]


if __name__ == "__main__":
    raise SystemExit(main())
