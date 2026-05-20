"""
Mutant ProLIF IFP 分析 — Channel A Top 候选的交互指纹验证

针对饱和扫描 Top 候选，对每个突变体的 mutant 受体 + mutant 对接 pose
运行 ProLIF，生成残基级接触频率，并与 WT 基线对比。

输入：
  experiments/docking-repro/results/ifp_analysis_mutants/
    receptors/{Rec}_{Label}_tm.pdb     # 从 Windows 回传
    poses/{Rec}_{Label}_{ligand}_poses.pdbqt

输出：
  experiments/docking-repro/results/ifp_analysis_mutants/
    mutant_contacts.csv                # 全部突变体 × 配体 × 残基 × interaction 频率
    mutant_vs_wt_diff.md               # 相对 WT 的接触差异摘要
    tmp/*_withH.pdb, *_poses.sdf       # 中间产物

依赖 run_ifp_analysis.py 的通用函数：add_hydrogens / pdbqt_to_sdf /
get_pocket / analyze_pair / compute_contact_frequency
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from run_ifp_analysis import (
    add_hydrogens,
    analyze_pair,
    compute_contact_frequency,
    pdbqt_to_sdf,
)
from utils import get_project_root, load_config

# Channel A Top 候选（04-11 饱和扫描 + alanine scan 合并）
TOP_MUTANTS = [
    ("Gpr2", "M327A"),
    ("Gpr2", "M327D"),
    ("Gpr2", "R59F"),
    ("Gpr3", "V138R"),
    ("Gpr3", "F170E"),
    ("Gpr3", "I141A"),
]
LIGANDS = ["ascr18", "ascr3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mutant ProLIF IFP 分析")
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--top-mutants", nargs="+", default=None,
                        help="覆盖默认 TOP_MUTANTS 列表，格式 Rec/Label（如 Gpr3/V138M Gpr3/F170L）")
    parser.add_argument("--out-subdir", default=None,
                        help="覆盖输出子目录（相对 results_dir），默认 ifp_analysis_mutants。"
                             "用于 F 方案重跑时隔离输出：ifp_analysis_mutants_gpr3_f")
    parser.add_argument("--wt-csv", default=None,
                        help="覆盖 WT IFP CSV 路径（默认 ifp_analysis/ifp_all.csv）。"
                             "F 方案 Gpr3 WT 在 ifp_analysis_gpr3_f/ifp_all.csv")
    return parser.parse_args()


def load_wt_contacts(csv_path: Path) -> dict[str, dict[str, int]]:
    """读取 WT 的 ifp_all.csv，按 (receptor, ligand) 聚合到 {pair: {residue: count}}"""
    wt: dict[str, dict[str, int]] = {}
    if not csv_path.exists():
        print(f"  [WARN] WT IFP CSV 不存在: {csv_path}，跳过 WT 对比")
        return wt
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            pair = f"{row['receptor']}_{row['ligand']}"
            res = row['residue']
            count = int(row['count'])
            wt.setdefault(pair, {}).setdefault(res, 0)
            wt[pair][res] += count
    return wt


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root
    root = get_project_root(config)

    # receptors/ 和 poses/ 始终从默认位置读（数据源）
    src_dir = root / "experiments/docking-repro/results/ifp_analysis_mutants"
    rec_dir = src_dir / "receptors"
    pose_dir = src_dir / "poses"

    # 输出目录：out-subdir 覆盖时隔离（F 方案不污染旧数据）
    if args.out_subdir:
        work_dir = root / "experiments/docking-repro/results" / args.out_subdir
        work_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] 输出子目录覆盖: {work_dir}")
    else:
        work_dir = src_dir
    tmp_dir = work_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    wt_csv = Path(args.wt_csv) if args.wt_csv else root / "experiments/docking-repro/results/ifp_analysis/ifp_all.csv"
    wt_contacts = load_wt_contacts(wt_csv)

    # 解析 --top-mutants
    active_mutants = TOP_MUTANTS
    if args.top_mutants:
        active_mutants = []
        for spec in args.top_mutants:
            rec, label = spec.split("/", 1)
            active_mutants.append((rec, label))

    # 聚合表：{(rec,label,lig): {residue: {itype: count}}}
    all_freq: dict[tuple, dict] = {}

    for rec_name, label in active_mutants:
        pdb_path = rec_dir / f"{rec_name}_{label}_tm.pdb"
        if not pdb_path.exists():
            print(f"  [SKIP] {pdb_path} 不存在")
            continue

        print(f"\n{'='*60}")
        print(f"  {rec_name} {label}")
        print(f"{'='*60}")

        pdb_h = tmp_dir / f"{rec_name}_{label}_withH.pdb"
        add_hydrogens(pdb_path, pdb_h)

        for lig_name in LIGANDS:
            pair_tag = f"{rec_name}_{label}_{lig_name}"
            pdbqt_path = pose_dir / f"{pair_tag}_poses.pdbqt"
            if not pdbqt_path.exists():
                print(f"  [SKIP] {pdbqt_path} 不存在")
                continue

            sdf_path = tmp_dir / f"{pair_tag}_poses.sdf"
            pdbqt_to_sdf(pdbqt_path, sdf_path)

            lig_cfg = config.get("ligands", {}).get(lig_name, {})
            try:
                df, n_poses = analyze_pair(pdb_h, sdf_path, args.top_n,
                                           template_smiles=lig_cfg.get("smiles_pH74"))
                freq = compute_contact_frequency(df)
                all_freq[(rec_name, label, lig_name)] = freq
                n_contacts = sum(sum(v.values()) for v in freq.values())
                print(f"  [{lig_name}] {len(freq)} 残基, {n_contacts} 接触 ({n_poses} poses)")

                threshold = len(df) * 0.5
                high_freq = sorted(
                    ((r, sum(v.values()), v) for r, v in freq.items()
                     if sum(v.values()) >= threshold),
                    key=lambda x: -x[1],
                )[:10]
                if high_freq:
                    print(f"    Top-10 高频 (>={int(threshold)}/{len(df)}):")
                    for r, total, itypes in high_freq:
                        detail = ", ".join(f"{k}={v}" for k, v in itypes.items())
                        print(f"      {r}: {total} ({detail})")
            except Exception as e:
                print(f"  [ERROR {lig_name}] {e}")
                continue

    if not all_freq:
        print("\n无结果")
        sys.exit(1)

    # ---- 输出 CSV ----
    out_csv = work_dir / "mutant_contacts.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["receptor", "mutation", "ligand", "residue", "interaction", "count"])
        for (rec, label, lig), freq in all_freq.items():
            for res, itypes in freq.items():
                for itype, count in itypes.items():
                    w.writerow([rec, label, lig, res, itype, count])
    print(f"\n[OK] 全部突变体接触 → {out_csv}")

    # ---- 每突变体 Top 接触表（Markdown） ----
    out_md = work_dir / "mutant_vs_wt_diff.md"
    lines = ["# Mutant IFP 差异分析", ""]
    lines.append(f"**突变体数**: {len(active_mutants)}  **配体**: {'+'.join(LIGANDS)}")
    lines.append(f"**方法**: ProLIF Fingerprint, top-{args.top_n} poses, pocket=15Å\n")

    for rec_name, label in active_mutants:
        key18 = (rec_name, label, "ascr18")
        key3 = (rec_name, label, "ascr3")
        if key18 not in all_freq or key3 not in all_freq:
            continue
        freq18 = all_freq[key18]
        freq3 = all_freq[key3]
        res18 = set(freq18.keys())
        res3 = set(freq3.keys())

        lines.append(f"\n## {rec_name} {label}\n")

        wt18 = wt_contacts.get(f"{rec_name}_ascr18", {})
        wt3 = wt_contacts.get(f"{rec_name}_ascr3", {})

        ascr18_only = res18 - res3
        ascr3_only = res3 - res18
        shared = res18 & res3

        def totals(freq: dict, r: str) -> int:
            return sum(freq.get(r, {}).values())

        lines.append(f"- ascr18 独有（保留接触）: {len(ascr18_only)} | ascr3 独有: {len(ascr3_only)} | 共享: {len(shared)}")

        # Top 共享，按 ascr18 频率排序
        lines.append("\n### Top 共享接触（mutant vs WT 变化）\n")
        lines.append("| 残基 | mut ascr18 | mut ascr3 | WT ascr18 | WT ascr3 | Δmut(18−3) |")
        lines.append("|------|-----------:|----------:|----------:|---------:|-----------:|")
        ranked = sorted(shared, key=lambda r: -totals(freq18, r))[:12]
        for r in ranked:
            m18 = totals(freq18, r)
            m3 = totals(freq3, r)
            w18 = wt18.get(r, 0)
            w3 = wt3.get(r, 0)
            lines.append(f"| {r} | {m18} | {m3} | {w18} | {w3} | {m18 - m3:+d} |")

        if ascr18_only:
            lines.append("\n### ascr18 专属（mutant 中）")
            top = sorted(ascr18_only, key=lambda r: -totals(freq18, r))[:5]
            for r in top:
                lines.append(f"- {r}: {totals(freq18, r)}")
        if ascr3_only:
            lines.append("\n### ascr3 专属（mutant 中）")
            top = sorted(ascr3_only, key=lambda r: -totals(freq3, r))[:5]
            for r in top:
                lines.append(f"- {r}: {totals(freq3, r)}")

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Markdown 摘要 → {out_md}")


if __name__ == "__main__":
    main()
