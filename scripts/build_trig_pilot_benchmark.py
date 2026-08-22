"""Build the reviewable pilot benchmark without modifying source CMM-Math data."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import sympy as sp

from trig_solver.models import (
    AngleState,
    ConstraintSpec,
    ExprAST,
    ExpressionSpec,
    GoldAnswer,
    GoalSpec,
    IntervalCell,
    PeriodicSet,
    RawProblem,
    TaskFamily,
    TrigURM,
)
from trig_solver.preprocessing import split_options
from trig_solver.qwen import QwenRawParser
from trig_solver.solver import _point_periodic_set


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "CMM-Math" / "data.jsonl"
ATOMIC_SOURCE_PATHS = (
    ROOT / "data" / "CMM-Math" / "明确多子题_118题_全部拆分_合并版.jsonl",
    ROOT / "data" / "CMM-Math" / "第二部分_潜在多子题_22题_全部原子化拆分_84条.jsonl",
)
OUTPUT_DIR = ROOT / "data" / "benchmarks" / "trig_pilot_v1"
LOCKED_TEST_SELECTION_SHA256 = "8e778f7754c29057027328d581db8fdcc0d998e3d9510be75696eb0ec2960fb3"
GOLD_SCHEMA_V02_SHA256 = "7f41b5d02ec4117c2cd676a06a55660d08e26d8a40c326cb7c87fda081a4ba09"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


SOURCE_ROWS: dict[str, dict[str, Any]] = {}
SOURCE_FILES: dict[str, str] = {}
for _source_path in (SOURCE_PATH, *ATOMIC_SOURCE_PATHS):
    for _row in _read_jsonl(_source_path):
        _source_id = str(_row["id"])
        SOURCE_ROWS[_source_id] = _row
        SOURCE_FILES[_source_id] = str(_source_path.relative_to(ROOT))
SOURCE_QUESTIONS = {source_id: str(row.get("question") or "") for source_id, row in SOURCE_ROWS.items()}
MAIN_SOURCE_IDS = {str(row["id"]) for row in _read_jsonl(SOURCE_PATH)}


def _parent_id(source_id: str) -> str:
    direct = source_id.split("-", 1)[0]
    if direct in MAIN_SOURCE_IDS:
        return direct
    if len(direct) > 5 and direct[:5] in MAIN_SOURCE_IDS:
        return direct[:5]
    return direct


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expression(expr: sp.Basic, identifier: str = "E1") -> ExpressionSpec:
    return ExpressionSpec(id=identifier, source_latex=sp.latex(expr), ast=ExprAST.from_sympy(expr))


def _urm(
    expression: sp.Basic,
    family: TaskFamily,
    operator: str,
    *,
    properties: list[str] | None = None,
    constraints: list[sp.Basic] | None = None,
    quadrant: int | None = None,
) -> TrigURM:
    symbols = sorted(expression.free_symbols, key=str)
    variable = symbols[0] if symbols else sp.Symbol("x", real=True)
    expressions = [_expression(expression)]
    constraint_specs: list[ConstraintSpec] = []
    for index, constraint in enumerate(constraints or [], start=2):
        expressions.append(_expression(constraint, f"E{index}"))
        constraint_specs.append(
            ConstraintSpec(
                kind="equation" if isinstance(constraint, sp.Equality) else "inequality",
                expression=ExprAST.from_sympy(constraint),
            )
        )
    return TrigURM(
        angles=[AngleState(symbol=str(variable), unit="radian", quadrant=quadrant)],
        expressions=expressions,
        constraints=constraint_specs,
        goal=GoalSpec(
            task_family=family,
            operator=operator,
            target_refs=["E1"],
            property_names=properties or [],
            completeness="all_real" if family == TaskFamily.EQUATION else "not_applicable",
        ),
    )


def _record(
    source_id: str,
    family: TaskFamily,
    question: str,
    expression: sp.Basic,
    operator: str,
    *,
    options: list[str] | None = None,
    gold_option: str | None = None,
    gold_value: Any,
    properties: list[str] | None = None,
    constraints: list[sp.Basic] | None = None,
    quadrant: int | None = None,
    template_group: str,
) -> dict[str, Any]:
    parent_id = _parent_id(source_id)
    source_question = SOURCE_QUESTIONS.get(parent_id)
    structured_gold = GoldAnswer.from_value(gold_value).model_dump(mode="json")
    return {
        "source_id": source_id,
        "split": "dev",
        "task_family": family,
        "problem": RawProblem(question=question, options=options or [], source_id=source_id).model_dump(mode="json"),
        "oracle_urm": _urm(
            expression,
            family,
            operator,
            properties=properties,
            constraints=constraints,
            quadrant=quadrant,
        ).model_dump(mode="json"),
        "gold_option": gold_option,
        "gold_answer": structured_gold,
        "template_group": template_group,
        "provenance": "cmm_atomized",
        "source_question_sha256": _sha256_text(source_question) if source_question is not None else None,
        "review": {"status": "machine_prepared", "annotator": "benchmark_builder"},
    }


def build_dev() -> list[dict[str, Any]]:
    x = sp.Symbol("x", real=True)
    alpha = sp.Symbol("alpha", real=True)
    records: list[dict[str, Any]] = []

    # EVAL: two multiple choice and three open atomizations.
    records.extend(
        [
            _record("2449-eval", TaskFamily.EVAL, r"计算 $\sin 30^{\circ}$。", sp.sin(sp.pi / 6), "evaluate", gold_value=sp.Rational(1, 2), options=["$0$", "$\\frac{1}{2}$", "$\\frac{\\sqrt{3}}{2}$", "$1$"], gold_option="B", template_group="eval-special-sin"),
            _record("18061-eval", TaskFamily.EVAL, r"计算 $\frac{1-\tan 15^{\circ}}{1+\tan 15^{\circ}}$。", (1-sp.tan(sp.pi/12))/(1+sp.tan(sp.pi/12)), "evaluate", gold_value=sp.sqrt(3)/3, options=["$-\\sqrt{3}$", "$\\sqrt{3}$", "$\\frac{\\sqrt{3}}{3}$", "$\\frac{1}{2}$"], gold_option="C", template_group="eval-tan-addition"),
            _record("18042-eval", TaskFamily.EVAL, r"计算 $\cos 45^{\circ}\cos 15^{\circ}+\sin 45^{\circ}\sin 15^{\circ}$。", sp.cos(sp.pi/4)*sp.cos(sp.pi/12)+sp.sin(sp.pi/4)*sp.sin(sp.pi/12), "evaluate", gold_value=sp.sqrt(3)/2, template_group="eval-cos-difference"),
            _record("18045-eval", TaskFamily.EVAL, r"求 $\frac{2\cos 10^{\circ}-\sin 20^{\circ}}{\sin 70^{\circ}}$ 的值。", (2*sp.cos(sp.pi/18)-sp.sin(sp.pi/9))/sp.sin(7*sp.pi/18), "evaluate", gold_value=sp.sqrt(3), template_group="eval-special-transform"),
            _record("17750-eval", TaskFamily.EVAL, r"已知 $\tan\alpha=-\frac{5}{12}$，且 $\alpha$ 为第四象限角，求 $\sin\alpha$。", sp.sin(alpha), "evaluate", gold_value=-sp.Rational(5, 13), constraints=[sp.Eq(sp.tan(alpha), -sp.Rational(5,12))], quadrant=4, template_group="eval-quadrant-given-tan"),
        ]
    )

    # IDENTITY.
    records.extend(
        [
            _record("17762-identity-mc", TaskFamily.IDENTITY, r"化简 $\sin^2x+\cos^2x$。", sp.sin(x)**2+sp.cos(x)**2, "simplify", gold_value=sp.Integer(1), options=["$0$", "$1$", "$2$", "$\\sin 2x$"], gold_option="B", template_group="identity-pythagorean"),
            _record("18273-identity-mc", TaskFamily.IDENTITY, r"化简 $(1+\tan^2x)\cos^2x$。", (1+sp.tan(x)**2)*sp.cos(x)**2, "simplify", gold_value=sp.Integer(1), options=["$0$", "$\\sin^2x$", "$1$", "$\\cos^2x$"], gold_option="C", template_group="identity-sec-tan"),
            _record("18060-identity", TaskFamily.IDENTITY, r"化简 $\sin(x+\frac{\pi}{2})-\cos x$。", sp.sin(x+sp.pi/2)-sp.cos(x), "simplify", gold_value=sp.Integer(0), template_group="identity-cofunction"),
            _record("18267-identity", TaskFamily.IDENTITY, r"化简 $\frac{\tan x\cos x}{\sin x}$。", sp.tan(x)*sp.cos(x)/sp.sin(x), "simplify", gold_value=sp.Integer(1), template_group="identity-quotient"),
            _record("18202-identity", TaskFamily.IDENTITY, r"化简 $2\sin x\cos x-\sin 2x$。", 2*sp.sin(x)*sp.cos(x)-sp.sin(2*x), "simplify", gold_value=sp.Integer(0), template_group="identity-double-angle"),
        ]
    )

    # SINUSOID_PROPERTY.
    records.extend(
        [
            _record("17859-amplitude", TaskFamily.SINUSOID_PROPERTY, r"函数 $y=3\sin(2x+\frac{\pi}{3})-1$ 的振幅是（ ）。", 3*sp.sin(2*x+sp.pi/3)-1, "property", gold_value=sp.Integer(3), properties=["amplitude"], options=["$1$", "$2$", "$3$", "$6$"], gold_option="C", template_group="property-amplitude"),
            _record("1811303-period", TaskFamily.SINUSOID_PROPERTY, r"函数 $y=2\sin(\frac{x}{2}+\frac{\pi}{6})$ 的最小正周期是（ ）。", 2*sp.sin(x/2+sp.pi/6), "property", gold_value=4*sp.pi, properties=["period"], options=["$\\pi$", "$2\\pi$", "$3\\pi$", "$4\\pi$"], gold_option="D", template_group="property-period"),
            _record("17542-phase", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=\sin(2x-\frac{\pi}{3})$ 的相位平移量。", sp.sin(2*x-sp.pi/3, evaluate=False), "property", gold_value=sp.pi/6, properties=["phase_shift"], template_group="property-phase"),
            _record("1745901-maximum", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=3+2\cos(2x+\frac{\pi}{3})$ 的最大值。", 3+2*sp.cos(2*x+sp.pi/3), "property", gold_value=sp.Integer(5), properties=["maximum"], template_group="property-maximum"),
            _record("18114-axis", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=2\sin(2x-\frac{\pi}{4})$ 的全部对称轴。", 2*sp.sin(2*x-sp.pi/4), "property", gold_value=_point_periodic_set(x, sp.pi/2, [3*sp.pi/8]), properties=["symmetry_axis"], template_group="property-symmetry-axis"),
        ]
    )

    # EQUATION. These are explicit single-goal atomizations of equation patterns
    # in the source corpus so periodic completeness can be evaluated directly.
    equation_specs = [
        ("17805-equation-mc", sp.Eq(sp.sin(x), sp.Rational(1,2)), [r"$x=2k\pi+\frac{\pi}{6}$ 或 $x=2k\pi+\frac{5\pi}{6}$", r"$x=k\pi+\frac{\pi}{6}$", r"$x=2k\pi+\frac{\pi}{3}$ 或 $x=2k\pi+\frac{2\pi}{3}$", r"$x=2k\pi-\frac{\pi}{6}$ 或 $x=2k\pi+\frac{7\pi}{6}$"], "A", "equation-sin", _point_periodic_set(x, 2*sp.pi, [sp.pi/6, 5*sp.pi/6])),
        ("18125-equation-mc", sp.Eq(sp.tan(2*x), 1), [r"$x=k\pi+\frac{\pi}{4}$", r"$x=\frac{k\pi}{2}+\frac{\pi}{8}$", r"$x=2k\pi+\frac{\pi}{8}$", r"$x=\frac{k\pi}{2}+\frac{\pi}{4}$"], "B", "equation-tan-affine", _point_periodic_set(x, sp.pi/2, [sp.pi/8])),
    ]
    for source_id, equation, options, gold, group, expected in equation_specs:
        records.append(_record(source_id, TaskFamily.EQUATION, f"解方程 ${sp.latex(equation)}$，给出全部实数解。", equation, "solve_equation", gold_value=expected, options=options, gold_option=gold, template_group=group))
    for source_id, equation, group in [
        ("17445-equation-cos", sp.Eq(sp.cos(x), 0), "equation-cos"),
        ("1841102-equation-affine", sp.Eq(sp.sin(2*x-sp.pi/3), 0), "equation-sin-affine"),
        ("3607-equation-quadratic", sp.Eq(2*sp.sin(x)**2-sp.sin(x)-1, 0), "equation-quadratic-same-atom"),
    ]:
        expected = {
            "17445-equation-cos": _point_periodic_set(x, 2*sp.pi, [sp.pi/2, 3*sp.pi/2]),
            "1841102-equation-affine": _point_periodic_set(x, sp.pi, [sp.pi/6, 2*sp.pi/3]),
            "3607-equation-quadratic": _point_periodic_set(x, 2*sp.pi, [sp.pi/2, 7*sp.pi/6, 11*sp.pi/6]),
        }[source_id]
        records.append(_record(source_id, TaskFamily.EQUATION, f"解方程 ${sp.latex(equation)}$，给出全部实数解。", equation, "solve_equation", gold_value=expected, template_group=group))

    # DOMAIN_RANGE_INEQUALITY.
    records.extend(
        [
            _record("1762104-range-mc", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"函数 $y=2\sin x+3$ 的值域是（ ）。", 2*sp.sin(x)+3, "range", gold_value=sp.Interval(1, 5), options=["$[-2,3]$", "$[1,5]$", "$[-1,5]$", "$[2,5]$"], gold_option="B", template_group="range-sine-affine"),
            _record("1745902-range-mc", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"函数 $y=-3\cos(2x)+1$ 的值域是（ ）。", -3*sp.cos(2*x)+1, "range", gold_value=sp.Interval(-2, 4), options=["$[-3,3]$", "$[-4,2]$", "$[-2,4]$", "$[-3,4]$"], gold_option="C", template_group="range-cosine-affine"),
            _record("1729401-domain", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"求函数 $y=\sqrt{1-\sin x}$ 的定义域。", sp.sqrt(1-sp.sin(x)), "domain", gold_value=sp.S.Reals, template_group="domain-radical-nonnegative"),
            _record("17742-inequality", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"解不等式 $\sin x\leq\cos x$，给出全部实数解。", sp.Le(sp.sin(x), sp.cos(x)), "solve_inequality", gold_value=PeriodicSet(period=ExprAST.from_sympy(2*sp.pi), intervals=[IntervalCell(start=ExprAST.from_sympy(sp.Integer(0)), end=ExprAST.from_sympy(sp.pi/4)), IntervalCell(start=ExprAST.from_sympy(5*sp.pi/4), end=ExprAST.from_sympy(2*sp.pi))]), template_group="inequality-sin-cos"),
            _record("18386-inequality", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"解不等式 $\tan x>0$，给出全部实数解。", sp.Gt(sp.tan(x), 0), "solve_inequality", gold_value=PeriodicSet(period=ExprAST.from_sympy(sp.pi), intervals=[IntervalCell(start=ExprAST.from_sympy(sp.Integer(0)), end=ExprAST.from_sympy(sp.pi/2), left_open=True, right_open=True)]), template_group="inequality-tan-sign"),
        ]
    )
    assert len(records) == 25
    for family in TaskFamily:
        family_rows = [row for row in records if row["task_family"] == family]
        assert len(family_rows) == 5
        assert sum(bool(row["problem"]["options"]) for row in family_rows) == 2
    return records


def _candidate_family(question: str) -> TaskFamily | None:
    rules = [
        (TaskFamily.EQUATION, r"解方程|方程.*解|所有实数解|全部实数解"),
        (TaskFamily.DOMAIN_RANGE_INEQUALITY, r"定义域|值域|不等式|取值范围"),
        (TaskFamily.SINUSOID_PROPERTY, r"周期|振幅|相位|单调|对称|最值|最大值|最小值|平移"),
        (TaskFamily.IDENTITY, r"化简|恒等式|求证|证明"),
        (TaskFamily.EVAL, r"求值|计算|等于|的值是|的值为"),
    ]
    for family, pattern in rules:
        if re.search(pattern, question):
            return family
    return None


def _direct_spec(
    source_id: str,
    family: TaskFamily,
    output_format: str,
    template_group: str,
    *,
    options_override: list[str] | None = None,
    transformation: str | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "family": family,
        "output_format": output_format,
        "template_group": template_group,
        "question_override": None,
        "options_override": options_override,
        "provenance": "cmm_atomized" if source_id not in MAIN_SOURCE_IDS else "cmm_direct",
        "transformation": transformation,
    }


def _equation_spec(
    source_id: str,
    output_format: str,
    template_group: str,
    question: str,
    options: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "family": TaskFamily.EQUATION,
        "output_format": output_format,
        "template_group": template_group,
        "question_override": question,
        "options_override": options or [],
        "provenance": "cmm_equation_reframed",
        "transformation": (
            "Extract the source problem's explicit trigonometric equation and ask for its complete "
            "real solution set; no new mathematical constants or external data were introduced."
        ),
    }


def test_selection_specs() -> list[dict[str, Any]]:
    specs = [
        # EVAL: five multiple-choice and five open questions.
        _direct_spec("18032", TaskFamily.EVAL, "multiple_choice", "eval-cos-supplement-transform"),
        _direct_spec("18046", TaskFamily.EVAL, "multiple_choice", "eval-sine-supplement-special"),
        _direct_spec("18068", TaskFamily.EVAL, "multiple_choice", "eval-tangent-sum-reciprocal"),
        _direct_spec("17906", TaskFamily.EVAL, "multiple_choice", "eval-unit-circle-coordinate"),
        _direct_spec("17772", TaskFamily.EVAL, "multiple_choice", "eval-quadrant-induction"),
        _direct_spec("17767", TaskFamily.EVAL, "open", "eval-large-angle-ratio"),
        _direct_spec("17788", TaskFamily.EVAL, "open", "eval-periodic-induction-parameter"),
        _direct_spec("17789", TaskFamily.EVAL, "open", "eval-linear-relation-product"),
        _direct_spec("3597", TaskFamily.EVAL, "open", "eval-special-angle-product"),
        _direct_spec("17608", TaskFamily.EVAL, "open", "eval-ratio-to-double-angle"),
        # IDENTITY.
        _direct_spec("17785", TaskFamily.IDENTITY, "multiple_choice", "identity-induction-rational"),
        _direct_spec("18257", TaskFamily.IDENTITY, "multiple_choice", "identity-double-angle-ratio-special"),
        _direct_spec(
            "17606",
            TaskFamily.IDENTITY,
            "multiple_choice",
            "identity-half-angle-square-combination",
            options_override=[
                r"$2+\sin\alpha$",
                r"$2+\sqrt{2}\sin\left(\alpha-\frac{\pi}{4}\right)$",
                r"$2$",
                r"$2+\sqrt{2}\sin\left(\alpha+\frac{\pi}{4}\right)$",
            ],
            transformation="Normalize the malformed C-option label; mathematical option contents are unchanged.",
        ),
        _direct_spec("17513", TaskFamily.IDENTITY, "multiple_choice", "identity-radical-sign-reduction"),
        _direct_spec("18085", TaskFamily.IDENTITY, "multiple_choice", "identity-half-angle-radical"),
        _direct_spec("18093", TaskFamily.IDENTITY, "open", "identity-radical-quadrant-half-angle"),
        _direct_spec("17903", TaskFamily.IDENTITY, "open", "identity-radical-unit-circle-sign"),
        _direct_spec("17357", TaskFamily.IDENTITY, "open", "identity-rational-proof"),
        _direct_spec("17360", TaskFamily.IDENTITY, "open", "identity-radical-quotient-quadrant"),
        _direct_spec("18277", TaskFamily.IDENTITY, "open", "identity-polynomial-two-angle"),
        # SINUSOID_PROPERTY.
        _direct_spec("17824", TaskFamily.SINUSOID_PROPERTY, "multiple_choice", "property-monotonic-interval"),
        _direct_spec("17825", TaskFamily.SINUSOID_PROPERTY, "multiple_choice", "property-symmetry-phase-parameter"),
        _direct_spec("17817", TaskFamily.SINUSOID_PROPERTY, "multiple_choice", "property-symmetry-center"),
        _direct_spec("17843", TaskFamily.SINUSOID_PROPERTY, "multiple_choice", "property-graph-horizontal-shift"),
        _direct_spec("17549", TaskFamily.SINUSOID_PROPERTY, "multiple_choice", "property-period-to-symmetry-axis"),
        _direct_spec("17864", TaskFamily.SINUSOID_PROPERTY, "open", "property-phase-from-point-then-monotonic"),
        _direct_spec("17863", TaskFamily.SINUSOID_PROPERTY, "open", "property-integer-frequency-from-monotonic"),
        _direct_spec("18109", TaskFamily.SINUSOID_PROPERTY, "open", "property-phase-from-extremum-restricted-monotonic"),
        _direct_spec("17638", TaskFamily.SINUSOID_PROPERTY, "open", "property-frequency-from-monotonic-change"),
        _direct_spec("1742002", TaskFamily.SINUSOID_PROPERTY, "open", "property-absolute-sine-period"),
        # EQUATION: every stem explicitly requests all real solutions.
        _equation_spec(
            "17774",
            "multiple_choice",
            "equation-induction-linear-complete",
            r"解方程 $\sin(\pi+x)=-\sqrt{3}\cos(2\pi-x)$，给出全部实数解，其中 $k$ 为整数。",
            [
                r"$x=k\pi+\frac{\pi}{3}$",
                r"$x=2k\pi+\frac{\pi}{3}$",
                r"$x=k\pi-\frac{\pi}{3}$",
                r"$x=k\pi+\frac{2\pi}{3}$",
            ],
        ),
        _equation_spec(
            "17756",
            "multiple_choice",
            "equation-sin-cos-ratio-complete",
            r"解方程 $\sin x=2\cos x$，给出全部实数解，其中 $k$ 为整数。",
            [
                r"$x=\arctan 2+k\pi$",
                r"$x=\arctan 2+2k\pi$",
                r"$x=-\arctan 2+k\pi$",
                r"$x=\arctan\frac{1}{2}+k\pi$",
            ],
        ),
        _equation_spec(
            "18078",
            "multiple_choice",
            "equation-tangent-reciprocal-quadratic-complete",
            r"解方程 $\tan x+\frac{1}{\tan x}=4$，给出全部实数解，其中 $k$ 为整数。",
            [
                r"$x=k\pi+\frac{\pi}{12}$ 或 $x=k\pi+\frac{5\pi}{12}$",
                r"$x=k\pi+\frac{\pi}{6}$ 或 $x=k\pi+\frac{\pi}{3}$",
                r"$x=2k\pi+\frac{\pi}{12}$ 或 $x=2k\pi+\frac{5\pi}{12}$",
                r"$x=k\pi-\frac{\pi}{12}$ 或 $x=k\pi-\frac{5\pi}{12}$",
            ],
        ),
        _equation_spec(
            "17524",
            "multiple_choice",
            "equation-squared-double-angle-complete",
            r"解方程 $\sin^2x+\cos 2x=\frac{1}{4}$，给出全部实数解，其中 $k$ 为整数。",
            [
                r"$x=k\pi\pm\frac{\pi}{3}$",
                r"$x=2k\pi\pm\frac{\pi}{3}$",
                r"$x=k\pi\pm\frac{\pi}{6}$",
                r"$x=2k\pi\pm\frac{2\pi}{3}$",
            ],
        ),
        _equation_spec(
            "18084",
            "multiple_choice",
            "equation-sine-double-angle-nonspecial-complete",
            r"解方程 $\sin 2x=\frac{2}{3}$，给出全部实数解，其中 $k$ 为整数。",
            [
                r"$x=\frac{1}{2}\arcsin\frac{2}{3}+k\pi$ 或 $x=\frac{\pi}{2}-\frac{1}{2}\arcsin\frac{2}{3}+k\pi$",
                r"$x=\arcsin\frac{2}{3}+2k\pi$ 或 $x=\pi-\arcsin\frac{2}{3}+2k\pi$",
                r"$x=\frac{1}{2}\arcsin\frac{2}{3}+2k\pi$ 或 $x=\frac{\pi}{2}-\frac{1}{2}\arcsin\frac{2}{3}+2k\pi$",
                r"$x=\frac{1}{2}\arccos\frac{2}{3}+k\pi$ 或 $x=\frac{\pi}{2}-\frac{1}{2}\arccos\frac{2}{3}+k\pi$",
            ],
        ),
        _equation_spec("17758", "open", "equation-linear-combination-nonspecial-complete", r"解方程 $\sin x-\cos x=\frac{4}{3}$，给出全部实数解。"),
        _equation_spec("17765", "open", "equation-induction-linear-combination-complete", r"解方程 $\sin(\pi-x)-\cos(-x)=\frac{1}{2}$，给出全部实数解。"),
        _equation_spec("18048", "open", "equation-shifted-cosine-nonspecial-complete", r"解方程 $\cos\left(x-\frac{\pi}{6}\right)=\frac{1}{3}$，给出全部实数解。"),
        _equation_spec("18394", "open", "equation-product-to-double-angle-complete", r"解方程 $\sin x\cos x=\frac{1}{8}$，给出全部实数解。"),
        _equation_spec("18091", "open", "equation-shifted-sine-nonspecial-complete", r"解方程 $\sin\left(x+\frac{\pi}{4}\right)=-\frac{5}{13}$，给出全部实数解。"),
        # DOMAIN_RANGE_INEQUALITY.
        _direct_spec("17743", TaskFamily.DOMAIN_RANGE_INEQUALITY, "multiple_choice", "domain-tangent-affine"),
        _direct_spec("18056", TaskFamily.DOMAIN_RANGE_INEQUALITY, "multiple_choice", "range-parameter-linear-combination"),
        _direct_spec("3606", TaskFamily.DOMAIN_RANGE_INEQUALITY, "multiple_choice", "inequality-acute-angle-cosine"),
        _direct_spec(
            "17464",
            TaskFamily.DOMAIN_RANGE_INEQUALITY,
            "multiple_choice",
            "range-absolute-sine",
            options_override=[r"$[-1,1]$", r"$[-2,2]$", r"$[-2,0]$", r"$[0,2]$"],
            transformation="Normalize the malformed C-option label; mathematical option contents are unchanged.",
        ),
        _direct_spec("18195", TaskFamily.DOMAIN_RANGE_INEQUALITY, "multiple_choice", "domain-radical-cosine"),
        _direct_spec("17745", TaskFamily.DOMAIN_RANGE_INEQUALITY, "open", "range-sine-restricted-interval"),
        _direct_spec("17297", TaskFamily.DOMAIN_RANGE_INEQUALITY, "open", "inequality-cosine-periodic"),
        _direct_spec("17833", TaskFamily.DOMAIN_RANGE_INEQUALITY, "open", "range-tangent-quadratic-restricted"),
        _direct_spec("17901", TaskFamily.DOMAIN_RANGE_INEQUALITY, "open", "range-sign-piecewise-finite"),
        _direct_spec("17617", TaskFamily.DOMAIN_RANGE_INEQUALITY, "open", "range-polynomial-sine-restricted"),
    ]
    assert len(specs) == 50
    assert len({spec["source_id"] for spec in specs}) == 50
    for family in TaskFamily:
        family_specs = [spec for spec in specs if spec["family"] == family]
        assert len(family_specs) == 10
        assert sum(spec["output_format"] == "multiple_choice" for spec in family_specs) == 5
    return specs


def _template_hash(question: str) -> str:
    skeleton = re.sub(r"\d+", "N", re.sub(r"\$.*?\$", "<FORMULA>", question, flags=re.DOTALL))
    return _sha256_text(re.sub(r"\s+", "", skeleton))


def _candidate_record(source_id: str, family: TaskFamily) -> dict[str, Any]:
    row = SOURCE_ROWS[source_id]
    question = str(row.get("question") or "")
    options = split_options(row.get("options"))
    return {
        "source_id": source_id,
        "source_parent_id": _parent_id(source_id),
        "source_file": SOURCE_FILES[source_id],
        "task_family_candidate": family,
        "output_format_candidate": "multiple_choice" if options else "open",
        "question": question,
        "options": options,
        "question_sha256": _sha256_text(question),
        "template_group_candidate": _template_hash(question)[:16],
        "provenance": "cmm_atomized" if source_id not in MAIN_SOURCE_IDS else "cmm_direct",
    }


def build_test_candidates(dev: list[dict[str, Any]], specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a high-recall, source-only pool of 30 candidates per family."""

    dev_parents = {_parent_id(row["source_id"]) for row in dev}
    selected_by_family = {
        family: [spec["source_id"] for spec in specs if spec["family"] == family]
        for family in TaskFamily
    }
    eligible: list[tuple[str, TaskFamily]] = []
    equation_reframe_eligible: list[str] = []
    for source_id, row in SOURCE_ROWS.items():
        question = str(row.get("question") or "")
        if _parent_id(source_id) in dev_parents:
            continue
        if row.get("image") or "<ImageHere>" in question:
            continue
        if not re.search(r"\\(?:sin|cos|tan)|正弦|余弦|正切|三角", question, flags=re.IGNORECASE):
            continue
        if (
            "=" in question
            and not re.search(r"\([1-9]\)|（[1-9]）|求下列|分别求", question)
            and not re.search(r"向量|三角形|边长|面积|轨迹|圆锥|立体", question)
        ):
            equation_reframe_eligible.append(source_id)
        family = _candidate_family(question)
        if family is not None:
            eligible.append((source_id, family))

    candidates: list[dict[str, Any]] = []
    used_sources = {spec["source_id"] for spec in specs}
    for family in TaskFamily:
        bucket: list[str] = []
        for source_id in selected_by_family[family]:
            if source_id not in SOURCE_ROWS:
                raise ValueError(f"selected source record is missing: {source_id}")
            if _parent_id(source_id) in dev_parents:
                raise ValueError(f"selected test source shares a parent with development: {source_id}")
            bucket.append(source_id)
        seen_parents = {_parent_id(source_id) for source_id in bucket}
        seen_questions = {_sha256_text(SOURCE_QUESTIONS[source_id]) for source_id in bucket}
        family_eligible = [source_id for source_id, candidate_family in eligible if candidate_family == family]
        if family == TaskFamily.EQUATION:
            family_eligible.extend(equation_reframe_eligible)
        for source_id in family_eligible:
            if len(bucket) == 30:
                break
            if source_id in used_sources:
                continue
            parent_id = _parent_id(source_id)
            question_hash = _sha256_text(SOURCE_QUESTIONS[source_id])
            if parent_id in seen_parents or question_hash in seen_questions:
                continue
            bucket.append(source_id)
            used_sources.add(source_id)
            seen_parents.add(parent_id)
            seen_questions.add(question_hash)
        if len(bucket) != 30:
            raise ValueError(f"insufficient {family} candidates: expected 30, got {len(bucket)}")
        candidates.extend(_candidate_record(source_id, family) for source_id in bucket)
    assert len(candidates) == 150
    return candidates


