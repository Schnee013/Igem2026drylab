"""
配体准备 Runner：Orca DFT 优化 + ADFR PDBQT 生成

为所有 config.yaml 中定义的配体执行完整 Hu2024 准备流程：
  SMILES → RDKit ETKDGv3 → Orca B3LYP/def2-TZVP → ADFR PDBQT

用法（Windows）：
    python run_prepare_ligands.py
    python run_prepare_ligands.py --ligands ascr1
    python run_prepare_ligands.py --project-root D:\drylab-tools\workspace
"""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from prepare_ligand import prepare_all_ligands
from utils import generate_run_id, get_project_root, load_config, setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="配体准备：Orca DFT + ADFR PDBQT")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--ligands", nargs="+", default=None,
                        help="仅准备指定配体（默认全部）。例：--ligands ascr1")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    logger = setup_logging(root / config["paths"]["log_dir"], f"prepare_ligands_{generate_run_id()}")
    logger.info("=== 配体准备启动 ===")

    try:
        paths = prepare_all_ligands(config, only=args.ligands)
    except Exception:
        logger.error("=== 配体准备失败 ===\n" + traceback.format_exc())
        sys.exit(1)

    logger.info("=== 配体准备完成 ===")
    for name, p in paths.items():
        logger.info(f"  {name}: {p}")


if __name__ == "__main__":
    main()
