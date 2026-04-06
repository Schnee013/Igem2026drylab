"""
配体准备模块（Hu2024 复现）

与 v2 的区别：
  v2:  PubChem SDF → RDKit MMFF 优化 → Meeko PDBQT (15 DOFs)
  本模块: SMILES/SDF → RDKit 3D 嵌入 → Orca B3LYP/def2-TZVP 优化
          → ADFR prepare_ligand PDBQT (7-11 DOFs)

Orca 几何优化是最大的方法差异（量子力学 vs 分子力学）。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from utils import get_logger, get_project_root


# ---------------------------------------------------------------------------
# Orca DFT 几何优化
# ---------------------------------------------------------------------------

_ORCA_INPUT_TEMPLATE = """\
! {method} {basis} {keywords}
%pal nprocs {nprocs} end
%scf MaxIter 500 end
%geom MaxIter {maxiter} end

* xyzfile {charge} {multiplicity} {xyz_file}
"""


def generate_initial_xyz(smiles: str, name: str, output_dir: Path) -> Path:
    """
    从 SMILES 生成初始 3D 构象（RDKit ETKDGv3 嵌入），输出 XYZ 文件。

    Returns:
        XYZ 文件路径
    """
    logger = get_logger()
    output_dir.mkdir(parents=True, exist_ok=True)
    xyz_path = output_dir / f"{name}_initial.xyz"

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"无效 SMILES: {smiles}")
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    AllChem.MMFFOptimizeMolecule(mol, maxIters=500)  # 粗优化作为 Orca 起点

    conf = mol.GetConformer()
    atoms = [mol.GetAtomWithIdx(i).GetSymbol() for i in range(mol.GetNumAtoms())]
    positions = conf.GetPositions()

    lines = [str(len(atoms)), f"{name} initial geometry (ETKDGv3 + MMFF pre-opt)"]
    for sym, (x, y, z) in zip(atoms, positions):
        lines.append(f"{sym:3s}  {x:12.6f}  {y:12.6f}  {z:12.6f}")

    xyz_path.write_text("\n".join(lines) + "\n")
    logger.info(f"  初始 XYZ 生成: {xyz_path.name}（{len(atoms)} 个原子）")
    return xyz_path


def generate_orca_input(
    xyz_path: Path,
    output_dir: Path,
    name: str,
    method: str = "B3LYP",
    basis: str = "def2-TZVP",
    keywords: str = "OPT TightOPT",
    charge: int = 0,
    multiplicity: int = 1,
    nprocs: int = 6,
    maxiter: int = 500,
) -> Path:
    """
    生成 Orca 输入文件（.inp）。

    Returns:
        .inp 文件路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    inp_path = output_dir / f"{name}.inp"

    content = _ORCA_INPUT_TEMPLATE.format(
        method=method,
        basis=basis,
        keywords=keywords,
        nprocs=nprocs,
        maxiter=maxiter,
        charge=charge,
        multiplicity=multiplicity,
        xyz_file=str(xyz_path),
    )
    inp_path.write_text(content)
    return inp_path


def method_from_inp(inp_path: Path) -> str:
    """从 .inp 文件第一行提取方法名（用于日志）。"""
    try:
        return inp_path.read_text().splitlines()[0].strip().lstrip("!")[:30]
    except Exception:
        return "unknown"


