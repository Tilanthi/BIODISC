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
"""Board-protocol fleet-charging simulator (Traffic paper, Phase IV).

Discrete-event minute ticks over a 24 h horizon.  N fleet EVs on job
cycles decide where/when to charge; M stations with stalls, power and
contract masks serve them.  Coordination arms:

  BOARD       shared one-way board: staleness decay f(dt), decay-reclaim
              of stale bookings, attractor-beam reroute cohorts, priority
              channel with attestation + per-fleet budget
  NODECAY     same plant and protocol, trust never decays (isolates the
              pheromone: EVs keep trusting reports from dead stations)
  CENTRAL     full-fresh-knowledge global greedy every cycle (the
              upper-bound incumbent; its op count is the O(n m) bill)
  NEAREST     no bookings: drive to nearest station, FIFO queue (the
              naive incumbent)

Scenarios (kwargs): drop (report loss), outage=(a,b) wholesale window
(40% of stations die at minute a, revive at b), longtail (session
overrun sigma, lognormal), noshow (booked EV fails to appear, booking
released only by staleness), fraud (share of EVs falsely claiming dire
priority), preempt_events (medical mid-charge preemptions per day).

All draws through numpy Generator.  The no-double-book invariant is
asserted at every slot write.
"""

from __future__ import annotations

import numpy as np

# ----------------------------------------------------------------- constants
HORIZON = 24 * 60             # minutes
BUCKET = 5                    # booking bucket, minutes
NB = HORIZON // BUCKET        # 288 buckets
REPORT = 5                    # report cadence, minutes
TTL = 30                      # staleness horizon: confidence reaches 0
ALPHA = 3.0                   # decay exponent (slow, then fast)
MAXB = 24                     # max booking length in buckets (120 min)
KMIT = 40.0                   # world side, km
SPEED = 40.0 / 60.0           # km per minute
CONS = 1.2                    # kWh per km
STALE_OWN = 2 * REPORT        # owner stale after 2 missed reports
VLT = 0.15                    # genuine dire SoC threshold
VICINITY = 6.0                 # decision radius, km (the k in O(nk))
W_AGE = 0.4                    # wait-time aging weight (anti-starvation)


def conf(age_min, alpha=ALPHA, ttl=TTL):
    """Pheromone confidence in [0,1]: slow at first, 0 at TTL."""
    a = np.asarray(age_min, float)
    return np.maximum(0.0, 1.0 - np.power(np.minimum(a, ttl) / ttl, alpha))


# ================================================================ metrics
class Metrics:
    def __init__(self, world):
        self.w = world
        self.served = 0
        self.energy = 0.0
        self.stranded = 0
        self.unmet = 0
        self.wait_times = []
        self.wait_honest = []
        self.dire_wait = []
        self.book_race = 0            # writes that lost the CAS race
        self.invariant_violation = 0  # actual occupancy > capacity
        self.queries = 0
        self.cand_scans = 0
        self.central_ops = 0
        self.polls = 0
        self.fraud_prio_served = 0
        self.genuine_prio = 0
        self.fraud_caught = 0
        self.preemptions = 0
        self.walkins = 0
        self.reroutes = 0
        self.reclaim_release = 0
        self.stall_min = 0.0
        self.max_queue = 0

    def summary(self):
        w = self.w
        v = np.asarray(self.wait_times)
        h = np.asarray(self.wait_honest)
        d = np.asarray(self.dire_wait)
        return dict(
            served=self.served, energy_kwh=round(self.energy, 1),
            stranded=self.stranded, stranded_frac=self.stranded / w.n,
            unmet=self.unmet,
            wait_mean=float(v.mean()) if v.size else 0.0,
            wait_p95=float(np.percentile(v, 95)) if v.size else 0.0,
            honest_wait_mean=float(h.mean()) if h.size else 0.0,
            dire_wait_mean=float(d.mean()) if d.size else 0.0,
            jain=_jain(v),
            book_race=self.book_race,
            invariant_violation=self.invariant_violation,
            polls=self.polls, queries=self.queries,
            cand_scans=self.cand_scans,
            cand_per_query=self.cand_scans / max(self.queries, 1),
            central_ops=self.central_ops,
            fraud_prio_served=self.fraud_prio_served,
            genuine_prio=self.genuine_prio,
            fraud_caught=self.fraud_caught,
            preemptions=self.preemptions,
            walkins=self.walkins, reroutes=self.reroutes,
            reclaim_release=self.reclaim_release,
            stall_util=self.stall_min / (w.stalls.sum() * HORIZON),
            max_queue=self.max_queue)


