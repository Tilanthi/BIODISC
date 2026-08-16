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
"""Phase I pilot: minimal abstraction and controller analysis (Appendix B).

Deliverables, each mapped to a Phase I commitment in Sec. 4.1:

  P1-1  equilibrium verification  -- eq:eqm against numerical integration
  P1-2  phase diagram over (beta*tau, gamma*kappa / beta*(mu+w)) with the
        analytic Hopf boundary (eq:char) verified against simulated
        oscillation onset
  P1-3  anchored parameter box (tau_prod/tau_signal in [10,100], biology-
        anchored mu, beta, w; loop gain gamma anchored to the demand-
        tracking requirement y = gamma/(beta m) in [0.5, 10]) -> the
        quantitative-gate volume: asymptotically stable AND overshoot
        <= 50% AND settling within five production delays
  P1-4  robustness: survival of the gate under simultaneous +/-20% error
        in every parameter (8 perturbed copies per box point)
  P1-5  first-order Sobol indices on the gate (Saltelli, covariance
        estimator, bootstrap CIs)
  P1-6  the four named extensions: finite production capacity,
        Michaelis-Menten clearance, delayed+noisy residual measurement,
        heterogeneous responders -- gate volume under each
  P1-7  the no-P3 divergence formula of Phase II prediction 1: T =
        -(1/m) ln[(u0/m - N_T)/(u0/m - N0)] validated numerically, with
        its near-ceiling divergence and the full model's contrast

Outputs: phase1_results.json, figA1_phase_diagram.(pdf|png),
figA2_volume.(pdf|png).
"""

from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/phase12")
import jay_core as jc

OUT = "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/phase12"
RNG = np.random.default_rng(20260816)

# anchored box (Sec. 4.1): free (mu, beta, tau, y, w_mult); kappa=p0=1,
# u0=mu; w = w_mult*mu; gamma = y*beta*m.  Units: signal timescale 1.


def draw_box(n, rng):
    mu = 10 ** rng.uniform(-2, -1, n)              # responder lifespan 10-100
    beta = 10 ** rng.uniform(-2, np.log10(0.3), n)  # production relaxation
    tau = 10 ** rng.uniform(1, 2, n)               # tau_prod/tau_signal 10-100
    y = 10 ** rng.uniform(np.log10(0.5), 1, n)     # loop gain / antagonist
    w_mult = rng.uniform(1, 10, n)                 # demand 1-10x turnover
    w = w_mult * mu
    m = mu + w
    gamma = y * beta * m
    return dict(mu=mu, beta=beta, tau=tau, y=y, w_mult=w_mult, w=w, m=m,
                gamma=gamma)


def gate(batch, tau):
    """Deprecated helper kept out; use gate_metrics."""
    raise NotImplementedError


def gate_metrics(mu, beta, gamma, tau, w, **kw):
    """Run the step-response batch and apply the Phase I quantitative gate.

    Returns (metrics dict, pass mask, per-criterion masks).
    """
    res = jc.simulate_batch(mu, beta, gamma, tau, w, **kw)
    y = gamma / (beta * (mu + w))
    stable = jc.is_stable(beta, mu + w, gamma, tau)
    ov_ok = res["overshootN"] <= 0.50
    st_ok = res["settle_tau"] <= 5.0
    passed = stable & ov_ok & st_ok
    res.update(stable=stable, ov_ok=ov_ok, st_ok=st_ok, passed=passed, y=y)
    return res


# --------------------------------------------------------------------- P1-1
def equilibria_check(n=400):
    box = draw_box(n, RNG)
    res = jc.simulate_batch(box["mu"], box["beta"], box["gamma"], box["tau"],
                            box["w"], dt=0.025, T=None)
    eq_N = (box["gamma"] + box["beta"] * box["mu"]) / (
        box["gamma"] + box["beta"] * box["m"])
    err = np.abs(res["finalN"] - eq_N) / eq_N
    stable = jc.is_stable(box["beta"], box["m"], box["gamma"], box["tau"])
    th = jc.hopf_tau(box["beta"], box["m"], box["gamma"])
    ratio = np.where(np.isnan(th), 0.0, box["tau"] / th)
    deep = stable & (ratio < 0.5)     # converged: well inside the boundary
    err_s = err[stable]
    return dict(n=n, n_stable=int(stable.sum()),
                max_rel_err_stable=float(err_s.max()),
                p95_rel_err_stable=float(np.percentile(err_s, 95)),
                p95_rel_err_deep=float(np.percentile(err[deep], 95)),
                note="tail error sits at tau/tau_H in [0.5,1): "
                     "damped ringing slower than 12 tau, not integrator bias")


