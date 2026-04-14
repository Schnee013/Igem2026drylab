"""
解析 AF3 Server 结果，提取 pLDDT / iPAE / ipTM 并生成排名表。

用法:
  conda activate chimeric
  python parse_af3_results.py

输入:
  af3_predictions/downloads/<folder_name>/
    fold_*_summary_confidences_{0-4}.json  — 高级指标
    fold_*_full_data_{0-4}.json            — per-atom pLDDT + PAE 矩阵
    fold_*_model_{0-4}.cif                 — 结构 (per-residue pLDDT = CA B-factor)

输出:
  analysis/monomer_scores.csv   — 单体 pLDDT (全局 + C-terminal) + pTM
  analysis/complex_scores.csv   — 复合物 ipTM + iPAE + ranking_score
  analysis/ranking_summary.md   — 排名 + 推荐
"""

import json
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE / "af3_predictions" / "downloads"
ANALYSIS_DIR = BASE / "analysis"

# 所有已知嵌合体（name → graft length）
GRAFT_LENGTHS = {
    "Gpa1-WT": 0,
    "Gpa1-AoGpa2-C5": 5, "Gpa1-AoGpa2-C10": 10, "Gpa1-AoGpa2-C15": 15,
    "Gpa1-AoGpa2-C25": 25, "Gpa1-AoGpa2-C37": 37,
    "Gpa1-AfGasA-C5": 5, "Gpa1-AfGasA-C10": 10, "Gpa1-AfGasA-C15": 15,
    "Gpa1-AfGasA-C25": 25, "Gpa1-AfGasA-C37": 37,
}

COGNATE_PAIRS = {
    ("Gpr2", "AoGpa2"), ("Gpr3", "AoGpa2"),
    ("GprC", "AfGasA"),
}

# lowercase → display name 的映射（用于从 downloads/ 文件夹名反推 job 信息）
_CHIMERA_KEYS = {c.lower().replace("-", "_"): c for c in GRAFT_LENGTHS}
_RECEPTOR_KEYS = {r.lower(): r for r in ["Gpr2", "Gpr3", "GprC", "Ste2"]}


