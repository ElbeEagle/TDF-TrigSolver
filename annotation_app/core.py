"""Pure annotation logic shared by the local UI and offline tests.

This module deliberately imports representation and parsing code only.  It does
not import the solver, experiment runner, Qwen adapter, or source CMM answers.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import sympy as sp
from sympy.core.relational import Relational

from trig_solver.models import (
    AngleState,
    ConstraintSpec,
    ExprAST,
    ExpressionSpec,
    GoldAnswer,
    GoalSpec,
    IntervalCell,
    PeriodicSet,
    SetSpec,
    TaskFamily,
    TrigURM,
)
from trig_solver.preprocessing import FormulaParseError, extract_formula_strings, parse_latex_ast


FORBIDDEN_INPUT_KEYS = {
    "answer",
    "analysis",
    "solution",
    "solver_output",
    "solver_prediction",
    "model_prediction",
    "prior_label",
    "prior_labels",
}
ANNOTATOR_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
DEFAULT_OPERATORS: dict[TaskFamily, str] = {
    TaskFamily.EVAL: "evaluate",
    TaskFamily.IDENTITY: "simplify",
    TaskFamily.SINUSOID_PROPERTY: "property",
    TaskFamily.EQUATION: "solve_equation",
    TaskFamily.DOMAIN_RANGE_INEQUALITY: "range",
}
OPERATORS_BY_FAMILY: dict[TaskFamily, tuple[str, ...]] = {
    TaskFamily.EVAL: ("evaluate",),
    TaskFamily.IDENTITY: ("simplify", "prove_identity"),
    TaskFamily.SINUSOID_PROPERTY: ("property",),
    TaskFamily.EQUATION: ("solve_equation",),
    TaskFamily.DOMAIN_RANGE_INEQUALITY: ("domain", "range", "solve_inequality"),
}


class AnnotationError(ValueError):
    """Base class for safe, user-facing annotation errors."""


class TemplateBoundaryError(AnnotationError):
    """Raised when an input violates the sealed annotation boundary."""


class DraftValidationError(AnnotationError):
    """Raised when a human draft cannot become a completed annotation."""


@dataclass(frozen=True)
class ValidatedAnnotation:
    oracle_urm: TrigURM
    gold_answer: GoldAnswer
    gold_option: str | None


@dataclass(frozen=True)
class SessionPaths:
    root: Path
    annotations: Path
    drafts: Path
    events: Path


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise TemplateBoundaryError(f"cannot read valid JSONL from {path}: {exc}") from exc


def _jsonl_text(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        path.chmod(0o600)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _walk_forbidden_keys(value: Any, path: str = "record") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_INPUT_KEYS:
                raise TemplateBoundaryError(f"forbidden field {path}.{key} is present")
            _walk_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_forbidden_keys(child, f"{path}[{index}]")


def validate_annotator_id(value: str) -> str:
    normalized = value.strip()
    if not ANNOTATOR_PATTERN.fullmatch(normalized):
        raise TemplateBoundaryError(
            "annotator id must start with an alphanumeric character and contain only letters, digits, '_' or '-'"
        )
    return normalized


def load_sealed_template(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    manifest_path = path.parent / "manifest.json"
    if not manifest_path.is_file():
        raise TemplateBoundaryError("annotation template must sit beside its benchmark manifest")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TemplateBoundaryError(f"cannot read benchmark manifest: {exc}") from exc
    expected_hash = manifest.get("test_annotation_template_sha256")
    actual_hash = _sha256_bytes(path.read_bytes())
    if not expected_hash or actual_hash != expected_hash:
        raise TemplateBoundaryError("annotation template hash does not match the frozen manifest")
    rows = _read_jsonl(path)
    if len(rows) != 50 or len({row.get("source_id") for row in rows}) != 50:
        raise TemplateBoundaryError("sealed annotation template must contain 50 unique records")
    for row in rows:
        _walk_forbidden_keys(row)
        if row.get("oracle_urm") is not None or row.get("gold_answer") is not None or row.get("gold_option") is not None:
            raise TemplateBoundaryError("sealed input must not contain prefilled Oracle or Gold fields")
        annotation = row.get("annotation") or {}
        if annotation != {
            "annotator": None,
            "annotation_status": "pending",
            "independent_reviewer": None,
            "adjudication_status": "pending",
            "notes": None,
        }:
            raise TemplateBoundaryError("sealed input must not contain a prior human annotation")
        gold_review = row.get("gold_review") or {}
        if gold_review.get("annotator") is not None or gold_review.get("independent_reviewer") is not None:
            raise TemplateBoundaryError("sealed input must not identify prior Gold reviewers")
        review = row.get("selection_review") or {}
        if review.get("solver_prediction_consulted") is not False:
            raise TemplateBoundaryError("selection boundary does not explicitly exclude solver predictions")
    return rows


def _immutable_payload(row: dict[str, Any]) -> dict[str, Any]:
    mutable = {"oracle_urm", "gold_answer", "gold_option", "annotation"}
    return {key: value for key, value in row.items() if key not in mutable}


class AnnotationSession:
    """One annotator's isolated, resumable annotation state."""

    def __init__(self, template_path: Path, workspace: Path, annotator_id: str):
        self.annotator_id = validate_annotator_id(annotator_id)
        self.template_path = template_path.resolve()
        self.template_rows = load_sealed_template(self.template_path)
        workspace_root = workspace.resolve()
        session_root = (workspace_root / self.annotator_id).resolve()
        if session_root.parent != workspace_root:
            raise TemplateBoundaryError("annotator session escaped the configured workspace")
        self.paths = SessionPaths(
            root=session_root,
            annotations=session_root / "annotations.jsonl",
            drafts=session_root / "drafts.json",
            events=session_root / "events.jsonl",
        )
        self.paths.root.mkdir(parents=True, exist_ok=True)
        self.paths.root.chmod(0o700)
        self.records = self._load_or_initialize_records()
        self.drafts = self._load_drafts()

    def _load_or_initialize_records(self) -> list[dict[str, Any]]:
        if not self.paths.annotations.exists():
            rows = copy.deepcopy(self.template_rows)
            for row in rows:
                row["annotation"] = {
                    "annotator": self.annotator_id,
                    "annotation_status": "pending",
                    "independent_reviewer": None,
                    "adjudication_status": "pending",
                    "notes": None,
                }
            _atomic_write(self.paths.annotations, _jsonl_text(rows))
            return rows
        rows = _read_jsonl(self.paths.annotations)
        if len(rows) != len(self.template_rows):
            raise TemplateBoundaryError("saved annotation count differs from the sealed template")
        for template, saved in zip(self.template_rows, rows, strict=True):
            _walk_forbidden_keys(saved)
            if _immutable_payload(template) != _immutable_payload(saved):
                raise TemplateBoundaryError(f"locked fields changed for {template['source_id']}")
            annotation = saved.get("annotation") or {}
            if annotation.get("annotator") != self.annotator_id:
                raise TemplateBoundaryError(f"annotation belongs to another annotator: {template['source_id']}")
            if annotation.get("independent_reviewer") is not None:
                raise TemplateBoundaryError("independent annotation mode cannot load adjudicated records")
        return rows

    def _load_drafts(self) -> dict[str, dict[str, Any]]:
        if not self.paths.drafts.exists():
            return {}
        try:
            value = json.loads(self.paths.drafts.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TemplateBoundaryError(f"cannot read annotator draft state: {exc}") from exc
        if not isinstance(value, dict):
            raise TemplateBoundaryError("draft state must be a JSON object")
        _walk_forbidden_keys(value, "drafts")
        valid_ids = {row["source_id"] for row in self.template_rows}
        if not set(value).issubset(valid_ids):
            raise TemplateBoundaryError("draft state contains records outside the sealed template")
        return value

    def save_draft(self, source_id: str, draft: dict[str, Any]) -> None:
        if source_id not in {row["source_id"] for row in self.template_rows}:
            raise TemplateBoundaryError("cannot save a draft outside the sealed template")
        _walk_forbidden_keys(draft, "draft")
        self.drafts[source_id] = copy.deepcopy(draft)
        _atomic_write(self.paths.drafts, json.dumps(self.drafts, ensure_ascii=False, indent=2) + "\n")

    def complete(self, source_id: str, validated: ValidatedAnnotation, notes: str | None) -> None:
        index = next((i for i, row in enumerate(self.records) if row["source_id"] == source_id), None)
        if index is None:
            raise TemplateBoundaryError("cannot complete a record outside the sealed template")
        row = copy.deepcopy(self.records[index])
        validate_completed_annotation(row, validated)
        row["oracle_urm"] = validated.oracle_urm.model_dump(mode="json")
        row["gold_answer"] = validated.gold_answer.model_dump(mode="json")
        row["gold_option"] = validated.gold_option
        row["annotation"] = {
            "annotator": self.annotator_id,
            "annotation_status": "completed",
            "independent_reviewer": None,
            "adjudication_status": "pending",
            "notes": notes.strip() if notes and notes.strip() else None,
        }
        self.records[index] = row
        _atomic_write(self.paths.annotations, _jsonl_text(self.records))
        self._append_event(source_id, "completed")

    def _append_event(self, source_id: str, action: str) -> None:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "annotator": self.annotator_id,
            "source_id": source_id,
            "action": action,
        }
        existing = self.paths.events.read_text(encoding="utf-8") if self.paths.events.exists() else ""
        _atomic_write(self.paths.events, existing + json.dumps(event, ensure_ascii=False) + "\n")

    @property
    def completed_count(self) -> int:
        return sum((row.get("annotation") or {}).get("annotation_status") == "completed" for row in self.records)

    def record(self, source_id: str) -> dict[str, Any]:
        return next(row for row in self.records if row["source_id"] == source_id)

    def export_bytes(self) -> bytes:
        return self.paths.annotations.read_bytes()


