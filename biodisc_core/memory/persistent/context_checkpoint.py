"""
Context Checkpoint System for BIODISC
=====================================

Saves and restores work context when running out of token space.

This system addresses the critical issue of losing work context
when conversations run long and hit token limits.

Key Features:
- Automatic context checkpointing during work
- Work state preservation (tasks, files, decisions)
- Quick context restoration on restart
- Minimizes repetitive work after context loss

Usage:
    # During work, before hitting context limit:
    checkpoint = ContextCheckpoint()
    checkpoint.save_current_state(
        task_description="Fixing BIODISC discovery process",
        files_modified=['file1.py', 'file2.py'],
        next_steps=['Step 1', 'Step 2'],
        decisions_made={'issue': 'deduplication bug', 'solution': 'persistent hash storage'}
    )

    # After context restart:
    checkpoint = ContextCheckpoint()
    state = checkpoint.get_latest_checkpoint()
    print(f"Resuming: {state['task_description']}")
    print(f"Files modified: {state['files_modified']}")
    print(f"Next steps: {state['next_steps']}")
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import os


@dataclass
class WorkState:
    """Represents the current work state at a point in time."""
    timestamp: str
    task_description: str
    task_status: str  # 'in_progress', 'completed', 'blocked'
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_read: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    decisions_made: Dict[str, str] = field(default_factory=dict)
    issues_discovered: List[str] = field(default_factory=list)
    solutions_implemented: List[str] = field(default_factory=list)
    test_results: Dict[str, str] = field(default_factory=dict)
    git_status: Optional[str] = None
    current_branch: Optional[str] = None
    working_directory: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkState':
        """Create from dictionary."""
        return cls(**data)


class ContextCheckpoint:
    """
    Manages context checkpointing for work state preservation.

    This system automatically saves work context so that when
    token limits are hit and context is lost, work can be
    quickly resumed without repetition.
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize context checkpoint system.

        Args:
            checkpoint_dir: Directory to store checkpoints (defaults to ~/.biodisc_persistent/checkpoints)
        """
        if checkpoint_dir is None:
            checkpoint_dir = Path.home() / '.biodisc_persistent' / 'checkpoints'

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.current_checkpoint_file = self.checkpoint_dir / 'current_checkpoint.json'
        self.checkpoint_history = self.checkpoint_dir / 'checkpoint_history.jsonl'

    def save_current_state(self,
                         task_description: str,
                         task_status: str = 'in_progress',
                         files_modified: Optional[List[str]] = None,
                         files_created: Optional[List[str]] = None,
                         files_read: Optional[List[str]] = None,
                         next_steps: Optional[List[str]] = None,
                         decisions_made: Optional[Dict[str, str]] = None,
                         issues_discovered: Optional[List[str]] = None,
                         solutions_implemented: Optional[List[str]] = None,
                         test_results: Optional[Dict[str, str]] = None,
                         notes: str = "") -> str:
        """
        Save the current work state.

        Args:
            task_description: What task is being worked on
            task_status: Current status of the task
            files_modified: List of files modified in this work session
            files_created: List of files created in this work session
            files_read: List of files read during this work session
            next_steps: List of next steps to continue work
            decisions_made: Dictionary of decisions made (issue -> solution)
            issues_discovered: List of issues discovered during work
            solutions_implemented: List of solutions implemented
            test_results: Dictionary of test results
            notes: Additional notes about the work state

        Returns:
            Checkpoint ID (hash of the state)
        """
        # Get git status if available
        git_status = self._get_git_status()
        current_branch = self._get_current_branch()
        working_dir = os.getcwd()

        # Create work state
        state = WorkState(
            timestamp=datetime.now().isoformat(),
            task_description=task_description,
            task_status=task_status,
            files_modified=files_modified or [],
            files_created=files_created or [],
            files_read=files_read or [],
            next_steps=next_steps or [],
            decisions_made=decisions_made or {},
            issues_discovered=issues_discovered or [],
            solutions_implemented=solutions_implemented or [],
            test_results=test_results or {},
            git_status=git_status,
            current_branch=current_branch,
            working_directory=working_dir,
            notes=notes
        )

        # Generate checkpoint ID
        state_dict = state.to_dict()
        checkpoint_id = hashlib.md5(json.dumps(state_dict, sort_keys=True).encode()).hexdigest()

        # Save current checkpoint
        with open(self.current_checkpoint_file, 'w') as f:
            json.dump(state_dict, f, indent=2)

        # Append to history
        with open(self.checkpoint_history, 'a') as f:
            f.write(json.dumps({**state_dict, 'checkpoint_id': checkpoint_id}) + '\n')

        print(f"💾 Checkpoint saved: {checkpoint_id}")
        print(f"   Task: {task_description}")
        print(f"   Status: {task_status}")
        if files_modified:
            print(f"   Files modified: {len(files_modified)}")
        if next_steps:
            print(f"   Next steps: {len(next_steps)}")

        return checkpoint_id

    def get_latest_checkpoint(self) -> Optional[WorkState]:
        """
        Get the latest saved checkpoint.

        Returns:
            WorkState if checkpoint exists, None otherwise
        """
        if not self.current_checkpoint_file.exists():
            return None

        try:
            with open(self.current_checkpoint_file, 'r') as f:
                state_dict = json.load(f)
            return WorkState.from_dict(state_dict)
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
            return None

    def get_checkpoint_history(self, limit: int = 10) -> List[WorkState]:
        """
        Get recent checkpoint history.

        Args:
            limit: Maximum number of checkpoints to return

        Returns:
            List of recent WorkStates
        """
        if not self.checkpoint_history.exists():
            return []

        checkpoints = []
        try:
            with open(self.checkpoint_history, 'r') as f:
                for line in f:
                    if line.strip():
                        state_dict = json.loads(line)
                        checkpoints.append(WorkState.from_dict(state_dict))
                        if len(checkpoints) >= limit:
                            break
        except Exception as e:
            print(f"❌ Error loading checkpoint history: {e}")

        # Return in reverse chronological order
        return list(reversed(checkpoints))

    def clear_current_checkpoint(self):
        """Clear the current checkpoint (e.g., after task completion)."""
        if self.current_checkpoint_file.exists():
            self.current_checkpoint_file.unlink()
            print("✅ Current checkpoint cleared")

    def restore_and_display(self) -> bool:
        """
        Display the latest checkpoint in a user-friendly format.

        Returns:
            True if checkpoint was found and displayed, False otherwise
        """
        state = self.get_latest_checkpoint()
        if state is None:
            print("📋 No checkpoint found - starting fresh")
            return False

        print("🔄 **RESTORING FROM CHECKPOINT**")
        print(f"⏰ **Timestamp**: {state.timestamp}")
        print(f"📝 **Task**: {state.task_description}")
        print(f"📊 **Status**: {state.task_status}")

        if state.files_modified:
            print(f"\n📁 **Files Modified** ({len(state.files_modified)}):")
            for f in state.files_modified:
                print(f"   - {f}")

        if state.files_created:
            print(f"\n✨ **Files Created** ({len(state.files_created)}):")
            for f in state.files_created:
                print(f"   - {f}")

        if state.decisions_made:
            print(f"\n🔍 **Decisions Made** ({len(state.decisions_made)}):")
            for issue, solution in state.decisions_made.items():
                print(f"   - {issue}: {solution}")

        if state.issues_discovered:
            print(f"\n⚠️ **Issues Discovered** ({len(state.issues_discovered)}):")
            for issue in state.issues_discovered:
                print(f"   - {issue}")

        if state.solutions_implemented:
            print(f"\n✅ **Solutions Implemented** ({len(state.solutions_implemented)}):")
            for solution in state.solutions_implemented:
                print(f"   - {solution}")

        if state.next_steps:
            print(f"\n➡️ **Next Steps** ({len(state.next_steps)}):")
            for i, step in enumerate(state.next_steps, 1):
                print(f"   {i}. {step}")

        if state.test_results:
            print(f"\n🧪 **Test Results** ({len(state.test_results)}):")
            for test_name, result in state.test_results.items():
                print(f"   - {test_name}: {result}")

        if state.notes:
            print(f"\n📝 **Notes**: {state.notes}")

        if state.git_status:
            print(f"\n🔧 **Git Status**: {state.git_status[:100]}...")

        return True

    def _get_git_status(self) -> Optional[str]:
        """Get current git status if available."""
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--short'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch if available."""
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None


def create_work_checkpoint(task_description: str, **kwargs) -> str:
    """
    Convenience function to quickly create a work checkpoint.

    Args:
        task_description: What task is being worked on
        **kwargs: Additional arguments to pass to save_current_state

    Returns:
        Checkpoint ID
    """
    checkpoint = ContextCheckpoint()
    return checkpoint.save_current_state(task_description, **kwargs)


def restore_work_checkpoint() -> Optional[WorkState]:
    """
    Convenience function to quickly restore the latest checkpoint.

    Returns:
        Latest WorkState if available, None otherwise
    """
    checkpoint = ContextCheckpoint()
    return checkpoint.get_latest_checkpoint()