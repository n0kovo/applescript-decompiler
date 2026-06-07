"""Reader for the FAS ('Fasd UAS') serialization format of compiled AppleScript.

Port of FasLoad from the original AppleScript runtime. `Loader` wraps the
input stream (TBasicInputStream in the binary); `FasLoadTable` owns the
reference table and drives object loading via the readers in
`applescript_decompiler.fas.objects`.
"""

import struct
from pathlib import Path
from typing import Any, BinaryIO

from applescript_decompiler.fas.objects import LOADERS
from applescript_decompiler.fas.values import NIL


class Stack(list):
    def push(self, item: Any) -> None:
        self.append(item)


class Loader:
    """Byte-level reader for a FAS stream.

    The original implementation keeps this state in globals; instances keep
    separate files separate.

    Usage::

        script = Loader().load("compiled.scpt")
    """

    def __init__(self) -> None:
        self.f: BinaryIO | None = None
        self.stack = Stack()
        self.big_endian = True
        # Filled by user-identifier objects (type 11) during loading.
        self.user_identifiers: dict[bytes, bytes] = {}

    def load(self, path: str | Path) -> Any:
        """Load a compiled script and return its root object."""
        with Path(path).open("rb") as f:
            self.f = f
            self.stack = Stack()
            table = FasLoadTable(self)
            table.load_object(0)
            return self.stack.pop()

    def read(self, size: int) -> bytes:
        assert self.f is not None
        return self.f.read(size)

    def seek(self, offset: int, whence: int = 1) -> None:
        assert self.f is not None
        self.f.seek(offset, whence)

    def tell(self) -> int:
        assert self.f is not None
        return self.f.tell()

    def read_raw(self, size: int) -> bytes:
        """Read `size` bytes in stream order (reversed for little-endian files)."""
        data = self.read(size)
        return data if self.big_endian else data[::-1]

    def read_u8(self) -> int:
        return struct.unpack(">B", self.read_raw(1))[0]

    def read_u16(self) -> int:
        return struct.unpack(">H", self.read_raw(2))[0]

    def read_s16(self) -> int:
        return struct.unpack(">h", self.read_raw(2))[0]

    def read_u32(self) -> int:
        return struct.unpack(">L", self.read_raw(4))[0]

    def read_s32(self) -> int:
        return struct.unpack(">l", self.read_raw(4))[0]

    def read_u64(self) -> int:
        return struct.unpack(">Q", self.read_raw(8))[0]


class FasLoadTable:
    """Reference table and object dispatcher for one FAS stream."""

    MAX_REF_ERRORS = 200

    def __init__(self, loader: Loader) -> None:
        self.loader = loader
        self.depth = 0

        # Header state carried over between load_object calls when a RefID
        # mismatch forces a retry (static fields in the original binary).
        self.reuse_header = False
        self.index = 0
        self.ref = 0
        self.inlined = 0
        self.ref_errors: list[str] = []

        # Scripts may be prefixed with a shebang line; skip it.
        if loader.read(2) == b"#!":
            while loader.read(1) not in (b"\n", b""):
                pass
        else:
            loader.seek(-2)

        if loader.read_raw(4) != b"Fasd":
            raise ValueError("Not a compiled AppleScript: missing 'Fasd' magic")
        if loader.read_raw(4) != b"UAS ":
            raise ValueError("Not a compiled AppleScript: missing 'UAS ' magic")

        version = loader.read_raw(4)
        if version >= b"1.10":
            version = loader.read_raw(4)
        if version <= b"0.97":
            raise ValueError(f"File version too low: {version!r}")
        if version >= b"1.11":
            raise ValueError(f"File version too high: {version!r}")
        self.version = version

        self.ref_table: list[tuple[Any, Any]] = [(NIL, 2)] * 32

    def load_object(self, num: int) -> None:
        pos = self.loader.tell()
        if self.reuse_header:
            self.reuse_header = False
        else:
            self.index, self.ref, self.inlined = self.read_header()

        self.depth += 1
        if self.ref == num:
            self.load_object_body(num, self.index, self.inlined)
        else:
            self.reuse_header = True
            self.ref_errors.append(
                f"{pos:08x}: RefID mismatch. Expected {num}, found {self.ref}."
            )
            if len(self.ref_errors) >= self.MAX_REF_ERRORS:
                raise ValueError(
                    f"AppleScript: Too many RefID errors (>{self.MAX_REF_ERRORS})."
                )
            self.loader.stack.push(NIL)
        self.depth -= 1

    def find_object(self, num: int, load: bool = True) -> bool | None:
        """Push the object for reference `num`, loading it if necessary.

        With load=False, only consults the reference table and returns whether
        the object was found (and pushed).
        """
        # Ref 0 denotes NIL explicitly in the reference stream (the initial
        # refTable slot is NIL and is never registered), so short-circuit
        # rather than trying to follow a stream offset that isn't ours.
        if load and num == 0:
            self.loader.stack.push(NIL)
            return None
        if not load:
            if num >= 0:
                exists, result = self.look_up_ref(num)
                if exists:
                    self.loader.stack.push(result)
                    return True
            return False
        if num < 0:
            self.load_object(num)
        else:
            exists, result = self.look_up_ref(num)
            if exists:
                self.loader.stack.push(result)
            else:
                self.load_object(num)
        return None

    def read_header(self) -> tuple[int, int, int]:
        """Read an object header: (type index, reference id, inlined size)."""
        index = self.loader.read_u8()
        ref = self.loader.read_s16()
        inlined = self.loader.read_u16()
        return index, ref, inlined

    def load_object_body(self, ref: int, index: int, inlined: int) -> None:
        reader = LOADERS.get(index)
        if reader is None:
            raise ValueError(f"Error -1702: unknown object type: {index}!")

        if index in (2, 7, 10, 11):
            ref = 0  # not used in binary

        stack = self.loader.stack
        prev_len = len(stack)
        reader(self, ref, inlined)
        assert len(stack) == prev_len + 1, reader.__name__  # little check

    def look_up_ref(self, num: int) -> tuple[bool, Any]:
        if num >= len(self.ref_table):
            return False, None
        value, slot_type = self.ref_table[num]
        return slot_type in (14, 30), value

    def register_object(self, ref: int, value: Any) -> None:
        if ref < 0:
            return
        if ref >= len(self.ref_table):
            self.ref_table += [(NIL, 0)] * (ref - len(self.ref_table) + 1)
        self.ref_table[ref] = (value, 30)
