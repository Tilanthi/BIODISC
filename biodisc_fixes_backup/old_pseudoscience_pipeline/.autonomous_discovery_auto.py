
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, '/Users/gjw255/astrodata/SWARM/BIODISC')

try:
    from biodisc_core.reasoning.v73_autonomous_discovery import get_autonomous_discovery_system, AutonomousDiscoveryConfig

    config = AutonomousDiscoveryConfig(
        max_cpu_percent=15.0,
        max_hours_per_week=168.0,  # 24x7 - run continuously when computer is on
        idle_timeout_minutes=1,  # Reduced from 2 for faster discovery
        min_confidence_to_store=0.65,  # 65% confidence - appropriate for bioscience
        min_evidence_count=1,  # 1 evidence source - more flexible for bioscience
        bioscience_mode=True,  # Enable bioscience-aware validation
        questions_per_cycle=10,  # Increased from 3 for faster discovery
        cycle_interval_seconds=2,  # Reduced for faster discovery cycles
        log_all_discoveries=True,
        discovery_log_path=str('/Users/gjw255/astrodata/SWARM/BIODISC/autonomous_discoveries.jsonl')
    )

    system = get_autonomous_discovery_system(config)
    system.start()

    print("✓ Autonomous discovery started in background")

    # Keep process alive
    try:
        while True:
            time.sleep(60)
            status = system.get_status()
            if not status.get('running', False):
                break
    except KeyboardInterrupt:
        system.stop()
        raise

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
