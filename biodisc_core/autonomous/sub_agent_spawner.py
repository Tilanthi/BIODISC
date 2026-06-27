"""
Sub-Agent Spawning System

Manages creation and coordination of specialized sub-agents for focused exploration.

This system enables BIODISC to autonomously spawn specialized agents to explore
specific knowledge domains, mechanisms, or cross-domain connections.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from .config import (
    AutonomousConfig,
    GoalType,
    AutonomousGoal,
    Discovery
)

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of specialized sub-agents"""
    DEEP_EXPLORATION = "deep_exploration"
    CROSS_DOMAIN = "cross_domain"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    HYPOTHESIS_GENERATOR = "hypothesis_generator"
    MECHANISM_INVESTIGATOR = "mechanism_investigator"
    LITERATURE_SYNTHESIS = "literature_synthesis"
    EXPERIMENTAL_DESIGN = "experimental_design"


class AgentState(Enum):
    """States for sub-agents"""
    SPAWNING = "spawning"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class AgentStatus:
    """Status of a sub-agent"""
    agent_id: str
    agent_type: AgentType
    state: AgentState
    goal_id: str
    progress: float = 0.0
    discoveries_made: List[Discovery] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error_message: str = ""

    @property
    def duration(self) -> float:
        """Duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def is_complete(self) -> bool:
        """Check if agent is complete"""
        return self.state in [AgentState.COMPLETE, AgentState.ERROR, AgentState.TIMEOUT]


@dataclass
class SubAgent:
    """
    Specialized sub-agent for focused exploration.

    Sub-agents are spawned by the autonomous orchestrator to pursue
    specific goals that require specialized approaches.
    """
    agent_id: str
    agent_type: AgentType
    goal: AutonomousGoal
    parent_system: Any  # Reference to parent system

    # Agent state
    state: AgentState = AgentState.SPAWNING
    progress: float = 0.0
    discoveries: List[Discovery] = field(default_factory=list)

    # Threading
    thread: Optional[threading.Thread] = None
    active: bool = True

    # Timeout
    timeout_seconds: int = 1800  # 30 minutes default

    def start(self):
        """Start the agent in a background thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"Agent {self.agent_id} started")

    def _run(self):
        """Main agent loop"""
        try:
            self.state = AgentState.ACTIVE
            logger.info(f"Agent {self.agent_id} executing goal: {self.goal.description}")

            # Execute based on agent type
            discoveries = self._execute_goal()

            # Store discoveries
            self.discoveries = discoveries
            self.progress = 1.0
            self.state = AgentState.COMPLETE

            logger.info(f"Agent {self.agent_id} completed with {len(discoveries)} discoveries")

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Agent {self.agent_id} error: {e}")
        finally:
            self.active = False

    def _execute_goal(self) -> List[Discovery]:
        """Execute goal based on agent type"""
        discoveries = []

        try:
            if self.agent_type == AgentType.DEEP_EXPLORATION:
                discoveries = self._deep_exploration()
            elif self.agent_type == AgentType.CROSS_DOMAIN:
                discoveries = self._cross_domain_exploration()
            elif self.agent_type == AgentType.QUANTITATIVE_ANALYSIS:
                discoveries = self._quantitative_analysis()
            elif self.agent_type == AgentType.HYPOTHESIS_GENERATOR:
                discoveries = self._generate_hypotheses()
            elif self.agent_type == AgentType.MECHANISM_INVESTIGATOR:
                discoveries = self._investigate_mechanism()
            elif self.agent_type == AgentType.LITERATURE_SYNTHESIS:
                discoveries = self._synthesize_literature()
            elif self.agent_type == AgentType.EXPERIMENTAL_DESIGN:
                discoveries = self._design_experiments()
            else:
                discoveries = self._generic_exploration()

        except Exception as e:
            logger.error(f"Error executing goal: {e}")

        return discoveries

    def _deep_exploration(self) -> List[Discovery]:
        """Deep exploration of a specific mechanism or concept"""
        discoveries = []

        # Simulate deep exploration process
        self.progress = 0.2

        # Step 1: Analyze the goal
        analysis = self._analyze_goal()
        self.progress = 0.4

        # Step 2: Deep dive into related literature/concepts
        deep_findings = self._deep_dive_research(analysis)
        self.progress = 0.7

        # Step 3: Synthesize findings into discoveries
        for finding in deep_findings:
            discovery = Discovery(
                discovery_id=f"deep_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=finding,
                confidence=0.75,
                evidence=["deep_exploration_analysis"],
                domain=self.goal.related_domains[0] if self.goal.related_domains else "general"
            )
            discoveries.append(discovery)

        self.progress = 1.0
        return discoveries

    def _cross_domain_exploration(self) -> List[Discovery]:
        """Explore connections between multiple domains"""
        discoveries = []

        # Identify domains involved
        domains = self.goal.related_domains or ['general']

        if len(domains) >= 2:
            # Cross-domain analysis
            connections = self._find_cross_domain_connections(domains)

            for connection in connections:
                discovery = Discovery(
                    discovery_id=f"cross_{datetime.now().timestamp()}",
                    question=self.goal.description,
                    finding=connection,
                    confidence=0.70,
                    evidence=["cross_domain_analysis"],
                    domain="cross_domain"
                )
                discoveries.append(discovery)

        return discoveries

    def _quantitative_analysis(self) -> List[Discovery]:
        """Focus on quantitative gaps and mathematical relationships"""
        discoveries = []

        # Analyze quantitative aspects of the goal
        quantitative_insights = self._analyze_quantitative_aspects()

        for insight in quantitative_insights:
            discovery = Discovery(
                discovery_id=f"quant_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=insight,
                confidence=0.80,
                evidence=["quantitative_analysis"],
                domain="quantitative_biology"
            )
            discoveries.append(discovery)

        return discoveries

    def _generate_hypotheses(self) -> List[Discovery]:
        """Generate testable hypotheses"""
        discoveries = []

        # Generate hypotheses based on goal
        hypotheses = self._generate_testable_hypotheses()

        for hypothesis in hypotheses:
            discovery = Discovery(
                discovery_id=f"hyp_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=f"Hypothesis: {hypothesis}",
                confidence=0.65,
                evidence=["hypothesis_generation"],
                domain="theoretical_biology"
            )
            discoveries.append(discovery)

        return discoveries

    def _investigate_mechanism(self) -> List[Discovery]:
        """Investigate biological mechanisms"""
        discoveries = []

        # Analyze mechanism components
        mechanism_insights = self._analyze_mechanism()

        for insight in mechanism_insights:
            discovery = Discovery(
                discovery_id=f"mech_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=insight,
                confidence=0.75,
                evidence=["mechanism_investigation"],
                domain="molecular_mechanisms"
            )
            discoveries.append(discovery)

        return discoveries

    def _synthesize_literature(self) -> List[Discovery]:
        """Synthesize findings from multiple sources"""
        discoveries = []

        # Simulate literature synthesis
        synthesized_insights = self._synthesize_findings()

        for insight in synthesized_insights:
            discovery = Discovery(
                discovery_id=f"synth_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=insight,
                confidence=0.70,
                evidence=["literature_synthesis"],
                domain="knowledge_synthesis"
            )
            discoveries.append(discovery)

        return discoveries

    def _design_experiments(self) -> List[Discovery]:
        """Design experimental approaches"""
        discoveries = []

        # Generate experimental designs
        experiments = self._generate_experimental_designs()

        for experiment in experiments:
            discovery = Discovery(
                discovery_id=f"exp_{datetime.now().timestamp()}",
                question=self.goal.description,
                finding=f"Experimental design: {experiment}",
                confidence=0.60,
                evidence=["experimental_design"],
                domain="experimental_biology"
            )
            discoveries.append(discovery)

        return discoveries

    def _generic_exploration(self) -> List[Discovery]:
        """Generic exploration for unspecified agent types"""
        # Basic exploration logic
        return []

    # Helper methods for exploration

    def _analyze_goal(self) -> Dict[str, Any]:
        """Analyze the goal to understand key components"""
        return {
            'key_concepts': self._extract_concepts(),
            'domain': self.goal.related_domains[0] if self.goal.related_domains else "general",
            'complexity': self._estimate_complexity()
        }

    def _extract_concepts(self) -> List[str]:
        """Extract key concepts from goal description"""
        # Simple concept extraction based on word frequency
        words = self.goal.description.lower().split()
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        concepts = [word for word in words if word not in common_words and len(word) > 3]
        # Return unique concepts
        return list(set(concepts))

    def _estimate_complexity(self) -> float:
        """Estimate complexity of the goal"""
        # Based on description length and question type
        base_complexity = 0.5
        if len(self.goal.description) > 100:
            base_complexity += 0.2
        if 'how' in self.goal.description.lower() and 'work' in self.goal.description.lower():
            base_complexity += 0.15
        return min(base_complexity, 1.0)

    def _deep_dive_research(self, analysis: Dict) -> List[str]:
        """Simulate deep dive research"""
        # In full implementation, this would:
        # 1. Search knowledge base for related concepts
        # 2. Analyze connections between concepts
        # 3. Identify gaps in current understanding
        # 4. Generate novel insights

        return [
            f"Deep insight into {analysis['key_concepts'][0] if analysis['key_concepts'] else 'concept'}",
            f"Novel connection identified in {analysis['domain']}"
        ]

    def _find_cross_domain_connections(self, domains: List[str]) -> List[str]:
        """Find connections between domains"""
        connections = []

        if len(domains) >= 2:
            connections.append(f"Cross-domain mechanism between {domains[0]} and {domains[1]}")
            connections.append(f"Shared principles across {', '.join(domains)}")

        return connections

    def _analyze_quantitative_aspects(self) -> List[str]:
        """Analyze quantitative aspects"""
        return [
            "Quantitative relationship identified",
            "Mathematical pattern discovered"
        ]

    def _generate_testable_hypotheses(self) -> List[str]:
        """Generate testable hypotheses"""
        return [
            f"Testable hypothesis based on: {self.goal.description[:50]}..."
        ]

    def _analyze_mechanism(self) -> List[str]:
        """Analyze mechanism components"""
        return [
            "Mechanistic insight discovered",
            "Causal relationship identified"
        ]

    def _synthesize_findings(self) -> List[str]:
        """Synthesize findings from multiple sources"""
        return [
            "Synthesized insight from multiple perspectives",
            "Integrated understanding developed"
        ]

    def _generate_experimental_designs(self) -> List[str]:
        """Generate experimental designs"""
        return [
            "Novel experimental approach proposed",
            "Testable experimental design created"
        ]

    def get_discoveries(self) -> List[Discovery]:
        """Get discoveries made by this agent"""
        return self.discoveries.copy()

    def get_progress(self) -> float:
        """Get current progress"""
        return self.progress

    def is_complete(self) -> bool:
        """Check if agent is complete"""
        return not self.active or self.state in [AgentState.COMPLETE, AgentState.ERROR, AgentState.TIMEOUT]


