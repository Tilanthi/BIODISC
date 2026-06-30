#!/usr/bin/env python3
"""
Complete Integration Test for BIODISC Autonomous Discovery

Tests the complete pipeline from V73 question generation through V74 filtering
to decision maker goal creation and V73 discovery execution with analysis modules.
"""

import sys
sys.path.insert(0, '.')

def test_complete_pipeline():
    """Test the complete autonomous discovery pipeline"""
    print("🧪 Testing Complete Autonomous Discovery Pipeline")
    print("=" * 70)

    try:
        # Apply V73 fix
        from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
        add_identify_knowledge_gaps_method()

        # Import required modules
        from biodisc_core.autonomous.config import get_default_config
        from biodisc_core.reasoning.v73_curiosity_engine import get_curiosity_engine
        from biodisc_core.autonomous.decision_maker import AutonomousDecisionMaker
        from biodisc_core.reasoning.v73_autonomous_discovery import AutonomousDiscoveryOrchestrator

        # Get configuration
        config = get_default_config()
        print(f"📊 Configuration:")
        print(f"   Min discovery confidence: {config.min_discovery_confidence}")
        print(f"   Computational novelty threshold: {config.computational_novelty_threshold}")
        print(f"   Synthesis quality threshold: {config.synthesis_quality_threshold}")

        # Step 1: Test V73 Curiosity Engine with V74 filter
        print(f"\n🔍 Step 1: V73 Curiosity Engine + V74 Filter")
        curiosity_engine = get_curiosity_engine()
        questions = curiosity_engine.generate_questions(knowledge_base=None, max_questions=5)
        print(f"   Generated {len(questions)} V74-filtered questions")

        for i, q in enumerate(questions[:3], 1):
            print(f"   {i}. {q.question[:60]}...")
            print(f"      Type: {q.question_type}, Priority: {q.priority}, Confidence: {q.confidence}")

        # Step 2: Test Decision Maker Goal Generation
        print(f"\n🎯 Step 2: Decision Maker Goal Generation")
        decision_maker = AutonomousDecisionMaker(v73_curiosity=curiosity_engine, config=config)
        meta_assessment = {'knowledge_gaps': [], 'readiness': True}
        goals = decision_maker.generate_goals(meta_assessment)
        print(f"   Generated {len(goals)} autonomous goals")

        if goals:
            for i, goal in enumerate(goals[:3], 1):
                print(f"   {i}. {goal.description[:60]}...")
                print(f"      Type: {goal.goal_type}, Priority: {goal.priority}")
        else:
            print("   ❌ NO GOALS GENERATED")
            return False

        # Step 3: Test V73 Discovery Execution with Analysis Modules
        print(f"\n🔬 Step 3: V73 Discovery Execution with Analysis Modules")
        orchestrator = AutonomousDiscoveryOrchestrator()

        # Check analysis module availability from module constants
        from biodisc_core.reasoning.v73_autonomous_discovery import (
            COMPUTATIONAL_BIOLOGY_AVAILABLE,
            CROSS_DOMAIN_SYNTHESIS_AVAILABLE,
            INSIGHT_GENERATOR_AVAILABLE
        )

        print(f"   Analysis Modules Status:")
        print(f"      Computational Biology: {'✅' if COMPUTATIONAL_BIOLOGY_AVAILABLE else '❌'}")
        print(f"      Cross-Domain Synthesis: {'✅' if CROSS_DOMAIN_SYNTHESIS_AVAILABLE else '❌'}")
        print(f"      Insight Generator: {'✅' if INSIGHT_GENERATOR_AVAILABLE else '❌'}")

        # Test question exploration with analysis modules
        if goals:
            test_goal = goals[0]
            print(f"\n   Testing exploration of: {test_goal.description[:60]}...")

            # Create a CuriosityQuestion from the goal
            from biodisc_core.reasoning.v73_curiosity_engine import CuriosityQuestion, QuestionType, Priority
            test_question = CuriosityQuestion(
                question=test_goal.description,
                question_type=QuestionType.KNOWLEDGE_GAP,
                priority=Priority.MEDIUM,
                confidence=0.8,
                knowledge_gap=test_goal.description
            )

            # Explore the question
            discovery = orchestrator.explore_question(test_question)

            if discovery:
                print(f"   ✅ DISCOVERY MADE!")
                print(f"      Summary: {discovery.summary[:80]}...")
                print(f"      Confidence: {discovery.confidence}")
                print(f"      Novelty: {discovery.novelty}")
                print(f"      Evidence items: {len(discovery.evidence)}")
                return True
            else:
                print(f"   ❌ No discovery made")
                return False

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logger_fix():
    """Test that the logger fix works"""
    print("\n🔧 Testing Logger Fix")
    print("=" * 70)

    try:
        from biodisc_core.reasoning.v73_autonomous_discovery_identify_gaps import add_identify_knowledge_gaps_method
        add_identify_knowledge_gaps_method()

        from biodisc_core.reasoning.v73_autonomous_discovery import AutonomousDiscoveryOrchestrator
        orchestrator = AutonomousDiscoveryOrchestrator()

        # This should not raise a logger error
        gaps = orchestrator.identify_knowledge_gaps()
        print(f"✅ Logger fix working! Identified {len(gaps)} knowledge gaps")
        return True

    except Exception as e:
        print(f"❌ Logger fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test logger fix first
    logger_ok = test_logger_fix()

    # Test complete pipeline
    pipeline_ok = test_complete_pipeline()

    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS:")
    print(f"   Logger Fix: {'✅ PASS' if logger_ok else '❌ FAIL'}")
    print(f"   Complete Pipeline: {'✅ PASS' if pipeline_ok else '❌ FAIL'}")

    if logger_ok and pipeline_ok:
        print("\n🎉 ALL TESTS PASSED! Autonomous discovery integration is working!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - needs more work")
        sys.exit(1)
