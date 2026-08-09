from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.data_extraction.dataset_adapters import (
    CMMMathAdapter,
    DatasetFormatError,
    GenericAdapter,
    NormalizedRecord,
    UGMathBenchAdapter,
    iter_json_records,
    iter_local_normalized,
)
from scripts.data_extraction.extract_trig_problems import build_parser, extract
from scripts.data_extraction.export_original_format import export_original_format
from scripts.data_extraction.trig_rules import classify_record
from scripts.data_extraction.validate_extraction import validate


CMM_PATH = REPO_ROOT / "data" / "CMM-Math" / "all_data.jsonl"


def normalized(problem: str, auxiliary: str = "", record_id: str = "fixture") -> NormalizedRecord:
    return NormalizedRecord(
        dataset="fixture",
        config=None,
        split="test",
        record_id=record_id,
        group_id=record_id,
        row_index=0,
        problem_text=problem,
        auxiliary_text=auxiliary,
        image_refs=[],
        raw_record={"id": record_id, "question": problem, "analysis": auxiliary},
    )


@pytest.mark.parametrize(
    ("problem", "auxiliary", "expected"),
    [
        (r"求函数 $y=2\sin(3x+\pi/4)$ 的最小正周期。", "", "A"),
        (r"化简 $\sin^2 x+\cos^2 x$。", "", "A"),
        (
            r"在 $\triangle ABC$ 中，a=1,b=2,C=60^\circ，求边 c。",
            r"由余弦定理可得。",
            "B",
        ),
        ("测得塔顶仰角为30°，观测点距塔底20米，求塔高。", "", "B"),
        (
            r"(1) 在 $\triangle ABC$ 中求角 A；(2) 求函数 $f(x)=\sin x$ 的最大值。",
            "",
            "MIXED",
        ),
        (
            "A PDE discretization contains the basis sin(x); report its memory usage.",
            "",
            "C",
        ),
        ("", r"The analysis happens to use $\sin x$.", "UNCERTAIN"),
    ],
)
def test_rule_classes(problem: str, auxiliary: str, expected: str) -> None:
    result = classify_record(normalized(problem, auxiliary))
    assert result is not None
    assert result["label"] == expected
    assert result["matched_rules"]
    assert result["decision_trace"]


def test_non_candidate_is_skipped() -> None:
    assert classify_record(normalized("计算 2+3 的值。")) is None


