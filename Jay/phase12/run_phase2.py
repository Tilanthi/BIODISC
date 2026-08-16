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
"""Phase II pilot: digital wound sandbox (Appendix B).

Deliverables, each mapped to a Phase II commitment in Sec. 4.2:

  P2-A  2^5 P1-P5 factorial knockout on the infection scenario:
        failure-rate regression with bootstrap CIs and the three named
        interactions (P3xP5, P2xP4, P1xP2)
  P2-B  six arms (hormonal / fixed / measured / backpressure / gossip /
        oracle) x three scenarios (injury / infection / chronic) at
        matched seeds, with the cost vector
  P2-C  H1 scaling: demand mass sweep -- time-to-resolve and failure
        for hormonal vs fixed (the sandbox face of the no-P3 ceiling)
  P2-D  H2 fibrosis: chronic release with and without P5 (antagonist
        termination) -- post-release pool and production
  P2-E  H2b adversarial recruitment: false-signal rate x P4 guard --
        false burn and resolve time
  P2-F  H3 coordinator denial / churn: oracle under outages vs the
        physical residual; churn sweep on the hormonal arm

Outputs: phase2_results.json (+ console log).
"""

from __future__ import annotations

import itertools
import json
import sys
import time

import numpy as np

sys.path.insert(0, "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/phase12")
from sandbox import WoundSandbox

OUT = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/phase12"
SEEDS = 30

SCEN = {
    # injury: one-shot demand mass (default r_demand = 6)
    "injury": dict(),
    # infection: demand refills at a constant per-site rate
    "infection": dict(refill=0.02),
    # chronic: refilling demand that eventually clears at t = 6 tau
    "chronic": dict(refill=0.02, release_t=120.0, T_end=320.0),
}
RUN_KW = dict(e_s=60.0, e_c=30.0, chi=6.0)      # calibrated field scales


def cell(scenario="infection", seeds=SEEDS, **kw):
    sb = WoundSandbox(seeds=seeds, **{**SCEN[scenario], **RUN_KW, **kw})
    return sb.run()


# ---------------------------------------------------------------------- P2-A
def factorial():
    """2^5 knockout design on the infection scenario.

    Response per cell: failure indicator per seed (and unmet rate).
    OLS on cell means with main effects + the three named interactions;
    bootstrap over seeds for CIs.
    """
    names = ["P1", "P2", "P3", "P4", "P5"]
    cells = []
    for bits in itertools.product([0, 1], repeat=5):
        kw = dict(p1=bool(bits[0]), p2=bool(bits[1]), p3=bool(bits[2]),
                  p4=bool(bits[3]), p5=bool(bits[4]))
        out = cell("infection", **kw)
        cells.append(dict(bits=bits, fail=out["failure"], unmet=out[
            "unmet_rate"], resolved=np.where(np.isfinite(out["resolved_t"]),
                                             out["resolved_t"], out["T"])))
        print(f"  {''.join(map(str, bits))} fail={out['failure'].mean():.2f}"
              f" unmet={out['unmet_rate'].mean():.3f}")
    # design matrix: intercept, 5 mains, 3 named interactions
    B = np.array([c["bits"] for c in cells], float)
    cols = ["int"] + names + ["P3:P5", "P2:P4", "P1:P2"]
    X = np.column_stack([np.ones(32), B,
                         B[:, 2] * B[:, 4], B[:, 1] * B[:, 3],
                         B[:, 0] * B[:, 1]])
    yf = np.array([c["fail"].mean() for c in cells])
    yu = np.array([c["unmet"].mean() for c in cells])
    beta_f = np.linalg.lstsq(X, yf, rcond=None)[0]
    beta_u = np.linalg.lstsq(X, yu, rcond=None)[0]
    # bootstrap: resample seeds within each cell, refit
    rng = np.random.default_rng(11)
    boot_f = np.empty((500, X.shape[1]))
    boot_u = np.empty((500, X.shape[1]))
    for b in range(500):
        yb_f = np.array([c["fail"][rng.integers(0, c["fail"].size,
                                                 c["fail"].size)].mean()
                         for c in cells])
        yb_u = np.array([c["unmet"][rng.integers(0, c["unmet"].size,
                                                 c["unmet"].size)].mean()
                         for c in cells])
        boot_f[b] = np.linalg.lstsq(X, yb_f, rcond=None)[0]
        boot_u[b] = np.linalg.lstsq(X, yb_u, rcond=None)[0]
    def pack(beta, boot):
        return {c: dict(est=float(beta[i]),
                        lo=float(np.percentile(boot[:, i], 2.5)),
                        hi=float(np.percentile(boot[:, i], 97.5)))
                for i, c in enumerate(cols)}
    return dict(cols=cols, failure=pack(beta_f, boot_f),
                unmet=pack(beta_u, boot_u),
                cells=[dict(bits="".join(map(str, c["bits"])),
                            fail=float(c["fail"].mean()),
                            unmet=float(c["unmet"].mean()))
                       for c in cells])


