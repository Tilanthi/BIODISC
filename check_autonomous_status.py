#!/usr/bin/env python3
"""
Quick check of BIODISC autonomous discovery status
"""
import sys
import time
sys.path.insert(0, '.')

try:
    from biodisc_core import create_biodisc_system
    from biodisc_core.core.unified_enhanced import EnhancedUnifiedConfig

    # Quick status check
    config = EnhancedUnifiedConfig(
        enable_autonomous=True,
        autonomous_config={
            'max_cpu_percent': 80.0,
            'idle_timeout_minutes': 1,
            'discovery_cycle_interval_seconds': 10
        }
    )

    system = create_biodisc_system(config)

    if system.autonomous_orchestrator:
        print("🧬 BIODISC Autonomous Discovery Status:")
        print(f"   State: {system.autonomous_orchestrator.autonomous_state.value}")
        print(f"   Loop Active: {system.autonomous_orchestrator.autonomous_loop_active}")
        print(f"   Cycles Completed: {system.autonomous_orchestrator.discovery_cycle_count}")
        print(f"   Discoveries Made: {len(system.autonomous_orchestrator.discoveries_made)}")
        print(f"   Discoveries Validated: {len(system.autonomous_orchestrator.discoveries_validated)}")
        print(f"   Last User Activity: {system.autonomous_orchestrator.last_user_activity}")

        # Force an idle state check
        print("\n🔍 Checking autonomous conditions...")
        from datetime import datetime
        idle_time = (datetime.now() - system.autonomous_orchestrator.last_user_activity).total_seconds() / 60
        print(f"   Idle time: {idle_time:.1f} minutes (timeout: {system.autonomous_orchestrator.config.idle_timeout_minutes} minutes)")

        should_run = system.autonomous_orchestrator._should_be_autonomous()
        print(f"   Should be autonomous: {should_run}")

        if not should_run:
            print("   Reasons:")
            if idle_time < system.autonomous_orchestrator.config.idle_timeout_minutes:
                print("      • Not idle long enough")
            if system.autonomous_orchestrator.resource_manager:
                status = system.autonomous_orchestrator.resource_manager.check_resource_availability()
                print(f"      • CPU available: {status.cpu_available} (current: {status.current_cpu_percent:.1f}% , limit: {system.autonomous_orchestrator.config.max_cpu_percent}%)")
                print(f"      • Memory available: {status.memory_available} (current: {status.current_memory_percent:.1f}% , limit: {system.autonomous_orchestrator.config.max_memory_percent}%)")
    else:
        print("❌ No autonomous orchestrator available")

except Exception as e:
    print(f"❌ Error: {e}")