def test_jsonl_streaming_and_invalid_handling(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text('{"id": 1}\nnot-json\n{"id": 2}\n', encoding="utf-8")
    errors: list[dict[str, object]] = []
    rows = list(iter_json_records(path, skip_invalid=True, errors=errors))
    assert [row["id"] for row in rows] == [1, 2]
    assert errors[0]["line"] == 2
    with pytest.raises(DatasetFormatError, match="invalid JSONL record"):
        list(iter_json_records(path))


def test_json_array_streaming_and_single_object(tmp_path: Path) -> None:
    array_path = tmp_path / "records.json"
    array_path.write_text(
        json.dumps([{"id": 1, "text": "x" * 70000}, {"id": 2}]),
        encoding="utf-8",
    )
    assert [row["id"] for row in iter_json_records(array_path)] == [1, 2]

    object_path = tmp_path / "single.json"
    object_path.write_text('{"id": 3}', encoding="utf-8")
    assert list(iter_json_records(object_path)) == [{"id": 3}]


def test_cmm_split_lookup_uses_ids_not_order(tmp_path: Path) -> None:
    all_path = tmp_path / "all_data.jsonl"
    train_path = tmp_path / "train_data.jsonl"
    test_path = tmp_path / "test_data.jsonl"
    rows = [
        {"id": "test-1", "question": "q", "options": "", "analysis": "", "image": []},
        {"id": "train-1", "question": "q", "options": "", "analysis": "", "image": []},
    ]
    all_path.write_text("\n".join(json.dumps(x) for x in reversed(rows)) + "\n")
    train_path.write_text(json.dumps(rows[1]) + "\n")
    test_path.write_text(json.dumps(rows[0]) + "\n")
    adapter = CMMMathAdapter(all_path)
    records = list(iter_local_normalized(all_path, adapter))
    assert {item.record_id: item.split for item in records} == {
        "train-1": "train",
        "test-1": "test",
    }


def test_ugmathbench_expands_three_versions() -> None:
    raw = {
        "id": "Trigonometry_0001",
        "subject": "Trigonometry",
        "topic": "Functions",
        "problem_v1": "p1",
        "problem_v2": "p2",
        "problem_v3": "p3",
        "answer_v1": ["1"],
        "answer_v2": ["2"],
        "answer_v3": ["3"],
    }
    records = list(UGMathBenchAdapter().normalize(raw, 0))
    assert [item.record_id for item in records] == [
        "Trigonometry_0001:v1",
        "Trigonometry_0001:v2",
        "Trigonometry_0001:v3",
    ]
    assert {item.group_id for item in records} == {"Trigonometry_0001"}


def test_generic_adapter_field_mapping() -> None:
    adapter = GenericAdapter(
        dataset_name="custom",
        id_field="pid",
        text_fields=("prompt",),
        auxiliary_fields=("rationale",),
        image_fields=("figure",),
        group_field="source_problem",
    )
    [record] = adapter.normalize(
        {
            "pid": "p1",
            "source_problem": "g1",
            "prompt": "hello",
            "rationale": "world",
            "figure": {"src": "https://example.test/image.png"},
        },
        4,
    )
    assert record.record_id == "p1"
    assert record.group_id == "g1"
    assert record.image_refs == ["https://example.test/image.png"]


def test_end_to_end_extraction_and_validation(tmp_path: Path) -> None:
    source = tmp_path / "input.jsonl"
    source.write_text(
        "\n".join(
            [
            json.dumps({"id": "a", "question": r"求 $\sin 30^\circ$ 的值。"}),
            json.dumps(
                {
                    "id": "b",
                    "question": r"在 $\triangle ABC$ 中，a=1,b=2,C=60^\circ，求 c。",
                }
            ),
            json.dumps({"id": "n", "question": "计算 1+1。"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "out"
    args = build_parser().parse_args(
        [
            "--dataset",
            "generic",
            "--input",
            str(source),
            "--output-dir",
            str(output),
        ]
    )
    summary = extract(args)
    assert summary["scanned"] == 3
    assert summary["candidates"] == 2
    assert (output / "A.jsonl").exists()
    assert (output / "B.jsonl").exists()

    report = validate(
        argparse.Namespace(
            output_dir=str(output), source=str(source), source_id_field="id"
        )
    )
    assert report["status"] == "passed"
    assert report["candidate_count"] == 2


def test_export_original_format_preserves_raw_schema(tmp_path: Path) -> None:
    source = tmp_path / "A.jsonl"
    output = tmp_path / "A_original_format.jsonl"
    raw_records = [
        {"id": "1", "question": "q1", "options": ["a"], "analysis": "a1"},
        {"id": "2", "analysis": "a2", "question": "q2", "options": []},
    ]
    wrappers = [
        {
            "source": {"id": raw["id"]},
            "classification": {"label": "A"},
            "raw_record": raw,
        }
        for raw in raw_records
    ]
    source.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in wrappers),
        encoding="utf-8",
    )

    summary = export_original_format(source, output)

    exported = list(iter_json_records(output))
    assert exported == raw_records
    assert list(exported[0]) == list(raw_records[0])
    assert list(exported[1]) == list(raw_records[1])
    assert summary["records"] == 2
    assert summary["fields"] == list(raw_records[0])
    with pytest.raises(FileExistsError, match="use --overwrite"):
        export_original_format(source, output)


def test_export_original_format_rejects_invalid_wrapper(tmp_path: Path) -> None:
    source = tmp_path / "A.jsonl"
    source.write_text('{"classification":{"label":"A"}}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="raw_record"):
        export_original_format(source, tmp_path / "output.jsonl")


@pytest.mark.skipif(not CMM_PATH.exists(), reason="CMM-Math data is not available")
def test_real_cmm_regression_ids() -> None:
    expected = {
        "17742": "A",
        "17824": "A",
        "17861": "A",
        "17873": "A",
        "18032": "A",
        "18437": "B",
        "18444": "B",
        "2470": "B",
        "3368": "B",
        "17642": "MIXED",
        "18135": "MIXED",
        "19054": "MIXED",
        "19146": "MIXED",
    }
    adapter = CMMMathAdapter(CMM_PATH)
    found: dict[str, str] = {}
    for record in iter_local_normalized(CMM_PATH, adapter):
        if record.record_id not in expected:
            continue
        classification = classify_record(record)
        assert classification is not None, record.record_id
        found[record.record_id] = classification["label"]
    assert found == expected
