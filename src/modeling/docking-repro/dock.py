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
from datetime import datetime, timezone
from pathlib import Path

from grid_box import GridBox, compute_box_center_of_mass

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


def get_manual_box_center(config: dict, receptor_name: str) -> tuple[float, float, float] | None:
    """从 config["tm_topology"][rec].manual_box_center 读取 dock frame 手动指定 box center。

    返回 (x, y, z) in Å（dock frame），None 则走 compute_box_center_of_mass 自动质心。
    Gpr3（2026-04-23 方案 F 起）用 ECL2 质心 [0.42, 7.16, -17.11] 强制搜索胞外口袋。
    当 manual_box_center 非 None 时，extracellular_z_offset 不再叠加（center 已直接指定）。
    设计与执行证据见 docs/logs/2026-04-23.md。
    """
    tm_topo = config.get("tm_topology")
    if tm_topo is None:
        return None
    rec_topo = tm_topo.get(receptor_name)
    if rec_topo is None:
        return None
    raw = rec_topo.get("manual_box_center")
    if raw is None:
        return None
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError(
            f"manual_box_center 必须为长度 3 列表，得到 {raw}"
        )
    return (float(raw[0]), float(raw[1]), float(raw[2]))


def get_receptor_box_size(config: dict, receptor_name: str) -> float | None:
    """从 config["tm_topology"][rec].box_size 读取 per-receptor docking box 边长（Å）。

    None 表示走 config["vina"]["singlestage"]["box_size"] 默认值（40 Å）。
    Gpr3 的当前值由 config.yaml 指定；2026-04-23 的设计与变更证据见当日日志。
    """
    tm_topo = config.get("tm_topology")
    if tm_topo is None:
        return None
    rec_topo = tm_topo.get(receptor_name)
    if rec_topo is None:
        return None
    raw = rec_topo.get("box_size")
    if raw is None:
        return None
    return float(raw)


