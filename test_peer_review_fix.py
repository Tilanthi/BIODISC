"""Verify the peer_review geo_id / geo_dataset_id fix."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from biodisc_core.fixed_pipeline.peer_review_validator import PeerReviewValidator

v = PeerReviewValidator()

report = {
    "question": ("Does STAT3 activation differ with a specific inhibitor vs untreated "
                 "control in glioblastoma?"),
    "differential_expression": {
        "significant_genes": 50,
        "total_genes_tested": 1000,
        "top_upregulated": [{"gene_symbol": "STAT3"}, {"gene_symbol": "MYC"}],
        "method": "ttest",
    },
    "dataset": {"geo_id": "GSE2034", "organism": "Homo sapiens", "sample_count": 286},
}

# 1. Reproducibility must now see the accession (geo_id) -> 8.0, not 2.0.
rep_score, rep_issues = v._assess_reproducibility(report)
assert rep_score >= 8.0, (
    f"FIX FAILED: reproducibility {rep_score}/10 with geo_id present (issues: {rep_issues})"
)

# 2. data_quality must NOT flag a missing accession when geo_id is present.
dq_score, dq_issues = v._assess_data_quality(report)
assert not any("accession" in i.lower() for i in dq_issues), (
    f"FIX FAILED: data_quality still flags accession: {dq_issues}"
)

# 3. Full review should not be tanked by the old mismatch.
result = v.validate_discovery_for_peer_review(report)
print(f"overall={result.overall_score}/40 decision={result.decision.value} "
      f"novelty={result.novelty_score} merit={result.scientific_merit} "
      f"data_quality={result.data_quality} reproducibility={result.reproducibility}")

# 4. Guard: a report with no accession is still penalized.
no_acc = {"dataset": {"geo_id": "", "organism": "Homo sapiens", "sample_count": 10}}
rep2, _ = v._assess_reproducibility(no_acc)
assert rep2 <= 6.0, f"guard failed: missing accession should score low, got {rep2}"

print("ALL PEER-REVIEW FIX CHECKS PASS")
