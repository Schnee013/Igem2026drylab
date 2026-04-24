"""
S2: 多 Seed 方差评估 — 量化 Vina 随机噪声，为关键结果提供统计置信度

问题：所有对接使用单一 seed=42，无统计误差棒。
      iGEM 评审期望结果具备统计可信度。

策略：
  1. WT 受体（GprC/Gpr2/Gpr3）× 配体 × 5 seeds = 多次对接
  2. Channel A 候选（Gpr2 M327A, R59A, Gpr3 I141A）× 配体 × 5 seeds
  3. 计算 mean ± SD，报告 95% CI 和 ΔΔG_sel 统计显著性

依赖：
  - S1 完成后可用 wt_twostage 结果校验
  - 使用 v2 prepared PDBQTs（同 S1）
  - 突变体 PDBQT 来自 mutagenesis 已生成的文件

用法（Windows）：
    python run_multiseed.py
    python run_multiseed.py --wt-only                        # 仅跑 WT（更快）
    python run_multiseed.py --seeds 42 123 456               # 自定义 seed 列表
    python run_multiseed.py --ligands ascr7                  # 仅跑指定配体
    python run_multiseed.py --ligands ascr7 --wt-only        # ascr7 WT only
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from dock import (
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

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

DEFAULT_SEEDS = [42, 123, 456, 789, 1024]

# WT 受体文件（v2 prepared，TM-only）
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

# 方差评估的突变体（Channel A 候选，2026-04-10 更新）
# PDBQT 由 mutagenesis.py 生成后复制到 mutagenesis/af3_prepared/（按受体子目录）。
TOP_MUTANTS = {
    ("Gpr2", "M327A"): "Gpr2_M327A_tm.pdbqt",
    ("Gpr2", "R59A"):  "Gpr2_R59A_tm.pdbqt",
    ("Gpr3", "I141A"): "Gpr3_I141A_tm.pdbqt",
}


def _stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return {"mean": mean, "sd": float("nan"), "ci95": float("nan"), "n": n, "values": values}
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    sd = math.sqrt(var)
    # 95% CI（t 分布；n-1 自由度，超出表则用正态近似 1.960）
    t_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 9: 2.262}.get(n - 1, 1.960)
    ci = t_95 * sd / math.sqrt(n)
    return {"mean": mean, "sd": sd, "ci95": ci, "n": n, "values": values}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="S2: 多 seed 方差评估")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--wt-only", action="store_true", help="仅跑 WT，跳过突变体")
    parser.add_argument(
        "--ligands", nargs="+", default=None,
        help="仅跑指定配体（如 --ligands ascr7），默认跑所有配体"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(root / config["paths"]["log_dir"], f"multiseed_{run_id}")
    logger.info(f"S2 多 seed 方差评估启动 [run_id={run_id}, seeds={args.seeds}]")

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"
    mut_dir = root / config["paths"]["mutagenesis_dir"] / "prepared"

    # preflight 检查
    active_ligands_check = args.ligands if args.ligands else list(LIGAND_PDBQTS.keys())
    preflight_check(
        [{"type": "file_exists", "path": lig_dir / LIGAND_PDBQTS[lg],
          "hint": f"{lg} 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"}
         for lg in active_ligands_check]
        + [{"type": "file_exists", "path": rec_dir / RECEPTOR_PDBQTS[rc],
            "hint": f"{rc} 受体 PDBQT 不存在，请检查 prepared/receptors/"}
           for rc in ["GprC", "Gpr2", "Gpr3"]],
        logger,
    )

    out_dir = get_results_subdir(config, "multiseed_subdir")

    # 汇总：{pair_name: {seed: affinity}}
    all_raw: dict[str, list[float]] = {}

    # ── WT 对接 ─────────────────────────────────────────────────────────────
    active_ligands = args.ligands if args.ligands else list(LIGAND_PDBQTS.keys())
    wt_pairs = [
        (rec, lig)
        for rec in ["GprC", "Gpr2", "Gpr3"]
        for lig in active_ligands
    ]
    total_wt = len(wt_pairs) * len(args.seeds)
    done = 0

    for rec_name, lig_name in wt_pairs:
        pair_name = f"{rec_name}_{lig_name}"
        all_raw[pair_name] = []
        rec_pdbqt = rec_dir / RECEPTOR_PDBQTS[rec_name]
        tm_pdb    = rec_dir / RECEPTOR_TM_PDBS[rec_name]
        lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]
        helix_ranges = get_tm_helix_ranges(config, rec_name)
        box_offset = get_box_center_offset(config, rec_name)
        rec_box_size = get_receptor_box_size(config, rec_name)
        manual_center = get_manual_box_center(config, rec_name)

        for seed in args.seeds:
            done += 1
            logger.info(f"[WT {done}/{total_wt}] {pair_name} seed={seed}")
            pair_out = out_dir / "poses" / f"{pair_name}_seed{seed}"
            r = dock_pair_singlestage(
                receptor_pdbqt=rec_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                pair_name=f"{pair_name}_s{seed}",
                tm_pdb=tm_pdb,
                output_dir=pair_out,
                config=config,
                seed=seed,
                tm_helix_ranges=helix_ranges,
                box_center_offset=box_offset,
                receptor_box_size=rec_box_size,
                manual_box_center=manual_center,
            )
            all_raw[pair_name].append(r.best_affinity)
            logger.info(f"  ΔG = {r.best_affinity:.3f} kcal/mol")

    # ── 突变体对接 ──────────────────────────────────────────────────────────
    if not args.wt_only:
        mut_total = len(TOP_MUTANTS) * len(active_ligands) * len(args.seeds)
        mut_done = 0

        for (rec_name, mut_name), mut_pdbqt_name in TOP_MUTANTS.items():
            mut_pdbqt = mut_dir / mut_pdbqt_name
            if not mut_pdbqt.exists():
                logger.warning(f"突变体 PDBQT 不存在，跳过: {mut_pdbqt}")
                continue

            tm_pdb = rec_dir / RECEPTOR_TM_PDBS[rec_name]
            helix_ranges = get_tm_helix_ranges(config, rec_name)
            box_offset = get_box_center_offset(config, rec_name)
            rec_box_size = get_receptor_box_size(config, rec_name)
            manual_center = get_manual_box_center(config, rec_name)

            for lig_name in active_ligands:
                pair_name = f"{rec_name}_{mut_name}_{lig_name}"
                all_raw[pair_name] = []
                lig_pdbqt = lig_dir / LIGAND_PDBQTS[lig_name]

                for seed in args.seeds:
                    mut_done += 1
                    logger.info(f"[Mut {mut_done}/{mut_total}] {pair_name} seed={seed}")
                    pair_out = out_dir / "poses" / f"{pair_name}_seed{seed}"
                    r = dock_pair_singlestage(
                        receptor_pdbqt=mut_pdbqt,
                        ligand_pdbqt=lig_pdbqt,
                        pair_name=f"{pair_name}_s{seed}",
                        tm_pdb=tm_pdb,
                        output_dir=pair_out,
                        config=config,
                        seed=seed,
                        tm_helix_ranges=helix_ranges,
                        box_center_offset=box_offset,
                        receptor_box_size=rec_box_size,
                        manual_box_center=manual_center,
                    )
                    all_raw[pair_name].append(r.best_affinity)

    # ── 统计分析 ────────────────────────────────────────────────────────────
    stats: dict[str, dict] = {k: _stats(v) for k, v in all_raw.items() if v}

    out_json = save_results_json(
        stats, out_dir, run_id, config, filename="multiseed_stats.json",
    )

    # 打印结果表
    print("\n" + "=" * 70)
    print("  S2 多 Seed 方差评估结果")
    print(f"  Seeds: {args.seeds}  (n={len(args.seeds)})")
    print("=" * 70)
    print(f"  {'对接对':<28} {'mean':>8} {'±SD':>7} {'95%CI':>8}")
    print("-" * 60)
    for pair_name, s in stats.items():
        print(f"  {pair_name:<28} {s['mean']:>8.3f} {s['sd']:>7.3f} ±{s['ci95']:>6.3f}")

    # ΔΔG_sel 统计（仅 WT）
    print("\n  WT 选择性统计（ΔG_sel = ΔG(18) - ΔG(3)，mean ± CI）：")
    print("-" * 60)
    for rec in ["GprC", "Gpr2", "Gpr3"]:
        k18 = f"{rec}_ascr18"
        k3  = f"{rec}_ascr3"
        if k18 in stats and k3 in stats:
            # 每次 seed 的 ΔG_sel
            sel_values = [
                a - b
                for a, b in zip(stats[k18]["values"], stats[k3]["values"])
            ]
            sel = _stats(sel_values)
            print(
                f"  {rec}: ΔG_sel = {sel['mean']:+.3f} ± {sel['ci95']:.3f} "
                f"(SD={sel['sd']:.3f})"
            )

    # ΔΔG_sel 统计（突变体）— 使用 seed-paired 差异（更准确，反映 WT+mut 联合方差）
    if not args.wt_only:
        print("\n  突变体 ΔΔG_sel 统计（seed-paired）：")
        print("-" * 60)
        # seed-paired：同一 seed 的突变体 ΔG 减去同 seed 的 WT ΔG，避免 WT mean 作固定锚点低估方差
        for (rec_name, mut_name), _ in TOP_MUTANTS.items():
            k_mut_18 = f"{rec_name}_{mut_name}_ascr18"
            k_mut_3  = f"{rec_name}_{mut_name}_ascr3"
            k_wt_18  = f"{rec_name}_ascr18"
            k_wt_3   = f"{rec_name}_ascr3"
            if any(k not in stats for k in [k_mut_18, k_mut_3, k_wt_18, k_wt_3]):
                continue

            wt_18_vals  = stats[k_wt_18]["values"]
            wt_3_vals   = stats[k_wt_3]["values"]
            mut_18_vals = stats[k_mut_18]["values"]
            mut_3_vals  = stats[k_mut_3]["values"]

            # seed-paired ΔΔG_sel = (mut18_i - wt18_i) - (mut3_i - wt3_i)
            ddg_sel_values = [
                (m18 - w18) - (m3 - w3)
                for m18, w18, m3, w3 in zip(mut_18_vals, wt_18_vals, mut_3_vals, wt_3_vals)
            ]
            ddg = _stats(ddg_sel_values)
            sig = "✓ 显著" if abs(ddg["mean"]) > ddg["ci95"] else "✗ 不显著"
            print(
                f"  {rec_name} {mut_name}: ΔΔG_sel = {ddg['mean']:+.3f} "
                f"± {ddg['ci95']:.3f}  {sig}"
            )

    print(f"\n  详细数据: {out_json}")
    logger.info("S2 多 seed 方差评估完成")


if __name__ == "__main__":
    main()
