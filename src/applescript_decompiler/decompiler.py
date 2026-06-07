"""Reconstruction of AppleScript source from compiled handler bytecode.

`AppleScriptDecompiler` interprets one handler's instruction stream against a
simulated value stack, emitting AppleScript statements as side effects of the
stateful opcodes. `decompile_file` drives it over every handler in a .scpt.
"""

from collections import Counter
from pathlib import Path

from applescript_decompiler.fas.loader import Loader
from applescript_decompiler.literals import (
    clean_global,
    format_arg_name,
    format_value,
    make_identifier,
)
from applescript_decompiler.opcodes import REFERENCE_FORMS, Instruction, disassemble

# Handler data is a value block whose slot 0 is the block-type byte, shifting
# every field up by one.
NAME_INDEX = 1
ARGS_INDEX = 3
LITERALS_INDEX = 6
CODE_INDEX = 7

# Binary operators, by opcode name.
BIN_OPS: dict[str, str] = {
    "Add": "+",
    "Subtract": "-",
    "Multiply": "*",
    "Divide": "/",
    "Quotient": "div",
    "Remainder": "mod",
    "Power": "^",
    "Equal": "=",
    "NotEqual": "≠",
    "LessThan": "<",
    "GreaterThan": ">",
    "LessThanOrEqual": "≤",
    "GreaterThanOrEqual": "≥",
    "Concatenate": "&",
    "Contains": "contains",
    "StartsWith": "starts with",
    "EndsWith": "ends with",
}


# Module-level opcode coverage tracking. Tests read and reset these.
OPCODE_COUNTS: Counter[str] = Counter()
UNHANDLED: Counter[str] = Counter()


def reset_coverage() -> None:
    OPCODE_COUNTS.clear()
    UNHANDLED.clear()


def _rewrite_loop_header(statements: list[tuple[int, str]], new_header: str) -> None:
    """Overwrite the most recent `repeat` placeholder emitted by LinkRepeat."""
    for i in range(len(statements) - 1, -1, -1):
        indent, text = statements[i]
        if text == "repeat":
            statements[i] = (indent, new_header)
            return
    # Fallback: no placeholder found, just append.
    statements.append((0, new_header))


