"""
V80: Experimental Design & Simulation Engine

Generates detailed experimental designs to test novel biological hypotheses.
This capability enables BIODISC to move from hypothesis generation to actionable
experimental protocols for wet-lab validation.

Date: 2026-05-09
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import os
from datetime import datetime


class ExperimentalType(Enum):
    """Types of experimental designs"""
    IN_VITRO = "in_vitro"           # Cell culture experiments
    IN_VIVO = "in_vivo"             # Animal models
    IN_SILICO = "in_silico"         # Computational simulations
    BIOCHEMICAL = "biochemical"     # Purified protein assays
    GENETIC = "genetic"             # Genetic manipulation experiments
    IMAGING = "imaging"             # Microscopy/visualization
    OMICS = "omics"                 # High-throughput assays


class ControlType(Enum):
    """Types of control conditions"""
    NEGATIVE = "negative"           # No treatment, baseline
    POSITIVE = "positive"           # Known effect, validates assay
    VEHICLE = "vehicle"             # Solvent/control substance
    SHAM = "sham"                   # Procedural control
    BLANK = "blank"                 # No biological material
    REFERENCE = "reference"         # Standard comparison


class FeasibilityLevel(Enum):
    """Feasibility of experimental design"""
    HIGH = "high"                   # Routine experiment, widely used
    MEDIUM = "medium"               # Requires expertise but established
    LOW = "low"                     # Cutting-edge, requires specialist
    VERY_LOW = "very_low"           # Theoretical, not yet established
    IMPOSSIBLE = "impossible"       # Cannot be performed with current tech


@dataclass
class ExperimentalVariable:
    """A variable in the experimental design"""
    variable_id: str
    name: str
    type: str                       # independent, dependent, confounding
    description: str
    measurement_method: str
    units: Optional[str] = None
    expected_range: Optional[Tuple[float, float]] = None
    timepoints: Optional[List[float]] = None


@dataclass
class ControlCondition:
    """A control condition in the experiment"""
    control_id: str
    control_type: ControlType
    description: str
    purpose: str
    conditions: Dict[str, Any]


@dataclass
class ExperimentalStep:
    """A single step in the experimental protocol"""
    step_number: int
    title: str
    description: str
    duration_minutes: Optional[float] = None
    required_materials: List[str] = field(default_factory=list)
    required_equipment: List[str] = field(default_factory=list)
    critical_parameters: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class StatisticalPower:
    """Statistical power analysis for the experiment"""
    sample_size: int
    effect_size: float
    power: float                    # Typically 0.8 or higher
    significance_level: float       # Typically 0.05
    statistical_tests: List[str]
    assumptions: List[str]


@dataclass
class ResourceRequirement:
    """Resources needed for the experiment"""
    category: str                   # reagents, equipment, personnel, time
    items: List[str]
    estimated_cost_usd: Optional[float] = None
    availability: Optional[str] = None


@dataclass
class ExperimentalDesign:
    """Complete experimental design for testing a hypothesis"""
    design_id: str
    hypothesis: str
    experimental_type: ExperimentalType
    title: str
    objective: str
    background: str
    variables: List[ExperimentalVariable]
    controls: List[ControlCondition]
    protocol: List[ExperimentalStep]
    expected_outcomes: List[str]
    statistical_analysis: StatisticalPower
    feasibility: FeasibilityLevel
    resources: List[ResourceRequirement]
    timeline_days: int
    risk_assessment: List[str]
    potential_pitfalls: List[str]
    alternative_approaches: List[str]
    generated_at: float
    confidence: float = 0.0


class ExperimentalDesignEngine:
    """
    Generates experimental designs to test novel biological hypotheses.

    CAPABILITIES:
    - Hypothesis operationalization (convert to testable predictions)
    - Experimental variables identification (independent, dependent, confounding)
    - Control condition design (negative, positive, vehicle, sham)
    - Statistical power analysis (sample size, effect size, power)
    - Feasibility checking (against bioinformatics databases)
    - Cost and time estimation
    - Risk assessment and alternative approaches

    WORKFLOW:
    1. Analyze hypothesis to identify testable predictions
    2. Design experimental variables and measurements
    3. Select appropriate experimental type
    4. Design control conditions
    5. Generate step-by-step protocol
    6. Perform statistical power analysis
    7. Check feasibility against databases
    8. Estimate resources and timeline
    9. Assess risks and alternatives
    """

    def __init__(self):
        self.designs: List[ExperimentalDesign] = []
        self._load_design_history()

        # Common experimental materials database
        self._load_materials_database()

    def _load_design_history(self):
        """Load historical experimental designs"""
        try:
            history_path = "/Users/gjw255/.biodisc_persistent/experimental_designs.jsonl"
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            design_dict = json.loads(line)
                            design = self._dict_to_design(design_dict)
                            self.designs.append(design)
        except Exception as e:
            print(f"Error loading design history: {e}")

    def _load_materials_database(self):
        """Load database of common experimental materials and equipment"""
        self.materials_db = {
            "cell_culture": {
                "reagents": ["DMEM", "FBS", "Penicillin-Streptomycin", "Trypsin-EDTA", "PBS"],
                "equipment": ["CO2 incubator", "Biosafety cabinet", "Centrifuge", "Microscope"],
                "typical_cost": 5000
            },
            "protein_biochemistry": {
                "reagents": ["Protein A/G beads", "Lysis buffer", "Protease inhibitors", "SDS-PAGE reagents"],
                "equipment": ["Sonicator", "Centrifuge", "SDS-PAGE apparatus", "Western blot transfer system"],
                "typical_cost": 8000
            },
            "molecular_biology": {
                "reagents": ["PCR primers", "dNTPs", "DNA polymerase", "Agarose", "Restriction enzymes"],
                "equipment": ["Thermocycler", "Gel electrophoresis system", "UV transilluminator"],
                "typical_cost": 6000
            },
            "microscopy": {
                "reagents": ["Fluorescent dyes", "Antibodies", "Mounting medium", "Coverslips"],
                "equipment": ["Confocal microscope", "Fluorescence microscope", "Image analysis software"],
                "typical_cost": 15000
            },
            "omics": {
                "reagents": ["RNA extraction kit", "Library prep kit", "Sequencing reagents"],
                "equipment": ["Sequencer", "Bioanalyzer", "Real-time PCR machine"],
                "typical_cost": 50000
            }
        }

    def design_experiment(self, hypothesis: str, context: Optional[Dict[str, Any]] = None) -> ExperimentalDesign:
        """
        Generate a complete experimental design to test a hypothesis.

        Args:
            hypothesis: The hypothesis to test
            context: Additional context (domain, available resources, constraints)

        Returns:
            Complete experimental design with protocol and analysis
        """
        context = context or {}

        # Generate unique ID
        import hashlib
        hash_input = f"{hypothesis}_{datetime.now().isoformat()}"
        design_id = f"exp_{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"

        # Analyze hypothesis to determine experimental type
        exp_type = self._determine_experimental_type(hypothesis, context)

        # Identify testable predictions
        predictions = self._extract_predictions(hypothesis)

        # Design variables
        variables = self._design_variables(hypothesis, predictions, exp_type)

        # Design controls
        controls = self._design_controls(exp_type, variables)

        # Generate protocol
        protocol = self._generate_protocol(exp_type, hypothesis, variables, controls)

        # Statistical power analysis
        stats = self._perform_power_analysis(variables, protocol)

        # Check feasibility
        feasibility = self._check_feasibility(protocol, context)

        # Resource requirements
        resources = self._estimate_resources(exp_type, protocol, stats.sample_size)

        # Timeline
        timeline = self._estimate_timeline(exp_type, protocol, stats.sample_size)

        # Risk assessment
        risks = self._assess_risks(exp_type, protocol)

        # Potential pitfalls
        pitfalls = self._identify_pitfalls(exp_type, hypothesis, variables)

        # Alternative approaches
        alternatives = self._suggest_alternatives(exp_type, hypothesis)

        # Expected outcomes
        expected = self._predict_outcomes(hypothesis, predictions, variables)

        # Calculate confidence
        confidence = self._calculate_confidence(feasibility, stats, risks)

        design = ExperimentalDesign(
            design_id=design_id,
            hypothesis=hypothesis,
            experimental_type=exp_type,
            title=self._generate_title(hypothesis, exp_type),
            objective=self._generate_objective(hypothesis),
            background=self._generate_background(hypothesis, context),
            variables=variables,
            controls=controls,
            protocol=protocol,
            expected_outcomes=expected,
            statistical_analysis=stats,
            feasibility=feasibility,
            resources=resources,
            timeline_days=timeline,
            risk_assessment=risks,
            potential_pitfalls=pitfalls,
            alternative_approaches=alternatives,
            generated_at=datetime.now().timestamp(),
            confidence=confidence
        )

        # Save design
        self.designs.append(design)
        self._save_design_history(design)

        return design

    def _determine_experimental_type(self, hypothesis: str, context: Dict[str, Any]) -> ExperimentalType:
        """Determine the most appropriate experimental type"""
        hypothesis_lower = hypothesis.lower()

        # Keywords for different experimental types
        type_keywords = {
            ExperimentalType.IN_VITRO: ["cell", "culture", "in vitro", "cell line", "primary cells"],
            ExperimentalType.IN_VIVO: ["animal", "mouse", "rat", "in vivo", "organism", "whole organism"],
            ExperimentalType.IN_SILICO: ["simulation", "computational", "model", "in silico", "predict"],
            ExperimentalType.BIOCHEMICAL: ["protein", "enzyme", "binding", "interaction", "purified", "biochemical"],
            ExperimentalType.GENETIC: ["gene", "knockout", "knockdown", "mutant", "crispr", "overexpression"],
            ExperimentalType.IMAGING: ["visualize", "image", "microscopy", "localization", "structure"],
            ExperimentalType.OMICS: ["transcriptome", "proteome", "genome", "sequencing", "high-throughput", "omics"]
        }

        # Score each experimental type
        scores = {}
        for exp_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in hypothesis_lower)
            scores[exp_type] = score

        # Get the type with highest score
        if max(scores.values()) == 0:
            return ExperimentalType.IN_VITRO  # Default

        return max(scores, key=scores.get)

    def _extract_predictions(self, hypothesis: str) -> List[str]:
        """Extract testable predictions from hypothesis"""
        # This is a simplified version - would use NLP in production
        predictions = []

        # Look for prediction keywords
        if "will" in hypothesis.lower():
            parts = hypothesis.split(".")
            for part in parts:
                if "will" in part.lower():
                    predictions.append(part.strip())

        # If no explicit predictions, create implicit ones
        if not predictions:
            predictions = [
                f"Hypothesis is true: {hypothesis}",
                f"Hypothesis is false: Negation of {hypothesis}"
            ]

        return predictions

    def _design_variables(self, hypothesis: str, predictions: List[str], exp_type: ExperimentalType) -> List[ExperimentalVariable]:
        """Design experimental variables"""
        variables = []

        # Independent variable (what we manipulate)
        independent = ExperimentalVariable(
            variable_id="var_001",
            name="Independent variable",
            type="independent",
            description="The variable that is manipulated in the experiment",
            measurement_method="Experimental manipulation",
            expected_range=None
        )
        variables.append(independent)

        # Dependent variable (what we measure)
        dependent = ExperimentalVariable(
            variable_id="var_002",
            name="Dependent variable",
            type="dependent",
            description="The outcome that is measured",
            measurement_method=self._get_measurement_method(exp_type),
            units=self._get_units(exp_type),
            expected_range=(0, 100)
        )
        variables.append(dependent)

        # Confounding variables (to control for)
        confounders = self._identify_confounders(exp_type)
        for i, confounder in enumerate(confounders, 3):
            var = ExperimentalVariable(
                variable_id=f"var_{i:03d}",
                name=confounder,
                type="confounding",
                description=f"Potential confounding variable: {confounder}",
                measurement_method="Standardized protocol",
                units=None
            )
            variables.append(var)

        return variables

    def _get_measurement_method(self, exp_type: ExperimentalType) -> str:
        """Get appropriate measurement method for experimental type"""
        methods = {
            ExperimentalType.IN_VITRO: "Cell-based assay (e.g., fluorescence, luminescence)",
            ExperimentalType.IN_VIVO: "In vivo measurement (e.g., imaging, blood test)",
            ExperimentalType.IN_SILICO: "Computational simulation output",
            ExperimentalType.BIOCHEMICAL: "Biochemical assay (e.g., spectrophotometry, binding assay)",
            ExperimentalType.GENETIC: "Genetic analysis (e.g., qPCR, sequencing)",
            ExperimentalType.IMAGING: "Microscopy-based quantification",
            ExperimentalType.OMICS: "High-throughput assay (e.g., RNA-seq, mass spectrometry)"
        }
        return methods.get(exp_type, "Standard assay")

    def _get_units(self, exp_type: ExperimentalType) -> str:
        """Get appropriate units for measurements"""
        units = {
            ExperimentalType.IN_VITRO: "Relative fluorescence units (RFU)",
            ExperimentalType.IN_VIVO: "Concentration (mg/dL)",
            ExperimentalType.IN_SILICO: "Arbitrary units (a.u.)",
            ExperimentalType.BIOCHEMICAL: "Concentration (µM)",
            ExperimentalType.GENETIC: "Fold change",
            ExperimentalType.IMAGING: "Intensity (a.u.)",
            ExperimentalType.OMICS: "Normalized counts"
        }
        return units.get(exp_type, "Arbitrary units")

    def _identify_confounders(self, exp_type: ExperimentalType) -> List[str]:
        """Identify potential confounding variables"""
        common_confounders = [
            "Temperature",
            "pH",
            "Batch effects",
            "Operator variability",
            "Reagent lot variability",
            "Cell passage number"
        ]
        return common_confounders[:5]  # Return top 5

    def _design_controls(self, exp_type: ExperimentalType, variables: List[ExperimentalVariable]) -> List[ControlCondition]:
        """Design appropriate control conditions"""
        controls = []

        # Negative control (no treatment)
        negative = ControlCondition(
            control_id="ctrl_001",
            control_type=ControlType.NEGATIVE,
            description="No treatment or control substance",
            purpose="Establish baseline measurement",
            conditions={"treatment": "none"}
        )
        controls.append(negative)

        # Positive control (known effect)
        positive = ControlCondition(
            control_id="ctrl_002",
            control_type=ControlType.POSITIVE,
            description="Treatment with known effect",
            purpose="Validate assay is working",
            conditions={"treatment": "known_positive_control"}
        )
        controls.append(positive)

        # Vehicle control (if applicable)
        if exp_type in [ExperimentalType.IN_VITRO, ExperimentalType.IN_VIVO, ExperimentalType.BIOCHEMICAL]:
            vehicle = ControlCondition(
                control_id="ctrl_003",
                control_type=ControlType.VEHICLE,
                description="Treatment with vehicle/solvent only",
                purpose="Control for solvent effects",
                conditions={"treatment": "vehicle"}
            )
            controls.append(vehicle)

        return controls

    def _generate_protocol(self, exp_type: ExperimentalType, hypothesis: str, variables: List[ExperimentalVariable], controls: List[ControlCondition]) -> List[ExperimentalStep]:
        """Generate step-by-step experimental protocol"""
        protocol = []

        # Get base protocol for experimental type
        base_protocol = self._get_base_protocol(exp_type)

        # Customize for specific experiment
        for i, step_info in enumerate(base_protocol, 1):
            step = ExperimentalStep(
                step_number=i,
                title=step_info["title"],
                description=step_info["description"],
                duration_minutes=step_info.get("duration"),
                required_materials=step_info.get("materials", []),
                required_equipment=step_info.get("equipment", []),
                critical_parameters=step_info.get("parameters", {}),
                notes=step_info.get("notes", [])
            )
            protocol.append(step)

        return protocol

    def _get_base_protocol(self, exp_type: ExperimentalType) -> List[Dict[str, Any]]:
        """Get base protocol for experimental type"""
        protocols = {
            ExperimentalType.IN_VITRO: [
                {
                    "title": "Cell culture preparation",
                    "description": "Culture cells to appropriate density",
                    "duration": 60,
                    "materials": ["Cell line", "Culture medium", "Incubator"],
                    "equipment": ["Biosafety cabinet", "CO2 incubator"],
                    "parameters": {"cell_density": "70-80% confluency"},
                    "notes": ["Use cells at low passage number", "Check for mycoplasma contamination"]
                },
                {
                    "title": "Treatment application",
                    "description": "Apply experimental treatments to cells",
                    "duration": 30,
                    "materials": ["Treatment compounds", "Vehicle"],
                    "equipment": ["Pipettes"],
                    "parameters": {"concentration_range": "0.1-100 µM"},
                    "notes": ["Include vehicle controls", "Use triplicate wells"]
                },
                {
                    "title": "Incubation",
                    "description": "Allow treatment to take effect",
                    "duration": 1440,  # 24 hours
                    "materials": [],
                    "equipment": ["CO2 incubator"],
                    "parameters": {"temperature": "37°C", "CO2": "5%"},
                    "notes": ["Monitor cell health", "Check for contamination"]
                },
                {
                    "title": "Measurement",
                    "description": "Measure dependent variable",
                    "duration": 60,
                    "materials": ["Assay reagents"],
                    "equipment": ["Plate reader", "Microscope"],
                    "parameters": {},
                    "notes": ["Use appropriate filters", "Include standards"]
                },
                {
                    "title": "Data analysis",
                    "description": "Analyze and interpret results",
                    "duration": 120,
                    "materials": [],
                    "equipment": ["Computer", "Analysis software"],
                    "parameters": {},
                    "notes": ["Perform statistical tests", "Create visualizations"]
                }
            ],
            ExperimentalType.IN_VIVO: [
                {
                    "title": "Animal preparation",
                    "description": "Acclimate and prepare animals",
                    "duration": 4320,  # 3 days
                    "materials": ["Animals", "Food", "Water"],
                    "equipment": ["Animal facility"],
                    "parameters": {"group_size": "n=8-10"},
                    "notes": ["Follow IACUC guidelines", "Randomize to groups"]
                },
                {
                    "title": "Treatment administration",
                    "description": "Administer experimental treatments",
                    "duration": 30,
                    "materials": ["Treatment compounds", "Vehicle"],
                    "equipment": ["Syringes", "Scale"],
                    "parameters": {"dose": "Based on pilot study"},
                    "notes": ["Record body weight", "Monitor for adverse effects"]
                },
                {
                    "title": "Monitoring period",
                    "description": "Monitor animals over treatment period",
                    "duration": 10080,  # 7 days
                    "materials": ["Food", "Water"],
                    "equipment": ["Scale", "Monitoring equipment"],
                    "parameters": {},
                    "notes": ["Daily health checks", "Record behavior"]
                },
                {
                    "title": "Sample collection",
                    "description": "Collect biological samples",
                    "duration": 240,
                    "materials": ["Collection tubes", "Preservatives"],
                    "equipment": ["Centrifuge", "-80°C freezer"],
                    "parameters": {},
                    "notes": ["Process samples immediately", "Store at -80°C"]
                },
                {
                    "title": "Analysis",
                    "description": "Analyze samples and interpret results",
                    "duration": 1440,
                    "materials": ["Assay kits"],
                    "equipment": ["Assay equipment"],
                    "parameters": {},
                    "notes": ["Blind analysis", "Include controls"]
                }
            ],
            ExperimentalType.IN_SILICO: [
                {
                    "title": "Model setup",
                    "description": "Set up computational model",
                    "duration": 240,
                    "materials": ["Model parameters", "Initial conditions"],
                    "equipment": ["Computer", "Modeling software"],
                    "parameters": {"time_step": "appropriate for system"},
                    "notes": ["Validate model setup", "Document parameters"]
                },
                {
                    "title": "Simulation runs",
                    "description": "Run simulations under different conditions",
                    "duration": 480,
                    "materials": [],
                    "equipment": ["Computer cluster", "Simulation software"],
                    "parameters": {"replicates": "n=100"},
                    "notes": ["Use random seeds", "Save intermediate states"]
                },
                {
                    "title": "Data analysis",
                    "description": "Analyze simulation outputs",
                    "duration": 360,
                    "materials": [],
                    "equipment": ["Computer", "Analysis software"],
                    "parameters": {},
                    "notes": ["Statistical analysis", "Visualization"]
                },
                {
                    "title": "Validation",
                    "description": "Validate against experimental data if available",
                    "duration": 240,
                    "materials": ["Experimental data"],
                    "equipment": ["Computer"],
                    "parameters": {},
                    "notes": ["Compare to literature", "Identify discrepancies"]
                }
            ]
        }

        return protocols.get(exp_type, protocols[ExperimentalType.IN_VITRO])

    def _perform_power_analysis(self, variables: List[ExperimentalVariable], protocol: List[ExperimentalStep]) -> StatisticalPower:
        """Perform statistical power analysis"""
        # This is a simplified power analysis
        # In practice, would use more sophisticated methods

        # Determine appropriate statistical tests
        tests = ["ANOVA", "t-test with multiple comparisons correction"]

        # Sample size calculation (simplified)
        effect_size = 0.5  # Medium effect size (Cohen's d)
        power = 0.8  # Standard power
        alpha = 0.05  # Standard significance level

        # Simplified sample size calculation
        # n = 2 * (Z_alpha + Z_beta)^2 / d^2
        import math
        from scipy import stats
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        sample_size = int(2 * (z_alpha + z_beta)**2 / effect_size**2)
        sample_size = max(sample_size, 8)  # Minimum 8 per group

        assumptions = [
            "Normal distribution of data",
            "Homogeneity of variance",
            "Independent observations",
            "No significant outliers"
        ]

        return StatisticalPower(
            sample_size=sample_size,
            effect_size=effect_size,
            power=power,
            significance_level=alpha,
            statistical_tests=tests,
            assumptions=assumptions
        )

    def _check_feasibility(self, protocol: List[ExperimentalStep], context: Dict[str, Any]) -> FeasibilityLevel:
        """Check feasibility of experimental design"""
        # Check if required equipment and materials are available
        required_equipment = set()
        required_materials = set()

        for step in protocol:
            required_equipment.update(step.required_equipment)
            required_materials.update(step.required_materials)

        # Check against databases (simplified)
        # In practice, would query bioinformatics databases

        # Simplified feasibility assessment
        score = 0
        if len(required_equipment) <= 5:
            score += 1
        if len(required_materials) <= 10:
            score += 1
        if all(step.duration_minutes for step in protocol if step.duration_minutes):
            score += 1

        if score >= 3:
            return FeasibilityLevel.HIGH
        elif score >= 2:
            return FeasibilityLevel.MEDIUM
        elif score >= 1:
            return FeasibilityLevel.LOW
        else:
            return FeasibilityLevel.VERY_LOW

    def _estimate_resources(self, exp_type: ExperimentalType, protocol: List[ExperimentalStep], sample_size: int) -> List[ResourceRequirement]:
        """Estimate resource requirements"""
        resources = []

        # Reagents
        reagents = set()
        for step in protocol:
            reagents.update(step.required_materials)

        if reagents:
            # Estimate cost
            base_cost = self.materials_db.get(exp_type.name.lower(), {}).get("typical_cost", 5000)
            scaled_cost = base_cost * (sample_size / 10)  # Scale with sample size

            resources.append(ResourceRequirement(
                category="reagents",
                items=list(reagents),
                estimated_cost_usd=scaled_cost,
                availability="Commercially available"
            ))

        # Equipment
        equipment = set()
        for step in protocol:
            equipment.update(step.required_equipment)

        if equipment:
            resources.append(ResourceRequirement(
                category="equipment",
                items=list(equipment),
                estimated_cost_usd=None,  # Equipment usually available
                availability="Core facility / Institutional"
            ))

        # Personnel
        resources.append(ResourceRequirement(
            category="personnel",
            items=["Research technician", "PI supervision"],
            estimated_cost_usd=sample_size * 100,  # Rough estimate
            availability="Available"
        ))

        # Time
        total_time = sum((s.duration_minutes or 0) for s in protocol)
        resources.append(ResourceRequirement(
            category="time",
            items=[f"{total_time/60:.1f} hours of hands-on time"],
            estimated_cost_usd=None,
            availability=f"{total_time/60/8:.1f} days"
        ))

        return resources

    def _estimate_timeline(self, exp_type: ExperimentalType, protocol: List[ExperimentalStep], sample_size: int) -> int:
        """Estimate experimental timeline in days"""
        base_timelines = {
            ExperimentalType.IN_VITRO: 7,
            ExperimentalType.IN_VIVO: 14,
            ExperimentalType.IN_SILICO: 3,
            ExperimentalType.BIOCHEMICAL: 5,
            ExperimentalType.GENETIC: 10,
            ExperimentalType.IMAGING: 7,
            ExperimentalType.OMICS: 21
        }

        base = base_timelines.get(exp_type, 7)

        # Scale with sample size
        scale_factor = 1 + (sample_size - 10) / 100

        return int(base * scale_factor)

    def _assess_risks(self, exp_type: ExperimentalType, protocol: List[ExperimentalStep]) -> List[str]:
        """Assess experimental risks"""
        risks = [
            "Technical failure of assay",
            "Contamination",
            "Insufficient statistical power",
            "Unexpected side effects"
        ]

        # Add type-specific risks
        type_risks = {
            ExperimentalType.IN_VITRO: [
                "Cell line drift",
                "Mycoplasma contamination",
                "Passage number effects"
            ],
            ExperimentalType.IN_VIVO: [
                "Animal welfare concerns",
                "Inter-animal variability",
                "Ethical approval delays"
            ],
            ExperimentalType.IN_SILICO: [
                "Model assumptions invalid",
                "Computational limitations",
                "Validation data unavailable"
            ]
        }

        risks.extend(type_risks.get(exp_type, []))

        return risks

    def _identify_pitfalls(self, exp_type: ExperimentalType, hypothesis: str, variables: List[ExperimentalVariable]) -> List[str]:
        """Identify potential experimental pitfalls"""
        pitfalls = [
            "Insufficient replication",
            "Inadequate controls",
            "Measurement not sensitive enough",
            "Time points not appropriate"
        ]

        return pitfalls

    def _suggest_alternatives(self, exp_type: ExperimentalType, hypothesis: str) -> List[str]:
        """Suggest alternative experimental approaches"""
        alternatives = []

        # Suggest other experimental types
        all_types = list(ExperimentalType)
        for alt_type in all_types:
            if alt_type != exp_type:
                alternatives.append(f"Alternative approach: {alt_type.value.replace('_', ' ').title()}")

        return alternatives[:3]

    def _predict_outcomes(self, hypothesis: str, predictions: List[str], variables: List[ExperimentalVariable]) -> List[str]:
        """Predict experimental outcomes"""
        outcomes = [
            "If hypothesis is correct: Significant difference between treatment and control groups",
            "If hypothesis is incorrect: No significant difference between groups"
        ]

        return outcomes

    def _calculate_confidence(self, feasibility: FeasibilityLevel, stats: StatisticalPower, risks: List[str]) -> float:
        """Calculate confidence in experimental design"""
        confidence = 0.5  # Base confidence

        # Adjust for feasibility
        if feasibility == FeasibilityLevel.HIGH:
            confidence += 0.2
        elif feasibility == FeasibilityLevel.MEDIUM:
            confidence += 0.1
        elif feasibility == FeasibilityLevel.LOW:
            confidence -= 0.1
        elif feasibility == FeasibilityLevel.VERY_LOW:
            confidence -= 0.2

        # Adjust for statistical power
        if stats.power >= 0.8:
            confidence += 0.1
        elif stats.power < 0.6:
            confidence -= 0.1

        # Adjust for risks
        risk_penalty = min(len(risks) * 0.02, 0.2)
        confidence -= risk_penalty

        return max(0.0, min(1.0, confidence))

    def _generate_title(self, hypothesis: str, exp_type: ExperimentalType) -> str:
        """Generate title for experimental design"""
        return f"Testing {hypothesis[:50]}... using {exp_type.value.replace('_', ' ').title()}"

    def _generate_objective(self, hypothesis: str) -> str:
        """Generate objective statement"""
        return f"To experimentally test the hypothesis: {hypothesis}"

    def _generate_background(self, hypothesis: str, context: Dict[str, Any]) -> str:
        """Generate background information"""
        return f"This experiment aims to test the hypothesis: {hypothesis}. " \
               f"The design incorporates appropriate controls and statistical power to ensure reliable results."

    def _dict_to_design(self, design_dict: Dict[str, Any]) -> ExperimentalDesign:
        """Convert dictionary to ExperimentalDesign object"""
        # This would implement full conversion
        # For now, return a placeholder
        return None

    def _save_design_history(self, design: ExperimentalDesign):
        """Save experimental design to persistent storage"""
        try:
            os.makedirs("/Users/gjw255/.biodisc_persistent", exist_ok=True)
            history_path = "/Users/gjw255/.biodisc_persistent/experimental_designs.jsonl"

            design_dict = {
                'design_id': design.design_id,
                'hypothesis': design.hypothesis,
                'experimental_type': design.experimental_type.value,
                'title': design.title,
                'objective': design.objective,
                'variables': [
                    {
                        'variable_id': v.variable_id,
                        'name': v.name,
                        'type': v.type,
                        'description': v.description
                    }
                    for v in design.variables
                ],
                'controls': [
                    {
                        'control_id': c.control_id,
                        'control_type': c.control_type.value,
                        'description': c.description
                    }
                    for c in design.controls
                ],
                'feasibility': design.feasibility.value,
                'timeline_days': design.timeline_days,
                'confidence': design.confidence,
                'generated_at': design.generated_at
            }

            with open(history_path, 'a') as f:
                f.write(json.dumps(design_dict) + '\n')

        except Exception as e:
            print(f"Error saving design history: {e}")

    def get_design_summary(self, design_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a specific experimental design"""
        for design in self.designs:
            if design.design_id == design_id:
                return {
                    'design_id': design.design_id,
                    'title': design.title,
                    'hypothesis': design.hypothesis,
                    'experimental_type': design.experimental_type.value,
                    'feasibility': design.feasibility.value,
                    'timeline_days': design.timeline_days,
                    'confidence': design.confidence
                }
        return None


def create_experimental_design_engine() -> ExperimentalDesignEngine:
    """Factory function to create experimental design engine"""
    return ExperimentalDesignEngine()


# Singleton instance
_instance = None

def get_experimental_design_engine() -> ExperimentalDesignEngine:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_experimental_design_engine()
    return _instance
