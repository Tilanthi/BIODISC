#!/usr/bin/env python3
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
"""Pre-registered kill criteria for the bounded field trial.

Written before the rung-1 measurements were taken; thresholds are
frozen here so the trial's exit cannot be chosen post hoc.  Each
criterion names the rung it gates, its measurement, its threshold,
and its verdict semantics:

  CONTINUE   measurement inside the operating envelope
  REVISE     protocol constant must be re-fit before the next rung
  KILL       the protocol's value proposition fails here; stop

Criteria (from the paper's Phase V recommendation):
  K1  T calibration  implied T for f(median age) >= 0.9 must sit in
                     [15, 60] min; outside -> REVISE-T (or KILL if
                     no timestamped feed in the trial area can do
                     better: the law has nothing to read).
  K2  decision value decay-weighted reading must change >= 1% of
                     top-1 routing choices vs trust-everything; below
                     -> KILL rung 1 as a no-op (skip to rung 2 or
                     stop).
  K3  no-show rate   (rung 2) field p_ns > 0.30 (2x the simulator's
                     tested 0.15) -> re-run the reclaim-vs-overbook
                     trade at field rates before rung 2 proceeds.
  K4  fairness floor (rung 2/3) field Jain(wait) < 0.20 sustained for
                     a week -> the structural weakness is field-fatal.
  K5  attestation    (rung 3) genuine dire claims falsely rejected >
                     20% in the pilot -> the priority channel inverts
                     its own value (paper E5).

K3-K5 are registered now and evaluated when their rung's data exists;
until then they report NOT-YET-MEASURED.
"""

import argparse
import json

HERE = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/Traffic/trial"

K1_LO, K1_HI = 15.0, 60.0
K2_MIN_FLIP = 0.01
K3_MAX_NS = 0.30
K4_MIN_JAIN = 0.20
K5_MAX_FALSE_REJ = 0.20


def fmt(x, unit=""):
    if x is None:
        return "--"
    if x >= 10000:
        return f"{x:,.0f}{unit}"
    return f"{x:.4g}{unit}"


def evaluate(reports, rung2=None, rung3=None):
    """reports: list of rung-1 report dicts (one per snapshot)."""
    rows = []

    # ---- K1: T calibration (worst snapshot governs) ---------------------
    for r in reports:
        it = r.get("implied_T_min")
        verdict = "CONTINUE"
        if it is None:
            verdict = "KILL"          # no timestamps at all: nothing to read
        elif it < K1_LO:
            verdict = "REVISE-T"      # fresher than the law assumed
        elif it > K1_HI:
            verdict = "REVISE-T"
        rows.append(dict(
            crit="K1", rung=1, area=r.get("area") or r.get("snapshot"),
            measurement="implied T (f(median age)>=0.9)",
            value=fmt(it, " min"),
            threshold=f"[{K1_LO:.0f}, {K1_HI:.0f}] min",
            verdict=verdict))

    # ---- K2: decision flips (best snapshot governs: any feed where the
    #          law changes decisions keeps the rung alive) ----------------
    best = None
    for r in reports:
        fr = r.get("top1_flip_rate")
        if fr is not None and (best is None or fr > best[0]):
            best = (fr, r)
    if best:
        fr, r = best
        rows.append(dict(
            crit="K2", rung=1, area=r.get("area") or r.get("snapshot"),
            measurement="top-1 flip rate (decay vs trust-all)",
            value=f"{100 * fr:.1f}%",
            threshold=f">= {100 * K2_MIN_FLIP:.0f}%",
            verdict="CONTINUE" if fr >= K2_MIN_FLIP else "KILL"))
    else:
        rows.append(dict(crit="K2", rung=1, area="all",
                         measurement="top-1 flip rate",
                         value="--", threshold=f">= 1%",
                         verdict="KILL"))

    # ---- K3-K5: registered, measured at their rungs ---------------------
    if rung2:
        rows.append(dict(
            crit="K3", rung=2, area=rung2.get("area", "--"),
            measurement="field no-show rate",
            value=fmt(rung2.get("p_ns")),
            threshold=f"<= {K3_MAX_NS:.2f}",
            verdict="CONTINUE" if rung2.get("p_ns", 0) <= K3_MAX_NS
            else "REVISE"))
        rows.append(dict(
            crit="K4", rung=2, area=rung2.get("area", "--"),
            measurement="Jain(wait), weekly",
            value=fmt(rung2.get("jain")),
            threshold=f">= {K4_MIN_JAIN:.2f}",
            verdict="CONTINUE" if rung2.get("jain", 1) >= K4_MIN_JAIN
            else "KILL"))
    else:
        for crit, m in (("K3", "field no-show rate"),
                        ("K4", "Jain(wait), weekly")):
            rows.append(dict(crit=crit, rung=2, area="--",
                             measurement=m, value="--",
                             threshold="registered",
                             verdict="NOT-YET-MEASURED"))
    if rung3:
        rows.append(dict(
            crit="K5", rung=3, area=rung3.get("area", "--"),
            measurement="genuine dire claims falsely rejected",
            value=fmt(rung3.get("false_reject")),
            threshold=f"<= {K5_MAX_FALSE_REJ:.2f}",
            verdict="CONTINUE" if rung3.get("false_reject", 0)
            <= K5_MAX_FALSE_REJ else "KILL"))
    else:
        rows.append(dict(crit="K5", rung=3, area="--",
                         measurement="genuine dire claims falsely rejected",
                         value="--", threshold="registered",
                         verdict="NOT-YET-MEASURED"))
    return rows


def to_tex(rows, path):
    def esc(s):
        return (str(s).replace(">=", r"$\ge$").replace("<=", r"$\le$")
                .replace(">", r"$>$").replace("<", r"$<$")
                .replace("%", r"\%"))
    body = "\n".join(
        f"{esc(r['crit'])} & {r['rung']} & {esc(r['area'])} & "
        f"{esc(r['measurement'])} & "
        f"{esc(r['value'])} & {esc(r['threshold'])} & {esc(r['verdict'])} \\\\"
        for r in rows)
    tex = f"""\\begin{{table}}
\\centering\\small
\\caption{{Pre-registered kill criteria for the bounded field trial,
evaluated on the rung-1 captures (K3--K5 register now, measure at
their rungs).  Verdicts: CONTINUE / REVISE-$T$ / KILL.}}
\\label{{tab:trialkill}}
\\begin{{tabular}}{{@{{}}lllllll@{{}}}}
\\toprule
crit & rung & area & measurement & value & threshold & verdict \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    open(path, "w").write(tex)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reports", nargs="+", required=True)
    ap.add_argument("--rung2", default=None)
    ap.add_argument("--rung3", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tex", default=None)
    args = ap.parse_args()
    reports = [json.load(open(p)) for p in args.reports]
    rung2 = json.load(open(args.rung2)) if args.rung2 else None
    rung3 = json.load(open(args.rung3)) if args.rung3 else None
    rows = evaluate(reports, rung2, rung3)
    json.dump(rows, open(args.out, "w"), indent=1)
    if args.tex:
        to_tex(rows, args.tex)
    for r in rows:
        print(f"  {r['crit']} (rung {r['rung']}) {r['measurement']}: "
              f"{r['value']} vs {r['threshold']} -> {r['verdict']}")


if __name__ == "__main__":
    main()
