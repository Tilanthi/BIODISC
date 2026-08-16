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
"""RETIRED (2026-07-14) — legacy V73 discovery loop. Do not run.

This file previously ran the V73 autonomous orchestrator and wrote discoveries
directly to autonomous_discoveries.jsonl, BYPASSING the machine-verification
chokepoint — a fiction surface. It is retired per the single-always-on-path
consolidation (ASTRA §11: never run a legacy loop alongside the new one).

The canonical always-on path is now:
    launchd -> discovery_watchdog.py -> .fixed_autonomous_discovery.py
whose every write passes the write chokepoint (discovery_store.append_verified).

(biodisc_auto_start.py previously regenerated this file at runtime; it no longer
does — it launches the canonical watchdog instead.)
"""
import sys

if __name__ == "__main__":
    sys.stderr.write(
        "DEPRECATED: .autonomous_discovery_auto.py is a retired legacy loop.\n"
        "Canonical path: python discovery_watchdog.py  (-> .fixed_autonomous_discovery.py)\n"
        "Refusing to run.\n"
    )
    sys.exit(2)
