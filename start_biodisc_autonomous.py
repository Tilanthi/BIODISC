#!/usr/bin/env python3
"""
BIODISC Background Autonomous Startup

Starts BIODISC autonomous discovery in background mode for continuous operation.
User priority protocol ensures immediate responsiveness to any user interaction.
"""

import logging
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('biodisc_autonomous.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Start BIODISC autonomous discovery in background"""

    logger.info("🧬 BIODISC V5.0 - Background Autonomous Discovery Starting")
    logger.info("=" * 70)

    try:
        # Apply V73 integration fixes
        logger.info("🔧 Applying V73 autonomous discovery integration fixes...")
        try:
            import sys
            sys.path.insert(0, '.')
            from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
            add_identify_knowledge_gaps_method()
            logger.info("✅ Knowledge gap identification fix applied")

            from biodisc_core.reasoning.v73_explore_question_fix import add_explore_question_method
            add_explore_question_method()
            logger.info("✅ Question exploration fix applied")

            logger.info("✅ All V73 integration fixes applied successfully")
        except Exception as e:
            logger.warning(f"Could not apply V73 fixes: {e}")

        from biodisc_core import create_biodisc_system
        from biodisc_core.core.unified_enhanced import EnhancedUnifiedConfig

        # Configure for autonomous operation
        config = EnhancedUnifiedConfig(
            enable_autonomous=True,
            autonomous_config={
                # Realistic resource usage for background operation
                'max_cpu_percent': 80.0,  # Allow up to 80% CPU usage
                'max_hours_per_week': 168.0,
                'max_memory_percent': 80.0,  # Allow up to 80% memory usage
                'idle_timeout_minutes': 1,  # Quick start when idle

                # V74 Genuine Discovery Filter (strict)
                'enable_genuine_discovery_filter': True,
                'require_published_data_sources': True,
                'computational_novelty_threshold': 0.7,
                'synthesis_quality_threshold': 0.6,
                'allow_literature_lookup_questions': False,
                'allow_definition_questions': False,

                # All autonomous components enabled
                'enable_v73_discovery': True,
                'enable_v60_swarm': True,
                'enable_v93_metacognition': True,
                'enable_self_modification': True,
                'enable_sub_agent_spawning': True,

                # Discovery settings for continuous operation
                'discovery_validation_mode': 'strict',
                'min_discovery_confidence': 0.50,  # Lowered to enable goal generation
                'min_discovery_novelty': 0.60,
                'discoveries_per_cycle': 5,
                'discovery_cycle_interval_seconds': 60  # Check every minute
            }
        )

        logger.info("🚀 Initializing BIODISC system with autonomous discovery...")
        system = create_biodisc_system(config)

        if system.autonomous_orchestrator:
            logger.info("✅ BIODISC autonomous discovery started successfully!")
            logger.info(f"🤖 Autonomous State: {system.autonomous_orchestrator.autonomous_state.value}")
            logger.info(f"🔄 Loop Active: {system.autonomous_orchestrator.autonomous_loop_active}")
            logger.info(f"⏰ Idle Timeout: {system.autonomous_orchestrator.config.idle_timeout_minutes} minutes")
            logger.info("")
            logger.info("⚡ User Priority Protocol Active:")
            logger.info("   • User queries IMMEDIATELY pause autonomous operations")
            logger.info("   • Autonomous resumes after 1 minute of idle time")
            logger.info("   • All processing resources prioritized for user requests")
            logger.info("")
            logger.info("🧬 BIODISC Ready for Autonomous Discovery!")
            logger.info("   • System will conduct autonomous research during idle periods")
            logger.info("   • All discoveries validated with V74 Genuine Discovery Filter")
            logger.info("   • Genuine discoveries stored in memory palace")
            logger.info("")
            logger.info("📊 System Status:")
            logger.info(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"   Running in: {Path.cwd()}")
            logger.info(f"   Log file: biodisc_autonomous.log")
            logger.info("")
            logger.info("💡 Use biodisc_autonomous_startup.py for interactive mode")
            logger.info("💡 Monitor this log for autonomous discovery progress")
            logger.info("")
            logger.info("🔬 Autonomous Discovery Cycles Beginning...")
            logger.info("=" * 70)

            # Keep the main thread alive and periodically report status
            try:
                while True:
                    time.sleep(300)  # Report every 5 minutes

                    # Log status update
                    orchestrator = system.autonomous_orchestrator
                    logger.info("")
                    logger.info("📊 Autonomous Discovery Status Update:")
                    logger.info(f"   State: {orchestrator.autonomous_state.value}")
                    logger.info(f"   Cycles Completed: {orchestrator.discovery_cycle_count}")
                    logger.info(f"   Discoveries Made: {len(orchestrator.discoveries_made)}")
                    logger.info(f"   Discoveries Validated: {len(orchestrator.discoveries_validated)}")
                    logger.info(f"   Weekly Usage: {orchestrator.weekly_usage_hours:.1f} hours")
                    logger.info(f"   Last User Activity: {orchestrator.last_user_activity.strftime('%Y-%m-%d %H:%M:%S')}")

                    if orchestrator.discoveries_validated:
                        logger.info(f"   ✅ Recent Validated Discoveries:")
                        for discovery in orchestrator.discoveries_validated[-3:]:
                            logger.info(f"      • {discovery.title[:60]}...")

                    logger.info("=" * 70)

            except KeyboardInterrupt:
                logger.info("🛑 Shutting down BIODISC autonomous discovery...")

        else:
            logger.error("❌ Autonomous orchestrator not available")
            logger.error("System running in reactive mode only")
            return 1

    except Exception as e:
        logger.error(f"❌ Failed to start BIODISC autonomous discovery: {e}")
        logger.error(f"Error details: {e}", exc_info=True)
        return 1

    logger.info("👋 BIODISC autonomous discovery shutdown complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())