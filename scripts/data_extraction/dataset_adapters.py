#!/usr/bin/env python3
"""Streaming readers and dataset-specific normalization adapters."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


class DatasetFormatError(ValueError):
    """Raised when an input record cannot be decoded or normalized."""


@dataclass(slots=True)
class NormalizedRecord:
    dataset: str
    config: str | None
    split: str | None
    record_id: str
    group_id: str
    row_index: int
    problem_text: str
    auxiliary_text: str
    image_refs: list[str]
    raw_record: dict[str, Any]

    def source_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "config": self.config,
            "split": self.split,
            "id": self.record_id,
            "group_id": self.group_id,
            "row_index": self.row_index,
        }

    def normalized_dict(self) -> dict[str, Any]:
        return {
            "problem_text": self.problem_text,
            "auxiliary_text": self.auxiliary_text,
            "image_refs": self.image_refs,
        }


def _stringify(value: Any) -> str:
    if value is None or value == "null":
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return "\n".join(_stringify(item) for item in value if item is not None)
    if isinstance(value, Mapping):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _flatten_image_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if not value:
        return refs
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        src = value.get("src") or value.get("url") or value.get("path")
        if src:
            refs.append(str(src))
        return refs
    if isinstance(value, Sequence):
        for item in value:
            refs.extend(_flatten_image_refs(item))
    return refs


def iter_json_records(
    path: str | Path,
    *,
    skip_invalid: bool = False,
    errors: list[dict[str, Any]] | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield records from JSONL or a top-level JSON object/array.

    JSONL is processed line-by-line. JSON arrays are decoded incrementally from a
    bounded buffer, so a large array does not need to be loaded into memory.
    """

    source = Path(path)
    if source.suffix.lower() in {".jsonl", ".ndjson"}:
        with source.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise DatasetFormatError("record is not a JSON object")
                except (json.JSONDecodeError, DatasetFormatError) as exc:
                    detail = {
                        "path": str(source),
                        "line": line_number,
                        "error": str(exc),
                    }
                    if errors is not None:
                        errors.append(detail)
                    if skip_invalid:
                        continue
                    raise DatasetFormatError(
                        f"{source}:{line_number}: invalid JSONL record: {exc}"
                    ) from exc
                yield value
        return

    yield from _iter_json_document(
        source, skip_invalid=skip_invalid, errors=errors
    )


def _iter_json_document(
    source: Path,
    *,
    skip_invalid: bool,
    errors: list[dict[str, Any]] | None,
    chunk_size: int = 64 * 1024,
) -> Iterator[dict[str, Any]]:
    decoder = json.JSONDecoder()
    with source.open("r", encoding="utf-8-sig") as handle:
        buffer = ""
        position = 0
        eof = False

        def refill() -> None:
            nonlocal buffer, position, eof
            if position:
                buffer = buffer[position:]
                position = 0
            chunk = handle.read(chunk_size)
            if chunk:
                buffer += chunk
            else:
                eof = True

        refill()
        while not eof and not buffer.strip():
            refill()
        position = len(buffer) - len(buffer.lstrip())
        if position >= len(buffer):
            return

        if buffer[position] == "{":
            while not eof:
                refill()
            try:
                value = json.loads(buffer[position:])
            except json.JSONDecodeError as exc:
                raise DatasetFormatError(f"{source}: invalid JSON object: {exc}") from exc
            if not isinstance(value, dict):
                raise DatasetFormatError(f"{source}: top-level JSON object expected")
            yield value
            return

        if buffer[position] != "[":
            raise DatasetFormatError(
                f"{source}: JSON input must contain an object or top-level array"
            )
        position += 1
        item_index = 0

        while True:
            while True:
                while position < len(buffer) and buffer[position].isspace():
                    position += 1
                if position < len(buffer):
                    break
                if eof:
                    raise DatasetFormatError(f"{source}: unterminated JSON array")
                refill()

            if buffer[position] == "]":
                return
            if buffer[position] == ",":
                position += 1
                continue

            while True:
                try:
                    value, end = decoder.raw_decode(buffer, position)
                    position = end
                    break
                except json.JSONDecodeError as exc:
                    if not eof:
                        refill()
                        continue
                    detail = {
                        "path": str(source),
                        "index": item_index,
                        "error": str(exc),
                    }
                    if errors is not None:
                        errors.append(detail)
                    if not skip_invalid:
                        raise DatasetFormatError(
                            f"{source}: invalid JSON array item {item_index}: {exc}"
                        ) from exc
                    next_comma = buffer.find(",", position)
                    next_end = buffer.find("]", position)
                    candidates = [x for x in (next_comma, next_end) if x >= 0]
                    if not candidates:
                        return
                    position = min(candidates)
                    value = None
                    break

            if value is not None:
                if isinstance(value, dict):
                    yield value
                else:
                    detail = {
                        "path": str(source),
                        "index": item_index,
                        "error": "record is not a JSON object",
                    }
                    if errors is not None:
                        errors.append(detail)
                    if not skip_invalid:
                        raise DatasetFormatError(
                            f"{source}: JSON array item {item_index} is not an object"
                        )
            item_index += 1