def get_box_center_offset(config: dict, receptor_name: str) -> tuple[float, float, float]:
    """从 config["tm_topology"] 提取 docking box center 偏移向量。默认 (0,0,0)。

    支持两种 config 格式:
      float        → (0, 0, z)  — 向后兼容（GprC/Gpr3 的 0.0）
      [dx, dy, dz] → (dx, dy, dz) — 3D 向量（Gpr2 膜法线方向偏移）

    背景: TM-only 截断暴露胞内疏水腔，Gpr2 需沿膜法线 +10Å 排除胞内 pose。
    CHARMM-GUI 旋转后膜法线不沿 dock Z，需用 3D 向量。
    → docs/logs/2026-04-16.md §Gpr2 Docking Pose 朝向验证
    → config.yaml tm_topology.{receptor}.extracellular_z_offset
    """
    tm_topo = config.get("tm_topology")
    if tm_topo is None:
        return (0.0, 0.0, 0.0)
    rec_topo = tm_topo.get(receptor_name)
    if rec_topo is None:
        return (0.0, 0.0, 0.0)
    raw = rec_topo.get("extracellular_z_offset", 0.0)
    if isinstance(raw, (list, tuple)):
        if len(raw) != 3:
            raise ValueError(
                f"extracellular_z_offset 列表长度必须为 3，得到 {len(raw)}: {raw}"
            )
        return (float(raw[0]), float(raw[1]), float(raw[2]))
    return (0.0, 0.0, float(raw))


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
    min_rmsd: float,
    max_evals: int,
    cpu: int,
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
        "--min_rmsd",       f"{min_rmsd:.1f}",
        "--max_evals",      str(max_evals),
        "--cpu",            str(cpu),
        "--seed",           str(seed),
        "--out",      str(output),
    ]
    logger.debug("vina cmd: " + " ".join(cmd))

    command_path = output.parent / f"{output.stem}.vina.command.json"
    stdout_path = output.parent / f"{output.stem}.vina.stdout.txt"
    stderr_path = output.parent / f"{output.stem}.vina.stderr.txt"
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as exc:
        elapsed = time.monotonic() - started
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        command_path.write_text(
            json.dumps(
                {
                    "schema": "vina-command-v2",
                    "argv": cmd,
                    "started_at_utc": started_at,
                    "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "elapsed_sec": elapsed,
                    "returncode": None,
                    "status": "invocation_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        raise
    elapsed = time.monotonic() - started
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    command_path.write_text(
        json.dumps(
            {
                "schema": "vina-command-v2",
                "argv": cmd,
                "started_at_utc": started_at,
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_sec": elapsed,
                "returncode": proc.returncode,
                "status": "process_complete",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
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
        min_rmsd=vina_cfg["min_rmsd"],
        max_evals=vina_cfg["max_evals"],
        cpu=config["frame_repair"]["compute"]["cpu_per_job"],
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
        min_rmsd=vina_cfg["min_rmsd"],
        max_evals=vina_cfg["max_evals"],
        cpu=config["frame_repair"]["compute"]["cpu_per_job"],
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
    box_center_offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
    receptor_box_size: float | None = None,
    manual_box_center: tuple[float, float, float] | None = None,
    vina_bin_override: str | None = None,
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
        box_center_offset: 3D 偏移向量 (dx, dy, dz)（Å），叠加到 box center。
            Gpr2 用 [6.17, 0.65, -7.85]（10Å 沿膜法线方向）排除胞内假口袋。
            默认 (0,0,0)。
        receptor_box_size: 可选 box 边长（Å），None 则用 config["vina"]["singlestage"]["box_size"]。
            Gpr3（2026-04-23 方案 F 起）用 20 Å 强制 ECL2 区搜索，排除 TM-POPC 界面 groove。
        manual_box_center: 可选 dock frame 手动指定 box center (x,y,z)。
            非 None 时完全跳过 compute_box_center_of_mass + box_center_offset，直接用此坐标。
            Gpr3 方案 F 用 ECL2 (150-175) 质心 [0.42, 7.16, -17.11]。

    Returns:
        DockingResult（stage2_box 为空 dict，box_type="singlestage"）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vina_bin = vina_bin_override or config["remote"]["vina_bin"]
    vina_cfg = config["vina"]
    ss_cfg = vina_cfg.get("singlestage", {
        "spacing": 0.1,
        "box_size": 40.0,
        "exhaustiveness": 200,
    })

    effective_box_size = receptor_box_size if receptor_box_size is not None else ss_cfg["box_size"]

    effective_seed = seed if seed is not None else vina_cfg["seed"]

    t_start = time.time()

    if manual_box_center is not None:
        # 方案 F：手动指定 box center，跳过 TM-COM + z_offset
        box = GridBox(
            center_x=float(manual_box_center[0]),
            center_y=float(manual_box_center[1]),
            center_z=float(manual_box_center[2]),
            size_x=effective_box_size,
            size_y=effective_box_size,
            size_z=effective_box_size,
        )
        logger.info(
            f"  manual box center: ({box.center_x:.2f}, {box.center_y:.2f}, {box.center_z:.2f}) "
            f"[dock frame]，跳过 COM+offset"
        )
    else:
        box = compute_box_center_of_mass(
            tm_pdb, box_size=effective_box_size, tm_helix_ranges=tm_helix_ranges,
        )
    if manual_box_center is None and any(v != 0.0 for v in box_center_offset):
        # 3D 偏移: 沿膜法线方向移动 box center，排除 ICL 截断暴露的胞内假口袋
        # → docs/logs/2026-04-16.md §Gpr2 Docking Pose 朝向验证
        box = GridBox(
            center_x=box.center_x + box_center_offset[0],
            center_y=box.center_y + box_center_offset[1],
            center_z=box.center_z + box_center_offset[2],
            size_x=box.size_x,
            size_y=box.size_y,
            size_z=box.size_z,
        )
        logger.info(
            f"  box offset: [{box_center_offset[0]:+.2f}, {box_center_offset[1]:+.2f}, "
            f"{box_center_offset[2]:+.2f}] → center=({box.center_x:.2f}, "
            f"{box.center_y:.2f}, {box.center_z:.2f})"
        )
    n_points = ((effective_box_size / ss_cfg["spacing"]) + 1) ** 3
    logger.info(
        f"[Singlestage] {pair_name}: box={effective_box_size}A, "
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
        box_size=effective_box_size,
        spacing=ss_cfg["spacing"],
        exhaustiveness=ss_cfg["exhaustiveness"],
        num_modes=vina_cfg["num_modes"],
        energy_range=vina_cfg["energy_range"],
        min_rmsd=vina_cfg["min_rmsd"],
        max_evals=vina_cfg["max_evals"],
        cpu=config["frame_repair"]["compute"]["cpu_per_job"],
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
                    "size": [effective_box_size] * 3},
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
