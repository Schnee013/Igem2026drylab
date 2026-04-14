"""
⚠️ SUPERSEDED — 本脚本基于 v2 MMFF alanine scan 结论（Y200A/Y378A 为 Channel A 候选）。
Orca DFT + ICL3 截断修复后，Y200A/Y378A 降为 neutral。
当前 Channel A 位点为 M327A/R59A（Gpr2）和 I141A（Gpr3）。
饱和扫描已改用 generate_saturation_fastas.py（2026-04-10）。
保留本脚本仅作为历史参考和 pipeline 测试用途。

---
原始 S3: Gpr2 Y200/Y378 饱和突变扫描

背景（已过时）：
  v2 Alanine scan 发现 Gpr2 Y200A (ΔΔG_sel=+1.12) 和 Y378A (+0.92)——
  这些结果基于 MMFF 配体和错误的两阶段协议，已被 2026-04-10 最终结果取代。

依赖：
  - S1（run_wt_twostage.py）已完成，wt_twostage/docking_results.json 存在
  - 否则退回到 v2 WT 基线（降精度但不阻塞）

用法（Windows）：
    python run_saturation_gpr2.py
    python run_saturation_gpr2.py --use-v2-wt     # 强制使用 v2 WT 基线
    python run_saturation_gpr2.py --residues 200  # 仅扫描 Y200
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir.parent / "docking"))
sys.path.insert(0, str(_this_dir))

from mutagenesis import run_mutagenesis
from utils import generate_run_id, get_project_root, load_config, preflight_check, setup_logging


# 排除的氨基酸（同已扫描的 A，加上结构破坏性的 P/C）
EXCLUDE_AAS = ["A", "P", "C"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="S3: Gpr2 Y200/Y378 饱和扫描")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--residues", nargs="+", type=int, default=[200, 378],
                        help="扫描的残基编号（默认 200 378）")
    parser.add_argument("--use-v2-wt", action="store_true",
                        help="强制使用 v2 WT 基线（S1 未完成时使用）")
    return parser.parse_args()


def load_wt_baseline(root: Path, use_v2: bool, config: dict) -> dict[str, float] | None:
    """
    优先加载 S1 两阶段 WT 基线；S1 未完成时退回 v2 基线并警告。
    返回 {pair_name: best_affinity}，None 表示让 run_mutagenesis 自行加载。
    """
    if not use_v2:
        s1_json = root / config["paths"]["results_dir"] / config["paths"]["wt_twostage_subdir"] / config["paths"].get("results_filename", "docking_results.json")
        if s1_json.exists():
            raw = json.loads(s1_json.read_text(encoding="utf-8"))
            baseline = {r["pair_name"]: r["best_affinity"] for r in raw}
            print(f"[S3] 使用 S1 两阶段 WT 基线（{s1_json}）")
            for k, v in sorted(baseline.items()):
                print(f"     {k}: {v:.3f} kcal/mol")
            return baseline
        else:
            print(
                f"[S3] 警告: S1 WT 基线不存在 ({s1_json})\n"
                f"     退回到 v2 WT 基线（误差 ~0.7 kcal/mol，但方向可信）"
            )

    # 退回 v2 基线（run_mutagenesis 自行从 wt_baseline="v2" 加载）
    return None


def make_saturation_config(base_config: dict, residues: list[int], use_v2_wt: bool) -> dict:
    """构建饱和扫描专用 config（深拷贝，不修改原 config）。"""
    cfg = copy.deepcopy(base_config)

    cfg["mutagenesis"]["scan_type"] = "saturation"
    cfg["mutagenesis"]["target_receptors"] = ["Gpr2"]
    cfg["mutagenesis"]["scan_residues"] = {"Gpr2": residues}
    cfg["mutagenesis"]["exclude_aas"] = EXCLUDE_AAS

    # WT 基线来源（S1 完成则用 repro 模式；否则 v2）
    cfg["mutagenesis"]["wt_baseline"] = "v2" if use_v2_wt else "repro"

    # 输出到独立子目录，不覆盖 alanine scan 结果
    cfg["paths"]["mutagenesis_dir"] = (
        cfg["paths"].get("mutagenesis_dir", "experiments/docking-repro/mutagenesis")
        .rstrip("/") + "_saturation_gpr2"
    )

    return cfg


def print_saturation_summary(results: list) -> None:
    """打印饱和扫描结果：按 ΔΔG_sel 分残基排名。"""
    from collections import defaultdict
    by_res: dict[int, list] = defaultdict(list)
    for r in results:
        by_res[r.residue_num].append(r)

    print("\n" + "=" * 70)
    print("  S3 Gpr2 饱和扫描结果（各位点最优替换 Top-10）")
    print("  ΔΔG_sel < 0 → 增强 ascr18 偏好；> 0 → 增强 ascr3 偏好")
    print("=" * 70)

    for resnum in sorted(by_res.keys()):
        res_results = sorted(by_res[resnum], key=lambda r: r.ddg_selectivity)
        wt_aa = res_results[0].wt_residue if res_results else "?"
        print(f"\n  位置 {resnum}（WT = {wt_aa}）  [负值更优]")
        print(f"  {'替换':<6} {'ΔΔG(18)':<10} {'ΔΔG(3)':<10} {'ΔΔG_sel':<10} {'解读'}")
        print("  " + "-" * 60)

        for r in res_results[:10]:
            mut_label = f"{wt_aa}{resnum}{r.mut_residue}"
            interp = (
                "✓✓ 增强 ascr18" if r.ddg_selectivity < -0.5
                else "✓ 轻微增强" if r.ddg_selectivity < 0
                else "— 中性"     if abs(r.ddg_selectivity) < 0.2
                else "✗ 增强 ascr3"
            )
            print(
                f"  {mut_label:<6}  {r.ddg_ascr18:>+8.3f}  "
                f"{r.ddg_ascr3:>+8.3f}  {r.ddg_selectivity:>+8.3f}  {interp}"
            )

    print("\n  [湿实验建议]")
    top_candidates = sorted(
        [r for results_list in by_res.values() for r in results_list],
        key=lambda r: r.ddg_selectivity
    )[:5]
    for i, r in enumerate(top_candidates, 1):
        wt_aa = r.wt_residue
        mut_label = f"{wt_aa}{r.residue_num}{r.mut_residue}"
        print(
            f"  {i}. Gpr2 {mut_label}: ΔΔG_sel = {r.ddg_selectivity:+.3f} kcal/mol"
            f"  → 优先定点突变"
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
        f"saturation_gpr2_{run_id}"
    )

    # preflight 检查
    prepared_root = root / config["paths"]["prepared_dir"]
    lig_dir = prepared_root / "ligands"
    rec_dir = prepared_root / "receptors"
    preflight_check([
        {"type": "file_exists", "path": lig_dir / "ascr18_optimized.pdbqt",
         "hint": "ascr18 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
        {"type": "file_exists", "path": lig_dir / "ascr3_optimized.pdbqt",
         "hint": "ascr3 配体不存在，请先完成 Orca 配体准备（run_prepare_ligands.py）"},
        {"type": "file_exists", "path": rec_dir / "Gpr2_G1X9E2_tm.pdbqt",
         "hint": "Gpr2 受体 PDBQT 不存在，请检查 prepared/receptors/"},
    ], logger)

    logger.info(
        f"S3 Gpr2 饱和扫描启动 [run_id={run_id}, residues={args.residues}]"
    )
    logger.info(f"  扫描位点: Gpr2 {args.residues}")
    logger.info(f"  排除氨基酸: {EXCLUDE_AAS}（Ala 已测/Pro 扰骨架/Cys 二硫）")
    logger.info(
        f"  预计突变数: {len(args.residues)} × {20 - len(EXCLUDE_AAS)} = "
        f"{len(args.residues) * (20 - len(EXCLUDE_AAS))} 个"
    )

    # 加载 WT 基线（优先 S1 两阶段结果）
    wt_baseline = load_wt_baseline(root, args.use_v2_wt, config)

    # 构建饱和扫描专用 config
    sat_config = make_saturation_config(config, args.residues, args.use_v2_wt)

    # 注入 exclude_aas 到 mutagenesis.make_saturation_scan_mutations
    # （通过 config 传入，mutagenesis.py 已支持 config["mutagenesis"]["exclude_aas"]）
    # 兼容性：若 mutagenesis.py 不读 exclude_aas，需确认版本
    logger.info(
        f"WT 基线来源: {'S1 两阶段' if wt_baseline else 'v2（退回）'}"
    )

    # 执行扫描
    results = run_mutagenesis(sat_config, wt_dock_results=wt_baseline)

    if not results:
        logger.error("饱和扫描无结果，请检查日志")
        sys.exit(1)

    logger.info(f"饱和扫描完成：{len(results)} 个突变体")

    # 打印汇总
    print_saturation_summary(results)

    # 输出文件路径
    out_dir = root / sat_config["paths"]["mutagenesis_dir"]
    print(f"\n  完整 JSON: {out_dir}/mutagenesis_results.json")
    print(f"  完整报告: {out_dir}/mutagenesis_report.md")
    logger.info("S3 完成")


if __name__ == "__main__":
    main()
