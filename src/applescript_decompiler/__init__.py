"""Decompiler for compiled AppleScript (.scpt) files."""

from applescript_decompiler.decompiler import (
    AppleScriptDecompiler,
    decompile_file,
)

__all__ = ["AppleScriptDecompiler", "decompile_file"]
__version__ = "1.0.0"
