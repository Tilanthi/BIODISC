"""
V80-V85 Integration System: Novel Biological Discovery Capabilities

Integrates V80-V85 into a cohesive novel discovery system.
This enables BIODISC to move from characterizing existing biology to
generating genuinely new biological insights.

Date: 2026-05-09
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Import V80-V85 components
try:
    from .v80_experimental_design import ExperimentalDesignEngine, get_experimental_design_engine
    V80_AVAILABLE = True
except ImportError:
    V80_AVAILABLE = False

try:
    from .v81_quantitative_prediction import QuantitativeBioEngine, get_quantitative_bio_engine
    V81_AVAILABLE = True
except ImportError:
    V81_AVAILABLE = False

try:
    from .v82_live_database_integration import LiveBioDatabaseIntegration, get_live_bio_database_integration
    V82_AVAILABLE = True
except ImportError:
    V82_AVAILABLE = False

try:
    from .v83_causal_validation import CausalValidationEngine, get_causal_validation_engine
    V83_AVAILABLE = True
except ImportError:
    V83_AVAILABLE = False

try:
    from .v84_active_literature_learning import ActiveLiteratureLearning, get_active_literature_learning
    V84_AVAILABLE = True
except ImportError:
    V84_AVAILABLE = False

try:
    from .v85_hypothesis_generation import HypothesisGenerator, get_hypothesis_generator
    V85_AVAILABLE = True
except ImportError:
    V85_AVAILABLE = False


class NovelDiscoveryOrchestrator:
    """
    Main orchestrator for novel biological discovery.

    INTEGRATES:
    - V80: Experimental Design (design experiments to test hypotheses)
    - V81: Quantitative Prediction (make quantitative predictions)
    - V82: Live Database Integration (real-time access to knowledge)
    - V83: Causal Validation (distinguish correlation from causation)
    - V84: Active Literature Learning (continuous pattern discovery)
    - V85: Hypothesis Generation (generate novel hypotheses)

    WORKFLOW:
    1. Generate novel hypotheses (V85)
    2. Check databases for related knowledge (V82)
    3. Make quantitative predictions (V81)
    4. Validate causal claims (V83)
    5. Design experiments (V80)
    6. Learn from literature continuously (V84)

    This enables BIODISC to move beyond characterization to genuine discovery.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.discovery_cycle_count = 0

        # Initialize components
        self.experimental_design = get_experimental_design_engine() if V80_AVAILABLE else None
        self.quantitative_prediction = get_quantitative_bio_engine() if V81_AVAILABLE else None
        self.database_integration = get_live_bio_database_integration() if V82_AVAILABLE else None
        self.causal_validation = get_causal_validation_engine() if V83_AVAILABLE else None
        self.literature_learning = get_active_literature_learning() if V84_AVAILABLE else None
        self.hypothesis_generator = get_hypothesis_generator() if V85_AVAILABLE else None

    def start_discovery_cycle(self, domain: str = "general") -> Dict[str, Any]:
        """
        Run one complete discovery cycle.

        Args:
            domain: Biological domain to focus on

        Returns:
            Summary of discovery cycle results
        """
        self.discovery_cycle_count += 1
        self.logger.info(f"=== Novel Discovery Cycle {self.discovery_cycle_count} ===")

        results = {
            "cycle_number": self.discovery_cycle_count,
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "hypotheses": [],
            "predictions": [],
            "experimental_designs": [],
            "causal_validations": [],
            "literature_discoveries": []
        }

        # Step 1: Generate novel hypotheses
        self.logger.info("Step 1: Generating novel hypotheses...")
        if self.hypothesis_generator:
            hypotheses = self.hypothesis_generator.generate_hypotheses(domain, count=10)
            results["hypotheses"] = [
                {
                    "title": h.title,
                    "type": h.hypothesis_type.value,
                    "novelty": h.novelty_level.value,
                    "testability": h.testability.value,
                    "confidence": h.confidence
                }
                for h in hypotheses[:5]
            ]
            self.logger.info(f"  Generated {len(hypotheses)} novel hypotheses")

        # Step 2: Check databases for related knowledge
        self.logger.info("Step 2: Checking databases for related knowledge...")
        if self.database_integration:
            updates = self.database_integration.check_for_updates(since_days=7)
            results["database_updates"] = len(updates)
            self.logger.info(f"  Found {len(updates)} database updates")

        # Step 3: Learn from literature
        self.logger.info("Step 3: Learning from literature...")
        if self.literature_learning:
            papers = self.literature_learning.scan_papers(max_papers=200)
            results["papers_scanned"] = len(papers)
            patterns = self.literature_learning.get_discovery_summary()["total_patterns_discovered"]
            results["patterns_discovered"] = patterns
            self.logger.info(f"  Scanned {len(papers)} papers, discovered {patterns} patterns")

        # Step 4: Make quantitative predictions
        self.logger.info("Step 4: Making quantitative predictions...")
        if self.quantitative_prediction and results["hypotheses"]:
            # Make predictions for top hypotheses
            for hyp in results["hypotheses"][:3]:
                question = f"What are the quantitative predictions for: {hyp['title']}?"
                try:
                    prediction = self.quantitative_prediction.predict(question, context={"domain": domain})
                    results["predictions"].append({
                        "question": question,
                        "prediction_type": prediction.prediction_type.value,
                        "confidence": prediction.prediction_score
                    })
                except Exception as e:
                    self.logger.warning(f"  Prediction failed: {e}")
            self.logger.info(f"  Made {len(results['predictions'])} quantitative predictions")

        # Step 5: Validate causal claims
        self.logger.info("Step 5: Validating causal claims...")
        if self.causal_validation and results["hypotheses"]:
            # Validate causal claims from hypotheses
            for hyp in results["hypotheses"][:2]:
                if hyp["type"] == "mechanism":
                    try:
                        from .v83_causal_validation import CausalHypothesis, CausalType
                        causal_hyp = CausalHypothesis(
                            hypothesis_id=f"hyp_{hyp['title'][:20]}",
                            cause="unknown",
                            effect="unknown",
                            causal_type=CausalType.DIRECT,
                            description=hyp["title"],
                            context={},
                            proposed_mechanism=hyp["title"],
                            confounders=[]
                        )
                        validation = self.causal_validation.validate_causal_claim(causal_hyp)
                        results["causal_validations"].append({
                            "hypothesis": hyp["title"],
                            "method": validation.validation_method.value,
                            "support": validation.causal_support,
                            "quality": validation.evidence_quality.value
                        })
                    except Exception as e:
                        self.logger.warning(f"  Validation failed: {e}")
            self.logger.info(f"  Validated {len(results['causal_validations'])} causal claims")

        # Step 6: Design experiments
        self.logger.info("Step 6: Designing experiments...")
        if self.experimental_design and results["hypotheses"]:
            # Design experiments for top hypotheses
            for hyp in results["hypotheses"][:2]:
                if hyp["testability"] in ["testable", "highly_testable"]:
                    try:
                        design = self.experimental_design.design_experiment(hyp["title"])
                        results["experimental_designs"].append({
                            "hypothesis": hyp["title"],
                            "design_id": design.design_id,
                            "experimental_type": design.experimental_type.value,
                            "feasibility": design.feasibility.value,
                            "confidence": design.confidence
                        })
                    except Exception as e:
                        self.logger.warning(f"  Design failed: {e}")
            self.logger.info(f"  Designed {len(results['experimental_designs'])} experiments")

        # Save results
        self._save_discovery_results(results)

        return results

    def _save_discovery_results(self, results: Dict[str, Any]):
        """Save discovery cycle results"""
        try:
            import os
            import json

            os.makedirs("/Users/gjw255/.biodisc_persistent", exist_ok=True)
            results_path = "/Users/gjw255/.biodisc_persistent/novel_discovery_cycles.jsonl"

            with open(results_path, 'a') as f:
                f.write(json.dumps(results) + '\n')

        except Exception as e:
            self.logger.error(f"Error saving discovery results: {e}")

    def get_discovery_status(self) -> Dict[str, Any]:
        """Get current status of discovery system"""
        status = {
            "running": self.running,
            "cycle_count": self.discovery_cycle_count,
            "components": {
                "v80_experimental_design": V80_AVAILABLE,
                "v81_quantitative_prediction": V81_AVAILABLE,
                "v82_live_database_integration": V82_AVAILABLE,
                "v83_causal_validation": V83_AVAILABLE,
                "v84_active_literature_learning": V84_AVAILABLE,
                "v85_hypothesis_generation": V85_AVAILABLE
            },
            "components_initialized": {
                "v80_experimental_design": self.experimental_design is not None,
                "v81_quantitative_prediction": self.quantitative_prediction is not None,
                "v82_live_database_integration": self.database_integration is not None,
                "v83_causal_validation": self.causal_validation is not None,
                "v84_active_literature_learning": self.literature_learning is not None,
                "v85_hypothesis_generation": self.hypothesis_generator is not None
            }
        }

        # Add component-specific summaries
        if self.database_integration:
            status["database_summary"] = self.database_integration.get_database_summary()

        if self.literature_learning:
            status["literature_summary"] = self.literature_learning.get_discovery_summary()

        return status


def create_novel_discovery_orchestrator() -> NovelDiscoveryOrchestrator:
    """Factory function to create novel discovery orchestrator"""
    return NovelDiscoveryOrchestrator()


# Singleton instance
_instance = None

def get_novel_discovery_orchestrator() -> NovelDiscoveryOrchestrator:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_novel_discovery_orchestrator()
    return _instance
