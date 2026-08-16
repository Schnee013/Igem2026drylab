"""A framework-level ODE solver for the yeast GPCR sensor pathway.

This module deliberately implements only the Phase-0 lumped model:

``ligand -> Gpr -> chimeric Gpa1 -> MAPK -> sTF -> GAL -> color``.

All numeric values come from an explicitly labelled scenario configuration.
They are not project calibration values, and docking scores are not accepted as
kinetic inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Integral, Real
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
OPTIONAL_TOP_LEVEL_FIELDS = {"parameter_note"}
SECTION_FIELDS = {
    "time": ({"duration_hours", "output_points"}, set()),
    "input": ({"ligand_normalized"}, {"note"}),
    "receptor": (
        {
            "basal_activity",
            "efficacy",
            "half_activation_normalized",
            "hill_coefficient",
            "evidence_status",
        },
        set(),
    ),
    "g_protein": (
        {"coupling_rate_per_hour", "deactivation_rate_per_hour", "evidence_status"},
        set(),
    ),
    "mapk": (
        {"activation_rate_per_hour", "deactivation_rate_per_hour", "evidence_status"},
        set(),
    ),
    "transcription": (
        {
            "basal_activity",
            "efficacy",
            "half_activation",
            "hill_coefficient",
            "evidence_status",
        },
        set(),
    ),
    "gal_output": (
        {
            "copy_number",
            "leak_rate",
            "gain_rate",
            "half_activation",
            "evidence_status",
        },
        {"note"},
    ),
    "color": (
        {"production_rate_per_hour", "loss_rate_per_hour", "evidence_status"},
        set(),
    ),
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

    if not math.isfinite(half_activation) or half_activation <= 0:
        raise ValueError("half_activation must be positive")
    if not math.isfinite(hill_coefficient) or hill_coefficient <= 0:
        raise ValueError("hill_coefficient must be positive")

    signal_array = np.asarray(signal, dtype=float)
    if not np.all(np.isfinite(signal_array)):
        raise ValueError("Hill-response input must be finite")
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


def _validate_fields(
    mapping: Mapping[str, Any],
    label: str,
    required: set[str],
    optional: set[str],
) -> None:
    missing = required.difference(mapping)
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    unknown = set(mapping).difference(required | optional)
    if unknown:
        raise ValueError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _require_string(mapping: Mapping[str, Any], field: str, label: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{field} must be a non-empty string")
    return value


def _finite_number(section: Mapping[str, Any], field: str) -> float:
    value = section.get(field)
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


def _positive(section: Mapping[str, Any], field: str) -> float:
    value = _finite_number(section, field)
    if value <= 0:
        raise ValueError(f"{field} must be positive")
    return value


def _non_negative(section: Mapping[str, Any], field: str) -> float:
    value = _finite_number(section, field)
    if value < 0:
        raise ValueError(f"{field} must be non-negative")
    return value


def _positive_integer(section: Mapping[str, Any], field: str) -> int:
    value = section.get(field)
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{field} must be an integer")
    integer = int(value)
    if integer <= 0:
        raise ValueError(f"{field} must be positive")
    return integer


def validate_config(config: Mapping[str, Any]) -> None:
    """Validate the deliberately small single-scenario configuration contract."""

    if not isinstance(config, Mapping):
        raise ValueError("configuration must be an object")
    _validate_fields(
        config,
        "configuration",
        REQUIRED_TOP_LEVEL_FIELDS,
        OPTIONAL_TOP_LEVEL_FIELDS,
    )
    _require_string(config, "scenario_id", "configuration")
    _require_string(config, "model_scope", "configuration")
    if "parameter_note" in config:
        _require_string(config, "parameter_note", "configuration")
    if config["evidence_status"] != "scenario_prior":
        raise ValueError("minimal solver accepts only evidence_status='scenario_prior'")

    sections: dict[str, Mapping[str, Any]] = {}
    for section_name, (required, optional) in SECTION_FIELDS.items():
        section = _require_mapping(config, section_name)
        _validate_fields(section, section_name, required, optional)
        sections[section_name] = section
        if "evidence_status" in required:
            _require_string(section, "evidence_status", section_name)
        if "note" in section:
            _require_string(section, "note", section_name)

    time = sections["time"]
    _positive(time, "duration_hours")
    points = _positive_integer(time, "output_points")
    if points < 2:
        raise ValueError("output_points must be at least 2")

    input_section = sections["input"]
    _non_negative(input_section, "ligand_normalized")

    receptor = sections["receptor"]
    basal_receptor = _non_negative(receptor, "basal_activity")
    receptor_efficacy = _non_negative(receptor, "efficacy")
    _positive(receptor, "half_activation_normalized")
    _positive(receptor, "hill_coefficient")
    if basal_receptor + receptor_efficacy > 1:
        raise ValueError("receptor basal_activity + efficacy must not exceed 1")

    g_protein = sections["g_protein"]
    _positive(g_protein, "coupling_rate_per_hour")
    _positive(g_protein, "deactivation_rate_per_hour")

    mapk = sections["mapk"]
    _positive(mapk, "activation_rate_per_hour")
    _positive(mapk, "deactivation_rate_per_hour")

    transcription = sections["transcription"]
    basal_tf = _non_negative(transcription, "basal_activity")
    tf_efficacy = _non_negative(transcription, "efficacy")
    _positive(transcription, "half_activation")
    _positive(transcription, "hill_coefficient")
    if basal_tf + tf_efficacy > 1:
        raise ValueError("transcription basal_activity + efficacy must not exceed 1")

    gal_output = sections["gal_output"]
    _positive_integer(gal_output, "copy_number")
    _non_negative(gal_output, "leak_rate")
    _non_negative(gal_output, "gain_rate")
    _positive(gal_output, "half_activation")

    color = sections["color"]
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

    # Adaptive Runge--Kutta stages can briefly probe a few floating-point ulps
    # outside the invariant [0, 1] state interval near a zero-signal boundary.
    # Use the physical interval for the algebraic Hill interface while leaving
    # the raw state in the ODE terms so the vector field still restores bounds.
    mapk_for_tf = float(np.clip(mapk_active, 0.0, 1.0))

    tf_activity = float(
        transcription["basal_activity"]
        + transcription["efficacy"]
        * hill_response(
            mapk_for_tf,
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
    if not np.all(np.isfinite(solution.y)):
        raise RuntimeError("ODE solver returned non-finite state values")

    g_on = solution.y[0]
    mapk_active = solution.y[1]
    state_tolerance = 1e-8
    for state_name, values in (("g_on", g_on), ("mapk_active", mapk_active)):
        if np.any(values < -state_tolerance) or np.any(values > 1.0 + state_tolerance):
            raise RuntimeError(f"ODE solver returned out-of-bounds {state_name} values")
    g_on = np.clip(g_on, 0.0, 1.0)
    mapk_active = np.clip(mapk_active, 0.0, 1.0)
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
    if not np.all(np.isfinite(stf_activity)) or not np.all(np.isfinite(gal_product_rate)):
        raise RuntimeError("ODE algebraic outputs contain non-finite values")

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