# --------------------------------------------------------------------- P1-2
def phase_diagram():
    """Analytic boundary in (beta*tau, y) at three m/beta contours, plus
    a simulated onset check across the boundary at the Fig. 3 slice."""
    deltas = [0.1, 1.0, 10.0]                      # m / beta contours
    curves = {}
    for d in deltas:
        beta = 1.0
        m = d * beta
        y = np.linspace(1.001, 12, 400)
        gk = y * beta * m
        th = jc.hopf_tau(beta, m, gk)
        curves[d] = dict(y=y.tolist(), beta_tau=(beta * th).tolist())
    # simulation check: beta = mu = 1, sustained w = 0.2 (active branch),
    # sweep tau through the analytic boundary at three gains and measure
    # the oscillation amplitude over the last quarter of the run
    beta = 1.0
    m_sim = 1.2                           # mu=1, w=0.2
    sims = []
    for y in [1.5, 3.0, 6.0]:
        gk = y * beta * m_sim
        tau_h = float(jc.hopf_tau(beta, m_sim, gk))
        taus = tau_h * np.array([0.5, 0.8, 1.0, 1.2, 2.0])
        res = jc.simulate_batch(np.full_like(taus, 1.0),
                                np.full_like(taus, beta),
                                np.full_like(taus, gk), taus,
                                np.full_like(taus, 0.2),
                                dt=0.005, T=None)
        for j, tv in enumerate(taus):
            sims.append(dict(y=y, tau=float(tv), tau_over_tauH=float(
                tv / tau_h), osc=float(res["osc"][j])))
    return dict(curves={str(k): v for k, v in curves.items()}, sims=sims,
                fig3=dict(beta=1.0, m=1.0, gk=1.5,
                          tauH=float(jc.hopf_tau(1.0, 1.0, 1.5))))


# ------------------------------------------------------------------- P1-3/4
def box_volume(n=4096, n_pert=8):
    box = draw_box(n, RNG)
    base = gate_metrics(box["mu"], box["beta"], box["gamma"], box["tau"],
                        box["w"], dt=0.025)
    # robustness: perturb every parameter simultaneously by up to +/-20%
    rng = np.random.default_rng(99)
    pert_pass = np.ones(n, bool)
    for k in range(n_pert):
        f = np.exp(rng.uniform(np.log(0.8), np.log(1.2),
                               (n, 5)))          # mu, beta, tau, y, w_mult
        mu_p = box["mu"] * f[:, 0]
        beta_p = box["beta"] * f[:, 1]
        tau_p = box["tau"] * f[:, 2]
        w_p = box["w"] * f[:, 4]
        gamma_p = (box["y"] * f[:, 3]) * beta_p * (mu_p + w_p)
        rp = gate_metrics(mu_p, beta_p, gamma_p, tau_p, w_p, dt=0.025)
        pert_pass &= rp["passed"]
    return dict(box=box, base=base, pert_pass=pert_pass)


# --------------------------------------------------------------------- P1-5
def sobol_gate(N=1024):
    """First-order Sobol indices of the gate indicator via Saltelli A/B
    matrices and the covariance estimator, with bootstrap CIs."""
    rng = np.random.default_rng(7)
    d = 5

    def sample(n):
        return np.column_stack([
            10 ** rng.uniform(-2, -1, n),
            10 ** rng.uniform(-2, np.log10(0.3), n),
            10 ** rng.uniform(1, 2, n),
            10 ** rng.uniform(np.log10(0.5), 1, n),
            rng.uniform(1, 10, n)])

    def run(X):
        mu, beta, tau, y, wm = X.T
        w = wm * mu
        gamma = y * beta * (mu + w)
        return gate_metrics(mu, beta, gamma, tau, w, dt=0.025)["passed"]

    A, B = sample(N), sample(N)
    yA, yB = run(A).astype(float), run(B).astype(float)
    varY = np.var(np.concatenate([yA, yB]))
    S = np.zeros(d)
    mats = []
    for i in range(d):
        Abi = A.copy()
        Abi[:, i] = B[:, i]
        yBi = run(Abi).astype(float)
        mats.append(yBi)
        S[i] = np.cov(yA, yBi)[0, 1] / max(varY, 1e-12)
    # bootstrap CIs (resample the N design points)
    boots = np.zeros((500, d))
    idx = np.arange(N)
    for b in range(500):
        sel = rng.choice(idx, N, replace=True)
        v = np.var(np.concatenate([yA[sel], yB[sel]]))
        for i in range(d):
            boots[b, i] = np.cov(yA[sel], mats[i][sel])[0, 1] / max(v, 1e-12)
    names = ["mu", "beta", "tau", "y (gain/antagonist)", "w_mult (demand)"]
    return dict(names=names, S=S.tolist(),
                S_lo=np.percentile(boots, 2.5, axis=0).tolist(),
                S_hi=np.percentile(boots, 97.5, axis=0).tolist())


