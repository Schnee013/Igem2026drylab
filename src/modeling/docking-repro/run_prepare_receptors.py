"""
受体 PDBQT 准备（单独步骤）

从已提取的 TM PDB 生成 ADFR PDBQT。
TM PDB 应预先在 Mac 端生成并上传到 prepared/receptors/。

用法（在 Windows 上运行）：
    python run_prepare_receptors.py
    python run_prepare_receptors.py --project-root D:/drylab-tools/workspace
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from prepare_receptor import prepare_all_receptors
from utils import get_project_root, load_config, setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="受体 PDBQT 准备（ADFR）")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    log_dir = root / config["paths"]["log_dir"]
    logger = setup_logging(log_dir, "prepare_receptors")
    logger.info("受体 PDBQT 准备启动")

    # 清除旧的 cleaned PDB 和 PDBQT（强制重新生成）
    rec_out = root / config["paths"]["prepared_dir"] / "receptors"
    for old in rec_out.glob("*_cleaned.pdb"):
        old.unlink()
        logger.info(f"  删除旧文件: {old.name}")
    for old in rec_out.glob("*.pdbqt"):
        old.unlink()
        logger.info(f"  删除旧文件: {old.name}")

    paths = prepare_all_receptors(config)

    print("\n=== 受体准备完成 ===")
    for name, pdbqt in paths["receptors"].items():
        print(f"  {name}: {pdbqt}")
        print(f"    TM PDB: {paths['tm_pdbs'][name]}")

    logger.info("受体 PDBQT 准备完成")


if __name__ == "__main__":
    main()
