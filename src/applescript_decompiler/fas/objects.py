"""Readers for each object type index in the FAS stream.

Every reader takes the load table, the object's reference id, and the inlined
size/payload from the object header, and pushes exactly one value onto the
loader stack. `LOADERS` maps type index to reader; `FasLoadTable` dispatches
through it.
"""

import struct
from typing import TYPE_CHECKING, Any, Callable

from applescript_decompiler.fas.values import (
    NIL,
    SECOND_ACTOR,
    Binding,
    Constant,
    EmptyPair,
    EventIdentifier,
    Fixnum,
    Object,
    Pair,
    Statement,
    String,
    UnicodeText,
    parse_value,
)

if TYPE_CHECKING:
    from applescript_decompiler.fas.loader import FasLoadTable

LoaderFn = Callable[["FasLoadTable", int, int], None]

LOADERS: dict[int, LoaderFn] = {}


def _register(*type_indexes: int) -> Callable[[LoaderFn], LoaderFn]:
    def decorator(fn: LoaderFn) -> LoaderFn:
        for index in type_indexes:
            LOADERS[index] = fn
        return fn

    return decorator


class Symbol:
    def __init__(self, num: int) -> None:
        self.num = num

    def __repr__(self) -> str:
        return f"<Symbol num=0x{self.num:x}>"


class Descriptor:
    """An AppleEvent descriptor embedded in a data block (e.g. an alias)."""

    def __init__(self, type: bytes, content: bytes) -> None:
        self.type = type
        self.content = content

    def __repr__(self) -> str:
        return f"<Descriptor type={self.type!r} content={self.content!r}>"


class RefList:
    """A vector of reference ids, resolved to loaded objects on demand.

    The original implementation builds this inline on the interpreter stack;
    since the stack is discarded after loading, a plain list works here.
    """

    def __init__(self, table: "FasLoadTable", size: int, offset: int) -> None:
        self.table = table
        self.size = size
        self.offset = offset
        self.refs = [0] * size

    def read_refs(self) -> None:
        for i in range(self.offset, self.size):
            self.refs[i] = self.table.loader.read_s16()

    def resolve(self) -> list:
        resolved: list[Any] = [NIL] * self.size
        for i in range(self.offset, self.size):
            self.table.find_object(self.refs[i])
            resolved[i] = self.table.loader.stack.pop()
        return resolved


@_register(1)
def load_symbol(table: "FasLoadTable", ref: int, inlined: int) -> None:
    # TODO: symbol translated when not run only?
    if inlined:
        table.loader.stack.push(Symbol(table.loader.read_u64()))
    else:
        table.loader.stack.push(NIL)


@_register(2)
def load_list(table: "FasLoadTable", ref: int, size: int) -> None:
    if size == 2:
        r = cur = Pair(NIL, EmptyPair())
        while True:
            a = table.loader.read_s16()
            b = table.loader.read_s16()
            table.find_object(a)
            cur.first = table.loader.stack.pop()
            if table.find_object(b, load=False):
                break
            _index, _ref, size = table.read_header()
            if _index != 2:
                table.load_object_body(_ref, _index, size)
                cur.second = table.loader.stack.pop()
            if size != 2:
                break
            cur.second = Pair(NIL, EmptyPair())
            cur = cur.second
            table.register_object(_ref, cur)
        if size:
            raise ValueError("Error -1702: size 0 expected")
        cur.second = EmptyPair()
    else:
        r = EmptyPair()

    table.loader.stack.push(r)


@_register(3)
def load_int(table: "FasLoadTable", ref: int, inlined: int) -> None:
    table.loader.stack.push(Fixnum(inlined))


@_register(4)
@_register(14)
def load_value_block(table: "FasLoadTable", ref: int, size: int) -> None:
    block_type = table.loader.read_u8()
    if size == 0 and block_type == 15:
        table.loader.stack.push(SECOND_ACTOR)
    else:
        ref_list = RefList(table, size + 1, 1)
        ref_list.read_refs()
        resolved = ref_list.resolve()
        resolved[0] = block_type  # slot 0 carries the block-type byte
        table.loader.stack.push(resolved)

    table.register_object(ref, table.loader.stack[-1])


@_register(6)
def load_record(table: "FasLoadTable", ref: int, size: int) -> None:
    if size == 3:
        record = Binding(NIL, NIL, NIL)
        table.loader.stack.push(record)
        table.register_object(ref, record)
        while size == 3:
            a = table.loader.read_s16()
            b = table.loader.read_s16()
            c = table.loader.read_s16()
            table.find_object(a)
            record.a = table.loader.stack.pop()
            table.find_object(b)
            record.b = table.loader.stack.pop()
            if not table.find_object(c, load=False):
                index, next_ref, size = table.read_header()
                if index != 6:
                    table.load_object_body(next_ref, index, size)
                    record.next = table.loader.stack.pop()
                    break
                if size != 3:
                    break
                record.next = Binding(NIL, NIL, NIL)
                record = record.next
            else:
                record.next = table.loader.stack.pop()
                break
        table.register_object(ref, record)
    elif size == 1:
        table.loader.stack.push(Binding(NIL, NIL, NIL))
    else:
        raise ValueError(f"unknown fas record type: {size}")


