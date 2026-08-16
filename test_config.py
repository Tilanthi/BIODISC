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