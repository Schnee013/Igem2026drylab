#!/usr/bin/env python3
"""
P0 分子对接 Pipeline 入口脚本

用法示例:
    # 开发/测试（快速模式，全流程）
    python run_pipeline.py --step all --fast

    # 仅准备 PDBQT 文件
    python run_pipeline.py --step prepare

    # Production 对接（可能需要 2-4 小时）
    python run_pipeline.py --step dock

    # 仅重跑分析（不重新对接）
    python run_pipeline.py --step analyze

    # 断点续跑（跳过已有结果）
    python run_pipeline.py --step dock --resume

    # 查看计划但不执行
    python run_pipeline.py --step all --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

# 将当前目录加入 Python 路径（方便相对 import）
sys.path.insert(0, str(Path(__file__).parent))

from analyze import run_analysis
from dock import dock_blind_validation, dock_matrix, load_docking_results
from prepare import load_prepared_paths, prepare_all
from utils import ensure_dirs, generate_run_id, load_config, setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="P0 分子对接 Pipeline（AutoDock Vina）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).parent / "config.yaml"),
        help="配置文件路径（默认: config.yaml）",
    )
    parser.add_argument(
        "--step",
        choices=["prepare", "dock", "analyze", "all"],
        default="all",
        help="执行步骤（默认: all）",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="快速模式（exhaustiveness=32，约 30 min 完成全矩阵，用于开发测试）",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="断点续跑：跳过已有结果的对接（不重新计算）",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="对接后额外运行 blind docking 验证（每受体多一次对接）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="打印执行计划但不实际运行",
    )
    return parser.parse_args()


def print_plan(args: argparse.Namespace, config: dict) -> None:
    """Dry-run 模式：打印执行计划。"""
    print("\n" + "=" * 60)
    print("  分子对接 Pipeline 执行计划（Dry Run）")
    print("=" * 60)
    print(f"  配置文件: {args.config}")
    print(f"  执行步骤: {args.step}")
    print(f"  模式: {'FAST (exhaustiveness=32)' if args.fast else 'PRODUCTION (exhaustiveness=200)'}")
    print(f"  Blind 验证: {'是' if args.validate else '否'}")
    print(f"  断点续跑: {'是' if args.resume else '否'}")
    print()
    print("  受体（3 个）:")
    for name, cfg in config["receptors"].items():
        print(f"    - {name}: {cfg['pdb_file']} ({cfg['n_residues']} 残基)")
    print()
    print("  配体（3 个）:")
    for name, cfg in config["ligands"].items():
        print(f"    - {name}: {cfg['sdf_file']}")
    print()

    vina = config["vina"]
    if args.fast:
        exh = vina["fast"]["exhaustiveness"]
        est = "~30 min"
    else:
        exh = vina["exhaustiveness"]
        est = "~2-4 小时"

    print(f"  Vina 参数: exhaustiveness={exh}, num_modes={vina['num_modes']}")
    print(f"  估计运行时间: {est}（9 对，M1 Mac）")
    print()
    print("  输出：")
    root = config["paths"]["project_root"]
    print(f"    - PDBQT: {root}/experiments/docking/prepared/")
    print(f"    - Pose: {root}/experiments/docking/results/poses/")
    print(f"    - 亲和力矩阵: {root}/experiments/docking/analysis/affinity_matrix.csv")
    print(f"    - 热图: {root}/experiments/docking/analysis/affinity_heatmap.png")
    print(f"    - PLIP: {root}/experiments/docking/results/interactions/")
    print(f"    - 验证报告: {root}/experiments/docking/analysis/validation_report.md")
    print(f"    - PyMOL 脚本: {root}/experiments/docking/analysis/pymol_scripts/")
    print()
    print("  （Dry Run 结束，未执行实际计算）")
    print("=" * 60)


def main() -> None:
    args = parse_args()

    # 加载配置
    config = load_config(args.config)

    # Dry run 模式
    if args.dry_run:
        print_plan(args, config)
        return

    # 初始化
    run_id = generate_run_id()
    from pathlib import Path as P
    log_dir = P(config["paths"]["project_root"]) / config["paths"]["log_dir"]
    logger = setup_logging(log_dir, run_id)
    ensure_dirs(config)

    logger.info(f"P0 分子对接 Pipeline 启动 [run_id={run_id}]")
    logger.info(f"步骤: {args.step} | 模式: {'FAST' if args.fast else 'PRODUCTION'}")

    t_total = time.time()

    # === Step: prepare ===
    if args.step in ("prepare", "all"):
        logger.info("--- Step 1/3: 准备 PDBQT ---")
        prepared_paths = prepare_all(config)
    elif args.step in ("dock", "analyze"):
        prepared_paths = load_prepared_paths(config)

    # === Step: dock ===
    if args.step in ("dock", "all"):
        logger.info("--- Step 2/3: 分子对接 ---")
        results = dock_matrix(config, prepared_paths, fast=args.fast, resume=args.resume)

        if args.validate:
            logger.info("--- Blind Docking 验证 ---")
            dock_blind_validation(config, prepared_paths, fast=True)
    elif args.step == "analyze":
        results = load_docking_results(config)

    # === Step: analyze ===
    if args.step in ("analyze", "all"):
        logger.info("--- Step 3/3: 结果分析 ---")
        run_analysis(config, results, prepared_paths)

    elapsed = time.time() - t_total
    logger.info(f"Pipeline 完成！总用时: {elapsed/60:.1f} 分钟")
    logger.info(
        f"输出目录: {config['paths']['project_root']}/experiments/docking/analysis/"
    )


if __name__ == "__main__":
    main()
