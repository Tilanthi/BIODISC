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
STAN_IX_ASTRO Mathematical Reasoning Module

This module contains enhanced mathematical reasoning capabilities for STAN,
including the Aletheia-style 3-agent architecture for IMO-ProofBench problems.

Components:
- AletheiaBIODISCSystem: Enhanced 3-agent architecture (Generator-Verifier-Reviser)
- AletheiaProofSystem: Basic 3-agent architecture
"""

from .aletheia_stan_architecture import (
    AletheiaBIODISCSystem,
    ProofStrategy,
    VerdictType,
    ProofAttempt,
    ValidationResult,
    GeneratorOutput
)

__all__ = [
    'AletheiaBIODISCSystem',
    'ProofStrategy',
    'VerdictType',
    'ProofAttempt',
    'ValidationResult',
    'GeneratorOutput'
]
