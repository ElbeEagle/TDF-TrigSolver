import importlib.util

import pytest

from trig_solver.models import TaskFamily
from trig_solver.preprocessing import preprocess_problem
from trig_solver.models import RawProblem
from trig_solver.qwen import RawSchemaError, RawSemanticMap, semantic_map_to_urm


pytestmark = pytest.mark.skipif(importlib.util.find_spec("antlr4") is None, reason="ANTLR is an optional parser dependency")


def test_semantic_map_cannot_reference_missing_formula():
    problem = preprocess_problem(RawProblem(question=r"化简 $\sin^2 x+\cos^2 x$"))
    mapped = RawSemanticMap.model_validate(
        {
            "goal": {
                "task_family": "IDENTITY",
                "operator": "simplify",
                "target_refs": ["E9"],
                "property_names": [],
                "completeness": "not_applicable",
            },
            "angles": [{"symbol": "x"}],
            "constraint_refs": [],
        }
    )
    with pytest.raises(RawSchemaError, match="unknown references"):
        semantic_map_to_urm(mapped, problem)


def test_semantic_map_contains_no_answer_field():
    assert "answer" not in RawSemanticMap.model_fields
    assert "solution" not in RawSemanticMap.model_fields
    assert TaskFamily.IDENTITY.value == "IDENTITY"


def test_semantic_map_normalizes_latex_greek_angle_symbol():
    problem = preprocess_problem(
        RawProblem(question=r"已知 $\tan\alpha=-\frac{5}{12}$，求 $\sin\alpha$。")
    )
    mapped = RawSemanticMap.model_validate(
        {
            "goal": {
                "task_family": "EVAL",
                "operator": "evaluate",
                "target_refs": ["E2"],
                "property_names": [],
                "completeness": "not_applicable",
            },
            "angles": [{"symbol": r"\alpha", "unit": "radian", "quadrant": 4, "domain": "Reals"}],
            "constraint_refs": ["E1"],
        }
    )
    urm = semantic_map_to_urm(mapped, problem)
    assert urm.angles[0].symbol == "alpha"
