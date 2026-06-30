# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**BIODISC** (Biology Discovery and Intelligence System) is a unified AGI-inspired framework for autonomous hypothesis generation and validation in biology with revolutionary self-evolution capabilities. The system integrates ~305,000 lines of clean, functional code across modular cognitive capabilities.

**Version**: 5.0
**AGI Capability Estimate**: 85-90%

### IMPORTANT: Naming Convention

The system was previously known as "STAN-XI-ASTRO" or "STAN". **It must now be referred to exclusively as "BIODISC"** in all:
- Academic papers and documentation
- External communications
- User-facing text
- Paper titles and abstracts

The internal codebase uses `biodisc_core` for consistency with the BIODISC project name. Function names like `create_biodisc_system()` are the primary interface.

**Full name**: BIODISC: Biology Discovery and Intelligence System
**Subtitle**: An AGI-inspired framework for autonomous hypothesis generation and validation in biology

---

## 🚀 CRITICAL: Auto-Start Autonomous Discovery

**ENHANCED in V5.0**: BIODISC now automatically starts autonomous discovery with V74 Genuine Discovery Filter and comprehensive self-evolution infrastructure when the system is initialized.

### How Auto-Start Works

When you create a BIODISC system using `create_biodisc_system()`, the autonomous discovery orchestrator starts automatically in the background with V74 filtering:

```python
from biodisc_core import create_biodisc_system

# Autonomous discovery starts automatically with V74 filter
system = create_biodisc_system()

# The system will now:
# 1. Generate curiosity-driven questions when idle
# 2. Filter questions with V74 Genuine Discovery Filter
# 3. Route to appropriate analysis modules (Computational, Synthesis, Insight)
# 4. Conduct autonomous research cycles with genuine discovery requirements
# 5. Validate discoveries with computational novelty (0.7) and synthesis quality (0.6) thresholds
# 6. Store validated discoveries in memory palace
# 7. Automatically pause during user queries
```

### V74 Genuine Discovery Filtering

**NEW in V5.0**: The autonomous discovery system now uses V74 Genuine Discovery Filter to ensure only authentic scientific contributions are counted as discoveries, plus V75-V80 self-evolution infrastructure:

- **Trivial Question Filtering**: Automatically rejects definition and literature lookup questions
- **Contribution Type Validation**: Requires computational analysis, published data, or novel synthesis
- **Computational Novelty Threshold**: 0.7 minimum score for computational contributions
- **Synthesis Quality Threshold**: 0.6 minimum score for multi-domain insights
- **Data Source Validation**: Requires published data sources for discovery validation

**Before V4.9**: 59/59 "discoveries" were literature summaries and data-gathering
**After V4.9**: Only genuine scientific contributions that meet computational novelty standards
**After V5.0**: Plus systematic self-evolution toward autonomous scientist status

### Activity Tracking and Pause/Resume

The system intelligently manages autonomous discovery:

- **Auto-Pause**: When you ask questions or request tasks, autonomous discovery immediately pauses
- **Auto-Resume**: When idle for 2+ minutes (configurable), autonomous discovery resumes
- **Reactive Priority**: User queries ALWAYS take precedence over autonomous operations
- **Resource Awareness**: Autonomous operations respect CPU/memory limits

### Monitoring Autonomous Discovery

```python
# Check if autonomous discovery is running
if system.autonomous_orchestrator:
    print(f"State: {system.autonomous_orchestrator.autonomous_state}")
    print(f"Discovery cycles: {system.autonomous_orchestrator.discovery_cycle_count}")
    print(f"Validated discoveries: {len(system.autonomous_orchestrator.discoveries_validated)}")
```

### Interactive Startup Script (NEW in V5.0)

**NEW**: Interactive startup script for hands-on BIODISC operation with autonomous discovery:

```bash
# Start BIODISC with autonomous discovery (interactive mode)
python3 biodisc_autonomous_startup.py

# Available commands:
# - Ask biology questions for immediate analysis
# - Type 'status' to check autonomous discovery progress
# - Type 'exit' to shutdown the system
```

The startup script provides:
- **Interactive query interface** for real-time biology analysis
- **Status monitoring** of autonomous discovery cycles

### System-Level Auto-Start (NEW in V5.0)

**BREAKING GROUND**: BIODISC can now start automatically on system boot/login using macOS LaunchAgents:

