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
from logging.handlers import RotatingFileHandler
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
        RotatingFileHandler(log_dir / "fixed_discovery.log", maxBytes=10_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Phase B supervision: status/rejection logging + flagging gate + heartbeat yield.
from biodisc_core.fixed_pipeline import discovery_status
from biodisc_core.fixed_pipeline.discovery_gate import stamp_report
# Verification-first layer: write chokepoint + funnel instrumentation.
from biodisc_core.fixed_pipeline.discovery_store import (
    append_verified, build_verification_block, UnverifiedDiscoveryError,
)
from biodisc_core.fixed_pipeline.verdict_log import log_verdict, print_funnel


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

        # Shared ontology mapper for question<->dataset relevance pinning.
        try:
            from biodisc_core.fixed_pipeline.dataset_question_validation.ontology_mapper import OntologyMapper
            self._ontology_mapper = OntologyMapper()
        except Exception:
            self._ontology_mapper = None

        # Validation statistics tracking
        self.discoveries_made = 0
        self.discoveries_rejected = 0
        self.discoveries_validated = 0
        self.discovery_count = 0  # For periodic summary reporting

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
                # Yield to user tasks: if the assistant signalled activity
                # recently, sleep and skip this cycle (user astronomy tasks win;
                # discovery fills idle gaps).
                if discovery_status.is_user_active():
                    logger.info("👤 User task active — yielding (skipping discovery cycle)")
                    time.sleep(60)
                    continue

                logger.info("🔄 Starting fixed discovery cycle...")

                # Generate biological questions
                questions = self._generate_biological_questions()

                # Validity pre-filter: drop questions that have no matching
                # verified dataset, so the loop doesn't burn iterations (and
                # pollute the funnel) on unanswerable questions. This was the #1
                # funnel bucket (~33% no_datasets). It is a validity screen, not
                # an interestingness screen — a question with no data can never
                # yield a discovery, so there is zero eureka cost. It uses the
                # same matcher as the dataset search below, so it never drops a
                # question the loop would have accepted. (audit 2026-07-17)
                questions = self._filter_answerable_questions(questions)

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
                        discovery_status.record_rejection("no_datasets")
                        log_verdict({"question": question, "outcome": "rejected",
                                     "both_pass": False, "reason": "no_datasets"})
                        continue

                    # Try each dataset until one works
                    discovery_made = False
                    for j, dataset_metadata in enumerate(geo_datasets, 1):
                        dataset_id = dataset_metadata.get('id', 'Unknown')
                        sample_count = dataset_metadata.get('samples', 0)

                        logger.info(f"   Trying dataset {j}/{len(geo_datasets)}: {dataset_id} ({sample_count} samples)")

                        try:
                            # Generate GENUINE discovery using REAL GEO dataset
                            discovery_report = self.orchestrator.generate_genuine_discovery(
                                question=question,
                                geo_dataset_id=dataset_id
                            )

                            if discovery_report:
                                # Add comprehensive validation statistics logging
                                # Note: These keys come from validate_discovery_comprehensive() 5-layer validation
                                validation_stats = discovery_report.get('comprehensive_validation_statistics', {})

                                logger.info("📊 COMPREHENSIVE VALIDATION STATISTICS:")
                                logger.info(f"   Duplicate Detection: {validation_stats.get('duplicate_detection', {})}")
                                logger.info(f"   Dataset-Question Validation: {validation_stats.get('dataset_question_validation', {})}")
                                logger.info(f"   Probe-Gene Mapping: {validation_stats.get('probe_gene_mapping', {})}")
                                logger.info(f"   FDR Significance Gate: {validation_stats.get('fdr_significance_gate', {})}")
                                logger.info(f"   Template Detection: {validation_stats.get('template_detection', {})}")

                                # Save the discovery
                                self.save_discovery(discovery_report)
                                discoveries_made_this_cycle += 1
                                self.discoveries_made += 1
                                self.discoveries_validated += 1
                                self.discovery_count += 1
                                discovery_made = True

                                logger.info(f"✅ Discovery {i} generated and saved using dataset {dataset_id}")
                                logger.info(f"   All validation gates PASSED")

                                # Log validation summary every 10 discoveries
                                if self.discovery_count % 10 == 0:
                                    self.log_validation_summary()

                                break  # Success! Don't try other datasets for this question
                            else:
                                logger.info(f"❌ Discovery {i} failed validation with dataset {dataset_id}")
                                self.discoveries_rejected += 1
                                discovery_status.record_rejection("orchestrator_none")
                                log_verdict({"question": question, "dataset_id": dataset_id,
                                             "outcome": "rejected", "both_pass": False,
                                             "reason": "generation_failed_before_or_at_validation"})
                                logger.info(f"   Trying next dataset...")

                        except Exception as e:
                            logger.error(f"Error processing question {i} with dataset {dataset_id}: {e}")
                            discovery_status.record_rejection("exception")
                            log_verdict({"question": question, "dataset_id": dataset_id,
                                         "outcome": "rejected", "both_pass": False,
                                         "reason": f"exception: {type(e).__name__}"})
                            continue

                    if not discovery_made:
                        logger.warning(f"❌ Question {i} failed with all available datasets")

                logger.info(f"\n📊 Discovery cycle complete: {discoveries_made_this_cycle} discoveries")
                discovery_status.record_cycle(discoveries_made_this_cycle)

                # Save session state
                self.save_session_state()

                # Robust rest mechanism with sleep detection
                logger.info("💤 Resting before next discovery cycle...")
                cycle_start = time.time()

                # Use smaller sleep intervals for better sleep/wake handling
                for i in range(30):  # 30 intervals of 10 seconds = 5 minutes total
                    time.sleep(10)  # 10 second intervals are more resilient

                    # Check if we've been asleep (system time jump detection)
                    elapsed = time.time() - cycle_start
                    if elapsed > 600:  # If more than 10 minutes elapsed, system was asleep
                        logger.warning(f"⚠️  System sleep detected (elapsed: {elapsed:.1f}s)")
                        logger.info("🔄 Restarting discovery cycle after sleep...")
                        break  # Break to start fresh discovery cycle

                # If we broke out of sleep due to system sleep detection, continue to next iteration
                if elapsed > 600:
                    continue  # Skip to next while loop iteration

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
        """Return the VERIFIED datasets biologically relevant to a question, or [].

        Pins the question to its matching dataset(s) via
        ``select_datasets_for_question`` (organism/tissue/disease entity overlap
        on canonical IDs). If NO dataset is biologically relevant to the question,
        returns [] so the loop SKIPS it — we do not rotate an unmatched question
        onto an unrelated dataset, because that yields an incoherent candidate
        (e.g. a glioblastoma question on a breast-cancer dataset) that the
        entity-sparse validator cannot catch. You cannot honestly answer a
        question with data that has no biological relation to it.
        """
        try:
            from biodisc_core.fixed_pipeline.real_datasets import REAL_GEO_DATASETS
            from biodisc_core.fixed_pipeline.specific_questions import select_datasets_for_question

            datasets = select_datasets_for_question(
                question, REAL_GEO_DATASETS, mapper=self._ontology_mapper,
                max_results=max_results,
            )

            if datasets:
                logger.info(f"✅ Pinned {len(datasets)} VERIFIED dataset(s) relevant to question")
                for i, dataset in enumerate(datasets, 1):
                    logger.info(f"   {i}. {dataset.get('id', 'Unknown')}: {dataset.get('samples', 0)} samples - {dataset.get('title', 'Unknown')[:50]}")
            else:
                logger.info(f"↪ No verified dataset is biologically relevant to this "
                            f"question — skipping (quality gate prevents incoherent pairing)")

            return datasets

        except Exception as e:
            logger.error(f"❌ Error loading verified datasets: {e}")
            return []

    def _filter_answerable_questions(self, questions: List[str]) -> List[str]:
        """Drop questions that have no biologically-matching verified dataset.

        A question with no dataset home is definitionally unanswerable under the
        current verified pool — it can only produce a ``no_datasets`` rejection
        and pollute the funnel. This pre-filter removes such questions *before*
        the loop iterates, so cycles focus on questions that can actually yield a
        discovery. It is a VALIDITY screen (not interestingness): zero eureka
        cost, because a question with no data can never be a eureka. It uses the
        same matcher as :meth:`_search_real_geo_datasets`, so it never drops a
        question the loop would have accepted. Fails open on import error.
        (audit 2026-07-17)
        """
        try:
            from biodisc_core.fixed_pipeline.real_datasets import REAL_GEO_DATASETS
            from biodisc_core.fixed_pipeline.specific_questions import select_datasets_for_question
        except Exception as e:
            logger.warning(f"Could not import dataset matcher for pre-filter (failing open): {e}")
            return questions

        answerable = [
            q for q in questions
            if select_datasets_for_question(q, REAL_GEO_DATASETS, mapper=self._ontology_mapper)
        ]
        dropped = len(questions) - len(answerable)
        if dropped:
            logger.info(f"↪ Pre-filter dropped {dropped}/{len(questions)} question(s) with no "
                        f"matching dataset (would have been no_datasets); "
                        f"{len(answerable)} answerable remain")
        return answerable

    def _generate_biological_questions(self) -> List[str]:
        """
        Generate SPECIFIC biological questions using SpecificQuestionsGenerator.

        Replaces generic questions with specific, novel questions.
        """

        try:
            from biodisc_core.fixed_pipeline.specific_questions import create_specific_questions_generator
            generator = create_specific_questions_generator()
            # Use the diverse + dataset-aligned, shuffled pool so each cycle
            # varies which question is attempted first (reduces duplicate-
            # statistical-profile rejections from re-running one combo).
            questions = generator.generate_question_pool()

            logger.info(f"✅ Generated {len(questions)} biological questions "
                        f"(diverse + dataset-aligned, shuffled)")
            logger.info("   (Replaces generic questions for genuine novelty)")

            return questions

        except Exception as e:
            logger.warning(f"Could not use specific questions generator: {e}")
            # Fallback to basic questions
            logger.warning("   Using fallback basic questions")
            questions = [
                "How does gene expression change between specific conditions?",
                "What specific genes regulate cellular differentiation?",
                "How do signaling pathways respond to stimuli?",
            ]

            return questions

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
        """Save a discovery through the write CHOKEPOINT (the single legal write path).

        The chokepoint requires a machine verification block — fiction (an
        unverified/hallucinated record) is structurally impossible to store.
        The flagging tier (genuine vs candidate_unconfirmed) routes the record to
        the verified store or the candidate quarantine. Genuine requires
        replication; single-cohort findings are quarantined, never asserted as
        new knowledge.
        """
        try:
            stamped, decision = stamp_report(discovery_report)
            verification = build_verification_block(stamped)
            try:
                target = append_verified(stamped, verification)
            except UnverifiedDiscoveryError as e:
                logger.error(f"❌ CHOKEPOINT refused write (fiction prevented): {e}")
                return

            discovery_status.record_validated_discovery(
                stamped.get('discovery_id', stamped.get('discoveryId', '')))
            logger.info(f"💾 Discovery stored via chokepoint [{decision.tier}] "
                        f"(is_genuine={decision.is_genuine}) -> {target}")

        except Exception as e:
            logger.error(f"Failed to save discovery: {e}")

    def save_session_state(self):
        """Save session state"""

        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'running': self.running,
                'discoveries_made': self.orchestrator.discoveries_made if self.orchestrator else 0,
                'discoveries_rejected': self.orchestrator.discoveries_rejected if self.orchestrator else 0,
                'discoveries_validated': self.orchestrator.discoveries_validated if self.orchestrator else 0,
                'session_discoveries_made': self.discoveries_made,
                'session_discoveries_rejected': self.discoveries_rejected,
                'session_discoveries_validated': self.discoveries_validated,
                'discovery_count': self.discovery_count,
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

                # Load validation statistics
                self.discoveries_made = state.get('session_discoveries_made', 0)
                self.discoveries_rejected = state.get('session_discoveries_rejected', 0)
                self.discoveries_validated = state.get('session_discoveries_validated', 0)
                self.discovery_count = state.get('discovery_count', 0)

                logger.info(f"   Session discoveries made: {self.discoveries_made}")
                logger.info(f"   Session discoveries rejected: {self.discoveries_rejected}")

        except Exception as e:
            logger.info("No previous session state found")

    def log_validation_summary(self):
        """Log summary of validation statistics."""
        logger.info("📊 VALIDATION SUMMARY:")
        logger.info("=" * 60)

        # Get statistics from orchestrator if available
        if self.orchestrator:
            logger.info(f"   Orchestrator Discoveries Made: {self.orchestrator.discoveries_made}")
            logger.info(f"   Orchestrator Discoveries Rejected: {self.orchestrator.discoveries_rejected}")
            logger.info(f"   Orchestrator Discoveries Validated: {self.orchestrator.discoveries_validated}")

            # Get peer review validator statistics
            if hasattr(self.orchestrator, 'peer_review_validator'):
                validator = self.orchestrator.peer_review_validator
                logger.info(f"   Peer Review Validations: {validator.validations_performed}")
                logger.info(f"   Peer Review Rejections: {validator.rejections}")
                if validator.validations_performed > 0:
                    peer_review_rejection_rate = (validator.rejections / validator.validations_performed) * 100
                    logger.info(f"   Peer Review Rejection Rate: {peer_review_rejection_rate:.2f}%")

        logger.info(f"   Session Total Discoveries Made: {self.discoveries_made}")
        logger.info(f"   Session Total Discoveries Rejected: {self.discoveries_rejected}")
        logger.info(f"   Session Total Discoveries Validated: {self.discoveries_validated}")

        if self.discoveries_made > 0:
            rejection_rate = (self.discoveries_rejected / self.discoveries_made) * 100
            logger.info(f"   Session Rejection Rate: {rejection_rate:.2f}%")

        # Surface the discovery funnel: where candidates actually die.
        logger.info(print_funnel())

        logger.info("=" * 60)


if __name__ == "__main__":
    discovery_system = FixedAutonomousDiscovery()
    discovery_system.start()