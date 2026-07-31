"""Prepare run-local WT and frame-aligned mutant receptors with locked ADFR."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import (
    create_pdbqt_manifest,
    verify_environment_manifest,
    verify_frame_manifest,
    verify_frame_run_manifest,
)
from utils import load_af3_job_filter, load_config


def prepare_one(
    pdb_path: Path,
    out_pdbqt: Path,
    prepare_receptor_cmd: list[str],
) -> tuple[bool, list[str], str, str]:
    cmd = [
        *prepare_receptor_cmd,
        "-r",
        str(pdb_path),
        "-o",
        str(out_pdbqt),
        "-A",
        "hydrogens",
        "-U",
        "nphs_lps_waters_nonstdres",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return (
        result.returncode == 0 and out_pdbqt.exists(),
        cmd,
        result.stdout,
        result.stderr,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    parser.add_argument(
        "--environment-manifest",
        default=None,
        help="默认 <frame-run-root>/environment_manifest.json",
    )
    parser.add_argument(
        "--job-names-file",
        nargs="+",
        default=None,
        help="可选 AF3 job JSON 过滤；对应受体的 WT 始终包含",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    frame_run_root = Path(args.frame_run_root).resolve()
    verify_frame_run_manifest(
        frame_run_root / "run_manifest.json", verify_records=True
    )
    environment_path = (
        Path(args.environment_manifest).resolve()
        if args.environment_manifest
        else frame_run_root / "environment_manifest.json"
    )
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=frame_run_root,
        require_production_ready=True,
    )
    adfr = environment["executables"]["adfr_prepare_receptor"]
    prepare_receptor_cmd = [adfr["path"]]
    tm_dir = frame_run_root / "aligned_receptors"
    out_base = frame_run_root / "prepared_receptors"
    job_filter = load_af3_job_filter(args.job_names_file)

    pdb_files = sorted(tm_dir.glob("*/*/*_tm.aligned.pdb"))
    if job_filter is not None:
        filtered_receptors = {receptor for receptor, _ in job_filter}
        pdb_files = [
            path
            for path in pdb_files
            if (
                path.parent.name == "WT"
                and path.parents[1].name in filtered_receptors
            )
            or (
                path.parents[1].name,
                path.parent.name.upper(),
            )
            in job_filter
        ]
    allowed_receptors = set(config["frame_repair"]["allowed_receptors"])
    unexpected = sorted({path.parents[1].name for path in pdb_files} - allowed_receptors)
    if unexpected:
        raise ValueError(f"frame repair 不允许的 receptor: {unexpected}")
    if job_filter is None:
        expected = config["frame_repair"]["expected_total_mutants"] + len(
            allowed_receptors
        )
        if len(pdb_files) != expected:
            raise ValueError(
                f"receptor preparation matrix mismatch: "
                f"expected={expected}, actual={len(pdb_files)}"
            )

    print(f"找到 {len(pdb_files)} 个 run-local WT/mutant TM PDB")
    print(
        "prepare_receptor: "
        f"{adfr['path']} sha256={adfr['sha256']} "
        f"version={environment['observed_versions']['adfr_prepare_receptor']}"
    )

    ok = 0
    failures: list[str] = []
    for pdb in pdb_files:
        receptor = pdb.parents[1].name
        subject = pdb.parent.name
        frame_manifest_path = pdb.parent / "frame_manifest.json"
        verify_frame_manifest(
            frame_manifest_path,
            aligned_tm_pdb=pdb,
            expected_receptor=receptor,
            expected_mutation=subject,
        )
        out_dir = out_base / receptor
        out_dir.mkdir(parents=True, exist_ok=True)
        out_pdbqt = out_dir / f"{subject}_tm.pdbqt"
        pdbqt_manifest = out_dir / f"{subject}_tm.pdbqt.manifest.json"
        if out_pdbqt.exists() or pdbqt_manifest.exists():
            raise FileExistsError(
                "拒绝跳过、复用或覆盖既有 receptor preparation；"
                f"请使用新 run root: {out_pdbqt}"
            )

        success, command, stdout, stderr = prepare_one(
            pdb, out_pdbqt, prepare_receptor_cmd
        )
        if not success:
            failures.append(f"{receptor}/{subject}: {stderr.strip()}")
            print(f"  {receptor}/{subject}: FAILED")
            continue
        try:
            create_pdbqt_manifest(
                frame_manifest_path=frame_manifest_path,
                aligned_pdb=pdb,
                pdbqt_path=out_pdbqt,
                output_manifest_path=pdbqt_manifest,
                preparation_command=command,
                environment_manifest_path=environment_path,
            )
        except Exception:
            out_pdbqt.unlink(missing_ok=True)
            pdbqt_manifest.unlink(missing_ok=True)
            raise
        log_path = out_dir / f"{subject}_prepare_receptor.log"
        log_path.write_text(
            f"STDOUT\n{stdout}\nSTDERR\n{stderr}\n",
            encoding="utf-8",
        )
        print(f"  {receptor}/{subject}: OK")
        ok += 1

    print(f"\n完成: {ok} 成功, {len(failures)} 失败 / {len(pdb_files)} 总计")
    if failures:
        raise RuntimeError("ADFR preparation failures:\n" + "\n".join(failures))


if __name__ == "__main__":
    main()
