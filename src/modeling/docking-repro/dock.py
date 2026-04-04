"""
AutoDock Vina 两阶段对接（Hu2024 复现）

与 v2 的区别：
  v2:  单阶段，spacing=0.25，box=40Å
  本模块: 两阶段——Stage1 定位（spacing=0.25, box=40Å）→ Stage2 精修（spacing=0.1, box=20Å）

原因：spacing=0.1 + box=40Å 产生 64M 格点，触发 Vina szv_grid.cpp 断言（上限 ~27M）。
两阶段方案：Stage2 用 20Å box，格点数 8.1M，在限制内，同时达到 Hu2024 的 0.1Å 精度。
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from vina import Vina

sys.path.insert(0, str(Path(__file__).parent.parent / "docking"))  # 复用 v2 的 grid_box.py
from grid_box import GridBox, compute_box_center_of_mass, compute_box_blind

from utils import get_logger, get_project_root


@dataclass
class DockingResult:
    pair_name: str
    receptor: str
    ligand: str
    best_affinity: float
    all_affinities: list[float]
    poses_path: str
    stage1_box: dict           # Stage1 grid box（40Å）
    stage2_box: dict           # Stage2 grid box（20Å，精修用）
    box_type: str              # "twostage"
    exhaustiveness: int        # Stage2 exhaustiveness
    spacing: float             # Stage2 spacing（0.1）
    elapsed_sec: float


def _extract_pose_centroid(poses_pdbqt: Path) -> tuple[float, float, float]:
    """
    从 PDBQT pose 文件中提取最佳 pose（第一个 MODEL）的质心坐标。
    """
    coords = []
    in_model = False
    for line in poses_pdbqt.read_text().splitlines():
        if line.startswith("MODEL        1"):
            in_model = True
        elif line.startswith("ENDMDL") and in_model:
            break
        elif in_model and line.startswith(("ATOM", "HETATM")):
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append((x, y, z))
            except ValueError:
                continue

    if not coords:
        raise RuntimeError(f"无法从 {poses_pdbqt} 提取 pose 坐标")

    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    cz = sum(c[2] for c in coords) / len(coords)
    return cx, cy, cz


def dock_pair_twostage(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    pair_name: str,
    tm_pdb: Path,
    output_dir: Path,
    config: dict,
) -> DockingResult:
    """
    两阶段对接（Hu2024 spacing=0.1 复现）。

    Stage 1: box=40Å, spacing=0.25, exh=32  → 定位结合口袋
    Stage 2: box=20Å（以 Stage1 top pose 质心为中心），spacing=0.1, exh=200

    Args:
        receptor_pdbqt: 受体 PDBQT 路径
        ligand_pdbqt: 配体 PDBQT 路径
        pair_name: 对接对名称（如 "GprC_ascr18"）
        tm_pdb: TM-only PDB（用于计算受体质心）
        output_dir: 结果输出目录
        config: pipeline 配置字典

    Returns:
        DockingResult（Stage2 精修结果）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vina_cfg = config["vina"]
    stage1_cfg = vina_cfg["stage1"]
    stage2_cfg = vina_cfg["stage2"]

    t_start = time.time()

    # -----------------------------------------------------------------------
    # Stage 1: 全局搜索（定位结合口袋）
    # -----------------------------------------------------------------------
    stage1_poses = output_dir / f"{pair_name}_stage1_poses.pdbqt"
    stage1_box = compute_box_center_of_mass(tm_pdb, box_size=stage1_cfg["box_size"])
    logger.info(f"[Stage1] {pair_name}: box={stage1_cfg['box_size']}Å, spacing={stage1_cfg['spacing']}, exh={stage1_cfg['exhaustiveness']}")

    v = Vina(sf_name="vina", seed=vina_cfg["seed"], verbosity=0)
    v.set_receptor(str(receptor_pdbqt))
    v.set_ligand_from_file(str(ligand_pdbqt))
    v.compute_vina_maps(
        center=list(stage1_box.center),
        box_size=[stage1_cfg["box_size"]] * 3,
        spacing=stage1_cfg["spacing"],
    )
    v.dock(
        exhaustiveness=stage1_cfg["exhaustiveness"],
        n_poses=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
    )
    v.write_poses(str(stage1_poses), n_poses=vina_cfg["num_modes"], overwrite=True)
    stage1_best = v.energies(n_poses=1)[0][0]
    logger.info(f"  Stage1 最佳 ΔG = {stage1_best:.2f} kcal/mol")

    # -----------------------------------------------------------------------
    # Stage 2: 局部精修（spacing=0.1，20Å box）
    # -----------------------------------------------------------------------
    pose_center = _extract_pose_centroid(stage1_poses)
    stage2_poses = output_dir / f"{pair_name}_poses.pdbqt"
    stage2_box = GridBox(
        center=pose_center,
        size=(stage2_cfg["box_size"], stage2_cfg["box_size"], stage2_cfg["box_size"]),
    )

    # 验证格点数量
    n_points = ((stage2_cfg["box_size"] / stage2_cfg["spacing"]) + 1) ** 3
    logger.info(
        f"[Stage2] {pair_name}: box={stage2_cfg['box_size']}Å, spacing={stage2_cfg['spacing']}, "
        f"exh={stage2_cfg['exhaustiveness']}, 格点数={n_points/1e6:.1f}M"
    )
    if n_points > 27e6:
        raise RuntimeError(
            f"Stage2 格点数 {n_points/1e6:.1f}M > 27M 限制！"
            f"请减小 box_size（当前: {stage2_cfg['box_size']}Å）"
        )

    v2 = Vina(sf_name="vina", seed=vina_cfg["seed"], verbosity=0)
    v2.set_receptor(str(receptor_pdbqt))
    v2.set_ligand_from_file(str(ligand_pdbqt))
    v2.compute_vina_maps(
        center=list(stage2_box.center),
        box_size=[stage2_cfg["box_size"]] * 3,
        spacing=stage2_cfg["spacing"],
    )
    v2.dock(
        exhaustiveness=stage2_cfg["exhaustiveness"],
        n_poses=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
    )
    v2.write_poses(str(stage2_poses), n_poses=vina_cfg["num_modes"], overwrite=True)

    all_energies = [e[0] for e in v2.energies(n_poses=vina_cfg["num_modes"])]
    best_affinity = all_energies[0]
    elapsed = time.time() - t_start

    logger.info(
        f"  Stage2 最佳 ΔG = {best_affinity:.2f} kcal/mol "
        f"（Stage1: {stage1_best:.2f}，Δ={best_affinity - stage1_best:+.2f}）"
        f"（{elapsed:.0f} 秒）"
    )

    return DockingResult(
        pair_name=pair_name,
        receptor=receptor_pdbqt.stem,
        ligand=ligand_pdbqt.stem,
        best_affinity=best_affinity,
        all_affinities=all_energies,
        poses_path=str(stage2_poses),
        stage1_box={"center": list(stage1_box.center), "size": [stage1_cfg["box_size"]] * 3},
        stage2_box={"center": list(stage2_box.center), "size": [stage2_cfg["box_size"]] * 3},
        box_type="twostage",
        exhaustiveness=stage2_cfg["exhaustiveness"],
        spacing=stage2_cfg["spacing"],
        elapsed_sec=elapsed,
    )