def _strip_math_delimiters(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped.startswith("$") and stripped.endswith("$"):
        return stripped[1:-1].strip()
    if stripped.startswith(r"\(") and stripped.endswith(r"\)"):
        return stripped[2:-2].strip()
    return stripped


def _parse_annotation_expression(latex: str) -> ExprAST:
    """Parse annotation LaTeX, including common paired absolute-value bars.

    SymPy's strict ANTLR parser does not accept ``\\left|...\\right|`` even
    though absolute value is part of the project's AST allowlist.  Replace only
    balanced, innermost bar pairs with temporary symbols, parse through the
    existing strict adapter, and then substitute explicit ``abs`` AST nodes.
    This is syntax normalization only; it does not simplify or solve the input.
    """

    normalized = _strip_math_delimiters(latex)
    placeholders: dict[str, ExprAST] = {}
    pair = re.compile(r"\\left\|((?:(?!\\left\||\\right\|)[\s\S])+?)\\right\|")
    while match := pair.search(normalized):
        inner = match.group(1).strip()
        if not inner:
            raise DraftValidationError("absolute-value bars cannot be empty")
        marker_index = 9000 + len(placeholders)
        marker_latex = rf"q_{{{marker_index}}}"
        while marker_latex in normalized or marker_latex in placeholders:
            marker_index += 1
            marker_latex = rf"q_{{{marker_index}}}"
        marker_value = marker_latex
        placeholders[marker_value] = ExprAST(op="abs", args=[_parse_annotation_expression(inner)])
        normalized = normalized[: match.start()] + marker_latex + normalized[match.end() :]
    if r"\left|" in normalized or r"\right|" in normalized:
        raise DraftValidationError("absolute-value bars must be balanced")

    ast = parse_latex_ast(normalized)

    def substitute(node: ExprAST) -> ExprAST:
        if node.op == "symbol" and str(node.value) in placeholders:
            return placeholders[str(node.value)]
        if not node.args:
            return node
        return ExprAST(op=node.op, value=node.value, args=[substitute(arg) for arg in node.args])

    return substitute(ast)


def _expression_ast(latex: str) -> ExprAST:
    if not latex.strip():
        raise DraftValidationError("a mathematical expression is required")
    try:
        return _parse_annotation_expression(latex)
    except FormulaParseError as exc:
        raise DraftValidationError(str(exc)) from exc


def _safe_variable(value: str) -> str:
    variable = value.strip()
    if not variable or not variable.replace("_", "").isalnum() or variable[0].isdigit():
        raise DraftValidationError("variable must be a safe non-empty symbol")
    return variable


def _constraint_specs(lines: str) -> tuple[list[ConstraintSpec], list[ExpressionSpec]]:
    constraints: list[ConstraintSpec] = []
    expressions: list[ExpressionSpec] = []
    for raw_line in lines.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^\[(equation|inequality|membership|property)]\s*(.+)$", line, flags=re.IGNORECASE)
        declared_kind = match.group(1).lower() if match else None
        payload = match.group(2).strip() if match else line
        if declared_kind in {"membership", "property"}:
            if "=" not in payload:
                raise DraftValidationError(f"{declared_kind} constraint must use name=value syntax")
            name, value = (part.strip() for part in payload.split("=", 1))
            constraints.append(ConstraintSpec(kind=declared_kind, name=name, value=value))
            continue
        ast = _expression_ast(payload)
        sympy_value = ast.to_sympy()
        if declared_kind is None:
            if isinstance(sympy_value, sp.Equality):
                kind = "equation"
            elif isinstance(sympy_value, Relational):
                kind = "inequality"
            else:
                raise DraftValidationError("constraint needs [property]/[membership] or a relational formula")
        else:
            kind = declared_kind
        if kind == "equation" and not isinstance(sympy_value, sp.Equality):
            raise DraftValidationError("[equation] constraint is not an equality")
        if kind == "inequality" and (not isinstance(sympy_value, Relational) or isinstance(sympy_value, sp.Equality)):
            raise DraftValidationError("[inequality] constraint is not an inequality")
        expression_id = f"E{len(expressions) + 2}"
        expressions.append(ExpressionSpec(id=expression_id, source_latex=payload, ast=ast))
        constraints.append(ConstraintSpec(kind=kind, expression=ast))
    return constraints, expressions


def build_oracle_urm(draft: dict[str, Any], family: TaskFamily) -> TrigURM:
    operator = str(draft.get("operator") or "").strip()
    if operator not in OPERATORS_BY_FAMILY[family]:
        raise DraftValidationError(f"operator {operator!r} is not allowed for {family}")
    target_latex = str(draft.get("target_latex") or "").strip()
    target_ast = _expression_ast(target_latex)
    variable = _safe_variable(str(draft.get("variable") or "x"))
    constraint_specs, constraint_expressions = _constraint_specs(str(draft.get("constraints") or ""))
    unit = str(draft.get("unit") or "radian")
    quadrant_raw = draft.get("quadrant")
    quadrant = int(quadrant_raw) if quadrant_raw not in (None, "", 0, "0") else None
    property_names = [item.strip() for item in str(draft.get("property_names") or "").split(",") if item.strip()]
    completeness = str(draft.get("completeness") or "not_applicable")
    if family == TaskFamily.EQUATION:
        completeness = "all_real"
    return TrigURM(
        angles=[AngleState(symbol=variable, unit=unit, quadrant=quadrant)],
        expressions=[ExpressionSpec(id="E1", source_latex=target_latex, ast=target_ast), *constraint_expressions],
        constraints=constraint_specs,
        goal=GoalSpec(
            task_family=family,
            operator=operator,
            target_refs=["E1"],
            property_names=property_names,
            completeness=completeness,
        ),
    )


def _nonempty_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _parse_interval(value: str, *, allow_infinite: bool) -> SetSpec:
    match = re.match(r"^\s*([\[(])\s*(.*?)\s*,\s*(.*?)\s*([\]\)])\s*$", value)
    if not match:
        raise DraftValidationError("interval must look like [a,b], (a,b], [a,b), or (a,b)")
    left_token, start_text, end_text, right_token = match.groups()
    negative_infinity = {"-oo", "-inf", r"-\infty", "-∞"}
    positive_infinity = {"oo", "+oo", "inf", "+inf", r"\infty", r"+\infty", "∞", "+∞"}
    if start_text in negative_infinity:
        if not allow_infinite:
            raise DraftValidationError("periodic intervals cannot be unbounded")
        start = None
    else:
        start = _expression_ast(start_text)
    if end_text in positive_infinity:
        if not allow_infinite:
            raise DraftValidationError("periodic intervals cannot be unbounded")
        end = None
    else:
        end = _expression_ast(end_text)
    left_open = left_token == "("
    right_open = right_token == ")"
    if start is None:
        left_open = True
    if end is None:
        right_open = True
    return SetSpec(
        kind="interval",
        start=start,
        end=end,
        left_open=left_open,
        right_open=right_open,
    )


def _parse_set_component(value: str) -> SetSpec:
    text = value.strip()
    if text.lower() in {"r", "reals", "real", r"\mathbb{r}", r"\mathbf{r}"}:
        return SetSpec(kind="reals")
    if text.lower() in {"empty", "emptyset", r"\emptyset", "∅"}:
        return SetSpec(kind="empty")
    if text.startswith("{") and text.endswith("}"):
        items = [item.strip() for item in text[1:-1].split(",") if item.strip()]
        if not items:
            return SetSpec(kind="empty")
        return SetSpec(kind="finite", elements=[_expression_ast(item) for item in items])
    return _parse_interval(text, allow_infinite=True)


def build_set_gold(kind: str, primary: str, secondary: str = "") -> GoldAnswer:
    if kind == "empty":
        set_value = SetSpec(kind="empty")
    elif kind == "reals":
        set_value = SetSpec(kind="reals")
    elif kind == "finite":
        elements = [_expression_ast(item) for item in _nonempty_lines(primary)]
        if not elements:
            raise DraftValidationError("finite set requires at least one element")
        set_value = SetSpec(kind="finite", elements=elements)
    elif kind == "interval":
        set_value = _parse_interval(primary, allow_infinite=True)
    elif kind == "union":
        children = [_parse_set_component(item) for item in _nonempty_lines(primary)]
        if len(children) < 2:
            raise DraftValidationError("union requires at least two components, one per line")
        set_value = SetSpec(kind="union", children=children)
    elif kind == "difference":
        if not primary.strip() or not secondary.strip():
            raise DraftValidationError("difference requires a base set and a removed set")
        set_value = SetSpec(
            kind="difference",
            children=[_parse_set_component(primary), _parse_set_component(secondary)],
        )
    else:
        raise DraftValidationError(f"unsupported set kind: {kind}")
    return GoldAnswer(kind="set", set_value=set_value)


def _exact_true(value: sp.Basic) -> bool:
    return sp.simplify(value) == sp.S.true


def _ensure_unique(values: list[ExprAST], label: str) -> None:
    sympy_values = [value.to_sympy() for value in values]
    for index, left in enumerate(sympy_values):
        for right in sympy_values[index + 1 :]:
            if sp.simplify(left - right) == 0:
                raise DraftValidationError(f"{label} contains duplicate values")


def validate_periodic_set(value: PeriodicSet) -> None:
    period = sp.simplify(value.period.to_sympy())
    if period.free_symbols or period.is_positive is not True:
        raise DraftValidationError("period must be an exact positive constant")
    if value.full_period and (value.points or value.intervals):
        raise DraftValidationError("full_period cannot be combined with included points or intervals")
    if not value.full_period and not value.points and not value.intervals:
        raise DraftValidationError("non-full periodic set requires at least one point or interval")
    _safe_variable(value.variable)
    _ensure_unique(value.points, "periodic points")
    _ensure_unique(value.excluded_points, "excluded points")
    for label, expressions in (("point", value.points), ("excluded point", value.excluded_points)):
        for expression in expressions:
            item = sp.simplify(expression.to_sympy())
            if item.free_symbols or not _exact_true(sp.Ge(item, 0)) or not _exact_true(sp.Lt(item, period)):
                raise DraftValidationError(f"{label} must lie in the fundamental interval [0, period)")
    for interval in value.intervals:
        start = sp.simplify(interval.start.to_sympy())
        end = sp.simplify(interval.end.to_sympy())
        if start.free_symbols or end.free_symbols:
            raise DraftValidationError("periodic interval endpoints must be exact constants")
        if not _exact_true(sp.Ge(start, 0)) or not _exact_true(sp.Le(end, period)):
            raise DraftValidationError("periodic intervals must lie inside [0, period]")
        if not _exact_true(sp.Lt(start, end)):
            raise DraftValidationError("periodic interval start must be smaller than its end")
        if sp.simplify(end - period) == 0 and not interval.right_open:
            raise DraftValidationError("an interval ending at period must be right-open")


def build_periodic_gold(draft: dict[str, Any]) -> GoldAnswer:
    period = _expression_ast(str(draft.get("period") or ""))
    points = [_expression_ast(item) for item in _nonempty_lines(str(draft.get("points") or ""))]
    excluded = [_expression_ast(item) for item in _nonempty_lines(str(draft.get("excluded_points") or ""))]
    intervals: list[IntervalCell] = []
    for item in _nonempty_lines(str(draft.get("intervals") or "")):
        parsed = _parse_interval(item, allow_infinite=False)
        assert parsed.start is not None and parsed.end is not None
        intervals.append(
            IntervalCell(
                start=parsed.start,
                end=parsed.end,
                left_open=parsed.left_open,
                right_open=parsed.right_open,
            )
        )
    periodic = PeriodicSet(
        period=period,
        points=points,
        intervals=intervals,
        excluded_points=excluded,
        full_period=bool(draft.get("full_period", False)),
        variable=_safe_variable(str(draft.get("periodic_variable") or draft.get("variable") or "x")),
    )
    validate_periodic_set(periodic)
    return GoldAnswer(kind="periodic_set", periodic_set=periodic)


def validate_completed_annotation(record: dict[str, Any], validated: ValidatedAnnotation) -> None:
    family = TaskFamily(record["task_family"])
    if validated.oracle_urm.goal.task_family != family:
        raise DraftValidationError("Oracle task family differs from the locked task family")
    if family == TaskFamily.EQUATION:
        if validated.oracle_urm.goal.completeness != "all_real":
            raise DraftValidationError("every EQUATION annotation must request all real solutions")
        if validated.gold_answer.kind != "periodic_set":
            raise DraftValidationError("every EQUATION Gold must be a PeriodicSet")
    output_format = record["output_format"]
    if output_format == "multiple_choice":
        if validated.gold_option not in {"A", "B", "C", "D"}:
            raise DraftValidationError("multiple-choice annotation requires one Gold option")
        options = (record.get("problem") or {}).get("options") or []
        if ord(validated.gold_option) - ord("A") >= len(options):
            raise DraftValidationError("Gold option does not exist in the locked options")
    elif validated.gold_option is not None:
        raise DraftValidationError("open question must not contain gold_option")


def validate_draft(record: dict[str, Any], draft: dict[str, Any]) -> ValidatedAnnotation:
    family = TaskFamily(record["task_family"])
    oracle = build_oracle_urm(draft, family)
    gold_kind = str(draft.get("gold_kind") or "")
    if family == TaskFamily.EQUATION:
        gold_kind = "periodic_set"
    if gold_kind == "expression":
        gold = GoldAnswer(kind="expression", expression=_expression_ast(str(draft.get("gold_expression") or "")))
    elif gold_kind == "set":
        gold = build_set_gold(
            str(draft.get("set_kind") or ""),
            str(draft.get("set_primary") or ""),
            str(draft.get("set_secondary") or ""),
        )
    elif gold_kind == "periodic_set":
        gold = build_periodic_gold(draft)
    else:
        raise DraftValidationError("choose one Gold kind")
    selected_option = str(draft.get("gold_option") or "").strip().upper() or None
    if record["output_format"] == "open":
        selected_option = None
    validated = ValidatedAnnotation(oracle_urm=oracle, gold_answer=gold, gold_option=selected_option)
    validate_completed_annotation(record, validated)
    return validated


def default_draft(record: dict[str, Any]) -> dict[str, Any]:
    family = TaskFamily(record["task_family"])
    formulas = extract_formula_strings((record.get("problem") or {}).get("question") or "")
    candidate = formulas[-1].strip().rstrip("=").strip() if formulas else ""
    variable = "x"
    for formula in reversed(formulas):
        try:
            symbols = sorted(_expression_ast(formula.strip().rstrip("=").strip()).to_sympy().free_symbols, key=str)
        except DraftValidationError:
            continue
        if symbols:
            variable = str(symbols[0])
            break
    if family == TaskFamily.EQUATION:
        gold_kind = "periodic_set"
    elif family == TaskFamily.DOMAIN_RANGE_INEQUALITY:
        gold_kind = "set"
    elif family == TaskFamily.SINUSOID_PROPERTY and re.search(
        r"对称轴|对称中心|单调.*区间", (record.get("problem") or {}).get("question") or ""
    ):
        gold_kind = "periodic_set"
    else:
        gold_kind = "expression"
    return {
        "target_latex": candidate,
        "variable": variable,
        "unit": "radian",
        "quadrant": "",
        "operator": DEFAULT_OPERATORS[family],
        "property_names": "",
        "completeness": "all_real" if family == TaskFamily.EQUATION else "not_applicable",
        "constraints": "",
        "gold_kind": gold_kind,
        "gold_expression": "",
        "set_kind": "interval",
        "set_primary": "",
        "set_secondary": "",
        "period": "",
        "periodic_variable": variable,
        "points": "",
        "intervals": "",
        "excluded_points": "",
        "full_period": False,
        "gold_option": "",
        "notes": "",
    }
