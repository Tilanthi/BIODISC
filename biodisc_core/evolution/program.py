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
"""Representation + safe compilation of evolvable DE programs.

A DE program is a Python source string that defines::

    def score(expression, labels) -> np.ndarray

returning per-gene DE scores (higher = more DE). Evolution mutates the SOURCE;
the controller compiles each candidate to score it.

SECURITY NOTE: compile_de_program() execs program source. In Phase 1 the source
is either the trusted seed or LLM-proposed diffs. A production deployment MUST
run candidate programs in a sandbox (separate process/container, no network,
CPU/memory limits). This is the standard AlphaEvolve-style trust model: the
*evaluator* is trusted, the candidate code is not.
"""
import ast
from typing import Callable

import numpy as np

DE_PROGRAM_CONTRACT = (
    "Source must define `def score(expression, labels):` returning a 1D numpy "
    "array of per-gene scores (higher = more differentially expressed)."
)


def validate_program_source(source: str) -> bool:
    """Static check: source parses and defines a top-level ``score`` function."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(n, ast.FunctionDef) and n.name == "score"
        for n in tree.body
    )


def compile_de_program(source: str) -> Callable[[np.ndarray, np.ndarray], np.ndarray]:
    """Compile DE program source into a callable ``score(expression, labels)``.

    Raises ValueError if the source is invalid or does not define ``score``.
    """
    if not validate_program_source(source):
        raise ValueError(f"Invalid DE program source. {DE_PROGRAM_CONTRACT}")

    namespace: dict = {"np": np, "__name__": "de_program"}
    exec(compile(source, "<de_program>", "exec"), namespace)  # noqa: S102 (see SECURITY NOTE)
    fn = namespace.get("score")
    if not callable(fn):
        raise ValueError(f"DE program did not define a callable `score`. {DE_PROGRAM_CONTRACT}")
    return fn
