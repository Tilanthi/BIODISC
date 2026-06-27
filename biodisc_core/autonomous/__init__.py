"""
BIODISC Autonomous System

This module provides autonomous capabilities for BIODISC, including:
- Autonomous discovery orchestration
- Adaptive decision-making
- Sub-agent spawning and coordination
- Discovery validation and reporting
- Safe self-modification framework

The autonomous system operates alongside reactive query processing,
only becoming active when the system is idle and within resource constraints.
"""

from .config import (
    AutonomousConfig,
    AutonomousState,
    GoalType,
    ValidationMode,
    AutonomousGoal,
    Discovery,
    ValidationResult,
    ModificationProposal,
    ModificationResult,
    ResourceStatus,
    DiscoveryReport,
    get_default_config,
    get_conservative_config,
    get_exploratory_config,
    get_testing_config
)

# Export main components
from .autonomous_orchestrator import AutonomousOrchestrator
from .decision_maker import AutonomousDecisionMaker
from .discovery_validator import DiscoveryValidator
from .resource_manager import ResourceManager
from .self_modification import SelfModificationFramework
from .sub_agent_spawner import SubAgentSpawner, SubAgent
from .discovery_reporter import DiscoveryReporter

__all__ = [
    # Configuration
    'AutonomousConfig',
    'AutonomousState',
    'GoalType',
    'ValidationMode',
    'AutonomousGoal',
    'Discovery',
    'ValidationResult',
    'ModificationProposal',
    'ModificationResult',
    'ResourceStatus',
    'DiscoveryReport',
    'get_default_config',
    'get_conservative_config',
    'get_exploratory_config',
    'get_testing_config',

    # Main Components
    'AutonomousOrchestrator',
    'AutonomousDecisionMaker',
    'DiscoveryValidator',
    'ResourceManager',
    'SelfModificationFramework',
    'SubAgentSpawner',
    'SubAgent',
    'DiscoveryReporter',
]

# Version
__version__ = '1.0.0'