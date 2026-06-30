# BIODISC Memory System

## CRITICAL: Persistent Memory Initialization

**IMPORTANT**: At the start of EVERY session, initialize the persistent memory system. This ensures:
- Previous session context is restored
- Known hallucinations are loaded and prevented
- User preferences are applied
- Anti-hallucination protection is active

```python
# RUN THIS AT SESSION START
from biodisc_core.memory.persistent import create_integrator, quick_hallucination_check

integrator = create_integrator()
integrator.initialize_session()
```

## Before Making Any Factual Claim

ALWAYS verify numerical claims against the hallucination register:

```python
result = integrator.verify_claim_before_output("protein folding mechanism")
if not result.safe:
    # Use the correct value instead
    correct = result.hallucination_match.correct_value
```

## Known Hallucinations

The hallucination register is stored in `~/.biodisc_persistent/hallucination_register.json`.
To view or manage entries:

```python
from biodisc_core.memory.persistent import BootstrapMemory
bm = BootstrapMemory()
bm.list_hallucinations()  # View all entries
bm.remove_hallucination("54 MHz")  # Remove if no longer needed
```

## Document Review Protocol

When reviewing ANY document:
1. Extract key info first (experimental conditions, sample sizes, methodologies)
2. Verify each claim with `quick_hallucination_check()`
3. Include mandatory anti-hallucination verification table in all reviews

## Checkpoint During Long Sessions

```python
# Periodically save session state
integrator.create_session_checkpoint({"current_task": "your task description"})
```

## Memory Palace Location

Autonomous discoveries are stored at:
`~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/`

## Persistent Memory Location

Session persistence and hallucination register at:
`~/.biodisc_persistent/`

## Memory Hierarchy

- **MORK Ontology**: `biodisc_core/memory/mork_ontology.py` (concept hierarchies)
- **Memory Graph**: `biodisc_core/memory/context_graph.py` (context relationships)
- **Working Memory**: `biodisc_core/memory/working/` (7±2 capacity constraint)
- **Persistent Memory**: `biodisc_core/memory/persistent.py` (session persistence, hallucination register)
- **Memory Palace**: `~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/` (autonomous discoveries)
