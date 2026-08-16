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
"""Closed loop of Eqs. 1-2 (eq:integral / eq:pool) + Sec. 3.2 analytics.

Layer of the Phase I-II pilot (Jay paper, Appendix B):

  * simulate()      -- single-run DDE integrator (Fig. 3's structure:
                       history buffer, Euler steps), with the four
                       Phase-I extensions as options.
  * simulate_batch()-- ensemble-vectorised step responses for the
                       Monte-Carlo box, robustness and Saltelli sweeps.
  * equilibrium()   -- the unique positive equilibrium (eq:eqm).
  * hopf_frequency() / hopf_tau() / is_stable()
                    -- the delay-Hopf boundary of eq:char in closed
                       form: a crossing exists iff gamma*kappa >
                       beta*(mu+w), and it is unique.

Normalisation for Phase I sweeps: kappa = p0 = 1, u0 = mu, so the
no-demand baseline is N = 1 with zero residual (Fig. 3's normalisation
generalised); free parameters are (mu, beta, gamma, tau, w).  Units:
the signal (residual/clearance) timescale is 1, so tau directly spans
the reference ratio tau_prod/tau_signal ~ 10-100.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# equilibrium (eq:eqm)
# ---------------------------------------------------------------------------

def equilibrium(mu, beta, kappa=1.0, p0=1.0, u0=None, gamma=1.5, w=0.0):
    """Unique positive equilibrium of Eqs. 1-2 under constant demand w.

    Inactive branch: fixed-production ceiling N* = u0/m, u* = u0, valid
    when kappa*u0/m >= p0 (residual zero).  Otherwise the active branch
    N* = (gamma p0 + beta u0)/(gamma kappa + beta m).  Returns a dict.
    """
    u0 = mu if u0 is None else u0
    m = mu + w
    ceiling = u0 / m
    if kappa * ceiling >= p0:
        return dict(u_star=u0, N_star=ceiling, r_star=0.0, active=False,
                    ceiling=ceiling, m=m)
    N_star = (gamma * p0 + beta * u0) / (gamma * kappa + beta * m)
    return dict(u_star=m * N_star, N_star=N_star, r_star=p0 - kappa * N_star,
                active=True, ceiling=ceiling, m=m)


# ---------------------------------------------------------------------------
# characteristic equation (eq:char) / Hopf boundary
# ---------------------------------------------------------------------------

def hopf_frequency(beta, m, gk):
    """Boundary-crossing frequency of eq:char.

    |q(iw)|^2 = w^4 + (beta^2 + m^2) w^2 + (beta m)^2 is strictly
    increasing in w^2, so a crossing exists iff gk > beta m and is
    unique.  Returns nan where no crossing exists.
    """
    beta, m, gk = np.broadcast_arrays(np.asarray(beta, float),
                                      np.asarray(m, float),
                                      np.asarray(gk, float))
    disc = gk * gk - (beta * m) ** 2
    w2 = 0.5 * (-(beta ** 2 + m ** 2)
                + np.sqrt((beta ** 2 + m ** 2) ** 2 + 4 * np.where(
                    disc > 0, disc, 0.0)))
    w = np.sqrt(np.where(disc > 0, w2, np.nan))
    return w if w.ndim else (float(w) if np.isfinite(w) else None)


def hopf_tau(beta, m, gk):
    """Smallest delay at which eq:char crosses the imaginary axis.

    Phase condition at lambda = iw: gk sin(w tau) = (beta+m) w and
    gk cos(w tau) = w^2 - beta m.  nan (or None) where the loop is
    delay-unconditionally stable (gk <= beta m).
    """
    w = hopf_frequency(beta, m, gk)
    if w is None:
        return None
    with np.errstate(invalid="ignore"):
        theta = np.arctan2((beta + m) * w, w * w - beta * m)
        theta = np.where(theta <= 0, theta + 2 * np.pi, theta)
        tau_h = theta / w
    return tau_h if tau_h.ndim else (float(tau_h) if np.isfinite(tau_h)
                                     else None)


def is_stable(beta, m, gk, tau):
    """Active-branch asymptotic stability from eq:char (analytic)."""
    tau_h = hopf_tau(beta, m, gk)
    if tau_h is None:
        return np.ones_like(np.asarray(tau, float), dtype=bool)
    with np.errstate(invalid="ignore"):
        ok = np.isnan(tau_h) | (np.asarray(tau, float) < tau_h)
    return ok


# ---------------------------------------------------------------------------
# single-run integration (Eqs. 1-2)
# ---------------------------------------------------------------------------

def simulate(mu=1.0, beta=1.0, kappa=1.0, p0=1.0, u0=1.0, gamma=1.5,
             tau=1.5, w_fun=None, T=26.0, dt=0.005, u_max=None,
             mm_clearance=False, r_delay=0.0, r_noise=0.0, rng=None,
             N_init=None):
    """Integrate Eqs. 1-2 by Euler with a maturation-delay history.

    Extensions: u_max (finite production capacity, hard clamp),
    mm_clearance (saturating clearance c = c_max N/(K+N) with c_max =
    2 p0 and K such that c(N0) = p0 at the no-demand baseline),
    r_delay / r_noise (factory sees a delayed residual, with sampled
    log-normal measurement jitter held over hold_every steps).
    N_init overrides the starting pool (post-burst tests).
    """
    if w_fun is None:
        w_fun = lambda t: 2.0 if 5.0 <= t < 10.0 else 0.0
    rng = np.random.default_rng(0) if rng is None else rng
    n = int(np.ceil(T / dt))
    k_tau = max(int(round(tau / dt)), 1)
    k_r = int(round(r_delay / dt))
    N0 = u0 / mu if N_init is None else N_init
    if mm_clearance:
        c_max, K_M = 2.0 * p0, N0
        clearance = lambda x: c_max * x / (K_M + x)
    else:
        clearance = lambda x: kappa * x
    t = np.arange(n + 1) * dt
    N = np.empty(n + 1); u = np.empty(n + 1); r = np.empty(n + 1)
    hist_u = np.full(k_tau, u0)         # pre-history: baseline production
    hist_r = np.zeros(max(k_r, 1))
    Nc, uc = N0, u0
    r_cur = max(p0 - clearance(Nc), 0.0)
    for i in range(n + 1):
        N[i], u[i], r[i] = Nc, uc, r_cur
        w = w_fun(t[i])
        r_seen = hist_r[0] if k_r > 0 else r_cur
        if r_noise > 0.0:
            if i % 10 == 0:                      # sampled-and-held jitter
                noise_f = np.exp(rng.normal(0.0, r_noise))
            r_seen *= noise_f
        u_new = uc + (gamma * r_seen - beta * (uc - u0)) * dt
        if u_max is not None:
            u_new = min(u_new, u_max)
        u_del = hist_u[0]
        N_new = max(Nc + (u_del - (mu + w) * Nc) * dt, 0.0)
        hist_u[:-1] = hist_u[1:]; hist_u[-1] = u_new
        if k_r > 0:
            hist_r[:-1] = hist_r[1:]; hist_r[-1] = r_cur
        Nc, uc = N_new, u_new
        r_cur = max(p0 - clearance(Nc), 0.0)
    return dict(t=t, N=N, u=u, r=r)


def step_metrics(res, tau, tol=0.05):
    """Quantitative-gate metrics on a step response.

    Overshoot is the maximum excursion above the equilibrium target
    after the depletion trough (the trough is the demand shock, not
    controller error); settling is the last exit time from the +/-
    tol band around the target, in production delays.
    """
    t, q = res["t"], res["N"]
    q_star = q[-1]                        # target = final equilibrium
    i_min = int(np.argmin(q))
    peak_after = np.max(q[i_min:])
    overshoot = max(0.0, (peak_after - q_star) / abs(q_star))
    band = tol * abs(q_star)
    outside = np.abs(q - q_star) > band
    idx = np.where(outside)[0]
    settle = t[idx[-1]] - t[0] if len(idx) else 0.0
    return dict(overshoot=overshoot, settle=settle,
                settle_over_tau=settle / tau, final=q[-1], trough=q[i_min],
                osc=float(np.std(q[len(q) // 4 * 3:]) if len(q) > 8 else 0.0))


# ---------------------------------------------------------------------------
# ensemble integration (vectorised over parameter points)
# ---------------------------------------------------------------------------

def simulate_batch(mu, beta, gamma, tau, w, dt=0.02, T=None, chunk=4096,
                   u_max=None, mm_clearance=False, r_delay_frac=0.0,
                   r_noise=0.0, seed=0, stride=25):
    """Step responses of Eqs. 1-2 for P parameter points at once.

    Demand w switches on at t=0 and is sustained.  Normalisation
    kappa = p0 = 1, u0 = mu (baseline N = 1, r = 0).  Returns per-point
    metrics plus strided trajectory tails for post-hoc checks.  The
    maturation delay is a per-point ring buffer indexed by (i - k_tau)
    mod K; pre-history is the constant baseline u0, as in simulate().
    """
    mu = np.asarray(mu, float); beta = np.asarray(beta, float)
    gamma = np.asarray(gamma, float); tau = np.asarray(tau, float)
    w = np.asarray(w, float)
    P = mu.size
    if T is None:
        T = float(np.max(12.0 * tau))
    n_steps = int(np.ceil(T / dt))
    m = mu + w
    if mm_clearance:
        # saturating clearance c = 2N/(1+N): equilibrium solves
        # gamma (1-N)/(1+N) = beta (mN - mu)  ->  quadratic in N
        a = beta * m
        b = beta * (m - mu) + gamma
        c = -(beta * mu + gamma)
        N_star = (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)
    else:
        N_star = (gamma + beta * mu) / (gamma + beta * m)
    u_star = m * N_star
    res = {k: np.empty(P) for k in
           ("overshootN", "overshootu", "settle", "settle_tau", "osc",
            "finalN", "finalu", "finalr", "minN")}
    res["traj"] = []
    for lo in range(0, P, chunk):
        hi = min(lo + chunk, P)
        p = hi - lo
        sl = slice(lo, hi)
        mu_c, be_c, ga_c = mu[sl], beta[sl], gamma[sl]
        w_c, m_c = w[sl], m[sl]
        Ns_c, us_c = N_star[sl], u_star[sl]
        k_tau = np.maximum((tau[sl] / dt).round().astype(int), 1)
        K = int(k_tau.max())
        ring_u = np.full((p, K), mu_c[:, None])
        # per-point residual-measurement delay: a fraction of that point's
        # own production delay (pre-history zero: r = 0 at baseline)
        k_r = np.maximum((r_delay_frac * tau[sl] / dt).round().astype(int),
                         0) if r_delay_frac > 0 else np.zeros(p, int)
        K_r = max(int(k_r.max()), 1)
        ring_r = np.zeros((p, K_r))
        rng = np.random.default_rng(seed + lo)
        N = np.ones(p); u = mu_c.copy()
        keep = max(n_steps // stride, 4)
        snapN = np.empty((keep, p)); snapu = np.empty((keep, p))
        j = 0
        for i in range(n_steps + 1):
            if i % stride == 0 and j < keep:
                snapN[j] = N; snapu[j] = u; j += 1
            if i == n_steps:
                break
            if mm_clearance:
                r_true = np.maximum(1.0 - 2.0 * N / (1.0 + N), 0.0)
            else:
                r_true = np.maximum(1.0 - N, 0.0)
            if k_r.max() > 0:
                r_seen = ring_r[np.arange(p), (i - k_r) % K_r]
                if r_noise > 0.0:
                    if i % 10 == 0:              # sampled-and-held jitter
                        noise_f = np.exp(rng.normal(0.0, r_noise, p))
                    r_seen = r_seen * noise_f
                ring_r[:, i % K_r] = r_true
            else:
                r_seen = r_true
            u_del = ring_u[np.arange(p), (i - k_tau) % K]
            u_new = u + (ga_c * r_seen - be_c * (u - mu_c)) * dt
            if u_max is not None:
                u_new = np.minimum(u_new, u_max)
            N_new = np.maximum(N + (u_del - m_c * N) * dt, 0.0)
            ring_u[:, i % K] = u_new
            N, u = N_new, u_new
        # post-hoc metrics from strided snapshots
        i_min = np.argmin(snapN[:j], axis=0)
        rows = np.arange(j)[:, None] > i_min[None, :]
        peakN = np.max(np.where(rows, snapN[:j], -np.inf), axis=0)
        res["overshootN"][sl] = np.maximum((peakN - Ns_c) / Ns_c, 0.0)
        res["overshootu"][sl] = np.maximum(
            (snapu[:j].max(axis=0) - us_c) / us_c, 0.0)
        outside = np.abs(snapN[:j] - Ns_c) > 0.05 * np.abs(Ns_c)
        last = np.where(outside, np.arange(j)[:, None], 0).max(axis=0)
        res["settle"][sl] = last * stride * dt
        res["settle_tau"][sl] = last * stride * dt / tau[sl]
        n_q = max(j // 4, 1)
        res["osc"][sl] = snapN[:j][-n_q:].std(axis=0)
        res["finalN"][sl] = N; res["finalu"][sl] = u
        res["finalr"][sl] = np.maximum(1.0 - N, 0.0)
        res["minN"][sl] = snapN[:j].min(axis=0)
        res["traj"].append((snapN[:j].copy(), snapu[:j].copy()))
    res["N_star"], res["u_star"], res["m"] = N_star, u_star, m
    return res
