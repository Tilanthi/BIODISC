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
