"""Run the P2 economic-benefit MVP from a JSON scenario config."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.economic.economic_model import evaluate_config
else:
    from .economic_model import evaluate_config


def clean_value(value):
    if isinstance(value, float):
        return round(value, 6)
    return value


def clean_rows(rows: list[dict]) -> list[dict]:
    return [{key: clean_value(value) for key, value in row.items()} for row in rows]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic P2 economic-benefit MVP scenarios.")
    parser.add_argument(
        "--config",
        default="experiments/economic/configs/public_mvp_framework.json",
        help="Scenario JSON config.",
    )
    parser.add_argument(
        "--out",
        default="experiments/economic/results/public_mvp_framework_results.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("no rows to write")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    out_path = Path(args.out)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    rows = clean_rows(evaluate_config(config))
    write_csv(out_path, rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
