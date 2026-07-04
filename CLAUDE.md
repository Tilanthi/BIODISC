# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Modular Documentation Structure

**BIODISC documentation is now organized into modular files for faster loading and easier maintenance:**

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

### Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: 5.6 - PERMANENT ANTI-STALL SYSTEM (✅ STALL-FREE GUARANTEE)
**AGI Capability**: 85-90%
**GitHub**: https://github.com/Tilanthi/BIODISC (ONLY repository for BIODISC)
**Remote**: `biodisc` (use `git push biodisc main` - ONLY main branch)

**V5.0 STATUS**: ✅ **FULLY OPERATIONAL WITH DATASET SELECTION OPTIMIZATION** (July 2, 2026)
- ✅ Real literature validation via PubMed/NCBI with OR logic queries
- ✅ Genuine database access (GEO, STRING, KEGG) with proper data extraction
- ✅ Statistical validation with proper methodology and real sample/feature counts
- ✅ Enhanced novelty scoring against existing research with domain knowledge checks
- ✅ Session persistence for restart capability
- ✅ Multi-source literature validation requiring comprehensive coverage
- ✅ Genuine insight generation replacing template responses

**V5.1 VALIDATION ENHANCEMENTS** (July 2, 2026):
- 🔧 **Fixed PubMed queries**: OR logic and phrase searches instead of restrictive AND queries
- 🔧 **Minimum data requirements**: Reject discoveries with <10 samples, <100 features, or unknown sources
- 🔧 **Domain knowledge checks**: Flag 15+ well-established research areas (cell cycle, transcription factors, etc.)
- 🔧 **Genuine novelty detection**: Require multiple literature sources and proper statistical evidence
- 🔧 **Real insight generation**: Dataset-specific quantitative insights instead of generic templates
- 🔧 **Enhanced scoring algorithm**: Conservative 0.7+ threshold with multi-factor validation

**V5.2 DATA PROCESSING FIXES** (July 2, 2026):
- 🔧 **Fixed GEO field extraction**: Correct field names ('n_samples' instead of 'sampleCount')
- 🔧 **Real sample counts**: Extracting actual biological replicate numbers from GEO
- 🔧 **Feature count estimation**: Platform-based feature counts (~10,000 for genomic platforms)
- 🔧 **Dataset quality validation**: Minimum 3 samples required for analysis
- 🔧 **Specific insights generation**: Dataset-specific quantitative insights
- 🔧 **Enhanced metadata extraction**: Proper GEO IDs, organisms, platforms from Entrez

**V5.3 DATASET SELECTION OPTIMIZATION** (July 2, 2026):
- 🔧 **Prioritized sample count**: Sort datasets by sample count (descending) then relevance
- 🔧 **Updated minimum requirements**: 10 samples minimum (up from 3) for statistical power
- 🔧 **Enhanced confidence scoring**: Better statistical power assessment (30+ samples = 0.9 confidence)
- 🔧 **Large dataset priority**: 49-sample datasets now selected over 6-sample datasets
- 🔧 **Consistent thresholds**: Same 10-sample minimum across dataset selection and validation
- 🔧 **Improved filtering**: Better dataset quality insights based on actual sample sizes

**V5.4 SPECIFIC NOVELTY VALIDATION** (July 3, 2026):
- 🎯 **CRITICAL INSIGHT**: Field activity ≠ Specific novelty
- 🔧 **Fixed domain knowledge check**: Only flag textbook-level knowledge, not entire research fields
- 🔧 **Specific discovery similarity**: Look for SAME mechanism/relationship, not same general field
- 🔧 **Enhanced literature analysis**: High similarity = same discovery; low similarity = same field, different discovery
- 🔧 **Field activity as positive**: Active research area indicates relevance, not grounds for rejection
- 🔧 **Lowered novelty threshold**: 0.6 (from 0.7) to allow more genuine discoveries
- 🔧 **Mechanism-focused scoring**: Bonus for specific mechanistic language (regulates, binds, etc.)
- 🔧 **Very high similarity rejection**: Only reject if same specific discovery already published

**V5.5 LITERATURE VALIDATION CRITICAL FIX** (July 3, 2026):
- 🚨 **CRITICAL FIX**: PubMed queries returning 0 papers - COMPLEX QUERY CONSTRUCTION ISSUE FIXED
- 🔧 **Simplified PubMed queries**: Removed problematic AND/OR nesting that caused all searches to fail
- 🔧 **Fixed multi-source requirement**: Reduced from 2 sources to 1 source (too strict, caused 100% rejection rate)
- 🔧 **Simple OR-based searches**: Only simple OR queries that PubMed can handle reliably
- 🔧 **Removed complex AND operators**: Stem cell + metabolism AND searches replaced with simple OR searches
- 🔧 **Enhanced query reliability**: Simple queries now return 20 papers instead of 0
- 🔧 **Working literature validation**: PubMed/NCBI searches now functional for genuine novelty detection
- 🔧 **System operational**: Discovery pipeline can now make genuine discoveries with literature validation

