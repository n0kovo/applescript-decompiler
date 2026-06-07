"""Command-line interface: `asdec file.scpt`."""

import argparse
import sys
from pathlib import Path

from applescript_decompiler.decompiler import decompile_file


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="asdec",
        description="Decompile a compiled AppleScript (.scpt) file to source.",
    )
    parser.add_argument("file", type=Path, help="compiled AppleScript file")
    args = parser.parse_args()

    if not args.file.is_file():
        parser.error(f"no such file: {args.file}")
    try:
        print(decompile_file(args.file))
    except ValueError as e:
        sys.exit(f"asdec: {e}")


if __name__ == "__main__":
    main()
