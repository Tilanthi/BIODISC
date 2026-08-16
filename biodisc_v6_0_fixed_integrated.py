#!/usr/bin/env python3
# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
BIODISC V6.0-FIXED INTEGRATED SYSTEM

This is the COMPLETE integration of:
✅ V6.0 Architectural Enhancements (graded autonomy, epistemic prevention, hybrid discovery)
✅ FIXED Discovery Pipeline (genuine scientific discoveries with real statistics)

This unified system provides:
1. Advanced AI capabilities for autonomous exploration
2. Genuine scientific discovery generation with real data
3. External validation (no self-scoring)
4. Anti-stall mechanisms and error recovery
5. Session persistence and restart capability

Date: 2026-07-05
Version: 6.0-FIXED-INTEGRATED
"""

import sys
import os
import signal
import logging
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import V6.0 architecture components
try:
    from biodisc_core.v6_architecture.graded_autonomy import (
        get_graded_autonomy_controller, AutonomyLevel, DiscoveryContext
    )
    from biodisc_core.v6_architecture.epistemic_collapse_prevention import (
        get_epistemic_collapse_prevention
    )
    from biodisc_core.v6_architecture.hybrid_discovery_engine import (
        get_hybrid_discovery_engine, HybridDiscoveryResult
    )
    from biodisc_core.v6_architecture.domain_method_alignment import (
        get_domain_method_optimizer, MethodType
    )
    from biodisc_core.v6_architecture.active_epistemic_exploration import (
        get_active_epistemic_explorer, ExplorationExperiment
    )
except ImportError as e:
    print(f"Warning: Could not import V6.0 components: {e}")
    print("Using fallback implementations...")

# Import FIXED pipeline components
try:
    from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import (
        create_fixed_discovery_orchestrator
    )
    from biodisc_core.fixed_pipeline.dataset_verification import create_dataset_verifier
    from biodisc_core.fixed_pipeline.differential_expression import create_differential_expression_analyzer
    from biodisc_core.fixed_pipeline.pathway_analysis import create_pathway_analyzer
    from biodisc_core.fixed_pipeline.external_validation import create_external_validation_system
except ImportError as e:
    print(f"Warning: Could not import FIXED pipeline: {e}")
    print("Genuine discovery not available...")

# Configure logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "biodisc_v6_0_fixed_integrated.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class V6FixedIntegratedSystem:
    """
    Complete integration of V6.0 architectural enhancements with FIXED discovery pipeline.

    This system provides:
    1. V6.0 autonomous exploration and question generation
    2. FIXED genuine scientific discovery with real statistics
    3. Anti-stall mechanisms and error recovery
    4. Session persistence and restart capability
    """

    def __init__(self):
        logger.info("🧬 Initializing BIODISC V6.0-FIXED Integrated System")

        # Initialize V6.0 components
        try:
            self.graded_autonomy = get_graded_autonomy_controller()
            logger.info("🎛️  Graded Autonomy Controller initialized")

            self.epistemic_prevention = get_epistemic_collapse_prevention()
            logger.info("🛡️  Epistemic Collapse Prevention System initialized")

            self.hybrid_engine = get_hybrid_discovery_engine()
            logger.info("🧠 Hybrid Discovery Engine initialized")

            self.domain_optimizer = get_domain_method_optimizer()
            logger.info("🎯 Domain-Method Alignment Optimizer initialized")

            self.active_explorer = get_active_epistemic_explorer()
            logger.info("🔭 Active Epistemic Explorer initialized")

        except Exception as e:
            logger.warning(f"V6.0 components not fully available: {e}")

        # Initialize FIXED pipeline
        try:
            self.fixed_orchestrator = create_fixed_discovery_orchestrator()
            logger.info("🔬 FIXED Discovery Orchestrator initialized")

            self.dataset_verifier = create_dataset_verifier()
            self.expression_analyzer = create_differential_expression_analyzer()
            self.pathway_analyzer = create_pathway_analyzer()
            self.external_validator = create_external_validation_system()

            logger.info("✅ All FIXED pipeline components initialized")

        except Exception as e:
            logger.warning(f"FIXED pipeline not fully available: {e}")

        # System state
        self.running = False
        self.discoveries_made = 0
        self.start_time = None
        self.last_activity = time.time()
        self.session_file = project_root / "session_state_v6_fixed.json"

        # Anti-stall mechanisms
        self.last_progress = time.time()
        self.stall_threshold = 300  # 5 minutes without progress
        self.user_activity_timeout = 120  # 2 minutes

        # Load previous session
        self.load_session()

    def load_session(self):
        """Load previous session state"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)

                logger.info(f"📂 Loaded V6.0-FIXED session from {session_data.get('timestamp', 'unknown')}")
                logger.info(f"   Version: {session_data.get('version', 'unknown')}")
                logger.info(f"   Previous discoveries: {session_data.get('discovery_count', 0)}")

                self.discoveries_made = session_data.get('discovery_count', 0)

        except Exception as e:
            logger.warning(f"Could not load session: {e}")

    def save_session(self):
        """Save current session state"""
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'mode': 'autonomous',
                'running': self.running,
                'discovery_count': self.discoveries_made,
                'version': '6.0-FIXED-INTEGRATED',
                'components_operational': [
                    'graded_autonomy',
                    'epistemic_prevention',
                    'hybrid_discovery',
                    'fixed_pipeline',
                    'domain_alignment',
                    'active_exploration',
                    'anti_stall',
                    'session_persistence'
                ]
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Could not save session: {e}")

    def check_user_activity(self) -> bool:
        """Check if user is active"""
        current_time = time.time()
        time_since_last_activity = current_time - self.last_activity

        if time_since_last_activity < self.user_activity_timeout:
            return True

        return False

    def generate_research_questions(self) -> List[str]:
        """Generate research questions using V6.0 active exploration"""
        try:
            # Use active epistemic exploration to generate questions
            experiments = self.active_explorer.design_exploration_agenda(
                knowledge_state={},
                exploration_budget=10
            )

            questions = []
            for exp in experiments[:5]:  # Top 5 experiments
                questions.append(exp.question)

            logger.info(f"🔭 Generated {len(questions)} research questions")
            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return ["How does gene expression change in cancer cells?"]

    def make_genuine_discovery(self, question: str) -> Optional[Dict]:
        """DISABLED: this legacy path used SYNTHETIC data, which violates the
        BIODISC "no synthetic data in the discovery path" rule.

        P0.3b (integrity follow-up): this method previously generated fake
        expression data (GENE_#### identifiers, dataset_id=SYNTHETIC_<ts>) and
        ran DE analysis on it, producing pseudo-scientific "discoveries". It is
        NOT referenced by the active watchdog/loop (which uses
        FixedDiscoveryOrchestrator with real GEO data), but it was a dormant
        integrity landmine. It now refuses, mirroring the disabled
        `_simulate_realistic_geo_data`.

        For genuine discovery, use the real-data orchestrator:
            FixedDiscoveryOrchestrator.generate_genuine_discovery(question, geo_id)
        """
        logger.error("❌ FATAL: biodisc_v6_0_fixed_integrated.make_genuine_discovery() is DISABLED")
        logger.error("   It used SYNTHETIC data, which is forbidden in the discovery path.")
        logger.error("   Use FixedDiscoveryOrchestrator.generate_genuine_discovery() with a real dataset id.")
        raise RuntimeError(
            "make_genuine_discovery() is DISABLED (P0.3b): it used synthetic data, "
            "which is forbidden in the discovery path. Use "
            "FixedDiscoveryOrchestrator.generate_genuine_discovery(question, geo_id) "
            "with a real dataset instead."
        )

    def save_discovery(self, discovery: Dict):
        """Save discovery to file.

        BYPASS WRITE NEUTRALIZED (audit 2026-07-17): direct unverified writes to
        the genuine store are forbidden. All discoveries must route through
        biodisc_core.fixed_pipeline.discovery_store.append_verified, which
        requires a machine verification block. This legacy method now refuses.
        """
        raise RuntimeError(
            "Direct unverified write to autonomous_discoveries.jsonl is disabled. "
            "Route through biodisc_core.fixed_pipeline.discovery_store.append_verified."
        )

    def check_stall(self) -> bool:
        """Check if system is stalled"""
        time_since_progress = time.time() - self.last_progress

        if time_since_progress > self.stall_threshold:
            logger.warning(f"⚠️  System stalled: {time_since_progress:.0f}s without progress")
            return True

        return False

    def discovery_cycle(self):
        """Run one complete discovery cycle"""

        # Check for user activity
        if self.check_user_activity():
            logger.info("👤 User active - pausing discovery")
            time.sleep(30)
            return

        # Check for stall
        if self.check_stall():
            logger.warning("🔄 System stalled - restarting cycle")
            self.last_progress = time.time()
            return

        try:
            # Step 1: Generate research question
            logger.info("🔭 Step 1: Generate research question")
            questions = self.generate_research_questions()

            if not questions:
                logger.warning("No questions generated - skipping cycle")
                return

            question = questions[0]
            logger.info(f"   Selected question: {question[:60]}...")

            # Step 2: Make genuine discovery
            logger.info("🔬 Step 2: Make genuine discovery")
            discovery = self.make_genuine_discovery(question)

            if discovery:
                # Step 3: Save discovery
                logger.info("💾 Step 3: Save discovery")
                self.save_discovery(discovery)

                # Step 4: Update session
                self.save_session()

                logger.info(f"✅ Discovery cycle complete. Total discoveries: {self.discoveries_made}")
            else:
                logger.warning("⚠️  Discovery failed - continuing to next cycle")

        except Exception as e:
            logger.error(f"❌ Discovery cycle error: {e}", exc_info=True)

    def run_autonomous_discovery(self):
        """Run continuous autonomous discovery"""

        logger.info("🚀 Starting V6.0-FIXED autonomous discovery")
        logger.info("=" * 80)
        logger.info("🎯 V6.0-FIXED INTEGRATED ARCHITECTURE:")
        logger.info("   ✅ V6.0 Architectural Enhancements (graded autonomy, epistemic prevention)")
        logger.info("   ✅ FIXED Discovery Pipeline (genuine scientific discoveries)")
        logger.info("   ✅ Anti-Stall Mechanisms (automatic recovery)")
        logger.info("   ✅ Session Persistence (restart capability)")
        logger.info("=" * 80)

        self.running = True
        self.start_time = time.time()

        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"\n🔄 Discovery Cycle #{cycle_count}")

                # Run discovery cycle
                self.discovery_cycle()

                # Save session periodically
                if cycle_count % 5 == 0:
                    self.save_session()

                # Wait before next cycle
                logger.info("⏳ Waiting 30 seconds before next cycle...")
                time.sleep(30)

            except KeyboardInterrupt:
                logger.info("🛑 Interrupted by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Fatal error in discovery loop: {e}", exc_info=True)
                time.sleep(60)  # Wait before retry

        logger.info("🛑 V6.0-FIXED autonomous discovery stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum} - shutting down...")
    # System will shut down gracefully
    sys.exit(0)


def main():
    """Main entry point"""

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run system
    system = V6FixedIntegratedSystem()
    system.run_autonomous_discovery()


if __name__ == "__main__":
    main()