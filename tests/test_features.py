"""Feature tests: compile a small AppleScript snippet, decompile it, and assert
on the reconstructed source.

Each test states one expected behaviour. `decompile_snippet` compiles the
source with osacompile (skipped if unavailable) and returns the decompiled
body of the last handler (the implicit `run` handler unless noted).
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from applescript_decompiler import decompile_file

pytestmark = pytest.mark.skipif(
    shutil.which("osacompile") is None, reason="osacompile not available"
)


def decompile_snippet(source: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td, "snippet.applescript")
        src.write_text(source)
        out = Path(td, "snippet.scpt")
        r = subprocess.run(
            ["osacompile", "-o", str(out), str(src)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            pytest.skip(f"snippet did not compile: {r.stderr.strip()}")
        return decompile_file(out)


def recompiles(decompiled: str) -> bool:
    """Whether osacompile accepts the decompiled output as valid AppleScript."""
    body = "\n".join(
        ln
        for ln in decompiled.splitlines()
        if not ln.startswith(("=", "Function:", "Arguments:"))
    )
    with tempfile.TemporaryDirectory() as td:
        src = Path(td, "rt.applescript")
        src.write_text(body)
        out = Path(td, "rt.scpt")
        r = subprocess.run(
            ["osacompile", "-o", str(out), str(src)],
            capture_output=True,
            text=True,
        )
        return r.returncode == 0


# --- repeat loops -----------------------------------------------------------


def test_repeat_range_keeps_bounds():
    out = decompile_snippet(
        "on f(x)\n"
        "    repeat with i from 2 to x\n"
        "        log i\n"
        "    end repeat\n"
        "end f\n"
    )
    assert "from 2 to x" in out
    assert "undefined" not in out


def test_repeat_range_with_step():
    out = decompile_snippet(
        "repeat with k from 2 to 10 by 3\n    log k\nend repeat\n"
    )
    assert "from 2 to 10 by 3" in out


def test_repeat_in_collection_keeps_collection():
    out = decompile_snippet(
        'repeat with z in {"a", "b"}\n    log z\nend repeat\n'
    )
    assert '{"a", "b"}' in out
    assert "in undefined" not in out


def test_repeat_n_times():
    out = decompile_snippet("repeat 3 times\n    beep\nend repeat\n")
    assert "repeat 3 times" in out


# --- if / else if -----------------------------------------------------------


def test_else_if_chain_does_not_swallow_following_code():
    out = decompile_snippet(
        "set x to 5\n"
        "if x < 0 then\n"
        '    log "neg"\n'
        "else if x = 0 then\n"
        '    log "zero"\n'
        "else\n"
        '    log "pos"\n'
        "end if\n"
        "set y to 99\n"
    )
    # The trailing statement must be at top level, not nested in the else.
    assert any(
        line == "set y to 99" for line in out.splitlines()
    ), "trailing statement was swallowed into the if/else"
    # if openers and end-if closers must balance.
    opens = sum(1 for ln in out.splitlines() if ln.strip().startswith("if "))
    closes = sum(1 for ln in out.splitlines() if ln.strip() == "end if")
    assert opens == closes, f"{opens} if-opens vs {closes} end-ifs"
    assert recompiles(out)


def test_simple_if_has_no_empty_else():
    out = decompile_snippet("if true then\n    beep\nend if\n")
    assert "else" not in out


# --- references / set -------------------------------------------------------


def test_set_item_of_list():
    out = decompile_snippet("set myList to {1, 2, 3}\nset item 1 of myList to 4\n")
    assert "set item 1 of myList to 4" in out


def test_destructuring_keeps_container():
    out = decompile_snippet("set {p, q, r} to {7, 8, 9}\n")
    assert "of item" not in out  # container must not be the class token
    assert "item 1 of {7, 8, 9}" in out


def test_word_character_paragraph_nouns():
    out = decompile_snippet(
        'set w to word 1 of "hi there"\n'
        'set c to character 2 of "abc"\n'
        'set p to paragraph 1 of "x"\n'
    )
    assert "word 1 of" in out
    assert "character 2 of" in out
    assert "paragraph 1 of" in out


# --- constants & commands ---------------------------------------------------


def test_current_date_is_a_command_not_a_code():
    out = decompile_snippet("set d to current date\n")
    assert "current date" in out
    assert "curd" not in out


def test_pi_constant_not_pipe_mangled():
    out = decompile_snippet("set c to pi\n")
    assert "pi" in out
    assert "|«" not in out  # chevron forms must not be pipe-quoted


def test_application_reference():
    out = decompile_snippet(
        'tell application "Finder" to get name of startup disk\n'
    )
    assert 'application "Finder"' in out
    assert ".app" not in out


# --- handler argument names -------------------------------------------------


def test_typed_argument_name_recovered():
    out = decompile_snippet("on f(x as integer)\n    return x\nend f\n")
    assert "Arguments: x" in out
    assert "123" not in out  # the raw typed-param marker must not leak
    assert "return x" in out


def test_positional_argument_names_recovered():
    out = decompile_snippet("on g(alpha, beta)\n    return alpha\nend g\n")
    assert "Arguments: alpha, beta" in out


def test_patterned_argument_name_recovered():
    out = decompile_snippet("on h({p, q})\n    return p\nend h\n")
    assert "{p, q}" in out


# --- no leaked internal markers ---------------------------------------------


def test_empty_list_literal_renders():
    out = decompile_snippet("set e to {}\nset f to e & {1}\n")
    assert "{}" in out
    import re

    assert not re.search(r"<\d+ b", out), "leaked Pair/raw-bytes repr"


@pytest.mark.parametrize(
    "source",
    [
        "set d to current date\n",
        'set w to word 1 of "hi"\n',
        "on f(x)\n    repeat with i from 2 to x\n        log i\n    end repeat\nend f\n",
    ],
)
def test_no_leaked_markers(source: str):
    import re

    out = decompile_snippet(source)
    assert not re.search(r"<\d+ b", out), "leaked Pair/raw-bytes repr"
    assert "|literal_" not in out, "leaked out-of-range literal placeholder"
    assert "undefined" not in out
