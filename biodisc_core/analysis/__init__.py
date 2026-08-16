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
Analysis Module - Genuine Discovery Capabilities

This package provides computational analysis, cross-domain synthesis, and original
insight generation capabilities for BIODISC to create genuine scientific discoveries.

Modules:
- computational_biology: Statistical and computational analysis of biological data
- cross_domain_synthesis: Multi-domain integration and novel connection discovery
- insight_generator: Original insight and hypothesis generation

Date: 2026-06-28
Version: 1.0.0
"""

# Import main analysis classes
from .computational_biology import ComputationalBiologyAnalyzer, create_computational_biology_analyzer
from .cross_domain_synthesis import CrossDomainSynthesisEngine, create_cross_domain_synthesis_engine
from .insight_generator import OriginalInsightGenerator, create_insight_generator

# Export factory functions
__all__ = [
    'ComputationalBiologyAnalyzer',
    'create_computational_biology_analyzer',
    'CrossDomainSynthesisEngine',
    'create_cross_domain_synthesis_engine',
    'OriginalInsightGenerator',
    'create_insight_generator'
]
