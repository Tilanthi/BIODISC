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
"""Emit LaTeX tables for the Traffic paper from traffic_results.json.

Writes tab_*.tex fragments; the paper \\input{}s them so numbers are
never hand-transcribed.
"""

import json

import numpy as np

HERE = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/Traffic"
R = json.load(open(f"{HERE}/traffic_results.json"))

LBL = {"BOARD": "board", "NODECAY": "no-decay",
       "CENTRAL": "central", "NEAREST": "nearest"}


def agg(block, cfg=""):
    return {r["arm"]: r for r in R[block]["agg"] if r["cfg"] == cfg}


def f(x, nd=1):
    if x is None:
        return "--"
    if isinstance(x, (int, np.integer)):
        return f"{x:,}"
    return f"{x:.{nd}f}"


# ------------------------------------------------------------- E1 baseline
def tab_e1():
    a15, a5 = agg("E1_baseline", "cyc15"), agg("E1_baseline", "cyc5")
    rows = []
    for arm, tag in (("BOARD", ""), ("NODECAY", ""),
                     ("CENTRAL", "cyc5"), ("CENTRAL", "cyc15"),
                     ("NEAREST", "")):
        d = a5[arm] if tag == "cyc5" else a15[arm] if tag == "cyc15" \
            else agg("E1_baseline", "")[arm]
        name = LBL[arm] + (f" ({tag})" if tag else "")
        rows.append(
            f"{name} & {f(d['served'],0)} & {f(d['stranded'],1)} & "
            f"{f(d['unmet'],0)} & {f(d['wait_mean'])} & {f(d['wait_p95'],0)} & "
            f"{f(d['jain'],2)} & {f(d['stall_util'],2)} & "
            f"{f(d['cand_per_query']) if arm in ('BOARD','NODECAY') else '--'} \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Baseline (S1), $n=10^4$, $m=250$, demand $\\delta=2.4$; mean of
10 seeds.  Central sees perfect fresh information; its 5- and 15-min
cycle variants bracket the batching latency.  $k$ = vicinity stations
per query.}}
\\label{{tab:e1}}
\\begin{{tabular}}{{@{{}}lrrrrrrrr@{{}}}}
\\toprule
arm & served & strand & unmet & wait & p95 & Jain & util & $k$ \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    open(f"{HERE}/tab_e1.tex", "w").write(tex)


