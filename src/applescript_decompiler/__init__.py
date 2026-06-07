"""Decompiler for compiled AppleScript (.scpt) files."""

from importlib.metadata import PackageNotFoundError, version

from applescript_decompiler.decompiler import (
    AppleScriptDecompiler,
    decompile_file,
)

try:
    __version__ = version("applescript-decompiler")
except PackageNotFoundError:  # running from an uninstalled source tree
    __version__ = "0.0.0+unknown"

__all__ = ["AppleScriptDecompiler", "decompile_file", "__version__"]
