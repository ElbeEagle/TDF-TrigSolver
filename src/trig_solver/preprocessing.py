"""Formula extraction, normalization, and strict LaTeX-to-AST conversion."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import sympy as sp

from .models import ExprAST, ExpressionSpec, RawProblem


class FormulaParseError(ValueError):
    pass


@dataclass(frozen=True)
class PreprocessedProblem:
    question: str
    options: list[str]
    expressions: list[ExpressionSpec]
    needs_image: bool


MATH_PATTERN = re.compile(r"\$(.+?)\$|\\\((.+?)\\\)", re.DOTALL)
OPTION_PATTERN = re.compile(r"(?m)(?:^|\n)\s*([A-Da-d])\s*[\.、．·]\s*")
UNSUPPORTED_LATEX = re.compile(r"\\(?:includegraphics|begin\s*\{array\}|overset|underset|not\b)")
ALLOWED_LATEX_COMMANDS = {
    "alpha",
    "abs",
    "beta",
    "cdot",
    "circ",
    "cos",
    "displaystyle",
    "frac",
    "geq",
    "geqslant",
    "left",
    "leq",
    "leqslant",
    "pi",
    "phi",
    "right",
    "sin",
    "sqrt",
    "tan",
    "theta",
    "textstyle",
    "varphi",
    "omega",
}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    replacements = {
        "≤": r"\leq ",
        "≥": r"\geq ",
        "−": "-",
        "×": r"\cdot ",
        "π": r"\pi ",
        "；": ";",
        "，": ",",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"[ \t]+", " ", text).strip()


def split_options(options: list[str] | str | None) -> list[str]:
    if not options:
        return []
    if isinstance(options, list):
        return [normalize_text(str(item)) for item in options if str(item).strip()]
    matches = list(OPTION_PATTERN.finditer(options))
    if not matches:
        return [normalize_text(options)]
    result: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(options)
        result.append(normalize_text(options[match.end() : end]))
    return result


def extract_formula_strings(question: str) -> list[str]:
    formulas: list[str] = []
    for match in MATH_PATTERN.finditer(question):
        value = next(group for group in match.groups() if group is not None).strip()
        if value:
            formulas.append(value)
    return formulas


def _strip_assignment(latex: str) -> str:
    value = latex.strip().rstrip(".,;，。")
    value = re.sub(r"^\\(?:displaystyle|textstyle)\s*", "", value)
    value = re.sub(r"=\s*$", "", value).strip()
    assignment = re.match(r"^(?:[yf]\s*(?:\([^=]+\))?)\s*=\s*(.+)$", value, re.DOTALL)
    if assignment:
        return assignment.group(1).strip()
    return value


def _degrees_to_radians(latex: str) -> str:
    pattern = re.compile(r"(?P<atom>(?:\d+(?:\.\d+)?|\([^()]+\)))\s*\^\s*\{?\\circ\}?")
    while pattern.search(latex):
        latex = pattern.sub(lambda match: rf"\left(\frac{{{match.group('atom')}\pi}}{{180}}\right)", latex)
    return latex


def parse_latex_ast(latex: str) -> ExprAST:
    if not latex or len(latex) > 2000:
        raise FormulaParseError("empty or oversized formula")
    if UNSUPPORTED_LATEX.search(latex):
        raise FormulaParseError("formula contains unsupported layout or commands")
    commands = set(re.findall(r"\\([A-Za-z]+)", latex))
    unknown_commands = commands - ALLOWED_LATEX_COMMANDS
    if unknown_commands:
        raise FormulaParseError(f"formula contains unknown commands: {sorted(unknown_commands)}")
    normalized = _degrees_to_radians(_strip_assignment(latex))
    normalized = normalized.replace(r"\leqslant", r"\leq").replace(r"\geqslant", r"\geq")
    normalized = normalized.replace(r"\mathbf{R}", r"\mathbb{R}")
    try:
        from sympy.parsing.latex import parse_latex

        # SymPy 1.14's Lark grammar rejects the constant ``\\pi`` and returns
        # ambiguity trees for common forms such as ``\\sin^2 x+\\cos^2 x``.
        # ANTLR strict mode rejects partial input while the AST conversion below
        # remains the executable allowlist and node-budget boundary.
        expr = parse_latex(normalized, backend="antlr", strict=True)
    except Exception as exc:  # the external parser exposes several exception classes
        raise FormulaParseError(f"cannot parse formula {latex!r}: {exc}") from exc
    if not isinstance(expr, sp.Basic):
        raise FormulaParseError("formula did not produce a SymPy expression")
    try:
        ast = ExprAST.from_sympy(expr)
    except (TypeError, ValueError) as exc:
        raise FormulaParseError(str(exc)) from exc
    if ast.node_count() > 256:
        raise FormulaParseError("formula exceeds the 256-node safety limit")
    return ast


def preprocess_problem(problem: RawProblem) -> PreprocessedProblem:
    question = normalize_text(problem.question)
    visual_cue = bool(re.search(r"下图|如图|图象如下|图像如下|表中数据", question))
    needs_image = bool(problem.images) or visual_cue
    expressions: list[ExpressionSpec] = []
    failures: list[str] = []
    for index, latex in enumerate(extract_formula_strings(question), start=1):
        try:
            ast = parse_latex_ast(latex)
        except FormulaParseError as exc:
            failures.append(str(exc))
            continue
        expressions.append(ExpressionSpec(id=f"E{index}", source_latex=latex, ast=ast))
    if failures:
        raise FormulaParseError(failures[0])
    if not expressions:
        detail = failures[0] if failures else "no delimited mathematical expression was found"
        raise FormulaParseError(detail)
    return PreprocessedProblem(
        question=question,
        options=split_options(problem.options),
        expressions=expressions,
        needs_image=needs_image,
    )
    "beta",
