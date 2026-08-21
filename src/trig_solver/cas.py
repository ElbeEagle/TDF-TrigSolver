"""Allowlisted SymPy operations with a bounded wall-clock time."""

from __future__ import annotations

import signal
from contextlib import contextmanager
from typing import Any, Iterator

import sympy as sp
from sympy.calculus.util import continuous_domain, periodicity
from sympy.solvers.inequalities import solve_univariate_inequality


class CASTimeout(TimeoutError):
    pass


class CASUnsolved(RuntimeError):
    pass


@contextmanager
def _timeout(seconds: float) -> Iterator[None]:
    def handler(_signum: int, _frame: object) -> None:
        raise CASTimeout(f"CAS operation exceeded {seconds:g}s")

    if not hasattr(signal, "setitimer") or seconds <= 0:
        yield
        return
    previous = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


class CASExecutor:
    ALLOWED = {
        "trigsimp",
        "expand_trig",
        "solveset",
        "periodicity",
        "continuous_domain",
        "solve_inequality",
        "simplify",
        "solve",
    }

    def __init__(self, timeout_seconds: float = 2.0) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, operation: str, expression: sp.Basic, symbol: sp.Basic | None = None) -> Any:
        if operation not in self.ALLOWED:
            raise ValueError(f"CAS operation is not allowlisted: {operation}")
        with _timeout(self.timeout_seconds):
            if operation == "trigsimp":
                result = sp.trigsimp(expression, method="fu")
            elif operation == "expand_trig":
                result = sp.expand_trig(expression)
            elif operation == "simplify":
                result = sp.simplify(expression)
            elif operation == "solveset":
                result = sp.solveset(expression, symbol, domain=sp.S.Reals)
            elif operation == "solve":
                result = sp.solve(sp.Eq(expression, 0), symbol)
            elif operation == "periodicity":
                result = periodicity(expression, symbol)
            elif operation == "continuous_domain":
                result = continuous_domain(expression, symbol, sp.S.Reals)
            else:
                result = solve_univariate_inequality(expression, symbol, relational=False)
        if isinstance(result, sp.ConditionSet):
            raise CASUnsolved("SymPy returned ConditionSet")
        return result
