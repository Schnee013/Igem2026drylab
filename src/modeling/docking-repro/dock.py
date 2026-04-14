"""
AutoDock Vina 对接模块（Hu2024 复现）

提供两种对接协议：
  dock_pair_singlestage: 单阶段，spacing=0.1, box=40A, exh=200（Hu2024 原文参数）
  dock_pair_twostage:    两阶段（保留向后兼容）—— Stage1 定位（spacing=0.25, box=40A）
                         → Stage2 精修（spacing=0.1, box=20A）

注：Vina 1.2.7 可正常运行 40A/0.1（64.5M 格点），仅输出 WARNING，不崩溃。
    此前认为有 ~27M 格点限制，是错误假设，已移除硬限制。

注意：使用 AutoDock-Vina 独立可执行文件（vina.exe），不依赖 Python vina 包。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from grid_box import compute_box_center_of_mass

from utils import get_logger, get_project_root


def get_tm_helix_ranges(config: dict, receptor_name: str) -> list[list[int]] | None:
    """
    从 config["tm_topology"] 中提取指定受体的 TM 螺旋范围列表。

    Returns:
        [[start, end], ...] 按 TM1-TM7 顺序，或 None（config 无 tm_topology）
    """
    tm_topo = config.get("tm_topology")
    if tm_topo is None:
        return None
    rec_topo = tm_topo.get(receptor_name)
    if rec_topo is None:
        return None
    helices = rec_topo.get("helices", {})
    return [helices[k] for k in sorted(helices.keys())]


@dataclass
class DockingResult:
    pair_name: str
    receptor: str
    ligand: str
    best_affinity: float
    all_affinities: list[float]
    poses_path: str
    stage1_box: dict    # twostage: Stage1 box（40A）；singlestage: 单阶段对接 box（40A）
    stage2_box: dict    # twostage: Stage2 box（20A）；singlestage: {}（空）
    box_type: str       # "twostage" | "singlestage"
    exhaustiveness: int
    spacing: float
    elapsed_sec: float


def _parse_vina_output(output: str) -> list[float]:
    """
    解析 Vina CLI 标准输出中的结合能列表。

    Vina 输出格式：
      mode |   affinity | dist from best mode
           | (kcal/mol) | rmsd l.b.| rmsd u.b.
      -----+------------+----------+----------
         1         -8.3      0.000      0.000
         2         -7.9      1.234      2.345
    """
    affinities = []
    for line in output.splitlines():
        m = re.match(r"\s*\d+\s+([-\d.]+)\s+[\d.]+\s+[\d.]+", line)
        if m:
            affinities.append(float(m.group(1)))
    return affinities


def _run_vina(
    vina_bin: str,
    receptor: Path,
    ligand: Path,
    center: tuple[float, float, float],
    box_size: float,
    spacing: float,
    exhaustiveness: int,
    num_modes: int,
    energy_range: float,
    seed: int,
    output: Path,
) -> list[float]:
    """
    调用 vina.exe CLI 执行对接，返回结合能列表（kcal/mol）。
    """
    logger = get_logger()
    cmd = [
        vina_bin,
        "--receptor", str(receptor),
        "--ligand",   str(ligand),
        "--center_x", f"{center[0]:.4f}",
        "--center_y", f"{center[1]:.4f}",
        "--center_z", f"{center[2]:.4f}",
        "--size_x",   f"{box_size:.2f}",
        "--size_y",   f"{box_size:.2f}",
        "--size_z",   f"{box_size:.2f}",
        "--spacing",  f"{spacing:.3f}",
        "--exhaustiveness", str(exhaustiveness),
        "--num_modes",      str(num_modes),
        "--energy_range",   f"{energy_range:.1f}",
        "--seed",           str(seed),
        "--out",      str(output),
    ]
    logger.debug("vina cmd: " + " ".join(cmd))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"vina.exe 失败（exit {proc.returncode}）\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )

    affinities = _parse_vina_output(proc.stdout)
    if not affinities:
        raise RuntimeError(
            f"vina.exe 未输出结合能。stdout:\n{proc.stdout}"
        )
    return affinities


def _extract_pose_centroid(poses_pdbqt: Path) -> tuple[float, float, float]:
    """
    从 PDBQT pose 文件中提取最佳 pose（第一个 MODEL）的质心坐标。
    """
    coords = []
    in_model = False
    for line in poses_pdbqt.read_text(encoding="utf-8", errors="replace").splitlines():
        # 兼容 vina.exe ("MODEL 1") 和 Python vina 包 ("MODEL        1") 两种格式
        parts = line.split()
        if len(parts) == 2 and parts[0] == "MODEL" and parts[1] == "1":
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
    seed: int | None = None,
    stage2_box_size: float | None = None,
    tm_helix_ranges: list[list[int]] | None = None,
) -> DockingResult:
    """
    两阶段对接（Hu2024 spacing=0.1 复现）。

    Stage 1: box=40A, spacing=0.25, exh=32  → 定位结合口袋
    Stage 2: box=20A（以 Stage1 top pose 质心为中心），spacing=0.1, exh=200

    Args:
        receptor_pdbqt: 受体 PDBQT 路径
        ligand_pdbqt: 配体 PDBQT 路径
        pair_name: 对接对名称（如 "GprC_ascr18"）
        tm_pdb: TM-only PDB（用于计算受体质心）
        output_dir: 结果输出目录
        config: pipeline 配置字典
        seed: 随机种子（覆盖 config["vina"]["seed"]；用于多 seed 方差实验）
        stage2_box_size: Stage2 box 边长覆盖（Å）；None 则用 config 默认值（20A）
        tm_helix_ranges: 可选 TM 螺旋范围 [[start, end], ...]，
            提供时仅用 TM 螺旋原子计算 Stage1 质心

    Returns:
        DockingResult（Stage2 精修结果）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vina_bin = config["remote"]["vina_bin"]
    vina_cfg = config["vina"]
    stage1_cfg = vina_cfg["stage1"]
    stage2_cfg = vina_cfg["stage2"]

    effective_seed = seed if seed is not None else vina_cfg["seed"]
    effective_stage2_box = stage2_box_size if stage2_box_size is not None else stage2_cfg["box_size"]

    t_start = time.time()

    # -----------------------------------------------------------------------
    # Stage 1: 全局搜索（定位结合口袋）
    # -----------------------------------------------------------------------
    stage1_poses = output_dir / f"{pair_name}_stage1_poses.pdbqt"
    stage1_box = compute_box_center_of_mass(
        tm_pdb, box_size=stage1_cfg["box_size"], tm_helix_ranges=tm_helix_ranges,
    )
    logger.info(
        f"[Stage1] {pair_name}: box={stage1_cfg['box_size']}A, "
        f"spacing={stage1_cfg['spacing']}, exh={stage1_cfg['exhaustiveness']}"
    )

    stage1_affinities = _run_vina(
        vina_bin=vina_bin,
        receptor=receptor_pdbqt,
        ligand=ligand_pdbqt,
        center=(stage1_box.center_x, stage1_box.center_y, stage1_box.center_z),
        box_size=stage1_cfg["box_size"],
        spacing=stage1_cfg["spacing"],
        exhaustiveness=stage1_cfg["exhaustiveness"],
        num_modes=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
        seed=effective_seed,
        output=stage1_poses,
    )
    stage1_best = stage1_affinities[0]
    logger.info(f"  Stage1 最佳 ΔG = {stage1_best:.2f} kcal/mol")

    # -----------------------------------------------------------------------
    # Stage 2: 局部精修（spacing=0.1，20A box）
    # -----------------------------------------------------------------------
    pose_center = _extract_pose_centroid(stage1_poses)
    stage2_poses = output_dir / f"{pair_name}_poses.pdbqt"

    # 验证格点数量
    n_points = ((effective_stage2_box / stage2_cfg["spacing"]) + 1) ** 3
    logger.info(
        f"[Stage2] {pair_name}: box={effective_stage2_box}A, spacing={stage2_cfg['spacing']}, "
        f"exh={stage2_cfg['exhaustiveness']}, grid_points={n_points/1e6:.1f}M, seed={effective_seed}"
    )
    if n_points > 27e6:
        logger.warning(
            f"Stage2 grid {n_points/1e6:.1f}M > 27M（Vina 1.2.7 仍可运行，仅输出 WARNING）"
        )

    stage2_affinities = _run_vina(
        vina_bin=vina_bin,
        receptor=receptor_pdbqt,
        ligand=ligand_pdbqt,
        center=pose_center,
        box_size=effective_stage2_box,
        spacing=stage2_cfg["spacing"],
        exhaustiveness=stage2_cfg["exhaustiveness"],
        num_modes=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
        seed=effective_seed,
        output=stage2_poses,
    )

    best_affinity = stage2_affinities[0]
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
        all_affinities=stage2_affinities,
        poses_path=str(stage2_poses),
        stage1_box={"center": [stage1_box.center_x, stage1_box.center_y, stage1_box.center_z], "size": [stage1_cfg["box_size"]] * 3},
        stage2_box={"center": list(pose_center), "size": [effective_stage2_box] * 3},
        box_type="twostage",
        exhaustiveness=stage2_cfg["exhaustiveness"],
        spacing=stage2_cfg["spacing"],
        elapsed_sec=elapsed,
    )


