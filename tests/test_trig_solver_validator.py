import sympy as sp

from trig_solver.models import ExprAST, IntervalCell, PeriodicSet
from trig_solver.validator import match_options, match_periodic_options, periodic_equal


def test_interval_option_matching():
    option, error = match_options(
        sp.Interval(-1, 5),
        [r"$[-2,5]$", r"$[-1,5]$", r"$(-1,5)$", r"$[-1,6]$"],
    )
    assert error is None
    assert option == "B"


def test_periodic_point_option_matching():
    periodic = PeriodicSet(
        period=ExprAST.from_sympy(2 * sp.pi),
        points=[ExprAST.from_sympy(sp.pi / 6), ExprAST.from_sympy(5 * sp.pi / 6)],
        variable="x",
    )
    option, error = match_periodic_options(
        periodic,
        [
            r"$x=2k\pi+\frac{\pi}{6}$ 或 $x=2k\pi+\frac{5\pi}{6}$",
            r"$x=k\pi+\frac{\pi}{6}$",
            r"$x=2k\pi+\frac{\pi}{3}$ 或 $x=2k\pi+\frac{2\pi}{3}$",
            r"$x=2k\pi-\frac{\pi}{6}$ 或 $x=2k\pi+\frac{7\pi}{6}$",
        ],
    )
    assert error is None
    assert option == "A"


def test_periodic_equality_accepts_equivalent_larger_fundamental_period():
    compact = PeriodicSet(
        period=ExprAST.from_sympy(2 * sp.pi),
        points=[ExprAST.from_sympy(sp.pi / 6), ExprAST.from_sympy(5 * sp.pi / 6)],
    )
    expanded = PeriodicSet(
        period=ExprAST.from_sympy(4 * sp.pi),
        points=[
            ExprAST.from_sympy(sp.pi / 6),
            ExprAST.from_sympy(5 * sp.pi / 6),
            ExprAST.from_sympy(13 * sp.pi / 6),
            ExprAST.from_sympy(17 * sp.pi / 6),
        ],
    )
    assert periodic_equal(compact, expanded)


def test_periodic_equality_accepts_full_period_minus_excluded_point():
    excluded = PeriodicSet(
        period=ExprAST.from_sympy(sp.pi),
        full_period=True,
        excluded_points=[ExprAST.from_sympy(sp.pi / 2)],
    )
    split_intervals = PeriodicSet(
        period=ExprAST.from_sympy(sp.pi),
        intervals=[
            IntervalCell(
                start=ExprAST.from_sympy(sp.Integer(0)),
                end=ExprAST.from_sympy(sp.pi / 2),
                right_open=True,
            ),
            IntervalCell(
                start=ExprAST.from_sympy(sp.pi / 2),
                end=ExprAST.from_sympy(sp.pi),
                left_open=True,
                right_open=True,
            ),
        ],
    )
    assert periodic_equal(excluded, split_intervals)
