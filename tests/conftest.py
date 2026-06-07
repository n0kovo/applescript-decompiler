"""Pytest fixtures: compile the coverage corpus into tests/_build/ before tests run.

Scripts that fail to compile (AppleScript source-level errors in the corpus itself)
are skipped — we can only round-trip ones that osacompile accepts.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

CORPUS = Path(__file__).resolve().parent / "applescripts"
BUILD = Path(__file__).resolve().parent / "_build"


def _compile_corpus() -> list[Path]:
    if shutil.which("osacompile") is None:
        pytest.skip("osacompile not available", allow_module_level=True)
    BUILD.mkdir(exist_ok=True)
    compiled: list[Path] = []
    for src in sorted(CORPUS.glob("*.applescript")):
        out = BUILD / (src.stem + ".scpt")
        if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
            compiled.append(out)
            continue
        r = subprocess.run(
            ["osacompile", "-o", str(out), str(src)],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0 and out.exists():
            compiled.append(out)
    return compiled


_COMPILED = _compile_corpus()


def pytest_generate_tests(metafunc):
    if "scpt_path" in metafunc.fixturenames:
        metafunc.parametrize("scpt_path", _COMPILED, ids=[p.name for p in _COMPILED])
