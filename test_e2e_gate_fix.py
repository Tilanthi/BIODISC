"""
End-to-end integration verification: prove the gate fixes unblock a REAL
discovery all the way through download -> DE -> 5-layer validation -> save.

Uses a small, known-good GEO dataset (GSE2034) so it does not depend on the
async loop's dataset-pick luck. Writes to a TEST file so production records
stay clean; the live loop populates the production file independently.
"""
import sys, json, time, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")

from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import (
    create_fixed_discovery_orchestrator,
)

# GSE2034 = breast cancer study (small-ish). Question is relevant to it and is
# one of the curated specific questions (so Layer 5 novelty now passes too).
QUESTION = ("Does MMP2 expression correlate with invasiveness in "
            "triple-negative vs HER2+ breast cancer?")
DATASET = "GSE2034"
TEST_OUT = Path("test_e2e_save_output.jsonl")

print(f"Question : {QUESTION}")
print(f"Dataset  : {DATASET}")
print("Running full pipeline (download + DE + 5-layer gates)... this takes 1-3 min")
print("-" * 70)

t0 = time.time()
orch = create_fixed_discovery_orchestrator()
report = orch.generate_genuine_discovery(QUESTION, DATASET)
elapsed = time.time() - t0

print("-" * 70)
print(f"Elapsed  : {elapsed:.0f}s")
if report is None:
    print("RESULT   : REJECTED (returned None) — a gate still blocks. See WARNING/ERROR above.")
    sys.exit(2)

# Passed ALL 5 layers. Save to test file and report the goods.
de = report.get("differential_expression", {})
ds = report.get("dataset", {})
with open(TEST_OUT, "a") as f:
    f.write(json.dumps(report) + "\n")
print("RESULT   : ACCEPTED — passed ALL 5 validation gates")
print(f"  significant genes : {de.get('significant_genes')}")
print(f"  dataset samples   : {ds.get('sample_count')}")
print(f"  top upregulated   : {[g.get('gene_symbol') for g in de.get('top_upregulated', [])[:5]]}")
print(f"  saved to          : {TEST_OUT}")
sys.exit(0)
