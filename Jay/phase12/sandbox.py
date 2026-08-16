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
"""Phase II digital wound sandbox (pilot instantiation, Appendix B).

Grid discretisation of Eqs. 3-4 on a torus, coupled to the systemic
supply loop of Eqs. 1-2:

  * local fields (eq:medium): a stress concentration S (diffuse +
    decay, emitted by demanding sites and by adversaries) and a
    co-signal C (P4's locally verifiable second signal, faster decay);
    a housekeeping field Hk carries routine traffic that
    receptor-correct responders must ignore (P1's payload);
  * responders (eq:response): a density Nr that migrates up the sensed
    gradient above threshold (P2), serves demand where co-signal is
    present (P4 gate), is expended by serving, lost at rate mu, and
    dissolved after recruitment when P5 is on;
  * systemic loop (Eqs. 1-2): production u of new responders driven
    by the residual r = [1 - kappa N]_+, maturing after delay tau,
    relaxed by the antagonist beta (P5), released well-mixed.

P1-P5 are toggles; the six Phase II arms are production/redistribution
policies on the same plant at matched information and budget:
hormonal (physical residual), fixed (P3 knockout), measured (same law,
error from site reports), backpressure (queue-driven), gossip
(neighbour-estimate-driven), oracle (true global error + instant
redistribution -- the upper bound).  Field routing (and its broadcast
cost) is charged only to the arms that use it.

All runs batched over seeds; every draw through numpy Generator.
"""

from __future__ import annotations

import numpy as np


def _lap(f):
    return (np.roll(f, 1, -2) + np.roll(f, -1, -2)
            + np.roll(f, 1, -1) + np.roll(f, -1, -1) - 4.0 * f)


FIELD_ARMS = ("hormonal", "fixed", "measured")   # arms that route on S