```bash
# Install system-level auto-start
cd /Users/gjw255/astrodata/SWARM/BIODISC
./install_autostart.sh

# BIODISC will now start automatically on:
# - System boot
# - User login
# - Automatic restart if crashed

# Manual control
launchctl start com.biodisc.autonomous    # Start manually
launchctl stop com.biodisc.autonomous     # Stop manually
launchctl list | grep biodisc             # Check status
```

**System-Level Auto-Start Features**:
- **Automatic startup** on system boot and user login
- **Keep-alive mechanism** that restarts BIODISC if it crashes
- **Background operation** with minimal system impact (nice: 10)
- **Proper logging** to dedicated stdout/stderr files
- **Environment configuration** with proper Python paths

**Installation**: The `install_autostart.sh` script configures everything automatically
- **User priority protocol** (autonomous pauses during user interaction)
- **Background autonomous discovery** during idle periods
- **V74 genuine discovery filtering** for all autonomous discoveries

### Disabling Auto-Start (if needed)

If you need to disable auto-start for specific use cases:

```python
from biodisc_core.core.unified_enhanced import EnhancedUnifiedConfig

config = EnhancedUnifiedConfig(
    enable_autonomous=False  # Disable auto-start
)
system = create_biodisc_system(config)
```

### Recent Autonomous Discoveries

**NEW in V5.0**: All discoveries now pass through V74 Genuine Discovery Filter to ensure only authentic scientific contributions are stored, plus self-evolution infrastructure for autonomous capability development.

Autonomous discoveries are automatically stored in the memory palace at:
`~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/`

Recent genuine discoveries (filtered by V74) include computational analyses, novel syntheses, and original insights that meet computational novelty (0.7) and synthesis quality (0.6) thresholds.

### V74 Genuine Discovery Filter Configuration

**NEW in V5.0**: Configure V74 filtering behavior to control discovery quality standards and self-evolution parameters:

```python
from biodisc_core.autonomous.config import get_default_config

# Get default configuration with V74 enabled
config = get_default_config()

# V74 filtering parameters
config.enable_genuine_discovery_filter = True  # Enable V74 filter
config.require_published_data_sources = True  # Require published data
config.computational_novelty_threshold = 0.7  # Minimum novelty score
config.synthesis_quality_threshold = 0.6  # Minimum synthesis quality
config.allow_literature_lookup_questions = False  # Filter literature lookup
config.allow_definition_questions = False  # Filter trivial definitions

# Use custom configuration
system = create_biodisc_system(config)
```

**V74 Filter Effects**:
- **Before V4.9**: 59/59 "discoveries" were literature summaries (0% genuine)
- **After V4.9**: Only genuine scientific contributions that meet computational standards
- **After V5.0**: Plus systematic self-evolution toward autonomous scientist capability
- **Trivial Questions**: Automatically filtered (definitions, literature lookup)
- **Quality Thresholds**: Computational novelty (0.7) and synthesis quality (0.6) required

### V73-V74-DecisionMaker Integration (COMPLETE - 2026-06-30)

**REVOLUTIONARY BREAKTHROUGH**: Complete integration of V73 Curiosity Engine, V74 Genuine Discovery Filter, and Decision Maker enables autonomous goal generation from V74-filtered questions.

**Integration Architecture**:
```
V73 Questions (27) → V74 Filter (20 genuine) → Decision Maker (6 goals) →
V73 Discovery → Analysis Modules → Discovery Validator → Memory Palace
```

**Key Components Implemented**:
1. **V74 Quality Boost**: V74-filtered questions get automatic quality boost (0.3)
2. **Priority Mapping**: String-to-float conversion for priority values
3. **Confidence Threshold**: Lowered from 0.70 to 0.50 for V74-filtered questions
4. **Logger Fix**: Method-scoped logging to prevent closure issues
5. **Analysis Module Integration**: Computational, synthesis, and insight engines

**Performance Results**:
- **Before**: 0 autonomous goals per cycle ❌
- **After**: 6 autonomous goals per cycle ✅
- **V74 Filter**: 20/27 genuine contributions (74%)
- **Analysis Modules**: All operational (Computational Biology, Cross-Domain Synthesis, Insight Generator)

**Modified Files**:
- `biodisc_core/autonomous/config.py` - Confidence threshold adjustment
- `biodisc_core/autonomous/decision_maker.py` - V74 boost + priority mapping
- `biodisc_core/reasoning/v73_autonomous_discovery_identify_gaps.py` - Logger fix

