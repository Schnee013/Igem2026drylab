"""Top 6 突变体 PyMOL 可视化素材生成器。

为 Tier 1 Top 6 突变体（Gpr2 M327A/M327D/R59F, Gpr3 V138R/F170E/I141A）生成
**分离的**受体 PDB 和配体 PDB 供 PyMOL 加载。

选择分离而非合并 complex 的原因：
    用户加载后需要分别操作受体和配体（独立着色、选择、隐藏等）。PyMOL 的
    ``polymer.protein`` / ``organic`` 选择子在加载多个对象后会自动跨对象生效，
    所以样式脚本可以完全不依赖具体对象名。

输出结构：
    experiments/docking-repro/analysis/pymol_top6/
    ├── receptors/      # 8 个受体 PDB（WT ×2 + mutants ×6）
    │                     直接复制 prepared/ 或 ifp_analysis_mutants/receptors/
    └── ligands/        # 16 个配体 PDB（每个受体 × ascr18/ascr3）
                          obabel 抽取 MODEL 1 并改写为 HETATM chain X resi 901 resn LIG
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from utils import get_project_root, load_config

# ---------------------------------------------------------------------------
# 配置：Top 6 突变体清单
# ---------------------------------------------------------------------------
TOP6: list[tuple[str, str]] = [
    ("Gpr2", "M327A"),
    ("Gpr2", "M327D"),
    ("Gpr2", "R59F"),
    ("Gpr3", "V138R"),
    ("Gpr3", "F170E"),
    ("Gpr3", "I141A"),
]
LIGANDS = ["ascr18", "ascr3"]

WT_RECEPTOR_FILES = {
    "Gpr2": "Gpr2_G1X9E2_tm.pdb",
    "Gpr3": "Gpr3_G1XJN1_tm.pdb",
    "GprC": "GprC_A0A437AGY2_tm.pdb",
}


def extract_top_pose_as_pdb(pdbqt_path: Path, out_pdb: Path) -> None:
    """obabel 从多模型 PDBQT 抽 MODEL 1 → PDB。"""
    cmd = [
        "obabel",
        str(pdbqt_path),
        "-O",
        str(out_pdb),
        "-f",
        "1",
        "-l",
        "1",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def rewrite_ligand_records(
    src_pdb: Path, dst_pdb: Path, resname: str = "LIG"
) -> None:
    """把 obabel 生成的配体 PDB 里的 ATOM/HETATM 行规范化。

    - 统一为 HETATM
    - chain=X, resSeq=901, resname=LIG
    - 保留坐标/occ/B/elem
    - 保留 CONECT
    - 加 END 行
    """
    lines_out: list[str] = ["REMARK Top 1 Vina pose (extracted by obabel -f 1 -l 1)"]
    for line in src_pdb.read_text().splitlines():
        if line.startswith(("ATOM", "HETATM")):
            if len(line) < 54:
                continue
            serial = int(line[6:11])
            atom_name = line[12:16]
            coord_and_tail = line[26:]  # iCode + fill + x + y + z + occ + B + ... + elem
            new_line = (
                f"HETATM{serial:>5d} {atom_name}"
                f" {resname} X 901"
                f"{coord_and_tail}"
            )
            lines_out.append(new_line)
        elif line.startswith("CONECT"):
            lines_out.append(line)
    lines_out.append("END")
    dst_pdb.write_text("\n".join(lines_out) + "\n")


def main() -> None:
    config = load_config(Path(__file__).parent / "config.yaml")
    root = get_project_root(config)

    prepared_dir = root / config["paths"]["prepared_dir"] / "receptors"
    wt_poses_dir = root / config["paths"]["results_dir"] / "wt_singlestage" / "poses"
    mut_root = root / config["paths"]["results_dir"] / "ifp_analysis_mutants"
    mut_rec_dir = mut_root / "receptors"
    mut_pose_dir = mut_root / "poses"

    base = root / config["paths"]["analysis_dir"] / "pymol_top6"
    rec_out = base / "receptors"
    lig_out = base / "ligands"
    tmp_dir = base / "_tmp"
    rec_out.mkdir(parents=True, exist_ok=True)
    lig_out.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    rec_done: list[str] = []
    lig_done: list[str] = []

    # ---- WT 受体 + 配体 ----
    wt_recs_needed = sorted({rec for rec, _ in TOP6})
    for rec in wt_recs_needed:
        src_rec = prepared_dir / WT_RECEPTOR_FILES[rec]
        if not src_rec.exists():
            print(f"[SKIP] 缺 WT 受体: {src_rec}")
            continue
        dst_rec = rec_out / f"{rec}_WT.pdb"
        shutil.copyfile(src_rec, dst_rec)
        rec_done.append(dst_rec.name)
        print(f"[REC] {dst_rec.name}")

        for lig in LIGANDS:
            pose_pdbqt = wt_poses_dir / f"{rec}_{lig}" / f"{rec}_{lig}_poses.pdbqt"
            if not pose_pdbqt.exists():
                print(f"[SKIP] 缺 WT pose: {pose_pdbqt}")
                continue
            raw_lig = tmp_dir / f"{rec}_WT_{lig}_raw.pdb"
            extract_top_pose_as_pdb(pose_pdbqt, raw_lig)
            dst_lig = lig_out / f"{rec}_WT_{lig}.pdb"
            rewrite_ligand_records(raw_lig, dst_lig)
            lig_done.append(dst_lig.name)
            print(f"[LIG] {dst_lig.name}")

    # ---- Mutant 受体 + 配体 ----
    for rec, mut in TOP6:
        src_rec = mut_rec_dir / f"{rec}_{mut}_tm.pdb"
        if not src_rec.exists():
            print(f"[SKIP] 缺突变体受体: {src_rec}")
            continue
        dst_rec = rec_out / f"{rec}_{mut}.pdb"
        shutil.copyfile(src_rec, dst_rec)
        rec_done.append(dst_rec.name)
        print(f"[REC] {dst_rec.name}")

        for lig in LIGANDS:
            pose_pdbqt = mut_pose_dir / f"{rec}_{mut}_{lig}_poses.pdbqt"
            if not pose_pdbqt.exists():
                print(f"[SKIP] 缺突变体 pose: {pose_pdbqt}")
                continue
            raw_lig = tmp_dir / f"{rec}_{mut}_{lig}_raw.pdb"
            extract_top_pose_as_pdb(pose_pdbqt, raw_lig)
            dst_lig = lig_out / f"{rec}_{mut}_{lig}.pdb"
            rewrite_ligand_records(raw_lig, dst_lig)
            lig_done.append(dst_lig.name)
            print(f"[LIG] {dst_lig.name}")

    # 清理临时文件
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    print(f"\n生成 {len(rec_done)} 个受体 PDB + {len(lig_done)} 个配体 PDB 于 {base}")


if __name__ == "__main__":
    main()
