"""
WT 单阶段对接 — Hu2024 精确复现协议

参数：box=40Å, spacing=0.1Å, exhaustiveness=200, center=TM螺旋质量加权质心
配体：ascr1, ascr18, ascr3, ascr7（共 12 对接对）

用法（在 Windows 上运行）：
    python run_wt_singlestage.py
    python run_wt_singlestage.py --project-root D:/drylab-repro
    python run_wt_singlestage.py --receptors GprC --ligands ascr18 ascr3

输出：
    experiments/docking-repro/results/wt_singlestage/docking_results.json
    experiments/docking-repro/results/wt_singlestage/poses/<pair_name>/
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from dock import (
    DockingResult,
    dock_pair_singlestage,
    get_box_center_offset,
    get_manual_box_center,
    get_receptor_box_size,
    get_tm_helix_ranges,
)
from utils import (
    generate_run_id, get_project_root, get_results_subdir, load_config,
    preflight_check, save_results_json, setup_logging,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WT 单阶段重对接（Hu2024 精确复现）")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None,
                        help="覆盖 config.yaml 中的 project_root（Windows 上使用）")
    parser.add_argument("--receptors", nargs="+", default=["GprC", "Gpr2", "Gpr3"],
                        help="对接的受体列表（默认全部三个）")
    parser.add_argument("--ligands", nargs="+", default=["ascr1", "ascr18", "ascr3", "ascr7"],
                        help="对接的配体列表（默认 ascr1 + ascr18 + ascr3 + ascr7）")
    parser.add_argument("--vina-bin", default=None,
                        help="覆盖 config 中的 vina_bin 路径（跨平台使用）")
    parser.add_argument("--out-subdir", default=None,
                        help="覆盖输出目录相对路径（相对 results_dir），默认用 config.paths.wt_singlestage_subdir。"
                             "用于试跑时不覆盖主 WT baseline，例如 'wt_singlestage_gpr3_box25_test'。")
    return parser.parse_args()


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
    "ascr1":  "ascr1_optimized.pdbqt",
    "ascr18": "ascr18_optimized.pdbqt",
    "ascr3":  "ascr3_optimized.pdbqt",
    "ascr7":  "ascr7_optimized.pdbqt",
}


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root
    if args.vina_bin:
        config["remote"]["vina_bin"] = args.vina_bin

    root = get_project_root(config)
    run_id = generate_run_id()
    log_dir = root / config["paths"]["log_dir"]
    logger = setup_logging(log_dir, f"wt_singlestage_{run_id}")
    logger.info(f"WT 单阶段对接启动 [run_id={run_id}]")

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"

    # preflight 检查
    checks = []
    for lg in args.ligands:
        if lg not in LIGAND_PDBQTS:
            logger.error(f"未知配体: {lg}，支持: {list(LIGAND_PDBQTS.keys())}")
            sys.exit(1)
        checks.append({
            "type": "file_exists",
            "path": lig_dir / LIGAND_PDBQTS[lg],
            "hint": f"{lg} 配体 PDBQT 不存在，请先运行 run_prepare_ligands.py 完成 Orca 配体准备",
        })
    for rc in args.receptors:
        if rc not in RECEPTOR_PDBQTS:
            logger.error(f"未知受体: {rc}，支持: {list(RECEPTOR_PDBQTS.keys())}")
            sys.exit(1)
        checks.append({
            "type": "file_exists",
            "path": rec_dir / RECEPTOR_PDBQTS[rc],
            "hint": f"{rc} 受体 PDBQT 不存在，请检查 prepared/receptors/",
        })
        checks.append({
            "type": "file_exists",
            "path": rec_dir / RECEPTOR_TM_PDBS[rc],
            "hint": f"{rc} TM PDB 不存在，请检查 prepared/receptors/",
        })
    preflight_check(checks, logger)

    # 输出目录（--out-subdir 覆盖时绕过 config 键，直接用相对路径）
    if args.out_subdir:
        out_dir = root / config["paths"]["results_dir"] / args.out_subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出子目录覆盖: {out_dir}（不覆盖主 WT baseline）")
    else:
        out_dir = get_results_subdir(config, "wt_singlestage_subdir")

    results: list[DockingResult] = []
    pairs_total = len(args.receptors) * len(args.ligands)
    pairs_done = 0

    for rec_name in args.receptors:
        rec_pdbqt = rec_dir / RECEPTOR_PDBQTS[rec_name]
        tm_pdb = rec_dir / RECEPTOR_TM_PDBS[rec_name]
        helix_ranges = get_tm_helix_ranges(config, rec_name)
        box_offset = get_box_center_offset(config, rec_name)
        rec_box_size = get_receptor_box_size(config, rec_name)
        manual_center = get_manual_box_center(config, rec_name)

        for lig_name in args.ligands:
            lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]
            pairs_done += 1
            pair_name = f"{rec_name}_{lig_name}"
            pair_dir = out_dir / "poses" / pair_name
            logger.info(f"[{pairs_done}/{pairs_total}] {pair_name}")

            result = dock_pair_singlestage(
                receptor_pdbqt=rec_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                pair_name=pair_name,
                tm_pdb=tm_pdb,
                output_dir=pair_dir,
                config=config,
                tm_helix_ranges=helix_ranges,
                box_center_offset=box_offset,
                receptor_box_size=rec_box_size,
                manual_box_center=manual_center,
            )
            results.append(result)
            logger.info(
                f"  ✓ {pair_name}: ΔG = {result.best_affinity:.3f} kcal/mol "
                f"（{result.elapsed_sec:.0f}s）"
            )

    # 保存 JSON 结果（时间戳 + latest）
    out_json = save_results_json(
        [asdict(r) for r in results], out_dir, run_id, config,
    )

    # 汇总表
    print("\n" + "=" * 65)
    print("  WT 单阶段对接结果（Hu2024 协议：40Å/0.1/exh=200）")
    print("=" * 65)
    print(f"  {'受体':<8} {'配体':<8} {'ΔG (kcal/mol)':>14}  {'Hu2024 参考':>12}")
    print("  " + "-" * 50)

    validation = config.get("validation", {})
    reference = validation.get("reference", {})
    kuo_abs = validation.get("kuo2024_absolute", {})

    for r in results:
        ref_key = r.pair_name
        ref_val = reference.get(ref_key) or kuo_abs.get(ref_key)
        ref_str = f"{ref_val:>+.2f}" if ref_val is not None else "  n/a"
        diff_str = ""
        if ref_val is not None:
            diff = r.best_affinity - ref_val
            diff_str = f"  Δ={diff:+.2f}"
        r_rec = r.pair_name.split("_")[0]
        print(f"  {r_rec:<8} {r.ligand.split('_')[0]:<8} {r.best_affinity:>14.3f}  {ref_str}{diff_str}")

    print("=" * 65)
    print(f"\n结果已保存: {out_json}")

    # Hu2024 验证
    gprc_18 = next((r.best_affinity for r in results if r.pair_name == "GprC_ascr18"), None)
    gprc_3  = next((r.best_affinity for r in results if r.pair_name == "GprC_ascr3"),  None)
    tol = validation.get("tolerance_kcal", 0.5)

    if gprc_18 is not None and gprc_3 is not None:
        print("\n  Hu2024 验证（GprC）：")
        ref18 = reference.get("GprC_ascr18", -8.29)
        ref3  = reference.get("GprC_ascr3",  -8.31)
        d18 = abs(gprc_18 - ref18)
        d3  = abs(gprc_3  - ref3)
        status18 = "PASS" if d18 <= tol else "FAIL"
        status3  = "PASS" if d3  <= tol else "FAIL"
        print(f"    ascr18: {gprc_18:.3f} vs {ref18} → Δ={d18:.2f}  [{status18}]")
        print(f"    ascr3:  {gprc_3:.3f} vs {ref3} → Δ={d3:.2f}  [{status3}]")

    # Kuo2024 验证（排名）
    gpr2_3  = next((r.best_affinity for r in results if r.pair_name == "Gpr2_ascr3"),  None)
    gpr2_7  = next((r.best_affinity for r in results if r.pair_name == "Gpr2_ascr7"),  None)
    gpr3_3  = next((r.best_affinity for r in results if r.pair_name == "Gpr3_ascr3"),  None)
    gpr3_7  = next((r.best_affinity for r in results if r.pair_name == "Gpr3_ascr7"),  None)

    if gpr2_3 is not None and gpr2_7 is not None:
        gpr2_ok = gpr2_7 < gpr2_3  # ascr7 更负 = 更强
        print(f"\n  Kuo2024 验证（排名）：")
        print(f"    Gpr2 ascr7 ({gpr2_7:.3f}) < ascr3 ({gpr2_3:.3f}): "
              f"{'PASS' if gpr2_ok else 'FAIL'} （期望 ascr7 亲和力更强）")
    if gpr3_3 is not None and gpr3_7 is not None:
        gpr3_ok = gpr3_3 < gpr3_7  # ascr3 更负 = 更强
        print(f"    Gpr3 ascr3 ({gpr3_3:.3f}) < ascr7 ({gpr3_7:.3f}): "
              f"{'PASS' if gpr3_ok else 'FAIL'} （期望 ascr3 亲和力更强）")

    logger.info("WT 单阶段对接完成")


if __name__ == "__main__":
    main()
