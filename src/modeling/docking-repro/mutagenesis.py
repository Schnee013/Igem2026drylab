"""
In silico 突变扫描模块 — 预测增强 ascr#18/ascr#3 选择性的突变位点

目标：通过系统性突变受体结合口袋残基，找到能够提高对 ascr#18（PPN 标志物）
      识别特异性、同时降低对 ascr#3（自由生活线虫标志物）亲和力的突变位点。

方法路线：
  1. FoldX RepairPDB  — 预处理受体 PDB（能量最小化，修复异常键长/键角）
  2. FoldX BuildModel — 为每个候选突变生成突变体结构（秒级，~0.5 kcal/mol 精度）
  3. ADFR prepare_receptor — 将突变体 PDB 转换为 PDBQT
  4. 两阶段 Vina 对接（复用 dock.py）— 对 ascr18 + ascr3 分别打分
  5. ΔΔG 选择性评分：
       ΔG_sel(WT)  = ΔG(WT, ascr18)  - ΔG(WT, ascr3)
       ΔG_sel(mut) = ΔG(mut, ascr18) - ΔG(mut, ascr3)
       ΔΔG_sel     = ΔG_sel(mut) - ΔG_sel(WT)
       ΔΔG_sel < 0 → 突变增强了对 ascr18 的偏好性（目标方向）

参考文献：
  Hu et al. 2024 Nat Microbiol — GprC 关键残基（N2.57/R6.45/S2.41）实验验证
  FoldX: Schymkowitz et al. 2005 Nucleic Acids Res — 突变体结构预测

FoldX 下载（学术免费）：https://foldxsuite.crg.eu/academic-license-info
"""

from __future__ import annotations

import json
import subprocess
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from utils import get_logger, get_project_root, resolve_path
from prepare_receptor import prepare_receptor_adfr


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

ONE_LETTER = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
THREE_LETTER = {v: k for k, v in ONE_LETTER.items()}

ALL_AAS = list("ACDEFGHIKLMNPQRSTVWY")


@dataclass
class MutantDockingResult:
    """单个突变体的对接结果。"""
    receptor: str          # 受体名（如 "GprC"）
    mutation: str          # 突变描述（如 "N83A"）
    wt_residue: str        # 野生型氨基酸单字母
    mut_residue: str       # 突变型氨基酸单字母
    residue_num: int       # 残基编号
    dg_ascr18: float       # ΔG(mut, ascr18) kcal/mol
    dg_ascr3: float        # ΔG(mut, ascr3)  kcal/mol
    dg_wt_ascr18: float    # ΔG(WT, ascr18)  kcal/mol（参考）
    dg_wt_ascr3: float     # ΔG(WT, ascr3)   kcal/mol（参考）
    ddg_ascr18: float      # ΔΔG(ascr18) = dg_ascr18 - dg_wt_ascr18
    ddg_ascr3: float       # ΔΔG(ascr3)  = dg_ascr3  - dg_wt_ascr3
    ddg_selectivity: float # ΔΔG_sel = ddg_ascr18 - ddg_ascr3（<0 = 增强 ascr18 偏好）
    sel_wt: float          # ΔG_sel(WT)  = dg_wt_ascr18 - dg_wt_ascr3
    sel_mut: float         # ΔG_sel(mut) = dg_ascr18 - dg_ascr3


# ---------------------------------------------------------------------------
# FoldX 工具函数
# ---------------------------------------------------------------------------

