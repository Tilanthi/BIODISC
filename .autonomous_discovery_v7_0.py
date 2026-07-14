#!/usr/bin/env python3
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
