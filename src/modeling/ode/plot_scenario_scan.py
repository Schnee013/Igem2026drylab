"""Render compact, bounded summary plots for the Phase-1 ODE scan suite."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT / "experiments/ode-model/results/stage1_scenario_scan/final_metrics.csv"
DEFAULT_OUTPUT = ROOT / "experiments/ode-model/results/stage1_scenario_scan/stage1_scenario_summary.png"
REQUIRED_COLUMNS = {
    "scan_id",
    "scenario_role",
    "evidence_status",
    "parameter__input__ligand_normalized",
    "parameter__receptor__half_activation_normalized",
    "parameter__g_protein__coupling_rate_per_hour",
    "parameter__gal_output__leak_rate",
    "parameter__gal_output__copy_number",
    "parameter__gal_output__gain_rate",
    "parameter__time__duration_hours",
    "final_color_signal_arbitrary_units",
    "final_color_ratio_vs_no_ligand",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot compact Phase-1 scenario-prior ODE scan summaries."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="final_metrics.csv input.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="PNG output path.")
    return parser.parse_args()


def load_metrics(path: Path) -> list[dict[str, str]]:
    """Read self-describing summary metrics and retain their evidence boundary."""

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"metrics CSV is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError("metrics CSV cannot be empty")
    if {row["evidence_status"] for row in rows} != {"scenario_prior"}:
        raise ValueError("Stage-1 plots require exclusively scenario_prior metrics")
    return rows


def _number(row: dict[str, str], field: str) -> float:
    return float(row[field])


def _input_rows(rows: list[dict[str, str]], scan_id: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["scan_id"] == scan_id and row["scenario_role"] == "ligand_input"
    ]


def plot_metrics(rows: list[dict[str, str]], output_path: Path) -> None:
    """Plot the three pre-registered scan families without calibration claims."""

    figure, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    dose_rows = _input_rows(rows, "dose_by_half_activation")
    dose_groups = sorted(
        {_number(row, "parameter__receptor__half_activation_normalized") for row in dose_rows}
    )
    for half_activation in dose_groups:
        subset = sorted(
            (
                row
                for row in dose_rows
                if _number(row, "parameter__receptor__half_activation_normalized") == half_activation
                and _number(row, "parameter__input__ligand_normalized") > 0
            ),
            key=lambda row: _number(row, "parameter__input__ligand_normalized"),
        )
        axes[0].plot(
            [_number(row, "parameter__input__ligand_normalized") for row in subset],
            [_number(row, "final_color_signal_arbitrary_units") for row in subset],
            marker="o",
            linewidth=1.8,
            label=f"half activation={half_activation:g}",
        )
    axes[0].set_xscale("log")
    axes[0].set_title("Dose × half-activation")
    axes[0].set_xlabel("Normalized ligand input")
    axes[0].set_ylabel("Final color signal (arbitrary units)")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=7, frameon=False)

    coupling_rows = _input_rows(rows, "coupling_by_output_leak")
    coupling_groups = sorted(
        {_number(row, "parameter__g_protein__coupling_rate_per_hour") for row in coupling_rows}
    )
    for coupling in coupling_groups:
        subset = sorted(
            (
                row
                for row in coupling_rows
                if _number(row, "parameter__g_protein__coupling_rate_per_hour") == coupling
            ),
            key=lambda row: _number(row, "parameter__gal_output__leak_rate"),
        )
        axes[1].plot(
            [_number(row, "parameter__gal_output__leak_rate") for row in subset],
            [_number(row, "final_color_ratio_vs_no_ligand") for row in subset],
            marker="o",
            linewidth=1.8,
            label=f"coupling={coupling:g} h$^{{-1}}$",
        )
    axes[1].set_title("Coupling × output leak")
    axes[1].set_xlabel("Output leak rate (arbitrary rate)")
    axes[1].set_ylabel("Final signal / no-ligand control")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=7, frameon=False)

    copy_rows = _input_rows(rows, "copy_gain_by_time_window")
    copy_groups = sorted(
        {
            (
                _number(row, "parameter__gal_output__copy_number"),
                _number(row, "parameter__gal_output__gain_rate"),
            )
            for row in copy_rows
        }
    )
    for copy_number, gain_rate in copy_groups:
        subset = sorted(
            (
                row
                for row in copy_rows
                if _number(row, "parameter__gal_output__copy_number") == copy_number
                and _number(row, "parameter__gal_output__gain_rate") == gain_rate
            ),
            key=lambda row: _number(row, "parameter__time__duration_hours"),
        )
        axes[2].plot(
            [_number(row, "parameter__time__duration_hours") for row in subset],
            [_number(row, "final_color_signal_arbitrary_units") for row in subset],
            marker="o",
            linewidth=1.5,
            label=f"N={copy_number:g}, gain={gain_rate:g}",
        )
    axes[2].set_title("Copy × gain × time window")
    axes[2].set_xlabel("Observation window (hours)")
    axes[2].set_ylabel("Final color signal (arbitrary units)")
    axes[2].grid(alpha=0.25)
    axes[2].legend(fontsize=6.5, frameon=False, ncols=2)

    figure.suptitle("P0 ODE Phase-1 normalized engineering scenarios", fontsize=13)
    figure.text(
        0.5,
        0.01,
        "All panels are scenario_prior simulations, not calibrated affinities, detection limits, or final construct recommendations.",
        ha="center",
        fontsize=8.5,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 0.92))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main() -> None:
    args = parse_args()
    plot_metrics(load_metrics(args.input), args.out)
    print(f"Wrote Stage-1 scenario figure to {args.out}")


if __name__ == "__main__":
    main()
