# BIODISC Quick Start Guide

## Project Overview

**BIODISC** (Biology Discovery and Intelligence System) is a unified AGI-inspired framework for autonomous hypothesis generation and validation in biology with revolutionary self-evolution capabilities. The system integrates ~305,000 lines of clean, functional code across modular cognitive capabilities.

**Version**: 5.0
**AGI Capability Estimate**: 85-90%

### Naming Convention

The system was previously known as "STAN-XI-ASTRO" or "STAN". **It must now be referred to exclusively as "BIODISC"** in all:
- Academic papers and documentation
- External communications
- User-facing text
- Paper titles and abstracts

The internal codebase uses `biodisc_core` for consistency with the BIODISC project name. Function names like `create_biodisc_system()` are the primary interface.

**Full name**: BIODISC: Biology Discovery and Intelligence System
**Subtitle**: An AGI-inspired framework for autonomous hypothesis generation and validation in biology

## GitHub Repository Target

**IMPORTANT**: When pushing to GitHub from this BIODISC repository, ALWAYS use:
- **Repository**: https://github.com/Tilanthi/BIODISC
- **Remote**: `biodisc` (not `origin`)
- **Command**: `git push biodisc main`

**NEVER push BIODISC changes to the ASTRA-dev repository** - that is for a different project.

### Correct Git Workflow for BIODISC

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
