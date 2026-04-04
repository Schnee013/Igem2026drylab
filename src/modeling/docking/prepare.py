"""
受体和配体准备模块。

受体: PDB → PDBQT（BioPython 清理 + OpenBabel 加氢/赋电荷）
配体: SDF → PDBQT（RDKit 加氢 + Meeko 生成 PDBQT）
"""

from __future__ import annotations

import json
from pathlib import Path

from Bio import PDB
from openbabel import openbabel as ob
from rdkit import Chem
from rdkit.Chem import AllChem

from utils import get_logger, get_project_root, resolve_path


# ---------------------------------------------------------------------------
# TM 域提取
# ---------------------------------------------------------------------------

def extract_tm_domain(
    pdb_path: Path,
    output_path: Path,
    plddt_threshold: float = 80.0,
    min_helix_length: int = 18,
    flank: int = 5,
) -> tuple[int, int]:
    """
    从 AlphaFold PDB 提取跨膜（TM）域，匹配 Hu2024 "transmembrane portions" 策略。

    原理：AlphaFold PDB 的 B-factor 列存储 pLDDT 置信度（0-100）。
    TM 螺旋区 pLDDT 通常 > 80，N 端信号肽和 C 端尾部 < 70（无序）。
    找到所有连续 ≥18 个残基 pLDDT > 80 的区段作为 TM 螺旋候选，
    保留从第一个候选前 flank 残基到最后一个候选后 flank 残基的范围。

    Args:
        pdb_path: AlphaFold 受体 PDB 路径
        output_path: TM-only PDB 输出路径
        plddt_threshold: pLDDT 阈值（默认 80）
        min_helix_length: 最短 TM 螺旋长度（默认 18 残基）
        flank: TM 域边界外额外保留的残基数（默认 5）

    Returns:
        (first_res_id, last_res_id) TM 域的残基号范围
    """
    logger = get_logger()
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("rec", str(pdb_path))
    chain = structure[0]["A"]

    # 收集所有标准残基的 (残基号, pLDDT)
    residue_info: list[tuple[int, float]] = []
    for res in chain.get_residues():
        if res.get_id()[0] != " ":  # 跳过 HETATM
            continue
        if "CA" not in res:
            continue
        plddt = res["CA"].get_bfactor()
        residue_info.append((res.get_id()[1], plddt))

    if not residue_info:
        raise ValueError(f"PDB {pdb_path.name} 中无标准残基")

    n = len(residue_info)

    def _find_tm_segments(threshold: float) -> list[tuple[int, int]]:
        """在给定 pLDDT 阈值下寻找 TM 螺旋候选区段（序列索引）。"""
        is_high = [plddt >= threshold for _, plddt in residue_info]
        segments = []
        i = 0
        while i < n:
            if is_high[i]:
                j = i
                while j < n and is_high[j]:
                    j += 1
                if j - i >= min_helix_length:
                    segments.append((i, j - 1))
                i = j
            else:
                i += 1
        return segments

    tm_segments = _find_tm_segments(plddt_threshold)
    if len(tm_segments) < 5:
        fallback_threshold = max(plddt_threshold - 10.0, 60.0)  # 相对降低，不硬编码 70
        logger.warning(
            f"{pdb_path.name}: pLDDT>{plddt_threshold} 仅找到 {len(tm_segments)} 个 TM 候选，"
            f"降低阈值到 {fallback_threshold} 重试"
        )
        tm_segments = _find_tm_segments(fallback_threshold)

    if not tm_segments:
        logger.warning(f"{pdb_path.name}: 无法识别 TM 域，使用全长蛋白（精度下降）")
        first_res_id = residue_info[0][0]
        last_res_id = residue_info[-1][0]
    else:
        first_idx = max(0, tm_segments[0][0] - flank)
        last_idx = min(n - 1, tm_segments[-1][1] + flank)
        first_res_id = residue_info[first_idx][0]
        last_res_id = residue_info[last_idx][0]
        n_tm = last_idx - first_idx + 1
        # 7TM 蛋白应有 5-7 个 TM 螺旋；< 5 个时提示质量不足
        if len(tm_segments) < 5:
            logger.warning(
                f"{pdb_path.name}: 仅识别到 {len(tm_segments)} 个 TM 候选螺旋（期望 5-7 个），"
                f"TM 提取质量可能不足，保留残基 {first_res_id}–{last_res_id}（{n} → {n_tm} 残基）"
            )
        else:
            logger.info(
                f"{pdb_path.name}: 识别到 {len(tm_segments)} 个 TM 候选螺旋，"
                f"保留残基 {first_res_id}–{last_res_id}（{n} → {n_tm} 残基）"
            )

    class TmSelect(PDB.Select):
        def accept_chain(self, c):
            return c.id == "A"

        def accept_residue(self, res):
            rid = res.get_id()[1]
            return res.get_id()[0] == " " and first_res_id <= rid <= last_res_id

    io = PDB.PDBIO()
    io.set_structure(structure)
    io.save(str(output_path), TmSelect())
    return first_res_id, last_res_id


