#!/usr/bin/env python3
"""Run the pinned DeepMind AF2 Amber relax protocol and prepare review outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from transient_paths import transient_root

from af2_amber_relax_engine import PROTOCOL_ID, REPORT_SCHEMA
from atomic_publish import DelayedPublishSignal
from compare_raw_relaxed import compare
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external
from make_raw_relaxed_review_pml import (
    DEFAULT_RAW_OBJECT,
    DEFAULT_RELAXED_OBJECT,
    build_pml,
    pymol_selection_for_review_scope,
)
from make_tm_review_pml import PYMOL_ACCENT_COLOR, PYMOL_BASE_COLOR
from parse_tm_topology import InputError, MinimalArgumentParser, ensure_output_available
from run_geometry_validation import _require_file, publish_bytes_many

_ORIGINAL_SUBPROCESS_RUN = subprocess.run


def _run_engine_process(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    if subprocess.run is not _ORIGINAL_SUBPROCESS_RUN:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            shell=False,
            text=False,
        )
    return run_external(argv, check=False, text=False)  # type: ignore[return-value]


def _read_expected_output(temp_path: Path) -> bytes:
    if not temp_path.exists() or not temp_path.is_file():
        raise InputError(f"AF2 relax engine did not create expected output: {temp_path}")
    try:
        return temp_path.read_bytes()
    except OSError as exc:
        raise InputError(f"could not read expected output {temp_path}: {exc}") from exc


def _validated_report_bytes(
    temp_report: Path,
    structure_bytes: bytes,
    expected_output: Path,
    protocol_id: str,
) -> bytes:
    report_bytes = _read_expected_output(temp_report)
    try:
        payload = json.loads(report_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"AF2 relax engine wrote an invalid JSON report: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != REPORT_SCHEMA:
        raise InputError("AF2 relax engine wrote an unsupported report schema")
    if payload.get("protocol_id") != protocol_id:
        raise InputError("AF2 relax engine report protocol does not match the requested protocol")
    output = payload.get("output")
    if not isinstance(output, dict):
        raise InputError("AF2 relax engine report has no output identity")
    expected_hash = hashlib.sha256(structure_bytes).hexdigest()
    if output.get("sha256") != expected_hash:
        raise InputError("AF2 relax engine report hash does not match its relaxed PDB")
    reported_path = output.get("path")
    if not isinstance(reported_path, str) or Path(reported_path).resolve() != expected_output.resolve():
        raise InputError("AF2 relax engine report names the wrong final relaxed PDB path")
    return report_bytes


def build_parser() -> MinimalArgumentParser:
    template = (
        "run_restrained_minimization.py --protocol "
        f"{PROTOCOL_ID} --input-structure <pdb> "
        "--output-structure <pdb> --report-json <json> "
        "[--comparison-json <json> --review-pml <pml> "
        "--review-atom-selection <ca-only|backbone>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Run one protein-only PDB through the pinned DeepMind AlphaFold 2 Amber "
            "relaxation preset. The protocol fixes Amber99SB, HBonds constraints, "
            "non-hydrogen restraints (10.0 kcal/mol/A^2), a 2.39 kcal/mol/nm RMS "
            "force tolerance, unlimited inner minimization, three outer iterations, "
            "and OpenMM CPU. These scientific values cannot be changed under this "
            "protocol ID. When both review outputs are requested, the relaxed "
            "structure is compared with the input and a matching PyMOL view is built."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The sibling af2_amber_relax_engine.py is always launched with this same "
            "Python executable; arbitrary external programs or OpenMM arguments are "
            "not accepted. Standard output and standard error remain visible while "
            "the engine runs. "
            "After a zero exit, copies are saved beside --report-json. A non-zero exit "
            "code is returned when relaxation or review fails. An engine failure "
            "publishes nothing. If relaxation succeeds but the "
            "explicit atom mapping cannot be compared, the four minimization outputs "
            "are retained and the review stage returns an error. No acceptance decision "
            "is made.\n\n"
            f"Call template:\n  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--protocol",
        required=True,
        choices=(PROTOCOL_ID,),
        help="fixed, versioned DeepMind AF2 Amber relaxation protocol",
    )
    required.add_argument("--input-structure", required=True, type=Path, help="input structure")
    required.add_argument("--output-structure", required=True, type=Path, help="final minimized structure output")
    required.add_argument("--report-json", required=True, type=Path, help="final minimization report JSON output")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--comparison-json", type=Path, help="raw/minimized numeric comparison JSON; requires --review-pml")
    optional.add_argument("--review-pml", type=Path, help="PyMOL review script; requires --comparison-json")
    optional.add_argument(
        "--review-atom-selection",
        choices=("ca-only", "backbone"),
        default="ca-only",
        help="one atom scope shared by numeric comparison and PyMOL alignment (default: ca-only)",
    )
    optional.add_argument("--force", action="store_true", help="overwrite existing outputs")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_structure = args.input_structure.expanduser()
    output_structure = args.output_structure.expanduser()
    report_json = args.report_json.expanduser()
    comparison_json = (
        args.comparison_json.expanduser() if args.comparison_json is not None else None
    )
    review_pml = args.review_pml.expanduser() if args.review_pml is not None else None
    stdout_path = report_json.with_suffix(report_json.suffix + ".stdout.txt")
    stderr_path = report_json.with_suffix(report_json.suffix + ".stderr.txt")
    minimization_artifacts = [
        ToolArtifact(output_structure, "AF2 Amber relaxed 结构"),
        ToolArtifact(report_json, "AF2 Amber relax 报告"),
        ToolArtifact(stdout_path, "AF2 Amber relax 标准输出"),
        ToolArtifact(stderr_path, "AF2 Amber relax 标准错误"),
    ]
    try:
        if (comparison_json is None) != (review_pml is None):
            raise InputError("--comparison-json and --review-pml must be supplied together")
        if input_structure.suffix.lower() != ".pdb":
            raise InputError("--input-structure must be a protein-only .pdb file")
        _require_file(input_structure, "--input-structure")
        target_paths = [output_structure, report_json, stdout_path, stderr_path]
        if comparison_json is not None and review_pml is not None:
            target_paths.extend((comparison_json, review_pml))
        resolved_targets = {path.resolve() for path in target_paths}
        if len(resolved_targets) != len(target_paths):
            raise InputError("all minimization and review output paths must differ")
        if input_structure.resolve() in resolved_targets:
            raise InputError("all minimization and review outputs must differ from --input-structure")
        for path in target_paths:
            ensure_output_available(path, args.force)
        with tempfile.TemporaryDirectory(
            prefix="restrained-minimization-", dir=transient_root()
        ) as temp_name:
            temp_dir = Path(temp_name)
            temp_structure = temp_dir / output_structure.name
            temp_report = temp_dir / report_json.name
            engine_script = Path(__file__).resolve().with_name(
                "af2_amber_relax_engine.py"
            )
            engine_argv = [
                sys.executable,
                str(engine_script),
                "--protocol",
                args.protocol,
                "--input-pdb",
                str(input_structure),
                "--output-pdb",
                str(temp_structure),
                "--report-json",
                str(temp_report),
                "--published-output-pdb",
                str(output_structure),
            ]
            completed = _run_engine_process(engine_argv)
            if completed.returncode != 0:
                if subprocess.run is not _ORIGINAL_SUBPROCESS_RUN:
                    sys.stderr.write(completed.stderr.decode("utf-8", errors="replace"))
                print(f"Error: AF2 relax engine exited with code {completed.returncode}", file=sys.stderr)
                return completed.returncode or 1
            structure_bytes = _read_expected_output(temp_structure)
            report_bytes = _validated_report_bytes(
                temp_report,
                structure_bytes,
                output_structure,
                args.protocol,
            )
            base_outputs = [
                (output_structure, structure_bytes),
                (report_json, report_bytes),
                (stdout_path, completed.stdout),
                (stderr_path, completed.stderr),
            ]
            if comparison_json is not None and review_pml is not None:
                try:
                    comparison = compare(
                        input_structure,
                        temp_structure,
                        args.review_atom_selection,
                    )
                    comparison["relaxed_file"] = str(output_structure.resolve())
                    comparison_bytes = (
                        json.dumps(comparison, indent=2, sort_keys=True) + "\n"
                    ).encode("utf-8")
                    review_bytes = build_pml(
                        input_structure,
                        output_structure,
                        DEFAULT_RAW_OBJECT,
                        DEFAULT_RELAXED_OBJECT,
                        PYMOL_BASE_COLOR,
                        PYMOL_ACCENT_COLOR,
                        pymol_selection_for_review_scope(
                            args.review_atom_selection
                        ),
                    ).encode("utf-8")
                except InputError as exc:
                    publish_bytes_many(base_outputs, args.force)
                    print(f"Wrote {output_structure}")
                    print(f"Wrote {report_json}")
                    write_tool_result(minimization_artifacts)
                    print(
                        "Error: minimization completed, but review could not be "
                        f"prepared: {exc}",
                        file=sys.stderr,
                    )
                    return 1
                publish_bytes_many(
                    [
                        *base_outputs,
                        (comparison_json, comparison_bytes),
                        (review_pml, review_bytes),
                    ],
                    args.force,
                )
            else:
                publish_bytes_many(base_outputs, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except DelayedPublishSignal as exc:
        return 128 + exc.signum
    print(f"Wrote {output_structure}")
    print(f"Wrote {report_json}")
    artifacts = list(minimization_artifacts)
    if comparison_json is not None and review_pml is not None:
        print(f"Wrote {comparison_json}")
        print(f"Wrote {review_pml}")
        artifacts.extend(
            (
                ToolArtifact(comparison_json, "原始与优化结构比较"),
                ToolArtifact(review_pml, "优化前后结构复核脚本"),
            )
        )
    write_tool_result(artifacts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
