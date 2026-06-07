"""Opcode-coverage regression: decompile every corpus script, then assert
the union of unhandled opcodes is in our known-gap set.
"""

from __future__ import annotations

from pathlib import Path

from applescript_decompiler import decompiler

# Opcodes we deliberately haven't modeled yet. Shrink this set over time; never grow it.
KNOWN_GAPS: set[str] = set()


def test_no_unhandled_opcodes(scpt_path: Path):
    decompiler.reset_coverage()
    decompiler.decompile_file(scpt_path)
    unexpected = set(decompiler.UNHANDLED) - KNOWN_GAPS
    assert not unexpected, (
        f"{scpt_path.name}: unhandled opcodes {sorted(unexpected)} "
        f"(counts: { {k: decompiler.UNHANDLED[k] for k in unexpected} })"
    )


def test_coverage_report(scpt_path: Path):
    """Prints an opcode histogram per script — not an assertion, just signal."""
    decompiler.reset_coverage()
    decompiler.decompile_file(scpt_path)
    print(f"\n{scpt_path.name}: {len(decompiler.OPCODE_COUNTS)} distinct opcodes")
    print(f"  unhandled: {dict(decompiler.UNHANDLED) or 'none'}")
