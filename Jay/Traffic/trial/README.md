# Bounded field trial (paper Appendix, v1.10)

Rung-1 instrument and pre-registered kill criteria for the bounded
field trial recommended by the paper's Phase V verdict. Deployability
ladder, cheapest rung first:

1. **Rung 1 — client-side decay reading.** No standardisation: any
   client computes staleness decay from timestamped status it already
   receives. *Status: instrumented; first light captured (2026-08-17).*
2. **Rung 2 — booking TTLs.** Additive server semantics
   (decay-reclaim of no-show capacity). Gated by K3/K4.
3. **Rung 3 — attested priority.** Last; billing/liability dominate.
   Gated by K5.

## Files

| file | role |
|---|---|
| `trial_client.py` | capture snapshots / analyze ages + decision flips |
| `kill_criteria.py` | frozen thresholds; evaluates reports, emits LaTeX |
| `gen_fixture.py` | OCPI-shaped fixture with controlled ages (instrument test) |
| `data/` | snapshots + reports (real feeds and fixture) |

The decay law (`TTL`, `ALPHA`, `conf`) is **imported from
`board_sim.py`** so the trial and the simulator cannot drift apart.

## Providers

| provider | auth | grade | status |
|---|---|---|---|
| `ocpi` | env `OCPI_URL`, `OCPI_TOKEN` (Token A) | operator telemetry | drop-in ready, needs operator credentials |
| `ocm` | env `OCM_KEY` | registry | implemented |
| `osm` | none (Overpass, 3-mirror fallback) | human survey | **captured: IE + Amsterdam** |
| `fixture` | none | synthetic | instrument validation |

## Commands

```bash
python trial_client.py capture --provider osm --area IE --out data/osm_IE.json
python trial_client.py capture --provider osm --bbox 52.27,4.66,52.46,5.06 \
    --limit 20000 --out data/osm_AMS.json
python trial_client.py analyze --snap data/osm_IE.json --out data/rung1_IE.json

python gen_fixture.py --out data/fixture_ocpi.json
python trial_client.py demo --fixture data/fixture_ocpi.json --out data/rung1_fixture.json

python kill_criteria.py --reports data/rung1_IE.json data/rung1_AMS.json \
    --out data/trial_verdict.json --tex ../tab_trialkill.tex
```

`analyze` measures: age percentiles, date coverage, implied T (the T
that would put the median age at f = 0.9), and leave-one-out top-1/top-3
decision-flip rates of Eq. 2 with vs without the decay term (queries at
station locations, vicinity 6 km, k ≤ 15 — the paper's decision radius).

## Pre-registered criteria (frozen before measurement)

| crit | rung | measurement | threshold | verdict if out |
|---|---|---|---|---|
| K1 | 1 | implied T | ∈ [15, 60] min | REVISE-T (KILL if no feed can do better) |
| K2 | 1 | top-1 flip rate | ≥ 1% | KILL rung 1 as no-op |
| K3 | 2 | field no-show rate | ≤ 0.30 | re-run E4 trade at field rates |
| K4 | 2/3 | Jain(wait), weekly | ≥ 0.20 | KILL |
| K5 | 3 | genuine-dire false rejection | ≤ 0.20 | KILL |

## First light (2026-08-17, OSM)

| snapshot | records | dated | median age | implied T | top-1 flips |
|---|---|---|---|---|---|
| Ireland (national) | 1,061 | 2.4% | ≈ 2.25 yr | ≈ 4.9 yr | 0/346 |
| Amsterdam (bbox) | 1,378 | 1.6% | ≈ 6.4 mo | ≈ 1.2 yr | 0/400 |
| fixture (instrument test) | 48 | 100% | 18.5 min | 39.8 min | 58.3% |

Verdict (per the frozen criteria): **K1 REVISE-T** (implied T five
orders of magnitude outside the envelope), **K2 KILL-as-no-op** on
web-grade feeds: with ~98% of records undated and the dated tail
months-to-years old, the law reads *uniform* zero trust, which is a
constant offset to every score — rankings are unchanged, so
decay-weighted reading changes no decisions. The fixture (heterogeneous
ages, 58% flips) proves the zero is a property of the feed, not of the
analyzer.

**Conclusion:** human-survey-grade feeds cannot support rung 1 — the
kill criteria did their job on the worst-case feed. Rung 1 requires
OCPI-grade telemetry; the client is drop-in ready for an operator
(`OCPI_URL` + `OCPI_TOKEN`). K3–K5 stay registered for rungs 2–3.
