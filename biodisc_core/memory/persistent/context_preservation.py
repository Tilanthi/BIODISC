"""
Context Preservation System for BIODISC
=========================================

Preserves the last complete conversational context across context clears and session resets.

Key Features:
- Single fixed-size file (never grows)
- Auto-saves on user questions and responses
- Survives /clear commands
- Integrates with session startup hook
- Minimal performance impact

Usage:
    from biodisc_core.memory.persistent.context_preservation import save_last_context, load_last_context

    # Save context after user question
    save_last_context(
        question="What were the key findings?",
        response=None,  # Updated when assistant responds
        metadata={"current_task": "discovery_analysis"}
    )

    # Load context on startup
    context = load_last_context()
    if context:
        print(f"Last question: {context['last_user_question']}")
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import threading


@dataclass
class LastContextState:
    """Represents the last complete conversational context."""
    timestamp: str
    session_id: str
    last_user_question: str = ""
    last_assistant_response: str = ""
    current_task: str = ""
    files_in_scope: list = field(default_factory=list)
    context_summary: str = ""
    active_work: str = ""
    priority: int = 1
    question_type: str = "user"  # 'user' or 'autonomous'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LastContextState':
        """Create from dictionary."""
        return cls(**data)


class ContextPreservation:
    """
    Context preservation system for last conversational state.

    Maintains a single fixed-size file that stores the last complete context.
    Never grows - always overwrites on each save.
    """

    def __init__(self, context_file: Optional[Path] = None):
        """
        Initialize context preservation system.

        Args:
            context_file: Path to context file (defaults to BIODISC_ROOT/last_context_state.json)
        """
        if context_file is None:
            # Default to BIODISC root directory
            biodisc_root = Path(__file__).parent.parent.parent.parent
            context_file = biodisc_root / 'last_context_state.json'

        self.context_file = Path(context_file)
        self.context_file.parent.mkdir(parents=True, exist_ok=True)

        # Thread-safe lock for file operations
        self._lock = threading.Lock()

        # Current context state
        self._current_context: Optional[LastContextState] = None

    def save_last_context(
        self,
        question: str,
        response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save the last conversational context.

        Args:
            question: The user's last question
            response: The assistant's last response (optional, can be updated later)
            metadata: Additional context information (optional)

        Returns:
            True if save successful, False otherwise
        """
        try:
            with self._lock:
                # Generate session ID if not exists
                session_id = self._generate_session_id()

                # Create context state
                context = LastContextState(
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    last_user_question=question[:5000],  # Limit question size
                    last_assistant_response=response[:10000] if response else "",
                    current_task=metadata.get('current_task', '') if metadata else '',
                    files_in_scope=metadata.get('files_in_scope', []) if metadata else [],
                    context_summary=metadata.get('context_summary', '') if metadata else '',
                    active_work=metadata.get('active_work', '') if metadata else '',
                    priority=metadata.get('priority', 1) if metadata else 1,
                    question_type=metadata.get('question_type', 'user') if metadata else 'user'
                )

                # Save to file (overwrites, never grows)
                with open(self.context_file, 'w', encoding='utf-8') as f:
                    json.dump(context.to_dict(), f, indent=2, ensure_ascii=False)

                self._current_context = context
                return True

        except Exception as e:
            # Silent fail - don't break the system if context save fails
            print(f"Warning: Could not save context state: {e}")
            return False

    def load_last_context(self) -> Optional[Dict[str, Any]]:
        """
        Load the last conversational context.

        Returns:
            Context dictionary if available, None otherwise
        """
        try:
            with self._lock:
                if not self.context_file.exists():
                    return None

                with open(self.context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self._current_context = LastContextState.from_dict(data)
                return data

        except Exception as e:
            # Silent fail - don't break the system if context load fails
            print(f"Warning: Could not load context state: {e}")
            return None

    def update_context_field(self, field: str, value: Any) -> bool:
        """
        Update a specific field in the current context.

        Args:
            field: Field name to update
            value: New value for the field

        Returns:
            True if update successful, False otherwise
        """
        try:
            with self._lock:
                # Load current context
                context_data = self.load_last_context()
                if not context_data:
                    return False

                # Update field
                context_data[field] = value
                context_data['timestamp'] = datetime.now().isoformat()

                # Save back
                with open(self.context_file, 'w', encoding='utf-8') as f:
                    json.dump(context_data, f, indent=2, ensure_ascii=False)

                return True

        except Exception as e:
            print(f"Warning: Could not update context field: {e}")
            return False

    def clear_last_context(self) -> bool:
        """
        Clear the last context state.

        Returns:
            True if clear successful, False otherwise
        """
        try:
            with self._lock:
                if self.context_file.exists():
                    self.context_file.unlink()
                self._current_context = None
                return True

        except Exception as e:
            print(f"Warning: Could not clear context state: {e}")
            return False

    def _generate_session_id(self) -> str:
        """Generate a session ID."""
        if self._current_context:
            return self._current_context.session_id
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]

    def get_context_summary(self) -> Optional[str]:
        """
        Get a summary of the last context.

        Returns:
            Summary string if context exists, None otherwise
        """
        context = self.load_last_context()
        if not context:
            return None

        parts = [
            f"Last Question: {context.get('last_user_question', 'No previous question')}",
        ]

        if context.get('last_assistant_response'):
            parts.append(f"Last Response: {context.get('last_assistant_response', '')[:200]}...")

        if context.get('current_task'):
            parts.append(f"Current Task: {context.get('current_task')}")

        if context.get('active_work'):
            parts.append(f"Active Work: {context.get('active_work')}")

        return "\n".join(parts)


# Global context preservation instance
_context_preservation: Optional[ContextPreservation] = None
_preservation_lock = threading.Lock()


def get_context_preservation() -> ContextPreservation:
    """Get global context preservation instance."""
    global _context_preservation
    with _preservation_lock:
        if _context_preservation is None:
            _context_preservation = ContextPreservation()
    return _context_preservation


def save_last_context(
    question: str,
    response: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Save the last conversational context."""
    return get_context_preservation().save_last_context(question, response, metadata)


def load_last_context() -> Optional[Dict[str, Any]]:
    """Load the last conversational context."""
    return get_context_preservation().load_last_context()


def update_context_field(field: str, value: Any) -> bool:
    """Update a specific field in the current context."""
    return get_context_preservation().update_context_field(field, value)


def clear_last_context() -> bool:
    """Clear the last context state."""
    return get_context_preservation().clear_last_context()


def get_context_summary() -> Optional[str]:
    """Get a summary of the last context."""
    return get_context_preservation().get_context_summary()


__all__ = [
    'ContextPreservation',
    'LastContextState',
    'get_context_preservation',
    'save_last_context',
    'load_last_context',
    'update_context_field',
    'clear_last_context',
    'get_context_summary'
]
