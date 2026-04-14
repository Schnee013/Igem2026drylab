"""
生成突变体 FASTA 文件，供手动提交 AlphaFold 3 Server（alphafoldserver.com）

注意：Hu2024 原文使用 AF2 web server（5 models, 24 max_recycles, 2 num_ensemble），
但 alphafoldserver.com 现运行 AF3（diffusion-based 架构），不提供上述参数。
我们使用 AF3 默认参数。详见 docs/logs/2026-04-07.md §5。

输出目录：experiments/docking-repro/mutagenesis/fastas/{rec_name}/

FASTA 文件命名：{label}.fasta（如 N83A.fasta）
    > {rec_name}_{label}
    {突变后全长序列}

完整执行流程（AF3 提交 → 结构处理 → 对接）：
    见 ~/.claude/plans/sequential-dancing-origami.md

用法：
    python generate_mutant_fastas.py
    python generate_mutant_fastas.py --receptors GprC
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_this_dir = Path(__file__).parent
sys.path.insert(0, str(_this_dir))

from utils import get_project_root, load_config

ONE_LETTER = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

# 20 种标准氨基酸单字母代码（saturation scan 使用）
ALL_AAS = list("ACDEFGHIKLMNPQRSTVWY")


def _read_sequence_from_pdb(pdb_path: Path, chain_id: str = "A") -> tuple[list[int], list[str]]:
    """从 PDB 读取残基序列（CA 原子），返回 (residue_nums, one_letter_codes) 列表。"""
    res_nums = []
    res_codes = []
    seen = set()
    for line in pdb_path.read_text(errors="replace").splitlines():
        if not line.startswith("ATOM"):
            continue
        if len(line) < 27:
            continue
        atom_name = line[12:16].strip()
        if atom_name != "CA":
            continue
        chain = line[21]
        if chain != chain_id:
            continue
        try:
            resseq = int(line[22:26].strip())
        except ValueError:
            continue
        resname = line[17:20].strip()
        if resseq not in seen:
            seen.add(resseq)
            res_nums.append(resseq)
            res_codes.append(ONE_LETTER.get(resname, "X"))
    return res_nums, res_codes


def generate_fastas_for_receptor(
    rec_name: str,
    pdb_path: Path,
    scan_residues: list[int],
    output_dir: Path,
    chain_id: str = "A",
) -> list[Path]:
    """
    为指定受体的所有 alanine scan 残基生成突变 FASTA 文件。
    跳过本身已是 Ala 的残基。

    Returns:
        生成的 FASTA 文件路径列表
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    res_nums, res_codes = _read_sequence_from_pdb(pdb_path, chain_id)
    num_to_idx = {n: i for i, n in enumerate(res_nums)}

    generated = []
    skipped = []
    for resnum in scan_residues:
        if resnum not in num_to_idx:
            print(f"  警告: 残基 {resnum} 在 {pdb_path.name} 中未找到，跳过")
            continue
        idx = num_to_idx[resnum]
        wt_aa = res_codes[idx]
        if wt_aa == "A":
            skipped.append(f"{wt_aa}{resnum}A（WT 已是 Ala）")
            continue

        label = f"{wt_aa}{resnum}A"
        mut_codes = res_codes.copy()
        mut_codes[idx] = "A"
        sequence = "".join(mut_codes)

        fasta_path = output_dir / f"{label}.fasta"
        fasta_path.write_text(
            f">{rec_name}_{label}\n{sequence}\n",
            encoding="utf-8",
        )
        generated.append(fasta_path)

    print(f"  {rec_name}: 生成 {len(generated)} 个 FASTA 文件 → {output_dir}")
    if skipped:
        print(f"  跳过: {', '.join(skipped)}")
    return generated


