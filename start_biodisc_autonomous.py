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
"""DEPRECATED entry point — redirects to the canonical discovery watchdog.

Historically this launched the V73 autonomous orchestrator (create_biodisc_system
+ V74 filter + memory palace), the pseudo-science-era architecture. That system
ran ALONGSIDE the fixed real-data pipeline — the exact "legacy loop beside the
new one" hazard (ASTRA §11). It is retired.

The single always-on path is now: launchd -> discovery_watchdog.py ->
.fixed_autonomous_discovery.py (the fixed real-data pipeline, verified through
the write chokepoint). This stub keeps the old filename alive as a redirect so
any caller (or stale launchd reference) lands on the canonical path rather than
reviving the legacy loop.
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    watchdog = PROJECT_ROOT / "discovery_watchdog.py"
    logger.warning("start_biodisc_autonomous.py is DEPRECATED (legacy V73 loop retired).")
    logger.warning("Redirecting to the canonical discovery watchdog -> %s", watchdog)
    if not watchdog.exists():
        logger.error("Canonical watchdog not found; refusing to start any legacy loop.")
        return 1
    # The watchdog's single-process guard prevents duplicate discovery processes,
    # so exec'ing it is safe even if another watchdog instance is already running.
    os.execv(sys.executable, [sys.executable, str(watchdog)])


if __name__ == "__main__":
    sys.exit(main())
