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
