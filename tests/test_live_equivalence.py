# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Equivalence of the catalogue against the LIVE HGNC API.

Skipped unless you ask for it:

    BIODISC_HGNC_LIVE=1 python -m pytest tests/test_live_equivalence.py -s

It is opt-in because it makes a few hundred requests to rest.genenames.org and
takes about a minute. Nothing else in the test suite touches the network.

What it checks, symbol by symbol: the verdict the code USED to reach, by
calling `fetch/symbol/<symbol>` with the URL built exactly the way the previous
implementation built it, against the verdict the catalogue reaches. Any
disagreement is a change to which genes enter an analysis, and would mean this
change is not an optimisation.

The sample is deliberately adversarial rather than random. A random sample of
gene symbols is nearly all ordinary approved ones and hides the classes where
the two paths could differ: withdrawn entries, non-human capitalisation,
multi-gene probe annotations such as ``MIR4640///DDR1``, and symbols the
anti-fabrication heuristics are meant to catch.
"""
import os
import time

import pytest
import requests

from biodisc_core.fixed_pipeline import gene_symbol_validation as gsv

pytestmark = pytest.mark.skipif(
    not os.environ.get("BIODISC_HGNC_LIVE"),
    reason="live HGNC test; set BIODISC_HGNC_LIVE=1 to run it")

PACE = 0.12  # HGNC publish a 10 requests/second ceiling; stay under it.

# Non-human capitalisation. These must land exactly where they landed before -
# right or wrong. (They are, for the record, one of the reasons a mouse dataset
# validates against a human nomenclature authority at all; that question is a
# scientific one and is untouched here.)
NON_HUMAN_CASED = ["Mtor", "Trp53", "Xist", "Gm10801", "Best1", "Cradd",
                   "Rcan2", "Actb", "Sox2", "Nanog"]
# Real GPL96 probe annotations that name more than one gene.
MULTI_GENE = ["MIR4640///DDR1", "TP53///TP63", "GAGE12F///GAGE12I",
              "HBA1///HBA2", "MT1L///MT1E"]
FABRICATED = ["RPL166", "KRT113", "ALDO52", "GAPD115", "HSP167", "COL219"]
ODD = ["TNF alpha", "C1orf112", "HLA-DRB1", "MIR4640", "---", "NA"]


def _live_verdict(session, symbol):
    """Exactly what the previous implementation did, including building the URL
    by string concatenation with no escaping."""
    try:
        r = session.get("https://rest.genenames.org/fetch/symbol/" + symbol,
                        headers={"Accept": "application/json"}, timeout=15)
        if r.status_code == 200:
            body = r.json()
            if body.get("response") and "numFound" in body["response"]:
                return ("VALID" if body["response"]["numFound"] > 0 else "INVALID"), r.status_code
        return "UNANSWERABLE", r.status_code
    except Exception as e:  # noqa: BLE001
        return "UNANSWERABLE", type(e).__name__


def test_catalogue_agrees_with_the_per_symbol_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("BIODISC_HGNC_CATALOGUE", str(tmp_path / "catalogue.json"))
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE", None)
    monkeypatch.setattr(gsv, "_HGNC_CATALOGUE_TRIED", False)

    catalogue = gsv._hgnc_catalogue()
    assert catalogue, "catalogue could not be fetched"

    session = requests.Session()
    # Reference populations, fetched INDEPENDENTLY of the catalogue under test.
    # Deriving the sample from the catalogue itself would let a catalogue that
    # omits a class of symbols also omit the very symbols that would expose it.
    everything = session.get("https://rest.genenames.org/search/symbol/*",
                             headers={"Accept": "application/json"}, timeout=180)
    all_symbols = {d["symbol"].upper() for d in everything.json()["response"]["docs"]}
    approved = session.get("https://rest.genenames.org/search/status/Approved",
                           headers={"Accept": "application/json"}, timeout=180)
    approved_symbols = {d["symbol"].upper() for d in approved.json()["response"]["docs"]}
    non_approved = sorted(all_symbols - approved_symbols)

    n = int(os.environ.get("BIODISC_HGNC_LIVE_SAMPLE") or "60")
    ordered = sorted(all_symbols)
    buckets = {
        "approved_spread": sorted(approved_symbols)[::max(1, len(approved_symbols) // n)][:n],
        "non_approved": non_approved[::max(1, len(non_approved) // n)][:n],
        "non_human_cased": NON_HUMAN_CASED,
        "multi_gene": MULTI_GENE,
        "fabricated": FABRICATED,
        "odd": ODD,
    }

    agree = disagree = unanswerable = 0
    problems = []
    for bucket, symbols in buckets.items():
        for symbol in symbols:
            live, status = _live_verdict(session, symbol)
            mine = "VALID" if symbol.upper() in catalogue else "INVALID"
            if live == "UNANSWERABLE":
                unanswerable += 1
                problems.append(f"[live could not answer] {bucket} {symbol!r} http={status}")
            elif live == mine:
                agree += 1
            else:
                disagree += 1
                problems.append(f"[DISAGREE] {bucket} {symbol!r} live={live} catalogue={mine}")
            time.sleep(PACE)

    total = agree + disagree + unanswerable
    enough = agree >= min(100, total)
    print(f"\nCOVERAGE: {total} symbols compared over {len(buckets)} buckets "
          f"({', '.join(f'{k}={len(v)}' for k, v in buckets.items())}); "
          f"HGNC holds {len(all_symbols)} symbols with {len(non_approved)} of them "
          f"not of status Approved; the catalogue under test holds {len(catalogue)}")
    for p in problems:
        print("  " + p)
    print(f"VERDICT: {'GREEN' if disagree == 0 and enough else 'RED'} - "
          f"agree={agree} disagree={disagree} live-unanswerable={unanswerable}")

    assert total >= 100, "too few comparisons to mean anything"
    assert disagree == 0, problems