# ---------------------------------------------------------------------- P2-B
def arms():
    out = {}
    for scen in ("injury", "infection", "chronic"):
        out[scen] = {}
        for arm in ("hormonal", "fixed", "measured", "backpressure",
                    "gossip", "oracle"):
            o = cell(scen, policy=arm)
            rt = np.where(np.isfinite(o["resolved_t"]), o["resolved_t"],
                          o["T"])
            out[scen][arm] = dict(
                fail=float(o["failure"].mean()),
                resolve_med=float(np.median(rt)),
                unmet=float(o["unmet_rate"].mean()),
                N_peak_over_base=float(np.median(o["N_peak"]
                                                 / o["N_base"])),
                N_end_over_base=float(np.median(o["N_end"]
                                                / o["N_base"])),
                u_peak_over_u0=float(np.median(o["u_peak"] / o["u0"])),
                produced_over_base=float(np.median(o["produced"]
                                                   / o["N_base"])),
                cost=o["cost"])
            print(f"  {scen:9s} {arm:12s} fail={out[scen][arm]['fail']:.2f}"
                  f" res={out[scen][arm]['resolve_med']:6.1f}"
                  f" unmet={out[scen][arm]['unmet']:.3f}")
    return out


# ---------------------------------------------------------------------- P2-C
def h1_scaling():
    """Demand-mass sweep: the hormonal arm scales, fixed hits its ceiling."""
    rows = []
    for rd in (2.0, 4.0, 6.0, 8.0, 10.0, 12.0):
        for arm in ("hormonal", "fixed"):
            o = cell("injury", policy=arm, r_demand=rd)
            rt = np.where(np.isfinite(o["resolved_t"]), o["resolved_t"],
                          o["T"])
            rows.append(dict(r_demand=rd, arm=arm,
                             fail=float(o["failure"].mean()),
                             resolve_med=float(np.median(rt)),
                             unmet=float(o["unmet_rate"].mean()),
                             u_peak_over_u0=float(np.median(o["u_peak"]
                                                            / o["u0"]))))
            print(f"  D={rd:4.1f} {arm:9s} fail={rows[-1]['fail']:.2f}"
                  f" res={rows[-1]['resolve_med']:6.1f}"
                  f" u_pk/u0={rows[-1]['u_peak_over_u0']:5.1f}")
    return dict(rows=rows)


# ---------------------------------------------------------------------- P2-D
def h2_fibrosis():
    """Chronic scenario: demand clears at t=6 tau; P5 decides whether the
    system stands down."""
    out = {}
    for p5 in (True, False):
        o = cell("chronic", policy="hormonal", p5=p5)
        rt = np.where(np.isfinite(o["resolved_t"]), o["resolved_t"], o["T"])
        out["P5 on" if p5 else "P5 off"] = dict(
            fail=float(o["failure"].mean()),
            resolve_med=float(np.median(rt)),
            unmet=float(o["unmet_rate"].mean()),
            N_end_over_base=float(np.median(o["N_end"] / o["N_base"])),
            N_peak_over_base=float(np.median(o["N_peak"] / o["N_base"])),
            u_end_over_u0=float(np.median(o["u_end"] / o["u0"])),
            osc=float(np.median(o["osc"])))
        k = "P5 on" if p5 else "P5 off"
        print(f"  {k}: N_end/N0={out[k]['N_end_over_base']:.2f} "
              f"u_end/u0={out[k]['u_end_over_u0']:.2f} "
              f"fail={out[k]['fail']:.2f}")
    return out


