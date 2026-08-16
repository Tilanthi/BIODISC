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
"""P1.1 — program representation, seed, and benchmark headroom.

The seed (Student's t-test) must compile and run, and it must score HIGH on the
easy benchmark but LOWER on the hard benchmark — i.e. there is headroom for
evolution to discover a more robust statistic. If t-test were already perfect
on the hard benchmark, evolution would have nothing to optimize.
"""
import numpy as np
import pytest

from biodisc_core.evolution.program import (
    compile_de_program, validate_program_source, DE_PROGRAM_CONTRACT,
)
from biodisc_core.evolution.seeds import get_seed_program
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark, score_de_method


def test_seed_source_is_valid():
    assert validate_program_source(get_seed_program()) is True


def test_rejects_source_without_score():
    assert validate_program_source("x = 1\n") is False
    with pytest.raises(ValueError):
        compile_de_program("def not_score():\n    return 0\n")


def test_compiled_seed_returns_correct_shape():
    fn = compile_de_program(get_seed_program())
    case = make_de_benchmark(n_genes=50, n_samples=20, n_de=5, seed=0)
    scores = fn(case.expression, case.labels)
    assert isinstance(scores, np.ndarray)
    assert scores.shape == (50,)


def test_seed_scores_high_on_easy_benchmark():
    fn = compile_de_program(get_seed_program())
    easy = make_de_benchmark(n_genes=400, n_samples=40, n_de=40, seed=1, noise="gaussian")
    s = score_de_method(fn, easy)
    assert s.aggregate > 0.90, f"seed should be strong on easy data, got {s.aggregate}"


def test_hard_benchmark_leaves_headroom_for_evolution():
    fn = compile_de_program(get_seed_program())
    easy = make_de_benchmark(n_genes=400, n_samples=40, n_de=40, seed=1, noise="gaussian")
    hard = make_de_benchmark(
        n_genes=400, n_samples=16, n_de=40, seed=1,
        effect_size=0.8, noise="heteroscedastic",
    )
    s_easy = score_de_method(fn, easy)
    s_hard = score_de_method(fn, hard)
    # The seed must be WORSE on the hard benchmark — that is evolution's headroom.
    assert s_hard.aggregate < s_easy.aggregate, (
        f"expected headroom: hard ({s_hard.aggregate}) < easy ({s_easy.aggregate})"
    )
    assert s_hard.aggregate < 0.98, (
        f"hard benchmark too easy (seed={s_hard.aggregate}); widen headroom"
    )
