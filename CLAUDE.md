# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Modular Documentation Structure

**BIODISC documentation is organized into modular files for faster loading and easier maintenance:**

### Core Documentation
- **Quick Start**: `docs/01_quick_start.md` - Project overview, GitHub workflow, basic usage
- **Autonomous System**: `docs/02_autonomous_system.md` - V73-V80 auto-start, self-evolution
- **Capabilities**: `docs/03_capabilities.md` - V61-V80 detailed capabilities
- **Architecture**: `docs/04_architecture.md` - System layers, design patterns, communication
- **Testing**: `docs/05_testing.md` - Test procedures, verification
- **Development**: `docs/06_development.md` - Workflow, file organization, pitfalls
- **Memory System**: `docs/07_memory_system.md` - Persistent memory, hallucination register
- **Physics Constants**: `docs/08_physics_constants.md` - Physics constants and reference values
- **PDF Generation**: `docs/09_pdf_generation.md` - PDF generation requirements
- **Genuine Discovery**: `docs/10_genuine_discovery_system.md` - V5.0 genuine discovery system
- **Session Recovery**: `docs/11_session_recovery.md` - Session persistence and restart
- **Validation System**: `docs/validation_system_architecture.md` - 5-layer validation architecture
- **Peer Review Fixes**: `docs/peer_review_fixes_implementation.md` - V7.3 critical fixes

### Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: 8.0 - VERIFICATION-FIRST (✅ CHOKEPOINT + REAL GATE-2 + REPLICATION)
**AGI Capability**: 90-95%
**GitHub**: https://github.com/Tilanthi/BIODISC (ONLY repository for BIODISC)
**Remote**: `biodisc` (use `git push biodisc main` - ONLY main branch)

### Version Summary

