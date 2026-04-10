"""
IFP 接触频率热图生成器

数据来源: experiments/docking-repro/results/ifp_analysis/contact_frequency.json
输出: experiments/docking-repro/analysis/ifp_heatmap_{receptor}.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))
from utils import get_project_root, load_config

LIGANDS = ["ascr18", "ascr3", "ascr7"]

# Tier 1 候选（2026-04-10 alanine scan 结果）
TIER1 = {
    "Gpr2": {"M327", "R59"},
    "Gpr3": {"I141"},
    "GprC": set(),
}
TIER2 = {
    "Gpr2": set(),
    "Gpr3": {"F170", "V138"},
    "GprC": set(),
}


def residue_label(key: str) -> str:
    """将 'MET327.A' → 'M327' 风格标签"""
    name = key.split(".")[0]          # 'MET327'
    THREE = {
        "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
        "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
        "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
        "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
    }
    for three, one in THREE.items():
        if name.startswith(three):
            num = name[len(three):]
            return f"{one}{num}"
    return name


def total_contacts(interaction_dict: dict) -> int:
    return sum(interaction_dict.values())


def plot_receptor(ax, rec: str, data: dict, scan_residues: list[int], wt_sel: float):
    """单受体热图（ascr18/ascr3/ascr7 列，残基行）。"""
    # 收集该受体所有涉及配体的残基
    all_residues: dict[str, dict[str, int]] = {}  # label -> {lig: count}
    for lig in LIGANDS:
        key = f"{rec}_{lig}"
        if key not in data:
            continue
        for res_key, idict in data[key].items():
            label = residue_label(res_key)
            if label not in all_residues:
                all_residues[label] = {l: 0 for l in LIGANDS}
            all_residues[label][lig] = total_contacts(idict)

    if not all_residues:
        ax.set_visible(False)
        return

    # 按 ascr18 接触频率降序排列
    sorted_res = sorted(all_residues.keys(),
                        key=lambda r: all_residues[r]["ascr18"], reverse=True)

    matrix = np.array([[all_residues[r][l] for l in LIGANDS] for r in sorted_res],
                       dtype=float)

    # 归一化（每格显示绝对次数，颜色用相对）
    vmax = matrix.max() if matrix.max() > 0 else 1.0

    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd",
                   vmin=0, vmax=vmax, interpolation="nearest")

    # 轴标签
    ax.set_xticks(range(len(LIGANDS)))
    ax.set_xticklabels(["ascr#18", "ascr#3", "ascr#7"], fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(sorted_res)))

    # Y 标签颜色编码
    yticks = []
    for label in sorted_res:
        num_str = "".join(c for c in label if c.isdigit())
        try:
            resnum = int(num_str)
        except ValueError:
            resnum = -1

        in_scan = resnum in scan_residues
        short = label[0]
        in_t1 = short + num_str in TIER1.get(rec, set()) or label in TIER1.get(rec, set())
        in_t2 = short + num_str in TIER2.get(rec, set()) or label in TIER2.get(rec, set())
        yticks.append((label, in_scan, in_t1, in_t2))

    ax.set_yticklabels([t[0] for t in yticks], fontsize=7.5)

    # 着色扫描残基标签
    for i, (label, in_scan, in_t1, in_t2) in enumerate(yticks):
        color = "black"
        weight = "normal"
        if in_t1:
            color = "#d62728"  # 红
            weight = "bold"
        elif in_t2:
            color = "#ff7f0e"  # 橙
            weight = "bold"
        elif in_scan:
            color = "#1f77b4"  # 蓝
        ax.get_yticklabels()[i].set_color(color)
        ax.get_yticklabels()[i].set_fontweight(weight)

    # 格内写数字
    for i, r in enumerate(sorted_res):
        for j, l in enumerate(LIGANDS):
            v = int(matrix[i, j])
            if v > 0:
                tc = "white" if matrix[i, j] > vmax * 0.6 else "black"
                ax.text(j, i, str(v), ha="center", va="center",
                        fontsize=6.5, color=tc)

    # WT 选择性标注
    ax.set_title(f"{rec}  (WT dG_sel = {wt_sel:+.2f} kcal/mol)",
                 fontsize=10, fontweight="bold", pad=6)

    return im


def main():
    config = load_config(str(_this_dir / "config.yaml"))
    root = get_project_root(config)

    ifp_json = root / config["paths"]["results_dir"] / config["paths"]["ifp_subdir"] / "contact_frequency.json"
    data = json.loads(ifp_json.read_text())

    scan_residues_cfg = config["mutagenesis"]["scan_residues"]

    wt_sel = {
        "GprC": -8.275 - (-7.477),   # -0.798
        "Gpr2": -6.834 - (-6.430),   # -0.404
        "Gpr3": -5.726 - (-5.921),   # +0.195
    }

    out_dir = root / config["paths"]["analysis_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    receptors = ["GprC", "Gpr2", "Gpr3"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 10),
                             gridspec_kw={"wspace": 0.45})
    fig.suptitle("IFP Contact Frequency Heatmap — WT Docking (singlestage, exh=200)\n"
                 "Values = contact counts across 20 poses; color intensity proportional to frequency",
                 fontsize=11, y=1.01)

    last_im = None
    for ax, rec in zip(axes, receptors):
        scan = scan_residues_cfg.get(rec, [])
        last_im = plot_receptor(ax, rec, data, scan, wt_sel[rec])

    # 颜色条
    if last_im is not None:
        cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.6])
        fig.colorbar(last_im, cax=cbar_ax, label="Contacts / 20 poses")

    # 图例
    legend_elements = [
        mpatches.Patch(color="#d62728", label="Tier 1 (ddG_sel <= -0.48)"),
        mpatches.Patch(color="#ff7f0e", label="Tier 2 (ddG_sel <= -0.16)"),
        mpatches.Patch(color="#1f77b4", label="Current scan_residues"),
        mpatches.Patch(color="black",   label="Other contact residues"),
    ]
    fig.legend(handles=legend_elements, loc="lower center",
               ncol=4, fontsize=8.5, bbox_to_anchor=(0.5, -0.02))

    out_path = out_dir / "ifp_heatmap_all_receptors.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"保存: {out_path}")

    # 同时输出每个受体的单独高清图
    for rec in receptors:
        fig2, ax2 = plt.subplots(figsize=(5, 9))
        scan = scan_residues_cfg.get(rec, [])
        plot_receptor(ax2, rec, data, scan, wt_sel[rec])
        ax2.set_title(f"{rec}  IFP Contact Frequency\n(WT dG_sel = {wt_sel[rec]:+.2f} kcal/mol)",
                      fontsize=11, fontweight="bold")
        fig2.tight_layout()
        p2 = out_dir / f"ifp_heatmap_{rec}.png"
        fig2.savefig(p2, dpi=150, bbox_inches="tight")
        plt.close(fig2)
        print(f"保存: {p2}")

    plt.close(fig)
    print("完成")


if __name__ == "__main__":
    main()
