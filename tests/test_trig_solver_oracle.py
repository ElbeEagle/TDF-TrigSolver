import sympy as sp

from trig_solver.models import (
    AbstainCode,
    AngleState,
    ConstraintSpec,
    ExprAST,
    ExpressionSpec,
    GoalSpec,
    SolverConfig,
    TaskFamily,
    TrigURM,
)
from trig_solver.pipeline import solve_oracle


def make_urm(expression, family, operator, *, properties=None, constraints=None, quadrant=None):
    symbols = sorted(expression.free_symbols, key=str)
    symbol = symbols[0] if symbols else sp.Symbol("x", real=True)
    return TrigURM(
        expressions=[ExpressionSpec(id="E1", source_latex=sp.latex(expression), ast=ExprAST.from_sympy(expression))],
        constraints=constraints or [],
        goal=GoalSpec(
            task_family=family,
            operator=operator,
            target_refs=["E1"],
            property_names=properties or [],
            completeness="all_real" if family == TaskFamily.EQUATION else "not_applicable",
        ),
        angles=[AngleState(symbol=str(symbol), unit="radian", quadrant=quadrant)],
    )


def test_exact_special_value():
    result = solve_oracle(make_urm(sp.sin(sp.pi / 6), TaskFamily.EVAL, "evaluate"))
    assert result.status == "solved"
    assert result.answer == r"\frac{1}{2}"


def test_quadrant_constraint_evaluation():
    alpha = sp.Symbol("alpha", real=True)
    constraint = ConstraintSpec(kind="equation", expression=ExprAST.from_sympy(sp.Eq(sp.tan(alpha), -sp.Rational(5, 12))))
    result = solve_oracle(
        make_urm(sp.sin(alpha), TaskFamily.EVAL, "evaluate", constraints=[constraint], quadrant=4)
    )
    assert result.status == "solved"
    assert result.answer == r"- \frac{5}{13}"


def test_identity_rewrite():
    x = sp.Symbol("x", real=True)
    result = solve_oracle(make_urm(sp.sin(x) ** 2 + sp.cos(x) ** 2, TaskFamily.IDENTITY, "simplify"))
    assert result.status == "solved"
    assert result.answer == "1"
    assert result.trace[-1].verified


def test_sinusoid_period_and_amplitude():
    x = sp.Symbol("x", real=True)
    expression = 2 * sp.sin(x / 2 + sp.pi / 5)
    result = solve_oracle(
        make_urm(expression, TaskFamily.SINUSOID_PROPERTY, "property", properties=["period", "amplitude"])
    )
    assert result.status == "solved"
    assert result.answer == r"period=4 \pi, amplitude=2"


def test_sinusoid_monotonic_interval_is_periodically_completed():
    x = sp.Symbol("x", real=True)
    expression = 2 * sp.sin(2 * x - sp.pi / 4)
    result = solve_oracle(
        make_urm(
            expression,
            TaskFamily.SINUSOID_PROPERTY,
            "property",
            properties=["monotonic_increasing"],
        )
    )
    assert result.status == "solved"
    assert result.periodic_set is not None
    assert result.periodic_set.period.to_sympy() == sp.pi
    interval = result.periodic_set.intervals[0]
    assert interval.start.to_sympy() == -sp.pi / 8
    assert interval.end.to_sympy() == 3 * sp.pi / 8


def test_cosine_symmetry_centers_are_periodic_points():
    x = sp.Symbol("x", real=True)
    expression = -3 * sp.cos(2 * x + sp.pi / 3) + 1
    result = solve_oracle(
        make_urm(
            expression,
            TaskFamily.SINUSOID_PROPERTY,
            "property",
            properties=["symmetry_center"],
        )
    )
    assert result.status == "solved"
    assert result.periodic_set is not None
    assert result.periodic_set.period.to_sympy() == sp.pi / 2
    assert result.periodic_set.points[0].to_sympy() == sp.pi / 12


def test_equation_returns_complete_periodic_branches():
    x = sp.Symbol("x", real=True)
    result = solve_oracle(make_urm(sp.Eq(sp.sin(x), sp.Rational(1, 2)), TaskFamily.EQUATION, "solve_equation"))
    assert result.status == "solved"
    assert result.periodic_set is not None
    assert result.periodic_set.period.to_sympy() == 2 * sp.pi
    assert {item.to_sympy() for item in result.periodic_set.points} == {sp.pi / 6, 5 * sp.pi / 6}


def test_inequality_is_lifted_from_fundamental_interval():
    x = sp.Symbol("x", real=True)
    result = solve_oracle(
        make_urm(sp.Le(sp.sin(x), sp.cos(x)), TaskFamily.DOMAIN_RANGE_INEQUALITY, "solve_inequality")
    )
    assert result.status == "solved"
    assert result.periodic_set is not None
    assert result.periodic_set.period.to_sympy() == 2 * sp.pi
    assert result.periodic_set.intervals


def test_non_affine_equation_abstains():
    x = sp.Symbol("x", real=True)
    result = solve_oracle(make_urm(sp.Eq(sp.sin(x**2), 0), TaskFamily.EQUATION, "solve_equation"))
    assert result.status == "abstained"
    assert result.abstain_code == AbstainCode.TMM_PRECONDITION


def test_periodic_ablation_cannot_claim_a_complete_answer():
    x = sp.Symbol("x", real=True)
    result = solve_oracle(
        make_urm(sp.Eq(sp.sin(x), 0), TaskFamily.EQUATION, "solve_equation"),
        config=SolverConfig(enable_periodic_completion=False),
    )
    assert result.status == "abstained"
    assert result.abstain_code == AbstainCode.NO_ROUTE