**V8.0 - VERIFICATION-FIRST** (July 14, 2026):
- **Write chokepoint**: exactly ONE function (`discovery_store.append_verified`)
  may write a discovery, and it REQUIRES a machine `verification` block with
  objective real-data evidence. Fiction/hallucinated records are structurally
  impossible to store (ASTRA lesson #1).
- **Two stores**: `autonomous_discoveries.jsonl` = genuine (replicated) findings
  only; `autonomous_discoveries_candidates.jsonl` = machine-verified but
  unreplicated candidates (quarantined, never asserted as knowledge).
- **Real Gate-2** (`literature_gate.py`): PubMed abstract TF-similarity
  novelty check replaces the keyword heuristic; `known` claims are rejected,
  transient `retrieval_failed` is non-blocking and never cached.
- **Held-out replication anchor** (`replication_gate.py`): `is_genuine` requires
  the headline statistic to replicate on a held-out sample split.
- **Funnel instrumentation** (`verdict_log.py`): one structured verdict per
  candidate; `print_funnel()` shows where candidates die.
- **Single always-on path**: launchd → `discovery_watchdog.py` →
  `.fixed_autonomous_discovery.py`. Legacy V73 loops retired.
- **Evolution ON** (supervised, `evolution_integration.py`): AlphaEvolve-style
  method-evolution against benchmark ground truth; outputs are methods, not
  discoveries (separate provenance log). Real-cohort evaluator hook is the next step.
- **Question/dataset diversity** (2026-07-15): `specific_questions.py` now serves a
  diverse + dataset-aligned, shuffled question pool (`generate_question_pool`);
  `_search_real_geo_datasets` rotates the pool per cycle. This fixed a ~90%
  duplicate-statistical-profile rejection rate caused by re-running one question
  on one dataset. **Throughput is still capped by the 3-dataset verified pool**
  (GSE2034 / GSE13159 / GSE15822) — expanding it is the real next lever; the
  verdict funnel quantifies the rest.
- **Stability fixes** (2026-07-15, V8.0.2): (1) `geo_data_downloader` streamed
  matrix downloads are now hard-bounded by total wall-clock (10 min) + size
  (600 MB) via `_read_stream_bounded` — a stalled mid-stream read can no longer
  hang the loop for hours (the recurring stall). (2) Watchdog stall threshold
  lowered 6 h → 30 min (SIGTERM→SIGKILL escalation already present) so any
  residual hang is recovered promptly. (3) Organism normalization: the dataset-
  question validator now compares on canonical NCBITaxon IDs, so `mouse` matches
  `mus musculus` (was a false mismatch that rejected the entire GSE15822 mouse
  dataset). Same for tissue synonyms (`breast`↔`mammary`).
- Full test suite green (184 tests). See `docs/peer_review_fixes_implementation.md`.

**V7.3 - PEER REVIEW FIXES** (July 10, 2026):
- 5-layer validation system to prevent pseudo-science
- Duplicate detection, dataset-question validation, probe-gene mapping
- FDR significance gates, template pattern detection
- **See**: `docs/peer_review_fixes_implementation.md`

**V7.2 - AUTO-RESTART & CONTROL PROBE FIXES** (July 10, 2026):
- Control probe filtering expanded (15+ patterns)
- Auto-restart system with watchdog monitoring
- Sleep/wake detection and crash recovery
- **See**: `docs/02_autonomous_system.md`

**V7.1 - MULTI-REPOSITORY EXPANSION** (July 7, 2026):
- Expanded from GEO-only to 13+ biological data repositories
- ~100+ million datasets (10-20x increase from GEO-only)
- Proteomics, metabolomics, epigenomics, clinical data, networks
- **See**: `docs/10_genuine_discovery_system.md`

**V7.0 - SCIENTIFIC INTEGRITY FIXES** (July 7, 2026):
- Gene symbol validation as HARD GATE
- Dataset verification with REAL accession numbers
- Real GEO data download implemented
- Fixed pipeline replacement (no more pseudo-science)
- **See**: `docs/10_genuine_discovery_system.md`

**V6.0 - CLOSED-LOOP DISCOVERY ARCHITECTURE** (July 4, 2026):
- 8 major architectural enhancements based on cutting-edge AI research
- Graded autonomy, epistemic collapse prevention
- Hybrid discovery engine with multi-paradigm reasoning
- **See**: `docs/04_architecture.md`

**V5.0 - GENUINE DISCOVERY SYSTEM** (July 1, 2026):
- Real literature validation via PubMed/NCBI
- Genuine database access (GEO, STRING, KEGG)
- Statistical validation with proper methodology
- **See**: `docs/10_genuine_discovery_system.md`

### CRITICAL: GitHub Push Rules

**🎯 MANDATORY: BIODISC changes ONLY push to main branch of https://github.com/Tilanthi/BIODISC**

**When I ask you to "push updates" or "push changes" from BIODISC:**
- ✅ **ALWAYS** push to: `https://github.com/Tilanthi/BIODISC` (repository)
- ✅ **ALWAYS** push to: `main` branch (ONLY main branch - never other branches)
- ❌ **NEVER** push to: ASTRA-dev repository (completely separate project)
- ❌ **NEVER** push to: origin remote (use `biodisc` remote instead)

**Correct Git Workflow:**
```bash
# Add changes
git add .

# Commit changes
git commit -m "🧬 BIODISC: descriptive message"

# Push to CORRECT repository and branch
git push biodisc main  # ✅ CORRECT
```

### Most Common Tasks

**Start Autonomous Discovery** (V7.3 with 5-layer validation):
```bash
# The watchdog auto-starts when entering BIODISC directory
# Check if running:
ps aux | grep "discovery_watchdog.py" | grep -v grep
ps aux | grep "fixed_autonomous_discovery.py" | grep -v grep

# Check status
tail -50 logs/autonomous_discovery_fixed.log
tail -20 logs/discovery_watchdog.log

# Manual restart if needed
python discovery_watchdog.py &
```

**Check Discovery Status:**
```bash
# GENUINE (replicated) findings — the verified store (written via the chokepoint)
tail -5 autonomous_discoveries.jsonl
wc -l autonomous_discoveries.jsonl

# CANDIDATE quarantine — machine-verified but NOT yet replicated (single cohort)
tail -5 autonomous_discoveries_candidates.jsonl
wc -l autonomous_discoveries_candidates.jsonl

# Discovery funnel — WHERE candidates die (gate1 / gate2-known / retrieval / duplicate)
tail -5 discovery_verdicts.jsonl
python -c "from biodisc_core.fixed_pipeline.verdict_log import print_funnel; print_funnel()"

# Check validation statistics
tail -100 logs/fixed_discovery.log | grep "VALIDATION"
```

**Use BIODISC System Interactively:**
```python
from biodisc_core import create_biodisc_system
system = create_biodisc_system()
result = system.answer("What causes protein misfolding?")
```

**Initialize Memory (REQUIRED at session start):**
```python
from biodisc_core.memory.persistent import create_integrator
integrator = create_integrator()
integrator.initialize_session()
```

**Check Literature Mining Results:**
```python
from biodisc_core.analysis.literature_mining_integration import create_genuine_discovery_orchestrator
orchestrator = create_genuine_discovery_orchestrator()
# Validates discoveries against PubMed literature
```

**Run Tests:**
```bash
python biodisc_core/comprehensive_system_test.py
```

### Key Points

1. **Naming**: Always use "BIODISC" (not "STAN" or "STAN-XI-ASTRO")
2. **GitHub**: Push to `biodisc` remote, not `origin`
3. **VERIFICATION-FIRST (V8.0)**: One write chokepoint (`discovery_store.append_verified`)
   requires a machine verification block — fiction is structurally impossible to store
4. **Real Data Analysis**: Uses actual GEO datasets, not simulated data
5. **Scientific Integrity**: 6-layer validation (incl. real PubMed Gate-2) + held-out
   replication anchor; `is_genuine` requires replication, single-cohort findings are quarantined
6. **Session Persistence**: Automatic restart capability via session_state.json
7. **Memory**: Always initialize persistent memory at session start
8. **NO SLATE REFERENCES**: BIODISC is a separate biological discovery system
9. **SINGLE ALWAYS-ON PATH**: launchd → `discovery_watchdog.py` → `.fixed_autonomous_discovery.py`
   (legacy V73 loops are retired stubs — never revive them)
10. **Auto-Restart**: System automatically recovers from sleep, crashes, or idle periods

### System Status

- **Code**: 307,000+ lines, 518+ Python files
- **Capabilities**: 66+ specialist (V36-V94) + 20 revolutionary (V61-V80)
- **Current System**: V7.3 - PEER REVIEW FIXES with 5-layer validation
- **Domains**: 10 biology-focused domain modules
- **Agency**: 45% → 70% (Year 1) → 95%+ (5 years)
- **Self-Evolution**: V75-V80 operational (first AI with systematic self-evolution)

### Critical Reminders

- **NEVER push to ASTRA-dev repository** - use BIODISC repository only
- **ALWAYS initialize persistent memory** at session start
- **🚨 ALWAYS RUNNING REQUIREMENT**: Discovery pipeline must ALWAYS be running with automatic startup and restart
- **🔧 AUTO-RESTART ENABLED**: System automatically restarts after sleep/wake cycles, crashes, or idle periods
- **Use factory functions** - never direct constructors
- **Verify claims** against hallucination register
- **WRITE CHOKEPOINT (V8.0)**: Every discovery is written through `discovery_store.append_verified`, which requires a machine verification block. Never add a second write path. Genuine (replicated) → `autonomous_discoveries.jsonl`; candidates → `autonomous_discoveries_candidates.jsonl`
- **6-LAYER VALIDATION + GATE-2 + REPLICATION**: duplicate / dataset-question / probe-gene / FDR-significance / template / **PubMed literature-novelty (Gate-2)**, plus a held-out **replication** anchor for `is_genuine`

---

**For detailed information, see the modular documentation files in `docs/`**
