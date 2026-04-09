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
    ├── ifp_all.csv                    # 全部 IFP 矩阵
    ├── contact_frequency.csv          # 残基 × 配体 接触频率
    ├── differential_contacts.csv      # 差异接触残基
    └── figures/                       # 可视化

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


def get_pocket(prot: mda.AtomGroup, lig_center: np.ndarray,
               radius: float = POCKET_RADIUS) -> mda.AtomGroup:
    """选择配体周围 radius Å 内的蛋白残基"""
    dists = np.linalg.norm(prot.positions - lig_center, axis=1)
    near_resids = set(prot.atoms[np.where(dists < radius)[0]].resids)
    if not near_resids:
        raise ValueError(f"No residues within {radius}Å of ligand center {lig_center}")
    pocket_sel = " or ".join([f"resid {rid}" for rid in sorted(near_resids)])
    return prot.select_atoms(pocket_sel)


def analyze_pair(
    rec_pdb_h: Path,
    pose_sdf: Path,
    top_n: int = 20,
) -> pd.DataFrame:
    """对单个 receptor×ligand 对运行 ProLIF IFP"""
    # 读取受体
    u_rec = mda.Universe(str(rec_pdb_h))
    prot = u_rec.select_atoms("protein")

    # 读取配体 pose 坐标（用于定义 pocket）
    suppl_rd = Chem.SDMolSupplier(str(pose_sdf), removeHs=False)
    pose1 = next(iter(suppl_rd))
    if pose1 is None:
        raise ValueError(f"无法读取 SDF: {pose_sdf}")
    conf = pose1.GetConformer()
    lig_center = np.mean(
        [list(conf.GetAtomPosition(i)) for i in range(pose1.GetNumAtoms())],
        axis=0,
    )

    # 选择 pocket
    pocket = get_pocket(prot, lig_center)
    prot_mol = plf.Molecule.from_mda(pocket)

    # 配体 poses
    lig_suppl = plf.sdf_supplier(str(pose_sdf))
    poses = list(lig_suppl[:top_n])

    # 运行 IFP
    fp = plf.Fingerprint()
    fp.run_from_iterable(poses, prot_mol)
    return fp.to_dataframe()


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
    wt_ss_dir = get_results_subdir(config, "wt_singlestage_subdir")
    pose_dir = wt_ss_dir / "poses"
    out_dir = get_results_subdir(config, "ifp_subdir")
    (out_dir / "figures").mkdir(exist_ok=True)

    # 临时目录用于加氢 PDB 和 SDF 转换
    tmp_dir = out_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    all_freq: dict[str, dict[str, dict[str, int]]] = {}  # {pair: {res: {itype: count}}}

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
            print(f"\n  [{pair_name}] 运行 ProLIF...")
            try:
                df = analyze_pair(pdb_h, sdf_path, args.top_n)
                freq = compute_contact_frequency(df)
                all_freq[pair_name] = freq

                # 打印结果
                n_contacts = sum(sum(v.values()) for v in freq.values())
                n_residues = len(freq)
                print(f"    {n_residues} 接触残基, {n_contacts} 总接触次数 (across {len(df)} poses)")

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
            n_poses = args.top_n
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
