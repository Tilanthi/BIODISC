"""
Hierarchical processing utilities for PHOTON-inspired compression

Provides base classes and utilities for implementing hierarchical compression,
bottom-up encoding, and top-down decoding patterns across BIODISC systems.

Design Principles:
- Bottom-up encoding: compress fine-grained data into low-rate summaries
- Top-down decoding: reconstruct detailed data from compressed summaries
- Bounded local attention: process chunks in parallel with local focus
- Hierarchical consistency: align summaries with reconstructions
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import time
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class HierarchicalLevel:
    """
    Configuration for a single level in hierarchical processing

    Attributes:
        level: Level index (0 = coarsest, higher = finer)
        chunk_size: Number of lower-level units per chunk at this level
        compression_ratio: Target compression ratio for this level
        description: Human-readable description of this level
    """
    level: int
    chunk_size: int
    compression_ratio: float
    description: str = ""

    def __post_init__(self):
        """Validate level configuration"""
        if self.level < 0:
            raise ValueError(f"Level must be >= 0, got {self.level}")
        if self.chunk_size <= 0:
            raise ValueError(f"Chunk size must be > 0, got {self.chunk_size}")
        if self.compression_ratio <= 0:
            raise ValueError(f"Compression ratio must be > 0, got {self.compression_ratio}")
        if not self.description:
            self.description = f"Level {self.level} (chunk_size={self.chunk_size}, ratio={self.compression_ratio:.1f}x)"


@dataclass
class CompressionResult:
    """
    Result of hierarchical compression operation

    Attributes:
        compressed_data: Compressed representation
        compression_ratio: Actual compression ratio achieved
        compression_time: Time taken for compression (seconds)
        original_size: Size of original data (bytes or tokens)
        compressed_size: Size of compressed data (bytes or tokens)
        metadata: Additional compression metadata
    """
    compressed_data: Any
    compression_ratio: float
    compression_time: float
    original_size: int
    compressed_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def efficiency_score(self) -> float:
        """Calculate compression efficiency (ratio/time)"""
        if self.compression_time > 0:
            return self.compression_ratio / self.compression_time
        return 0.0


@dataclass
class ReconstructionResult:
    """
    Result of hierarchical reconstruction operation

    Attributes:
        reconstructed_data: Reconstructed data
        reconstruction_time: Time taken for reconstruction (seconds)
        similarity_score: Similarity to original (0.0 to 1.0)
        reconstruction_level: Level reconstructed to
        metadata: Additional reconstruction metadata
    """
    reconstructed_data: Any
    reconstruction_time: float
    similarity_score: float
    reconstruction_level: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def quality_score(self) -> float:
        """Calculate reconstruction quality (similarity/time)"""
        if self.reconstruction_time > 0:
            return self.similarity_score / self.reconstruction_time
        return 0.0


class HierarchicalProcessor(ABC):
    """
    Abstract base class for hierarchical processing systems

    Implements the core PHOTON pattern:
    1. Bottom-up encoding: compress into low-rate summaries
    2. Top-down decoding: reconstruct from summaries with bounded attention
    3. Hierarchical consistency: maintain alignment between levels
    """

    def __init__(self, levels: List[HierarchicalLevel], name: str = "HierarchicalProcessor"):
        """
        Initialize hierarchical processor

        Args:
            levels: List of hierarchical levels (coarsest to finest)
            name: Name for this processor instance
        """
        if not levels:
            raise ValueError("Must provide at least one level")

        # Sort levels by index (coarsest first)
        self.levels = sorted(levels, key=lambda l: l.level)
        self.name = name

        # Validate levels form proper hierarchy
        for i in range(len(self.levels) - 1):
            if self.levels[i].level >= self.levels[i + 1].level:
                raise ValueError(f"Levels must be strictly increasing: {self.levels[i].level} >= {self.levels[i + 1].level}")

        # Processing state
        self.compression_cache: Dict[str, CompressionResult] = {}
        self.reconstruction_cache: Dict[str, ReconstructionResult] = {}

        logger.info(f"Initialized {self.name} with {len(self.levels)} levels")
        for level in self.levels:
            logger.info(f"  {level.description}")

    def encode_bottom_up(self, data: Any, cache_key: Optional[str] = None) -> List[Any]:
        """
        Encode data through hierarchical compression (bottom-up)

        Args:
            data: Original fine-grained data to compress
            cache_key: Optional cache key for storing results

        Returns:
            List of compressed representations (coarsest to finest)
        """
        start_time = time.time()

        # Check cache
        if cache_key and cache_key in self.compression_cache:
            logger.debug(f"Cache hit for encode_bottom_up: {cache_key}")
            return self.compression_cache[cache_key].compressed_data

        # Bottom-up encoding
        current_data = data
        hierarchy = [current_data]  # Level 0 = original data

        for level_obj in self.levels:
            # Compress current level to next level
            compressed = self._compress_level(current_data, level_obj)
            hierarchy.append(compressed)
            current_data = compressed

        encoding_time = time.time() - start_time

        # Calculate compression statistics
        original_size = self._estimate_size(data)
        compressed_size = self._estimate_size(hierarchy[-1])
        compression_ratio = original_size / max(compressed_size, 1)

        # Create compression result
        result = CompressionResult(
            compressed_data=hierarchy,
            compression_ratio=compression_ratio,
            compression_time=encoding_time,
            original_size=original_size,
            compressed_size=compressed_size,
            metadata={"levels": len(self.levels)}
        )

        # Cache result
        if cache_key:
            self.compression_cache[cache_key] = result

        logger.info(f"{self.name} encoded data in {encoding_time:.3f}s with {compression_ratio:.1f}x compression")

        return hierarchy

    def decode_top_down(self, hierarchy: List[Any], query: Any,
                      target_level: int = 0, cache_key: Optional[str] = None) -> Any:
        """
        Decode data through hierarchical reconstruction (top-down)

        Args:
            hierarchy: Compressed hierarchy (coarsest to finest)
            query: Query or context for reconstruction
            target_level: Target reconstruction level (0 = finest)
            cache_key: Optional cache key for storing results

        Returns:
            Reconstructed data at target level
        """
        start_time = time.time()

        # Check cache
        if cache_key and cache_key in self.reconstruction_cache:
            logger.debug(f"Cache hit for decode_top_down: {cache_key}")
            return self.reconstruction_cache[cache_key].reconstructed_data

        # Validate hierarchy
        if not hierarchy:
            raise ValueError("Hierarchy cannot be empty")
        if target_level < 0 or target_level >= len(hierarchy):
            raise ValueError(f"Invalid target_level: {target_level} (must be 0-{len(hierarchy)-1})")

        # Start from coarsest level
        current_data = hierarchy[-1]

        # Top-down reconstruction
        for level_idx in range(len(hierarchy) - 1, 0, -1):
            level_obj = self.levels[level_idx - 1]

            # Reconstruct from coarser to finer level
            reconstructed = self._reconstruct_level(
                current_data,
                hierarchy[level_idx - 1],
                level_obj,
                query
            )
            current_data = reconstructed

            # Early exit if target reached
            if level_idx == target_level:
                break

        reconstruction_time = time.time() - start_time

        # Calculate similarity to original
        original_data = hierarchy[0]
        similarity = self._calculate_similarity(original_data, current_data)

        # Create reconstruction result
        result = ReconstructionResult(
            reconstructed_data=current_data,
            reconstruction_time=reconstruction_time,
            similarity_score=similarity,
            reconstruction_level=target_level,
            metadata={"query": str(query)[:100] if query else ""}
        )

        # Cache result
        if cache_key:
            self.reconstruction_cache[cache_key] = result

        logger.info(f"{self.name} reconstructed data in {reconstruction_time:.3f}s with {similarity:.3f} similarity")

        return current_data

    @abstractmethod
    def _compress_level(self, data: Any, level: HierarchicalLevel) -> Any:
        """
        Compress data to next hierarchical level

        Args:
            data: Data at current level
            level: Target level configuration

        Returns:
            Compressed data at next level
        """
        pass

    @abstractmethod
    def _reconstruct_level(self, coarse_data: Any, fine_reference: Any,
                          level: HierarchicalLevel, query: Any) -> Any:
        """
        Reconstruct data from coarser level

        Args:
            coarse_data: Data at coarser level
            fine_reference: Reference data at finer level
            level: Level configuration for reconstruction
            query: Query context for reconstruction

        Returns:
            Reconstructed data at finer level
        """
        pass

    def _estimate_size(self, data: Any) -> int:
        """
        Estimate size of data in bytes/tokens

        Args:
            data: Data to estimate size for

        Returns:
            Estimated size
        """
        if isinstance(data, (str, list, dict)):
            return len(str(data))
        elif isinstance(data, (int, float, bool)):
            return 1
        else:
            # For complex objects, use string representation
            return len(str(data))

    def _calculate_similarity(self, original: Any, reconstructed: Any) -> float:
        """
        Calculate similarity between original and reconstructed data

        Args:
            original: Original data
            reconstructed: Reconstructed data

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple string-based similarity (can be overridden)
        orig_str = str(original).lower()
        recon_str = str(reconstructed).lower()

        if not orig_str and not recon_str:
            return 1.0
        if not orig_str or not recon_str:
            return 0.0

        # Simple character overlap similarity
        orig_chars = set(orig_str)
        recon_chars = set(recon_str)

        if not orig_chars or not recon_chars:
            return 0.0

        overlap = len(orig_chars & recon_chars)
        total = len(orig_chars | recon_chars)

        return overlap / total if total > 0 else 0.0

    def clear_cache(self) -> None:
        """Clear compression and reconstruction caches"""
        self.compression_cache.clear()
        self.reconstruction_cache.clear()
        logger.info(f"Cleared caches for {self.name}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "name": self.name,
            "num_levels": len(self.levels),
            "compression_cache_size": len(self.compression_cache),
            "reconstruction_cache_size": len(self.reconstruction_cache),
            "levels": [
                {
                    "level": level.level,
                    "chunk_size": level.chunk_size,
                    "compression_ratio": level.compression_ratio,
                    "description": level.description
                }
                for level in self.levels
            ]
        }


