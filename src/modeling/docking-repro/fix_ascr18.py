"""
修复 ascr18 配体：从已有的 Orca 优化 PDB 重新运行 ADFR prepare_ligand。

旧版 freeze_terminal_torsions 有 bug：删除了原子（而非仅冻结旋转键），
导致 ascr18 从 23 个重原子被截断到 14 个（ascarylose 糖环丢失）。

本脚本使用修复后的 prepare_ligand.py 重新生成 PDBQT。

用法（Windows）：
    python fix_ascr18.py
    python fix_ascr18.py --project-root D:/drylab-repro
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from prepare_ligand import prepare_ligand_adfr, count_dofs
from utils import get_project_root, load_config, setup_logging, generate_run_id


def main() -> None:
    parser = argparse.ArgumentParser(description="修复 ascr18 配体 PDBQT")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(root / config["paths"]["log_dir"], f"fix_ascr18_{run_id}")

    # 已有的 Orca 优化 PDB
    orca_pdb = root / config["paths"]["orca_dir"] / "ascr18" / "ascr18_optimized.pdb"
    if not orca_pdb.exists():
        logger.error(f"Orca 优化 PDB 不存在: {orca_pdb}")
        sys.exit(1)

    # 备份旧 PDBQT
    prepared_dir = root / config["paths"]["prepared_dir"] / "ligands"
    old_pdbqt = prepared_dir / "ascr18_optimized.pdbqt"
    if old_pdbqt.exists():
        backup = old_pdbqt.with_suffix(".pdbqt.bak_truncated")
        old_pdbqt.rename(backup)
        logger.info(f"旧 PDBQT 备份: {backup}")

    # 重新运行 ADFR prepare_ligand（使用修复后的 freeze_terminal_torsions）
    adfr_bin = config["remote"]["adfr_bin"]
    max_dofs = config["adfr"]["ligand"]["max_dofs"]

    logger.info(f"重新准备 ascr18: {orca_pdb}")
    logger.info(f"  max_dofs={max_dofs}")

    pdbqt = prepare_ligand_adfr(orca_pdb, prepared_dir, adfr_bin, max_dofs)

    # 验证
    n_atoms = sum(1 for line in pdbqt.read_text().splitlines()
                  if line.startswith(("ATOM", "HETATM")))
    n_dofs = count_dofs(pdbqt)
    logger.info(f"修复后 ascr18: {n_atoms} 原子, {n_dofs} DOFs")

    if n_atoms < 20:
        logger.error(f"原子数异常偏低 ({n_atoms})，可能仍有问题！")
        sys.exit(1)

    print(f"\nascr18 PDBQT 修复完成: {pdbqt}")
    print(f"  原子数: {n_atoms}（修复前: 15）")
    print(f"  DOFs: {n_dofs}（上限: {max_dofs}）")


if __name__ == "__main__":
    main()
