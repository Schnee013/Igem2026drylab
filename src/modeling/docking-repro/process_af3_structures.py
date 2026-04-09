"""
处理 AF3 Server 下载的突变体结构

输入：{mutagenesis_dir}/af3_downloads/{job_name}/
输出：{mutagenesis_dir}/af3_structures/{RecName}/{Label}.cif（最优 model）

流程：
  1. 读取每个 job 的 5 个 summary_confidences，按 ranking_score 选最优
  2. 复制最优 model CIF 到 af3_structures/
  3. 输出汇总表

用法：
    python process_af3_structures.py
    python process_af3_structures.py --config path/to/config.yaml --project-root /path/to/root
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_this_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_this_dir))

from utils import get_project_root, load_config

# job 目录名到 (RecName, Label) 的映射
# 目录名格式: gprc_n83a → (GprC, N83A)
REC_NAME_MAP = {"gprc": "GprC", "gpr2": "Gpr2", "gpr3": "Gpr3"}


def parse_job_name(dirname: str) -> tuple[str, str]:
    """gprc_n83a → (GprC, N83A)"""
    parts = dirname.split("_", 1)
    rec_key = parts[0]
    label = parts[1].upper()
    rec_name = REC_NAME_MAP.get(rec_key, rec_key)
    return rec_name, label


def find_best_model(job_dir: Path) -> tuple[int, float, dict]:
    """从 5 个 model 中选 ranking_score 最高的，返回 (model_idx, score, full_conf)"""
    best_idx = 0
    best_score = -1.0
    best_conf = {}

    for i in range(5):
        conf_file = list(job_dir.glob(f"*_summary_confidences_{i}.json"))
        if not conf_file:
            continue
        conf = json.loads(conf_file[0].read_text())
        score = conf.get("ranking_score", 0.0)
        if score > best_score:
            best_score = score
            best_idx = i
            best_conf = conf

    return best_idx, best_score, best_conf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="处理 AF3 Server 下载的突变体结构")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    mut_dir = root / config["paths"]["mutagenesis_dir"]
    downloads_dir = mut_dir / "af3_downloads"
    output_dir = mut_dir / "af3_structures"

    if not downloads_dir.exists():
        print(f"错误: {downloads_dir} 不存在")
        return

    job_dirs = sorted([d for d in downloads_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    print(f"找到 {len(job_dirs)} 个 AF3 job 目录\n")

    results = []

    for job_dir in job_dirs:
        dirname = job_dir.name
        try:
            rec_name, label = parse_job_name(dirname)
        except (IndexError, KeyError):
            print(f"  跳过: {dirname}（无法解析名称）")
            continue

        best_idx, best_score, best_conf = find_best_model(job_dir)

        # 找到最优 model CIF
        cif_files = list(job_dir.glob(f"*_model_{best_idx}.cif"))
        if not cif_files:
            print(f"  错误: {dirname} 没有 model_{best_idx}.cif")
            continue

        # 复制到输出目录
        out_dir = output_dir / rec_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_cif = out_dir / f"{label}.cif"
        shutil.copy2(cif_files[0], out_cif)

        ptm = best_conf.get("ptm", "n/a")
        frac_dis = best_conf.get("fraction_disordered", "n/a")

        results.append({
            "rec": rec_name,
            "label": label,
            "model": best_idx,
            "ranking_score": best_score,
            "ptm": ptm,
            "frac_disordered": frac_dis,
            "out": str(out_cif),
        })

        print(f"  {rec_name}/{label}: model_{best_idx} (ranking={best_score:.2f}, ptm={ptm})")

    # 汇总
    print(f"\n{'='*65}")
    print(f"  共处理 {len(results)} 个突变体结构")
    print(f"  输出目录: {output_dir}")
    print(f"{'='*65}")
    print(f"  {'受体':<8} {'突变':<8} {'Model':>5} {'Ranking':>8} {'pTM':>6} {'Disordered':>10}")
    print(f"  {'-'*55}")
    for r in results:
        print(f"  {r['rec']:<8} {r['label']:<8} {r['model']:>5} {r['ranking_score']:>8.2f} {r['ptm']:>6} {r['frac_disordered']:>10}")


if __name__ == "__main__":
    main()
