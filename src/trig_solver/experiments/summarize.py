"""Print the latest saved experiment summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", action="store_true", help="summarize the newest run")
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    if args.run_dir:
        run_dir = args.run_dir
    else:
        candidates = sorted((root / "results" / "trig_pilot").glob("*"))
        if not candidates:
            raise SystemExit("no experiment runs found")
        run_dir = candidates[-1]
    print(json.dumps(json.loads((run_dir / "summary.json").read_text(encoding="utf-8")), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

