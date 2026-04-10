"""
ProLIF LigNetwork 2D 交互示意图生成器

从 WT docking pose 重跑 ProLIF Fingerprint，生成交互式 2D 残基-配体
interaction diagram (HTML)。

输入：
  - 加氢 PDB: experiments/docking-repro/results/ifp_analysis/tmp/{Rec}_withH.pdb
  - Pose SDF:  experiments/docking-repro/results/ifp_analysis/tmp/{Rec}_{Lig}_poses.sdf

输出：
  experiments/docking-repro/analysis/lignetwork/
    ├── Gpr2_ascr18_lignetwork.html
    ├── Gpr2_ascr3_lignetwork.html
    ├── Gpr3_ascr18_lignetwork.html
    └── GprC_ascr18_lignetwork.html

用法：
    python plot_ifp_2d_diagram.py
    python plot_ifp_2d_diagram.py --pairs Gpr2_ascr18 GprC_ascr18
    python plot_ifp_2d_diagram.py --threshold 0.5
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_project_root, get_results_subdir, load_config

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
import prolif as plf
import MDAnalysis as mda
from rdkit import Chem
from prolif.plotting.network import LigNetwork

POCKET_RADIUS = 15.0  # Å

DEFAULT_PAIRS = [
    "Gpr2_ascr18",
    "Gpr2_ascr3",
    "Gpr3_ascr18",
    "Gpr3_ascr3",
    "GprC_ascr18",
    "GprC_ascr3",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ProLIF LigNetwork 2D diagram")
    parser.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS,
                        help="Receptor_Ligand pairs (default: %(default)s)")
    parser.add_argument("--top-n", type=int, default=20,
                        help="Pose count for fingerprint (default: 20)")
    parser.add_argument("--threshold", type=float, default=0.3,
                        help="Interaction frequency threshold for display (default: 0.3)")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    return parser.parse_args()


def get_pocket(prot: mda.AtomGroup, lig_center: np.ndarray,
               radius: float = POCKET_RADIUS) -> mda.AtomGroup:
    """选择配体周围 radius Å 内的蛋白残基"""
    dists = np.linalg.norm(prot.positions - lig_center, axis=1)
    near_resids = set(prot.atoms[np.where(dists < radius)[0]].resids)
    if not near_resids:
        raise ValueError(f"No residues within {radius}Å of ligand center")
    pocket_sel = " or ".join([f"resid {rid}" for rid in sorted(near_resids)])
    return prot.select_atoms(pocket_sel)


def run_fingerprint(rec_pdb_h: Path, pose_sdf: Path,
                    top_n: int = 20) -> tuple[plf.Fingerprint, Chem.Mol]:
    """运行 ProLIF 并返回 (Fingerprint, ligand_mol)"""
    # 受体
    u_rec = mda.Universe(str(rec_pdb_h))
    prot = u_rec.select_atoms("protein")

    # 配体第一个 pose — 用于定义 pocket 和获取 ligand mol
    suppl_rd = Chem.SDMolSupplier(str(pose_sdf), removeHs=False)
    pose1 = next(iter(suppl_rd))
    if pose1 is None:
        raise ValueError(f"无法读取 SDF: {pose_sdf}")
    conf = pose1.GetConformer()
    lig_center = np.mean(
        [list(conf.GetAtomPosition(i)) for i in range(pose1.GetNumAtoms())],
        axis=0,
    )

    # Pocket 选择
    pocket = get_pocket(prot, lig_center)
    prot_mol = plf.Molecule.from_mda(pocket)

    # 配体 poses
    lig_suppl = plf.sdf_supplier(str(pose_sdf))
    poses = list(lig_suppl[:top_n])

    # 运行 IFP
    fp = plf.Fingerprint()
    fp.run_from_iterable(poses, prot_mol)

    return fp, pose1


def enhance_html(html_path: Path, title: str) -> None:
    """注入自定义 UI：全屏画布、缩放速度调节、重置按钮、缩放滑块。"""
    html = html_path.read_text(encoding="utf-8")

    # 1. 画布高度 500px → 扣除标题栏(36px)+控制栏(50px)
    html = html.replace('"height": "500px"', '"height": "calc(100vh - 86px)"')

    # 2. 隐藏 UNL1 节点（ProLIF 默认配体标签，远离骨架干扰居中）
    html = re.sub(
        r'\{"id": "UNL1"[^}]*\}',
        lambda m: m.group(0).replace('"physics": true', '"physics": false, "hidden": true'),
        html,
    )

    # 3. 注入 zoomSpeed + 残基弹簧拉近（springLength 缩短）
    html = html.replace(
        '"physics":',
        '"interaction": {"zoomSpeed": 0.15, "zoomView": true}, "physics":',
    )
    # 缩短弹簧自然长度，让残基节点更贴近配体骨架
    html = html.replace(
        '"springConstant": 0.1',
        '"springConstant": 0.2, "springLength": 60',
    )

    # 4. 注入控制栏 CSS + HTML + JS（在 </body> 之前）
    controls = """
