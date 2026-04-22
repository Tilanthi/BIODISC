# Migration Guide: ASTRA → BIODISC

This guide helps users migrating from ASTRA (astrophysics) to BIODISC (biology).

## Overview

BIODISC (Biology Discovery and Intelligence System) is a transformation of ASTRA (Autonomous Scientific Discovery in Astrophysics) from astronomy-focused AGI to biology-focused AGI.

## API Changes

### Factory Functions

```python
# OLD (ASTRA)
from astra_core import create_stan_system
system = create_stan_system()

# NEW (BIODISC)
from biodisc_core import create_biodisc_system
system = create_biodisc_system()

# Backward compatibility (deprecated)
from biodisc_core import create_stan_system  # Still works, but deprecated
```

### Import Statements

```python
# OLD
from astra_core.domains import DomainRegistry
from astra_core.memory import MORKOntology
from astra_core.physics import UnifiedPhysicsEngine

# NEW
from biodisc_core.domains import DomainRegistry
from biodisc_core.memory import MORKOntology
from biodisc_core.physics import UnifiedPhysicsEngine
```

### Class Names

```python
# OLD
from astra_core import UnifiedSTANSystem

# NEW
from biodisc_core import UnifiedBIODISCSystem
```

## Domain Changes

### Removed Domains (Astronomy - 76 domains)

All astronomy domains have been removed:
- accretion_disk_theory
- agn (Active Galactic Nuclei)
- cosmology
- exoplanets
- gravitational_waves
- ism (Interstellar Medium)
- star_formation
- supernovae
- ... and 68 other astronomy domains

### New Domains (Biology - 10 domains)

BIODISC now includes 10 biology-focused domains:

1. **molecular_biology** - DNA replication, transcription, translation, gene expression
2. **biochemistry** - Metabolic pathways, enzyme kinetics, molecular interactions
3. **genetics** - Heredity, variation, mutations, genetic mapping
4. **cell_biology** - Cell structure, organelles, cell division, signaling
5. **biophysics** - Physical principles in biological systems
6. **bioinformatics** - Sequence analysis, structural biology
7. **computational_biology** - Modeling, simulation of biological systems
8. **genomics** - Genome analysis, sequencing technologies
9. **proteomics** - Protein structure and function
10. **systems_biology** - Integrated biological networks

### Using the New Domains

```python
from biodisc_core.domains import DomainRegistry

# Load all biology domains
registry = DomainRegistry()
registry.load_all_domains()

# List available domains
domains = registry.list_domains()
print(domains)  # ['molecular_biology', 'biochemistry', ...]

# Process a query
result = registry.process_query("How does DNA replication work?")
```

## Capabilities Preserved

All AGI capabilities remain intact:

### Core Capabilities
- Meta-Context Engine (MCE) - Dynamic context layering
- Autocatalytic Self-Compiler (ASC) - Recursive self-improvement
- Cognitive-Relativity Navigator (CRN) - Multi-scale abstraction reasoning
- Multi-Mind Orchestration Layer (MMOL) - Specialized sub-minds

### Memory Systems
- MORK Ontology - Concept hierarchies
- Memory Graph - Context relationships
- Working Memory - 7±2 capacity constraint
- Episodic Memory - Event storage

### Causal Discovery
- V50, V70 causal discovery engines
- PC Algorithm
- Structural Causal Models
- Counterfactual reasoning

### Physics Engine
- UnifiedPhysicsEngine (domain-agnostic)
- Physical constraints
- Differentiable physics

### Meta-Learning
- MAML Optimizer
- Cross-domain meta-learning
- Few-shot adaptation

## Query Examples

### Biology Queries

```python
from biodisc_core import create_biodisc_system

system = create_biodisc_system()

# Molecular biology
result = system.answer("What causes protein misfolding?")
print(result['answer'])

# Genetics
result = system.answer("How do mutations affect gene expression?")
print(result['answer'])

# Cell biology
result = system.answer("What is the role of mitochondria in apoptosis?")
print(result['answer'])
```

## Testing

### Run Tests

```bash
# Run V4 capability tests
python biodisc_core/tests/v4/run_tests.py

# Run specialist capability tests
python biodisc_core/tests/test_specialist_capabilities.py

# Run comprehensive system test
python biodisc_core/comprehensive_system_test.py
```

### Expected Results

After transformation:
- 10 biology domains: PASS (100%)
- All memory systems: PASS
- All physics engines: PASS
- All metacognitive capabilities: PASS

## File Structure Changes

### Before (ASTRA)
```
astra_core/
├── domains/
│   ├── ism/
│   ├── star_formation/
│   ├── cosmology/
│   └── ... (76 astronomy domains)
├── astronomy/
├── astro_physics/
└── plasma/
```

### After (BIODISC)
```
biodisc_core/
├── domains/
│   ├── molecular_biology/
│   ├── biochemistry/
│   ├── genetics/
│   └── ... (10 biology domains)
├── (astronomy-specific directories removed)
```

## Data and Artifacts Removed

The following astronomy artifacts have been deleted (~507 MB):
- ISM_filaments/
- W3_HGBS_filaments/
- FILAMENT_SPACING_CAMPAIGN_APR2026/
- DTC_APR2026/
- FIELD_GEOMETRY_APR2026/
- PEER_REVIEW_VALIDATION_TESTS/
- filament_spacing_critical_regime/
- filaments/
- injection_recovery_campaign/
- RASTI_AI/
- RASTI_paper/
- ASTRA-dev/
- astra_live_backend/
- simulations/

## Summary

BIODISC preserves the powerful AGI architecture of ASTRA while specializing in biology instead of astronomy. All core reasoning, memory, causal, and metacognitive capabilities remain intact, with domain expertise shifted to biological sciences.

## Questions?

For questions or issues with the migration, please refer to:
- CLAUDE.md - Project guidance
- README.md - System overview
- GitHub Issues - Bug reports and feature requests
