# BIODISC Physics Constants and Reference Values

## Physics Constants (CGS units)

Defined in `UnifiedPhysicsEngine.constants`:

- `G`: 6.674e-8 (gravitational)
- `c`: 2.998e10 (speed of light)
- `h`: 6.626e-27 (Planck)
- `k_B`: 1.381e-16 (Boltzmann)
- `M_sun`: 1.989e33 (solar mass)
- `R_sun`: 6.957e10 (solar radius)

## Abstraction Scale (CRN)

0 = atomic facts, 50 = concepts, 100 = pure philosophy

## Cognitive Frames (MCE)

PREDICTIVE, ANALYTICAL, EMOTIONAL, CREATIVE, CRITICAL, SYNTHETIC, NARRATIVE, CONTEMPLATIVE

## Autonomous Discovery Constants

Default configuration (`get_default_config()`):
- **Idle timeout**: 2 minutes (autonomous discovery starts when idle)
- **Discovery cycle interval**: 30 seconds (between discovery cycles)
- **Validation threshold**: 65% confidence (for storing discoveries)
- **Max weekly usage**: 20 hours (resource limit)
- **CPU limit**: 80% (resource limit)

## Important Usage Notes

### Hardcoded Physics Values

**ALWAYS use `UnifiedPhysicsEngine.constants`**, never hardcode physical constants in your code. This ensures consistency and makes updates easier.

```python
# CORRECT: Use constants from UnifiedPhysicsEngine
from biodisc_core.physics import UnifiedPhysicsEngine
G = UnifiedPhysicsEngine.constants.G
c = UnifiedPhysicsEngine.constants.c

# WRONG: Hardcoded values
G = 6.674e-8  # Don't do this
c = 2.998e10  # Don't do this
```

### Physics Curriculum Learning

Physics capabilities develop through staged curriculum (`ComplexityLevel.BASIC` → `EXPERT`). Do not skip stages. Use `PhysicsCurriculum.get_next_stage()` for progression.

## Physics Modules Location

- **Relativistic Physics**: `biodisc_core/physics/relativistic_physics.py`
- **Quantum Mechanics**: `biodisc_core/physics/quantum_mechanics.py`
- **Nuclear Physics**: `biodisc_core/physics/nuclear_physics.py`
- **Unified Physics Engine**: `biodisc_core/physics/unified.py`