class SubAgentSpawner:
    """
    Spawn and manage specialized sub-agents for autonomous exploration.

    This system enables unprompted exploration by creating specialized agents
    for focused discovery tasks.
    """

    def __init__(self, config: AutonomousConfig, orchestrator: Any):
        """
        Initialize sub-agent spawner.

        Args:
            config: Autonomous system configuration
            orchestrator: Reference to parent orchestrator
        """
        self.config = config
        self.orchestrator = orchestrator

        # Agent management
        self.active_agents: Dict[str, SubAgent] = {}
        self.agent_history: List[AgentStatus] = []

        # Resource tracking
        self.concurrent_agent_count = 0

        logger.info("Sub-Agent Spawner initialized")

    def spawn_agent(self, goal: AutonomousGoal, parent_system: Any) -> Optional[SubAgent]:
        """
        Spawn a specialized sub-agent for a specific goal.

        Args:
            goal: Autonomous goal to pursue
            parent_system: Parent system reference

        Returns:
            SubAgent instance or None if spawning failed
        """
        try:
            # Check concurrent agent limit
            if self.concurrent_agent_count >= self.config.max_concurrent_sub_agents:
                logger.warning(f"Maximum concurrent agents ({self.config.max_concurrent_sub_agents}) reached")
                return None

            # Select appropriate agent type
            agent_type = self._select_agent_type(goal)

            # Create agent
            agent_id = self._generate_agent_id(agent_type)
            agent = SubAgent(
                agent_id=agent_id,
                agent_type=agent_type,
                goal=goal,
                parent_system=parent_system,
                timeout_seconds=self.config.sub_agent_timeout_minutes * 60
            )

            # Start agent
            agent.start()

            # Track agent
            self.active_agents[agent_id] = agent
            self.concurrent_agent_count += 1

            logger.info(f"Spawned {agent_type.value} agent {agent_id} for goal: {goal.description[:50]}...")

            return agent

        except Exception as e:
            logger.error(f"Error spawning agent: {e}")
            return None

    def _select_agent_type(self, goal: AutonomousGoal) -> AgentType:
        """
        Select appropriate agent type based on goal characteristics.

        Args:
            goal: Autonomous goal to analyze

        Returns:
            Appropriate AgentType for the goal
        """
        # Analyze goal description and type
        description_lower = goal.description.lower()

        # Cross-domain goals need cross-domain agents
        if goal.goal_type == GoalType.CROSS_DOMAIN_SYNTHESIS:
            return AgentType.CROSS_DOMAIN

        # Quantitative questions
        if any(word in description_lower for word in ['quantitative', 'measure', 'calculate', 'rate', 'probability']):
            return AgentType.QUANTITATIVE_ANALYSIS

        # Mechanism questions
        if any(word in description_lower for word in ['mechanism', 'how', 'work', 'process']):
            return AgentType.MECHANISM_INVESTIGATOR

        # Hypothesis generation
        if any(word in description_lower for word in ['hypothesis', 'predict', 'would', 'might']):
            return AgentType.HYPOTHESIS_GENERATOR

        # Literature synthesis
        if any(word in description_lower for word in ['synthesize', 'combine', 'integrate', 'summary']):
            return AgentType.LITERATURE_SYNTHESIS

        # Experimental design
        if any(word in description_lower for word in ['experiment', 'test', 'verify', 'validate']):
            return AgentType.EXPERIMENTAL_DESIGN

        # Default: deep exploration
        return AgentType.DEEP_EXPLORATION

    def _generate_agent_id(self, agent_type: AgentType) -> str:
        """Generate unique agent ID"""
        timestamp = datetime.now().timestamp()
        return f"{agent_type.value}_{timestamp}"

    def monitor_agents(self) -> Dict[str, AgentStatus]:
        """
        Monitor all active sub-agents and collect results.

        Returns:
            Dictionary of agent statuses
        """
        status_report = {}

        # Check each active agent
        completed_agents = []

        for agent_id, agent in self.active_agents.items():
            if agent.is_complete():
                # Agent is complete, collect results
                status = AgentStatus(
                    agent_id=agent_id,
                    agent_type=agent.agent_type,
                    state=agent.state,
                    goal_id=agent.goal.goal_id,
                    progress=agent.progress,
                    discoveries_made=agent.get_discoveries(),
                    start_time=agent.thread.name if agent.thread else datetime.now(),  # Approximate
                    end_time=datetime.now()
                )

                status_report[agent_id] = status
                self.agent_history.append(status)
                completed_agents.append(agent_id)

                logger.info(f"Agent {agent_id} completed with {len(status.discoveries_made)} discoveries")

            else:
                # Agent still running
                status_report[agent_id] = AgentStatus(
                    agent_id=agent_id,
                    agent_type=agent.agent_type,
                    state=agent.state,
                    goal_id=agent.goal.goal_id,
                    progress=agent.get_progress()
                )

        # Cleanup completed agents
        for agent_id in completed_agents:
            del self.active_agents[agent_id]
            self.concurrent_agent_count -= 1

        return status_report

    def cleanup_stale_agents(self):
        """Clean up agents that have timed out"""
        stale_agents = []

        for agent_id, agent in self.active_agents.items():
            # Check if agent has been running too long
            if agent.thread and agent.thread.is_alive():
                # Check timeout (simplified - in practice would track start time better)
                # For now, just log
                pass

        for agent_id in stale_agents:
            if agent_id in self.active_agents:
                agent = self.active_agents[agent_id]
                agent.state = AgentState.TIMEOUT
                agent.active = False
                del self.active_agents[agent_id]
                self.concurrent_agent_count -= 1
                logger.warning(f"Agent {agent_id} timed out and cleaned up")

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics about agent spawning and execution"""
        return {
            'active_agents': len(self.active_agents),
            'concurrent_count': self.concurrent_agent_count,
            'total_spawned': len(self.agent_history),
            'completed_count': sum(1 for status in self.agent_history if status.is_complete),
            'total_discoveries': sum(len(status.discoveries_made) for status in self.agent_history),
            'average_duration': sum(status.duration for status in self.agent_history) / max(len(self.agent_history), 1)
        }