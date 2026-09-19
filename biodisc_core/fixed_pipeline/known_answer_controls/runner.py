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
"""Known-answer control runner — re-derive real findings through the REAL analyzer.

For each control case: resolve the dataset's expression data, run the real DE
analyzer, and require the case's verified genes to come back same-direction +
FDR-significant. A case PASSES iff at least ``min_gene_recovery`` of its genes
recover (re-downloaded data can legitimately reshuffle a few marginal genes;
the headline genes must survive).

Honesty properties:
  * statuses are a labeled ladder — a failing control can never look green:
    ``PASS | FAIL_DIRECTION | FAIL_SIGNIFICANCE | FAIL_ABSENT | SKIP_NO_DATA | ERROR``
  * data that cannot be resolved is ``SKIP_NO_DATA`` (counted separately, never
    in the pass rate denominator as a pass)
  * the pass rate is over DECIDED cases (pass + fail) only.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

from ..paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
REPORT_FILE = PROJECT_ROOT / "known_answer_report.json"

# Field-standard significance bar for recovery (matches the pipeline's FDR gate).
RECOVERY_FDR = 0.05
# Fraction of a case's genes that must recover for the case to PASS.
MIN_GENE_RECOVERY = 0.7

Statuses = ("PASS", "FAIL_DIRECTION", "FAIL_SIGNIFICANCE", "FAIL_ABSENT",
            "SKIP_NO_DATA", "ERROR")

DataResolver = Callable[[object], "tuple"]  # case -> (expression, symbols, labels)


def _gene_verdict(exp: dict, by_gene: dict) -> dict:
    """One expected gene vs the fresh DE result -> labeled verdict."""
    r = by_gene.get(exp["symbol"].upper())
    if r is None:
        return {"symbol": exp["symbol"], "expected_direction": exp["direction"],
                "observed_direction": None, "observed_fdr": None, "ok": False,
                "verdict": "FAIL_ABSENT"}
    l2 = getattr(r, "log2_fold_change", 0.0)
    obs_dir = "up" if float(l2) >= 0 else "down"
    fdr = getattr(r, "fdr_p_value", None)
    if obs_dir != exp["direction"]:
        verdict = "FAIL_DIRECTION"
    elif fdr is None or float(fdr) >= RECOVERY_FDR:
        verdict = "FAIL_SIGNIFICANCE"
    else:
        verdict = "ok"
    return {"symbol": exp["symbol"], "expected_direction": exp["direction"],
            "observed_direction": obs_dir, "observed_fdr": fdr,
            "ok": verdict == "ok", "verdict": verdict}


def _default_resolver():
    """Resolve data via the same orchestrator path the live loop uses.

    Bounded by the downloader's own wall-clock/size limits; any failure maps to
    SKIP_NO_DATA (never ERROR — an unreachable dataset is not a pipeline defect).
    """
    def resolve(case):
        from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import (
            create_fixed_discovery_orchestrator)
        orch = create_fixed_discovery_orchestrator()
        return orch.download_real_data_multi_repo(
            dataset_id=case.dataset_id, repository="GEO", n_samples=12, n_genes=2000)
    return resolve


def run_controls(cases=None, data_resolver: Optional[DataResolver] = None,
                 analyzer=None, write: bool = False,
                 min_gene_recovery: float = MIN_GENE_RECOVERY) -> dict:
    from .cases import load_cases
    if cases is None:
        cases = load_cases()
    if data_resolver is None:
        data_resolver = _default_resolver()
    if analyzer is None:
        from biodisc_core.fixed_pipeline.differential_expression import (
            create_differential_expression_analyzer)
        analyzer = create_differential_expression_analyzer()

    results = []
    summary = {"pass": 0, "fail": 0, "skip": 0, "error": 0}
    for case in cases:
        entry = {"case_id": case.case_id, "dataset_id": case.dataset_id,
                 "question": case.question, "genes": [], "reason": ""}
        try:
            try:
                expression, symbols, labels = data_resolver(case)
            except Exception as e:  # noqa: BLE001 - unreachable data != pipeline defect
                entry["status"] = "SKIP_NO_DATA"
                entry["reason"] = f"data unresolved ({type(e).__name__}: {e})"
                summary["skip"] += 1
                results.append(entry)
                continue

            de = analyzer.perform_differential_expression_analysis(
                np.asarray(expression), list(symbols), np.asarray(labels),
                case.question, case.dataset_id)
            by_gene = {str(r.gene_symbol).upper().strip(): r for r in de.results}

            gene_results = [_gene_verdict(g, by_gene) for g in case.genes]
            entry["genes"] = gene_results
            ok_frac = (sum(1 for g in gene_results if g["ok"]) /
                       max(1, len(gene_results)))
            entry["gene_recovery"] = round(ok_frac, 3)
            if ok_frac >= min_gene_recovery:
                entry["status"] = "PASS"
                summary["pass"] += 1
                entry["reason"] = f"{ok_frac:.0%} of verified genes recovered"
            else:
                worst = next((g["verdict"] for g in gene_results
                              if not g["ok"]), "FAIL")
                entry["status"] = worst if worst.startswith("FAIL") else "FAIL_SIGNIFICANCE"
                summary["fail"] += 1
                entry["reason"] = (f"only {ok_frac:.0%} of verified genes recovered "
                                   f"(first failure: {worst})")
        except Exception as e:  # noqa: BLE001 - a crash in the analyzer IS a defect
            entry["status"] = "ERROR"
            entry["reason"] = f"{type(e).__name__}: {e}"
            summary["error"] += 1
        results.append(entry)
        logger.info("known-answer %s -> %s (%s)", case.case_id,
                    entry["status"], entry["reason"])

    decided = summary["pass"] + summary["fail"]
    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_cases": len(results),
        "summary": summary,
        "pass_rate": round(summary["pass"] / decided, 4) if decided else None,
        "min_gene_recovery": min_gene_recovery,
        "results": results,
        "note": ("pass_rate is over DECIDED cases only (skips are infrastructure, "
                 "not pipeline health; errors are defects). A FAIL here means the "
                 "pipeline can no longer recover a finding it already verified."),
    }
    if write:
        REPORT_FILE.write_text(json.dumps(report, indent=2))
        logger.info("known-answer report -> %s (pass_rate=%s)", REPORT_FILE,
                    report["pass_rate"])
    return report


def main(argv=None) -> int:
    import argparse
    from .cases import seed_from_genuine_store, save_cases, load_cases
    p = argparse.ArgumentParser(
        description="Real-data known-answer controls (must-recover suite).")
    p.add_argument("--seed", action="store_true",
                   help="(re)seed known_answer_cases.json from the genuine store")
    p.add_argument("--max-cases", type=int, default=10)
    args = p.parse_args(argv)
    if args.seed:
        cases = seed_from_genuine_store(max_cases=args.max_cases)
        save_cases(cases)
        print(f"[seed] {len(cases)} control cases")
    cases = load_cases()
    if not cases:
        print("[run] no control cases — run with --seed first")
        return 0
    report = run_controls(cases[: args.max_cases], write=True)
    s = report["summary"]
    print(f"[run] pass={s['pass']} fail={s['fail']} skip={s['skip']} "
          f"error={s['error']} pass_rate={report['pass_rate']}")
    for r in report["results"]:
        if r["status"] != "PASS":
            print(f"  {r['status']:18s} {r['case_id']}: {r['reason']}")
    return 0 if (s["fail"] == 0 and s["error"] == 0) else 1


__all__ = ["run_controls", "main", "REPORT_FILE", "Statuses"]
