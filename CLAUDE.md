# CLAUDE.md - BIODISC Project Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Modular Documentation Structure

**BIODISC documentation is now organized into modular files for faster loading and easier maintenance:**

### Core Documentation
- **Quick Start**: `docs/01_quick_start.md` - Project overview, GitHub workflow, basic usage
- **Autonomous System**: `docs/02_autonomous_system.md` - V73-V80 auto-start, self-evolution
- **Capabilities**: `docs/03_capabilities.md` - V61-V80 detailed capabilities
- **Architecture**: `docs/04_architecture.md` - System layers, design patterns, communication
- **Testing**: `docs/05_testing.md` - Test procedures, verification
- **Development**: `docs/06_development.md` - Workflow, file organization, pitfalls
- **Memory System**: `docs/07_memory_system.md` - Persistent memory, hallucination register
- **Physics Constants**: `docs/08_physics_constants.md` - Physics constants and reference values
- **PDF Generation**: `docs/09_pdf_generation.md` - PDF generation requirements

### Quick Reference

**Project**: BIODISC (Biology Discovery and Intelligence System)
**Version**: 5.0
**AGI Capability**: 85-90%
**GitHub**: https://github.com/Tilanthi/BIODISC
**Remote**: `biodisc` (use `git push biodisc main`)

### Most Common Tasks

**Start BIODISC System**:
```python
from biodisc_core import create_biodisc_system
system = create_biodisc_system()  # Auto-starts autonomous discovery
result = system.answer("What causes protein misfolding?")
```

**Initialize Memory (REQUIRED at session start)**:
```python
from biodisc_core.memory.persistent import create_integrator
integrator = create_integrator()
integrator.initialize_session()
```

**Run Tests**:
```bash
python biodisc_core/comprehensive_system_test.py
```

### Key Points

1. **Naming**: Always use "BIODISC" (not "STAN" or "STAN-XI-ASTRO")
2. **GitHub**: Push to `biodisc` remote, not `origin`
3. **Auto-Start**: Autonomous discovery starts automatically
4. **Memory**: Always initialize persistent memory at session start
5. **Documentation**: See `.claude/` directory for detailed docs

### System Status

- **Code**: 307,000+ lines, 518+ Python files
- **Capabilities**: 66+ specialist (V36-V94) + 20 revolutionary (V61-V80)
- **Domains**: 10 biology-focused domain modules
- **Agency**: 45% → 70% (Year 1) → 95%+ (5 years)
- **Self-Evolution**: V75-V80 operational (first AI with systematic self-evolution)

### Critical Reminders

- **NEVER push to ASTRA-dev repository** - use BIODISC repository only
- **ALWAYS initialize persistent memory** at session start
- **Let autonomous discovery run** - don't disable auto-start
- **Use factory functions** - never direct constructors
- **Verify claims** against hallucination register

---

**For detailed information, see the modular documentation files in `docs/`**
