#!/usr/bin/env python3
"""
Context Preservation System Test Suite
======================================

Tests for the context preservation system that survives /clear commands.

Run: python test_context_preservation.py
"""

import json
import sys
import time
from pathlib import Path

# Add biodisc_core to path
sys.path.insert(0, str(Path(__file__).parent))

from biodisc_core.memory.persistent.context_preservation import (
    save_last_context,
    load_last_context,
    update_context_field,
    clear_last_context,
    get_context_summary
)


def test_basic_save_load():
    """Test 1: Basic context save and load"""
    print("\n=== Test 1: Basic Save/Load ===")

    # Clear any existing context
    clear_last_context()

    # Save a test question
    test_question = "What were the key findings from the last discovery?"
    save_last_context(
        question=test_question,
        response=None,
        metadata={'current_task': 'discovery_analysis', 'question_type': 'user'}
    )

    # Load and verify
    context = load_last_context()
    assert context is not None, "Failed to load context"
    assert context['last_user_question'] == test_question, f"Question mismatch: {context.get('last_user_question')}"
    assert context['current_task'] == 'discovery_analysis', f"Task mismatch: {context.get('current_task')}"

    print("✅ Basic save/load successful")
    return True


def test_response_update():
    """Test 2: Update with response"""
    print("\n=== Test 2: Response Update ===")

    test_response = "Based on the autonomous discoveries log, the top discovery is about post-translational modifications affecting protein folding kinetics in vivo."

    # Update with response
    update_context_field('last_assistant_response', test_response)
    update_context_field('current_task', 'Completed query in auto mode')

    # Load and verify
    context = load_last_context()
    assert context is not None, "Failed to load context after update"
    assert context['last_assistant_response'] == test_response, "Response mismatch"
    assert 'Completed' in context['current_task'], "Task not updated"

    print("✅ Response update successful")
    return True


def test_file_size_stability():
    """Test 3: File size remains constant (never grows)"""
    print("\n=== Test 3: File Size Stability ===")

    context_file = Path(__file__).parent / 'last_context_state.json'
    initial_size = context_file.stat().st_size if context_file.exists() else 0

    # Save 100 different questions
    for i in range(100):
        save_last_context(
            question=f"Test question {i}: What is the meaning of {i}?",
            response=f"Test response {i}",
            metadata={'current_task': f'test_task_{i}'}
        )

    # Check file size hasn't grown significantly
    final_size = context_file.stat().st_size
    size_diff = abs(final_size - initial_size)
    size_ratio = final_size / initial_size if initial_size > 0 else 1.0

    # File should be roughly the same size (allow 10% variance for JSON formatting differences)
    assert size_ratio < 1.1, f"File grew too much: {initial_size} -> {final_size} ({size_ratio:.2f}x)"

    print(f"✅ File size stable: {initial_size} -> {final_size} bytes ({size_ratio:.2f}x)")
    return True


def test_context_summary():
    """Test 4: Context summary generation"""
    print("\n=== Test 4: Context Summary ===")

    # Save complete context
    save_last_context(
        question="What are the key mechanisms in protein folding?",
        response="The key mechanisms include chaperone-mediated folding, co-translational folding, and post-translational modifications.",
        metadata={
            'current_task': 'Analyzing protein folding mechanisms',
            'active_work': 'protein_folding_analysis'
        }
    )

    # Get summary
    summary = get_context_summary()
    assert summary is not None, "Failed to get summary"
    assert 'protein folding' in summary.lower(), "Summary missing key content"
    assert 'mechanisms' in summary.lower(), "Summary missing task information"

    print("✅ Context summary generation successful")
    print(f"Summary preview:\n{summary[:200]}...")
    return True


def test_clear_context():
    """Test 5: Clear context"""
    print("\n=== Test 5: Clear Context ===")

    # Clear context
    result = clear_last_context()
    assert result is True, "Failed to clear context"

    # Verify context is gone
    context = load_last_context()
    assert context is None, "Context still exists after clear"

    print("✅ Context clear successful")
    return True


def test_autonomous_question_tracking():
    """Test 6: Autonomous discovery question tracking"""
    print("\n=== Test 6: Autonomous Question Tracking ===")

    # Save autonomous question
    save_last_context(
        question="What are the key mechanisms in epigenetics that remain unexplored?",
        response=None,
        metadata={
            'current_task': 'Autonomous exploration: epigenetics',
            'question_type': 'autonomous',
            'active_work': 'autonomous_discovery'
        }
    )

    # Load and verify
    context = load_last_context()
    assert context is not None, "Failed to load autonomous context"
    assert context['question_type'] == 'autonomous', "Question type not set correctly"
    assert 'epigenetics' in context['last_user_question'].lower(), "Autonomous question not saved"

    # Update with discovery
    update_context_field(
        'last_assistant_response',
        "Discovery: Novel epigenetic mechanism involving histone modification cross-talk..."
    )

    # Verify update
    context = load_last_context()
    assert 'histone' in context['last_assistant_response'].lower(), "Discovery not updated"

    print("✅ Autonomous question tracking successful")
    return True


def test_json_structure():
    """Test 7: JSON structure validity"""
    print("\n=== Test 7: JSON Structure Validity ===")

    # Save test context
    save_last_context(
        question="Test question",
        response="Test response",
        metadata={'test_field': 'test_value'}
    )

    # Read raw JSON
    context_file = Path(__file__).parent / 'last_context_state.json'
    with open(context_file, 'r') as f:
        raw_data = json.load(f)

    # Verify required fields
    required_fields = [
        'timestamp', 'session_id', 'last_user_question',
        'last_assistant_response', 'current_task', 'question_type'
    ]

    for field in required_fields:
        assert field in raw_data, f"Missing required field: {field}"

    print("✅ JSON structure valid")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Context Preservation System Test Suite")
    print("=" * 60)

    tests = [
        test_basic_save_load,
        test_response_update,
        test_file_size_stability,
        test_context_summary,
        test_clear_context,
        test_autonomous_question_tracking,
        test_json_structure
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ {test.__name__} failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} error: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    # Clean up
    clear_last_context()

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
