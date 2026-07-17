# Broken Files Baseline — biodisc_core

Following the astra_core external review approach: these files are truncated /
syntactically broken from an automated edit session (same fabrication-adjacent
failure mode). They are NOT guess-repaired (guessing truncated code is
fabrication-adjacent). They are orphaned — not in the live pipeline import chain,
not in the test suite, not imported by fixed_pipeline or the discovery loop.

## Live pipeline status: CLEAN
- fixed_pipeline/: 44/44 files pass syntax check
- evolution/: 26/26 files pass syntax check
- tests/: 215/215 pass, 0 fail

## 34 broken files (baselined, not repaired)

| File | Error |
|---|---|
| biodisc_core/arc_agi/pattern_library.py | line 492: unterminated triple-quoted string literal (detected at line 501) |
| biodisc_core/arc_reasoning/improved_solver.py | line 107: '[' was never closed |
| biodisc_core/arc_reasoning/llm_code_generator.py | line 103: unterminated triple-quoted string literal (detected at line 104) |
| biodisc_core/arc_reasoning/neuro_symbolic_solver.py | line 228: unterminated triple-quoted string literal (detected at line 230) |
| biodisc_core/arc_reasoning/super_ensemble_solver.py | line 196: '{' was never closed |
| biodisc_core/capabilities/vXX_enhanced_causal_discovery.py | line 785: unmatched ')' |
| biodisc_core/core/v105/scientific_discovery.py | line 378: '(' was never closed |
| biodisc_core/gsd/atomic_workflow.py | line 276: unterminated triple-quoted string literal (detected at line 283) |
| biodisc_core/gsd/codebase_mapper.py | line 362: '{' was never closed |
| biodisc_core/gsd/xml_task_formatting.py | line 269: expected an indented block after 'if' statement on line 269 |
| biodisc_core/intelligence/redundant_executor.py | line 149: '[' was never closed |
| biodisc_core/legacy/systems/v40/meta_cognitive.py | line 544: expected an indented block after 'for' statement on line 544 |
| biodisc_core/legacy/systems/v92/v92_system.py | line 336: expected an indented block after function definition on line 336 |
| biodisc_core/legacy/systems/v93/self_modifying_architecture.py | line 92: '(' was never closed |
| biodisc_core/legacy/systems/v94/language_grounding.py | line 543: expected an indented block after function definition on line 543 |
| biodisc_core/legacy/systems/v94/sensorimotor_system.py | line 231: unterminated triple-quoted string literal (detected at line 232) |
| biodisc_core/mathematical/aletheia_stan_architecture.py | line 127: '{' was never closed |
| biodisc_core/metacognitive/evolutionary_context_layer.py | line 146: '[' was never closed |
| biodisc_core/reasoning/abstraction_stack.py | line 2: invalid syntax |
| biodisc_core/reasoning/formal_logic_enhanced.py | line 112: expected an indented block after function definition on line 112 |
| biodisc_core/reasoning/integrated_reasoning.py | line 217: unmatched ')' |
| biodisc_core/reasoning/symbolic_verification.py | line 508: '(' was never closed |
| biodisc_core/reasoning/v70_predictive_geometry.py | line 354: '[' was never closed |
| biodisc_core/reasoning/v70_teleology_filter.py | line 355: unexpected indent |
| biodisc_core/retrieval/context_distiller.py | line 243: '{' was never closed |
| biodisc_core/retrieval/query_expander.py | line 275: '{' was never closed |
| biodisc_core/retrieval/sharded_retrieval.py | line 251: '{' was never closed |
| biodisc_core/scientific_discovery/paper_rag_query.py | line 353: '[' was never closed |
| biodisc_core/scientific_discovery/setup_paper_library.py | line 132: expected an indented block after 'if' statement on line 132 |
| biodisc_core/self_teaching/architecture_rewriter.py | line 144: '(' was never closed |
| biodisc_core/self_teaching/consciousness_simulator.py | line 340: '{' was never closed |
| biodisc_core/symbolic/tool_integration.py | line 139: '{' was never closed |
| biodisc_core/symbolic/v37_system.py | line 182: unterminated triple-quoted string literal (detected at line 185) |
| biodisc_core/trading/analysis/causal_analysis.py | line 9: expected 'except' or 'finally' block |

## What to do about them
These are dead code from the V36-V94+ "AGI capability" era. They should be
either (a) deleted (recoverable from git history) or (b) left as-is since they
don't affect the live system. Guess-repairing truncated code is explicitly avoided.

Generated 2026-07-17 by a syntax audit prompted by the astra_core external review.