def dock_pair_singlestage(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    pair_name: str,
    tm_pdb: Path,
    output_dir: Path,
    config: dict,
    seed: int | None = None,
    tm_helix_ranges: list[list[int]] | None = None,
) -> DockingResult:
    """
    单阶段对接（精确复现 Hu2024 参数）。

    参数：box=40Å, spacing=0.1Å, exhaustiveness=200, center=受体全原子质量加权质心

    Args:
        receptor_pdbqt: 受体 PDBQT 路径
        ligand_pdbqt: 配体 PDBQT 路径
        pair_name: 对接对名称（如 "GprC_ascr18"）
        tm_pdb: TM-only PDB（用于计算受体质心）
        output_dir: 结果输出目录
        config: pipeline 配置字典
        seed: 随机种子（覆盖 config["vina"]["seed"]）
        tm_helix_ranges: 可选 TM 螺旋范围 [[start, end], ...]，
            提供时仅用 TM 螺旋原子计算质心（排除 ECL/ICL loop）

    Returns:
        DockingResult（stage2_box 为空 dict，box_type="singlestage"）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vina_bin = config["remote"]["vina_bin"]
    vina_cfg = config["vina"]
    ss_cfg = vina_cfg.get("singlestage", {
        "spacing": 0.1,
        "box_size": 40.0,
        "exhaustiveness": 200,
    })

    effective_seed = seed if seed is not None else vina_cfg["seed"]

    t_start = time.time()

    box = compute_box_center_of_mass(
        tm_pdb, box_size=ss_cfg["box_size"], tm_helix_ranges=tm_helix_ranges,
    )
    n_points = ((ss_cfg["box_size"] / ss_cfg["spacing"]) + 1) ** 3
    logger.info(
        f"[Singlestage] {pair_name}: box={ss_cfg['box_size']}A, "
        f"spacing={ss_cfg['spacing']}, exh={ss_cfg['exhaustiveness']}, "
        f"grid={n_points/1e6:.1f}M, seed={effective_seed}"
    )
    if n_points > 27e6:
        logger.warning(
            f"  grid {n_points/1e6:.1f}M > 27M（Vina 1.2.7 可运行，仅 WARNING）"
        )

    poses_out = output_dir / f"{pair_name}_poses.pdbqt"
    affinities = _run_vina(
        vina_bin=vina_bin,
        receptor=receptor_pdbqt,
        ligand=ligand_pdbqt,
        center=(box.center_x, box.center_y, box.center_z),
        box_size=ss_cfg["box_size"],
        spacing=ss_cfg["spacing"],
        exhaustiveness=ss_cfg["exhaustiveness"],
        num_modes=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
        seed=effective_seed,
        output=poses_out,
    )

    best_affinity = affinities[0]
    elapsed = time.time() - t_start
    logger.info(
        f"  ΔG = {best_affinity:.3f} kcal/mol（{elapsed:.0f}s）"
    )

    return DockingResult(
        pair_name=pair_name,
        receptor=receptor_pdbqt.stem,
        ligand=ligand_pdbqt.stem,
        best_affinity=best_affinity,
        all_affinities=affinities,
        poses_path=str(poses_out),
        stage1_box={"center": [box.center_x, box.center_y, box.center_z],
                    "size": [ss_cfg["box_size"]] * 3},
        stage2_box={},
        box_type="singlestage",
        exhaustiveness=ss_cfg["exhaustiveness"],
        spacing=ss_cfg["spacing"],
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
        f"Stage2: spacing={config['vina']['stage2']['spacing']}A, "
        f"exh={config['vina']['stage2']['exhaustiveness']}] ==="
    )

    results = []
    idx = 0
    for rec_name, rec_pdbqt in receptors.items():
        tm_pdb = tm_pdbs[rec_name]
        helix_ranges = get_tm_helix_ranges(config, rec_name)
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
                tm_helix_ranges=helix_ranges,
            )
            results.append(result)

    # 保存汇总 JSON
    results_filename = config["paths"].get("results_filename", "docking_results.json")
    results_json = root / config["paths"]["results_dir"] / results_filename
    results_data = [asdict(r) for r in results]
    results_json.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"对接矩阵完成，结果已保存: {results_json}")

    return results
