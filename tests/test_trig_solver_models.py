import pytest
import sympy as sp
from pydantic import ValidationError

from trig_solver.models import ExprAST


def test_expr_ast_round_trip_for_allowlisted_expression():
    x = sp.Symbol("x", real=True)
    expression = 2 * sp.sin(x + sp.pi / 3) ** 2
    ast = ExprAST.from_sympy(expression)
    assert sp.simplify(ast.to_sympy() - expression) == 0
    assert ast.node_count() < 256


def test_expr_ast_rejects_unknown_operations():
    with pytest.raises(ValidationError):
        ExprAST(op="__import__", value="os")


def test_expr_ast_rejects_unsafe_symbols():
    ast = ExprAST(op="symbol", value="x;import_os")
    with pytest.raises(ValueError, match="unsafe symbol"):
        ast.to_sympy()