def _jain(x):
    if x.size == 0:
        return 1.0
    return float((x.sum() ** 2) / (x.size * (x ** 2).sum()))


# ================================================================ grid
class Grid:
    """Uniform grid over the city; vicinity lookup without full scans."""

    def __init__(self, x, y, cell=8.0):
        self.cell = cell
        self.d = {}
        for j in range(len(x)):
            k = (int(x[j] // cell), int(y[j] // cell))
            self.d.setdefault(k, []).append(j)
        self._cache = {}

    def query(self, x, y, radius=16.0):
        cx, cy = int(x // self.cell), int(y // self.cell)
        r = int(radius // self.cell) + 1
        key = (cx, cy, r)
        if key in self._cache:
            return self._cache[key]
        out = []
        for a in range(cx - r, cx + r + 1):
            for b in range(cy - r, cy + r + 1):
                out.extend(self.d.get((a, b), ()))
        self._cache[key] = out
        return out


# ================================================================ simulator
class Sim:
    def __init__(self, arm="BOARD", beam=True, prio=True, attest=True,
                 attest_detect=0.8, prio_budget=0.05, central_cycle=15,
                 emergency_range=12.0, seed=0, n_ev=10_000, n_st=250,
                 fraud=0.0, drop=0.0, outage=(None, None), longtail=0.0,
                 noshow=0.0, preempt_events=0, contract_frac=0.3,
                 drain_scale=1.0, reclaim=True):
        assert arm in ("BOARD", "NODECAY", "CENTRAL", "NEAREST")
        self.arm = arm
        self.use_board = arm in ("BOARD", "NODECAY")
        self.decay = (arm != "NODECAY")
        self.beam = beam and arm == "BOARD"
        self.prio = prio and arm == "BOARD"
        self.attest = attest and arm == "BOARD"
        self.attest_detect = attest_detect
        self.prio_budget = prio_budget
        self.central_cycle = central_cycle
        self.emergency_range = emergency_range
        self.fraud, self.drop = fraud, drop
        self.outage = outage
        self.longtail, self.noshow = longtail, noshow
        self.preempt_events = preempt_events
        self.contract_frac = contract_frac
        self.drain_scale = drain_scale
        self.reclaim = reclaim
        self._build(n_ev, n_st, seed)

    # ------------------------------------------------------------- build
    def _build(self, n, m, seed):
        r = self.rng = np.random.default_rng(seed)
        self.n, self.m = n, m
        # ---- stations
        self.st_x = r.uniform(0, KMIT, m)
        self.st_y = r.uniform(0, KMIT, m)
        self.stalls = r.integers(4, 13, m).astype(np.int16)
        self.power = r.choice([50.0, 150.0, 350.0], m, p=[.25, .55, .20])
        self.contract_fleet = r.integers(0, 10, m)
        self.reserved = np.floor(self.contract_frac
                                 * self.stalls).astype(np.int16)
        self.st_age = np.zeros(m)
        self.st_dead = np.zeros(m, bool)
        self.st_rep = r.integers(0, REPORT, m)
        # ---- EVs
        self.ev_x = r.uniform(0, KMIT, n)
        self.ev_y = r.uniform(0, KMIT, n)
        self.batt = r.uniform(80.0, 145.0, n)
        self.legacy_ev = r.random(n) < 0.25
        self.fleet = r.integers(0, 10, n)
        self.fleet_size = np.bincount(self.fleet, minlength=10)
        self.soc = r.uniform(0.45, 0.95, n)
        self.honest = r.random(n) >= self.fraud
        self.work_end = r.integers(20, 160, n)
        self.break_len = r.integers(30, 91, n)
        # states: 0 work, 1 seek, 2 drive, 3 queue, 4 charge, 5 resume, 9 out
        self.state = np.zeros(n, np.int8)
        self.book_st = np.full(n, -1, np.int16)
        self.book_b0 = np.full(n, -1, np.int16)
        self.book_b1 = np.full(n, -1, np.int16)
        self.eta = np.zeros(n, np.int32)
        self.sess_end = np.zeros(n, np.int32)
        self.sess_st = np.full(n, -1, np.int16)
        self.wait_start = np.zeros(n, np.int32)
        self.plan_kwh = np.zeros(n)
        self.claim_prio = np.zeros(n, bool)
        self.preempted = np.zeros(n, bool)
        self.no_prio = np.zeros(n, bool)
        self.poll = r.integers(0, REPORT, n)
        self.ev_age = np.zeros(n)
        self.stale_credit = np.zeros(n, bool)
        self.noshow_draw = np.zeros(n, bool)
        self.mute = np.zeros(n, bool)
        # ---- board
        self.occ = np.zeros((m, NB), np.int16)
        self.occ_stale = np.zeros((m, NB), np.int16)
        self.beam_targets = {}
        self.prio_tokens = np.zeros(10)
        self.prio_hour = 0
        self.metrics = Metrics(self)
        self.grid = Grid(self.st_x, self.st_y, cell=3.0)
        # effective power table: (legacy, fast) x (50, 150, 350 kW)
        self._pwt = np.array([[50.0, 50.0, 50.0],
                              [50.0, 150.0, 350.0]], np.float32)
        self._pcls = ((self.power == 50) * 0 + (self.power == 150) * 1
                      + (self.power == 350) * 2).astype(np.int8)
        self._ev_cls = np.where(self.legacy_ev, 0, 1).astype(np.int8)
        self.preempt_times = np.sort(
            r.integers(120, HORIZON - 60, self.preempt_events)) \
            if self.preempt_events else np.array([], int)
        self._serving_ref = []

    def pw_for(self, i, j):
        return float(self._pwt[self._ev_cls[i], self._pcls[j]])

    # ================================================================ run
    def run(self):
        serving = [[] for _ in range(self.m)]
        queues = [[] for _ in range(self.m)]
        qlen = np.zeros(self.m, np.int32)
        self._serving_ref = serving
        for t in range(HORIZON):
            self._scenario(t, serving)
            self._reports(t)
            if self.use_board:
                self._reclaim(t)
            self._transitions(t)
            if self.arm in ("BOARD", "NODECAY"):
                self._board_poll(t)
            elif self.arm == "CENTRAL" and t % self.central_cycle == 0:
                self._central(t)
            elif self.arm == "NEAREST":
                self._nearest_poll(t)
            self._arrivals(t, queues, qlen)
            self._serve(t, queues, qlen, serving)
            self._charge(t, serving)
            self.metrics.stall_min += sum(len(s) for s in serving)
            self.metrics.max_queue = max(self.metrics.max_queue,
                                         int(qlen.max()))
        return self.metrics.summary()

    # ------------------------------------------------------------ scenario
    def _scenario(self, t, serving):
        a, b = self.outage
        if a is not None and t == a:
            k = int(0.4 * self.m)
            dead = self.rng.choice(self.m, k, replace=False)
            self.st_dead[dead] = True
        if b is not None and t == b:
            self.st_dead[:] = False
            self.st_age[self.st_rep == t % REPORT] = 0
        if self.preempt_events and t in self.preempt_times:
            self._preempt_medical(t, serving)

    def _preempt_medical(self, t, serving):
        charging = np.where((self.state == 4)
                            & (self.sess_end > t + 10))[0]
        if charging.size == 0:
            return
        i = int(self.rng.choice(charging))
        j = int(self.sess_st[i])
        if j in range(len(serving)) and i in serving[j]:
            serving[j].remove(i)
        # partial credit for the partial session
        kwh = 0.3 * self.plan_kwh[i]
        self.soc[i] = min(1.0, self.soc[i] + kwh / self.batt[i])
        self.state[i] = 1
        self.wait_start[i] = t
        self.claim_prio[i] = True
        self.no_prio[i] = False
        self.preempted[i] = True
        self.metrics.preemptions += 1

    # ------------------------------------------------------------- reports
    def _reports(self, t):
        due = (self.poll == t % REPORT) & ~self.mute
        M = self.metrics
        M.polls += int(due.sum())
        drop = self.rng.random(int(due.sum())) < self.drop
        idx = np.where(due)[0]
        self.ev_age[idx[~drop]] = 0
        rep = self.st_rep == t % REPORT
        self.st_age[rep & ~self.st_dead] = 0
        self.st_age += 1
        self.ev_age += 1

    # ------------------------------------------------------------- reclaim
    def _reclaim(self, t):
        """Credit stale-owned bookings; TTL-release abandoned ones.
        With reclaim=False an abandoned booking is honoured blind for
        its full scheduled window (airline-style hold): the slot idles
        until the window passes and only then returns the owner to
        the pool.  The board instead releases at the staleness TTL."""
        if self.reclaim:
            newly = np.where((self.book_st >= 0) & ~self.stale_credit
                             & (self.ev_age > STALE_OWN))[0]
            for i in newly:
                self.occ_stale[self.book_st[i],
                               self.book_b0[i]:self.book_b1[i]] += 1
                self.stale_credit[i] = True
            gone = np.where((self.book_st >= 0)
                            & ((self.ev_age >= TTL) | (self.state == 9)
                               | (self.state == 0)))[0]
        else:
            gone = np.where((self.book_st >= 0)
                            & ((self.book_b1 * BUCKET <= t)
                               | (self.state == 9)
                               | (self.state == 0)))[0]
        for i in gone:
            self._release(i)
            self.book_st[i] = -1
            self.mute[i] = False
            self.metrics.reclaim_release += 1

    # --------------------------------------------------------- transitions
    def _transitions(self, t):
        r = self.rng
        done = np.where((self.state == 5) & (self.eta <= t))[0]
        if done.size:
            self.state[done] = 0
            self.work_end[done] = t + r.integers(60, 240, done.size)
            self.ev_x[done] = r.uniform(0, KMIT, done.size)
            self.ev_y[done] = r.uniform(0, KMIT, done.size)
            self.soc[done] = np.maximum(0.0, self.soc[done] - self.drain_scale
                                        * r.uniform(0.05, 0.15, done.size))
        new = np.where((self.state == 0) & (self.work_end <= t))[0]
        if new.size:
            hi = self.soc[new] > 0.7
            skip = new[hi]
            self.work_end[skip] = t + r.integers(60, 240, skip.size)
            self.soc[skip] = np.maximum(0.0, self.soc[skip] - self.drain_scale
                                        * r.uniform(0.02, 0.08, skip.size))
            go = new[~hi]
            self.state[go] = 1
            self.wait_start[go] = t
            self._set_priority(go)
        # break window expired while still seeking/queued -> give up
        for st in (1, 3):
            timeout = np.where((self.state == st)
                               & (t - self.wait_start > self.break_len)
                               & ~self.claim_prio)[0]
            if timeout.size:
                self.state[timeout] = 5
                self.eta[timeout] = t + 5
                self.metrics.unmet += timeout.size
                for i in timeout:
                    self._release(i)
                    self.book_st[i] = -1
        # dire escalation while waiting
        for st in (1, 2, 3):
            esc = np.where((self.state == st) & ~self.claim_prio
                           & ~self.no_prio & (self.soc < 0.10))[0]
            self.claim_prio[esc] = True
            self.metrics.genuine_prio += esc.size

    def _set_priority(self, go):
        self.claim_prio[go] = False
        gen = go[self.soc[go] < VLT]
        self.claim_prio[gen] = True
        self.metrics.genuine_prio += gen.size
        fr = go[~self.honest[go]]
        liars = fr[self.soc[fr] < 0.45]
        self.claim_prio[liars] = True

    def _release(self, i):
        j, b0, b1 = self.book_st[i], self.book_b0[i], self.book_b1[i]
        if j < 0 or b0 < 0:
            return
        self.occ[j, b0:b1] -= 1
        if self.stale_credit[i]:
            self.occ_stale[j, b0:b1] -= 1
            self.stale_credit[i] = False
        self.book_b0[i] = self.book_b1[i] = -1

    # ---------------------------------------------------------- board poll
    def _board_poll(self, t):
        cand = np.where((self.state == 1)
                        & (self.poll == t % REPORT))[0]
        if cand.size == 0:
            return
        M = self.metrics
        M.queries += cand.size
        # attestation on priority claims (telemetry cross-check)
        if self.prio:
            if t - self.prio_hour >= 60:
                self.prio_tokens[:] = 0
                self.prio_hour = t
            for i in cand[self.claim_prio[cand]]:
                self._attest(i)
        cf = conf(self.st_age) if self.decay else np.ones(self.m)
        winners = self._score_batch(cand, t, cf)
        won = set()
        for i, j, b0, b1, bumped in winners:
            self._book(i, j, b0, b1, t, bumped=bumped)
            won.add(i)
        # fallback: unbooked EVs drive to the nearest REACHABLE live
        # station (walk-in); a dire EV that can reach nothing is towed
        for i in cand:
            if i in won or self.state[i] != 1:
                continue
            j = self._nearest_live(i, max_d=self._range_km(i))
            if j is not None:
                self._send(i, j, t, walk_in=True)
                self.metrics.walkins += 1
            elif self.soc[i] < 0.05:
                self._strand(i)

    def _attest(self, i):
        """Anti-fraud: telemetry check + per-fleet priority budget.
        With attest=False the channel is fully credulous: no telemetry
        check, no budget."""
        if not self.attest:
            return
        if self.claim_prio[i] and self.soc[i] >= VLT and not self.honest[i]:
            if self.rng.random() < self.attest_detect:
                self.claim_prio[i] = False
                self.no_prio[i] = True
                self.metrics.fraud_caught += 1
                return
        # unverifiable claims draw on the fleet's hourly budget
        if self.claim_prio[i] and self.soc[i] >= VLT:
            f = self.fleet[i]
            self.prio_tokens[f] += 1
            if self.prio_tokens[f] > self.prio_budget * self.fleet_size[f]:
                self.claim_prio[i] = False

    def _score_batch(self, cand, t, cf):
        """Vectorised vicinity scoring -> [(i, j, b0, b1, bumped), ...]."""
        M = self.metrics
        gq = self.grid.query
        ex, ey = self.ev_x, self.ev_y
        pairs_e, pairs_j = [], []
        for i in cand:
            for j in gq(ex[i], ey[i], VICINITY):
                if not self.st_dead[j]:
                    pairs_e.append(i)
                    pairs_j.append(j)
        if not pairs_e:
            return []
        pe = np.asarray(pairs_e)
        pj = np.asarray(pairs_j)
        dist = np.hypot(self.st_x[pj] - ex[pe], self.st_y[pj] - ey[pe])
        rng_km = self.soc[pe] * self.batt[pe] / CONS * 0.5
        own = self.fleet[pe] == self.contract_fleet[pj]
        cap = np.where(own, self.stalls[pj],
                       self.stalls[pj] - self.reserved[pj])
        pw = self._pwt[self._ev_cls[pe], self._pcls[pj]]
        deficit = np.maximum(0.0, (0.9 - self.soc[pe]) * self.batt[pe])
        b_len = np.ceil(deficit / pw * 60.0 / BUCKET).astype(np.int32)
        window = np.minimum(self.break_len[pe] + 30, 120)
        b_len = np.minimum(b_len, window // BUCKET)
        b_start = (t + 10) // BUCKET + 1
        ok = (dist <= np.minimum(rng_km, VICINITY)) & (cap >= 1) \
            & (pw >= 30) & (b_len >= 1) & (b_start + b_len <= NB)
        pe, pj, dist, cap, pw, b_len = (v[ok] for v in
                                        (pe, pj, dist, cap, pw, b_len))
        M.cand_scans += pe.size          # post-filter: the true k
        if pe.size == 0:
            return []
        # segment occupancy: (P, MAXB) gather; -1e6 marks invalid cells
        occs = np.full((pe.size, MAXB), -10 ** 6, np.int32)
        stal = np.zeros((pe.size, MAXB), np.int32)
        for k in range(MAXB):
            m_ = k < b_len
            bb = min(b_start + k, NB - 1)
            occs[m_, k] = self.occ[pj[m_], bb]
            stal[m_, k] = self.occ_stale[pj[m_], bb]
        free_min = (cap[:, None] - occs).min(axis=1)
        stale_min = stal.min(axis=1)
        confj = cf[pj] if self.decay else np.ones(pj.size)
        eff_free = free_min.copy()
        bumpable = np.zeros(pe.size, bool)
        if self.prio:
            pri = self.claim_prio[pe] & ~self.no_prio[pe]
            # stale-owned slots usable at full credit by priority EVs
            eff_free = np.where(pri & (stale_min >= 1),
                                np.maximum(eff_free + 1, 1), eff_free)
            # emergency bump: dire EV displaces newest non-prio booking
            bumpable = (pri & (free_min < 1) & (stale_min < 1)
                        & (dist <= self.emergency_range)
                        & (occs.min(axis=1) >= 0))
            eff_free = np.where(bumpable, np.maximum(eff_free, 1), eff_free)
        feas = (eff_free >= 1) & (confj > 0.05)
        if not feas.any():
            return []
        beam_b = np.zeros(pe.size)
        if self.beam and self.beam_targets:
            live_beam = {j for j, (c, ts) in self.beam_targets.items()
                         if t - ts < TTL}
            keys = np.array([j in live_beam for j in pj])
            beam_b[keys] = 0.25
        age = np.minimum((t - self.wait_start[pe]) / 60.0, 1.5) * W_AGE
        score = (np.log(pw / 50.0) + 0.6 * np.exp(-dist / 12.0)
                 + 2.0 * (confj - 1.0) + beam_b + age)
        score = np.where(feas, score, -np.inf)
        best = np.full(self.n, -np.inf)
        np.maximum.at(best, pe, score)
        sel = np.isfinite(score) & (score >= best[pe] - 1e-12)
        if not sel.any():
            return []
        # first pair per EV (cand is in priority order)
        _, first_idx = np.unique(pe[sel], return_index=True)
        idx = np.where(sel)[0][first_idx]
        out = []
        for k in idx:
            out.append((int(pe[k]), int(pj[k]), int(b_start),
                        int(b_start + b_len[k]), bool(bumpable[k])))
        return out

    def _do_bump(self, i, j, t):
        """Dire EV displaces the newest non-priority booking at j."""
        cands = np.where((self.book_st == j) & ~self.claim_prio
                         & ~self.preempted)[0]
        if cands.size == 0:
            return -1
        victim = int(cands[np.argmax(self.wait_start[cands])])
        self._release(victim)
        self.book_st[victim] = -1
        if self.state[victim] in (2, 3):
            self.state[victim] = 1
        self.preempted[victim] = True
        self.metrics.preemptions += 1
        return victim

    def _book(self, i, j, b0, b1, t, bumped=False):
        if bumped:
            if self._do_bump(i, j, t) < 0:
                return False                 # nobody to displace
        cap = self.stalls[j] if self.fleet[i] == self.contract_fleet[j] \
            else self.stalls[j] - self.reserved[j]
        if np.any(self.occ[j, b0:b1] >= cap):
            self.metrics.book_race += 1
            return False
        self.occ[j, b0:b1] += 1
        self.book_st[i], self.book_b0[i], self.book_b1[i] = j, b0, b1
        self.stale_credit[i] = False
        self.noshow_draw[i] = self.rng.random() < self.noshow
        self.plan_kwh[i] = (b1 - b0) * BUCKET / 60.0 * self.pw_for(i, j)
        self._send(i, j, t)
        if self.claim_prio[i] and not self.honest[i]:
            self.metrics.fraud_prio_served += 1
        return True

    def _send(self, i, j, t, walk_in=False):
        self.book_st[i] = j                    # drive target (always)
        if walk_in:
            self.book_b0[i] = self.book_b1[i] = -1
        self.state[i] = 2
        d = np.hypot(self.st_x[j] - self.ev_x[i],
                     self.st_y[j] - self.ev_y[i])
        self.eta[i] = t + max(int(d / SPEED), 1)
        if walk_in:
            self.plan_kwh[i] = max((0.9 - self.soc[i]) * self.batt[i], 5.0)

    # --------------------------------------------------------- central arm
    def _central(self, t):
        cand = np.where(self.state == 1)[0]
        if cand.size == 0:
            return
        M = self.metrics
        order = np.lexsort((self.soc[cand], ~self.claim_prio[cand]))
        cand = cand[order]
        b_start = (t + 10) // BUCKET + 1
        free = (self.stalls[:, None] - self.occ).astype(np.int32)
        for i in cand:
            deficit = max(0.0, (0.9 - self.soc[i]) * self.batt[i])
            window = min(self.break_len[i] + 30, 120)
            best, best_s, best_bl = -1, -1e18, 1
            rng_km = self.soc[i] * self.batt[i] / CONS * 0.5
            for j in range(self.m):
                if self.st_dead[j]:
                    continue
                pw = self.pw_for(i, j)
                if pw < 30:
                    continue
                M.central_ops += 1
                d = np.hypot(self.st_x[j] - self.ev_x[i],
                             self.st_y[j] - self.ev_y[i])
                if d > rng_km:
                    continue
                cap = free[j, :] - (0 if self.fleet[i] == self.contract_fleet[j]
                                    else self.reserved[j])
                bl = min(int(np.ceil(deficit / pw * 60.0 / BUCKET)),
                         window // BUCKET, MAXB)
                if bl < 1 or b_start + bl > NB:
                    continue
                if cap[b_start:b_start + bl].min() < 1:
                    continue
                s = np.log(pw / 50.0) + 0.6 * np.exp(-d / 12.0)
                if s > best_s:
                    best, best_s, best_bl = j, s, bl
            if best >= 0:
                free[best, b_start:b_start + best_bl] -= 1
                self.occ[best, b_start:b_start + best_bl] += 1
                self.book_st[i] = best
                self.book_b0[i], self.book_b1[i] = b_start, b_start + best_bl
                self.stale_credit[i] = False
                self.noshow_draw[i] = self.rng.random() < self.noshow
                self._send(i, best, t)
                self.plan_kwh[i] = best_bl * BUCKET / 60.0 \
                    * self.pw_for(i, best)

    # --------------------------------------------------------- nearest arm
    def _nearest_poll(self, t):
        cand = np.where((self.state == 1)
                        & (self.poll == t % REPORT))[0]
        for i in cand:
            j = self._nearest_live(i, max_d=self._range_km(i))
            if j is None:
                if self.soc[i] < 0.05:
                    self._strand(i)
                continue
            self.metrics.queries += 1
            self.metrics.cand_scans += len(
                self.grid.query(self.ev_x[i], self.ev_y[i], 25.0))
            self._send(i, j, t, walk_in=True)
            self.metrics.walkins += 1

    def _nearest_live(self, i, max_d=None):
        """Nearest live station; if max_d given, only reachable ones."""
        best, bd = -1, 1e9
        for j in self.grid.query(self.ev_x[i], self.ev_y[i], 25.0):
            if self.st_dead[j] or self.pw_for(i, j) < 30:
                continue
            d = np.hypot(self.st_x[j] - self.ev_x[i],
                         self.st_y[j] - self.ev_y[i])
            if d < bd and (max_d is None or d <= max_d):
                best, bd = j, d
        return best if best >= 0 else None

    def _range_km(self, i, margin=0.8):
        return margin * self.soc[i] * self.batt[i] / CONS

    # ------------------------------------------------------------ movement
    def _arrivals(self, t, queues, qlen):
        arr = np.where((self.state == 2) & (self.eta <= t))[0]
        for i in arr:
            j = int(self.book_st[i])
            if j < 0:
                self.state[i] = 1
                continue
            if self.st_dead[j]:
                self._reroute(i, t)
                continue
            d = np.hypot(self.st_x[j] - self.ev_x[i],
                         self.st_y[j] - self.ev_y[i])
            self.soc[i] = max(0.0, self.soc[i] - d * CONS / self.batt[i])
            if self.soc[i] <= 0.001:
                self._strand(i)
                continue
            self.ev_x[i], self.ev_y[i] = self.st_x[j], self.st_y[j]
            if self.use_board and self.book_b0[i] >= 0 \
                    and not self.noshow_draw[i]:
                self.state[i] = 3
                queues[j].insert(0, i)            # booked: head of line
            elif self.book_b0[i] >= 0 and self.noshow_draw[i]:
                # no-show (any booked arm): drives off, goes silent;
                # the abandoned booking is reclaimed only by staleness
                self.state[i] = 5
                self.eta[i] = t + 10
                self.mute[i] = True
            else:
                self.state[i] = 3
                queues[j].append(i)
            qlen[j] = len(queues[j])

    def _reroute(self, i, t):
        """Attractor beam: EV aimed at a dead station follows the cohort.
        Releases the abandoned booking before moving on."""
        self.metrics.reroutes += 1
        self._release(i)
        j = self._nearest_live(i, max_d=self._range_km(i))
        if j is None:
            if self.soc[i] < 0.05:
                self._strand(i)
            else:
                self.state[i] = 1
            return
        if self.beam:
            c, ts = self.beam_targets.get(j, (0, t))
            self.beam_targets[j] = [c + 1, ts]
        self.book_b0[i] = self.book_b1[i] = -1
        self._send(i, j, t, walk_in=True)

    def _strand(self, i):
        self.state[i] = 9
        self.metrics.stranded += 1
        self._release(i)
        self.book_st[i] = -1

    # ------------------------------------------------------ queues/serving
    def _serve(self, t, queues, qlen, serving):
        for j in range(self.m):
            q = queues[j]
            if self.st_dead[j]:
                for i in q:
                    self._reroute(i, t)
                queues[j] = []
                qlen[j] = 0
                continue
            while q and len(serving[j]) < self.stalls[j]:
                k = next((k for k, i in enumerate(q) if self.claim_prio[i]),
                         0)
                i = q.pop(k)
                qlen[j] = len(q)
                self._start_session(i, j, t, serving)

    def _start_session(self, i, j, t, serving):
        pw = self.pw_for(i, j)
        need = max((0.9 - self.soc[i]) * self.batt[i], 5.0)
        kwh = need if self.plan_kwh[i] <= 0 else min(need, self.plan_kwh[i])
        dur = kwh / pw * 60.0
        if self.longtail > 0:
            dur *= float(self.rng.lognormal(0.0, self.longtail))
        self.state[i] = 4
        self.sess_end[i] = t + max(int(dur), 5)
        self.sess_st[i] = j
        self.plan_kwh[i] = kwh
        serving[j].append(i)
        self.metrics.wait_times.append(t - self.wait_start[i])
        if self.honest[i]:
            self.metrics.wait_honest.append(t - self.wait_start[i])
        if self.claim_prio[i]:
            self.metrics.dire_wait.append(t - self.wait_start[i])
        if int(self.book_st[i]) == j:
            self._release(i)
            self.book_st[i] = -1

    def _charge(self, t, serving):
        done = np.where((self.state == 4) & (self.sess_end <= t))[0]
        for i in done:
            j = int(self.sess_st[i])
            if 0 <= j < len(serving) and i in serving[j]:
                serving[j].remove(i)
            kwh = self.plan_kwh[i]
            self.soc[i] = min(1.0, self.soc[i] + kwh / self.batt[i])
            self.metrics.served += 1
            self.metrics.energy += kwh
            self.state[i] = 5
            self.eta[i] = t + self.rng.integers(5, 20)
            self.claim_prio[i] = False
            self.no_prio[i] = False
            self.preempted[i] = False


# ---------------------------------------------------------------- runner
def run_arm(arm, seed=0, **kw):
    return Sim(arm=arm, seed=seed, **kw).run()


if __name__ == "__main__":
    import json, sys
    arm = sys.argv[1] if len(sys.argv) > 1 else "BOARD"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    kw = dict(n_ev=n, n_st=max(n // 40, 10))
    print(json.dumps(run_arm(arm, **kw), indent=2))
