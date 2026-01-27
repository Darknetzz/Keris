"""Compiles Keris AST to bytecode."""

from typing import List

from .ast import *
from .bytecode import Chunk, Op


class CompilerError(Exception):
    """Raised when compilation fails."""
    pass


class Compiler:
    """Compiles AST to a single Chunk. Functions are emitted inline with JUMP-over."""

    def __init__(self) -> None:
        self.chunk = Chunk()
        self._loop_stack: List[tuple] = []  # (break_list, continue_ip) for patch

    def compile(self, statements: List[Stmt]) -> Chunk:
        """Compile a list of statements into self.chunk. Returns the chunk."""
        for stmt in statements:
            self._stmt(stmt)
        return self.chunk

    def _stmt(self, s: Stmt) -> None:
        if isinstance(s, Expression):
            self._expr(s.expr)
            self.chunk.emit(Op.POP)
        elif isinstance(s, Var):
            if s.initializer:
                self._expr(s.initializer)
            else:
                self.chunk.emit(Op.LOAD_CONST, self.chunk.add_const(None))
            self.chunk.emit(Op.STORE_VAR, s.name)
        elif isinstance(s, Block):
            for x in s.statements:
                self._stmt(x)
        elif isinstance(s, If):
            self._expr(s.condition)
            jump_else = self.chunk.emit(Op.JUMP_IF_FALSE, 0)
            self.chunk.emit(Op.POP)
            self._stmt(s.then_branch)
            if s.else_branch is not None:
                jump_end = self.chunk.emit(Op.JUMP, 0)
                self.chunk.patch(jump_else, len(self.chunk.code))
                self.chunk.emit(Op.POP)
                self._stmt(s.else_branch)
                self.chunk.patch(jump_end, len(self.chunk.code))
            else:
                self.chunk.patch(jump_else, len(self.chunk.code))
                self.chunk.emit(Op.POP)
        elif isinstance(s, While):
            start = len(self.chunk.code)
            self._expr(s.condition)
            jump_out = self.chunk.emit(Op.JUMP_IF_FALSE, 0)
            self.chunk.emit(Op.POP)
            break_list: List[int] = [jump_out]
            self._loop_stack.append((break_list, start))
            try:
                self._stmt(s.body)
            finally:
                self._loop_stack.pop()
            self.chunk.emit(Op.JUMP, start)
            loop_end = len(self.chunk.code)
            for j in break_list:
                self.chunk.patch(j, loop_end)
            self.chunk.emit(Op.POP)
        elif isinstance(s, For):
            self._expr(s.iterable)
            self.chunk.emit(Op.STORE_VAR, "__for_iter")
            self.chunk.emit(Op.LOAD_CONST, self.chunk.add_const(0))
            self.chunk.emit(Op.STORE_VAR, "__for_idx")
            start = len(self.chunk.code)
            self.chunk.emit(Op.LOAD_VAR, "__for_idx")
            self.chunk.emit(Op.LOAD_VAR, "__for_iter")
            self.chunk.emit(Op.LEN)
            self.chunk.emit(Op.LT)
            jump_out = self.chunk.emit(Op.JUMP_IF_FALSE, 0)
            self.chunk.emit(Op.POP)
            self.chunk.emit(Op.LOAD_VAR, "__for_iter")
            self.chunk.emit(Op.LOAD_VAR, "__for_idx")
            self.chunk.emit(Op.INDEX)
            self.chunk.emit(Op.STORE_VAR, s.variable)
            break_list = [jump_out]
            self._loop_stack.append((break_list, start))
            try:
                self._stmt(s.body)
            finally:
                self._loop_stack.pop()
            self.chunk.emit(Op.LOAD_VAR, "__for_idx")
            self.chunk.emit(Op.LOAD_CONST, self.chunk.add_const(1))
            self.chunk.emit(Op.ADD)
            self.chunk.emit(Op.STORE_VAR, "__for_idx")
            self.chunk.emit(Op.JUMP, start)
            loop_end = len(self.chunk.code)
            for j in break_list:
                self.chunk.patch(j, loop_end)
            self.chunk.emit(Op.POP)
        elif isinstance(s, Break):
            if not self._loop_stack:
                raise CompilerError("break outside loop")
            break_list, _ = self._loop_stack[-1]
            jump = self.chunk.emit(Op.JUMP, 0)
            break_list.append(jump)
        elif isinstance(s, Continue):
            if not self._loop_stack:
                raise CompilerError("continue outside loop")
            _, continue_ip = self._loop_stack[-1]
            self.chunk.emit(Op.JUMP, continue_ip)
        elif isinstance(s, Return):
            if s.value is not None:
                self._expr(s.value)
                self.chunk.emit(Op.RETURN)
            else:
                self.chunk.emit(Op.RETURN_NONE)
        elif isinstance(s, Function):
            over = self.chunk.emit(Op.JUMP, 0)
            body_start = len(self.chunk.code)
            for st in s.body:
                self._stmt(st)
            self.chunk.emit(Op.RETURN_NONE)
            self.chunk.patch(over, len(self.chunk.code))
            self.chunk.emit(Op.MAKE_FUNCTION, (body_start, s.params))
            self.chunk.emit(Op.STORE_VAR, s.name)
        elif isinstance(s, Try):
            try_ip_placeholder = self.chunk.emit(Op.TRY, (0, s.catch_var))
            self._stmt(s.try_block)
            self.chunk.emit(Op.END_TRY)
            jump_over = self.chunk.emit(Op.JUMP, 0)
            catch_ip = len(self.chunk.code)
            self.chunk.patch(try_ip_placeholder, (catch_ip, s.catch_var))
            self._stmt(s.catch_block)
            self.chunk.patch(jump_over, len(self.chunk.code))
        else:
            raise CompilerError(f"Unknown statement: {type(s)}")

    def _expr(self, e: Expr) -> None:
        if isinstance(e, Literal):
            idx = self.chunk.add_const(e.value)
            self.chunk.emit(Op.LOAD_CONST, idx)
        elif isinstance(e, Identifier):
            self.chunk.emit(Op.LOAD_VAR, e.name)
        elif isinstance(e, Binary):
            if e.operator == "and":
                self._expr(e.left)
                skip = self.chunk.emit(Op.JUMP_IF_FALSE, 0)
                self.chunk.emit(Op.POP)
                self._expr(e.right)
                self.chunk.patch(skip, len(self.chunk.code))
                self.chunk.emit(Op.POP)
                return
            if e.operator == "or":
                self._expr(e.left)
                skip = self.chunk.emit(Op.JUMP_IF_TRUE, 0)
                self.chunk.emit(Op.POP)
                self._expr(e.right)
                self.chunk.patch(skip, len(self.chunk.code))
                self.chunk.emit(Op.POP)
                return
            self._expr(e.left)
            self._expr(e.right)
            op = e.operator
            if op == "+":
                self.chunk.emit(Op.ADD)
            elif op == "-":
                self.chunk.emit(Op.SUB)
            elif op == "*":
                self.chunk.emit(Op.MUL)
            elif op == "/":
                self.chunk.emit(Op.DIV)
            elif op == "%":
                self.chunk.emit(Op.MOD)
            elif op == "**":
                self.chunk.emit(Op.POW)
            elif op == "==":
                self.chunk.emit(Op.EQ)
            elif op == "!=":
                self.chunk.emit(Op.NE)
            elif op == "<":
                self.chunk.emit(Op.LT)
            elif op == "<=":
                self.chunk.emit(Op.LE)
            elif op == ">":
                self.chunk.emit(Op.GT)
            elif op == ">=":
                self.chunk.emit(Op.GE)
            else:
                raise CompilerError(f"Unknown binary op: {op}")
        elif isinstance(e, Unary):
            self._expr(e.right)
            if e.operator == "-":
                self.chunk.emit(Op.NEG)
            elif e.operator in ("!", "not"):
                self.chunk.emit(Op.NOT)
            else:
                raise CompilerError(f"Unknown unary op: {e.operator}")
        elif isinstance(e, Call):
            self._expr(e.callee)
            for a in e.arguments:
                self._expr(a)
            self.chunk.emit(Op.CALL, len(e.arguments))
        elif isinstance(e, Get):
            self._expr(e.obj)
            self.chunk.emit(Op.GET_ATTR, e.name)
        elif isinstance(e, Set):
            self._expr(e.obj)
            self._expr(e.value)
            self.chunk.emit(Op.SET_ATTR, e.name)
        elif isinstance(e, Index):
            self._expr(e.obj)
            self._expr(e.index)
            self.chunk.emit(Op.INDEX)
        elif isinstance(e, IndexSet):
            self._expr(e.obj)
            self._expr(e.index)
            self._expr(e.value)
            self.chunk.emit(Op.INDEX_SET)
        elif isinstance(e, ListLiteral):
            for x in e.elements:
                self._expr(x)
            self.chunk.emit(Op.BUILD_LIST, len(e.elements))
        elif isinstance(e, DictLiteral):
            for k, v in e.pairs:
                self._expr(k)
                self._expr(v)
            self.chunk.emit(Op.BUILD_DICT, len(e.pairs))
        elif isinstance(e, Assign):
            self._expr(e.value)
            self.chunk.emit(Op.STORE_VAR, e.name)
        elif isinstance(e, Throw):
            self._expr(e.value)
            self.chunk.emit(Op.THROW)
        else:
            raise CompilerError(f"Unknown expression: {type(e)}")


def compile_chunk(statements: List[Stmt]) -> Chunk:
    """Compile statements to a single chunk. Entry point."""
    c = Compiler()
    return c.compile(statements)