<style>
#zoom-controls {
    position: fixed; bottom: 0; left: 0; right: 0;
    height: 50px; background: #f5f5f5; border-top: 1px solid #ddd;
    display: flex; align-items: center; justify-content: center; gap: 12px;
    z-index: 999; padding: 0 20px;
}
#zoom-controls button {
    cursor: pointer; padding: 6px 14px; border: 1px solid #bbb;
    border-radius: 4px; background: #fff; font-size: 13px;
}
#zoom-controls button:hover { background: #e8e8e8; }
#zoom-slider {
    width: 240px; cursor: pointer; accent-color: #5979e3;
}
#zoom-label { font-size: 12px; color: #666; min-width: 50px; text-align: center; }
#title-bar {
    position: fixed; top: 0; left: 0; right: 0;
    height: 36px; background: #fff; border-bottom: 1px solid #eee;
    display: flex; align-items: center; justify-content: center;
    font: bold 14px Arial, sans-serif; color: #333; z-index: 999;
}
#mynetwork { margin-top: 36px; }
</style>
<div id="title-bar">TITLE_PLACEHOLDER</div>
<div id="zoom-controls">
    <button id="btn-fit" title="Reset view">Reset View</button>
    <button id="btn-zout">-</button>
    <input type="range" id="zoom-slider" min="0.2" max="3" step="0.05" value="1">
    <button id="btn-zin">+</button>
    <span id="zoom-label">100%</span>
</div>
<script>
(function() {
    var slider = document.getElementById('zoom-slider');
    var label = document.getElementById('zoom-label');
    var updating = false;

    function fitCenter() {
        // 只 fit 可见节点（UNL1 已 hidden）
        var visibleIds = [];
        ifp.body.data.nodes.forEach(function(n) { if (!n.hidden) visibleIds.push(n.id); });
        ifp.fit({nodes: visibleIds, animation: {duration: 300, easingFunction: 'easeInOutQuad'}});
    }
    document.getElementById('btn-fit').addEventListener('click', fitCenter);
    document.getElementById('btn-zin').addEventListener('click', function() {
        var s = ifp.getScale() * 1.3;
        ifp.moveTo({scale: s, animation: {duration: 200}});
    });
    document.getElementById('btn-zout').addEventListener('click', function() {
        var s = ifp.getScale() / 1.3;
        ifp.moveTo({scale: s, animation: {duration: 200}});
    });

    slider.addEventListener('input', function() {
        updating = true;
        var s = parseFloat(this.value);
        ifp.moveTo({scale: s});
        label.textContent = Math.round(s * 100) + '%';
        updating = false;
    });

    ifp.on('zoom', function(params) {
        if (!updating) {
            var s = ifp.getScale();
            slider.value = Math.min(Math.max(s, 0.2), 3);
            label.textContent = Math.round(s * 100) + '%';
        }
    });

    // 初始加载后居中 + 同步滑块
    ifp.once('stabilized', function() {
        fitCenter();
        setTimeout(function() {
            var s = ifp.getScale();
            slider.value = Math.min(Math.max(s, 0.2), 3);
            label.textContent = Math.round(s * 100) + '%';
        }, 600);
    });
})();
</script>
"""
    controls = controls.replace("TITLE_PLACEHOLDER", title)
    html = html.replace("</body>", controls + "\n</body>")

    html_path.write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    root = get_project_root(config)

    tmp_dir = root / config["paths"]["results_dir"] / config["paths"]["ifp_subdir"] / "tmp"
    out_dir = root / config["paths"]["analysis_dir"] / "lignetwork"
    out_dir.mkdir(parents=True, exist_ok=True)

    for pair in args.pairs:
        parts = pair.split("_", 1)
        if len(parts) != 2:
            print(f"  [SKIP] 无效 pair 格式: {pair}")
            continue
        rec_name, lig_name = parts

        rec_pdb_h = tmp_dir / f"{rec_name}_withH.pdb"
        pose_sdf = tmp_dir / f"{pair}_poses.sdf"

        if not rec_pdb_h.exists():
            print(f"  [SKIP] 受体 PDB 不存在: {rec_pdb_h}")
            continue
        if not pose_sdf.exists():
            print(f"  [SKIP] Pose SDF 不存在: {pose_sdf}")
            continue

        print(f"\n[{pair}] 运行 ProLIF Fingerprint...")
        try:
            fp, lig_mol = run_fingerprint(rec_pdb_h, pose_sdf, args.top_n)
            n_interactions = fp.to_dataframe().shape[1]
            print(f"  {n_interactions} interaction columns across {len(fp.to_dataframe())} poses")

            # 生成 LigNetwork
            net = LigNetwork.from_fingerprint(
                fp, lig_mol,
                kind="aggregate",
                threshold=args.threshold,
            )

            html_path = out_dir / f"{pair}_lignetwork.html"
            net.save(str(html_path))

            # 注入自定义 UI
            title = f"{rec_name} \u00d7 {lig_name} \u2014 LigNetwork (aggregate, {args.top_n} poses, threshold={args.threshold})"
            enhance_html(html_path, title)
            print(f"  保存: {html_path}")

        except Exception as e:
            print(f"  [ERROR] {pair}: {e}")
            continue

    print("\n完成。用浏览器打开 HTML 文件查看交互式 2D 图。")


if __name__ == "__main__":
    main()