def dock_matrix(
    prepared_paths: dict,
    config: dict,
) -> list[DockingResult]:
    """
    运行完整对接矩阵（N 受体 × M 配体，两阶段对接）。

    Args:
        prepared_paths: {"receptors": {name: Path}, "tm_pdbs": {name: Path}, "ligands": {name: Path}}
        config: pipeline 配置字典

    Returns:
        所有对接结果列表
    """
    logger = get_logger()
    root = get_project_root(config)
    results_dir = root / config["paths"]["results_dir"] / "poses"
    results_dir.mkdir(parents=True, exist_ok=True)

    receptors = prepared_paths["receptors"]
    tm_pdbs = prepared_paths["tm_pdbs"]
    ligands = prepared_paths["ligands"]
    total = len(receptors) * len(ligands)

    logger.info(
        f"=== 两阶段对接矩阵 [{len(receptors)}×{len(ligands)}，"
        f"Stage2: spacing={config['vina']['stage2']['spacing']}Å, "
        f"exh={config['vina']['stage2']['exhaustiveness']}] ==="
    )

    results = []
    idx = 0
    for rec_name, rec_pdbqt in receptors.items():
        tm_pdb = tm_pdbs[rec_name]
        for lig_name, lig_pdbqt in ligands.items():
            idx += 1
            pair_name = f"{rec_name}_{lig_name}"
            pair_dir = results_dir / pair_name
            logger.info(f"[{idx}/{total}] {pair_name}")

            result = dock_pair_twostage(
                receptor_pdbqt=rec_pdbqt,
                ligand_pdbqt=lig_pdbqt,
                pair_name=pair_name,
                tm_pdb=tm_pdb,
                output_dir=pair_dir,
                config=config,
            )
            results.append(result)

    # 保存汇总 JSON
    results_json = root / config["paths"]["results_dir"] / "docking_results.json"
    results_data = [asdict(r) for r in results]
    results_json.write_text(json.dumps(results_data, indent=2, ensure_ascii=False))
    logger.info(f"对接矩阵完成，结果已保存: {results_json}")

    return results
