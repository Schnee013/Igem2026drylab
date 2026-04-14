"""
Alanine Scan：3 受体全量扫描（GprC × 11 残基，Gpr2 × 9 残基，Gpr3 × 8 残基 = 28 突变体）

依赖：
  - WT 单阶段基线：experiments/docking-repro/results/wt_singlestage/docking_results.json
  - Orca 配体：experiments/docking-repro/prepared/ligands/ascr{18,3}_optimized.pdbqt
  - AF3 突变体 PDBQT：experiments/docking-repro/mutagenesis/af3_prepared/{RecName}/{Label}_tm.pdbqt
  - WT TM PDB：experiments/docking-repro/prepared/receptors/Gpr{2,3,C}_*_tm.pdb

用法（Windows）：
    python run_mutagenesis_alanine.py
    python run_mutagenesis_alanine.py --project-root D:\\drylab-tools\\workspace
    python run_mutagenesis_alanine.py --receptors GprC Gpr2   # 仅扫描指定受体

输出：
    experiments/docking-repro/mutagenesis/{RecName}/{Label}/docking/ — 对接中间文件
    experiments/docking-repro/mutagenesis/mutagenesis_results.json
    experiments/docking-repro/mutagenesis/mutagenesis_report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from mutagenesis import run_mutagenesis
from utils import generate_run_id, get_project_root, load_config, preflight_check, setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="全量 Alanine Scan（3 受体 × 全部 scan_residues）")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--receptors", nargs="+", default=["GprC", "Gpr2", "Gpr3"],
        help="扫描的受体列表（默认全部）",
    )
    return parser.parse_args()


def load_wt_baseline(root: Path, config: dict) -> dict[str, float]:
    """从 WT 单阶段结果加载基线，并校验预期键存在。"""
    results_dir = root / config["paths"]["results_dir"]
    subdir = config["paths"]["wt_singlestage_subdir"]
    filename = config["paths"].get("results_filename", "docking_results.json")
    wt_json = results_dir / subdir / filename
    if not wt_json.exists():
        raise FileNotFoundError(
            f"WT 单阶段基线不存在: {wt_json}\n"
            "请先完成 run_wt_singlestage.py。"
        )
    raw = json.loads(wt_json.read_text(encoding="utf-8"))
    baseline = {r["pair_name"]: r["best_affinity"] for r in raw}
    expected = [
        "GprC_ascr18", "GprC_ascr3",
        "Gpr2_ascr18", "Gpr2_ascr3",
        "Gpr3_ascr18", "Gpr3_ascr3",
    ]
    missing = [k for k in expected if k not in baseline]
    if missing:
        raise ValueError(
            f"WT 基线缺少键: {missing}\n"
            f"实际键: {sorted(baseline.keys())}\n"
            "请检查 run_wt_singlestage.py 输出的 pair_name 格式。"
        )
    return baseline


def print_summary(results: list, receptors: list[str], wt_baseline: dict) -> None:
    print("\n" + "=" * 70)
    print("  Alanine Scan 汇总（ΔΔG_sel < 0 → 增强 ascr18 偏好）")
    print("=" * 70)
    by_rec: dict[str, list] = {r: [] for r in receptors}
    for res in results:
        if res.receptor in by_rec:
            by_rec[res.receptor].append(res)

    for rec_name, rec_results in by_rec.items():
        if not rec_results:
            print(f"\n  {rec_name}: 无结果")
            continue
        rec_results.sort(key=lambda r: r.ddg_selectivity)
        wt_sel = wt_baseline.get(f"{rec_name}_ascr18", 0.0) - wt_baseline.get(f"{rec_name}_ascr3", 0.0)
        print(f"\n  {rec_name}  (WT sel = {wt_sel:+.3f})")
        print(f"  {'突变':<8} {'ΔΔG(18)':<10} {'ΔΔG(3)':<10} {'ΔΔG_sel':<10} {'解读'}")
        print("  " + "-" * 55)
        for r in rec_results:
            interp = (
                "✓✓ 增强 ascr18" if r.ddg_selectivity < -0.5
                else "✓ 轻微增强" if r.ddg_selectivity < 0
                else "— 中性"     if abs(r.ddg_selectivity) < 0.3
                else "✗ 增强 ascr3"
            )
            print(
                f"  {r.mutation:<8}  {r.ddg_ascr18:>+8.3f}  "
                f"{r.ddg_ascr3:>+8.3f}  {r.ddg_selectivity:>+8.3f}  {interp}"
            )
    print("=" * 70)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(
        root / config["paths"]["log_dir"],
        f"mutagenesis_alanine_{run_id}",
    )

    # 使用 AF3 突变体结构 + 单阶段对接协议
    # wt_baseline 强制 "repro"（忽略 config.yaml 中的字段，此处为权威源）
    config["mutagenesis"]["wt_baseline"] = "repro"
    config["mutagenesis"]["mutant_source"] = "af3"
    config["mutagenesis"]["docking_mode"] = "singlestage"
    config["mutagenesis"]["scan_type"] = "alanine"
    config["mutagenesis"]["target_receptors"] = args.receptors

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"
    mut_dir = root / config["paths"]["mutagenesis_dir"]

    # preflight 检查
    receptor_tm_pdbs = {
        rec: Path(config["receptors"][rec]["pdb_file"]).stem + "_tm.pdb"
        for rec in ["GprC", "Gpr2", "Gpr3"]
        if rec in config["receptors"]
    }
    wt_baseline_dir = (root / config["paths"]["results_dir"]
                       / config["paths"]["wt_singlestage_subdir"])
    wt_baseline_file = config["paths"].get("results_filename", "docking_results.json")
    checks = [
        {"type": "file_exists",
         "path": wt_baseline_dir / wt_baseline_file,
         "hint": "WT 单阶段基线不存在，请先运行 run_wt_singlestage.py"},
        {"type": "file_exists", "path": lig_dir / "ascr18_optimized.pdbqt",
         "hint": "ascr18 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
        {"type": "file_exists", "path": lig_dir / "ascr3_optimized.pdbqt",
         "hint": "ascr3 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
    ] + [
        {"type": "file_exists", "path": rec_dir / tm_pdb,
         "hint": f"{rec} TM PDB 不存在，请检查 prepared/receptors/"}
        for rec, tm_pdb in receptor_tm_pdbs.items()
        if rec in args.receptors
    ] + [
        {"type": "file_exists", "path": mut_dir / "af3_prepared" / rec,
         "hint": f"{rec} AF3 突变体 PDBQT 目录不存在，请先运行 ADFR prepare_receptor"}
        for rec in args.receptors
    ]
    preflight_check(checks, logger)

    # 加载 WT 单阶段基线
    wt_baseline = load_wt_baseline(root, config)
    logger.info(f"已加载 WT 单阶段基线（{len(wt_baseline)} 对）：")
    for k, v in sorted(wt_baseline.items()):
        logger.info(f"  {k}: {v:.3f} kcal/mol")

    # 计算预期突变数
    total_muts = sum(
        len(config["mutagenesis"]["scan_residues"].get(rec, []))
        for rec in args.receptors
    )
    logger.info(
        f"Alanine Scan 启动 [run_id={run_id}]"
        f"\n  突变体来源: AF3"
        f"\n  对接协议: 单阶段 (40Å/0.1/exh=200)"
        f"\n  受体: {args.receptors}"
        f"\n  预计突变数: {total_muts} （每突变 × 2 配体 × singlestage）"
        f"\n  预计用时: ~{total_muts * 4 // 60}-{total_muts * 6 // 60} 小时"
    )

    # 执行扫描
    results = run_mutagenesis(config, wt_dock_results=wt_baseline)

    if not results:
        logger.error("扫描无结果，请检查日志")
        sys.exit(1)

    logger.info(f"Alanine Scan 完成：{len(results)} 个突变体")

    # 打印汇总
    print_summary(results, args.receptors, wt_baseline)

    # 输出路径
    out_dir = root / config["paths"]["mutagenesis_dir"]
    print(f"\n  完整 JSON: {out_dir}/mutagenesis_results.json")
    print(f"  完整报告: {out_dir}/mutagenesis_report.md")
    print(f"  突变体 PDBQT: {out_dir}/prepared/（供 S2/S4 使用）")
    logger.info("Alanine Scan 完成")


if __name__ == "__main__":
    main()