def discover_jobs() -> list[dict]:
    """扫描 downloads/ 目录，从文件夹名推断 job 元信息。

    替代原来的 af3_jobs.json 读取——不再依赖任何外部 manifest。
    """
    jobs = []
    if not DOWNLOADS_DIR.exists():
        return jobs

    for folder in sorted(DOWNLOADS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        fname = folder.name  # e.g. "gpr2_gpa1_aogpa2_c15_complex"

        if fname.endswith("_monomer"):
            chimera_key = fname.replace("_monomer", "")
            chimera = _CHIMERA_KEYS.get(chimera_key)
            if chimera is None:
                print(f"  [?] unrecognized monomer: {fname}")
                continue
            jobs.append({
                "name": chimera + "_monomer",
                "type": "monomer",
                "chimera": chimera,
            })

        elif fname.endswith("_complex"):
            body = fname.replace("_complex", "")
            chimera, receptor = None, None
            # 尝试匹配已知嵌合体（最长匹配优先）
            for key in sorted(_CHIMERA_KEYS, key=len, reverse=True):
                if key in body:
                    chimera = _CHIMERA_KEYS[key]
                    remainder = body.replace(key, "").strip("_")
                    receptor = _RECEPTOR_KEYS.get(remainder)
                    break
            if chimera is None or receptor is None:
                print(f"  [?] unrecognized complex: {fname}")
                continue

            donor = "AoGpa2" if "AoGpa2" in chimera else "AfGasA" if "AfGasA" in chimera else "WT"
            is_cognate = (receptor, donor) in COGNATE_PAIRS
            pairing = "cognate" if is_cognate else ("control" if chimera == "Gpa1-WT" else "cross")

            jobs.append({
                "name": f"{receptor}_{chimera}_complex",
                "type": "complex",
                "chimera": chimera,
                "receptor": receptor,
                "pairing": pairing,
            })
    return jobs


def job_name_to_folder(name: str) -> str:
    """AF3 Server 将 job name 小写化 + 连字符替换为下划线。"""
    return name.lower().replace("-", "_")


def find_best_model(folder: Path) -> int:
    """从 5 个 model 的 summary_confidences 中选 ranking_score 最高的。"""
    best_idx, best_score = 0, -1.0
    for i in range(5):
        conf_files = list(folder.glob(f"*summary_confidences_{i}.json"))
        if not conf_files:
            continue
        with open(conf_files[0]) as f:
            data = json.load(f)
        score = data.get("ranking_score", 0.0)
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def load_summary(folder: Path, model_idx: int) -> dict:
    """加载 summary_confidences JSON。"""
    files = list(folder.glob(f"*summary_confidences_{model_idx}.json"))
    if not files:
        return {}
    with open(files[0]) as f:
        return json.load(f)


def load_full_data(folder: Path, model_idx: int) -> dict:
    """加载 full_data JSON。"""
    files = list(folder.glob(f"*full_data_{model_idx}.json"))
    if not files:
        return {}
    with open(files[0]) as f:
        return json.load(f)


def parse_ca_plddts_from_cif(folder: Path, model_idx: int) -> list[float]:
    """从 CIF 文件提取 CA 原子的 B-factor (= per-residue pLDDT)。"""
    cif_files = list(folder.glob(f"*model_{model_idx}.cif"))
    if not cif_files:
        return []
    ca_plddts = []
    with open(cif_files[0]) as f:
        for line in f:
            if line.startswith("ATOM") and " CA " in line:
                parts = line.split()
                # B_iso_or_equiv is the 15th field (0-indexed: 14)
                try:
                    ca_plddts.append(float(parts[14]))
                except (IndexError, ValueError):
                    pass
    return ca_plddts


def compute_interface_pae(full_data: dict) -> float:
    """计算跨链平均 PAE (iPAE)。"""
    pae = full_data.get("pae", [])
    chain_ids = full_data.get("token_chain_ids", [])
    if not pae or not chain_ids:
        return float("inf")

    unique_chains = list(dict.fromkeys(chain_ids))
    if len(unique_chains) < 2:
        return float("inf")

    cross_values = []
    n = len(chain_ids)
    for i in range(n):
        for j in range(n):
            if chain_ids[i] != chain_ids[j]:
                cross_values.append(pae[i][j])

    return sum(cross_values) / len(cross_values) if cross_values else float("inf")


def analyze_monomers(jobs: list) -> list[dict]:
    """分析单体结果。"""
    monomer_jobs = [j for j in jobs if j["type"] == "monomer"]
    results = []

    for job in monomer_jobs:
        folder_name = job_name_to_folder(job["name"])
        folder = DOWNLOADS_DIR / folder_name
        if not folder.exists():
            print(f"  [SKIP] {folder_name}/ not found")
            continue

        best_idx = find_best_model(folder)
        summary = load_summary(folder, best_idx)
        ca_plddts = parse_ca_plddts_from_cif(folder, best_idx)

        chimera_name = job["chimera"]
        graft_len = GRAFT_LENGTHS.get(chimera_name, 0)

        global_plddt = sum(ca_plddts) / len(ca_plddts) if ca_plddts else 0.0
        ct_plddt = 0.0
        if graft_len > 0 and ca_plddts:
            ct_values = ca_plddts[-graft_len:]
            ct_plddt = sum(ct_values) / len(ct_values)

        # 所有 5 个 model 的 ranking_score
        all_scores = []
        for i in range(5):
            s = load_summary(folder, i)
            if s:
                all_scores.append(s.get("ranking_score", 0))

        row = {
            "name": job["name"],
            "chimera": chimera_name,
            "graft_len": graft_len,
            "best_model": best_idx,
            "plddt_global": round(global_plddt, 2),
            "plddt_cterminal": round(ct_plddt, 2) if graft_len > 0 else "N/A",
            "ptm": round(summary.get("ptm", 0), 4),
            "ranking_score": round(summary.get("ranking_score", 0), 4),
            "fraction_disordered": round(summary.get("fraction_disordered", 0), 3),
            "score_range": f"{min(all_scores):.4f}-{max(all_scores):.4f}" if all_scores else "N/A",
        }
        results.append(row)
        ct_str = f"C-term({graft_len}aa)={row['plddt_cterminal']}" if graft_len > 0 else "WT"
        print(f"  [OK] {folder_name}: pLDDT={row['plddt_global']}, "
              f"{ct_str}, pTM={row['ptm']}, rank={row['ranking_score']}")

    return results


def analyze_complexes(jobs: list) -> list[dict]:
    """分析复合物结果。"""
    complex_jobs = [j for j in jobs if j["type"] == "complex"]
    results = []

    for job in complex_jobs:
        folder_name = job_name_to_folder(job["name"])
        folder = DOWNLOADS_DIR / folder_name
        if not folder.exists():
            print(f"  [SKIP] {folder_name}/ not found")
            continue

        best_idx = find_best_model(folder)
        summary = load_summary(folder, best_idx)
        full_data = load_full_data(folder, best_idx)

        chimera_name = job["chimera"]
        receptor_name = job["receptor"]
        pairing = job["pairing"]

        ipae = compute_interface_pae(full_data)

        # chain_pair_pae_min from summary (AF3 built-in)
        cppm = summary.get("chain_pair_pae_min", [])
        min_cross_pae = "N/A"
        if cppm and len(cppm) >= 2 and len(cppm[0]) >= 2:
            min_cross_pae = round(cppm[0][1], 2)

        # 所有 5 个 model 的 iptm
        all_iptm = []
        for i in range(5):
            s = load_summary(folder, i)
            if s and s.get("iptm") is not None:
                all_iptm.append(s["iptm"])

        row = {
            "name": job["name"],
            "receptor": receptor_name,
            "chimera": chimera_name,
            "pairing": pairing,
            "best_model": best_idx,
            "iptm": round(summary.get("iptm", 0) or 0, 4),
            "ptm": round(summary.get("ptm", 0), 4),
            "ipae_mean": round(ipae, 2) if ipae != float("inf") else "N/A",
            "chain_pair_pae_min": min_cross_pae,
            "ranking_score": round(summary.get("ranking_score", 0), 4),
            "fraction_disordered": round(summary.get("fraction_disordered", 0), 3),
            "has_clash": summary.get("has_clash", 0),
            "iptm_range": f"{min(all_iptm):.4f}-{max(all_iptm):.4f}" if all_iptm else "N/A",
        }
        results.append(row)
        tag = "★" if pairing == "cognate" else ("◎" if pairing == "control" else "○")
        print(f"  [OK] {folder_name}: ipTM={row['iptm']}, "
              f"iPAE={row['ipae_mean']}, pae_min={min_cross_pae}, "
              f"rank={row['ranking_score']} {tag}")

    return results


def write_csv(rows: list[dict], output_path: Path):
    if not rows:
        print(f"  No data for {output_path.name}")
        return
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  → {output_path}")


def generate_ranking(monomer_results: list, complex_results: list) -> str:
    lines = ["# AF3 嵌合 Gpa1 排名分析", "",
             f"> 生成时间: {__import__('datetime').date.today()}", ""]

    # --- 单体折叠质量 ---
    lines.append("## 1. 单体折叠质量 (Batch A + B)")
    lines.append("")
    if monomer_results:
        wt = next((r for r in monomer_results if r["chimera"] == "Gpa1-WT"), None)
        wt_plddt = wt["plddt_global"] if wt else 0

        lines.append("| 嵌合体 | 全局 pLDDT | C-term pLDDT | ΔpLDDT vs WT | pTM | ranking_score | disorder |")
        lines.append("|--------|-----------|-------------|-------------|-----|-------------|----------|")
        for r in sorted(monomer_results, key=lambda x: x["plddt_global"], reverse=True):
            delta = round(r["plddt_global"] - wt_plddt, 2) if wt_plddt else "N/A"
            delta_str = f"{delta:+.2f}" if isinstance(delta, float) else delta
            ct_str = str(r["plddt_cterminal"]) if r["plddt_cterminal"] != "N/A" else "—"
            lines.append(
                f"| {r['chimera']} | {r['plddt_global']} | "
                f"{ct_str} | {delta_str} | "
                f"{r['ptm']} | {r['ranking_score']} | {r['fraction_disordered']} |"
            )
        lines.append("")
        lines.append("> **判读**: pLDDT > 80 = 可信折叠; |ΔpLDDT| < 5 = 嫁接未显著破坏骨架; disorder < 0.2 = 整体有序")
    lines.append("")

    # --- 复合物偶联质量 ---
    lines.append("## 2. 复合物偶联质量 (Batch C + D)")
    lines.append("")
    if complex_results:
        for receptor in ["Ste2", "Gpr2", "Gpr3", "GprC"]:
            group = [r for r in complex_results if r["receptor"] == receptor]
            if not group:
                continue
            lines.append(f"### {receptor}")
            lines.append("")
            lines.append("| 嵌合体 | 类型 | ipTM | iPAE | pae_min | ranking | disorder |")
            lines.append("|--------|------|------|------|---------|---------|----------|")
            for r in sorted(group, key=lambda x: x["iptm"], reverse=True):
                tag = {"cognate": "★", "cross": "○", "control": "◎"}[r["pairing"]]
                lines.append(
                    f"| {r['chimera']} | {tag} {r['pairing']} | "
                    f"{r['iptm']} | {r['ipae_mean']} | "
                    f"{r['chain_pair_pae_min']} | {r['ranking_score']} | "
                    f"{r['fraction_disordered']} |"
                )
            lines.append("")

        lines.append("> **判读标准**:")
        lines.append("> - ipTM > 0.6 = 可能存在真实界面; ipTM > 0.8 = 高置信度偶联")
        lines.append("> - iPAE < 10 Å = 界面位置预测可靠")
        lines.append("> - pae_min: AF3 内置的链对最小 PAE，越低越好")
        lines.append("> - cognate (★) ipTM 应显著高于 cross (○) — 否则嫁接未起效")
    lines.append("")

    # --- 综合推荐 ---
    lines.append("## 3. 综合推荐")
    lines.append("")
    if complex_results:
        # cognate 对
        cognate = [r for r in complex_results if r["pairing"] == "cognate"]
        cross = [r for r in complex_results if r["pairing"] == "cross"]

        if cognate:
            cognate_sorted = sorted(cognate, key=lambda x: x["iptm"], reverse=True)
            lines.append("### Top cognate 偶联 (按 ipTM 排序)")
            lines.append("")
            for i, r in enumerate(cognate_sorted, 1):
                lines.append(f"{i}. `{r['chimera']}` × `{r['receptor']}`: "
                             f"ipTM={r['iptm']}, iPAE={r['ipae_mean']}, "
                             f"ranking={r['ranking_score']}")
            lines.append("")

        # cognate vs cross 对比
        if cognate and cross:
            avg_cog = sum(r["iptm"] for r in cognate) / len(cognate)
            avg_cross = sum(r["iptm"] for r in cross) / len(cross)
            lines.append(f"### cognate vs cross 对比")
            lines.append(f"- cognate 平均 ipTM: {avg_cog:.4f} (n={len(cognate)})")
            lines.append(f"- cross 平均 ipTM: {avg_cross:.4f} (n={len(cross)})")
            lines.append(f"- Δ(cognate - cross): {avg_cog - avg_cross:+.4f}")
            lines.append("")
            if avg_cog > avg_cross + 0.05:
                lines.append("> ✓ cognate 偶联信号显著优于 cross — C 端嫁接有效")
            elif avg_cog > avg_cross:
                lines.append("> △ cognate 偶联信号略优于 cross — 效果微弱，需更多验证")
            else:
                lines.append("> ✗ cognate 偶联信号未优于 cross — 嫁接可能未起效")
    lines.append("")

    return "\n".join(lines)


def main():
    jobs = discover_jobs()
    if not jobs:
        print(f"ERROR: no job folders found in {DOWNLOADS_DIR}")
        return

    monomers = [j for j in jobs if j["type"] == "monomer"]
    complexes = [j for j in jobs if j["type"] == "complex"]
    print(f"Discovered {len(jobs)} jobs ({len(monomers)} monomers, {len(complexes)} complexes)")
    print()

    # 分析单体
    print("=== Monomer Analysis ===")
    monomer_results = analyze_monomers(jobs)
    print()

    # 分析复合物
    print("=== Complex Analysis ===")
    complex_results = analyze_complexes(jobs)
    print()

    # 写出 CSV
    ANALYSIS_DIR.mkdir(exist_ok=True)
    print("=== Writing outputs ===")
    write_csv(monomer_results, ANALYSIS_DIR / "monomer_scores.csv")
    write_csv(complex_results, ANALYSIS_DIR / "complex_scores.csv")

    # 生成排名摘要
    ranking_md = generate_ranking(monomer_results, complex_results)
    ranking_path = ANALYSIS_DIR / "ranking_summary.md"
    ranking_path.write_text(ranking_md)
    print(f"  → {ranking_path}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
