# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: V8.0.38 — VERIFICATION-FIRST (Eureka-steering rebuild: anomaly-first discovery — observed surprises are now the primary input)
**Capability**: not a fixed % — measured by the capability index (`capability_index.json`). **20 genuine discoveries** to date (internally replicated; genuine store cleaned of ~6.2k legacy unreplicated rows on 2026-07-17). Index ~15/100; trend is the signal.
**GitHub**: https://github.com/Tilanthi/BIODISC (ONLY repository)
**Remote**: `biodisc` (use `git push biodisc main` — ONLY main branch)

**Full version history**: `docs/12_version_history.md`

## CRITICAL: GitHub Push Rules

✅ ALWAYS push to: `https://github.com/Tilanthi/BIODISC`, `main` branch only
❌ NEVER push to: ASTRA-dev, origin, or any other branch

```bash
git add . && git commit -m "🧬 BIODISC: descriptive message" && git push biodisc main
```

## Most Common Tasks

**Check Discovery Status:**
```bash
# GENUINE (replicated) findings
wc -l autonomous_discoveries.jsonl && tail -1 autonomous_discoveries.jsonl | python -m json.tool

# CANDIDATE quarantine (unreplicated)
wc -l autonomous_discoveries_candidates.jsonl

# Discovery funnel — WHERE candidates die
python -c "from biodisc_core.fixed_pipeline.verdict_log import print_funnel; print_funnel()"

# Capability index + RSI effectiveness
python -c "from biodisc_core.fixed_pipeline.capability_index import run; run()"
```

**Start / Restart Autonomous Discovery:**
```bash
# The watchdog auto-starts. Manual restart:
ps aux | grep fixed_autonomous_discovery | grep -v grep  # check running
python discovery_watchdog.py &                            # start watchdog
```

**Run Tests:**
```bash
python -m pytest tests/ -q
```

**Run the RSI Miner (self-improvement loop):**
```bash
python -m biodisc_core.fixed_pipeline.rsi_miner        # mine failures → propose fixes → measure
python -m biodisc_core.fixed_pipeline.capability_index  # compute the index
```

**Use BIODISC Interactively:**
```python
from biodisc_core import create_biodisc_system
system = create_biodisc_system()
result = system.answer("What causes protein misfolding?")
```

## Critical Reminders

- **WRITE CHOKEPOINT**: Every discovery goes through `discovery_store.append_verified` (requires a machine verification block). Never add a second write path. Genuine → `autonomous_discoveries.jsonl`; candidates → `autonomous_discoveries_candidates.jsonl`. (The 4 dormant legacy bypass writes were neutralized to `raise RuntimeError` on 2026-07-17, making the chokepoint structurally — not just conventionally — the only write path.)
- **6-LAYER VALIDATION + REPLICATION**: duplicate / dataset-question / probe-gene / FDR-significance / template / PubMed Gate-2 (literature novelty), plus a held-out replication anchor for `is_genuine`.
- **SINGLE ALWAYS-ON PATH**: launchd → `discovery_watchdog.py` → `.fixed_autonomous_discovery.py`. Legacy V73 loops are retired stubs — never revive them.
- **CODE INTEGRITY** (full audit 2026-07-17): `import biodisc_core` works. Live pipeline (fixed_pipeline + evolution) is syntactically clean; 731 files scanned, the 34 truncated legacy files are an exact match to `BROKEN_FILES_BASELINE.md` (zero regressions). The single write chokepoint is now **structurally** airtight — 4 dormant legacy bypass writes (`biodisc_v5_6_*`, `biodisc_v6_0_*`, `v73_*`) were neutralized to `raise RuntimeError`. The `domains/__init__.py` astrophysics-import cascade (which drove the "Domain system not available" warnings) is fixed. Tests: 215/215 pass. Legacy truncations remain baselined, not guess-repaired.
- **DISCOVERY SELECTION → EUREKA-STEERING REBUILD** (V8.0.17–30): the selector historically optimized for *realness* (replicability), which is anti-correlated with novelty — it surfaced textbook biology by construction. The rebuild holds realness as a floor and steers at *surprise*, end-to-end: **selection** — value-of-compute gate funds DE only for high-EV questions (novelty × importance × surprise / cost) + 15% exploration slice (V8.0.21); contrarian/anti-textbook questions (V8.0.22); **analysis** — a **gene-specific hypothesis primitive** tests the *named* gene's direction (not a top-N list), so a contrarian bet can deliver a real surprise (V8.0.27); a **Layer-7 binding gate** rejects findings whose named gene isn't in the result, and **Layer-7b** rejects a *failed* contrarian (textbook held) (V8.0.26); **cross-dataset direction primitive** finds flip *bridges* (V8.0.28); **Gate-2 checks the specific directional RESULT claim** against PubMed (V8.0.29); **measure** — `contrarian_success_rate` (supported-and-novel) is the trend to watch, in the capability index (V8.0.30). Plus: cross-dataset synthesis + sandbox (V8.0.23/.24), pool 6→13 (V8.0.20/.25), dedup/pre-filter/synonyms (V8.0.17–19), organism-conflict exclusion (V8.0.26). **Keystone proven end-to-end (V8.0.31–37):** a live contrarian reached `supports=True` (MTOR confirmed to decrease vs the textbook), literature-novel + replicated — blocked only by dedup on an exhausted contrast; fixes along the way: force-include the named gene (V8.0.33), an orientation bug in the gene-specific test that had kept it from ever running (V8.0.34), binding deferring to 7b when the gene was measured (V8.0.35), numpy-safe verdict logging so the metric tracks (V8.0.36), and contrarians now preferentially steered at *fresh* (least-mined) datasets so they clear dedup (V8.0.37).
- **ANOMALY-FIRST DISCOVERY (V8.0.38)** — the keystone architectural shift. The contrarian channel *guesses* a surprise and mostly misses (textbook usually holds). The **anomaly miner** (`anomaly_miner.py`) inverts this: it scans each DE result for **observed** surprises — a gene whose direction *flips vs its prior discoveries*, or an extreme effect (|log2FC|≥1.5) — and makes that observed surprise the discovery's **primary claim** (`observed_surprise` leads `_build_claim_text`; Gate-2 scores the observed anomaly's novelty). The surprise is real by construction; the contrarian question is demoted to a secondary entry point. Calibrated to the real effect distribution (median |log2FC|≈0.04). Surfaces 30 candidates on the current store; yield scales with data that has cross-context overlap / large effects.
- **NEVER push to ASTRA-dev** — use BIODISC repository only.
- **Naming**: Always use "BIODISC" (not "STAN" or "STAN-XI-ASTRO").
- **Use factory functions** — never direct constructors.
- **Initialize persistent memory** at session start.

## Modular Documentation

| File | Content |
|---|---|
| `docs/12_version_history.md` | Full V5.0→V8.0.15 changelog (moved from CLAUDE.md) |
| `docs/peer_review_fixes_implementation.md` | V7.3 validation fixes detail |
| `docs/10_genuine_discovery_system.md` | V5.0 genuine discovery system |
| `docs/02_autonomous_system.md` | Auto-start, watchdog, session recovery |
| `BROKEN_FILES_BASELINE.md` | Code integrity audit (34 truncated legacy files) |

---

**For detailed information, see the modular documentation files in `docs/`**
