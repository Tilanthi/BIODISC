# Validation System Architecture

## Overview

The BIODISC V7.3 validation system is a **5-layer hard gate architecture** that prevents pseudo-science generation and ensures only genuine scientific discoveries are published.

## Design Principles

1. **HARD GATES**: All validation layers are non-negotiable - no fallbacks, no overrides
2. **FAIL-FAST**: Reject invalid discoveries as early as possible to save resources
3. **TRACEABILITY**: Every validation decision is logged with detailed reasoning
4. **SCIENTIFIC INTEGRITY**: Prioritize correctness over quantity of discoveries

## Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   FixedDiscoveryOrchestrator                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Comprehensive 5-Layer Validation               │ │
│  │                                                        │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │ │
│  │  │  Duplicate  │  │ Dataset-   │  │  Probe-    │      │ │
│  │  │  Detection  │→ │  Question  │→ │  Gene      │      │ │
│  │  │             │  │  Validation│  │  Mapping   │      │ │
│  │  └────────────┘  └────────────┘  └────────────┘      │ │
│  │                                                ↓         │ │
│  │  ┌────────────┐  ┌────────────┐                  │ │
│  │  │  FDR       │  │  Template  │                  │ │
│  │  │  Significance│ │ Detection  │                  │ │
│  │  └────────────┘  └────────────┘                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  - Orchestrates all validation layers                         │
│  - Aggregates validation statistics                           │
│  - Makes final publish/reject decision                        │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

```
DISCOVERY_REPORT
    │
    ├─→ DuplicateDetector.check_duplicate()
    │   ├─→ DiscoveryFingerprint.from_discovery()
    │   ├─→ DiscoveryCache.is_duplicate()
    │   └─→ Returns: (is_duplicate, reason)
    │
    ├─→ BiologicalRelevanceValidator.validate_relevance()
    │   ├─→ OntologyMapper.extract_entities()
    │   ├─→ OntologyMapper.check_relevance()
    │   └─→ Returns: RelevanceValidationResult
    │
    ├─→ ProbeGeneMapper.validate_and_resolve()
    │   ├─→ PlatformParser.detect_probe_ids()
    │   ├─→ GeneResolver.resolve_probes_to_genes()
    │   └─→ Returns: GeneResolutionResult
    │
    ├─→ SignificanceValidator.validate_significance()
    │   ├─→ Check FDR thresholds
    │   ├─→ Check significant gene counts
    │   └─→ Returns: SignificanceValidationResult
    │
    └─→ TemplateDetector.validate_question()
        ├─→ QuestionClassifier.classify_question()
        ├─→ NoveltyEstimator.estimate_novelty()
        └─→ Returns: (is_valid, classification, novelty)
```

## Component Details

### 1. Duplicate Detection

**Purpose:** Prevent identical statistical profiles from being published multiple times

**Implementation:**
- Statistical fingerprinting using MD5 hashes
- LRU cache with 10,000 discovery capacity
- Three-level duplicate detection:
  1. Exact combined hash match
  2. Same question + dataset pair
  3. Identical statistical profile

**Key Methods:**
- `DiscoveryFingerprint.from_discovery()` - Create fingerprint
- `DiscoveryCache.is_duplicate()` - Check for duplicates
- `DuplicateDetector.check_duplicate()` - Main validation interface

**Data Structures:**
```python
@dataclass
class DiscoveryFingerprint:
    question_hash: str      # 8-character MD5 of question
    dataset_hash: str       # 8-character MD5 of dataset ID
    statistical_hash: str   # 8-character MD5 of key stats
    gene_set_hash: str      # 8-character MD5 of top 10 genes
    combined_hash: str      # 32-character MD5 master hash
```

### 2. Dataset-Question Validation

**Purpose:** Ensure dataset is biologically relevant to research question

**Implementation:**
- Ontology-based entity extraction (Uberon, DOID, NCBITaxon)
- Multi-level matching:
  1. Organism matching (critical)
  2. Tissue matching (important)
  3. Disease matching (important)
- Scoring system (0-10) with minimum threshold of 6.0

**Key Methods:**
- `OntologyMapper.extract_entities()` - Extract biological entities
- `BiologicalRelevanceValidator.validate_relevance()` - Main validation

**Ontology Mappings:**
- Tissues: breast, colon, lung, liver, brain, etc. → Uberon IDs
- Diseases: cancer types, diabetes, IBD, etc. → DOID IDs
- Organisms: human, mouse, rat, zebrafish, etc. → NCBITaxon IDs

### 3. Probe-Gene Mapping

**Purpose:** Require real gene symbols, reject numeric probe IDs

**Implementation:**
- Probe ID detection using regex patterns
- Platform-specific annotation parsing
- Resolution mapping or rejection

**Probe ID Patterns:**
- Pure numeric: `455`, `1195`, `382` (peer review case)
- Affymetrix: `1007_s_at`, `1053_at`
- Illumina: `ILMN_12345`

**Key Methods:**
- `PlatformParser.is_probe_id()` - Detect probe IDs
- `GeneResolver.resolve_probes_to_genes()` - Resolve to genes
- `ProbeGeneMapper.validate_and_resolve()` - Main validation

**Critical Decision:** Reject if ANY probe IDs detected (100% gene symbol requirement)

### 4. FDR Significance Gate

**Purpose:** Ensure minimum statistical significance before publication

