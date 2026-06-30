#!/usr/bin/env python3
"""Test configuration loading"""
import sys
sys.path.insert(0, '.')

from biodisc_core.autonomous.config import AutonomousConfig

# Test 1: Default config
default_config = AutonomousConfig()
print("Default config memory limit:", default_config.max_memory_percent)

# Test 2: Config with dictionary override
config_dict = {
    'max_cpu_percent': 80.0,
    'max_memory_percent': 80.0,
    'idle_timeout_minutes': 1
}

test_config = AutonomousConfig(**config_dict)
print("Test config memory limit:", test_config.max_memory_percent)
print("Test config CPU limit:", test_config.max_cpu_percent)