# --------------------------------------------------------------------- P1-6
def extensions(n=2048):
    box = draw_box(n, RNG)
    kw = dict(dt=0.025)
    base = gate_metrics(box["mu"], box["beta"], box["gamma"], box["tau"],
                        box["w"], **kw)
    out = {"baseline": float(base["passed"].mean())}
    out["finite capacity (u<=4u0)"] = float(gate_metrics(
        box["mu"], box["beta"], box["gamma"], box["tau"], box["w"],
        u_max=4 * box["mu"], **kw)["passed"].mean())
    out["MM clearance"] = float(gate_metrics(
        box["mu"], box["beta"], box["gamma"], box["tau"], box["w"],
        mm_clearance=True, **kw)["passed"].mean())
    out["delayed+noisy residual"] = float(gate_metrics(
        box["mu"], box["beta"], box["gamma"], box["tau"], box["w"],
        r_delay_frac=0.5, r_noise=0.1, **kw)["passed"].mean())
    # decomposition: measurement jitter is free (the integral loop averages
    # it); measurement latency is not (it spends the settling budget)
    out["noise only (sigma=0.1)"] = float(gate_metrics(
        box["mu"], box["beta"], box["gamma"], box["tau"], box["w"],
        r_delay_frac=0.0, r_noise=0.1, **kw)["passed"].mean())
    for fd in (0.1, 0.25):
        out[f"delay {fd:.2f} tau only"] = float(gate_metrics(
            box["mu"], box["beta"], box["gamma"], box["tau"], box["w"],
            r_delay_frac=fd, **kw)["passed"].mean())
    # heterogeneous responders: two pools at mu*(1 +/- 0.4), shared
    # residual and split production
    het = _het_batch(box, **kw)
    out["heterogeneous responders"] = het
    return out, base


def _het_batch(box, dt=0.025, frac=0.4):
    """Two-population pool (mu1, mu2), shared residual, split production."""
    mu, beta, gamma, tau, w = (box["mu"], box["beta"], box["gamma"],
                                box["tau"], box["w"])
    P = mu.size
    m = mu + w
    N_star = (gamma + beta * mu) / (gamma + beta * m)
    chunk = 4096
    passed = np.zeros(P, bool)
    for lo in range(0, P, chunk):
        hi = min(lo + chunk, P)
        p = hi - lo
        sl = slice(lo, hi)
        mu1, mu2 = mu[sl] * (1 - frac), mu[sl] * (1 + frac)
        m1, m2 = mu1 + w[sl], mu2 + w[sl]
        # production split that preserves the total baseline N = 1
        s1 = (1 / mu1) / (1 / mu1 + 1 / mu2)
        s2 = 1.0 - s1
        k_tau = np.maximum((tau[sl] / dt).round().astype(int), 1)
        K = int(k_tau.max())
        ring = np.full((p, K), mu[sl][:, None])
        ar = np.arange(p)
        N1 = s1.copy(); N2 = s2.copy()
        u = mu[sl].copy()
        keep = 6144
        snap = np.empty((keep, p)); j = 0
        n_steps = int(np.ceil(8.5 * tau[sl].max() / dt))
        for i in range(n_steps + 1):
            if i % 25 == 0 and j < keep:
                snap[j] = N1 + N2; j += 1
            if i == n_steps:
                break
            r = np.maximum(1.0 - (N1 + N2), 0.0)
            u_new = u + (gamma[sl] * r - beta[sl] * (u - mu[sl])) * dt
            u_del = ring[ar, (i - k_tau) % K]
            N1 = np.maximum(N1 + (s1 * u_del - m1 * N1) * dt, 0.0)
            N2 = np.maximum(N2 + (s2 * u_del - m2 * N2) * dt, 0.0)
            ring[:, i % K] = u_new
            u = u_new
        i_min = np.argmin(snap[:j], axis=0)
        rows = np.arange(j)[:, None] > i_min[None, :]
        peak = np.max(np.where(rows, snap[:j], -np.inf), axis=0)
        ov = np.maximum((peak - N_star[sl]) / N_star[sl], 0.0)
        outside = np.abs(snap[:j] - N_star[sl]) > 0.05 * np.abs(N_star[sl])
        last = np.where(outside, np.arange(j)[:, None], 0).max(axis=0)
        st = last * 25 * dt / tau[sl]
        stable = jc.is_stable(beta[sl], m[sl], gamma[sl], tau[sl])
        passed[sl] = stable & (ov <= 0.5) & (st <= 5.0)
    return float(passed.mean())


