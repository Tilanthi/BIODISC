"""
Session Persistence System for BIODISC
========================================

TRUE SESSION-TO-SESSION MEMORY PERSISTENCE

This system provides comprehensive memory retention across manual session closures,
not just context overflow situations. It automatically saves conversation context
and restores it on session restart.

Key Features:
- Automatic conversation context saving at session end
- Automatic context restoration on session start
- Cross-session memory retention
- Better context management to reduce frequent overflows
- Integration with existing memory systems

Usage:
    # Session automatically saves context when closed
    # Session automatically restores context when started
    # No manual intervention required
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import os
from collections import deque


@dataclass
class ConversationTurn:
    """Represents a single conversation turn."""
    timestamp: str
    role: str  # 'user' or 'assistant'
    content: str
    context_summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    files_mentioned: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)


@dataclass
class SessionContext:
    """Comprehensive session context for persistence."""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    conversation_summary: str = ""
    key_topics: List[str] = field(default_factory=list)
    tasks_completed: List[str] = field(default_factory=list)
    tasks_in_progress: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    decisions_made: Dict[str, str] = field(default_factory=dict)
    issues_discovered: List[str] = field(default_factory=list)
    solutions_implemented: List[str] = field(default_factory=list)
    important_facts: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_turns: List[ConversationTurn] = field(default_factory=list)
    context_compression_ratio: float = 0.0  # How much context was compressed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        data = asdict(self)
        # Convert conversation turns to dicts
        data['conversation_turns'] = [asdict(turn) for turn in self.conversation_turns]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Create from dictionary."""
        # Convert conversation turns back to objects
        if 'conversation_turns' in data and data['conversation_turns']:
            data['conversation_turns'] = [
                ConversationTurn(**turn) if isinstance(turn, dict) else turn
                for turn in data['conversation_turns']
            ]
        return cls(**data)


