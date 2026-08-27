"""Shared data, prompt, hashing, and conservative scoring helpers."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SOURCE_RELATIVE_PATH = Path("data/CMM-Math/data.jsonl")
BENCHMARK_RELATIVE_DIR = Path("data/benchmarks/cmm_trig_text_llm_v1")
EXPECTED_SOURCE_SHA256 = "4a3b7c103b97676f0624143ae89140663ee1276bf365c27f1f4cce0bd531c0a5"
EXPECTED_TOTAL = 795
EXPECTED_INCLUDED = 726
EXPECTED_EXCLUDED = 69
EXPECTED_MULTIPLE_CHOICE = 369
EXPECTED_OPEN = 357
EXPECTED_OPEN_MISSING_ANSWER = 20

SYSTEM_PROMPT = """你是一名严谨的三角函数题求解助手。请独立求解用户提供的题目，只使用题干和选项中的信息。
给出简洁但完整的推导，并把最终答案单独放在回复的最后一行。
最后一行必须严格使用以下格式：FINAL_ANSWER: <答案>
选择题的 <答案> 只能是一个大写选项字母。开放题应给出精确数学答案，不使用小数近似替代精确值。
多子题应在同一个最后答案中按 (1)...; (2)... 的顺序列出全部结果。
不要使用外部工具、联网搜索或先前对话内容。"""

FORBIDDEN_REQUEST_KEYS = {"answer", "analysis", "solution", "gold_answer", "gold_option"}


@dataclass(frozen=True)
class ModelSpec:
    label: str
    requested_model: str
    fallback_models: tuple[str, ...] = ()
    enable_thinking: bool = False


MODEL_SPECS = {
    "qwen3.5-flash": ModelSpec(
        label="Qwen3.5-Flash",
        requested_model="qwen3.5-flash-2026-02-23",
        fallback_models=("qwen3.5-flash",),
        enable_thinking=True,
    ),
    "deepseek-v3": ModelSpec(
        label="DeepSeek-V3",
        requested_model="deepseek-v3",
    ),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def question_sha256(record: dict[str, Any]) -> str:
    return sha256_bytes(str(record.get("question", "")).encode("utf-8"))


def input_sha256(record: dict[str, Any]) -> str:
    payload = {"question": record.get("question", ""), "options": record.get("options", "")}
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL row {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row must be an object: {path}:{line_number}")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_selection_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selection: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in source_rows:
        source_id = str(row.get("id", "")).strip()
        if not source_id or source_id in seen_ids:
            raise ValueError(f"missing or duplicate source id: {source_id!r}")
        seen_ids.add(source_id)
        included = not bool(row.get("image"))
        selection.append(
            {
                "source_id": source_id,
                "question_sha256": question_sha256(row),
                "included": included,
                "reason": "included_text_only" if included else "excluded_nonempty_image",
            }
        )
    return selection


def validate_source_and_selection(
    source_path: Path,
    source_rows: list[dict[str, Any]],
    selection_rows: list[dict[str, Any]],
) -> None:
    actual_hash = sha256_file(source_path)
    if actual_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"source hash changed: expected {EXPECTED_SOURCE_SHA256}, got {actual_hash}")
    if len(source_rows) != EXPECTED_TOTAL or len(selection_rows) != EXPECTED_TOTAL:
        raise ValueError(f"expected {EXPECTED_TOTAL} source rows")
    included = [row for row in selection_rows if row["included"]]
    excluded = [row for row in selection_rows if not row["included"]]
    source_by_id = {str(row["id"]): row for row in source_rows}
    for selection in selection_rows:
        source = source_by_id.get(selection["source_id"])
        if source is None:
            raise ValueError(f"selection references missing source: {selection['source_id']}")
        if selection["question_sha256"] != question_sha256(source):
            raise ValueError(f"question hash mismatch: {selection['source_id']}")
    included_source = [source_by_id[row["source_id"]] for row in included]
    multiple_choice = sum(bool(row.get("options")) for row in included_source)
    open_count = sum(not bool(row.get("options")) for row in included_source)
    open_missing_answer = sum(
        not bool(row.get("options")) and not str(row.get("answer", "")).strip()
        for row in included_source
    )
    actual = (len(included), len(excluded), multiple_choice, open_count, open_missing_answer)
    expected = (
        EXPECTED_INCLUDED,
        EXPECTED_EXCLUDED,
        EXPECTED_MULTIPLE_CHOICE,
        EXPECTED_OPEN,
        EXPECTED_OPEN_MISSING_ANSWER,
    )
    if actual != expected:
        raise ValueError(f"selection counts changed: expected {expected}, got {actual}")


def prompt_hash() -> str:
    return sha256_bytes(SYSTEM_PROMPT.encode("utf-8"))


def request_payload(source_row: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "question": str(source_row.get("question", "")),
        "options": str(source_row.get("options", "")) if source_row.get("options") else None,
    }
    if FORBIDDEN_REQUEST_KEYS & payload.keys():
        raise AssertionError("gold-bearing field entered the request payload")
    return payload


def build_messages(source_row: dict[str, Any]) -> list[dict[str, str]]:
    payload = request_payload(source_row)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


FINAL_ANSWER_RE = re.compile(r"(?mi)^\s*FINAL_ANSWER\s*[:：]\s*(.*?)\s*$")


def extract_final_answer(content: str) -> tuple[str | None, str]:
    matches = FINAL_ANSWER_RE.findall(content or "")
    if not matches:
        return None, "missing_final_answer"
    answer = matches[-1].strip()
    if not answer:
        return None, "empty_final_answer"
    return answer, "parsed"


def extract_choice(answer: str | None) -> str | None:
    if not answer:
        return None
    normalized = unicodedata.normalize("NFKC", answer).upper().strip()
    normalized = re.sub(r"^\\?BOXED\s*\{\s*([A-F])\s*\}$", r"\1", normalized)
    match = re.fullmatch(r"(?:选项\s*)?([A-F])(?:[.。)]|答案)?", normalized)
    return match.group(1) if match else None


def normalize_open_answer(answer: str | None) -> str:
    if answer is None:
        return ""
    value = unicodedata.normalize("NFKC", answer).strip()
    value = value.replace("−", "-").replace("–", "-").replace("—", "-")
    value = value.replace("π", r"\pi")
    value = value.replace(r"\dfrac", r"\frac")
    value = value.replace(r"\left", "").replace(r"\right", "")
    value = re.sub(r"[。；;，,]+$", "", value).strip()
    if value.startswith("$") and value.endswith("$") and len(value) >= 2:
        value = value[1:-1]
    if value.startswith(r"\(") and value.endswith(r"\)"):
        value = value[2:-2]
    value = re.sub(r"\s+", "", value)
    return value


def included_source_rows(
    source_rows: list[dict[str, Any]], selection_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    included_ids = {row["source_id"] for row in selection_rows if row["included"]}
    selected = [row for row in source_rows if str(row["id"]) in included_ids]
    if len(selected) != EXPECTED_INCLUDED:
        raise ValueError(f"expected {EXPECTED_INCLUDED} included source rows, got {len(selected)}")
    return selected
