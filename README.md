# applescript-decompiler

Decompiler for compiled AppleScript (`.scpt`) files. Parses the `Fasd UAS`
binary format and reconstructs readable AppleScript source from the bytecode —
including handlers, control flow (`if`/`repeat`/`try`/`tell` blocks), object
specifiers, and literals.

Built on (and a significant extension of)
[Jinmo/applescript-disassembler](https://github.com/Jinmo/applescript-disassembler).

## Installation

```sh
pip install applescript-decompiler
```

Or from a checkout:

```sh
pip install .
```

Requires Python 3.11+.

## Usage

### Command line

```sh
asdec compiled.scpt
```

```
========================================
Function: areaOfCircle
Arguments: none
========================================
if (not ({real, integer} contains class of var_0)) then
    error "Radius must be number."
else
end if
return ((var_0 * var_0) * |«class pi  »|)
```

### As a library

```python
from applescript_decompiler import decompile_file

source = decompile_file("compiled.scpt")
print(source)
```

## How it works

- `applescript_decompiler.fas` parses the `Fasd UAS` serialization format
  (a port of the `FasLoad` routine from the original AppleScript runtime):
  reference tables, value blocks, records, literals, and embedded bytecode.
- `applescript_decompiler.opcodes` knows the 256-entry instruction set and
  disassembles handler bytecode.
- `applescript_decompiler.decompiler` interprets each handler's instructions
  against a simulated value stack, emitting AppleScript statements as it goes.

## Limitations

Decompilation reconstructs source from bytecode, and some information is
discarded at compile time or only meaningful with an application's
terminology dictionary. Expect:

- **Local variable names** are not stored in compiled scripts, so they appear
  as `var_0`, `var_1`, … Handler argument names (including typed and
  destructuring patterns), globals, and properties *are* recovered.
- **Labeled parameters of application/scripting-addition commands** are not
  reconstructed. A command's name is recovered (e.g. `make`, `display
  dialog`), but its arguments are rendered positionally rather than with their
  `with properties` / `given` labels.
- **`use` statements, `property` initializers, and `script` object structure**
  (inheritance, nesting) are not reconstructed; only the handlers they contain
  are emitted.
- **Output is per-handler**, framed with `=`/`Function:`/`Arguments:` headers,
  not a single recompilable file. The handler bodies are valid AppleScript for
  most inputs; pathological scripts can still leave a stray marker.

A trailing `return` of the last expression is emitted for every handler (the
compiler stores it as the result), which is harmless but not always present in
the original.

## Development

```sh
uv sync          # install dev dependencies
uv run pytest    # run the test suite
```

The test suite compiles a corpus of AppleScript sources with `osacompile`
(macOS only) and verifies that decompilation round-trips: output must contain
no unknown markers, balance its blocks, recompile cleanly, and leave no opcode
unhandled.

## License

MIT — see [LICENSE](LICENSE). Original disassembler © 2017
[Jinmo](https://github.com/Jinmo); decompiler extension © 2026
[n0kovo](https://github.com/n0kovo).
