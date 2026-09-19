# Verifier Independence Audit (V9.1)

**Date:** 2026-09-19
**Trigger:** Paper2Agent (Nature s41586-026-11044-y) verification discipline —
"worker completion alone does not establish success": every verifier must derive
its verdict from primary evidence, structurally distinct from the producer, and
must never assert what it did not check.
**Scope:** the 6-layer validation stack, Layer 7/7b, the replication gate, and
the write-chokepoint verification block.

## Verdict per layer

| Layer | What it checks | Re-derives from primary data? | Consumes producer output? | Verdict |
|---|---|---|---|---|
| L1 duplicate detection | statistical-profile duplication | yes — recomputes the profile hash from the DE result | profile only | ✅ independent |
| L2 dataset-question validation | organism/tissue/disease coherence | yes — canonical-ID comparison of dataset vs question | metadata only | ✅ independent |
| L3 probe-gene mapping | probe IDs posing as genes | yes — inspects the gene symbols themselves | symbols only | ✅ independent |
| L4 FDR significance | signal exists (FDR < 0.05) | yes — its own thresholds over the DE stats | DE stats (input, not verdict) | ✅ independent |
| L5 template detection | boilerplate questions | yes — its own novelty scoring over the question | question text | ✅ independent |
| L6 Gate-2 literature novelty | claim entailed by PubMed | yes — its own retrieval + TF-cosine over abstracts | **claim text only** (by design — its job is to check the claim) | ✅ independent |
| L7 question-result binding | named gene present in result | yes — its own gene extraction over the question and result | question + result | ✅ independent |
| L7b contrarian support | named gene moved in claimed direction | yes — the gene-specific hypothesis test re-runs on the expression matrix | the claim's direction | ✅ independent |
| Replication gate | headline statistic on held-out data | **yes — re-runs DE on BOTH splits itself** via the analyzer; independent-cohort mode recomputes the cohort DE | discovery top genes (the things being tested) | ✅ independent |
| Write chokepoint (`append_verified`) | verification block present + complete | structural check only | the block | ✅ structural |
| **Verification block (`build_verification_block`)** | records gate outcomes | — | **❌ DEFECT (fixed): hardcoded `fdr_significance: True` unconditionally** | 🔧 fixed in V9.1 |

## The defect found and fixed

`build_verification_block` (`biodisc_core/fixed_pipeline/discovery_store.py`)
wrote `"fdr_significance": True` into every stored record's machine-verification
block regardless of what Layer 4 actually decided. The block is BIODISC's
objective-evidence layer — an unconditional assertion in it is exactly the
"worker completion establishes success" failure Paper2Agent's protocol forbids.

**Fix (two halves, both required for evidence to flow):**
1. The orchestrator now records Layer 4's actual verdict in
   `comprehensive_validation_statistics.fdr_significance_gate.passes_significance_gate`
   (previously only counters were stored, so the verdict was unrecoverable from
   the report).
2. `build_verification_block` **derives** the field from that recorded verdict
   (`_fdr_passed`), falling back to `None` (unknown) when no evidence is present
   — never asserting True without evidence.

Tests: `tests/test_discovery_chokepoint.py` (verifier-independence section).

## Side effects (intentional strictness)

- `_validation_passed` (discovery_gate.py) now sees the recorded FDR verdict, so
  a report that failed Layer 4 but somehow reached flagging is correctly
  rejected instead of waved through.
- Stored records from before V9.1 carry `fdr_significance: true` in their
  verification blocks; those blocks were built by the asserting code, so the
  field should be read as "asserted, not evidenced" for legacy rows. New writes
  are evidence-derived.

## Ongoing rule

Any new gate or evidence block must state where its verdict comes from. An
assertion without a recorded observation is a bug. When in doubt, re-derive.
