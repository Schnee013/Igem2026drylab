#!/usr/bin/env python3
"""
ratio_channel_analysis.py — 比值型双通道 Docking 数据分析

读取突变对接结果（含 Gpr2/Gpr3 alanine+saturation + GprC alanine+saturation），按 sel_mut 全谱排名，
提取 Channel A (ascr18偏好) / Channel B (ascr3偏好) 候选，
计算跨受体配对判别力 D 和平衡度 balance。

产出：
  - ratio_spectrum.csv          全谱排名
  - ratio_pairings.csv          跨受体配对排名
  - ratio_channel_report.md     Markdown 报告
"""

import json
import csv
from pathlib import Path
from itertools import product

# ── 路径 ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent  # experiments/docking-repro
INPUT_JSON = REPO_ROOT / "mutagenesis" / "mutagenesis_results_merged_20260416.json"
OUT_DIR = SCRIPT_DIR  # analysis/

# ── 参数 ──────────────────────────────────────────────────────────
NOISE_SD = 0.159          # Gpr2_ascr18 multiseed SD (最保守估计)
SIGMA_THRESHOLD = 3       # 显著性倍数
SEL_THRESHOLD = NOISE_SD * SIGMA_THRESHOLD   # 0.477 ≈ 0.48
AFFINITY_FLOOR = 5.0      # |ΔG| 下限 (kcal/mol)


def load_data():
    with open(INPUT_JSON, encoding="utf-8") as f:
        records = json.load(f)
    return records


def is_gprc_ala(rec):
    """GprC alanine scan 候选标记 caveat"""
    return rec["receptor"] == "GprC" and rec["mut_residue"] == "A"


def classify(rec):
    """返回 channel 分类: 'A', 'B', 'neutral'"""
    sel = rec["sel_mut"]
    if sel < -SEL_THRESHOLD and abs(rec["dg_ascr18"]) >= AFFINITY_FLOOR:
        return "A"
    elif sel > SEL_THRESHOLD and abs(rec["dg_ascr3"]) >= AFFINITY_FLOOR:
        return "B"
    else:
        return "neutral"


def classify_strength(rec):
    """选择性强度标签（边界与 classify() 一致）"""
    abs_sel = abs(rec["sel_mut"])
    if abs_sel > SEL_THRESHOLD:
        return "strong"
    elif abs_sel > NOISE_SD:
        return "moderate"  # 1-3σ: 有信号但不满足 Channel 筛选
    else:
        return "noise"


def annotate(records):
    """给每条记录添加分析字段"""
    for rec in records:
        rec["channel"] = classify(rec)
        rec["strength"] = classify_strength(rec)
        rec["gprc_caveat"] = is_gprc_ala(rec)
        rec["label"] = f"{rec['receptor']}_{rec['mutation']}"
    return records


