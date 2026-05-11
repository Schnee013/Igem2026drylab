"""Common helpers for chimeric GPCR-Galpha MD analysis.

Selections assume CHARMM-GUI segment IDs for chctrl:
- PROA = Gpa1-WT, residues 1-472
- PROB = Ste2, residues 1-431
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

GPA1 = "segid PROA"
STE2 = "segid PROB"
PROTEIN = f"({GPA1}) or ({STE2})"
BACKBONE = f"({PROTEIN}) and backbone"
CA = f"({PROTEIN}) and name CA"
ALPHA5 = f"({GPA1}) and resid 448:472 and backbone"
GPA1_LAST5 = f"({GPA1}) and resid 468:472"
# Ste2 interface clusters are project structural selections derived from PDB 7AD3
# Ste2 residues within ~8 A of Gpa1 alpha5/eCT, then confirmed in chctrl
# step5_input.pdb. See analysis/cutoff_source_audit.md before treating them as
# literature-quoted residue ranges.
STE2_INTERFACE = f"({STE2}) and (resid 69:84 or resid 145:160 or resid 222:251 or resid 288:304)"
STE2_CLUSTER_A = f"({STE2}) and (resid 222:251)"  # receptor intracellular interface cluster A
STE2_CLUSTER_B = f"({STE2}) and (resid 288:304)"  # receptor intracellular interface cluster B

@dataclass(frozen=True)
class Replicate:
    rep: str
    topology: Path
    trajectory: Path


def default_base() -> Path:
    return Path("experiments/md-simulation/results/chimeric-ste2-gpa1-wt")


def analysis_base() -> Path:
    return default_base() / "analysis"


def replicates(base: Path | None = None) -> list[Replicate]:
    base = base or default_base()
    out = []
    for i in (1, 2, 3):
        d = base / "processed" / f"rep{i}"
        out.append(Replicate(f"rep{i}", d / "protein_ref.pdb", d / "prod_protein.xtc"))
    return out


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