# ---------------------------------------------------------------------------
# 受体准备
# ---------------------------------------------------------------------------

def _clean_pdb(pdb_path: Path, output_path: Path) -> None:
    """去除水分子、HETATM，只保留 chain A，写出干净的 PDB。"""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("rec", str(pdb_path))

    # 自定义 PDBIO select：只保留 chain A 的标准残基
    class CleanSelect(PDB.Select):
        def accept_chain(self, chain):
            return chain.id == "A"

        def accept_residue(self, residue):
            # 排除 HETATM（水、小分子）
            return residue.get_id()[0] == " "

    io = PDB.PDBIO()
    io.set_structure(structure)
    io.save(str(output_path), CleanSelect())


def prepare_receptor(pdb_path: str | Path, output_dir: str | Path) -> Path:
    """
    将受体 PDB 文件转换为 AutoDock Vina 所需的 PDBQT 格式。

    流程:
    1. BioPython 清理（去水、只保留 chain A）
    2. OpenBabel: 加极性氢 + Gasteiger 电荷 → 输出 PDBQT

    Args:
        pdb_path: 原始受体 PDB 路径
        output_dir: PDBQT 输出目录

    Returns:
        输出 PDBQT 文件路径
    """
    logger = get_logger()
    pdb_path = Path(pdb_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = pdb_path.stem
    cleaned_pdb = output_dir / f"{stem}_cleaned.pdb"
    output_pdbqt = output_dir / f"{stem}.pdbqt"

    logger.info(f"准备受体: {pdb_path.name}")

    # Step 1: 清理 PDB
    _clean_pdb(pdb_path, cleaned_pdb)
    logger.debug(f"  清理后 PDB: {cleaned_pdb}")

    # Step 2: OpenBabel 转换 PDB → PDBQT（rigid receptor 格式，不含 ROOT/BRANCH）
    ob_conv = ob.OBConversion()
    ob_conv.SetInAndOutFormats("pdb", "pdbqt")
    ob_conv.AddOption("r", ob.OBConversion.OUTOPTIONS)  # rigid receptor 模式

    mol = ob.OBMol()
    if not ob_conv.ReadFile(mol, str(cleaned_pdb)):
        raise RuntimeError(f"OpenBabel 无法读取: {cleaned_pdb}")

    # 加氢（极性氢）
    mol.AddHydrogens(True, True, 7.4)  # polaronly=True, correctForPH=True, pH=7.4

    # Gasteiger 电荷
    charge_model = ob.OBChargeModel.FindType("gasteiger")
    if charge_model:
        charge_model.ComputeCharges(mol)

    if not ob_conv.WriteFile(mol, str(output_pdbqt)):
        raise RuntimeError(f"OpenBabel 无法写入: {output_pdbqt}")

    n_atoms = mol.NumAtoms()
    logger.info(f"  受体 PDBQT 完成: {output_pdbqt.name}（{n_atoms} 个原子）")
    return output_pdbqt


# ---------------------------------------------------------------------------
# 配体准备
# ---------------------------------------------------------------------------

def prepare_ligand(sdf_path: str | Path, output_dir: str | Path, ph: float = 7.4) -> Path:
    """
    将配体 SDF 文件转换为 AutoDock Vina 所需的 PDBQT 格式。

    流程:
    1. RDKit 读取 SDF → 加氢 → MMFF 能量最小化
    2. Meeko MoleculePreparation → 生成 PDBQT（自动处理可旋转键）

    Args:
        sdf_path: 配体 SDF 文件路径
        output_dir: PDBQT 输出目录
        ph: 质子化 pH（影响电荷状态）

    Returns:
        输出 PDBQT 文件路径
    """
    logger = get_logger()
    sdf_path = Path(sdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = sdf_path.stem
    output_pdbqt = output_dir / f"{stem}.pdbqt"

    logger.info(f"准备配体: {sdf_path.name}")

    # Step 1: RDKit 读取 SDF
    mol = Chem.MolFromMolFile(str(sdf_path), removeHs=False)
    if mol is None:
        # 尝试不带氢的读取
        mol = Chem.MolFromMolFile(str(sdf_path), removeHs=True)
    if mol is None:
        raise RuntimeError(f"RDKit 无法读取: {sdf_path}")

    # 添加氢
    mol = Chem.AddHs(mol)

    # 如果没有 3D 坐标则生成
    if mol.GetNumConformers() == 0:
        AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())

    # MMFF 能量最小化
    result = AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)
    if result == 1:
        logger.warning(f"  {sdf_path.name}: MMFF 最小化未收敛，使用当前坐标继续")
    elif result == -1:
        logger.warning(f"  {sdf_path.name}: MMFF 参数化失败，跳过最小化")

    # Step 2: Meeko 准备 PDBQT
    try:
        from meeko import MoleculePreparation, PDBQTWriterLegacy

        mk_prep = MoleculePreparation()
        molsetup_list = mk_prep.prepare(mol)
        if not molsetup_list:
            raise RuntimeError("Meeko 返回空的 molsetup 列表")
        molsetup = molsetup_list[0]

        pdbqt_str, is_ok, err_msg = PDBQTWriterLegacy.write_string(molsetup)
        if not is_ok:
            raise RuntimeError(f"Meeko PDBQT 写入错误: {err_msg}")

        output_pdbqt.write_text(pdbqt_str)

    except Exception as e:
        logger.warning(f"  Meeko 失败（{e}），改用 OpenBabel 备选方案")
        output_pdbqt = _prepare_ligand_openbabel(sdf_path, output_dir)

    # 统计可旋转键数
    n_rotbonds = _count_rotatable_bonds(mol)
    n_atoms = mol.GetNumAtoms()
    logger.info(
        f"  配体 PDBQT 完成: {output_pdbqt.name}"
        f"（{n_atoms} 个原子，{n_rotbonds} 个可旋转键）"
    )
    return output_pdbqt