@_register(7)
def load_long_int(table: "FasLoadTable", ref: int, inlined: int) -> None:
    if inlined != 4:
        raise ValueError("Error -1702: LongInteger size error")
    table.loader.stack.push(table.loader.read_s32())


@_register(8)
def load_float(table: "FasLoadTable", ref: int, inlined: int) -> None:
    if inlined != 8:
        raise ValueError("Error -1702: Float size error")
    table.loader.stack.push(struct.unpack(">d", table.loader.read_raw(8))[0])


@_register(9)
def load_bool(table: "FasLoadTable", ref: int, inlined: int) -> None:
    table.loader.stack.push(bool(inlined))


@_register(10)
def load_code_identifier(table: "FasLoadTable", ref: int, size: int) -> None:
    kind = table.loader.read_u8()

    def size_error(expected: int) -> ValueError:
        return ValueError(
            f"Error -1702: Invalid size on codeId: expected {expected}, value: {size}"
        )

    if kind == 11:
        # The engine internalizes the constant when reading; we don't.
        if size != 8:
            raise size_error(8)
        table.loader.stack.push(Object(Constant(table.loader.read_u64())))
    elif kind in (10, 47):
        # Class identifier?
        if size != 4:
            raise size_error(4)
        table.loader.stack.push(Object(Constant(table.loader.read_u32())))
    elif kind == 46:
        if size != 24:
            raise size_error(24)
        a, b, c, d, e, f = (table.loader.read_u32() for _ in range(6))
        # Yes, not a typo: the serialized order is a-b-c-d-f-e, not a-b-c-d-e-f.
        table.loader.stack.push(Object(EventIdentifier(a, b, c, d, f, e)))


@_register(11)
def load_user_identifier(table: "FasLoadTable", ref: int, size: int) -> None:
    kind = table.loader.read_u8()
    if kind != 48:
        raise ValueError("Error -1702: nope")
    a_len = table.loader.read_u16()
    a = table.loader.read(a_len)
    b_len = table.loader.read_u16()
    b = table.loader.read(b_len)
    if a_len >= 0x100 or b_len >= 0x100:
        raise ValueError("Malformed file")
    value = b if b_len else a
    table.loader.stack.push(value)
    table.loader.user_identifiers[b if b_len else a] = b


@_register(12)
def load_string(table: "FasLoadTable", ref: int, inlined: int) -> None:
    text = bytes(table.loader.read(table.loader.read_u16()))
    style = bytes(table.loader.read(table.loader.read_u16()))
    table.loader.stack.push(Object(UnicodeText(text, style)))


@_register(13)
def load_cmd_block(table: "FasLoadTable", ref: int, size: int) -> None:
    table.loader.read_u8()
    type_info, bytecode_start, bytecode_end = (
        table.loader.read_u16() for _ in range(3)
    )

    ref_list = RefList(table, size + 3, 3)
    ref_list.read_refs()
    statement = Statement(type_info, bytecode_start, bytecode_end)
    table.register_object(ref, statement)
    statement.children = ref_list.resolve()
    table.loader.stack.push(statement)


@_register(15)
def load_data_block(table: "FasLoadTable", ref: int, inlined: int) -> None:
    stack = table.loader.stack
    type_index = table.loader.read_u8()
    if type_index == 8:
        # Application descriptor: 90 bytes of header we don't model, then a
        # 4-char descriptor type and its payload.
        table.loader.read(90)
        desc = Descriptor(table.loader.read(4), table.loader.read(inlined - 94))
        stack.push(desc)
    else:
        stack.push(parse_value(type_index, table.loader.read(inlined)))
    table.register_object(ref, stack[-1])


@_register(16)
def load_pointer_block(table: "FasLoadTable", ref: int, size: int) -> None:
    ref_list = RefList(table, size, 0)
    ref_list.read_refs()
    vector = ref_list.resolve()
    table.register_object(ref, vector)
    table.loader.stack.push(vector)


@_register(17)
def load_untyped_data_block(table: "FasLoadTable", ref: int, size: int) -> None:
    table.loader.stack.push(String(table.loader.read(size)))


@_register(18)
def load_long_data_block(table: "FasLoadTable", ref: int, _inlined: int) -> None:
    type_index = table.loader.read_u8()
    size = table.loader.read_u32()
    table.loader.stack.push(parse_value(type_index, table.loader.read(size)))


@_register(19)
def load_untyped_long_data_block(
    table: "FasLoadTable", ref: int, _inlined: int
) -> None:
    size = table.loader.read_u32()
    table.loader.stack.push(String(table.loader.read(size)))
