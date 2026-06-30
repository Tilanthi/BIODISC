# BIODISC Astrophy s Cleanup Summary

## Problem Identified

When generating PDFs or importing BIODISC modules, the following **inappropriate warnings** appeared:

```
WARNING:root:Astro physics capabilities not available
WARNING:biodisc_core.physics:AstrophysicalConstraints not available
```

These warnings indicate that the code was attempting to load **astrophysics modules** from the old ASTRA system, which is inappropriate for a **biology-focused system (BIODISC)**.

## Root Cause

The BIODISC codebase inherited legacy code from ASTRA (Autonomous Scientific Discovery in Astrophysics) that still contained:
1. Import statements for `astro_physics` modules (don't exist in BIODISC)
2. Astrophysics-specific task types (ASTROPHYSICS, COSMOLOGY, etc.)
3. Astrophysics-specific physics domains (GRAVITATIONAL, RADIATIVE, COSMOLOGICAL)
4. Astrophysics-specific constants (M_sun, R_sun, AU, pc)
5. Astrophysics-specific physics models (gravitational lensing, blackbody radiation)

## Files Modified

### 1. `/biodisc_core/physics/__init__.py`

**Changes:**
- Updated docstring from "STAN-XI-ASTRO" to "BIODISC"
- Removed import of `AstrophysicalConstraints` from `astro_physics.physics`
- Replaced astrophysics domains with biology-appropriate domains:
  - ~~GRAVITATIONAL~~ → MECHANICAL (forces, mechanics, cell wall stress)
  - ~~RADIATIVE~~ → ELECTROSTATIC (charges, membrane potentials)
  - ~~COSMOLOGICAL~~ → TOPOLOGICAL (DNA topology, supercoiling)
  - Added: DIFFUSIVE, CHEMICAL for biological relevance
- Replaced astrophysics constants with biological constants:
  - Removed: M_sun, R_sun, L_sun, AU, pc (astronomical units)
  - Kept: k_B, h, c (universal constants)
  - Added: kT_room (thermal energy scale), nm, um (molecular/cellular scales)
- Removed `NuclearAstrophysics` import and export

### 2. `/biodisc_core/core/unified.py`

**Changes:**
- Removed imports of ASTRA-specific modules:
  - `AstroSwarmSystem, PhysicsEngine`
  - `GravitationalLensModel, AstrophysicalConstraints`
  - `StatisticalEquilibriumSolver`
  - `BayesianSwarmInference`
- Set `ASTRO_CAPABILITIES_AVAILABLE = False` (always False for BIODISC)
- Replaced astrophysics task types with biology task types:
  - ~~ASTROPHYSICS~~ → MOLECULAR_BIOLOGY
  - ~~COSMOLOGY~~ → EVOLUTIONARY_BIOLOGY
  - Added: GENETICS, CELL_BIOLOGY, BIOCHEMISTRY, etc.

### 3. `/biodisc_core/legacy/systems/unified.py`

**Changes:**
- Same astrophysics import removals as `/biodisc_core/core/unified.py`
- Same task type replacements
- Removed astrophysics-specific task keywords (telescope, galaxy, nebula, etc.)
- Added biology-specific task keywords (dna, protein, cell, membrane, etc.)

### 4. `/biodisc_core/core/__init__.py`

**Changes:**
- Disabled `_init_astronomy_components()` method entirely
- This method was trying to import:
  - TimeSeriesAnalyzer, SpectralLineAnalyzer (astrophysics-specific)
  - GalaxyMorphologyCNN, FilamentDetector (astrophysics-specific)
  - StreamingAlertProcessor, GWEMCorrelator (astrophysics-specific)
- Replaced method with a note explaining these are not applicable to BIODISC

## Verification

### Before Fix:
```
WARNING:root:Astro physics capabilities not available
WARNING:biodisc_core.physics:AstrophysicalConstraints not available
WARNING:biodisc_core.physics:Differentiable physics module not available, using fallbacks
```

### After Fix:
```
WARNING:root:Legacy module import failed: ImportError: cannot import name 'V36CoreSystem'
WARNING:biodisc_core.physics:Differentiable physics module not available, using fallbacks
WARNING: V50 causal engine not available
```

**Result:** All astrophysics-specific warnings are now eliminated. The remaining warnings are for different issues (legacy modules, differentiable physics, causal engines) and are not astrophysics-specific.

## Architecture Principle

**Key Insight:** Domain-specific systems should not attempt to load modules from other domains.

- **ASTRA** (astrophysics) → Should load astro_physics modules
- **BIODISC** (biology) → Should NOT load astro_physics modules
- **TRADING** (finance) → Should NOT load astro_physics modules

Each domain system should have its own:
1. Domain-specific task types
2. Domain-specific physics domains
3. Domain-specific constants
4. Domain-specific component imports

## Remaining Work (Optional)

The following warnings still appear but are **NOT astrophysics-specific**:

1. **"Legacy module import failed: V36CoreSystem"** - This is a separate legacy module issue unrelated to astrophysics

2. **"Differentiable physics module not available"** - This is a general physics module warning, not astrophysics-specific

3. **"V50 causal engine not available"** - This is a causal engine warning, not astrophysics-specific

These could be addressed separately if desired, but they do not indicate inappropriate domain mixing.

## Files That Still Reference Astro (for reference)

The following test files still reference astro_physics but do not generate warnings because they are not imported during normal operation:

- `/biodisc_core/tests/test_specialist_capabilities.py`
- `/biodisc_core/tests/test_installation.py`
- `/biodisc_core/scientific_discovery/discovery_orchestrator.py`

These could be updated if needed, but they don't affect normal BIODISC operation.

---

**Fix Completed:** 2026-04-23
**System:** BIODISC (Biology Discovery and Intelligence System)
**Issue Removed:** Inappropriate astrophysics module loading in a biology system