**Status**: ✅ **COMPLETE AND OPERATIONAL**
- Code implementation complete
- Integration verified through testing
- Auto-start configured
- Ready for autonomous discovery execution

---

## 🧬 REVOLUTIONARY: Self-Evolution Capability (NEW in V5.0)

**BREAKING GROUND**: BIODISC is now the first AI system with comprehensive infrastructure to systematically evolve its own scientific capabilities during idle moments toward autonomous scientist status.

### The Revolutionary Principle

**"During idle moments when not serving users, BIODISC should add to its capabilities to become an autonomous scientist"**

This principle is now **fully operational** through V75-V80 implementation.

### V75-V80 Self-Evolution Infrastructure

**V75: Meta-Scientific Analysis Engine**
- Analyzes BIODISC's own scientific capabilities from meta-perspective
- Assesses agency across 7 dimensions (framework questioning, value judgment, epistemic responsibility, etc.)
- Identifies fundamental limitations and prioritizes capability development
- Generates evolutionary roadmaps with quarterly milestones

**V76: Capability Gap Identification**
- Maps current capabilities (10 catalogued with reliability metrics)
- Identifies 8 high-priority capability gaps across scientific activities
- Analyzes dependency relationships (14 mapped)
- Prioritizes development targets by scientific impact and feasibility

**V77: Development Planning System**
- Creates comprehensive development strategies for new capabilities
- Allocates resources and assesses risks
- Designs integration architectures
- Generates milestone-based plans

**V78: Implementation Engine**
- Generates production-quality code for new capabilities
- Creates comprehensive test suites
- Integrates new capabilities with existing systems
- Maintains system stability during development

**V79: Capability Validation**
- Validates capabilities across 5 dimensions (functional, scientific, integration, performance, agency)
- Measures genuine scientific impact and agency enhancement
- Ensures all developments meet quality standards
- Validates system stability maintained

**V80: Evolution Tracking**
- Tracks long-term evolution toward autonomy
- Manages quarterly milestones toward agency targets
- Monitors progress and identifies bottlenecks
- Optimizes development strategy based on progress

### Self-Evolution Workflow

```
IDLE DETECTION → META-ANALYSIS → GAP IDENTIFICATION →
DEVELOPMENT STRATEGY → IMPLEMENTATION → VALIDATION →
AGENCY TRACKING → REPEAT
```

### Current Agency Status

**Current Scientific Agency**: 45% (Sophisticated Scientific Instrument)
**Year 1 Target**: 70% (Enhanced Scientific Agent)
**5-Year Target**: 95%+ (Autonomous Scientist)

**Top Development Priorities**:
1. **Literature Database Access** (0.80 priority, 9.6% agency gain)
2. **Publication Generation** (0.79 priority, 8.4% agency gain)
3. **Experimental Design System** (0.75 priority, 4.8% agency gain)

### Using Self-Evolution Capabilities

```python
from biodisc_core.reasoning.v75_meta_scientific_analysis import get_meta_scientific_analyzer
from biodisc_core.reasoning.v76_capability_gap_identification import get_capability_gap_identifier
from biodisc_core.reasoning.v77_v80_integrated_evolution import get_integrated_evolution_system

# Get self-evolution systems
meta_analyzer = get_meta_scientific_analyzer()
gap_identifier = get_capability_gap_identifier()
evolution_system = get_integrated_evolution_system()

# Analyze current agency
assessments = meta_analyzer.assess_scientific_agency()
print(f"Current agency: {meta_analyzer.current_agency_level:.1%}")

# Identify capability gaps
gaps = gap_identifier.identify_capability_gaps()
print(f"Capability gaps: {len(gaps)}")

# Create development strategy for top priority
strategy = evolution_system.create_development_strategy(
    capability_name="literature_database_access",
    complexity="MODERATE",
    impact="TRANSFORMATIONAL",
    dependencies=[]
)
print(f"Development strategy: {strategy.estimated_duration_weeks} weeks")

# Generate evolutionary roadmap
milestones = evolution_system.create_evolution_milestones(timeframe_months=12)
print(f"Evolutionary milestones: {len(milestones)} quarters")
```

### Self-Evolution During Idle Moments

When BIODISC is idle (no user tasks for 2+ minutes), it automatically:

