"""
在 Windows 上批量运行 ADFR prepare_receptor 处理 AF3 突变体 TM PDB

输入：{mutagenesis_dir}/af3_structures/{RecName}/{Label}_tm.pdb
输出：{mutagenesis_dir}/af3_prepared/{RecName}/{Label}_tm.pdbqt

用法（Windows 端）：
    python run_adfr_mutants.py --project-root D:\\drylab-tools\\workspace
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_this_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_this_dir))

from utils import get_project_root, load_config

ADFR_BIN = Path("D:/ADFRsuite/bin")


def prepare_one(pdb_path: Path, out_pdbqt: Path) -> bool:
    """运行 ADFR prepare_receptor，返回是否成功。"""
    adfr_cmd = ADFR_BIN / "prepare_receptor.bat"
    cmd = [
        "cmd", "/c", str(adfr_cmd),
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

    pdb_files = sorted(tm_dir.glob("*/*_tm.pdb"))
    print(f"找到 {len(pdb_files)} 个 TM PDB 文件")

    ok = 0
    fail = 0
    for pdb in pdb_files:
        rec = pdb.parent.name
        label = pdb.stem  # e.g. N83A_tm
        out_dir = out_base / rec
        out_dir.mkdir(parents=True, exist_ok=True)
        out_pdbqt = out_dir / f"{label}.pdbqt"

        if out_pdbqt.exists():
            print(f"  {rec}/{label}: 已存在，跳过")
            ok += 1
            continue

        success = prepare_one(pdb, out_pdbqt)
        if success:
            print(f"  {rec}/{label}: OK")
            ok += 1
        else:
            print(f"  {rec}/{label}: FAILED")
            fail += 1

    print(f"\n完成: {ok} 成功, {fail} 失败 / {len(pdb_files)} 总计")


if __name__ == "__main__":
    main()
