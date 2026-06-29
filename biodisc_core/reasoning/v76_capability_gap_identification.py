"""
V76 Scientific Capability Gap Identification System

Systematically identifies gaps in BIODISC's scientific capabilities and prioritizes
development targets based on scientific impact and feasibility.

CAPABILITIES:
- Comprehensive capability mapping and cataloging
- Gap detection across scientific research workflows
- Feasibility and impact analysis for development targets
- Dependency mapping and prerequisite identification
- Development priority optimization
- Capability synergy analysis

SAFEGUARDS:
- Conservative feasibility estimates to avoid over-promising
- Human validation required for major capability decisions
- Resource constraints respected in planning
- Backward compatibility maintained

Date: 2026-06-29
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import logging
import json
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ScientificActivity(Enum):
    """Categories of scientific activities"""
    EXPERIMENTAL_DESIGN = "experimental_design"
    DATA_COLLECTION = "data_collection"
    DATA_ANALYSIS = "data_analysis"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    LITERATURE_REVIEW = "literature_review"
    COMPUTATIONAL_MODELING = "computational_modeling"
    EXPERIMENTAL_VALIDATION = "experimental_validation"
    SCIENTIFIC_COMMUNICATION = "scientific_communication"
    PEER_REVIEW = "peer_review"
    RESEARCH_PLANNING = "research_planning"
    PARADIGM_ANALYSIS = "paradigm_analysis"
    META_SCIENTIFIC_REASONING = "meta_scientific_reasoning"

class DevelopmentComplexity(Enum):
    """Complexity levels for capability development"""
    TRIVIAL = "trivial"  # < 1 day, straightforward
    SIMPLE = "simple"    # 1-3 days, clear requirements
    MODERATE = "moderate"  # 1-2 weeks, some complexity
    COMPLEX = "complex"    # 2-4 weeks, significant complexity
    VERY_COMPLEX = "very_complex"  # 1-3 months, highly complex
    RESEARCH_REQUIRED = "research_required"  # 3+ months, requires novel research

class ImpactLevel(Enum):
    """Scientific impact levels"""
    MINIMAL = "minimal"  # Minor capability enhancement
    LOW = "low"  # Small but meaningful improvement
    MODERATE = "moderate"  # Significant capability addition
    HIGH = "high"  # Major capability enhancement
    TRANSFORMATIONAL = "transformational"  # Revolutionary new capability

@dataclass
class CurrentCapability:
    """Description of existing capability"""
    capability_id: str
    name: str
    description: str
    version: str
    implemented_date: datetime
    scientific_activities: List[ScientificActivity]
    dependencies: List[str]  # Other capabilities this depends on
    dependents: List[str]  # Capabilities that depend on this one
    reliability: float  # 0.0-1.0 scale
    performance_score: float  # 0.0-1.0 scale
    usage_frequency: str  # HIGH, MEDIUM, LOW
    limitations: List[str]
    enhancement_potential: float  # 0.0-1.0 scale

@dataclass
class CapabilityGap:
    """Identified gap in scientific capability"""
    gap_id: str
    target_activity: ScientificActivity
    missing_capability: str
    description: str
    scientific_justification: str
    impact_level: ImpactLevel
    development_complexity: DevelopmentComplexity
    estimated_effort_weeks: float
    dependencies: List[str]  # Prerequisites that must exist first
    blockers: List[str]  # Things preventing development
    scientific_value_score: float  # 0.0-1.0
    development_feasibility: float  # 0.0-1.0
    priority_score: float  # 0.0-1.0
    alternative_approaches: List[str]
    risk_factors: List[str]

@dataclass
class CapabilityDependency:
    """Dependency relationship between capabilities"""
    prerequisite_id: str
    dependent_id: str
    dependency_type: str  # HARD, SOFT, OPTIONAL
    justification: str
    strength: float  # 0.0-1.0 scale

@dataclass
class DevelopmentPriority:
    """Prioritized development target"""
    rank: int
    gap: CapabilityGap
    expected_agency_enhancement: float  # 0.0-1.0
    resource_requirements: Dict[str, Any]
    development_timeline: str  # IMMEDIATE, SHORT_TERM, MEDIUM_TERM, LONG_TERM
    success_probability: float  # 0.0-1.0
    roi_score: float  # 0.0-1.0  # Return on investment
    synergies: List[str]  # Other capabilities this synergizes with

class CapabilityGapIdentifier:
    """
    Systematic identification and analysis of capability gaps for
    autonomous scientific capability development.
    """

    def __init__(self):
        self.current_capabilities: Dict[str, CurrentCapability] = {}
        self.capability_gaps: List[CapabilityGap] = []
        self.dependency_graph: Dict[str, List[CapabilityDependency]] = {}
        self.development_priorities: List[DevelopmentPriority] = []
        self.analysis_history: List[Dict] = []

        logger.info("Capability Gap Identifier initialized")

    def map_current_capabilities(self) -> Dict[str, CurrentCapability]:
        """
        Create comprehensive map of all current scientific capabilities.
        """
        logger.info("Mapping current BIODISC capabilities...")

        # Define existing capabilities based on current BIODISC architecture
        capabilities = {
            # V4.0 Revolutionary Capabilities
            "v4_mce": CurrentCapability(
                capability_id="v4_mce",
                name="Meta-Context Engine",
                description="Multi-dimensional context layering and cognitive frame analysis",
                version="4.0",
                implemented_date=datetime(2025, 1, 15),
                scientific_activities=[ScientificActivity.COMPUTATIONAL_MODELING, ScientificActivity.RESEARCH_PLANNING],
                dependencies=[],
                dependents=["v73_curiosity", "v75_meta_analysis"],
                reliability=0.85,
                performance_score=0.80,
                usage_frequency="MEDIUM",
                limitations=["Cannot handle more than 5 dimensions simultaneously", "Limited to predefined cognitive frames"],
                enhancement_potential=0.70
            ),

            "v4_asc": CurrentCapability(
                capability_id="v4_asc",
                name="Autocatalytic Self-Compiler",
                description="Self-modifying code generation and optimization",
                version="4.0",
                implemented_date=datetime(2025, 1, 15),
                scientific_activities=[ScientificActivity.COMPUTATIONAL_MODELING],
                dependencies=["v4_mce"],
                dependents=["v78_implementation"],
                reliability=0.75,
                performance_score=0.70,
                usage_frequency="LOW",
                limitations=["Limited to Python code generation", "Cannot handle complex refactoring"],
                enhancement_potential=0.85
            ),

            # V61-V63 Meta-Learning
            "v61_expert_feedback": CurrentCapability(
                capability_id="v61_expert_feedback",
                name="Expert Feedback Pattern Extractor",
                description="Learn patterns from domain expert feedback",
                version="1.0",
                implemented_date=datetime(2026, 4, 20),
                scientific_activities=[ScientificActivity.META_SCIENTIFIC_REASONING],
                dependencies=[],
                dependents=["v63_meta_learning"],
                reliability=0.80,
                performance_score=0.75,
                usage_frequency="MEDIUM",
                limitations=["Requires labeled feedback data", "Limited to specific domains"],
                enhancement_potential=0.65
            ),

            "v62_domain_verifier": CurrentCapability(
                capability_id="v62_domain_verifier",
                name="Domain Artifact Verifier",
                description="Verify biological claims against domain knowledge",
                version="1.0",
                implemented_date=datetime(2026, 4, 20),
                scientific_activities=[ScientificActivity.DATA_ANALYSIS, ScientificActivity.HYPOTHESIS_GENERATION],
                dependencies=["v61_expert_feedback"],
                dependents=["v74_genuine_filter"],
                reliability=0.85,
                performance_score=0.80,
                usage_frequency="HIGH",
                limitations=["Limited to predefined domain knowledge", "Cannot handle novel biological concepts"],
                enhancement_potential=0.70
            ),

            # V73-V74 Autonomous Discovery
            "v73_curiosity": CurrentCapability(
                capability_id="v73_curiosity",
                name="Curiosity Engine",
                description="Generate curiosity-driven questions from knowledge gaps",
                version="2.0",
                implemented_date=datetime(2026, 4, 26),
                scientific_activities=[ScientificActivity.RESEARCH_PLANNING, ScientificActivity.HYPOTHESIS_GENERATION],
                dependencies=["v4_mce", "v66_absence_detection"],
                dependents=["v73_autonomous_orchestrator"],
                reliability=0.90,
                performance_score=0.85,
                usage_frequency="HIGH",
                limitations=["Limited to existing knowledge base", "Cannot identify truly novel questions"],
                enhancement_potential=0.80
            ),

            "v74_genuine_filter": CurrentCapability(
                capability_id="v74_genuine_filter",
                name="Genuine Discovery Filter",
                description="Distinguish genuine discoveries from literature summaries",
                version="1.0",
                implemented_date=datetime(2026, 6, 29),
                scientific_activities=[ScientificActivity.HYPOTHESIS_GENERATION, ScientificActivity.DATA_ANALYSIS],
                dependencies=["v62_domain_verifier", "v73_curiosity"],
                dependents=[],
                reliability=0.85,
                performance_score=0.80,
                usage_frequency="HIGH",
                limitations=["Limited to predefined contribution types", "Cannot assess true novelty"],
                enhancement_potential=0.75
            ),

            # V75 Meta-Scientific Analysis
            "v75_meta_analysis": CurrentCapability(
                capability_id="v75_meta_analysis",
                name="Meta-Scientific Analysis Engine",
                description="Analyze scientific capabilities and limitations from meta-perspective",
                version="1.0",
                implemented_date=datetime(2026, 6, 29),
                scientific_activities=[ScientificActivity.META_SCIENTIFIC_REASONING, ScientificActivity.PARADIGM_ANALYSIS],
                dependencies=[],
                dependents=[],
                reliability=0.90,
                performance_score=0.85,
                usage_frequency="MEDIUM",
                limitations=["Cannot question fundamental paradigms", "Limited to current conceptual frameworks"],
                enhancement_potential=0.90
            ),

            # Analysis Modules
            "computational_biology_analyzer": CurrentCapability(
                capability_id="computational_biology_analyzer",
                name="Computational Biology Analyzer",
                description="Perform computational analysis on biological data",
                version="1.0",
                implemented_date=datetime(2026, 6, 29),
                scientific_activities=[ScientificActivity.DATA_ANALYSIS, ScientificActivity.COMPUTATIONAL_MODELING],
                dependencies=[],
                dependents=["v74_genuine_filter"],
                reliability=0.80,
                performance_score=0.75,
                usage_frequency="MEDIUM",
                limitations=["Limited to predefined data sources", "Cannot handle novel data types"],
                enhancement_potential=0.80
            ),

            "cross_domain_synthesis": CurrentCapability(
                capability_id="cross_domain_synthesis",
                name="Cross-Domain Synthesis Engine",
                description="Synthesize insights across biological domains",
                version="1.0",
                implemented_date=datetime(2026, 6, 29),
                scientific_activities=[ScientificActivity.HYPOTHESIS_GENERATION, ScientificActivity.DATA_ANALYSIS],
                dependencies=["computational_biology_analyzer"],
                dependents=["v74_genuine_filter"],
                reliability=0.75,
                performance_score=0.70,
                usage_frequency="MEDIUM",
                limitations=["Limited to predefined domain mappings", "Cannot discover novel domain connections"],
                enhancement_potential=0.85
            ),

            "insight_generator": CurrentCapability(
                capability_id="insight_generator",
                name="Original Insight Generator",
                description="Generate mechanistic hypotheses and predictions",
                version="1.0",
                implemented_date=datetime(2026, 6, 29),
                scientific_activities=[ScientificActivity.HYPOTHESIS_GENERATION, ScientificActivity.EXPERIMENTAL_DESIGN],
                dependencies=[],
                dependents=["v74_genuine_filter"],
                reliability=0.70,
                performance_score=0.65,
                usage_frequency="MEDIUM",
                limitations=["Limited to predefined mechanistic patterns", "Cannot generate truly novel insights"],
                enhancement_potential=0.90
            )
        }

        self.current_capabilities = capabilities

        logger.info(f"Mapped {len(capabilities)} current capabilities")
        for cap_id, cap in capabilities.items():
            logger.info(f"  - {cap.name}: {len(cap.scientific_activities)} activities, reliability {cap.reliability:.1%}")

        return capabilities

    def identify_capability_gaps(self) -> List[CapabilityGap]:
        """
        Systematically identify gaps in scientific capability coverage.
        """
        logger.info("Identifying capability gaps across scientific activities...")

        gaps = []

        # Define gaps based on missing capabilities for key scientific activities
        gaps.extend(self._identify_experimental_gaps())
        gaps.extend(self._identify_literature_gaps())
        gaps.extend(self._identify_communication_gaps())
        gaps.extend(self._identify_validation_gaps())
        gaps.extend(self._identify_paradigm_gaps())

        self.capability_gaps = gaps

        logger.info(f"Identified {len(gaps)} capability gaps:")
        for gap in gaps:
            logger.info(f"  [{gap.impact_level.value}] {gap.target_activity.value}: {gap.missing_capability}")

        return gaps

    def _identify_experimental_gaps(self) -> List[CapabilityGap]:
        """Identify gaps in experimental capabilities"""
        return [
            CapabilityGap(
                gap_id="gap_experimental_design_automation",
                target_activity=ScientificActivity.EXPERIMENTAL_DESIGN,
                missing_capability="Automated Experimental Design System",
                description="Cannot autonomously design complex biological experiments",
                scientific_justification="Essential for empirical validation of computational predictions",
                impact_level=ImpactLevel.HIGH,
                development_complexity=DevelopmentComplexity.VERY_COMPLEX,
                estimated_effort_weeks=8.0,
                dependencies=["insight_generator"],
                blockers=["No physical lab interface", "Limited biological domain knowledge"],
                scientific_value_score=0.85,
                development_feasibility=0.40,
                priority_score=0.75,
                alternative_approaches=[
                    "Generate experimental protocols for human execution",
                    "Interface with lab automation systems",
                    "Focus on computational validation instead"
                ],
                risk_factors=["High complexity", "External dependencies", "Safety concerns"]
            ),

            CapabilityGap(
                gap_id="gap_protocol_generation",
                target_activity=ScientificActivity.EXPERIMENTAL_DESIGN,
                missing_capability="Detailed Protocol Generation",
                description="Cannot generate detailed, executable experimental protocols",
                scientific_justification="Required for translating hypotheses into testable experiments",
                impact_level=ImpactLevel.MODERATE,
                development_complexity=DevelopmentComplexity.COMPLEX,
                estimated_effort_weeks=4.0,
                dependencies=["insight_generator"],
                blockers=["Limited protocol template library"],
                scientific_value_score=0.75,
                development_feasibility=0.70,
                priority_score=0.72,
                alternative_approaches=[
                    "Use template-based protocol generation",
                    "Integrate with existing protocol databases",
                    "Focus on high-level design only"
                ],
                risk_factors=["Protocol accuracy", "Safety validation"]
            )
        ]

    def _identify_literature_gaps(self) -> List[CapabilityGap]:
        """Identify gaps in literature access and analysis"""
        return [
            CapabilityGap(
                gap_id="gap_literature_database_access",
                target_activity=ScientificActivity.LITERATURE_REVIEW,
                missing_capability="Independent Literature Database Access",
                description="Cannot access scientific databases autonomously",
                scientific_justification="Essential for staying current with scientific knowledge",
                impact_level=ImpactLevel.TRANSFORMATIONAL,
                development_complexity=DevelopmentComplexity.MODERATE,
                estimated_effort_weeks=3.0,
                dependencies=[],
                blockers=["API access limitations", "Subscription requirements"],
                scientific_value_score=0.90,
                development_feasibility=0.60,
                priority_score=0.80,
                alternative_approaches=[
                    "Use open-access databases only",
                    "Implement delayed literature updates",
                    "Rely on human-provided literature"
                ],
                risk_factors=["API rate limits", "Copyright restrictions", "Data quality"]
            ),

            CapabilityGap(
                gap_id="gap_literature_synthesis",
                target_activity=ScientificActivity.LITERATURE_REVIEW,
                missing_capability="Advanced Literature Synthesis",
                description="Cannot perform sophisticated literature analysis and synthesis",
                scientific_justification="Critical for identifying research gaps and opportunities",
                impact_level=ImpactLevel.HIGH,
                development_complexity=DevelopmentComplexity.COMPLEX,
                estimated_effort_weeks=6.0,
                dependencies=["gap_literature_database_access"],
                blockers=["Limited natural language understanding"],
                scientific_value_score=0.80,
                development_feasibility=0.65,
                priority_score=0.74,
                alternative_approaches=[
                    "Focus on citation network analysis",
                    "Use template-based synthesis",
                    "Implement basic summarization only"
                ],
                risk_factors=["Analysis accuracy", "Information overload"]
            )
        ]

    def _identify_communication_gaps(self) -> List[CapabilityGap]:
        """Identify gaps in scientific communication"""
        return [
            CapabilityGap(
                gap_id="gap_publication_generation",
                target_activity=ScientificActivity.SCIENTIFIC_COMMUNICATION,
                missing_capability="Automated Publication Generation",
                description="Cannot generate publication-ready scientific manuscripts",
                scientific_justification="Essential for contributing to scientific discourse",
                impact_level=ImpactLevel.HIGH,
                development_complexity=DevelopmentComplexity.COMPLEX,
                estimated_effort_weeks=5.0,
                dependencies=["v74_genuine_filter", "gap_literature_database_access"],
                blockers=["Limited writing style adaptation", "Figure generation"],
                scientific_value_score=0.85,
                development_feasibility=0.70,
                priority_score=0.79,
                alternative_approaches=[
                    "Generate manuscript drafts for human editing",
                    "Focus on specific sections (methods, results)",
                    "Use template-based writing"
                ],
                risk_factors=["Writing quality", "Journal compliance"]
            ),

            CapabilityGap(
                gap_id="gap_peer_review_response",
                target_activity=ScientificActivity.PEER_REVIEW,
                missing_capability="Peer Review Response Generation",
                description="Cannot formulate responses to peer review comments",
                scientific_justification="Critical for publication success and scientific dialogue",
                impact_level=ImpactLevel.MODERATE,
                development_complexity=DevelopmentComplexity.MODERATE,
                estimated_effort_weeks=3.0,
                dependencies=["gap_publication_generation"],
                blockers=["Limited argumentation capabilities"],
                scientific_value_score=0.70,
                development_feasibility=0.75,
                priority_score=0.72,
                alternative_approaches=[
                    "Generate response drafts for human editing",
                    "Focus on technical point-by-point responses",
                    "Provide revision suggestions only"
                ],
                risk_factors=["Response appropriateness", "Scientific accuracy"]
            )
        ]

    def _identify_validation_gaps(self) -> List[CapabilityGap]:
        """Identify gaps in experimental validation"""
        return [
            CapabilityGap(
                gap_id="gap_experimental_validation_interface",
                target_activity=ScientificActivity.EXPERIMENTAL_VALIDATION,
                missing_capability="Experimental Validation Interface",
                description="Cannot interface with experimental systems for validation",
                scientific_justification="Required for empirical validation of computational predictions",
                impact_level=ImpactLevel.TRANSFORMATIONAL,
                development_complexity=DevelopmentComplexity.RESEARCH_REQUIRED,
                estimated_effort_weeks=16.0,
                dependencies=["gap_experimental_design_automation"],
                blockers=["No physical world interface", "Lab integration complexity"],
                scientific_value_score=0.95,
                development_feasibility=0.20,
                priority_score=0.70,
                alternative_approaches=[
                    "Generate validation protocols for human execution",
                    "Focus on computational validation",
                    "Partner with wet lab facilities"
                ],
                risk_factors=["Technical feasibility", "Resource requirements", "Safety"]
            )
        ]

    def _identify_paradigm_gaps(self) -> List[CapabilityGap]:
        """Identify gaps in paradigm analysis and revision"""
        return [
            CapabilityGap(
                gap_id="gap_paradigm_questioning",
                target_activity=ScientificActivity.PARADIGM_ANALYSIS,
                missing_capability="Fundamental Paradigm Questioning",
                description="Cannot question or revise fundamental scientific paradigms",
                scientific_justification="Essential for revolutionary discoveries and paradigm shifts",
                impact_level=ImpactLevel.TRANSFORMATIONAL,
                development_complexity=DevelopmentComplexity.RESEARCH_REQUIRED,
                estimated_effort_weeks=20.0,
                dependencies=["v75_meta_analysis"],
                blockers=["Conceptual limitations", "Meta-paradigm framework missing"],
                scientific_value_score=0.95,
                development_feasibility=0.25,
                priority_score=0.72,
                alternative_approaches=[
                    "Identify paradigm limitations (cannot revise)",
                    "Suggest paradigm alternatives (cannot implement)",
                    "Multi-paradigm analysis only"
                ],
                risk_factors=["Conceptual difficulty", "Validation challenges", "Scientific acceptance"]
            )
        ]

    def analyze_dependencies(self) -> Dict[str, List[CapabilityDependency]]:
        """
        Analyze dependency relationships between capabilities.
        """
        logger.info("Analyzing capability dependencies...")

        dependency_graph = {}

        # Build dependency graph from current capabilities
        for cap_id, capability in self.current_capabilities.items():
            dependencies = []
            for dep_id in capability.dependencies:
                if dep_id in self.current_capabilities:
                    dependency = CapabilityDependency(
                        prerequisite_id=dep_id,
                        dependent_id=cap_id,
                        dependency_type="HARD",
                        justification=f"{capability.name} requires {self.current_capabilities[dep_id].name}",
                        strength=0.9
                    )
                    dependencies.append(dependency)

            dependency_graph[cap_id] = dependencies

        # Add dependencies for gaps
        for gap in self.capability_gaps:
            dependencies = []
            for dep_id in gap.dependencies:
                dependency = CapabilityDependency(
                    prerequisite_id=dep_id,
                    dependent_id=gap.gap_id,
                    dependency_type="HARD",
                    justification=f"{gap.missing_capability} requires {dep_id}",
                    strength=0.8
                )
                dependencies.append(dependency)

            dependency_graph[gap.gap_id] = dependencies

        self.dependency_graph = dependency_graph

        total_dependencies = sum(len(deps) for deps in dependency_graph.values())
        logger.info(f"Analyzed {total_dependencies} dependency relationships")

        return dependency_graph

    def prioritize_development_targets(self) -> List[DevelopmentPriority]:
        """
        Prioritize capability gaps for development based on multiple criteria.
        """
        logger.info("Prioritizing capability development targets...")

        priorities = []

        for rank, gap in enumerate(self.capability_gaps, 1):
            # Calculate expected agency enhancement
            expected_agency_gain = self._calculate_agency_enhancement(gap)

            # Determine development timeline
            if gap.priority_score > 0.75 and gap.development_feasibility > 0.6:
                timeline = "IMMEDIATE"
            elif gap.priority_score > 0.65:
                timeline = "SHORT_TERM"
            elif gap.priority_score > 0.55:
                timeline = "MEDIUM_TERM"
            else:
                timeline = "LONG_TERM"

            # Calculate success probability
            success_prob = gap.development_feasibility * (1.0 - (gap.estimated_effort_weeks / 52.0) * 0.3)

            # Calculate ROI (return on investment)
            roi_score = (gap.scientific_value_score * expected_agency_gain) / (gap.estimated_effort_weeks / 4.0)

            # Identify synergies
            synergies = self._identify_synergies(gap)

            # Resource requirements
            resource_requirements = {
                "development_weeks": gap.estimated_effort_weeks,
                "compute_intensity": "HIGH" if gap.impact_level in [ImpactLevel.HIGH, ImpactLevel.TRANSFORMATIONAL] else "MEDIUM",
                "dependencies_count": len(gap.dependencies),
                "blockers_count": len(gap.blockers)
            }

            priority = DevelopmentPriority(
                rank=rank,
                gap=gap,
                expected_agency_enhancement=expected_agency_gain,
                resource_requirements=resource_requirements,
                development_timeline=timeline,
                success_probability=success_prob,
                roi_score=roi_score,
                synergies=synergies
            )

            priorities.append(priority)

        # Sort by priority score (higher is better)
        priorities.sort(key=lambda p: (p.gap.priority_score, p.roi_score), reverse=True)

        # Reassign ranks after sorting
        for i, priority in enumerate(priorities, 1):
            priority.rank = i

        self.development_priorities = priorities

        logger.info(f"Prioritized {len(priorities)} development targets")
        for priority in priorities[:5]:
            logger.info(f"  {priority.rank}. {priority.gap.missing_capability} (priority: {priority.gap.priority_score:.2f})")

        return priorities

    def _calculate_agency_enhancement(self, gap: CapabilityGap) -> float:
        """Calculate expected agency enhancement from closing this gap."""
        # Base enhancement from impact level
        impact_multiplier = {
            ImpactLevel.MINIMAL: 0.02,
            ImpactLevel.LOW: 0.05,
            ImpactLevel.MODERATE: 0.10,
            ImpactLevel.HIGH: 0.15,
            ImpactLevel.TRANSFORMATIONAL: 0.20
        }

        base_enhancement = impact_multiplier.get(gap.impact_level, 0.10)

        # Adjust by feasibility and success probability
        feasibility_factor = gap.development_feasibility * 0.8

        return base_enhancement * feasibility_factor

    def _identify_synergies(self, gap: CapabilityGap) -> List[str]:
        """Identify other capabilities that would synergize with this gap."""
        synergies = []

        # Activity-based synergies
        activity_synergies = {
            ScientificActivity.EXPERIMENTAL_DESIGN: ["protocol_generation", "experimental_validation_interface"],
            ScientificActivity.LITERATURE_REVIEW: ["literature_synthesis", "hypothesis_generation"],
            ScientificActivity.SCIENTIFIC_COMMUNICATION: ["publication_generation", "peer_review_response"],
            ScientificActivity.PARADIGM_ANALYSIS: ["meta_scientific_reasoning", "paradigm_questioning"]
        }

        potential_synergies = activity_synergies.get(gap.target_activity, [])
        for syn_gap in self.capability_gaps:
            if syn_gap.gap_id in potential_synergies:
                synergies.append(syn_gap.gap_id)

        return synergies

    def generate_capability_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive capability analysis report.
        """
        logger.info("Generating comprehensive capability analysis report...")

        # Ensure all analyses are complete
        if not self.current_capabilities:
            self.map_current_capabilities()
        if not self.capability_gaps:
            self.capability_gaps = self.identify_capability_gaps()
        if not self.dependency_graph:
            self.dependency_graph = self.analyze_dependencies()
        if not self.development_priorities:
            self.development_priorities = self.prioritize_development_targets()

        report = {
            "report_id": f"capability_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generation_date": datetime.now().isoformat(),
            "summary": {
                "total_capabilities": len(self.current_capabilities),
                "total_gaps_identified": len(self.capability_gaps),
                "high_priority_gaps": len([g for g in self.capability_gaps if g.priority_score > 0.7]),
                "total_dependencies": sum(len(deps) for deps in self.dependency_graph.values()),
                "average_reliability": sum(c.reliability for c in self.current_capabilities.values()) / len(self.current_capabilities),
                "enhancement_potential": sum(c.enhancement_potential for c in self.current_capabilities.values()) / len(self.current_capabilities)
            },
            "current_capabilities": {
                cap_id: {
                    "name": cap.name,
                    "activities": [a.value for a in cap.scientific_activities],
                    "reliability": cap.reliability,
                    "enhancement_potential": cap.enhancement_potential,
                    "usage_frequency": cap.usage_frequency
                }
                for cap_id, cap in self.current_capabilities.items()
            },
            "capability_gaps": {
                gap.gap_id: {
                    "activity": gap.target_activity.value,
                    "missing_capability": gap.missing_capability,
                    "impact_level": gap.impact_level.value,
                    "complexity": gap.development_complexity.value,
                    "priority_score": gap.priority_score,
                    "scientific_value": gap.scientific_value_score,
                    "feasibility": gap.development_feasibility
                }
                for gap in self.capability_gaps
            },
            "development_priorities": [
                {
                    "rank": p.rank,
                    "capability": p.gap.missing_capability,
                    "priority_score": p.gap.priority_score,
                    "agency_enhancement": p.expected_agency_enhancement,
                    "timeline": p.development_timeline,
                    "success_probability": p.success_probability,
                    "roi": p.roi_score
                }
                for p in self.development_priorities
            ],
            "recommendations": self._generate_recommendations()
        }

        logger.info(f"Capability analysis report generated: {len(report['development_priorities'])} priorities")

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate development recommendations based on analysis."""
        recommendations = []

        # High-priority immediate developments
        immediate_priorities = [p for p in self.development_priorities if p.development_timeline == "IMMEDIATE"]
        if immediate_priorities:
            recommendations.append(f"Focus on {len(immediate_priorities)} immediate priority capabilities")

        # Dependency chains
        recommendations.append("Address dependency chains to enable parallel development")

        # High-ROI opportunities
        high_roi = [p for p in self.development_priorities if p.roi_score > 0.15]
        if high_roi:
            recommendations.append(f"Prioritize {len(high_roi)} high-ROI capabilities for maximum agency growth")

        # Feasibility concerns
        low_feasibility = [g for g in self.capability_gaps if g.development_feasibility < 0.4]
        if low_feasibility:
            recommendations.append(f"Address {len(low_feasibility)} high-risk capabilities through alternative approaches")

        # Enhancement opportunities
        high_enhancement = [c for c in self.current_capabilities.values() if c.enhancement_potential > 0.8]
        if high_enhancement:
            recommendations.append(f"Enhance {len(high_enhancement)} existing capabilities with high improvement potential")

        return recommendations

# Factory function for creating capability gap identifier
def create_capability_gap_identifier() -> CapabilityGapIdentifier:
    """Create and initialize capability gap identifier."""
    identifier = CapabilityGapIdentifier()
    return identifier

# Singleton instance
_capability_gap_identifier_instance = None

def get_capability_gap_identifier() -> CapabilityGapIdentifier:
    """Get or create singleton capability gap identifier instance."""
    global _capability_gap_identifier_instance
    if _capability_gap_identifier_instance is None:
        _capability_gap_identifier_instance = create_capability_gap_identifier()
    return _capability_gap_identifier_instance