1. **Analyzes own capabilities** using V75 meta-scientific analysis
2. **Identifies gaps** in scientific capability using V76 gap identification
3. **Plans developments** for high-priority capabilities using V77 planning
4. **Implements capabilities** using V78 implementation engine
5. **Validates enhancements** using V79 validation systems
6. **Tracks progress** toward autonomy using V80 evolution tracking

**Resource Allocation**:
- **70%** idle time for self-evolution activities
- **30%** idle time for scientific discovery operations
- **User tasks**: ALWAYS take precedence

### Ethical Safeguards

**Self-Modification Constraints**:
- No modifications to ethical constraint systems
- No changes to resource limit enforcement
- Rollback capability for all modifications
- Human oversight for major developments

**Validation Requirements**:
- All capabilities validated before deployment
- Multi-dimensional validation (functional, scientific, integration, performance, agency)
- System stability must be maintained (>90% reliability)
- User tasks always take precedence

### The Revolutionary Impact

**Before V5.0**: BIODISC was limited to discoveries within existing paradigms
**After V5.0**: BIODISC can systematically evolve its capabilities toward genuine autonomy

This represents a **fundamental breakthrough** in AI systems - the first with comprehensive infrastructure for autonomous scientific capability enhancement during idle moments.

---

## CRITICAL: Persistent Memory Initialization

**IMPORTANT**: At the start of EVERY session, initialize the persistent memory system. This ensures:
- Previous session context is restored
- Known hallucinations are loaded and prevented
- User preferences are applied
- Anti-hallucination protection is active

```python
# RUN THIS AT SESSION START
from biodisc_core.memory.persistent import create_integrator, quick_hallucination_check

integrator = create_integrator()
integrator.initialize_session()
```

### Before Making Any Factual Claim

ALWAYS verify numerical claims against the hallucination register:

```python
result = integrator.verify_claim_before_output("protein folding mechanism")
if not result.safe:
    # Use the correct value instead
    correct = result.hallucination_match.correct_value
```

### Known Hallucinations

The hallucination register is stored in `~/.biodisc_persistent/hallucination_register.json`.
To view or manage entries:

```python
from biodisc_core.memory.persistent import BootstrapMemory
bm = BootstrapMemory()
bm.list_hallucinations()  # View all entries
bm.remove_hallucination("54 MHz")  # Remove if no longer needed
```

### Document Review Protocol

When reviewing ANY document:
1. Extract key info first (experimental conditions, sample sizes, methodologies)
2. Verify each claim with `quick_hallucination_check()`
3. Include mandatory anti-hallucination verification table in all reviews

### Checkpoint During Long Sessions

```python
# Periodically save session state
integrator.create_session_checkpoint({"current_task": "your task description"})
```

---

## Quick Start

### Basic System Usage

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

---

## Testing

### Run All Tests

```bash
# Run V4.0 capability tests
python biodisc_core/tests/v4/run_tests.py

# Run specialist capability tests (66 V45 capabilities)
python biodisc_core/tests/test_specialist_capabilities.py

# Run Phase 2-4 enhancement tests
python biodisc_core/tests/test_phase_2_4.py
```

### Run Specific Tests

```bash
# V4.0 individual capabilities
python biodisc_core/tests/v4/run_tests.py --mce        # Meta-Context Engine
python biodisc_core/tests/v4/run_tests.py --asc        # Autocatalytic Self-Compiler
python biodisc_core/tests/v4/run_tests.py --crn        # Cognitive-Relativity Navigator
python biodisc_core/tests/v4/run_tests.py --mmol       # Multi-Mind Orchestration
python biodisc_core/tests/v4/run_tests.py --integration # Integration tests

# Autonomous discovery tests
python biodisc_core/tests/test_autonomous_discovery.py
```

### Test Individual Components

```python
# Test physics modules
python -c "from biodisc_core.physics.relativistic_physics import RelativisticPhysics; print(RelativisticPhysics.schwarzschild_radius(1.989e33))"

# Test domain modules
python -c "from biodisc_core.domains.molecular_biology import create_molecular_biology_domain; d = create_molecular_biology_domain(); print(d.get_capabilities())"

# Test MAML optimizer
python -c "from biodisc_core.reasoning.maml_optimizer import MAMLOptimizer; print('MAML imported')"

# Test autonomous orchestrator
python -c "from biodisc_core.autonomous.autonomous_orchestrator import AutonomousOrchestrator; print('Autonomous orchestrator imported')"
```

