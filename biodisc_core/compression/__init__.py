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