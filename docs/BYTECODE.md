# Bytecode VM (bytecode-vm branch)

This branch adds a **bytecode compiler** and **stack-based VM** alongside the existing tree-walk interpreter.

## Overview

- **Compiler** (`src/compiler.py`): Compiles Keris AST to a linear bytecode (list of `(opcode, arg?)`).
- **VM** (`src/vm.py`): Executes bytecode using a value stack, global scope, and call frames (with closures).
- **Bytecode** (`src/bytecode.py`): Opcode enum and `Chunk` (constants + code).

Scripts run through the VM by default. Use `--tree-walk` to force the original interpreter.

## Opcodes (summary)

- **Stack**: `LOAD_CONST`, `LOAD_VAR`, `STORE_VAR`, `POP`
- **Arithmetic**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `POW`
- **Comparison**: `EQ`, `NE`, `LT`, `LE`, `GT`, `GE`
- **Unary**: `NEG`, `NOT`
- **Control**: `JUMP`, `JUMP_IF_FALSE`, `JUMP_IF_TRUE`
- **Calls**: `CALL`, `RETURN`, `RETURN_NONE`, `MAKE_FUNCTION`
- **Objects**: `GET_ATTR`, `SET_ATTR`, `INDEX`, `INDEX_SET`, `BUILD_LIST`, `BUILD_DICT`, `LEN`
- **Exceptions**: `TRY`, `END_TRY`, `THROW`

## Execution flow

1. Source → **Lexer** → tokens → **Parser** → AST.
2. AST → **Compiler** → Chunk (bytecode + constants).
3. **VM.run(chunk)**: fetch-decode-execute loop; frames for function calls; closures captured at `MAKE_FUNCTION`.

The VM uses the same stdlib and runtime semantics as the tree-walk interpreter. On compile error (e.g. unsupported construct), `run()` falls back to the tree-walk interpreter.
