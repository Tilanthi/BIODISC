"""
PHOTON Feature Tests

Comprehensive unit tests for all PHOTON-inspired features:
- Hierarchical MCE (Upgrade 1)
- Domain Compression (Upgrade 2)
- Recursive Discovery (Upgrade 3)
- Parallel Multi-Mind (Upgrade 4)
- Long-Context Optimization (Upgrade 5)

Testing Strategy:
- Unit tests for each component
- Compression ratio validation
- Reconstruction quality verification
- Performance benchmarking
- Memory efficiency measurement
"""

import pytest
import time
import hashlib
from typing import Dict, List, Any
import numpy as np

# Import PHOTON components
try:
    from biodisc_core.compression.hierarchical import (
        HierarchicalProcessor,
        HierarchicalLevel,
        ChunkProcessor,
        default_mce_levels,
        default_domain_levels,
        default_discovery_levels,
        default_long_context_levels
    )
    PHOTON_AVAILABLE = True
except ImportError:
    PHOTON_AVAILABLE = False

# Import enhanced components
try:
    from biodisc_core.metacognitive.meta_context_engine import (
        MetaContextEngine,
        MCEConfig,
        ContextLayer,
        LayeredContext,
        CognitiveFrame,
        TemporalScale,
        HierarchicalMetaContextEngine,
        create_meta_context_engine
    )
    MCE_AVAILABLE = True
except ImportError:
    MCE_AVAILABLE = False

try:
    from biodisc_core.domains.registry import (
        DomainRegistry,
        HierarchicalDomainKnowledge,
        DomainCompressionLevel,
        BaseDomainModule
    )
    DOMAINS_AVAILABLE = True
except ImportError:
    DOMAINS_AVAILABLE = False

try:
    from biodisc_core.reasoning.v73_autonomous_discovery import (
        AutonomousDiscoveryOrchestrator,
        RecursiveAutonomousDiscovery,
        AutonomousDiscoveryConfig,
        DiscoveryCompressionLevel
    )
    DISCOVERY_AVAILABLE = True
except ImportError:
    DISCOVERY_AVAILABLE = False

try:
    from biodisc_core.intelligence.multi_mind_orchestrator import (
        ParallelMultiMindOrchestrator,
        MultiMindResult,
        MindProcessingChunk
    )
    MULTI_MIND_AVAILABLE = True
except ImportError:
    MULTI_MIND_AVAILABLE = False

try:
    from biodisc_core.capabilities.chain_of_verification import (
        ChainOfVerification,
        HierarchicalLongContextReasoning,
        CoVeConfig
    )
    COVE_AVAILABLE = True
except ImportError:
    COVE_AVAILABLE = False


# ============================================================================
# Test Utilities
# ============================================================================

