# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: V8.0.19 — VERIFICATION-FIRST (code-integrity audit + discovery-selection sharpening)
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
- **DISCOVERY SELECTION** (sharpened 2026-07-17, V8.0.17–19): near-duplicate dedup now seeds from the genuine store at init, so the same-dataset gene-overlap check (V8.0.13) actually fires. A pre-DE question-validity filter drops questions with no matching verified dataset — cutting the #1 `no_datasets` funnel bucket (~40% of questions had no dataset home). `OntologyMapper` learned anatomical synonyms (hepatic→liver, cardiac→heart, pulmonary→lung, …) so adjective-form questions pin their dataset instead of false-negative-rejecting. Structural ceiling remains the 6-dataset verified pool; expanding it is the long-term throughput lever.
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
