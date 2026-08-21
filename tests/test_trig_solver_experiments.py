from pathlib import Path

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
