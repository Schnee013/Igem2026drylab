"""Run the Phase-0 normalized ODE scenario and write a time-course CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.ode.minimal_solver import solve_normalized_scenario
else:
    from .minimal_solver import solve_normalized_scenario


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "experiments/ode-model/configs/minimal_normalized_scenario.json"
DEFAULT_OUTPUT = ROOT / "experiments/ode-model/results/minimal_normalized_timecourse.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the normalized, scenario-prior P0 ODE minimum solver."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Scenario JSON configuration.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="Time-course CSV output path.")
    return parser.parse_args()


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    if not rows:
        raise ValueError("time-course export cannot be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    result = solve_normalized_scenario(config)
    rows = result.as_rows(config["scenario_id"], config["evidence_status"])
    write_csv(args.out, rows)
    print(f"Wrote {len(rows)} normalized scenario rows to {args.out}")


if __name__ == "__main__":
    main()