class BaseAdapter:
    dataset_name = "generic"

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        raise NotImplementedError


class CMMMathAdapter(BaseAdapter):
    dataset_name = "cmm_math"

    def __init__(self, input_path: str | Path | None = None) -> None:
        self.split_lookup: dict[str, str] = {}
        if input_path:
            self.split_lookup = self._load_split_lookup(Path(input_path))

    @staticmethod
    def _load_split_lookup(input_path: Path) -> dict[str, str]:
        if input_path.name != "all_data.jsonl":
            return {}
        lookup: dict[str, str] = {}
        for split, filename in (("train", "train_data.jsonl"), ("test", "test_data.jsonl")):
            sibling = input_path.with_name(filename)
            if not sibling.exists():
                continue
            for raw in iter_json_records(sibling):
                record_id = str(raw.get("id", ""))
                if not record_id:
                    continue
                previous = lookup.get(record_id)
                if previous and previous != split:
                    raise DatasetFormatError(
                        f"CMM-Math id {record_id!r} occurs in both train and test"
                    )
                lookup[record_id] = split
        return lookup

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        record_id = str(raw.get("id", row_index))
        problem = "\n".join(
            part for part in (_stringify(raw.get("question")), _stringify(raw.get("options"))) if part
        )
        auxiliary = "\n".join(
            part
            for part in (
                _stringify(raw.get("analysis")),
                _stringify(raw.get("solution")),
                _stringify(raw.get("answer")),
            )
            if part
        )
        yield NormalizedRecord(
            dataset=self.dataset_name,
            config=None,
            split=split or self.split_lookup.get(record_id),
            record_id=record_id,
            group_id=record_id,
            row_index=row_index,
            problem_text=problem,
            auxiliary_text=auxiliary,
            image_refs=_flatten_image_refs(raw.get("image")),
            raw_record=raw,
        )


class UGMathBenchAdapter(BaseAdapter):
    dataset_name = "ugmathbench"

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        parent_id = str(raw.get("id", row_index))
        metadata = "\n".join(
            _stringify(raw.get(key))
            for key in ("subject", "topic", "subtopic", "keywords")
            if raw.get(key)
        )
        for version in (1, 2, 3):
            problem = _stringify(raw.get(f"problem_v{version}"))
            if not problem:
                continue
            options = _stringify(raw.get(f"options_v{version}"))
            auxiliary = "\n".join(
                value
                for value in (
                    metadata,
                    _stringify(raw.get(f"answer_v{version}")),
                    _stringify(raw.get(f"answer_type_v{version}")),
                )
                if value
            )
            yield NormalizedRecord(
                dataset=self.dataset_name,
                config=_stringify(raw.get("subject")) or None,
                split=split or "test",
                record_id=f"{parent_id}:v{version}",
                group_id=parent_id,
                row_index=row_index,
                problem_text="\n".join(x for x in (problem, options) if x),
                auxiliary_text=auxiliary,
                image_refs=[],
                raw_record=raw,
            )


class MathVistaAdapter(BaseAdapter):
    dataset_name = "mathvista"

    def __init__(self, config: str = "default") -> None:
        self.config = config

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        record_id = str(raw.get("pid", row_index))
        problem = "\n".join(
            x
            for x in (
                _stringify(raw.get("question")),
                _stringify(raw.get("choices")),
                _stringify(raw.get("query")),
            )
            if x
        )
        auxiliary = "\n".join(
            x
            for x in (
                _stringify(raw.get("answer")),
                _stringify(raw.get("metadata")),
            )
            if x
        )
        images = _flatten_image_refs(raw.get("decoded_image"))
        images.extend(_flatten_image_refs(raw.get("image")))
        yield NormalizedRecord(
            dataset=self.dataset_name,
            config=self.config,
            split=split,
            record_id=record_id,
            group_id=record_id,
            row_index=row_index,
            problem_text=problem,
            auxiliary_text=auxiliary,
            image_refs=list(dict.fromkeys(images)),
            raw_record=raw,
        )


class MathVerseAdapter(BaseAdapter):
    dataset_name = "mathverse"

    def __init__(self, config: str = "testmini") -> None:
        self.config = config

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        problem_index = str(raw.get("problem_index", row_index))
        sample_index = str(raw.get("sample_index", row_index))
        version = _stringify(raw.get("problem_version")) or "unknown"
        record_id = f"{problem_index}:{sample_index}:{version}"
        problem = "\n".join(
            x
            for x in (
                _stringify(raw.get("question")),
                _stringify(raw.get("question_for_eval")),
                _stringify(raw.get("query_wo")),
            )
            if x
        )
        auxiliary = "\n".join(
            x
            for x in (
                _stringify(raw.get("answer")),
                _stringify(raw.get("metadata")),
                version,
            )
            if x
        )
        yield NormalizedRecord(
            dataset=self.dataset_name,
            config=self.config,
            split=split,
            record_id=record_id,
            group_id=problem_index,
            row_index=row_index,
            problem_text=problem,
            auxiliary_text=auxiliary,
            image_refs=_flatten_image_refs(raw.get("image")),
            raw_record=raw,
        )


