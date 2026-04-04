"""
AutoDock Vina 对接引擎。

使用 Vina Python API（非命令行），支持：
- 3x3 对接矩阵（3 受体 × 3 配体）
- Blind docking 验证（确认结合口袋位置与文献一致）
- Fast 模式（exhaustiveness=32）用于开发测试
- Resume 模式（跳过已有结果）
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from vina import Vina

from grid_box import GridBox, compute_box_blind, get_grid_box
from utils import get_logger, get_project_root


@dataclass
class DockingResult:
    pair_name: str          # e.g. "Gpr2_ascr18"
    receptor: str
    ligand: str
    best_affinity: float    # kcal/mol，最低（最佳）结合能
    all_affinities: list[float]  # 所有 pose 的结合能
    poses_path: str         # PDBQT 输出文件路径
    grid_box: dict          # {"center": [...], "size": [...]}
    box_type: str           # "informed" 或 "blind"
    exhaustiveness: int
    elapsed_sec: float


def _get_vina_params(config: dict, fast: bool) -> dict:
    """从配置中提取 Vina 参数，fast=True 时使用快速模式。"""
    vina_cfg = config["vina"]
    if fast:
        return {
            "exhaustiveness": vina_cfg["fast"]["exhaustiveness"],
            "num_modes": vina_cfg["fast"]["num_modes"],
            "energy_range": vina_cfg["energy_range"],
            "seed": vina_cfg["seed"],
            "spacing": vina_cfg.get("spacing", 0.375),
        }
    return {
        "exhaustiveness": vina_cfg["exhaustiveness"],
        "num_modes": vina_cfg["num_modes"],
        "energy_range": vina_cfg["energy_range"],
        "seed": vina_cfg["seed"],
        "spacing": vina_cfg.get("spacing", 0.375),
    }


def dock_pair(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    grid_box: GridBox,
    vina_params: dict,
    output_dir: Path,
    pair_name: str,
    box_type: str = "informed",
) -> DockingResult:
    """
    对单个受体-配体对进行 AutoDock Vina 对接。

    Args:
        receptor_pdbqt: 受体 PDBQT 路径
        ligand_pdbqt: 配体 PDBQT 路径
        grid_box: 搜索空间定义
        vina_params: {"exhaustiveness", "num_modes", "energy_range", "seed"}
        output_dir: 输出目录
        pair_name: 标识符（用于文件命名）
        box_type: "informed" 或 "blind"

    Returns:
        DockingResult
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    poses_path = output_dir / f"{pair_name}_poses.pdbqt"
    logger.info(
        f"  对接 {pair_name} "
        f"[exhaustiveness={vina_params['exhaustiveness']}, box={box_type}]"
    )

    t0 = time.time()

    v = Vina(sf_name="vina", seed=vina_params["seed"], verbosity=0)
    v.set_receptor(str(receptor_pdbqt))
    v.set_ligand_from_file(str(ligand_pdbqt))

    spacing = vina_params.get("spacing", 0.375) or 0.375
    center = [grid_box.center_x, grid_box.center_y, grid_box.center_z]
    box_size = [grid_box.size_x, grid_box.size_y, grid_box.size_z]

    # 注：spacing < 0.2 与 40Å box 组合会触发 Vina C++ assertion，不可被 try/except 捕获
    # config 中 spacing=0.25 是经过验证的最小可用值
    v.compute_vina_maps(center=center, box_size=box_size, spacing=spacing)

    v.dock(
        exhaustiveness=vina_params["exhaustiveness"],
        n_poses=vina_params["num_modes"],
    )

    v.write_poses(str(poses_path), n_poses=vina_params["num_modes"], overwrite=True)

    # 提取结合能（第一列为 affinity kcal/mol）
    energies = v.energies(n_poses=vina_params["num_modes"])
    affinities = [float(e[0]) for e in energies]
    best_affinity = affinities[0]

    elapsed = time.time() - t0

    logger.info(
        f"  {pair_name}: 最佳 ΔG = {best_affinity:.2f} kcal/mol "
        f"（{elapsed:.0f} 秒）"
    )
    logger.debug(
        f"  {pair_name} 所有 pose 结合能: "
        + ", ".join(f"{a:.2f}" for a in affinities[:5])
    )

    rec_name = pair_name.split("_")[0]
    lig_name = "_".join(pair_name.split("_")[1:])

    return DockingResult(
        pair_name=pair_name,
        receptor=rec_name,
        ligand=lig_name,
        best_affinity=best_affinity,
        all_affinities=affinities,
        poses_path=str(poses_path),
        grid_box=grid_box.as_dict(),
        box_type=box_type,
        exhaustiveness=vina_params["exhaustiveness"],
        elapsed_sec=elapsed,
    )


