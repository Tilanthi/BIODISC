#!/usr/bin/env python3
"""Test V73-V74 integration with analysis modules"""
import sys
sys.path.insert(0, '.')

try:
    # Apply fixes first
    from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
    add_identify_knowledge_gaps_method()

    from biodisc_core.autonomous.decision_maker import AutonomousDecisionMaker
    from biodisc_core.autonomous.config import get_default_config
    from biodisc_core.reasoning.v73_curiosity_engine import get_curiosity_engine

    print("🧪 Testing V73-V74-Analysis Integration")
    print("=" * 60)

    # Get configuration
    config = get_default_config()
    print(f"Min discovery confidence: {config.min_discovery_confidence}")

    # Initialize V73 Curiosity Engine with V74 filter
    curiosity_engine = get_curiosity_engine()
    print(f"✅ V73 Curiosity Engine initialized (with V74 filter)")

    # Generate V74-filtered questions
    questions = curiosity_engine.generate_questions(
        knowledge_base=None,
        max_questions=5
    )
    print(f"📝 V74-Filtered Questions: {len(questions)}")

    for i, q in enumerate(questions[:3]):
        print(f"  {i+1}. {q.question[:60]}...")
        print(f"     Type: {q.question_type}, Priority: {q.priority}, Confidence: {q.confidence}")

    # Initialize decision maker with V73
    decision_maker = AutonomousDecisionMaker(
        v73_curiosity=curiosity_engine,
        config=config
    )
    print(f"✅ Decision Maker initialized with V73 integration")

    # Test goal generation with V74-filtered questions
    meta_assessment = {
        'knowledge_gaps': [],
        'readiness': True
    }

    print(f"\n🎯 Testing goal generation with V73-V74 integration...")
    goals = decision_maker.generate_goals(meta_assessment)

    print(f"🎯 Generated {len(goals)} goals")

    if goals:
        print(f"\n✅ SUCCESS! V74-filtered questions are being converted to goals:")
        for i, goal in enumerate(goals[:3], 1):
            print(f"  {i}. {goal.description[:60]}...")
            print(f"     Type: {goal.goal_type}, Priority: {goal.priority}")

        # Now test if goals can be executed with analysis modules
        print(f"\n🔬 Testing analysis module integration...")
        # Check if V73 discovery has analysis modules
        try:
            from biodisc_core.reasoning.v73_autonomous_discovery import (
                COMPUTATIONAL_BIOLOGY_AVAILABLE,
                CROSS_DOMAIN_SYNTHESIS_AVAILABLE,
                INSIGHT_GENERATOR_AVAILABLE
            )
            print(f"  Computational Biology: {'✅' if COMPUTATIONAL_BIOLOGY_AVAILABLE else '❌'}")
            print(f"  Cross-Domain Synthesis: {'✅' if CROSS_DOMAIN_SYNTHESIS_AVAILABLE else '❌'}")
            print(f"  Insight Generator: {'✅' if INSIGHT_GENERATOR_AVAILABLE else '❌'}")

            if all([COMPUTATIONAL_BIOLOGY_AVAILABLE, CROSS_DOMAIN_SYNTHESIS_AVAILABLE, INSIGHT_GENERATOR_AVAILABLE]):
                print(f"  ✅ All analysis modules available for genuine discovery!")
            else:
                print(f"  ⚠️  Some analysis modules missing")

        except Exception as e:
            print(f"  ❌ Error checking analysis modules: {e}")

    else:
        print(f"❌ FAILED: No goals generated")
        print(f"\n🔍 Checking knowledge gap assessment...")

        gaps = decision_maker._assess_knowledge_gaps(meta_assessment)
        print(f"  Knowledge gaps: {len(gaps)}")

        for i, gap in enumerate(gaps[:3], 1):
            quality = decision_maker._evaluate_goal_quality(gap, meta_assessment)
            print(f"  Gap {i}: importance={gap.importance:.3f}, quality={quality:.3f}, threshold={config.min_discovery_confidence}")
            if quality >= config.min_discovery_confidence:
                print(f"    ✅ Would create goal")
            else:
                print(f"    ❌ Quality too low")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