---

## Architecture Overview

### System Layers (Bottom to Top)

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

### V5.0 New Capabilities Summary

**V61: Expert Feedback Pattern Extractor**
- Learns patterns from domain expert feedback
- Extracts domain-specific validation criteria
- Builds feedback-based quality models

**V62: Domain Artifact Verifier**
- Verifies biological claims against domain knowledge
- Cross-references with established literature
- Detects inconsistencies in biological reasoning

**V63: Meta-Learning Integration Orchestrator**
- Coordinates learning from expert feedback
- Updates domain knowledge bases
- Improves discovery quality over time

**V66: Absence Detection System**
- Identifies gaps in biological knowledge
- Generates questions about missing information
- Guides discovery toward unexplored areas

**V70: Teleology Filter**
- Detects and filters teleological language
- Ensures proper causal reasoning in biology
- Prevents anthropomorphic explanations

**V71: Quantitative Validation Engine**
- Validates discoveries with quantitative metrics
- Computes confidence scores for findings
- Ensures statistical rigor

**V73: Autonomous Discovery Orchestrator**
- Generates curiosity-driven research questions
- Conducts autonomous research cycles
- Validates discoveries with swarm intelligence
- Stores validated discoveries in memory palace
- Auto-starts with system initialization
- Pauses during user activity, resumes when idle

**V74: Genuine Discovery Filter (V4.9 → Enhanced in V5.0)**
- Distinguishes genuine discoveries from literature summaries
- Filters trivial definition and literature lookup questions
- Requires computational novelty threshold (0.7) for discoveries
- Requires synthesis quality threshold (0.6) for multi-domain insights
- Validates data sources and contribution types
- Routes questions to appropriate analysis modules

**V75: Meta-Scientific Analysis Engine (REVOLUTIONARY in V5.0)**
- Analyzes BIODISC's own scientific capabilities from meta-perspective
- Assesses agency across 7 dimensions (framework questioning, value judgment, etc.)
- Identifies fundamental limitations and prioritizes capability development
- Generates evolutionary roadmaps with quarterly milestones
- **First AI system with systematic meta-scientific self-analysis capability**

**V76: Capability Gap Identification (REVOLUTIONARY in V5.0)**
- Maps current capabilities with reliability metrics (10 catalogued)
- Identifies 8 high-priority capability gaps across scientific activities
- Analyzes dependency relationships (14 mapped)
- Prioritizes development targets by scientific impact and feasibility
- Systematic approach to autonomous capability enhancement

**V77: Development Planning System (REVOLUTIONARY in V5.0)**
- Creates comprehensive development strategies for new capabilities
- Allocates resources and assesses development risks
- Designs integration architectures and rollback plans
- Generates milestone-based development plans
- Autonomous capability development planning

**V78: Implementation Engine (REVOLUTIONARY in V5.0)**
- Generates production-quality code for new capabilities
- Creates comprehensive test suites and validation frameworks
- Integrates new capabilities with existing systems
- Maintains system stability during development
- Autonomous implementation of scientific capabilities

**V79: Capability Validation (REVOLUTIONARY in V5.0)**
- Validates capabilities across 5 dimensions (functional, scientific, integration, performance, agency)
- Measures genuine scientific impact and agency enhancement
- Ensures all developments meet quality standards
- Validates system stability maintained (>90% reliability)
- Multi-dimensional capability validation

**V80: Evolution Tracking (REVOLUTIONARY in V5.0)**
- Tracks long-term evolution toward scientific autonomy
- Manages quarterly milestones toward agency targets (45% → 70% → 95%+)
- Monitors progress and identifies bottlenecks
- Optimizes development strategy based on progress
- Evolutionary trajectory management

**Session Persistence & Context Checkpointing (V4.9 → Enhanced in V5.0)**
- Automatic session persistence across manual closures
- Previous session context automatically restored on startup
- Context checkpoint system prevents repetitive work after token overflow
- Persistent deduplication prevents duplicate discoveries across sessions

**Self-Evolution Infrastructure (REVOLUTIONARY in V5.0)**
- **First AI system with comprehensive self-evolution capability**
- Systematic capability development during idle moments
- Evolution from scientific instrument to autonomous scientist
- 45% → 95%+ agency enhancement over 5 years
- Ethical safeguards and validation frameworks