def _rejection_reason(candidate: dict[str, Any]) -> str:
    question = candidate["question"]
    if re.search(r"答案[:：]|解析[:：]|故选|正确选项", question):
        return "answer_or_solution_leakage_in_question"
    if re.search(r"\([1-9]\)|（[1-9]）|求下列|分别求", question):
        return "multiple_targets_or_non_atomic_stem"
    if re.search(r"向量|三角形|边长|面积|轨迹|圆锥|立体", question):
        return "mixed_context_outside_direct_trigonometric_scope"
    if candidate["task_family_candidate"] == TaskFamily.EQUATION:
        return "not_a_complete_all_real_basic_equation_item"
    return "not_selected_after_scope_quota_and_template_balance"


def build_selection_audit(candidates: list[dict[str, Any]], specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = {spec["source_id"]: spec for spec in specs}
    audit: list[dict[str, Any]] = []
    for candidate in candidates:
        spec = selected.get(candidate["source_id"])
        if spec is None:
            decision = "rejected"
            reason = _rejection_reason(candidate)
            selected_id = None
        else:
            decision = "selected"
            reason = "in_scope_single_target_and_selected_for_family_output_template_balance"
            selected_id = f"{candidate['source_id']}-test"
        audit.append(
            {
                "source_id": candidate["source_id"],
                "task_family_candidate": candidate["task_family_candidate"],
                "decision": decision,
                "reason_code": reason,
                "selection_id": selected_id,
                "screening_basis": "research_scope_and_benchmark_composition_only",
                "solver_prediction_consulted": False,
                "reviewer": "codex_scope_audit",
            }
        )
    assert sum(row["decision"] == "selected" for row in audit) == 50
    return audit


def build_test_selection(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for spec in specs:
        source_id = spec["source_id"]
        source_row = SOURCE_ROWS[source_id]
        source_question = str(source_row.get("question") or "")
        question = spec["question_override"] or source_question
        options = spec["options_override"]
        if options is None:
            options = split_options(source_row.get("options"))
        if spec["output_format"] == "multiple_choice" and len(options) != 4:
            raise ValueError(f"multiple-choice selection requires four options: {source_id}")
        if spec["output_format"] == "open" and options:
            raise ValueError(f"open selection must not contain options: {source_id}")
        selection_id = f"{source_id}-test"
        selected.append(
            {
                "source_id": selection_id,
                "source_record_id": source_id,
                "source_parent_id": _parent_id(source_id),
                "source_file": SOURCE_FILES[source_id],
                "split": "test_selection",
                "task_family": spec["family"],
                "output_format": spec["output_format"],
                "problem": RawProblem(question=question, options=options, source_id=selection_id).model_dump(mode="json"),
                "template_group": spec["template_group"],
                "provenance": spec["provenance"],
                "source_question_sha256": _sha256_text(source_question),
                "question_sha256": _sha256_text(question),
                "transformation_note": spec["transformation"],
                "selection_review": {
                    "status": "locked",
                    "reviewer": "codex_scope_audit",
                    "basis": "research_scope_only",
                    "solver_prediction_consulted": False,
                },
                "gold_review": {
                    "status": "pending_independent_human_annotation",
                    "annotator": None,
                    "independent_reviewer": None,
                },
            }
        )
    assert len(selected) == 50
    assert len({row["template_group"] for row in selected}) == 50
    return selected


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = build_dev()
    dev_path = OUTPUT_DIR / "dev.jsonl"
    dev_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in dev), encoding="utf-8")
    specs = test_selection_specs()
    candidates = build_test_candidates(dev, specs)
    candidates_path = OUTPUT_DIR / "test_candidates.jsonl"
    candidates_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
    audit = build_selection_audit(candidates, specs)
    audit_path = OUTPUT_DIR / "test_selection_audit.jsonl"
    audit_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in audit), encoding="utf-8")
    selection = build_test_selection(specs)
    dev_templates = {row["template_group"] for row in dev}
    test_templates = {row["template_group"] for row in selection}
    if dev_templates & test_templates:
        raise RuntimeError("development and test selection share a template group")
    dev_parents = {_parent_id(row["source_id"]) for row in dev}
    test_parents = {row["source_parent_id"] for row in selection}
    if dev_parents & test_parents:
        raise RuntimeError("development and test selection share a source parent")
    if len(test_parents) != len(selection):
        raise RuntimeError("test selection contains multiple records from one source parent")
    selection_path = OUTPUT_DIR / "test_selection.jsonl"
    selection_content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selection)
    selection_sha256 = _sha256_text(selection_content)
    if selection_sha256 != LOCKED_TEST_SELECTION_SHA256:
        raise RuntimeError("test selection differs from the locked 50-question composition")
    selection_path.write_text(selection_content, encoding="utf-8")
    annotation_template = [
        {
            **row,
            "split": "test",
            "oracle_urm": None,
            "gold_answer": None,
            "gold_option": None,
            "annotation": {
                "annotator": None,
                "annotation_status": "pending",
                "independent_reviewer": None,
                "adjudication_status": "pending",
                "notes": None,
            },
        }
        for row in selection
    ]
    annotation_path = OUTPUT_DIR / "test_annotation_template.jsonl"
    annotation_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in annotation_template),
        encoding="utf-8",
    )
    gold_schema_path = OUTPUT_DIR / "gold_answer.schema.json"
    gold_schema_content = json.dumps(GoldAnswer.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
    gold_schema_sha256 = _sha256_text(gold_schema_content)
    if gold_schema_sha256 != GOLD_SCHEMA_V02_SHA256:
        raise RuntimeError("GoldAnswer JSON schema differs from frozen v0.2")
    gold_schema_path.write_text(gold_schema_content, encoding="utf-8")
    manifest = {
        "schema_version": "0.2",
        "gold_schema_version": "0.2",
        "frozen": False,
        "selection_frozen": True,
        "source_path": "data/CMM-Math/data.jsonl",
        "allowed_source_files": [
            str(SOURCE_PATH.relative_to(ROOT)),
            *(str(path.relative_to(ROOT)) for path in ATOMIC_SOURCE_PATHS),
        ],
        "source_sha256": hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(),
        "dev_count": len(dev),
        "dev_sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(),
        "test_candidate_count": len(candidates),
        "test_candidate_sha256": hashlib.sha256(candidates_path.read_bytes()).hexdigest(),
        "test_selection_audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        "test_selection_count": len(selection),
        "test_selection_sha256": selection_sha256,
        "test_annotation_template_sha256": hashlib.sha256(annotation_path.read_bytes()).hexdigest(),
        "gold_schema_sha256": gold_schema_sha256,
        "test_sha256": None,
        "prompt_sha256": QwenRawParser.prompt_hash(),
        "freeze_blocker": (
            "The 50 questions are selection-locked, but Oracle-URM and structured mathematical Gold "
            "still require independent human annotation and adjudication before test.jsonl can be frozen."
        ),
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
