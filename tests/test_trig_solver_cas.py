import time

import pytest
import sympy as sp

from trig_solver.cas import CASExecutor, CASTimeout


def test_cas_timeout_is_reported(monkeypatch):
    def slow_simplify(_expression):
        time.sleep(0.1)
        return sp.Integer(0)

    monkeypatch.setattr(sp, "simplify", slow_simplify)
    with pytest.raises(CASTimeout):
        CASExecutor(0.01).run("simplify", sp.Symbol("x"))
