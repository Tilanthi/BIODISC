# BIODISC Testing Guide

## Run All Tests

```bash
# Run V4.0 capability tests
python biodisc_core/tests/v4/run_tests.py

# Run specialist capability tests (66 V45 capabilities)
python biodisc_core/tests/test_specialist_capabilities.py

# Run Phase 2-4 enhancement tests
python biodisc_core/tests/test_phase_2_4.py
```

## Run Specific Tests

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

## Test Individual Components

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
