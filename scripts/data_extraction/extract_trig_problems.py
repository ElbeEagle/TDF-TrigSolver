#!/usr/bin/env python3
"""Extract explainable A/B/C/MIXED/UNCERTAIN trigonometry subsets."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.data_extraction import RULE_VERSION
from scripts.data_extraction.dataset_adapters import (
    NormalizedRecord,
    iter_hf_rows,
    iter_local_normalized,
    make_adapter,
    parse_csv_fields,
)
from scripts.data_extraction.trig_rules import LABELS, classify_record, matched_rule_ids

DEFAULT_DOWNLOAD_LABELS = ("A", "MIXED", "UNCERTAIN")
REVIEW_TARGETS = {
    "A_high": 30,
    "A_medium": 30,
    "B": 30,
    "C": 20,
    "MIXED": 20,
    "UNCERTAIN": 20,
}


class Reservoir:
    def __init__(self, size: int, seed: int) -> None:
        self.size = size
        self.random = random.Random(seed)
        self.seen = 0
        self.items: list[dict[str, Any]] = []

    def add(self, item: dict[str, Any]) -> None:
        self.seen += 1
        if len(self.items) < self.size:
            self.items.append(item)
            return
        replacement = self.random.randrange(self.seen)
        if replacement < self.size:
            self.items[replacement] = item


def _stable_seed(base: int, value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base + int.from_bytes(digest[:4], "big")


def _json_line(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_id(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return result[:120] or "record"


def _extension(url: str, content_type: str | None) -> str:
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
        if guessed:
            return ".jpg" if guessed == ".jpe" else guessed
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"} else ".img"


def _download_selected_images(
    record: NormalizedRecord,
    output_root: Path,
    *,
    token: str | None,
    remaining: int | None,
) -> tuple[list[dict[str, Any]], int]:
    results: list[dict[str, Any]] = []
    used = 0
    for index, url in enumerate(record.image_refs):
        if remaining is not None and used >= remaining:
            break
        if not url.startswith(("http://", "https://")):
            results.append({"source_url": url, "status": "reference_only"})
            continue
        request = urllib.request.Request(url)
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
            digest = hashlib.sha256(payload).hexdigest()
            filename = (
                f"{_safe_id(record.record_id)}-{index}-{digest[:16]}"
                f"{_extension(url, content_type)}"
            )
            relative = Path("images") / filename
            target = output_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            results.append(
                {
                    "source_url": url,
                    "status": "downloaded",
                    "path": relative.as_posix(),
                    "sha256": digest,
                    "bytes": len(payload),
                }
            )
            used += 1
        except (urllib.error.URLError, OSError) as exc:
            results.append(
                {"source_url": url, "status": "error", "error": str(exc)}
            )
    return results, used


def _fetch_hf_metadata(repo: str, token: str | None) -> dict[str, Any]:
    url = f"https://huggingface.co/api/datasets/{urllib.parse.quote(repo, safe='/')}"
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        return {
            "id": payload.get("id"),
            "sha": payload.get("sha"),
            "last_modified": payload.get("lastModified"),
            "private": payload.get("private"),
            "gated": payload.get("gated"),
        }
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"metadata_error": str(exc)}


def _iter_input(args: argparse.Namespace) -> tuple[Iterator[NormalizedRecord], list[dict[str, Any]], Any]:
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
            raise ValueError("--hf-repo requires both --config and --split")
        iterator = iter_hf_rows(
            args.hf_repo,
            args.config,
            args.split,
            adapter=adapter,
            offset=args.offset,
            limit=args.limit,
            page_size=args.page_size,
            hf_token=os.environ.get("HF_TOKEN"),
        )
    else:
        if not args.input:
            raise ValueError("one of --input or --hf-repo is required")
        iterator = iter_local_normalized(
            args.input,
            adapter,
            split=args.split,
            skip_invalid=args.skip_invalid,
            errors=errors,
            offset=args.offset,
            limit=args.limit,
        )
    return iterator, errors, adapter


def _default_output(dataset: str) -> Path:
    return Path("data") / "derived" / "trigonometry" / dataset / RULE_VERSION


def extract(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output_dir) if args.output_dir else _default_output(args.dataset)
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise FileExistsError(
            f"output directory already exists: {output}; use --overwrite to replace it"
        )
    if output.exists() and args.overwrite:
        shutil.rmtree(output)

    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    iterator, parse_errors, _adapter = _iter_input(args)
    files: dict[str, Any] = {}
    stats: dict[str, Counter[str]] = {
        "labels": Counter(),
        "confidence": Counter(),
        "splits": Counter(),
        "rules": Counter(),
        "subjects": Counter(),
    }
    counters = Counter()
    review = {
        stratum: Reservoir(size, _stable_seed(args.review_seed, stratum))
        for stratum, size in REVIEW_TARGETS.items()
    }
    token = os.environ.get("HF_TOKEN")
    download_labels = set(parse_csv_fields(args.download_images_for))
    download_count = 0

    try:
        files["all"] = (temporary / "all_candidates.jsonl").open("w", encoding="utf-8")
        for label in LABELS:
            files[label] = (temporary / f"{label}.jsonl").open("w", encoding="utf-8")

        for normalized in iterator:
            counters["scanned"] += 1
            stats["splits"][normalized.split or "unknown"] += 1
            subject = normalized.raw_record.get("subject")
            if subject:
                stats["subjects"][str(subject)] += 1
            classification = classify_record(normalized)
            if classification is None:
                counters["not_candidate"] += 1
                continue
            counters["candidates"] += 1
            label = classification["label"]
            stats["labels"][label] += 1
            stats["confidence"][f"{label}_{classification['confidence']}"] += 1
            for rule_id in matched_rule_ids(classification):
                stats["rules"][rule_id] += 1
            if normalized.image_refs:
                counters["candidates_with_image_refs"] += 1
                if label == "A":
                    counters["a_with_image_refs"] += 1

            normalized_payload = normalized.normalized_dict()
            should_download = args.hf_repo and label in download_labels
            if should_download and (
                args.max_download_images is None
                or download_count < args.max_download_images
            ):
                remaining = (
                    None
                    if args.max_download_images is None
                    else args.max_download_images - download_count
                )
                downloaded, used = _download_selected_images(
                    normalized, temporary, token=token, remaining=remaining
                )
                if downloaded:
                    normalized_payload["downloaded_images"] = downloaded
                download_count += used

            wrapper = {
                "source": normalized.source_dict(),
                "normalized": normalized_payload,
                "classification": classification,
                "raw_record": normalized.raw_record,
            }
            line = _json_line(wrapper)
            files["all"].write(line)
            files[label].write(line)

            if label == "A":
                stratum = f"A_{classification['confidence']}"
            else:
                stratum = label
            if stratum in review:
                review[stratum].add(wrapper)

        for handle in files.values():
            handle.close()
        files.clear()

        review_path = temporary / "review_sample.jsonl"
        with review_path.open("w", encoding="utf-8") as handle:
            for stratum in REVIEW_TARGETS:
                for item in review[stratum].items:
                    sample = dict(item)
                    sample["review_stratum"] = stratum
                    handle.write(_json_line(sample))

        audit = {
            "rule_version": RULE_VERSION,
            "scanned": counters["scanned"],
            "not_candidate": counters["not_candidate"],
            "candidates": counters["candidates"],
            "labels": dict(stats["labels"]),
            "confidence": dict(stats["confidence"]),
            "splits": dict(stats["splits"]),
            "subjects": dict(stats["subjects"]),
            "rule_contributions": dict(stats["rules"]),
            "candidates_with_image_refs": counters["candidates_with_image_refs"],
            "a_with_image_refs": counters["a_with_image_refs"],
            "invalid_records": parse_errors,
            "historical_sanity_check": {
                "historical_a_candidates": 499,
                "historical_a_with_images": 81,
                "is_acceptance_target": False,
                "difference_explanation": (
                    "v1 also admits formula-only direct tasks and semantic periodic models; "
                    "counts are diagnostic and are never tuned to match the historical screen"
                ),
            },
        }
        (temporary / "audit.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        source: dict[str, Any]
        if args.hf_repo:
            source = {
                "kind": "huggingface_dataset_viewer",
                "repo": args.hf_repo,
                "config": args.config,
                "split": args.split,
                "offset": args.offset,
                "limit": args.limit,
                "hub_metadata": _fetch_hf_metadata(args.hf_repo, token),
            }
        else:
            input_path = Path(args.input).resolve()
            source = {
                "kind": "local",
                "path": str(input_path),
                "sha256": _sha256_file(input_path),
                "offset": args.offset,
                "limit": args.limit,
            }
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "rule_version": RULE_VERSION,
            "dataset": args.dataset,
            "source": source,
            "output_schema": 1,
            "counts": {
                "scanned": counters["scanned"],
                "candidates": counters["candidates"],
                "labels": dict(stats["labels"]),
            },
            "download_images_for": sorted(download_labels),
            "downloaded_image_count": download_count,
            "review_seed": args.review_seed,
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (temporary / "validation.json").write_text(
            json.dumps(
                {
                    "status": "not_run",
                    "message": "run validate_extraction.py for source-level validation",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, output)
        return {"output_dir": str(output), **audit}
    except Exception:
        for handle in files.values():
            handle.close()
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="local JSON/JSONL input")
    source.add_argument("--hf-repo", help="Hugging Face dataset repo, e.g. AI4Math/MathVista")
    parser.add_argument("--config")
    parser.add_argument("--split")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--output-dir")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-invalid", action="store_true")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--group-field")
    parser.add_argument("--text-fields", default="question,options")
    parser.add_argument("--auxiliary-fields", default="analysis,solution,answer")
    parser.add_argument("--image-fields", default="image,images")
    parser.add_argument(
        "--download-images-for", default=",".join(DEFAULT_DOWNLOAD_LABELS)
    )
    parser.add_argument("--max-download-images", type=int)
    parser.add_argument("--review-seed", type=int, default=20260809)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = extract(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

