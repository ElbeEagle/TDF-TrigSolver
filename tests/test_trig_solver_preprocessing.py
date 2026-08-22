import importlib.util

import pytest
import sympy as sp

from trig_solver.models import AbstainCode, RawProblem
from trig_solver.pipeline import solve_raw
from trig_solver.preprocessing import FormulaParseError, parse_latex_ast, preprocess_problem, split_options


pytestmark = pytest.mark.skipif(importlib.util.find_spec("antlr4") is None, reason="ANTLR is an optional parser dependency")


def test_latex_parser_handles_affine_sinusoid_and_degrees():
    x = sp.Symbol("x", real=True)
    parsed = parse_latex_ast(r"2\sin\left(\frac{x}{2}+\frac{\pi}{5}\right)").to_sympy()
    assert sp.trigsimp(parsed - 2 * sp.sin(x / 2 + sp.pi / 5)) == 0
    degree = parse_latex_ast(r"\sin 30^{\circ}").to_sympy()
    assert sp.trigsimp(degree - sp.Rational(1, 2)) == 0


def test_latex_parser_handles_inverse_trigonometric_constants():
    parsed = parse_latex_ast(r"\frac{1}{2}\arcsin\frac{2}{3}").to_sympy()
    assert parsed == sp.asin(sp.Rational(2, 3)) / 2


def test_incomplete_formula_is_rejected():
    with pytest.raises(FormulaParseError):
        parse_latex_ast(r"\sin x +")


def test_one_invalid_formula_rejects_the_whole_problem():
    problem = RawProblem(question=r"已知 $\sin x$，再看 $\unknown{x}$。")
    with pytest.raises(FormulaParseError):
        preprocess_problem(problem)


def test_preprocessor_assigns_grounded_expression_ids():
    problem = RawProblem(
        question=r"函数 $y=2\sin(\frac{x}{2}+\frac{\pi}{5})$ 的周期和振幅是",
        options=r"A. $4\pi,2$" + "\n" + r"B. $2\pi,2$",
    )
    parsed = preprocess_problem(problem)
    assert [item.id for item in parsed.expressions] == ["E1"]
    assert len(parsed.options) == 2


def test_visual_input_abstains_before_external_api(monkeypatch):
    problem = RawProblem(question=r"根据下图判断函数 $y=\sin x$ 的周期")
    result = solve_raw(problem)
    assert result.status == "abstained"
    assert result.abstain_code == AbstainCode.UNSUPPORTED_INPUT


def test_option_split_accepts_cmm_string_and_open_array():
    assert split_options("A. 1\nB. 2\nC. 3") == ["1", "2", "3"]
    assert split_options([]) == []