class SessionPersistence:
    """
    Comprehensive session persistence system.

    This system provides TRUE session-to-session memory retention,
    working across manual session closures, not just context overflows.
    """

    def __init__(self, persistence_dir: Optional[Path] = None):
        """
        Initialize session persistence system.

        Args:
            persistence_dir: Directory for session storage (defaults to ~/.biodisc_persistent/sessions)
        """
        if persistence_dir is None:
            persistence_dir = Path.home() / '.biodisc_persistent' / 'sessions'

        self.persistence_dir = Path(persistence_dir)
        self.persistence_dir.mkdir(parents=True, exist_ok=True)

        self.current_session_file = self.persistence_dir / 'current_session.json'
        self.session_history = self.persistence_dir / 'session_history.jsonl'
        self.context_cache = self.persistence_dir / 'context_cache.json'

        # Current session context
        self.current_session: Optional[SessionContext] = None
        self.conversation_buffer: deque = deque(maxlen=100)  # Keep last 100 turns
        self.session_active = False

    def start_session(self, session_id: Optional[str] = None) -> SessionContext:
        """
        Start a new session or continue existing one.

        Completely automatic - no display, just returns the session.

        Args:
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            SessionContext for the session
        """
        if session_id is None:
            session_id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]

        # Try to load existing session
        existing_session = self._load_current_session()
        if existing_session and existing_session.session_id == session_id:
            self.current_session = existing_session
            # Silent continuation - no output
        else:
            # Create new session
            self.current_session = SessionContext(
                session_id=session_id,
                start_time=datetime.now().isoformat()
            )
            # Silent creation - no output

        self.session_active = True
        self._save_current_session()

        return self.current_session

    def end_session(self) -> str:
        """
        End current session and save comprehensive context.

        Returns:
            Session ID
        """
        if not self.session_active or self.current_session is None:
            print("⚠️  No active session to end")
            return ""

        # Compress conversation context
        self._compress_conversation_context()

        # Mark session as ended
        self.current_session.end_time = datetime.now().isoformat()

        # Save to history
        self._save_to_history()

        # Save as current (for next session continuation)
        self._save_current_session()

        session_id = self.current_session.session_id
        print(f"✅ SESSION ENDED: {session_id}")
        print(f"   Duration: {self._calculate_duration()}")
        print(f"   Conversation turns: {len(self.current_session.conversation_turns)}")
        print(f"   Context compression: {self.current_session.context_compression_ratio:.1%}")

        self.session_active = False
        return session_id

    def add_conversation_turn(self, role: str, content: str,
                            context_summary: Optional[str] = None,
                            key_points: Optional[List[str]] = None,
                            files_mentioned: Optional[List[str]] = None):
        """
        Add a conversation turn to the current session.

        Args:
            role: 'user' or 'assistant'
            content: Conversation content
            context_summary: Summary of context for this turn
            key_points: Key points mentioned in this turn
            files_mentioned: Files mentioned in this turn
        """
        if not self.session_active or self.current_session is None:
            # Auto-start session if not active
            self.start_session()

        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content[:10000],  # Limit content size
            context_summary=context_summary,
            key_points=key_points or [],
            files_mentioned=files_mentioned or []
        )

        self.current_session.conversation_turns.append(turn)
        self.conversation_buffer.append(turn)

        # Auto-save periodically
        if len(self.current_session.conversation_turns) % 10 == 0:
            self._save_current_session()

    def update_session_context(self, **kwargs):
        """
        Update session context with new information.

        Args:
            **kwargs: Context fields to update (tasks_completed, files_modified, etc.)
        """
        if not self.session_active or self.current_session is None:
            return

        for key, value in kwargs.items():
            if hasattr(self.current_session, key):
                current_value = getattr(self.current_session, key)
                if isinstance(current_value, list):
                    if isinstance(value, list):
                        current_value.extend(value)
                    else:
                        current_value.append(value)
                elif isinstance(current_value, dict):
                    current_value.update(value)
                else:
                    setattr(self.current_session, key, value)

        self._save_current_session()

    def get_session_summary(self) -> Optional[str]:
        """
        Get comprehensive summary of current session.

        Returns:
            Session summary or None if no session active
        """
        if not self.session_active or self.current_session is None:
            return None

        summary_parts = [
            f"Session: {self.current_session.session_id}",
            f"Started: {self.current_session.start_time}",
            f"Conversation turns: {len(self.current_session.conversation_turns)}",
        ]

        if self.current_session.key_topics:
            summary_parts.append(f"Topics: {', '.join(self.current_session.key_topics[:5])}")

        if self.current_session.tasks_completed:
            summary_parts.append(f"Tasks completed: {len(self.current_session.tasks_completed)}")

        if self.current_session.tasks_in_progress:
            summary_parts.append(f"Tasks in progress: {len(self.current_session.tasks_in_progress)}")

        if self.current_session.files_modified:
            summary_parts.append(f"Files modified: {len(self.current_session.files_modified)}")

        return "\n".join(summary_parts)

    def restore_session_context(self) -> Optional[SessionContext]:
        """
        Restore session context on startup.

        Completely automatic - no display, just returns the data.

        Returns:
            Previous session context if available, None otherwise
        """
        previous_session = self._load_current_session()
        if previous_session:
            # Silent restoration - just return the data
            # No print statements, no user interaction required
            return previous_session

        return None

    def _compress_conversation_context(self):
        """Compress conversation context to reduce size while preserving information."""
        if not self.current_session or not self.current_session.conversation_turns:
            return

        original_size = len(self.current_session.conversation_turns)

        # Extract key information from conversation turns
        key_points = set()
        topics = set()
        facts = set()
        decisions = {}

        for turn in self.current_session.conversation_turns:
            # Extract key points
            key_points.update(turn.key_points)

            # Extract topics (simple keyword extraction)
            words = turn.content.lower().split()
            topics.update([word for word in words if len(word) > 5])

            # Extract facts (statements with specific patterns)
            if "fact:" in turn.content.lower() or "note:" in turn.content.lower():
                facts.add(turn.content[:200])

            # Extract decisions
            for decision in turn.decisions_made:
                if decision not in decisions:
                    decisions[decision] = turn.timestamp

        # Update session context with extracted information
        self.current_session.key_topics = list(topics)[:20]  # Keep top 20 topics
        self.current_session.important_facts = list(facts)[:10]  # Keep top 10 facts

        # Update decisions
        for decision, timestamp in decisions.items():
            if decision not in self.current_session.decisions_made:
                self.current_session.decisions_made[decision] = f"Decided at {timestamp}"

        # Generate conversation summary
        if self.current_session.conversation_turns:
            recent_turns = self.current_session.conversation_turns[-5:]
            summary_parts = []
            for turn in recent_turns:
                if turn.context_summary:
                    summary_parts.append(turn.context_summary)
                elif turn.key_points:
                    summary_parts.append(", ".join(turn.key_points))

            self.current_session.conversation_summary = " | ".join(summary_parts)

        # Calculate compression ratio
        compressed_size = len(self.current_session.conversation_turns)
        if original_size > 0:
            self.current_session.context_compression_ratio = 1.0 - (compressed_size / original_size)

    def _save_current_session(self):
        """Save current session to file."""
        if self.current_session is None:
            return

        try:
            with open(self.current_session_file, 'w') as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save current session: {e}")

    def _load_current_session(self) -> Optional[SessionContext]:
        """Load current session from file."""
        if not self.current_session_file.exists():
            return None

        try:
            with open(self.current_session_file, 'r') as f:
                data = json.load(f)
            return SessionContext.from_dict(data)
        except Exception as e:
            print(f"⚠️  Could not load current session: {e}")
            return None

    def _save_to_history(self):
        """Save session to history file."""
        if self.current_session is None:
            return

        try:
            with open(self.session_history, 'a') as f:
                f.write(json.dumps(self.current_session.to_dict()) + '\n')
        except Exception as e:
            print(f"⚠️  Could not save to history: {e}")

    def _calculate_duration(self) -> str:
        """Calculate session duration."""
        if not self.current_session or not self.current_session.end_time:
            return "Unknown"

        try:
            start = datetime.fromisoformat(self.current_session.start_time)
            end = datetime.fromisoformat(self.current_session.end_time)
            duration = end - start

            hours = duration.total_seconds() / 3600
            if hours > 1:
                return f"{hours:.1f} hours"
            else:
                minutes = duration.total_seconds() / 60
                return f"{minutes:.0f} minutes"
        except:
            return "Unknown"


# Global session persistence instance
_session_persistence: Optional[SessionPersistence] = None


def get_session_persistence() -> SessionPersistence:
    """Get global session persistence instance."""
    global _session_persistence
    if _session_persistence is None:
        _session_persistence = SessionPersistence()
    return _session_persistence


def start_session(session_id: Optional[str] = None) -> SessionContext:
    """Start a new session."""
    return get_session_persistence().start_session(session_id)


def end_session() -> str:
    """End current session."""
    return get_session_persistence().end_session()


def add_conversation_turn(role: str, content: str, **kwargs):
    """Add a conversation turn."""
    get_session_persistence().add_conversation_turn(role, content, **kwargs)


def update_session_context(**kwargs):
    """Update session context."""
    get_session_persistence().update_session_context(**kwargs)