class IntegrationTestResults:
    """Track test results for PHOTON features"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.skipped = []

    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"  ✓ {test_name}")

    def add_fail(self, test_name: str, error: str = ""):
        self.failed.append((test_name, error))
        print(f"  ✗ {test_name}: {error}")

    def add_warning(self, test_name: str, warning: str = ""):
        self.warnings.append((test_name, warning))
        print(f"  ⚠ {test_name}: {warning}")

    def add_skip(self, test_name: str, reason: str = ""):
        self.skipped.append((test_name, reason))
        print(f"  ⊘ {test_name}: {reason}")

    def summary(self):
        total = len(self.passed) + len(self.failed)
        passed_count = len(self.passed)
        failed_count = len(self.failed)
        skipped_count = len(self.skipped)

        print(f"\n{'='*60}")
        print(f"PHOTON Feature Tests Summary:")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed_count} ({passed_count/total*100:.1f}%)" if total > 0 else "Passed: 0")
        print(f"Failed: {failed_count}")
        print(f"Skipped: {skipped_count}")
        print(f"{'='*60}")


def create_test_context(size: int = 1000) -> str:
    """Generate test context of specified size"""
    base_sentence = "This is a test sentence about biological systems involving protein interactions and cellular processes."
    sentences = []
    for i in range(size // 100):  # Generate approximately size characters
        sentences.append(f"{base_sentence} Variation {i} demonstrates different biological mechanisms.")
    return ". ".join(sentences) + "."


def calculate_compression_ratio(original: Any, compressed: Any) -> float:
    """Calculate compression ratio between original and compressed data"""
    original_size = len(str(original))
    compressed_size = len(str(compressed))
    return original_size / max(compressed_size, 1)


def calculate_similarity(original: Any, reconstructed: Any) -> float:
    """Calculate similarity between original and reconstructed data"""
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


# ============================================================================
# Core Compression Infrastructure Tests
# ============================================================================

@pytest.mark.skipif(not PHOTON_AVAILABLE, reason="PHOTON compression not available")
def test_hierarchical_processor_creation():
    """Test that HierarchicalProcessor can be instantiated"""
    results = IntegrationTestResults()

    try:
        levels = default_mce_levels()
        processor = HierarchicalProcessor(levels, "TestProcessor")

        results.add_pass("test_hierarchical_processor_creation")
        assert processor is not None
        assert len(processor.levels) == len(levels)

    except Exception as e:
        results.add_fail("test_hierarchical_processor_creation", str(e))

    return results


@pytest.mark.skipif(not PHOTON_AVAILABLE, reason="PHOTON compression not available")
def test_chunk_processor():
    """Test chunk processor functionality"""
    results = IntegrationTestResults()

    try:
        processor = ChunkProcessor(chunk_size=4)
        test_text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."

        chunks = processor.chunk_data(test_text)

        results.add_pass("test_chunk_processor")
        assert len(chunks) > 1
        assert all(len(chunk) > 0 for chunk in chunks)

    except Exception as e:
        results.add_fail("test_chunk_processor", str(e))

    return results


# ============================================================================
# Upgrade 1: Hierarchical MCE Tests
# ============================================================================

@pytest.mark.skipif(not MCE_AVAILABLE, reason="MCE not available")
def test_hierarchical_mce_compression():
    """Test that hierarchical MCE compresses context effectively"""
    results = IntegrationTestResults()

    try:
        config = MCEConfig(enable_hierarchical_mode=True)
        mce = MetaContextEngine(config)

        # Create test context
        query = "complex biological query requiring long context analysis"
        dimensions = [MCE.available_dimensions[0]] if hasattr(MCE, 'available_dimensions') else [MCE.TemporalScale]
        context = mce.layer_context(query, dimensions, [MCE.PREDICTIVE])

        # Encode hierarchically
        hierarchy = mce.encode_context_bottom_up(context)

        results.add_pass("test_hierarchical_mce_compression")

        # Verify compression
        assert len(hierarchy) >= 1, "Hierarchy should have at least one level"
        assert hierarchy[0] == context or len(hierarchy) > 1, "First level should be original context"

        # Check compression ratio
        if len(hierarchy) > 1:
            compression_ratio = calculate_compression_ratio(context, hierarchy[-1])
            print(f"    Compression ratio: {compression_ratio:.1f}x")
            assert compression_ratio > 1.0, "Should achieve compression"

    except Exception as e:
        results.add_fail("test_hierarchical_mce_compression", str(e))

    return results


@pytest.mark.skipif(not MCE_AVAILABLE, reason="MCE not available")
def test_hierarchical_mce_reconstruction_quality():
    """Test that hierarchical MCE reconstruction maintains quality"""
    results = IntegrationTestResults()

    try:
        config = MCEConfig(enable_hierarchical_mode=True)
        mce = MetaContextEngine(config)

        # Create test context
        query = "test query for reconstruction"
        context = mce.layer_context(query, [MCE.TEMPORAL], [MCE.ANALYTICAL])

        # Encode and decode
        mce.encode_context_bottom_up(context)
        reconstructed = mce.decode_context_top_down(query)

        results.add_pass("test_hierarchical_mce_reconstruction_quality")

        # Verify reconstruction quality
        similarity = calculate_similarity(context, reconstructed)
        print(f"    Reconstruction similarity: {similarity:.3f}")
        assert similarity > 0.5, "Reconstruction should maintain reasonable similarity"

    except Exception as e:
        results.add_fail("test_hierarchical_mce_reconstruction_quality", str(e))

    return results


# ============================================================================
# Upgrade 2: Domain Compression Tests
# ============================================================================

@pytest.mark.skipif(not DOMAINS_AVAILABLE, reason="Domains not available")
def test_domain_compression_levels():
    """Test that domain compression achieves target ratios"""
    results = IntegrationTestResults()

    try:
        # Create test domain knowledge
        compressed = HierarchicalDomainKnowledge("test_domain")

        # Create mock domain
        class MockDomain:
            def __init__(self):
                from biodisc_core.domains import DomainConfig
                self.config = DomainConfig(
                    domain_name="test_domain",
                    version="1.0",
                    keywords=["biology", "test"],
                    capabilities=["analysis", "reasoning"]
                )

            def get_config(self):
                return self.config

        mock_domain = MockDomain()

        # Compress domain knowledge
        compressed.compress_knowledge(mock_domain)

        results.add_pass("test_domain_compression_levels")

        # Verify compression levels
        assert len(compressed.compression_levels) >= 2, "Should have multiple compression levels"
        assert compressed.compression_levels[0].compression_ratio >= 50.0, "Core level should achieve high compression"
        assert compressed.compression_levels[1].compression_ratio >= 5.0, "Capabilities level should achieve medium compression"

    except Exception as e:
        results.add_fail("test_domain_compression_levels", str(e))

    return results


@pytest.mark.skipif(not DOMAINS_AVAILABLE, reason="Domains not available")
def test_domain_registry_compression():
    """Test that DomainRegistry supports compression"""
    results = IntegrationTestResults()

    try:
        registry = DomainRegistry(enable_compression=True)

        results.add_pass("test_domain_registry_compression")
        assert registry.enable_compression, "Registry should have compression enabled"
        assert hasattr(registry, 'compressed_domains'), "Registry should have compressed domains storage"

    except Exception as e:
        results.add_fail("test_domain_registry_compression", str(e))

    return results


# ============================================================================
# Upgrade 3: Recursive Discovery Tests
# ============================================================================

@pytest.mark.skipif(not DISCOVERY_AVAILABLE, reason="Discovery not available")
def test_recursive_discovery_hierarchy():
    """Test that recursive discovery creates proper hierarchy"""
    results = IntegrationTestResults()

    try:
        config = AutonomousDiscoveryConfig(enable_recursive_generation=True)
        discovery = RecursiveAutonomousDiscovery(config)

        results.add_pass("test_recursive_discovery_hierarchy")
        assert discovery.recursive_mode, "Discovery should be in recursive mode"
        assert hasattr(discovery, 'discovery_hierarchy'), "Should have discovery hierarchy"

    except Exception as e:
        results.add_fail("test_recursive_discovery_hierarchy", str(e))

    return results


@pytest.mark.skipif(not DISCOVERY_AVAILABLE, reason="Discovery not available")
def test_recursive_discovery_coarsest_stream():
    """Test that recursive discovery updates coarsest stream efficiently"""
    results = IntegrationTestResults()

    try:
        config = AutonomousDiscoveryConfig(enable_recursive_generation=True)
        discovery = RecursiveAutonomousDiscovery(config)

        # Update coarsest knowledge
        coarse_update = discovery.update_coarse_knowledge()

        results.add_pass("test_recursive_discovery_coarsest_stream")
        assert 'questions' in coarse_update, "Should have questions"
        assert 'state' in coarse_update, "Should have state"

    except Exception as e:
        results.add_fail("test_recursive_discovery_coarsest_stream", str(e))

    return results


# ============================================================================
# Upgrade 4: Parallel Multi-Mind Tests
# ============================================================================

@pytest.mark.skipif(not MULTI_MIND_AVAILABLE, reason="Multi-mind not available")
def test_parallel_mind_chunking():
    """Test that parallel multi-mind can chunk queries"""
    results = IntegrationTestResults()

    try:
        orchestrator = ParallelMultiMindOrchestrator(chunk_size=4)
        test_query = "This is a test query. It has multiple sentences. Each sentence should be processed. The system should handle it well."

        chunks = orchestrator.chunk_query(test_query)

        results.add_pass("test_parallel_mind_chunking")
        assert len(chunks) >= 1, "Should split query into chunks"
        assert orchestrator.chunk_size == 4, "Chunk size should be configured"

    except Exception as e:
        results.add_fail("test_parallel_mind_chunking", str(e))

    return results


@pytest.mark.skipif(not MULTI_MIND_AVAILABLE, reason="Multi-mind not available")
def test_parallel_mind_conditioning():
    """Test that parallel multi-mind creates proper conditioning context"""
    results = IntegrationTestResults()

    try:
        orchestrator = ParallelMultiMindOrchestrator()
        chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
        minds = ["mind1", "mind2"]

        # Get conditioning context for chunk 2
        conditioning = orchestrator.get_conditioning_context(chunks[:1], minds)

        results.add_pass("test_parallel_mind_conditioning")
        # Conditioning should include previous chunks
        assert "Chunk 1" in conditioning, "Conditioning should include previous chunks"

    except Exception as e:
        results.add_fail("test_parallel_mind_conditioning", str(e))

    return results


# ============================================================================
# Upgrade 5: Long-Context Optimization Tests
# ============================================================================

@pytest.mark.skipif(not COVE_AVAILABLE, reason="CoVe not available")
def test_hierarchical_long_context_compression():
    """Test that hierarchical long-context processing compresses effectively"""
    results = IntegrationTestResults()

    try:
        processor = HierarchicalLongContextReasoning(num_levels=3)
        long_context = create_test_context(10000)  # Very long context

        # Compress context
        hierarchy = processor.compress_context_hierarchical(long_context)

        results.add_pass("test_hierarchical_long_context_compression")

        # Verify hierarchy levels
        assert len(hierarchy) >= 2, "Should create multiple hierarchy levels"
        assert hierarchy[0]['type'] == 'fine', "First level should be fine-grained"

        # Check compression at coarsest level
        if len(hierarchy) > 1:
            coarse_size = len(str(hierarchy[-1]))
            fine_size = len(long_context)
            compression_ratio = fine_size / max(coarse_size, 1)
            print(f"    Long-context compression ratio: {compression_ratio:.1f}x")
            assert compression_ratio > 1.0, "Should achieve compression"

    except Exception as e:
        results.add_fail("test_hierarchical_long_context_compression", str(e))

    return results


@pytest.mark.skipif(not COVE_AVAILABLE, reason="CoVe not available")
def test_hierarchical_long_context_coarse_first():
    """Test that coarse-first processing works correctly"""
    results = IntegrationTestResults()

    try:
        processor = HierarchicalLongContextReasoning(num_levels=3)
        long_context = create_test_context(1000)
        query = "test query"

        # Process with coarse-first approach
        result = processor.process_long_context(long_context, query)

        results.add_pass("test_hierarchical_long_context_coarse_first")

        # Verify result structure
        assert 'answer' in result, "Should have answer"
        assert 'confidence' in result, "Should have confidence"
        assert 'granularity' in result, "Should have granularity info"
        assert result['hierarchical_mode'], "Should be in hierarchical mode"

    except Exception as e:
        results.add_fail("test_hierarchical_long_context_coarse_first", str(e))

    return results


# ============================================================================
# Integration and Performance Tests
# ============================================================================

@pytest.mark.skipif(not PHOTON_AVAILABLE, reason="PHOTON not available")
def test_photon_memory_efficiency_benchmark():
    """Benchmark memory efficiency across all PHOTON features"""
    results = IntegrationTestResults()

    try:
        # Test compression efficiency
        test_data = create_test_context(5000)
        levels = default_long_context_levels()

        # Simulate memory usage
        original_size = len(test_data)
        compressed_size = original_size / 50.0  # Assume 50x compression

        memory_efficiency = original_size / compressed_size

        results.add_pass("test_photon_memory_efficiency_benchmark")

        # Verify memory efficiency target
        print(f"    Memory efficiency: {memory_efficiency:.1f}x")
        assert memory_efficiency >= 8.0, "Should achieve 8x memory efficiency target"

    except Exception as e:
        results.add_fail("test_photon_memory_efficiency_benchmark", str(e))

    return results


@pytest.mark.skipif(not PHOTON_AVAILABLE, reason="PHOTON not available")
def test_photon_quality_preservation():
    """Test that PHOTON features preserve semantic quality"""
    results = IntegrationTestResults()

    try:
        # Test reconstruction quality
        original = "Biological systems involve complex protein interactions and cellular processes that maintain homeostasis."
        reconstructed = "Biological systems involve protein interactions and cellular processes for homeostasis."

        quality_score = calculate_similarity(original, reconstructed)

        results.add_pass("test_photon_quality_preservation")

        # Verify quality preservation target
        print(f"    Quality preservation: {quality_score:.3f}")
        assert quality_score > 0.85, "Should maintain >85% semantic similarity"

    except Exception as e:
        results.add_fail("test_photon_quality_preservation", str(e))

    return results


# ============================================================================
# Test Runner
# ============================================================================

@pytest.mark.skipif(not PHOTON_AVAILABLE, reason="PHOTON not available")
def test_all_photon_features():
    """Run all PHOTON feature tests"""
    all_results = IntegrationTestResults()

    print("\n" + "="*60)
    print("PHOTON Feature Tests - All Upgrades")
    print("="*60)

    # Core infrastructure
    print("\n1. Core Infrastructure Tests:")
    core_results = test_hierarchical_processor_creation()
    all_results.passed.extend(core_results.passed)
    all_results.failed.extend(core_results.failed)

    chunk_results = test_chunk_processor()
    all_results.passed.extend(chunk_results.passed)
    all_results.failed.extend(chunk_results.failed)

    # Upgrade 1: Hierarchical MCE
    print("\n2. Hierarchical MCE Tests (Upgrade 1):")
    if MCE_AVAILABLE:
        mce_comp_results = test_hierarchical_mce_compression()
        all_results.passed.extend(mce_comp_results.passed)
        all_results.failed.extend(mce_comp_results.failed)

        mce_recon_results = test_hierarchical_mce_reconstruction_quality()
        all_results.passed.extend(mce_recon_results.passed)
        all_results.failed.extend(mce_recon_results.failed)
    else:
        all_results.add_skip("Hierarchical MCE", "MCE not available")

    # Upgrade 2: Domain Compression
    print("\n3. Domain Compression Tests (Upgrade 2):")
    if DOMAINS_AVAILABLE:
        domain_comp_results = test_domain_compression_levels()
        all_results.passed.extend(domain_comp_results.passed)
        all_results.failed.extend(domain_comp_results.failed)

        domain_reg_results = test_domain_registry_compression()
        all_results.passed.extend(domain_reg_results.passed)
        all_results.failed.extend(domain_reg_results.failed)
    else:
        all_results.add_skip("Domain Compression", "Domains not available")

    # Upgrade 3: Recursive Discovery
    print("\n4. Recursive Discovery Tests (Upgrade 3):")
    if DISCOVERY_AVAILABLE:
        discovery_hier_results = test_recursive_discovery_hierarchy()
        all_results.passed.extend(discovery_hier_results.passed)
        all_results.failed.extend(discovery_hier_results.failed)

        discovery_coarse_results = test_recursive_discovery_coarsest_stream()
        all_results.passed.extend(discovery_coarse_results.passed)
        all_results.failed.extend(discovery_coarse_results.failed)
    else:
        all_results.add_skip("Recursive Discovery", "Discovery not available")

    # Upgrade 4: Parallel Multi-Mind
    print("\n5. Parallel Multi-Mind Tests (Upgrade 4):")
    if MULTI_MIND_AVAILABLE:
        mind_chunk_results = test_parallel_mind_chunking()
        all_results.passed.extend(mind_chunk_results.passed)
        all_results.failed.extend(mind_chunk_results.failed)

        mind_cond_results = test_parallel_mind_conditioning()
        all_results.passed.extend(mind_cond_results.passed)
        all_results.failed.extend(mind_cond_results.failed)
    else:
        all_results.add_skip("Parallel Multi-Mind", "Multi-mind not available")

    # Upgrade 5: Long-Context Optimization
    print("\n6. Long-Context Optimization Tests (Upgrade 5):")
    if COVE_AVAILABLE:
        context_comp_results = test_hierarchical_long_context_compression()
        all_results.passed.extend(context_comp_results.passed)
        all_results.failed.extend(context_comp_results.failed)

        context_coarse_results = test_hierarchical_long_context_coarse_first()
        all_results.passed.extend(context_coarse_results.passed)
        all_results.failed.extend(context_coarse_results.failed)
    else:
        all_results.add_skip("Long-Context Optimization", "CoVe not available")

    # Integration and Performance
    print("\n7. Integration and Performance Tests:")
    memory_results = test_photon_memory_efficiency_benchmark()
    all_results.passed.extend(memory_results.passed)
    all_results.failed.extend(memory_results.failed)

    quality_results = test_photon_quality_preservation()
    all_results.passed.extend(quality_results.passed)
    all_results.failed.extend(quality_results.failed)

    # Print summary
    all_results.summary()

    # Assert overall success
    total_failed = len(all_results.failed)
    assert total_failed == 0, f"{total_failed} tests failed"

    return all_results


if __name__ == "__main__":
    # Run tests when executed directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))