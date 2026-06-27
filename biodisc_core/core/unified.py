"""
BIODISC-CORE: Unified AGI System - All Capabilities Integrated (BIOLOGY ENHANCED)
==============================================================================

This is the unified BIODISC system that automatically integrates ALL capabilities
from versions V36-V94 into a single, optimized system that selects the best
approaches for maximum performance without version dependencies.

**BIOLOGY ENHANCED VERSION**: This specialized version integrates biology domain
knowledge, training data, and specialized reasoning capabilities for molecular
biology, genetics, and life sciences applications.

Core Integrated Capabilities:
- Symbolic causal reasoning (V36)
- Swarm intelligence & memory (V37)
- Bayesian inference & tools (V38)
- Advanced reasoning capabilities (V39)
- Formal logic & causal models (V40)
- Self-reflection & analogical reasoning (V41)
- GPQA-optimized scientific reasoning (V42-V50)
- Neural-symbolic integration (V80)
- Metacognitive consciousness (V90)
- Embodied social AGI (V91)
- Scientific discovery (V92)
- Self-modifying architecture (V93)
- Embodied learning (V94)

**BIOLOGY-SPECIFIC ENHANCEMENTS**:
- Molecular and cellular biology reasoning
- Genetics and genomics expertise
- Protein structure and function analysis
- Metabolic pathway modeling
- Biochemical reaction networks
- Systems biology integration
- Drug discovery and mechanism analysis
- Evolutionary biology and phylogenetics

The system automatically selects optimal capabilities based on the task.
"""

__version__ = "4.8.0-BIOLOGY"

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import logging
import re

# Import meta-cognitive data sufficiency for graceful degradation
try:
    from ..metacognitive.data_sufficiency_evaluator import DataSufficiency
    DATA_SUFFICIENCY_AVAILABLE = True
except ImportError:
    DATA_SUFFICIENCY_AVAILABLE = False
    # Create dummy enum for graceful degradation
    class DataSufficiency(Enum):
        SUFFICIENT = "sufficient"
        UNCERTAIN = "uncertain"
        INSUFFICIENT = "insufficient"

# Import all capabilities from version-specific modules
try:
    # Core reasoning capabilities (from core_legacy)
    from ..core_legacy.v36 import V36CoreSystem
    from ..core_legacy.v37 import V37CompleteSystem
    from ..core_legacy.v38 import V38CompleteSystem
    from ..core_legacy.v39 import V39CompleteSystem
    from ..core_legacy.v40 import V40CompleteSystem
    from ..core_legacy.v41 import V41CompleteSystem
    from ..core_legacy.v42 import V42CompleteSystem
    from ..core_legacy.v80 import V80CompleteSystem
    from ..core_legacy.v90 import V90CompleteSystem
    from ..core_legacy.v91 import V91CompleteSystem
    from ..core_legacy.v92 import V92CompleteSystem
    from ..core_legacy.v93 import V93CompleteSystem
    from ..core_legacy.v94 import V94CompleteSystem
except Exception as e:
    # Log the error but don't fail - legacy modules are optional for V100
    import logging
    logging.warning(f"Legacy module import failed: {type(e).__name__}: {e}")
    # Set all to None
    V36CoreSystem = None
    V37CompleteSystem = None
    V38CompleteSystem = None
    V39CompleteSystem = None
    V40CompleteSystem = None
    V41CompleteSystem = None
    V42CompleteSystem = None
    V80CompleteSystem = None
    V90CompleteSystem = None
    V91CompleteSystem = None
    V92CompleteSystem = None
    V93CompleteSystem = None
    V94CompleteSystem = None

# Import memory and intelligence systems
from ..memory import MemoryGraph, MORKOntology, ExpandedMORK
from ..intelligence import SwarmOrchestrator, DigitalPheromoneField
from ..capabilities import (
    BayesianInference, CausalDiscovery, AbductiveInference,
    SelfConsistency, ExternalKnowledge, LLMInference,
    MetaLearning, AnalogicalReasoning, ToolIntegration
)

# BIOLOGY-specific capabilities (removed astrophysics imports)
# These imports were removed as they were astronomy-specific:
# - AstroSwarmSystem, PhysicsEngine (from astro_physics)
# - GravitationalLensModel, AstrophysicalConstraints (from astro_physics.physics)
# - StatisticalEquilibriumSolver (from astro_physics.radiative_transfer)
# - BayesianSwarmInference (from astro_physics.inference)
#
# BIODISC uses biology-specific modules instead:
# - Molecular biology reasoning engines
# - Genetics and genomics analysis
# - Biochemical pathway modeling
# - Protein structure analysis

BIOLOGY_CAPABILITIES_AVAILABLE = False  # Set to True when biology modules are loaded

class TaskType(Enum):
    """Automatically detected task types for optimal capability selection"""
    SCIENTIFIC_REASONING = "scientific"
    MATHEMATICAL = "mathematical"
    CAUSAL_ANALYSIS = "causal"
    PATTERN_RECOGNITION = "pattern"
    SOCIAL_REASONING = "social"
    CREATIVE_PROBLEM_SOLVING = "creative"
    FORMAL_REASONING = "formal"
    METACOGNITIVE = "metacognitive"
    EMBODIED_TASK = "embodied"
    ETHICAL_REASONING = "ethical"
    COMPLEX_SYSTEM = "complex"
    ARBITRARY = "arbitrary"

    # BIOLOGY-SPECIFIC TASK TYPES (replaced astrophysics tasks)
    MOLECULAR_BIOLOGY = "molecular_biology"
    GENETICS = "genetics"
    CELL_BIOLOGY = "cell_biology"
    BIOCHEMISTRY = "biochemistry"
    EVOLUTIONARY_BIOLOGY = "evolutionary_biology"
    SYSTEMS_BIOLOGY = "systems_biology"
    BIOINFORMATICS = "bioinformatics"
    PROTEOMICS = "proteomics"
    GENOMICS = "genomics"
    BIOPHYSICS = "biophysics"

@dataclass
class UnifiedConfig:
    """Configuration for the unified BIODISC system"""
    # Capability selection
    auto_optimize: bool = True
    use_all_capabilities: bool = True
    prefer_latest_capabilities: bool = True

    # Performance settings
    max_compute_budget: float = 100.0  # Computational units
    timeout_seconds: float = 300.0