"""
受体准备模块（Hu2024 复现）

与 v2 的区别：
  v2: OpenBabel PDB → PDBQT
  本模块: ADFR Suite prepare_receptor → PDBQT
  差异：ADFR 使用 AutoDock4 原子类型指派，对 Vina 评分更优化

TM 域提取逻辑复用 v2 prepare.py 的实现（方法相同）。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from Bio import PDB

from utils import get_logger, get_project_root, resolve_path


# ---------------------------------------------------------------------------
# TM 域提取（直接复用 v2 逻辑，保持方法一致）
# ---------------------------------------------------------------------------

def extract_tm_domain(
    pdb_path: Path,
    output_path: Path,
    plddt_threshold: float = 80.0,
    min_helix_length: int = 18,
    flank: int = 5,
) -> tuple[int, int]:
    """
    从 AlphaFold PDB 提取跨膜（TM）域。

    逻辑与 v2 prepare.py 完全相同：
    - B-factor 列 = pLDDT 置信度
    - 连续 ≥ min_helix_length 个残基 pLDDT > threshold = TM 螺旋候选
    - 保留第一个候选前 flank 到最后候选后 flank 的范围

    Returns:
        (first_res_id, last_res_id)
    """
    logger = get_logger()
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("rec", str(pdb_path))
    chain = structure[0]["A"]

    residue_info: list[tuple[int, float]] = []
    for res in chain.get_residues():
        if res.get_id()[0] != " ":
            continue
        if "CA" not in res:
            continue
        plddt = res["CA"].get_bfactor()
        residue_info.append((res.get_id()[1], plddt))

    if not residue_info:
        raise ValueError(f"PDB {pdb_path.name} 中无标准残基")

    n = len(residue_info)

    def _find_tm_segments(threshold: float) -> list[tuple[int, int]]:
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
        fallback_threshold = max(plddt_threshold - 10.0, 60.0)
        logger.warning(
            f"{pdb_path.name}: pLDDT>{plddt_threshold} 仅找到 {len(tm_segments)} 个 TM 候选，"
            f"降低阈值到 {fallback_threshold} 重试"
        )
        tm_segments = _find_tm_segments(fallback_threshold)

    if not tm_segments:
        logger.warning(f"{pdb_path.name}: 无法识别 TM 域，使用全长蛋白")
        first_res_id = residue_info[0][0]
        last_res_id = residue_info[-1][0]
    else:
        first_idx = max(0, tm_segments[0][0] - flank)
        last_idx = min(n - 1, tm_segments[-1][1] + flank)
        first_res_id = residue_info[first_idx][0]
        last_res_id = residue_info[last_idx][0]
        n_tm = last_idx - first_idx + 1
        if len(tm_segments) < 5:
            logger.warning(
                f"{pdb_path.name}: 仅识别到 {len(tm_segments)} 个 TM 候选螺旋，"
                f"保留残基 {first_res_id}–{last_res_id}（{n} → {n_tm} 残基）"
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


def _clean_pdb(pdb_path: Path, output_path: Path) -> None:
    """去除水分子和 HETATM，只保留 chain A 标准残基。"""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("rec", str(pdb_path))

    class CleanSelect(PDB.Select):
        def accept_chain(self, chain):
            return chain.id == "A"

        def accept_residue(self, residue):
            return residue.get_id()[0] == " "

    io = PDB.PDBIO()
    io.set_structure(structure)
    io.save(str(output_path), CleanSelect())


# ---------------------------------------------------------------------------
# ADFR Suite 受体准备
# ---------------------------------------------------------------------------

def prepare_receptor_adfr(
    pdb_path: Path,
    output_dir: Path,
    adfr_bin: str,
) -> Path:
    """
    将受体 TM-only PDB 转换为 PDBQT（ADFR Suite 方法，匹配 Hu2024）。

    流程:
    1. BioPython 提取 TM 域（pLDDT 导向）
    2. BioPython 清理 PDB（去水/HETATM）
    3. ADFR prepare_receptor 转换（加氢、原子类型指派）

    Args:
        pdb_path: 原始受体 PDB
        output_dir: PDBQT 输出目录
        adfr_bin: ADFR Suite bin 目录路径（本地或远程映射路径）

    Returns:
        输出 PDBQT 文件路径
    """
    logger = get_logger()
    pdb_path = Path(pdb_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = pdb_path.stem
    # Step 1: TM 域提取
    tm_pdb = output_dir / f"{stem}_tm.pdb"
    if not tm_pdb.exists():
        extract_tm_domain(pdb_path, tm_pdb)
    else:
        logger.info(f"  TM PDB 已存在，跳过提取: {tm_pdb.name}")

    # Step 2: 清理
    cleaned_pdb = output_dir / f"{stem}_tm_cleaned.pdb"
    _clean_pdb(tm_pdb, cleaned_pdb)

    # Step 3: ADFR prepare_receptor
    output_pdbqt = output_dir / f"{stem}_tm.pdbqt"
    adfr_receptor = Path(adfr_bin) / "prepare_receptor"
    if sys.platform == "win32":
        # Windows 可执行文件可能带或不带 .exe
        if not adfr_receptor.exists():
            adfr_receptor = Path(adfr_bin) / "prepare_receptor.exe"
        if not adfr_receptor.exists():
            # MGLTools 风格: prepare_receptor4.py
            adfr_receptor = Path(adfr_bin) / "prepare_receptor4.py"

    cmd = [
        str(adfr_receptor),
        "-r", str(cleaned_pdb),
        "-o", str(output_pdbqt),
        "-A", "hydrogens",                # 加极性氢
        "-U", "nphs_lps_waters_nonstdres", # 清理选项（匹配 ADFR 默认）
    ]
    logger.info(f"准备受体（ADFR）: {pdb_path.name}")
    logger.debug(f"  CMD: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ADFR prepare_receptor 失败 (code={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    if not output_pdbqt.exists():
        raise RuntimeError(f"ADFR 未生成 PDBQT: {output_pdbqt}")

    n_atoms = sum(1 for line in output_pdbqt.read_text().splitlines()
                  if line.startswith(("ATOM", "HETATM")))
    logger.info(f"  受体 PDBQT 完成（ADFR）: {output_pdbqt.name}（{n_atoms} 个原子）")
    return output_pdbqt


# ---------------------------------------------------------------------------
# 批量准备
# ---------------------------------------------------------------------------

def prepare_all_receptors(config: dict) -> dict:
    """批量准备所有受体，返回 {name: Path} 字典。"""
    logger = get_logger()
    root = get_project_root(config)
    receptor_dir = root / config["paths"]["receptor_dir"]
    prepared_dir = root / config["paths"]["prepared_dir"]
    rec_out = prepared_dir / "receptors"
    adfr_bin = config["remote"]["adfr_bin"]

    paths = {"receptors": {}, "tm_pdbs": {}}

    logger.info("=== 准备所有受体（TM 域提取 + ADFR PDBQT）===")
    for name, rec_cfg in config["receptors"].items():
        pdb_path = receptor_dir / rec_cfg["pdb_file"]
        pdbqt_path = prepare_receptor_adfr(pdb_path, rec_out, adfr_bin)
        paths["receptors"][name] = pdbqt_path
        paths["tm_pdbs"][name] = rec_out / f"{pdb_path.stem}_tm.pdb"

    return paths
