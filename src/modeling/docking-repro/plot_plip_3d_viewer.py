"""
PLIP 3D 交互式 Viewer 生成器

从 WT docking pose + 受体 PDB 运行 PLIP 分析，生成基于 3Dmol.js 的
交互式 3D HTML viewer，标注 H-bond/Hydrophobic/Salt-bridge。

输入：
  - 加氢 PDB: experiments/docking-repro/results/ifp_analysis/tmp/{Rec}_withH.pdb
  - Pose SDF:  experiments/docking-repro/results/ifp_analysis/tmp/{Rec}_{Lig}_poses.sdf

输出：
  experiments/docking-repro/analysis/plip_3d/
    ├── {Rec}_{Lig}_plip3d.html     (交互式 3D viewer)
    └── {Rec}_{Lig}_plip_report.txt (PLIP 文本报告)

用法：
    python plot_plip_3d_viewer.py
    python plot_plip_3d_viewer.py --pairs Gpr2_ascr18 GprC_ascr18
    python plot_plip_3d_viewer.py --pocket-radius 8.0
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_project_root, load_config

import numpy as np
from rdkit import Chem
from plip.structure.preparation import PDBComplex

POCKET_RADIUS = 6.0  # Å — 3D view 中 pocket 残基显示范围

DEFAULT_PAIRS = [
    "Gpr2_ascr18",
    "Gpr2_ascr3",
    "Gpr3_ascr18",
    "Gpr3_ascr3",
    "GprC_ascr18",
    "GprC_ascr3",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PLIP 3D viewer generator")
    parser.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS,
                        help="Receptor_Ligand pairs (default: %(default)s)")
    parser.add_argument("--pocket-radius", type=float, default=POCKET_RADIUS,
                        help="Pocket display radius in Å (default: %(default)s)")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    return parser.parse_args()


def create_combined_pdb(rec_pdb: Path, pose_sdf: Path) -> tuple[str, np.ndarray]:
    """合并受体 PDB + 最佳 docking pose → PDB 字符串 + 配体质心。"""
    suppl = Chem.SDMolSupplier(str(pose_sdf), removeHs=False)
    best_pose = next(iter(suppl))
    if best_pose is None:
        raise ValueError(f"无法读取 SDF: {pose_sdf}")

    lig_pdb_block = Chem.MolToPDBBlock(best_pose)

    # 配体质心
    conf = best_pose.GetConformer()
    coords = np.array([list(conf.GetAtomPosition(i))
                       for i in range(best_pose.GetNumAtoms())])
    lig_center = coords.mean(axis=0)

    with open(rec_pdb) as f:
        rec_lines = f.readlines()

    combined = [l for l in rec_lines if not l.startswith(("END", "CONECT"))]
    for line in lig_pdb_block.splitlines():
        if line.startswith("HETATM"):
            combined.append(line + "\n")
    combined.append("END\n")

    return "".join(combined), lig_center


def run_plip(pdb_string: str) -> dict:
    """运行 PLIP 分析，返回交互数据字典。"""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdb", mode="w", delete=False) as tmp:
        tmp.write(pdb_string)
        tmp_path = tmp.name

    mol = PDBComplex()
    mol.load_pdb(tmp_path)
    mol.analyze()

    Path(tmp_path).unlink()

    interactions = {}
    for key, iset in mol.interaction_sets.items():
        hbonds = []
        for hb in list(iset.hbonds_ldon) + list(iset.hbonds_pdon):
            hbonds.append({
                "restype": hb.restype, "resnr": hb.resnr,
                "donor": list(hb.d.coords), "acceptor": list(hb.a.coords),
                "distance": round(hb.distance_ad, 2),
                "angle": round(hb.angle, 1),
                "protisdon": hb.protisdon,
            })

        hydrophobic = []
        for hp in iset.hydrophobic_contacts:
            hydrophobic.append({
                "restype": hp.restype, "resnr": hp.resnr,
                "prot_coords": list(hp.bsatom.coords),
                "lig_coords": list(hp.ligatom.coords),
                "distance": round(hp.distance, 2),
            })

        saltbridges = []
        for sb in list(iset.saltbridge_lneg) + list(iset.saltbridge_pneg):
            saltbridges.append({
                "restype": sb.restype, "resnr": sb.resnr,
                "prot_center": list(sb.positive.center) if sb.protispos else list(sb.negative.center),
                "lig_center": list(sb.negative.center) if sb.protispos else list(sb.positive.center),
                "distance": round(sb.distance, 2),
                "protispos": sb.protispos,
            })

        pistacking = []
        for pi in iset.pistacking:
            pistacking.append({
                "restype": pi.restype, "resnr": pi.resnr,
                "prot_center": list(pi.proteinring.center),
                "lig_center": list(pi.ligandring.center),
                "distance": round(pi.distance, 2),
                "type": pi.type,
            })

        interactions[key] = {
            "hbonds": hbonds,
            "hydrophobic": hydrophobic,
            "saltbridges": saltbridges,
            "pistacking": pistacking,
        }

    return interactions


def generate_text_report(pair: str, interactions: dict) -> str:
    """生成 PLIP 文本报告。"""
    lines = [f"PLIP Interaction Report: {pair}", "=" * 50, ""]

    for key, idata in interactions.items():
        lines.append(f"Binding site: {key}")
        lines.append("-" * 40)

        lines.append(f"\nHydrogen bonds ({len(idata['hbonds'])}):")
        for hb in idata["hbonds"]:
            direction = "P→L" if hb["protisdon"] else "L→P"
            lines.append(f"  {hb['restype']}{hb['resnr']} ({direction}) "
                         f"d={hb['distance']}Å angle={hb['angle']}°")

        lines.append(f"\nHydrophobic contacts ({len(idata['hydrophobic'])}):")
        for hp in idata["hydrophobic"]:
            lines.append(f"  {hp['restype']}{hp['resnr']} d={hp['distance']}Å")

        lines.append(f"\nSalt bridges ({len(idata['saltbridges'])}):")
        for sb in idata["saltbridges"]:
            lines.append(f"  {sb['restype']}{sb['resnr']} d={sb['distance']}Å")

        lines.append(f"\nPi-stacking ({len(idata['pistacking'])}):")
        for pi in idata["pistacking"]:
            lines.append(f"  {pi['restype']}{pi['resnr']} d={pi['distance']}Å ({pi['type']})")

        lines.append("")

    return "\n".join(lines)


def generate_3d_html(pair: str, pdb_string: str, interactions: dict,
                     lig_center: np.ndarray, pocket_radius: float) -> str:
    """生成 3Dmol.js 交互式 HTML。"""
    rec_name, lig_name = pair.split("_", 1)

    # 统计交互
    total = sum(
        len(v["hbonds"]) + len(v["hydrophobic"]) + len(v["saltbridges"]) + len(v["pistacking"])
        for v in interactions.values()
    )

    # Interaction lines for 3Dmol.js
    js_interactions = []
    legend_counts = {"hbond": 0, "hydrophobic": 0, "saltbridge": 0, "pistack": 0}

    for idata in interactions.values():
        for hb in idata["hbonds"]:
            d, a = hb["donor"], hb["acceptor"]
            label = f"{hb['restype']}{hb['resnr']}"
            js_interactions.append(
                f'addDash(viewer, {json.dumps(d)}, {json.dumps(a)}, "#00CED1", "{label}: H-bond {hb["distance"]}Å");'
            )
            legend_counts["hbond"] += 1

        for hp in idata["hydrophobic"]:
            p, l = hp["prot_coords"], hp["lig_coords"]
            label = f"{hp['restype']}{hp['resnr']}"
            js_interactions.append(
                f'addDash(viewer, {json.dumps(p)}, {json.dumps(l)}, "#32CD32", "{label}: Hydrophobic {hp["distance"]}Å");'
            )
            legend_counts["hydrophobic"] += 1

        for sb in idata["saltbridges"]:
            p, l = sb["prot_center"], sb["lig_center"]
            label = f"{sb['restype']}{sb['resnr']}"
            js_interactions.append(
                f'addDash(viewer, {json.dumps(p)}, {json.dumps(l)}, "#FF69B4", "{label}: Salt bridge {sb["distance"]}Å");'
            )
            legend_counts["saltbridge"] += 1

        for pi in idata["pistacking"]:
            p, l = pi["prot_center"], pi["lig_center"]
            label = f"{pi['restype']}{pi['resnr']}"
            js_interactions.append(
                f'addDash(viewer, {json.dumps(p)}, {json.dumps(l)}, "#FFA500", "{label}: Pi-stack {pi["distance"]}Å");'
            )
            legend_counts["pistack"] += 1

    # Collect interacting residue numbers for label display
    interacting_resnrs = set()
    for idata in interactions.values():
        for hb in idata["hbonds"]:
            interacting_resnrs.add(hb["resnr"])
        for hp in idata["hydrophobic"]:
            interacting_resnrs.add(hp["resnr"])
        for sb in idata["saltbridges"]:
            interacting_resnrs.add(sb["resnr"])
        for pi in idata["pistacking"]:
            interacting_resnrs.add(pi["resnr"])

    # Escape PDB for JS embedding
    pdb_escaped = json.dumps(pdb_string)

    # Build legend items (only show non-zero)
    legend_items = []
    if legend_counts["hbond"]:
        legend_items.append(f'<span class="legend-item"><span class="dot" style="background:#00CED1"></span>H-bond ({legend_counts["hbond"]})</span>')
    if legend_counts["hydrophobic"]:
        legend_items.append(f'<span class="legend-item"><span class="dot" style="background:#32CD32"></span>Hydrophobic ({legend_counts["hydrophobic"]})</span>')
    if legend_counts["saltbridge"]:
        legend_items.append(f'<span class="legend-item"><span class="dot" style="background:#FF69B4"></span>Salt bridge ({legend_counts["saltbridge"]})</span>')
    if legend_counts["pistack"]:
        legend_items.append(f'<span class="legend-item"><span class="dot" style="background:#FFA500"></span>Pi-stack ({legend_counts["pistack"]})</span>')
    legend_html = " ".join(legend_items)

    cx, cy, cz = lig_center.tolist()
    resnr_list = json.dumps(sorted(interacting_resnrs))
    interaction_js = "\n        ".join(js_interactions)

    html = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>{rec_name} x {lig_name} — PLIP 3D Viewer</title>
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; }}
    #header {{
        height: 44px; display: flex; align-items: center; justify-content: space-between;
        padding: 0 16px; background: #16213e; border-bottom: 1px solid #0f3460;
    }}
    #header h1 {{ font-size: 15px; font-weight: 600; }}
    #legend {{ display: flex; gap: 14px; font-size: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 4px; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    #viewer {{ width: 100%; height: calc(100vh - 88px); position: relative; }}
    #controls {{
        height: 44px; display: flex; align-items: center; justify-content: center;
        gap: 10px; background: #16213e; border-top: 1px solid #0f3460;
    }}
    #controls button {{
        cursor: pointer; padding: 5px 12px; border: 1px solid #0f3460;
        border-radius: 4px; background: #1a1a2e; color: #eee; font-size: 12px;
    }}
    #controls button:hover {{ background: #0f3460; }}
    #controls label {{ font-size: 12px; }}
    #controls input[type=checkbox] {{ cursor: pointer; }}
    #zoom-slider {{ width: 160px; cursor: pointer; accent-color: #5979e3; vertical-align: middle; }}
    #zoom-label {{ font-size: 11px; color: #aaa; min-width: 40px; text-align: center; }}
    #tooltip {{
        position: fixed; display: none; padding: 6px 10px; background: rgba(0,0,0,0.85);
        color: #fff; font-size: 12px; border-radius: 4px; pointer-events: none; z-index: 100;
    }}
    </style>
    </head>
    <body>
    <div id="header">
        <h1>{rec_name} &times; {lig_name} &mdash; PLIP 3D ({total} interactions)</h1>
        <div id="legend">{legend_html}</div>
    </div>
    <div id="viewer"></div>
    <div id="controls">
        <button id="btn-reset">Reset View</button>
        <button id="btn-spin">Spin</button>
        <button id="btn-zout">&minus;</button>
        <input type="range" id="zoom-slider" min="0.2" max="5" step="0.05" value="1">
        <button id="btn-zin">+</button>
        <span id="zoom-label">100%</span>
        <label><input type="checkbox" id="chk-surface"> Surface</label>
        <label><input type="checkbox" id="chk-labels" checked> Labels</label>
        <label><input type="checkbox" id="chk-cartoon" checked> Backbone</label>
    </div>
    <div id="tooltip"></div>

    <script>
    var pdbData = {pdb_escaped};
    var ligCenter = {{x: {cx:.2f}, y: {cy:.2f}, z: {cz:.2f}}};
    var pocketRadius = {pocket_radius};
    var interactingRes = {resnr_list};

    var viewer = $3Dmol.createViewer("viewer", {{
        backgroundColor: "#1a1a2e",
        antialias: true,
    }});

    var model = viewer.addModel(pdbData, "pdb");

    var pocketSel = {{byres: true, within: {{distance: pocketRadius, sel: {{resn: "UNL"}}}}, not: {{resn: "UNL"}}}};

    function applyBaseStyle(showCartoon) {{
        if (showCartoon) {{
            viewer.setStyle({{not: {{resn: "UNL"}}}}, {{cartoon: {{color: "#8888aa", opacity: 0.6}}}});
            viewer.addStyle(pocketSel, {{stick: {{radius: 0.15, colorscheme: "whiteCarbon"}}}});
        }} else {{
            viewer.setStyle({{not: {{resn: "UNL"}}}}, {{}});
            viewer.setStyle(pocketSel, {{stick: {{radius: 0.15, colorscheme: "whiteCarbon"}}}});
        }}
        viewer.setStyle({{resn: "UNL"}}, {{stick: {{radius: 0.25, color: "#FFD700"}}}});
        viewer.render();
    }}

    // 默认显示 cartoon 骨架
    applyBaseStyle(true);

    // 缩放控件
    var slider = document.getElementById("zoom-slider");
    var zoomLabel = document.getElementById("zoom-label");
    var baseScale = null;
    var sliderUpdating = false;

    function syncSlider() {{
        if (sliderUpdating) return;
        var s = viewer.getView()[4];
        if (baseScale === null) baseScale = s;
        var ratio = s / baseScale;
        var clamped = Math.min(Math.max(ratio, 0.2), 5);
        slider.value = clamped;
        slider.dataset.prev = clamped;
        zoomLabel.textContent = Math.round(ratio * 100) + "%";
    }}

    // 初始基准：等 zoomTo 完成后记录
    setTimeout(function() {{ baseScale = viewer.getView()[4]; syncSlider(); }}, 900);

    // 滑块拖动：用相对 zoom factor
    slider.dataset.prev = "1";
    slider.addEventListener("input", function() {{
        sliderUpdating = true;
        var oldVal = parseFloat(this.dataset.prev) || 1;
        var newVal = parseFloat(this.value);
        if (oldVal > 0) viewer.zoom(newVal / oldVal);
        this.dataset.prev = newVal;
        zoomLabel.textContent = Math.round(newVal * 100) + "%";
        sliderUpdating = false;
    }});

    // +/- 按钮
    document.getElementById("btn-zin").addEventListener("click", function() {{
        viewer.zoom(1.3);
        setTimeout(syncSlider, 50);
    }});
    document.getElementById("btn-zout").addEventListener("click", function() {{
        viewer.zoom(0.7);
        setTimeout(syncSlider, 50);
    }});

    // 滚轮缩放：capture phase 拦截，stopPropagation 阻断 3Dmol.js 内置 handler
    document.getElementById("viewer").addEventListener("wheel", function(e) {{
        e.preventDefault();
        e.stopPropagation();
        viewer.zoom(e.deltaY > 0 ? 1.08 : 0.92);
        setTimeout(syncSlider, 50);
    }}, {{capture: true, passive: false}});

    // Labels for interacting residues
    var labelGroup = [];
    interactingRes.forEach(function(resnr) {{
        var atoms = viewer.selectedAtoms({{resi: resnr, atom: "CA"}});
        if (atoms.length > 0) {{
            var a = atoms[0];
            var lab = viewer.addLabel(a.resn + a.resi, {{
                position: {{x: a.x, y: a.y, z: a.z}},
                backgroundColor: "rgba(0,0,0,0.6)",
                fontColor: "#fff",
                fontSize: 11,
                showBackground: true,
                backgroundOpacity: 0.6,
            }});
            labelGroup.push(lab);
        }}
    }});

    // Interaction dashed lines
    function addDash(v, from, to, color, label) {{
        v.addCylinder({{
            start: {{x: from[0], y: from[1], z: from[2]}},
            end: {{x: to[0], y: to[1], z: to[2]}},
            radius: 0.04,
            color: color,
            dashed: true,
            dashLength: 0.2,
            gapLength: 0.1,
            fromCap: 1,
            toCap: 1,
        }});
    }}

    {interaction_js}

    // Center on ligand
    viewer.zoomTo({{resn: "UNL"}}, 800);
    viewer.render();

    // Controls
    var spinning = false;
    document.getElementById("btn-reset").addEventListener("click", function() {{
        viewer.zoomTo({{resn: "UNL"}}, 500);
        setTimeout(function() {{ baseScale = viewer.getView()[4]; syncSlider(); }}, 600);
    }});
    document.getElementById("btn-spin").addEventListener("click", function() {{
        spinning = !spinning;
        viewer.spin(spinning ? "y" : false);
        this.textContent = spinning ? "Stop" : "Spin";
    }});
    document.getElementById("chk-surface").addEventListener("change", function() {{
        if (this.checked) {{
            viewer.addSurface($3Dmol.SurfaceType.VDW,
                {{opacity: 0.5, color: "#6688aa"}},
                pocketSel
            );
        }} else {{
            viewer.removeAllSurfaces();
        }}
        viewer.render();
    }});
    document.getElementById("chk-labels").addEventListener("change", function() {{
        labelGroup.forEach(function(l) {{ viewer.removeLabel(l); }});
        if (this.checked) {{
            labelGroup = [];
            interactingRes.forEach(function(resnr) {{
                var atoms = viewer.selectedAtoms({{resi: resnr, atom: "CA"}});
                if (atoms.length > 0) {{
                    var a = atoms[0];
                    var lab = viewer.addLabel(a.resn + a.resi, {{
                        position: {{x: a.x, y: a.y, z: a.z}},
                        backgroundColor: "rgba(0,0,0,0.6)",
                        fontColor: "#fff",
                        fontSize: 11,
                        showBackground: true,
                        backgroundOpacity: 0.6,
                    }});
                    labelGroup.push(lab);
                }}
            }});
        }}
        viewer.render();
    }});
    document.getElementById("chk-cartoon").addEventListener("change", function() {{
        applyBaseStyle(this.checked);
    }});
    </script>
    </body>
    </html>
    """)

    return html


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    root = get_project_root(config)

    tmp_dir = root / config["paths"]["results_dir"] / config["paths"]["ifp_subdir"] / "tmp"
    out_dir = root / config["paths"]["analysis_dir"] / "plip_3d"
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

        print(f"\n[{pair}] 合并 PDB + 运行 PLIP...")
        try:
            pdb_string, lig_center = create_combined_pdb(rec_pdb_h, pose_sdf)
            interactions = run_plip(pdb_string)

            # 文本报告
            report = generate_text_report(pair, interactions)
            report_path = out_dir / f"{pair}_plip_report.txt"
            report_path.write_text(report, encoding="utf-8")
            print(f"  报告: {report_path}")

            # 3D HTML
            html = generate_3d_html(pair, pdb_string, interactions,
                                    lig_center, args.pocket_radius)
            html_path = out_dir / f"{pair}_plip3d.html"
            html_path.write_text(html, encoding="utf-8")
            print(f"  3D viewer: {html_path}")

            # 统计
            for key, idata in interactions.items():
                n = (len(idata["hbonds"]) + len(idata["hydrophobic"])
                     + len(idata["saltbridges"]) + len(idata["pistacking"]))
                print(f"  [{key}] {n} interactions "
                      f"(H:{len(idata['hbonds'])} Hp:{len(idata['hydrophobic'])} "
                      f"SB:{len(idata['saltbridges'])} Pi:{len(idata['pistacking'])})")

        except Exception as e:
            print(f"  [ERROR] {pair}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n完成。用浏览器打开 HTML 文件查看交互式 3D 图。")


if __name__ == "__main__":
    main()
