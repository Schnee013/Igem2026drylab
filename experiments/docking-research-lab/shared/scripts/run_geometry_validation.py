#!/usr/bin/env python3
"""Run one explicit geometry validator command and preserve native output."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from atomic_publish import AtomicPublishError, DelayedPublishSignal, publish_staged_files
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external
from parse_tm_topology import InputError, MinimalArgumentParser, ensure_output_available
from summarize_geometry_validation import build_summary, parse_metric
from transient_paths import transient_root

_ORIGINAL_SUBPROCESS_RUN = subprocess.run


PLACEHOLDERS = {
    "{structure}": "structure",
    "{output_dir}": "output_dir",
    "{stdout}": "stdout",
    "{stderr}": "stderr",
}


def parse_metric_unit(raw: str) -> tuple[str, str]:
    name, separator, unit = raw.partition("=")
    if not separator or not name.strip() or not unit.strip():
        raise argparse.ArgumentTypeError("metric unit must be NAME=UNIT")
    return name.strip(), unit.strip()


def _require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise InputError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise InputError(f"{label} is not a regular file: {path}")


def _require_executable(path: Path, label: str) -> None:
    _require_file(path, label)
    if not os.access(path, os.X_OK):
        raise InputError(f"{label} is not executable: {path}")


def expand_args(raw_args: list[str], values: dict[str, Path]) -> list[str]:
    if not raw_args:
        raise InputError("--arg must be supplied at least once; no validator arguments are added automatically")
    expanded: list[str] = []
    for arg in raw_args:
        value = arg
        for token, key in PLACEHOLDERS.items():
            value = value.replace(token, str(values[key]))
        expanded.append(value)
    return expanded


def _run_validator_process(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    if subprocess.run is not _ORIGINAL_SUBPROCESS_RUN:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            shell=False,
            text=False,
        )
    return run_external(argv, check=False, text=False)  # type: ignore[return-value]


def _write_stage(path: Path, data: bytes) -> Path:
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        staged = temporary_path
        temporary_path = None
        return staged
    except OSError as exc:
        raise InputError(f"could not stage output {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def publish_bytes_many(outputs: list[tuple[Path, bytes]], force: bool) -> None:
    if not outputs:
        return
    resolved = [path.resolve() for path, _ in outputs]
    if len(set(resolved)) != len(resolved):
        raise InputError("standard-output, standard-error, and run-list paths must be distinct")
    for path, _ in outputs:
        ensure_output_available(path, force)

    stages: list[tuple[Path, Path]] = []
    try:
        stages = [(path, _write_stage(path, data)) for path, data in outputs]
        publish_staged_files(
            [(stage_path, final_path) for final_path, stage_path in stages],
            overwrite=force,
        )
        stages = []
    except FileExistsError as exc:
        raise InputError("an output appeared during writing; no run outputs were published") from exc
    except AtomicPublishError as exc:
        raise InputError(f"could not save all run outputs: {exc}") from exc
    except OSError as exc:
        raise InputError(f"could not save all run outputs: {exc}") from exc
    finally:
        for _, stage_path in stages:
            try:
                stage_path.unlink()
            except FileNotFoundError:
                pass


def build_parser() -> MinimalArgumentParser:
    template = (
        "run_geometry_validation.py --backend <label> --executable <path> "
        "--structure <model.pdb> --output-dir <dir> --arg <program-argument>... "
        "[--native-result <relative.json> --metric <name=/json/pointer>... "
        "--metric-unit <name=unit>... --result-format json-pointer-v1] "
        "[--manifest <manifest.json>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Run the selected geometry-checking program once with the arguments "
            "provided here. In combined mode, an installed adapter also declares one "
            "native result JSON and its versioned metric mappings; the checker runs in "
            "temporary staging and the native result, logs, manifest, and mechanical "
            "summary are published together. No thresholds are selected or applied."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Placeholders accepted inside --arg values:\n"
            "  {structure} {output_dir} {stdout} {stderr}\n\n"
            "Standard output and standard error remain visible while the checker runs. "
            "A non-zero exit code is returned if checking or summary extraction fails. "
            "Combined mode requires {output_dir} in the argument template so native "
            "files stay in hidden staging until the checker succeeds. Missing metrics "
            "are errors, never zeroes or pass decisions. A non-zero checker exit "
            "publishes nothing. If checking succeeds but summary extraction fails, the "
            "native result, logs, and manifest are retained with a non-zero exit.\n\n"
            f"Call template:\n  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--backend", required=True, help="geometry-checking program name and version")
    required.add_argument("--executable", required=True, type=Path, help="geometry-checking program to start")
    required.add_argument("--structure", required=True, type=Path, help="structure file to check")
    required.add_argument("--output-dir", required=True, type=Path, help="existing directory where the program writes its native results")
    required.add_argument("--arg", required=True, action="append", help="one program argument after the executable; repeat in execution order")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--manifest", type=Path, help="JSON file describing this run, its outputs, and exit code (default: <output-dir>/manifest.json)")
    optional.add_argument("--native-result", help="adapter-declared native JSON path relative to the staged output directory")
    optional.add_argument("--result-format", default="json-pointer-v1", help="versioned native JSON layout used by the metric adapter (default: json-pointer-v1)")
    optional.add_argument("--metric", action="append", type=parse_metric, help="adapter-declared NAME=/json/pointer scalar extraction; repeat for every metric")
    optional.add_argument("--metric-unit", action="append", type=parse_metric_unit, help="adapter-declared NAME=UNIT entry matching every --metric")
    optional.add_argument("--summary-output", type=Path, help="summary JSON output (default: <output-dir>/geometry-summary.json)")
    optional.add_argument("--force", action="store_true", help="replace existing saved standard output, standard error, and run list")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def _validated_native_result_path(path: Path) -> Path:
    if path.is_absolute() or not path.parts or path == Path("."):
        raise InputError("--native-result must be a non-empty relative JSON path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise InputError("--native-result must stay inside the staged output directory")
    if path.suffix.lower() != ".json":
        raise InputError("--native-result must identify a JSON file")
    return path


def _ensure_combined_output_root(output_dir: Path) -> None:
    if output_dir.exists():
        if not output_dir.is_dir():
            raise InputError(f"--output-dir is not a directory: {output_dir}")
        return
    if not output_dir.parent.exists() or not output_dir.parent.is_dir():
        raise InputError(f"output directory parent does not exist: {output_dir.parent}")


def _ensure_combined_targets_available(paths: Sequence[Path], force: bool) -> None:
    resolved = [path.resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise InputError("native result, summary, manifest, stdout, and stderr paths must differ")
    for path in paths:
        if path.exists() and path.is_dir():
            raise InputError(f"output target is a directory: {path}")
        if path.exists() and not force:
            raise InputError(f"output already exists: {path} (use --force to overwrite)")


def _publish_combined_outputs(
    outputs: list[tuple[Path, bytes]], output_dir: Path, force: bool
) -> None:
    output_dir.mkdir(exist_ok=True)
    for path, _data in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    publish_bytes_many(outputs, force)


def _run_combined_validation(
    args: argparse.Namespace,
    *,
    executable: Path,
    structure: Path,
    output_dir: Path,
    manifest: Path,
    stdout_path: Path,
    stderr_path: Path,
) -> int:
    if args.native_result is None or not args.metric or not args.metric_unit:
        raise InputError(
            "combined geometry validation requires --native-result, at least one "
            "--metric, and one matching --metric-unit per metric"
        )
    if not any("{output_dir}" in raw for raw in args.arg):
        raise InputError(
            "combined geometry validation requires {output_dir} in the --arg template"
        )
    native_relative = _validated_native_result_path(Path(args.native_result))
    metric_names = [name for name, _pointer in args.metric]
    unit_names = [name for name, _unit in args.metric_unit]
    if len(metric_names) != len(set(metric_names)):
        raise InputError("combined geometry metric names must be unique")
    if len(unit_names) != len(set(unit_names)):
        raise InputError("combined geometry metric-unit names must be unique")
    if set(metric_names) != set(unit_names):
        missing = sorted(set(metric_names) - set(unit_names))
        extra = sorted(set(unit_names) - set(metric_names))
        details = []
        if missing:
            details.append("missing units for " + ", ".join(missing))
        if extra:
            details.append("units without metrics for " + ", ".join(extra))
        raise InputError("metric-unit mapping mismatch: " + "; ".join(details))
    metric_units = dict(args.metric_unit)
    native_output = output_dir / native_relative
    summary_output = (
        args.summary_output.expanduser()
        if args.summary_output is not None
        else output_dir / "geometry-summary.json"
    )
    targets = [native_output, summary_output, manifest, stdout_path, stderr_path]
    _ensure_combined_output_root(output_dir)
    _ensure_combined_targets_available(targets, args.force)
    if structure.resolve() in {path.resolve() for path in targets}:
        raise InputError("geometry outputs must differ from --structure")

    with tempfile.TemporaryDirectory(
        prefix="geometry-validation-", dir=transient_root()
    ) as temp_name:
        staged_output_dir = Path(temp_name) / "native-output"
        staged_output_dir.mkdir()
        staged_stdout = staged_output_dir / stdout_path.name
        staged_stderr = staged_output_dir / stderr_path.name
        native_args = expand_args(
            args.arg,
            {
                "structure": structure,
                "output_dir": staged_output_dir,
                "stdout": staged_stdout,
                "stderr": staged_stderr,
            },
        )
        completed = _run_validator_process([str(executable), *native_args])
        if completed.returncode != 0:
            sys.stderr.write(completed.stderr.decode("utf-8", errors="replace"))
            print(
                f"Error: validator exited with code {completed.returncode}",
                file=sys.stderr,
            )
            return completed.returncode or 1

        staged_native = staged_output_dir / native_relative
        if not staged_native.exists() or not staged_native.is_file():
            raise InputError(
                "validator completed but did not create the adapter-declared native "
                f"result: {native_relative}"
            )
        try:
            native_bytes = staged_native.read_bytes()
        except OSError as exc:
            raise InputError(f"could not read native geometry result: {exc}") from exc

        summary_error: InputError | None = None
        summary_bytes: bytes | None = None
        try:
            summary = build_summary(
                staged_native,
                args.result_format,
                args.metric,
            )
            summary["source_file"] = str(native_output.resolve())
            summary["metric_units"] = {
                name: metric_units[name] for name in metric_names
            }
            summary_bytes = (
                json.dumps(summary, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
        except InputError as exc:
            message = str(exc).replace(str(staged_native), str(native_output))
            summary_error = InputError(message)

        manifest_content = json.dumps(
            {
                "backend": args.backend,
                "program_path": str(executable),
                "program_argument_template": args.arg,
                "program_arguments": [
                    value.replace(str(staged_output_dir), "{staging_output_dir}")
                    for value in native_args
                ],
                "structure": str(structure.resolve()),
                "output_dir": str(output_dir.resolve()),
                "native_result": str(native_output.resolve()),
                "native_result_relative_path": str(native_relative),
                "result_format": args.result_format,
                "metric_mappings": [f"{name}={pointer}" for name, pointer in args.metric],
                "metric_units": metric_units,
                "summary": str(summary_output.resolve()),
                "summary_status": "failed" if summary_error is not None else "completed",
                "summary_error": str(summary_error) if summary_error is not None else None,
                "stdout": str(stdout_path.resolve()),
                "stderr": str(stderr_path.resolve()),
                "exit_code": completed.returncode,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
        outputs = [
            (native_output, native_bytes),
            (manifest, manifest_content.encode("utf-8")),
            (stdout_path, completed.stdout),
            (stderr_path, completed.stderr),
        ]
        if summary_bytes is not None:
            outputs.append((summary_output, summary_bytes))
        _publish_combined_outputs(outputs, output_dir, args.force)

    artifacts = [
        ToolArtifact(output_dir, "几何检查结果组", "directory"),
        ToolArtifact(native_output, "几何检查原生结果"),
        ToolArtifact(manifest, "几何检查运行清单"),
        ToolArtifact(stdout_path, "几何检查标准输出"),
        ToolArtifact(stderr_path, "几何检查标准错误"),
    ]
    if summary_error is not None:
        print(f"Wrote {native_output}")
        print(f"Wrote {manifest}")
        write_tool_result(artifacts)
        print(
            f"Error: geometry check completed, but summary extraction failed: {summary_error}",
            file=sys.stderr,
        )
        return 1

    artifacts.append(ToolArtifact(summary_output, "几何检查摘要"))
    print(f"Wrote {native_output}")
    print(f"Wrote {summary_output}")
    print(f"Wrote {manifest}")
    write_tool_result(artifacts)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    executable = args.executable.expanduser()
    structure = args.structure.expanduser()
    output_dir = args.output_dir.expanduser()
    manifest = args.manifest.expanduser() if args.manifest is not None else output_dir / "manifest.json"
    stdout_path = output_dir / "geometry-validator.stdout.txt"
    stderr_path = output_dir / "geometry-validator.stderr.txt"
    try:
        _require_executable(executable, "--executable")
        _require_file(structure, "--structure")
        combined_requested = (
            args.native_result is not None
            or bool(args.metric)
            or bool(args.metric_unit)
            or args.summary_output is not None
        )
        if combined_requested:
            return _run_combined_validation(
                args,
                executable=executable,
                structure=structure,
                output_dir=output_dir,
                manifest=manifest,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
            )
        if not output_dir.exists() or not output_dir.is_dir():
            raise InputError(f"--output-dir must be an existing directory: {output_dir}")
        resolved_targets = {path.resolve() for path in (stdout_path, stderr_path, manifest)}
        if len(resolved_targets) != 3:
            raise InputError("--manifest must differ from the standard-output and standard-error files")
        for path in (stdout_path, stderr_path, manifest):
            ensure_output_available(path, args.force)
        native_args = expand_args(
            args.arg,
            {"structure": structure, "output_dir": output_dir, "stdout": stdout_path, "stderr": stderr_path},
        )
        completed = _run_validator_process([str(executable), *native_args])
        if completed.returncode != 0:
            sys.stderr.write(completed.stderr.decode("utf-8", errors="replace"))
            print(f"Error: validator exited with code {completed.returncode}", file=sys.stderr)
            return completed.returncode or 1
        content = json.dumps(
            {
                "backend": args.backend,
                "program_path": str(executable),
                "program_arguments": native_args,
                "structure": str(structure.resolve()),
                "output_dir": str(output_dir.resolve()),
                "stdout": str(stdout_path.resolve()),
                "stderr": str(stderr_path.resolve()),
                "exit_code": completed.returncode,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
        publish_bytes_many(
            [
                (stdout_path, completed.stdout),
                (stderr_path, completed.stderr),
                (manifest, content.encode("utf-8")),
            ],
            args.force,
        )
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except DelayedPublishSignal as exc:
        return 128 + exc.signum
    print(f"Wrote {manifest}")
    write_tool_result(
        [
            ToolArtifact(output_dir, "几何检查输出目录", "directory"),
            ToolArtifact(manifest, "几何检查运行清单"),
            ToolArtifact(stdout_path, "几何检查标准输出"),
            ToolArtifact(stderr_path, "几何检查标准错误"),
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
