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
"""Sandboxed executor for LLM-generated analysis code (evolution / hypothesis-as-code).

This is the one place in the pipeline that can do real harm: ``exec()`` of
model-written code. It gets three layers of defense-in-depth, and it is OPT-IN
and OFF by default (``BIODISC_EVOLUTION_SANDBOX=1``). It is never wired into the
always-on loop unattended.

Layers:
1. **Process isolation** — generated code runs in a *child subprocess*, never in
   the loop's process. A crash, ``sys.exit``, or infinite loop cannot take down
   discovery, and resource limits are scoped to the child.
2. **Resource limits** — the child sets ``RLIMIT_CPU`` (CPU seconds -> SIGXCPU),
   ``RLIMIT_FSIZE`` (max file write -> SIGXFSZ), and ``RLIMIT_AS`` (address space,
   where supported). A runaway program is killed by the kernel.
3. **Wall-clock timeout + private cwd** — a hard ``timeout`` kills the child if
   CPU limits don't catch it; the working directory is a private temp dir that is
   removed afterward, so generated code cannot pollute the repo or read private
   files by relative path.

What this is NOT: a security sandbox for UNTRUSTED code. True network and
filesystem isolation needs OS-level containment (a container / seccomp / network
namespace), which is Linux-specific. On macOS (this host) the network cannot be
reliably blocked and ``RLIMIT_AS`` is partly honored. So this executor is for
SUPERVISED, opt-in use — a human reviews generated programs, and the proposer is
a trusted gateway (the configured Anthropic-compatible endpoint). Do NOT use it
for untrusted code without a Linux container around it.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 200_000  # cap captured stdout/stderr so a flood can't exhaust memory

# Opt-in flag. The executor refuses to run unless this is "1", so it can never
# be triggered accidentally (e.g. by the always-on loop importing a caller).
ENABLE_FLAG = "BIODISC_EVOLUTION_SANDBOX"


def is_enabled() -> bool:
    """True only when explicitly opted in via the environment."""
    return os.environ.get(ENABLE_FLAG) == "1"


@dataclass
class SandboxResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    truncated: bool
    duration_s: float
    killed_by_limit: bool

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def _preamble(cpu_s: int, fs_mb: int, mem_mb: int) -> str:
    """Child-side code that sets rlimits BEFORE the user program runs."""
    fs_bytes = fs_mb * 1024 * 1024
    mem_bytes = mem_mb * 1024 * 1024
    return (
        "import resource\n"
        "try:\n"
        f"    resource.setrlimit(resource.RLIMIT_CPU, ({cpu_s}, {cpu_s}))\n"
        "except Exception:\n"
        "    pass\n"
        "try:\n"
        f"    resource.setrlimit(resource.RLIMIT_FSIZE, ({fs_bytes}, {fs_bytes}))\n"
        "except Exception:\n"
        "    pass\n"
        "try:\n"  # RLIMIT_AS is ignored on some platforms (notably older macOS); best-effort.
        f"    resource.setrlimit(resource.RLIMIT_AS, ({mem_bytes}, {mem_bytes}))\n"
        "except Exception:\n"
        "    pass\n"
    )


def run_code(source: str,
             *,
             timeout_s: float = 15.0,
             cpu_s: int = 8,
             fs_mb: int = 50,
             mem_mb: int = 1024,
             python: Optional[str] = None,
             _enforce_opt_in: bool = True) -> SandboxResult:
    """Run generated ``source`` in a sandboxed child subprocess.

    Refuses to run unless the sandbox is opted in (``BIODISC_EVOLUTION_SANDBOX=1``),
    unless ``_enforce_opt_in=False`` (used by the self-tests so they can exercise
    the executor without flipping a global flag).
    """
    if _enforce_opt_in and not is_enabled():
        logger.warning("sandboxed executor called while disabled (set %s=1 to enable); refusing.",
                       ENABLE_FLAG)
        return SandboxResult(ok=False, exit_code=-1, stdout="", stderr="sandbox disabled",
                             timed_out=False, truncated=False, duration_s=0.0,
                             killed_by_limit=False)

    python = python or sys.executable
    tmp = Path(tempfile.mkdtemp(prefix="biodisc_sandbox_"))
    main = tmp / "_user_program.py"
    # preamble (rlimits) runs first, then the user program in the same process.
    main.write_text(_preamble(cpu_s, fs_mb, mem_mb) + "\n" + source)
    t0 = time.time()
    timed_out = False
    killed_by_limit = False
    try:
        proc = subprocess.run(
            [python, str(main)], cwd=str(tmp),
            capture_output=True, timeout=timeout_s, text=True)
        exit_code = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        # Negative signals on POSIX: SIGXCPU (-24), SIGXFSZ (-25) => killed by a rlimit.
        if exit_code in (-24, -25):
            killed_by_limit = True
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code = -1
        out = e.stdout or ""
        err = e.stderr or ""
        stdout = out.decode() if isinstance(out, (bytes, bytearray)) else (out or "")
        stderr = err.decode() if isinstance(err, (bytes, bytearray)) else (err or "")
    duration = time.time() - t0

    truncated = len(stdout) > MAX_OUTPUT_CHARS or len(stderr) > MAX_OUTPUT_CHARS
    stdout = stdout[:MAX_OUTPUT_CHARS]
    stderr = stderr[-MAX_OUTPUT_CHARS:]  # keep the tail (tracebacks) on truncation
    ok = (not timed_out) and exit_code == 0
    shutil.rmtree(tmp, ignore_errors=True)
    return SandboxResult(ok=ok, exit_code=exit_code, stdout=stdout, stderr=stderr,
                         timed_out=timed_out, truncated=truncated,
                         duration_s=round(duration, 3), killed_by_limit=killed_by_limit)
