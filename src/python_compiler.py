"""Transpiles Keris AST to Python AST and compiles to bytecode for fast execution."""

import ast
import sys
from typing import Any, Dict, List, Optional

from .ast import *


class TranspileError(Exception):
    """Raised when Keris cannot be transpiled to Python."""
    pass


def _store() -> ast.Store:
    return ast.Store()


def _load() -> ast.Load:
    return ast.Load()


def _subscript_slice(index_expr: ast.expr) -> ast.expr:
    """Subscript slice for list/dict access. Python 3.9+ uses expr directly; 3.8 uses ast.Index."""
    if sys.version_info >= (3, 9):
        return index_expr
    return ast.Index(value=index_expr)


class PythonTranspiler:
    """Converts Keris AST to Python AST. Run with exec(compile(module, '<keris>', 'exec'), globals)."""

    def transpile(self, statements: List[Stmt]) -> ast.Module:
        """Return a Python ast.Module that can be compiled and executed."""
        body = [self._stmt(s) for s in statements]
        return ast.Module(body=body, type_ignores=[])

    def _stmt(self, s: Stmt) -> ast.stmt:
        if isinstance(s, Expression):
            return ast.Expr(value=self._expr(s.expr))
        if isinstance(s, Var):
            value = self._expr(s.initializer) if s.initializer else ast.Constant(value=None)
            return ast.Assign(
                targets=[ast.Name(id=s.name, ctx=_store())],
                value=value,
            )
        if isinstance(s, Block):
            return ast.Module(body=[self._stmt(x) for x in s.statements], type_ignores=[])
        if isinstance(s, If):
            then_body = self._stmt_to_list(s.then_branch)
            else_body = [self._stmt(s.else_branch)] if s.else_branch else []
            return ast.If(
                test=self._expr(s.condition),
                body=then_body,
                orelse=else_body,
            )
        if isinstance(s, While):
            return ast.While(
                test=self._expr(s.condition),
                body=self._stmt_to_list(s.body),
                orelse=[],
            )
        if isinstance(s, For):
            return ast.For(
                target=ast.Name(id=s.variable, ctx=_store()),
                iter=self._expr(s.iterable),
                body=self._stmt_to_list(s.body),
                orelse=[],
            )
        if isinstance(s, Break):
            return ast.Break()
        if isinstance(s, Continue):
            return ast.Continue()
        if isinstance(s, Return):
            value = self._expr(s.value) if s.value is not None else None
            return ast.Return(value=value)
        if isinstance(s, Function):
            return ast.FunctionDef(
                name=s.name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=p) for p in s.params],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[self._stmt(x) for x in s.body],
                decorator_list=[],
            )
        if isinstance(s, Try):
            try_body = self._stmt_to_list(s.try_block)
            catch_body = self._stmt_to_list(s.catch_block)
            # Keris catch_var is the error message string; Python gives us the exception.
            assign_msg = ast.Assign(
                targets=[ast.Name(id=s.catch_var, ctx=_store())],
                value=ast.Call(
                    func=ast.Name(id="str", ctx=_load()),
                    args=[ast.Name(id=s.catch_var, ctx=_load())],
                    keywords=[],
                ),
            )
            handler = ast.ExceptHandler(
                type=ast.Name(id="BaseException", ctx=_load()),  # catch all
                name=s.catch_var,
                body=[assign_msg] + catch_body,
            )
            return ast.Try(
                body=try_body,
                handlers=[handler],
                orelse=[],
                finalbody=[],
            )
        if isinstance(s, Throw):
            # Throw as statement: evaluate value and raise (statement form).
            return ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="_keris_throw", ctx=_load()),
                    args=[self._expr(s.value)],
                    keywords=[],
                )
            )
        raise TranspileError(f"Unsupported statement: {type(s).__name__}")

    def _stmt_to_list(self, s: Stmt) -> List[ast.stmt]:
        """Flatten Block to list of Python statements."""
        if isinstance(s, Block):
            return [self._stmt(x) for x in s.statements]
        return [self._stmt(s)]

    def _expr(self, e: Expr) -> ast.expr:
        if isinstance(e, Literal):
            return ast.Constant(value=e.value)
        if isinstance(e, Identifier):
            return ast.Name(id=e.name, ctx=_load())
        if isinstance(e, Binary):
            return self._binary(e)
        if isinstance(e, Unary):
            return self._unary(e)
        if isinstance(e, Call):
            return ast.Call(
                func=self._expr(e.callee),
                args=[self._expr(a) for a in e.arguments],
                keywords=[],
            )
        if isinstance(e, Get):
            return ast.Attribute(
                value=self._expr(e.obj),
                attr=e.name,
                ctx=_load(),
            )
        if isinstance(e, Set):
            # Keris allows obj.x = value as expression (returns value). Emit setattr then value.
            obj_py = self._expr(e.obj)
            val_py = self._expr(e.value)
            setattr_call = ast.Call(
                func=ast.Name(id="setattr", ctx=_load()),
                args=[obj_py, ast.Constant(value=e.name), val_py],
                keywords=[],
            )
            return ast.BoolOp(op=ast.Or(), values=[setattr_call, val_py])
        if isinstance(e, Index):
            return ast.Subscript(
                value=self._expr(e.obj),
                slice=_subscript_slice(self._expr(e.index)),
                ctx=_load(),
            )
        if isinstance(e, IndexSet):
            # Keris list[i]=val as expression returns val. (obj.__setitem__(idx, val) or val)
            obj_py = self._expr(e.obj)
            idx_py = self._expr(e.index)
            val_py = self._expr(e.value)
            setitem_call = ast.Call(
                func=ast.Attribute(value=obj_py, attr="__setitem__", ctx=_load()),
                args=[idx_py, val_py],
                keywords=[],
            )
            return ast.BoolOp(op=ast.Or(), values=[setitem_call, val_py])
        if isinstance(e, ListLiteral):
            return ast.List(elts=[self._expr(x) for x in e.elements], ctx=_load())
        if isinstance(e, DictLiteral):
            keys = [self._expr(k) for k, _ in e.pairs]
            values = [self._expr(v) for _, v in e.pairs]
            return ast.Dict(keys=keys, values=values)
        if isinstance(e, Assign):
            # Keris assignment is an expression (returns value). Use walrus.
            return ast.NamedExpr(
                target=ast.Name(id=e.name, ctx=_store()),
                value=self._expr(e.value),
            )
        if isinstance(e, Throw):
            # Throw in expression position: call helper that raises so we stay in expr form.
            return ast.Call(
                func=ast.Name(id="_keris_throw", ctx=_load()),
                args=[self._expr(e.value)],
                keywords=[],
            )
        raise TranspileError(f"Unsupported expression: {type(e).__name__}")

    def _binary(self, e: Binary) -> ast.expr:
        cmp_op_map = {
            "==": ast.Eq(),
            "!=": ast.NotEq(),
            "<": ast.Lt(),
            "<=": ast.LtE(),
            ">": ast.Gt(),
            ">=": ast.GtE(),
        }
        bin_op_map = {
            "+": ast.Add(),
            "-": ast.Sub(),
            "*": ast.Mult(),
            "/": ast.Div(),
            "%": ast.Mod(),
            "**": ast.Pow(),
        }
        if e.operator == "and":
            return ast.BoolOp(op=ast.And(), values=[self._expr(e.left), self._expr(e.right)])
        if e.operator == "or":
            return ast.BoolOp(op=ast.Or(), values=[self._expr(e.left), self._expr(e.right)])
        if e.operator in cmp_op_map:
            return ast.Compare(
                left=self._expr(e.left),
                ops=[cmp_op_map[e.operator]],
                comparators=[self._expr(e.right)],
            )
        op = bin_op_map.get(e.operator)
        if op is None:
            raise TranspileError(f"Unknown binary operator: {e.operator}")
        return ast.BinOp(left=self._expr(e.left), op=op, right=self._expr(e.right))

    def _unary(self, e: Unary) -> ast.expr:
        if e.operator == "-":
            return ast.UnaryOp(op=ast.USub(), operand=self._expr(e.right))
        if e.operator in ("!", "not"):
            return ast.UnaryOp(op=ast.Not(), operand=self._expr(e.right))
        raise TranspileError(f"Unknown unary operator: {e.operator}")


def transpile_to_python(statements: List[Stmt]) -> ast.Module:
    """Transpile Keris statements to a Python ast.Module."""
    t = PythonTranspiler()
    return t.transpile(statements)


def compile_to_python(statements: List[Stmt], filename: str = "<keris>") -> Any:
    """
    Compile Keris AST to a Python code object.
    Returns (code_object, globals_dict) so you can exec(code_object, globals_dict).
    """
    from .stdlib import create_stdlib
    module = transpile_to_python(statements)
    ast.fix_missing_locations(module)
    code = compile(module, filename, "exec")
    globals_dict = create_stdlib()

    def _keris_throw(x: Any) -> None:
        raise RuntimeError(str(x))

    globals_dict["_keris_throw"] = _keris_throw
    return code, globals_dict