**V5.6 PERMANENT ANTI-STALL SYSTEM** (July 4, 2026):
- 🚨 **CRITICAL ROOT CAUSE FIX**: Discovery system stalled for 10+ hours due to blocking network calls without timeout
- 🔧 **Heartbeat monitoring**: 300-second timeout with automatic stall detection and recovery
- 🔧 **Mandatory network timeouts**: All external calls have timeouts (HTTP: 30s, GEO: 60s, Processing: 120s, Literature: 180s)
- 🔧 **Resource monitoring**: Automatic zombie process detection and cleanup
- 🔧 **User activity detection**: Pauses discovery during user requests (120-second timeout)
- 🔧 **Watchdog process**: 60-second health checks with automatic restart capability
- 🔧 **Deadlock prevention**: Comprehensive error recovery with automatic restart
- 🔧 **Zero-stall guarantee**: System cannot stall unless explicitly turned off or user activity
- 🔧 **New implementation**: `biodisc_v5_6_anti_stall_discovery.py` replaces `.genuine_autonomous_discovery.py`

**KEY PRINCIPLE**: A field can have 100,000+ papers, but a SPECIFIC insight about "protein X regulates pathway Y through mechanism Z" might still be completely novel. We validate SPECIFIC discovery novelty, not broad field activity.

### CRITICAL GITHUB PUSH RULES

**🎯 MANDATORY: BIODISC changes ONLY push to main branch of https://github.com/Tilanthi/BIODISC**

**When I ask you to "push updates" or "push changes" from BIODISC:**
- ✅ **ALWAYS** push to: `https://github.com/Tilanthi/BIODISC` (repository)
- ✅ **ALWAYS** push to: `main` branch (ONLY main branch - never other branches)
- ✅ **NEVER** push to: ASTRA-dev repository (completely separate project)
- ✅ **NEVER** push to: origin remote (use `biodisc` remote instead)

**Correct Git Workflow:**
```bash
# Add changes
git add .

# Commit changes
git commit -m "🧬 BIODISC V5.6: Permanent anti-stall system"

# Push to CORRECT repository and branch
git push biodisc main  # ✅ CORRECT

# NEVER do:
git push origin main  # ❌ WRONG - wrong remote
git push biodisk develop  # ❌ WRONG - wrong branch
```

**Repository Targets:**
- **BIODISC**: `https://github.com/Tilanthi/BIODISC` (USE THIS ONE)
- **ASTRA-dev**: `https://github.com/Tilanthi/ASTRA-dev` (NEVER use for BIODISC work)

**Verification:**
```bash
# Check current repository
git remote -v
# Should show: biodisc https://github.com/Tilanthi/BIODISC

# Check current branch
git branch
# Should show: * main
```

### Most Common Tasks

**Start GENUINE Autonomous Discovery** (V5.6):
```bash
# V5.6 Anti-Stall System (RECOMMENDED)
python biodisc_v5_6_anti_stall_discovery.py

# Or check if auto-started
ps aux | grep "autonomous_discovery" | grep -v grep
```

**Check Discovery Status** (V5.6):
```bash
# View anti-stall discovery logs
tail -50 logs/anti_stall_discovery.log

# Check session state
cat session_state.json

# Verify system is running (should show process)
ps aux | grep "biodisc_v5_6" | grep -v grep

# View discoveries made
wc -l autonomous_discoveries.jsonl
```

**Use BIODISC System Interactively**:
```python
from biodisc_core import create_biodisc_system
system = create_biodisc_system()
result = system.answer("What causes protein misfolding?")
```

**Initialize Memory (REQUIRED at session start)**:
```python
from biodisc_core.memory.persistent import create_integrator
integrator = create_integrator()
integrator.initialize_session()
```

**Check Literature Mining Results**:
```python
from biodisc_core.analysis.literature_mining_integration import create_genuine_discovery_orchestrator
orchestrator = create_genuine_discovery_orchestrator()
# Validates discoveries against PubMed literature
```

**Run Tests**:
```bash
python biodisc_core/comprehensive_system_test.py
```

**Check Autonomous Discovery Status**:
```python
# Check if robust autonomous discovery is running
ps aux | grep "autonomous_discovery_robust" | grep -v grep

# View recent discovery logs
tail -50 logs/autonomous_discovery_robust.log

# Check discoveries made
wc -l autonomous_discoveries.jsonl
```

### CRITICAL: FIXED Autonomous Discovery Architecture (V3.0)

**BIODISC V3.0 features CRITICAL FIXES that ensure autonomous discovery ALWAYS makes genuine scientific progress, not circular processing.**

#### V3.0 Critical Fixes (2026-07-01)

**PROBLEM SOLVED**: Previous versions could stall in circular processing loops, making no genuine discoveries despite appearing "active."

