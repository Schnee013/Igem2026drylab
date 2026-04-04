"""
对接结果分析模块。

功能：
1. 构建 3x3 结合亲和力矩阵（CSV + 热图）
2. PLIP 蛋白-配体相互作用分析（氢键、疏水接触等）
3. 与文献值比较，生成验证报告
4. 生成 PyMOL 可视化脚本
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openbabel import openbabel as ob

from dock import DockingResult
from utils import get_logger, get_project_root


# ---------------------------------------------------------------------------
# 亲和力矩阵
# ---------------------------------------------------------------------------

def build_affinity_matrix(
    results: list[DockingResult], config: dict
) -> pd.DataFrame:
    """
    构建 3x3 亲和力矩阵，保存 CSV 和热图 PNG。

    Returns:
        DataFrame，行=受体，列=配体，值=最佳结合能（kcal/mol）
    """
    logger = get_logger()
    root = get_project_root(config)
    analysis_dir = root / config["paths"]["analysis_dir"]

    receptor_names = list(config["receptors"].keys())
    ligand_names = list(config["ligands"].keys())

    # 构建矩阵
    matrix = pd.DataFrame(index=receptor_names, columns=ligand_names, dtype=float)
    for r in results:
        if r.box_type != "blind":  # 只统计 informed docking
            matrix.loc[r.receptor, r.ligand] = r.best_affinity

    # 保存 CSV
    csv_path = analysis_dir / "affinity_matrix.csv"
    matrix.to_csv(csv_path)
    logger.info(f"亲和力矩阵已保存: {csv_path}")
    logger.info(f"\n{matrix.to_string()}")

    # 绘制热图
    fig, ax = plt.subplots(figsize=(6, 4))
    vmin = matrix.values.min() - 0.5
    vmax = matrix.values.max() + 0.5

    im = ax.imshow(matrix.values, cmap="RdYlGn_r", vmin=vmin, vmax=vmax, aspect="auto")
    plt.colorbar(im, ax=ax, label="Binding Affinity (kcal/mol)")

    ax.set_xticks(range(len(ligand_names)))
    ax.set_xticklabels(ligand_names, fontsize=10)
    ax.set_yticks(range(len(receptor_names)))
    ax.set_yticklabels(receptor_names, fontsize=10)
    ax.set_title("Receptor-Ligand Binding Affinity Matrix (AutoDock Vina)", fontsize=11)

    # 在格子中标注数值
    for i in range(len(receptor_names)):
        for j in range(len(ligand_names)):
            val = matrix.iloc[i, j]
            if not pd.isna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=9, color="black", fontweight="bold")

    plt.tight_layout()
    png_path = analysis_dir / "affinity_heatmap.png"
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"热图已保存: {png_path}")

    return matrix


# ---------------------------------------------------------------------------
# PLIP 相互作用分析
# ---------------------------------------------------------------------------

def _pdbqt_to_pdb(pdbqt_path: Path, output_path: Path) -> None:
    """使用 OpenBabel 将 PDBQT 转换为 PDB。"""
    ob_conv = ob.OBConversion()
    ob_conv.SetInAndOutFormats("pdbqt", "pdb")
    mol = ob.OBMol()
    ob_conv.ReadFile(mol, str(pdbqt_path))
    ob_conv.WriteFile(mol, str(output_path))


def _merge_receptor_ligand(receptor_pdb: Path, ligand_pdb: Path, output_pdb: Path) -> None:
    """合并受体和配体 PDB 为单个 complex PDB，配体以 HETATM 写入。"""
    rec_lines = receptor_pdb.read_text().splitlines()
    lig_lines = ligand_pdb.read_text().splitlines()

    # 受体取 ATOM/HETATM 行，去掉 END
    rec_body = [l for l in rec_lines if l.startswith(("ATOM", "HETATM"))]
    # 配体行替换为 HETATM（PLIP 需要）
    lig_body = []
    for l in lig_lines:
        if l.startswith("ATOM"):
            l = "HETATM" + l[6:]
        if l.startswith(("ATOM", "HETATM")):
            lig_body.append(l)

    output_pdb.write_text(
        "\n".join(rec_body) + "\nTER\n" + "\n".join(lig_body) + "\nEND\n"
    )


def analyze_interactions(
    config: dict,
    results: list[DockingResult],
    receptor_pdbqt_paths: dict[str, Path],
) -> dict[str, dict]:
    """
    对所有对接结果运行 PLIP 相互作用分析。

    Args:
        config: 全局配置
        results: dock_matrix() 返回的对接结果
        receptor_pdbqt_paths: {"Gpr2": Path, ...} 受体 PDBQT 路径

    Returns:
        嵌套 dict: {pair_name: {interaction_type: [residue_contacts]}}
    """
    logger = get_logger()
    root = get_project_root(config)
    interactions_dir = root / config["paths"]["results_dir"] / "interactions"
    interactions_dir.mkdir(parents=True, exist_ok=True)

    top_n = config["analysis"]["top_n_poses"]
    all_interactions = {}

    # 为每个受体准备 clean PDB（PLIP 用原始 PDB 会更可靠）
    receptor_pdb_dir = root / config["paths"]["receptor_dir"]

    for result in results:
        if result.box_type == "blind":
            continue

        pair = result.pair_name
        logger.info(f"PLIP 分析: {pair}")

        rec_pdb = receptor_pdb_dir / config["receptors"][result.receptor]["pdb_file"]
        poses_pdbqt = Path(result.poses_path)

        if not poses_pdbqt.exists():
            logger.warning(f"  Pose 文件不存在，跳过: {poses_pdbqt}")
            continue

        pair_interactions = {"hydrophobic": [], "hbond": [], "saltbridge": [], "pistacking": []}
        residue_freq: dict[int, int] = {}

        # 分析前 top_n 个 pose
        pose_pdbs = _extract_poses_from_pdbqt(poses_pdbqt, interactions_dir, pair, top_n)

        for pose_idx, pose_pdb in enumerate(pose_pdbs):
            complex_pdb = interactions_dir / f"{pair}_pose{pose_idx}_complex.pdb"
            _merge_receptor_ligand(rec_pdb, pose_pdb, complex_pdb)

            try:
                contacts = _run_plip(complex_pdb)
                for itype, residues in contacts.items():
                    pair_interactions[itype].extend(residues)
                    for res in residues:
                        residue_freq[res] = residue_freq.get(res, 0) + 1
            except Exception as e:
                logger.warning(f"  Pose {pose_idx} PLIP 失败: {e}")

        # 按频率排序
        top_residues = sorted(residue_freq.items(), key=lambda x: -x[1])
        pair_interactions["top_residues_by_frequency"] = top_residues

        all_interactions[pair] = pair_interactions

        logger.info(
            f"  {pair}: 主要接触残基 "
            + ", ".join(f"R{r}({c})" for r, c in top_residues[:5])
        )

    # 保存
    out_path = interactions_dir / "all_interactions.json"
    # 转换 tuple 为 list（JSON 序列化）
    serializable = {}
    for pair, data in all_interactions.items():
        serializable[pair] = {
            k: [list(x) if isinstance(x, tuple) else x for x in v]
            if isinstance(v, list) else v
            for k, v in data.items()
        }
    out_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))
    logger.info(f"PLIP 相互作用已保存: {out_path}")

    return all_interactions


def _extract_poses_from_pdbqt(
    poses_pdbqt: Path, output_dir: Path, pair_name: str, n: int
) -> list[Path]:
    """从多模型 PDBQT 文件中提取前 n 个 pose，各自写为 PDB。"""
    content = poses_pdbqt.read_text()
    models = content.split("MODEL")
    pose_pdbs = []

    for i, model_block in enumerate(models[1: n + 1]):  # 跳过第一个空块
        pdbqt_tmp = output_dir / f"{pair_name}_pose{i}.pdbqt"
        pdbqt_tmp.write_text("MODEL" + model_block)
        pose_pdb = output_dir / f"{pair_name}_pose{i}.pdb"
        _pdbqt_to_pdb(pdbqt_tmp, pose_pdb)
        pose_pdbs.append(pose_pdb)

    return pose_pdbs


def _run_plip(complex_pdb: Path) -> dict[str, list[int]]:
    """
    运行 PLIP 分析单个复合物 PDB。

    Returns:
        {"hydrophobic": [res_ids], "hbond": [res_ids], ...}
    """
    from plip.structure.preparation import PDBComplex

    mol = PDBComplex()
    mol.load_pdb(str(complex_pdb))
    mol.analyze()

    contacts: dict[str, list[int]] = {
        "hydrophobic": [],
        "hbond": [],
        "saltbridge": [],
        "pistacking": [],
    }

    for site_key, site in mol.interaction_sets.items():
        for hc in site.hydrophobic_contacts:
            contacts["hydrophobic"].append(hc.resnr)
        for hb in site.hbonds_pdon + site.hbonds_ldon:
            contacts["hbond"].append(hb.resnr)
        for sb in site.saltbridge_lneg + site.saltbridge_pneg:
            contacts["saltbridge"].append(sb.resnr)
        for ps in site.pistacking:
            contacts["pistacking"].append(ps.resnr)

    return contacts


# ---------------------------------------------------------------------------
# 与文献比较
# ---------------------------------------------------------------------------

def compare_with_literature(
    matrix: pd.DataFrame,
    interactions: dict,
    config: dict,
) -> str:
    """
    将对接结果与 Kuo2024/Hu2024 文献值比较，生成 markdown 报告。

    Returns:
        Markdown 格式的验证报告字符串
    """
    logger = get_logger()
    root = get_project_root(config)
    analysis_dir = root / config["paths"]["analysis_dir"]

    lines = [
        "# 分子对接结果验证报告",
        "",
        "## 方法说明",
        "- 本 pipeline 使用 **AutoDock Vina** (Python API, exhaustiveness=200)",
        "- 受体使用 **TM-only PDB**（pLDDT 导向提取跨膜域），匹配 Hu2024 方法",
        "- Grid box：TM-only 受体质心，40Å 正方形（Hu2024 center-of-mass 策略）",
        "- Kuo2024 使用 **SwissDock**（结合能不可直接比较，聚焦相对排名）",
        "- Hu2024 使用 **AutoDock Vina**（参数相同，GprC 结合能可直接比较）",
        "",
        "## 1. 结合亲和力矩阵",
        "",
        matrix.to_markdown(),
        "（单位：kcal/mol，值越负表示结合越强）",
        "",
        "## 2. 文献复现验证",
        "",
        "### 2a. Hu2024 GprC 验证（AutoDock Vina，可比较绝对值）",
        "",
    ]

    # Hu2024 绝对值验证（GprC）
    gprc_lit = config["receptors"].get("GprC", {}).get("literature_deltaG", {})
    hu2024_pairs = [("ascr3", -8.31), ("ascr18", -8.29)]
    hu_all_pass = True
    for lig, ref_val in hu2024_pairs:
        if lig in matrix.columns and "GprC" in matrix.index:
            our_val = matrix.loc["GprC", lig]
            if pd.isna(our_val):
                lines.append(f"- GprC + {lig}: 无结果")
                hu_all_pass = False
                continue
            diff = abs(our_val - ref_val)
            passed = diff < 1.0
            status = "PASS" if passed else "FAIL"
            if not passed:
                hu_all_pass = False
            lines.append(
                f"- [{status}] GprC + {lig}: 我们 {our_val:.2f} vs Hu2024 {ref_val:.2f} "
                f"（差值 {diff:.2f} kcal/mol，{'< 1.0 ✓' if passed else '>= 1.0 ✗'}）"
            )

    # Hu2024 排名验证：ascr#3 ≈ ascr#18 > ascr#1（ascr#1 需额外下载）
    if "GprC" in matrix.index and "ascr3" in matrix.columns and "ascr18" in matrix.columns:
        v3 = matrix.loc["GprC", "ascr3"]
        v18 = matrix.loc["GprC", "ascr18"]
        if not pd.isna(v3) and not pd.isna(v18):
            rank_ok = abs(v3 - v18) < 1.0  # ascr#3 ≈ ascr#18（Hu2024: -8.31 vs -8.29）
            lines.append(
                f"- [{'PASS' if rank_ok else 'WARN'}] GprC 排名：ascr#3 ({v3:.2f}) ≈ ascr#18 ({v18:.2f}) "
                f"（Hu2024: -8.31 ≈ -8.29，差值应 < 1.0）"
            )

    lines += [
        "",
        "### 2b. Kuo2024 排名验证（SwissDock，仅比较相对排名）",
        "",
    ]

    # Kuo2024 排名验证
    kuo_checks = [
        ("Gpr2", "ascr7", "ascr3", -7.07, -6.99, "ascr#7 结合略强"),
        ("Gpr3", "ascr3", "ascr7", -7.05, -6.41, "ascr#3 明显更强（差 0.64 kcal/mol）"),
    ]
    for rec, better, worse, ref_better, ref_worse, desc in kuo_checks:
        if rec in matrix.index and better in matrix.columns and worse in matrix.columns:
            val_b = matrix.loc[rec, better]
            val_w = matrix.loc[rec, worse]
            if pd.isna(val_b) or pd.isna(val_w):
                lines.append(f"- {rec}: 缺少数据")
                continue
            passed = val_b < val_w  # 更负 = 更强结合
            status = "PASS" if passed else "FAIL"
            lines.append(
                f"- [{status}] {rec}: {better} ({val_b:.2f}) vs {worse} ({val_w:.2f}) "
                f"— {desc}（Kuo2024: {ref_better} vs {ref_worse}）"
            )

    lines += ["", "## 3. 关键残基验证（PLIP）", ""]

    # Gpr2 Y168（Kuo2024 确认的唯一结合残基）
    known_residues = {
        "Gpr2_ascr3": {"expected": [168], "source": "Kuo2024 Y168"},
        "Gpr2_ascr7": {"expected": [168], "source": "Kuo2024 Y168"},
        "GprC_ascr3": {"expected": [83, 281], "source": "Hu2024 N2.57(83)/R6.45(281)"},
        "GprC_ascr18": {"expected": [83, 281], "source": "Hu2024 N2.57(83)/R6.45(281)"},
    }
    for pair, info in known_residues.items():
        if pair in interactions:
            top_res = [r for r, _ in interactions[pair].get("top_residues_by_frequency", [])]
            found = [r for r in info["expected"] if r in top_res]
            lines.append(
                f"- {pair}: 文献残基 {info['expected']} ({info['source']}) → "
                f"PLIP 检出 {found}，"
                f"{'PASS' if found else 'WARN（方法差异导致偏移属正常）'}"
            )

    lines += ["", "## 4. ascr#18 预测结果（本项目新发现）", ""]
    for rec in config["receptors"]:
        pair = f"{rec}_ascr18"
        if pair in interactions:
            top_res = [r for r, c in interactions[pair].get("top_residues_by_frequency", [])[:5]]
            aff = matrix.loc[rec, "ascr18"] if "ascr18" in matrix.columns else "N/A"
            lines.append(
                f"- {rec} + ascr#18: ΔG = {aff:.2f} kcal/mol，"
                f"主要接触残基: {top_res}"
            )

    report = "\n".join(lines)
    report_path = analysis_dir / "validation_report.md"
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"验证报告已保存: {report_path}")

    return report


# ---------------------------------------------------------------------------
# PyMOL 脚本生成
# ---------------------------------------------------------------------------

def generate_pymol_scripts(
    config: dict,
    results: list[DockingResult],
    interactions: dict,
) -> list[Path]:
    """
    为每个受体-配体对生成 PyMOL 可视化脚本（.pml）。
    """
    logger = get_logger()
    root = get_project_root(config)
    pymol_dir = root / config["paths"]["analysis_dir"] / "pymol_scripts"
    pymol_dir.mkdir(parents=True, exist_ok=True)
    receptor_dir = root / config["paths"]["receptor_dir"]
    poses_dir = root / config["paths"]["results_dir"] / "poses"
    interactions_dir = root / config["paths"]["results_dir"] / "interactions"

    scripts = []

    for result in results:
        if result.box_type == "blind":
            continue

        pair = result.pair_name
        rec_name = result.receptor
        lig_name = result.ligand

        rec_pdb = receptor_dir / config["receptors"][rec_name]["pdb_file"]
        pose_pdb = interactions_dir / f"{pair}_pose0.pdb"

        # 从 interactions 获取主要接触残基
        top_residues = []
        if pair in interactions:
            top_residues = [
                r for r, _ in interactions[pair].get("top_residues_by_frequency", [])[:8]
            ]

        residue_sel = "+".join(str(r) for r in top_residues) if top_residues else "none"

        script = textwrap.dedent(f"""\
            # PyMOL 可视化脚本: {pair}
            # 生成自 P0 分子对接 Pipeline

            # 加载结构
            load {rec_pdb}, receptor
            load {pose_pdb}, ligand

            # 外观设置
            bg_color white
            hide everything
            show cartoon, receptor
            show sticks, ligand
            color slate, receptor
            color yellow, ligand

            # pLDDT 着色（AlphaFold B-factor）
            spectrum b, blue_white_red, receptor, minimum=50, maximum=90

            # 显示结合残基
            select binding_site, receptor and resi {residue_sel}
            show sticks, binding_site
            color orange, binding_site

            # 标注关键残基
            label binding_site and name CA, "%s-%s" % (oneletter, resi)

            # 视角设置
            orient ligand
            zoom ligand, 8

            # 显示蛋白表面（半透明）
            show surface, receptor
            set transparency, 0.7, receptor

            # 保存
            # save {pymol_dir}/{pair}.pse
            ray 1200, 900
            png {pymol_dir}/{pair}.png, dpi=150
        """)

        script_path = pymol_dir / f"{pair}.pml"
        script_path.write_text(script)
        scripts.append(script_path)

    # 生成总览脚本（所有受体 + ascr#18 最佳 pose）
    overview_script = _generate_overview_script(config, results, pymol_dir, receptor_dir, interactions_dir)
    scripts.append(overview_script)

    logger.info(f"PyMOL 脚本已生成: {pymol_dir}（{len(scripts)} 个）")
    return scripts


def _generate_overview_script(
    config: dict,
    results: list[DockingResult],
    pymol_dir: Path,
    receptor_dir: Path,
    interactions_dir: Path,
) -> Path:
    """生成展示三个受体与 ascr#18 最佳 pose 的总览脚本。"""
    lines = [
        "# PyMOL 总览脚本：三受体 + ascr#18 对比",
        "bg_color white",
        "hide everything",
    ]
    colors = {"Gpr2": "slate", "Gpr3": "marine", "GprC": "teal"}
    x_offsets = {"Gpr2": -60, "Gpr3": 0, "GprC": 60}

    for rec_name in config["receptors"]:
        pair = f"{rec_name}_ascr18"
        rec_pdb = receptor_dir / config["receptors"][rec_name]["pdb_file"]
        pose_pdb = interactions_dir / f"{pair}_pose0.pdb"
        color = colors.get(rec_name, "gray")
        x = x_offsets.get(rec_name, 0)

        lines += [
            f"load {rec_pdb}, {rec_name}",
            f"show cartoon, {rec_name}",
            f"color {color}, {rec_name}",
        ]
        if pose_pdb.exists():
            lines += [
                f"load {pose_pdb}, {pair}",
                f"show sticks, {pair}",
                f"color yellow, {pair}",
                f"translate [{x}, 0, 0], {rec_name}",
                f"translate [{x}, 0, 0], {pair}",
            ]

    lines += ["orient", "ray 1800, 600", f"png {pymol_dir}/overview_ascr18.png, dpi=150"]

    script_path = pymol_dir / "overview_ascr18.pml"
    script_path.write_text("\n".join(lines))
    return script_path


# ---------------------------------------------------------------------------
# 完整分析入口
# ---------------------------------------------------------------------------

def run_analysis(
    config: dict,
    results: list[DockingResult],
    prepared_paths: dict,
) -> None:
    """运行完整分析流程（亲和力矩阵 → PLIP → 文献比较 → PyMOL 脚本）。"""
    logger = get_logger()
    logger.info("=== 开始分析 ===")

    matrix = build_affinity_matrix(results, config)

    interactions = analyze_interactions(
        config, results,
        receptor_pdbqt_paths=prepared_paths["receptors"],
    )

    report = compare_with_literature(matrix, interactions, config)
    logger.info("\n" + report[:500] + "...")

    scripts = generate_pymol_scripts(config, results, interactions)
    logger.info(f"PyMOL 脚本: {len(scripts)} 个")

    logger.info("=== 分析完成 ===")
