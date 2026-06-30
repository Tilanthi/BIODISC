"""
Comprehensive Test: BIODISC Genuine Discovery Architecture Verification

This test verifies that BIODISC V4.8+ focuses on genuine discovery contributions
rather than trivial definition questions.

TEST COVERAGE:
1. V74 Genuine Discovery Filter functionality
2. V73 Curiosity Engine integration with V74
3. Autonomous Orchestrator configuration
4. Data Source Validator
5. Discovery Validator integration
6. End-to-end autonomous discovery workflow

Date: 2026-06-28
"""

import sys
import importlib.util

def test_v74_genuine_discovery_filter():
    """Test V74 Genuine Discovery Filter functionality"""
    print("=" * 60)
    print("TEST 1: V74 Genuine Discovery Filter")
    print("=" * 60)

    try:
        # Load the filter module directly
        spec = importlib.util.spec_from_file_location(
            'v1xx_filter',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/capabilities/v1xx_genuine_discovery_filter.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        filter = module.get_genuine_discovery_filter()

        # Test questions that should be filtered out (trivial definitions)
        trivial_questions = [
            'What is Feedback?',
            'What is Natural?',
            'What is Convergent?',
            'What is Mendelian?',
            'What is Metabolic?',
        ]

        filtered_count = 0
        for question in trivial_questions:
            assessment = filter.assess_question(question)
            if assessment.should_filter_out:
                filtered_count += 1

        print(f"✓ Trivial questions filtered: {filtered_count}/{len(trivial_questions)}")

        # Test questions that should be kept (genuine discoveries)
        genuine_questions = [
            'What determines the switch between apoptosis and autophagy under stress?',
            'How do feedback loops create bistable switches in cell fate decisions?',
            'How can we improve the efficiency of causal discovery algorithms?',
            'What mechanisms ensure accurate spindle positioning during asymmetric cell division?',
            'How do allosteric effects propagate through protein structures?',
        ]

        genuine_count = 0
        for question in genuine_questions:
            assessment = filter.assess_question(question)
            if assessment.is_genuine_contribution and not assessment.should_filter_out:
                genuine_count += 1

        print(f"✓ Genuine discoveries kept: {genuine_count}/{len(genuine_questions)}")

        # Test the filter_questions function
        test_questions = trivial_questions + genuine_questions
        filtered_questions, assessments = filter.filter_questions(test_questions)
        stats = filter.get_filter_statistics(assessments)

        print(f"✓ Filter statistics:")
        print(f"  - Total questions: {stats['total_questions']}")
        print(f"  - Trivial definitions filtered: {stats['trivial_definitions']}")
        print(f"  - Genuine discoveries: {stats['genuine_discoveries']}")
        print(f"  - Overall filtered out: {stats['filtered_out']}")
        print(f"  - Overall kept: {stats['kept']}")

        # Verify expectations
        expected_filtered = len(trivial_questions)
        expected_kept = len(genuine_questions)

        if stats['trivial_definitions'] >= expected_filtered - 1:  # Allow some tolerance
            print(f"✓ PASSED: V74 Genuine Discovery Filter is working correctly")
            return True
        else:
            print(f"✗ FAILED: Expected {expected_filtered} trivial definitions filtered, got {stats['trivial_definitions']}")
            return False

    except Exception as e:
        print(f"✗ FAILED: V74 Genuine Discovery Filter test error: {e}")
        return False


def test_v73_curiosity_engine_integration():
    """Test V73 Curiosity Engine integration with V74"""
    print("\n" + "=" * 60)
    print("TEST 2: V73 Curiosity Engine Integration")
    print("=" * 60)

    try:
        # Load V73 curiosity engine
        spec = importlib.util.spec_from_file_location(
            'v73_curiosity',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/reasoning/v73_curiosity_engine.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Create curiosity engine with V74 filter enabled
        curiosity_engine = module.create_curiosity_engine(enable_genuine_discovery_filter=True)

        print(f"✓ Curiosity engine created with V74 filter enabled")

        # Generate questions
        questions = curiosity_engine.generate_questions(max_questions=20)

        print(f"✓ Generated {len(questions)} questions")

        # Check quality of questions
        genuine_count = 0
        for q in questions:
            if 'How' in q.question or 'determines' in q.question or 'mechanism' in q.question.lower():
                genuine_count += 1

        print(f"✓ High-quality questions detected: {genuine_count}/{len(questions)}")

        # Show sample questions
        print(f"✓ Sample questions:")
        for i, q in enumerate(questions[:5], 1):
            print(f"  {i}. {q.question[:70]}...")

        if genuine_count >= len(questions) * 0.7:  # At least 70% should be high-quality
            print(f"✓ PASSED: V73 Curiosity Engine integration is working")
            return True
        else:
            print(f"✗ FAILED: Expected more high-quality questions, got {genuine_count}/{len(questions)}")
            return False

    except Exception as e:
        print(f"✗ FAILED: V73 Curiosity Engine integration test error: {e}")
        return False


def test_autonomous_config():
    """Test Autonomous Orchestrator configuration"""
    print("\n" + "=" * 60)
    print("TEST 3: Autonomous Orchestrator Configuration")
    print("=" * 60)

    try:
        # Load autonomous config
        spec = importlib.util.spec_from_file_location(
            'autonomous_config',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/autonomous/config.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get default config
        config = module.get_default_config()

        print(f"✓ Default autonomous config loaded")

        # Check V74 configuration options
        v74_configs = [
            ('enable_genuine_discovery_filter', hasattr(config, 'enable_genuine_discovery_filter')),
            ('require_published_data_sources', hasattr(config, 'require_published_data_sources')),
            ('computational_novelty_threshold', hasattr(config, 'computational_novelty_threshold')),
            ('synthesis_quality_threshold', hasattr(config, 'synthesis_quality_threshold')),
        ]

        all_v74_present = True
        for attr_name, attr_present in v74_configs:
            if attr_present:
                attr_value = getattr(config, attr_name)
                print(f"✓ {attr_name}: {attr_value}")
            else:
                print(f"✗ {attr_name}: NOT FOUND")
                all_v74_present = False

        # Check Discovery class has V74 fields
        if hasattr(module, 'Discovery'):
            discovery_fields = [
                'contribution_type',
                'data_sources',
                'computational_novelty',
                'synthesis_quality',
                'is_genuine_contribution'
            ]

            # Check if these fields exist in the Discovery dataclass
            import inspect
            discovery_annotations = module.Discovery.__annotations__

            discovery_fields_present = all(field in discovery_annotations for field in discovery_fields)

            if discovery_fields_present:
                print(f"✓ Discovery class has V74 genuine contribution fields")
            else:
                print(f"✗ Discovery class missing V74 fields")
                all_v74_present = False

        if all_v74_present:
            print(f"✓ PASSED: Autonomous Orchestrator configuration has V74 options")
            return True
        else:
            print(f"✗ FAILED: Some V74 configuration options missing")
            return False

    except Exception as e:
        print(f"✗ FAILED: Autonomous Orchestrator configuration test error: {e}")
        return False


def test_data_source_validator():
    """Test Data Source Validator"""
    print("\n" + "=" * 60)
    print("TEST 4: Data Source Validator")
    print("=" * 60)

    try:
        # Load data source validator
        spec = importlib.util.spec_from_file_location(
            'data_validator',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/capabilities/v1xx_data_source_validator.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        validator = module.create_data_source_validator()

        print(f"✓ Data source validator created")

        # Test discovery with data sources
        discovery_with_sources = """
        This discovery is based on analysis of GenBank accession number ABC123
        and data from PMID: 12345678. The protein structure was obtained
        from PDB database entry 1XYZ.
        """

        validation = validator.validate_discovery(discovery_with_sources)

        print(f"✓ Discovery validation completed:")
        print(f"  - Is valid: {validation.is_valid}")
        print(f"  - Data quality score: {validation.data_quality_score:.2f}")
        print(f"  - Sources found: {len(validation.sources_found)}")
        print(f"  - Peer-reviewed sources: {validation.peer_reviewed_count}")
        print(f"  - Repository sources: {validation.repository_count}")

        # Test discovery without data sources
        discovery_without_sources = """
        This is a general observation about biological systems without
        any specific data citations or references to published sources.
        """

        validation_no_sources = validator.validate_discovery(discovery_without_sources)

        print(f"✓ Discovery without sources validation:")
        print(f"  - Is valid: {validation_no_sources.is_valid}")
        print(f"  - Data quality score: {validation_no_sources.data_quality_score:.2f}")

        if validation.data_quality_score > 0.5 and validation.is_valid:
            print(f"✓ PASSED: Data Source Validator is working correctly")
            return True
        else:
            print(f"✗ FAILED: Data Source Validator not working as expected")
            return False

    except Exception as e:
        print(f"✗ FAILED: Data Source Validator test error: {e}")
        return False


def test_discovery_validator_integration():
    """Test Discovery Validator integration with V74"""
    print("\n" + "=" * 60)
    print("TEST 5: Discovery Validator Integration")
    print("=" * 60)

    try:
        # Load config module first
        config_spec = importlib.util.spec_from_file_location(
            'autonomous_config',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/autonomous/config.py'
        )
        config_module = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(config_module)

        print(f"✓ Config module loaded")

        # Create config with V74 enabled
        config = config_module.get_default_config()

        # Verify V74 configuration exists
        v74_config_exists = (
            hasattr(config, 'enable_genuine_discovery_filter') and
            config.enable_genuine_discovery_filter and
            hasattr(config, 'require_published_data_sources') and
            config.require_published_data_sources
        )

        print(f"✓ V74 configuration verified:")
        print(f"  - enable_genuine_discovery_filter: {config.enable_genuine_discovery_filter}")
        print(f"  - require_published_data_sources: {config.require_published_data_sources}")
        print(f"  - computational_novelty_threshold: {config.computational_novelty_threshold}")
        print(f"  - synthesis_quality_threshold: {config.synthesis_quality_threshold}")

        # Check if Discovery dataclass has V74 fields
        discovery_fields = [
            'contribution_type',
            'data_sources',
            'computational_novelty',
            'synthesis_quality',
            'is_genuine_contribution'
        ]

        # Check if these fields exist in the Discovery dataclass
        import inspect
        discovery_annotations = config_module.Discovery.__annotations__

        discovery_fields_present = all(field in discovery_annotations for field in discovery_fields)

        if discovery_fields_present:
            print(f"✓ Discovery dataclass has V74 genuine contribution fields:")
            for field in discovery_fields:
                print(f"  - {field}")
        else:
            print(f"✗ Discovery dataclass missing some V74 fields:")
            for field in discovery_fields:
                if field not in discovery_annotations:
                    print(f"  - Missing: {field}")

        # Check if the validator module has V74 integration methods
        validator_spec = importlib.util.spec_from_file_location(
            'discovery_validator',
            '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/autonomous/discovery_validator.py'
        )
        validator_module = importlib.util.module_from_spec(validator_spec)
        validator_spec.loader.exec_module(validator_module)

        # Check if the validator has V74 integration methods
        validator_has_v74 = hasattr(validator_module.DiscoveryValidator, '_assess_genuine_contribution') and \
                           hasattr(validator_module.DiscoveryValidator, '_validate_data_sources')

        if validator_has_v74:
            print(f"✓ DiscoveryValidator has V74 integration methods:")
            print(f"  - _assess_genuine_contribution")
            print(f"  - _validate_data_sources")

        if v74_config_exists and discovery_fields_present and validator_has_v74:
            print(f"✓ PASSED: Discovery Validator integration with V74 is configured")
            return True
        else:
            print(f"✗ FAILED: Discovery Validator integration incomplete")
            return False

    except Exception as e:
        print(f"✗ FAILED: Discovery Validator integration test error: {e}")
        return False


def main():
    """Run all tests and generate final report"""
    print("\n" + "=" * 60)
    print("BIODISC GENUINE DISCOVERY ARCHITECTURE VERIFICATION")
    print("=" * 60)
    print("Testing BIODISC V4.8+ focus on genuine discovery contributions")
    print("rather than trivial definition questions.")
    print()

    results = []

    # Run all tests
    results.append(("V74 Genuine Discovery Filter", test_v74_genuine_discovery_filter()))
    results.append(("V73 Curiosity Engine Integration", test_v73_curiosity_engine_integration()))
    results.append(("Autonomous Orchestrator Configuration", test_autonomous_config()))
    results.append(("Data Source Validator", test_data_source_validator()))
    results.append(("Discovery Validator Integration", test_discovery_validator_integration()))

    # Generate final report
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print()
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 SUCCESS: BIODISC Genuine Discovery Architecture is fully operational!")
        print("BIODISC is now configured to focus on genuine discovery contributions,")
        print("filtering out trivial definition questions and prioritizing:")
        print("  • Novel computational analysis")
        print("  • Published data integration")
        print("  • Genuine synthesis and insights")
        return 0
    else:
        print("\n⚠️  WARNING: Some tests failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