def dock_matrix(
    config: dict,
    prepared_paths: dict,
    fast: bool = False,
    resume: bool = False,
) -> list[DockingResult]:
    """
    对所有 3x3 受体-配体组合进行对接。

    Args:
        config: 全局配置
        prepared_paths: {"receptors": {...}, "ligands": {...}} 路径字典
        fast: 是否使用快速模式（exhaustiveness=32）
        resume: 是否跳过已有结果文件的对接

    Returns:
        所有 9 个 DockingResult 的列表
    """
    logger = get_logger()
    root = get_project_root(config)
    poses_dir = root / config["paths"]["results_dir"] / "poses"
    receptor_dir = root / config["paths"]["receptor_dir"]

    vina_params = _get_vina_params(config, fast)
    receptor_names = list(config["receptors"].keys())
    ligand_names = list(config["ligands"].keys())
    total = len(receptor_names) * len(ligand_names)

    logger.info(
        f"=== 开始 3×3 对接矩阵 "
        f"[{'FAST' if fast else 'PRODUCTION'}, exhaustiveness={vina_params['exhaustiveness']}] ==="
    )

    results = []
    count = 0

    for rec_name in receptor_names:
        rec_pdbqt = prepared_paths["receptors"][rec_name]
        # 使用 TM-only PDB 计算质心（匹配 Hu2024 center-of-mass 策略）
        tm_pdb = prepared_paths["tm_pdbs"].get(rec_name)
        if tm_pdb and Path(tm_pdb).exists():
            pdb_path = Path(tm_pdb)
        else:
            pdb_path = receptor_dir / config["receptors"][rec_name]["pdb_file"]
            logger.warning(f"{rec_name}: 未找到 TM-only PDB，使用全长（精度可能下降）")
        grid_box = get_grid_box(config, rec_name, pdb_path)

        for lig_name in ligand_names:
            count += 1
            lig_pdbqt = prepared_paths["ligands"][lig_name]
            pair_name = f"{rec_name}_{lig_name}"

            logger.info(f"[{count}/{total}] {pair_name}")

            # Resume 模式：跳过已有结果
            poses_path = poses_dir / f"{pair_name}_poses.pdbqt"
            result_json = poses_dir / f"{pair_name}_result.json"
            if resume and result_json.exists():
                logger.info(f"  已有结果，跳过（{result_json.name}）")
                saved = json.loads(result_json.read_text())
                results.append(DockingResult(**saved))
                continue

            result = dock_pair(
                receptor_pdbqt=rec_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                grid_box=grid_box,
                vina_params=vina_params,
                output_dir=poses_dir,
                pair_name=pair_name,
                box_type="informed" if config["receptors"][rec_name].get("binding_residues") else "blind_informed",
            )
            results.append(result)

            # 保存单个结果 JSON
            result_json.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False))

    # 保存完整矩阵结果
    matrix_json = root / config["paths"]["results_dir"] / "docking_results.json"
    matrix_json.write_text(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
    logger.info(f"对接矩阵完成，结果已保存: {matrix_json}")

    return results


def dock_blind_validation(
    config: dict,
    prepared_paths: dict,
    fast: bool = True,
) -> list[dict]:
    """
    对每个受体用 blind docking 验证结合口袋位置。

    对每个受体使用 ascr#3 进行 blind docking，比较 top pose 质心
    与 informed docking top pose 的距离。距离 < 5 Å 视为一致。

    Returns:
        验证报告列表，每个受体一条
    """
    logger = get_logger()
    root = get_project_root(config)
    receptor_dir = root / config["paths"]["receptor_dir"]
    poses_dir = root / config["paths"]["results_dir"] / "poses"

    validation_lig = config["analysis"]["blind_validation_ligand"]
    threshold = config["analysis"]["blind_rmsd_threshold"]
    vina_params = _get_vina_params(config, fast=fast)  # blind 验证用快速模式

    logger.info("=== Blind Docking 验证 ===")
    reports = []

    lig_pdbqt = prepared_paths["ligands"][validation_lig]

    for rec_name in config["receptors"]:
        rec_pdbqt = prepared_paths["receptors"][rec_name]

        # Blind box 也用 TM-only PDB（确保与 informed docking 同一受体范围）
        tm_pdb = prepared_paths["tm_pdbs"].get(rec_name)
        if tm_pdb and Path(tm_pdb).exists():
            pdb_path = Path(tm_pdb)
        else:
            pdb_path = receptor_dir / config["receptors"][rec_name]["pdb_file"]

        blind_padding = config["grid_box"]["blind_padding"]
        blind_box = compute_box_blind(pdb_path, padding=blind_padding)

        blind_pair = f"{rec_name}_{validation_lig}_blind"
        logger.info(f"  Blind docking: {blind_pair}")

        blind_result = dock_pair(
            receptor_pdbqt=rec_pdbqt,
            ligand_pdbqt=lig_pdbqt,
            grid_box=blind_box,
            vina_params=vina_params,
            output_dir=poses_dir,
            pair_name=blind_pair,
            box_type="blind",
        )

        # 读取 informed docking 的 top pose 质心
        informed_pair = f"{rec_name}_{validation_lig}"
        informed_json = poses_dir / f"{informed_pair}_result.json"

        report = {
            "receptor": rec_name,
            "blind_affinity": blind_result.best_affinity,
            "blind_box_center": blind_result.grid_box["center"],
        }

        if informed_json.exists():
            informed = json.loads(informed_json.read_text())
            informed_center = informed["grid_box"]["center"]
            blind_center = blind_result.grid_box["center"]

            # 估算 blind top pose 与 informed box 中心的距离
            dist = float(np.linalg.norm(
                np.array(blind_center) - np.array(informed_center)
            ))
            report["informed_box_center"] = informed_center
            report["center_distance_A"] = round(dist, 2)
            report["pass"] = dist < threshold
            status = "PASS" if report["pass"] else "WARN"
            logger.info(
                f"  {rec_name}: blind vs informed box 中心距离 = {dist:.1f} Å [{status}]"
            )
        else:
            logger.warning(
                f"  {rec_name}: 无 informed 结果可比较（先运行 dock_matrix）"
            )
            report["pass"] = None

        reports.append(report)

    # 保存验证报告
    val_path = root / config["paths"]["results_dir"] / "blind_validation.json"
    val_path.write_text(json.dumps(reports, indent=2, ensure_ascii=False))
    logger.info(f"Blind 验证报告: {val_path}")

    return reports


def load_docking_results(config: dict) -> list[DockingResult]:
    """从 JSON 加载已保存的对接结果。"""
    root = get_project_root(config)
    results_json = root / config["paths"]["results_dir"] / "docking_results.json"

    if not results_json.exists():
        raise FileNotFoundError(
            f"对接结果不存在: {results_json}。请先运行 --step dock。"
        )

    data = json.loads(results_json.read_text())
    return [DockingResult(**d) for d in data]
