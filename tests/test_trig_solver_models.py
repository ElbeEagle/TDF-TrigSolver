import pytest
import sympy as sp
from pydantic import ValidationError

from trig_solver.models import ExprAST, GoldAnswer, SetSpec


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


def test_expr_ast_round_trip_for_inverse_trigonometric_constant():
    expression = sp.asin(sp.Rational(2, 3)) / 2
    ast = ExprAST.from_sympy(expression)
    assert ast.to_sympy() == expression


def test_gold_answer_uses_structured_set_union():
    value = sp.Union(sp.Interval(-sp.oo, -1), sp.Interval(1, sp.oo))
    gold = GoldAnswer.from_value(value)
    assert gold.kind == "set"
    assert gold.set_value is not None
    assert gold.set_value.kind == "union"
    assert SetSpec.model_validate(gold.set_value.model_dump()).to_sympy() == value