def _prepare_ligand_openbabel(sdf_path: Path, output_dir: Path) -> Path:
    """Meeko 备选方案：使用 OpenBabel 转换 SDF → PDBQT。"""
    logger = get_logger()
    stem = sdf_path.stem
    output_pdbqt = output_dir / f"{stem}.pdbqt"

    ob_conv = ob.OBConversion()
    ob_conv.SetInAndOutFormats("sdf", "pdbqt")

    mol = ob.OBMol()
    if not ob_conv.ReadFile(mol, str(sdf_path)):
        raise RuntimeError(f"OpenBabel 无法读取: {sdf_path}")

    mol.AddHydrogens(True, True, 7.4)
    charge_model = ob.OBChargeModel.FindType("gasteiger")
    if charge_model:
        charge_model.ComputeCharges(mol)

    if not ob_conv.WriteFile(mol, str(output_pdbqt)):
        raise RuntimeError(f"OpenBabel 无法写入: {output_pdbqt}")

    logger.info(f"  配体 PDBQT（OpenBabel）完成: {output_pdbqt.name}")
    return output_pdbqt


def _count_rotatable_bonds(mol) -> int:
    """统计可旋转键数（单键、非环、非末端）。"""
    from rdkit.Chem import rdMolDescriptors
    return rdMolDescriptors.CalcNumRotatableBonds(mol)