class GenericAdapter(BaseAdapter):
    dataset_name = "generic"

    def __init__(
        self,
        *,
        dataset_name: str = "generic",
        id_field: str = "id",
        text_fields: Sequence[str] = ("question", "options"),
        auxiliary_fields: Sequence[str] = ("analysis", "solution", "answer"),
        image_fields: Sequence[str] = ("image", "images"),
        group_field: str | None = None,
    ) -> None:
        self.dataset_name = dataset_name
        self.id_field = id_field
        self.text_fields = tuple(text_fields)
        self.auxiliary_fields = tuple(auxiliary_fields)
        self.image_fields = tuple(image_fields)
        self.group_field = group_field

    def normalize(
        self, raw: dict[str, Any], row_index: int, split: str | None = None
    ) -> Iterable[NormalizedRecord]:
        record_id = str(raw.get(self.id_field, row_index))
        group_id = str(raw.get(self.group_field, record_id)) if self.group_field else record_id
        images: list[str] = []
        for field in self.image_fields:
            images.extend(_flatten_image_refs(raw.get(field)))
        yield NormalizedRecord(
            dataset=self.dataset_name,
            config=None,
            split=split,
            record_id=record_id,
            group_id=group_id,
            row_index=row_index,
            problem_text="\n".join(
                _stringify(raw.get(field)) for field in self.text_fields if raw.get(field)
            ),
            auxiliary_text="\n".join(
                _stringify(raw.get(field))
                for field in self.auxiliary_fields
                if raw.get(field)
            ),
            image_refs=list(dict.fromkeys(images)),
            raw_record=raw,
        )


def make_adapter(
    dataset: str,
    *,
    input_path: str | Path | None = None,
    config: str | None = None,
    id_field: str = "id",
    text_fields: Sequence[str] = ("question", "options"),
    auxiliary_fields: Sequence[str] = ("analysis", "solution", "answer"),
    image_fields: Sequence[str] = ("image", "images"),
    group_field: str | None = None,
) -> BaseAdapter:
    normalized = dataset.lower().replace("-", "_")
    if normalized in {"cmm", "cmm_math"}:
        return CMMMathAdapter(input_path)
    if normalized in {"ugmath", "ugmathbench"}:
        return UGMathBenchAdapter()
    if normalized == "mathvista":
        return MathVistaAdapter(config or "default")
    if normalized == "mathverse":
        return MathVerseAdapter(config or "testmini")
    return GenericAdapter(
        dataset_name=dataset,
        id_field=id_field,
        text_fields=text_fields,
        auxiliary_fields=auxiliary_fields,
        image_fields=image_fields,
        group_field=group_field,
    )


def iter_local_normalized(
    path: str | Path,
    adapter: BaseAdapter,
    *,
    split: str | None = None,
    skip_invalid: bool = False,
    errors: list[dict[str, Any]] | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> Iterator[NormalizedRecord]:
    emitted = 0
    for row_index, raw in enumerate(
        iter_json_records(path, skip_invalid=skip_invalid, errors=errors)
    ):
        if row_index < offset:
            continue
        for normalized in adapter.normalize(raw, row_index, split):
            if limit is not None and emitted >= limit:
                return
            yield normalized
            emitted += 1


def iter_hf_rows(
    repo: str,
    config: str,
    split: str,
    *,
    adapter: BaseAdapter,
    offset: int = 0,
    limit: int | None = None,
    page_size: int = 100,
    hf_token: str | None = None,
    timeout: int = 60,
) -> Iterator[NormalizedRecord]:
    """Page Dataset Viewer rows without downloading image binary payloads."""

    if page_size < 1 or page_size > 100:
        raise ValueError("Dataset Viewer page_size must be between 1 and 100")
    next_offset = offset
    emitted = 0
    total: int | None = None
    base = "https://datasets-server.huggingface.co/rows"

    while total is None or next_offset < total:
        remaining = page_size if limit is None else min(page_size, limit - emitted)
        if remaining <= 0:
            return
        query = urllib.parse.urlencode(
            {
                "dataset": repo,
                "config": config,
                "split": split,
                "offset": next_offset,
                "length": remaining,
            }
        )
        request = urllib.request.Request(f"{base}?{query}")
        if hf_token:
            request.add_header("Authorization", f"Bearer {hf_token}")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Hugging Face Dataset Viewer request failed at offset {next_offset}: {exc}"
            ) from exc
        if payload.get("error"):
            raise RuntimeError(f"Hugging Face Dataset Viewer error: {payload['error']}")
        total = int(payload.get("num_rows_total", 0))
        rows = payload.get("rows", [])
        if not rows:
            return
        for item in rows:
            raw = item.get("row")
            if not isinstance(raw, dict):
                continue
            row_index = int(item.get("row_idx", next_offset))
            for normalized in adapter.normalize(raw, row_index, split):
                if limit is not None and emitted >= limit:
                    return
                yield normalized
                emitted += 1
        next_offset += len(rows)


def parse_csv_fields(value: str) -> tuple[str, ...]:
    return tuple(field.strip() for field in value.split(",") if field.strip())

