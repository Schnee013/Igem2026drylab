#!/usr/bin/env python3
"""Parse one DeepTMHMM or Phyre 2.2 topology file into validated JSON."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from docking_tool_result import ToolArtifact, write_tool_result


COORDINATE_SYSTEM = "1-based-inclusive"
SOURCE_FORMATS = ("deeptmhmm-gff3", "phyre2-memsat-svm")
JSON_FIELDS = (
    "source_format",
    "source_file",
    "fasta_id",
    "sequence_length",
    "coordinate_system",
    "tm_segments",
    "helix_count",
    "n_terminal",
    "signal_peptide",
    "signal_score",
    "reentrant_helices",
    "score",
)


class InputError(ValueError):
    """An input or output does not satisfy the declared interface."""


class MinimalArgumentParser(argparse.ArgumentParser):
    """Keep argument failures short while retaining the missing option names."""

    def __init__(self, *args: Any, short_usage: str, **kwargs: Any) -> None:
        self.short_usage = short_usage
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        self.exit(
            2,
            f"Error: {message}\n"
            f"Usage: {self.short_usage}\n"
            "Use -h or --help for details.\n",
        )


def read_text_file(path: Path, label: str) -> str:
    """Read a required UTF-8 text file with a path-specific error."""
    if not path.exists():
        raise InputError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise InputError(f"{label} is not a regular file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"{label} is not valid UTF-8: {path} ({exc})") from exc
    except OSError as exc:
        raise InputError(f"{label} is not readable: {path} ({exc})") from exc


def read_single_fasta(path: Path) -> tuple[str, str]:
    """Return the identifier and sequence from exactly one FASTA record."""
    text = read_text_file(path, "FASTA file")
    records: list[tuple[str, list[str]]] = []
    header: str | None = None
    sequence_lines: list[str] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append((header, sequence_lines))
            header = line[1:].strip()
            sequence_lines = []
            if not header:
                raise InputError(f"{path}: empty FASTA header at line {line_number}")
        else:
            if header is None:
                raise InputError(
                    f"{path}: sequence data appears before the first FASTA header "
                    f"at line {line_number}"
                )
            sequence_lines.append("".join(line.split()).upper())

    if header is not None:
        records.append((header, sequence_lines))
    if len(records) != 1:
        raise InputError(
            f"{path}: expected exactly one FASTA record, found {len(records)}"
        )

    fasta_header, lines = records[0]
    sequence = "".join(lines)
    if not sequence:
        raise InputError(f"{path}: the FASTA record has an empty sequence")
    invalid = sorted(set(sequence) - set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    if invalid:
        raise InputError(
            f"{path}: FASTA sequence contains invalid character(s): "
            f"{', '.join(repr(value) for value in invalid)}"
        )
    return fasta_header.split()[0], sequence


def _integer(value: str, path: Path, field: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise InputError(f"{path}: {field} must be an integer, got {value!r}") from exc


def _number(value: str, path: Path, field: str) -> int | float:
    stripped = value.strip()
    if re.fullmatch(r"[+-]?\d+", stripped):
        return int(stripped)
    try:
        number = float(stripped)
    except ValueError as exc:
        raise InputError(f"{path}: {field} must be numeric, got {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{path}: {field} must be finite, got {value!r}")
    return number


def _segments(intervals: list[tuple[int, int]]) -> list[dict[str, int]]:
    ordered = sorted(intervals)
    return [
        {"index": index, "start": start, "end": end}
        for index, (start, end) in enumerate(ordered, start=1)
    ]


def detect_source_format(path: Path) -> str:
    """Identify only an unambiguous, structurally recognizable topology source."""
    text = read_text_file(path, "topology source file")
    lines = text.splitlines()
    data_lines = [
        line for line in lines if line.strip() and not line.lstrip().startswith("#")
    ]
    deeptmhmm_features = {"TMhelix", "inside", "outside"}
    deeptmhmm_marker = False
    deeptmhmm_candidate = bool(data_lines)
    for raw_line in data_lines:
        fields = raw_line.split("\t")
        if len(fields) != 8:
            deeptmhmm_candidate = False
            continue
        sequence_id, feature = fields[0].strip(), fields[1].strip()
        if feature in deeptmhmm_features:
            deeptmhmm_marker = True
        if (
            not sequence_id
            or not re.fullmatch(r"[+-]?\d+", fields[2].strip())
            or not re.fullmatch(r"[+-]?\d+", fields[3].strip())
        ):
            deeptmhmm_candidate = False
    deeptmhmm_candidate = deeptmhmm_candidate and deeptmhmm_marker

    result_starts = [
        index for index, line in enumerate(lines) if line.strip() == "Results:"
    ]
    phyre_candidate = False
    if result_starts:
        recognized_keys = {"Topology", "Helix count", "N-terminal"}
        final_values = {
            raw_line.partition(":")[0].strip()
            for raw_line in lines[result_starts[-1] + 1 :]
            if ":" in raw_line
        }
        phyre_candidate = recognized_keys.issubset(final_values)

    if phyre_candidate and (deeptmhmm_candidate or deeptmhmm_marker):
        raise InputError(
            f"{path}: source format is ambiguous: both DeepTMHMM and final "
            "Phyre 2.2 MEMSAT-SVM signatures were found"
        )
    if deeptmhmm_candidate:
        return "deeptmhmm-gff3"
    if phyre_candidate:
        return "phyre2-memsat-svm"
    raise InputError(
        f"{path}: could not detect source format: expected an approved 8-column "
        "DeepTMHMM layout with recognized topology fields, or a final Phyre 2.2 "
        "MEMSAT-SVM Results block with Topology, Helix count, and N-terminal"
    )


def parse_deeptmhmm_gff3(path: Path) -> dict[str, Any]:
    """Parse the approved eight-column DeepTMHMM export layout."""
    text = read_text_file(path, "DeepTMHMM topology file")
    intervals: list[tuple[int, int]] = []
    tm_sequence_ids: set[str] = set()
    n_terminal_labels: set[str] = set()

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.startswith("#"):
            continue
        fields = raw_line.split("\t")
        if len(fields) != 8:
            raise InputError(
                f"{path}: line {line_number} has {len(fields)} tab-separated fields; "
                "the approved DeepTMHMM layout requires exactly 8"
            )
        sequence_id, feature = fields[0].strip(), fields[1].strip()
        if not sequence_id:
            raise InputError(f"{path}: empty sequence identifier at line {line_number}")
        start = _integer(fields[2].strip(), path, f"line {line_number} start")
        end = _integer(fields[3].strip(), path, f"line {line_number} end")
        if feature == "TMhelix":
            intervals.append((start, end))
            tm_sequence_ids.add(sequence_id)
        elif feature in {"inside", "outside"} and start == 1:
            n_terminal_labels.add(feature)

    if len(tm_sequence_ids) > 1:
        raise InputError(
            f"{path}: TMhelix rows contain multiple sequence identifiers: "
            f"{', '.join(sorted(tm_sequence_ids))}"
        )
    if len(n_terminal_labels) > 1:
        raise InputError(
            f"{path}: conflicting N-terminal labels found: "
            f"{', '.join(sorted(n_terminal_labels))}"
        )
    return {
        "tm_segments": _segments(intervals),
        "helix_count": len(intervals),
        "n_terminal": next(iter(n_terminal_labels), None),
        "signal_peptide": None,
        "signal_score": None,
        "reentrant_helices": None,
        "score": None,
    }


def parse_phyre2_memsat_svm(path: Path) -> dict[str, Any]:
    """Parse only the last final Results block from MEMSAT-SVM output."""
    text = read_text_file(path, "Phyre 2.2 MEMSAT-SVM topology file")
    lines = text.splitlines()
    result_starts = [
        index for index, line in enumerate(lines) if line.strip() == "Results:"
    ]
    if not result_starts:
        raise InputError(f"{path}: no independent 'Results:' line was found")

    recognized = {
        "Topology",
        "Helix count",
        "N-terminal",
        "Signal peptide",
        "Signal score",
        "Re-entrant helices",
        "Score",
    }
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        lines[result_starts[-1] + 1 :], start=result_starts[-1] + 2
    ):
        if not raw_line.strip():
            continue
        key, separator, value = raw_line.partition(":")
        if not separator:
            raise InputError(
                f"{path}: malformed line {line_number} in the final Results block: "
                f"{raw_line!r}"
            )
        key = key.strip()
        if key not in recognized:
            continue
        if key in values:
            raise InputError(
                f"{path}: duplicate {key!r} field in the final Results block"
            )
        values[key] = value.strip()

    missing = [
        field for field in ("Topology", "Helix count", "N-terminal")
        if field not in values
    ]
    if missing:
        raise InputError(
            f"{path}: final Results block is missing required field(s): "
            f"{', '.join(missing)}"
        )

    topology_parts = [part.strip() for part in values["Topology"].split(",")]
    if not topology_parts or any(not part for part in topology_parts):
        raise InputError(f"{path}: Topology is not a non-empty interval list")
    intervals: list[tuple[int, int]] = []
    for position, part in enumerate(topology_parts, start=1):
        match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if not match:
            raise InputError(
                f"{path}: Topology interval {position} is invalid: {part!r}"
            )
        intervals.append((int(match.group(1)), int(match.group(2))))

    helix_count = _integer(values["Helix count"], path, "Helix count")
    if helix_count != len(intervals):
        raise InputError(
            f"{path}: Helix count is {helix_count}, but Topology contains "
            f"{len(intervals)} interval(s)"
        )
    n_terminal = values["N-terminal"].lower()
    if n_terminal not in {"in", "out"}:
        raise InputError(
            f"{path}: N-terminal must be 'in' or 'out', got "
            f"{values['N-terminal']!r}"
        )

    def optional_text(field: str) -> str | None:
        if field not in values:
            return None
        if not values[field]:
            raise InputError(f"{path}: {field} is present but empty")
        return values[field]

    return {
        "tm_segments": _segments(intervals),
        "helix_count": helix_count,
        "n_terminal": n_terminal,
        "signal_peptide": optional_text("Signal peptide"),
        "signal_score": (
            _number(values["Signal score"], path, "Signal score")
            if "Signal score" in values
            else None
        ),
        "reentrant_helices": optional_text("Re-entrant helices"),
        "score": (
            _number(values["Score"], path, "Score")
            if "Score" in values
            else None
        ),
    }


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_topology_json(
    data: object,
    *,
    source: str,
    expected_sequence_length: int | None = None,
) -> dict[str, Any]:
    """Validate the standard topology JSON used by both PML generators."""
    if not isinstance(data, dict):
        raise InputError(f"{source}: topology JSON root must be an object")
    missing = [field for field in JSON_FIELDS if field not in data]
    if missing:
        raise InputError(
            f"{source}: topology JSON is missing field(s): {', '.join(missing)}"
        )
    if data["source_format"] not in SOURCE_FORMATS:
        raise InputError(
            f"{source}: unsupported source_format: {data['source_format']!r}"
        )
    for field in ("source_file", "fasta_id"):
        if not isinstance(data[field], str) or not data[field]:
            raise InputError(f"{source}: {field} must be a non-empty string")
    sequence_length = data["sequence_length"]
    if not _is_integer(sequence_length) or sequence_length < 1:
        raise InputError(f"{source}: sequence_length must be a positive integer")
    if expected_sequence_length is not None and sequence_length != expected_sequence_length:
        raise InputError(
            f"{source}: sequence_length is {sequence_length}, but the supplied "
            f"FASTA length is {expected_sequence_length}"
        )
    if data["coordinate_system"] != COORDINATE_SYSTEM:
        raise InputError(
            f"{source}: coordinate_system must be {COORDINATE_SYSTEM!r}"
        )

    raw_segments = data["tm_segments"]
    if not isinstance(raw_segments, list) or not raw_segments:
        raise InputError(f"{source}: tm_segments must contain at least one segment")
    previous_end = 0
    for expected_index, segment in enumerate(raw_segments, start=1):
        if not isinstance(segment, dict):
            raise InputError(
                f"{source}: tm_segments[{expected_index - 1}] must be an object"
            )
        for field in ("index", "start", "end"):
            if field not in segment or not _is_integer(segment[field]):
                raise InputError(
                    f"{source}: TM{expected_index} {field} must be an integer"
                )
        if segment["index"] != expected_index:
            raise InputError(
                f"{source}: segment index {segment['index']} appears where "
                f"{expected_index} is required"
            )
        start, end = segment["start"], segment["end"]
        if not 1 <= start <= end <= sequence_length:
            raise InputError(
                f"{source}: TM{expected_index} interval {start}-{end} is outside "
                f"1-{sequence_length} or has start > end"
            )
        if start <= previous_end:
            raise InputError(
                f"{source}: TM{expected_index} interval {start}-{end} is not "
                "strictly ordered and non-overlapping"
            )
        previous_end = end

    helix_count = data["helix_count"]
    if not _is_integer(helix_count) or helix_count != len(raw_segments):
        raise InputError(
            f"{source}: helix_count must equal the {len(raw_segments)} TM segment(s)"
        )
    if data["n_terminal"] not in {None, "in", "out", "inside", "outside"}:
        raise InputError(
            f"{source}: n_terminal must be null, in, out, inside, or outside"
        )
    for field in ("signal_peptide", "reentrant_helices"):
        if data[field] is not None and not isinstance(data[field], str):
            raise InputError(f"{source}: {field} must be a string or null")
    for field in ("signal_score", "score"):
        if data[field] is not None and not _is_number(data[field]):
            raise InputError(f"{source}: {field} must be a finite number or null")
    return data


def load_topology_json(
    path: Path, *, expected_sequence_length: int | None = None
) -> dict[str, Any]:
    """Read and validate a topology JSON file for downstream scripts."""
    text = read_text_file(path, "topology JSON")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    return validate_topology_json(
        data, source=str(path), expected_sequence_length=expected_sequence_length
    )


def ensure_output_available(path: Path, force: bool) -> None:
    """Reject an existing output unless the caller explicitly permits replacement."""
    if path.exists() and not force:
        raise InputError(f"output already exists: {path} (use --force to overwrite)")
    if not path.parent.exists():
        raise InputError(f"output directory does not exist: {path.parent}")
    if not path.parent.is_dir():
        raise InputError(f"output parent is not a directory: {path.parent}")


def ensure_distinct_output(path: Path, inputs: Sequence[tuple[str, Path]]) -> None:
    """Prevent --force from replacing any declared input path."""
    resolved_output = path.resolve()
    for option, input_path in inputs:
        if resolved_output == input_path.resolve():
            raise InputError(f"--output must differ from {option}")


def atomic_write_text(path: Path, content: str, force: bool) -> None:
    """Publish completed text atomically, leaving no partial destination file."""
    ensure_output_available(path, force)
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if force:
            os.replace(temporary_path, path)
            temporary_path = None
        else:
            try:
                os.link(temporary_path, path)
            except FileExistsError as exc:
                raise InputError(
                    f"output appeared during writing and was not overwritten: {path}"
                ) from exc
    except InputError:
        raise
    except OSError as exc:
        raise InputError(f"could not write output {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def build_parser() -> MinimalArgumentParser:
    template = (
        "parse_tm_topology.py --input <topology_file> --format <source_format> "
        "--fasta <single_record_fasta> --output <topology_json> [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Parse one DeepTMHMM or Phyre 2.2 topology source into validated, "
            "1-based-inclusive JSON. Sources are never compared or merged."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "可用格式：\n"
            "  deeptmhmm-gff3    approved 8-column DeepTMHMM export\n"
            "  phyre2-memsat-svm final MEMSAT-SVM Results block\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--input", required=True, type=Path, help="topology source file")
    required.add_argument(
        "--format", required=True, choices=SOURCE_FORMATS, help="explicit source format"
    )
    required.add_argument(
        "--fasta", required=True, type=Path, help="corresponding single-record FASTA"
    )
    required.add_argument("--output", required=True, type=Path, help="output JSON path")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_path = args.input.expanduser()
    fasta_path = args.fasta.expanduser()
    output_path = args.output.expanduser()
    try:
        ensure_distinct_output(
            output_path,
            (("--input", input_path), ("--fasta", fasta_path)),
        )
        ensure_output_available(output_path, args.force)
        fasta_id, sequence = read_single_fasta(fasta_path)
        parsed = (
            parse_deeptmhmm_gff3(input_path)
            if args.format == "deeptmhmm-gff3"
            else parse_phyre2_memsat_svm(input_path)
        )
        data = {
            "source_format": args.format,
            "source_file": str(input_path.resolve()),
            "fasta_id": fasta_id,
            "sequence_length": len(sequence),
            "coordinate_system": COORDINATE_SYSTEM,
            **parsed,
        }
        validate_topology_json(data, source=str(input_path))
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        atomic_write_text(output_path, content, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "跨膜拓扑 JSON")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
