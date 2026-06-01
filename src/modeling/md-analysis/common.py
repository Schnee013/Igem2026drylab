"""Common helpers for chimeric GPCR-Galpha MD analysis.

The default configuration is chctrl for backward compatibility. Ch-1/Ch-2/Ch-4
must pass a system id so receptor/Galpha chain roles and residue selections come
from ``experiments/md-simulation/analysis/chimeric_systems.json``.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "experiments/md-simulation/analysis/chimeric_systems.json"

@dataclass(frozen=True)
class Replicate:
    rep: str
    topology: Path
    trajectory: Path


@dataclass(frozen=True)
class AnalysisContext:
    system: str
    label: str
    config: dict
    base: Path

    @property
    def receptor_name(self) -> str:
        return self.config["receptor"]["name"]

    @property
    def galpha_name(self) -> str:
        return self.config["galpha"]["name"]

    @property
    def receptor_selection(self) -> str:
        return self.config["receptor"]["selection"]

    @property
    def galpha_selection(self) -> str:
        return self.config["galpha"]["selection"]

    @property
    def protein_selection(self) -> str:
        return f"({self.galpha_selection}) or ({self.receptor_selection})"

    @property
    def backbone_selection(self) -> str:
        return f"({self.protein_selection}) and backbone"

    @property
    def ca_selection(self) -> str:
        return f"({self.protein_selection}) and name CA"

    @property
    def alpha5_selection(self) -> str:
        return self.config["galpha"]["alpha5_selection"]

    @property
    def galpha_ect_selection(self) -> str:
        return self.config["galpha"]["ect_selection"]

    @property
    def galpha_core_backbone_selection(self) -> str:
        return self.config["galpha"]["core_backbone_selection"]

    @property
    def receptor_interface_selection(self) -> str:
        return self.config["receptor"]["interface_selection"]

    @property
    def receptor_interface_clusters(self) -> dict[str, str]:
        clusters = self.config["receptor"].get("interface_clusters") or {}
        return clusters or {"receptor_interface": self.receptor_interface_selection}

    @property
    def junction_rmsf_regions(self) -> dict[str, str]:
        return self.config.get("junction_rmsf_regions") or {}

    @property
    def plot_segids(self) -> list[str]:
        return list(self.config.get("plot_segids") or ["PROA", "PROB"])

    @property
    def analysis_base(self) -> Path:
        return self.base / "analysis"

    def replicates(self) -> list[Replicate]:
        out = []
        for i in (1, 2, 3):
            d = self.base / "processed" / f"rep{i}"
            out.append(Replicate(f"rep{i}", d / "protein_ref.pdb", d / "prod_protein.xtc"))
        return out


def load_config(path: Path | None = None) -> dict:
    path = path or Path(os.environ.get("CHIMERIC_MD_CONFIG", CONFIG_PATH))
    return json.loads(path.read_text(encoding="utf-8"))


def available_systems() -> list[str]:
    return sorted(load_config()["systems"])


def system_config(system: str | None = None) -> tuple[str, dict]:
    root = load_config()
    system = system or os.environ.get("CHIMERIC_MD_SYSTEM") or root["default"]
    try:
        return system, root["systems"][system]
    except KeyError as exc:
        choices = ", ".join(sorted(root["systems"]))
        raise KeyError(f"unknown chimeric MD system '{system}'. Available: {choices}") from exc


def analysis_context(system: str | None = None, base: Path | None = None) -> AnalysisContext:
    system, cfg = system_config(system)
    return AnalysisContext(
        system=system,
        label=cfg.get("label", system),
        config=cfg,
        base=base or Path(cfg["result_dir"]),
    )


def default_base(system: str | None = None) -> Path:
    return analysis_context(system).base


def analysis_base(system: str | None = None) -> Path:
    return analysis_context(system).analysis_base


def replicates(base: Path | None = None, system: str | None = None) -> list[Replicate]:
    ctx = analysis_context(system, base=base)
    return ctx.replicates()


def add_system_argument(parser) -> None:
    parser.add_argument(
        "--system",
        default=None,
        choices=available_systems(),
        help="Chimeric MD system id; defaults to CHIMERIC_MD_SYSTEM or chctrl.",
    )


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def time_ns(ts) -> float:
    # GROMACS XTC stores time in ps; use frame index fallback if absent.
    try:
        return float(ts.time) / 1000.0
    except Exception:
        return float(ts.frame)


def linear_slope(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    return float(np.polyfit(x[mask], y[mask], 1)[0])


def write_judgement(path: Path, title: str, lines: list[str]) -> None:
    path.write_text("# " + title + "\n\n" + "\n".join(f"- {x}" for x in lines) + "\n", encoding="utf-8")


def save_csv(path: Path, rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


_CHCTRL_CONTEXT = analysis_context("chimeric-ste2-gpa1-wt")
GPA1 = _CHCTRL_CONTEXT.galpha_selection
STE2 = _CHCTRL_CONTEXT.receptor_selection
PROTEIN = _CHCTRL_CONTEXT.protein_selection
BACKBONE = _CHCTRL_CONTEXT.backbone_selection
CA = _CHCTRL_CONTEXT.ca_selection
ALPHA5 = _CHCTRL_CONTEXT.alpha5_selection
GPA1_LAST5 = _CHCTRL_CONTEXT.galpha_ect_selection
STE2_INTERFACE = _CHCTRL_CONTEXT.receptor_interface_selection
STE2_CLUSTER_A = _CHCTRL_CONTEXT.receptor_interface_clusters["ste2_cluster_A_222_251"]
STE2_CLUSTER_B = _CHCTRL_CONTEXT.receptor_interface_clusters["ste2_cluster_B_288_304"]