# --------------------------------------------------------------------- P1-7
def no_p3_divergence():
    """Prediction 1's fixed-production recovery: validate the closed-form
    T against simulation and measure the near-ceiling divergence + the
    tracking model's contrast.

    Setup: demand w is on throughout; a burst at t=0 removes a fraction b
    of the pool, leaving N_0 = 1 - b strictly below the fixed-production
    ceiling u0/m, so the no-P3 pool recovers UP toward the ceiling.  The
    requirement N_T = (1 - eps) * ceiling approaches the ceiling as
    eps -> 0; the closed form is T = -(1/m) ln[(ceiling - N_T)/
    (ceiling - N_0)], which diverges as eps -> 0.  The tracking model
    (P3 active, sub-threshold gain so the loop is delay-unconditionally
    stable) drives N above the ceiling and does not diverge.
    """
    mu, w = 0.05, 0.05
    m = mu + w
    beta = 0.5
    ceiling = mu / m
    burst = 0.7                          # N_0 = 0.3 < ceiling = 0.5
    N0 = 1.0 - burst
    gamma_track = 0.6 * beta * m         # y = 0.6 < 1: stable at every tau
    rows = []
    # eps must keep N_T strictly above N_0 (eps < 1 - N0/ceiling = 0.4)
    for eps in np.logspace(-0.45, -2.8, 9):
        NT = (1 - eps) * ceiling
        for arm in ["fixed", "hormonal"]:
            if arm == "fixed":
                res = jc.simulate(mu=mu, beta=0.0, u0=mu, gamma=0.0,
                                  tau=20, w_fun=lambda t: w, T=4000,
                                  dt=0.02, N_init=N0)
            else:
                res = jc.simulate(mu=mu, beta=beta, u0=mu, gamma=gamma_track,
                                  tau=20, w_fun=lambda t: w, T=4000,
                                  dt=0.02, N_init=N0)
            N, t = res["N"], res["t"]
            hit = np.where(N >= NT)[0]
            T_sim = float(t[hit[0]]) if len(hit) else np.inf
            T_theory_fixed = -(1 / m) * np.log(
                (ceiling - NT) / (ceiling - N0))
            rows.append(dict(eps=float(eps), arm=arm, T_sim=T_sim,
                             T_theory_fixed=float(T_theory_fixed)))
    return dict(mu=mu, w=w, m=m, ceiling=ceiling, burst=burst, N0=N0,
                gamma_track=gamma_track, rows=rows)


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    res = {}
    print("P1-1 equilibria ..."); res["equilibria"] = equilibria_check()
    print(json.dumps(res["equilibria"], indent=1))
    print("P1-2 phase diagram ..."); res["phase_diagram"] = phase_diagram()
    print("P1-3/4 box + robustness ...")
    bv = box_volume()
    box, base, pert = bv["box"], bv["base"], bv["pert_pass"]
    res["box"] = dict(
        n=len(base["passed"]),
        frac_stable=float(base["stable"].mean()),
        frac_overshoot_ok=float(base["ov_ok"].mean()),
        frac_settle_ok=float(base["st_ok"].mean()),
        frac_gate=float(base["passed"].mean()),
        robust_conditional=float(pert[base["passed"]].mean()),
        robust_unconditional=float((pert & base["passed"]).mean()),
        median_settle_tau=float(np.median(base["settle_tau"][
            base["passed"]])),
        median_overshoot=float(np.median(base["overshootN"][
            base["passed"]])))
    print(json.dumps(res["box"], indent=1))
    print("P1-5 Sobol ..."); res["sobol"] = sobol_gate()
    print(json.dumps(res["sobol"], indent=1))
    print("P1-6 extensions ...")
    ext, _ = extensions()
    res["extensions"] = ext
    print(json.dumps(ext, indent=1))
    print("P1-7 no-P3 divergence ...")
    res["no_p3"] = no_p3_divergence()
    for r in res["no_p3"]["rows"]:
        print(f"  eps={r['eps']:.4f} {r['arm']:9s} T_sim={r['T_sim']:8.2f} "
              f"T_theory(fixed)={r['T_theory_fixed']:8.2f}")
    np.savez(f"{OUT}/phase1_box.npz", **{k: v for k, v in box.items()},
             passed=base["passed"], pert_pass=pert,
             settle_tau=base["settle_tau"], overshootN=base["overshootN"])
    res["timing_s"] = time.time() - t0
    with open(f"{OUT}/phase1_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(f"done in {res['timing_s']:.0f}s -> phase1_results.json")


if __name__ == "__main__":
    main()
