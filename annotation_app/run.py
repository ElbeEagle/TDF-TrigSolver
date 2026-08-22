"""Safe launcher for the local Streamlit annotation page."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from annotation_app.core import TemplateBoundaryError, validate_annotator_id  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch one isolated Trig Gold annotation session")
    parser.add_argument("--annotator", required=True, help="Stable annotator id, for example annotator_a")
    parser.add_argument(
        "--template",
        type=Path,
        default=ROOT / "data" / "benchmarks" / "trig_pilot_v1" / "test_annotation_template.jsonl",
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=ROOT / "annotation_app" / "seeds" / "test_seed_v1.json",
        help="Machine-prepared Silver seed; pass an empty value only by editing the launcher configuration",
    )
    parser.add_argument("--workspace", type=Path, default=ROOT / "annotation_runs")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    try:
        annotator = validate_annotator_id(args.annotator)
    except TemplateBoundaryError as exc:
        parser.error(str(exc))
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")

    app_path = Path(__file__).with_name("app.py")
    environment = os.environ.copy()
    environment["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address=127.0.0.1",
        f"--server.port={args.port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--",
        "--annotator",
        annotator,
        "--template",
        str(args.template.resolve()),
        "--workspace",
        str(args.workspace.resolve()),
        "--seed",
        str(args.seed.resolve()),
    ]
    try:
        return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
