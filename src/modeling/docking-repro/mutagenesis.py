"""
In silico 突变扫描模块 — 预测增强 ascr#18/ascr#3 选择性的突变位点

目标：通过系统性突变受体结合口袋残基，找到能够提高对 ascr#18（PPN 标志物）
      识别特异性、同时降低对 ascr#3（自由生活线虫标志物）亲和力的突变位点。

方法路线：
  1. AlphaFold 3 Server — 预测突变体全长结构，ADFR 准备 PDBQT
  2. Vina 对接（复用 dock.py，支持 singlestage/twostage）— 对 ascr18 + ascr3 分别打分
  3. ΔΔG 选择性评分：
       ΔG_sel(WT)  = ΔG(WT, ascr18)  - ΔG(WT, ascr3)
       ΔG_sel(mut) = ΔG(mut, ascr18) - ΔG(mut, ascr3)
       ΔΔG_sel     = ΔG_sel(mut) - ΔG_sel(WT)
       ΔΔG_sel < 0 → 突变增强了对 ascr18 的偏好性（目标方向）

参考文献：
  Hu et al. 2024 Nat Microbiol — GprC 关键残基（N2.57/R6.45/S2.41）实验验证
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from utils import generate_run_id, get_logger, get_project_root, save_results_json


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
      2. 加载 AF3 预测的突变体 PDBQT（外部准备）
      3. 两阶段 Vina 对接（ascr18 + ascr3）
      4. 计算 ΔΔG_selectivity，生成排名报告

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

    mutant_source = mut_cfg.get("mutant_source", "af3")
    docking_mode = mut_cfg.get("docking_mode", "singlestage")
    logger.info(f"突变体来源: {mutant_source}，对接协议: {docking_mode}")

    # 确定 WT baseline 路径（v2 或 repro）
    wt_baseline = mut_cfg.get("wt_baseline", "repro")
    if wt_baseline == "v2":
        baseline_prepared_dir = root / "experiments/docking/prepared"
        baseline_results_dir = root / "experiments/docking/results"
        logger.info("WT 基线: v2 pipeline (experiments/docking/)")
    else:
        baseline_prepared_dir = root / config["paths"]["prepared_dir"]
        wt_subdir = config["paths"].get("wt_singlestage_subdir", "wt_singlestage")
        baseline_results_dir = root / config["paths"]["results_dir"] / wt_subdir
        logger.info("WT 基线: docking-repro pipeline")

    # 加载 WT 对接结果
    if wt_dock_results is None:
        results_filename = config["paths"].get("results_filename", "docking_results.json")
        results_json = baseline_results_dir / results_filename
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
        #   2. 受体质心计算（singlestage 对接）
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

        if mutant_source in ("af2", "af3"):
            # AF2/AF3 突变体 PDBQT 已通过外部流程准备好，直接加载
            # AF3 命名约定: {mutagenesis_dir}/af3_prepared/{rec_name}/{label}_tm.pdbqt
            # AF2 命名约定: {mutagenesis_dir}/af2_prepared/{rec_name}/{label}_tm.pdbqt
            # 可选：mutant_pdbqt_subdir（如 "saturation"）→ af3_prepared/{rec_name}/saturation/
            af_dir = mutant_dir / f"{mutant_source}_prepared" / rec_name
            pdbqt_subdir = mut_cfg.get("mutant_pdbqt_subdir", "")
            if pdbqt_subdir:
                af_dir = af_dir / pdbqt_subdir
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
            from dock import (
                dock_pair_singlestage,
                get_box_center_offset,
                get_manual_box_center,
                get_receptor_box_size,
                get_tm_helix_ranges,
            )
        else:
            from dock import dock_pair_twostage, get_tm_helix_ranges
        helix_ranges = get_tm_helix_ranges(config, rec_name)
        box_offset = get_box_center_offset(config, rec_name) if docking_mode == "singlestage" else None
        rec_box_size = get_receptor_box_size(config, rec_name) if docking_mode == "singlestage" else None
        manual_center = get_manual_box_center(config, rec_name) if docking_mode == "singlestage" else None

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
                    tm_ref = tm_pdb
                    if docking_mode == "singlestage":
                        result = dock_pair_singlestage(
                            receptor_pdbqt=pdbqt,
                            ligand_pdbqt=lig_pdbqt,
                            pair_name=pair_name,
                            tm_pdb=tm_ref,
                            output_dir=out_dir,
                            config=config,
                            tm_helix_ranges=helix_ranges,
                            box_center_offset=box_offset,
                            receptor_box_size=rec_box_size,
                            manual_box_center=manual_center,
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

    # 保存 JSON（时间戳 + latest）
    results_path = save_results_json(
        [asdict(r) for r in all_results], mutant_dir, generate_run_id(), config,
        filename="mutagenesis_results.json",
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
    mutant_source: str = "af3",
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
        f"1. **结构预测**：{'AlphaFold 3 Server（diffusion-based，全长蛋白预测 + pLDDT TM 域提取）' if mutant_source == 'af3' else 'AlphaFold 2 Server'}",
        "2. **受体准备**：ADFR Suite prepare_receptor（与 Hu2024 方法一致）",
        f"3. **对接**：AutoDock Vina {'单阶段（40Å/0.1Å, exh=200）' if docking_mode == 'singlestage' else '两阶段（Stage1: 40Å/0.25Å, Stage2: 20Å/0.1Å, exh=200）'}",
        "4. **验证基准**：N83A（Hu2024 报道丧失功能）、R281A（亲和力剧降）",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
