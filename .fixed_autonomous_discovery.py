#!/usr/bin/env python3
"""
BIODISC FIXED Autonomous Discovery System V6.0

TRUE AUTONOMOUS SCIENTIFIC DISCOVERY with FIXED pipeline:
✅ Real dataset verification (no hallucination)
✅ Real differential expression analysis (actual statistics)
✅ Pathway enrichment (Fisher's exact test)
✅ External validation only (no self-scoring)
✅ Dataset verification (no fake datasets)

This REPLACES the previous pseudo-science pipeline that generated template-filled documents.

Date: 2026-07-05
Version: 6.0 - FIXED Genuine Discovery System
"""

import sys
import os
import signal
import logging
import time
from pathlib import Path
from datetime import datetime
import threading
import json
from typing import Dict, List, Optional

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "fixed_discovery.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FixedAutonomousDiscovery:
    """
    FIXED autonomous discovery system that generates GENUINE scientific discoveries.

    KEY DIFFERENCES FROM OLD PIPELINE:
    ❌ NO MORE: Template filling, pseudo-science, self-scoring
    ✅ NOW: Real statistics, external validation, genuine discoveries
    """

    def __init__(self):
        self.orchestrator = None
        self.running = False
        self.session_file = project_root / "fixed_discovery_state.json"
        self.discoveries_file = project_root / "autonomous_discoveries.jsonl"

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, saving state and shutting down...")
        self.save_session_state()
        self.stop()
        sys.exit(0)

    def start(self):
        """Start fixed autonomous discovery"""
        logger.info("🧬 BIODISC FIXED Autonomous Discovery V6.0")
        logger.info("=" * 70)
        logger.info("GENUINE AUTONOMOUS SCIENTIFIC DISCOVERY")
        logger.info("=" * 70)
        logger.info("✅ Real dataset verification (no hallucination)")
        logger.info("✅ Real differential expression analysis (actual statistics)")
        logger.info("✅ Pathway enrichment (Fisher's exact test)")
        logger.info("✅ External validation only (no self-scoring)")
        logger.info("✅ Dataset verification (no fake datasets)")
        logger.info("=" * 70)

        self.running = True

        # Load previous session state if available
        self.load_session_state()

        # Import fixed orchestrator
        try:
            from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import create_fixed_discovery_orchestrator
            self.orchestrator = create_fixed_discovery_orchestrator()
            logger.info("✅ Fixed discovery orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize fixed orchestrator: {e}")
            logger.error("❌ FIXED PIPELINE NOT AVAILABLE - CANNOT START")
            return

        # Main discovery loop
        while self.running:
            try:
                logger.info("🔄 Starting fixed discovery cycle...")

                # Generate biological questions
                questions = self._generate_biological_questions()

                if not questions:
                    logger.warning("No questions generated - waiting...")
                    time.sleep(300)
                    continue

                logger.info(f"Generated {len(questions)} biological questions")

                discoveries_made_this_cycle = 0

                for i, question in enumerate(questions, 1):
                    logger.info(f"\n🔬 Processing question {i}/{len(questions)}: {question[:60]}...")

                    # Search for REAL GEO datasets instead of synthetic test data
                    geo_datasets = self._search_real_geo_datasets(question, max_results=3)

                    if not geo_datasets:
                        logger.warning(f"❌ No GEO datasets found for question {i}, skipping...")
                        continue

                    # Try each dataset until one works
                    discovery_made = False
                    for j, dataset_metadata in enumerate(geo_datasets, 1):
                        dataset_id = dataset_metadata.get('geo_id', 'Unknown')
                        sample_count = dataset_metadata.get('sample_count', 0)

                        logger.info(f"   Trying dataset {j}/{len(geo_datasets)}: {dataset_id} ({sample_count} samples)")

                        try:
                            # Generate GENUINE discovery using REAL GEO dataset
                            discovery_report = self.orchestrator.generate_genuine_discovery(
                                question=question,
                                geo_dataset_id=dataset_id
                            )

                            if discovery_report:
                                # Save the discovery
                                self.save_discovery(discovery_report)
                                discoveries_made_this_cycle += 1
                                discovery_made = True
                                logger.info(f"✅ Discovery {i} generated and saved using dataset {dataset_id}")
                                break  # Success! Don't try other datasets for this question
                            else:
                                logger.info(f"❌ Discovery {i} failed with dataset {dataset_id}, trying next...")

                        except Exception as e:
                            logger.error(f"Error processing question {i} with dataset {dataset_id}: {e}")
                            continue

                    if not discovery_made:
                        logger.warning(f"❌ Question {i} failed with all available datasets")

                logger.info(f"\n📊 Discovery cycle complete: {discoveries_made_this_cycle} discoveries")

                # Save session state
                self.save_session_state()

                # Wait before next cycle
                logger.info("💤 Resting before next discovery cycle...")
                time.sleep(300)  # 5 minutes between cycles

            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                logger.error(f"Discovery cycle error: {e}", exc_info=True)
                logger.info("💤 Waiting before retry...")
                time.sleep(60)

    def stop(self):
        """Stop autonomous discovery"""
        logger.info("Stopping fixed autonomous discovery...")
        self.running = False
        self.save_session_state()

    def _search_real_geo_datasets(self, question: str, max_results: int = 3) -> List[Dict]:
        """Search for REAL GEO datasets instead of using synthetic test data"""
        try:
            from biodisc_core.analysis.genuine_discovery_validator import create_real_data_analyzer
            data_analyzer = create_real_data_analyzer()

            # Search for relevant GEO datasets
            datasets = data_analyzer.search_relevant_geo_datasets(question, max_results=max_results)

            if datasets:
                logger.info(f"✅ Found {len(datasets)} real GEO datasets for question")
                for i, dataset in enumerate(datasets, 1):
                    logger.info(f"   {i}. {dataset.get('geo_id', 'Unknown')}: {dataset.get('sample_count', 0)} samples")
            else:
                logger.warning(f"❌ No GEO datasets found for question")

            return datasets

        except Exception as e:
            logger.error(f"❌ Error searching GEO datasets: {e}")
            return []

    def _generate_biological_questions(self) -> List[str]:
        """Generate biological questions from knowledge gaps across ALL biology domains"""

        # COMPREHENSIVE questions spanning BIODISC's full training scope
        questions = [
            # GENE EXPRESSION (current focus)
            "How does gene expression change between treated and control cells?",
            "What genes are differentially expressed in disease vs healthy tissue?",

            # EPIGENOMICS (methylation, chromatin, histone modifications)
            "How does DNA methylation patterns change during cellular differentiation?",
            "What histone modifications regulate gene expression in cancer cells?",
            "How does chromatin accessibility differ between cell types?",

            # PROTEOMICS (protein interactions, modifications)
            "What protein-protein interaction networks are disrupted in disease?",
            "How do post-translational modifications affect protein function?",
            "Which signaling pathways are activated by cellular stress?",

            # METABOLOMICS (metabolic pathways, networks)
            "How does metabolic reprogramming support cancer cell proliferation?",
            "What metabolic pathways are differentially active in disease states?",

            # NETWORK BIOLOGY (systems, interactions)
            "How do gene regulatory networks adapt to environmental changes?",
            "What network motifs characterize healthy vs disease states?",
            "How does protein interaction network topology change in disease?",

            # SINGLE-CELL ANALYSIS (cell types, heterogeneity)
            "What cell type-specific responses occur during disease progression?",
            "How does cellular heterogeneity affect treatment response?",

            # CAUSAL MECHANISMS (disease mechanisms, drug targets)
            "What are the causal mechanisms driving drug resistance?",
            "Which molecular targets are most effective for disease intervention?",

            # COMPUTATIONAL METHODS (algorithms, bioinformatics)
            "What computational methods improve biomarker discovery?",
            "How can machine learning identify novel disease patterns?",

            # EVOLUTIONARY BIOLOGY (comparative genomics)
            "How do gene regulatory networks evolve across species?",
            "What conserved molecular mechanisms underlie disease processes?",

            # SYSTEMS BIOLOGY (integrative analysis)
            "How do multiple omics layers integrate to regulate cellular function?",
            "What emergent properties arise from molecular network interactions?",

            # CLINICAL/MEDICAL (biomarkers, patient stratification)
            "What molecular signatures predict patient outcomes?",
            "How can we stratify patients based on molecular profiles?"
        ]

        return questions

    def save_discovery(self, discovery_report: Dict):
        """Save discovery to file"""

        try:
            with open(self.discoveries_file, 'a') as f:
                f.write(json.dumps(discovery_report) + '\n')

            logger.info(f"💾 Discovery saved to {self.discoveries_file}")

        except Exception as e:
            logger.error(f"Failed to save discovery: {e}")

    def save_session_state(self):
        """Save session state"""

        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'running': self.running,
                'discoveries_made': self.orchestrator.discoveries_made if self.orchestrator else 0,
                'pipeline_version': 'FIXED_6.0'
            }

            with open(self.session_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save session state: {e}")

    def load_session_state(self):
        """Load session state"""

        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    state = json.load(f)

                logger.info(f"📂 Loaded session state from {state.get('timestamp')}")
                logger.info(f"   Pipeline version: {state.get('pipeline_version')}")
                logger.info(f"   Previous discoveries: {state.get('discoveries_made')}")

        except Exception as e:
            logger.info("No previous session state found")


if __name__ == "__main__":
    discovery_system = FixedAutonomousDiscovery()
    discovery_system.start()