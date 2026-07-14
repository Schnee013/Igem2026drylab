"""Common helpers for config-driven GPCR-complex MD analysis.

The default configuration is chctrl for backward compatibility. Other systems
must pass a system id/config so molecular roles, selections, and optional
interpretation heuristics stay system-scoped.
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
    payload_base: Path

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
    def selection_rmsd_selection(self) -> str:
        selection = self.config.get("selection_rmsd_selection")
        if selection:
            return selection
        return self.alpha5_selection

    @property
    def selection_rmsd_mean_heuristic(self) -> dict | None:
        return self.config.get("selection_rmsd_mean_heuristic")

    @property
    def bsa_mean_fraction_heuristic(self) -> dict | None:
        return self.config.get("bsa_mean_fraction_heuristic")

    @property
    def contact_mean_fraction_heuristic(self) -> dict | None:
        return self.config.get("contact_mean_fraction_heuristic")

    @property
    def hbond_occupancy_reporting_heuristic(self) -> dict | None:
        return self.config.get("hbond_occupancy_reporting_heuristic")

    @property
    def interaction_partner_role(self) -> str:
        """Return the scientific role of the legacy ``galpha`` config slot."""
        return self.config.get("interaction_partner_role", "galpha")

    @property
    def com_target_label(self) -> str:
        return self.config.get("com_target_label") or f"{self.galpha_name} eCT"

    @property
    def com_distance_context_note(self) -> str | None:
        return self.config.get("com_distance_context_note")

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
        for i in configured_replicate_numbers():
            d = self.payload_base / "processed" / f"rep{i}"
            out.append(Replicate(f"rep{i}", d / "protein_ref.pdb", d / "prod_protein.xtc"))
        return out


def configured_replicate_numbers() -> list[int]:
    raw = os.environ.get("CHIMERIC_MD_REPS")
    if not raw:
        return [1, 2, 3]
    reps: list[int] = []
    for item in raw.replace(",", " ").split():
        token = item.strip().lower()
        if token.startswith("rep"):
            token = token[3:]
        try:
            rep = int(token)
        except ValueError as exc:
            raise ValueError(f"invalid CHIMERIC_MD_REPS token: {item!r}") from exc
        if rep <= 0:
            raise ValueError(f"CHIMERIC_MD_REPS entries must be positive: {item!r}")
        reps.append(rep)
    if not reps:
        raise ValueError("CHIMERIC_MD_REPS is set but no replicate numbers were parsed")
    duplicates = sorted({rep for rep in reps if reps.count(rep) > 1})
    if duplicates:
        raise ValueError(
            "CHIMERIC_MD_REPS contains duplicate replicate numbers: "
            + ", ".join(map(str, duplicates))
        )
    return reps


def replicate_output_tag() -> str:
    """Return a filename tag that does not imply three reps for a single-rep run."""
    reps = configured_replicate_numbers()
    if len(reps) == 1:
        return f"rep{reps[0]}"
    return f"{len(reps)}rep"


def replicate_plot_path(directory: Path, stem: str) -> Path:
    return directory / f"{stem}_{replicate_output_tag()}.png"


def load_config(path: Path | None = None) -> dict:
    path = path or Path(os.environ.get("CHIMERIC_MD_CONFIG", CONFIG_PATH))
    return json.loads(path.read_text(encoding="utf-8"))


def available_systems() -> list[str]:
    return sorted(load_config()["systems"])


def system_config(
    system: str | None = None,
    config_path: Path | None = None,
) -> tuple[str, dict]:
    root = load_config(config_path)
    system = system or os.environ.get("CHIMERIC_MD_SYSTEM") or root["default"]
    try:
        return system, root["systems"][system]
    except KeyError as exc:
        choices = ", ".join(sorted(root["systems"]))
        raise KeyError(f"unknown MD analysis system '{system}'. Available: {choices}") from exc


def analysis_context(
    system: str | None = None,
    base: Path | None = None,
    payload_base: Path | None = None,
    config_path: Path | None = None,
) -> AnalysisContext:
    system, cfg = system_config(system, config_path=config_path)
    result_base = base or Path(cfg["result_dir"])
    if payload_base is None:
        direct_payload_root = os.environ.get("CHIMERIC_MD_PAYLOAD_ROOT")
        shared_payload_root = os.environ.get("DRYLAB_PAYLOAD_ROOT")
        if direct_payload_root:
            payload_base = Path(direct_payload_root)
        elif shared_payload_root:
            configured_result_dir = Path(cfg["result_dir"])
            if configured_result_dir.is_absolute():
                try:
                    configured_result_dir = configured_result_dir.relative_to(REPO_ROOT)
                except ValueError as exc:
                    raise ValueError(
                        "DRYLAB_PAYLOAD_ROOT requires result_dir to be repo-relative "
                        "or located under the repository root"
                    ) from exc
            payload_base = Path(shared_payload_root) / configured_result_dir
        else:
            payload_base = result_base
    return AnalysisContext(
        system=system,
        label=cfg.get("label", system),
        config=cfg,
        base=result_base,
        payload_base=payload_base,
    )


def default_base(system: str | None = None) -> Path:
    return analysis_context(system).base


def analysis_base(system: str | None = None) -> Path:
    return analysis_context(system).analysis_base


def replicates(base: Path | None = None, system: str | None = None) -> list[Replicate]:
    ctx = analysis_context(system, base=base, payload_base=base if base is not None else None)
    return ctx.replicates()


def add_system_argument(parser) -> None:
    parser.add_argument(
        "--system",
        default=None,
        choices=available_systems(),
        help="Configured MD system id; defaults to CHIMERIC_MD_SYSTEM or chctrl.",
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
