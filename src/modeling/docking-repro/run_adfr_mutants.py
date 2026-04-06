"""
在 Windows 上批量运行 ADFR prepare_receptor 处理 AF3 突变体 TM PDB

输入：D:/drylab-tools/workspace/experiments/docking-repro/mutagenesis/af3_tm_pdbs/{RecName}/{Label}_tm.pdb
输出：D:/drylab-tools/workspace/experiments/docking-repro/mutagenesis/af3_prepared/{RecName}/{Label}_tm.pdbqt

用法（Windows 端）：
    python run_adfr_mutants.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ADFR_BIN = Path("D:/ADFRsuite/bin")
TM_DIR = Path("D:/drylab-tools/workspace/experiments/docking-repro/mutagenesis/af3_tm_pdbs")
OUT_DIR = Path("D:/drylab-tools/workspace/experiments/docking-repro/mutagenesis/af3_prepared")


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


def main() -> None:
    pdb_files = sorted(TM_DIR.glob("*/*_tm.pdb"))
    print(f"找到 {len(pdb_files)} 个 TM PDB 文件")

    ok = 0
    fail = 0
    for pdb in pdb_files:
        rec = pdb.parent.name
        label = pdb.stem  # e.g. N83A_tm
        out_dir = OUT_DIR / rec
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
