"""
Saturation Scan：Channel A 核心位点饱和突变扫描
  Gpr2: M327 × 18 AA + R59 × 18 AA = 36
  Gpr3: I141 × 18 AA + F170 × 18 AA + V138 × 18 AA = 54
  共 90 突变体（排除 WT 和 Ala，Ala 已在 alanine scan 中完成）

依赖：
  - WT 单阶段基线：experiments/docking-repro/results/wt_singlestage/docking_results.json
  - Orca 配体：experiments/docking-repro/prepared/ligands/ascr{18,3}_optimized.pdbqt
  - AF3 突变体 PDBQT：experiments/docking-repro/mutagenesis/af3_prepared/{RecName}/{Label}_tm.pdbqt
  - WT TM PDB：experiments/docking-repro/prepared/receptors/Gpr{2,3}_*_tm.pdb

用法（Windows）：
    python run_mutagenesis_saturation.py
    python run_mutagenesis_saturation.py --project-root D:\\drylab-tools\\workspace
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import cast

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from mutagenesis import make_saturation_scan_mutations, run_mutagenesis
from utils import generate_run_id, get_project_root, load_config, preflight_check, setup_logging

# Channel A 核心饱和扫描位点
SATURATION_RESIDUES = {
    "Gpr2": [327, 59],      # M327 (Channel A), R59 (Channel A)
    "Gpr3": [141, 170, 138], # I141 (Channel A), F170 (Channel A), V138 (Channel A)
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Channel A 核心位点饱和突变扫描")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--receptors", nargs="+", default=None,
        help=f"子集（如 --receptors Gpr2），默认全部 {list(SATURATION_RESIDUES.keys())}",
    )
    parser.add_argument("--vina-bin", default=None,
                        help="覆盖 config 中的 vina_bin 路径（跨平台使用）")
    parser.add_argument("--cpu", type=int, default=None,
                        help="Vina 使用的 CPU 核心数（默认占满全部；Mac 长时间跑建议 4-6 避免过热）")
    return parser.parse_args()


def load_wt_baseline(root: Path, config: dict) -> dict[str, float]:
    """从 WT 单阶段结果加载基线。"""
    results_dir = root / config["paths"]["results_dir"]
    subdir = config["paths"]["wt_singlestage_subdir"]
    filename = config["paths"].get("results_filename", "docking_results.json")
    wt_json = results_dir / subdir / filename
    if not wt_json.exists():
        raise FileNotFoundError(f"WT 单阶段基线不存在: {wt_json}")
    raw = json.loads(wt_json.read_text(encoding="utf-8"))
    return {r["pair_name"]: r["best_affinity"] for r in raw}


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root
    if args.vina_bin:
        config["remote"]["vina_bin"] = args.vina_bin
    if args.cpu is not None:
        os.environ["VINA_CPU"] = str(args.cpu)

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(
        root / config["paths"]["log_dir"],
        f"mutagenesis_saturation_{run_id}",
    )

    # --receptors 子集过滤（未指定则全量）
    if args.receptors:
        unknown = [r for r in args.receptors if r not in SATURATION_RESIDUES]
        if unknown:
            raise SystemExit(f"未知受体: {unknown}。可用: {list(SATURATION_RESIDUES.keys())}")
        active_saturation = {r: SATURATION_RESIDUES[r] for r in args.receptors}
    else:
        active_saturation = dict(SATURATION_RESIDUES)

    # 配置：饱和扫描，排除 Ala（已在 alanine scan 中完成）
    config["mutagenesis"]["wt_baseline"] = "repro"
    config["mutagenesis"]["mutant_source"] = "af3"
    config["mutagenesis"]["docking_mode"] = "singlestage"
    config["mutagenesis"]["scan_type"] = "saturation"
    config["mutagenesis"]["exclude_aas"] = ["A"]
    config["mutagenesis"]["target_receptors"] = list(active_saturation.keys())

    # 覆盖 scan_residues 为仅 Channel A 核心位点
    config["mutagenesis"]["scan_residues"] = active_saturation

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"
    mut_dir = root / config["paths"]["mutagenesis_dir"]

    # preflight 检查
    receptors = list(active_saturation)
    receptor_tm_pdbs = {
        rec: Path(config["receptors"][rec]["pdb_file"]).stem + "_tm.pdb"
        for rec in receptors
    }
    wt_baseline_dir = (root / config["paths"]["results_dir"]
                       / config["paths"]["wt_singlestage_subdir"])
    wt_baseline_file = config["paths"].get("results_filename", "docking_results.json")
    checks = [
        {"type": "file_exists",
         "path": wt_baseline_dir / wt_baseline_file,
         "hint": "WT 单阶段基线不存在，请先运行 run_wt_singlestage.py"},
        {"type": "file_exists", "path": lig_dir / "ascr18_optimized.pdbqt",
         "hint": "ascr18 配体不存在"},
        {"type": "file_exists", "path": lig_dir / "ascr3_optimized.pdbqt",
         "hint": "ascr3 配体不存在"},
    ] + [
        {"type": "file_exists", "path": rec_dir / tm_pdb,
         "hint": f"{rec} TM PDB 不存在"}
        for rec, tm_pdb in receptor_tm_pdbs.items()
    ] + [
        {"type": "file_exists", "path": mut_dir / "af3_prepared" / rec,
         "hint": f"{rec} AF3 PDBQT 目录不存在，请先运行 run_adfr_mutants.py"}
        for rec in receptors
    ]
    preflight_check(checks, logger)

    wt_baseline = load_wt_baseline(root, config)
    logger.info(f"已加载 WT 基线（{len(wt_baseline)} 对）")

    # 按实际 WT 残基 + exclude_aas 展开突变列表，避免硬编码
    exclude_aas = cast(list[str], config["mutagenesis"].get("exclude_aas") or [])
    total_muts = 0
    for rec, residues in active_saturation.items():
        tm_pdb = cast(Path, rec_dir / receptor_tm_pdbs[rec])
        total_muts += len(make_saturation_scan_mutations(
            tm_pdb, residues, exclude_aas=exclude_aas,
        ))
    cpu_note = f"，CPU={args.cpu}" if args.cpu is not None else "（默认全部核心）"
    logger.info(
        f"Saturation Scan 启动 [run_id={run_id}]{cpu_note}"
        f"\n  受体: {receptors}"
        f"\n  位点: {active_saturation}"
        f"\n  排除氨基酸: {exclude_aas}"
        f"\n  预计突变数: {total_muts}（每突变 × 2 配体）"
        f"\n  预计对接数: {total_muts * 2}"
        f"\n  预计用时: ~{total_muts * 4 // 60}-{total_muts * 6 // 60} 小时"
    )

    results = run_mutagenesis(config, wt_dock_results=wt_baseline)

    if not results:
        logger.error("扫描无结果，请检查日志")
        sys.exit(1)

    logger.info(f"Saturation Scan 完成：{len(results)} 个突变体")

    # 打印汇总
    print(f"\n{'='*70}")
    print(f"  Saturation Scan 汇总（ΔΔG_sel < 0 → 增强 ascr18 偏好）")
    print(f"{'='*70}")
    for rec_name in receptors:
        rec_results = [r for r in results if r.receptor == rec_name]
        if not rec_results:
            continue
        rec_results.sort(key=lambda r: r.ddg_selectivity)
        wt_sel = wt_baseline.get(f"{rec_name}_ascr18", 0.0) - wt_baseline.get(f"{rec_name}_ascr3", 0.0)
        print(f"\n  {rec_name}  (WT sel = {wt_sel:+.3f})")
        print(f"  {'突变':<8} {'ΔΔG(18)':<10} {'ΔΔG(3)':<10} {'ΔΔG_sel':<10}")
        print("  " + "-" * 45)
        for r in rec_results:
            print(f"  {r.mutation:<8}  {r.ddg_ascr18:>+8.3f}  {r.ddg_ascr3:>+8.3f}  {r.ddg_selectivity:>+8.3f}")
    print(f"{'='*70}")

    out_dir = root / config["paths"]["mutagenesis_dir"]
    print(f"\n  完整 JSON: {out_dir}/mutagenesis_results.json")
    print(f"  完整报告: {out_dir}/mutagenesis_report.md")


if __name__ == "__main__":
    main()
