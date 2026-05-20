"""
批量将 AF3 输出的 mmCIF 转为 PDB 格式

输入：{mutagenesis_dir}/af3_structures/{RecName}/{Label}.cif
输出：{mutagenesis_dir}/af3_structures/{RecName}/{Label}.pdb

用法：
    python cif_to_pdb.py
    python cif_to_pdb.py --config path/to/config.yaml --project-root /path/to/root
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

from Bio.PDB import MMCIFParser, PDBIO
from Bio.PDB.PDBExceptions import PDBConstructionWarning

_this_dir = Path(__file__).resolve().parent

from utils import get_project_root, load_af3_job_filter, load_config


def convert_one(cif_path: Path) -> Path:
    """单个 CIF → PDB 转换，返回输出路径。"""
    parser = MMCIFParser(QUIET=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PDBConstructionWarning)
        structure = parser.get_structure(cif_path.stem, str(cif_path))

    pdb_path = cif_path.with_suffix(".pdb")
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(pdb_path))
    return pdb_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量 CIF → PDB 转换")
    parser.add_argument("--config", default=str(_this_dir / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--job-names-file", nargs="+", default=None,
        help="只转换指定 AF3 batch JSON 对应的结构，可传多个 JSON 文件",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="允许覆盖已存在的 PDB；默认跳过已存在文件",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root

    root = get_project_root(config)
    structures_dir = root / config["paths"]["mutagenesis_dir"] / "af3_structures"
    job_filter = load_af3_job_filter(args.job_names_file)

    cif_files = sorted(structures_dir.glob("*/*.cif"))
    if job_filter is not None:
        cif_files = [
            p for p in cif_files
            if (p.parent.name, p.stem.upper()) in job_filter
        ]
    print(f"找到 {len(cif_files)} 个 CIF 文件\n")

    converted = 0
    for cif in cif_files:
        rec = cif.parent.name
        label = cif.stem
        pdb_path = cif.with_suffix(".pdb")
        if pdb_path.exists() and not args.overwrite:
            print(f"  {rec}/{label}: 已存在，跳过（加 --overwrite 可重写）")
            continue
        pdb = convert_one(cif)
        print(f"  {rec}/{label}: {pdb.name}")
        converted += 1

    print(f"\n转换完成，共 {converted} 个 PDB 文件")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(_this_dir))
    main()
