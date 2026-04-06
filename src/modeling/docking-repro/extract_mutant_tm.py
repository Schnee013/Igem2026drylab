"""
批量提取 AF3 突变体结构的 TM 域

输入：experiments/docking-repro/mutagenesis/af3_structures/{RecName}/{Label}.pdb
输出：experiments/docking-repro/mutagenesis/af3_structures/{RecName}/{Label}_tm.pdb

优先使用 annotation-based 提取（ICL3 截断），读取 config.yaml 中的 tm_topology。
config 不存在或无 tm_topology 时回退到 pLDDT 方法。

用法：
    python extract_mutant_tm.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保能 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prepare_receptor import extract_tm_domain, extract_tm_domain_by_annotation

STRUCTURES_DIR = Path("experiments/docking-repro/mutagenesis/af3_structures")
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def _load_tm_topology() -> dict | None:
    """尝试从 config.yaml 加载 tm_topology。"""
    if not CONFIG_PATH.exists():
        return None
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
        return config.get("tm_topology")
    except Exception:
        return None


def main() -> None:
    tm_topology = _load_tm_topology()
    method = "annotation-based（ICL3 截断）" if tm_topology else "pLDDT-based（旧方法）"
    print(f"TM 提取方法: {method}\n")

    pdb_files = sorted(STRUCTURES_DIR.glob("*/*.pdb"))
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
    import os
    os.chdir(Path(__file__).resolve().parents[3])
    main()
