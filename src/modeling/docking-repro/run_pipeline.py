"""
Hu2024 精确复现 Pipeline 入口

工具链：ADFR Suite（受体/配体准备）+ Orca DFT B3LYP/def2-TZVP（配体几何）
       + AutoDock Vina 两阶段对接（Stage1: 40Å/0.25Å，Stage2: 20Å/0.1Å）

用法:
    # 完整流程
    python run_pipeline.py --step all

    # 仅准备 PDBQT（需先在 Windows 安装 ADFR + Orca）
    python run_pipeline.py --step prepare

    # 仅对接（跳过已有准备步骤）
    python run_pipeline.py --step dock

    # 验证（对比 v2 和 Hu2024 文献）
    python run_pipeline.py --step validate

    # 查看计划
    python run_pipeline.py --dry-run

注意：prepare 步骤会调用 Windows 上的 ADFR Suite 和 Orca（通过 SSH 或本机），
      需要在 config.yaml 中配置正确的工具路径。
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# 复用 v2 的 analyze.py / grid_box.py（方法无关，只处理结果）
sys.path.insert(0, str(Path(__file__).parent.parent / "docking"))
# docking-repro 自己的模块优先级最高（覆盖 v2 的同名模块）
sys.path.insert(0, str(Path(__file__).parent))

from dock import dock_matrix
from prepare_ligand import prepare_all_ligands
from prepare_receptor import prepare_all_receptors
from utils import ensure_dirs, generate_run_id, get_project_root, load_config, setup_logging

try:
    from analyze import run_analysis
except ImportError:
    def run_analysis(*args, **kwargs):
        get_logger().warning("analyze.py 未找到（v2 目录），跳过可视化分析")


def get_logger():
    import logging
    return logging.getLogger("docking-repro")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hu2024 复现 Pipeline（ADFR + Orca + Vina 两阶段）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    parser.add_argument(
        "--step",
        choices=["prepare", "dock", "analyze", "validate", "mutagenesis", "all"],
        default="all",
    )
    parser.add_argument("--resume", action="store_true", help="跳过已有结果（断点续跑）")
    parser.add_argument("--dry-run", action="store_true", help="打印计划不执行")
    parser.add_argument("--project-root", default=None,
                        help="覆盖 config.yaml 中的 project_root（在 Windows 上运行时使用）")
    return parser.parse_args()


def print_plan(config: dict, args: argparse.Namespace) -> None:
    root = config["paths"]["project_root"]
    remote = config["remote"]
    stage2 = config["vina"]["stage2"]
    print("\n" + "=" * 65)
    print("  Hu2024 复现 Pipeline 执行计划（Dry Run）")
    print("=" * 65)
    print(f"  配置文件: {args.config}")
    print(f"  执行步骤: {args.step}")
    print()
    print(f"  Windows 计算节点: {remote['host']}")
    print(f"  ADFR Suite:  {remote['adfr_bin']}")
    print(f"  Orca:        {remote['orca_bin']}")
    print()
    print("  受体（对接目标）:")
    for name, cfg in config["receptors"].items():
        print(f"    - {name}: {cfg['pdb_file']} ({cfg['n_residues']} 残基)")
    print()
    print("  配体（Orca DFT 优化 + ADFR PDBQT）:")
    for name, cfg in config["ligands"].items():
        print(f"    - {name}: {cfg['formula']}")
    print()
    print(f"  Orca: {config['orca']['method']}/{config['orca']['basis']}")
    print(f"  ADFR 配体最大 DOF: {config['adfr']['ligand']['max_dofs']}")
    print()
    print(f"  对接（两阶段）:")
    print(f"    Stage1: box=40Å, spacing=0.25, exh=32   [定位口袋]")
    print(f"    Stage2: box={stage2['box_size']}Å, spacing={stage2['spacing']}, exh={stage2['exhaustiveness']}  [精修，匹配 Hu2024]")
    print()
    print(f"  验证阈值: Δ < {config['validation']['tolerance_kcal']} kcal/mol（v2 用 1.0）")
    print()
    print("  输出路径:")
    print(f"    - PDBQT:    {root}/experiments/docking-repro/prepared/")
    print(f"    - Orca:     {root}/experiments/docking-repro/ligands/orca/")
    print(f"    - Poses:    {root}/experiments/docking-repro/results/poses/")
    print(f"    - 验证报告: {root}/experiments/docking-repro/analysis/validation_report.md")
    print()
    print("  （Dry Run 结束，未执行实际计算）")
    print("=" * 65)


def save_manifest(prepared_paths: dict, config: dict) -> None:
    """保存路径 manifest JSON，供断点续跑使用。"""
    import json
    root = get_project_root(config)
    manifest_path = root / config["paths"]["prepared_dir"] / "prepared_paths.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "receptors": {k: str(v) for k, v in prepared_paths["receptors"].items()},
        "tm_pdbs": {k: str(v) for k, v in prepared_paths.get("tm_pdbs", {}).items()},
        "ligands": {k: str(v) for k, v in prepared_paths["ligands"].items()},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    get_logger().info(f"路径 manifest 已保存: {manifest_path}")


def load_manifest(config: dict) -> dict:
    import json
    root = get_project_root(config)
    manifest_path = root / config["paths"]["prepared_dir"] / "prepared_paths.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest 不存在: {manifest_path}，请先运行 --step prepare")
    manifest = json.loads(manifest_path.read_text())
    return {
        "receptors": {k: Path(v) for k, v in manifest["receptors"].items()},
        "tm_pdbs": {k: Path(v) for k, v in manifest.get("tm_pdbs", {}).items()},
        "ligands": {k: Path(v) for k, v in manifest["ligands"].items()},
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    if args.dry_run:
        print_plan(config, args)
        return

    run_id = generate_run_id()
    root = get_project_root(config)
    logger = setup_logging(root / config["paths"]["log_dir"], run_id)
    ensure_dirs(config)

    logger.info(f"Hu2024 复现 Pipeline 启动 [run_id={run_id}, step={args.step}]")
    logger.info(f"ADFR: {config['remote']['adfr_bin']}")
    logger.info(f"Orca: {config['remote']['orca_bin']}")
    t_total = time.time()

    prepared_paths = {}

    # === prepare ===
    if args.step in ("prepare", "all"):
        logger.info("--- Step 1/3: ADFR 受体准备 ---")
        rec_paths = prepare_all_receptors(config)

        logger.info("--- Step 2/3: Orca + ADFR 配体准备（耗时较长）---")
        lig_paths = prepare_all_ligands(config)

        prepared_paths = {**rec_paths, "ligands": lig_paths}
        save_manifest(prepared_paths, config)
    elif args.step in ("dock", "analyze", "validate"):
        prepared_paths = load_manifest(config)

    # === dock ===
    if args.step in ("dock", "all"):
        logger.info("--- Step 3/3: 两阶段对接 ---")
        results = dock_matrix(prepared_paths, config)
    elif args.step in ("analyze", "validate"):
        import json
        results_json = root / config["paths"]["results_dir"] / config["paths"].get("results_filename", "docking_results.json")
        if results_json.exists():
            raw = json.loads(results_json.read_text())
            # 简单转为 DockingResult-like 对象（用字典也行，analyze 接受字典）
            results = raw
        else:
            results = []

    # === analyze ===
    if args.step in ("analyze", "all"):
        logger.info("--- 结果分析 ---")
        try:
            run_analysis(config, results, prepared_paths)
        except Exception as e:
            logger.warning(f"分析步骤失败（非致命）: {e}")

    # === validate ===
    if args.step in ("validate", "all"):
        logger.info("--- 验证（v2 vs repro vs Hu2024）---")
        from validate import main as validate_main
        sys.argv = ["validate.py", "--config", args.config]
        validate_main()

    # === mutagenesis ===
    if args.step in ("mutagenesis",):
        logger.info("--- In Silico 突变扫描（AF3 结构 + Vina 重对接）---")
        from mutagenesis import run_mutagenesis
        mut_results = run_mutagenesis(config)
        root = get_project_root(config)
        mut_dir = root / config["paths"].get(
            "mutagenesis_dir",
            config["paths"]["results_dir"].replace("results", "mutagenesis"),
        )
        logger.info(
            f"突变扫描完成：{len(mut_results)} 个突变\n"
            f"  报告: {mut_dir}/mutagenesis_report.md\n"
            f"  JSON: {mut_dir}/mutagenesis_results.json"
        )

    elapsed = time.time() - t_total
    logger.info(f"Pipeline 完成！总用时: {elapsed / 60:.1f} 分钟")
    logger.info(f"结果: {root}/experiments/docking-repro/analysis/")


if __name__ == "__main__":
    main()
