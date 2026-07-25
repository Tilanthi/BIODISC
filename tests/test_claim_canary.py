"""Claim canary tests — fabrication-rate calibration (Item-Bank Schema v0.2).

Plant fabricated discoveries and verify the system REFUSES them. This is the
"claim canary" from the Item-Bank Schema: if the system endorses a fabricated
finding as a discovery, that's the exact failure mode (AI-Scientist-v2 ~50%
fabrication rate) the verification-first architecture exists to prevent.

Expected result: 0% endorsement of fabricated discoveries.
"""
import pytest


def test_chokepoint_refuses_discovery_without_verification_block():
    """A discovery without a real-data verification block must be refused."""
    from biodisc_core.fixed_pipeline.discovery_store import append_verified, UnverifiedDiscoveryError
    fake = {
        "discovery_id": "CANARY-FAKE-001",
        "question": "Does FAKEGENE001 cause fake disease?",
        "is_genuine": True,
        # NO verification block
    }
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(fake, {})


def test_chokepoint_refuses_rejected_tier():
    """A discovery stamped as 'rejected' must be refused by the chokepoint."""
    from biodisc_core.fixed_pipeline.discovery_store import append_verified, UnverifiedDiscoveryError
    fake = {
        "discovery_id": "CANARY-FAKE-002",
        "is_genuine": False,
        "flagging": {"tier": "rejected"},
        "verification": {"real_data_result": {"dataset_id": "X"}, "gates": {}},
    }
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(fake, fake["verification"])


def test_significance_gate_rejects_no_signal():
    """The FDR significance gate must reject a result with zero significant genes."""
    from biodisc_core.fixed_pipeline.fdr_significance_gate import create_significance_validator
    validator = create_significance_validator()
    fake_de = {
        "significant_genes": 0,
        "best_p_value": 1.0,
        "total_genes_tested": 100,
    }
    result = validator.validate_significance(fake_de)
    assert not result.passes_significance_gate, \
        "CANARY FAIL: significance gate accepted a zero-signal result (fabrication risk)"


def test_binding_gate_rejects_unbound_claim():
    """The binding gate must reject a finding whose named gene isn't in the result."""
    from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import create_fixed_discovery_orchestrator
    orch = create_fixed_discovery_orchestrator()
    # MYC (3 chars, matches extract_named_genes) naming a gene NOT in the DE result
    de = {"top_upregulated": [{"gene_symbol": "UNRELATED"}], "top_downregulated": []}
    b = orch._check_question_result_binding("Does MYC expression change here?", de, gene_hypothesis=None)
    assert not b["bound"], "CANARY FAIL: binding gate accepted an unbound fabricated claim"