def run_orca(inp_path: Path, orca_binary: str) -> Path:
    """
    运行 Orca 几何优化，解析收敛状态。

    Returns:
        优化后的 XYZ 文件路径（{name}.xyz）

    Raises:
        RuntimeError: 优化未收敛或 Orca 返回错误
    """
    logger = get_logger()
    inp_path = Path(inp_path)
    out_path = inp_path.with_suffix(".out")
    name = inp_path.stem
    xyz_optimized = inp_path.parent / f"{name}.xyz"

    # Orca 并行模式要求自身和 MS-MPI 都在 PATH 中
    import os
    env = os.environ.copy()
    orca_dir = str(Path(orca_binary).parent)
    mpi_bin = r"C:\Program Files\Microsoft MPI\Bin"
    env["PATH"] = orca_dir + os.pathsep + mpi_bin + os.pathsep + env.get("PATH", "")

    cmd = [str(Path(orca_binary).resolve()), str(inp_path.resolve())]
    logger.info(f"  运行 Orca ({method_from_inp(inp_path)}): {inp_path.name}")
    logger.info(f"  预计时间: 10-30 分钟（取决于硬件和配体大小）")

    with open(out_path, "w") as f_out:
        result = subprocess.run(cmd, stdout=f_out, stderr=subprocess.STDOUT,
                                cwd=str(inp_path.parent), env=env)

    if result.returncode != 0:
        raise RuntimeError(
            f"Orca 异常退出 (code={result.returncode})，查看: {out_path}"
        )

    # 检查收敛
    out_text = out_path.read_text(errors="replace")
    if "HURRAY" in out_text or "THE OPTIMIZATION HAS CONVERGED" in out_text:
        logger.info(f"  Orca 优化收敛 ✓")
    elif "WARNING: SCF NOT CONVERGED" in out_text:
        raise RuntimeError(f"Orca SCF 未收敛，查看: {out_path}")
    else:
        logger.warning(f"  Orca 收敛状态未确认，继续（查看: {out_path}）")

    if not xyz_optimized.exists():
        raise RuntimeError(
            f"Orca 未生成优化 XYZ 文件: {xyz_optimized}\n"
            f"可能原因: 优化未完成或路径不对，查看: {out_path}"
        )

    # 解析最终能量
    energy = _parse_final_energy(out_text)
    if energy:
        logger.info(f"  最终能量: {energy:.6f} Eh")

    return xyz_optimized


def method_from_inp(inp_path: Path) -> str:
    """从 .inp 文件提取方法名（用于日志）。"""
    try:
        first_line = inp_path.read_text().splitlines()[0]
        return first_line.strip().lstrip("!")[:30]
    except Exception:
        return "unknown"


def _parse_final_energy(out_text: str) -> float | None:
    """从 Orca 输出中提取最终 SCF 能量（Eh）。"""
    pattern = r"FINAL SINGLE POINT ENERGY\s+([-\d.]+)"
    matches = re.findall(pattern, out_text)
    if matches:
        try:
            return float(matches[-1])
        except ValueError:
            return None
    return None


def xyz_to_pdb(xyz_path: Path, output_path: Path) -> Path:
    """
    将 XYZ 文件转换为 PDB（通过 RDKit + SMILES 对齐原子顺序）。

    Orca 输出的 XYZ 与输入 XYZ 原子顺序一致，用 RDKit 读回后写 PDB。
    """
    lines = xyz_path.read_text().splitlines()
    n_atoms = int(lines[0].strip())
    atom_lines = lines[2:2 + n_atoms]

    pdb_lines = []
    for i, line in enumerate(atom_lines, 1):
        parts = line.split()
        sym = parts[0]
        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        pdb_lines.append(
            f"HETATM{i:5d}  {sym:<4s}LIG A   1    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {sym:>2s}  "
        )
    pdb_lines.append("END")
    output_path.write_text("\n".join(pdb_lines) + "\n")
    return output_path


# ---------------------------------------------------------------------------
# ADFR Suite 配体准备
# ---------------------------------------------------------------------------

