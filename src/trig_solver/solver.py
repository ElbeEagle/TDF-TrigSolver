"""Trig-specific meta-models and the decoupled inference strategy."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

import sympy as sp
from sympy.core.relational import Relational

from .cas import CASExecutor, CASTimeout, CASUnsolved
from .models import (
    AbstainCode,
    ExprAST,
    IntervalCell,
    PeriodicSet,
    SetSpec,
    SolveResult,
    SolverConfig,
    TaskFamily,
    TraceStep,
    TrigURM,
)
from .validator import match_options, match_periodic_options, render_periodic, render_value


class TMMFailure(RuntimeError):
    def __init__(self, code: AbstainCode, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class SolverState:
    urm: TrigURM
    options: list[str]
    config: SolverConfig
    cas: CASExecutor
    value: Any = None
    answer_kind: str | None = None
    periodic_set: PeriodicSet | None = None
    option: str | None = None
    validated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    trace: list[TraceStep] = field(default_factory=list)

    @property
    def target(self) -> sp.Basic:
        by_id = {item.id: item for item in self.urm.expressions}
        refs = self.urm.goal.target_refs
        if len(refs) != 1:
            raise TMMFailure(AbstainCode.UNSUPPORTED_INPUT, "pilot requires exactly one target expression")
        return by_id[refs[0]].ast.to_sympy()

    @property
    def variable(self) -> sp.Symbol:
        if self.urm.angles:
            return sp.Symbol(self.urm.angles[0].symbol, real=True)
        symbols = sorted(self.target.free_symbols, key=str)
        if not symbols:
            return sp.Symbol("x", real=True)
        preferred = [item for item in symbols if str(item) in {"x", "alpha", "beta", "theta", "t"}]
        return preferred[0] if preferred else symbols[0]

    def state_hash(self) -> str:
        payload = {
            "kind": self.answer_kind,
            "value": str(self.value),
            "periodic": self.periodic_set.model_dump(mode="json") if self.periodic_set else None,
            "validated": self.validated,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def add_trace(self, tmm_id: str, operation: str, before: str, after: str, verified: bool = False) -> None:
        self.trace.append(
            TraceStep(
                tmm_id=tmm_id,
                operation=operation,
                input_summary=before,
                output_summary=after,
                verified=verified,
            )
        )


class TMM:
    id = "TMM-BASE"

    def match(self, state: SolverState) -> bool:
        raise NotImplementedError

    def execute(self, state: SolverState) -> None:
        raise NotImplementedError


def _quadrant_for(state: SolverState, symbol: sp.Symbol) -> int | None:
    for angle in state.urm.angles:
        if angle.symbol == str(symbol):
            return angle.quadrant
    return None


def _sign_for(function: str, quadrant: int | None) -> int | None:
    if quadrant is None:
        return None
    positive = {
        "sin": {1, 2},
        "cos": {1, 4},
        "tan": {1, 3},
    }
    return 1 if quadrant in positive[function] else -1


class AngleNormalizeTMM(TMM):
    id = "TMM-AngleNormalize"

    def match(self, state: SolverState) -> bool:
        return not state.metadata.get("angles_normalized")

    def execute(self, state: SolverState) -> None:
        before = ",".join(f"{item.symbol}:{item.unit}" for item in state.urm.angles) or "implicit radians"
        state.metadata["angles_normalized"] = True
        state.add_trace(self.id, "normalize angle state", before, "internal unit=radian", True)


class ExactEvaluateTMM(TMM):
    id = "TMM-ExactEvaluate"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.EVAL and state.value is None

    def execute(self, state: SolverState) -> None:
        target = state.target
        before = sp.sstr(target)
        if not target.free_symbols:
            value = state.cas.run("simplify", state.cas.run("trigsimp", target))
        else:
            value = self._from_constraints(state, target)
            if value is None:
                simplified = state.cas.run("trigsimp", target)
                if simplified.free_symbols:
                    raise TMMFailure(AbstainCode.CAS_UNSOLVED, "target still contains free symbols after exact evaluation")
                value = simplified
        state.value = sp.simplify(value)
        state.answer_kind = "scalar"
        state.add_trace(self.id, "exact trigonometric evaluation", before, sp.sstr(state.value), True)

    @staticmethod
    def _from_constraints(state: SolverState, target: sp.Basic) -> sp.Basic | None:
        if not isinstance(target, (sp.sin, sp.cos, sp.tan)):
            return None
        target_name = target.func.__name__
        angle_expr = target.args[0]
        if not isinstance(angle_expr, sp.Symbol):
            return None
        quadrant = _quadrant_for(state, angle_expr)
        for constraint in state.urm.constraints:
            if not constraint.expression:
                continue
            relation = constraint.expression.to_sympy()
            if not isinstance(relation, sp.Equality):
                continue
            lhs, rhs = relation.lhs, relation.rhs
            known = lhs if isinstance(lhs, (sp.sin, sp.cos, sp.tan)) else rhs if isinstance(rhs, (sp.sin, sp.cos, sp.tan)) else None
            numeric = rhs if known == lhs else lhs if known == rhs else None
            if known is None or numeric is None or known.args[0] != angle_expr or numeric.free_symbols:
                continue
            known_name = known.func.__name__
            numeric = sp.simplify(numeric)
            if known_name == target_name:
                return numeric
            if known_name == "tan":
                denom = sp.sqrt(1 + numeric**2)
                if target_name == "sin":
                    sign = _sign_for("sin", quadrant)
                    return None if sign is None else sign * sp.Abs(numeric) / denom
                if target_name == "cos":
                    sign = _sign_for("cos", quadrant)
                    return None if sign is None else sign / denom
            if known_name == "sin":
                cos_sign = _sign_for("cos", quadrant)
                cosine = None if cos_sign is None else cos_sign * sp.sqrt(1 - numeric**2)
                if target_name == "cos":
                    return cosine
                if target_name == "tan" and cosine is not None:
                    return numeric / cosine
            if known_name == "cos":
                sin_sign = _sign_for("sin", quadrant)
                sine = None if sin_sign is None else sin_sign * sp.sqrt(1 - numeric**2)
                if target_name == "sin":
                    return sine
                if target_name == "tan" and sine is not None:
                    return sine / numeric
        return None


class IdentityRewriteTMM(TMM):
    id = "TMM-IdentityRewrite"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.IDENTITY and state.value is None

    def execute(self, state: SolverState) -> None:
        target = state.target
        result, depth = _bounded_identity_search(
            target,
            state.cas,
            state.config.identity_max_depth,
            state.config.identity_beam_width,
        )
        # The CAS result is accepted only after symbolic equivalence succeeds.
        if state.cas.run("simplify", state.cas.run("trigsimp", target - result)) != 0:
            raise TMMFailure(AbstainCode.CAS_UNSOLVED, "identity rewrite could not be verified")
        state.value = result
        state.answer_kind = "expression"
        state.add_trace(
            self.id,
            f"bounded identity normalization (depth={depth}, beam={state.config.identity_beam_width})",
            sp.sstr(target),
            sp.sstr(result),
            True,
        )


def _identity_score(expression: sp.Basic) -> tuple[int, int]:
    return int(sp.count_ops(expression, visual=False)), len(sp.sstr(expression))


def _bounded_identity_search(
    expression: sp.Basic,
    cas: CASExecutor,
    max_depth: int,
    beam_width: int,
) -> tuple[sp.Basic, int]:
    """Small deterministic beam over allowlisted identity transformations."""

    best = expression
    best_depth = 0
    frontier = [expression]
    seen = {sp.srepr(expression)}
    for depth in range(1, max_depth + 1):
        candidates: list[sp.Basic] = []
        for current in frontier:
            transforms = [
                cas.run("trigsimp", current),
                cas.run("simplify", current),
                cas.run("expand_trig", current),
                current.rewrite(sp.sin),
            ]
            for candidate in transforms:
                key = sp.srepr(candidate)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(candidate)
                if _identity_score(candidate) < _identity_score(best):
                    best = candidate
                    best_depth = depth
        if not candidates:
            break
        frontier = sorted(candidates, key=_identity_score)[:beam_width]
    return best, best_depth


def canonical_sinusoid(
    expr: sp.Basic,
    variable: sp.Symbol,
    cas: CASExecutor,
    preferred_function: str | None = None,
) -> dict[str, sp.Basic]:
    reduced = cas.run("trigsimp", expr)
    constant, dependent = reduced.as_independent(variable, as_Add=True)
    coefficient, trig_term = dependent.as_coeff_Mul()
    if not isinstance(trig_term, (sp.sin, sp.cos)):
        raise TMMFailure(AbstainCode.TMM_PRECONDITION, "expression is not a single-harmonic sine/cosine form")
    argument = sp.expand(trig_term.args[0])
    omega = sp.simplify(argument.coeff(variable))
    phase = sp.simplify(argument.subs(variable, 0))
    if omega == 0 or sp.simplify(argument - (omega * variable + phase)) != 0:
        raise TMMFailure(AbstainCode.TMM_PRECONDITION, "trigonometric argument is not affine")
    function = trig_term.func.__name__
    if preferred_function == "sin" and function == "cos":
        phase = sp.simplify(phase + sp.pi / 2)
        function = "sin"
    elif preferred_function == "cos" and function == "sin":
        phase = sp.simplify(phase - sp.pi / 2)
        function = "cos"
    if coefficient.is_negative:
        coefficient = -coefficient
        phase = sp.simplify(phase + sp.pi)
    ratio = sp.simplify((phase + sp.pi) / (2 * sp.pi))
    if isinstance(ratio, sp.Rational):
        phase = sp.simplify(phase - 2 * sp.pi * sp.floor(ratio))
    return {
        "function": function,
        "amplitude_coefficient": coefficient,
        "omega": omega,
        "phase": phase,
        "midline": constant,
    }


class SinusoidCanonicalizeTMM(TMM):
    id = "TMM-SinusoidCanonicalize"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.SINUSOID_PROPERTY and "sinusoid" not in state.metadata

    def execute(self, state: SolverState) -> None:
        source = next(item.source_latex for item in state.urm.expressions if item.id == state.urm.goal.target_refs[0])
        preferred = (
            "sin"
            if r"\sin" in source and r"\cos" not in source
            else "cos"
            if r"\cos" in source and r"\sin" not in source
            else None
        )
        data = canonical_sinusoid(state.target, state.variable, state.cas, preferred)
        state.metadata["sinusoid"] = data
        state.add_trace(self.id, "extract A, omega, phase, midline", sp.sstr(state.target), str(data), True)


def _sympy_sign(value: sp.Basic) -> int | None:
    if value.is_positive:
        return 1
    if value.is_negative:
        return -1
    return None


class PropertyDeriveTMM(TMM):
    id = "TMM-PropertyDerive"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.SINUSOID_PROPERTY and "sinusoid" in state.metadata and state.value is None

    def execute(self, state: SolverState) -> None:
        data = state.metadata["sinusoid"]
        coefficient = data["amplitude_coefficient"]
        omega = data["omega"]
        phase = data["phase"]
        midline = data["midline"]
        amplitude = sp.Abs(coefficient)
        period = sp.simplify(2 * sp.pi / sp.Abs(omega))
        available: dict[str, Any] = {
            "period": period,
            "amplitude": amplitude,
            "phase_shift": sp.simplify(-phase / omega),
            "midline": midline,
            "maximum": sp.simplify(midline + amplitude),
            "minimum": sp.simplify(midline - amplitude),
            "range": sp.Interval(sp.simplify(midline - amplitude), sp.simplify(midline + amplitude)),
        }
        sign = _sympy_sign(sp.simplify(coefficient * omega))
        if sign is not None:
            function = data["function"]
            if function == "sin":
                increasing_angles = (-sp.pi / 2, sp.pi / 2) if sign > 0 else (sp.pi / 2, 3 * sp.pi / 2)
                decreasing_angles = (sp.pi / 2, 3 * sp.pi / 2) if sign > 0 else (-sp.pi / 2, sp.pi / 2)
                axis_angle = sp.pi / 2
                center_angle = sp.Integer(0)
            else:
                increasing_angles = (-sp.pi, 0) if sign > 0 else (0, sp.pi)
                decreasing_angles = (0, sp.pi) if sign > 0 else (-sp.pi, 0)
                axis_angle = sp.Integer(0)
                center_angle = sp.pi / 2
            available.update(
                {
                    "monotonic_increasing": _argument_interval_set(
                        state.variable, omega, phase, *increasing_angles
                    ),
                    "monotonic_decreasing": _argument_interval_set(
                        state.variable, omega, phase, *decreasing_angles
                    ),
                    "symmetry_axis": _argument_point_set(
                        state.variable, omega, phase, axis_angle, sp.pi
                    ),
                    "symmetry_center": _argument_point_set(
                        state.variable, omega, phase, center_angle, sp.pi
                    ),
                }
            )
        requested = state.urm.goal.property_names or [state.urm.goal.operator]
        unsupported = set(requested) - set(available)
        if unsupported:
            raise TMMFailure(AbstainCode.TMM_PRECONDITION, f"property not implemented in pilot: {sorted(unsupported)}")
        state.value = {name: available[name] for name in requested}
        if len(state.value) == 1:
            state.value = next(iter(state.value.values()))
        if isinstance(state.value, PeriodicSet):
            state.periodic_set = state.value
            state.answer_kind = "periodic_set"
        else:
            state.answer_kind = "property"
        state.add_trace(self.id, "derive sinusoid properties", str(requested), render_value(state.value), True)


def _argument_interval_set(
    variable: sp.Symbol,
    omega: sp.Basic,
    phase: sp.Basic,
    lower_angle: sp.Basic,
    upper_angle: sp.Basic,
) -> PeriodicSet:
    """Map a closed monotonic argument interval back to x and lift it periodically."""

    endpoints = [sp.simplify((lower_angle - phase) / omega), sp.simplify((upper_angle - phase) / omega)]
    endpoints.sort(key=lambda item: float(sp.N(item)))
    return PeriodicSet(
        period=ExprAST.from_sympy(sp.simplify(2 * sp.pi / sp.Abs(omega))),
        intervals=[
            IntervalCell(
                start=ExprAST.from_sympy(endpoints[0]),
                end=ExprAST.from_sympy(endpoints[1]),
            )
        ],
        variable=str(variable),
    )


def _argument_point_set(
    variable: sp.Symbol,
    omega: sp.Basic,
    phase: sp.Basic,
    base_angle: sp.Basic,
    argument_period: sp.Basic,
) -> PeriodicSet:
    period = sp.simplify(argument_period / sp.Abs(omega))
    point = sp.simplify((base_angle - phase) / omega)
    return _point_periodic_set(variable, period, [point])


def _normalize_base(value: sp.Basic, period: sp.Basic) -> sp.Basic:
    ratio = sp.simplify(value / period)
    if isinstance(ratio, sp.Rational):
        return sp.simplify(value - sp.floor(ratio) * period)
    numeric = float(sp.N(ratio))
    return sp.simplify(value - int(numeric // 1) * period)


def _point_periodic_set(variable: sp.Symbol, period: sp.Basic, points: list[sp.Basic]) -> PeriodicSet:
    unique: list[sp.Basic] = []
    for point in points:
        base = _normalize_base(sp.simplify(point), period)
        if not any(sp.simplify(base - existing) == 0 for existing in unique):
            unique.append(base)
    unique.sort(key=lambda item: float(sp.N(item / period)))
    return PeriodicSet(
        period=ExprAST.from_sympy(period),
        points=[ExprAST.from_sympy(item) for item in unique],
        variable=str(variable),
    )


class EquationBaseSolveTMM(TMM):
    id = "TMM-EquationBaseSolve"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.EQUATION and state.periodic_set is None

    def execute(self, state: SolverState) -> None:
        relation = state.target
        expression = relation.lhs - relation.rhs if isinstance(relation, sp.Equality) else relation
        variable = state.variable
        atoms = list(expression.atoms(sp.sin, sp.cos, sp.tan))
        if len(atoms) != 1:
            raise TMMFailure(AbstainCode.TMM_PRECONDITION, "equation must contain one trigonometric atom")
        atom = atoms[0]
        argument = sp.expand(atom.args[0])
        omega = sp.simplify(argument.coeff(variable))
        phase = sp.simplify(argument.subs(variable, 0))
        if omega == 0 or sp.simplify(argument - (omega * variable + phase)) != 0:
            raise TMMFailure(AbstainCode.TMM_PRECONDITION, "equation angle must be affine")
        roots = state.cas.run("solve", expression, atom)
        if not roots or len(roots) > 2:
            raise TMMFailure(AbstainCode.CAS_UNSOLVED, "cannot isolate the trigonometric atom")
        period_u = sp.pi if atom.func == sp.tan else 2 * sp.pi
        period_x = sp.simplify(period_u / sp.Abs(omega))
        bases: list[sp.Basic] = []
        for root in roots:
            if root.free_symbols:
                raise TMMFailure(AbstainCode.CAS_UNSOLVED, "equation root contains unsupported parameters")
            if atom.func in {sp.sin, sp.cos} and (root.is_real is False or bool(sp.Abs(root) > 1)):
                continue
            angles = (
                [sp.asin(root), sp.pi - sp.asin(root)]
                if atom.func == sp.sin
                else [sp.acos(root), -sp.acos(root)]
                if atom.func == sp.cos
                else [sp.atan(root)]
            )
            bases.extend(sp.simplify((angle - phase) / omega) for angle in angles)
        if not bases:
            raise TMMFailure(AbstainCode.CAS_UNSOLVED, "equation has no supported real branches")
        periodic = _point_periodic_set(variable, period_x, bases)
        # Verify every base point before periodic lifting.
        for point in periodic.points:
            residual = state.cas.run("trigsimp", expression.subs(variable, point.to_sympy()))
            if residual != 0:
                raise TMMFailure(AbstainCode.PERIODIC_FAILURE, "a generated base solution failed substitution")
        state.metadata["base_periodic_set"] = periodic
        state.add_trace(self.id, "solve within one fundamental period", sp.sstr(relation), render_periodic(periodic), True)


class DomainRangeInequalityTMM(TMM):
    id = "TMM-DomainRangeInequality"

    def match(self, state: SolverState) -> bool:
        return state.urm.goal.task_family == TaskFamily.DOMAIN_RANGE_INEQUALITY and state.value is None and state.periodic_set is None

    def execute(self, state: SolverState) -> None:
        operator = state.urm.goal.operator
        target = state.target
        variable = state.variable
        if operator == "domain":
            state.value = state.cas.run("continuous_domain", target, variable)
            state.answer_kind = "set"
            operation = "derive continuous domain"
        elif operator == "range":
            data = canonical_sinusoid(target, variable, state.cas)
            amplitude = sp.Abs(data["amplitude_coefficient"])
            state.value = sp.Interval(data["midline"] - amplitude, data["midline"] + amplitude)
            state.answer_kind = "set"
            operation = "derive sinusoid range"
        elif operator == "solve_inequality":
            if not isinstance(target, Relational):
                raise TMMFailure(AbstainCode.TMM_PRECONDITION, "inequality goal does not target a relation")
            period = state.cas.run("periodicity", target.lhs - target.rhs, variable)
            if period in {None, 0}:
                raise TMMFailure(AbstainCode.PERIODIC_FAILURE, "inequality period is unknown")
            base = state.cas.run("solve_inequality", target, variable)
            intervals = _interval_cells(base)
            if not intervals:
                raise TMMFailure(AbstainCode.CAS_UNSOLVED, "inequality did not yield interval cells")
            periodic = PeriodicSet(
                period=ExprAST.from_sympy(sp.simplify(period)),
                intervals=intervals,
                variable=str(variable),
            )
            state.metadata["base_periodic_set"] = periodic
            operation = "solve inequality in one periodic cell"
        else:
            raise TMMFailure(AbstainCode.TMM_PRECONDITION, f"unsupported operator: {operator}")
        output = render_value(state.value) if state.value is not None else render_periodic(state.metadata["base_periodic_set"])
        state.add_trace(self.id, operation, sp.sstr(target), output, True)


def _interval_cells(value: sp.Set) -> list[IntervalCell]:
    parts = list(value.args) if isinstance(value, sp.Union) else [value]
    cells: list[IntervalCell] = []
    for part in parts:
        if isinstance(part, sp.Interval) and part.start.is_finite and part.end.is_finite:
            cells.append(
                IntervalCell(
                    start=ExprAST.from_sympy(part.start),
                    end=ExprAST.from_sympy(part.end),
                    left_open=bool(part.left_open),
                    right_open=bool(part.right_open),
                )
            )
    return cells


class PeriodicCompleteTMM(TMM):
    id = "TMM-PeriodicComplete"

    def match(self, state: SolverState) -> bool:
        return state.config.enable_periodic_completion and state.periodic_set is None and "base_periodic_set" in state.metadata

    def execute(self, state: SolverState) -> None:
        periodic = state.metadata["base_periodic_set"]
        state.periodic_set = periodic
        state.answer_kind = "periodic_set"
        state.value = periodic
        state.add_trace(self.id, "lift base cells by integer periods", "fundamental cells", render_periodic(periodic), True)


class AnswerValidateTMM(TMM):
    id = "TMM-AnswerValidate"

    def match(self, state: SolverState) -> bool:
        return state.config.enable_validator and state.value is not None and not state.validated

    def execute(self, state: SolverState) -> None:
        before = render_periodic(state.periodic_set) if state.periodic_set else render_value(state.value)
        if state.options and state.periodic_set is None:
            option, error = match_options(state.value, state.options)
            if error:
                code = AbstainCode.VALIDATION_AMBIGUOUS if "multiple" in error else AbstainCode.VALIDATION_NO_MATCH
                raise TMMFailure(code, error)
            state.option = option
        elif state.options and state.periodic_set is not None:
            option, error = match_periodic_options(state.periodic_set, state.options)
            if error:
                code = AbstainCode.VALIDATION_AMBIGUOUS if "multiple" in error else AbstainCode.VALIDATION_NO_MATCH
                raise TMMFailure(code, error)
            state.option = option
        state.validated = True
        state.add_trace(self.id, "validate exact result and match options", before, state.option or "exact open answer", True)


ROUTES: dict[TaskFamily, list[type[TMM]]] = {
    TaskFamily.EVAL: [AngleNormalizeTMM, ExactEvaluateTMM, AnswerValidateTMM],
    TaskFamily.IDENTITY: [AngleNormalizeTMM, IdentityRewriteTMM, AnswerValidateTMM],
    TaskFamily.SINUSOID_PROPERTY: [AngleNormalizeTMM, SinusoidCanonicalizeTMM, PropertyDeriveTMM, AnswerValidateTMM],
    TaskFamily.EQUATION: [AngleNormalizeTMM, EquationBaseSolveTMM, PeriodicCompleteTMM, AnswerValidateTMM],
    TaskFamily.DOMAIN_RANGE_INEQUALITY: [AngleNormalizeTMM, DomainRangeInequalityTMM, PeriodicCompleteTMM, AnswerValidateTMM],
}


class DISSolver:
    def __init__(self, config: SolverConfig | None = None) -> None:
        self.config = config or SolverConfig()

    def solve(self, urm: TrigURM, options: list[str] | None = None) -> SolveResult:
        state = SolverState(
            urm=urm,
            options=options or [],
            config=self.config,
            cas=CASExecutor(self.config.cas_timeout_seconds),
        )
        route = ROUTES.get(urm.goal.task_family)
        if not route:
            return SolveResult.abstain(AbstainCode.NO_ROUTE, f"no route for {urm.goal.task_family}")
        seen: set[tuple[str, str]] = set()
        try:
            steps = 0
            for model_type in route:
                model = model_type()
                if not model.match(state):
                    continue
                signature = (model.id, state.state_hash())
                if signature in seen:
                    raise TMMFailure(AbstainCode.NO_ROUTE, f"repeated state transition for {model.id}")
                seen.add(signature)
                model.execute(state)
                steps += 1
                if steps > self.config.max_tmm_steps:
                    raise TMMFailure(AbstainCode.NO_ROUTE, "maximum TMM transition count exceeded")
            if state.value is None:
                raise TMMFailure(AbstainCode.NO_ROUTE, "route terminated without a result")
            if self.config.enable_validator and not state.validated:
                raise TMMFailure(AbstainCode.VALIDATION_NO_MATCH, "result was not validated")
            answer = render_periodic(state.periodic_set) if state.periodic_set else render_value(state.value)
            expression = None
            set_value = None
            if state.periodic_set is None and isinstance(state.value, sp.Set):
                set_value = SetSpec.from_sympy(state.value)
            elif state.periodic_set is None and isinstance(state.value, sp.Basic):
                expression = ExprAST.from_sympy(state.value)
            return SolveResult(
                status="solved",
                answer_kind=state.answer_kind,
                answer=answer,
                option=state.option,
                value=None if state.periodic_set else answer,
                expression=expression,
                set_value=set_value,
                periodic_set=state.periodic_set,
                trace=state.trace,
                metadata={key: str(value) for key, value in state.metadata.items() if key != "base_periodic_set"},
            )
        except CASTimeout as exc:
            return SolveResult.abstain(AbstainCode.CAS_TIMEOUT, str(exc), state.trace)
        except CASUnsolved as exc:
            return SolveResult.abstain(AbstainCode.CAS_UNSOLVED, str(exc), state.trace)
        except TMMFailure as exc:
            return SolveResult.abstain(exc.code, str(exc), state.trace)
        except (TypeError, ValueError, NotImplementedError) as exc:
            return SolveResult.abstain(AbstainCode.CAS_UNSOLVED, str(exc), state.trace)
