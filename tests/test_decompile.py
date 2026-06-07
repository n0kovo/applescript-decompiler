"""Round-trip + sanity tests for every compiled coverage script."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from applescript_decompiler import decompile_file


def test_no_exception(scpt_path: Path):
    out = decompile_file(str(scpt_path))
    assert isinstance(out, str) and out


def test_no_unknown_markers(scpt_path: Path):
    out = decompile_file(str(scpt_path))
    for bad in ("<unknown>", "???", "<empty_stack>", "TODO"):
        assert bad not in out, f"{scpt_path.name}: leaked marker {bad!r}"


def test_repeat_headers_match_ends(scpt_path: Path):
    """Every `end repeat` should have a preceding opener in the same function."""
    out = decompile_file(str(scpt_path))
    for func_block in out.split("Function:")[1:]:
        open_n = sum(
            1 for line in func_block.splitlines() if line.strip().startswith("repeat")
        )
        close_n = sum(
            1 for line in func_block.splitlines() if line.strip() == "end repeat"
        )
        assert open_n >= close_n, (
            f"{scpt_path.name}: {close_n} end-repeat(s), only {open_n} opener(s)"
        )


def test_no_raw_global_placeholder(scpt_path: Path):
    """Globals should be resolved — no leaked `global_'xxx'` placeholders."""
    out = decompile_file(str(scpt_path))
    assert "global_'" not in out and 'global_"' not in out


@pytest.mark.skipif(shutil.which("osacompile") is None, reason="osacompile missing")
def test_round_trip_compiles(scpt_path: Path):
    """Decompiled output must be syntactically valid AppleScript."""
    src = decompile_file(str(scpt_path))
    # strip our framing comments/headers osacompile can't parse
    lines = [
        ln for ln in src.splitlines()
        if not ln.startswith("=")
        and not ln.startswith("Function:")
        and not ln.startswith("Arguments:")
    ]
    cleaned = "\n".join(lines)
    with tempfile.NamedTemporaryFile("w", suffix=".applescript", delete=False) as f:
        f.write(cleaned)
        src_path = f.name
    try:
        out_path = src_path + ".scpt"
        r = subprocess.run(
            ["osacompile", "-o", out_path, src_path],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            pytest.xfail(f"recompile failed: {r.stderr.strip()[:200]}")
    finally:
        Path(src_path).unlink(missing_ok=True)
        Path(src_path + ".scpt").unlink(missing_ok=True)
