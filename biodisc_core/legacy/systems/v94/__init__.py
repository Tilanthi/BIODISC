"""
STAN V94: Embodied Learning and Grounded Cognition Architecture (ASTRO Version)

This module implements the paradigm shift from simulated intelligence to experienced intelligence
through embodied learning, sensorimotor integration, and grounded cognition.

WARNING: The astro_embodied_integration module has been DELETED from BIODISC (biology-focused system).
This astronomy-specific integration should be used in a separate astronomy system.
"""

from .embodied_learning_engine import EmbodiedLearningEngine
from .sensorimotor_system import SensorimotorInterface, WorldAction, Experience
from .developmental_learning import DevelopmentalLearning, PlayfulExplorer
from .common_sense_engine import CommonSenseEngine, PhysicsIntuitionModule
from .language_grounding import LanguageGroundingEngine, ConceptGroundingEngine
from .v94_complete import V94CompleteSystem, V94Config

# ASTRONOMY-SPECIFIC MODULE - DELETED FROM BIODISC
try:
    from .astro_embodied_integration import AstroEmbodiedIntegrator
    ASTRO_EMBODIED_AVAILABLE = True
except ImportError:
    ASTRO_EMBODIED_AVAILABLE = False
    AstroEmbodiedIntegrator = None

__all__ = [
    'EmbodiedLearningEngine',
    'SensorimotorInterface',
    'WorldAction',
    'Experience',
    'DevelopmentalLearning',
    'PlayfulExplorer',
    'CommonSenseEngine',
    'PhysicsIntuitionModule',
    'LanguageGroundingEngine',
    'ConceptGroundingEngine',
    'V94CompleteSystem',
    'V94Config',
    'AstroEmbodiedIntegrator',
    'ASTRO_EMBODIED_AVAILABLE'
]