def write_spectrum_csv(records, path):
    """全谱排名 CSV"""
    sorted_recs = sorted(records, key=lambda r: r["sel_mut"])
    fields = [
        "rank", "label", "receptor", "mutation", "mut_residue",
        "sel_mut", "dg_ascr18", "dg_ascr3",
        "ddg_ascr18", "ddg_ascr3",
        "channel", "strength", "gprc_caveat",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, rec in enumerate(sorted_recs, 1):
            row = {**rec, "rank": i}
            w.writerow(row)
    return sorted_recs


def compute_pairings(records):
    """跨受体配对，计算 D 和 balance。GprC alanine caveat 在两侧都排除到单独列表。"""
    ch_a = [r for r in records if r["channel"] == "A" and not r["gprc_caveat"]]
    ch_a_caveat = [r for r in records if r["channel"] == "A" and r["gprc_caveat"]]
    ch_b = [r for r in records if r["channel"] == "B" and not r["gprc_caveat"]]
    ch_b_caveat = [r for r in records if r["channel"] == "B" and r["gprc_caveat"]]

    pairings = []
    for a, b in product(ch_a, ch_b):
        if a["receptor"] == b["receptor"]:
            continue  # 跨受体优先
        d = a["sel_mut"] - b["sel_mut"]
        abs_a = abs(a["sel_mut"])
        abs_b = abs(b["sel_mut"])
        balance = abs_a / (abs_a + abs_b) if (abs_a + abs_b) > 0 else 0.5
        pairings.append({
            "channel_a": a["label"],
            "channel_b": b["label"],
            "receptor_a": a["receptor"],
            "receptor_b": b["receptor"],
            "sel_a": a["sel_mut"],
            "sel_b": b["sel_mut"],
            "dg_a_ascr18": a["dg_ascr18"],
            "dg_b_ascr3": b["dg_ascr3"],
            "D": d,
            "balance": balance,
            "has_caveat": False,
        })

    # 含 GprC caveat 的配对单独标注
    for a, b in product(ch_a, ch_b_caveat):
        if a["receptor"] == b["receptor"]:
            continue
        d = a["sel_mut"] - b["sel_mut"]
        abs_a = abs(a["sel_mut"])
        abs_b = abs(b["sel_mut"])
        balance = abs_a / (abs_a + abs_b) if (abs_a + abs_b) > 0 else 0.5
        pairings.append({
            "channel_a": a["label"],
            "channel_b": b["label"],
            "receptor_a": a["receptor"],
            "receptor_b": b["receptor"],
            "sel_a": a["sel_mut"],
            "sel_b": b["sel_mut"],
            "dg_a_ascr18": a["dg_ascr18"],
            "dg_b_ascr3": b["dg_ascr3"],
            "D": d,
            "balance": balance,
            "has_caveat": True,
        })

    pairings.sort(key=lambda p: p["D"])
    return pairings


def write_pairings_csv(pairings, path):
    fields = [
        "rank", "channel_a", "channel_b",
        "receptor_a", "receptor_b",
        "sel_a", "sel_b", "D", "balance",
        "dg_a_ascr18", "dg_b_ascr3", "has_caveat",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, p in enumerate(pairings, 1):
            row = {**p, "rank": i}
            w.writerow(row)


def generate_report(records, pairings, path):
    """生成 Markdown 报告"""
    sorted_recs = sorted(records, key=lambda r: r["sel_mut"])
    ch_a = [r for r in sorted_recs if r["channel"] == "A" and not r["gprc_caveat"]]
    ch_a_caveat = [r for r in sorted_recs if r["channel"] == "A" and r["gprc_caveat"]]
    ch_b = [r for r in sorted_recs if r["channel"] == "B"]
    ch_b_clean = [r for r in ch_b if not r["gprc_caveat"]]
    ch_b_caveat = [r for r in ch_b if r["gprc_caveat"]]
    neutral = [r for r in sorted_recs if r["channel"] == "neutral"]
    clean_pairings = [p for p in pairings if not p["has_caveat"]]
    caveat_pairings = [p for p in pairings if p["has_caveat"]]

    lines = []
    lines.append("# 比值型双通道 Docking 分析报告")
    lines.append("")
    lines.append(f"生成时间：自动生成 | 数据源：{INPUT_JSON.name} ({len(records)} 条)")
    lines.append("")

    # §1 框架
    lines.append("## 1. 分析框架")
    lines.append("")
    lines.append("PRD 定义了**双通道比值型**传感器：两个 Gpr 突变体分别偏好 ascr#18 和 ascr#3，")
    lines.append("输出比值判别植物寄生线虫 (PPN)。核心指标：")
    lines.append("")
    lines.append("```")
    lines.append("sel_mut = ΔG(ascr18) − ΔG(ascr3)")
    lines.append("  sel_mut << 0 → 偏好 ascr18 → Channel A")
    lines.append("  sel_mut >> 0 → 偏好 ascr3  → Channel B")
    lines.append("```")
    lines.append("")
    lines.append(f"| 参数 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 噪声 SD | {NOISE_SD} kcal/mol (Gpr2_ascr18 multiseed) |")
    lines.append(f"| 3σ 显著性阈值 | {SEL_THRESHOLD:.3f} kcal/mol |")
    lines.append(f"| 亲和力下限 | {AFFINITY_FLOOR} kcal/mol |")
    lines.append("")

    # WT baselines
    wt_baselines = {}
    for rec in records:
        r = rec["receptor"]
        if r not in wt_baselines:
            wt_baselines[r] = rec["sel_wt"]
    lines.append("### WT 基线")
    lines.append("")
    lines.append("| 受体 | sel_wt | 天然倾向 |")
    lines.append("|------|--------|---------|")
    for r in ["GprC", "Gpr2", "Gpr3"]:
        sw = wt_baselines.get(r, "N/A")
        if isinstance(sw, float):
            if sw < -SEL_THRESHOLD:
                bias = "强 ascr18 偏好"
            elif sw > SEL_THRESHOLD:
                bias = "强 ascr3 偏好"
            elif sw < -NOISE_SD:
                bias = "弱 ascr18 偏好"
            elif sw > NOISE_SD:
                bias = "弱 ascr3 偏好"
            else:
                bias = "噪声内"
            lines.append(f"| {r} | {sw:.3f} | {bias} |")
    lines.append("")

    # §2 全谱
    lines.append("## 2. 全谱排名（按 sel_mut 升序）")
    lines.append("")
    lines.append("| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | 通道 | 强度 | caveat |")
    lines.append("|---|--------|------|---------|------------|-----------|------|------|--------|")
    for i, rec in enumerate(sorted_recs, 1):
        caveat = "⚠ GprC-ala" if rec["gprc_caveat"] else ""
        lines.append(
            f"| {i} | {rec['label']} | {rec['receptor']} "
            f"| {rec['sel_mut']:.3f} | {rec['dg_ascr18']:.3f} | {rec['dg_ascr3']:.3f} "
            f"| {rec['channel']} | {rec['strength']} | {caveat} |"
        )
    lines.append("")

    # §3 Channel A
    lines.append("## 3. Channel A 候选（ascr18 偏好，sel_mut < −0.477）")
    lines.append("")
    if ch_a:
        lines.append("### 3a. 无 caveat")
        lines.append("")
        lines.append("| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) |")
        lines.append("|---|--------|------|---------|------------|-----------|-------------|")
        for i, rec in enumerate(ch_a, 1):
            lines.append(
                f"| {i} | {rec['label']} | {rec['receptor']} "
                f"| {rec['sel_mut']:.3f} | {rec['dg_ascr18']:.3f} | {rec['dg_ascr3']:.3f} "
                f"| {rec['ddg_ascr18']:.3f} |"
            )
        lines.append("")
    if ch_a_caveat:
        lines.append("### 3b. GprC alanine scan（⚠ caveat）")
        lines.append("")
        lines.append("| # | 突变体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) | ΔΔG(ascr3) |")
        lines.append("|---|--------|---------|------------|-----------|-------------|-------------|")
        for i, rec in enumerate(ch_a_caveat, 1):
            lines.append(
                f"| {i} | {rec['label']} "
                f"| {rec['sel_mut']:.3f} | {rec['dg_ascr18']:.3f} | {rec['dg_ascr3']:.3f} "
                f"| {rec['ddg_ascr18']:.3f} | {rec['ddg_ascr3']:.3f} |"
            )
        lines.append("")
    if not ch_a and not ch_a_caveat:
        lines.append("*无满足条件的候选*")
        lines.append("")

    # §4 Channel B
    lines.append("## 4. Channel B 候选（ascr3 偏好，sel_mut > +0.477）")
    lines.append("")
    if ch_b_clean:
        lines.append("### 4a. 无 caveat")
        lines.append("")
        lines.append("| # | 突变体 | 受体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | ΔΔG(ascr3) |")
        lines.append("|---|--------|------|---------|-----------|------------|-------------|")
        for i, rec in enumerate(ch_b_clean, 1):
            lines.append(
                f"| {i} | {rec['label']} | {rec['receptor']} "
                f"| {rec['sel_mut']:.3f} | {rec['dg_ascr3']:.3f} | {rec['dg_ascr18']:.3f} "
                f"| {rec['ddg_ascr3']:.3f} |"
            )
        lines.append("")

    if ch_b_caveat:
        lines.append("### 4b. GprC alanine scan（⚠ caveat：差异化破坏副产品，非真正选择性工程）")
        lines.append("")
        lines.append("| # | 突变体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | ΔΔG(ascr18) | ΔΔG(ascr3) |")
        lines.append("|---|--------|---------|-----------|------------|-------------|-------------|")
        for i, rec in enumerate(ch_b_caveat, 1):
            lines.append(
                f"| {i} | {rec['label']} "
                f"| {rec['sel_mut']:.3f} | {rec['dg_ascr3']:.3f} | {rec['dg_ascr18']:.3f} "
                f"| {rec['ddg_ascr18']:.3f} | {rec['ddg_ascr3']:.3f} |"
            )
        lines.append("")

    if not ch_b_clean and not ch_b_caveat:
        lines.append("*无满足条件的候选*")
        lines.append("")

    # §5 配对
    lines.append("## 5. 跨受体配对排名")
    lines.append("")
    lines.append("D = sel_A − sel_B（越负 = 判别力越强）")
    lines.append("")
    lines.append("balance = |sel_A| / (|sel_A| + |sel_B|)（理想 = 0.5）")
    lines.append("")

    if clean_pairings:
        lines.append("### 5a. 无 caveat 配对 Top 10")
        lines.append("")
        lines.append("| # | Channel A | Channel B | D | balance | sel_A | sel_B | ΔG_A(ascr18) | ΔG_B(ascr3) |")
        lines.append("|---|-----------|-----------|---|---------|-------|-------|--------------|-------------|")
        for i, p in enumerate(clean_pairings[:10], 1):
            lines.append(
                f"| {i} | {p['channel_a']} | {p['channel_b']} "
                f"| {p['D']:.3f} | {p['balance']:.3f} | {p['sel_a']:.3f} | {p['sel_b']:.3f} "
                f"| {p['dg_a_ascr18']:.3f} | {p['dg_b_ascr3']:.3f} |"
            )
        lines.append("")

    if caveat_pairings:
        lines.append("### 5b. 含 GprC-ala caveat 配对 Top 10（仅供参考，不直接进入湿实验推荐）")
        lines.append("")
        lines.append("| # | Channel A | Channel B | D | balance | sel_A | sel_B | caveat |")
        lines.append("|---|-----------|-----------|---|---------|-------|-------|--------|")
        for i, p in enumerate(caveat_pairings[:10], 1):
            lines.append(
                f"| {i} | {p['channel_a']} | {p['channel_b']} "
                f"| {p['D']:.3f} | {p['balance']:.3f} | {p['sel_a']:.3f} | {p['sel_b']:.3f} "
                f"| ⚠ GprC-ala |"
            )
        lines.append("")

    # §6 湿实验建议
    lines.append("## 6. 湿实验配对建议")
    lines.append("")
    if clean_pairings:
        top = clean_pairings[:3]
        lines.append("基于无 caveat 跨受体配对 Top 3：")
        lines.append("")
        for i, p in enumerate(top, 1):
            lines.append(f"{i}. **{p['channel_a']}** (Channel A, sel={p['sel_a']:.3f}) + "
                         f"**{p['channel_b']}** (Channel B, sel={p['sel_b']:.3f})")
            lines.append(f"   - D = {p['D']:.3f}, balance = {p['balance']:.3f}")
            lines.append(f"   - 亲和力：A端 ΔG(ascr18) = {p['dg_a_ascr18']:.3f}, B端 ΔG(ascr3) = {p['dg_b_ascr3']:.3f}")
            lines.append("")
    else:
        lines.append("**无可用的跨受体无 caveat 配对。**需要：")
        lines.append("- GprC saturation scan 补充 Channel B 候选")
        lines.append("- 或 Gpr3 saturation scan 寻找更强 Channel B 候选")
        lines.append("")

    # §7 caveat
    lines.append("## 7. 边界与 caveat")
    lines.append("")
    lines.append("1. **GprC alanine scan caveat**：GprC 13/14 个 Ala 突变体显示非特异性结合破坏"
                 "（ΔΔG(ascr18) 常 >2 kcal/mol），产生的表观 ascr3 偏好是差异化破坏副产品，"
                 "不代表真正的选择性工程。这些候选须经 saturation scan 验证后才可进入湿实验。")
    lines.append("2. **噪声阈值**：基于 Gpr2_ascr18 multiseed SD=0.159，这是系统中最大的 SD，"
                 "作为保守估计。|sel_mut| < 0.477 的选择性差异不可靠。")
    lines.append("3. **刚性对接局限**：AutoDock Vina 刚性对接不考虑蛋白柔性和溶剂效应，"
                 "ΔG 绝对值仅作相对排名参考，不代表真实结合自由能。")
    lines.append("4. **亲和力下限**：Channel 候选要求 |ΔG| ≥ 5.0 kcal/mol，"
                 "确保突变体仍有足够结合力激活信号通路。参照系统最弱 WT = Gpr3_ascr18 = −5.726。")
    lines.append("")

    # 统计摘要
    lines.append("## 附录：统计摘要")
    lines.append("")
    lines.append(f"| 类别 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 总突变数 | {len(records)} |")
    lines.append(f"| Channel A 无 caveat | {len(ch_a)} |")
    lines.append(f"| Channel A 含 GprC-ala caveat | {len(ch_a_caveat)} |")
    lines.append(f"| Channel B 无 caveat | {len(ch_b_clean)} |")
    lines.append(f"| Channel B 含 GprC-ala caveat | {len(ch_b_caveat)} |")
    lines.append(f"| 中性区 | {len(neutral)} |")
    lines.append(f"| 跨受体配对 (无 caveat) | {len(clean_pairings)} |")
    lines.append(f"| 跨受体配对 (含 caveat) | {len(caveat_pairings)} |")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print(f"读取 {INPUT_JSON} ...")
    records = load_data()
    print(f"  载入 {len(records)} 条记录")

    records = annotate(records)

    # 全谱排名 CSV
    spectrum_csv = OUT_DIR / "ratio_spectrum.csv"
    sorted_recs = write_spectrum_csv(records, spectrum_csv)
    print(f"  全谱 CSV → {spectrum_csv}")

    # 统计
    ch_a = [r for r in records if r["channel"] == "A" and not r["gprc_caveat"]]
    ch_a_caveat = [r for r in records if r["channel"] == "A" and r["gprc_caveat"]]
    ch_b = [r for r in records if r["channel"] == "B"]
    ch_b_clean = [r for r in ch_b if not r["gprc_caveat"]]
    ch_b_caveat = [r for r in ch_b if r["gprc_caveat"]]
    neutral = [r for r in records if r["channel"] == "neutral"]
    print(f"  Channel A: {len(ch_a)} (+ {len(ch_a_caveat)} caveat) | "
          f"Channel B: {len(ch_b_clean)} (+ {len(ch_b_caveat)} caveat) | "
          f"Neutral: {len(neutral)}")

    # 配对排名
    pairings = compute_pairings(records)
    pairings_csv = OUT_DIR / "ratio_pairings.csv"
    write_pairings_csv(pairings, pairings_csv)
    print(f"  配对 CSV → {pairings_csv}")
    clean_pairings = [p for p in pairings if not p["has_caveat"]]
    caveat_pairings = [p for p in pairings if p["has_caveat"]]
    print(f"  配对数: 无 caveat {len(clean_pairings)} | 含 caveat {len(caveat_pairings)}")

    # Markdown 报告
    report_md = OUT_DIR / "ratio_channel_report.md"
    generate_report(records, pairings, report_md)
    print(f"  报告 → {report_md}")

    # 验证
    print("\n── 验证 ──")
    print(f"  [OK] {len(records)} 条记录")

    for r in ch_a:
        assert r["sel_mut"] < -SEL_THRESHOLD, f"Channel A 候选 sel_mut 不满足: {r['label']}"
        assert abs(r["dg_ascr18"]) >= AFFINITY_FLOOR, f"Channel A 亲和力不足: {r['label']}"
    print(f"  [OK] Channel A 候选全部满足 sel_mut < −{SEL_THRESHOLD:.3f} 且 |ΔG(ascr18)| ≥ {AFFINITY_FLOOR}")

    for r in ch_b:
        assert r["sel_mut"] > SEL_THRESHOLD, f"Channel B 候选 sel_mut 不满足: {r['label']}"
        assert abs(r["dg_ascr3"]) >= AFFINITY_FLOOR, f"Channel B 亲和力不足: {r['label']}"
    print(f"  [OK] Channel B 候选全部满足 sel_mut > +{SEL_THRESHOLD:.3f} 且 |ΔG(ascr3)| ≥ {AFFINITY_FLOOR}")

    gprc_in_b = [r for r in ch_b if r["receptor"] == "GprC"]
    gprc_ala_in_b = [r for r in gprc_in_b if r["gprc_caveat"]]
    gprc_sat_in_b = [r for r in gprc_in_b if not r["gprc_caveat"]]
    for r in gprc_ala_in_b:
        assert r["mut_residue"] == "A", f"caveat 候选非 Ala: {r['label']}"
    print(f"  [OK] GprC Channel B: {len(gprc_ala_in_b)} caveat (Ala) + {len(gprc_sat_in_b)} saturation (无 caveat)")

    for r in ch_a_caveat:
        assert r["gprc_caveat"], f"Channel A caveat 候选缺少 caveat 标记: {r['label']}"
        assert r["receptor"] == "GprC", f"非 GprC 候选误入 caveat: {r['label']}"
    print(f"  [OK] Channel A caveat 候选全部为 GprC ({len(ch_a_caveat)} 个)")

    # D 值手算抽检
    if clean_pairings:
        p = clean_pairings[0]
        d_calc = p["sel_a"] - p["sel_b"]
        assert abs(p["D"] - d_calc) < 1e-9, f"D 值计算不一致: {p['D']} vs {d_calc}"
        print(f"  [OK] D 值抽检: {p['channel_a']} + {p['channel_b']} → D={p['D']:.3f} (手算={d_calc:.3f})")

    print("\n全部验证通过。")


if __name__ == "__main__":
    main()