class ChunkProcessor:
    """
    Utility for chunking data with bounded local attention

    Implements PHOTON's chunk-based parallel processing pattern.
    """

    def __init__(self, chunk_size: int = 4):
        """
        Initialize chunk processor

        Args:
            chunk_size: Number of units per chunk
        """
        self.chunk_size = chunk_size

    def chunk_data(self, data: Any) -> List[Any]:
        """
        Split data into chunks

        Args:
            data: Data to chunk (string, list, or dict)

        Returns:
            List of chunks
        """
        if isinstance(data, str):
            return self._chunk_string(data)
        elif isinstance(data, list):
            return self._chunk_list(data)
        elif isinstance(data, dict):
            return self._chunk_dict(data)
        else:
            # For other types, treat as single chunk
            return [data]

    def _chunk_string(self, text: str) -> List[str]:
        """Chunk string by sentences"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if len(current_chunk) >= self.chunk_size:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = []

        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')

        return chunks if chunks else [text]

    def _chunk_list(self, data: List[Any]) -> List[List[Any]]:
        """Chunk list into sublists"""
        chunks = []
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunks.append(chunk)
        return chunks if chunks else [data]

    def _chunk_dict(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk dict into subdicts"""
        items = list(data.items())
        chunks = []

        for i in range(0, len(items), self.chunk_size):
            chunk_items = items[i:i + self.chunk_size]
            chunk = dict(chunk_items)
            chunks.append(chunk)

        return chunks if chunks else [data]

    def get_conditioning_context(self, chunks: List[Any],
                                current_chunk_idx: int) -> Any:
        """
        Get conditioning context for a chunk from previous chunks

        Args:
            chunks: All chunks
            current_chunk_idx: Index of current chunk

        Returns:
            Conditioning context (concatenated previous chunks)
        """
        if current_chunk_idx == 0:
            return ""

        previous_chunks = chunks[:current_chunk_idx]

        # Simple concatenation (can be enhanced with summarization)
        if isinstance(previous_chunks[0], str):
            return " ".join(previous_chunks)
        elif isinstance(previous_chunks[0], list):
            # Flatten lists
            result = []
            for chunk in previous_chunks:
                result.extend(chunk)
            return result
        elif isinstance(previous_chunks[0], dict):
            # Merge dicts
            result = {}
            for chunk in previous_chunks:
                result.update(chunk)
            return result
        else:
            return previous_chunks