# ---------------------------------------------------------------------- P2-E
def h2b_adversarial():
    """False-signal injections vs the P4 co-stimulus guard (injury)."""
    rows = []
    for adv in (0.0, 0.02, 0.05, 0.10, 0.20):
        for p4 in (True, False):
            o = cell("injury", policy="hormonal", p4=p4, adversarial=adv)
            rt = np.where(np.isfinite(o["resolved_t"]), o["resolved_t"],
                          o["T"])
            rows.append(dict(adv=adv, p4=p4,
                             fail=float(o["failure"].mean()),
                             resolve_med=float(np.median(rt)),
                             false_burn=float(np.median(o["false_burn"])),
                             false_held=float(np.median(
                                 o["false_held"]))))
            print(f"  adv={adv:.2f} P4={'on ' if p4 else 'off'} "
                  f"fail={rows[-1]['fail']:.2f} "
                  f"burn={rows[-1]['false_burn']:6.2f} "
                  f"held={rows[-1]['false_held']:6.2f}")
    return dict(rows=rows)


# ---------------------------------------------------------------------- P2-F
def h3_denial():
    """Oracle under coordinator outages vs the physical residual, plus a
    churn sweep on the hormonal arm (infection)."""
    outages = ((0.0, 30.0), (50.0, 90.0))
    out = {"oracle_outage": {}, "churn": {}}
    for arm, kw in [("oracle", dict(policy="oracle",
                                    oracle_outages=outages)),
                    ("oracle_clean", dict(policy="oracle")),
                    ("hormonal", dict(policy="hormonal"))]:
        o = cell("infection", **kw)
        out["oracle_outage"][arm] = dict(
            fail=float(o["failure"].mean()),
            unmet=float(o["unmet_rate"].mean()),
            resolve_med=float(np.median(np.where(
                np.isfinite(o["resolved_t"]), o["resolved_t"], o["T"]))))
        print(f"  {arm:13s} fail={out['oracle_outage'][arm]['fail']:.2f} "
              f"unmet={out['oracle_outage'][arm]['unmet']:.3f}")
    for cf in (0.0, 0.10, 0.30, 0.50):
        o = cell("infection", policy="hormonal", churn_frac=cf,
                 churn_every=100)
        out["churn"][f"{cf:.2f}"] = dict(
            fail=float(o["failure"].mean()),
            unmet=float(o["unmet_rate"].mean()),
            resolve_med=float(np.median(np.where(
                np.isfinite(o["resolved_t"]), o["resolved_t"], o["T"]))))
        print(f"  churn {cf:.2f}: fail={out['churn'][f'{cf:.2f}']['fail']:.2f}"
              f" unmet={out['churn'][f'{cf:.2f}']['unmet']:.3f}")
    return out


# -------------------------------------------------------------------- driver
def main():
    t0 = time.time()
    res = {}
    print("P2-A factorial (32 cells x 30 seeds, infection) ...")
    res["factorial"] = factorial()
    print("P2-B six arms x three scenarios ...")
    res["arms"] = arms()
    print("P2-C H1 demand scaling ...")
    res["h1_scaling"] = h1_scaling()
    print("P2-D H2 fibrosis (chronic release) ...")
    res["h2_fibrosis"] = h2_fibrosis()
    print("P2-E H2b adversarial recruitment ...")
    res["h2b_adversarial"] = h2b_adversarial()
    print("P2-F H3 denial / churn ...")
    res["h3_denial"] = h3_denial()
    res["timing_s"] = time.time() - t0
    with open(f"{OUT}/phase2_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(f"done in {res['timing_s']:.0f}s -> phase2_results.json")


if __name__ == "__main__":
    main()
