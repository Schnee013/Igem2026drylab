#!/usr/bin/env python3
"""Run one pinned DeepMind AlphaFold 2 Amber relaxation protocol."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


PROTOCOL_ID = "deepmind-af2-c77e5d2-openmm8.2-cpu/v1"
REPORT_SCHEMA = "af2-amber-relax-report/v1"
SELF_CHECK_SCHEMA = "af2-amber-relax-self-check/v1"
ALPHAFOLD_COMMIT = "c77e5d2a8961d1a353632c462914ff0a32a950f6"
ALPHAFOLD_RUNTIME_DISTRIBUTION = "docking-af2-runtime"
ALPHAFOLD_RUNTIME_VERSION = "0.1.0+c77e5d2"
RUNTIME_MANIFEST_FILENAME = "docking_runtime_manifest.json"
RUNTIME_MANIFEST_SCHEMA = "docking-af2-runtime-manifest/v1"
AMBER99SB_SHA256 = "186f8570413f2ad3efe923578fc53cc895006d50de4b612e9fc58977a914c092"
STEREO_CHEMICAL_PROPS_SHA256 = (
    "24510899eeb49167cffedec8fa45363a4d08279c0c637a403b452f7d0ac09451"
)

MAX_ITERATIONS = 0
FORCE_TOLERANCE = 2.39
STIFFNESS = 10.0
MAX_OUTER_ITERATIONS = 3
MAX_ATTEMPTS_PER_OUTER_ITERATION = 100
EXCLUDE_RESIDUES: tuple[int, ...] = ()

STANDARD_RESIDUES = frozenset(
    {
        "ALA",
        "ARG",
        "ASN",
        "ASP",
        "CYS",
        "GLN",
        "GLU",
        "GLY",
        "HIS",
        "ILE",
        "LEU",
        "LYS",
        "MET",
        "PHE",
        "PRO",
        "SER",
        "THR",
        "TRP",
        "TYR",
        "VAL",
    }
)


class EngineError(RuntimeError):
    """The pinned runtime, input, or AF2 relaxation result is invalid."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise EngineError(f"could not hash {path}: {exc}") from exc
    return digest.hexdigest()


def _distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError as exc:
        raise EngineError(f"required Python package is missing: {name}") from exc


