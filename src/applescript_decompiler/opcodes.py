"""The AppleScript bytecode instruction set.

Everything that knows about the *encoding* of compiled handler code lives
here: the 256-entry opcode name table, which opcodes carry which operand
kinds, and the disassembler that turns raw code bytes into `Instruction`s.
"""

import struct
from typing import Any, NamedTuple

# Opcodes 0x00-0x2B: one name per byte.
_PRIMARY = (
    "Equal",
    "NotEqual",
    "GreaterThan",
    "GreaterThanOrEqual",
    "LessThan",
    "LessThanOrEqual",
    "StartsWith",
    "EndsWith",
    "Contains",
    "And",
    "Or",
    "Not",
    "MessageSend",
    "MakeList",
    "MakeRecord",
    "Return",
    "Continue",
    "ObjectAliasQuote",
    "Tell",
    "Consider",
    "ErrorHandler",
    "Error",
    "Exit",
    "LinkRepeat",
    "RepeatNTimes",
    "RepeatWhile",
    "RepeatUntil",
    "RepeatInCollection",
    "RepeatInRange",
    "TestIf",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Quotient",
    "Remainder",
    "Power",
    "Concatenate",
    "Coerce",
    "Negate",
    "GetData",
    "PushMe",
    "PushIt",
    "PositionalMessageSend",
)

# Opcodes 0x45-0x76.
_SECONDARY = (
    "GetData",
    "SetData",
    "CopyData",
    "Undefined",
    "Undefined",
    "PositionalContinue",
    "DefineActor",
    "DefineProcedure",
    "DefineClosure",
    "DefineProperty",
    "StoreResult",
    "GetResult",
    "Clone",
    "Of",
    "EndDefineActor",
    "EndOf",
    "EndTell",
    "EndConsider",
    "EndErrorHandler",
    "HandleError",
    "Jump",
    "Pop",
    "Dup",
    "GCSwap",
    "PushVariableExtended",
    "PopVariableExtended",
    "PushGlobalExtended",
    "PopGlobalExtended",
    "PushLiteralExtended",
    "PushParentVariable",
    "PopParentVariable",
    "PushNext",
    "PushTrue",
    "PushFalse",
    "PushEmpty",
    "PushUndefined",
    "PushMinus1",
    "Push0",
    "Push1",
    "Push2",
    "Push3",
    "BeginTimeout",
    "EndTimeout",
    "BeginTransaction",
    "EndTransaction",
    "Undefined",
    "Undefined",
    "Undefined",
    "MatchLiteral",
    "MakeVector",
)


def _build_opcode_table() -> tuple[str, ...]:
    ops: list[str] = list(_PRIMARY)  # 0x00-0x2B
    ops += ["MakeObjectAlias"] * 12  # 0x2C-0x37: object-specifier forms
    ops += ["MakeComp"] * 13  #         0x38-0x44: comparison-specifier forms
    ops += list(_SECONDARY)  #          0x45-0x76
    ops += ["Undefined"] * 41  #        0x77-0x9F: unassigned
    ops += ["PushVariable"] * 16  #     0xA0-0xAF: low nibble = variable index
    ops += ["PopVariable"] * 16  #      0xB0-0xBF
    ops += ["PushGlobal"] * 16  #       0xC0-0xCF
    ops += ["PopGlobal"] * 16  #        0xD0-0xDF
    ops += ["PushLiteral"] * 32  #      0xE0-0xFF
    assert len(ops) == 256
    return tuple(ops)


OPCODES: tuple[str, ...] = _build_opcode_table()


# Object-specifier form, keyed by MakeObjectAlias opcode byte. MakeComp bytes
# (0x38-0x44) deliberately have no entry and fall back to "Unknown".
REFERENCE_FORMS: dict[int, str] = {
    0x2C: "GetProperty",
    0x2D: "GetEvery",
    0x2E: "GetSome",
    0x2F: "GetIndexed",
    0x30: "GetKeyFrom",
    0x31: "GetNamed",
    0x32: "GetRange",
    0x33: "GetRelative",
    0x34: "GetFilter",
    0x35: "GetPositionBeginning",
    0x36: "GetPositionEnd",
    0x37: "GetMiddle",
}


# Operand encodings, by opcode name.
# One signed word, relative to the position after the operand (jump target):
JUMP_TARGET_OPS = frozenset(
    {
        "Jump",
        "TestIf",
        "And",
        "Or",
        "ErrorHandler",
        "EndErrorHandler",
        "LinkRepeat",
    }
)
# One signed word, used verbatim (literal/global/variable index, count, ...):
WORD_OPERAND_OPS = frozenset(
    {
        "MessageSend",
        "PositionalMessageSend",
        "Tell",
        "RepeatInRange",
        "PushGlobalExtended",
        "PopGlobalExtended",
        "PopVariableExtended",
        "PushVariableExtended",
        "DefineActor",
        "PushLiteralExtended",
    }
)
# Index packed into the low nibble of the opcode byte itself:
NIBBLE_OPERAND_OPS = frozenset(
    {"PushLiteral", "PushGlobal", "PopGlobal", "PopVariable", "PushVariable"}
)
# Two signed words:
DOUBLE_WORD_OPERAND_OPS = frozenset(
    {"HandleError", "PushParentVariable", "PopParentVariable"}
)


class Instruction(NamedTuple):
    pos: int
    op: str
    # Shape depends on the opcode's operand kind: int for single operands and
    # jump targets, (int, int) for double-word operands, None otherwise.
    arg: Any
    next_pos: int
    raw_byte: int


def disassemble(code: bytes) -> list[Instruction]:
    """Decode handler bytecode into a flat instruction list.

    Jump targets are resolved to absolute code offsets.
    """
    instructions: list[Instruction] = []
    pos = 0
    while pos < len(code):
        start_pos = pos
        byte = code[pos]
        pos += 1
        op = OPCODES[byte]

        def read_word() -> int:
            nonlocal pos
            word = struct.unpack(">H", code[pos : pos + 2])[0]
            pos += 2
            return word - 0x10000 if word & 0x8000 else word

        arg: int | tuple[int, int] | None = None
        if op in JUMP_TARGET_OPS:
            arg = pos + read_word()
        elif op in WORD_OPERAND_OPS:
            arg = read_word()
        elif op in NIBBLE_OPERAND_OPS:
            arg = byte & 0xF
        elif op in DOUBLE_WORD_OPERAND_OPS:
            arg = (read_word(), read_word())

        instructions.append(Instruction(start_pos, op, arg, pos, byte))
    return instructions
