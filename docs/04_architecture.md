# BIODISC System Architecture

## System Layers (Bottom to Top)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Entry Points (Top Layer)                     │
│  create_biodisc_system() | create_biodisc_v4_system() | process_query()   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│         V5.0 Self-Evolution Layer (REVOLUTIONARY - NEW)       │
│  V75 Meta-Analysis | V76 Gap ID | V77 Development | V78 Impl │
│  V79 Validation | V80 Evolution Tracking | Self-Enhancement  │
│  First AI System with Comprehensive Self-Evolution Capability │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│              V4.9 Autonomous Discovery Layer (Enhanced in V5.0) │
│  V73 Curiosity Engine | V74 Genuine Discovery Filter | Activity │
│  Tracking | Auto-Pause/Resume | Memory Palace Integration      │
│  Session Persistence | Context Checkpointing                   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                 V4.0 Revolutionary Capabilities                  │
│  MCE (Context) | ASC (Self-Improvement) | CRN (Abstraction)    │
│  MMOL (7 Specialized Minds)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│           V61-V63 Meta-Learning from Expert Feedback            │
│  Expert Feedback Pattern Extractor | Domain Artifact Verifier   │
│  Meta-Learning Integration Orchestrator                        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│           V66, V70-V71 Discovery & Inference Enhancement        │
│  Absence Detection | Teleology Filter | Quantitative Validation │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Domain Architecture                          │
│  BaseDomainModule → DomainRegistry → Specialized Domains        │
│  (10 domains: Molecular Biology, Biochemistry, Genetics,        │
│   Cell Biology, Biophysics, Bioinformatics, Computational       │
│   Biology, Genomics, Proteomics, Systems Biology)               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                Cross-Domain Meta-Learning                       │
│  MAMLOptimizer | CrossDomainMetaLearner | AdaptationResult      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   Physics & Causal Engines                      │
│  UnifiedPhysicsEngine | StructuralCausalModel | PCAlgorithm      │
│  PhysicsCurriculum | PhysicalAnalogicalReasoner                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  Memory & Knowledge Systems                     │
│  MORKOntology | MemoryGraph | VectorStore | WorkingMemory       │
│  Persistent Memory | Hallucination Register | Memory Palace      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Capabilities Registry                         │
│  66+ specialist capabilities (V36-V94) with auto-selection      │
└─────────────────────────────────────────────────────────────────┘
```

## Module Communication Patterns

### Auto-Start Autonomous Discovery
The system automatically starts autonomous discovery when initialized. Activity tracking ensures user queries always take precedence.

### Domain Hot-Swapping
All domain modules inherit from `BaseDomainModule` with standardized `process_query()` interface. Domains are loaded/unloaded at runtime via `DomainRegistry`. No system restart required.

### Graceful Degradation
Every import wrapped in try/except with fallback. Check `BASE_UNIFIED_AVAILABLE`, `DomainRegistry`, etc. for availability before use. System continues in degraded mode when components missing.

### Meta-Learning Coordination
`CrossDomainMetaLearner` observes all domain queries, builds transfer learning models, enables few-shot adaptation. Connected to `MAMLOptimizer` for inner-loop optimization.

### Multi-Mind Orchestration
7 specialized minds (Physics, Empathy, Politics, Poetry, Mathematics, Causal, Creative) process queries in parallel. `MindArbitrator` resolves conflicts using anticipatory confidence prediction.

## Key Design Patterns

### 1. Capability Auto-Selection

The system automatically selects capabilities based on task analysis. Do not manually invoke capabilities unless specifically testing individual components.

```python
# WRONG: Manual capability selection
result = system.reasoning.causal_discovery(query)

# CORRECT: Let system auto-select
result = system.answer(query)  # Auto-selects best capabilities
# Autonomous discovery automatically pauses during query processing
```

### 2. Module Registration Pattern

All domain modules use `@register_domain` decorator or explicit `DomainModuleRegistry.register()`. This enables runtime discovery and hot-swapping.

```python
from biodisc_core.domains import BaseDomainModule, register_domain

@register_domain
class MyDomain(BaseDomainModule):
    def get_default_config(self):
        return DomainConfig(
            domain_name="my_domain",
            version="1.0.0",
            keywords=["keyword1", "keyword2"],
            capabilities=["capability1", "capability2"]
        )
```

### 3. Factory Function Pattern

All major components use factory functions for creation, not direct constructors. This enables configuration injection and graceful fallback.

```python
# Use factory functions
system = create_biodisc_system()  # Auto-starts autonomous discovery
mce = create_meta_context_engine()
optimizer = create_maml_optimizer(model_fn, loss_fn)

# NOT: system = UnifiedBIODISCSystem()  # Avoid direct constructors
```

### 4. Physics Curriculum Learning

Physics capabilities develop through staged curriculum (`ComplexityLevel.BASIC` → `EXPERT`). Do not skip stages. Use `PhysicsCurriculum.get_next_stage()` for progression.

### 5. Autonomous Activity Tracking

User activity is automatically tracked to pause/resume autonomous discovery:

```python
# Activity tracking happens automatically in process_query()
system.answer("What causes protein misfolding?")  # Pauses autonomous discovery

# When idle for 2+ minutes, autonomous discovery automatically resumes
# No manual intervention required
```

## File Organization Conventions

### Capability Files

- **V36-V50 capabilities**: `biodisc_core/capabilities/vXX_*.py`
- **V61-V73 capabilities**: `biodisc_core/capabilities/v1XX_*.py`
- **Physics modules**: `biodisc_core/physics/*.py` (relativistic_physics.py, quantum_mechanics.py, nuclear_physics.py)
- **Domain modules**: `biodisc_core/domains/<domain_name>/__init__.py`
- **Meta-learning**: `biodisc_core/reasoning/maml_optimizer.py`, `cross_domain_meta_learner.py`
- **Autonomous system**: `biodisc_core/autonomous/` (orchestrator, decision_maker, validator, etc.)

### Memory Hierarchy

- **MORK Ontology**: `biodisc_core/memory/mork_ontology.py` (concept hierarchies)
- **Memory Graph**: `biodisc_core/memory/context_graph.py` (context relationships)
- **Working Memory**: `biodisc_core/memory/working/` (7±2 capacity constraint)
- **Persistent Memory**: `biodisc_core/memory/persistent.py` (session persistence, hallucination register)
- **Memory Palace**: `~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/` (autonomous discoveries)

### Test Files

- **Integration tests**: `biodisc_core/tests/v4/test_v4_integration.py`
- **Capability tests**: `biodisc_core/tests/test_specialist_capabilities.py`
- **Autonomous tests**: `biodisc_core/tests/test_autonomous_discovery.py`
- **Validation**: `biodisc_core/tests/validation_benchmarks.py`
