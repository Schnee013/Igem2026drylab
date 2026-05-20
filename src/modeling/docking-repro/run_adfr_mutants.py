"""
在 Windows 上批量运行 ADFR prepare_receptor 处理 AF3 突变体 TM PDB

输入：{mutagenesis_dir}/af3_structures/{RecName}/{Label}_tm.pdb
输出：{mutagenesis_dir}/af3_prepared/{RecName}/{Label}_tm.pdbqt

用法（Windows 端）：
    python run_adfr_mutants.py --project-root D:\\drylab-tools\\workspace
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

_this_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_this_dir))

from utils import get_project_root, load_af3_job_filter, load_config


def resolve_prepare_receptor(adfr_bin: str | None) -> list[str]:
    """Resolve the ADFR prepare_receptor command without assuming a platform path."""
    adfr_bin = adfr_bin or os.environ.get("ADFR_BIN")

    candidates: list[Path | str]
    if adfr_bin:
        base = Path(adfr_bin)
        candidates = [base] if base.name.startswith("prepare_receptor") else [
            base / "prepare_receptor",
            base / "prepare_receptor.bat",
            base / "prepare_receptor4.py",
        ]
    else:
        candidates = [
            shutil.which("prepare_receptor") or "",
            shutil.which("prepare_receptor4.py") or "",
        ]

    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() or isinstance(candidate, str):
            if path.suffix.lower() == ".bat":
                return ["cmd", "/c", str(path)]
            return [str(path)]

    raise FileNotFoundError(
        "未找到 ADFR prepare_receptor。请用 --adfr-bin 指向 ADFR bin 目录或 "
        "prepare_receptor 可执行文件，或设置 ADFR_BIN 环境变量。"
    )


def prepare_one(pdb_path: Path, out_pdbqt: Path, prepare_receptor_cmd: list[str]) -> bool:
    """运行 ADFR prepare_receptor，返回是否成功。"""
    cmd = [
        *prepare_receptor_cmd,
        "-r", str(pdb_path),
        "-o", str(out_pdbqt),
        "-A", "hydrogens",
        "-U", "nphs_lps_waters_nonstdres",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.returncode == 0 and out_pdbqt.exists()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量 ADFR prepare_receptor")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--job-names-file", nargs="+", default=None,
        help="只处理指定 AF3 batch JSON 对应的 TM PDB，可传多个 JSON 文件",
    )
    parser.add_argument(
        "--adfr-bin", default=None,
        help="ADFR bin 目录或 prepare_receptor 可执行文件；默认查 ADFR_BIN 或 PATH",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="允许覆盖已存在的 PDBQT；默认跳过已存在文件",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    mut_dir = root / config["paths"]["mutagenesis_dir"]
    tm_dir = mut_dir / "af3_structures"
    out_base = mut_dir / "af3_prepared"
    job_filter = load_af3_job_filter(args.job_names_file)
    prepare_receptor_cmd = resolve_prepare_receptor(args.adfr_bin)

    pdb_files = sorted(tm_dir.glob("*/*_tm.pdb"))
    if job_filter is not None:
        pdb_files = [
            p for p in pdb_files
            if (p.parent.name, p.stem.removesuffix("_tm").upper()) in job_filter
        ]
    print(f"找到 {len(pdb_files)} 个 TM PDB 文件")
    print(f"prepare_receptor: {' '.join(prepare_receptor_cmd)}")

    ok = 0
    fail = 0
    for pdb in pdb_files:
        rec = pdb.parent.name
        label = pdb.stem  # e.g. N83A_tm
        out_dir = out_base / rec
        out_dir.mkdir(parents=True, exist_ok=True)
        out_pdbqt = out_dir / f"{label}.pdbqt"

        if out_pdbqt.exists() and not args.overwrite:
            print(f"  {rec}/{label}: 已存在，跳过")
            ok += 1
            continue

        success = prepare_one(pdb, out_pdbqt, prepare_receptor_cmd)
        if success:
            print(f"  {rec}/{label}: OK")
            ok += 1
        else:
            print(f"  {rec}/{label}: FAILED")
            fail += 1

    print(f"\n完成: {ok} 成功, {fail} 失败 / {len(pdb_files)} 总计")


if __name__ == "__main__":
    main()
