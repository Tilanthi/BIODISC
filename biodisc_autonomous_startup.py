#!/usr/bin/env python3
"""
BIODISC Autonomous Startup Script

This script starts BIODISC with autonomous discovery enabled.
User queries always take priority over autonomous operations.
"""

import logging
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start BIODISC with autonomous discovery"""

    print("🧬 Starting BIODISC V5.0 - Biology Discovery and Intelligence System")
    print("=" * 70)

    try:
        # Apply V73 integration fix
        print("🔧 Applying V73 autonomous discovery integration fix...")
        try:
            from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
            add_identify_knowledge_gaps_method()
            print("✅ V73 integration fix applied successfully")
        except Exception as e:
            print(f"⚠️  Could not apply V73 fix: {e}")

        from biodisc_core import create_biodisc_system
        from biodisc_core.core.unified_enhanced import EnhancedUnifiedConfig

        # Configure BIODISC with autonomous discovery enabled
        config = EnhancedUnifiedConfig(
            enable_autonomous=True,  # Enable autonomous discovery
            autonomous_config={
                # Resource limits
                'max_cpu_percent': 80.0,
                'max_hours_per_week': 168.0,
                'max_memory_percent': 80.0,
                'idle_timeout_minutes': 2,  # Start autonomous after 2 minutes idle

                # V74 Genuine Discovery Filter settings
                'enable_genuine_discovery_filter': True,
                'require_published_data_sources': True,
                'computational_novelty_threshold': 0.7,
                'synthesis_quality_threshold': 0.6,
                'allow_literature_lookup_questions': False,
                'allow_definition_questions': False,

                # Enable all autonomous components
                'enable_v73_discovery': True,
                'enable_v60_swarm': True,
                'enable_v93_metacognition': True,
                'enable_self_modification': True,
                'enable_sub_agent_spawning': True,

                # Discovery settings
                'discovery_validation_mode': 'strict',
                'min_discovery_confidence': 0.50,  # Lowered to enable goal generation
                'min_discovery_novelty': 0.60,
                'discoveries_per_cycle': 10,
                'discovery_cycle_interval_seconds': 30  # Check every 30 seconds
            }
        )

        print("🚀 Creating BIODISC system with autonomous discovery...")
        system = create_biodisc_system(config)

        print("✅ BIODISC system started successfully!")
        print()
        print("🤖 Autonomous Discovery Status:")

        if system.autonomous_orchestrator:
            print(f"   State: {system.autonomous_orchestrator.autonomous_state.value}")
            print(f"   Loop Active: {system.autonomous_orchestrator.autonomous_loop_active}")
            print(f"   Idle Timeout: {system.autonomous_orchestrator.config.idle_timeout_minutes} minutes")
            print()
            print("⚡ User Priority Protocol:")
            print("   • User queries IMMEDIATELY pause autonomous operations")
            print("   • Autonomous resumes after 2 minutes of idle time")
            print("   • All processing resources prioritized for user requests")
        else:
            print("   ❌ Autonomous orchestrator not available")
            print("   System running in reactive mode only")

        print()
        print("🧬 BIODISC Ready for User Queries!")
        print("   • Ask biology questions for immediate analysis")
        print("   • Autonomous discovery runs during idle periods")
        print("   • Type 'status' to check autonomous discovery progress")
        print("   • Type 'exit' to shutdown the system")
        print()

        # Simple interactive loop
        while True:
            try:
                query = input("BIODISC> ").strip()

                if not query:
                    continue

                if query.lower() == 'exit':
                    print("🛑 Shutting down BIODISC...")
                    break

                if query.lower() == 'status':
                    if system.autonomous_orchestrator:
                        print(f"Autonomous State: {system.autonomous_orchestrator.autonomous_state.value}")
                        print(f"Cycles Completed: {system.autonomous_orchestrator.discovery_cycle_count}")
                        print(f"Discoveries Made: {len(system.autonomous_orchestrator.discoveries_made)}")
                        print(f"Discoveries Validated: {len(system.autonomous_orchestrator.discoveries_validated)}")
                    else:
                        print("No autonomous orchestrator available")
                    continue

                # Process user query (autonomous automatically pauses)
                print(f"🔄 Processing: {query}")
                result = system.answer(query)

                print(f"📊 Answer: {result.get('answer', 'No answer generated')}")
                print()

            except KeyboardInterrupt:
                print("\n🛑 Interrupt received. Type 'exit' to shutdown.")
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Failed to start BIODISC: {e}")
        logger.error(f"Startup failed: {e}", exc_info=True)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())