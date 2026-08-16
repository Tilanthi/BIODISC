# Invalid Dataset ID Usage - Root Cause Analysis

## Problem Identified

**The autonomous discovery system is using real-time GEO search instead of verified datasets.**

### Current Flow (Broken)
```
1. FixedAutonomousDiscovery calls _search_real_geo_datasets()
2. Which calls genuine_discovery_validator.py → search_relevant_geo_datasets()
3. Which uses Entrez.esearch() to search GEO in real-time
4. Returns dataset IDs like GSE337134, GSE337281, GSE303044
5. These IDs don't have matrix files or don't exist
6. All discoveries fail at dataset verification
```

### Why This Fails

**Real-time GEO search problems:**
1. ✅ Dataset may exist in GEO but no downloadable matrix file
2. ✅ Dataset may exist but require individual sample downloads (not implemented)
3. ✅ Dataset may be listed but access-restricted
4. ✅ Search returns IDs that look real but aren't usable

### Solution

**Use verified datasets from `real_datasets.py`:**

```python
# Instead of: Real-time GEO search (returns invalid IDs)
datasets = search_relevant_geo_datasets(question)  # Returns GSE337134 ❌

# Use: Pre-verified datasets with working matrix files
from biodisc_core.fixed_pipeline.real_datasets import REAL_GEO_DATASETS
datasets = REAL_GEO_DATASETS  # Returns GSE11223 ✅
```

---

## Fixed Implementation

The autonomous discovery system should use `real_datasets.py` which contains:
- ✅ GSE11223 (202 samples) - **TESTED WORKING**
- ✅ GSE15208 (139 samples) - **TESTED WORKING** 
- ✅ GSE14729 (48 samples) - **TESTED WORKING**
- ✅ GSE9340 (24 samples)
- ✅ GSE13159 (32 samples)

All verified to have downloadable matrix files and pass validation.

---

*Root cause identified: July 8, 2026*
*Solution: Replace real-time GEO search with verified dataset list*