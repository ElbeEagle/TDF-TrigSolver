"""Conservative exact scoring plus blinded adjudication export/finalization."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.llm_eval.protocol import (
    BENCHMARK_RELATIVE_DIR,
    EXPECTED_INCLUDED,
    MODEL_SPECS,
    SOURCE_RELATIVE_PATH,
    extract_choice,
    included_source_rows,
    normalize_open_answer,
    read_jsonl,
    repo_root,
    sha256_file,
    validate_source_and_selection,
    write_jsonl,
)


ANONYMIZATION_SEED = "cmm-trig-text-llm-v1-blinded-review"
VERDICTS = {"correct", "incorrect", "uncertain"}
REVIEW_BATCH_SIZE = 50


def build_blinded_review_records(
    model_key: str,
    source: dict[str, Any],
    prediction: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    source_id = str(source["id"])
    digest = hashlib.sha256(f"{ANONYMIZATION_SEED}|{model_key}|{source_id}".encode()).hexdigest()
    judgment_id = f"J-{digest[:16]}"
    review_item = {
        "judgment_id": judgment_id,
        "question": source.get("question", ""),
        "options": source.get("options") or None,
        "reference_answer": source.get("answer", ""),
        "reference_analysis": source.get("analysis", ""),
        "candidate_answer": prediction.get("final_answer"),
        "candidate_response": prediction.get("response_content", ""),
    }
    private_map = {"judgment_id": judgment_id, "model_key": model_key, "source_id": source_id}
    return review_item, private_map


def _load_context(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    root = repo_root()
    source_path = root / SOURCE_RELATIVE_PATH
    selection_path = root / BENCHMARK_RELATIVE_DIR / "selection.jsonl"
    manifest_path = root / BENCHMARK_RELATIVE_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("frozen") or manifest["selection_sha256"] != sha256_file(selection_path):
        raise RuntimeError("benchmark selection is not frozen")
    source_rows = read_jsonl(source_path)
    selection_rows = read_jsonl(selection_path)
    validate_source_and_selection(source_path, source_rows, selection_rows)
    selected = included_source_rows(source_rows, selection_rows)
    source_by_id = {str(row["id"]): row for row in selected}
    return selected, source_by_id


def stage_one(run_dir: Path) -> dict[str, Any]:
    selected, source_by_id = _load_context(run_dir)
    stage_rows: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    private_map: list[dict[str, Any]] = []
    for model_key in MODEL_SPECS:
        prediction_path = run_dir / f"{model_key}.predictions.jsonl"
        predictions = read_jsonl(prediction_path)
        by_id: dict[str, dict[str, Any]] = {}
        for prediction in predictions:
            source_id = str(prediction["source_id"])
            if source_id in by_id and prediction.get("api_error") is None:
                raise RuntimeError(f"duplicate successful prediction: {model_key}/{source_id}")
            if prediction.get("api_error") is None:
                by_id[source_id] = prediction
        missing = sorted(set(source_by_id) - set(by_id))
        if missing:
            raise RuntimeError(f"{model_key} has {len(missing)} missing successful predictions")
        if len(by_id) != EXPECTED_INCLUDED:
            raise RuntimeError(f"{model_key} must have exactly {EXPECTED_INCLUDED} successful predictions")
        for source in selected:
            source_id = str(source["id"])
            prediction = by_id[source_id]
            output_format = "multiple_choice" if source.get("options") else "open"
            reference_answer = str(source.get("answer", "")).strip()
            if output_format == "multiple_choice":
                predicted_choice = extract_choice(prediction.get("final_answer"))
                correct = predicted_choice == reference_answer.upper()
                status = "exact_match" if correct else "judged_incorrect"
                needs_review = False
                normalized_prediction = predicted_choice or ""
                normalized_reference = reference_answer.upper()
            else:
                normalized_prediction = normalize_open_answer(prediction.get("final_answer"))
                normalized_reference = normalize_open_answer(reference_answer)
                correct = bool(normalized_reference) and normalized_prediction == normalized_reference
                status = "exact_match" if correct else "needs_review"
                needs_review = not correct
            base = {
                "source_id": source_id,
                "model_key": model_key,
                "output_format": output_format,
                "normalized_prediction": normalized_prediction,
                "normalized_reference": normalized_reference,
                "stage_one_status": status,
                "correct": correct if not needs_review else None,
                "judgment_id": None,
            }
            if needs_review:
                review_item, map_item = build_blinded_review_records(model_key, source, prediction)
                judgment_id = review_item["judgment_id"]
                base["judgment_id"] = judgment_id
                review_items.append(review_item)
                private_map.append(map_item)
            stage_rows.append(base)
    random.Random(ANONYMIZATION_SEED).shuffle(review_items)
    review_dir = run_dir / "review"
    write_jsonl(run_dir / "stage_one_scores.jsonl", stage_rows)
    write_jsonl(review_dir / "judgment_queue.blinded.jsonl", review_items)
    write_jsonl(review_dir / "judgment_map.private.jsonl", private_map)
    batch_dir = review_dir / "batches"
    for old_batch in batch_dir.glob("batch_*.jsonl") if batch_dir.exists() else ():
        old_batch.unlink()
    for offset in range(0, len(review_items), REVIEW_BATCH_SIZE):
        batch_number = offset // REVIEW_BATCH_SIZE + 1
        write_jsonl(
            batch_dir / f"batch_{batch_number:03d}.jsonl",
            review_items[offset : offset + REVIEW_BATCH_SIZE],
        )
    write_jsonl(
        review_dir / "adjudications.template.jsonl",
        [
            {"judgment_id": item["judgment_id"], "verdict": None, "rationale": ""}
            for item in review_items
        ],
    )
    summary = {
        "n_predictions": len(stage_rows),
        "exact_matches": sum(row["stage_one_status"] == "exact_match" for row in stage_rows),
        "direct_incorrect_multiple_choice": sum(
            row["stage_one_status"] == "judged_incorrect" for row in stage_rows
        ),
        "needs_review": len(review_items),
        "review_batch_size": REVIEW_BATCH_SIZE,
        "review_batch_count": (len(review_items) + REVIEW_BATCH_SIZE - 1) // REVIEW_BATCH_SIZE,
        "review_queue_sha256": sha256_file(review_dir / "judgment_queue.blinded.jsonl"),
    }
    (run_dir / "stage_one_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def finalize(run_dir: Path, adjudications_path: Path) -> dict[str, Any]:
    stage_rows = read_jsonl(run_dir / "stage_one_scores.jsonl")
    map_rows = read_jsonl(run_dir / "review" / "judgment_map.private.jsonl")
    adjudications = read_jsonl(adjudications_path)
    mapping = {row["judgment_id"]: row for row in map_rows}
    verdict_by_id: dict[str, dict[str, Any]] = {}
    for row in adjudications:
        judgment_id = str(row.get("judgment_id", ""))
        verdict = row.get("verdict")
        if judgment_id not in mapping:
            raise RuntimeError(f"unknown judgment id: {judgment_id}")
        if judgment_id in verdict_by_id:
            raise RuntimeError(f"duplicate judgment id: {judgment_id}")
        if verdict not in VERDICTS:
            raise RuntimeError(f"invalid or missing verdict for {judgment_id}: {verdict!r}")
        verdict_by_id[judgment_id] = row
    expected_ids = set(mapping)
    if set(verdict_by_id) != expected_ids:
        raise RuntimeError(f"adjudication coverage mismatch: expected {len(expected_ids)}, got {len(verdict_by_id)}")
    uncertain = [key for key, row in verdict_by_id.items() if row["verdict"] == "uncertain"]
    if uncertain:
        raise RuntimeError(f"{len(uncertain)} uncertain judgments require human resolution")
    final_rows: list[dict[str, Any]] = []
    for row in stage_rows:
        final = dict(row)
        judgment_id = row.get("judgment_id")
        if judgment_id:
            adjudication = verdict_by_id[judgment_id]
            final["final_status"] = f"judged_{adjudication['verdict']}"
            final["correct"] = adjudication["verdict"] == "correct"
            final["rationale"] = adjudication.get("rationale", "")
        else:
            final["final_status"] = row["stage_one_status"]
            final["rationale"] = ""
        final_rows.append(final)
    write_jsonl(run_dir / "final_scores.jsonl", final_rows)
    summary: dict[str, Any] = {
        "denominator_per_model": EXPECTED_INCLUDED,
        "models": {},
        "adjudications_sha256": sha256_file(adjudications_path),
    }
    for model_key, spec in MODEL_SPECS.items():
        rows = [row for row in final_rows if row["model_key"] == model_key]
        if len(rows) != EXPECTED_INCLUDED:
            raise RuntimeError(f"final score count mismatch for {model_key}")
        correct = sum(bool(row["correct"]) for row in rows)
        summary["models"][model_key] = {
            "label": spec.label,
            "correct": correct,
            "n": EXPECTED_INCLUDED,
            "accuracy": correct / EXPECTED_INCLUDED,
            "status_counts": dict(Counter(row["final_status"] for row in rows)),
        }
    (run_dir / "final_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    stage_parser = subparsers.add_parser("stage-one")
    stage_parser.add_argument("--run-dir", type=Path, required=True)
    final_parser = subparsers.add_parser("finalize")
    final_parser.add_argument("--run-dir", type=Path, required=True)
    final_parser.add_argument("--adjudications", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "stage-one":
        result = stage_one(args.run_dir)
    else:
        result = finalize(args.run_dir, args.adjudications)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
