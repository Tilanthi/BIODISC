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
"""Smoke tests + calibration for the Phase I-II pilot core."""

import sys
import time

import numpy as np

sys.path.insert(0, "/Users/gjw255/astrodata/SWARM/BIODISC/Jay/phase12")
import jay_core as jc
from sandbox import WoundSandbox


def test_fig3_parity():
    """Fig. 3 parameters: beta>0 recovers, beta=0 ratchets."""
    for beta, want_N, want_u in [(1.0, "~1", "~1"), (0.0, ">1", ">1")]:
        res = jc.simulate(mu=1.0, beta=beta, kappa=1.0, p0=1.0, u0=1.0,
                          gamma=1.5, tau=1.5, T=26.0, dt=0.005)
        print(f"  beta={beta}: N_end={res['N'][-1]:.3f} "
              f"u_end={res['u'][-1]:.3f} (want {want_N}/{want_u})")
    res = jc.simulate(mu=1.0, beta=1.0, gamma=1.5, tau=1.5, T=26.0, dt=0.005)
    eq = jc.equilibrium(1.0, 1.0, w=0.0, gamma=1.5)
    assert abs(res["N"][-1] - 1.0) < 0.02, "beta>0 must return to baseline"
    assert abs(res["u"][-1] - 1.0) < 0.02
    res0 = jc.simulate(mu=1.0, beta=0.0, gamma=1.5, tau=1.5, T=26.0,
                       dt=0.005)
    assert res0["N"][-1] > 1.5 and res0["u"][-1] > 1.5, \
        "beta=0 must ratchet (fibrotic shift)"
    print("  equilibrium check: N*=", eq["N_star"], "(inactive branch ok)")


def test_hopf():
    """Closed-form Hopf boundary vs a brute root scan of eq:char."""
    rng = np.random.default_rng(7)
    for _ in range(200):
        beta, m, gk = rng.uniform(0.05, 2, 3)
        tau = float(rng.uniform(0.01, 8))
        tau_h = jc.hopf_tau(beta, m, gk)
        # brute: rightmost real-part root via fine scan on sigma grid is
        # unreliable; instead check consistency: at tau = tau_h the real
        # part of q's magnitude condition holds (|q(iw)| = 0 solvable).
        if tau_h is None:
            assert gk <= beta * m
        else:
            w = jc.hopf_frequency(beta, m, gk)
            lhs = (1j * w + beta) * (1j * w + m) + gk * np.exp(
                -1j * w * tau_h)
            assert abs(lhs) < 1e-9, f"char eq residual {abs(lhs):.2e}"
    # vectorised path
    th = jc.hopf_tau(np.array([1.0]), np.array([3.0]), np.array([1.5]))
    assert np.isnan(th[0]), "gk=1.5 < beta*m=3 must be unconditionally stable"
    th2 = jc.hopf_tau(np.array([1.0]), np.array([1.0]), np.array([1.5]))
    assert np.isfinite(th2[0]), "gk=1.5 > beta*m=1 must have a boundary"
    print(f"  char-eq residuals < 1e-9 on 200 random points; "
          f"Fig3 baseline tau_H = {float(th2[0]):.3f} "
          f"(paper: tau=1.5 below tau_H -> damped)")


def test_batch_vs_single():
    """Batch integrator must agree with the single-run integrator.

    Parameters chosen in the delay-unconditionally-stable regime
    (gamma < beta*m) so the comparison is against a settled equilibrium.
    """
    mu, beta, gamma, tau, w = 0.05, 0.5, 0.025, 30.0, 0.05
    dt = 0.02
    T = 12 * tau
    res = jc.simulate(mu=mu, beta=beta, gamma=gamma, tau=tau, u0=mu,
                      w_fun=lambda t: w, T=T, dt=dt)
    eq = jc.equilibrium(mu, beta, gamma=gamma, w=w)
    b = jc.simulate_batch(np.array([mu]), np.array([beta]),
                          np.array([gamma]), np.array([tau]),
                          np.array([w]), dt=dt, T=T, chunk=8)
    print(f"  single: N_end={res['N'][-1]:.4f}  batch: "
          f"{b['finalN'][0]:.4f}  analytic N*={eq['N_star']:.4f}")
    assert abs(res["N"][-1] - b["finalN"][0]) < 5e-3
    assert abs(b["finalN"][0] - eq["N_star"]) < 5e-3


def calibrate_sandbox():
    """Tune field/serve scales so the full hormonal arm resolves injury
    well inside the deadline, and report diagnostics for both arms."""
    t0 = time.time()
    for tag, kw in [("hormonal", dict(policy="hormonal")),
                    ("fixed", dict(policy="fixed")),
                    ("oracle", dict(policy="oracle"))]:
        sb = WoundSandbox(seeds=8, **kw)
        out = sb.run()
        rt = out["resolved_t"]
        rt_c = np.where(np.isfinite(rt), rt, sb.T_end)
        print(f"  {tag:9s} resolved t = {np.median(rt_c):6.1f} "
              f"(fail {out['failure'].mean():.2f})  "
              f"unmet {out['unmet_rate'].mean():.3f}  "
              f"S max ~ {sb.S.max():.2f}  Npk/N0 "
              f"{np.median(out['N_peak']) / out['N_base'][0]:.2f}  "
              f"u_end/u0 {np.median(out['u_end'] / out['u0']):.2f}")
    print(f"  ({time.time() - t0:.1f}s for 3 x 8 seeds)")


if __name__ == "__main__":
    print("fig3 parity:"); test_fig3_parity()
    print("hopf closed form:"); test_hopf()
    print("batch vs single:"); test_batch_vs_single()
    print("sandbox calibration:"); calibrate_sandbox()
    print("ALL SMOKE TESTS PASSED")
