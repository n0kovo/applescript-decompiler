"""Runtime value classes for objects deserialized from the FAS stream.

Known type indexes (first byte of a typed data block):
    0x01: Constant        0x0B: Constant
    0x02: List            0x0C: LargeFloat
    0x03: Integer         0x0D: RawData
    0x05: Float           0x0F: Actor
    0x07: Integer         0x2E: EventIdentifier
    0x08: Application     0x6C: Comment
    0x0A: ClassIdentifier 0x6E: Value
    0xB1: UnicodeText
"""

import struct
from typing import Any


class Value:
    type: int

    def __repr__(self) -> str:
        return f"<Value type={self.type}>"


class Special(Value):
    """Special constants serialized with type 2 (true / false / nil)."""

    type = 2
    KNOWN_CONSTANTS = {0x7A: "True", 0x79: "False", 0x00: "nil"}

    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        name = Special.KNOWN_CONSTANTS.get(self.value, f"unknown_0x{self.value:x}")
        return f"<Value type=special value={name}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Special) and other.value == self.value


NIL = Special(0)
TRUE = Special(0x7A)
FALSE = Special(0x79)


class Fixnum(Value):
    type = 6

    def __init__(self, value: int) -> None:
        # NB: stored as value * 8 + 6 in size_t format by the runtime.
        self.value = value

    def __repr__(self) -> str:
        return f"<Value type=fixnum value=0x{self.value:x}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Fixnum) and other.value == self.value


class Constant(Fixnum):
    type = 11

    def __repr__(self) -> str:
        return f"<Value type=constant value=0x{self.value:x}>"


class Object(Value):
    """Generic wrapper around another value."""

    type = 0

    def __init__(self, value: Any) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<Value type=object value={self.value!r}>"


class String(Value):
    type = 0  # or 8?

    def __init__(self, value: bytes) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<Value type=string value={self.value!r}>"


class RawData(Value):
    type = 0x0D  # kUASIndexRawData

    def __init__(self, value: bytes) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<Value type=rawdata value={self.value!r}>"


class Binding(Object):
    """One link of a record's key/value binding chain."""

    def __init__(self, a: Any, b: Any, c: Any) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.next: Any = None

    def __repr__(self) -> str:
        return f"<Binding a={self.a!r} b={self.b!r} c={self.c!r} next={self.next!r}>"


class EventIdentifier(Value):
    type = 46

    def __init__(self, a: int, b: int, c: int, d: int, e: int, f: int) -> None:
        self.identifier = (a, b, c, d, e, f)

    def __repr__(self) -> str:
        parts = "-".join(repr(struct.pack(">L", x)) for x in self.identifier)
        return f"<Value type=event_identifier value={parts}>"


class Reference:
    def __init__(self, to: str) -> None:
        self.to = to

    def __repr__(self) -> str:
        return f"<Reference to={self.to}>"


SECOND_ACTOR = Reference("secondActor")


class Pair(Value):
    """Cons cell; FAS lists are serialized as chains of these."""

    type = 4

    def __init__(self, first: Any, second: Any) -> None:
        self.first = first
        self.second = second

    def __repr__(self) -> str:
        return f"<Value type=pair first={self.first!r} second={self.second!r}>"


class EmptyPair(Pair):
    def __init__(self) -> None:
        pass  # the empty terminator carries no fields

    def __repr__(self) -> str:
        return "<Value type=pair empty>"


class Statement:
    """A command block: type info plus the bytecode range it covers."""

    def __init__(self, type_info: int, bytecode_start: int, bytecode_end: int) -> None:
        self.type_info = type_info
        self.bytecode_start = bytecode_start
        self.bytecode_end = bytecode_end
        self.children: list | None = None

    def __repr__(self) -> str:
        return (
            f"<Statement type_info={self.type_info!r}"
            f" bytecode_start={self.bytecode_start!r}"
            f" bytecode_end={self.bytecode_end!r} children={self.children!r}>"
        )


class UnicodeText(Value):
    type = 0xB1

    def __init__(self, text: bytes, style: bytes | None = None) -> None:
        self.text = text
        self.style = style

    def __repr__(self) -> str:
        return f"<UnicodeText text={self.text!r} style={self.style!r}>"


# Value classes by serialized type byte. NB: Object also nominally has type 0,
# but type-0 payloads read from data blocks are plain strings.
VALUE_TYPES: dict[int, type[Value]] = {
    0: String,
    2: Special,
    4: Pair,
    6: Fixnum,
    11: Constant,
    0x0D: RawData,
    46: EventIdentifier,
}


def parse_value(type_index: int, *payload: Any) -> Value:
    cls = VALUE_TYPES.get(type_index)
    if cls is None:
        raise ValueError(f"No value class registered for type {type_index}")
    return cls(*payload)
