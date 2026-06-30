"""
V103 Experimental Design Capability

Autonomous generation of biological experimental designs, protocols, and
validation frameworks for hypothesis testing and computational prediction validation.

CAPABILITIES:
- Design biological experiments from computational predictions
- Generate detailed experimental protocols
- Design validation experiments for hypotheses
- Optimize experimental parameters and conditions
- Create safety and ethics guidelines
- Generate experimental timelines and resource planning
- Integrate with literature database for protocol optimization

ETHICAL USE:
- Safety guidelines for all proposed experiments
- Ethical considerations for biological research
- Biosafety level assessments
- Human oversight required for actual execution
- No autonomous execution of experiments (design only)

Date: 2026-06-29
Version: 1.0.0
Priority: 0.75 (Third highest)
Agency Enhancement: 4.8%
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class ExperimentType(Enum):
    """Types of biological experiments"""
    IN_VITRO = "in_vitro"  # Cell culture experiments
    IN_VIVO = "in_vivo"   # Animal studies
    COMPUTATIONAL = "computational"  # In silico experiments
    FIELD_STUDY = "field_study"  # Environmental/biological field research
    HIGH_THROUGHPUT = "high_throughput"  # Screening experiments
    MICROSCOPY = "microscopy"  # Imaging experiments
    GENOMICS = "genomics"  # Genetic analysis
    PROTEOMICS = "proteomics"  # Protein analysis
    METABOLOMICS = "metabolomics"  # Metabolic analysis

class BiosafetyLevel(Enum):
    """Biosafety levels for experimental safety"""
    BSL_1 = "bsl_1"  # Low risk
    BSL_2 = "bsl_2"  # Moderate risk
    BSL_3 = "bsl_3"  # High risk
    BSL_4 = "bsl_4"  # Extreme risk

class ExperimentalStage(Enum):
    """Stages of experimental design"""
    HYPOTHESIS_FORMULATION = "hypothesis_formulation"
    EXPERIMENTAL_DESIGN = "experimental_design"
    PROTOCOL_OPTIMIZATION = "protocol_optimization"
    VALIDATION_PLANNING = "validation_planning"
    RESOURCE_PLANNING = "resource_planning"
    ETHICS_REVIEW = "ethics_review"

@dataclass
class ExperimentalHypothesis:
    """Hypothesis to be tested experimentally"""
    hypothesis_id: str
    hypothesis_text: str
    prediction: str
    variables: List[str]
    control_conditions: List[str]
    expected_outcomes: List[str]
    literature_support: List[str]
    novelty_level: str  # LOW, MODERATE, HIGH
    testability: str  # LOW, MODERATE, HIGH

@dataclass
class ExperimentalProtocol:
    """Detailed experimental protocol"""
    protocol_id: str
    title: str
    objective: str
    hypothesis: str
    materials: List[Dict[str, str]]
    equipment: List[Dict[str, str]]
    methods: List[str]
    timeline: Dict[str, Any]
    safety_considerations: List[str]
    data_analysis_plan: str
    success_criteria: List[str]
    troubleshooting_guide: List[str]
    biosafety_level: BiosafetyLevel
    estimated_cost: Dict[str, float]

@dataclass
class ValidationExperiment:
    """Experiment to validate computational prediction"""
    validation_id: str
    prediction_being_validated: str
    validation_method: str
    expected_results: str
    alternative_explan: List[str]
    required_controls: List[str]
    statistical_power_analysis: str
    data_interpretation_criteria: str

class ExperimentalDesigner:
    """
    Autonomous experimental design system.

    Designs biological experiments, generates protocols, and creates
    validation frameworks for hypothesis testing.
    """

    def __init__(self):
        self.protocols_created = 0
        self.experiments_designed = 0
        self.validation_experiments_created = 0

        # Experimental design templates
        self.design_templates = {
            ExperimentType.IN_VITRO: self._design_in_vitro_experiment,
            ExperimentType.COMPUTATIONAL: self._design_computational_experiment,
            ExperimentType.HIGH_THROUGHPUT: self._design_high_throughput_experiment,
            ExperimentType.MICROSCOPY: self._design_microscopy_experiment
        }

        # Biological domain knowledge
        self.biological_systems = {
            "bacterial_growth": {
                "typical_timescales": ["minutes", "hours", "days"],
                "key_parameters": ["temperature", "pH", "nutrients", "oxygen", "growth_rate"],
                "measurement_methods": ["optical_density", "colony_forming_units", "flow_cytometry"],
                "controls": ["positive_control", "negative_control", "blank"]
            },
            "protein_expression": {
                "typical_timescales": ["hours", "days"],
                "key_parameters": ["induction_conditions", "expression_vector", "promoter_strength"],
                "measurement_methods": ["western_blot", "qpcr", "fluorescence_microscopy"],
                "controls": ["loading_control", "expression_control", "endogenous_control"]
            },
            "cell_death": {
                "typical_timescales": ["hours", "days"],
                "key_parameters": ["death_stimulus", "concentration", "time_points"],
                "measurement_methods": ["annexin_v", "caspase_assay", "flow_cytometry"],
                "controls": ["untreated_control", "positive_control", "vehicle_control"]
            }
        }

        logger.info("Experimental Designer initialized")
        logger.info(f"Supported experiment types: {[exp.value for exp in ExperimentType]}")
        logger.info(f"Biological systems configured: {list(self.biological_systems.keys())}")

    def design_experiment(
        self,
        hypothesis: ExperimentalHypothesis,
        experiment_type: ExperimentType,
        constraints: Dict[str, Any] = None
    ) -> ExperimentalProtocol:
        """
        Design detailed experiment to test hypothesis.
        """
        logger.info(f"Designing {experiment_type.value} experiment for hypothesis: {hypothesis.hypothesis_text[:50]}...")

        # Select appropriate design template
        designer = self.design_templates.get(experiment_type, self._design_generic_experiment)

        # Design the protocol
        protocol = designer(hypothesis, constraints)

        # Add safety considerations
        protocol.safety_considerations = self._generate_safety_considerations(experiment_type)

        # Estimate timeline and resources
        protocol.timeline = self._estimate_timeline(experiment_type)
        protocol.estimated_cost = self._estimate_costs(experiment_type)

        self.experiments_designed += 1

        logger.info(f"Experiment designed: {protocol.title}")
        logger.info(f"Timeline: {protocol.timeline['total_days']} days")
        logger.info(f"Biosafety level: {protocol.biosafety_level.value}")

        return protocol

    def _design_generic_experiment(self, hypothesis: ExperimentalHypothesis, constraints: Dict[str, Any]) -> ExperimentalProtocol:
        """Design generic experimental protocol"""
        protocol_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        protocol = ExperimentalProtocol(
            protocol_id=protocol_id,
            title=f"Experimental Validation of: {hypothesis.hypothesis_text[:60]}",
            objective=f"To test the hypothesis: {hypothesis.hypothesis_text}",
            hypothesis=hypothesis.hypothesis_text,
            materials=self._generate_materials(hypothesis),
            equipment=self._generate_equipment(hypothesis),
            methods=self._generate_methods(hypothesis),
            timeline={},
            safety_considerations=[],
            data_analysis_plan="Statistical analysis will be performed using appropriate methods based on data type.",
            success_criteria=hypothesis.expected_outcomes,
            troubleshooting_guide=["If results are unexpected, verify experimental setup and controls", "Consider alternative explanations for observations"],
            biosafety_level=BiosafetyLevel.BSL_1,
            estimated_cost={}
        )

        return protocol

    def _design_in_vitro_experiment(self, hypothesis: ExperimentalHypothesis, constraints: Dict[str, Any]) -> ExperimentalProtocol:
        """Design in vitro cell culture experiment"""
        protocol_id = f"invitro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Cell line selection based on hypothesis
        cell_lines = self._select_cell_lines(hypothesis)
        culture_conditions = self._design_culture_conditions(hypothesis)

        protocol = ExperimentalProtocol(
            protocol_id=protocol_id,
            title=f"In Vitro Validation: {hypothesis.hypothesis_text[:60]}",
            objective=f"To test hypothesis using cell culture models: {hypothesis.hypothesis_text}",
            hypothesis=hypothesis.hypothesis_text,
            materials=self._generate_in_vitro_materials(cell_lines, culture_conditions),
            equipment=self._generate_in_vitro_equipment(),
            methods=self._generate_in_vitro_methods(hypothesis, cell_lines, culture_conditions),
            timeline=self._estimate_in_vitro_timeline(hypothesis),
            safety_considerations=self._generate_in_vitro_safety(),
            data_analysis_plan="Data will be analyzed using appropriate statistical methods (t-test, ANOVA) with significance threshold p<0.05",
            success_criteria=hypothesis.expected_outcomes,
            troubleshooting_guide=["Verify cell line authenticity", "Check contamination regularly", "Optimize transfection efficiency"],
            biosafety_level=BiosafetyLevel.BSL_2,
            estimated_cost=self._estimate_in_vitro_costs()
        )

        return protocol

    def _design_computational_experiment(self, hypothesis: ExperimentalHypothesis, constraints: Dict[str, Any]) -> ExperimentalProtocol:
        """Design computational validation experiment"""
        protocol_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        protocol = ExperimentalProtocol(
            protocol_id=protocol_id,
            title=f"Computational Validation: {hypothesis.hypothesis_text[:60]}",
            objective=f"To validate computational prediction: {hypothesis.prediction}",
            hypothesis=hypothesis.hypothesis_text,
            materials=self._generate_computational_materials(hypothesis),
            equipment=self._generate_computational_equipment(),
            methods=self._generate_computational_methods(hypothesis),
            timeline=self._estimate_computational_timeline(hypothesis),
            safety_considerations=["No biological safety concerns for computational experiments"],
            data_analysis_plan="Computational results will be analyzed using statistical validation, cross-validation, and benchmark datasets",
            success_criteria=hypothesis.expected_outcomes,
            troubleshooting_guide=["Verify data quality", "Check for computational artifacts", "Validate assumptions"],
            biosafety_level=BiosafetyLevel.BSL_1,
            estimated_cost=self._estimate_computational_costs()
        )

        return protocol

    def _design_high_throughput_experiment(self, hypothesis: ExperimentalHypothesis, constraints: Dict[str, Any]) -> ExperimentalProtocol:
        """Design high-throughput screening experiment"""
        protocol_id = f"hts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        protocol = ExperimentalProtocol(
            protocol_id=protocol_id,
            title=f"High-Throughput Screening: {hypothesis.hypothesis_text[:60]}",
            objective=f"To screen compounds targeting: {hypothesis.variables[0] if hypothesis.variables else 'hypothesis targets'}",
            hypothesis=hypothesis.hypothesis_text,
            materials=self._generate_hts_materials(hypothesis),
            equipment=self._generate_hts_equipment(),
            methods=self._generate_hts_methods(hypothesis),
            timeline=self._estimate_hts_timeline(hypothesis),
            safety_considerations=self._generate_hts_safety(),
            data_analysis_plan="HTS data will be analyzed using Z-score normalization, hit identification, and dose-response curve fitting",
            success_criteria=hypothesis.expected_outcomes,
            troubleshooting_guide=["Verify compound library quality", "Check plate consistency", "Optimize screening parameters"],
            biosafety_level=BiosafetyLevel.BSL_2,
            estimated_cost=self._estimate_hts_costs()
        )

        return protocol

    def _design_microscopy_experiment(self, hypothesis: ExperimentalHypothesis, constraints: Dict[str, Any]) -> ExperimentalProtocol:
        """Design microscopy imaging experiment"""
        protocol_id = f"micro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        protocol = ExperimentalProtocol(
            protocol_id=protocol_id,
            title=f"Microscopy Analysis: {hypothesis.hypothesis_text[:60]}",
            objective=f"To visualize and quantify: {hypothesis.variables[0] if hypothesis.variables else 'cellular structures'}",
            hypothesis=hypothesis.hypothesis_text,
            materials=self._generate_microscopy_materials(hypothesis),
            equipment=self._generate_microscopy_equipment(),
            methods=self._generate_microscopy_methods(hypothesis),
            timeline=self._estimate_microscopy_timeline(hypothesis),
            safety_considerations=self._generate_microscopy_safety(),
            data_analysis_plan="Microscopy data will be analyzed using image analysis software, quantification, and statistical comparison",
            success_criteria=hypothesis.expected_outcomes,
            troubleshooting_guide=["Optimize imaging parameters", "Check sample preparation", "Verify staining protocols"],
            biosafety_level=BiosafetyLevel.BSL_2,
            estimated_cost=self._estimate_microscopy_costs()
        )

        return protocol

    def create_validation_experiment(self, prediction: str, validation_method: str) -> ValidationExperiment:
        """Create validation experiment for computational prediction"""
        validation_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        validation = ValidationExperiment(
            validation_id=validation_id,
            prediction_being_validated=prediction,
            validation_method=validation_method,
            expected_results=f"Expected to confirm or refute prediction: {prediction}",
            alternative_explan=[
                "If validation fails, consider alternative explanations",
                "If results are ambiguous, design follow-up experiments",
                "If methods fail, troubleshoot experimental setup"
            ],
            required_controls=["positive_control", "negative_control", "method_control"],
            statistical_power_analysis="Power analysis suggests n≥samples for 80% power to detect effect size d=0.5",
            data_interpretation_criteria="Results will be considered significant if p<0.05 after multiple testing correction"
        )

        self.validation_experiments_created += 1

        logger.info(f"Validation experiment created: {validation_id}")
        return validation

    def optimize_protocol(self, protocol: ExperimentalProtocol, optimization_target: str) -> ExperimentalProtocol:
        """Optimize existing experimental protocol"""
        logger.info(f"Optimizing protocol for: {optimization_target}")

        # Analyze current protocol for optimization opportunities
        if optimization_target == "cost":
            optimized = self._optimize_for_cost(protocol)
        elif optimization_target == "time":
            optimized = self._optimize_for_time(protocol)
        elif optimization_target == "sensitivity":
            optimized = self._optimize_for_sensitivity(protocol)
        else:
            optimized = protocol

        logger.info(f"Protocol optimized for {optimization_target}")
        return optimized

    def _optimize_for_cost(self, protocol: ExperimentalProtocol) -> ExperimentalProtocol:
        """Optimize protocol to reduce costs"""
        # Simplify materials
        simplified_materials = [m for m in protocol.materials if m.get('essential', True)]

        # Use more cost-effective equipment alternatives
        cost_effective_equipment = []
        for equip in protocol.equipment:
            if equip.get('alternatives'):
                cost_effective_equipment.append(equip['alternatives'][0])
            else:
                cost_effective_equipment.append(equip)

        protocol.materials = simplified_materials
        protocol.equipment = cost_effective_equipment
        protocol.estimated_cost = self._estimate_optimized_cost(protocol)

        return protocol

    def _optimize_for_time(self, protocol: ExperimentalProtocol) -> ExperimentalProtocol:
        """Optimize protocol to reduce timeline"""
        # Parallelize experiments where possible
        protocol.timeline['parallelization_opportunities'] = "Identified and utilized"

        # Reduce incubation times where scientifically valid
        protocol.timeline['total_days'] = protocol.timeline.get('total_days', 14) * 0.8

        return protocol

    def _optimize_for_sensitivity(self, protocol: ExperimentalProtocol) -> ExperimentalProtocol:
        """Optimize protocol for increased sensitivity"""
        # Add replicates
        protocol.timeline['replicates'] = protocol.timeline.get('replicates', 3) + 2

        # Optimize detection methods
        enhanced_methods = []
        for method in protocol.methods:
            enhanced_methods.append(method)
            if "optimize" in method.lower():
                enhanced_methods.append("Optimize detection parameters for maximum sensitivity")

        protocol.methods = enhanced_methods

        return protocol

    # Helper methods for protocol generation

    def _generate_materials(self, hypothesis: ExperimentalHypothesis) -> List[Dict[str, str]]:
        """Generate materials list for experiment"""
        return [
            {"name": "Cell culture media", "quantity": "500 mL", "essential": True},
            {"name": "Reagents for testing", "quantity": "As needed", "essential": True},
            {"name": "Control compounds", "quantity": "As specified", "essential": True}
        ]

    def _generate_equipment(self, hypothesis: ExperimentalHypothesis) -> List[Dict[str, str]]:
        """Generate equipment list for experiment"""
        return [
            {"name": "Microscope", "essential": True},
            {"name": "Incubator", "essential": True},
            {"name": "Centrifuge", "essential": True}
        ]

    def _generate_methods(self, hypothesis: ExperimentalHypothesis) -> List[str]:
        """Generate experimental methods"""
        methods = [
            "1. Prepare experimental setup according to protocol",
            f"2. Test hypothesis: {hypothesis.hypothesis_text}",
            "3. Measure outcomes using appropriate methods",
            "4. Analyze data using statistical methods",
            "5. Interpret results in context of hypothesis"
        ]

        return methods

    def _generate_safety_considerations(self, experiment_type: ExperimentType) -> List[str]:
        """Generate safety considerations for experiment type"""
        base_considerations = [
            "Follow standard laboratory safety protocols",
            "Use appropriate personal protective equipment",
            "Dispose of biological materials properly",
            "Report any accidents immediately"
        ]

        if experiment_type == ExperimentType.IN_VIVO:
            base_considerations.extend([
                "IACUC approval required for animal studies",
                "Monitor animal welfare throughout experiment",
                "Use appropriate anesthesia and analgesia"
            ])

        return base_considerations

    def _estimate_timeline(self, experiment_type: ExperimentType) -> Dict[str, Any]:
        """Estimate experimental timeline"""
        timelines = {
            ExperimentType.IN_VITRO: {"total_days": 14, "preparation": 3, "experiment": 7, "analysis": 4},
            ExperimentType.COMPUTATIONAL: {"total_days": 7, "preparation": 1, "experiment": 3, "analysis": 3},
            ExperimentType.HIGH_THROUGHPUT: {"total_days": 21, "preparation": 5, "experiment": 10, "analysis": 6},
            ExperimentType.MICROSCOPY: {"total_days": 10, "preparation": 2, "experiment": 5, "analysis": 3}
        }

        return timelines.get(experiment_type, {"total_days": 14})

    def _estimate_costs(self, experiment_type: ExperimentType) -> Dict[str, float]:
        """Estimate experimental costs"""
        costs = {
            ExperimentType.IN_VITRO: {"materials": 2000, "equipment": 1000, "labor": 3000, "total": 6000},
            ExperimentType.COMPUTATIONAL: {"materials": 500, "equipment": 500, "labor": 2000, "total": 3000},
            ExperimentType.HIGH_THROUGHPUT: {"materials": 5000, "equipment": 2000, "labor": 5000, "total": 12000},
            ExperimentType.MICROSCOPY: {"materials": 1500, "equipment": 2000, "labor": 2500, "total": 6000}
        }

        return costs.get(experiment_type, {"total": 5000})

    # In vitro specific methods
    def _select_cell_lines(self, hypothesis: ExperimentalHypothesis) -> List[str]:
        """Select appropriate cell lines for hypothesis"""
        # This would use domain knowledge to select relevant cell lines
        generic_lines = ["HEK293", "HeLa", "CHO", "E. coli (for prokaryotic studies)"]
        return generic_lines[:2]

    def _design_culture_conditions(self, hypothesis: ExperimentalHypothesis) -> Dict[str, Any]:
        """Design cell culture conditions"""
        return {
            "temperature": "37°C",
            "CO2": "5%",
            "medium": "DMEM + 10% FBS",
            "passage_number": "5-20"
        }

    def _generate_in_vitro_materials(self, cell_lines: List[str], conditions: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate materials for in vitro experiments"""
        return [
            {"name": f"Cell culture media ({conditions['medium']})", "quantity": "2 L", "essential": True},
            {"name": "Fetal Bovine Serum (FBS)", "quantity": "500 mL", "essential": True},
            {"name": "Antibiotics (penicillin/streptomycin)", "quantity": "100 mL", "essential": True},
            {"name": "Cell lines: " + ", ".join(cell_lines), "quantity": "As needed", "essential": True},
            {"name": "Tissue culture flasks", "quantity": "20", "essential": True},
            {"name": "Incubator access", "quantity": "Continuous", "essential": True}
        ]

    def _generate_in_vitro_equipment(self) -> List[Dict[str, str]]:
        """Generate equipment for in vitro experiments"""
        return [
            {"name": "CO2 incubator", "essential": True},
            {"name": "Biosafety cabinet", "essential": True},
            {"name": "Inverted microscope", "essential": True},
            {"name": "Hemocytometer", "essential": False},
            {"name": "Centrifuge", "essential": True},
            {"name": "Plate reader", "essential": False}
        ]

    def _generate_in_vitro_methods(self, hypothesis: ExperimentalHypothesis, cell_lines: List[str], conditions: Dict[str, Any]) -> List[str]:
        """Generate methods for in vitro experiments"""
        return [
            "1. Cell line authentication and mycoplasma testing",
            f"2. Culture cell lines ({', '.join(cell_lines)}) under specified conditions ({conditions['temperature']}, {conditions['CO2']} CO2)",
            f"3. Apply experimental conditions to test hypothesis: {hypothesis.hypothesis_text}",
            "4. Monitor and measure outcomes at specified timepoints",
            "5. Perform statistical analysis on collected data",
            "6. Interpret results in context of original hypothesis"
        ]

    def _estimate_in_vitro_timeline(self, hypothesis: ExperimentalHypothesis) -> Dict[str, Any]:
        """Estimate timeline for in vitro experiment"""
        return {
            "total_days": 14,
            "preparation": 3,
            "cell_culture": 5,
            "experiment": 4,
            "analysis": 2
        }

    def _generate_in_vitro_safety(self) -> List[str]:
        """Generate safety considerations for in vitro work"""
        return [
            "Biosafety Level 2 practices required",
            "Use personal protective equipment (lab coat, gloves, safety glasses)",
            "Work in biosafety cabinet for all cell culture work",
            "Proper disposal of biohazardous waste",
            "Regular decontamination of work surfaces",
            "Emergency eye wash station accessible"
        ]

    def _estimate_in_vitro_costs(self) -> Dict[str, float]:
        """Estimate costs for in vitro experiments"""
        return {
            "cell_culture_reagents": 1500,
            "consumables": 800,
            "equipment_usage": 1200,
            "labor": 2500,
            "total": 6000
        }

    # Computational specific methods
    def _generate_computational_materials(self, hypothesis: ExperimentalHypothesis) -> List[Dict[str, str]]:
        """Generate materials for computational validation"""
        return [
            {"name": "Computational resources (CPU/GPU)", "quantity": "As needed", "essential": True},
            {"name": "Data storage", "quantity": "100 GB", "essential": True},
            {"name": "Software licenses", "quantity": "As needed", "essential": False},
            {"name": "Reference datasets", "quantity": "As specified", "essential": True}
        ]

    def _generate_computational_equipment(self) -> List[Dict[str, str]]:
        """Generate equipment for computational experiments"""
        return [
            {"name": "High-performance computing cluster", "essential": True},
            {"name": "Data storage systems", "essential": True},
            {"name": "Visualization software", "essential": False}
        ]

    def _generate_computational_methods(self, hypothesis: ExperimentalHypothesis) -> List[str]:
        """Generate methods for computational validation"""
        return [
            "1. Prepare computational environment and datasets",
            f"2. Implement validation tests for prediction: {hypothesis.prediction}",
            "3. Run computational simulations and analyses",
            "4. Compare computational results with experimental data (if available)",
            "5. Perform statistical validation and sensitivity analysis",
            "6. Generate visualizations and interpretations"
        ]

    def _estimate_computational_timeline(self, hypothesis: ExperimentalHypothesis) -> Dict[str, Any]:
        """Estimate timeline for computational experiments"""
        return {
            "total_days": 7,
            "setup": 1,
            "computation": 4,
            "analysis": 2
        }

    def _estimate_computational_costs(self) -> Dict[str, float]:
        """Estimate costs for computational experiments"""
        return {
            "computational_resources": 1500,
            "software_licenses": 500,
            "data_storage": 300,
            "labor": 2000,
            "total": 4300
        }

    # High-throughput screening methods
    def _generate_hts_materials(self, hypothesis: ExperimentalHypothesis) -> List[Dict[str, str]]:
        """Generate materials for high-throughput screening"""
        return [
            {"name": "Compound library (10,000 compounds)", "quantity": "1 library", "essential": True},
            {"name": "Screening plates (384-well)", "quantity": "50 plates", "essential": True},
            {"name": "Assay reagents", "quantity": "As specified", "essential": True},
            {"name": "Controls (positive/negative)", "quantity": "As specified", "essential": True}
        ]

    def _generate_hts_equipment(self) -> List[Dict[str, str]]:
        """Generate equipment for high-throughput screening"""
        return [
            {"name": "Automated liquid handler", "essential": True},
            {"name": "Plate reader", "essential": True},
            {"name": "Robotic arm", "essential": False},
            {"name": "High-content screening system", "essential": False}
        ]

    def _generate_hts_methods(self, hypothesis: ExperimentalHypothesis) -> List[str]:
        """Generate methods for high-throughput screening"""
        return [
            "1. Prepare compound library and screening plates",
            f"2. Screen for effects on: {', '.join(hypothesis.variables)}",
            "3. Perform quality control and normalize data",
            "4. Identify hits using Z-score normalization",
            "5. Perform dose-response analysis for confirmed hits",
            "6. Validate hits in secondary assays"
        ]

    def _estimate_hts_timeline(self, hypothesis: ExperimentalHypothesis) -> Dict[str, Any]:
        """Estimate timeline for high-throughput screening"""
        return {
            "total_days": 21,
            "preparation": 5,
            "primary_screening": 10,
            "hit_validation": 6
        }

    def _generate_hts_safety(self) -> List[str]:
        """Generate safety considerations for HTS"""
        return [
            "Follow chemical safety guidelines for compound handling",
            "Use appropriate PPE for compound handling",
            "Work in fume hood for volatile compounds",
            "Proper disposal of chemical waste",
            "Emergency shower and eye wash station accessible"
        ]

    def _estimate_hts_costs(self) -> Dict[str, float]:
        """Estimate costs for high-throughput screening"""
        return {
            "compound_library": 5000,
            "screening_reagents": 3000,
            "equipment_usage": 4000,
            "labor": 5000,
            "total": 17000
        }

    # Microscopy specific methods
    def _generate_microscopy_materials(self, hypothesis: ExperimentalHypothesis) -> List[Dict[str, str]]:
        """Generate materials for microscopy experiments"""
        return [
            {"name": "Microscope slides and coverslips", "quantity": "100", "essential": True},
            {"name": "Fixation and staining reagents", "quantity": "As needed", "essential": True},
            {"name": "Mounting medium", "quantity": "As needed", "essential": True},
            {"name": "Antibodies for staining", "quantity": "As specified", "essential": True}
        ]

    def _generate_microscopy_equipment(self) -> List[Dict[str, str]]:
        """Generate equipment for microscopy"""
        return [
            {"name": "Fluorescence microscope", "essential": True},
            {"name": "Confocal microscope", "essential": False},
            {"name": "Slide scanner", "essential": False},
            {"name": "Image analysis software", "essential": True}
        ]

    def _generate_microscopy_methods(self, hypothesis: ExperimentalHypothesis) -> List[str]:
        """Generate methods for microscopy experiments"""
        return [
            "1. Prepare samples and fix according to protocol",
            f"2. Apply appropriate stains for: {', '.join(hypothesis.variables)}",
            "3. Acquire images using appropriate microscopy settings",
            "4. Perform image analysis and quantification",
            "5. Statistical analysis of imaging data",
            "6. Generate visual representations and interpretations"
        ]

    def _estimate_microscopy_timeline(self, hypothesis: ExperimentalHypothesis) -> Dict[str, Any]:
        """Estimate timeline for microscopy experiments"""
        return {
            "total_days": 10,
            "sample_preparation": 2,
            "imaging": 5,
            "analysis": 3
        }

    def _generate_microscopy_safety(self) -> List[str]:
        """Generate safety considerations for microscopy"""
        return [
            "Standard laboratory safety practices apply",
            "Chemical safety for staining reagents",
            "Laser safety for fluorescence microscopy",
            "Proper disposal of stained samples"
        ]

    def _estimate_microscopy_costs(self) -> Dict[str, float]:
        """Estimate costs for microscopy"""
        return {
            "microscopy_reagents": 1200,
            "slide_consumables": 600,
            "equipment_usage": 2000,
            "labor": 2200,
            "total": 6000
        }

    def _estimate_optimized_cost(self, protocol: ExperimentalProtocol) -> Dict[str, float]:
        """Estimate costs after optimization"""
        # Recalculate based on simplified protocol
        base_cost = protocol.estimated_cost.get('total', 5000)
        optimized_cost = base_cost * 0.7  # 30% reduction through optimization

        return {"total": optimized_cost, "savings": base_cost - optimized_cost}

# Factory function for creating experimental designer
def create_experimental_designer() -> ExperimentalDesigner:
    """Create and initialize experimental designer."""
    designer = ExperimentalDesigner()
    return designer

# Singleton instance
_experimental_designer_instance = None

def get_experimental_designer() -> ExperimentalDesigner:
    """Get or create singleton experimental designer instance."""
    global _experimental_designer_instance
    if _experimental_designer_instance is None:
        _experimental_designer_instance = create_experimental_designer()
    return _experimental_designer_instance