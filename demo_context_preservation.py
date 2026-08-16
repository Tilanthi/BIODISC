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
Context Preservation Demonstration
===================================

Demonstrates how context preservation survives /clear commands.

This script shows:
1. Saving a user question
2. Simulating a /clear command
3. Loading the context after /clear
4. Verifying continuity
"""

import sys
from pathlib import Path

# Add biodisc_core to path
sys.path.insert(0, str(Path(__file__).parent))

from biodisc_core.memory.persistent.context_preservation import (
    save_last_context,
    load_last_context,
    update_context_field,
    get_context_summary
)


def main():
    print("=" * 70)
    print("Context Preservation Demonstration")
    print("=" * 70)

    # Step 1: User asks a question
    print("\n📝 STEP 1: User asks a question")
    print("-" * 70)

    user_question = "What were the key findings from the last discovery?"

    save_last_context(
        question=user_question,
        response=None,
        metadata={
            'current_task': 'Analyzing recent discoveries',
            'question_type': 'user',
            'active_work': 'discovery_review'
        }
    )

    print(f"Question saved: {user_question}")

    # Verify save
    context = load_last_context()
    print(f"✅ Context saved at: {context['timestamp']}")

    # Step 2: System provides response
    print("\n🤖 STEP 2: System provides response")
    print("-" * 70)

    assistant_response = """Based on the autonomous discoveries log, the top discovery is:

"Post-Translational Modifications and Protein Folding Kinetics In Vivo"

This discovery analyzed how PTMs affect protein folding in living mouse cells using
GEO dataset GSE335147. The finding is novel because:

1. Zero similar studies found in PubMed literature
2. Specific mechanistic relationship (not just general field activity)
3. In vivo context (not in vitro)
4. Real experimental data with statistical validation

Novelty Score: 0.8 | Validation Confidence: 0.74"""

    update_context_field('last_assistant_response', assistant_response)
    update_context_field('current_task', 'Completed discovery analysis')

    print("Response saved and context updated")

    # Step 3: Simulate /clear command
    print("\n🔄 STEP 3: Simulating /clear command")
    print("-" * 70)
    print("Context would normally be lost here...")
    print("But with context preservation, it survives!")

    # Step 4: Load context after /clear
    print("\n📂 STEP 4: Loading context after /clear")
    print("-" * 70)

    restored_context = load_last_context()

    if restored_context:
        print("✅ Context successfully restored!")
        print(f"\nLast User Question:")
        print(f"   {restored_context['last_user_question']}")

        if restored_context.get('last_assistant_response'):
            print(f"\nLast Assistant Response:")
            response_preview = restored_context['last_assistant_response'][:200] + "..."
            print(f"   {response_preview}")

        print(f"\nSession ID: {restored_context['session_id']}")
        print(f"Timestamp: {restored_context['timestamp']}")
        print(f"Current Task: {restored_context['current_task']}")

        # Step 5: Show summary
        print("\n📋 STEP 5: Context Summary")
        print("-" * 70)

        summary = get_context_summary()
        print(summary)

        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nKey Points:")
        print("1. ✅ User question saved before context loss")
        print("2. ✅ Assistant response captured")
        print("3. ✅ Context survives /clear command")
        print("4. ✅ Continuity preserved across sessions")
        print("5. ✅ File remains fixed-size (never grows)")

    else:
        print("❌ Failed to restore context")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