def _find_foldx(foldx_bin: Optional[str] = None) -> Path:
    """
    查找 FoldX 可执行文件。

    搜索顺序：
      1. config 指定路径
      2. 系统 PATH（foldx / foldx.exe）
      3. 常见安装路径

    未找到时抛出含下载指引的异常。
    """
    candidates = []
    if foldx_bin:
        candidates.append(Path(foldx_bin))

    # PATH 中查找
    for name in ["foldx", "foldx.exe", "FoldX", "FoldX.exe"]:
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))

    # 常见路径（包含版本化文件名）
    for p in [
        Path("D:/foldxWindows/foldx_20261231.exe"),
        Path("D:/drylab-tools/foldx/foldx.exe"),
        Path("D:/foldx/foldx.exe"),
        Path("/usr/local/bin/foldx"),
        Path.home() / "foldx" / "foldx",
        Path.home() / "Downloads" / "foldx" / "foldx",
    ]:
        candidates.append(p)

    for p in candidates:
        if p.exists():
            return p

    raise FileNotFoundError(
        "FoldX 未找到。请下载并安装 FoldX（学术免费）：\n"
        "  https://foldxsuite.crg.eu/academic-license-info\n"
        "下载后将 foldx 可执行文件放到以下任意位置：\n"
        "  Windows: D:\\drylab-tools\\foldx\\foldx.exe\n"
        "  Mac:     ~/foldx/foldx 并 chmod +x\n"
        "或在 config.yaml 的 mutagenesis.foldx_bin 中指定路径。"
    )


def _get_residue_wt(pdb_path: Path, chain_id: str, residue_num: int) -> str:
    """
    从 PDB 文件中查询指定残基的野生型单字母代码。
    使用 stdlib 文本解析，不依赖 Bio.PDB（避免 Windows SSH DLL crash）。
    """
    found = None
    available = []
    for line in Path(pdb_path).read_text(errors="replace").splitlines():
        if not line.startswith("ATOM"):
            continue
        if len(line) < 27:
            continue
        atom_name = line[12:16].strip()
        resname   = line[17:20].strip()
        chain     = line[21]
        try:
            resseq = int(line[22:26].strip())
        except ValueError:
            continue
        if chain != chain_id:
            continue
        if atom_name == "CA":
            available.append(resseq)
            if resseq == residue_num:
                found = resname
    if found is None:
        rng = f"{min(available)}–{max(available)}" if available else "（无 CA 原子）"
        raise KeyError(
            f"残基 {residue_num} 在链 {chain_id} 中未找到。可用范围: {rng}"
        )
    return ONE_LETTER.get(found, "X")