class AppleScriptDecompiler:
    """Decompiles a single handler (value block) into AppleScript statements."""

    def __init__(self, handler_data: list) -> None:
        self.literals: list = handler_data[LITERALS_INDEX]

        args = handler_data[ARGS_INDEX]
        if isinstance(args, list) and len(args) >= 3 and isinstance(args[2], list):
            self.arg_names = [format_arg_name(a) for a in args[2][1:]]
        else:
            self.arg_names = []

        self.name = format_value(handler_data[NAME_INDEX]).replace('"', "")
        if self.name == "oapp":
            self.name = "run"  # AppleEvent for Open Application (Main Script)

        self.code = bytes(handler_data[CODE_INDEX].value)
        self.instructions: list[Instruction] = []
        self.statements: list[tuple[int, str]] = []

    def _get_literal(self, idx: int) -> str:
        if idx < 0 or idx >= len(self.literals):
            return f"|literal_{idx}|"
        return format_value(self.literals[idx])

    def _get_variable(self, idx: int) -> str:
        if idx < len(self.arg_names):
            return self.arg_names[idx]
        return f"var_{idx}"

    def _is_command(self, idx: int) -> bool:
        """Whether literal `idx` is an AppleEvent verb (a command, not a
        handler name). Commands render as `verb args`, handlers as `name(args)`.
        """
        if not 0 <= idx < len(self.literals):
            return False
        lit = self.literals[idx]
        inner = getattr(lit, "value", lit)
        return getattr(inner, "type", None) == 46  # EventIdentifier

    def parse_to_ir(self) -> None:
        self.instructions = disassemble(self.code)

    def decompile(self) -> None:
        stack: list[str] = []
        indent = 0
        blocks: dict[int, str] = {}  # code offset -> block kind to close there
        result_reg = "undefined"
        loop_stack: list[str] = []  # header text pushed when a repeat opens
        # Open if/else-if blocks. Each: else target, end target (set when the
        # then-branch's trailing jump is seen), whether `else` was emitted, and
        # the index of the emitted `else` line (to drop empty else bodies).
        # Chained else-ifs nest and share one end target, so several frames can
        # close at the same offset.
        if_frames: list[dict] = []
        # Block-stack used as a safety net: whenever a structural End* op fires
        # while an earlier block is still open, close the stragglers in reverse.
        block_stack: list[str] = []

        def pop() -> str:
            return stack.pop() if stack else "missing value"

        def peek() -> str:
            return stack[-1] if stack else "missing value"

        def emit(text: str) -> None:
            self.statements.append((indent, text))

        def close_until(kind: str) -> None:
            """Pop the block stack until `kind` is closed, emitting `end X`
            for any intermediates that never got an explicit end.
            """
            nonlocal indent
            while block_stack:
                top = block_stack.pop()
                indent -= 1
                emit(f"end {top}")
                if top == kind:
                    return
            # kind wasn't on the stack; emit a bare end for caller safety.
            emit(f"end {kind}")

        for ins in self.instructions:
            pos, op, arg = ins.pos, ins.op, ins.arg

            OPCODE_COUNTS[op] += 1

            # Resolve if/else-if blocks that merge at this offset. Several
            # frames can close here (chained else-ifs share one end target).
            while if_frames:
                top = if_frames[-1]
                if top["end"] is None:
                    # No trailing jump → the false-branch target is the end.
                    if pos == top["else"]:
                        indent -= 1
                        emit("end if")
                        if_frames.pop()
                        continue
                    break
                if not top["else_done"] and pos == top["else"]:
                    indent -= 1
                    emit("else")
                    indent += 1
                    top["else_done"] = True
                    top["else_idx"] = len(self.statements) - 1
                    break
                if pos == top["end"]:
                    # Drop an else whose body turned out empty (the compiler
                    # emits a bare undefined result on the false path).
                    if top["else_idx"] == len(self.statements) - 1:
                        self.statements.pop()
                    indent -= 1
                    emit("end if")
                    if_frames.pop()
                    continue
                break

            if pos in blocks:
                block_type = blocks.pop(pos)
                if block_type == "try":
                    indent -= 1
                    emit("on error")
                    indent += 1
                elif block_type == "error":
                    indent -= 1
                    emit("end try")
                    if block_stack and block_stack[-1] == "try":
                        block_stack.pop()
                elif block_type == "repeat":
                    indent -= 1
                    emit("end repeat")
                    if loop_stack:
                        loop_stack.pop()
                else:
                    indent -= 1
                    emit(f"end {block_type}")

            # --- PUSH EXPRESSIONS ---
            if op.startswith("PushLiteral"):
                stack.append(self._get_literal(arg))
            elif op in ("Push0", "Push1", "Push2", "Push3"):
                stack.append(op[-1])
            elif op == "PushMinus1":
                stack.append("-1")
            elif op == "PushTrue":
                stack.append("true")
            elif op == "PushFalse":
                stack.append("false")
            elif op == "PushUndefined":
                stack.append("undefined")
            elif op == "PushIt":
                stack.append("it")
            elif op == "PushMe":
                stack.append("me")
            elif op.startswith("PushGlobal"):
                stack.append(clean_global(self._get_literal(arg)))
            elif op.startswith("PushVariable"):
                stack.append(self._get_variable(arg))
            elif op == "PushParentVariable":
                a, b = arg if isinstance(arg, tuple) else (arg, 0)
                stack.append(f"|parent_var_{a}_{b}|")

            # --- ASSIGNMENTS & STATE ---
            elif op.startswith("PopGlobal"):
                emit(f"set {clean_global(self._get_literal(arg))} to {peek()}")
            elif op.startswith("PopVariable"):
                emit(f"set {self._get_variable(arg)} to {peek()}")
            elif op == "PopParentVariable":
                a, b = arg if isinstance(arg, tuple) else (arg, 0)
                emit(f"set |parent_var_{a}_{b}| to {peek()}")
            elif op == "StoreResult":
                result_reg = pop()
            elif op == "GetResult":
                stack.append(result_reg)
            elif op == "SetData":
                # Stack before (bottom -> top): value, target.
                target = pop()
                val = pop()
                emit(f"set {target} to {val}")
            elif op == "CopyData":
                target = pop()
                val = pop()
                emit(f"copy {val} to {target}")
            elif op == "GetData":
                pass  # no-op: value already on stack

            # --- MATH / LOGIC ---
            elif op in BIN_OPS:
                right, left = pop(), pop()
                stack.append(f"({left} {BIN_OPS[op]} {right})")
            elif op == "And":
                # Short-circuit: runtime jumps past right-operand eval if left
                # is false. Best-effort: binary when both operands are present.
                if len(stack) >= 2:
                    right, left = pop(), pop()
                    stack.append(f"({left} and {right})")
            elif op == "Or":
                if len(stack) >= 2:
                    right, left = pop(), pop()
                    stack.append(f"({left} or {right})")
            elif op == "Not":
                stack.append(f"(not {pop()})")
            elif op == "Negate":
                stack.append(f"(-{pop()})")
            elif op == "Coerce":
                # Target type is on top of stack (pushed as literal beforehand).
                target = pop()
                val = pop()
                stack.append(f"({val} as {target.strip(chr(34))})")
            elif op == "Of":
                container = pop()
                prop = pop()
                stack.append(f"({prop} of {container})")

            # --- CONSTRUCTORS ---
            # Count is pushed immediately before these ops; pop it, then pop N.
            elif op in ("MakeList", "MakeVector"):
                try:
                    n = int(pop())
                except ValueError:
                    n = 0
                items = [pop() for _ in range(n)][::-1]
                stack.append("{" + ", ".join(items) + "}")
            elif op == "MakeRecord":
                try:
                    n = int(pop()) // 2
                except ValueError:
                    n = 0
                pairs = []
                for _ in range(n):
                    v = pop()
                    k = pop()
                    pairs.insert(0, f"{make_identifier(k)}:{v}")
                stack.append("{" + ", ".join(pairs) + "}")

            # --- CONTROL FLOW ---
            elif op == "TestIf":
                emit(f"if {pop()} then")
                indent += 1
                if_frames.append(
                    {"else": arg, "end": None, "else_done": False, "else_idx": -1}
                )
            elif op == "Jump":
                if arg <= pos:  # backward jump: loop end
                    if loop_stack:
                        loop_stack.pop()
                        indent -= 1
                    emit("end repeat")
                else:
                    # Forward jump ending an if/else-if then-branch: record the
                    # construct's end target on the matching open if-frame.
                    for frame in reversed(if_frames):
                        if frame["end"] is None and frame["else"] == ins.next_pos:
                            frame["end"] = arg
                            break
                    else:
                        emit(f"-- jump 0x{arg:x}")
            elif op == "RepeatNTimes":
                step = pop()
                start = pop()
                end = pop()
                if start == "1" and step in ("undefined", "1"):
                    header = f"repeat {end} times"
                else:
                    header = f"repeat with i from {start} to {end}"
                _rewrite_loop_header(self.statements, header)
            elif op == "RepeatWhile":
                cond = pop()
                pop()
                _rewrite_loop_header(self.statements, f"repeat while {cond}")
            elif op == "RepeatUntil":
                cond = pop()
                pop()
                _rewrite_loop_header(self.statements, f"repeat until {cond}")
            elif op == "RepeatInCollection":
                # Stack (top -> bottom): sentinel, 1, count-expression, collection.
                # The compiler emits `count of collection` to drive iteration;
                # the original collection sits beneath it.
                pop()  # undefined sentinel
                pop()  # start index (1)
                pop()  # count expression
                coll = pop()
                _rewrite_loop_header(self.statements, f"repeat with x in {coll}")
            elif op == "RepeatInRange":
                # Stack (top -> bottom): sentinel, step, end, start.
                # arg holds the loop variable's index.
                pop()  # undefined sentinel
                step = pop()
                end_v = pop()
                start_v = pop()
                var = self._get_variable(arg) if isinstance(arg, int) else "i"
                header = f"repeat with {var} from {start_v} to {end_v}"
                if step not in ("undefined", "1"):
                    header += f" by {step}"
                _rewrite_loop_header(self.statements, header)
            elif op == "LinkRepeat":
                # Opens a loop. For naked `repeat ... end repeat` this is the
                # only header. For typed variants (RepeatNTimes/While/Until/
                # InCollection/InRange), a later op overwrites the placeholder.
                emit("repeat")
                indent += 1
                loop_stack.append("repeat")
            elif op == "ErrorHandler":
                emit("try")
                indent += 1
                blocks[arg] = "try"
                block_stack.append("try")
            elif op == "EndErrorHandler":
                blocks[arg] = "error"
            elif op == "Error":
                msg = pop() if stack else '""'
                emit(f"error {msg}")
            elif op == "HandleError":
                pass  # catch-site marker; on-error clause already emitted
            elif op == "Tell":
                emit(f"tell {pop()}")
                indent += 1
                block_stack.append("tell")
            elif op == "EndTell":
                close_until("tell")
            elif op == "Consider":
                emit("considering case")
                indent += 1
                block_stack.append("considering")
            elif op == "EndConsider":
                close_until("considering")
            elif op == "BeginTimeout":
                secs = pop() if stack else "60"
                emit(f"with timeout of {secs} seconds")
                indent += 1
                block_stack.append("timeout")
            elif op == "EndTimeout":
                close_until("timeout")
            elif op == "BeginTransaction":
                emit("with transaction")
                indent += 1
                block_stack.append("transaction")
            elif op == "EndTransaction":
                close_until("transaction")
            elif op == "Return":
                ret_val = pop()
                if ret_val == "<empty_stack>":
                    continue
                if not (
                    self.statements and self.statements[-1][1].startswith("return ")
                ):
                    emit(f"return {ret_val}")
            elif op == "Exit":
                emit("exit repeat")
            elif op in ("Continue", "PositionalContinue"):
                # AppleScript `continue` must be followed by a handler name
                # (delegates to parent). Without that info, emit as a comment.
                emit("-- continue")

            # --- MESSAGING & FUNCTION CALLS ---
            elif op in ("MessageSend", "PositionalMessageSend"):
                func_name = self._get_literal(arg).replace('"', "")
                try:
                    num_args = int(pop())
                except ValueError:
                    num_args = 0
                args_list = []
                for _ in range(num_args):
                    args_list.insert(0, pop() if stack else "missing value")
                target = pop() if stack else None
                if self._is_command(arg):
                    # AppleEvent / scripting-addition command: render as
                    # `verb arg1 arg2` rather than a parenthesized handler call.
                    # Parameter labels aren't recovered, so positional args are
                    # space-joined.
                    call = func_name
                    if args_list:
                        call += " " + " ".join(args_list)
                else:
                    call = f"{func_name}({', '.join(args_list)})"
                if target is None or target in ("me", "it", "<empty_stack>"):
                    stack.append(call)
                else:
                    stack.append(f"({call} of {target})")

            # --- DEFINES (nested handlers / properties / closures) ---
            elif op in ("DefineProcedure", "DefineClosure", "DefineActor"):
                emit(f"-- {op}")
            elif op == "DefineProperty":
                val = pop() if stack else '""'
                emit(f"property anon : {val}")
            elif op in ("EndDefineActor", "EndOf"):
                pass

            # --- STACK BOOKKEEPING ---
            elif op == "Pop":
                if stack:
                    stack.pop()
            elif op == "Dup":
                val = pop()
                stack.extend([val, val])
            elif op == "GCSwap":
                if len(stack) >= 2:
                    stack[-1], stack[-2] = stack[-2], stack[-1]
            elif op == "Clone":
                if stack:
                    stack.append(stack[-1])
            elif op == "PushEmpty":
                stack.append('""')
            elif op == "PushNext":
                stack.append("(current application)")
            elif op in ("MatchLiteral", "ObjectAliasQuote"):
                pass

            elif op in ("MakeObjectAlias", "MakeComp"):
                self._emit_reference(stack, ins)

            else:
                UNHANDLED[op] += 1

        # Close any unterminated if/else-if blocks, then any unterminated
        # structural blocks (tell / considering / timeout / transaction / try),
        # so the output stays syntactically valid.
        while if_frames:
            if_frames.pop()
            indent -= 1
            emit("end if")
        while block_stack:
            top = block_stack.pop()
            indent -= 1
            emit(f"end {top}")
        while indent > 0:
            indent -= 1
            emit("-- implicit block close")

    @staticmethod
    def _emit_reference(stack: list[str], ins: Instruction) -> None:
        """Push an object-specifier expression (`item 3 of x`, `name of y`, ...)."""

        def pop() -> str:
            return stack.pop() if stack else "missing value"

        kind = REFERENCE_FORMS.get(ins.raw_byte, "Unknown")
        quote = chr(34)

        def noun() -> str:
            """Pop the element-class token and return its source-level noun.

            Element specifiers (`word 2 of x`, `every paragraph of y`, ...)
            push the element class just above the container. Unknown classes
            fall back to `item`.
            """
            token = pop().strip(quote)
            return token if token and not token.startswith("«") else "item"

        if kind == "GetProperty":
            # Stack: container, property-name.
            prop = pop()
            if stack:
                container = pop()
                p = prop.strip(quote)
                stack.append(f"{p} of {container}" if p else container)
            else:
                # Property access on an implicit container.
                stack.append(prop.strip(quote))
        elif kind == "GetIndexed":
            # Stack: container, element-class, index.
            idx = pop()
            element = noun()
            container = pop()
            stack.append(f"{element} {idx} of {container}")
        elif kind in ("GetNamed", "GetKeyFrom"):
            name = pop()
            container = pop()
            stack.append(f"{name.strip(quote)} of {container}")
        elif kind == "GetEvery":
            element = noun()
            stack.append(f"every {element} of {pop()}")
        elif kind == "GetSome":
            element = noun()
            stack.append(f"some {element} of {pop()}")
        elif kind == "GetRange":
            # Stack: container, element-class, start, end.
            end_i = pop()
            start_i = pop()
            element = noun()
            container = pop()
            stack.append(f"{element}s {start_i} thru {end_i} of {container}")
        elif kind == "GetMiddle":
            element = noun()
            stack.append(f"middle {element} of {pop()}")
        elif kind == "GetPositionBeginning":
            stack.append(f"beginning of {pop()}")
        elif kind == "GetPositionEnd":
            stack.append(f"end of {pop()}")
        elif kind == "GetRelative":
            ref = pop()
            container = pop()
            stack.append(f"{ref} of {container}")
        elif kind == "GetFilter":
            cond = pop()
            container = pop()
            stack.append(f"{container} whose {cond}")
        else:
            stack.append(f"({kind} of {pop()})")

    def render(self) -> str:
        lines = [
            "",
            "=" * 40,
            f"Function: {self.name}",
            f"Arguments: {', '.join(self.arg_names) if self.arg_names else 'none'}",
            "=" * 40,
        ]
        for indent, text in self.statements:
            lines.append("    " * indent + text)
        lines.append("")
        return "\n".join(lines)


def decompile_file(path: str | Path) -> str:
    """Decompile a .scpt file and return the full source as a string.

    Does not reset coverage counters; callers that want a fresh coverage
    snapshot should call reset_coverage() first.
    """
    script = Loader().load(path)
    handlers = script[-1]
    chunks = []
    for handler_data in handlers[2:]:
        if isinstance(handler_data, list) and len(handler_data) > CODE_INDEX:
            d = AppleScriptDecompiler(handler_data)
            d.parse_to_ir()
            d.decompile()
            chunks.append(d.render())
    return "\n".join(chunks)
