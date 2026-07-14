#!/usr/bin/env python3
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