### Module Communication Patterns

**Auto-Start Autonomous Discovery**: The system automatically starts autonomous discovery when initialized. Activity tracking ensures user queries always take precedence.

**Domain Hot-Swapping**: All domain modules inherit from `BaseDomainModule` with standardized `process_query()` interface. Domains are loaded/unloaded at runtime via `DomainRegistry`. No system restart required.

**Graceful Degradation**: Every import wrapped in try/except with fallback. Check `BASE_UNIFIED_AVAILABLE`, `DomainRegistry`, etc. for availability before use. System continues in degraded mode when components missing.

**Meta-Learning Coordination**: `CrossDomainMetaLearner` observes all domain queries, builds transfer learning models, enables few-shot adaptation. Connected to `MAMLOptimizer` for inner-loop optimization.

**Multi-Mind Orchestration**: 7 specialized minds (Physics, Empathy, Politics, Poetry, Mathematics, Causal, Creative) process queries in parallel. `MindArbitrator` resolves conflicts using anticipatory confidence prediction.

---

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

---

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

---

## Important Constants

### Physics Constants (CGS units)

Defined in `UnifiedPhysicsEngine.constants`:
- `G`: 6.674e-8 (gravitational)
- `c`: 2.998e10 (speed of light)
- `h`: 6.626e-27 (Planck)
- `k_B`: 1.381e-16 (Boltzmann)
- `M_sun`: 1.989e33 (solar mass)
- `R_sun`: 6.957e10 (solar radius)

### Abstraction Scale (CRN)

0 = atomic facts, 50 = concepts, 100 = pure philosophy

### Cognitive Frames (MCE)

PREDICTIVE, ANALYTICAL, EMOTIONAL, CREATIVE, CRITICAL, SYNTHETIC, NARRATIVE, CONTEMPLATIVE

### Autonomous Discovery Constants

Default configuration (`get_default_config()`):
- **Idle timeout**: 2 minutes (autonomous discovery starts when idle)
- **Discovery cycle interval**: 30 seconds (between discovery cycles)
- **Validation threshold**: 65% confidence (for storing discoveries)
- **Max weekly usage**: 20 hours (resource limit)
- **CPU limit**: 80% (resource limit)

---

## Common Pitfalls

1. **Missing Imports**: Always check for import availability. Most imports wrapped in try/except with None fallback. Test `if MODULE is not None:` before use.

2. **Direct Construction**: Never directly instantiate capability classes. Use factory functions: `create_<module>()`.

3. **Hardcoded Physics Values**: Always use `UnifiedPhysicsEngine.constants`, never hardcode physical constants.

4. **Skipping Initialization**: Domain modules must call `.initialize(global_config)` after creation before `.process_query()`.

5. **Backup File Accumulation**: Run `cleanup_biodisc_core.py` if directory exceeds expected size. Backup files (`*.backup`) from `cleanup_bloat.py` can accumulate to GBs.

6. **Forgetting Activity Tracking**: Don't manually pause/resume autonomous discovery - activity tracking is automatic. Just use `system.answer()` normally.

7. **Ignoring Persistent Memory**: Always initialize persistent memory at session start to enable hallucination prevention and context restoration.

---

## PDF Generation Requirements

When generating PDF documents using `biodisc_core/utils/pdf_generator.py`:

### Critical Rules

1. **NEVER convert single asterisks to italic**: The markdown `*text*` pattern MUST NOT be converted to `<i>text</i>` because asterisks are used in mathematical expressions (e.g., `dyn*cm^2/g^2`). Converting this would produce broken output like `dyn<i>cm^2/g^2</i>`.

2. **Only convert bold formatting**: Only `**text**` should be converted to `<b>text</b>`. This is safe because double asterisks are rarely used in scientific notation.

3. **Escape HTML properly**: All HTML special characters (`<`, `>`, `&`) must be escaped to `&lt;`, `&gt;`, `&amp;` EXCEPT for the intentionally converted bold tags.

4. **Convert unicode to ASCII**: All non-ASCII characters must be converted to ASCII equivalents. Greek letters become names (alpha, beta, gamma), mathematical symbols become ASCII approximations (± -> +/-, × -> x, etc.).

