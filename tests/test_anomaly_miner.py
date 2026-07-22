"""Tests for the anomaly miner (observed surprises as primary discovery input)."""
from biodisc_core.fixed_pipeline.anomaly_miner import mine_anomalies, best_anomaly


def _de(ups, downs):
    """ups/downs: list of (gene, log2fc_mag, p)."""
    return {
        "top_upregulated": [{"gene_symbol": g, "log2_fold_change": l, "p_value": p,
                             "fdr_p_value": p, "regulation": "up"} for g, l, p in ups],
        "top_downregulated": [{"gene_symbol": g, "log2_fold_change": -l, "p_value": p,
                               "fdr_p_value": p, "regulation": "down"} for g, l, p in downs],
    }


def test_direction_flip_vs_prior():
    de = _de([("GENEA", 0.5, 1e-5)], [])          # GENEA up here
    prior = {"GENEA": {"GSE_OTHER": "down"}}      # ...but down elsewhere
    cands = mine_anomalies(de, prior, dataset_id="GSE_THIS")
    assert cands and cands[0].gene == "GENEA"
    assert "direction_flip_vs_prior" in cands[0].kind
    assert cands[0].prior_direction == "down"
    assert "reversing" in cands[0].claim


def test_extreme_effect():
    de = _de([("GENEB", 3.0, 1e-8)], [])          # huge effect, no prior
    cands = mine_anomalies(de, {}, dataset_id="X")
    assert cands and cands[0].gene == "GENEB"
    assert "extreme_effect" in cands[0].kind


def test_no_anomaly_when_consistent_and_modest():
    de = _de([("GENEC", 0.4, 1e-4)], [])
    prior = {"GENEC": {"GSE_OTHER": "up"}}         # same direction, modest effect
    assert mine_anomalies(de, prior, dataset_id="GSE_THIS") == []


def test_self_dataset_prior_excluded():
    de = _de([("GENEA", 0.5, 1e-5)], [])           # up here
    prior = {"GENEA": {"GSE_THIS": "down"}}        # prior only in THIS dataset
    assert mine_anomalies(de, prior, dataset_id="GSE_THIS") == []


def test_hub_gene_ranks_above_obscure_for_same_surprise():
    # both flip; TP53 is a hub (importance 1.0), OBSCURE is not (0.2)
    de = _de([("TP53", 0.5, 1e-5), ("OBSCURE", 0.5, 1e-5)], [])
    prior = {"TP53": {"X": "down"}, "OBSCURE": {"X": "down"}}
    cands = mine_anomalies(de, prior, dataset_id="THIS")
    assert cands[0].gene == "TP53"


def test_best_anomaly_or_none():
    assert best_anomaly(_de([("GENEA", 0.3, 1e-4)], []), {}, "X") is None  # nothing surprising
    b = best_anomaly(_de([("GENEA", 3.0, 1e-8)], []), {}, "X")
    assert b is not None and b.gene == "GENEA"
