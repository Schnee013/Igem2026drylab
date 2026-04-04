"""
Grid box 计算模块。

提供两种对接搜索空间定义策略：
1. 文献指导（informed）：以已知结合残基为中心
2. Blind docking：覆盖全蛋白，用于验证
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from Bio import PDB
from Bio.PDB import PPBuilder

from utils import get_logger


@dataclass
class GridBox:
    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float

    def as_dict(self) -> dict:
        return {
            "center": [self.center_x, self.center_y, self.center_z],
            "size": [self.size_x, self.size_y, self.size_z],
        }

    def __repr__(self) -> str:
        return (
            f"GridBox(center=({self.center_x:.1f}, {self.center_y:.1f}, {self.center_z:.1f}), "
            f"size=({self.size_x:.1f}, {self.size_y:.1f}, {self.size_z:.1f}))"
        )


def _load_structure(pdb_path: str | Path, struct_id: str = "receptor") -> PDB.Structure.Structure:
    parser = PDB.PDBParser(QUIET=True)
    return parser.get_structure(struct_id, str(pdb_path))


def _get_ca_coords(structure: PDB.Structure.Structure, residue_ids: list[int],
                   chain_id: str = "A") -> np.ndarray:
    """提取指定残基的 CA 原子坐标。"""
    coords = []
    chain = structure[0][chain_id]
    for res_id in residue_ids:
        try:
            residue = chain[(" ", res_id, " ")]
            if "CA" in residue:
                coords.append(residue["CA"].get_vector().get_array())
        except KeyError:
            get_logger().warning(f"残基 {res_id} 不存在于 chain {chain_id}，已跳过")
    if not coords:
        raise ValueError(f"在 chain {chain_id} 中找不到任何指定残基: {residue_ids}")
    return np.array(coords)


def compute_box_from_residues(
    pdb_path: str | Path,
    residue_ids: list[int],
    box_size: float = 40.0,
    chain_id: str = "A",
) -> GridBox:
    """
    以指定结合残基的 CA 原子质心为中心定义 grid box（文献指导方式）。

    Args:
        pdb_path: 受体 PDB 文件路径
        residue_ids: 结合残基绝对编号列表
        box_size: 三轴均等的 box 大小（Å），默认 40.0 匹配 Hu2024
        chain_id: 蛋白链 ID

    Returns:
        GridBox 对象
    """
    structure = _load_structure(pdb_path)
    coords = _get_ca_coords(structure, residue_ids, chain_id)
    centroid = coords.mean(axis=0)

    box = GridBox(
        center_x=float(centroid[0]),
        center_y=float(centroid[1]),
        center_z=float(centroid[2]),
        size_x=box_size,
        size_y=box_size,
        size_z=box_size,
    )
    get_logger().info(
        f"Informed box（残基 {residue_ids}）: {box}"
    )
    return box


def compute_box_blind(
    pdb_path: str | Path,
    padding: float = 10.0,
    chain_id: str = "A",
) -> GridBox:
    """
    覆盖全蛋白的 blind docking grid box（用于验证结合口袋位置）。

    Args:
        pdb_path: 受体 PDB 文件路径
        padding: 在蛋白 bounding box 外额外扩充的距离（Å）
        chain_id: 蛋白链 ID

    Returns:
        GridBox 对象
    """
    structure = _load_structure(pdb_path)
    all_coords = []
    for atom in structure[0][chain_id].get_atoms():
        all_coords.append(atom.get_vector().get_array())

    coords = np.array(all_coords)
    min_coords = coords.min(axis=0)
    max_coords = coords.max(axis=0)
    centroid = (min_coords + max_coords) / 2
    extents = max_coords - min_coords + 2 * padding

    box = GridBox(
        center_x=float(centroid[0]),
        center_y=float(centroid[1]),
        center_z=float(centroid[2]),
        size_x=float(extents[0]),
        size_y=float(extents[1]),
        size_z=float(extents[2]),
    )
    get_logger().info(f"Blind box: {box}")
    return box


def compute_box_center_of_mass(
    pdb_path: str | Path,
    box_size: float = 40.0,
    chain_id: str = "A",
) -> GridBox:
    """
    以受体 TM-only PDB 的 CA 原子质心为中心定义 grid box。

    匹配 Hu2024: "box size of 40 Å around the centre of mass of the receptor"

    Args:
        pdb_path: TM-only 受体 PDB 路径（已裁剪到跨膜域）
        box_size: box 大小（Å），默认 40.0
        chain_id: 蛋白链 ID

    Returns:
        GridBox 对象
    """
    structure = _load_structure(pdb_path)
    ca_coords = []
    for res in structure[0][chain_id].get_residues():
        if res.get_id()[0] == " " and "CA" in res:
            ca_coords.append(res["CA"].get_vector().get_array())

    if not ca_coords:
        raise ValueError(f"无法从 {pdb_path} 提取 CA 原子坐标")

    coords = np.array(ca_coords)
    centroid = coords.mean(axis=0)

    box = GridBox(
        center_x=float(centroid[0]),
        center_y=float(centroid[1]),
        center_z=float(centroid[2]),
        size_x=box_size,
        size_y=box_size,
        size_z=box_size,
    )
    get_logger().info(
        f"Center-of-mass box ({len(ca_coords)} CA 原子): {box}"
    )
    return box


def resolve_bw_numbering(pdb_path: str | Path, chain_id: str = "A") -> dict[str, int | None]:
    """
    将 GprC 的 Ballesteros-Weinstein 编号映射到绝对残基编号。

    策略：
    - 在蛋白序列中找保守的 Asp (D)，定位 Asp2.50
    - 按偏移量推算 N2.57 (+7), S2.41 (-9), 和 R6.45

    由于 AlphaFold 预测结构缺少实验 TM helix 边界，我们扫描序列中
    连续出现的疏水性残基区段来推断 TM 螺旋位置，然后根据 GPCR 7TM
    拓扑结构（TM2 约在第 50–90 位，TM6 约在第 250–300 位）定位目标。

    Returns:
        dict 包含: Asp2_50, N2_57, S2_41, R6_45 的绝对残基编号（或 None）
    """
    logger = get_logger()
    structure = _load_structure(pdb_path)
    chain = structure[0][chain_id]

    # 收集所有残基的序号和氨基酸类型
    residues = []
    for res in chain.get_residues():
        if res.get_id()[0] == " ":  # 排除 HETATM
            residues.append((res.get_id()[1], res.get_resname()))

    if not residues:
        logger.error("PDB 中无标准残基")
        return {k: None for k in ["Asp2_50", "N2_57", "S2_41", "R6_45"]}

    # 3字母→1字母 氨基酸转换
    aa3to1 = {
        "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
        "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
        "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
        "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
    }

    seq = [(rid, aa3to1.get(rname, "X")) for rid, rname in residues]
    seq_str = "".join(aa for _, aa in seq)
    res_ids = [rid for rid, _ in seq]

    # 找 TM 螺旋区段（连续疏水残基：LIVMFYWC，窗口≥12 个中有 ≥8 个）
    hydrophobic = set("LIVMFYWC")
    window = 12
    hydro_score = []
    for i in range(len(seq_str)):
        w = seq_str[i: i + window]
        hydro_score.append(sum(1 for c in w if c in hydrophobic))

    # 找到疏水区段中心，按位置排序定义"TM螺旋"候选
    tm_centers = []
    in_tm = False
    start = 0
    for i, score in enumerate(hydro_score):
        if score >= 8 and not in_tm:
            in_tm = True
            start = i
        elif score < 6 and in_tm:
            in_tm = False
            tm_centers.append((start + i) // 2)
    if in_tm:
        tm_centers.append((start + len(hydro_score)) // 2)

    logger.debug(f"TM 候选螺旋中心位置（序列索引）: {tm_centers}")

    if len(tm_centers) < 6:
        logger.warning(
            f"仅找到 {len(tm_centers)} 个 TM 候选螺旋，GprC 需要至少 6 个 (TM1–6)。"
            "将使用备选策略：直接扫描 Asp 残基。"
        )

    # 策略：在 TM2 预期范围（大约序列 15–25% 处）找第一个 Asp
    # 对于 538 残基的 GprC，TM2 大约在 residue 80–130
    n_res = len(seq)
    tm2_start_idx = max(0, int(n_res * 0.13))
    tm2_end_idx = min(n_res, int(n_res * 0.28))

    tm2_window = seq[tm2_start_idx:tm2_end_idx]
    logger.debug(
        f"TM2 扫描范围: 序列索引 {tm2_start_idx}–{tm2_end_idx}"
        f"（残基号 {res_ids[tm2_start_idx]}–{res_ids[tm2_end_idx - 1]}）"
    )

    # 找 TM2 窗口中第一个 Asp 作为 Asp2.50 候选
    asp2_50_idx = None
    asp2_50_resid = None
    for i, (rid, aa) in enumerate(tm2_window):
        if aa == "D":
            asp2_50_idx = tm2_start_idx + i
            asp2_50_resid = rid
            break

    if asp2_50_resid is None:
        logger.error(
            "在 TM2 预期范围内未找到 Asp。BW 编号解析失败。"
            "请手动指定 config.yaml 中的 GprC binding_residues。"
        )
        return {k: None for k in ["Asp2_50", "N2_57", "S2_41", "R6_45"]}

    logger.info(f"Asp2.50 候选: 残基号 {asp2_50_resid}（序列索引 {asp2_50_idx}）")

    # 从 Asp2.50 推算偏移
    def get_resid_at_offset(base_idx: int, offset: int) -> int | None:
        target_idx = base_idx + offset
        if 0 <= target_idx < len(seq):
            return seq[target_idx][0]
        return None

    n2_57 = get_resid_at_offset(asp2_50_idx, +7)   # N2.57 = Asp2.50 + 7
    s2_41 = get_resid_at_offset(asp2_50_idx, -9)   # S2.41 = Asp2.50 - 9

    # TM6 的 R6.45：找 TM6 预期范围（约 55–70% 处）中第一个 Arg
    tm6_start_idx = int(n_res * 0.52)
    tm6_end_idx = int(n_res * 0.70)
    tm6_window = seq[tm6_start_idx:tm6_end_idx]

    r6_45 = None
    for rid, aa in tm6_window:
        if aa == "R":
            r6_45 = rid
            break

    result = {
        "Asp2_50": asp2_50_resid,
        "N2_57": n2_57,
        "S2_41": s2_41,
        "R6_45": r6_45,
    }

    logger.info(
        f"GprC BW 编号解析结果:\n"
        f"  Asp2.50 → 残基 {asp2_50_resid}\n"
        f"  N2.57   → 残基 {n2_57}\n"
        f"  S2.41   → 残基 {s2_41}\n"
        f"  R6.45   → 残基 {r6_45}"
    )
    return result


def get_grid_box(config: dict, receptor_name: str, pdb_path: str | Path) -> GridBox:
    """
    根据配置为指定受体获取 grid box。

    策略（由 config.grid_box.strategy 控制）：
    - "center_of_mass"（默认，匹配 Hu2024）：以 TM-only 受体 CA 质心为中心，40Å 正方形 box
    - "residue_based"（旧方法）：以文献结合残基 CA 质心为中心

    Args:
        pdb_path: 受体 PDB 路径（center_of_mass 模式下应为 TM-only PDB）
    """
    box_size = config["grid_box"]["default_size"]
    strategy = config["grid_box"].get("strategy", "center_of_mass")

    if strategy == "center_of_mass":
        return compute_box_center_of_mass(pdb_path, box_size)

    # Legacy: residue_based
    rec_cfg = config["receptors"][receptor_name]
    binding_residues = rec_cfg.get("binding_residues")
    if binding_residues:
        return compute_box_from_residues(pdb_path, binding_residues, box_size)

    get_logger().info(
        f"{receptor_name} 无已知结合残基，改用 blind docking box（padding=10Å）"
    )
    blind_padding = config["grid_box"]["blind_padding"]
    return compute_box_blind(pdb_path, padding=blind_padding)
