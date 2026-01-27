"""Stack-based VM for Keris bytecode."""

from typing import Any, Dict, List, Optional, Tuple

from .bytecode import Chunk, Op
from .runtime import RuntimeError
from .stdlib import create_stdlib


class VMFunction:
    """A Keris function compiled to bytecode."""
    __slots__ = ("chunk", "start_ip", "param_names", "closure")

    def __init__(self, chunk: Chunk, start_ip: int, param_names: List[str], closure: Dict[str, Any]):
        self.chunk = chunk
        self.start_ip = start_ip
        self.param_names = param_names
        self.closure = closure

    @property
    def nparams(self) -> int:
        return len(self.param_names)

    def __repr__(self) -> str:
        return "<function>"


class Frame:
    """One call frame: return address and local variables."""
    __slots__ = ("return_ip", "locals", "closure")

    def __init__(self, return_ip: int, locals_dict: Dict[str, Any], closure: Dict[str, Any]):
        self.return_ip = return_ip
        self.locals = locals_dict
        self.closure = closure


class VM:
    """Stack-based VM for executing Keris bytecode."""

    def __init__(self) -> None:
        self.chunk: Optional[Chunk] = None
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.frames: List[Frame] = []
        self.ip: int = 0
        self.try_stack: List[Tuple[int, str]] = []  # (catch_ip, catch_var)
        self._setup_globals()

    def _setup_globals(self) -> None:
        for name, value in create_stdlib().items():
            self.globals[name] = value

    def _current_frame(self) -> Optional[Frame]:
        return self.frames[-1] if self.frames else None

    def _resolve_var(self, name: str) -> Tuple[Dict[str, Any], str]:
        """Return (scope_dict, name) where to read."""
        frame = self._current_frame()
        if frame is not None:
            if name in frame.locals:
                return (frame.locals, name)
            if name in frame.closure:
                return (frame.closure, name)
        if name in self.globals:
            return (self.globals, name)
        raise RuntimeError(f"Undefined variable '{name}'")

    def _resolve_var_for_write(self, name: str) -> Tuple[Dict[str, Any], str]:
        """Return (scope_dict, name) where to write. Defines in current scope if new."""
        frame = self._current_frame()
        if frame is not None:
            if name in frame.locals:
                return (frame.locals, name)
            if name in frame.closure:
                return (frame.closure, name)
        if name in self.globals:
            return (self.globals, name)
        return (frame.locals if frame else self.globals, name)

    def _is_truthy(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def _is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def _check_number_operand(self, operator: str, operand: Any) -> None:
        if not isinstance(operand, (int, float)):
            raise RuntimeError(f"Operand must be a number for {operator}")

    def _check_number_operands(self, operator: str, left: Any, right: Any) -> None:
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise RuntimeError(f"Operands must be numbers for {operator}")

    def _index_get(self, obj: Any, index: Any) -> Any:
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise RuntimeError("List index must be an integer")
            if index < 0:
                index = len(obj) + index
            if index < 0 or index >= len(obj):
                raise RuntimeError("List index out of range")
            return obj[index]
        if isinstance(obj, dict):
            return obj.get(index)
        if isinstance(obj, str):
            if not isinstance(index, int):
                raise RuntimeError("String index must be an integer")
            if index < 0:
                index = len(obj) + index
            if index < 0 or index >= len(obj):
                raise RuntimeError("String index out of range")
            return obj[index]
        raise RuntimeError("Indexing not supported for this type")

    def _index_set(self, obj: Any, index: Any, value: Any) -> None:
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise RuntimeError("List index must be an integer")
            if index < 0:
                index = len(obj) + index
            if index < 0 or index >= len(obj):
                raise RuntimeError("List index out of range")
            obj[index] = value
            return
        if isinstance(obj, dict):
            obj[index] = value
            return
        raise RuntimeError("Index assignment not supported for this type")

    def run(self, chunk: Chunk) -> None:
        """Execute the chunk. Entry point."""
        self.chunk = chunk
        self.ip = 0
        self.stack.clear()
        self.frames.clear()
        self.try_stack.clear()
        code = chunk.code
        constants = chunk.constants

        while self.ip < len(code):
            try:
                inst = code[self.ip]
                op = inst[0]
                arg = inst[1] if len(inst) > 1 else None
                self.ip += 1

                if op == Op.LOAD_CONST:
                    self.stack.append(constants[arg])
                elif op == Op.LOAD_VAR:
                    scope, key = self._resolve_var(arg)
                    self.stack.append(scope[key])
                elif op == Op.STORE_VAR:
                    scope, key = self._resolve_var_for_write(arg)
                    scope[key] = self.stack[-1]
                elif op == Op.POP:
                    self.stack.pop()

                elif op == Op.ADD:
                    b, a = self.stack.pop(), self.stack.pop()
                    if isinstance(a, str) or isinstance(b, str):
                        self.stack.append(str(a) + str(b))
                    else:
                        self.stack.append(a + b)
                elif op == Op.SUB:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("-", a, b)
                    self.stack.append(a - b)
                elif op == Op.MUL:
                    b, a = self.stack.pop(), self.stack.pop()
                    if isinstance(a, str) and isinstance(b, (int, float)):
                        self.stack.append(a * int(b))
                    elif isinstance(b, str) and isinstance(a, (int, float)):
                        self.stack.append(b * int(a))
                    else:
                        self._check_number_operands("*", a, b)
                        self.stack.append(a * b)
                elif op == Op.DIV:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("/", a, b)
                    if b == 0:
                        raise RuntimeError("Division by zero")
                    self.stack.append(a / b)
                elif op == Op.MOD:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("%", a, b)
                    self.stack.append(a % b)
                elif op == Op.POW:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("**", a, b)
                    self.stack.append(a ** b)

                elif op == Op.EQ:
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(self._is_equal(a, b))
                elif op == Op.NE:
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(not self._is_equal(a, b))
                elif op == Op.LT:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("<", a, b)
                    self.stack.append(a < b)
                elif op == Op.LE:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands("<=", a, b)
                    self.stack.append(a <= b)
                elif op == Op.GT:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands(">", a, b)
                    self.stack.append(a > b)
                elif op == Op.GE:
                    b, a = self.stack.pop(), self.stack.pop()
                    self._check_number_operands(">=", a, b)
                    self.stack.append(a >= b)

                elif op == Op.NEG:
                    a = self.stack.pop()
                    self._check_number_operand("-", a)
                    self.stack.append(-a)
                elif op == Op.NOT:
                    self.stack.append(not self._is_truthy(self.stack.pop()))

                elif op == Op.JUMP:
                    self.ip = arg
                elif op == Op.JUMP_IF_FALSE:
                    if not self._is_truthy(self.stack[-1]):
                        self.ip = arg
                elif op == Op.JUMP_IF_TRUE:
                    if self._is_truthy(self.stack[-1]):
                        self.ip = arg

                elif op == Op.CALL:
                    nargs = arg
                    args = [self.stack.pop() for _ in range(nargs)][::-1]
                    callee = self.stack.pop()
                    if isinstance(callee, VMFunction):
                        if len(args) != callee.nparams:
                            raise RuntimeError(
                                f"Expected {callee.nparams} arguments but got {len(args)}"
                            )
                        new_locals = dict(zip(callee.param_names, args))
                        closure = dict(callee.closure)
                        self.frames.append(Frame(self.ip, new_locals, closure))
                        self.ip = callee.start_ip
                    elif callable(callee):
                        try:
                            result = callee(*args)
                            self.stack.append(result)
                        except TypeError as e:
                            raise RuntimeError(f"Function call error: {e}")
                    else:
                        raise RuntimeError("Can only call functions")

                elif op == Op.RETURN:
                    val = self.stack.pop()
                    frame = self.frames.pop()
                    self.ip = frame.return_ip
                    self.stack.append(val)
                elif op == Op.RETURN_NONE:
                    frame = self.frames.pop()
                    self.ip = frame.return_ip
                    self.stack.append(None)

                elif op == Op.GET_ATTR:
                    obj = self.stack.pop()
                    name = arg
                    if isinstance(obj, dict):
                        self.stack.append(obj.get(name))
                    elif isinstance(obj, list):
                        if name == "append":
                            self.stack.append(lambda item: obj.append(item))
                        elif name == "pop":
                            self.stack.append(lambda: obj.pop() if obj else None)
                        elif name == "len":
                            self.stack.append(len(obj))
                        elif name == "contains":
                            self.stack.append(lambda item: item in obj)
                        else:
                            raise RuntimeError(f"Property '{name}' not found")
                    elif hasattr(obj, "__getattr__"):
                        self.stack.append(getattr(obj, name, None))
                    else:
                        raise RuntimeError(f"Property '{name}' not found")
                elif op == Op.SET_ATTR:
                    value = self.stack.pop()
                    obj = self.stack.pop()
                    name = arg
                    if isinstance(obj, dict):
                        obj[name] = value
                    self.stack.append(value)
                elif op == Op.INDEX:
                    index = self.stack.pop()
                    obj = self.stack.pop()
                    self.stack.append(self._index_get(obj, index))
                elif op == Op.INDEX_SET:
                    value = self.stack.pop()
                    index = self.stack.pop()
                    obj = self.stack.pop()
                    self._index_set(obj, index, value)
                    self.stack.append(value)
                elif op == Op.BUILD_LIST:
                    n = arg
                    self.stack.append([self.stack.pop() for _ in range(n)][::-1])
                elif op == Op.BUILD_DICT:
                    n = arg
                    d = {}
                    for _ in range(n):
                        v = self.stack.pop()
                        k = self.stack.pop()
                        if not isinstance(k, (str, int, float, bool)):
                            k = str(k)
                        d[k] = v
                    self.stack.append(d)
                elif op == Op.LEN:
                    a = self.stack.pop()
                    self.stack.append(len(a))
                elif op == Op.MAKE_FUNCTION:
                    start_ip, param_info = arg
                    if isinstance(param_info, int):
                        param_names = [f"__arg{i}" for i in range(param_info)]
                    else:
                        param_names = list(param_info)
                    closure = dict(self.globals)
                    frame = self._current_frame()
                    if frame:
                        closure.update(frame.closure)
                        closure.update(frame.locals)
                    self.stack.append(VMFunction(self.chunk, start_ip, param_names, closure))
                elif op == Op.TRY:
                    catch_ip, catch_var = arg
                    self.try_stack.append((catch_ip, catch_var))
                elif op == Op.END_TRY:
                    self.try_stack.pop()
                elif op == Op.THROW:
                    val = self.stack.pop()
                    raise RuntimeError(str(val))
                else:
                    raise RuntimeError(f"Unknown opcode {op}")
            except RuntimeError as e:
                if self.try_stack:
                    catch_ip, catch_var = self.try_stack.pop()
                    frame = self._current_frame()
                    if frame is not None:
                        frame.locals[catch_var] = str(e.message)
                    self.ip = catch_ip
                else:
                    raise
