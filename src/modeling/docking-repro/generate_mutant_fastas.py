"""
生成突变体 FASTA 文件，供手动提交 AlphaFold 3 Server（alphafoldserver.com）

注意：Hu2024 原文使用 AF2 web server（5 models, 24 max_recycles, 2 num_ensemble），
但 alphafoldserver.com 现运行 AF3（diffusion-based 架构），不提供上述参数。
我们使用 AF3 默认参数。详见 docs/logs/2026-04-07.md §5。

输出目录：experiments/docking-repro/mutagenesis/fastas/{rec_name}/

FASTA 文件命名：{label}.fasta（如 N83A.fasta）
    > {rec_name}_{label}
    {突变后全长序列}

下载 AF2 结果后放置规范：
    experiments/docking-repro/mutagenesis/af2_structures/{rec_name}/{label}.pdb
    （选取 5 个 model 中 pLDDT 最高的，重命名为 {label}.pdb）

然后运行 TM 截断 + ADFR prepare_receptor（尚未自动化，需手动或补充脚本）：
    输出: experiments/docking-repro/mutagenesis/af2_prepared/{rec_name}/{label}_tm.pdbqt

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
sys.path.insert(0, str(_this_dir.parent / "docking"))

from utils import get_project_root, load_config

ONE_LETTER = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


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


def main() -> None:
    parser = argparse.ArgumentParser(description="为 AF3 Server 生成突变体 FASTA")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--receptors", nargs="+", default=None,
                        help="要处理的受体（默认: config 中 mutagenesis.target_receptors）")
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

        fastas = generate_fastas_for_receptor(
            rec_name=rec_name,
            pdb_path=full_pdb,
            scan_residues=scan_residues,
            output_dir=output_base / rec_name,
        )
        all_generated.extend(fastas)

    print(f"\n共生成 {len(all_generated)} 个 FASTA 文件。")
    print("\n下一步：")
    print("  1. 前往 https://alphafoldserver.com/")
    print("  2. 逐个（或批量）提交 FASTA 文件")
    print("     AF2 参数（匹配 Hu2024）：5 models, 24 max_recycles, 2 num_ensemble")
    print("  3. 下载结果，选取 pLDDT 最高的 model，")
    print("     重命名为 {label}.pdb，放入：")
    print(f"     {root}/experiments/docking-repro/mutagenesis/af2_structures/{{rec_name}}/")
    print("  4. 对每个 PDB 执行 TM 截断 + ADFR prepare_receptor，")
    print("     输出到 af2_prepared/{{rec_name}}/{{label}}_tm.pdbqt")
    print("  5. 在 config.yaml 中设置 mutagenesis.mutant_source: af2")
    print("     然后运行 run_mutagenesis_alanine.py")


if __name__ == "__main__":
    main()
