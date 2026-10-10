#!/usr/bin/env python3
"""Build the pinned AlphaFold source package used by Docking AF2 Amber relax."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Sequence


ALPHAFOLD_REPOSITORY = "https://github.com/google-deepmind/alphafold.git"
ALPHAFOLD_COMMIT = "c77e5d2a8961d1a353632c462914ff0a32a950f6"
RUNTIME_DISTRIBUTION = "docking-af2-runtime"
RUNTIME_VERSION = "0.1.0+c77e5d2"
MANIFEST_SCHEMA = "docking-af2-runtime-manifest/v1"
MANIFEST_FILENAME = "docking_runtime_manifest.json"
STEREO_URL = (
    "https://git.scicore.unibas.ch/schwede/openstructure/-/raw/"
    "7102c63615b64735c4941278d92b554ec94415f8/"
    "modules/mol/alg/src/stereo_chemical_props.txt"
)
STEREO_SHA256 = "24510899eeb49167cffedec8fa45363a4d08279c0c637a403b452f7d0ac09451"


class BuildError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run(argv: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise BuildError(f"could not run {argv[0]!r}: {exc}") from exc
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip()
        raise BuildError(f"command failed ({completed.returncode}): {' '.join(argv)}\n{details}")
    return completed


def _verify_source(source_root: Path) -> None:
    if not (source_root / "alphafold").is_dir():
        raise BuildError(f"AlphaFold package directory is missing under {source_root}")
    head = _run(("git", "-C", str(source_root), "rev-parse", "HEAD")).stdout.strip()
    if head != ALPHAFOLD_COMMIT:
        raise BuildError(
            f"AlphaFold commit mismatch: expected {ALPHAFOLD_COMMIT}, found {head}"
        )
    tracked = _run(
        (
            "git",
            "-C",
            str(source_root),
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
        )
    ).stdout.strip()
    if tracked:
        raise BuildError("AlphaFold checkout has modified tracked files:\n" + tracked)


def _obtain_source(source_dir: Path | None, temp_root: Path) -> Path:
    if source_dir is not None:
        source_root = source_dir.expanduser().resolve()
        _verify_source(source_root)
        return source_root
    source_root = temp_root / "alphafold-source"
    _run(
        (
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            ALPHAFOLD_REPOSITORY,
            str(source_root),
        )
    )
    _run(("git", "-C", str(source_root), "checkout", "--detach", ALPHAFOLD_COMMIT))
    _verify_source(source_root)
    return source_root


def _stereo_bytes(source_root: Path) -> bytes:
    local_path = source_root / "alphafold" / "common" / "stereo_chemical_props.txt"
    if local_path.is_file():
        candidate = local_path.read_bytes()
        if _sha256_bytes(candidate) == STEREO_SHA256:
            return candidate
    try:
        with urllib.request.urlopen(STEREO_URL, timeout=60) as response:
            downloaded = response.read()
    except OSError as exc:
        raise BuildError(f"could not download stereochemical parameters: {exc}") from exc
    downloaded_hash = _sha256_bytes(downloaded)
    if downloaded_hash != STEREO_SHA256:
        raise BuildError(
            "stereo_chemical_props.txt hash mismatch: "
            f"expected {STEREO_SHA256}, found {downloaded_hash}"
        )
    return downloaded


def _copy_runtime_tree(source_root: Path, staging_root: Path) -> Path:
    package_root = staging_root / "alphafold"
    shutil.copytree(
        source_root / "alphafold",
        package_root,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )
    stereo_path = package_root / "common" / "stereo_chemical_props.txt"
    stereo_path.write_bytes(_stereo_bytes(source_root))
    return package_root


def _write_manifest(package_root: Path) -> None:
    files = {
        path.relative_to(package_root).as_posix(): _sha256_file(path)
        for path in sorted(package_root.rglob("*"))
        if path.is_file() and path.name != MANIFEST_FILENAME
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "distribution": RUNTIME_DISTRIBUTION,
        "version": RUNTIME_VERSION,
        "upstream_repository": ALPHAFOLD_REPOSITORY,
        "upstream_commit": ALPHAFOLD_COMMIT,
        "stereochemical_parameters": {
            "source": STEREO_URL,
            "sha256": STEREO_SHA256,
        },
        "files": files,
    }
    (package_root / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_build_metadata(source_root: Path, staging_root: Path) -> None:
    shutil.copy2(source_root / "LICENSE", staging_root / "LICENSE")
    pyproject = f'''[build-system]
requires = ["setuptools>=69,<72", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{RUNTIME_DISTRIBUTION}"
version = "{RUNTIME_VERSION}"
description = "Pinned DeepMind AlphaFold 2 source runtime for Docking Amber relax"
requires-python = ">=3.11,<3.12"
license = {{file = "LICENSE"}}
dependencies = [
  "absl-py==1.0.0",
  "biopython==1.87",
  "dm-haiku==0.0.12",
  "jax==0.4.26",
  "ml-collections==0.1.0",
  "numpy==1.26.4",
  "openmm==8.2.0",
  "pdbfixer==1.12.0",
]

[project.urls]
Upstream = "{ALPHAFOLD_REPOSITORY}"

[tool.setuptools.packages.find]
where = ["."]
include = ["alphafold*"]

[tool.setuptools.package-data]
"alphafold" = ["{MANIFEST_FILENAME}"]
"alphafold.common" = ["stereo_chemical_props.txt", "testdata/*.pdb"]
"alphafold.relax" = ["testdata/*.pdb"]
'''
    (staging_root / "pyproject.toml").write_text(pyproject, encoding="utf-8")


def build_runtime(*, output_dir: Path, source_dir: Path | None) -> Path:
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    before = set(output_dir.glob("*.whl"))
    with tempfile.TemporaryDirectory(prefix="docking-af2-runtime-build-") as temp_name:
        temp_root = Path(temp_name)
        source_root = _obtain_source(source_dir, temp_root)
        staging_root = temp_root / "wheel-source"
        staging_root.mkdir()
        package_root = _copy_runtime_tree(source_root, staging_root)
        _write_manifest(package_root)
        _write_build_metadata(source_root, staging_root)
        _run(
            (
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(output_dir),
                str(staging_root),
            )
        )
    created = sorted(set(output_dir.glob("*.whl")) - before)
    if len(created) != 1:
        expected = sorted(output_dir.glob("docking_af2_runtime-*.whl"))
        if not expected:
            raise BuildError("wheel build completed but no runtime wheel was found")
        return expected[-1]
    return created[0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a portable wheel containing the exact AlphaFold source and "
            "stereochemical data required by the Docking AF2 Amber relax protocol."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="wheel output directory (default: ./dist)",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help=(
            "optional existing clean AlphaFold checkout at the pinned commit; "
            "otherwise the builder clones the official repository"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        wheel = build_runtime(output_dir=args.output_dir, source_dir=args.source_dir)
    except BuildError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(wheel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
