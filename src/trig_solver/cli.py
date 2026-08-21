"""Command-line access to the Raw and Oracle solver entry points."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import RawProblem, SolverConfig, TrigURM
from .pipeline import solve_oracle, solve_raw


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solve a whitelisted Chinese trigonometric-function problem")
    parser.add_argument("--mode", choices=("raw", "oracle"), required=True)
    parser.add_argument("--input", type=Path, help="JSON file containing RawProblem or {urm, options}")
    parser.add_argument("--question", help="Raw-mode question text")
    parser.add_argument("--options", help="Raw-mode option string")
    parser.add_argument("--model", default="qwen3.7-flash-2026-07-15")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
    config = SolverConfig(model_name=args.model)
    if args.mode == "raw":
        problem = RawProblem.model_validate(payload) if payload else RawProblem(question=args.question or "", options=args.options)
        result = solve_raw(problem, config)
    else:
        if payload is None or "urm" not in payload:
            raise SystemExit("oracle mode requires --input with an 'urm' object")
        result = solve_oracle(TrigURM.model_validate(payload["urm"]), payload.get("options"), config)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "solved" else 2


if __name__ == "__main__":
    raise SystemExit(main())