def repair_receptor(
    pdb_path: Path,
    output_dir: Path,
    foldx_bin: Path,
) -> Path:
    """
    FoldX RepairPDB：对受体进行能量最小化，修复异常键长/键角。
    这是 BuildModel 的必要前置步骤。

    Args:
        pdb_path: 受体 PDB（TM-only，已清理）
        output_dir: 输出目录
        foldx_bin: FoldX 可执行文件路径

    Returns:
        修复后的 PDB 路径（`<stem>_Repair.pdb`）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    repaired_pdb = output_dir / f"{pdb_path.stem}_Repair.pdb"
    if repaired_pdb.exists():
        logger.info(f"  RepairPDB 已存在，跳过: {repaired_pdb.name}")
        return repaired_pdb

    logger.info(f"FoldX RepairPDB: {pdb_path.name}")

    # FoldX 需要 rotabase.txt 在工作目录；将其从 FoldX 安装目录复制过来
    rotabase_src = Path(foldx_bin).parent / "rotabase.txt"
    rotabase_dst = Path(pdb_path.parent) / "rotabase.txt"
    if rotabase_src.exists() and not rotabase_dst.exists():
        shutil.copy2(rotabase_src, rotabase_dst)

    cmd = [
        str(foldx_bin),
        "--command=RepairPDB",
        f"--pdb={pdb_path.name}",
        f"--output-dir={output_dir}",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(pdb_path.parent),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"FoldX RepairPDB 失败 (code={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    if not repaired_pdb.exists():
        raise RuntimeError(f"FoldX 未生成修复 PDB: {repaired_pdb}")

    logger.info(f"  RepairPDB 完成: {repaired_pdb.name}")
    return repaired_pdb


def build_mutants(
    repaired_pdb: Path,
    mutations: list[dict],  # [{"wt": "N", "chain": "A", "resnum": 83, "mut": "A"}, ...]
    output_dir: Path,
    foldx_bin: Path,
) -> dict[str, Path]:
    """
    FoldX BuildModel：批量生成突变体 PDB 文件。

    FoldX individual_list.txt 格式（每行一个突变）：
      <WT_aa><chain><resnum><mut_aa>;
      示例：NA83A;  → 第 83 号残基 Asn → Ala（chain A）

    FoldX 输出：<pdb_stem>_1.pdb, <pdb_stem>_2.pdb, ...（按列表顺序编号）

    Args:
        repaired_pdb: FoldX RepairPDB 输出的 PDB
        mutations: 突变列表，每条含 wt/chain/resnum/mut 字段
        output_dir: 输出目录
        foldx_bin: FoldX 可执行文件路径

    Returns:
        {mutation_label: pdb_path} 字典
        mutation_label 格式："{wt}{resnum}{mut}"（如 "N83A"）
    """
    logger = get_logger()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 写 individual_list.txt
    list_path = output_dir / "individual_list.txt"
    lines = []
    labels = []
    for m in mutations:
        label = f"{m['wt']}{m['resnum']}{m['mut']}"
        foldx_line = f"{m['wt']}{m['chain']}{m['resnum']}{m['mut']};"
        lines.append(foldx_line)
        labels.append(label)

    list_path.write_text("\n".join(lines) + "\n")
    logger.info(f"突变列表已写入: {list_path} ({len(lines)} 个突变)")

    # FoldX 需要 rotabase.txt 在工作目录
    rotabase_src = Path(foldx_bin).parent / "rotabase.txt"
    rotabase_dst = Path(repaired_pdb.parent) / "rotabase.txt"
    if rotabase_src.exists() and not rotabase_dst.exists():
        shutil.copy2(rotabase_src, rotabase_dst)

    # 运行 BuildModel
    stem = repaired_pdb.stem
    cmd = [
        str(foldx_bin),
        "--command=BuildModel",
        f"--pdb={repaired_pdb.name}",
        f"--mutant-file={list_path.name}",
        f"--output-dir={output_dir}",
        "--numberOfRuns=1",
        "--out-pdb=true",
    ]
    logger.info(f"FoldX BuildModel: {len(mutations)} 个突变")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repaired_pdb.parent),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"FoldX BuildModel 失败 (code={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    # 收集输出（FoldX 按顺序编号 _1.pdb, _2.pdb, ...）
    # 特殊情况：单突变时部分 FoldX 版本输出无后缀 {stem}.pdb
    mutant_pdbs = {}
    for i, label in enumerate(labels, start=1):
        expected = output_dir / f"{stem}_{i}.pdb"
        if not expected.exists():
            alt_run = output_dir / f"{stem}_{i}_0.pdb"  # numberOfRuns>1 格式
            alt_single = output_dir / f"{stem}.pdb"      # 单突变无编号格式
            if alt_run.exists():
                expected = alt_run
            elif alt_single.exists() and len(labels) == 1:
                expected = alt_single
            else:
                logger.warning(f"  突变体 PDB 未找到: {expected.name}，跳过 {label}")
                continue
        # 重命名为有意义的文件名
        target = output_dir / f"{repaired_pdb.stem.replace('_Repair', '')}_{label}.pdb"
        shutil.copy2(expected, target)
        mutant_pdbs[label] = target
        logger.info(f"  生成突变体: {target.name}")

    logger.info(f"BuildModel 完成：{len(mutant_pdbs)}/{len(mutations)} 个突变体")
    return mutant_pdbs


# ---------------------------------------------------------------------------
# 突变列表生成
# ---------------------------------------------------------------------------

def make_alanine_scan_mutations(
    pdb_path: Path,
    residue_nums: list[int],
    chain_id: str = "A",
) -> list[dict]:
    """
    生成丙氨酸扫描突变列表（对每个目标残基替换为 Ala）。
    跳过本身已经是 Ala 的残基。

    Args:
        pdb_path: 受体 PDB（用于读取 WT 氨基酸）
        residue_nums: 目标残基编号列表
        chain_id: 链 ID

    Returns:
        突变列表，格式同 build_mutants() 的 mutations 参数
    """
    mutations = []
    for resnum in residue_nums:
        wt = _get_residue_wt(pdb_path, chain_id, resnum)
        if wt == "A":
            get_logger().info(f"  残基 {resnum} 本身已是 Ala，跳过")
            continue
        mutations.append({"wt": wt, "chain": chain_id, "resnum": resnum, "mut": "A"})
    return mutations


def make_saturation_scan_mutations(
    pdb_path: Path,
    residue_nums: list[int],
    chain_id: str = "A",
    exclude_aas: Optional[list[str]] = None,
) -> list[dict]:
    """
    生成饱和突变扫描列表（每个目标残基 × 所有 20 种氨基酸）。
    跳过与野生型相同的氨基酸。

    Args:
        pdb_path: 受体 PDB
        residue_nums: 目标残基编号列表
        chain_id: 链 ID
        exclude_aas: 排除的氨基酸（如 ["P", "C"]，脯氨酸和半胱氨酸通常影响结构稳定性）

    Returns:
        突变列表
    """
    exclude = set(exclude_aas or [])
    mutations = []
    for resnum in residue_nums:
        wt = _get_residue_wt(pdb_path, chain_id, resnum)
        for aa in ALL_AAS:
            if aa == wt or aa in exclude:
                continue
            mutations.append({"wt": wt, "chain": chain_id, "resnum": resnum, "mut": aa})
    return mutations


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_mutagenesis(
    config: dict,
    wt_dock_results: Optional[dict] = None,
) -> list[MutantDockingResult]:
    """
    执行 in silico 突变扫描完整流程。

    流程：
      1. 加载 WT 对接结果（来自 docking_results.json 或参数传入）
      2. FoldX RepairPDB → BuildModel 生成突变体
      3. ADFR 准备突变体 PDBQT
      4. 两阶段 Vina 对接（ascr18 + ascr3）
      5. 计算 ΔΔG_selectivity，生成排名报告

    Args:
        config: pipeline 配置字典
        wt_dock_results: 野生型对接结果 {pair_name: dg}，None 则从文件加载

    Returns:
        突变扫描结果列表，按 ΔΔG_selectivity 排序
    """
    logger = get_logger()
    root = get_project_root(config)
    mut_cfg = config.get("mutagenesis", {})

    # 目录结构
    mutant_dir = root / config["paths"].get(
        "mutagenesis_dir",
        config["paths"]["results_dir"].replace("results", "mutagenesis"),
    )
    mutant_dir.mkdir(parents=True, exist_ok=True)

    mutant_source = mut_cfg.get("mutant_source", "foldx")
    docking_mode = mut_cfg.get("docking_mode", "singlestage")
    logger.info(f"突变体来源: {mutant_source}，对接协议: {docking_mode}")

    # FoldX 路径（仅 foldx 模式需要）
    foldx_bin = None
    if mutant_source == "foldx":
        foldx_bin = _find_foldx(mut_cfg.get("foldx_bin"))
        logger.info(f"FoldX: {foldx_bin}")

    # 确定 WT baseline 路径（v2 或 repro）
    wt_baseline = mut_cfg.get("wt_baseline", "repro")
    if wt_baseline == "v2":
        baseline_prepared_dir = root / "experiments/docking/prepared"
        baseline_results_dir = root / "experiments/docking/results"
        logger.info("WT 基线: v2 pipeline (experiments/docking/)")
    else:
        baseline_prepared_dir = root / config["paths"]["prepared_dir"]
        baseline_results_dir = root / config["paths"]["results_dir"]
        logger.info("WT 基线: docking-repro pipeline")

    # 加载 WT 对接结果
    if wt_dock_results is None:
        results_json = baseline_results_dir / "docking_results.json"
        if not results_json.exists():
            raise FileNotFoundError(
                f"WT 对接结果不存在: {results_json}\n"
                + ("请先完成 v2 pipeline production run。" if wt_baseline == "v2"
                   else "请先运行 --step dock 完成野生型对接。")
            )
        raw = json.loads(results_json.read_text(encoding="utf-8"))
        wt_dock_results = {r["pair_name"]: r["best_affinity"] for r in raw}
        logger.info(f"已加载 WT 对接结果: {len(wt_dock_results)} 个对接对")

    # 确定要扫描的受体（默认仅 GprC，因为有 Hu2024 关键残基数据）
    target_receptors = mut_cfg.get("target_receptors", ["GprC"])

    all_results = []

    for rec_name in target_receptors:
        if rec_name not in config["receptors"]:
            logger.warning(f"受体 {rec_name} 不在 config 中，跳过")
            continue

        logger.info(f"\n{'='*60}")
        logger.info(f"突变扫描：{rec_name}")
        logger.info(f"{'='*60}")

        rec_cfg = config["receptors"][rec_name]
        receptor_dir = root / config["paths"]["receptor_dir"]
        pdb_path = receptor_dir / rec_cfg["pdb_file"]

        # WT 对接结果
        wt_ascr18 = wt_dock_results.get(f"{rec_name}_ascr18")
        wt_ascr3 = wt_dock_results.get(f"{rec_name}_ascr3")
        if wt_ascr18 is None or wt_ascr3 is None:
            logger.warning(
                f"{rec_name}: WT 对接结果不完整 "
                f"(ascr18={wt_ascr18}, ascr3={wt_ascr3})，跳过"
            )
            continue
        logger.info(
            f"WT: ΔG(ascr18)={wt_ascr18:.2f}, ΔG(ascr3)={wt_ascr3:.2f}, "
            f"选择性={wt_ascr18 - wt_ascr3:+.2f}"
        )

        # 确定扫描残基
        scan_residues = _get_scan_residues(config, rec_name)
        scan_type = mut_cfg.get("scan_type", "alanine")  # "alanine" or "saturation"

        logger.info(f"扫描残基: {scan_residues}，扫描类型: {scan_type}")

        # 突变体工作目录
        rec_mut_dir = mutant_dir / rec_name
        rec_mut_dir.mkdir(parents=True, exist_ok=True)

        # TM PDB — 必须先获取，用于：
        #   1. 确定突变列表（确保残基在 TM 域内）
        #   2. FoldX RepairPDB + BuildModel 的输入
        #   3. 受体质心计算（singlestage 对接）
        tm_pdb = baseline_prepared_dir / "receptors" / f"{pdb_path.stem}_tm.pdb"
        if not tm_pdb.exists():
            hint = ("experiments/docking/prepared/receptors/"
                    if wt_baseline == "v2" else "experiments/docking-repro/prepared/receptors/")
            raise FileNotFoundError(
                f"TM PDB 不存在: {tm_pdb}\n"
                f"请确认 {hint} 中有对应文件。"
            )

        # 生成突变列表（使用 TM PDB，确保残基在跨膜域内；域外残基会被 _get_residue_wt 跳过）
        if scan_type == "alanine":
            mutations = make_alanine_scan_mutations(tm_pdb, scan_residues)
        elif scan_type == "saturation":
            exclude_aas = mut_cfg.get("exclude_aas", None)
            mutations = make_saturation_scan_mutations(
                tm_pdb, scan_residues, exclude_aas=exclude_aas
            )
        else:
            raise ValueError(f"未知扫描类型: {scan_type}（支持 'alanine' / 'saturation'）")

        if not mutations:
            logger.warning(f"  {rec_name}: 无有效突变，跳过")
            continue
        logger.info(f"  共 {len(mutations)} 个突变待处理")

        repaired_pdb = None  # 仅 FoldX 模式使用

        if mutant_source == "foldx":
            # Step 1: FoldX RepairPDB
            repaired_pdb = repair_receptor(tm_pdb, rec_mut_dir / "foldx", foldx_bin)

            # Step 2: FoldX BuildModel
            mutant_pdbs = build_mutants(
                repaired_pdb,
                mutations,
                output_dir=rec_mut_dir / "foldx",
                foldx_bin=foldx_bin,
            )

            # Step 3: ADFR 准备突变体 PDBQT
            adfr_bin = config["remote"]["adfr_bin"]
            prepared_flat_dir = mutant_dir / "prepared"
            prepared_flat_dir.mkdir(parents=True, exist_ok=True)

            mutant_pdbqts = {}
            for label, mut_pdb in mutant_pdbs.items():
                pdbqt_dir = rec_mut_dir / label / "pdbqt"
                try:
                    pdbqt = prepare_receptor_adfr(
                        mut_pdb, pdbqt_dir, adfr_bin, skip_tm_extraction=True
                    )
                    mutant_pdbqts[label] = pdbqt
                    flat_name = f"{rec_name}_{label}_tm.pdbqt"
                    flat_dest = prepared_flat_dir / flat_name
                    shutil.copy2(pdbqt, flat_dest)
                    logger.info(f"  → 已复制到 prepared/: {flat_name}")
                except Exception as e:
                    logger.error(f"  ADFR 准备失败 ({label}): {e}")

        elif mutant_source in ("af2", "af3"):
            # AF2/AF3 突变体 PDBQT 已通过外部流程准备好，直接加载
            # AF3 命名约定: {mutagenesis_dir}/af3_prepared/{rec_name}/{label}_tm.pdbqt
            # AF2 命名约定: {mutagenesis_dir}/af2_prepared/{rec_name}/{label}_tm.pdbqt
            af_dir = mutant_dir / f"{mutant_source}_prepared" / rec_name
            mutant_pdbqts = {}
            for mut in mutations:
                label = f"{mut['wt']}{mut['resnum']}{mut['mut']}"
                pdbqt = af_dir / f"{label}_tm.pdbqt"
                if pdbqt.exists():
                    mutant_pdbqts[label] = pdbqt
                else:
                    logger.warning(
                        f"  {mutant_source.upper()} 突变体 PDBQT 不存在: {pdbqt}\n"
                        f"  请先通过 AlphaFold Server 预测并运行 ADFR prepare_receptor"
                    )
            if not mutant_pdbqts:
                logger.error(
                    f"  {rec_name}: 未找到任何 {mutant_source.upper()} 突变体 PDBQT，跳过。\n"
                    f"  运行 generate_mutant_fastas.py 生成序列后提交 AlphaFold Server。"
                )
                continue

        # Step 4: Vina 对接（ascr18 + ascr3）
        if docking_mode == "singlestage":
            from dock import dock_pair_singlestage, get_tm_helix_ranges
        else:
            from dock import dock_pair_twostage, get_tm_helix_ranges
        helix_ranges = get_tm_helix_ranges(config, rec_name)

        ligand_dir = baseline_prepared_dir / "ligands"
        lig_pdbqts = {}
        for lig_name in ["ascr18", "ascr3"]:
            # Orca DFT 输出命名约定：{lig_name}_optimized.pdbqt
            lig_pdbqt = ligand_dir / f"{lig_name}_optimized.pdbqt"
            if lig_pdbqt.exists():
                lig_pdbqts[lig_name] = lig_pdbqt
            else:
                logger.warning(f"  配体 PDBQT 不存在: {lig_pdbqt}（Orca 配体准备是否已完成？）")

        for label, pdbqt in mutant_pdbqts.items():
            dg = {}
            for lig_name, lig_pdbqt in lig_pdbqts.items():
                pair_name = f"{rec_name}_{label}_{lig_name}"
                out_dir = rec_mut_dir / label / "docking"
                try:
                    # COM 计算用 WT TM PDB（单残基突变对质心影响 <0.1Å）
                    # FoldX 模式用 repaired_pdb 保持历史兼容
                    tm_ref = repaired_pdb if mutant_source == "foldx" else tm_pdb
                    if docking_mode == "singlestage":
                        result = dock_pair_singlestage(
                            receptor_pdbqt=pdbqt,
                            ligand_pdbqt=lig_pdbqt,
                            pair_name=pair_name,
                            tm_pdb=tm_ref,
                            output_dir=out_dir,
                            config=config,
                            tm_helix_ranges=helix_ranges,
                        )
                    else:
                        result = dock_pair_twostage(
                            receptor_pdbqt=pdbqt,
                            ligand_pdbqt=lig_pdbqt,
                            pair_name=pair_name,
                            tm_pdb=tm_ref,
                            output_dir=out_dir,
                            config=config,
                            tm_helix_ranges=helix_ranges,
                        )
                    dg[lig_name] = result.best_affinity
                except Exception as e:
                    logger.error(f"  对接失败 ({pair_name}): {e}")

            if "ascr18" in dg and "ascr3" in dg:
                ddg18 = dg["ascr18"] - wt_ascr18
                ddg3 = dg["ascr3"] - wt_ascr3
                ddg_sel = ddg18 - ddg3

                # 解析突变标签（如 "N83A"）
                mut_info = next(
                    m for m in mutations
                    if f"{m['wt']}{m['resnum']}{m['mut']}" == label
                )

                mr = MutantDockingResult(
                    receptor=rec_name,
                    mutation=label,
                    wt_residue=mut_info["wt"],
                    mut_residue=mut_info["mut"],
                    residue_num=mut_info["resnum"],
                    dg_ascr18=dg["ascr18"],
                    dg_ascr3=dg["ascr3"],
                    dg_wt_ascr18=wt_ascr18,
                    dg_wt_ascr3=wt_ascr3,
                    ddg_ascr18=ddg18,
                    ddg_ascr3=ddg3,
                    ddg_selectivity=ddg_sel,
                    sel_wt=wt_ascr18 - wt_ascr3,
                    sel_mut=dg["ascr18"] - dg["ascr3"],
                )
                all_results.append(mr)
                logger.info(
                    f"  {label}: ΔG(18)={dg['ascr18']:.2f}, ΔG(3)={dg['ascr3']:.2f}, "
                    f"ΔΔG_sel={ddg_sel:+.2f}"
                )

    # 排序（ΔΔG_sel 升序，越小越好）
    all_results.sort(key=lambda r: r.ddg_selectivity)

    # 保存 JSON
    results_path = mutant_dir / "mutagenesis_results.json"
    results_path.write_text(
        json.dumps([asdict(r) for r in all_results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"\n突变扫描完成，结果已保存: {results_path}")

    # 生成报告
    report_path = mutant_dir / "mutagenesis_report.md"
    _write_report(all_results, report_path, mutant_source=mutant_source, docking_mode=docking_mode)
    logger.info(f"报告已保存: {report_path}")

    return all_results


# ---------------------------------------------------------------------------
# 辅助：确定扫描残基
# ---------------------------------------------------------------------------

def _get_scan_residues(config: dict, rec_name: str) -> list[int]:
    """
    确定要扫描的残基列表。

    优先级：
      1. config mutagenesis.scan_residues[rec_name]（用户显式指定）
      2. config analysis.key_residues[rec_name]（文献关键残基）
      3. 提示用户手动指定
    """
    mut_cfg = config.get("mutagenesis", {})

    # 用户显式指定
    user_residues = mut_cfg.get("scan_residues", {}).get(rec_name)
    if user_residues:
        return sorted(user_residues)

    # 文献关键残基（权威源：config.yaml analysis.key_residues）
    key_res = config.get("analysis", {}).get("key_residues", {}).get(rec_name, {})
    if key_res:
        # 结构化格式 {bw: {seqpos, resname, ...}} → 提取 seqpos
        return sorted(v["seqpos"] if isinstance(v, dict) else v for v in key_res.values())

    raise ValueError(
        f"未找到 {rec_name} 的扫描残基。\n"
        f"请在 config.yaml 的 mutagenesis.scan_residues.{rec_name} 中指定残基编号列表。"
    )


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

def _write_report(
    results: list[MutantDockingResult],
    output_path: Path,
    mutant_source: str = "foldx",
    docking_mode: str = "singlestage",
) -> None:
    """生成 Markdown 格式的突变扫描报告。"""
    if not results:
        output_path.write_text("# 突变扫描结果\n\n无有效结果。\n", encoding="utf-8")
        return

    lines = [
        "# In Silico 突变扫描报告",
        "",
        "**目标**：预测增强 GprC 对 ascr#18（PPN 标志物）选择性的突变位点",
        "",
        "**评分标准**：ΔΔG_sel < 0 表示突变增强了对 ascr#18 的偏好性",
        f"  - ΔΔG_sel = ΔΔG(ascr18) - ΔΔG(ascr3) = [ΔG(mut,18) - ΔG(WT,18)] - [ΔG(mut,3) - ΔG(WT,3)]",
        "",
        "---",
        "",
        "## 结果排名（按选择性改善从大到小）",
        "",
        "| 排名 | 突变 | ΔG(18) | ΔG(3) | ΔΔG(18) | ΔΔG(3) | ΔΔG_sel | 评估 |",
        "|------|------|--------|-------|---------|--------|---------|------|",
    ]

    # WT 参考值（取第一个结果的 WT 值）
    ref = results[0]
    sel_wt = ref.sel_wt

    for i, r in enumerate(results, 1):
        flag = ""
        if r.ddg_selectivity < -0.5:
            flag = "✅ 显著改善"
        elif r.ddg_selectivity < -0.2:
            flag = "↑ 轻微改善"
        elif r.ddg_selectivity > 0.5:
            flag = "❌ 降低特异性"
        lines.append(
            f"| {i} | **{r.mutation}** | {r.dg_ascr18:.2f} | {r.dg_ascr3:.2f} | "
            f"{r.ddg_ascr18:+.2f} | {r.ddg_ascr3:+.2f} | **{r.ddg_selectivity:+.2f}** | {flag} |"
        )

    lines += [
        "",
        f"> WT 参考：ΔG(ascr18)={ref.dg_wt_ascr18:.2f}, ΔG(ascr3)={ref.dg_wt_ascr3:.2f}, "
        f"选择性={sel_wt:+.2f} kcal/mol",
        "",
        "---",
        "",
        "## 方法说明",
        "",
        f"1. **结构预测**：{'AlphaFold 3 Server（diffusion-based，全长蛋白预测 + pLDDT TM 域提取）' if mutant_source == 'af3' else 'AlphaFold 2 Server' if mutant_source == 'af2' else 'FoldX BuildModel（WT 结构基础上的副链替换）'}",
        "2. **受体准备**：ADFR Suite prepare_receptor（与 Hu2024 方法一致）",
        f"3. **对接**：AutoDock Vina {'单阶段（40Å/0.1Å, exh=200）' if docking_mode == 'singlestage' else '两阶段（Stage1: 40Å/0.25Å, Stage2: 20Å/0.1Å, exh=200）'}",
        "4. **验证基准**：N83A（Hu2024 报道丧失功能）、R281A（亲和力剧降）",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
