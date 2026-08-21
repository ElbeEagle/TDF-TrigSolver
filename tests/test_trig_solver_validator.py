import sympy as sp

from trig_solver.models import ExprAST, PeriodicSet
from trig_solver.validator import match_options, match_periodic_options


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
