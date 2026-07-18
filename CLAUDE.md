# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: V8.0.25 — VERIFICATION-FIRST (code-integrity audit + Eureka-steering rebuild)
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
- **DISCOVERY SELECTION → EUREKA-STEERING REBUILD** (V8.0.17–25): the selector historically optimized for *realness* (replicability), which is anti-correlated with novelty — it surfaced textbook biology by construction. The rebuild holds realness as a floor and steers compute at *surprise*: (1) a **value-of-compute gate** funds DE only for high-EV questions (novelty × importance × surprise / cost) plus a 15% exploration slice, so the loop stops re-deriving known biology (V8.0.21); (2) **contrarian/anti-textbook questions** are generated to score high on surprise (V8.0.22); (3) **cross-dataset module synthesis** finds direction-flip *bridges* between datasets — the paradigm-relevant pattern invisible to single-dataset DE (V8.0.23); (4) the **verified pool expanded 6→13** toward under-studied contexts (prostate, colorectal, kidney, ovary, liver-disease spectrum) via the `dataset_preflight` onboarding path (V8.0.20/.25); (5) LLM-written analysis code runs only through an **opt-in 3-layer sandbox**, OFF by default (V8.0.24). Earlier plumbing: near-dup dedup seeded from the store (V8.0.17), `no_datasets` pre-filter (V8.0.18), `OntologyMapper` synonyms (V8.0.19).
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
