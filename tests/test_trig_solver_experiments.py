from pathlib import Path
import json

import pytest

from trig_solver.experiments.run import load_records, run_experiment
from trig_solver.models import TaskFamily


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = ROOT / "data" / "benchmarks" / "trig_pilot_v1"


def test_development_benchmark_balance():
    records = load_records(BENCHMARK_DIR / "dev.jsonl")
    assert len(records) == 25
    for family in TaskFamily:
        family_records = [record for record in records if record.task_family == family]
        assert len(family_records) == 5
        assert sum(bool(record.problem.options) for record in family_records) == 2


def test_unfrozen_test_split_cannot_run():
    with pytest.raises(RuntimeError, match="not frozen"):
        run_experiment("test", "oracle", "full", False)


def test_locked_test_selection_balance_and_equation_completeness():
    path = BENCHMARK_DIR / "test_selection.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 50
    assert all(row["selection_review"]["solver_prediction_consulted"] is False for row in rows)
    for family in TaskFamily:
        family_rows = [row for row in rows if row["task_family"] == family]
        assert len(family_rows) == 10
        assert sum(row["output_format"] == "multiple_choice" for row in family_rows) == 5
    equation_rows = [row for row in rows if row["task_family"] == TaskFamily.EQUATION]
    assert all("全部实数解" in row["problem"]["question"] for row in equation_rows)
    assert all(row["gold_review"]["status"] == "pending_independent_human_annotation" for row in rows)
