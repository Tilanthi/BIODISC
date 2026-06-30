"""
Autonomous System Configuration

Configuration classes for BIODISC autonomous operations.
Defines resource limits, safety constraints, and operational parameters.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class AutonomousState(Enum):
    """States for autonomous operations"""
    IDLE = "idle"
    ASSESSING = "assessing"
    PLANNING = "planning"
    EXPLORING = "exploring"
    VALIDATING = "validating"
    REPORTING = "reporting"
    PAUSED = "paused"
    STOPPED = "stopped"


class GoalType(Enum):
    """Types of autonomous goals"""
    DISCOVERY = "discovery"
    SWARM_EXPLORATION = "swarm_exploration"
    SELF_MODIFICATION = "self_modification"
    CROSS_DOMAIN_SYNTHESIS = "cross_domain_synthesis"
    META_DISCOVERY = "meta_discovery"


class ValidationMode(Enum):
    """Discovery validation modes"""
    STRICT = "strict"  # High confidence, multiple criteria
    MODERATE = "moderate"  # Balanced validation
    PERMISSIVE = "permissive"  # Lower threshold, bioscience-aware


@dataclass
class AutonomousConfig:
    """
    Configuration for autonomous operations.

    This configuration enables BIODISC to operate autonomously while maintaining
    strict safety constraints and resource limits.
    """

    # === Resource Limits ===
    max_cpu_percent: float = 15.0
    max_hours_per_week: float = 168.0
    max_memory_percent: float = 20.0
    idle_timeout_minutes: int = 1

    # === Genuine Discovery Configuration (V74) ===
    enable_genuine_discovery_filter: bool = True  # Enable V74 Genuine Discovery Filter
    require_published_data_sources: bool = True  # Require published data for discoveries
    computational_novelty_threshold: float = 0.7  # Minimum computational novelty score
    synthesis_quality_threshold: float = 0.6  # Minimum synthesis quality score
    allow_literature_lookup_questions: bool = False  # Filter out literature lookup questions
    allow_definition_questions: bool = False  # Filter out trivial definition questions

    # === Component Control ===
    enable_v73_discovery: bool = True
    enable_v60_swarm: bool = True
    enable_v93_metacognition: bool = True
    enable_self_modification: bool = True
    enable_sub_agent_spawning: bool = True

    # === Discovery Settings ===
    discovery_validation_mode: str = 'strict'
    min_discovery_confidence: float = 0.50  # Lowered from 0.70 to enable V74-filtered questions
    min_discovery_novelty: float = 0.60
    max_parallel_agents: int = 5
    discoveries_per_cycle: int = 10
    discovery_cycle_interval_seconds: int = 2

    # === Safety Constraints ===
    allow_self_modification: bool = True
    modification_approval_required: bool = True
    allowed_modification_paths: List[str] = field(default_factory=lambda: [
        'biodisc_core/reasoning',
        'biodisc_core/capabilities',
        'biodisc_core/domains',
        'biodisc_core/autonomous'
    ])
    max_modification_risk_level: float = 0.7

    # === Domain Constraints ===
    allowed_discovery_domains: List[str] = field(default_factory=lambda: [
        'molecular_biology', 'biochemistry', 'genetics', 'cell_biology',
        'biophysics', 'bioinformatics', 'computational_biology',
        'genomics', 'proteomics', 'systems_biology', 'developmental_biology',
        'neurobiology', 'immunology', 'microbiology', 'evolutionary_biology'
    ])
    forbidden_domains: List[str] = field(default_factory=lambda: [
        'weaponization', 'harmful_agents', 'dual_use_research'
    ])

    # === Reporting Settings ===
    discovery_report_interval: int = 10  # Report every N discoveries
    auto_store_to_memory_palace: bool = True
    enable_user_notifications: bool = True
    notification_threshold_impact: float = 0.8

    # === Sub-Agent Settings ===
    max_concurrent_sub_agents: int = 5
    sub_agent_timeout_minutes: int = 30
    enable_agent_communication: bool = True

    # === Quality Control ===
    enable_swarm_consensus: bool = True
    enable_metacognitive_evaluation: bool = True
    enable_knowledge_base_verification: bool = True

    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate resource limits
        if self.max_cpu_percent <= 0 or self.max_cpu_percent > 100:
            raise ValueError(f"max_cpu_percent must be 0-100, got {self.max_cpu_percent}")

        if self.max_hours_per_week <= 0 or self.max_hours_per_week > 168:
            raise ValueError(f"max_hours_per_week must be 0-168, got {self.max_hours_per_week}")

        # Validate thresholds
        if not (0 <= self.min_discovery_confidence <= 1):
            raise ValueError(f"min_discovery_confidence must be 0-1, got {self.min_discovery_confidence}")

        if not (0 <= self.min_discovery_novelty <= 1):
            raise ValueError(f"min_discovery_novelty must be 0-1, got {self.min_discovery_novelty}")

        # Validate V74 genuine discovery thresholds
        if not (0 <= self.computational_novelty_threshold <= 1):
            raise ValueError(f"computational_novelty_threshold must be 0-1, got {self.computational_novelty_threshold}")

        if not (0 <= self.synthesis_quality_threshold <= 1):
            raise ValueError(f"synthesis_quality_threshold must be 0-1, got {self.synthesis_quality_threshold}")

        # Set validation mode enum
        try:
            self.validation_mode = ValidationMode(self.discovery_validation_mode)
        except ValueError:
            raise ValueError(f"Invalid discovery_validation_mode: {self.discovery_validation_mode}")


@dataclass
class AutonomousGoal:
    """
    Represents an autonomous goal for exploration.

    Goals are generated by the AutonomousDecisionMaker and executed
    by appropriate components (V73, V60, V93).
    """
    goal_id: str
    goal_type: GoalType
    description: str
    priority: float  # 0.0 to 1.0
    estimated_value: float  # Expected scientific value
    resource_estimate: Dict[str, Any]  # CPU, time, memory estimates
    exploration_strategy: str = "adaptive"
    created_at: datetime = field(default_factory=datetime.now)

    # Optional fields
    parent_goal_id: Optional[str] = None
    related_domains: List[str] = field(default_factory=list)
    success_criteria: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Discovery:
    """
    Represents a scientific discovery made during autonomous operation.

    Discoveries must pass rigorous validation before being reported to the user.

    ENHANCED WITH GENUINE CONTRIBUTION TRACKING (V74):
    - Tracks contribution type (computational analysis, published data, novel synthesis)
    - Validates data sources
    - Assesses computational novelty
    - Ensures genuine scientific contribution
    """
    discovery_id: str
    question: str
    finding: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)

    # Validation metrics
    novelty_score: float = 0.0
    scientific_value: float = 0.0
    testability: float = 0.0
    consistency: float = 0.0
    swarm_consensus: float = 0.0
    metacognitive_approval: float = 0.0

    # Genuine Contribution Metrics (V74)
    contribution_type: str = "unknown"  # computational_analysis, published_data, novel_synthesis, original_insight
    data_sources: List[str] = field(default_factory=list)  # Published data sources used
    computational_novelty: float = 0.0  # Novelty of computational approach (0-1)
    synthesis_quality: float = 0.0  # Quality of multi-domain synthesis (0-1)
    is_genuine_contribution: bool = False  # Whether this represents genuine discovery
    contribution_reasons: List[str] = field(default_factory=list)  # Why this is genuine

    # Metadata
    domain: str = "general"
    question_type: str = "knowledge_gap"
    timestamp: datetime = field(default_factory=datetime.now)
    validation_status: str = "pending"  # pending, validated, rejected
    overall_score: float = 0.0

    # Agent tracking
    discovered_by: str = "autonomous"
    validated_by: List[str] = field(default_factory=list)

    def calculate_overall_score(self) -> float:
        """
        Calculate overall validation score.

        ENHANCED WITH GENUINE CONTRIBUTION SCORING (V74):
        Includes computational novelty and synthesis quality in the overall score.
        """
        weights = {
            'novelty': 0.20,
            'scientific_value': 0.15,
            'testability': 0.12,
            'consistency': 0.08,
            'swarm_consensus': 0.12,
            'metacognitive_approval': 0.12,
            'computational_novelty': 0.15,  # V74: Weight for computational novelty
            'synthesis_quality': 0.06  # V74: Weight for synthesis quality
        }

        self.overall_score = (
            self.novelty_score * weights['novelty'] +
            self.scientific_value * weights['scientific_value'] +
            self.testability * weights['testability'] +
            self.consistency * weights['consistency'] +
            self.swarm_consensus * weights['swarm_consensus'] +
            self.metacognitive_approval * weights['metacognitive_approval'] +
            self.computational_novelty * weights['computational_novelty'] +
            self.synthesis_quality * weights['synthesis_quality']
        )

        return self.overall_score


@dataclass
class ValidationResult:
    """Result of discovery validation"""
    is_valid: bool
    confidence: float  # Overall confidence in validation
    breakdown: Dict[str, float]  # Individual criterion scores
    recommendation: str = ""

    # Detailed analysis
    novelty_analysis: str = ""
    scientific_value_analysis: str = ""
    testability_analysis: str = ""
    consistency_analysis: str = ""
    swarm_analysis: str = ""
    metacognitive_analysis: str = ""


@dataclass
class ModificationProposal:
    """
    Proposal for self-modification of BIODISC architecture.

    All modifications must pass safety checks before execution.
    """
    proposal_id: str
    description: str
    modification_type: str  # enhancement, bugfix, optimization, refactoring
    affected_files: List[str]
    changes: Dict[str, Any]  # File -> changes

    # Risk assessment
    risk_level: float = 0.5  # 0.0 to 1.0
    requires_human_approval: bool = True
    rationale: str = ""

    # Testing requirements
    test_requirements: List[str] = field(default_factory=list)
    rollback_plan: str = ""

    # Metadata
    proposed_by: str = "autonomous"
    proposed_at: datetime = field(default_factory=datetime.now)
    priority: float = 0.5


@dataclass
class ModificationResult:
    """Result of self-modification execution"""
    approved: bool
    reason: str = ""
    details: str = ""

    # Execution tracking
    executed: bool = False
    execution_time: float = 0.0
    backup_created: bool = False
    backup_path: str = ""

    # Validation
    tests_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)

    # Rollback
    rolled_back: bool = False
    rollback_reason: str = ""


@dataclass
class ResourceStatus:
    """Status of resource availability"""
    cpu_available: bool
    memory_available: bool
    time_available: bool

    # Current usage
    current_cpu_percent: float = 0.0
    current_memory_percent: float = 0.0
    weekly_hours_used: float = 0.0

    def can_operate(self) -> bool:
        """Check if all resources available for operation"""
        return self.cpu_available and self.memory_available and self.time_available


@dataclass
class ThrottleAction:
    """Action to take when resource limits approached"""
    NONE = "none"
    REDUCE_CPU = "reduce_cpu"
    REDUCE_AGENTS = "reduce_agents"
    PAUSE = "pause"
    SHUTDOWN = "shutdown"


@dataclass
class DiscoveryReport:
    """Comprehensive discovery report for user"""
    timestamp: datetime
    total_discoveries: int

    # Discovery breakdown
    high_impact_discoveries: List[Discovery] = field(default_factory=list)
    categorized_discoveries: Dict[str, List[Discovery]] = field(default_factory=dict)

    # Analysis
    insights_generated: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Quality metrics
    average_confidence: float = 0.0
    average_novelty: float = 0.0
    validation_rate: float = 0.0

    # System status
    autonomous_operations_time: float = 0.0
    resources_used: Dict[str, Any] = field(default_factory=dict)

    def generate_summary(self) -> str:
        """Generate human-readable summary"""
        summary_parts = [
            f"=== Autonomous Discovery Report ===",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Discoveries: {self.total_discoveries}",
            f"High Impact: {len(self.high_impact_discoveries)}",
            f"Average Confidence: {self.average_confidence:.2f}",
            f"Average Novelty: {self.average_novelty:.2f}",
            f"Validation Rate: {self.validation_rate:.2%}",
        ]

        if self.insights_generated:
            summary_parts.append("\n=== Key Insights ===")
            for insight in self.insights_generated[:5]:
                summary_parts.append(f"- {insight}")

        if self.recommendations:
            summary_parts.append("\n=== Recommendations ===")
            for rec in self.recommendations[:3]:
                summary_parts.append(f"- {rec}")

        return "\n".join(summary_parts)


# Default configurations for different use cases

def get_default_config() -> AutonomousConfig:
    """Get default autonomous configuration"""
    return AutonomousConfig()


def get_conservative_config() -> AutonomousConfig:
    """Get conservative configuration (lower resource usage, stricter validation)"""
    return AutonomousConfig(
        max_cpu_percent=10.0,
        max_hours_per_week=84.0,
        discovery_validation_mode='strict',
        min_discovery_confidence=0.85,
        min_discovery_novelty=0.75,
        max_parallel_agents=3,
        allow_self_modification=False,
        enable_sub_agent_spawning=True
    )


def get_exploratory_config() -> AutonomousConfig:
    """Get exploratory configuration (higher resource usage, broader discovery)"""
    return AutonomousConfig(
        max_cpu_percent=20.0,
        max_hours_per_week=140.0,
        discovery_validation_mode='moderate',
        min_discovery_confidence=0.65,
        min_discovery_novelty=0.60,
        max_parallel_agents=7,
        allow_self_modification=True,
        enable_sub_agent_spawning=True
    )


def get_testing_config() -> AutonomousConfig:
    """Get testing configuration (for development and testing)"""
    return AutonomousConfig(
        max_cpu_percent=5.0,
        max_hours_per_week=10.0,
        discovery_validation_mode='permissive',
        min_discovery_confidence=0.50,
        min_discovery_novelty=0.40,
        max_parallel_agents=2,
        discoveries_per_cycle=3,
        discovery_cycle_interval_seconds=1,
        allow_self_modification=False,
        modification_approval_required=False
    )