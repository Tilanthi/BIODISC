"""
Autonomous Orchestrator - Main Coordinator for BIODISC Autonomous Operations

This module implements the central coordinator that integrates V73 autonomous discovery,
V60 swarm intelligence, and V93 metacognition into a unified autonomous framework.

PRINCIPLES:
1. Reactive Priority: User queries always take precedence
2. Idle Activation: Autonomous operations only when idle
3. Resource Constraints: Strict CPU/time limits
4. Safety Boundaries: BIODISC folder only, human oversight for major changes
5. Discovery Quality: Multi-criteria validation for genuine discoveries
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .config import (
    AutonomousConfig,
    AutonomousState,
    GoalType,
    AutonomousGoal,
    Discovery,
    ValidationResult,
    ResourceStatus,
    DiscoveryReport
)

logger = logging.getLogger(__name__)


class AutonomousOrchestrator:
    """
    Main autonomous coordinator for BIODISC.

    This orchestrator manages all self-initiated activities, including:
    - V73 autonomous discovery integration
    - V60 swarm intelligence coordination
    - V93 metacognitive oversight
    - Adaptive decision-making
    - Sub-agent spawning and management
    - Discovery validation and reporting
    - Resource management and safety constraints
    """

    def __init__(self, config: Optional[AutonomousConfig] = None):
        """
        Initialize the autonomous orchestrator.

        Args:
            config: Configuration for autonomous operations
        """
        self.config = config or AutonomousConfig()

        # Core autonomous components (to be initialized)
        self.v73_discovery = None
        self.v60_swarm = None
        self.v93_metacognition = None
        self.decision_maker = None
        self.sub_agent_spawner = None
        self.discovery_validator = None
        self.resource_manager = None
        self.self_modification = None
        self.discovery_reporter = None

        # State management
        self.autonomous_state = AutonomousState.IDLE
        self.last_user_activity = datetime.now()
        self.autonomous_loop_active = False
        self.autonomous_thread: Optional[threading.Thread] = None

        # Discovery tracking
        self.discoveries_made: List[Discovery] = []
        self.discoveries_validated: List[Discovery] = []
        self.discovery_cycle_count = 0

        # Resource tracking
        self.weekly_usage_hours = 0.0
        self.session_start_time = datetime.now()

        # Initialize components
        self._initialize_components()

        logger.info("Autonomous Orchestrator initialized with state: %s", self.autonomous_state)

    def _initialize_components(self):
        """Initialize autonomous components with graceful fallback"""
        try:
            # Import and initialize V73 autonomous discovery
            if self.config.enable_v73_discovery:
                self.v73_discovery = self._initialize_v73_discovery()

            # Import and initialize V60 swarm intelligence
            if self.config.enable_v60_swarm:
                self.v60_swarm = self._initialize_v60_swarm()

            # Import and initialize V93 metacognition
            if self.config.enable_v93_metacognition:
                self.v93_metacognition = self._initialize_v93_metacognition()

            # Initialize decision-maker
            from .decision_maker import AutonomousDecisionMaker
            self.decision_maker = AutonomousDecisionMaker(
                v73_curiosity=self.v73_discovery,
                v60_swarm=self.v60_swarm,
                v93_metacognition=self.v93_metacognition,
                config=self.config
            )

            # Initialize sub-agent spawner
            from .sub_agent_spawner import SubAgentSpawner
            self.sub_agent_spawner = SubAgentSpawner(
                config=self.config,
                orchestrator=self
            )

            # Initialize discovery validator
            from .discovery_validator import DiscoveryValidator
            self.discovery_validator = DiscoveryValidator(
                config=self.config,
                v60_swarm=self.v60_swarm,
                v93_metacognition=self.v93_metacognition
            )

            # Initialize resource manager
            from .resource_manager import ResourceManager
            self.resource_manager = ResourceManager(self.config)

            # Initialize self-modification framework
            if self.config.enable_self_modification:
                from .self_modification import SelfModificationFramework
                self.self_modification = SelfModificationFramework(self.config)

            # Initialize discovery reporter
            from .discovery_reporter import DiscoveryReporter
            self.discovery_reporter = DiscoveryReporter(self.config)

            logger.info("All autonomous components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize autonomous components: {e}")
            # Continue with available components

    def _initialize_v73_discovery(self):
        """Initialize V73 autonomous discovery"""
        try:
            from ..reasoning.v73_autonomous_discovery import RecursiveAutonomousDiscovery
            return RecursiveAutonomousDiscovery()
        except ImportError:
            logger.warning("V73 autonomous discovery not available")
            return None

    def _initialize_v60_swarm(self):
        """Initialize V60 swarm intelligence"""
        try:
            from ..swarm.orchestrator import SwarmOrchestrator
            return SwarmOrchestrator()
        except ImportError:
            logger.warning("V60 swarm intelligence not available")
            return None

    def _initialize_v93_metacognition(self):
        """Initialize V93 metacognition"""
        try:
            from ..legacy.systems.v93.v93_system import V93System
            return V93System()
        except ImportError:
            logger.warning("V93 metacognition not available")
            return None

    def start_autonomous_loop(self):
        """
        Start the autonomous operation loop in a background thread.

        The loop continuously checks for idle state and executes autonomous cycles
        when appropriate, always respecting resource constraints.
        """
        if self.autonomous_loop_active:
            logger.warning("Autonomous loop already active")
            return

        self.autonomous_loop_active = True
        self.autonomous_thread = threading.Thread(target=self._autonomous_loop, daemon=True)
        self.autonomous_thread.start()

        logger.info("Autonomous loop started in background thread")

    def _autonomous_loop(self):
        """
        Main autonomous operation loop.

        Runs continuously, checking for:
        1. Idle state (no recent user activity)
        2. Resource availability
        3. Appropriate autonomous state

        Executes autonomous cycles when conditions are met.
        """
        logger.info("Entering autonomous operation loop")

        while self.autonomous_loop_active:
            try:
                # Check if we should operate autonomously
                if self._should_be_autonomous():
                    # Execute one autonomous cycle
                    self._execute_autonomous_cycle()

                    # Update resource tracking
                    self._update_resource_tracking()

                # Small sleep to prevent busy-waiting
                time.sleep(self.config.discovery_cycle_interval_seconds)

            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")
                # Continue despite errors

        logger.info("Exiting autonomous operation loop")

    def _should_be_autonomous(self) -> bool:
        """
        Determine if autonomous operations should be active.

        Returns:
            True if all conditions for autonomous operation are met
        """
        # Check idle state
        idle_time = datetime.now() - self.last_user_activity
        if idle_time < timedelta(minutes=self.config.idle_timeout_minutes):
            return False  # User is active, prioritize reactive mode

        # Check resource availability
        if self.resource_manager:
            resource_status = self.resource_manager.check_resource_availability()
            if not resource_status.can_operate():
                return False  # Resource limits reached

        # Check if autonomous operations are paused
        if self.autonomous_state in [AutonomousState.PAUSED, AutonomousState.STOPPED]:
            return False

        return True

    def _execute_autonomous_cycle(self):
        """
        Execute one complete autonomous cycle.

        Cycle stages:
        1. Metacognitive assessment (V93)
        2. Generate autonomous goals (Decision Maker)
        3. Execute goals (V73/V60/V93/Sub-agents)
        4. Validate discoveries (Validator)
        5. Report back (Reporter)
        """
        try:
            # Stage 1: Metacognitive assessment
            self.autonomous_state = AutonomousState.ASSESSING
            meta_assessment = self._metacognitive_assessment()

            # Stage 2: Generate autonomous goals
            self.autonomous_state = AutonomousState.PLANNING
            autonomous_goals = self._generate_autonomous_goals(meta_assessment)

            if not autonomous_goals:
                logger.debug("No autonomous goals generated this cycle")
                return

            # Stage 3: Execute goals
            self.autonomous_state = AutonomousState.EXPLORING
            discoveries_made = self._execute_autonomous_goals(autonomous_goals)

            # Stage 4: Validate discoveries
            self.autonomous_state = AutonomousState.VALIDATING
            validated_discoveries = self._validate_discoveries(discoveries_made)

            # Stage 5: Report discoveries
            self.autonomous_state = AutonomousState.REPORTING
            self._report_discoveries(validated_discoveries)

            # Return to idle state
            self.autonomous_state = AutonomousState.IDLE
            self.discovery_cycle_count += 1

            logger.info(f"Autonomous cycle {self.discovery_cycle_count} completed. "
                       f"{len(validated_discoveries)} discoveries validated.")

        except Exception as e:
            logger.error(f"Error in autonomous cycle: {e}")
            self.autonomous_state = AutonomousState.IDLE

    def _metacognitive_assessment(self) -> Dict[str, Any]:
        """
        Perform metacognitive assessment of current knowledge state.

        Returns:
            Assessment results from V93 metacognition or empty dict
        """
        if self.v93_metacognition:
            try:
                # Use V93 to assess current cognitive state
                assessment = {
                    'cognitive_state': self.v93_metacognition.assess_cognitive_state(),
                    'knowledge_gaps': self._identify_knowledge_gaps(),
                    'bias_check': self._check_cognitive_biases(),
                    'readiness': self._assess_readiness_for_autonomous_operation()
                }
                return assessment
            except Exception as e:
                logger.error(f"Error in metacognitive assessment: {e}")

        # Fallback: basic assessment without V93
        return {
            'knowledge_gaps': self._identify_knowledge_gaps(),
            'readiness': True
        }

    def _identify_knowledge_gaps(self) -> List[str]:
        """Identify current knowledge gaps"""
        # This would interface with V73 curiosity engine
        gaps = []

        if self.v73_discovery and hasattr(self.v73_discovery, 'identify_knowledge_gaps'):
            try:
                gaps = self.v73_discovery.identify_knowledge_gaps()
            except Exception as e:
                logger.error(f"Error identifying knowledge gaps: {e}")

        return gaps

    def _check_cognitive_biases(self) -> Dict[str, Any]:
        """Check for cognitive biases in current state"""
        # This would interface with V93 metacognition
        return {'biases_detected': [], 'bias_severity': 'low'}

    def _assess_readiness_for_autonomous_operation(self) -> bool:
        """Assess if system is ready for autonomous operation"""
        # Check resource availability
        if self.resource_manager:
            resource_status = self.resource_manager.check_resource_availability()
            if not resource_status.can_operate():
                return False

        return True

    def _generate_autonomous_goals(self, meta_assessment: Dict[str, Any]) -> List[AutonomousGoal]:
        """
        Generate autonomous goals based on metacognitive assessment.

        Args:
            meta_assessment: Results from metacognitive assessment

        Returns:
            List of prioritized autonomous goals
        """
        if not self.decision_maker:
            return []

        try:
            goals = self.decision_maker.generate_goals(meta_assessment)
            logger.info(f"Generated {len(goals)} autonomous goals")
            return goals
        except Exception as e:
            logger.error(f"Error generating autonomous goals: {e}")
            return []

    def _execute_autonomous_goals(self, goals: List[AutonomousGoal]) -> List[Discovery]:
        """
        Execute autonomous goals using appropriate capabilities.

        Args:
            goals: List of autonomous goals to execute

        Returns:
            List of discoveries made during goal execution
        """
        all_discoveries = []

        for goal in goals[:self.config.discoveries_per_cycle]:
            try:
                # Execute goal based on type
                if goal.goal_type == GoalType.DISCOVERY:
                    discoveries = self._execute_discovery_goal(goal)
                elif goal.goal_type == GoalType.SWARM_EXPLORATION:
                    discoveries = self._coordinate_swarm_exploration(goal)
                elif goal.goal_type == GoalType.SELF_MODIFICATION:
                    # Self-modification doesn't produce discoveries directly
                    self._execute_self_modification(goal)
                    discoveries = []
                else:
                    discoveries = self._execute_generic_goal(goal)

                all_discoveries.extend(discoveries)

            except Exception as e:
                logger.error(f"Error executing goal {goal.goal_id}: {e}")

        return all_discoveries

    def _execute_discovery_goal(self, goal: AutonomousGoal) -> List[Discovery]:
        """Execute discovery goal using V73"""
        discoveries = []

        if self.v73_discovery:
            try:
                # Use V73 for discovery
                result = self.v73_discovery.explore_question(goal.description)
                if result:
                    discovery = self._convert_v73_result_to_discovery(result, goal)
                    discoveries.append(discovery)
            except Exception as e:
                logger.error(f"Error in V73 discovery: {e}")

        return discoveries

    def _coordinate_swarm_exploration(self, goal: AutonomousGoal) -> List[Discovery]:
        """Coordinate V60 swarm for parallel hypothesis exploration"""
        discoveries = []

        if self.v60_swarm:
            try:
                # Coordinate multiple agents for exploration
                # This would involve spawning Explorer, Falsifier, Analogist, Evolver agents
                logger.info(f"Coordinating swarm exploration for goal: {goal.description}")
                # Implementation would interface with V60 swarm orchestrator
            except Exception as e:
                logger.error(f"Error in swarm coordination: {e}")

        return discoveries

    def _execute_self_modification(self, goal: AutonomousGoal):
        """Execute self-modification goal"""
        if self.self_modification:
            try:
                # Create modification proposal
                proposal = self._create_modification_proposal(goal)
                # Execute with safety checks
                result = self.self_modification.propose_modification(proposal)
                logger.info(f"Self-modification result: {result.approved}")
            except Exception as e:
                logger.error(f"Error in self-modification: {e}")

    def _execute_generic_goal(self, goal: AutonomousGoal) -> List[Discovery]:
        """Execute generic goal using sub-agent spawning"""
        discoveries = []

        if self.sub_agent_spawner:
            try:
                # Spawn specialized sub-agent for goal
                agent = self.sub_agent_spawner.spawn_agent(goal, parent_system=self)
                # Get results from agent
                if agent:
                    discoveries = agent.get_discoveries()
            except Exception as e:
                logger.error(f"Error spawning sub-agent: {e}")

        return discoveries

    def _convert_v73_result_to_discovery(self, v73_result: Dict, goal: AutonomousGoal) -> Discovery:
        """Convert V73 result to Discovery object"""
        return Discovery(
            discovery_id=f"disc_{datetime.now().timestamp()}",
            question=goal.description,
            finding=v73_result.get('discovery', ''),
            confidence=v73_result.get('confidence', 0.7),
            evidence=v73_result.get('evidence', []),
            domain=v73_result.get('domain', 'general'),
            question_type=v73_result.get('question_type', 'knowledge_gap')
        )

    def _create_modification_proposal(self, goal: AutonomousGoal):
        """Create modification proposal from goal"""
        from .config import ModificationProposal
        return ModificationProposal(
            proposal_id=f"mod_{datetime.now().timestamp()}",
            description=goal.description,
            modification_type="enhancement",
            affected_files=[],
            changes={},
            risk_level=0.5,
            requires_human_approval=True
        )

    def _validate_discoveries(self, discoveries: List[Discovery]) -> List[Discovery]:
        """
        Validate discoveries using multi-criteria validation.

        Args:
            discoveries: List of discoveries to validate

        Returns:
            List of validated discoveries
        """
        validated = []

        for discovery in discoveries:
            try:
                if self.discovery_validator:
                    result = self.discovery_validator.validate(discovery)
                    discovery.validation_status = "validated" if result.is_valid else "rejected"
                    discovery.calculate_overall_score()

                    if result.is_valid:
                        validated.append(discovery)
                        logger.info(f"Discovery validated: {discovery.question}")
                    else:
                        logger.debug(f"Discovery rejected: {discovery.question}")

            except Exception as e:
                logger.error(f"Error validating discovery: {e}")

        # Store validated discoveries
        self.discoveries_validated.extend(validated)

        return validated

    def _report_discoveries(self, discoveries: List[Discovery]):
        """
        Report validated discoveries to user.

        Args:
            discoveries: List of validated discoveries to report
        """
        if not discoveries:
            return

        try:
            if self.discovery_reporter:
                report = self.discovery_reporter.report_discoveries(discoveries)

                # Store report
                self.discoveries_made.extend(discoveries)

                # Log high-impact discoveries
                high_impact = [d for d in discoveries if d.overall_score > self.config.notification_threshold_impact]
                if high_impact:
                    logger.info(f"=== HIGH IMPACT DISCOVERY ===")
                    for discovery in high_impact:
                        logger.info(f"Question: {discovery.question}")
                        logger.info(f"Finding: {discovery.finding}")
                        logger.info(f"Confidence: {discovery.confidence:.2f}")

                # Auto-store to memory palace if enabled
                if self.config.auto_store_to_memory_palace:
                    self._auto_store_to_memory_palace(discoveries)

        except Exception as e:
            logger.error(f"Error reporting discoveries: {e}")

    def _auto_store_to_memory_palace(self, discoveries: List[Discovery]):
        """Auto-store discoveries to memory palace"""
        try:
            # Interface with memory palace integration
            from ..reasoning.v73_memory_palace_integration import auto_store_discovery_to_memory_palace

            for discovery in discoveries:
                auto_store_discovery_to_memory_palace(discovery)
                logger.debug(f"Stored discovery to memory palace: {discovery.discovery_id}")

        except ImportError:
            logger.debug("Memory palace integration not available")
        except Exception as e:
            logger.error(f"Error storing to memory palace: {e}")

    def _update_resource_tracking(self):
        """Update resource usage tracking"""
        # Update weekly hours
        session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600
        self.weekly_usage_hours = min(session_duration, self.config.max_hours_per_week)

    def update_user_activity(self):
        """
        Update last user activity timestamp.

        Call this method when user interacts with the system to ensure
        reactive priority - autonomous operations will pause.
        """
        self.last_user_activity = datetime.now()
        logger.debug("User activity updated - autonomous operations paused")

    def get_validated_discoveries(self) -> List[Discovery]:
        """Get list of validated discoveries"""
        return self.discoveries_validated.copy()

    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get current autonomous system status"""
        return {
            'state': self.autonomous_state.value,
            'idle_time_minutes': (datetime.now() - self.last_user_activity).total_seconds() / 60,
            'discovery_cycles': self.discovery_cycle_count,
            'discoveries_validated': len(self.discoveries_validated),
            'weekly_hours_used': self.weekly_usage_hours,
            'autonomous_loop_active': self.autonomous_loop_active
        }

    def pause(self):
        """Pause autonomous operations"""
        self.autonomous_state = AutonomousState.PAUSED
        logger.info("Autonomous operations paused")

    def resume(self):
        """Resume autonomous operations"""
        if self.autonomous_state == AutonomousState.PAUSED:
            self.autonomous_state = AutonomousState.IDLE
            logger.info("Autonomous operations resumed")

    def stop(self):
        """Stop autonomous operations"""
        self.autonomous_loop_active = False
        self.autonomous_state = AutonomousState.STOPPED

        if self.autonomous_thread:
            self.autonomous_thread.join(timeout=5)

        logger.info("Autonomous operations stopped")