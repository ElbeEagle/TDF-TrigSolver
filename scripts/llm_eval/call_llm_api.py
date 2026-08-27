"""Call direct LLM baselines with checkpointed, resumable JSONL output."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.llm_eval.protocol import (
    BENCHMARK_RELATIVE_DIR,
    MODEL_SPECS,
    SOURCE_RELATIVE_PATH,
    ModelSpec,
    build_messages,
    extract_final_answer,
    included_source_rows,
    input_sha256,
    prompt_hash,
    read_jsonl,
    repo_root,
    sha256_file,
    validate_source_and_selection,
)


TEMPERATURE = 0.01
MAX_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 180.0
DEFAULT_MAX_ATTEMPTS = 3
_thread_local = threading.local()


def _credentials() -> tuple[str, str]:
    root = repo_root()
    config = dotenv_values(root / ".env.local")
    api_key = config.get("DASHSCOPE_API_KEY")
    base_url = config.get("DASHSCOPE_BASE_URL") or config.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        raise RuntimeError(
            "DASHSCOPE_API_KEY and DASHSCOPE_BASE_URL (or OPENAI_BASE_URL) "
            "must be configured in .env.local"
        )
    return str(api_key), str(base_url)


def _client() -> OpenAI:
    client = getattr(_thread_local, "client", None)
    if client is None:
        api_key, base_url = _credentials()
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=DEFAULT_TIMEOUT_SECONDS)
        _thread_local.client = client
    return client


def _reasoning_content(message: Any) -> str:
    direct = getattr(message, "reasoning_content", None)
    if direct:
        return str(direct)
    extra = getattr(message, "model_extra", None) or {}
    return str(extra.get("reasoning_content") or "")


def _usage_dict(response: Any) -> dict[str, int] | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    return {
        "prompt_tokens": int(usage.prompt_tokens or 0),
        "completion_tokens": int(usage.completion_tokens or 0),
        "total_tokens": int(usage.total_tokens or 0),
    }


def _single_request(source_row: dict[str, Any], spec: ModelSpec, model_name: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": model_name,
        "messages": build_messages(source_row),
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }
    if spec.enable_thinking:
        kwargs["extra_body"] = {"enable_thinking": True}
    response = _client().chat.completions.create(**kwargs)
    message = response.choices[0].message
    content = message.content or ""
    final_answer, parse_status = extract_final_answer(content)
    return {
        "model_returned": response.model,
        "reasoning_content": _reasoning_content(message),
        "response_content": content,
        "final_answer": final_answer,
        "parse_status": parse_status,
        "token_usage": _usage_dict(response),
    }


def resolve_model(spec: ModelSpec, *, max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> tuple[str, dict[str, Any]]:
    synthetic = {
        "id": "synthetic-model-probe",
        "question": r"计算 $\sin 30^\circ$。",
        "options": "",
    }
    failures: list[dict[str, str]] = []
    for candidate in (spec.requested_model, *spec.fallback_models):
        for attempt in range(1, max_attempts + 1):
            try:
                started = time.perf_counter()
                response = _single_request(synthetic, spec, candidate)
                response["latency_seconds"] = time.perf_counter() - started
                response["attempt_count"] = attempt
                return candidate, response
            except APIStatusError as exc:
                failures.append({"model": candidate, "error": type(exc).__name__, "status": str(exc.status_code)})
                if exc.status_code in {400, 404}:
                    break
                if exc.status_code not in {408, 409, 429} and exc.status_code < 500:
                    raise
            except (APIConnectionError, APITimeoutError) as exc:
                failures.append({"model": candidate, "error": type(exc).__name__, "status": "transient"})
            if attempt < max_attempts:
                time.sleep(min(8.0, 2 ** (attempt - 1)) + random.random() * 0.25)
    raise RuntimeError(f"no usable model endpoint for {spec.label}: {failures}")


def call_problem(
    source_row: dict[str, Any],
    spec: ModelSpec,
    resolved_model: str,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict[str, Any]:
    last_error: dict[str, Any] | None = None
    started = time.perf_counter()
    attempt_count = 0
    for attempt in range(1, max_attempts + 1):
        attempt_count = attempt
        try:
            payload = _single_request(source_row, spec, resolved_model)
            return {
                "source_id": str(source_row["id"]),
                "question_sha256": hashlib.sha256(
                    str(source_row.get("question", "")).encode("utf-8")
                ).hexdigest(),
                "input_sha256": input_sha256(source_row),
                "model_label": spec.label,
                "model_requested": spec.requested_model,
                "model_resolved": resolved_model,
                "prompt_sha256": prompt_hash(),
                **payload,
                "latency_seconds": time.perf_counter() - started,
                "attempt_count": attempt,
                "api_error": None,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        except APIStatusError as exc:
            last_error = {"type": type(exc).__name__, "status_code": exc.status_code}
            retryable = exc.status_code in {408, 409, 429} or exc.status_code >= 500
            if not retryable:
                break
        except (APIConnectionError, APITimeoutError) as exc:
            last_error = {"type": type(exc).__name__, "status_code": None}
        if attempt < max_attempts:
            time.sleep(min(8.0, 2 ** (attempt - 1)) + random.random() * 0.25)
    return {
        "source_id": str(source_row["id"]),
        "question_sha256": hashlib.sha256(
            str(source_row.get("question", "")).encode("utf-8")
        ).hexdigest(),
        "input_sha256": input_sha256(source_row),
        "model_label": spec.label,
        "model_requested": spec.requested_model,
        "model_resolved": resolved_model,
        "model_returned": None,
        "prompt_sha256": prompt_hash(),
        "reasoning_content": "",
        "response_content": "",
        "final_answer": None,
        "parse_status": "api_error",
        "latency_seconds": time.perf_counter() - started,
        "token_usage": None,
        "attempt_count": attempt_count,
        "api_error": last_error,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def _completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for row in read_jsonl(path):
        if row.get("api_error") is None:
            completed.add(str(row["source_id"]))
    return completed


def _append_record(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def run_model(
    model_key: str,
    run_dir: Path,
    *,
    workers: int = 4,
    limit: int | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict[str, Any]:
    root = repo_root()
    source_path = root / SOURCE_RELATIVE_PATH
    selection_path = root / BENCHMARK_RELATIVE_DIR / "selection.jsonl"
    manifest_path = root / BENCHMARK_RELATIVE_DIR / "manifest.json"
    if not manifest_path.exists() or not selection_path.exists():
        raise RuntimeError("build the frozen benchmark before calling models")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("frozen") or manifest.get("selection_sha256") != sha256_file(selection_path):
        raise RuntimeError("benchmark manifest is not frozen or its selection hash changed")
    source_rows = read_jsonl(source_path)
    selection_rows = read_jsonl(selection_path)
    validate_source_and_selection(source_path, source_rows, selection_rows)
    selected = included_source_rows(source_rows, selection_rows)
    if limit is not None:
        selected = selected[:limit]
    spec = MODEL_SPECS[model_key]
    run_dir.mkdir(parents=True, exist_ok=True)
    resolution_path = run_dir / f"{model_key}.model_resolution.json"
    if resolution_path.exists():
        resolution = json.loads(resolution_path.read_text(encoding="utf-8"))
        resolved_model = str(resolution["resolved_model"])
    else:
        resolved_model, probe = resolve_model(spec, max_attempts=max_attempts)
        resolution = {
            "model_key": model_key,
            "model_label": spec.label,
            "requested_model": spec.requested_model,
            "resolved_model": resolved_model,
            "fallback_used": resolved_model != spec.requested_model,
            "probe": probe,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }
        resolution_path.write_text(json.dumps(resolution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_path = run_dir / f"{model_key}.predictions.jsonl"
    completed = _completed_ids(output_path)
    pending = [row for row in selected if str(row["id"]) not in completed]
    errors = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(call_problem, row, spec, resolved_model, max_attempts=max_attempts): str(row["id"])
            for row in pending
        }
        for future in as_completed(futures):
            row = future.result()
            _append_record(output_path, row)
            if row["api_error"] is not None:
                errors += 1
            print(
                json.dumps(
                    {
                        "model": model_key,
                        "source_id": row["source_id"],
                        "parse_status": row["parse_status"],
                        "api_error": row["api_error"],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    successful = len(_completed_ids(output_path))
    summary = {
        "model": model_key,
        "resolved_model": resolved_model,
        "target_count": len(selected),
        "successful_count": successful,
        "new_api_errors": errors,
        "complete": successful == len(selected),
        "output_path": str(output_path),
    }
    (run_dir / f"{model_key}.run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=(*MODEL_SPECS.keys(), "all"), required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 16:
        parser.error("--workers must be between 1 and 16")
    if not 1 <= args.max_attempts <= DEFAULT_MAX_ATTEMPTS:
        parser.error(f"--max-attempts must be between 1 and {DEFAULT_MAX_ATTEMPTS}")
    keys = tuple(MODEL_SPECS) if args.model == "all" else (args.model,)
    summaries = [
        run_model(
            key,
            args.run_dir,
            workers=args.workers,
            limit=args.limit,
            max_attempts=args.max_attempts,
        )
        for key in keys
    ]
    print(json.dumps({"summaries": summaries}, ensure_ascii=False, indent=2))
    return 0 if all(summary["complete"] for summary in summaries) else 2


if __name__ == "__main__":
    raise SystemExit(main())
