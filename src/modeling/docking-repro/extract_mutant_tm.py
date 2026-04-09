"""
批量提取 AF3 突变体结构的 TM 域

输入：{mutagenesis_dir}/af3_structures/{RecName}/{Label}.pdb
输出：{mutagenesis_dir}/af3_structures/{RecName}/{Label}_tm.pdb

优先使用 annotation-based 提取（ICL3 截断），读取 config.yaml 中的 tm_topology。
config 不存在或无 tm_topology 时回退到 pLDDT 方法。

用法：
    python extract_mutant_tm.py
    python extract_mutant_tm.py --config path/to/config.yaml --project-root /path/to/root
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_this_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_this_dir))

from prepare_receptor import extract_tm_domain, extract_tm_domain_by_annotation
from utils import get_project_root, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量 TM 域提取")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    structures_dir = root / config["paths"]["mutagenesis_dir"] / "af3_structures"
    tm_topology = config.get("tm_topology")

    method = "annotation-based（ICL3 截断）" if tm_topology else "pLDDT-based（旧方法）"
    print(f"TM 提取方法: {method}\n")

    pdb_files = sorted(structures_dir.glob("*/*.pdb"))
    # 排除已有的 _tm.pdb
    pdb_files = [p for p in pdb_files if not p.stem.endswith("_tm")]
    print(f"找到 {len(pdb_files)} 个突变体 PDB\n")

    results = []
    for pdb in pdb_files:
        rec = pdb.parent.name
        label = pdb.stem
        out = pdb.parent / f"{label}_tm.pdb"

        try:
            if tm_topology and rec in tm_topology:
                n_kept, n_removed, n_total = extract_tm_domain_by_annotation(
                    pdb, out, tm_topology, rec,
                )
                results.append((rec, label, n_kept, n_total, "OK"))
                print(f"  {rec}/{label}: {n_total} → {n_kept} 残基（-{n_removed}）")
            else:
                first, last = extract_tm_domain(pdb, out)
                results.append((rec, label, first, last, "OK (pLDDT)"))
                print(f"  {rec}/{label}: 残基 {first}–{last} (pLDDT)")
        except Exception as e:
            results.append((rec, label, 0, 0, str(e)))
            print(f"  {rec}/{label}: 错误 — {e}")

    print(f"\n{'='*55}")
    print(f"  共处理 {len(results)} 个突变体")
    print(f"  {'受体':<8} {'突变':<8} {'kept/start':>10} {'total/end':>10} {'状态'}")
    print(f"  {'-'*50}")
    for rec, label, a, b, status in results:
        print(f"  {rec:<8} {label:<8} {a:>10} {b:>10} {status}")


if __name__ == "__main__":
    main()
