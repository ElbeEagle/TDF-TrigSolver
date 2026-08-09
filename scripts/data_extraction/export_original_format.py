#!/usr/bin/env python3
"""Export classified records using only their original dataset schema."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.data_extraction.dataset_adapters import iter_json_records


DEFAULT_INPUT = Path(
    "data/derived/trigonometry/cmm_math/tdf_trig_v1/A.jsonl"
)
DEFAULT_OUTPUT = DEFAULT_INPUT.with_name("A_original_format.jsonl")


def _json_line(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"


def export_original_format(
    input_path: str | Path,
    output_path: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Stream wrapper records and write only each unchanged ``raw_record``."""

    source = Path(input_path).resolve()
    output = Path(output_path).resolve()
    if source == output:
        raise ValueError("input and output paths must be different")
    if output.exists() and not overwrite:
        raise FileExistsError(
            f"output file already exists: {output}; use --overwrite to replace it"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}-", suffix=".tmp", dir=output.parent
    )
    temporary = Path(temporary_name)
    count = 0
    field_order: list[str] | None = None
    field_names: set[str] | None = None

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for row_index, wrapped in enumerate(iter_json_records(source)):
                raw_record = wrapped.get("raw_record")
                if not isinstance(raw_record, dict):
                    raise ValueError(
                        f"record {row_index} in {source} has no object-valued raw_record"
                    )

                classification = wrapped.get("classification")
                if isinstance(classification, dict):
                    label = classification.get("label")
                    if label != "A":
                        raise ValueError(
                            f"record {row_index} in {source} has label {label!r}, expected 'A'"
                        )

                current_order = list(raw_record)
                if field_order is None:
                    field_order = current_order
                    field_names = set(current_order)
                elif set(current_order) != field_names:
                    raise ValueError(
                        f"record {row_index} in {source} has inconsistent fields"
                    )

                handle.write(_json_line(raw_record))
                count += 1
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return {
        "input": str(source),
        "output": str(output),
        "records": count,
        "fields": field_order or [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export extracted A records with the original CMM-Math schema"
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = export_original_format(
        args.input,
        args.output,
        overwrite=args.overwrite,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
