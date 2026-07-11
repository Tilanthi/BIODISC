"""Phase 4 — distillation: promote an evolved win into the default pipeline.

Takes the best program source from a run and writes it as a standalone,
importable module under biodisc_core/evolution/distilled/<target>.py so a
validated evolved method/normalizer can be adopted by the fixed pipeline — the
last-mile counterpart to AlphaEvolve distilling discovered improvements back
into production. The distilled module is a candidate for promotion; a human
still reviews before the pipeline imports it by default.
"""
import os

DEFAULT_DISTILL_DIR = os.path.join(os.path.dirname(__file__), "distilled")

_HEADER = (
    '"""Auto-distilled by BIODISC evolutionary method discovery.\n\n'
    "This module was produced by the AlphaEvolve-style evolution loop and written\n"
    "via distill.distill_program(). It is a CANDIDATE for promotion into the\n"
    "default pipeline; review before importing by default.\n"
    '"""\n'
)


def distill_program(source: str, target_name: str, out_dir: str = DEFAULT_DISTILL_DIR) -> str:
    """Write ``source`` as an importable module ``<out_dir>/<target_name>.py``.

    Returns the written path. ``target_name`` must be a valid module name.
    """
    if not target_name.isidentifier():
        raise ValueError(f"target_name must be a valid Python identifier, got {target_name!r}")
    os.makedirs(out_dir, exist_ok=True)
    # ensure the package is importable
    init_path = os.path.join(out_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write('"""Distilled (evolved) programs. Auto-generated candidates."""\n')

    path = os.path.join(out_dir, f"{target_name}.py")
    with open(path, "w") as f:
        f.write(_HEADER)
        f.write("\n")
        f.write(source)
    return path
