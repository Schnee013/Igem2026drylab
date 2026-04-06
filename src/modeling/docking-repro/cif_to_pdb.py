"""
批量将 AF3 输出的 mmCIF 转为 PDB 格式

输入：experiments/docking-repro/mutagenesis/af3_structures/{RecName}/{Label}.cif
输出：experiments/docking-repro/mutagenesis/af3_structures/{RecName}/{Label}.pdb

用法：
    python cif_to_pdb.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

from Bio.PDB import MMCIFParser, PDBIO
from Bio.PDB.PDBExceptions import PDBConstructionWarning

STRUCTURES_DIR = Path("experiments/docking-repro/mutagenesis/af3_structures")


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


def main() -> None:
    cif_files = sorted(STRUCTURES_DIR.glob("*/*.cif"))
    print(f"找到 {len(cif_files)} 个 CIF 文件\n")

    for cif in cif_files:
        rec = cif.parent.name
        label = cif.stem
        pdb = convert_one(cif)
        print(f"  {rec}/{label}: {pdb.name}")

    print(f"\n转换完成，共 {len(cif_files)} 个 PDB 文件")


if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).resolve().parents[3])
    main()
