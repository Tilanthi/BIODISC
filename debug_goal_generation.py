#!/usr/bin/env python3
"""Debug why autonomous goals are not being generated"""
import sys
sys.path.insert(0, '.')

try:
    # Apply fixes first
    from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
    add_identify_knowledge_gaps_method()

    from biodisc_core.autonomous.decision_maker import AutonomousDecisionMaker, KnowledgeGap
    from biodisc_core.autonomous.config import AutonomousConfig

    # Test the decision maker directly
    config = AutonomousConfig(
        max_cpu_percent=80.0,
        max_memory_percent=80.0,
        min_discovery_confidence=0.70,
        discoveries_per_cycle=10
    )

    decision_maker = AutonomousDecisionMaker(config=config)

    # Create test knowledge gaps similar to what V73 generates
    test_gaps = [
        KnowledgeGap(
            question="How do cells amplify mechanical signals at the molecular level?",
            domain="cell_biology",
            gap_type="knowledge_gap",
            importance=0.5,
            estimated_difficulty=0.5,
            resource_requirements={'estimated_time': 10, 'cpu_intensity': 0.3}
        ),
        KnowledgeGap(
            question="What mechanisms regulate non-coding RNA stability?",
            domain="molecular_biology",
            gap_type="knowledge_gap",
            importance=0.5,
            estimated_difficulty=0.5,
            resource_requirements={'estimated_time': 10, 'cpu_intensity': 0.3}
        )
    ]

    print("🔍 Debugging Goal Generation")
    print("=" * 50)

    for gap in test_gaps:
        print(f"\n📝 Gap: {gap.question[:60]}...")
        print(f"   Importance: {gap.importance}")
        print(f"   Difficulty: {gap.estimated_difficulty}")
        print(f"   Resource requirements: {gap.resource_requirements}")

        # Test goal quality evaluation
        meta_assessment = {'knowledge_gaps': [], 'readiness': True}
        quality = decision_maker._evaluate_goal_quality(gap, meta_assessment)
        print(f"   Quality score: {quality:.3f} (threshold: {config.min_discovery_confidence})")

        # Test resource feasibility
        feasible = decision_maker._is_resource_feasible(gap)
        print(f"   Resource feasible: {feasible}")

        # Check if goal would be created
        if quality >= config.min_discovery_confidence:
            print(f"   ✅ WOULD CREATE GOAL")
        else:
            print(f"   ❌ QUALITY TOO LOW (need {config.min_discovery_confidence}, got {quality:.3f})")

    # Test full goal generation
    print("\n🎯 Testing Full Goal Generation")
    print("=" * 50)

    meta_assessment = {
        'knowledge_gaps': ["How do cells amplify mechanical signals at the molecular level?"],
        'readiness': True
    }

    goals = decision_maker.generate_goals(meta_assessment)
    print(f"Goals generated: {len(goals)}")

    if goals:
        for i, goal in enumerate(goals, 1):
            print(f"   {i}. {goal.description[:60]}...")
    else:
        print("   ❌ NO GOALS GENERATED")

        # Check why
        print("\n🔍 Diagnosing why no goals generated:")
        gaps = decision_maker._assess_knowledge_gaps(meta_assessment)
        print(f"   Knowledge gaps assessed: {len(gaps)}")

        for i, gap in enumerate(gaps, 1):
            quality = decision_maker._evaluate_goal_quality(gap, meta_assessment)
            feasible = decision_maker._is_resource_feasible(gap)
            print(f"   Gap {i}: quality={quality:.3f}, feasible={feasible}, threshold={config.min_discovery_confidence}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()