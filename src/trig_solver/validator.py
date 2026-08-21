"""Exact answer rendering and option matching."""

from __future__ import annotations

import re
from typing import Any

import sympy as sp

from .cas import CASExecutor, CASTimeout, CASUnsolved
from .models import PeriodicSet
from .preprocessing import FormulaParseError, extract_formula_strings, parse_latex_ast


def symbolic_equal(left: sp.Basic, right: sp.Basic) -> bool:
    cas = CASExecutor(2.0)
    try:
        if isinstance(left, sp.Set) and isinstance(right, sp.Set):
            return left == right or cas.run("simplify", left.symmetric_difference(right)) == sp.EmptySet
        return cas.run("trigsimp", cas.run("simplify", left - right)) == 0
    except (CASTimeout, CASUnsolved, TypeError, ValueError, NotImplementedError):
        return False


def render_value(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}={render_value(item)}" for key, item in value.items())
    if isinstance(value, (tuple, list)):
        return "(" + ", ".join(render_value(item) for item in value) + ")"
    if isinstance(value, sp.Set):
        return sp.latex(value)
    if isinstance(value, sp.Basic):
        return sp.latex(value)
    return str(value)


def render_periodic(periodic: PeriodicSet) -> str:
    period = sp.latex(periodic.period.to_sympy())
    cells: list[str] = []
    cells.extend(sp.latex(point.to_sympy()) for point in periodic.points)
    for interval in periodic.intervals:
        left = "(" if interval.left_open else "["
        right = ")" if interval.right_open else "]"
        cells.append(f"{left}{sp.latex(interval.start.to_sympy())}, {sp.latex(interval.end.to_sympy())}{right}")
    joined = " \\cup ".join(cells) if cells else "\\varnothing"
    return f"\\bigcup_{{k\\in\\mathbb{{Z}}}}\\left(({joined})+k({period})\\right)"


def _option_parts(option: str) -> list[str]:
    math = extract_formula_strings(option)
    content = math[0] if math else option
    content = re.sub(r"^[A-Da-d]\s*[\.、．·]\s*", "", content).strip()
    if re.fullmatch(r"\s*[\[(].+,.+[\])]\s*", content):
        return [content]
    return [part.strip() for part in re.split(r"\s*,\s*", content) if part.strip()]


def _parse_option_part(part: str) -> sp.Basic:
    return parse_latex_ast(part).to_sympy()


def match_options(value: Any, options: list[str]) -> tuple[str | None, str | None]:
    if not options:
        return None, None
    expected = list(value.values()) if isinstance(value, dict) else list(value) if isinstance(value, (tuple, list)) else [value]
    matches: list[int] = []
    for index, option in enumerate(options):
        try:
            parts = _option_parts(option)
            if len(parts) != len(expected):
                continue
            parsed = [_parse_set_or_expression(part) for part in parts]
        except FormulaParseError:
            continue
        if all(isinstance(target, sp.Basic) and symbolic_equal(target, candidate) for target, candidate in zip(expected, parsed)):
            matches.append(index)
    if len(matches) == 1:
        return chr(ord("A") + matches[0]), None
    if not matches:
        return None, "no option is symbolically equivalent to the computed answer"
    return None, "multiple options are symbolically equivalent to the computed answer"


def _parse_set_or_expression(part: str) -> sp.Basic:
    interval = re.fullmatch(r"\s*([\[(])\s*(.+?)\s*,\s*(.+?)\s*([\])])\s*", part)
    if not interval:
        return _parse_option_part(part)
    start = _parse_option_part(interval.group(2))
    end = _parse_option_part(interval.group(3))
    return sp.Interval(
        start,
        end,
        left_open=interval.group(1) == "(",
        right_open=interval.group(4) == ")",
    )


def match_periodic_options(periodic: PeriodicSet, options: list[str]) -> tuple[str | None, str | None]:
    """Match the pilot's common ``x=a+kT`` multiple-choice notation exactly."""

    if periodic.intervals or periodic.excluded_points:
        return None, "periodic interval option matching is not implemented"
    expected_period = sp.simplify(periodic.period.to_sympy())
    expected_points = [point.to_sympy() for point in periodic.points]
    matches: list[int] = []
    for index, option in enumerate(options):
        formulas = extract_formula_strings(option)
        if not formulas:
            formulas = [part for part in re.split(r"\s*(?:或|or)\s*", option) if part.strip()]
        candidate_points: list[sp.Basic] = []
        valid = bool(formulas)
        for formula in formulas:
            equation_text = formula.strip()
            if "=" not in equation_text:
                valid = False
                break
            lhs_text, rhs_text = equation_text.split("=", 1)
            if lhs_text.strip() not in {periodic.variable, f"{periodic.variable} "}:
                valid = False
                break
            rhs_text = re.split(r",?\s*k\s*\\in", rhs_text, maxsplit=1)[0].strip()
            try:
                rhs = parse_latex_ast(rhs_text).to_sympy()
            except FormulaParseError:
                valid = False
                break
            k_symbols = [symbol for symbol in rhs.free_symbols if str(symbol) == "k"]
            if len(k_symbols) != 1:
                valid = False
                break
            k = k_symbols[0]
            candidate_period = sp.simplify(sp.Abs(rhs.coeff(k)))
            if not symbolic_equal(candidate_period, expected_period):
                valid = False
                break
            candidate_points.append(sp.simplify(rhs.subs(k, 0)))
        if not valid or len(candidate_points) != len(expected_points):
            continue
        unmatched = expected_points.copy()
        for candidate in candidate_points:
            hit = next(
                (
                    point
                    for point in unmatched
                    if sp.simplify((candidate - point) / expected_period).is_integer is True
                ),
                None,
            )
            if hit is None:
                valid = False
                break
            unmatched.remove(hit)
        if valid and not unmatched:
            matches.append(index)
    if len(matches) == 1:
        return chr(ord("A") + matches[0]), None
    if not matches:
        return None, "no option is symbolically equivalent to the periodic answer"
    return None, "multiple options are symbolically equivalent to the periodic answer"
