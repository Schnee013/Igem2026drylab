#!/usr/bin/env python3
"""Report drylab payload tracking policy issues without modifying the repo."""

from __future__ import annotations

import argparse
import csv
import fnmatch
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_TRACKED = [
    ("experiments/md-simulation/**/index.fixed.ndx", "generated repaired index body"),
    ("experiments/md-simulation/results/**/raw/**", "MD raw result payload"),
    ("experiments/md-simulation/results/**/processed/**", "MD processed trajectory payload"),
    ("experiments/md-simulation/results/**/processed_*/*", "MD processed trajectory payload"),
    ("experiments/md-simulation/results/**/production_smoke/**", "MD runtime smoke payload"),
    ("experiments/md-simulation/results/**/input/gromacs/**", "copied runtime input package"),
    ("experiments/md-simulation/results/**/hostname.txt", "remote machine-state artifact"),
    ("experiments/md-simulation/results/**/whoami.txt", "remote machine-state artifact"),
    ("experiments/md-simulation/results/**/pwd.txt", "remote machine-state artifact"),
    ("experiments/md-simulation/results/**/run_*_time.txt", "remote run timestamp artifact"),
    ("experiments/md-simulation/results/**/mdrun_start_time.txt", "remote run timestamp artifact"),
    ("experiments/md-simulation/systems/**/receptor/clean_receptor.pdb", "generated receptor payload"),
    ("experiments/md-simulation/systems/**/receptor/ppm_submission/*.pdb", "PPM submission copy"),
    ("experiments/md-simulation/systems/**/receptor/ppm_submission/output/*.pdb", "PPM output payload"),
    ("experiments/md-simulation/systems/**/gromacs/*_coordinate_completion/*.gro", "coordinate-completion payload"),
    ("experiments/md-simulation/systems/**/gromacs/*_coordinate_completion/*.pdb", "coordinate-completion payload"),
    ("experiments/md-simulation/systems/**/gromacs/source_archives/**", "local CHARMM-GUI/source archive"),
    ("experiments/md-simulation/systems/**/gromacs/charmm_gui_returned/**", "CHARMM-GUI returned package"),
    ("experiments/md-simulation/systems/**/gromacs/returned_package/**", "returned package payload"),
    ("experiments/md-simulation/systems/**/gromacs/charmm-gui-*.tgz", "CHARMM-GUI archive"),
    ("experiments/md-simulation/systems/**/gromacs/charmm_gui_*.tgz", "CHARMM-GUI archive"),
    ("experiments/chimeric-gpa1/literature/source_attachments/*.pdf", "local literature source binary"),
    ("experiments/chimeric-gpa1/literature/source_attachments/*.zip", "local literature source binary"),
    ("experiments/chimeric-gpa1/literature/research_runs/**", "literature research run state"),
    ("docs/papers/pdf/**", "local paper PDF body"),
]

CANONICAL_PAYLOAD_ALLOWLIST = {
    "experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/"
    "ascr3_coordinate_completion/ASCR3_pose_completed.gro",
}

# These tables contain the word ``manifest`` but are not row-per-payload
# manifests: one is a mixed remote/source pin ledger and one is a future gate
# field template. Applying the payload-body schema would invent path, size, and
# recovery semantics that the tables do not claim.
NON_PAYLOAD_MANIFEST_TABLES = {
    "experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv",
    "experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/"
    "prototype_manifest_template.tsv",
}

RECOMMENDED_MANIFEST_COLUMNS = {
    "path",
    "role",
    "owner",
    "tracked_policy",
    "bytes",
    "sha256",
    "storage_location",
    "producer",
    "consumer",
    "stage",
    "required_for",
    "recovery_pointer",
}


def git_lines(*args: str, nul: bool = False) -> list[str]:
    cmd = ["git", *args]
    result = subprocess.run(cmd, cwd=ROOT, text=not nul, capture_output=True, check=True)
    if nul:
        raw = result.stdout
        if isinstance(raw, bytes):
            return [p.decode() for p in raw.split(b"\0") if p]
        return [p for p in raw.split("\0") if p]
    return [line for line in result.stdout.splitlines() if line]


def matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def check_forbidden_tracked(tracked: list[str]) -> list[str]:
    errors: list[str] = []
    for path in tracked:
        if path in CANONICAL_PAYLOAD_ALLOWLIST:
            continue
        for pattern, reason in FORBIDDEN_TRACKED:
            if matches(path, pattern):
                errors.append(f"{path}\t{reason}\tpattern={pattern}")
                break
    return errors


def check_tracked_ignored() -> list[str]:
    # This is intentionally kept as a separate Git-native check because it
    # catches already-tracked files that current ignore rules classify as local.
    return git_lines("ls-files", "-ci", "--exclude-standard")


def candidate_manifests(paths: list[str]) -> list[str]:
    selected = []
    for path in paths:
        if path in NON_PAYLOAD_MANIFEST_TABLES:
            continue
        name = Path(path).name
        if name.endswith(".tsv") and "manifest" in name:
            selected.append(path)
        elif name == "source_files.sha256" or name.endswith(".sha256"):
            selected.append(path)
    return selected


def read_tsv_header(path: Path) -> list[str] | None:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            return next(reader, None)
    except (OSError, UnicodeDecodeError):
        return None


def check_manifest_schema(paths: list[str], strict_schema: bool) -> list[str]:
    warnings: list[str] = []
    for rel in candidate_manifests(paths):
        path = ROOT / rel
        if not path.exists() or path.suffix != ".tsv":
            continue
        header = read_tsv_header(path)
        if not header:
            warnings.append(f"{rel}\tempty or unreadable TSV manifest")
            continue
        cols = set(header)
        if "sha256" not in cols:
            warnings.append(f"{rel}\tmanifest lacks sha256 column")
        if strict_schema:
            missing = sorted(RECOMMENDED_MANIFEST_COLUMNS - cols)
            if missing:
                warnings.append(f"{rel}\tmissing recommended columns: {','.join(missing)}")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict-schema",
        action="store_true",
        help="warn when TSV manifests do not include the full recommended schema",
    )
    args = parser.parse_args()

    tracked = git_lines("ls-files")
    visible_untracked = git_lines("ls-files", "--others", "--exclude-standard")

    errors = []
    errors.extend(check_forbidden_tracked(tracked))
    errors.extend(f"tracked ignored by current .gitignore: {p}" for p in check_tracked_ignored())

    warnings = check_manifest_schema(tracked + visible_untracked, args.strict_schema)

    if errors:
        print("Payload tracking policy errors:")
        for item in errors:
            print(f"ERROR\t{item}")
    else:
        print("No payload tracking policy errors found.")

    if warnings:
        print("\nManifest/schema warnings:")
        for item in warnings:
            print(f"WARN\t{item}")

    print("\nChecked files:")
    print(f"tracked={len(tracked)}")
    print(f"visible_untracked={len(visible_untracked)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