def generate_saturation_fastas_for_receptor(
    rec_name: str,
    pdb_path: Path,
    scan_residues: list[int],
    output_dir: Path,
    chain_id: str = "A",
) -> list[Path]:
    """
    为饱和突变扫描生成 FASTA 文件。
    每个目标位点生成除 WT 氨基酸和 Ala 外的氨基酸突变体（通常 18 种；
    若 WT 本身为 Ala，则生成 19 种——此时 Ala 约束等价于 WT 约束）。
    （Ala 突变体已在 alanine scan 中生成，避免重复。）

    Returns:
        生成的 FASTA 文件路径列表（按位点 × 氨基酸排列）
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    res_nums, res_codes = _read_sequence_from_pdb(pdb_path, chain_id)
    num_to_idx = {n: i for i, n in enumerate(res_nums)}

    generated = []
    for resnum in scan_residues:
        if resnum not in num_to_idx:
            print(f"  警告: 残基 {resnum} 在 {pdb_path.name} 中未找到，跳过")
            continue
        idx = num_to_idx[resnum]
        wt_aa = res_codes[idx]

        # 排除 WT 本身和 Ala（Ala 已由 alanine scan 覆盖）
        mut_aas = [aa for aa in ALL_AAS if aa != wt_aa and aa != "A"]
        for mut_aa in mut_aas:
            label = f"{wt_aa}{resnum}{mut_aa}"
            mut_codes = res_codes.copy()
            mut_codes[idx] = mut_aa
            sequence = "".join(mut_codes)

            fasta_path = output_dir / f"{label}.fasta"
            fasta_path.write_text(
                f">{rec_name}_{label}\n{sequence}\n",
                encoding="utf-8",
            )
            generated.append(fasta_path)

        print(f"  {rec_name} {wt_aa}{resnum}: 生成 {len(mut_aas)} 个饱和突变 FASTA")

    print(f"  {rec_name}: 共生成 {len(generated)} 个饱和突变 FASTA → {output_dir}")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="为 AF3 Server 生成突变体 FASTA")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--receptors", nargs="+", default=None,
                        help="要处理的受体（默认: config 中 mutagenesis.target_receptors）")
    parser.add_argument(
        "--scan-type", choices=["alanine", "saturation"], default="alanine",
        help="扫描类型：alanine（默认，每位点→Ala）或 saturation（每位点×18 AA）",
    )
    parser.add_argument(
        "--positions", nargs="+", type=int, default=None,
        help="saturation 模式下的目标位点列表（残基编号），覆盖 config scan_residues",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    mut_cfg = config.get("mutagenesis", {})
    target_receptors = args.receptors or mut_cfg.get("target_receptors", ["GprC"])

    # 使用全长 PDB 生成 FASTA（NOT TM-only）
    # 原因：Hu2024 提交全长序列给 AF server，获得全长预测后提取 TM 域。
    # AF 的 MSA 和结构预测依赖全长序列上下文，截断 TM 域会改变预测结果。
    receptor_dir = root / config["paths"]["receptor_dir"]

    output_base = root / config["paths"]["mutagenesis_dir"] / "fastas"
    scan_residues_cfg = mut_cfg.get("scan_residues", {})

    all_generated = []
    for rec_name in target_receptors:
        if rec_name not in config["receptors"]:
            print(f"受体 {rec_name} 不在 config 中，跳过")
            continue

        rec_cfg = config["receptors"][rec_name]
        full_pdb = receptor_dir / rec_cfg["pdb_file"]

        if not full_pdb.exists():
            print(f"  错误: 全长 PDB 不存在: {full_pdb}")
            print(f"  请检查 {receptor_dir}")
            continue

        scan_residues = scan_residues_cfg.get(rec_name, [])
        if not scan_residues:
            print(f"  {rec_name}: config 中无 scan_residues，跳过")
            continue

        if args.scan_type == "saturation":
            # saturation 模式：使用 --positions 指定位点，或退回 config scan_residues
            target_positions = args.positions if args.positions else scan_residues
            print(f"\n[{rec_name}] saturation scan，位点：{target_positions}")
            fastas = generate_saturation_fastas_for_receptor(
                rec_name=rec_name,
                pdb_path=full_pdb,
                scan_residues=target_positions,
                output_dir=output_base / rec_name / "saturation",
            )
        else:
            fastas = generate_fastas_for_receptor(
                rec_name=rec_name,
                pdb_path=full_pdb,
                scan_residues=scan_residues,
                output_dir=output_base / rec_name,
            )
        all_generated.extend(fastas)

    print(f"\n共生成 {len(all_generated)} 个 FASTA 文件。")
    print(f"输出目录：{output_base}")


if __name__ == "__main__":
    main()
