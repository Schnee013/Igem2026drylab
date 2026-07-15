"""A framework-level ODE solver for the yeast GPCR sensor pathway.

This module deliberately implements only the Phase-0 lumped model:

``ligand -> Gpr -> chimeric Gpa1 -> MAPK -> sTF -> GAL -> color``.

All numeric values come from an explicitly labelled scenario configuration.
They are not project calibration values, and docking scores are not accepted as
kinetic inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp


REQUIRED_TOP_LEVEL_FIELDS = {
    "scenario_id",
    "evidence_status",
    "model_scope",
    "time",
    "input",
    "receptor",
    "g_protein",
    "mapk",
    "transcription",
    "gal_output",
    "color",
}


@dataclass(frozen=True)
class SimulationResult:
    """One normalized time-course and its algebraic intermediate outputs."""

    time_hours: np.ndarray
    receptor_active: np.ndarray
    g_on: np.ndarray
    mapk_active: np.ndarray
    stf_activity: np.ndarray
    gal_product_rate: np.ndarray
    color_signal: np.ndarray
    input_ligand_normalized: float

    def as_rows(self, scenario_id: str, evidence_status: str) -> list[dict[str, float | str]]:
        """Return rows suitable for a transparent CSV time-course export."""

        return [
            {
                "scenario_id": scenario_id,
                "evidence_status": evidence_status,
                "time_hours": float(time),
                "input_ligand_normalized": self.input_ligand_normalized,
                "receptor_active": float(receptor),
                "g_on": float(g_on),
                "mapk_active": float(mapk),
                "stf_activity": float(stf),
                "gal_product_rate": float(product_rate),
                "color_signal_arbitrary_units": float(color),
            }
            for time, receptor, g_on, mapk, stf, product_rate, color in zip(
                self.time_hours,
                self.receptor_active,
                self.g_on,
                self.mapk_active,
                self.stf_activity,
                self.gal_product_rate,
                self.color_signal,
                strict=True,
            )
        ]


def hill_response(signal: np.ndarray | float, half_activation: float, hill_coefficient: float) -> np.ndarray | float:
    """Return a bounded Hill response for non-negative normalized inputs."""

    if half_activation <= 0:
        raise ValueError("half_activation must be positive")
    if hill_coefficient <= 0:
        raise ValueError("hill_coefficient must be positive")

    signal_array = np.asarray(signal, dtype=float)
    if np.any(signal_array < 0):
        raise ValueError("Hill-response input must be non-negative")

    numerator = np.power(signal_array, hill_coefficient)
    denominator = np.power(half_activation, hill_coefficient) + numerator
    response = numerator / denominator
    return float(response) if signal_array.ndim == 0 else response


def _require_mapping(config: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = config.get(field)
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _positive(section: Mapping[str, Any], field: str) -> float:
    value = float(section[field])
    if value <= 0:
        raise ValueError(f"{field} must be positive")
    return value


def _non_negative(section: Mapping[str, Any], field: str) -> float:
    value = float(section[field])
    if value < 0:
        raise ValueError(f"{field} must be non-negative")
    return value


def validate_config(config: Mapping[str, Any]) -> None:
    """Validate the deliberately small single-scenario configuration contract."""

    missing = REQUIRED_TOP_LEVEL_FIELDS.difference(config)
    if missing:
        raise ValueError(f"missing required configuration fields: {', '.join(sorted(missing))}")
    if config["evidence_status"] != "scenario_prior":
        raise ValueError("minimal solver accepts only evidence_status='scenario_prior'")

    time = _require_mapping(config, "time")
    _positive(time, "duration_hours")
    points = int(time["output_points"])
    if points < 2:
        raise ValueError("output_points must be at least 2")

    input_section = _require_mapping(config, "input")
    _non_negative(input_section, "ligand_normalized")

    receptor = _require_mapping(config, "receptor")
    basal_receptor = _non_negative(receptor, "basal_activity")
    receptor_efficacy = _non_negative(receptor, "efficacy")
    _positive(receptor, "half_activation_normalized")
    _positive(receptor, "hill_coefficient")
    if basal_receptor + receptor_efficacy > 1:
        raise ValueError("receptor basal_activity + efficacy must not exceed 1")

    g_protein = _require_mapping(config, "g_protein")
    _positive(g_protein, "coupling_rate_per_hour")
    _positive(g_protein, "deactivation_rate_per_hour")

    mapk = _require_mapping(config, "mapk")
    _positive(mapk, "activation_rate_per_hour")
    _positive(mapk, "deactivation_rate_per_hour")

    transcription = _require_mapping(config, "transcription")
    basal_tf = _non_negative(transcription, "basal_activity")
    tf_efficacy = _non_negative(transcription, "efficacy")
    _positive(transcription, "half_activation")
    _positive(transcription, "hill_coefficient")
    if basal_tf + tf_efficacy > 1:
        raise ValueError("transcription basal_activity + efficacy must not exceed 1")

    gal_output = _require_mapping(config, "gal_output")
    _positive(gal_output, "copy_number")
    _non_negative(gal_output, "leak_rate")
    _non_negative(gal_output, "gain_rate")
    _positive(gal_output, "half_activation")

    color = _require_mapping(config, "color")
    _positive(color, "production_rate_per_hour")
    _positive(color, "loss_rate_per_hour")


def receptor_activity(config: Mapping[str, Any]) -> float:
    """Evaluate the static normalized ligand-to-Gpr activation interface."""

    receptor = _require_mapping(config, "receptor")
    ligand = float(_require_mapping(config, "input")["ligand_normalized"])
    return float(
        receptor["basal_activity"]
        + receptor["efficacy"]
        * hill_response(
            ligand,
            float(receptor["half_activation_normalized"]),
            float(receptor["hill_coefficient"]),
        )
    )


def _rhs(_: float, state: np.ndarray, config: Mapping[str, Any], r_active: float) -> np.ndarray:
    """Lumped Gpa1 and MAPK state equations plus color accumulation."""

    g_on, mapk_active, color_signal = state
    g_protein = _require_mapping(config, "g_protein")
    mapk = _require_mapping(config, "mapk")
    transcription = _require_mapping(config, "transcription")
    gal_output = _require_mapping(config, "gal_output")
    color = _require_mapping(config, "color")

    tf_activity = float(
        transcription["basal_activity"]
        + transcription["efficacy"]
        * hill_response(
            mapk_active,
            float(transcription["half_activation"]),
            float(transcription["hill_coefficient"]),
        )
    )
    gal_product_rate = float(
        gal_output["leak_rate"]
        + float(gal_output["copy_number"])
        * float(gal_output["gain_rate"])
        * tf_activity
        / (float(gal_output["half_activation"]) + tf_activity)
    )

    d_g_on = (
        float(g_protein["coupling_rate_per_hour"]) * r_active * (1.0 - g_on)
        - float(g_protein["deactivation_rate_per_hour"]) * g_on
    )
    d_mapk = (
        float(mapk["activation_rate_per_hour"]) * g_on * (1.0 - mapk_active)
        - float(mapk["deactivation_rate_per_hour"]) * mapk_active
    )
    d_color = (
        float(color["production_rate_per_hour"]) * gal_product_rate
        - float(color["loss_rate_per_hour"]) * color_signal
    )
    return np.array([d_g_on, d_mapk, d_color], dtype=float)


def solve_normalized_scenario(config: Mapping[str, Any]) -> SimulationResult:
    """Solve one normalized, scenario-prior time-course.

    The state vector is ``[G_on, M, C]``. Receptor activation, sTF activity,
    and GAL product rate are algebraic interfaces so this Phase-0 model keeps
    the complete pathway visible without inventing uncalibrated extra states.
    """

    validate_config(config)
    time = _require_mapping(config, "time")
    output_points = int(time["output_points"])
    duration_hours = float(time["duration_hours"])
    time_hours = np.linspace(0.0, duration_hours, output_points)
    r_active = receptor_activity(config)

    solution = solve_ivp(
        _rhs,
        (0.0, duration_hours),
        y0=np.zeros(3, dtype=float),
        t_eval=time_hours,
        args=(config, r_active),
        rtol=1e-8,
        atol=1e-10,
    )
    if not solution.success:
        raise RuntimeError(f"ODE solver failed: {solution.message}")

    g_on = solution.y[0]
    mapk_active = solution.y[1]
    transcription = _require_mapping(config, "transcription")
    gal_output = _require_mapping(config, "gal_output")
    stf_activity = np.asarray(
        float(transcription["basal_activity"])
        + float(transcription["efficacy"])
        * hill_response(
            mapk_active,
            float(transcription["half_activation"]),
            float(transcription["hill_coefficient"]),
        ),
        dtype=float,
    )
    gal_product_rate = np.asarray(
        float(gal_output["leak_rate"])
        + float(gal_output["copy_number"])
        * float(gal_output["gain_rate"])
        * stf_activity
        / (float(gal_output["half_activation"]) + stf_activity),
        dtype=float,
    )

    return SimulationResult(
        time_hours=solution.t,
        receptor_active=np.full_like(solution.t, r_active, dtype=float),
        g_on=g_on,
        mapk_active=mapk_active,
        stf_activity=stf_activity,
        gal_product_rate=gal_product_rate,
        color_signal=solution.y[2],
        input_ligand_normalized=float(_require_mapping(config, "input")["ligand_normalized"]),
    )