class WoundSandbox:
    """One batch of seeds of the sandbox; run() returns per-seed metrics."""

    def __init__(self, seeds=30, G=24, p1=True, p2=True, p3=True, p4=True,
                 p5=True, policy="hormonal", n_sites=3, site_radius=2,
                 mu=0.02, beta=0.05, gamma=3.0, tau=20.0,
                 D_s=0.8, lam_s=0.12, lam_c=0.30, theta=0.30, theta_c=0.05,
                 chi=2.5, D_N=0.20, serve=0.25, expend=0.05,
                 e_s=6.0, e_c=4.0, r_demand=6.0, refill=0.0,
                 release_t=None, adversarial=0.0, churn_frac=0.0,
                 churn_every=0, oracle_outages=(), deadline=None,
                 T_end=None, dt=0.2, seed0=0, report_every=10,
                 gossip_every=3, teleport=0.10, hk_amp=3.0, hk_rate=0.02):
        self.B, self.G = seeds, G
        self.p1, self.p2, self.p3, self.p4, self.p5 = p1, p2, p3, p4, p5
        self.policy = policy
        self.n_sites, self.site_radius = n_sites, site_radius
        self.mu, self.beta, self.gamma, self.tau = mu, beta, gamma, tau
        self.D_s, self.lam_s, self.lam_c = D_s, lam_s, lam_c
        self.theta, self.theta_c = theta, theta_c
        self.chi, self.D_N = chi, D_N
        self.serve, self.expend = serve, expend
        self.e_s, self.e_c = e_s, e_c
        self.r_demand, self.refill = r_demand, refill
        self.release_t = release_t
        self.adversarial = adversarial
        self.churn_frac, self.churn_every = churn_frac, churn_every
        self.oracle_outages = oracle_outages
        self.dt, self.report_every = dt, report_every
        self.gossip_every, self.teleport = gossip_every, teleport
        self.hk_amp, self.hk_rate = hk_amp, hk_rate
        self.deadline = 8.0 * tau if deadline is None else deadline
        self.T_end = (self.deadline + 2 * tau) if T_end is None else T_end
        self.use_field = policy in FIELD_ARMS
        self._setup(seed0)

    # ------------------------------------------------------------------ setup
    def _setup(self, seed0):
        B, G = self.B, self.G
        rng = np.random.default_rng(seed0)
        yy, xx = np.mgrid[0:G, 0:G]
        site = np.zeros((B, G, G), bool)
        site_masks = []
        for b in range(B):
            per_seed = []
            for _ in range(self.n_sites):
                cy, cx = rng.integers(0, G, 2)
                dy = np.minimum(np.abs(yy - cy), G - np.abs(yy - cy))
                dx = np.minimum(np.abs(xx - cx), G - np.abs(xx - cx))
                mk = dy * dy + dx * dx <= self.site_radius ** 2
                per_seed.append(mk)
                site[b] |= mk
            site_masks.append(per_seed)
        self.site_masks = site_masks
        self.site_bool = np.stack([np.stack(per_seed, axis=0)
                                   for per_seed in site_masks], axis=0)
        self.site = site
        # per-site normalised masks: presence-weighted emission (a wound
        # emits at full local strength while any of its demand remains)
        self.site_emitters = np.stack([
            np.stack([mk / max(mk.sum(), 1) for mk in per_seed], axis=0)
            for per_seed in site_masks], axis=0)     # (B, n_sites, G, G)
        self.site = site
        self.site_norm = site / np.maximum(site.sum(axis=(1, 2))[
            :, None, None], 1.0)
        self.D = self.r_demand * self.site_norm.copy()
        self.D0 = self.D.sum(axis=(1, 2)).copy()
        self.S = np.zeros((B, G, G))
        self.C = np.zeros((B, G, G))
        self.Hk = np.zeros((B, G, G))
        self.Nr = np.full((B, G, G), 0.02)
        self.N_tot0 = self.Nr.sum(axis=(1, 2))
        self.kappa = 1.0 / self.N_tot0
        self.u0 = self.mu * self.N_tot0
        self.u_cap = 8.0 * self.u0          # finite factories (A1)
        self.u = self.u0.copy()
        self.k_tau = max(int(round(self.tau / self.dt)), 1)
        self.ring_u = np.tile(self.u0[:, None], (1, self.k_tau))
        self.load = np.zeros((B, G, G))
        self.r_report = np.zeros(B)
        self.cost = dict(emissions=0.0, deliveries=0.0, messages=0.0)

    # ------------------------------------------------------------------- run
    def run(self):
        B, G, dt = self.B, self.G, self.dt
        n_steps = int(round(self.T_end / dt))
        unmet = np.zeros((B, n_steps))
        Ntot = np.zeros((B, n_steps))
        uprod = np.zeros((B, n_steps))
        false_burn = np.zeros(B)
        false_held = np.zeros(B)
        resolved_t = np.full(B, np.inf)
        rng = np.random.default_rng(seed0 := 1000 + B)  # runtime draws
        ar = np.arange(B)
        for i in range(n_steps):
            t = i * dt
            released = self.release_t is not None and t >= self.release_t
            live = 0.0 if released else 1.0
            demand_frac = self.D.sum(axis=1).sum(axis=1) \
                / np.maximum(self.D0, 1e-9)
            emitting = (self.D > 1e-9) if not released else np.zeros_like(
                self.D > 1e-9)
            # ---- local fields (Eq. 3) ------------------------------------
            if self.use_field or self.adversarial > 0 or not self.p2:
                # per-site presence: a site emits at full strength while
                # any of its demand remains (wounds do not fade with size)
                mass_s = (self.D[:, None] * self.site_bool).sum(
                    axis=(-2, -1))                       # (B, n_sites)
                present = ((mass_s > 1e-9) & (live > 0)).astype(float)
                emit_map = np.einsum("bsxy,bs->bxy", self.site_emitters,
                                     present)
                self.S += dt * self.e_s * emit_map
                self.C += dt * self.e_c * emit_map
                if self.adversarial > 0:
                    inj = (rng.random(self.S.shape)
                           < self.adversarial * dt) & ~self.site
                    self.S[inj] += 0.60
                    self.cost["emissions"] += inj.sum() / B
                # medium physics (decay) is independent of the P2 toggle:
                # P2's knockout removes the threshold, not the physics
                self.S += dt * self.D_s * _lap(self.S) - dt * self.lam_s * self.S
                self.C += dt * self.D_s * _lap(self.C) - dt * self.lam_c * self.C
                self.S = np.maximum(self.S, 0.0)
                self.C = np.maximum(self.C, 0.0)
            # routine housekeeping traffic (P1's distractor key): diffusive
            # pulses of a signal that receptor-correct receivers must ignore
            pulses = rng.random(self.Hk.shape) < self.hk_rate * dt
            self.Hk = np.where(pulses, self.Hk + self.hk_amp, self.Hk)
            self.Hk += dt * self.D_s * _lap(self.Hk)
            self.Hk *= (1.0 - dt * 0.30)
            self.Hk = np.maximum(self.Hk, 0.0)
            # ---- sense + move (Eq. 4) ------------------------------------
            if self.policy in ("backpressure", "gossip"):
                guide = self.load
            else:
                guide = self.S if self.p1 else np.maximum(
                    self.S, 1.5 * self.Hk)
            gate = (guide >= self.theta) if self.p2 else (guide > 1e-9)
            gy, gx = np.gradient(guide, axis=(-2, -1))
            vy = np.clip(self.chi * gy, -2.0, 2.0) * gate
            vx = np.clip(self.chi * gx, -2.0, 2.0) * gate
            # donor-cell (upwind) advective flux: positivity-preserving,
            # stable for (|vy|+|vx|)*dt <= 1
            Fy = np.where(vy > 0, self.Nr, np.roll(self.Nr, -1, -2)) * vy
            Fx = np.where(vx > 0, self.Nr, np.roll(self.Nr, -1, -1)) * vx
            self.Nr = np.maximum(
                self.Nr + dt * (np.roll(Fy, 1, -2) - Fy
                                + np.roll(Fx, 1, -1) - Fx)
                + dt * self.D_N * _lap(self.Nr), 0.0)
            # ---- oracle teleport redistribution ---------------------------
            if self.policy == "oracle" and not self._outage(t) and not released:
                on = self.D > 1e-9
                off_mass = (self.Nr * ~on).sum(axis=(1, 2))
                want = np.minimum(self.teleport * self.D.sum(axis=(1, 2)),
                                  off_mass)
                share = want / np.maximum(off_mass, 1e-9)
                take = np.where(on, 0.0, share[:, None, None])
                self.Nr = self.Nr * (1 - take)
                self.Nr += on * (want[:, None, None] / np.maximum(
                    on.sum(axis=(1, 2))[:, None, None], 1))
            # ---- serving + expenditure (P4 co-stimulus gate) ---------------
            # the co-signal gate applies to signal-mediated action; arms that
            # route on their own side channel serve where they route
            cosig = self.C >= self.theta_c
            gated = (self.p4 and self.use_field)
            serve_ok = (self.D > 1e-9) & (cosig if gated else True)
            served = dt * self.serve * self.Nr * serve_ok
            self.D = np.maximum(self.D - served, 0.0)
            self.Nr -= dt * self.expend * self.Nr * serve_ok
            # misallocated holding: gate is open where there is no demand
            # (stale halos, adversary injections, housekeeping distractors)
            held_cells = gate & (self.D <= 1e-9) & ~self.site
            false_held = np.maximum(false_held,
                                    (self.Nr * held_cells).sum(axis=(1, 2)))
            if not self.p4:
                burned = dt * self.expend * self.Nr * held_cells
                false_burn += burned.sum(axis=(1, 2))
                self.Nr -= burned
            # ---- scenario refill (infection / chronic) ----------------------
            if self.refill > 0 and not released:
                self.D += dt * self.refill * self.site_norm
            # ---- churn ------------------------------------------------------
            if self.churn_every and i and i % self.churn_every == 0:
                kill = (rng.random(self.Nr.shape) < self.churn_frac) \
                    & ~self.site
                self.Nr = np.where(kill, 0.0, self.Nr)
            # ---- systemic production (Eqs. 1-2 + arms) ----------------------
            N_tot = self.Nr.sum(axis=(1, 2))
            r = np.maximum(1.0 - self.kappa * N_tot, 0.0)
            if self.policy == "fixed" or not self.p3:
                e = np.zeros(B)
            elif self.policy == "measured":
                if i % self.report_every == 0:
                    self.r_report = r.copy()
                    self.cost["messages"] += self.n_sites
                e = self.r_report
            elif self.policy == "backpressure":
                e = demand_frac
            elif self.policy == "gossip":
                e = np.clip(self.load.sum(axis=(1, 2))
                            / np.maximum(self.D0, 1e-9) * 4.0, 0.0, 1.0)
            elif self.policy == "oracle":
                e = 0.0 if self._outage(t) else demand_frac
            else:
                e = r
            beta_eff = self.beta if self.p5 else 0.0
            u_new = self.u + dt * (self.gamma * e
                                   - beta_eff * (self.u - self.u0))
            self.u = np.clip(u_new, 0.0, self.u_cap)   # finite factories (A1)
            self.ring_u[:, i % self.k_tau] = self.u
            u_del = self.ring_u[ar, (i - self.k_tau) % self.k_tau]
            # ---- losses, P5 dissolution, release of new responders ----------
            d_rec = 0.05 if self.p5 else 0.0
            self.Nr -= dt * (self.mu + d_rec * gate) * self.Nr
            self.Nr += dt * u_del[:, None, None] / (G * G)
            self.Nr = np.maximum(self.Nr, 0.0)
            # ---- arm side channels (costs) -----------------------------------
            if self.policy == "gossip" and i % self.gossip_every == 0:
                inject = 5.0 * self.site_norm * demand_frac[:, None, None]
                self.load = (self.load + 0.30 * (_lap(self.load) * 0.5
                                                 + inject)) * (1.0 - 0.010)
                self.cost["messages"] += 4.0 * G * G
            elif self.policy == "backpressure" and i % self.report_every == 0:
                self.load = self.D
                self.cost["emissions"] += self.n_sites
                self.cost["deliveries"] += self.n_sites * G * G
            if self.use_field:                      # the medium's own bill
                n_emit = float(np.mean(emitting.sum(axis=(1, 2))))
                self.cost["emissions"] += n_emit
                self.cost["deliveries"] += n_emit * G * G
            # ---- logs --------------------------------------------------------
            unmet[:, i] = demand_frac
            Ntot[:, i] = N_tot
            uprod[:, i] = self.u
            gone = (demand_frac <= 0.01) & np.isinf(resolved_t)
            resolved_t[gone] = t
        T = self.T_end
        n_q = max(n_steps // 4, 1)
        cost = {k: v / T for k, v in self.cost.items()}
        cost["agent_state"] = 3.0 * G * G          # state words (not rates)
        if self.use_field:
            cost["medium_state"] = 4.0 * G * G     # only arms that route on
        if self.policy == "oracle":                # the medium pay for it
            cost["oracle_read"] = 1.0 * G * G      # global-state access
        produced = np.trapezoid(uprod, dx=dt, axis=1)
        return dict(
            resolved_t=resolved_t,
            failure=(resolved_t > self.deadline).astype(float),
            unmet_rate=unmet.mean(axis=1),
            N_end=Ntot[:, -1], N_peak=Ntot.max(axis=1), N_base=self.N_tot0,
            u_end=uprod[:, -1], u_peak=uprod.max(axis=1), u0=self.u0,
            produced=produced, osc=Ntot[:, -n_q:].std(axis=1),
            false_burn=false_burn, false_held=false_held,
            cost=cost, T=T, deadline=self.deadline)

    def _outage(self, t):
        return any(a <= t < b for a, b in self.oracle_outages)
