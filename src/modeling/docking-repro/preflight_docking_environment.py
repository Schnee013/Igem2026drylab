"""Record the local docking toolchain without installing or changing anything."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import (
    ENVIRONMENT_MANIFEST_SCHEMA,
    verify_frame_run_manifest,
)
from frame_alignment import canonical_json_bytes, sha256_file, write_canonical_json
from utils import load_config


def command_version(candidates: list[Path | str], args: list[str]) -> dict:
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            continue
        result = subprocess.run(
            [str(path), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = "\n".join(
            part.strip() for part in (result.stdout, result.stderr) if part.strip()
        )
        return {
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
            "returncode": result.returncode,
            "version_output": output,
        }
    return {"path": None, "sha256": None, "returncode": None, "version_output": None}


def extract_semver(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r"(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else None


def conda_package_record(name: str) -> dict:
    """Return the exact conda package identity for the active prefix.

    Some upstream CLIs embed a different upstream version string (OpenBabel)
    or only a git revision (Vina).  The resolved conda record is therefore the
    version/build authority, while CLI output and executable hashes remain
    independently recorded.
    """
    metadata_dir = Path(sys.prefix) / "conda-meta"
    matches = sorted(metadata_dir.glob(f"{name}-*.json"))
    if len(matches) != 1:
        return {
            "name": name,
            "version": None,
            "build": None,
            "build_number": None,
            "channel": None,
            "filename": None,
            "record_path": None,
            "record_sha256": None,
            "match_count": len(matches),
        }
    record_path = matches[0]
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    return {
        "name": payload.get("name"),
        "version": payload.get("version"),
        "build": payload.get("build") or payload.get("build_string"),
        "build_number": payload.get("build_number"),
        "channel": payload.get("channel"),
        "filename": payload.get("fn"),
        "record_path": str(record_path.resolve()),
        "record_sha256": sha256_file(record_path),
        "match_count": 1,
    }


def text_file_record(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "text": text,
    }


def extract_adfr_build(text: str) -> str | None:
    match = re.search(r"\bBUILD\s+(\d+)\b", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    frame_run_root = Path(args.frame_run_root).resolve()
    run_manifest_path = frame_run_root / "run_manifest.json"
    if not run_manifest_path.is_file():
        raise FileNotFoundError(f"缺少 frame run manifest: {run_manifest_path}")
    run_manifest = verify_frame_run_manifest(
        run_manifest_path, verify_records=True
    )

    target = config["frame_repair"]["target_toolchain"]
    bin_dir = Path(sys.executable).resolve().parent
    adfr_runtime_root = Path(target["adfr_runtime_root"])
    vina = command_version(
        [bin_dir / "vina", shutil.which("vina") or ""],
        ["--version"],
    )
    openbabel = command_version(
        [bin_dir / "obabel", shutil.which("obabel") or ""],
        ["-V"],
    )
    adfr = command_version(
        [
            adfr_runtime_root / "bin" / "prepare_receptor",
            bin_dir / "prepare_receptor",
            bin_dir / "prepare_receptor4.py",
            shutil.which("prepare_receptor") or "",
            shutil.which("prepare_receptor4.py") or "",
        ],
        ["--help"],
    )
    vina_package = conda_package_record("vina")
    openbabel_package = conda_package_record("openbabel")
    adfr_version_file = text_file_record(Path(target["adfr_version_file"]))
    adfr_release_notes = text_file_record(Path(target["adfr_release_notes"]))
    adfr_installer = Path(target["adfr_installer"])
    adfr_installer_record = {
        "path": str(adfr_installer.resolve()),
        "sha256": sha256_file(adfr_installer),
        "official_url": target["adfr_official_url"],
    }
    adfr_version = adfr_version_file["text"].splitlines()[0].strip()
    adfr_build = extract_adfr_build(adfr_release_notes["text"])
    observed = {
        "vina_cli": extract_semver(vina["version_output"]),
        "vina_python_distribution": package_version("vina"),
        "vina_conda_package": vina_package["version"],
        "openbabel_cli": extract_semver(openbabel["version_output"]),
        "openbabel_conda_package": openbabel_package["version"],
        "adfr_prepare_receptor": adfr_version if adfr["path"] else None,
        "adfr_suite_build": adfr_build if adfr["path"] else None,
    }
    compute_contract = {
        "cpu_per_job": int(
            config["frame_repair"]["compute"]["cpu_per_job"]
        ),
        "requested_max_modes": int(config["vina"]["num_modes"]),
        "energy_range": float(config["vina"]["energy_range"]),
        "min_rmsd": float(config["vina"]["min_rmsd"]),
        "max_evals": int(config["vina"]["max_evals"]),
    }
    checks = {
        "vina_conda_package_matches_target": (
            vina_package["version"] == target["vina"]
            and vina_package["match_count"] == 1
            and observed["vina_python_distribution"] == target["vina"]
        ),
        "openbabel_conda_package_matches_target": (
            openbabel_package["version"] == target["openbabel"]
            and openbabel_package["match_count"] == 1
        ),
        "adfr_available_and_version_locked": bool(adfr["path"])
        and isinstance(target.get("adfr"), str)
        and bool(target["adfr"])
        and observed["adfr_prepare_receptor"] == target["adfr"]
        and observed["adfr_suite_build"] == str(target["adfr_build"])
        and adfr_installer_record["sha256"] == target["adfr_installer_sha256"],
        "host_supports_cpu_contract": (
            (__import__("os").cpu_count() or 0)
            >= compute_contract["cpu_per_job"]
        ),
    }
    payload = {
        "schema": ENVIRONMENT_MANIFEST_SCHEMA,
        "status": (
            "production_ready" if all(checks.values()) else "blocked_toolchain_mismatch"
        ),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpu_count": __import__("os").cpu_count(),
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": platform.python_version(),
        },
        "target_toolchain": target,
        "frame_run": {
            "path": str(run_manifest_path),
            "sha256": sha256_file(run_manifest_path),
            "run_identity": run_manifest["run_identity"],
        },
        "configuration": {
            "path": str(Path(args.config).resolve()),
            "sha256": sha256_file(Path(args.config)),
            "environment_lock": {
                "path": str(
                    (
                        Path(args.config).resolve().parents[3]
                        / config["frame_repair"]["environment_lock"]
                    ).resolve()
                ),
                "sha256": sha256_file(
                    Path(args.config).resolve().parents[3]
                    / config["frame_repair"]["environment_lock"]
                ),
            },
        },
        "observed_versions": observed,
        "compute_contract": compute_contract,
        "package_manager_identities": {
            "vina": vina_package,
            "openbabel": openbabel_package,
        },
        "adfr_suite_identity": {
            "version_file": adfr_version_file,
            "release_notes": adfr_release_notes,
            "installer": adfr_installer_record,
        },
        "executables": {
            "vina": vina,
            "openbabel": openbabel,
            "adfr_prepare_receptor": adfr,
        },
        "analysis_packages": {
            "prolif": package_version("prolif"),
            "rdkit": package_version("rdkit"),
            "MDAnalysis": package_version("MDAnalysis"),
            "pymol": package_version("pymol-open-source")
            or package_version("pymol"),
        },
        "checks": checks,
        "authorization_boundary": {
            "remote_preflight_performed": True,
            "dependencies_installed": True,
            "docking_run_performed": False,
        },
    }
    payload["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    output = frame_run_root / "environment_manifest.json"
    if output.exists():
        raise FileExistsError(
            f"拒绝覆盖既有 environment preflight；请使用新 frame run: {output}"
        )
    write_canonical_json(output, payload)
    print(json.dumps({"path": str(output), **payload}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
