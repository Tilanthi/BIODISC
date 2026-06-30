# BIODISC Development Workflow

## Development Workflow

1. **Test before modifying**: Always run relevant tests first to establish baseline
2. **Respect graceful degradation**: Any new module must have try/except imports and fallback behavior
3. **Use factory functions**: Create via `create_<module>()` pattern
4. **Register new domains**: Use `@register_domain` decorator for discoverability
5. **Update exports**: Add new public classes to `__all__` in module `__init__.py`
6. **Initialize persistent memory**: Always run `create_integrator().initialize_session()` at session start
7. **Let autonomous discovery run**: Don't disable auto-start unless absolutely necessary

## Common Pitfalls

1. **Missing Imports**: Always check for import availability. Most imports wrapped in try/except with None fallback. Test `if MODULE is not None:` before use.

2. **Direct Construction**: Never directly instantiate capability classes. Use factory functions: `create_<module>()`.

3. **Hardcoded Physics Values**: Always use `UnifiedPhysicsEngine.constants`, never hardcode physical constants.

4. **Skipping Initialization**: Domain modules must call `.initialize(global_config)` after creation before `.process_query()`.

5. **Backup File Accumulation**: Run `cleanup_biodisc_core.py` if directory exceeds expected size. Backup files (`*.backup`) from `cleanup_bloat.py` can accumulate to GBs.

6. **Forgetting Activity Tracking**: Don't manually pause/resume autonomous discovery - activity tracking is automatic. Just use `system.answer()` normally.

7. **Ignoring Persistent Memory**: Always initialize persistent memory at session start to enable hallucination prevention and context restoration.

## Code Organization

### Capability Files Location

- **V36-V50 capabilities**: `biodisc_core/capabilities/vXX_*.py`
- **V61-V73 capabilities**: `biodisc_core/capabilities/v1XX_*.py`
- **Physics modules**: `biodisc_core/physics/*.py`
- **Domain modules**: `biodisc_core/domains/<domain_name>/__init__.py`
- **Meta-learning**: `biodisc_core/reasoning/maml_optimizer.py`, `cross_domain_meta_learner.py`
- **Autonomous system**: `biodisc_core/autonomous/` (orchestrator, decision_maker, validator, etc.)

### Memory Hierarchy

- **MORK Ontology**: `biodisc_core/memory/mork_ontology.py` (concept hierarchies)
- **Memory Graph**: `biodisc_core/memory/context_graph.py` (context relationships)
- **Working Memory**: `biodisc_core/memory/working/` (7±2 capacity constraint)
- **Persistent Memory**: `biodisc_core/memory/persistent.py` (session persistence, hallucination register)
- **Memory Palace**: `~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/` (autonomous discoveries)

### Test Files

- **Integration tests**: `biodisc_core/tests/v4/test_v4_integration.py`
- **Capability tests**: `biodisc_core/tests/test_specialist_capabilities.py`
- **Autonomous tests**: `biodisc_core/tests/test_autonomous_discovery.py`
- **Validation**: `biodisc_core/tests/validation_benchmarks.py`
