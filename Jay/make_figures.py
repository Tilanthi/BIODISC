#!/usr/bin/env python3
"""Figures for 'Coordination Without a Coordinator' (BIODISC/Jay paper).

Generates three schematic figures as vector PDFs for the two-column mnras
layout, plus 300 dpi PNG previews for inspection.

Colour roles are fixed across all figures (dataviz-validated palette, light mode):
  blue   #2a78d6  - ordinary agents / circulating pool
  orange #eb6834  - producing or coordinating entities (hub, factory, stressed source)
  aqua   #1baf7a  - signals (halos, fluxes)
  ink    #0b0b0b / #52514e / #898781 - text;  #c3c2b7 / #e1e0d9 - lines & fills
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Rectangle

# ---------------------------------------------------------------- palette ---
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
LINE, HAIR = "#c3c2b7", "#e1e0d9"
BLUE100, BLUE250 = "#cde2fb", "#86b6ef"          # sequential steps (washes)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "text.color": INK,
    "axes.edgecolor": LINE,
})

COL_W, FULL_W = 84 / 25.4, 176 / 25.4            # mm -> inches


def node(ax, x, y, r, fc, ec="none", lw=0, z=3):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z))


# ============================================================== FIGURE 1 ====
def fig1(path):
    fig, (a, b) = plt.subplots(2, 1, figsize=(COL_W, 2.62))

    # ---- (a) central orchestration ----------------------------------------
    a.set_xlim(-1.55, 1.55); a.set_ylim(-1.42, 1.28)
    a.set_aspect("equal"); a.axis("off")
    a.text(-1.48, 1.16, "(a)", fontsize=7, color=INK2, weight="bold",
           ha="left", va="top")
    n, R = 8, 1.0
    ang = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    px, py = R * np.cos(ang), R * np.sin(ang)
    for i in range(n):                                    # O(n^2) pairwise chords
        for j in range(i + 1, n):
            a.plot([px[i], px[j]], [py[i], py[j]], ls=(0, (2, 2)), lw=0.6,
                   color=HAIR, zorder=1)
    for i in range(n):                                    # hub spokes
        a.plot([0, px[i]], [0, py[i]], lw=1.0, color=LINE, zorder=2)
        node(a, px[i], py[i], 0.13, BLUE)
    node(a, 0, 0, 0.20, ORANGE)
    a.text(0, 0, "C", ha="center", va="center", fontsize=7, color="white",
           weight="bold", zorder=4)
    a.annotate("single point\nof failure", xy=(0.14, 0.14), xytext=(0.62, 0.52),
               fontsize=6, color=INK2, va="center",
               arrowprops=dict(arrowstyle="-", lw=0.6, color=MUTED))

    # ---- (b) hormonal medium ----------------------------------------------
    b.set_xlim(-1.55, 1.55); b.set_ylim(-1.18, 1.18)
    b.set_aspect("equal"); b.axis("off")
    b.text(-1.48, 1.06, "(b)", fontsize=7, color=INK2, weight="bold",
           ha="left", va="top")
    b.add_patch(FancyBboxPatch((-1.42, -0.92), 2.84, 1.86,
                boxstyle="round,pad=0.06,rounding_size=0.10", fc=BLUE100,
                ec=LINE, lw=0.8, zorder=0))
    b.text(0, 1.04, "shared medium — diffusion + decay (concentration fields)",
           ha="center", fontsize=6.3, color=INK2)

    others = [(-1.05, 0.55), (-0.45, -0.62), (0.30, 0.72), (1.10, 0.18),
              (0.95, -0.62), (-1.12, -0.18), (0.10, -0.05)]
    for x, y in others:
        node(b, x, y, 0.11, BLUE)
    responders = [(-0.55, 0.38), (0.62, -0.28)]            # receptor-equipped
    for x, y in responders:
        node(b, x, y, 0.11, BLUE, ec=INK, lw=1.1)
    node(b, -0.05, 0.34, 0.13, ORANGE)                     # stressed emitter
    for r, al in ((0.28, 0.85), (0.44, 0.55), (0.62, 0.30), (0.82, 0.14)):
        b.add_patch(Circle((-0.05, 0.34), r, fc=AQUA, ec="none", alpha=al * 0.35,
                            zorder=1))
    b.annotate("", xy=(-0.62, 0.30), xytext=(-0.38, 0.33),
               arrowprops=dict(arrowstyle="-|>", lw=0.9, color=AQUA))
    b.annotate("", xy=(0.58, -0.22), xytext=(-0.02, 0.28),
               arrowprops=dict(arrowstyle="-|>", lw=0.9, color=AQUA,
                               connectionstyle="arc3,rad=0.25"))
    b.text(-0.98, 0.80, "stress signal\n(blind broadcast)", fontsize=6,
           color=INK2, ha="center")
    b.text(0.78, 0.50, "receptor only:\nresponds", fontsize=6, color=INK2,
           ha="center")
    b.text(0.30, -0.88, "no receptor: signal ignored", fontsize=6, color=MUTED,
           ha="center")

    fig.subplots_adjust(left=0, right=1, top=1.02, bottom=0.02, hspace=0.06)
    fig.savefig(f"{path}.pdf")
    fig.savefig(f"{path}.png", dpi=300)
    plt.close(fig)


# ============================================================== FIGURE 2 ====
def fig2(path):
    fig, ax = plt.subplots(figsize=(FULL_W, 2.15))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis("off")

    phases = [("Haemostasis", 0.15, 1.7, BLUE250), ("Inflammation", 1.85, 3.4, "#5598e7"),
              ("Proliferation", 5.25, 3.2, "#3987e5"), ("Remodelling", 8.45, 1.4, "#2a78d6")]
    OV = 0.42     # deliberate overlap: phases share trigger/output intervals in vivo
    for k, (name, x0, w, c) in enumerate(phases):
        lo = x0 - (OV if k > 0 else 0)          # washes bleed into neighbours ...
        hi = x0 + w + (OV if k < len(phases) - 1 else 0)
        ax.add_patch(Rectangle((lo, 0.30), hi - lo, 3.42, fc=c, alpha=0.13, ec="none"))
        ax.add_patch(Rectangle((x0, 3.72), w, 0.30, fc=c, ec="none"))   # ... strips do not
        ax.text(x0 + w / 2, 3.87, name, ha="center", va="center", fontsize=7.5,
                color="white", weight="bold")

    KW = 0.070        # data units per character at fontsize 6.4 (calibrated)

    def chip(x, y, text, ec, chars=None, fs=6.4):
        """Rounded chip whose width follows the widest rendered line.
        Returns the x where the next chip may start."""
        lines = text.split("\n")
        w = (chars if chars else max(len(s) for s in lines)) * KW + 0.14
        h = 0.36 if len(lines) == 1 else 0.78
        ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h,
                     boxstyle="round,pad=0.03,rounding_size=0.08", fc="white",
                     ec=ec, lw=0.9, zorder=3))
        if len(lines) == 1:
            ax.text(x + w / 2, y, lines[0], fontsize=fs, ha="center",
                    va="center", color=INK, zorder=4)
        else:
            ax.text(x + w / 2, y + 0.17, lines[0], fontsize=fs, ha="center",
                    va="center", color=INK, zorder=4)
            ax.text(x + w / 2, y - 0.17, lines[1], fontsize=fs, ha="center",
                    va="center", color=INK, zorder=4)
        return x + w

    def lane(y, label):
        ax.text(1.42, y, label, fontsize=7, ha="right", va="center",
                color=INK2, weight="bold")

    # lane 1 — local signals
    lane(3.45, "local\nsignals")
    x = chip(1.95, 3.45, "thrombin · fibrin", AQUA)
    x = chip(x + 0.24, 3.45, "DAMPs · IL-1 · C5a · CXCL8", AQUA)
    x = chip(x + 0.24, 3.45, "PDGF · VEGF · TGF-$\\beta$", AQUA, chars=19)
    chip(8.62, 3.45, "MMPs", AQUA)

    # lane 2 — actors (sequential handoff left to right)
    lane(2.42, "actors")
    x = chip(1.65, 2.42, "platelets: plug", BLUE)
    x = chip(x + 0.22, 2.42, "neutrophils: phagocytosis", BLUE)
    x = chip(x + 0.22, 2.42, "macrophages M1$\\rightarrow$M2", BLUE, chars=17)
    x = chip(x + 0.22, 2.42, "fibroblasts · vessels\nkeratinocytes", BLUE)
    chip(x + 0.22, 2.42, "matrix turnover", BLUE)

    # lane 3 — systemic escalation
    lane(1.02, "systemic\nescalation")
    x = chip(1.65, 1.02, "TPO residual $\\uparrow$ $\\Rightarrow$ megakaryopoiesis",
             ORANGE, chars=30)
    chip(x + 0.28, 1.02, "G-CSF $\\Rightarrow$ emergency granulopoiesis",
         ORANGE, chars=30)

    ax.annotate("", xy=(9.70, 0.42), xytext=(1.65, 0.42),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color=INK2))
    ax.text(5.68, 0.56, "time (minutes $\\rightarrow$ months, not to scale)",
            fontsize=6.2, color=MUTED, ha="center", va="bottom")

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(f"{path}.pdf")
    fig.savefig(f"{path}.png", dpi=300)
    plt.close(fig)


# ============================================================== FIGURE 3 ====
def fig3(path):
    """Numerical integration of the closed loop (Eqs. 1-2 of the paper).

        N: responder pool        dN/dt = u(t-tau) - mu*N - w(t)*N
        u: production rate       du/dt = gamma*r - beta*(u - u0)
        r: signal residual       r = [p0 - kappa*N]_+   (receptor clearance kN)

    Baseline N0=1, mu=1, u0=1, kappa=p0=1 so r=0 at rest. A demand pulse
    (per-capita consumption rate w=2 on t in [5,10)) depletes responders.
    Panel (a) beta>0: recovery to baseline (with delay-tau overshoot).
    Panel (b) beta=0: production ratchets and never relaxes -- the pool
    settles permanently high: the fibrotic shift. Consumption per-capita
    keeps N >= 0 structurally.
    """
    mu, u0, p0, kap, gam, tau, w0 = 1.0, 1.0, 1.0, 1.0, 1.5, 1.5, 2.0
    T, dt = 26.0, 0.005
    n = int(T / dt)

    def run(beta):
        N, u, r = np.zeros(n + 1), np.zeros(n + 1), np.zeros(n + 1)
        N[0], u[0] = 1.0, u0
        for i in range(n):
            t = i * dt
            u_hist = u[max(0, i - int(round(tau / dt)))]     # maturation delay
            w = w0 if 5.0 <= t < 10.0 else 0.0
            r[i] = max(p0 - kap * N[i], 0.0)
            N[i + 1] = N[i] + (u_hist - mu * N[i] - w * N[i]) * dt
            u[i + 1] = u[i] + (gam * r[i] - beta * (u[i] - u0)) * dt
        r[n] = max(p0 - kap * N[n], 0.0)
        return N, u, r

    t = np.linspace(0, T, n + 1)
    Na, ua, ra = run(1.0)                                    # antagonist on
    Nb, ub, rb = run(0.0)                                    # beta = 0

    fig, (a, b) = plt.subplots(2, 1, figsize=(COL_W, 2.55), sharex=True)

    def panel(ax, N, u, r, tag, note):
        ax.set_xlim(0, T); ax.set_ylim(-0.08, 4.0)
        ax.axis("off")
        ax.text(0.3, 3.84, tag, fontsize=7, color=INK2, weight="bold")
        ax.add_patch(Rectangle((5.0, 3.72), 5.0, 0.24, fc=LINE, ec="none"))
        ax.text(7.5, 3.62, "demand $w(t)$", fontsize=6, color=MUTED, ha="center")
        ax.plot(t, N, lw=1.6, color=BLUE)
        ax.plot(t, u, lw=1.3, color=ORANGE, ls=(0, (4, 2)))
        ax.plot(t, r, lw=1.1, color=AQUA)
        ax.axhline(1.0, lw=0.5, color=HAIR, zorder=0)
        ax.text(T - 0.3, N[-1], " $N$", fontsize=6.2, color=BLUE, va="center")
        ax.text(T - 0.3, u[-1], " $u$", fontsize=6.2, color=ORANGE, va="center")
        ax.text(11.2, r[int(7.5 / dt)] + 0.06, "$r$", fontsize=6.2, color=AQUA)
        # notes live in the open region right of the pulse (x>11, y 2.1-2.9):
        # in (a) N,u <= 1.9 there; in (b) both curves sit >= 3.4 — no collision
        ax.text(11.5, 2.9, note, fontsize=6.0, color=INK2, va="top")

    panel(a, Na, ua, ra, "(a)",
          "residual $r$ rises as $N$ falls;\n"
          "production follows with delay-$\\tau$\n"
          "overshoot, then recovers to baseline")
    panel(b, Nb, ub, rb, "(b)",
          "$\\beta=0$: $u$ ratchets, never relaxes\n"
          "--- the pool settles at $\\approx$4$\\times$\n"
          "baseline: the fibrotic shift")
    b.annotate("", xy=(9.7, 0.12), xytext=(0.3, 0.12),
               arrowprops=dict(arrowstyle="-|>", lw=1.0, color=INK2))
    b.text(5.0, 0.28, "time", fontsize=6.2, color=MUTED, ha="center")

    fig.subplots_adjust(left=0, right=1, top=1.0, bottom=0.02, hspace=0.16)
    fig.savefig(f"{path}.pdf")
    fig.savefig(f"{path}.png", dpi=300)
    plt.close(fig)
    print(f"  diagnostics: beta=1 -> N_end={Na[-1]:.3f} u_end={ua[-1]:.3f}; "
          f"beta=0 -> N_end={Nb[-1]:.3f} u_end={ub[-1]:.3f} "
          f"(want ~1/1 and >1/>1)")


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for name, fn in [("fig1_architecture", fig1), ("fig2_timeline", fig2),
                     ("fig3_closedloop", fig3)]:
        fn(name)
        print(f"wrote {name}.pdf / .png")
