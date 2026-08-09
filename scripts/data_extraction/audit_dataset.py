#!/usr/bin/env python3
"""Audit dataset schemas, field coverage, candidate signals, and rule contributions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.data_extraction.dataset_adapters import (
    iter_hf_rows,
    iter_local_normalized,
    make_adapter,
    parse_csv_fields,
)
from scripts.data_extraction.trig_rules import classify_record, matched_rule_ids


def audit(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    adapter = make_adapter(
        args.dataset,
        input_path=args.input,
        config=args.config,
        id_field=args.id_field,
        text_fields=parse_csv_fields(args.text_fields),
        auxiliary_fields=parse_csv_fields(args.auxiliary_fields),
        image_fields=parse_csv_fields(args.image_fields),
        group_field=args.group_field,
    )
    if args.hf_repo:
        if not args.config or not args.split:
            raise ValueError("--hf-repo requires --config and --split")
        records = iter_hf_rows(
            args.hf_repo,
            args.config,
            args.split,
            adapter=adapter,
            offset=args.offset,
            limit=args.limit,
            page_size=args.page_size,
        )
    else:
        records = iter_local_normalized(
            args.input,
            adapter,
            split=args.split,
            offset=args.offset,
            limit=args.limit,
            skip_invalid=args.skip_invalid,
            errors=errors,
        )

    counts = Counter()
    labels = Counter()
    confidence = Counter()
    schemas = Counter()
    empty_fields = Counter()
    splits = Counter()
    subjects = Counter()
    rules = Counter()
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for record in records:
        counts["records"] += 1
        schemas[tuple(sorted(record.raw_record))] += 1
        splits[record.split or "unknown"] += 1
        subject = record.raw_record.get("subject")
        if subject:
            subjects[str(subject)] += 1
        if not record.problem_text.strip():
            empty_fields["problem_text"] += 1
        if not record.auxiliary_text.strip():
            empty_fields["auxiliary_text"] += 1
        if not record.image_refs:
            empty_fields["image_refs"] += 1
        else:
            counts["records_with_image_refs"] += 1
        if record.record_id in seen_ids:
            duplicate_ids.append(record.record_id)
        seen_ids.add(record.record_id)

        classification = classify_record(record)
        if classification is None:
            counts["not_candidate"] += 1
            continue
        counts["candidates"] += 1
        label = classification["label"]
        labels[label] += 1
        confidence[f"{label}_{classification['confidence']}"] += 1
        for rule_id in matched_rule_ids(classification):
            rules[rule_id] += 1

    return {
        "dataset": args.dataset,
        "records": counts["records"],
        "unique_ids": len(seen_ids),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_id_examples": duplicate_ids[:20],
        "records_with_image_refs": counts["records_with_image_refs"],
        "empty_fields": dict(empty_fields),
        "splits": dict(splits),
        "subjects": dict(subjects),
        "schemas": [
            {"fields": list(fields), "count": count}
            for fields, count in schemas.most_common()
        ],
        "not_candidate": counts["not_candidate"],
        "candidates": counts["candidates"],
        "labels": dict(labels),
        "confidence": dict(confidence),
        "rule_contributions": dict(rules),
        "invalid_records": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input")
    source.add_argument("--hf-repo")
    parser.add_argument("--config")
    parser.add_argument("--split")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--output")
    parser.add_argument("--skip-invalid", action="store_true")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--group-field")
    parser.add_argument("--text-fields", default="question,options")
    parser.add_argument("--auxiliary-fields", default="analysis,solution,answer")
    parser.add_argument("--image-fields", default="image,images")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = audit(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

