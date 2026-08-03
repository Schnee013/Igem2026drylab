"""
ProLIF 交互指纹分析 — 识别选择性决定残基

基于 WT singlestage 对接 pose，使用 ProLIF 生成残基级交互指纹 (IFP)，
通过差异分析识别 ascr18/ascr3/ascr7 选择性相关残基。

文献依据：
  - Vass et al. 2016, Curr Opin Pharmacol 30:59-68（IFP 方法论框架）
  - Bouysset & Fiorucci 2021, J Cheminform 13:72（ProLIF 工具）
  - Haddad et al. 2023（contact accuracy > 0.2 可指导定点突变）

输入：
  - 受体 PDB（OpenBabel 加氢）：experiments/docking-repro/prepared/receptors/*.pdb
  - Pose PDBQT → SDF（obabel 转换）：experiments/docking-repro/results/wt_singlestage/poses/

输出：
  experiments/docking-repro/results/ifp_analysis/
    ├── ifp_all.csv                    # 全部 IFP 矩阵（receptor, ligand, residue, interaction, count, frequency）
    └── contact_frequency.json         # 残基 × 配体 接触频率（嵌套 dict）

用法（Mac 本地）：
    python run_ifp_analysis.py
    python run_ifp_analysis.py --receptors GprC         # 仅分析 GprC
    python run_ifp_analysis.py --top-n 5                # 仅分析 top-5 poses
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_project_root, get_results_subdir, load_config

import numpy as np
import pandas as pd

# Suppress warnings before importing heavy libs
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import prolif as plf
import MDAnalysis as mda
from rdkit import Chem
from rdkit.Chem.AllChem import AssignBondOrdersFromTemplate


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

RECEPTORS = {
    "GprC": "GprC_A0A437AGY2_tm.pdb",
    "Gpr2": "Gpr2_G1X9E2_tm.pdb",
    "Gpr3": "Gpr3_G1XJN1_tm.pdb",
}

LIGANDS = ["ascr1", "ascr18", "ascr3", "ascr7"]

# Hu2024 已知功能残基：权威源在 config.yaml analysis.key_residues
# 由 _build_key_residues() 从 config 动态构建，禁止硬编码副本


def _build_key_residues(config: dict, rec_name: str = "GprC") -> dict[str, dict]:
    """从 config.yaml analysis.key_residues 构建 {RESNAME+SEQPOS: {bw, role, desc}}。"""
    key_res = config.get("analysis", {}).get("key_residues", {}).get(rec_name, {})
    result = {}
    for bw_key, info in key_res.items():
        display_key = f"{info['resname']}{info['seqpos']}"
        result[display_key] = {
            "bw": bw_key.replace("_", "."),
            "role": info["role"],
            "desc": info["desc"],
        }
    return result

# ProLIF 2.1.0 全部可用交互类型（15 种）。
# 默认 9 种 + 非默认 6 种，显式枚举以保证审计可追溯。
# ascarylose 无芳环（Pi*/EdgeToFace/FaceToFace 预期=0）、
# 无金属（Metal*=0）、无卤素（XB*=0）；
# Hydrophobic 应在脂肪链×TM 疏水口袋处检出。
ALL_INTERACTION_TYPES = [
    "Anionic", "Cationic", "CationPi", "PiCation",
    "EdgeToFace", "FaceToFace", "PiStacking",
    "HBAcceptor", "HBDonor", "Hydrophobic",
    "MetalAcceptor", "MetalDonor",
    "VdWContact",
    "XBAcceptor", "XBDonor",
]

POCKET_RADIUS = 15.0  # Å, 选择配体周围的蛋白残基


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ProLIF IFP 分析")
    parser.add_argument("--receptors", nargs="+", default=list(RECEPTORS.keys()))
    parser.add_argument("--ligands", nargs="+", default=LIGANDS)
    parser.add_argument("--top-n", type=int, default=20,
                        help="分析的 pose 数量（默认全部 20）")
    parser.add_argument("--project-root", default=None,
                        help="覆盖 config.yaml 中的 project_root")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    parser.add_argument("--pose-subdir", default=None,
                        help="覆盖 pose 目录（相对 results_dir）。默认用 config.paths.wt_singlestage_subdir。"
                             "例：wt_singlestage_gpr3_f_test 指向 Gpr3 方案 F 重跑 pose。")
    parser.add_argument("--out-subdir", default=None,
                        help="覆盖 IFP 输出目录。默认 ifp_analysis。")
    return parser.parse_args()


def add_hydrogens(pdb_path: Path, out_path: Path) -> Path:
    """用 OpenBabel 给受体 PDB 加氢（保留残基信息）"""
    if out_path.exists():
        return out_path
    result = subprocess.run(
        ["obabel", str(pdb_path), "-O", str(out_path), "-h"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"obabel 加氢失败: {result.stderr}")
    return out_path


def pdbqt_to_sdf(pdbqt_path: Path, sdf_path: Path) -> Path:
    """用 OpenBabel 将多 model PDBQT 转为单个 SDF 文件"""
    if sdf_path.exists():
        return sdf_path
    result = subprocess.run(
        ["obabel", str(pdbqt_path), "-O", str(sdf_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"obabel PDBQT→SDF 失败: {result.stderr}")
    return sdf_path


def fix_sdf_valence(sdf_path: Path, top_n: int = 20,
                    template_smiles: str | None = None) -> list[plf.Molecule]:
    """读取 SDF 并修复 implicit H，返回 ProLIF Molecule 列表。

    OpenBabel 的 PDBQT→SDF 转换不含氢原子，V2000 valence 仅反映显式键数。
    RDKit 在无显式 H 的 V2000 SDF 中通常将 noImplicit=True + numHs=0，
    导致 Hydrophobic SMARTS（要求 C&H2 等）匹配失败。修复：清除
    NoImplicit 标志，让 RDKit 按标准化合价推导 implicit H。

    若提供 template_smiles（pH 7.4 去质子 SMILES），则通过
    AssignBondOrdersFromTemplate 注入形式电荷，使 ProLIF Anionic/Cationic
    盐桥检测生效。template_smiles=None 时保持原行为（向后兼容）。
    """
    if not sdf_path.exists():
        raise FileNotFoundError(f"SDF not found: {sdf_path}")

    # 构建电荷模板
    template = None
    if template_smiles is not None:
        tmpl = Chem.MolFromSmiles(template_smiles)
        if tmpl is None:
            print(f"    [WARN] fix_sdf_valence: 无效 template_smiles={template_smiles!r}，跳过电荷注入")
        else:
            template = Chem.RemoveHs(tmpl)

    suppl = Chem.SDMolSupplier(str(sdf_path), removeHs=False, sanitize=False)
    molecules = []
    for i, mol in enumerate(suppl):
        if mol is None:
            continue
        if len(molecules) >= top_n:
            break
        rw = Chem.RWMol(mol)
        for atom in rw.GetAtoms():
            atom.SetNoImplicit(False)
        try:
            Chem.SanitizeMol(rw)
        except Exception as e:
            print(f"    [WARN] fix_sdf_valence: pose {i} sanitization failed ({e}), skipping")
            continue

        # 注入形式电荷（通过 pH 7.4 模板）
        if template is not None:
            try:
                mol_noH = Chem.RemoveHs(rw.GetMol())
                charged = AssignBondOrdersFromTemplate(template, mol_noH)
                molecules.append(plf.Molecule.from_rdkit(charged))
            except Exception as e:
                print(f"    [WARN] fix_sdf_valence: pose {i} 模板匹配失败 ({e})，使用无电荷版本")
                molecules.append(plf.Molecule.from_rdkit(rw.GetMol()))
        else:
            molecules.append(plf.Molecule.from_rdkit(rw.GetMol()))

    if not molecules:
        raise ValueError(f"fix_sdf_valence: no valid molecules parsed from {sdf_path}")
    return molecules


def fix_receptor_charges(prot_mol: Chem.Mol) -> Chem.Mol:
    """注入受体 pH 7.4 形式电荷，使 ProLIF 盐桥检测生效。

    修改范围（只改标准氨基酸中确定带电的基团）：
    - ARG guanidinium: NE 原子 SetFormalCharge(+1)（pKa ~12.5，完全带电）
    - ASP OD2 / GLU OE2 carboxylate: SetFormalCharge(-1) + 删除 OH 的 H
      （pKa ~4，pH 7.4 完全去质子）

    不修改：LYS（需插入第3个H的3D坐标）、HIS（pKa~6 近中性）、末端（远离口袋）。
    """
    rw = Chem.RWMol(prot_mol)

    # ARG guanidinium: NE → +1
    # SMARTS 匹配 guanidinium C=N，标记 NE（NH0X2）
    arg_smarts = Chem.MolFromSmarts("[NH0X2:1]=[CX3]([NH2X3])[NH2X3]")
    if arg_smarts is not None:
        for match in prot_mol.GetSubstructMatches(arg_smarts):
            ne_idx = match[0]
            atom = rw.GetAtomWithIdx(ne_idx)
            mi = atom.GetMonomerInfo()
            if mi and mi.GetResidueName().strip() == "ARG":
                atom.SetFormalCharge(1)

    # ASP OD2 / GLU OE2: 去质子 → -1，删除 OH 的 H
    asp_glu_smarts = Chem.MolFromSmarts("[OX2H1:1]-[CX3](=[OX1])")
    h_to_remove: set[int] = set()
    if asp_glu_smarts is not None:
        for match in prot_mol.GetSubstructMatches(asp_glu_smarts):
            o_idx = match[0]
            atom = rw.GetAtomWithIdx(o_idx)
            mi = atom.GetMonomerInfo()
            if mi and mi.GetResidueName().strip() in ("ASP", "GLU"):
                atom_name = mi.GetName().strip()
                if atom_name in ("OD2", "OE2"):
                    atom.SetFormalCharge(-1)
                    atom.SetNoImplicit(True)
                    for nb in rw.GetAtomWithIdx(o_idx).GetNeighbors():
                        if nb.GetAtomicNum() == 1:
                            h_to_remove.add(nb.GetIdx())

    for h_idx in sorted(h_to_remove, reverse=True):
        rw.RemoveAtom(h_idx)

    try:
        Chem.SanitizeMol(rw)
    except Exception as e:
        print(f"    [WARN] fix_receptor_charges: sanitization failed ({e}), 返回原始分子")
        return prot_mol

    return rw.GetMol()


def get_pocket(prot: mda.AtomGroup, lig_center: np.ndarray,
               radius: float = POCKET_RADIUS) -> mda.AtomGroup:
    """选择配体周围 radius Å 内的蛋白残基"""
    dists = np.linalg.norm(prot.positions - lig_center, axis=1)
    near_resids = set(prot.atoms[np.where(dists < radius)[0]].resids)
    if not near_resids:
        raise ValueError(f"No residues within {radius}Å of ligand center {lig_center}")
    pocket_sel = " or ".join([f"resid {rid}" for rid in sorted(near_resids)])
    return prot.select_atoms(pocket_sel)


def get_pose_set_pocket(
    prot: mda.AtomGroup,
    pose_sdf: Path,
    *,
    top_n: int,
    radius: float = POCKET_RADIUS,
) -> mda.AtomGroup:
    """选择任一 pose 重原子 radius Å 内的蛋白残基并集。

    frame-repair 主线必须对完整 pose 分布做 IFP。只按 MODEL 1 质心选择
    pocket 会静默遗漏其他 MODEL 附近的接触，因此这里用前 ``top_n`` 个
    可解析 SDF record 的全部重原子构造残基并集。
    """
    supplier = Chem.SDMolSupplier(
        str(pose_sdf),
        removeHs=False,
        sanitize=False,
        strictParsing=True,
    )
    ligand_coordinate_sets: list[np.ndarray] = []
    for record_index, molecule in enumerate(supplier, start=1):
        if record_index > top_n:
            break
        if molecule is None:
            raise ValueError(
                f"SDF record {record_index} 无法解析，拒绝构造 pose-set pocket"
            )
        conformer = molecule.GetConformer()
        coordinates = np.asarray(
            [
                list(conformer.GetAtomPosition(atom.GetIdx()))
                for atom in molecule.GetAtoms()
                if atom.GetAtomicNum() > 1
            ],
            dtype=float,
        )
        if not len(coordinates):
            raise ValueError(f"SDF record {record_index} 不含配体重原子")
        ligand_coordinate_sets.append(coordinates)
    if len(ligand_coordinate_sets) != top_n:
        raise ValueError(
            f"pose-set pocket 需要 {top_n} 个 SDF records，"
            f"实际 {len(ligand_coordinate_sets)}"
        )

    near_resids: set[int] = set()
    protein_positions = np.asarray(prot.positions, dtype=float)
    for ligand_coordinates in ligand_coordinate_sets:
        distances = np.linalg.norm(
            protein_positions[:, np.newaxis, :]
            - ligand_coordinates[np.newaxis, :, :],
            axis=2,
        )
        atom_indices = np.where(np.any(distances < radius, axis=1))[0]
        near_resids.update(int(value) for value in prot.atoms[atom_indices].resids)
    if not near_resids:
        raise ValueError(
            f"No residues within {radius}Å of any ligand atom in {pose_sdf}"
        )
    pocket_sel = " or ".join(f"resid {rid}" for rid in sorted(near_resids))
    return prot.select_atoms(pocket_sel)


def analyze_pair(
    rec_pdb_h: Path,
    pose_sdf: Path,
    top_n: int = 20,
    template_smiles: str | None = None,
    pocket_mode: str = "pose1_centroid",
) -> tuple[pd.DataFrame, int]:
    """对单个 receptor×ligand 对运行 ProLIF IFP，返回 (IFP DataFrame, 实际 pose 数)

    template_smiles: pH 7.4 去质子配体 SMILES（来自 config.yaml smiles_pH74），
    用于为配体注入形式电荷，启用 ProLIF Anionic/Cationic 盐桥检测。
    None 时保持原行为。
    """
    # 读取受体
    u_rec = mda.Universe(str(rec_pdb_h))
    prot = u_rec.select_atoms("protein")

    if pocket_mode == "pose1_centroid":
        suppl_rd = Chem.SDMolSupplier(str(pose_sdf), removeHs=False)
        pose1 = next(iter(suppl_rd))
        if pose1 is None:
            raise ValueError(f"无法读取 SDF: {pose_sdf}")
        conf = pose1.GetConformer()
        lig_center = np.mean(
            [list(conf.GetAtomPosition(i)) for i in range(pose1.GetNumAtoms())],
            axis=0,
        )
        pocket = get_pocket(prot, lig_center)
    elif pocket_mode == "all_pose_heavy_atom_union":
        pocket = get_pose_set_pocket(prot, pose_sdf, top_n=top_n)
    else:
        raise ValueError(f"未知 IFP pocket_mode: {pocket_mode}")

    # 注入受体 pH 7.4 形式电荷（ARG +1 / ASP,GLU -1）
    prot_mol = plf.Molecule.from_mda(pocket)
    rdkit_charged = fix_receptor_charges(prot_mol)
    prot_mol = plf.Molecule.from_rdkit(rdkit_charged)

    # 配体 poses（修复 PDBQT→SDF 转换导致的 implicit H 丢失；注入 pH 7.4 电荷）
    poses = fix_sdf_valence(pose_sdf, top_n, template_smiles=template_smiles)

    # 运行 IFP — 显式枚举全部 15 种交互类型
    fp = plf.Fingerprint(interactions=ALL_INTERACTION_TYPES)
    fp.run_from_iterable(poses, prot_mol)
    return fp.to_dataframe(), len(poses)


def compute_contact_frequency(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    """从 IFP DataFrame 计算残基接触频率

    ProLIF DataFrame 列为 3 级 MultiIndex: (ligand, protein, interaction)
    """
    freq: dict[str, dict[str, int]] = {}
    for col in df.columns:
        # col = ('UNL1', 'ASN60.A', 'VdWContact')
        res_id = str(col[1])   # protein residue
        itype = col[2]         # interaction type
        count = int(df[col].sum())
        if count > 0:
            freq.setdefault(res_id, {})[itype] = count
    return freq


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root
    root = get_project_root(config)
    rec_dir = root / config["paths"]["prepared_dir"] / "receptors"
    if args.pose_subdir:
        wt_ss_dir = root / config["paths"]["results_dir"] / args.pose_subdir
        print(f"[INFO] pose_subdir 覆盖: {wt_ss_dir}")
    else:
        wt_ss_dir = get_results_subdir(config, "wt_singlestage_subdir")
    pose_dir = wt_ss_dir / "poses"
    if args.out_subdir:
        out_dir = root / config["paths"]["results_dir"] / args.out_subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] out_subdir 覆盖: {out_dir}")
    else:
        out_dir = get_results_subdir(config, "ifp_subdir")

    # 临时目录用于加氢 PDB 和 SDF 转换
    tmp_dir = out_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    all_freq: dict[str, dict[str, dict[str, int]]] = {}  # {pair: {res: {itype: count}}}
    pair_n_poses: dict[str, int] = {}  # {pair: actual_pose_count}

    for rec_name in args.receptors:
        pdb_path = rec_dir / RECEPTORS[rec_name]
        if not pdb_path.exists():
            print(f"  [SKIP] 受体 PDB 不存在: {pdb_path}")
            continue

        # 加氢
        pdb_h = tmp_dir / f"{rec_name}_withH.pdb"
        print(f"\n{'='*60}")
        print(f"  受体: {rec_name}")
        print(f"{'='*60}")
        add_hydrogens(pdb_path, pdb_h)

        for lig_name in args.ligands:
            pair_name = f"{rec_name}_{lig_name}"
            pdbqt_path = pose_dir / pair_name / f"{pair_name}_poses.pdbqt"
            if not pdbqt_path.exists():
                print(f"  [SKIP] Pose 不存在: {pdbqt_path}")
                continue

            # PDBQT → SDF
            sdf_path = tmp_dir / f"{pair_name}_poses.sdf"
            pdbqt_to_sdf(pdbqt_path, sdf_path)

            # IFP 分析
            lig_cfg = config.get("ligands", {}).get(lig_name, {})
            template_smiles = lig_cfg.get("smiles_pH74")
            print(f"\n  [{pair_name}] 运行 ProLIF...")
            try:
                df, n_poses = analyze_pair(pdb_h, sdf_path, args.top_n,
                                           template_smiles=template_smiles)
                freq = compute_contact_frequency(df)
                all_freq[pair_name] = freq
                pair_n_poses[pair_name] = n_poses

                # 打印结果
                n_contacts = sum(sum(v.values()) for v in freq.values())
                n_residues = len(freq)
                print(f"    {n_residues} 接触残基, {n_contacts} 总接触次数 (across {n_poses} poses)")

                # 高频残基（>50% poses）
                threshold = len(df) * 0.5
                high_freq = {
                    res: itypes
                    for res, itypes in freq.items()
                    if sum(itypes.values()) >= threshold
                }
                if high_freq:
                    print(f"    高频残基 (>{int(threshold)} poses):")
                    for res, itypes in sorted(high_freq.items(),
                                              key=lambda x: sum(x[1].values()),
                                              reverse=True):
                        total = sum(itypes.values())
                        detail = ", ".join(f"{k}={v}" for k, v in itypes.items())
                        print(f"      {res}: {total}/{len(df)} ({detail})")
            except Exception as e:
                print(f"    [ERROR] {e}")
                continue

    if not all_freq:
        print("\n没有成功分析的对接对！")
        sys.exit(1)

    # =====================================================================
    # 差异接触分析
    # =====================================================================
    print("\n" + "=" * 70)
    print("  差异接触分析")
    print("=" * 70)

    for rec_name in args.receptors:
        print(f"\n--- {rec_name} ---")

        # 收集每个配体的接触残基集合
        lig_contacts: dict[str, set[str]] = {}
        for lig_name in args.ligands:
            pair = f"{rec_name}_{lig_name}"
            if pair in all_freq:
                lig_contacts[lig_name] = set(all_freq[pair].keys())
            else:
                lig_contacts[lig_name] = set()

        if "ascr18" not in lig_contacts or "ascr3" not in lig_contacts:
            print("  缺少 ascr18 或 ascr3 数据，跳过")
            continue

        ascr18_only = lig_contacts["ascr18"] - lig_contacts["ascr3"]
        ascr3_only = lig_contacts["ascr3"] - lig_contacts["ascr18"]
        shared = lig_contacts["ascr18"] & lig_contacts["ascr3"]

        print(f"\n  ascr18 独有接触残基（保护位点，不应突变）: {len(ascr18_only)}")
        for r in sorted(ascr18_only):
            itypes = all_freq[f"{rec_name}_ascr18"].get(r, {})
            print(f"    {r}: {itypes}")

        print(f"\n  ascr3 独有接触残基（突变候选，削弱 ascr3 偏好）: {len(ascr3_only)}")
        for r in sorted(ascr3_only):
            itypes = all_freq[f"{rec_name}_ascr3"].get(r, {})
            print(f"    {r}: {itypes}")

        print(f"\n  共享接触残基: {len(shared)}")
        for r in sorted(shared):
            i18 = all_freq[f"{rec_name}_ascr18"].get(r, {})
            i3 = all_freq[f"{rec_name}_ascr3"].get(r, {})
            t18 = sum(i18.values())
            t3 = sum(i3.values())
            print(f"    {r}: ascr18={t18}, ascr3={t3}")

        # ascr7 参照
        if "ascr7" in lig_contacts:
            ascr7_only = lig_contacts["ascr7"] - lig_contacts["ascr18"] - lig_contacts["ascr3"]
            if ascr7_only:
                print(f"\n  ascr7 独有: {sorted(ascr7_only)}")

    # =====================================================================
    # Hu2024 阳性对照验证（GprC）
    # =====================================================================
    print("\n" + "=" * 70)
    print("  Hu2024 阳性对照验证（GprC）")
    print("=" * 70)

    gprc_18 = all_freq.get("GprC_ascr18", {})
    gprc_3 = all_freq.get("GprC_ascr3", {})

    hu2024_residues = _build_key_residues(config, "GprC")
    for res_3letter, info in hu2024_residues.items():
        bw = info["bw"]
        role = info["role"]
        desc = info["desc"]
        # ProLIF 格式：如 ASN60.A
        plf_key = f"{res_3letter}.A"
        c18 = gprc_18.get(plf_key, {})
        c3 = gprc_3.get(plf_key, {})
        total_18 = sum(c18.values())
        total_3 = sum(c3.values())

        if role == "pos":
            # 阳性对照：N2.57/R6.45 应有接触；S2.41 远离 binding site 无接触也 OK
            if "far" in desc.lower() or "远离" in desc:
                status = "PASS (no contact expected)"
            elif total_18 > 0 or total_3 > 0:
                status = "PASS"
            else:
                status = "MISS"
        else:  # neg
            status = "OK (neg ctrl)"

        print(f"  {bw} ({res_3letter}): [{status}]  ascr18={total_18}  ascr3={total_3}  {c18}")
        if role == "neg":
            print(f"    ↳ 阴性对照：突变无影响，接触≠功能必需")

    # =====================================================================
    # 交互类型汇总（审计链）
    # =====================================================================
    print("\n" + "=" * 70)
    print("  交互类型检出汇总")
    print("=" * 70)
    type_totals: dict[str, int] = {}
    for pair_freq in all_freq.values():
        for res_itypes in pair_freq.values():
            for itype, count in res_itypes.items():
                type_totals[itype] = type_totals.get(itype, 0) + count
    for itype in ALL_INTERACTION_TYPES:
        total = type_totals.get(itype, 0)
        status = f"{total} hits" if total > 0 else "0 (expected for ascarylose)"
        print(f"  {itype:20s}: {status}")

    # =====================================================================
    # 保存结果
    # =====================================================================

    # 保存全部频率数据为 JSON
    out_json = out_dir / "contact_frequency.json"
    out_json.write_text(
        json.dumps(all_freq, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n接触频率数据: {out_json}")

    # 保存差异接触为 CSV
    rows = []
    for rec_name in args.receptors:
        for lig_name in args.ligands:
            pair = f"{rec_name}_{lig_name}"
            if pair not in all_freq:
                continue
            n_poses = pair_n_poses.get(pair, args.top_n)
            for res, itypes in all_freq[pair].items():
                for itype, count in itypes.items():
                    rows.append({
                        "receptor": rec_name,
                        "ligand": lig_name,
                        "residue": res,
                        "interaction": itype,
                        "count": count,
                        "frequency": count / n_poses,
                    })
    df_all = pd.DataFrame(rows)
    csv_path = out_dir / "ifp_all.csv"
    df_all.to_csv(csv_path, index=False)
    print(f"完整 IFP 数据: {csv_path}")


if __name__ == "__main__":
    main()
