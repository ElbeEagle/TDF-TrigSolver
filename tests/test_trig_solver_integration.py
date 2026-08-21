import os

import pytest

from trig_solver.models import RawProblem, TaskFamily
from trig_solver.preprocessing import preprocess_problem
from trig_solver.qwen import QwenRawParser


pytestmark = pytest.mark.integration


CASES = [
    (r"计算 $\sin 30^{\circ}$。", TaskFamily.EVAL),
    (r"化简 $\sin^2x+\cos^2x$。", TaskFamily.IDENTITY),
    (r"求函数 $y=2\sin(2x-\frac{\pi}{3})$ 的最小正周期。", TaskFamily.SINUSOID_PROPERTY),
    (r"解方程 $\sin x=\frac{1}{2}$，给出全部实数解。", TaskFamily.EQUATION),
    (r"求函数 $y=2\sin x+3$ 的值域。", TaskFamily.DOMAIN_RANGE_INEQUALITY),
]


@pytest.mark.skipif(os.getenv("RUN_LLM_INTEGRATION") != "1", reason="external Qwen API is opt-in")
@pytest.mark.parametrize(("question", "expected_family"), CASES)
def test_qwen_live_grounded_mapping_for_each_family(question, expected_family):
    prepared = preprocess_problem(RawProblem(question=question))
    mapped, metadata = QwenRawParser("qwen3.7-flash-2026-07-15").parse(prepared)
    assert not mapped.abstain
    assert mapped.goal.task_family == expected_family
    assert set(mapped.goal.target_refs) <= {item.id for item in prepared.expressions}
    assert metadata["model"] == "qwen3.7-flash-2026-07-15"
    assert metadata["total_tokens"] > 0
