"""Build and freeze the 795-row audit / 726-row text-only selection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.llm_eval.protocol import (
    BENCHMARK_RELATIVE_DIR,
    EXPECTED_EXCLUDED,
    EXPECTED_INCLUDED,
    EXPECTED_MULTIPLE_CHOICE,
    EXPECTED_OPEN,
    EXPECTED_OPEN_MISSING_ANSWER,
    EXPECTED_SOURCE_SHA256,
    EXPECTED_TOTAL,
    SOURCE_RELATIVE_PATH,
    build_selection_rows,
    read_jsonl,
    repo_root,
    sha256_file,
    validate_source_and_selection,
    write_jsonl,
)


def build(output_dir: Path | None = None) -> tuple[Path, Path]:
    root = repo_root()
    source_path = root / SOURCE_RELATIVE_PATH
    target_dir = output_dir or root / BENCHMARK_RELATIVE_DIR
    selection_path = target_dir / "selection.jsonl"
    manifest_path = target_dir / "manifest.json"
    source_rows = read_jsonl(source_path)
    selection_rows = build_selection_rows(source_rows)
    validate_source_and_selection(source_path, source_rows, selection_rows)
    write_jsonl(selection_path, selection_rows)
    manifest = {
        "schema_version": "1.0",
        "name": "CMM-Math trigonometry text-only direct-LLM evaluation",
        "frozen": True,
        "source_path": str(SOURCE_RELATIVE_PATH),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_count": EXPECTED_TOTAL,
        "included_count": EXPECTED_INCLUDED,
        "excluded_nonempty_image_count": EXPECTED_EXCLUDED,
        "multiple_choice_count": EXPECTED_MULTIPLE_CHOICE,
        "open_count": EXPECTED_OPEN,
        "open_missing_answer_count": EXPECTED_OPEN_MISSING_ANSWER,
        "selection_path": "selection.jsonl",
        "selection_sha256": sha256_file(selection_path),
        "scope_label": "CMM-Math trigonometry text-only subset accuracy",
        "selection_rule": "include only rows whose image array is empty; apply no other scope filter",
    }
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return selection_path, manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    selection_path, manifest_path = build(args.output_dir)
    print(json.dumps({"selection": str(selection_path), "manifest": str(manifest_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
