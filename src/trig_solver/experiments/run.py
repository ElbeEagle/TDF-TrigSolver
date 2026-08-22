"""Run Raw/Oracle experiments without exposing gold fields to the solver."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, Field

import sympy as sp

from ..cas import CASExecutor, CASTimeout, CASUnsolved
from ..models import (
    AbstainCode,
    ExprAST,
    GoldAnswer,
    RawProblem,
    SetSpec,
    SolveResult,
    SolverConfig,
    TaskFamily,
    TraceStep,
    TrigURM,
)
from ..pipeline import solve_oracle, solve_raw
from ..qwen import QwenRawParser
from ..validator import match_options, render_value, result_matches_gold


class ReviewState(BaseModel):
    status: str = "pending"
    annotator: str | None = None
    independent_reviewer: str | None = None
    adjudication_note: str | None = None


class BenchmarkRecord(BaseModel):
    source_id: str
    split: str
    task_family: TaskFamily
    problem: RawProblem
    oracle_urm: TrigURM
    gold_option: str | None = None
    gold_answer: GoldAnswer | None = None
    template_group: str
    provenance: str = "verbatim"
    source_question_sha256: str | None = None
    review: ReviewState = Field(default_factory=ReviewState)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "unknown"


def _git_dirty(root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _implementation_hash(root: Path) -> str:
    digest = hashlib.sha256()
    paths = [root / "pyproject.toml", root / "scripts" / "build_trig_pilot_benchmark.py"]
    paths.extend(sorted((root / "src" / "trig_solver").rglob("*.py")))
    for path in paths:
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_records(path: Path) -> list[BenchmarkRecord]:
    records: list[BenchmarkRecord] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                records.append(BenchmarkRecord.model_validate_json(line))
            except ValueError as exc:
                raise ValueError(f"invalid benchmark row {path}:{line_number}: {exc}") from exc
    return records


def check_frozen(root: Path, split: str, data_path: Path, records: list[BenchmarkRecord]) -> None:
    if split != "test":
        return
    manifest_path = data_path.parent / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("frozen test requires manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("frozen"):
        raise RuntimeError("test manifest is not frozen")
    expected_hash = manifest.get("test_sha256")
    if not expected_hash or expected_hash != _sha256(data_path):
        raise RuntimeError("test file hash does not match the frozen manifest")
    pending = [item.source_id for item in records if item.review.status != "double_verified" or not item.review.independent_reviewer]
    if pending:
        raise RuntimeError(f"test has {len(pending)} records without independent review")


def _correct(result: SolveResult, record: BenchmarkRecord, *, require_option: bool = True) -> bool:
    if result.status != "solved" or record.gold_answer is None:
        return False
    if not result_matches_gold(result, record.gold_answer):
        return False
    return not (require_option and record.gold_option) or result.option == record.gold_option


def _modes(requested: str) -> Iterable[str]:
    return ("oracle", "raw") if requested == "both" else (requested,)


def _cas_only(record: BenchmarkRecord, config: SolverConfig) -> SolveResult:
    target = record.oracle_urm.expressions[0].ast.to_sympy()
    variable = (
        sp.Symbol(record.oracle_urm.angles[0].symbol, real=True)
        if record.oracle_urm.angles
        else next(iter(target.free_symbols), sp.Symbol("x", real=True))
    )
    cas = CASExecutor(config.cas_timeout_seconds)
    family = record.task_family
    operator = record.oracle_urm.goal.operator
    try:
        if family in {TaskFamily.EVAL, TaskFamily.IDENTITY}:
            value = cas.run("simplify", cas.run("trigsimp", target))
        elif family == TaskFamily.SINUSOID_PROPERTY and operator == "property" and record.oracle_urm.goal.property_names == ["period"]:
            value = cas.run("periodicity", target, variable)
        elif family == TaskFamily.EQUATION:
            value = cas.run("solveset", target, variable)
        elif family == TaskFamily.DOMAIN_RANGE_INEQUALITY and operator == "domain":
            value = cas.run("continuous_domain", target, variable)
        elif family == TaskFamily.DOMAIN_RANGE_INEQUALITY and operator == "solve_inequality":
            value = cas.run("solve_inequality", target, variable)
        else:
            return SolveResult.abstain(AbstainCode.CAS_UNSOLVED, "CAS-only baseline has no direct operation")
        answer = render_value(value)
        option = None
        if record.problem.options:
            option, error = match_options(value, record.problem.options)
            if error:
                return SolveResult.abstain(AbstainCode.VALIDATION_NO_MATCH, error)
        return SolveResult(
            status="solved",
            answer_kind="cas_result",
            answer=answer,
            value=answer,
            expression=None if isinstance(value, sp.Set) else ExprAST.from_sympy(value) if isinstance(value, sp.Basic) else None,
            set_value=SetSpec.from_sympy(value) if isinstance(value, sp.Set) else None,
            option=option,
            trace=[
                TraceStep(
                    tmm_id="CAS-only",
                    operation=operator,
                    input_summary=sp.sstr(target),
                    output_summary=answer,
                    verified=True,
                )
            ],
        )
    except CASTimeout as exc:
        return SolveResult.abstain(AbstainCode.CAS_TIMEOUT, str(exc))
    except (CASUnsolved, TypeError, ValueError, NotImplementedError) as exc:
        return SolveResult.abstain(AbstainCode.CAS_UNSOLVED, str(exc))


def run_experiment(split: str, mode: str, variant: str, freeze_check: bool) -> tuple[Path, dict[str, Any]]:
    root = _repo_root()
    data_path = root / "data" / "benchmarks" / "trig_pilot_v1" / f"{split}.jsonl"
    if split == "test":
        # Test execution is always gated. The CLI flag is retained for command
        # compatibility, but omitting it cannot bypass the research protocol.
        check_frozen(root, split, data_path, [])
    records = load_records(data_path)
    if freeze_check and split != "test":
        check_frozen(root, split, data_path, records)
    elif split == "test":
        check_frozen(root, split, data_path, records)
    config = SolverConfig(
        enable_periodic_completion=variant != "no-periodic",
        enable_validator=variant != "no-validator",
    )
    rows: list[dict[str, Any]] = []
    for current_mode in _modes(mode):
        for record in records:
            started = time.perf_counter()
            if variant == "cas-only":
                if current_mode != "oracle":
                    raise ValueError("cas-only baseline requires --mode oracle")
                result = _cas_only(record, config)
            else:
                result = (
                    solve_oracle(record.oracle_urm, record.problem.options, config)
                    if current_mode == "oracle"
                    else solve_raw(record.problem, config)
                )
            latency_seconds = time.perf_counter() - started
            rows.append(
                {
                    "source_id": record.source_id,
                    "mode": current_mode,
                    "variant": variant,
                    "task_family": record.task_family,
                    "correct": _correct(result, record, require_option=variant != "no-validator"),
                    "gold_option": record.gold_option,
                    "gold_answer": record.gold_answer.model_dump(mode="json") if record.gold_answer else None,
                    "latency_seconds": latency_seconds,
                    "total_tokens": int(result.metadata.get("total_tokens", 0)),
                    "result": result.model_dump(mode="json"),
                }
            )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = root / "results" / "trig_pilot" / f"{timestamp}-{split}-{mode}-{variant}"
    output_dir.mkdir(parents=True, exist_ok=False)
    results_path = output_dir / "predictions.jsonl"
    results_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    summary = summarize_rows(rows)
    summary.update(
        {
            "split": split,
            "mode": mode,
            "variant": variant,
            "dataset_sha256": _sha256(data_path),
            "git_commit": _git_commit(root),
            "git_dirty": _git_dirty(root),
            "implementation_sha256": _implementation_hash(root),
            "model_snapshot": config.model_name if "raw" in tuple(_modes(mode)) else None,
            "prompt_sha256": QwenRawParser.prompt_hash() if "raw" in tuple(_modes(mode)) else None,
            "created_at": timestamp,
        }
    )
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_dir, summary


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(bool(row["correct"]) for row in rows)
    attempted = sum(row["result"]["status"] == "solved" for row in rows)
    failures = Counter(
        row["result"].get("abstain_code") or "WRONG_ANSWER"
        for row in rows
        if not row["correct"]
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['mode']}:{row['task_family']}"].append(row)
    by_group = {
        key: {
            "n": len(items),
            "correct": sum(bool(item["correct"]) for item in items),
            "accuracy": sum(bool(item["correct"]) for item in items) / len(items),
        }
        for key, items in sorted(grouped.items())
    }
    periodic_rows = [
        row
        for row in rows
        if row["task_family"] in {TaskFamily.EQUATION, TaskFamily.DOMAIN_RANGE_INEQUALITY}
        and row["result"].get("periodic_set") is not None
    ]
    return {
        "n": total,
        "correct": correct,
        "overall_accuracy": correct / total if total else 0.0,
        "coverage": attempted / total if total else 0.0,
        "conditional_accuracy": correct / attempted if attempted else 0.0,
        "periodic_completeness": (
            sum(bool(row["correct"]) for row in periodic_rows) / len(periodic_rows) if periodic_rows else 0.0
        ),
        "mean_latency_seconds": sum(float(row["latency_seconds"]) for row in rows) / total if total else 0.0,
        "total_tokens": sum(int(row["total_tokens"]) for row in rows),
        "failure_types": dict(sorted(failures.items())),
        "by_group": by_group,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the frozen TrigSolver pilot protocol")
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--mode", choices=("raw", "oracle", "both"), required=True)
    parser.add_argument("--variant", choices=("full", "cas-only", "no-periodic", "no-validator"), default="full")
    parser.add_argument("--freeze-check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output_dir, summary = run_experiment(args.split, args.mode, args.variant, args.freeze_check)
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps({"output_dir": str(output_dir), "summary": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
