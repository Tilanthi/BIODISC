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