# ---------------------------------------------------------------------------
# 批量准备
# ---------------------------------------------------------------------------

def prepare_all(config: dict) -> dict:
    """
    批量准备所有受体和配体，返回路径字典。

    流程：
    1. 提取受体 TM 域（pLDDT 导向，匹配 Hu2024 "transmembrane portions"）
    2. 从 TM-only PDB 生成受体 PDBQT
    3. 生成配体 PDBQT

    Returns:
        {
            "receptors": {"Gpr2": Path, ...},   # TM-only PDBQT 路径
            "tm_pdbs":   {"Gpr2": Path, ...},   # TM-only PDB 路径（用于 grid box 计算）
            "ligands":   {"ascr18": Path, ...},
        }
    """
    logger = get_logger()
    root = get_project_root(config)
    receptor_dir = root / config["paths"]["receptor_dir"]
    ligand_dir = root / config["paths"]["ligand_dir"]
    prepared_dir = root / config["paths"]["prepared_dir"]
    rec_out = prepared_dir / "receptors"
    lig_out = prepared_dir / "ligands"

    paths: dict = {"receptors": {}, "tm_pdbs": {}, "ligands": {}}

    logger.info("=== 准备所有受体（TM 域提取 + PDBQT）===")
    for name, rec_cfg in config["receptors"].items():
        pdb_path = receptor_dir / rec_cfg["pdb_file"]

        # Step 1: 提取 TM 域
        tm_pdb_path = rec_out / f"{pdb_path.stem}_tm.pdb"
        rec_out.mkdir(parents=True, exist_ok=True)
        extract_tm_domain(pdb_path, tm_pdb_path)
        paths["tm_pdbs"][name] = tm_pdb_path

        # Step 2: 从 TM-only PDB 生成 PDBQT
        pdbqt_path = prepare_receptor(tm_pdb_path, rec_out)
        paths["receptors"][name] = pdbqt_path

    logger.info("=== 准备所有配体 ===")
    for name, lig_cfg in config["ligands"].items():
        sdf_path = ligand_dir / lig_cfg["sdf_file"]
        pdbqt_path = prepare_ligand(sdf_path, lig_out)
        paths["ligands"][name] = pdbqt_path

    # 保存路径 manifest
    manifest_path = prepared_dir / "prepared_paths.json"
    manifest = {
        "receptors": {k: str(v) for k, v in paths["receptors"].items()},
        "tm_pdbs":   {k: str(v) for k, v in paths["tm_pdbs"].items()},
        "ligands":   {k: str(v) for k, v in paths["ligands"].items()},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    logger.info(f"路径 manifest 已保存: {manifest_path}")

    return paths


def load_prepared_paths(config: dict) -> dict:
    """从 manifest JSON 加载已有的准备路径。"""
    root = get_project_root(config)
    prepared_dir = root / config["paths"]["prepared_dir"]
    manifest_path = prepared_dir / "prepared_paths.json"

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"路径 manifest 不存在: {manifest_path}。请先运行 --step prepare。"
        )

    manifest = json.loads(manifest_path.read_text())
    return {
        "receptors": {k: Path(v) for k, v in manifest["receptors"].items()},
        "tm_pdbs":   {k: Path(v) for k, v in manifest.get("tm_pdbs", {}).items()},
        "ligands":   {k: Path(v) for k, v in manifest["ligands"].items()},
    }
