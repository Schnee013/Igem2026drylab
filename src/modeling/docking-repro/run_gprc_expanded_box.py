"""
S4: GprC 扩大 Docking Box — 捕获 Hu2024 外周关键残基

方案：GprC 专用 box=25Å（251³=15.8M 格点，< 27M 限制），对以下 pair 重对接：
  - GprC WT (ascr18, ascr3)    — 建立 25Å box WT 基线
  - GprC 突变体（config gprc_expanded_box.target_mutants）— 检测结合能变化

验证目标：
  N60A (N2.57) 已知（Hu2024）突变后丧失功能 → 预期 ΔΔG(ascr18) > 0
  R395A (R6.45?) 突变后亲和力剧降 → 预期 ΔΔG(ascr18) > 0

依赖：突变体 PDBQT 来自 mutagenesis 步骤已生成文件

用法（Windows）：
    python run_gprc_expanded_box.py
    python run_gprc_expanded_box.py --box-size 25  # 自定义 box（Å）
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir.parent / "docking"))
sys.path.insert(0, str(_this_dir))

from dock import DockingResult, dock_pair_twostage, get_tm_helix_ranges
from utils import (
    generate_run_id, get_project_root, load_config, preflight_check,
    save_results_json, setup_logging,
)


RECEPTOR_TM_PDBQT = "GprC_A0A437AGY2_tm.pdbqt"
RECEPTOR_TM_PDB   = "GprC_A0A437AGY2_tm.pdb"

# Orca DFT 输出命名约定：{name}_optimized.pdbqt
LIGAND_PDBQTS = {
    "ascr18": "ascr18_optimized.pdbqt",
    "ascr3":  "ascr3_optimized.pdbqt",
}

# 突变体 PDBQT：从 config gprc_expanded_box.target_mutants 动态构建
# 命名约定：GprC_{Mutation}_tm.pdbqt（mutagenesis.py 生成）


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="S4: GprC 扩大 Box 对接")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--box-size", type=float, default=25.0,
                        help="Stage2 box 边长 Å（默认 25，最大 ~29.7 = 27M 限制）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(root / config["paths"]["log_dir"], f"gprc_expanded_{run_id}")

    box_size = args.box_size
    spacing = config["vina"]["stage2"]["spacing"]
    n_pts = ((box_size / spacing) + 1) ** 3
    logger.info(
        f"S4 GprC 扩大 box 启动 [run_id={run_id}]"
        f"\n  box={box_size}Å, spacing={spacing}Å → {n_pts/1e6:.1f}M 格点"
    )
    if n_pts > 27e6:
        logger.error(f"Box {box_size}Å → {n_pts/1e6:.1f}M 格点超出 27M 限制！请减小 --box-size")
        sys.exit(1)

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"

    # 突变体 PDBQT 统一平铺目录（由 mutagenesis.py 生成并复制）
    mut_prepared_dir = root / config["paths"]["mutagenesis_dir"] / "prepared"

    # preflight 检查
    preflight_check([
        {"type": "file_exists",   "path": rec_dir / RECEPTOR_TM_PDBQT,
         "hint": "GprC 受体 PDBQT 不存在，请检查 prepared/receptors/"},
        {"type": "file_exists",   "path": rec_dir / RECEPTOR_TM_PDB,
         "hint": "GprC 受体 TM PDB 不存在，请检查 prepared/receptors/"},
        {"type": "file_exists",   "path": lig_dir / LIGAND_PDBQTS["ascr18"],
         "hint": "ascr18 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
        {"type": "file_exists",   "path": lig_dir / LIGAND_PDBQTS["ascr3"],
         "hint": "ascr3 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
    ], logger)

    results_base = root / config["paths"]["results_dir"]
    out_dir = results_base / f"gprc_box{int(box_size)}A"
    out_dir.mkdir(parents=True, exist_ok=True)

    rec_pdbqt = rec_dir / RECEPTOR_TM_PDBQT
    tm_pdb    = rec_dir / RECEPTOR_TM_PDB
    helix_ranges = get_tm_helix_ranges(config, "GprC")

    # 从 config 动态构建突变体 PDBQT 映射和阳性对照集合
    target_mutants = config.get("gprc_expanded_box", {}).get("target_mutants", [])
    mutant_pdbqts = {m: f"GprC_{m}_tm.pdbqt" for m in target_mutants}

    key_residues = config.get("analysis", {}).get("key_residues", {}).get("GprC", {})
    expected_loss_mutants = set()
    for _bw, info in key_residues.items():
        if info["role"] == "pos" and "远离" not in info.get("desc", ""):
            expected_loss_mutants.add(f"{info['resname']}{info['seqpos']}A")

    all_results: list[DockingResult] = []

    # ── WT（建立 25Å 基线）──────────────────────────────────────────────────
    for lig_name in ["ascr18", "ascr3"]:
        pair_name = f"GprC_WT_{lig_name}"
        lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]
        logger.info(f"[WT] {pair_name}")
        r = dock_pair_twostage(
            receptor_pdbqt=rec_pdbqt,
            ligand_pdbqt=lig_pdbqt,
            pair_name=pair_name,
            tm_pdb=tm_pdb,
            output_dir=out_dir / "poses" / pair_name,
            config=config,
            stage2_box_size=box_size,
            tm_helix_ranges=helix_ranges,
        )
        all_results.append(r)
        logger.info(f"  ΔG = {r.best_affinity:.3f} kcal/mol")

    wt_18 = next(r.best_affinity for r in all_results if "ascr18" in r.pair_name)
    wt_3  = next(r.best_affinity for r in all_results if "ascr3"  in r.pair_name)
    logger.info(f"WT 25Å baseline: ΔG(18)={wt_18:.3f}, ΔG(3)={wt_3:.3f}, sel={wt_18-wt_3:+.3f}")

    # ── 突变体 ────────────────────────────────────────────────────────────
    mut_results: dict[str, dict[str, float]] = {}

    for mut_name, mut_pdbqt_name in mutant_pdbqts.items():
        # 在多个可能路径中查找
        mut_pdbqt = None
        for search_dir in [mut_prepared_dir, rec_dir]:
            candidate = search_dir / mut_pdbqt_name
            if candidate.exists():
                mut_pdbqt = candidate
                break

        if mut_pdbqt is None:
            logger.warning(f"  突变体 PDBQT 不存在，跳过 {mut_name}: {mut_pdbqt_name}")
            continue

        mut_results[mut_name] = {}
        for lig_name in ["ascr18", "ascr3"]:
            pair_name = f"GprC_{mut_name}_{lig_name}"
            lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]
            logger.info(f"[Mut] {pair_name}")
            r = dock_pair_twostage(
                receptor_pdbqt=mut_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                pair_name=pair_name,
                tm_pdb=tm_pdb,
                output_dir=out_dir / "poses" / pair_name,
                config=config,
                stage2_box_size=box_size,
                tm_helix_ranges=helix_ranges,
            )
            all_results.append(r)
            mut_results[mut_name][lig_name] = r.best_affinity
            logger.info(f"  ΔG = {r.best_affinity:.3f} kcal/mol")

    # 保存（时间戳 + latest）
    out_json = save_results_json(
        [asdict(r) for r in all_results], out_dir, run_id, config,
    )

    # 打印分析
    print("\n" + "=" * 65)
    print(f"  S4 GprC 扩大 Box ({box_size}Å) 结果")
    print("=" * 65)
    print(f"  WT 基线 (25Å): ΔG(18)={wt_18:.3f}, ΔG(3)={wt_3:.3f}, sel={wt_18-wt_3:+.3f}")
    print()
    print(f"  {'突变':<8} {'ΔG(18)':<10} {'ΔG(3)':<10} {'ΔΔG(18)':<10} {'ΔΔG_sel':<10} {'验证'}")
    print("  " + "-" * 62)
    for mut_name, ligs in mut_results.items():
        if "ascr18" not in ligs or "ascr3" not in ligs:
            continue
        dg18 = ligs["ascr18"]
        dg3  = ligs["ascr3"]
        ddg18 = dg18 - wt_18
        ddg3  = dg3  - wt_3
        ddg_sel = ddg18 - ddg3

        # 验证：N60A/R395A 应显示亲和力损失（Hu2024 阳性对照）
        expected_loss = mut_name in expected_loss_mutants
        check = ("✓ 符合预期" if expected_loss and ddg18 > 0.1
                 else "✗ 与预期不符" if expected_loss and ddg18 < -0.1
                 else "")
        print(
            f"  {mut_name:<8} {dg18:>8.3f}  {dg3:>8.3f}  "
            f"{ddg18:>+8.3f}  {ddg_sel:>+8.3f}  {check}"
        )

    pos_names = "/".join(sorted(expected_loss_mutants)) or "无"
    print(f"\n  {pos_names} 验证：若 ΔΔG(ascr18) > 0 → 阳性对照成立")
    print(f"  结果文件: {out_json}")
    logger.info("S4 GprC 扩大 box 完成")


if __name__ == "__main__":
    main()
