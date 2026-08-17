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
"""Traffic paper figures.

figT1: (a) staleness law; (b) E2 scaling -- vicinity k and central ops
       per query vs fleet size.
figT2: (a) E3 outage -- stranded and mean wait by arm; (b) E4 no-show --
       stall utilisation and reclaim by arm.
figT3: (a) E5 fraud -- honest wait and undetected fraud service vs
       fraud rate, attestation on/off; (b) E6 herding -- max queue and
       stranded, beam on/off.

Style matches the Jay house style (palette, 84 mm columns).
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from board_sim import conf

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
LINE, HAIR = "#c3c2b7", "#e1e0d9"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "text.color": INK, "axes.edgecolor": LINE,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.labelcolor": INK2, "font.size": 6.5,
})

COL_W, FULL_W = 84 / 25.4, 176 / 25.4
HERE = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/Traffic"


def _despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _load():
    return json.load(open(f"{HERE}/traffic_results.json"))


# ================================================================ FIG T1 ====
def figT1():
    R = _load()
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_W, 1.9))

    # ---- (a) staleness law ------------------------------------------------
    d = np.linspace(0, 34, 200)
    for al, c, lab in ((1.0, MUTED, r"$\alpha=1$ (linear)"),
                       (3.0, BLUE, r"$\alpha=3$ (tested)"),
                       (6.0, ORANGE, r"$\alpha=6$")):
        a.plot(d, conf(d, alpha=al), lw=1.1, color=c, label=lab)
    a.axvline(10, lw=0.6, color=LINE, ls=":")
    a.axvline(20, lw=0.6, color=LINE, ls=":")
    a.text(10, 1.03, r"$2T_r$", fontsize=5.4, ha="center", color=MUTED)
    a.text(20, 1.03, r"$4T_r$", fontsize=5.4, ha="center", color=MUTED)
    a.set_xlabel(r"report age $\Delta$ (min)")
    a.set_ylabel(r"confidence $f(\Delta)$")
    a.set_ylim(0, 1.12)
    a.legend(frameon=False, fontsize=5.4, loc="lower left")
    a.text(0.03, 0.97, "(a)", transform=a.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(a)

    # ---- (b) scaling ------------------------------------------------------
    rows = R["E2_scaling"]["rows"]
    ns = sorted({r["n_ev"] for r in rows})
    k = [np.mean([r["cand_per_query"] for r in rows
                  if r["n_ev"] == n and r["arm"] == "BOARD"]) for n in ns]
    co = [np.mean([r["central_ops"] / max(r["queries"], 1)
                   for r in rows if r["n_ev"] == n
                   and r["arm"] == "CENTRAL"]) for n in ns]
    a2 = b
    a2.plot(ns, k, "o-", lw=1.1, ms=3.2, color=BLUE,
            label=r"board: vicinity $k$ per query")
    a2.plot(ns, co, "s-", lw=1.1, ms=3.2, color=ORANGE,
            label=r"central: stations scanned per query")
    a2.set_xscale("log")
    a2.set_yscale("log")
    a2.set_xlabel(r"fleet size $n$ (stations fixed at $m=250$)")
    a2.set_ylabel("work per vehicle query")
    a2.legend(frameon=False, fontsize=5.4, loc="center left")
    a2.text(0.03, 0.97, "(b)", transform=a2.transAxes, fontsize=7,
            color=INK2, weight="bold", va="top")
    _despine(a2)

    fig.subplots_adjust(left=0.075, right=0.995, top=0.97, bottom=0.19,
                        wspace=0.30)
    fig.savefig(f"{HERE}/figT1_scaling.pdf")
    fig.savefig(f"{HERE}/figT1_scaling.png", dpi=300)
    plt.close(fig)
    print("wrote figT1_scaling.pdf / .png")


# ================================================================ FIG T2 ====
def figT2():
    R = _load()
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_W, 1.9))

    # ---- (a) E3 outage ----------------------------------------------------
    arms = ["BOARD", "NODECAY", "CENTRAL", "NEAREST"]
    lab = ["board", "no-decay", "central", "nearest"]
    ag = {r["arm"]: r for r in R["E3_outage"]["agg"] if r["cfg"] == "outage"}
    x = np.arange(4)
    st = [ag[ar]["stranded"] for ar in arms]
    wt = [ag[ar]["wait_mean"] for ar in arms]
    a.bar(x, st, 0.58, color=BLUE, label="stranded vehicles / day")
    a.set_xticks(x, lab)
    a.set_ylabel("stranded vehicles (mean of 10 seeds)")
    for xi, s in zip(x, st):
        a.text(xi, s + max(st) * 0.03, f"{s:.0f}", ha="center",
               fontsize=5.8, color=INK2)
    a2 = a.twinx()
    a2.plot(x, wt, "s--", ms=3.0, lw=0.9, color=ORANGE)
    a2.set_ylabel("mean wait (min)", color=INK2)
    a2.set_ylim(0, max(wt) * 1.6)
    a2.tick_params(colors=INK2)
    a.text(0.03, 0.97, "(a)", transform=a.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(a); _despine(a2)
    a2.spines["top"].set_visible(False)

    # ---- (b) E4 no-show ---------------------------------------------------
    ag = {r["arm"]: r for r in R["E4_noshow"]["agg"] if r["cfg"] == "noshow"}
    ut = [ag[ar]["stall_util"] for ar in arms]
    rc = [ag[ar]["reclaim_release"] for ar in arms]
    b.bar(x, ut, 0.58, color=AQUA, label="stall utilisation")
    b.set_xticks(x, lab)
    b.set_ylabel("stall utilisation")
    b.set_ylim(0, 0.6)
    b2 = b.twinx()
    b2.plot(x, rc, "o--", ms=3.0, lw=0.9, color=INK)
    b2.set_ylabel("stale bookings reclaimed", color=INK2)
    b2.set_ylim(0, max(rc) * 1.5 if max(rc) > 0 else 1)
    b2.tick_params(colors=INK2)
    b.text(0.03, 0.97, "(b)", transform=b.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(b); _despine(b2)
    b2.spines["top"].set_visible(False)

    fig.subplots_adjust(left=0.085, right=0.92, top=0.97, bottom=0.19,
                        wspace=0.62)
    fig.savefig(f"{HERE}/figT2_robust.pdf")
    fig.savefig(f"{HERE}/figT2_robust.png", dpi=300)
    plt.close(fig)
    print("wrote figT2_robust.pdf / .png")


# ================================================================ FIG T3 ====
def figT3():
    R = _load()
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_W, 1.9))

    # ---- (a) E5 fraud -----------------------------------------------------
    rows = R["E5_fraud"]["rows"]
    fr = sorted({r["fraud"] for r in rows})
    hw = {att: [np.mean([r["honest_wait_mean"] for r in rows
                         if r["fraud"] == f and r["attest"] == att])
                for f in fr] for att in (True, False)}
    fp = {att: [np.mean([r["fraud_prio_served"] for r in rows
                         if r["fraud"] == f and r["attest"] == att])
                for f in fr] for att in (True, False)}
    a.plot(np.array(fr) * 100, hw[True], "o-", lw=1.1, ms=3.2, color=BLUE,
           label="honest wait, attest on")
    a.plot(np.array(fr) * 100, hw[False], "s--", lw=1.1, ms=3.2,
           color=ORANGE, label="honest wait, attest off")
    a.set_xlabel(r"fraud rate $\rho$ (%)")
    a.set_ylabel("mean wait, honest EVs (min)")
    a.legend(frameon=False, fontsize=5.4, loc="upper left")
    a2 = a.twinx()
    a2.plot(np.array(fr) * 100, fp[True], "o:", ms=2.8, lw=0.9, color=INK)
    a2.plot(np.array(fr) * 100, fp[False], "s:", ms=2.8, lw=0.9,
            color=MUTED)
    a2.set_ylabel("fraud served with priority", color=INK2)
    a2.tick_params(colors=INK2)
    a.text(0.03, 0.97, "(a)", transform=a.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(a); _despine(a2)
    a2.spines["top"].set_visible(False)

    # ---- (b) E6 herding ---------------------------------------------------
    ag = {r["cfg"]: r for r in R["E6_herding"]["agg"]}
    on, off = ag["beam1"], ag["beam0"]
    x = np.arange(2)
    b.bar(x - 0.14, [on["stranded"], off["stranded"]], 0.26, color=BLUE,
          label="stranded")
    b.set_xticks(x, ["beam on", "beam off"])
    b.set_ylabel("stranded vehicles")
    b2 = b.twinx()
    b2.bar(x + 0.14, [on["max_queue"], off["max_queue"]], 0.26,
           color=ORANGE, label="max queue")
    b2.set_ylabel("max station queue", color=INK2)
    b2.tick_params(colors=INK2)
    for xi, v in zip(x - 0.14, [on["stranded"], off["stranded"]]):
        b.text(xi, v + 0.5, f"{v:.0f}", ha="center", fontsize=5.8,
               color=INK2)
    for xi, v in zip(x + 0.14, [on["max_queue"], off["max_queue"]]):
        b2.text(xi, v + 0.5, f"{v:.0f}", ha="center", fontsize=5.8,
                color=INK2)
    b.text(0.03, 0.97, "(b)", transform=b.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(b); _despine(b2)
    b2.spines["top"].set_visible(False)

    fig.subplots_adjust(left=0.085, right=0.92, top=0.97, bottom=0.19,
                        wspace=0.62)
    fig.savefig(f"{HERE}/figT3_fraud_herd.pdf")
    fig.savefig(f"{HERE}/figT3_fraud_herd.png", dpi=300)
    plt.close(fig)
    print("wrote figT3_fraud_herd.pdf / .png")


if __name__ == "__main__":
    figT1()
    figT2()
    figT3()
