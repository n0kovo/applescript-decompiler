"""Rendering of FAS runtime values as AppleScript source literals."""

import re
import struct
from typing import Any

from applescript_decompiler.names import (
    COMMAND_NAMES,
    DOUBLE_CC,
    EVENT_NAMES,
    FOUR_CC,
)

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_GLOBAL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]*$")


def make_identifier(raw: str) -> str:
    """Return a valid AppleScript identifier.

    Pipe-quotes the name if it contains spaces or other characters that would
    break bare-identifier parsing (``|foo bar|`` is valid AppleScript).
    """
    s = raw.strip('"').strip("'").strip()
    if not s:
        return "|"  # degenerate
    if _IDENT_RE.match(s):
        return s
    return f"|{s}|"


def clean_global(raw: Any) -> str:
    """Normalize a global/property name literal into an identifier."""
    s = str(raw).strip()
    for q in ('"', "'"):
        if s.startswith(q) and s.endswith(q) and len(s) >= 2:
            s = s[1:-1]
    s = s.strip()
    # Raw chevron forms (`«class pi  »`, `«constant …»`) are already valid
    # AppleScript; pipe-quoting them would turn them into bogus identifiers.
    if s.startswith("«"):
        return s
    if not s or not _GLOBAL_RE.match(s):
        return f"|{s}|"
    return s.rstrip()


def decode_bytes(b: bytes | str) -> str:
    """Decode raw string data and escape it for an AppleScript string literal."""
    if not b:
        return ""
    if isinstance(b, str):
        s = b
    elif b"\x00" in b:
        s = b.decode("utf-16-be", errors="ignore").rstrip("\x00")
    else:
        try:
            s = b.decode("utf-8", errors="ignore")
        except Exception:
            s = b.decode("mac_roman", errors="ignore")
    # Escape backslash and double-quote for valid AppleScript string literals.
    return s.replace("\\", "\\\\").replace('"', '\\"')


def format_arg_name(spec: Any) -> str:
    """Render one handler parameter spec as its source name.

    Handles plain names (`a`), typed parameters (`[123, name, type, default]`
    → the name), and list-pattern parameters (`[4, n, [0, p, q]]` → `{p, q}`).
    """
    if isinstance(spec, list):
        if spec and spec[0] == 123:  # typed parameter
            return format_arg_name(spec[1])
        if len(spec) >= 3 and isinstance(spec[2], list):  # destructuring pattern
            inner = ", ".join(format_arg_name(s) for s in spec[2][1:])
            return "{" + inner + "}"
    return format_value(spec).replace('"', "")


def format_value(val: Any) -> str:
    """Format a value from the literal table as AppleScript source text."""
    if val is None:
        return "null"

    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, bytes):
        return f'"{decode_bytes(val)}"'

    if isinstance(val, list):
        if len(val) == 2:
            return format_value(val[1])
        return "[" + ", ".join(format_value(v) for v in val) + "]"

    if not hasattr(val, "type"):
        return str(val)

    v_type = val.type

    if v_type == 4:  # Pair / cons cell -> AppleScript list (EmptyPair -> {})
        items = []
        node = val
        while hasattr(node, "first") and hasattr(node, "second"):
            items.append(format_value(node.first))
            node = node.second
        return "{" + ", ".join(items) + "}"

    v_content: Any = getattr(
        val, "value", getattr(val, "identifier", getattr(val, "content", b""))
    )

    # Unwrap the loader's nested Descriptors.
    if hasattr(v_content, "content"):
        v_content = v_content.content

    if v_type == 0:  # generic object wrapper
        if hasattr(v_content, "type") or isinstance(v_content, list):
            return format_value(v_content)
        if isinstance(v_content, bytes):
            return f'"{decode_bytes(v_content)}"'
        return f'"{v_content}"' if isinstance(v_content, str) else str(v_content)

    if v_type == 2:  # special constant
        if v_content == 0x7A:
            return "true"
        if v_content == 0x79:
            return "false"
        return "null"

    if v_type == 6:  # fixnum
        return str(v_content)

    if v_type in (11, "constant", b"constant", "type", b"type"):
        try:
            code = int(v_content)
        except (TypeError, ValueError):
            return str(v_content)
        if code >= 2**32:
            # Eight-character enumerator/pseudo-constant (type + value).
            code8 = struct.pack(">Q", code).decode("mac_roman", "replace")
            if code8 in DOUBLE_CC:
                return DOUBLE_CC[code8]
            return f"«constant {code8}»"
        mac_code = struct.pack(">I", code).decode("mac_roman", "replace")
        if mac_code in FOUR_CC:
            return FOUR_CC[mac_code]
        # Raw-chevron form: valid AppleScript syntax for any 4-char code.
        return f"«class {mac_code}»"

    if v_type in (0x0D, "alis", b"alis"):  # alias / application / raw data
        if isinstance(v_content, bytes):
            strs = [
                m.decode("utf-8", "ignore")
                for m in re.findall(rb"[A-Za-z0-9_ \.]{5,}", v_content)
            ]
            # An app descriptor embeds the bundle name; prefer the `.app`
            # entry and render it as an application reference.
            app = next((s for s in strs if s.endswith(".app")), None)
            if app:
                return f'application "{app[:-4]}"'
            if strs:
                return f'alias "{strs[-1]}"'
        return "<alias>"

    if v_type in (46, "event_identifier"):
        code = None
        if isinstance(v_content, tuple) and len(v_content) >= 2:
            c = v_content[1]
            try:
                if isinstance(c, bytes):
                    code = c.decode("mac_roman", "ignore")
                else:
                    code = struct.pack(">I", int(c)).decode("mac_roman")
            except Exception:
                pass
        elif isinstance(v_content, bytes):
            parts = v_content.split(b"-")
            if len(parts) >= 2:
                code = parts[1].decode("mac_roman", "ignore")
        if code:
            code = code.strip() or code
            return COMMAND_NAMES.get(code, EVENT_NAMES.get(code, code))
        return "<EventIdentifier>"

    if v_type == 0xB1:  # styled Unicode text
        text = getattr(val, "text", v_content)
        return f'"{decode_bytes(text)}"'

    return f"<{v_type} {v_content!r}>"
