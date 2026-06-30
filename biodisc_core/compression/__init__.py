"""
PHOTON-inspired compression utilities for BIODISC

Provides hierarchical compression, bottom-up encoding, top-down decoding,
and bounded local attention processing for memory-efficient AI operations.

Core Components:
- Hierarchical processing base classes
- Compression utilities and data structures
- Encoder/decoder patterns
- Memory optimization tools
"""

from .hierarchical import (
    HierarchicalProcessor,
    HierarchicalLevel,
    CompressionResult,
    ReconstructionResult,
    create_hierarchical_processor
)

__all__ = [
    "HierarchicalProcessor",
    "HierarchicalLevel",
    "CompressionResult",
    "ReconstructionResult",
    "create_hierarchical_processor",
]

# Version tracking
__version__ = "1.0.0"
__date__ = "2026-06-26"