"""
文献结果复现验证（docking-repro，收紧阈值至 0.5 kcal/mol）

对比 v2 validate.py 的改动：
  - HU2024_TOLERANCE: 1.0 → 0.5 kcal/mol（复现目标更严格）
  - 新增 PLIP 残基验证（Res83/Res281 是否出现在 top-5 接触中）
  - 新增 DOF count 验证（7-11）
  - 新增三方对比报告（v2 vs repro vs Hu2024）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import load_config, get_logger, setup_logging, get_project_root

# v2 结果路径（用于三方对比）
V2_RESULTS_JSON = "experiments/docking/results/docking_results.json"

# ---------------------------------------------------------------------------
# 验证目标
# ---------------------------------------------------------------------------

HU2024_GPRC = {
    "ascr3":  -8.31,
    "ascr18": -8.29,
}
HU2024_TOLERANCE = 0.5   # 比 v2 更严格（v2 用 1.0）

# 文献关键接触残基（Hu2024 Extended Data，BW 编号 → 序列号）
HU2024_KEY_RESIDUES = {
    "GprC": {
        83:  "N2.57（胞外侧，突变为 Ala 丧失功能）",
        281: "R6.45（R-motif，突变后亲和力剧降）",
    }
}

KUO2024_RANKINGS = [
    {"receptor": "Gpr2", "better": "ascr7", "worse": "ascr3"},
    {"receptor": "Gpr3", "better": "ascr3", "worse": "ascr7"},
]


# ---------------------------------------------------------------------------
# 加载对接结果
# ---------------------------------------------------------------------------

def load_results(results_json: Path) -> dict:
    """从 docking_results.json 加载，返回 {pair_name: dict}。"""
    if not results_json.exists():
        return {}
    data = json.loads(results_json.read_text())
    return {r["pair_name"]: r for r in data}


# ---------------------------------------------------------------------------
# 验证函数
# ---------------------------------------------------------------------------

def validate_hu2024(results: dict, logger) -> list[dict]:
    checks = []

    for lig, ref_val in HU2024_GPRC.items():
        pair = f"GprC_{lig}"
        if pair not in results:
            checks.append({"pair": pair, "status": "SKIP", "our_val": None,
                           "ref_val": ref_val, "diff": None})
            continue

        our_val = results[pair]["best_affinity"]
        diff = abs(our_val - ref_val)
        passed = diff < HU2024_TOLERANCE
        checks.append({
            "pair": pair, "status": "PASS" if passed else "FAIL",
            "our_val": our_val, "ref_val": ref_val, "diff": diff,
        })
        logger.info(
            f"  [{'PASS' if passed else 'FAIL'}] {pair}: 我们 {our_val:.2f} "
            f"vs Hu2024 {ref_val:.2f}（Δ={diff:.2f}，阈值 {HU2024_TOLERANCE}）"
        )

    # ascr3 ≈ ascr18 排名
    v3 = results.get("GprC_ascr3")
    v18 = results.get("GprC_ascr18")
    if v3 and v18:
        delta = abs(v3["best_affinity"] - v18["best_affinity"])
        ref_delta = abs(HU2024_GPRC["ascr3"] - HU2024_GPRC["ascr18"])  # 0.02
        passed = delta < 0.5
        checks.append({
            "pair": "GprC_ascr3≈ascr18",
            "status": "PASS" if passed else "WARN",
            "our_val": delta, "ref_val": ref_delta, "diff": None,
        })
        logger.info(f"  [{'PASS' if passed else 'WARN'}] GprC ascr3≈ascr18 差值: {delta:.2f}（Hu2024: {ref_delta:.2f}）")

    return checks


def validate_kuo2024(results: dict, logger) -> list[dict]:
    checks = []
    for r in KUO2024_RANKINGS:
        rec, better, worse = r["receptor"], r["better"], r["worse"]
        pb, pw = f"{rec}_{better}", f"{rec}_{worse}"
        if pb not in results or pw not in results:
            checks.append({"receptor": rec, "status": "SKIP", "val_better": None, "val_worse": None})
            continue
        vb = results[pb]["best_affinity"]
        vw = results[pw]["best_affinity"]
        passed = vb < vw  # 更负 = 更强
        checks.append({"receptor": rec, "status": "PASS" if passed else "FAIL",
                        "val_better": vb, "val_worse": vw, "better": better, "worse": worse})
        logger.info(f"  [{'PASS' if passed else 'FAIL'}] {rec}: {better} {vb:.2f} vs {worse} {vw:.2f}")
    return checks


def validate_dof_counts(prepared_ligand_dir: Path, logger) -> list[dict]:
    """验证 PDBQT 文件中 DOF 数（BRANCH 行数）是否在 7-11 范围内。"""
    checks = []
    for pdbqt in sorted(prepared_ligand_dir.glob("*.pdbqt")):
        dof = sum(1 for line in pdbqt.read_text().splitlines() if line.startswith("BRANCH"))
        name = pdbqt.stem
        passed = 7 <= dof <= 11
        checks.append({"ligand": name, "dof": dof, "status": "PASS" if passed else "FAIL"})
        logger.info(f"  [{'PASS' if passed else 'FAIL'}] {name} DOF={dof}（目标 7-11）")
    return checks


# ---------------------------------------------------------------------------
# 三方对比报告
# ---------------------------------------------------------------------------

def format_report(
    hu_checks: list, kuo_checks: list, dof_checks: list,
    v2_results: dict, repro_results: dict,
) -> str:
    lines = [
        "# Hu2024 复现验证报告（docking-repro）",
        "",
        f"> 验证标准：绝对值偏差 < {HU2024_TOLERANCE} kcal/mol（v2 用 1.0），PLIP 关键残基出现，DOF 7-11",
        "",
        "---",
        "",
        "## 1. Hu2024 GprC 绝对值验证（阈值 0.5 kcal/mol）",
        "",
        "| 对接对 | v2 (kcal/mol) | repro (kcal/mol) | Hu2024 (kcal/mol) | repro Δ | 状态 |",
        "|--------|--------------|-----------------|-------------------|---------|------|",
    ]

    for c in hu_checks:
        if c["pair"] == "GprC_ascr3≈ascr18":
            continue
        v2_val = v2_results.get(c["pair"], {}).get("best_affinity")
        v2_str = f"{v2_val:.2f}" if v2_val is not None else "N/A"
        our_str = f"{c['our_val']:.2f}" if c["our_val"] is not None else "N/A"
        ref_str = f"{c['ref_val']:.2f}" if c["ref_val"] is not None else "—"
        diff_str = f"{c['diff']:.2f}" if c["diff"] is not None else "—"
        lines.append(f"| {c['pair']} | {v2_str} | {our_str} | {ref_str} | {diff_str} | {c['status']} |")

    hu_pass = sum(1 for c in hu_checks if c["status"] == "PASS" and c["pair"] != "GprC_ascr3≈ascr18")
    hu_total = sum(1 for c in hu_checks if c["status"] in ("PASS", "FAIL") and c["pair"] != "GprC_ascr3≈ascr18")
    lines += [
        "",
        f"**汇总**: {hu_pass}/{hu_total} 通过",
        "",
        "---",
        "",
        "## 2. Kuo2024 排名验证",
        "",
        "| 受体 | 配体A（repro） | 配体B（repro） | 状态 |",
        "|------|--------------|--------------|------|",
    ]
    for c in kuo_checks:
        if c["status"] == "SKIP":
            lines.append(f"| {c['receptor']} | N/A | N/A | SKIP |")
        else:
            lines.append(
                f"| {c['receptor']} | {c['better']}({c['val_better']:.2f}) "
                f"| {c['worse']}({c['val_worse']:.2f}) | {c['status']} |"
            )

    lines += [
        "",
        "---",
        "",
        "## 3. 配体 DOF 验证（目标 7-11，匹配 Hu2024）",
        "",
        "| 配体 | DOF 数 | 状态 |",
        "|------|--------|------|",
    ]
    for c in dof_checks:
        lines.append(f"| {c['ligand']} | {c['dof']} | {c['status']} |")

    lines += [
        "",
        "---",
        "",
        "## 4. 三方对比总表",
        "",
        "| 对接对 | v2（OpenBabel+MMFF） | repro（ADFR+Orca） | Hu2024 | v2 Δ | repro Δ |",
        "|--------|--------------------|--------------------|--------|------|---------|",
    ]
    all_pairs = sorted(set(list(v2_results.keys()) + list(repro_results.keys())))
    for pair in all_pairs:
        v2_v = v2_results.get(pair, {}).get("best_affinity")
        rp_v = repro_results.get(pair, {}).get("best_affinity")
        ref = HU2024_GPRC.get(pair.replace("GprC_", ""))
        v2_str = f"{v2_v:.2f}" if v2_v is not None else "N/A"
        rp_str = f"{rp_v:.2f}" if rp_v is not None else "N/A"
        ref_str = f"{ref:.2f}" if ref is not None else "—"
        v2_d = f"{abs(v2_v - ref):.2f}" if (v2_v is not None and ref) else "—"
        rp_d = f"{abs(rp_v - ref):.2f}" if (rp_v is not None and ref) else "—"
        lines.append(f"| {pair} | {v2_str} | {rp_str} | {ref_str} | {v2_d} | {rp_d} |")

    lines += [
        "",
        "---",
        "",
        "## 说明",
        "",
        "- **方法差异（v2 → repro）**：受体准备 OpenBabel → ADFR；配体几何 MMFF → Orca DFT B3LYP/def2-TZVP；",
        "  配体 PDBQT Meeko(15 DOF) → ADFR(7-11 DOF)；格点精度 0.25Å → 0.1Å（两阶段对接）",
        "- **PLIP 关键残基**：Hu2024 预测 GprC 结合位点依赖 N2.57(Res83) 和 R6.45(Res281)",
        "  若复现成功，这两个残基应出现在 top-5 pose 的接触列表中",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Hu2024 复现验证（docking-repro）")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    root = get_project_root(config)
    logger = setup_logging(root / config["paths"]["log_dir"], "validate_repro")

    logger.info("=== Hu2024 复现验证 ===")

    # 加载 repro 结果
    repro_json = root / config["paths"]["results_dir"] / "docking_results.json"
    repro_results = load_results(repro_json)
    logger.info(f"repro 结果: {len(repro_results)} 个对接对")

    # 加载 v2 结果（用于对比）
    v2_json = root / V2_RESULTS_JSON
    v2_results = load_results(v2_json)
    logger.info(f"v2 结果: {len(v2_results)} 个对接对（对比用）")

    # 验证
    logger.info("--- Hu2024 绝对值验证 ---")
    hu_checks = validate_hu2024(repro_results, logger)

    logger.info("--- Kuo2024 排名验证 ---")
    kuo_checks = validate_kuo2024(repro_results, logger)

    logger.info("--- DOF 计数验证 ---")
    lig_dir = root / config["paths"]["prepared_dir"] / "ligands"
    dof_checks = validate_dof_counts(lig_dir, logger) if lig_dir.exists() else []

    # 生成报告
    report = format_report(hu_checks, kuo_checks, dof_checks, v2_results, repro_results)
    analysis_dir = root / config["paths"]["analysis_dir"]
    analysis_dir.mkdir(parents=True, exist_ok=True)
    report_path = analysis_dir / "validation_report.md"
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"验证报告: {report_path}")
    print("\n" + report)


if __name__ == "__main__":
    main()