**Implementation:**
- Three-level significance checking:
  1. Any significant genes? (FDR < 0.05)
  2. Minimum 3 significant genes?
  3. Best FDR < 0.01?

**Thresholds:**
- `MIN_FDR_THRESHOLD = 0.05` - FDR threshold
- `MIN_SIGNIFICANT_GENES = 3` - Minimum gene count
- `MIN_BEST_FDR = 0.01` - Best gene threshold

**Key Methods:**
- `SignificanceValidator.validate_significance()` - Main validation
- Returns score (0-10) and detailed feedback

**Critical Decision:** Null results (0 significant genes) are ALWAYS rejected

### 5. Template Pattern Detection

**Purpose:** Distinguish specific mechanistic questions from generic templates

**Implementation:**
- Question classification using regex patterns
- Novelty estimation based on literature saturation
- Multi-factor scoring:
  - Template pattern detection
  - Specific indicator detection
  - Word count analysis
  - Gene symbol detection

**Question Types:**
- `SPECIFIC_MECHANISTIC` - Novel, specific (8.5-9.0/10 novelty)
- `SPECIFIC_QUESTIONS` - Specific but broad (7.0/10 novelty)
- `GENERIC_TEMPLATE` - Template question (3.0/10 novelty)
- `SATURATED_FIELD` - Well-established (1.0/10 novelty)

**Saturated Fields:**
- BRCA1-PARP: ~5000 papers
- TP53-cancer: ~10000 papers
- Cell cycle yeast: ~3000 papers

**Key Methods:**
- `QuestionClassifier.classify_question()` - Classify question
- `NoveltyEstimator.estimate_novelty()` - Estimate novelty
- `TemplateDetector.validate_question()` - Main validation

## Validation Flow

### Decision Tree

```
START
  │
  ├─→ Is duplicate?
  │   └─→ YES → REJECT (Layer 1)
  │   └─→ NO → Continue
  │
  ├─→ Biologically relevant?
  │   └─→ NO → REJECT (Layer 2)
  │   └─→ YES → Continue
  │
  ├─→ Real gene symbols?
  │   └─→ NO → REJECT (Layer 3)
  │   └─→ YES → Continue
  │
  ├─→ Statistically significant?
  │   └─→ NO → REJECT (Layer 4)
  │   └─→ YES → Continue
  │
  ├─→ Novel specific question?
  │   └─→ NO → REJECT (Layer 5)
  │   └─→ YES → Continue
  │
  └─→ PUBLISH ✅
```

### Statistics Tracking

Each validation layer tracks:
- Validations performed
- Rejections made
- Rejection rate
- Additional metrics (cache size, mapping success, etc.)

Overall orchestrator tracks:
- Total discoveries attempted
- Total discoveries rejected
- Total discoveries validated
- Overall rejection rate

## Performance Considerations

### Time Complexity
- Duplicate detection: O(1) - hash lookup
- Dataset-question: O(n) - where n = entity count
- Probe-gene mapping: O(m) - where m = identifier count
- FDR significance: O(1) - simple threshold checks
- Template detection: O(k) - where k = pattern count

**Total validation time:** < 1 second per discovery

### Memory Usage
- Duplicate cache: 10,000 discoveries × ~100 bytes = ~1 MB
- Ontology mappings: ~50 KB static
- Platform annotations: ~500 KB (cached)

**Total memory:** < 10 MB for validation system

### Scalability
- Cache size: Configurable (default 10,000)
- Validation layers: Modular - easy to add/remove
- Parallelization: Layers are independent - could run in parallel

## Error Handling

### Validation Failures
All validation layers return structured results:
```python
@dataclass
class ValidationResult:
    passes: bool
    score: float
    reason: str
    details: Dict
```

### Logging Strategy
- DEBUG: Detailed validation steps
- INFO: Validation decisions and statistics
- WARNING: Borderline cases and rejections
- ERROR: Critical failures and pseudo-science prevention

### Recovery
No recovery needed - rejected discoveries are simply not published. System continues with next discovery attempt.

## Testing Strategy

### Unit Tests
Each validation layer has comprehensive unit tests:
- Test specific validation logic
- Test edge cases (null inputs, empty lists)
- Test rejection conditions

### Integration Tests
Comprehensive integration tests verify:
- All 5 layers work together correctly
- Rejection cascades work (stop at first failure)
- Valid discoveries pass all gates

### Peer Review Validation Tests
Critical tests for peer review issues:
- Duplicate detection prevents 214 identical discoveries
- Dataset-question validation prevents colon-for-breast mismatch
- Probe-gene mapping prevents probe IDs as genes
- FDR significance prevents null result publication
- Template detection prevents BRCA1-PARP template questions

## Future Enhancements

### Potential Improvements
1. **Machine Learning Classifier**: Train classifier on validated discoveries
2. **Literature Integration**: Real-time PubMed queries for novelty estimation
3. **Network Analysis**: Add pathway-level validation
4. **Cross-Validation**: Validate against external databases
5. **Confidence Calibration**: Dynamically adjust thresholds based on performance

### Extension Points
- Add new validation layers without modifying existing code
- Customize thresholds per domain (epigenomics vs. proteomics)
- Add domain-specific validation rules
- Integrate with external validation services

---

**Architecture Version:** V7.3
**Last Updated:** July 10, 2026
**Status:** ✅ OPERATIONAL