def create_hierarchical_processor(levels: List[HierarchicalLevel],
                                 processor_class: type,
                                 name: str = "HierarchicalProcessor") -> HierarchicalProcessor:
    """
    Factory function for creating hierarchical processors

    Args:
        levels: List of hierarchical levels
        processor_class: Class of processor to create
        name: Name for the processor instance

    Returns:
        Configured hierarchical processor instance
    """
    return processor_class(levels, name)


def generate_cache_key(data: Any, context: Optional[str] = None) -> str:
    """
    Generate cache key from data and context

    Args:
        data: Data to generate key from
        context: Optional context string

    Returns:
        Cache key string
    """
    # Create hash from data and context
    data_str = str(data)
    if context:
        data_str += context

    return hashlib.md5(data_str.encode()).hexdigest()


# Default hierarchical level configurations
def default_mce_levels() -> List[HierarchicalLevel]:
    """Default levels for Meta-Context Engine (5 levels)"""
    return [
        HierarchicalLevel(0, 16, 100.0, "Coarsest context (16:1 chunks, 100x compression)"),
        HierarchicalLevel(1, 8, 50.0, "Medium-coarse context (8:1 chunks, 50x compression)"),
        HierarchicalLevel(2, 4, 20.0, "Medium context (4:1 chunks, 20x compression)"),
        HierarchicalLevel(3, 2, 10.0, "Medium-fine context (2:1 chunks, 10x compression)"),
        HierarchicalLevel(4, 1, 1.0, "Finest context (1:1 chunks, no compression)")
    ]


def default_domain_levels() -> List[HierarchicalLevel]:
    """Default levels for Domain compression (3 levels)"""
    return [
        HierarchicalLevel(0, 1, 100.0, "Core concepts (100x compression)"),
        HierarchicalLevel(1, 1, 10.0, "Domain capabilities (10x compression)"),
        HierarchicalLevel(2, 1, 2.0, "Detailed knowledge (2x compression)")
    ]


def default_discovery_levels() -> List[HierarchicalLevel]:
    """Default levels for Discovery compression (3 levels)"""
    return [
        HierarchicalLevel(0, 1, 100.0, "Meta-patterns (100x compression)"),
        HierarchicalLevel(1, 1, 10.0, "Domain summaries (10x compression)"),
        HierarchicalLevel(2, 1, 2.0, "Detailed discoveries (2x compression)")
    ]


def default_long_context_levels() -> List[HierarchicalLevel]:
    """Default levels for Long-Context compression (3 levels)"""
    return [
        HierarchicalLevel(0, 1, 50.0, "Coarse summaries (50x compression)"),
        HierarchicalLevel(1, 1, 10.0, "Medium summaries (10x compression)"),
        HierarchicalLevel(2, 1, 2.0, "Fine details (2x compression)")
    ]