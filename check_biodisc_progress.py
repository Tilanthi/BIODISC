#!/usr/bin/env python3
"""
Quick check of BIODISC autonomous discovery progress
"""
import sys
import time
sys.path.insert(0, '.')

try:
    # Apply the fix first
    from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
    add_identify_knowledge_gaps_method()

    from biodisc_core.autonomous.autonomous_orchestrator import AutonomousOrchestrator
    from biodisc_core.autonomous.config import AutonomousConfig

    # Create test orchestrator to check status
    config = AutonomousConfig(
        max_cpu_percent=80.0,
        max_memory_percent=80.0,
        idle_timeout_minutes=1
    )

    orchestrator = AutonomousOrchestrator(config)

    print("🔍 BIODISC Autonomous Discovery System Check")
    print("=" * 50)

    # Check V73 curiosity engine
    if orchestrator.v73_discovery:
        print("✅ V73 Discovery Engine: Available")
        try:
            gaps = orchestrator.v73_discovery.identify_knowledge_gaps()
            print(f"   Knowledge gaps: {len(gaps)}")
            if gaps:
                print(f"   Sample gaps:")
                for i, gap in enumerate(gaps[:3], 1):
                    print(f"      {i}. {gap[:60]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("❌ V73 Discovery Engine: Not available")

    # Check decision maker
    if orchestrator.decision_maker:
        print("✅ Decision Maker: Available")
        try:
            meta_assessment = {'knowledge_gaps': [], 'readiness': True}
            goals = orchestrator.decision_maker.generate_goals(meta_assessment)
            print(f"   Goals generated: {len(goals)}")
            if goals:
                print(f"   Sample goals:")
                for i, goal in enumerate(goals[:3], 1):
                    print(f"      {i}. {goal.description[:60]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("❌ Decision Maker: Not available")

    # Check resource availability
    if orchestrator.resource_manager:
        print("✅ Resource Manager: Available")
        try:
            status = orchestrator.resource_manager.check_resource_availability()
            print(f"   CPU available: {status.cpu_available} (current: {status.current_cpu_percent:.1f}%)")
            print(f"   Memory available: {status.memory_available} (current: {status.current_memory_percent:.1f}%)")
            print(f"   Can operate: {status.can_operate()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("❌ Resource Manager: Not available")

    print("\n🔧 System Diagnosis:")
    print(f"   Should be autonomous: {orchestrator._should_be_autonomous()}")

    # Force a test cycle
    print("\n🧪 Forcing test autonomous cycle...")
    try:
        orchestrator.last_user_activity = time.datetime.now() - time.timedelta(minutes=2)
        should_be = orchestrator._should_be_autonomous()
        print(f"   After 2 minutes idle: {should_be}")

        if should_be:
            print("   ✅ System would conduct autonomous discovery")
        else:
            print("   ❌ System blocked from autonomous discovery")

    except Exception as e:
        print(f"   ❌ Error: {e}")

except Exception as e:
    print(f"❌ System check failed: {e}")
    import traceback
    traceback.print_exc()