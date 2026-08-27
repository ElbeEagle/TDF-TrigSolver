from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from scripts.llm_eval.build_benchmark import build
from scripts.llm_eval import call_llm_api
from scripts.llm_eval.call_llm_api import _completed_ids, call_problem
from scripts.llm_eval.protocol import (
    EXPECTED_INCLUDED,
    EXPECTED_MULTIPLE_CHOICE,
    EXPECTED_OPEN,
    EXPECTED_OPEN_MISSING_ANSWER,
    FORBIDDEN_REQUEST_KEYS,
    MODEL_SPECS,
    build_messages,
    build_selection_rows,
    extract_choice,
    extract_final_answer,
    normalize_open_answer,
    read_jsonl,
    repo_root,
    request_payload,
    sha256_file,
    validate_source_and_selection,
)
from scripts.llm_eval.score_predictions import build_blinded_review_records, finalize


def test_frozen_source_selection_counts() -> None:
    root = repo_root()
    source_path = root / "data/CMM-Math/data.jsonl"
    source_rows = read_jsonl(source_path)
    selection = build_selection_rows(source_rows)
    validate_source_and_selection(source_path, source_rows, selection)
    included = [row for row in selection if row["included"]]
    included_ids = {row["source_id"] for row in included}
    included_source = [row for row in source_rows if str(row["id"]) in included_ids]
    assert len(included) == EXPECTED_INCLUDED
    assert sum(bool(row.get("options")) for row in included_source) == EXPECTED_MULTIPLE_CHOICE
    assert sum(not bool(row.get("options")) for row in included_source) == EXPECTED_OPEN
    assert sum(
        not bool(row.get("options")) and not str(row.get("answer", "")).strip()
        for row in included_source
    ) == EXPECTED_OPEN_MISSING_ANSWER
    assert set(included[0]) == {"source_id", "question_sha256", "included", "reason"}


def test_build_benchmark_writes_hash_locked_manifest(tmp_path: Path) -> None:
    selection_path, manifest_path = build(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["frozen"] is True
    assert manifest["included_count"] == EXPECTED_INCLUDED
    assert manifest["selection_sha256"] == sha256_file(selection_path)


def test_request_payload_cannot_leak_gold_fields() -> None:
    source = {
        "question": "1+1=?",
        "options": "A. 1\nB. 2",
        "answer": "B",
        "analysis": "hidden",
        "solution": "hidden",
    }
    payload = request_payload(source)
    assert not (FORBIDDEN_REQUEST_KEYS & payload.keys())
    messages = build_messages(source)
    serialized = json.dumps(messages, ensure_ascii=False)
    assert "hidden" not in serialized
    assert '"answer"' not in serialized


@pytest.mark.parametrize(
    ("content", "answer", "status"),
    [
        ("推导\nFINAL_ANSWER: A", "A", "parsed"),
        ("FINAL_ANSWER： $\\frac{1}{2}$", "$\\frac{1}{2}$", "parsed"),
        ("没有固定末行", None, "missing_final_answer"),
    ],
)
def test_extract_final_answer(content: str, answer: str | None, status: str) -> None:
    assert extract_final_answer(content) == (answer, status)


def test_conservative_normalization_and_choice_extraction() -> None:
    assert extract_choice(r"\boxed{C}") == "C"
    assert extract_choice("选项 D") == "D"
    assert normalize_open_answer(r"$\left[ 0, π \right]$。") == r"[0,\pi]"
    assert normalize_open_answer(r"\dfrac{1}{2}") == r"\frac{1}{2}"
    assert normalize_open_answer(r"\frac{1+1}{2}") != normalize_open_answer("1")


def test_resume_only_skips_successful_rows(tmp_path: Path) -> None:
    output = tmp_path / "predictions.jsonl"
    output.write_text(
        json.dumps({"source_id": "ok", "api_error": None})
        + "\n"
        + json.dumps({"source_id": "retry", "api_error": {"type": "timeout"}})
        + "\n",
        encoding="utf-8",
    )
    assert _completed_ids(output) == {"ok"}


def test_transient_failure_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def fake_request(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise call_llm_api.APITimeoutError(httpx.Request("POST", "https://example.invalid"))
        return {
            "model_returned": "deepseek-v3",
            "reasoning_content": "",
            "response_content": "FINAL_ANSWER: B",
            "final_answer": "B",
            "parse_status": "parsed",
            "token_usage": None,
        }

    monkeypatch.setattr(call_llm_api, "_single_request", fake_request)
    monkeypatch.setattr(call_llm_api.time, "sleep", lambda _: None)
    result = call_problem(
        {"id": "synthetic", "question": "1+1=?", "options": "A. 1\nB. 2"},
        MODEL_SPECS["deepseek-v3"],
        "deepseek-v3",
    )
    assert calls == 2
    assert result["attempt_count"] == 2
    assert result["api_error"] is None


def test_blinded_queue_separates_private_model_mapping() -> None:
    item, private_map = build_blinded_review_records(
        "qwen3.5-flash",
        {"id": "42", "question": "题目", "answer": "1", "analysis": "依据"},
        {"final_answer": "2", "response_content": "推导"},
    )
    assert "model_key" not in item
    assert "source_id" not in item
    assert private_map == {
        "judgment_id": item["judgment_id"],
        "model_key": "qwen3.5-flash",
        "source_id": "42",
    }


def test_credentials_are_read_only_from_dotenv_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        call_llm_api,
        "dotenv_values",
        lambda _: {
            "DASHSCOPE_API_KEY": "file-key",
            "DASHSCOPE_BASE_URL": "https://example.invalid/v1",
        },
    )
    assert call_llm_api._credentials() == ("file-key", "https://example.invalid/v1")


def test_finalize_blocks_uncertain(tmp_path: Path) -> None:
    stage_rows = [
        {
            "source_id": "1",
            "model_key": "qwen3.5-flash",
            "stage_one_status": "needs_review",
            "correct": None,
            "judgment_id": "J-1",
        }
    ]
    review_dir = tmp_path / "review"
    review_dir.mkdir(parents=True)
    (tmp_path / "stage_one_scores.jsonl").write_text(json.dumps(stage_rows[0]) + "\n")
    (review_dir / "judgment_map.private.jsonl").write_text(
        json.dumps({"judgment_id": "J-1", "model_key": "qwen3.5-flash", "source_id": "1"}) + "\n"
    )
    uncertain = tmp_path / "uncertain.jsonl"
    uncertain.write_text(json.dumps({"judgment_id": "J-1", "verdict": "uncertain"}) + "\n")
    with pytest.raises(RuntimeError, match="uncertain"):
        finalize(tmp_path, uncertain)
