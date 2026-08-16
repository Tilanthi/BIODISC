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
"""Truth-known benchmark fixtures for scoring differential-expression methods.

WARNING / SCOPE — read before editing:
These fixtures are SYNTHETIC DATA WITH KNOWN GROUND TRUTH used to *score DE
methods*, exactly as DE-method benchmarks do in the bioinformatics literature.
They are NOT discovery data and must NEVER be emitted as a BIODISC discovery.
This is the legitimate exception to the "no synthetic data" rule (which governs
the *discovery* path). Every file here is named ``benchmark_*`` on purpose.
"""
from .truth_known_fixture import BenchmarkCase, make_de_benchmark
from .de_fitness import DEMethodScore, score_de_method

__all__ = ["BenchmarkCase", "make_de_benchmark", "DEMethodScore", "score_de_method"]