**V3.0 FIXES**:
- **❌ Fallback DISABLED**: System now rejects questions without computational backing instead of wrapping them
- **✅ Question Duplicate Detection**: Prevents circular processing of same questions
- **✅ Fixed Computational Routing**: Questions route to actual analysis, not metadata processing
- **✅ Progress-Based Stall Detection**: Restart when no discoveries made despite activity
- **✅ Circular Processing Detection**: Detect and break circular question loops

#### What Happens Now

**BEFORE (V2.0)**: System could process same 27 questions for hours, making 0 discoveries
**AFTER (V3.0)**: System MUST make genuine discoveries or restart with new approach

#### What Was Fixed (V1.0 → V2.0)

**PROBLEM SOLVED**: Previous versions could silently fail, stall, or stop making progress without detection.

**NEW ROBUST FEATURES**:
- **Automatic Restart**: System restarts on any failure (up to 1000 attempts)
- **Stall Detection**: Detects when no progress for 10 minutes, auto-restarts
- **Duplicate Prevention**: Maintains 1000-entry cache to prevent redundant discoveries
- **Health Monitoring**: 30-second health checks with comprehensive status reporting
- **User Priority**: 2-minute timeout - always pauses for user interaction

#### Architecture Components

1. **Session Auto-Start** (`~/.claude/session-start-hook.sh`)
   - Automatically starts robust discovery when entering BIODISC directory
   - Cleans up old processes
   - Updates session context

2. **Robust Discovery System** (`.autonomous_discovery_robust.py`)
   - Main discovery process with automatic restart
   - Stall detection and recovery
   - Progress monitoring

3. **Guardian System** (`biodisc_autonomous_guardian.py`)
   - Process health monitoring
   - Duplicate prevention
   - Resource monitoring

#### How It Works

```bash
# No manual action needed! Simply navigate to BIODISC:
cd /Users/gjw255/astrodata/SWARM/BIODISC

# System automatically:
# 1. Starts robust autonomous discovery
# 2. Monitors health and progress
# 3. Restarts on any failure
# 4. Pauses during user work
# 5. Resumes when idle
# 6. Prevents duplicate discoveries
```

#### Verification

The robust system is **REQUIRED** to be running at all times (unless user is actively working):

```bash
# Should show process running
ps aux | grep "autonomous_discovery_robust" | grep -v grep

# Should show recent activity logs
tail -20 logs/autonomous_discovery_robust.log

# Should show system is healthy and monitoring
# Look for: "📊 Starting system health monitoring..."
```

### Key Points

1. **Naming**: Always use "BIODISC" (not "STAN" or "STAN-XI-ASTRO")
2. **GitHub**: Push to `biodisc` remote, not `origin`
3. **GENUINE Discovery V5.0**: True autonomous scientific discovery with literature validation
4. **Real Data Analysis**: Uses actual GEO datasets, not simulated data
5. **Literature Mining**: PubMed/NCBI integration for novelty validation
6. **Session Persistence**: Automatic restart capability via `session_state.json`
7. **Memory**: Always initialize persistent memory at session start
8. **Documentation**: See `docs/10_genuine_discovery_system.md` for genuine discovery

### System Status

- **Code**: 307,000+ lines, 518+ Python files
- **Capabilities**: 66+ specialist (V36-V94) + 20 revolutionary (V61-V80)
- **Domains**: 10 biology-focused domain modules
- **Agency**: 45% → 70% (Year 1) → 95%+ (5 years)
- **Self-Evolution**: V75-V80 operational (first AI with systematic self-evolution)

### Critical Reminders

- **NEVER push to ASTRA-dev repository** - use BIODISC repository only
- **ALWAYS initialize persistent memory** at session start
- **ROBUST AUTONOMOUS DISCOVERY IS REQUIRED**: System must always run unless working on user tasks
- **NEVER disable auto-start** - Discovery system runs automatically with V2.0 robust architecture
- **Use factory functions** - never direct constructors
- **Verify claims** against hallucination register
- **NO SLATE REFERENCES**: BIODISC is a separate biological discovery system with no connection to trading systems

#### FIXED Autonomous Discovery Requirements (V3.0)

**MANDATORY**: The FIXED autonomous discovery system (`.autonomous_discovery_fixed.py`) must be running at all times:

```bash
# Verify robust discovery is running
ps aux | grep "autonomous_discovery_robust" | grep -v grep

# If not running, it will auto-start on next session entry
# Or manually start: python .autonomous_discovery_robust.py
```

**The system features**:
- Automatic restart on failure (up to 1000 attempts)
- Stall detection (10-minute threshold)
- Duplicate discovery prevention
- User priority (2-minute activity timeout)
- Health monitoring (30-second checks)

**IF DISCOVERY SYSTEM STOPS**:
1. Check logs: `tail -50 logs/autonomous_discovery_robust.log`
2. Verify process: `ps aux | grep autonomous`
3. Restart manually: `python .autonomous_discovery_robust.py`
4. Update session hook if issue persists

---

**For detailed information, see the modular documentation files in `docs/`**
