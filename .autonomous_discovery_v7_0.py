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
"""RETIRED (2026-07-14) — legacy standalone discovery loop. Do not run.

An earlier fixed-pipeline loop superseded by `.fixed_autonomous_discovery.py`
(the canonical loop supervised by discovery_watchdog.py). Retired per the
single-always-on-path consolidation (ASTRA §11). The canonical loop now writes
exclusively through the machine-verification chokepoint
(discovery_store.append_verified); this older loop did not.

Canonical path: python discovery_watchdog.py  (-> .fixed_autonomous_discovery.py)
"""
import sys

if __name__ == "__main__":
    sys.stderr.write(
        "DEPRECATED: .autonomous_discovery_v7_0.py is a retired legacy loop.\n"
        "Canonical path: python discovery_watchdog.py  (-> .fixed_autonomous_discovery.py)\n"
        "Refusing to run.\n"
    )
    sys.exit(2)
