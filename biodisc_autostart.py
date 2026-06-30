"""
BIODISC Auto-Start Module

Import this module at the beginning of any BIODISC session to ensure
autonomous discovery is always running in the background.

Usage:
    import biodisc_autostart  # Auto-starts autonomous discovery

The autonomous discovery will:
- Wait for 2 minutes of idle time
- Generate curiosity questions from knowledge gaps
- Explore questions using discovery capabilities
- Validate discoveries (95%+ confidence required)
- Automatically store validated discoveries to memory palace

Resource limits:
- Max 5% CPU usage
- Max 10 hours per week
- Pauses during active user interaction
"""

from biodisc_auto_start import ensure_autonomous_discovery

# Auto-start on import
ensure_autonomous_discovery()
