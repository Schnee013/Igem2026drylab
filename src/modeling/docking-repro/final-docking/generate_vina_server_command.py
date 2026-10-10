#!/usr/bin/env python3
"""Validate Vina server-command inputs and render one native shell command."""

from __future__ import annotations

import argparse
import math
import posixpath
import shlex
import sys
from dataclasses import asdict, dataclass
from typing import Mapping, Sequence


DEFAULT_VINA_EXECUTABLE = (
    "/ifs1/User/dengwei/igem/envs/docking-frame-repair-v1/bin/vina"
)
DEFAULT_CPU = "16"
DEFAULT_EXHAUSTIVENESS = "8"
DEFAULT_NUM_MODES = "9"
DEFAULT_ENERGY_RANGE = "3"
DEFAULT_SEED = "0"


@dataclass(frozen=True)
class VinaServerCommandInputs:
    """Complete textual input contract for one native Vina server command."""

    server_workdir: str = ""
    vina_executable: str = DEFAULT_VINA_EXECUTABLE
    receptor: str = ""
    ligand: str = ""
    center_x: str = ""
    center_y: str = ""
    center_z: str = ""
    size_x: str = ""
    size_y: str = ""
    size_z: str = ""
    cpu: str = DEFAULT_CPU
    exhaustiveness: str = DEFAULT_EXHAUSTIVENESS
    num_modes: str = DEFAULT_NUM_MODES
    energy_range: str = DEFAULT_ENERGY_RANGE
    seed: str = DEFAULT_SEED
    pose_output: str = ""
    log_output: str = ""

    @classmethod
    def from_mapping(
        cls, values: Mapping[str, object]
    ) -> "VinaServerCommandInputs":
        defaults = asdict(cls())
        return cls(
            **{
                dest: "" if values.get(dest, default) is None else str(values.get(dest, default))
                for dest, default in defaults.items()
            }
        )

    def values(self) -> dict[str, str]:
        return asdict(self)


VINA_INPUT_DESTS = tuple(VinaServerCommandInputs.__dataclass_fields__)

_PATH_DESTS = {
    "server_workdir",
    "vina_executable",
    "receptor",
    "ligand",
    "pose_output",
    "log_output",
}
_WORKDIR_RELATIVE_PATH_DESTS = {
    "receptor",
    "ligand",
    "pose_output",
    "log_output",
}
_NUMERIC_FIELDS = {
    "center_x": ("float", False),
    "center_y": ("float", False),
    "center_z": ("float", False),
    "size_x": ("float", True),
    "size_y": ("float", True),
    "size_z": ("float", True),
    "cpu": ("int", True),
    "exhaustiveness": ("int", True),
    "num_modes": ("int", True),
    "energy_range": ("float", True),
    "seed": ("int", False),
}
_COMMAND_OPTIONS = (
    ("receptor", "--receptor"),
    ("ligand", "--ligand"),
    ("center_x", "--center_x"),
    ("center_y", "--center_y"),
    ("center_z", "--center_z"),
    ("size_x", "--size_x"),
    ("size_y", "--size_y"),
    ("size_z", "--size_z"),
    ("cpu", "--cpu"),
    ("exhaustiveness", "--exhaustiveness"),
    ("num_modes", "--num_modes"),
    ("energy_range", "--energy_range"),
    ("seed", "--seed"),
    ("pose_output", "--out"),
)


class VinaCommandValidationError(ValueError):
    def __init__(self, errors: Mapping[str, str]) -> None:
        self.errors = dict(errors)
        dest, reason = next(iter(self.errors.items()))
        super().__init__(f"--{dest.replace('_', '-')}: {reason}")


def default_vina_server_command_values() -> dict[str, str]:
    """Return a fresh copy of every field's default textual value."""

    return VinaServerCommandInputs().values()


