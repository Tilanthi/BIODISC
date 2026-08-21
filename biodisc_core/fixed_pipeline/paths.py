"""Central filesystem layout for the fixed discovery pipeline.

Single source of truth for every path the live pipeline reads or writes.
Before this module existed, seven files each defined their own
``PROJECT_ROOT = Path(__file__).resolve().parents[2]`` — the pipeline's
state lived, by convention only, one directory above the package and was
not relocatable.

Resolution order for the data root:

1. ``$BIODISC_DATA_ROOT`` (environment override — makes the package
   standalone-relocatable);
2. the repository root two parents up (the historical default, preserved
   byte-for-byte so the always-on watchdog loop's paths do not move).

Guarded by ``tests/test_pipeline_paths.py`` (default unchanged + env
override + read/write through the helper).
"""

import os
from pathlib import Path

# Historical default: biodisc_core/fixed_pipeline/paths.py -> up 2 parents
# is the BIODISC repository root. parents[3] would be SWARM — one level too
# high (the bug discovery_store.py's comment records). Do not change the
# default: the live loop's stores, logs and indexes live there.
_DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[2]

#: Root for all pipeline state (stores, verdict log, index, RSI artifacts).
#: Set ``BIODISC_DATA_ROOT`` to relocate the whole pipeline.
DATA_ROOT = Path(os.environ.get("BIODISC_DATA_ROOT", str(_DEFAULT_DATA_ROOT)))

#: The biodisc_core package directory itself (for data shipped with the
#: package, e.g. fixed_pipeline/real_datasets_extra.json).
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def data_path(*parts) -> Path:
    """Join ``parts`` onto :data:`DATA_ROOT` (the env-overridable root)."""
    return DATA_ROOT.joinpath(*parts)


def package_path(*parts) -> Path:
    """Join ``parts`` onto the biodisc_core package directory."""
    return PACKAGE_ROOT.joinpath(*parts)
