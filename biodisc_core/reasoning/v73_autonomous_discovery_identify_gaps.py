"""
Missing method fix for V73 Autonomous Discovery

This adds the identify_knowledge_gaps() method that the autonomous orchestrator expects.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)

def add_identify_knowledge_gaps_method():
    """Add the missing identify_knowledge_gaps method to V73 AutonomousDiscovery"""

    try:
        import sys
        from pathlib import Path
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from biodisc_core.reasoning.v73_autonomous_discovery import AutonomousDiscoveryOrchestrator

        def identify_knowledge_gaps(self) -> List[str]:
            """
            Identify current knowledge gaps using the curiosity engine.

            Returns:
                List of knowledge gaps identified by the curiosity engine
            """
            # Get logger in method scope to avoid closure issues
            method_logger = logging.getLogger(__name__)
            gaps = []

            if self.curiosity_engine:
                try:
                    # Generate curiosity questions from built-in biological knowledge base
                    curiosity_questions = self.curiosity_engine.generate_questions(
                        knowledge_base=None,  # Use built-in biological KB
                        max_questions=10
                    )

                    # Extract knowledge gaps from questions
                    for q in curiosity_questions:
                        if hasattr(q, 'knowledge_gap') and q.knowledge_gap:
                            gaps.append(q.knowledge_gap)
                        else:
                            # Use the question itself as a gap
                            gaps.append(q.question)

                    method_logger.info(f"Identified {len(gaps)} knowledge gaps from curiosity engine")

                except Exception as e:
                    method_logger.error(f"Error identifying knowledge gaps: {e}")
                    # Fallback: generate generic gaps from curiosity questions
                    try:
                        curiosity_questions = self.curiosity_engine.generate_questions(
                            knowledge_base=None,
                            max_questions=10
                        )
                        # Simple fallback - use questions as gaps
                        gaps = [q.question for q in curiosity_questions if hasattr(q, 'question')]
                        method_logger.info(f"Fallback: generated {len(gaps)} generic knowledge gaps")
                    except Exception as fallback_error:
                        method_logger.error(f"Fallback also failed: {fallback_error}")
            else:
                method_logger.warning("Curiosity engine not available for gap identification")

            return gaps

        # Add the method to the class
        AutonomousDiscoveryOrchestrator.identify_knowledge_gaps = identify_knowledge_gaps

        logger.info("✅ Added identify_knowledge_gaps method to V73 AutonomousDiscoveryOrchestrator")
        return True

    except Exception as e:
        logger.error(f"Failed to add identify_knowledge_gaps method: {e}")
        return False

if __name__ == '__main__':
    # Test the fix
    if add_identify_knowledge_gaps_method():
        print("✅ Successfully added identify_knowledge_gaps method")

        # Test it
        from biodisc_core.reasoning.v73_autonomous_discovery import AutonomousDiscoveryOrchestrator

        orchestrator = AutonomousDiscoveryOrchestrator()
        gaps = orchestrator.identify_knowledge_gaps()

        print(f"🧬 Found {len(gaps)} knowledge gaps:")
        for i, gap in enumerate(gaps[:5], 1):
            print(f"   {i}. {gap[:80]}...")
    else:
        print("❌ Failed to add method")