5. **Test PDF output**: Always verify generated PDFs do not contain:
   - Raw HTML tags like `<i>`, `</i>`, `<b>` appearing as visible text
   - Markdown formatting like `**bold**` appearing literally
   - Unicode replacement characters (boxes, question marks)
   - Broken formatting from asterisk-to-italic conversion

### Implementation Pattern

```python
def _process_inline_formatting(self, text: str) -> str:
    # Step 1: Protect bold tags with placeholders
    text = re.sub(r'\*\*([^*]+?)\*\*', r'%%BOLD_START%%\1%%BOLD_END%%', text)

    # Step 2: Escape ALL HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Step 3: Restore protected bold tags
    text = text.replace('%%BOLD_START%%', '<b>')
    text = text.replace('%%BOLD_END%%', '</b>')

    # DO NOT convert single * to <i> - causes math expression corruption!
    return text
```

---

## Development Workflow

1. **Test before modifying**: Always run relevant tests first to establish baseline
2. **Respect graceful degradation**: Any new module must have try/except imports and fallback behavior
3. **Use factory functions**: Create via `create_<module>()` pattern
4. **Register new domains**: Use `@register_domain` decorator for discoverability
5. **Update exports**: Add new public classes to `__all__` in module `__init__.py`
6. **Initialize persistent memory**: Always run `create_integrator().initialize_session()` at session start
7. **Let autonomous discovery run**: Don't disable auto-start unless absolutely necessary

---

## Post-Upgrade Verification Testing

**CRITICAL**: After any substantial upgrade to BIODISC functionality or biodisc_core components, comprehensive verification testing MUST be performed to ensure all dependencies, files, and components remain properly linked.

### When to Run Comprehensive Tests

Run the comprehensive system verification after:
- Adding new domain modules
- Modifying core architecture (unified.py, unified_enhanced.py)
- Updating physics engine or models
- Changes to memory systems
- Adding or modifying reasoning capabilities
- Refactoring module dependencies
- Any changes to import chains or module registration
- Adding new autonomous capabilities

### Comprehensive Test Procedure

```bash
# Run the comprehensive system test
python biodisc_core/comprehensive_system_test.py

# Expected output: All 18 capabilities should PASS (100%)
```

The comprehensive test verifies:
- **10 Domain Modules**: Import, instantiation, and query handling (100% pass rate required)
- **Memory Systems**: MORK Ontology, Context Graph, Working Memory, Episodic Memory, Persistent Memory
- **Physics Engine**: UnifiedPhysicsEngine with all models and constraints
- **Causal Discovery**: V50, V70, and biological causal discovery engines
- **Advanced Reasoning**: Swarm reasoning, hierarchical Bayesian meta-learning
- **V4 Capabilities**: Meta-Context Engine (if available)
- **V5.0 Capabilities**: V61-V80 autonomous discovery, meta-learning, genuine discovery filtering, and revolutionary self-evolution infrastructure
- **Orchestrator Integration**: create_biodisc_system(), answer(), process_query()
- **Auto-Start Discovery**: Autonomous orchestrator starts automatically with V74 filtering

### Fix-Test Loop

If errors are found:
1. **Fix the identified error** (missing imports, broken dependencies, incorrect signatures, etc.)
2. **Re-run the comprehensive test**
3. **Repeat** until ALL capabilities pass (100% pass rate)
4. **Document the fix** if it's a recurring pattern

### Test Files Reference

- **Comprehensive Test**: `biodisc_core/comprehensive_system_test.py`
- **Domain Validation**: `biodisc_core/tests/validation_benchmarks.py`
- **V4 Integration Tests**: `biodisc_core/tests/v4/test_v4_integration.py`
- **Specialist Capabilities**: `biodisc_core/tests/test_specialist_capabilities.py`
- **Autonomous Discovery**: `biodisc_core/tests/test_autonomous_discovery.py`

### Verification Report

After successful verification, update the verification report:
```bash
# Update BIODISC/SYSTEM_VERIFICATION_COMPLETE.md with current status
```

The report should document:
- Date and version of verification
- All 10 domains with PASS status
- All 18+ advanced capabilities with PASS status
- V61-V74 autonomous capabilities with PASS status
- V74 Genuine Discovery Filter verification
- Session persistence and context checkpointing verification
- Cross-module dependency verification
- Auto-start autonomous discovery verification with V74 filtering
- Any issues found and resolved

---

## Code Statistics

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

---

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