def _load_runtime_manifest() -> tuple[Path, dict[str, Any]]:
    """Locate the installed AlphaFold package and verify its wheel manifest."""

    runtime_version = _distribution_version(ALPHAFOLD_RUNTIME_DISTRIBUTION)
    if runtime_version != ALPHAFOLD_RUNTIME_VERSION:
        raise EngineError(
            "AF2 runtime version mismatch: expected "
            f"{ALPHAFOLD_RUNTIME_VERSION}, found {runtime_version}"
        )

    spec = importlib.util.find_spec("alphafold")
    if spec is None or spec.origin is None:
        raise EngineError(
            "the alphafold package supplied by docking-af2-runtime is not importable"
        )
    package_root = Path(spec.origin).resolve().parent
    manifest_path = package_root / RUNTIME_MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise EngineError(f"AF2 runtime manifest is missing: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EngineError(f"could not read AF2 runtime manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise EngineError("AF2 runtime manifest must be a JSON object")
    expected_fields = {
        "schema": RUNTIME_MANIFEST_SCHEMA,
        "distribution": ALPHAFOLD_RUNTIME_DISTRIBUTION,
        "version": ALPHAFOLD_RUNTIME_VERSION,
        "upstream_commit": ALPHAFOLD_COMMIT,
    }
    for key, expected in expected_fields.items():
        if manifest.get(key) != expected:
            raise EngineError(
                f"AF2 runtime manifest {key} mismatch: expected {expected!r}, "
                f"found {manifest.get(key)!r}"
            )

    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise EngineError("AF2 runtime manifest has no packaged-file hashes")
    for relative_name, expected_hash in sorted(files.items()):
        if not isinstance(relative_name, str) or not isinstance(expected_hash, str):
            raise EngineError("AF2 runtime manifest contains an invalid file hash entry")
        relative_path = Path(relative_name)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise EngineError(
                f"AF2 runtime manifest contains an unsafe path: {relative_name!r}"
            )
        packaged_path = package_root / relative_path
        if not packaged_path.is_file():
            raise EngineError(f"AF2 runtime file is missing: {packaged_path}")
        actual_hash = _sha256_file(packaged_path)
        if actual_hash != expected_hash:
            raise EngineError(
                f"AF2 runtime file hash mismatch for {relative_name}: "
                f"expected {expected_hash}, found {actual_hash}"
            )
    return package_root, manifest


def inspect_runtime() -> dict[str, Any]:
    """Verify the exact executable code and data selected by the protocol."""

    if sys.version_info[:2] != (3, 11):
        raise EngineError(
            "protocol requires Python 3.11; found " + platform.python_version()
        )

    source_root, runtime_manifest = _load_runtime_manifest()
    source_commit = str(runtime_manifest["upstream_commit"])

    installed_versions = {
        name: _distribution_version(name)
        for name in (
            "absl-py",
            "biopython",
            "dm-haiku",
            "jax",
            "jaxlib",
            "ml-collections",
            "numpy",
            "openmm",
            "pdbfixer",
        )
    }
    exact_versions = {
        "absl-py": "1.0.0",
        "biopython": "1.87",
        "dm-haiku": "0.0.12",
        "jax": "0.4.26",
        "ml-collections": "0.1.0",
        "numpy": "1.26.4",
        "openmm": "8.2.0",
    }
    for name, expected in exact_versions.items():
        found = installed_versions[name]
        if found != expected:
            raise EngineError(
                f"{name} version mismatch: expected {expected}, found {found}"
            )
    pdbfixer_version = installed_versions["pdbfixer"]
    if pdbfixer_version not in {"1.12", "1.12.0"}:
        raise EngineError(
            f"PDBFixer version mismatch: expected 1.12.0, found {pdbfixer_version}"
        )
    jaxlib_version = installed_versions["jaxlib"]
    if not jaxlib_version.startswith("0.4.26"):
        raise EngineError(
            "JAXLIB version mismatch: expected a 0.4.26 build, "
            f"found {jaxlib_version}"
        )

    try:
        import jax
        import openmm
        from openmm import app as openmm_app
        from alphafold.relax.relax import AmberRelaxation
    except Exception as exc:  # scientific runtime can fail for ABI reasons
        raise EngineError(f"could not import the AF2 relax runtime: {exc}") from exc

    amber_path = Path(openmm_app.__file__).resolve().parent / "data" / "amber99sb.xml"
    stereo_path = source_root / "common" / "stereo_chemical_props.txt"
    if not amber_path.is_file():
        raise EngineError(f"OpenMM Amber99SB data file is missing: {amber_path}")
    if not stereo_path.is_file():
        raise EngineError(
            f"AlphaFold stereochemical parameter file is missing: {stereo_path}"
        )
    amber_hash = _sha256_file(amber_path)
    stereo_hash = _sha256_file(stereo_path)
    if amber_hash != AMBER99SB_SHA256:
        raise EngineError(
            "amber99sb.xml hash mismatch: "
            f"expected {AMBER99SB_SHA256}, found {amber_hash}"
        )
    if stereo_hash != STEREO_CHEMICAL_PROPS_SHA256:
        raise EngineError(
            "stereo_chemical_props.txt hash mismatch: "
            f"expected {STEREO_CHEMICAL_PROPS_SHA256}, found {stereo_hash}"
        )

    try:
        platforms = [
            openmm.Platform.getPlatform(index).getName()
            for index in range(openmm.Platform.getNumPlatforms())
        ]
        cpu_platform = openmm.Platform.getPlatformByName("CPU")
        cpu_default_properties = {
            name: cpu_platform.getPropertyDefaultValue(name)
            for name in cpu_platform.getPropertyNames()
        }
        jax_cpu_devices = [str(device) for device in jax.local_devices(backend="cpu")]
        if not jax_cpu_devices:
            raise EngineError("JAX did not expose a CPU device")
        # This validates the same OpenMM data-name lookup used by DeepMind.
        openmm_app.ForceField("amber99sb.xml")
    except EngineError:
        raise
    except Exception as exc:
        raise EngineError(f"CPU relax backend self-check failed: {exc}") from exc

    return {
        "schema": SELF_CHECK_SCHEMA,
        "status": "ok",
        "protocol_id": PROTOCOL_ID,
        "runtime": {
            "python": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "environment_prefix": str(Path(sys.prefix).resolve()),
            "system": platform.system(),
            "machine": platform.machine(),
            "alphafold_commit": source_commit,
            "alphafold_runtime": _distribution_version(
                ALPHAFOLD_RUNTIME_DISTRIBUTION
            ),
            "openmm": installed_versions["openmm"],
            "openmm_runtime": getattr(openmm, "__version__", "unknown"),
            "pdbfixer": pdbfixer_version,
            "jax": installed_versions["jax"],
            "jaxlib": jaxlib_version,
            "numpy": installed_versions["numpy"],
            "biopython": installed_versions["biopython"],
            "dm-haiku": installed_versions["dm-haiku"],
            "ml-collections": installed_versions["ml-collections"],
            "absl-py": installed_versions["absl-py"],
            "platform": "CPU",
            "available_openmm_platforms": platforms,
            "openmm_cpu_default_properties": cpu_default_properties,
            "jax_cpu_devices": jax_cpu_devices,
        },
        "source": {
            "root": str(source_root.resolve()),
            "commit": source_commit,
            "distribution": ALPHAFOLD_RUNTIME_DISTRIBUTION,
            "distribution_version": ALPHAFOLD_RUNTIME_VERSION,
            "manifest_schema": RUNTIME_MANIFEST_SCHEMA,
            "verified_packaged_files": len(runtime_manifest["files"]),
            "integrity": "wheel manifest hashes verified",
        },
        "force_field": {
            "name": "amber99sb.xml",
            "path": str(amber_path),
            "size_bytes": amber_path.stat().st_size,
            "sha256": amber_hash,
        },
        "stereochemical_parameters": {
            "path": str(stereo_path.resolve()),
            "size_bytes": stereo_path.stat().st_size,
            "sha256": stereo_hash,
        },
        "implementation": AmberRelaxation.__name__,
    }


def _self_check_payload() -> tuple[dict[str, Any], int]:
    try:
        return inspect_runtime(), 0
    except EngineError as exc:
        return {
            "schema": SELF_CHECK_SCHEMA,
            "status": "failed",
            "protocol_id": PROTOCOL_ID,
            "errors": [str(exc)],
        }, 1


def preflight_pdb(path: Path, pdb_bytes: bytes) -> dict[str, Any]:
    """Reject content that DeepMind cleanup would otherwise silently discard."""

    if path.suffix.lower() != ".pdb":
        raise EngineError("input must be a .pdb file")
    try:
        pdb_text = pdb_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EngineError(f"input PDB is not valid UTF-8/ASCII text: {exc}") from exc

    lines = pdb_text.splitlines()
    model_lines = [line for line in lines if line[:6].strip().upper() == "MODEL"]
    end_model_lines = [line for line in lines if line[:6].strip().upper() == "ENDMDL"]
    if len(model_lines) > 1:
        raise EngineError(
            f"input PDB contains {len(model_lines)} MODEL records; exactly one model is allowed"
        )
    if end_model_lines and not model_lines:
        raise EngineError("input PDB contains ENDMDL without a MODEL record")
    if len(end_model_lines) > 1:
        raise EngineError("input PDB contains more than one ENDMDL record")

    heterogens = [line for line in lines if line[:6].strip().upper() == "HETATM"]
    if heterogens:
        first = heterogens[0]
        residue = first[17:20].strip() if len(first) >= 20 else "unknown"
        raise EngineError(
            "input must be protein-only: found "
            f"{len(heterogens)} HETATM record(s), first residue {residue!r}"
        )

    residues: set[tuple[str, int, str]] = set()
    atoms: set[tuple[str, int, str, str]] = set()
    residues_by_chain: dict[str, set[tuple[int, str]]] = defaultdict(set)
    atom_count = 0
    hydrogen_count = 0
    for line_number, line in enumerate(lines, start=1):
        if line[:6].strip().upper() != "ATOM":
            continue
        if len(line) < 54:
            raise EngineError(f"ATOM record on line {line_number} is too short")
        alternate_location = line[16].strip()
        if alternate_location:
            raise EngineError(
                f"alternate atom location {alternate_location!r} on line {line_number} is unsupported"
            )
        insertion_code = line[26].strip()
        if insertion_code:
            raise EngineError(
                f"insertion code {insertion_code!r} on line {line_number} is unsupported"
            )
        residue_name = line[17:20].strip().upper()
        if residue_name not in STANDARD_RESIDUES:
            raise EngineError(
                f"non-standard protein residue {residue_name!r} on line {line_number} is unsupported"
            )
        try:
            residue_number = int(line[22:26])
            coordinates = tuple(float(line[start : start + 8]) for start in (30, 38, 46))
        except ValueError as exc:
            raise EngineError(
                f"invalid residue number or coordinates on line {line_number}"
            ) from exc
        if not all(math.isfinite(value) for value in coordinates):
            raise EngineError(f"non-finite coordinates on line {line_number}")
        chain_id = line[21]
        atom_name = line[12:16].strip().upper()
        if not atom_name:
            raise EngineError(f"missing atom name on line {line_number}")
        atom_key = (chain_id, residue_number, residue_name, atom_name)
        if atom_key in atoms:
            raise EngineError(
                "duplicate atom identity on line "
                f"{line_number}: chain {chain_id!r}, residue {residue_number}, atom {atom_name}"
            )
        atoms.add(atom_key)
        residues.add((chain_id, residue_number, residue_name))
        residues_by_chain[chain_id].add((residue_number, residue_name))
        atom_count += 1
        element = line[76:78].strip().upper() if len(line) >= 78 else ""
        if element == "H" or (not element and atom_name.startswith("H")):
            hydrogen_count += 1

    if atom_count == 0:
        raise EngineError("input PDB contains no ATOM records")
    short_chains = [
        chain_id for chain_id, chain_residues in residues_by_chain.items()
        if len(chain_residues) < 2
    ]
    if short_chains:
        display = ", ".join(repr(chain_id) for chain_id in short_chains)
        raise EngineError(
            "each protein chain must contain at least two residues; short chain(s): "
            + display
        )

    return {
        "model_count": 1,
        "chain_count": len(residues_by_chain),
        "residue_count": len(residues),
        "atom_record_count": atom_count,
        "hydrogen_atom_record_count": hydrogen_count,
        "hetero_atom_record_count": 0,
        "alternate_location_count": 0,
        "insertion_code_count": 0,
        "standard_residues_only": True,
    }


def _finite_float(value: Any, label: str) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise EngineError(f"AF2 returned a non-numeric {label}: {value!r}") from exc
    if not math.isfinite(converted):
        raise EngineError(f"AF2 returned a non-finite {label}: {converted!r}")
    return converted


def _ensure_output_target(path: Path, label: str) -> None:
    if path.exists():
        raise EngineError(f"{label} already exists: {path}")
    if not path.parent.is_dir():
        raise EngineError(f"{label} parent directory does not exist: {path.parent}")


def run_relaxation(
    *,
    input_pdb: Path,
    output_pdb: Path,
    report_json: Path,
    published_output_pdb: Path,
) -> None:
    runtime = inspect_runtime()
    if not input_pdb.is_file():
        raise EngineError(f"input PDB does not exist or is not a file: {input_pdb}")
    if output_pdb.resolve() == report_json.resolve():
        raise EngineError("output PDB and report JSON paths must differ")
    if input_pdb.resolve() in {output_pdb.resolve(), report_json.resolve()}:
        raise EngineError("engine outputs must differ from the input PDB")
    _ensure_output_target(output_pdb, "output PDB")
    _ensure_output_target(report_json, "report JSON")
    try:
        input_bytes = input_pdb.read_bytes()
    except OSError as exc:
        raise EngineError(f"could not read input PDB {input_pdb}: {exc}") from exc
    preflight = preflight_pdb(input_pdb, input_bytes)
    pdb_text = input_bytes.decode("utf-8")

    try:
        from absl import logging as absl_logging
        from alphafold.common import protein
        from alphafold.relax import relax

        absl_logging.set_verbosity(absl_logging.INFO)
        prot = protein.from_pdb_string(pdb_text)
        if len(prot.residue_index) != preflight["residue_count"]:
            raise EngineError(
                "AlphaFold parser did not retain every preflighted residue; input is unsupported"
            )
        relaxer = relax.AmberRelaxation(
            max_iterations=MAX_ITERATIONS,
            tolerance=FORCE_TOLERANCE,
            stiffness=STIFFNESS,
            exclude_residues=EXCLUDE_RESIDUES,
            max_outer_iterations=MAX_OUTER_ITERATIONS,
            use_gpu=False,
        )
        print(
            "Starting pinned DeepMind AF2 Amber relaxation on OpenMM CPU "
            f"({preflight['residue_count']} residues)",
            flush=True,
        )
        started = time.monotonic()
        relaxed_pdb, debug_data, violations = relaxer.process(prot=prot)
        elapsed_seconds = time.monotonic() - started
    except EngineError:
        raise
    except Exception as exc:
        raise EngineError(f"DeepMind AF2 Amber relaxation failed: {exc}") from exc

    output_bytes = relaxed_pdb.encode("utf-8")
    violation_mask = [
        _finite_float(value, "remaining violation mask value") for value in violations
    ]
    report = {
        "schema": REPORT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_scope": (
            "DeepMind AF2 c77e5d2 preset; not a ColabFold 1.6.2 source-match"
        ),
        "input": {
            "path": str(input_pdb.resolve()),
            "size_bytes": len(input_bytes),
            "sha256": _sha256_bytes(input_bytes),
            "preflight": preflight,
        },
        "output": {
            "path": str(published_output_pdb.resolve()),
            "size_bytes": len(output_bytes),
            "sha256": _sha256_bytes(output_bytes),
        },
        "runtime": runtime["runtime"],
        "source": runtime["source"],
        "force_field": runtime["force_field"],
        "stereochemical_parameters": runtime["stereochemical_parameters"],
        "parameters": {
            "constraints": "HBonds",
            "restraint_set": "non_hydrogen",
            "stiffness_kcal_per_mol_a2": STIFFNESS,
            "force_tolerance_kcal_per_mol_nm": FORCE_TOLERANCE,
            "max_iterations": MAX_ITERATIONS,
            "max_outer_iterations": MAX_OUTER_ITERATIONS,
            "max_attempts_per_outer_iteration": MAX_ATTEMPTS_PER_OUTER_ITERATION,
            "initial_exclude_residues": list(EXCLUDE_RESIDUES),
            "platform": "CPU",
            "random_seed": None,
            "pdbfixer_missing_atom_seed": 0,
        },
        "result": {
            "initial_potential_energy_kcal_per_mol": _finite_float(
                debug_data.get("initial_energy"), "initial potential energy"
            ),
            "final_potential_energy_kcal_per_mol": _finite_float(
                debug_data.get("final_energy"), "final potential energy"
            ),
            "af2_internal_rmsd_angstrom": _finite_float(
                debug_data.get("rmsd"), "AF2 internal RMSD"
            ),
            "final_iteration_attempts": int(debug_data.get("attempts")),
            "remaining_violation_count": int(sum(violation_mask)),
            "remaining_violation_mask": violation_mask,
            "elapsed_seconds": elapsed_seconds,
        },
    }
    try:
        report_bytes = (
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
            + "\n"
        ).encode("utf-8")
        with output_pdb.open("xb") as handle:
            handle.write(output_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        with report_json.open("xb") as handle:
            handle.write(report_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except (OSError, TypeError, ValueError) as exc:
        raise EngineError(f"could not write staged AF2 relax outputs: {exc}") from exc
    print(f"Wrote staged relaxed PDB: {output_pdb}", flush=True)
    print(f"Wrote staged AF2 relax report: {report_json}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Internal scientific engine for the pinned DeepMind AF2 Amber relax "
            "protocol. Normal users should call run_restrained_minimization.py."
        )
    )
    parser.add_argument("--self-check", action="store_true", help="verify runtime identity and exit")
    parser.add_argument("--protocol", choices=(PROTOCOL_ID,))
    parser.add_argument("--input-pdb", type=Path)
    parser.add_argument("--output-pdb", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument(
        "--published-output-pdb",
        type=Path,
        help="logical final PDB path recorded in the staged report",
    )
    return parser


def self_check_main() -> int:
    """Console entry point for installation and GUI runtime checks."""

    payload, return_code = _self_check_payload()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return return_code


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_check:
        supplied_run_args = any(
            value is not None
            for value in (
                args.protocol,
                args.input_pdb,
                args.output_pdb,
                args.report_json,
                args.published_output_pdb,
            )
        )
        if supplied_run_args:
            parser.error("--self-check cannot be combined with relaxation inputs")
        return self_check_main()

    missing = [
        option
        for option, value in (
            ("--protocol", args.protocol),
            ("--input-pdb", args.input_pdb),
            ("--output-pdb", args.output_pdb),
            ("--report-json", args.report_json),
        )
        if value is None
    ]
    if missing:
        parser.error("relaxation mode requires " + ", ".join(missing))
    assert args.input_pdb is not None
    assert args.output_pdb is not None
    assert args.report_json is not None
    published_output = args.published_output_pdb or args.output_pdb
    try:
        run_relaxation(
            input_pdb=args.input_pdb.expanduser(),
            output_pdb=args.output_pdb.expanduser(),
            report_json=args.report_json.expanduser(),
            published_output_pdb=published_output.expanduser(),
        )
    except EngineError as exc:
        print(f"Error: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
