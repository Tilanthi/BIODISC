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
"""Tests for the sandboxed executor (use _enforce_opt_in=False to bypass the gate in tests)."""
from biodisc_core.fixed_pipeline.sandboxed_executor import run_code


def test_safe_code_runs_and_captures_stdout():
    r = run_code("print(2 + 2)", _enforce_opt_in=False, timeout_s=15, cpu_s=8)
    assert r.ok is True
    assert r.exit_code == 0
    assert "4" in r.stdout


def test_infinite_loop_is_killed():
    r = run_code("while True:\n    x = 0\n", _enforce_opt_in=False,
                 timeout_s=6, cpu_s=2)
    assert r.ok is False
    # caught by CPU rlimit (SIGXCPU) or by the wall-clock timeout, either way not ok
    assert r.timed_out or r.killed_by_limit or r.exit_code != 0


def test_filesize_limit_blocks_huge_write():
    # write well past fs_mb -> SIGXFSZ / non-zero exit
    prog = "f = open('big.bin','wb')\nfor _ in range(100):\n    f.write(b'x'*(1024*1024))\n"
    r = run_code(prog, _enforce_opt_in=False, timeout_s=10, cpu_s=8, fs_mb=5)
    assert r.ok is False
    assert r.killed_by_limit or r.exit_code != 0


def test_nonzero_exit_captured():
    r = run_code("import sys\nsys.exit(7)", _enforce_opt_in=False, timeout_s=10, cpu_s=8)
    assert r.ok is False
    assert r.exit_code == 7


def test_exception_captured_in_stderr():
    r = run_code("raise ValueError('boom')", _enforce_opt_in=False, timeout_s=10, cpu_s=8)
    assert r.ok is False
    assert "boom" in r.stderr


def test_opt_in_gate_refuses_without_flag(monkeypatch):
    monkeypatch.delenv("BIODISC_EVOLUTION_SANDBOX", raising=False)
    r = run_code("print(1)")  # default _enforce_opt_in=True
    assert r.ok is False
    assert "disabled" in r.stderr
