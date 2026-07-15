"""Render the Phase-0 normalized ODE time-course as a two-panel PNG figure.

The source CSV is deliberately self-describing.  This renderer preserves its
``scenario_prior`` boundary in the figure so the output cannot be mistaken for
a calibrated dose-response or detection-limit result.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT / "experiments/ode-model/results/minimal_normalized_timecourse.csv"
DEFAULT_OUTPUT = ROOT / "experiments/ode-model/results/minimal_normalized_timecourse.png"

PATHWAY_SERIES = (
    ("receptor_active", "Receptor active", "#4c78a8", "--"),
    ("g_on", "G protein on", "#f58518", "-"),
    ("mapk_active", "Lumped MAPK active", "#54a24b", "-"),
    ("stf_activity", "sTF activity", "#e45756", "-"),
    ("gal_product_rate", "GAL product rate", "#b279a2", "-"),
)
REQUIRED_COLUMNS = {
    "scenario_id",
    "evidence_status",
    "time_hours",
    "color_signal_arbitrary_units",
    *(field for field, _, _, _ in PATHWAY_SERIES),
}


def parse_args() -> argparse.Namespace:
    """Parse source and destination paths for a static figure."""

    parser = argparse.ArgumentParser(
        description="Plot a self-describing normalized ODE time-course CSV."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Time-course CSV input path.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="PNG figure output path.")
    return parser.parse_args()


def load_timecourse(path: Path) -> list[dict[str, str]]:
    """Read and minimally validate a self-describing ODE time-course CSV."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS.difference(fieldnames)
        if missing:
            raise ValueError(f"time-course CSV is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    if len(rows) < 2:
        raise ValueError("time-course CSV must contain at least two rows")

    for column in REQUIRED_COLUMNS - {"scenario_id", "evidence_status"}:
        try:
            [float(row[column]) for row in rows]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"time-course CSV has a non-numeric {column!r} value") from error
    return rows


def _values(rows: Iterable[dict[str, str]], field: str) -> list[float]:
    return [float(row[field]) for row in rows]


def plot_timecourse(rows: list[dict[str, str]], output_path: Path) -> None:
    """Plot pathway interfaces separately from color signal's arbitrary units."""

    time_hours = _values(rows, "time_hours")
    scenario_id = rows[0]["scenario_id"]
    evidence_status = rows[0]["evidence_status"]

    figure, (pathway_axis, color_axis) = plt.subplots(
        2,
        1,
        figsize=(10, 7),
        sharex=True,
        gridspec_kw={"height_ratios": (3, 2)},
    )

    for field, label, color, line_style in PATHWAY_SERIES:
        pathway_axis.plot(
            time_hours,
            _values(rows, field),
            label=label,
            color=color,
            linestyle=line_style,
            linewidth=2,
        )
    pathway_axis.set_ylabel("Normalized activity /\neffective product rate")
    pathway_axis.set_ylim(-0.02, 1.02)
    pathway_axis.grid(axis="y", alpha=0.25)
    pathway_axis.legend(loc="lower right", frameon=False, ncols=2)

    color_axis.plot(
        time_hours,
        _values(rows, "color_signal_arbitrary_units"),
        label="Color signal",
        color="#72b7b2",
        linewidth=2.5,
    )
    color_axis.set_xlabel("Time (hours)")
    color_axis.set_ylabel("Color signal\n(arbitrary units)")
    color_axis.set_ylim(bottom=0)
    color_axis.grid(axis="y", alpha=0.25)
    color_axis.legend(loc="upper left", frameon=False)

    figure.suptitle(f"P0 normalized ODE time-course: {scenario_id}", fontsize=13)
    figure.text(
        0.5,
        0.01,
        f"Evidence status: {evidence_status}. Illustrative single-input scenario; not a calibrated prediction.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.04, 1, 0.95))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main() -> None:
    args = parse_args()
    rows = load_timecourse(args.input)
    plot_timecourse(rows, args.out)
    print(f"Wrote time-course figure to {args.out}")


if __name__ == "__main__":
    main()
