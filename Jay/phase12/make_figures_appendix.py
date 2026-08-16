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
# distributed under the License is distributed on an "AS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Appendix figures for the Phase I-II pilot (paper Appendix B).

figA1: (a) Hopf boundary of eq:char in the (beta*tau, y) plane with the
       anchored-box Monte Carlo and simulated onset markers; (b) first-order
       Sobol indices of the quantitative gate.
figA2: (a) H1 demand scaling in the sandbox (hormonal vs fixed); (b) H2
       fibrosis and H2b adversarial burn.

Style matches make_figures.py (same palette, column width 84 mm).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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
HERE = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay"
P12 = f"{HERE}/phase12"


def _despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ================================================================= FIG A1 ====
def figA1():
    import json
    res = json.load(open(f"{P12}/phase1_results.json"))
    box = np.load(f"{P12}/phase1_box.npz")

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_W, 1.95))

    # ---- (a) phase diagram ----------------------------------------------
    for d, c, lab in [("10.0", BLUE, "$m/\\beta=10$"),
                      ("1.0", ORANGE, "$m/\\beta=1$"),
                      ("0.1", AQUA, "$m/\\beta=0.1$")]:
        cu = res["phase_diagram"]["curves"][d]
        a.plot(cu["beta_tau"], cu["y"], lw=1.1, color=c, label=lab)
    # anchored-box Monte Carlo in the same coordinates
    y = box["y"]
    beta_tau = box["beta"] * box["tau"]
    gk = box["gamma"]
    y_coord = gk / (box["beta"] * box["m"])
    ok = box["passed"]
    a.scatter(beta_tau[~ok], y_coord[~ok], s=1.6, color=HAIR, zorder=1,
              label="box: gate fail")
    a.scatter(beta_tau[ok], y_coord[ok], s=1.6, color=BLUE, zorder=2,
              alpha=0.55, label="box: gate pass")
    # simulated oscillation onset at the Fig. 3 slice
    sims = res["phase_diagram"]["sims"]
    onset = [s for s in sims if s["tau_over_tauH"] >= 0.99
             and s["tau_over_tauH"] <= 1.01]
    for s in onset:
        a.scatter([s["tau"]], [s["y"]], marker="x", s=22, color=INK,
                  zorder=4)
    a.scatter([], [], marker="x", s=22, color=INK, zorder=4,
              label="sim. onset (on $\\tau_H$)")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlim(2e-3, 4e3); a.set_ylim(0.45, 12)
    a.set_xlabel(r"$\beta\tau$ (production delay $/$ relaxation)")
    a.set_ylabel(r"$y=\gamma\kappa/\beta(\mu+w)$")
    a.legend(frameon=False, fontsize=5.4, loc="lower left",
             handletextpad=0.3, borderaxespad=0.2)
    a.text(0.03, 0.97, "(a)", transform=a.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(a)

    # ---- (b) Sobol --------------------------------------------------------
    sob = res["sobol"]
    names = ["$\\mu$", "$\\beta$", "$\\tau$", "$y$", "$w$"]
    x = np.arange(5)
    err = [[max(v - lo, 0.0) for v, lo in zip(sob["S"], sob["S_lo"])],
           [max(hi - v, 0.0) for v, hi in zip(sob["S_hi"], sob["S"])]]
    b.bar(x, sob["S"], 0.62, color=[BLUE, ORANGE, AQUA, MUTED, BLUE],
          yerr=err, error_kw=dict(lw=0.7, color=INK2), zorder=3)
    b.axhline(0, lw=0.6, color=LINE)
    b.set_xticks(x, names)
    b.set_ylabel("first-order Sobol $S_i$ (gate indicator)")
    b.set_ylim(-0.05, 0.95)
    b.text(0.03, 0.97, "(b)", transform=b.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(b)

    fig.subplots_adjust(left=0.075, right=0.995, top=0.97, bottom=0.16,
                        wspace=0.24)
    fig.savefig(f"{HERE}/figA1_phase1.pdf")
    fig.savefig(f"{HERE}/figA1_phase1.png", dpi=300)
    plt.close(fig)
    print("wrote figA1_phase1.pdf / .png")


# ================================================================= FIG A2 ====
def figA2():
    import json
    res = json.load(open(f"{P12}/phase2_results.json"))

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_W, 1.95))

    # ---- (a) H1 demand scaling -------------------------------------------
    rows = res["h1_scaling"]["rows"]
    for arm, c, mk in [("hormonal", BLUE, "o"), ("fixed", ORANGE, "s")]:
        rs = [r for r in rows if r["arm"] == arm]
        D = [r["r_demand"] for r in rs]
        T = [r["resolve_med"] for r in rs]
        F = [r["fail"] for r in rs]
        a.plot(D, T, mk + "-", lw=1.1, ms=3.2, color=c,
               label="residual-driven" if arm == "hormonal"
               else "fixed (no P3)")
        for d, t, f in zip(D, T, F):
            if f >= 0.1:
                a.annotate(f"{int(round(f * 100))}%", (d, t),
                           textcoords="offset points", xytext=(4, -1),
                           fontsize=5.2, color=c)
    a.set_xlabel("demand mass $D$ (baseline units)")
    a.set_ylabel("median time to resolve")
    a.legend(frameon=False, fontsize=5.6, loc="upper left")
    a.text(0.03, 0.97, "(a)", transform=a.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(a)

    # ---- (b) H2 fibrosis + H2b burn ---------------------------------------
    h2 = res["h2_fibrosis"]
    b.bar([0], [h2["P5 on"]["N_end_over_base"]], 0.5, color=BLUE,
          label="P5 on: $N_{\\rm end}/N_0$")
    b.bar([1], [h2["P5 off"]["N_end_over_base"]], 0.5, color=ORANGE,
          label="P5 off: $N_{\\rm end}/N_0$")
    b.axhline(1.0, lw=0.6, color=LINE)
    b.text(0, h2["P5 on"]["N_end_over_base"] + 0.08,
           f"{h2['P5 on']['N_end_over_base']:.2f}", ha="center",
           fontsize=5.8, color=INK2)
    b.text(1, h2["P5 off"]["N_end_over_base"] + 0.08,
           f"{h2['P5 off']['N_end_over_base']:.2f}", ha="center",
           fontsize=5.8, color=INK2)
    b2 = b.twinx()
    adv = sorted({r["adv"] for r in res["h2b_adversarial"]["rows"]
                  if r["p4"] is False})
    burn_off = [next(r["false_burn"] for r in res["h2b_adversarial"]["rows"]
                     if r["adv"] == av and r["p4"] is False) for av in adv]
    burn_on = [next(r["false_burn"] for r in res["h2b_adversarial"]["rows"]
                    if r["adv"] == av and r["p4"]) for av in adv]
    b2.plot(np.arange(len(adv)) * 0.32 + 1.85, burn_off, "s--", ms=2.6,
            lw=0.9, color=ORANGE)
    b2.plot(np.arange(len(adv)) * 0.32 + 1.85, burn_on, "o--", ms=2.6,
            lw=0.9, color=BLUE)
    b2.set_ylim(0, 100)
    b2.set_ylabel("false burn (pool mass)", color=INK2)
    b2.text(1.85, 84, "P4 off", fontsize=5.6, color=ORANGE)
    b2.text(1.85, 22, "P4 on", fontsize=5.6, color=BLUE)
    b2.annotate("adversary rate $\\nu$: 0 $\\rightarrow$ 0.2",
                xy=(2.95, 40), fontsize=5.4, color=MUTED, ha="right")
    b2.tick_params(colors=INK2)
    b.set_xlim(-0.5, 3.3)
    b.set_xticks([0, 1], ["stand-down\n(P5 on)", "no antagonist\n(P5 off)"])
    b.set_ylabel("post-release pool $N_{\\rm end}/N_0$")
    b.set_ylim(0, 3.6)
    b.text(0.03, 0.97, "(b)", transform=b.transAxes, fontsize=7,
           color=INK2, weight="bold", va="top")
    _despine(b); _despine(b2)
    b2.spines["top"].set_visible(False)

    fig.subplots_adjust(left=0.075, right=0.92, top=0.97, bottom=0.20,
                        wspace=0.52)
    fig.savefig(f"{HERE}/figA2_phase2.pdf")
    fig.savefig(f"{HERE}/figA2_phase2.png", dpi=300)
    plt.close(fig)
    print("wrote figA2_phase2.pdf / .png")


if __name__ == "__main__":
    figA1()
    figA2()
