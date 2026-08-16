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
"""P3.5 — discovery evolution controller + publish flow."""
from biodisc_core.evolution.discovery_controller import DiscoveryEvolutionController
from biodisc_core.evolution.replication import make_replication_pair
from biodisc_core.evolution.publication import PUBLISH_ELIGIBLE

# A valid alternative discovery program (K=5, simplified CI) different from seed.
ALT_PROGRAM = '''\
import numpy as np
from scipy import stats

def discover(expression, labels, gene_symbols=None):
    treat = labels == 1
    ctrl = labels == 0
    n = expression.shape[0]
    K = min(5, n)
    scores = np.zeros(n)
    for i in range(n):
        t, _ = stats.ttest_ind(expression[i, treat], expression[i, ctrl])
        scores[i] = abs(t) if t == t else 0.0
    out = []
    for i in np.argsort(-scores)[:K]:
        a = expression[i, treat]; b = expression[i, ctrl]
        eff = float(a.mean() - b.mean())
        out.append({"gene_index": int(i), "direction": 1 if eff > 0 else -1,
                    "effect_size": eff, "ci_low": eff - 0.5, "ci_high": eff + 0.5,
                    "p_value": 0.01})
    return out
'''


def _pair():
    return make_replication_pair(n_genes=300, n_samples=30, n_de=30, seed=3,
                                 effect_size=1.2, noise="gaussian")


def test_seed_discovery_replicates_and_is_publish_eligible():
    ctrl = DiscoveryEvolutionController(_pair(), proposer=lambda s, u: ALT_PROGRAM)
    assert ctrl.seed_score.replication_rate > 0.6
    record, score, decision, best = ctrl.publish_best(human_approved=False)
    assert record.written is False  # dry run, no human approval
    assert decision.decision == PUBLISH_ELIGIBLE
    assert score.n_claims > 0


def test_step_accepts_valid_alternative_program():
    ctrl = DiscoveryEvolutionController(_pair(), proposer=lambda s, u: ALT_PROGRAM)
    before = len(ctrl.db.all_programs())
    log = ctrl.step(1)
    assert log.accepted is True
    assert len(ctrl.db.all_programs()) > before


def test_step_rejects_garbage():
    ctrl = DiscoveryEvolutionController(_pair(), proposer=lambda s, u: "not code or diffs")
    log = ctrl.step(1)
    assert log.accepted is False
    assert log.error is not None


def test_publish_writes_with_human_approval(tmp_path):
    log_path = tmp_path / "pub.jsonl"
    ctrl = DiscoveryEvolutionController(_pair(), proposer=lambda s, u: ALT_PROGRAM)
    ctrl.run(generations=1, attempts_per_generation=1)
    record, score, decision, best = ctrl.publish_best(
        human_approved=True, log_path=str(log_path))
    assert decision.decision == PUBLISH_ELIGIBLE
    assert record.written is True
    assert log_path.exists()
    # genealogy provenance present
    import json
    obj = json.loads(log_path.read_text().strip().splitlines()[-1])
    assert len(obj["genealogy"]) >= 1
    assert obj["replication_rate"] == score.replication_rate
