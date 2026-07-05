# BIODISC Quick Start Guide - V5.0 GENUINE DISCOVERY

## 🧬 What is BIODISC?

**BIODISC** (Biology Discovery and Intelligence System) is a **Version 5.0** **GENUINE** autonomous scientific discovery system that:

- ✅ **Mines literature** via PubMed/NCBI for novelty validation
- ✅ **Analyzes real data** from GEO datasets (not simulated)
- ✅ **Validates statistically** with proper methodology
- ✅ **Recovers automatically** from context exhaustion
- ✅ **Persists session state** for continuous operation

### 🎯 The "GENUINE" Difference

**❌ V1.0-V4.0** (Simulated):
- Fake statistics (r=0.87, p<0.001) with no real data
- No literature validation
- "Discoveries" were often known biology or fabricated claims

**✅ V5.0** (Genuine):
- Real GEO datasets from NCBI
- PubMed literature search for novelty
- Proper statistical methodology
- Only genuinely novel findings stored

## 🚀 Quick Start - GENUINE Discovery (V5.0 OPERATIONAL)

### 1. Install Requirements

```bash
cd /Users/gjw255/astrodata/SWARM/BIODISC

# Install scientific packages (if not already installed)
pip install biopython requests numpy pandas scipy scikit-learn

# Configure NCBI (recommended)
export ENTREZ_EMAIL="your-email@example.com"
```

### 2. Start Genuine Discovery

```bash
# System auto-starts when entering BIODISC directory
cd /Users/gjw255/astrodata/SWARM/BIODISC

# Or start manually
python .genuine_autonomous_discovery.py
```

**V5.0 Status**: ✅ **FULLY OPERATIONAL** (July 1, 2026)
- BioPython installed and working
- PubMed/NCBI integration operational
- Literature validation functional
- Database connectors ready

### 3. Monitor Progress

```bash
# Check logs
tail -f logs/genuine_discovery.log

# Check session state
cat session_state.json

# View discoveries
cat autonomous_discoveries.jsonl
```

## 🔄 Session Persistence

**Automatic Recovery**: The system automatically recovers from context exhaustion via:
- `session_state.json` - Stores system state between sessions
- Auto-save every discovery cycle
- Auto-load on restart
- Discovery continues from where it left off

**Manual Recovery**: See `docs/11_session_recovery.md`

## 📚 Documentation Structure

```bash
# Check current remotes
git remote -v

# Should show:
# biodisc  https://github.com/Tilanthi/BIODISC.git (fetch)
# biodisc  https://github.com/Tilanthi/BIODISC.git (push)

# Push BIODISC changes to correct repository
git add .
git commit -m "Your commit message"
git push biodisc main

# NEVER use 'origin' for BIODISC changes
```

## Basic System Usage

### Create System with Auto-Start

```python
from biodisc_core import create_biodisc_system

# Create system with auto-optimized capabilities
# Autonomous discovery starts automatically in V5.0+ with V74 filter and V75-V80 self-evolution
system = create_biodisc_system()

# Answer queries with automatic capability selection
result = system.answer("What causes protein misfolding?")
print(result['answer'])

# Autonomous discovery pauses automatically during queries
# and resumes when idle
```

### V4.0 Revolutionary Capabilities

```python
from biodisc_core.v4_revolutionary import create_biodisc_v4_system, IntegrationMode

# Create V4.0 system with MCE, ASC, CRN, MMOL capabilities
system = create_biodisc_v4_system()

# Process with different integration modes
result = system.process_query("biological query", mode=IntegrationMode.FULL)
```

### Individual Capability Usage

```python
# Meta-Context Engine
from biodisc_core.metacognitive.meta_context_engine import create_meta_context_engine
mce = create_meta_context_engine()
result = mce.layer_context(query, dimensions=["temporal", "perceptual"])

# Domain modules
from biodisc_core.domains import DomainRegistry
registry = DomainRegistry()
registry.load_all_domains()
result = registry.process_query("gene expression analysis")

# Physics engine
from biodisc_core.physics import UnifiedPhysicsEngine
physics = UnifiedPhysicsEngine()
result = physics.compute("blackbody", {"temperature": 5778, "wavelength": 500e-7})

# MAML optimizer
from biodisc_core.reasoning.maml_optimizer import create_maml_optimizer
optimizer = create_maml_optimizer(model_fn, loss_fn, n_inner_steps=5)

# Autonomous discovery orchestrator (manual control if needed)
from biodisc_core.autonomous.autonomous_orchestrator import AutonomousOrchestrator
from biodisc_core.autonomous.config import get_default_config

orchestrator = AutonomousOrchestrator(get_default_config())
orchestrator.start_autonomous_loop()
```

## System Statistics

- **Total Lines**: 307,000+
- **Python Files**: 518+
- **Directory Size**: ~9 MB (after cleanup from 3.6 GB of backups)
- **Specialist Capabilities**: 66+ (V36-V94 baseline)
- **V5.0 Revolutionary Capabilities**: 20 (V61-V80, including V75-V80 Self-Evolution)
- **Domain Modules**: 10 (biology-focused)
- **Physics Stages**: 15 learning stages (relativistic, quantum, nuclear)
- **Self-Evolution Infrastructure**: V75-V80 operational (2,300+ lines)
- **Current Agency**: 45% → Target: 70% (Year 1) → 95%+ (5 years)
- **Autonomous Discoveries**: Filtered for genuine contributions only (V74)

## Additional Resources

### Memory Palace Location
Autonomous discoveries are stored at:
`~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/`

### Persistent Memory Location
Session persistence and hallucination register at:
`~/.biodisc_persistent/`

### Configuration Files
- Autonomous system config: `biodisc_core/autonomous/config.py`
- Domain registry: `biodisc_core/domains/registry.py`
- Memory configuration: `biodisc_core/memory/persistent.py`