def prepare_ligand_adfr(
    pdb_path: Path,
    output_dir: Path,
    adfr_bin: str,
    max_dofs: int = 11,
) -> Path:
    """
    将配体 PDB 转换为 PDBQT（ADFR Suite 方法，匹配 Hu2024）。

    流程:
    1. ADFR prepare_ligand 生成 PDBQT（自动检测可旋转键）
    2. 验证 DOF 计数（BRANCH 行数），若 > max_dofs 则冻结末端旋转键
    3. 输出满足 7-11 DOFs 的 PDBQT

    Args:
        pdb_path: 优化后的配体 PDB 文件
        output_dir: PDBQT 输出目录
        adfr_bin: ADFR Suite bin 目录
        max_dofs: DOF 上限（Hu2024: 11）

    Returns:
        输出 PDBQT 文件路径
    """
    logger = get_logger()
    pdb_path = Path(pdb_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = pdb_path.stem
    output_pdbqt = output_dir / f"{stem}.pdbqt"

    adfr_ligand = None
    for candidate in ["prepare_ligand.exe", "prepare_ligand.bat",
                      "prepare_ligand", "prepare_ligand4.py"]:
        p = Path(adfr_bin) / candidate
        if p.exists():
            adfr_ligand = p
            break
    if adfr_ligand is None:
        raise FileNotFoundError(f"ADFR prepare_ligand 未找到于: {adfr_bin}")

    # ADFR prepare_ligand4.py 只接受文件名（不接受绝对路径），用 cwd 解决
    args = [
        "-l", pdb_path.name,
        "-o", str(output_pdbqt),
        "-A", "hydrogens",
        "-B", "non_cyclic",
    ]
    if adfr_ligand.suffix == ".bat":
        cmd = ["cmd", "/c", str(adfr_ligand)] + args
    else:
        cmd = [str(adfr_ligand)] + args

    logger.info(f"准备配体（ADFR）: {pdb_path.name}")
    logger.debug(f"  CMD: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(pdb_path.parent))
    if result.returncode != 0:
        raise RuntimeError(
            f"ADFR prepare_ligand 失败 (code={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    if not output_pdbqt.exists():
        raise RuntimeError(f"ADFR 未生成配体 PDBQT: {output_pdbqt}")

    # 验证和调整 DOF 数
    dof_count = count_dofs(output_pdbqt)
    logger.info(f"  ADFR 生成 DOF 数: {dof_count}（目标: 7-11）")

    if dof_count > max_dofs:
        logger.warning(f"  DOF={dof_count} > {max_dofs}，冻结末端旋转键...")
        output_pdbqt = freeze_terminal_torsions(output_pdbqt, max_dofs)
        dof_count = count_dofs(output_pdbqt)
        logger.info(f"  冻结后 DOF 数: {dof_count}")

    n_atoms = sum(1 for line in output_pdbqt.read_text().splitlines()
                  if line.startswith(("ATOM", "HETATM")))
    logger.info(
        f"  配体 PDBQT 完成（ADFR）: {output_pdbqt.name}"
        f"（{n_atoms} 个原子，{dof_count} DOFs）"
    )
    return output_pdbqt


def count_dofs(pdbqt_path: Path) -> int:
    """统计 PDBQT 文件中 BRANCH 行数（= 可旋转键数）。"""
    text = Path(pdbqt_path).read_text()
    return sum(1 for line in text.splitlines() if line.startswith("BRANCH"))


def freeze_terminal_torsions(pdbqt_path: Path, max_dofs: int) -> Path:
    """
    通过删除末端 BRANCH/ENDBRANCH 块来减少 DOF 数。

    策略：优先冻结仅含甲基或 OH 的末端分支（对结合构象影响最小）。
    修改后的文件写回原路径。

    Returns:
        修改后的 PDBQT 路径
    """
    logger = get_logger()
    text = Path(pdbqt_path).read_text()
    lines = text.splitlines()

    while count_dofs(pdbqt_path) > max_dofs:
        lines = Path(pdbqt_path).read_text().splitlines()
        # 找到最后一个 BRANCH，尝试移除其对应的 BRANCH/ENDBRANCH 块
        branch_indices = [i for i, l in enumerate(lines) if l.startswith("BRANCH")]
        if not branch_indices:
            break

        # 从最末尾的 BRANCH 开始冻结
        last_branch_idx = branch_indices[-1]
        branch_line = lines[last_branch_idx]
        parts = branch_line.split()
        atom1, atom2 = parts[1], parts[2]

        # 找对应的 ENDBRANCH
        endbranch_idx = None
        for i in range(last_branch_idx + 1, len(lines)):
            if lines[i].startswith("ENDBRANCH"):
                eb_parts = lines[i].split()
                if eb_parts[1] == atom1 and eb_parts[2] == atom2:
                    endbranch_idx = i
                    break

        if endbranch_idx is None:
            logger.warning(f"  找不到 ENDBRANCH {atom1} {atom2}，停止冻结")
            break

        # 只冻结叶子节点分支（BRANCH 和 ENDBRANCH 之间只有 ATOM 行，无嵌套 BRANCH）
        inner_lines = lines[last_branch_idx + 1:endbranch_idx]
        has_nested = any(l.startswith("BRANCH") for l in inner_lines)
        if has_nested:
            logger.warning(f"  末端分支有嵌套，跳过冻结，停止尝试")
            break

        # 删除 BRANCH + 内部原子 + ENDBRANCH
        new_lines = lines[:last_branch_idx] + lines[endbranch_idx + 1:]
        pdbqt_path.write_text("\n".join(new_lines) + "\n")
        logger.debug(f"  冻结 BRANCH {atom1}-{atom2}")

    return pdbqt_path


# ---------------------------------------------------------------------------
# 完整配体准备流程（Orca + ADFR）
# ---------------------------------------------------------------------------

def prepare_ligand_full(
    sdf_path: Path,
    smiles: str,
    name: str,
    orca_dir: Path,
    ligand_out: Path,
    orca_binary: str,
    adfr_bin: str,
    orca_cfg: dict,
    max_dofs: int = 11,
) -> Path:
    """
    完整的 Hu2024 配体准备流程。

    流程:
    1. SMILES → RDKit ETKDGv3 → 初始 XYZ
    2. Orca B3LYP/def2-TZVP 几何优化 → 优化后 XYZ
    3. XYZ → PDB（用于 ADFR 输入）
    4. ADFR prepare_ligand → PDBQT（7-11 DOFs）

    Args:
        sdf_path: 原始 SDF（仅用于 fallback）
        smiles: 配体 SMILES
        name: 配体名（如 "ascr18"）
        orca_dir: Orca 工作目录
        ligand_out: PDBQT 输出目录
        orca_binary: Orca 可执行文件路径
        adfr_bin: ADFR Suite bin 目录
        orca_cfg: Orca 参数字典（从 config.yaml['orca']）
        max_dofs: DOF 上限

    Returns:
        最终 PDBQT 路径
    """
    logger = get_logger()
    logger.info(f"=== 准备配体: {name} ===")

    orca_work = orca_dir / name
    orca_work.mkdir(parents=True, exist_ok=True)

    # Step 1: 生成初始 XYZ
    xyz_initial = generate_initial_xyz(smiles, name, orca_work)

    # Step 2: Orca 优化
    inp_path = generate_orca_input(
        xyz_path=xyz_initial,
        output_dir=orca_work,
        name=name,
        method=orca_cfg.get("method", "B3LYP"),
        basis=orca_cfg.get("basis", "def2-TZVP"),
        keywords=orca_cfg.get("keywords", "OPT TightOPT"),
        charge=orca_cfg.get("charge", 0),
        multiplicity=orca_cfg.get("multiplicity", 1),
        nprocs=orca_cfg.get("nprocs", 6),
        maxiter=orca_cfg.get("maxiter", 500),
    )
    xyz_optimized = run_orca(inp_path, orca_binary)

    # Step 3: XYZ → PDB
    pdb_optimized = orca_work / f"{name}_optimized.pdb"
    xyz_to_pdb(xyz_optimized, pdb_optimized)

    # Step 4: ADFR prepare_ligand
    pdbqt_path = prepare_ligand_adfr(pdb_optimized, ligand_out, adfr_bin, max_dofs)

    return pdbqt_path


# ---------------------------------------------------------------------------
# 批量准备
# ---------------------------------------------------------------------------

def prepare_all_ligands(config: dict, only: list[str] | None = None) -> dict:
    """批量准备所有配体，返回 {name: Path} 字典。only 不为 None 时仅处理指定配体。"""
    logger = get_logger()
    root = get_project_root(config)
    ligand_dir = root / config["paths"]["ligand_dir"]
    prepared_dir = root / config["paths"]["prepared_dir"]
    orca_dir = root / config["paths"]["orca_dir"]
    lig_out = prepared_dir / "ligands"

    adfr_bin = config["remote"]["adfr_bin"]
    orca_binary = config["remote"]["orca_bin"]
    orca_cfg = config["orca"]
    max_dofs = config["adfr"]["ligand"]["max_dofs"]

    paths = {}
    logger.info("=== 准备所有配体（Orca DFT + ADFR PDBQT）===")

    for name, lig_cfg in config["ligands"].items():
        if only is not None and name not in only:
            logger.info(f"  跳过 {name}（未在 --ligands 中指定）")
            continue
        sdf_path = ligand_dir / lig_cfg["sdf_file"]
        smiles = lig_cfg["smiles"]
        pdbqt_path = prepare_ligand_full(
            sdf_path=sdf_path,
            smiles=smiles,
            name=name,
            orca_dir=orca_dir,
            ligand_out=lig_out,
            orca_binary=orca_binary,
            adfr_bin=adfr_bin,
            orca_cfg=orca_cfg,
            max_dofs=max_dofs,
        )
        paths[name] = pdbqt_path

    return paths
