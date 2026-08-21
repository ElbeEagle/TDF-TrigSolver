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
    GoalSpec,
    RawProblem,
    TaskFamily,
    TrigURM,
)
from trig_solver.qwen import QwenRawParser
from trig_solver.solver import _point_periodic_set
from trig_solver.validator import render_periodic, render_value


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "CMM-Math" / "data.jsonl"
OUTPUT_DIR = ROOT / "data" / "benchmarks" / "trig_pilot_v1"
SOURCE_QUESTIONS = {
    str(row["id"]): str(row.get("question") or "")
    for row in (json.loads(line) for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines())
}
for _atomic_source in (
    ROOT / "data" / "CMM-Math" / "明确多子题_118题_全部拆分_合并版.jsonl",
    ROOT / "data" / "CMM-Math" / "第二部分_潜在多子题_22题_全部原子化拆分_84条.jsonl",
):
    SOURCE_QUESTIONS.update(
        {
            str(row["id"]): str(row.get("question") or "")
            for row in (json.loads(line) for line in _atomic_source.read_text(encoding="utf-8").splitlines())
        }
    )


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
    gold_answer: str | None = None,
    properties: list[str] | None = None,
    constraints: list[sp.Basic] | None = None,
    quadrant: int | None = None,
    template_group: str,
) -> dict[str, Any]:
    parent_id = source_id.split("-", 1)[0]
    source_question = SOURCE_QUESTIONS.get(parent_id)
    if gold_answer is not None:
        if family == TaskFamily.EQUATION or operator == "solve_inequality" or (properties and properties[0].startswith("symmetry_")):
            gold_kind = "periodic_set"
        elif operator in {"domain", "range"}:
            gold_kind = "set"
        elif family == TaskFamily.IDENTITY:
            gold_kind = "expression"
        else:
            gold_kind = "scalar"
        structured_gold: dict[str, str] | None = {"kind": gold_kind, "canonical": gold_answer}
    else:
        structured_gold = None
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
            _record("2449-eval", TaskFamily.EVAL, r"计算 $\sin 30^{\circ}$。", sp.sin(sp.pi / 6), "evaluate", options=["$0$", "$\\frac{1}{2}$", "$\\frac{\\sqrt{3}}{2}$", "$1$"], gold_option="B", template_group="eval-special-sin"),
            _record("18061-eval", TaskFamily.EVAL, r"计算 $\frac{1-\tan 15^{\circ}}{1+\tan 15^{\circ}}$。", (1-sp.tan(sp.pi/12))/(1+sp.tan(sp.pi/12)), "evaluate", options=["$-\\sqrt{3}$", "$\\sqrt{3}$", "$\\frac{\\sqrt{3}}{3}$", "$\\frac{1}{2}$"], gold_option="C", template_group="eval-tan-addition"),
            _record("18042-eval", TaskFamily.EVAL, r"计算 $\cos 45^{\circ}\cos 15^{\circ}+\sin 45^{\circ}\sin 15^{\circ}$。", sp.cos(sp.pi/4)*sp.cos(sp.pi/12)+sp.sin(sp.pi/4)*sp.sin(sp.pi/12), "evaluate", gold_answer=r"\frac{\sqrt{3}}{2}", template_group="eval-cos-difference"),
            _record("18045-eval", TaskFamily.EVAL, r"求 $\frac{2\cos 10^{\circ}-\sin 20^{\circ}}{\sin 70^{\circ}}$ 的值。", (2*sp.cos(sp.pi/18)-sp.sin(sp.pi/9))/sp.sin(7*sp.pi/18), "evaluate", gold_answer=r"\sqrt{3}", template_group="eval-special-transform"),
            _record("17750-eval", TaskFamily.EVAL, r"已知 $\tan\alpha=-\frac{5}{12}$，且 $\alpha$ 为第四象限角，求 $\sin\alpha$。", sp.sin(alpha), "evaluate", constraints=[sp.Eq(sp.tan(alpha), -sp.Rational(5,12))], quadrant=4, gold_answer=r"- \frac{5}{13}", template_group="eval-quadrant-given-tan"),
        ]
    )

    # IDENTITY.
    records.extend(
        [
            _record("17762-identity-mc", TaskFamily.IDENTITY, r"化简 $\sin^2x+\cos^2x$。", sp.sin(x)**2+sp.cos(x)**2, "simplify", options=["$0$", "$1$", "$2$", "$\\sin 2x$"], gold_option="B", template_group="identity-pythagorean"),
            _record("18273-identity-mc", TaskFamily.IDENTITY, r"化简 $(1+\tan^2x)\cos^2x$。", (1+sp.tan(x)**2)*sp.cos(x)**2, "simplify", options=["$0$", "$\\sin^2x$", "$1$", "$\\cos^2x$"], gold_option="C", template_group="identity-sec-tan"),
            _record("18060-identity", TaskFamily.IDENTITY, r"化简 $\sin(x+\frac{\pi}{2})-\cos x$。", sp.sin(x+sp.pi/2)-sp.cos(x), "simplify", gold_answer="0", template_group="identity-cofunction"),
            _record("18267-identity", TaskFamily.IDENTITY, r"化简 $\frac{\tan x\cos x}{\sin x}$。", sp.tan(x)*sp.cos(x)/sp.sin(x), "simplify", gold_answer="1", template_group="identity-quotient"),
            _record("18202-identity", TaskFamily.IDENTITY, r"化简 $2\sin x\cos x-\sin 2x$。", 2*sp.sin(x)*sp.cos(x)-sp.sin(2*x), "simplify", gold_answer="0", template_group="identity-double-angle"),
        ]
    )

    # SINUSOID_PROPERTY.
    records.extend(
        [
            _record("17859-amplitude", TaskFamily.SINUSOID_PROPERTY, r"函数 $y=3\sin(2x+\frac{\pi}{3})-1$ 的振幅是（ ）。", 3*sp.sin(2*x+sp.pi/3)-1, "property", properties=["amplitude"], options=["$1$", "$2$", "$3$", "$6$"], gold_option="C", template_group="property-amplitude"),
            _record("1811303-period", TaskFamily.SINUSOID_PROPERTY, r"函数 $y=2\sin(\frac{x}{2}+\frac{\pi}{6})$ 的最小正周期是（ ）。", 2*sp.sin(x/2+sp.pi/6), "property", properties=["period"], options=["$\\pi$", "$2\\pi$", "$3\\pi$", "$4\\pi$"], gold_option="D", template_group="property-period"),
            _record("17542-phase", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=\sin(2x-\frac{\pi}{3})$ 的相位平移量。", sp.sin(2*x-sp.pi/3, evaluate=False), "property", properties=["phase_shift"], gold_answer=r"\frac{\pi}{6}", template_group="property-phase"),
            _record("1745901-maximum", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=3+2\cos(2x+\frac{\pi}{3})$ 的最大值。", 3+2*sp.cos(2*x+sp.pi/3), "property", properties=["maximum"], gold_answer="5", template_group="property-maximum"),
            _record("18114-axis", TaskFamily.SINUSOID_PROPERTY, r"求函数 $y=2\sin(2x-\frac{\pi}{4})$ 的全部对称轴。", 2*sp.sin(2*x-sp.pi/4), "property", properties=["symmetry_axis"], gold_answer=render_periodic(_point_periodic_set(x, sp.pi/2, [3*sp.pi/8])), template_group="property-symmetry-axis"),
        ]
    )

    # EQUATION. These are explicit single-goal atomizations of equation patterns
    # in the source corpus so periodic completeness can be evaluated directly.
    equation_specs = [
        ("17805-equation-mc", sp.Eq(sp.sin(x), sp.Rational(1,2)), [r"$x=2k\pi+\frac{\pi}{6}$ 或 $x=2k\pi+\frac{5\pi}{6}$", r"$x=k\pi+\frac{\pi}{6}$", r"$x=2k\pi+\frac{\pi}{3}$ 或 $x=2k\pi+\frac{2\pi}{3}$", r"$x=2k\pi-\frac{\pi}{6}$ 或 $x=2k\pi+\frac{7\pi}{6}$"], "A", "equation-sin"),
        ("18125-equation-mc", sp.Eq(sp.tan(2*x), 1), [r"$x=k\pi+\frac{\pi}{4}$", r"$x=\frac{k\pi}{2}+\frac{\pi}{8}$", r"$x=2k\pi+\frac{\pi}{8}$", r"$x=\frac{k\pi}{2}+\frac{\pi}{4}$"], "B", "equation-tan-affine"),
    ]
    for source_id, equation, options, gold, group in equation_specs:
        records.append(_record(source_id, TaskFamily.EQUATION, f"解方程 ${sp.latex(equation)}$，给出全部实数解。", equation, "solve_equation", options=options, gold_option=gold, template_group=group))
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
        records.append(_record(source_id, TaskFamily.EQUATION, f"解方程 ${sp.latex(equation)}$，给出全部实数解。", equation, "solve_equation", gold_answer=render_periodic(expected), template_group=group))

    # DOMAIN_RANGE_INEQUALITY.
    records.extend(
        [
            _record("1762104-range-mc", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"函数 $y=2\sin x+3$ 的值域是（ ）。", 2*sp.sin(x)+3, "range", options=["$[-2,3]$", "$[1,5]$", "$[-1,5]$", "$[2,5]$"], gold_option="B", template_group="range-sine-affine"),
            _record("1745902-range-mc", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"函数 $y=-3\cos(2x)+1$ 的值域是（ ）。", -3*sp.cos(2*x)+1, "range", options=["$[-3,3]$", "$[-4,2]$", "$[-2,4]$", "$[-3,4]$"], gold_option="C", template_group="range-cosine-affine"),
            _record("1729401-domain", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"求函数 $y=\sqrt{1-\sin x}$ 的定义域。", sp.sqrt(1-sp.sin(x)), "domain", gold_answer=r"\mathbb{R}", template_group="domain-radical-nonnegative"),
            _record("17742-inequality", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"解不等式 $\sin x\leq\cos x$，给出全部实数解。", sp.Le(sp.sin(x), sp.cos(x)), "solve_inequality", gold_answer=r"\bigcup_{k\in\mathbb{Z}}\left(([0, \frac{\pi}{4}] \cup [\frac{5 \pi}{4}, 2 \pi))+k(2 \pi)\right)", template_group="inequality-sin-cos"),
            _record("18386-inequality", TaskFamily.DOMAIN_RANGE_INEQUALITY, r"解不等式 $\tan x>0$，给出全部实数解。", sp.Gt(sp.tan(x), 0), "solve_inequality", gold_answer=r"\bigcup_{k\in\mathbb{Z}}\left(((0, \frac{\pi}{2}))+k(\pi)\right)", template_group="inequality-tan-sign"),
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
        (TaskFamily.EQUATION, r"方程|所有实数解"),
        (TaskFamily.DOMAIN_RANGE_INEQUALITY, r"定义域|值域|不等式|取值范围"),
        (TaskFamily.SINUSOID_PROPERTY, r"周期|振幅|相位|单调|对称轴|最大值|最小值"),
        (TaskFamily.IDENTITY, r"化简|恒等式|证明"),
        (TaskFamily.EVAL, r"求值|计算|等于"),
    ]
    for family, pattern in rules:
        if re.search(pattern, question):
            return family
    return None


def build_test_candidates(dev: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dev_parents = {row["source_id"].split("-", 1)[0] for row in dev}
    buckets: dict[tuple[TaskFamily, bool], list[dict[str, Any]]] = {}
    seen_templates: set[str] = set()
    for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        question = str(row.get("question") or "")
        source_id = str(row.get("id"))
        if source_id in dev_parents or row.get("image") or "<ImageHere>" in question:
            continue
        if re.search(r"\([1-9]\)|（[1-9]）", question):
            continue
        family = _candidate_family(question)
        if family is None:
            continue
        is_mc = bool(row.get("options"))
        skeleton = re.sub(r"\d+", "N", re.sub(r"\$.*?\$", "<FORMULA>", question))
        skeleton_hash = _sha256_text(re.sub(r"\s+", "", skeleton))
        if skeleton_hash in seen_templates:
            continue
        key = (family, is_mc)
        if len(buckets.setdefault(key, [])) >= 5:
            continue
        seen_templates.add(skeleton_hash)
        buckets[key].append(
            {
                "source_id": source_id,
                "task_family_candidate": family,
                "question": question,
                "options": row.get("options") or [],
                "template_group_candidate": skeleton_hash[:16],
                "review": {"status": "pending", "annotator": None, "independent_reviewer": None},
            }
        )
    atomic_paths = [
        ROOT / "data" / "CMM-Math" / "明确多子题_118题_全部拆分_合并版.jsonl",
        ROOT / "data" / "CMM-Math" / "第二部分_潜在多子题_22题_全部原子化拆分_84条.jsonl",
    ]
    for atomic_path in atomic_paths:
        for line in atomic_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            question = str(row.get("question") or "")
            family = _candidate_family(question)
            if family is None or row.get("image") or "<ImageHere>" in question:
                continue
            is_mc = bool(row.get("options"))
            key = (family, is_mc)
            if len(buckets.setdefault(key, [])) >= 5:
                continue
            skeleton = re.sub(r"\d+", "N", re.sub(r"\$.*?\$", "<FORMULA>", question))
            skeleton_hash = _sha256_text(re.sub(r"\s+", "", skeleton))
            if skeleton_hash in seen_templates:
                continue
            seen_templates.add(skeleton_hash)
            buckets[key].append(
                {
                    "source_id": str(row.get("id")),
                    "task_family_candidate": family,
                    "question": question,
                    "options": row.get("options") or [],
                    "template_group_candidate": skeleton_hash[:16],
                    "review": {"status": "pending", "annotator": None, "independent_reviewer": None},
                }
            )
    candidates: list[dict[str, Any]] = []
    for family in TaskFamily:
        for is_mc in (True, False):
            candidates.extend(buckets.get((family, is_mc), []))
    return candidates


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = build_dev()
    dev_path = OUTPUT_DIR / "dev.jsonl"
    dev_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in dev), encoding="utf-8")
    candidates = build_test_candidates(dev)
    candidates_path = OUTPUT_DIR / "test_candidates.jsonl"
    candidates_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
    manifest = {
        "schema_version": "0.1",
        "frozen": False,
        "source_path": "data/CMM-Math/data.jsonl",
        "source_sha256": hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(),
        "dev_count": len(dev),
        "dev_sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(),
        "test_candidate_count": len(candidates),
        "test_sha256": None,
        "prompt_sha256": QwenRawParser.prompt_hash(),
        "freeze_blocker": "50 records require Oracle-URM/gold annotation and independent second-person review",
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
