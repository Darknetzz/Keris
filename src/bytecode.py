"""Bytecode format and opcodes for the Keris VM."""

from enum import IntEnum
from typing import Any, List, Tuple, Union


class Op(IntEnum):
    """Bytecode opcodes. Instructions are (Op, arg?) with arg optional."""
    # Stack / constants
    LOAD_CONST = 1   # arg: index into constants
    LOAD_VAR = 2     # arg: name (str)
    STORE_VAR = 3    # arg: name (str)
    POP = 4          # discard top of stack

    # Arithmetic
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    POW = 15

    # Comparison
    EQ = 20
    NE = 21
    LT = 22
    LE = 23
    GT = 24
    GE = 25

    # Logical (short-circuit handled by compiler with jumps)
    AND = 26
    OR = 27

    # Unary
    NEG = 30
    NOT = 31

    # Control flow
    JUMP = 40        # arg: target ip
    JUMP_IF_FALSE = 41   # arg: target ip; pop top, jump if falsy
    JUMP_IF_TRUE = 42    # arg: target ip; pop top, jump if truthy

    # Calls and returns
    CALL = 50        # arg: number of arguments; pops callee + args, pushes result
    RETURN = 51      # pop and return from current frame
    RETURN_NONE = 52

    # Objects
    GET_ATTR = 60   # arg: attribute name; obj on stack -> value
    SET_ATTR = 61  # arg: name; obj, value on stack
    INDEX = 62     # obj, index on stack -> obj[index]
    INDEX_SET = 63 # obj, index, value on stack; leaves value
    BUILD_LIST = 64   # arg: count; pop count items, push list
    BUILD_DICT = 65   # arg: count (pairs); pop count*2 (k,v,k,v,...), push dict

    # Helpers for for-loop etc.
    LEN = 66       # one arg on stack -> len(arg)
    MAKE_FUNCTION = 67  # arg: (start_ip, param_count); pushes VM function
    TRY = 70         # arg: (catch_ip, catch_var); push try record
    END_TRY = 71     # pop try record
    THROW = 72       # pop value, raise RuntimeError(value)


# Instruction = (Op, optional_arg). We store as tuple for clarity.
Instruction = Tuple[int, ...]  # (Op) or (Op, arg)


class Chunk:
    """Bytecode chunk: constants and linear code."""
    __slots__ = ("constants", "code")

    def __init__(self) -> None:
        self.constants: List[Any] = []
        self.code: List[Instruction] = []

    def emit(self, op: Op, arg: Any = None) -> int:
        """Append one instruction; return its index (ip)."""
        ip = len(self.code)
        if arg is not None:
            self.code.append((int(op), arg))
        else:
            self.code.append((int(op),))
        return ip

    def add_const(self, value: Any) -> int:
        """Append constant and return its index."""
        idx = len(self.constants)
        self.constants.append(value)
        return idx

    def patch(self, ip: int, arg: Any) -> None:
        """Replace the argument of the instruction at ip."""
        t = self.code[ip]
        self.code[ip] = (t[0], arg)

    def __len__(self) -> int:
        return len(self.code)
