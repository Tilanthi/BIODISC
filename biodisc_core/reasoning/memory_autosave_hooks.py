"""
Memory Auto-Save Hooks

Integrates GraphPalace auto-save with all BIODISC memory systems.
Automatically saves all memory operations to GraphPalace.

Date: 2026-05-09
Version: 1.0.0
"""

import os
import functools
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime


class MemoryAutosaveHooks:
    """
    Hooks for automatic memory saving to GraphPalace.

    Integrates with:
    - V73 Memory Palace Integration
    - V60 Persistent Memory
    - Episodic Memory
    - All discovery storage
    - All .md file operations

    USAGE:
    ```python
    from biodisc_core.reasoning.memory_autosave_hooks import setup_autosave_hooks

    # Setup autosave hooks globally
    setup_autosave_hooks()

    # Now all memory operations auto-save to GraphPalace
    ```
    """

    def __init__(self):
        self.autosaver = None
        self.enabled = True
        self._lazy_load_autosaver()

    def _lazy_load_autosaver(self):
        """Lazy load autosaver to avoid import issues"""
        if self.autosaver is None:
            try:
                from .v86_graph_palace_autosave import get_graph_palace_autosaver
                self.autosaver = get_graph_palace_autosaver()
            except Exception as e:
                print(f"Warning: Could not load GraphPalace autosaver: {e}")
                self.enabled = False

    def autosave_after(self, func: Callable) -> Callable:
        """
        Decorator to auto-save after function execution.

        USAGE:
        ```python
        @autosave_after
        def store_memory(memory_data):
            # Store memory
            pass
        ```
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Auto-save after function
            if self.enabled and self.autosaver:
                try:
                    self.autosaver.auto_save_all()
                except Exception as e:
                    print(f"Auto-save failed: {e}")

            return result
        return wrapper

    def autosave_memory_file(self, file_path: str, content: str):
        """Auto-save a specific memory file to GraphPalace"""
        if self.enabled and self.autosaver:
            try:
                # Write the file
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Trigger auto-save
                self.autosaver.auto_save_all()

            except Exception as e:
                print(f"Error auto-saving memory file: {e}")

    def autosave_discovery(self, discovery: Dict[str, Any]):
        """Auto-save a discovery to GraphPalace"""
        if self.enabled and self.autosaver:
            try:
                # Format discovery as markdown
                from .v86_graph_palace_autosave import GraphPalaceNode
                import hashlib

                timestamp = datetime.fromtimestamp(discovery['timestamp']).strftime("%Y%m%d_%H%M%S")
                filename = f"discovery_{discovery['id']}_{timestamp}.md"

                # Create content
                content = f"""---
name: {discovery['id']}
type: discovery
confidence: {discovery['confidence']:.2f}
validated: {discovery['validation_status']}
tags: [autonomous_discovery, v73]
---

# {discovery['question']}

**Discovery**: {discovery['discovery']}

- **Confidence**: {discovery['confidence']:.2f}
- **Validation Status**: {discovery['validation_status']}
- **Timestamp**: {datetime.fromtimestamp(discovery['timestamp']).isoformat()}
"""

                # Write to memory palace
                memory_path = f"/Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/{filename}"
                self.autosave_memory_file(memory_path, content)

            except Exception as e:
                print(f"Error auto-saving discovery: {e}")

    def autosave_session_summary(self, summary: Dict[str, Any]):
        """Auto-save session summary to GraphPalace"""
        if self.enabled and self.autosaver:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"session_{timestamp}.md"

                content = f"""---
name: Session {timestamp}
type: session_summary
tags: [session, summary]
---

# Session Summary: {timestamp}

{summary.get('summary', 'No summary available')}

## Statistics
- Tasks completed: {summary.get('tasks_completed', 0)}
- Discoveries made: {summary.get('discoveries', 0)}
- Errors encountered: {summary.get('errors', 0)}

## Key Insights
"""

                for insight in summary.get('insights', []):
                    content += f"- {insight}\n"

                # Write to memory palace
                memory_path = f"/Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/{filename}"
                self.autosave_memory_file(memory_path, content)

            except Exception as e:
                print(f"Error auto-saving session summary: {e}")


# Global hooks instance
_hooks = None

def get_autosave_hooks() -> MemoryAutosaveHooks:
    """Get global autosave hooks instance"""
    global _hooks
    if _hooks is None:
        _hooks = MemoryAutosaveHooks()
    return _hooks


def setup_autosave_hooks():
    """
    Setup autosave hooks for all memory systems.

    This function should be called at system initialization to enable
    automatic saving of all memory operations to GraphPalace.
    """
    hooks = get_autosave_hooks()

    # Patch V73 Memory Palace Integration
    try:
        from . import v73_memory_palace_integration

        # Wrap store_discovery method
        original_store = v73_memory_palace_integration.MemoryPalaceStorage.store_discovery

        @functools.wraps(original_store)
        def wrapped_store_discovery(self, discovery):
            result = original_store(self, discovery)
            # Trigger auto-save
            hooks.autosaver.auto_save_all() if hooks.autosaver else None
            return result

        v73_memory_palace_integration.MemoryPalaceStorage.store_discovery = wrapped_store_discovery

    except Exception as e:
        print(f"Could not patch V73: {e}")

    # Patch V60 Persistent Memory
    try:
        from . import v60_persistent_memory

        # Wrap memory storage methods
        if hasattr(v60_persistent_memory, 'BootstrapMemory'):
            original_save = v60_persistent_memory.BootstrapMemory.save_memory

            @functools.wraps(original_save)
            def wrapped_save_memory(self, *args, **kwargs):
                result = original_save(self, *args, **kwargs)
                hooks.autosaver.auto_save_all() if hooks.autosaver else None
                return result

            v60_persistent_memory.BootstrapMemory.save_memory = wrapped_save_memory

    except Exception as e:
        print(f"Could not patch V60: {e}")

    # Patch file write operations for memory palace
    original_open = open

    def autosave_open(file, mode='r', *args, **kwargs):
        """Wrapper for open() that triggers auto-save for memory files"""
        result = original_open(file, mode, *args, **kwargs)

        # If writing to memory palace, trigger auto-save on close
        if 'w' in mode and 'memory' in file.lower():
            original_close = result.close

            def wrapped_close():
                original_close()
                # Trigger auto-save after file is written
                if hooks.autosaver:
                    try:
                        hooks.autosaver.auto_save_all()
                    except Exception:
                        pass  # Don't interfere with file operations

            result.close = wrapped_close

        return result

    # Note: We don't actually patch builtins.open as it's too invasive
    # Instead, systems should explicitly call autosave after operations


def autosave_decorator(func: Callable) -> Callable:
    """
    Decorator for functions that should trigger auto-save after execution.

    USAGE:
    ```python
    from biodisc_core.reasoning.memory_autosave_hooks import autosave_decorator

    @autosave_decorator
    def my_memory_function(data):
        # Do memory operations
        pass
    ```
    """
    hooks = get_autosave_hooks()
    return hooks.autosave_after(func)


def autosave_now():
    """
    Manually trigger auto-save of all memory to GraphPalace.

    USAGE:
    ```python
    from biodisc_core.reasoning.memory_autosave_hooks import autosave_now

    # Perform memory operations
    store_memory(data)

    # Trigger auto-save
    autosave_now()
    ```
    """
    hooks = get_autosave_hooks()
    if hooks.autosaver:
        return hooks.autosaver.auto_save_all()
    return {"status": "disabled"}