def validate_vina_server_command(
    inputs: VinaServerCommandInputs | Mapping[str, object],
) -> dict[str, str]:
    """Return ordered field-specific validation reasons; an empty dict is valid."""

    command_inputs = _coerce_inputs(inputs)
    values = command_inputs.values()
    errors: dict[str, str] = {}

    for dest in VINA_INPUT_DESTS:
        raw = values[dest]
        if not raw.strip():
            errors[dest] = "不能为空。"
            continue
        if "\x00" in raw or "\n" in raw or "\r" in raw:
            errors[dest] = "不能包含换行或 NUL 字符。"

    for dest in _PATH_DESTS:
        raw = values[dest]
        if dest not in errors and raw != raw.strip():
            errors[dest] = "不能以空白开头或结尾。"

    for dest, (kind, positive) in _NUMERIC_FIELDS.items():
        if dest in errors:
            continue
        numeric = _parse_numeric(raw=values[dest], kind=kind)
        if numeric is None:
            errors[dest] = "必须是整数。" if kind == "int" else "必须是有限数值。"
        elif positive and numeric <= 0:
            errors[dest] = "必须大于 0。"

    workdir = values["server_workdir"]
    if "server_workdir" not in errors and not posixpath.isabs(workdir):
        errors["server_workdir"] = "必须填写绝对路径。"

    executable = values["vina_executable"]
    if "vina_executable" not in errors and not posixpath.isabs(executable):
        errors["vina_executable"] = "必须填写绝对路径。"

    for dest in _WORKDIR_RELATIVE_PATH_DESTS:
        path = values[dest]
        if dest not in errors and path.startswith(("~", "$")):
            errors[dest] = (
                "请使用相对工作目录路径或服务器绝对路径；"
                "命令不会展开 ~ 或 shell 变量。"
            )

    if not errors.keys() & {"server_workdir", "pose_output", "log_output"}:
        pose_path = _normalized_server_path(workdir, values["pose_output"])
        log_path = _normalized_server_path(workdir, values["log_output"])
        if pose_path == log_path:
            errors["log_output"] = "与姿势输出不能使用同一路径。"

    return errors


def render_vina_server_command(
    inputs: VinaServerCommandInputs | Mapping[str, object],
) -> str:
    """Render the validated native server Vina shell command without executing it."""

    command_inputs = _coerce_inputs(inputs)
    errors = validate_vina_server_command(command_inputs)
    if errors:
        raise VinaCommandValidationError(errors)

    values = command_inputs.values()
    lines = [
        f"cd -- {_quote_path(values['server_workdir'])} &&",
        f"{shlex.quote(values['vina_executable'])} \\",
    ]
    for dest, option in _COMMAND_OPTIONS:
        raw = values[dest]
        argument = _quote_path(raw) if dest in _PATH_DESTS else shlex.quote(raw.strip())
        lines.append(f"  {option} {argument} \\")
    lines.append(f"  > {_quote_path(values['log_output'])} 2>&1")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate inputs and print one native server Vina shell command. "
            "This command generator does not connect to SSH or run Vina."
        )
    )
    parser.add_argument("--server-workdir", required=True, help="Absolute server working directory.")
    parser.add_argument(
        "--vina-executable",
        default=DEFAULT_VINA_EXECUTABLE,
        help="Absolute Vina executable on the server.",
    )
    parser.add_argument("--receptor", required=True, help="Receptor PDBQT path on the server.")
    parser.add_argument("--ligand", required=True, help="Ligand PDBQT path on the server.")
    parser.add_argument("--center-x", required=True, help="Search-box center X.")
    parser.add_argument("--center-y", required=True, help="Search-box center Y.")
    parser.add_argument("--center-z", required=True, help="Search-box center Z.")
    parser.add_argument("--size-x", required=True, help="Positive search-box size X.")
    parser.add_argument("--size-y", required=True, help="Positive search-box size Y.")
    parser.add_argument("--size-z", required=True, help="Positive search-box size Z.")
    parser.add_argument("--cpu", default=DEFAULT_CPU, help="Positive Vina CPU count.")
    parser.add_argument(
        "--exhaustiveness",
        default=DEFAULT_EXHAUSTIVENESS,
        help="Positive Vina exhaustiveness.",
    )
    parser.add_argument(
        "--num-modes", default=DEFAULT_NUM_MODES, help="Positive number of poses to retain."
    )
    parser.add_argument(
        "--energy-range",
        default=DEFAULT_ENERGY_RANGE,
        help="Positive Vina energy range in kcal/mol.",
    )
    parser.add_argument("--seed", default=DEFAULT_SEED, help="Integer Vina random seed.")
    parser.add_argument("--pose-output", required=True, help="Pose PDBQT output path on the server.")
    parser.add_argument("--log-output", required=True, help="Vina log output path on the server.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)
    try:
        command = render_vina_server_command(vars(namespace))
    except VinaCommandValidationError as exc:
        parser.error(str(exc))
    sys.stdout.write(command)
    return 0


def _coerce_inputs(
    inputs: VinaServerCommandInputs | Mapping[str, object],
) -> VinaServerCommandInputs:
    if isinstance(inputs, VinaServerCommandInputs):
        return inputs
    return VinaServerCommandInputs.from_mapping(inputs)


def _parse_numeric(*, raw: str, kind: str) -> float | int | None:
    try:
        if kind == "int":
            return int(raw.strip())
        value = float(raw.strip())
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _normalized_server_path(workdir: str, path: str) -> str:
    return posixpath.normpath(path if posixpath.isabs(path) else posixpath.join(workdir, path))


def _quote_path(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
