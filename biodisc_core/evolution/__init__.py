"""AlphaEvolve-style evolutionary method discovery for BIODISC (Phase 1+).

Evolves the *code* of a bioinformatics method (here: a differential-expression
scoring function) via LLM-proposed search-and-replace diffs, scored by the
automated evaluator from biodisc_core.fixed_pipeline.benchmark.

This is CODE evolution (AlphaEvolve's mechanism), deliberately distinct from
the parameter/numeric evolution in biodisc_core.swarm.leapcore_evolution (which
mutates numeric Gene values and cannot represent open-ended program code).
"""
