"""
GprC Saturation Scan（5 位点 × 18 AA = 90 突变体）

位点选择依据：alanine scan channel 信号最强 + IFP 差异接触（见计划 §Part B）
  L377  sel_mut=-0.758  Channel A（ascr18，caveat）
  N378  sel_mut=+0.957  Channel B（ascr3，caveat，最强）
  Q411  sel_mut=+0.652  Channel B（caveat）
  V91   sel_mut=+0.525  Channel B（caveat）
  R174  neutral         IFP ascr3=25 vs ascr18=18（差异最大）

注意：saturation 结果**不**自动打 GprC-ala caveat——caveat 是 alanine scan 专属判定，
saturation 结果按正常 sel_mut 阈值评估（< −0.477 → Channel A，> +0.477 → Channel B）。

依赖（运行前需准备）：
  - WT 单阶段基线：experiments/docking-repro/results/wt_singlestage/docking_results.json
  - 配体：experiments/docking-repro/prepared/ligands/ascr{18,3}_optimized.pdbqt
  - GprC TM PDB：experiments/docking-repro/prepared/receptors/GprC_A0A437AGY2_tm.pdb
  - AF3 突变体 PDBQT：
      experiments/docking-repro/mutagenesis/af3_prepared/GprC/saturation/{Label}_tm.pdbqt

完整执行流程（FASTA 生成 → AF3 提交 → 结构处理）：
    见 ~/.claude/plans/sequential-dancing-origami.md §Part B

用法（Windows）：
    python run_saturation_gprc.py
    python run_saturation_gprc.py --project-root D:\\\\drylab-tools\\\\workspace
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

# GprC saturation scan 位点（5 位点 × 18 AA = 90 突变体）
SATURATION_RESIDUES = {
    "GprC": [377, 378, 411, 91, 174],  # L377, N378, Q411, V91, R174
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GprC Saturation Scan（5 位点 × 18 AA）")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
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

    root = get_project_root(config)
    run_id = generate_run_id()
    logger = setup_logging(
        root / config["paths"]["log_dir"],
        f"mutagenesis_saturation_gprc_{run_id}",
    )

    # 配置：饱和扫描，排除 Ala（已在 alanine scan 中完成）
    config["mutagenesis"]["wt_baseline"] = "repro"
    config["mutagenesis"]["mutant_source"] = "af3"
    config["mutagenesis"]["docking_mode"] = "singlestage"
    config["mutagenesis"]["scan_type"] = "saturation"
    config["mutagenesis"]["exclude_aas"] = ["A"]
    config["mutagenesis"]["target_receptors"] = list(SATURATION_RESIDUES.keys())
    # PDBQT 在 af3_prepared/GprC/saturation/ 子目录
    config["mutagenesis"]["mutant_pdbqt_subdir"] = "saturation"

    # 覆盖 scan_residues 为 GprC 5 个目标位点
    config["mutagenesis"]["scan_residues"] = SATURATION_RESIDUES

    prepared_root = root / config["paths"]["prepared_dir"]
    rec_dir = prepared_root / "receptors"
    lig_dir = prepared_root / "ligands"
    mut_dir = root / config["paths"]["mutagenesis_dir"]

    # preflight 检查
    rec_name = "GprC"
    rec_cfg = config["receptors"][rec_name]
    tm_pdb_name = Path(rec_cfg["pdb_file"]).stem + "_tm.pdb"
    wt_baseline_dir = (
        root / config["paths"]["results_dir"] / config["paths"]["wt_singlestage_subdir"]
    )
    wt_baseline_file = config["paths"].get("results_filename", "docking_results.json")

    checks = [
        {
            "type": "file_exists",
            "path": wt_baseline_dir / wt_baseline_file,
            "hint": "WT 单阶段基线不存在，请先运行 run_wt_singlestage.py",
        },
        {
            "type": "file_exists",
            "path": lig_dir / "ascr18_optimized.pdbqt",
            "hint": "ascr18 配体不存在",
        },
        {
            "type": "file_exists",
            "path": lig_dir / "ascr3_optimized.pdbqt",
            "hint": "ascr3 配体不存在",
        },
        {
            "type": "file_exists",
            "path": rec_dir / tm_pdb_name,
            "hint": f"GprC TM PDB 不存在：{rec_dir / tm_pdb_name}",
        },
        {
            "type": "file_exists",
            "path": mut_dir / "af3_prepared" / rec_name / "saturation",
            "hint": (
                "GprC saturation PDBQT 目录不存在。\n"
                "请先完成 AF3 提交 + 结构处理（Step 3-4），\n"
                f"并将 PDBQT 放入：{mut_dir}/af3_prepared/GprC/saturation/"
            ),
        },
    ]
    preflight_check(checks, logger)

    wt_baseline = load_wt_baseline(root, config)
    logger.info(f"已加载 WT 基线（{len(wt_baseline)} 对）")

    total_muts = len(SATURATION_RESIDUES[rec_name]) * 18  # 20 AA - WT - Ala = 18
    logger.info(
        f"GprC Saturation Scan 启动 [run_id={run_id}]"
        f"\n  位点: {SATURATION_RESIDUES[rec_name]}"
        f"\n  预计突变数: {total_muts}（每突变 × 2 配体）"
        f"\n  预计对接数: {total_muts * 2}"
        f"\n  预计用时: ~{total_muts * 4 // 60}-{total_muts * 6 // 60} 小时"
    )

    results = run_mutagenesis(config, wt_dock_results=wt_baseline)

    if not results:
        logger.error("扫描无结果，请检查日志")
        sys.exit(1)

    logger.info(f"GprC Saturation Scan 完成：{len(results)} 个突变体")

    # 打印汇总
    print(f"\n{'='*70}")
    print(f"  GprC Saturation Scan 汇总（ΔΔG_sel < 0 → 增强 ascr18 偏好）")
    print(f"{'='*70}")
    # run_mutagenesis 已按 ddg_selectivity 排序，无需重复
    wt_sel = (
        wt_baseline.get(f"{rec_name}_ascr18", 0.0)
        - wt_baseline.get(f"{rec_name}_ascr3", 0.0)
    )
    print(f"\n  {rec_name}  (WT sel_wt = {wt_sel:+.3f})")
    print(f"  {'突变':<10} {'ΔΔG(18)':<10} {'ΔΔG(3)':<10} {'ΔΔG_sel':<10} {'Channel'}")
    print("  " + "-" * 55)
    for r in results:
        # 按阈值初步判断 channel（saturation 不打 GprC-ala caveat）
        if r.ddg_selectivity < -0.477:
            ch = "A (ascr18↑)"
        elif r.ddg_selectivity > 0.477:
            ch = "B (ascr3↑)"
        else:
            ch = "—"
        print(
            f"  {r.mutation:<10}  {r.ddg_ascr18:>+8.3f}  {r.ddg_ascr3:>+8.3f}"
            f"  {r.ddg_selectivity:>+8.3f}  {ch}"
        )
    print(f"{'='*70}")

    out_dir = root / config["paths"]["mutagenesis_dir"]
    print(f"\n  完整 JSON: {out_dir}/mutagenesis_results.json")


if __name__ == "__main__":
    main()