# --------------------------------------------------------- E3 / E4 / E6
def tab_rob():
    out = {}
    for blk, tag, cap, lbl, norecl in (
            ("E3_outage", "outage",
             "Wholesale decline (S3): 40\\% of stations dead hours 8--14.",
             "tab:e3out", False),
            ("E3_drop", "drop",
             "Report loss (S2): $p_{\\rm drop}=0.25$.", "tab:e3drop", False),
            ("E4_noshow", "noshow",
             "No-shows (S5): $p_{\\rm ns}=0.15$; the no-reclaim row never "
             "releases abandoned bookings (stalls idle out their window).",
             "tab:e4ns", True),
            ("E4_longtail", "longtail",
             "Session overruns (S4): lognormal $\\sigma=0.6$.", "tab:e4lt",
             True)):
        a = agg(blk, tag)
        rows = []
        for arm in ("BOARD", "NODECAY", "CENTRAL", "NEAREST"):
            d = a[arm]
            rows.append(
                f"{LBL[arm]} & {f(d['served'],0)} & {f(d['stranded'],1)} & "
                f"{f(d['unmet'],0)} & {f(d['wait_mean'])} & "
                f"{f(d['wait_p95'],0)} & {f(d['jain'],2)} & "
                f"{f(d['stall_util'],2)} & {f(d['reclaim_release'],0)} \\\\")
        if norecl:
            d = agg(blk, f"{tag}-norecl")["BOARD"]
            rows.append(
                f"no-reclaim & {f(d['served'],0)} & {f(d['stranded'],1)} & "
                f"{f(d['unmet'],0)} & {f(d['wait_mean'])} & "
                f"{f(d['wait_p95'],0)} & {f(d['jain'],2)} & "
                f"{f(d['stall_util'],2)} & {f(d['reclaim_release'],0)} \\\\")
        body = "\n".join(rows)
        out[blk] = f"""\\begin{{table}}
\\centering
\\caption{{{cap}  Mean of 10 seeds.  reclaim = abandoned bookings
dissolved by the decay TTL; for the no-reclaim row the same column
counts window-end sweeps.}}
\\label{{{lbl}}}
\\begin{{tabular}}{{@{{}}lrrrrrrrr@{{}}}}
\\toprule
arm & served & strand & unmet & wait & p95 & Jain & util & reclaim \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
        open(f"{HERE}/tab_{blk}.tex", "w").write(out[blk])


# --------------------------------------------------------------- E5 fraud
def tab_e5():
    rows = R["E5_fraud"]["rows"]
    lines = []
    for rho in (0.0, 0.05, 0.2):
        for att in (True, False):
            rs = [r for r in rows if r["fraud"] == rho and r["attest"] == att]
            m = lambda k: np.mean([r[k] for r in rs])
            lines.append(
                f"{int(rho*100)}\\% & {'on' if att else 'off'} & "
                f"{m('honest_wait_mean'):.1f} & {m('dire_wait_mean'):.1f} & "
                f"{m('fraud_prio_served'):.0f} & {m('fraud_caught'):.0f} & "
                f"{m('stranded'):.1f} & {m('preemptions'):.0f} \\\\")
    body = "\n".join(lines)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Priority channel under fraud (S6), board arm, 30 medical
preemptions/day, mean of 10 seeds.  Honest wait = mean wait of
non-fraudulent EVs; fraud served = false dire claims that received
priority service.}}
\\label{{tab:e5}}
\\begin{{tabular}}{{@{{}}lr rrrrrr@{{}}}}
\\toprule
$\\rho$ & attest & honest & dire & fraud & caught & strand & preempt \\\\
 & & wait & wait & served & & & \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    open(f"{HERE}/tab_e5.tex", "w").write(tex)


# --------------------------------------------------------------- E6 herding
def tab_e6():
    a = {r["cfg"]: r for r in R["E6_herding"]["agg"]}
    on, off = a["beam1"], a["beam0"]
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Attractor-beam herding probe (S3 outage + board arm, mean of
10 seeds).  Max queue is the worst station queue in the run.}}
\\label{{tab:e6}}
\\begin{{tabular}}{{@{{}}lrrrrr@{{}}}}
\\toprule
beam & strand & wait & p95 & Jain & max queue \\\\
\\midrule
on  & {f(on['stranded'],1)} & {f(on['wait_mean'])} & {f(on['wait_p95'],0)} & {f(on['jain'],2)} & {f(on['max_queue'],0)} \\\\
off & {f(off['stranded'],1)} & {f(off['wait_mean'])} & {f(off['wait_p95'],0)} & {f(off['jain'],2)} & {f(off['max_queue'],0)} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    open(f"{HERE}/tab_e6.tex", "w").write(tex)


# ------------------------------------------------------------------ E2
def tab_e2():
    rows = R["E2_scaling"]["rows"]
    lines = []
    for n in sorted({r["n_ev"] for r in rows}):
        b = [r for r in rows if r["n_ev"] == n and r["arm"] == "BOARD"]
        c = [r for r in rows if r["n_ev"] == n and r["arm"] == "CENTRAL"]
        k = np.mean([r["cand_per_query"] for r in b])
        ck = np.mean([r["central_ops"] / max(r["queries"], 1) for r in c])
        w = np.mean([r["wall_s"] for r in b])
        lines.append(f"{n:,} & {k:.1f} & {ck:.0f} & {w:.1f} \\\\")
    body = "\n".join(lines)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Scaling (E2): stations fixed at $m=250$ while the fleet grows
$20\\times$; mean of 3 seeds.  $k$ = vicinity stations scored per query;
central = stations scanned per query-equivalent; wall = simulator
minutes-per-run proxy (single core).}}
\\label{{tab:e2}}
\\begin{{tabular}}{{@{{}}rrrr@{{}}}}
\\toprule
$n$ & board $k$ & central scans & wall (s) \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    open(f"{HERE}/tab_e2.tex", "w").write(tex)


if __name__ == "__main__":
    tab_e1()
    tab_rob()
    tab_e5()
    tab_e6()
    tab_e2()
    print("wrote tab_*.tex")
