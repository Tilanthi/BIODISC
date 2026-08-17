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
"""Experiment driver for the Board-protocol simulator (Phase IV).

E1  baseline: four arms (plus fast central) under a loaded city
E2  scaling: N = 500..10 000 at fixed M = 250 -- per-query work flat?
E3  robustness: wholesale outage (40% of stations, 8 h) and report loss
E4  no-shows and session overruns: decay-reclaim self-healing
E5  priority + fraud: attestation and budget under selfish claims
E6  herding: attractor beam on/off during the outage

Each cell is a mean over seeds; JSON -> traffic_results.json.
Multiprocessing over cells.
"""

from __future__ import annotations

import json
import time
from multiprocessing import Pool

from board_sim import run_arm

BASE = dict(n_ev=10_000, n_st=250, drain_scale=2.4)
SEEDS = list(range(10))
SEEDS3 = list(range(3))
KEYS = ("served", "stranded", "unmet", "wait_mean", "wait_p95",
        "honest_wait_mean", "dire_wait_mean", "jain", "stall_util",
        "cand_per_query", "central_ops", "queries", "walkins", "reroutes",
        "reclaim_release", "max_queue", "book_race",
        "invariant_violation", "fraud_prio_served", "fraud_caught",
        "preemptions", "genuine_prio", "energy_kwh")


def cell(job):
    """One (arm, kwargs-with-cfg-tag, seed) run."""
    arm, kw, seed = job
    cfg = kw.get("cfg", "")
    sim_kw = {k: v for k, v in kw.items() if k != "cfg"}
    t0 = time.perf_counter()
    d = run_arm(arm, seed=seed, **sim_kw)
    d["wall_s"] = round(time.perf_counter() - t0, 2)
    d["arm"], d["seed"], d["cfg"] = arm, seed, cfg
    for k in ("n_ev", "fraud", "attest"):
        if k in kw:
            d[k] = kw[k]
    return d


def _mean(rs, k):
    vals = [r[k] for r in rs if k in r]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)


def block(name, jobs, show=KEYS):
    """Run cells; aggregate per (arm, cfg); print a compact table."""
    with Pool(8) as p:
        rows = p.map(cell, jobs)
    agg = {}
    for r in rows:
        agg.setdefault((r["arm"], r["cfg"]), []).append(r)
    out = []
    for (arm, cfg), rs in sorted(agg.items()):
        m = {k: _mean(rs, k) for k in KEYS if rs and k in rs[0]}
        m.update(arm=arm, cfg=cfg, n_seeds=len(rs),
                 wall_s=_mean(rs, "wall_s"))
        out.append(m)
        print(f"  {name} {arm:8s} {cfg:12s} "
              f"served={m['served']:.0f} strand={m['stranded']:.1f} "
              f"wait={m['wait_mean']:.1f} p95={m['wait_p95']:.0f} "
              f"jain={m['jain']:.2f} util={m['stall_util']:.2f}",
              flush=True)
    return dict(rows=rows, agg=out)


def main():
    t0 = time.perf_counter()
    results = {}

    # ---- E1 baseline -------------------------------------------------
    jobs = []
    for arm, cfg, extra in (("BOARD", "", {}),
                            ("NODECAY", "", {}),
                            ("CENTRAL", "cyc15",
                             dict(central_cycle=15)),
                            ("CENTRAL", "cyc5", dict(central_cycle=5)),
                            ("NEAREST", "", {})):
        jobs += [(arm, {**BASE, **extra, "cfg": cfg}, s) for s in SEEDS]
    results["E1_baseline"] = block("E1", jobs)

    # ---- E2 scaling ----------------------------------------------------
    rows = []
    for n in (500, 1000, 2000, 5000, 10000):
        jobs = [(arm, dict(n_ev=n, n_st=250, drain_scale=2.4, cfg=f"N{n}"),
                 s) for arm in ("BOARD", "CENTRAL") for s in SEEDS3]
        with Pool(6) as p:
            rows += p.map(cell, jobs)
        b = [r for r in rows if r["cfg"] == f"N{n}" and r["arm"] == "BOARD"]
        c = [r for r in rows if r["cfg"] == f"N{n}" and r["arm"] == "CENTRAL"]
        print(f"E2 N={n:6d}: k={_mean(b, 'cand_per_query')} "
              f"central_ops={_mean(c, 'central_ops'):.3g} "
              f"wall={_mean(b, 'wall_s')}s", flush=True)
    results["E2_scaling"] = dict(rows=rows)

    # ---- E3 robustness --------------------------------------------------
    for tag, extra in (("outage", dict(outage=(480, 840))),
                       ("drop", dict(drop=0.25))):
        jobs = []
        for arm in ("BOARD", "NODECAY", "CENTRAL", "NEAREST"):
            jobs += [(arm, {**BASE, **extra, "cfg": tag}, s) for s in SEEDS]
        results[f"E3_{tag}"] = block(f"E3-{tag}", jobs)

    # ---- E4 no-shows / overruns -----------------------------------------
    for tag, extra in (("noshow", dict(noshow=0.15)),
                       ("longtail", dict(longtail=0.6))):
        jobs = []
        for arm in ("BOARD", "NODECAY", "CENTRAL", "NEAREST"):
            jobs += [(arm, {**BASE, **extra, "cfg": tag}, s) for s in SEEDS]
        results[f"E4_{tag}"] = block(f"E4-{tag}", jobs)

    # ---- E5 priority + fraud ---------------------------------------------
    jobs = []
    for fraud in (0.0, 0.05, 0.2):
        for attest in (True, False):
            kw = {**BASE, "fraud": fraud, "attest": attest,
                  "preempt_events": 30, "cfg": f"f{fraud}_a{int(attest)}"}
            jobs += [("BOARD", kw, s) for s in SEEDS]
    results["E5_fraud"] = block("E5", jobs)

    # ---- E6 herding ---------------------------------------------------
    jobs = []
    for beam in (True, False):
        kw = {**BASE, "outage": (480, 840), "beam": beam,
              "cfg": f"beam{int(beam)}"}
        jobs += [("BOARD", kw, s) for s in SEEDS]
    results["E6_herding"] = block("E6", jobs)

    with open("traffic_results.json", "w") as f:
        json.dump(results, f, indent=1)
    print(f"done in {time.perf_counter() - t0:.0f}s -> traffic_results.json")


if __name__ == "__main__":
    main()
