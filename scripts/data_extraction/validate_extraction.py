#!/usr/bin/env python3
"""Validate extraction integrity against outputs and an optional local source."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.data_extraction.dataset_adapters import iter_json_records
from scripts.data_extraction.trig_rules import LABELS


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.output_dir)
    errors: list[str] = []
    warnings: list[str] = []
    all_path = root / "all_candidates.jsonl"
    if not all_path.exists():
        raise FileNotFoundError(f"missing {all_path}")

    all_ids: set[str] = set()
    all_keys: set[tuple[str, str]] = set()
    source_hashes: dict[str, str] = {}
    label_counts = Counter()
    image_checks = Counter()
    candidate_count = 0

    for item in iter_json_records(all_path):
        candidate_count += 1
        source = item.get("source", {})
        classification = item.get("classification", {})
        record_id = str(source.get("id", ""))
        label = classification.get("label")
        if not record_id:
            errors.append(f"candidate {candidate_count} has no source id")
        if record_id in all_ids:
            errors.append(f"duplicate candidate id: {record_id}")
        all_ids.add(record_id)
        if label not in LABELS:
            errors.append(f"{record_id}: invalid label {label!r}")
            continue
        label_counts[label] += 1
        all_keys.add((record_id, label))
        rules = classification.get("matched_rules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{record_id}: classification has no matched_rules evidence")
        if not isinstance(item.get("raw_record"), dict):
            errors.append(f"{record_id}: raw_record is not an object")
        else:
            group_id = str(source.get("group_id", record_id))
            source_hashes.setdefault(group_id, _canonical_hash(item["raw_record"]))

        for media in item.get("normalized", {}).get("downloaded_images", []):
            if media.get("status") != "downloaded":
                image_checks[media.get("status", "unknown")] += 1
                continue
            path = root / str(media.get("path", ""))
            if not path.is_file():
                errors.append(f"{record_id}: downloaded image missing: {path}")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != media.get("sha256"):
                errors.append(f"{record_id}: image hash mismatch: {path}")
            else:
                image_checks["verified"] += 1

    classified_keys: set[tuple[str, str]] = set()
    classified_total = 0
    for label in LABELS:
        path = root / f"{label}.jsonl"
        if not path.exists():
            errors.append(f"missing label file: {path.name}")
            continue
        file_count = 0
        for item in iter_json_records(path):
            file_count += 1
            record_id = str(item.get("source", {}).get("id", ""))
            actual = item.get("classification", {}).get("label")
            if actual != label:
                errors.append(f"{path.name}: {record_id} carries label {actual!r}")
            key = (record_id, label)
            if key in classified_keys:
                errors.append(f"duplicate entry in label files: {record_id}/{label}")
            classified_keys.add(key)
        classified_total += file_count
        if file_count != label_counts[label]:
            errors.append(
                f"{label}.jsonl count {file_count} != all_candidates count {label_counts[label]}"
            )

    if classified_total != candidate_count:
        errors.append(
            f"label file total {classified_total} != candidate total {candidate_count}"
        )
    if classified_keys != all_keys:
        errors.append("classification files do not contain the same id/label pairs as all_candidates")

    source_checked = 0
    source_missing: set[str] = set(source_hashes)
    if args.source:
        for raw in iter_json_records(args.source):
            raw_id = str(raw.get(args.source_id_field, ""))
            if raw_id not in source_hashes:
                continue
            source_checked += 1
            source_missing.discard(raw_id)
            if _canonical_hash(raw) != source_hashes[raw_id]:
                errors.append(f"source raw_record mismatch for id {raw_id}")
        if source_missing:
            errors.append(
                f"{len(source_missing)} extracted group ids were not found in source; "
                f"examples: {sorted(source_missing)[:10]}"
            )

    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        errors.append("missing manifest.json")
    audit_path = root / "audit.json"
    if not audit_path.exists():
        errors.append("missing audit.json")
    review_path = root / "review_sample.jsonl"
    if not review_path.exists():
        errors.append("missing review_sample.jsonl")

    report = {
        "status": "passed" if not errors else "failed",
        "candidate_count": candidate_count,
        "label_counts": dict(label_counts),
        "unique_ids": len(all_ids),
        "source_records_checked": source_checked,
        "media_checks": dict(image_checks),
        "errors": errors,
        "warnings": warnings,
    }
    target = root / "validation.json"
    target.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source", help="optional original local JSON/JSONL")
    parser.add_argument("--source-id-field", default="id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

