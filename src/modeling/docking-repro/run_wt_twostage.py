"""
S1: WT 两阶段重对接 — 解决协议不匹配问题

问题：mutagenesis 扫描的突变体使用两阶段协议（Stage1→Stage2），
      但 WT 基线来自 v2 单阶段协议（spacing=0.25），导致 ~-0.7 kcal/mol
      系统性偏差。本脚本对 3 个 WT 受体 × 2 配体（ascr18, ascr3）
      用完全相同的两阶段协议对接，产出同协议 WT 基线。

用法（在 Windows 上运行）：
    python run_wt_twostage.py
    python run_wt_twostage.py --project-root D:/drylab-repro
    python run_wt_twostage.py --receptors GprC Gpr2  # 仅对接指定受体

输出：
    experiments/docking-repro/results/wt_twostage/docking_results.json
    experiments/docking-repro/results/wt_twostage/poses/<pair_name>/
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# 确保可以导入 docking-repro 和 docking 模块
_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))
sys.path.insert(0, str(_this_dir.parent / "docking"))

from dock import DockingResult, dock_pair_twostage
from utils import generate_run_id, get_project_root, load_config, preflight_check, setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="S1: WT 两阶段重对接")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None,
                        help="覆盖 config.yaml 中的 project_root（Windows 上使用）")
    parser.add_argument("--receptors", nargs="+", default=["GprC", "Gpr2", "Gpr3"],
                        help="对接的受体列表（默认全部三个）")
    parser.add_argument("--ligands", nargs="+", default=["ascr18", "ascr3", "ascr7"],
                        help="对接的配体列表（默认 ascr18 + ascr3 + ascr7）")
    return parser.parse_args()


# 受体 PDBQT 文件名（来自 v2 prepared，TM-only）
RECEPTOR_PDBQTS = {
    "GprC": "GprC_A0A437AGY2_tm.pdbqt",
    "Gpr2": "Gpr2_G1X9E2_tm.pdbqt",
    "Gpr3": "Gpr3_G1XJN1_tm.pdbqt",
}
RECEPTOR_TM_PDBS = {
    "GprC": "GprC_A0A437AGY2_tm.pdb",
    "Gpr2": "Gpr2_G1X9E2_tm.pdb",
    "Gpr3": "Gpr3_G1XJN1_tm.pdb",
}

LIGAND_PDBQTS = {
    "ascr18": "ascr18_optimized.pdbqt",
    "ascr3":  "ascr3_optimized.pdbqt",
    "ascr7":  "ascr7_optimized.pdbqt",
}


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    run_id = generate_run_id()
    log_dir = root / config["paths"]["log_dir"]
    logger = setup_logging(log_dir, f"wt_twostage_{run_id}")
    logger.info(f"S1 WT 两阶段重对接启动 [run_id={run_id}]")

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"

    # preflight 检查
    preflight_check(
        [{"type": "file_exists", "path": lig_dir / LIGAND_PDBQTS[lg],
          "hint": f"{lg} 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"}
         for lg in args.ligands]
        + [{"type": "file_exists", "path": rec_dir / RECEPTOR_PDBQTS[rc],
            "hint": f"{rc} 受体 PDBQT 不存在，请检查 prepared/receptors/"}
           for rc in args.receptors
           if rc in RECEPTOR_PDBQTS],
        logger,
    )

    # 输出目录
    out_dir = root / "experiments" / "docking-repro" / "results" / "wt_twostage"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[DockingResult] = []
    pairs_done = 0
    pairs_total = len(args.receptors) * len(args.ligands)

    for rec_name in args.receptors:
        rec_pdbqt = rec_dir / RECEPTOR_PDBQTS[rec_name]
        tm_pdb    = rec_dir / RECEPTOR_TM_PDBS[rec_name]

        if not rec_pdbqt.exists():
            logger.error(f"受体 PDBQT 不存在: {rec_pdbqt}")
            sys.exit(1)
        if not tm_pdb.exists():
            logger.error(f"受体 TM PDB 不存在: {tm_pdb}")
            sys.exit(1)

        for lig_name in args.ligands:
            lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]
            if not lig_pdbqt.exists():
                logger.error(f"配体 PDBQT 不存在: {lig_pdbqt}")
                sys.exit(1)

            pairs_done += 1
            pair_name = f"{rec_name}_{lig_name}"
            pair_dir = out_dir / "poses" / pair_name
            logger.info(f"[{pairs_done}/{pairs_total}] {pair_name}")

            result = dock_pair_twostage(
                receptor_pdbqt=rec_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                pair_name=pair_name,
                tm_pdb=tm_pdb,
                output_dir=pair_dir,
                config=config,
                # seed 和 stage2_box_size 使用 config 默认值（seed=42, box=20A）
            )
            results.append(result)
            logger.info(
                f"  ✓ {pair_name}: ΔG = {result.best_affinity:.3f} kcal/mol "
                f"（{result.elapsed_sec:.0f}s）"
            )

    # 保存 JSON 结果
    from dataclasses import asdict
    out_json = out_dir / "docking_results.json"
    out_json.write_text(
        json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 打印汇总表
    print("\n" + "=" * 60)
    print("  S1 WT 两阶段重对接结果")
    print("=" * 60)
    print(f"{'受体':<8} {'配体':<8} {'ΔG (kcal/mol)'}")
    print("-" * 40)
    for r in results:
        print(f"  {r.receptor:<8} {r.ligand:<8} {r.best_affinity:>8.3f}")
    print("=" * 60)
    print(f"\n结果已保存: {out_json}")

    # 计算 WT selectivity（ascr18 vs ascr3）
    print("\n  WT 选择性（ΔG_sel = ΔG(ascr18) - ΔG(ascr3)）：")
    print("  （注：ΔG_sel < 0 表示受体对 ascr18 亲和力更高）")
    print("-" * 40)
    by_rec: dict[str, dict[str, float]] = {}
    for r in results:
        rec = r.receptor.split("_")[0] if "_" in r.receptor else r.receptor
        # pair_name 形如 "GprC_ascr18"，从 pair_name 提取
        rec_key = r.pair_name.split("_")[0]
        lig_key = "_".join(r.pair_name.split("_")[1:])
        by_rec.setdefault(rec_key, {})[lig_key] = r.best_affinity

    for rec_name, ligs in by_rec.items():
        if "ascr18" in ligs and "ascr3" in ligs:
            sel = ligs["ascr18"] - ligs["ascr3"]
            print(f"  {rec_name}: ΔG(18)={ligs['ascr18']:.3f}, ΔG(3)={ligs['ascr3']:.3f}, sel={sel:+.3f}")

    logger.info("S1 WT 两阶段重对接完成")


if __name__ == "__main__":
    main()
