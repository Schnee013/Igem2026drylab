#!/usr/bin/env python3
"""Apply four frozen TM-align rigid-body transforms to full TWF154 PDBs."""

from pathlib import Path
import re


ALIGNMENT_ROOT = Path("/Users/yangruoxi/Projects/Docking-Research-Lab/alignment")

JOBS = (
    (
        "01_TWF154_Gpr2_vs_GprC",
        "inputs/structures/TWF154_Gpr2_TGJ68930.1_AF2.pdb",
        "TWF154_Gpr2_TGJ68930.1_full_transformed_to_GprC.pdb",
    ),
    (
        "02_TWF154_Gpr3_vs_GprC",
        "inputs/structures/TWF154_Gpr3_TGJ67963.1_AF2.pdb",
        "TWF154_Gpr3_TGJ67963.1_full_transformed_to_GprC.pdb",
    ),
    (
        "03_TWF154_Gpr2_vs_SRBC64",
        "inputs/structures/TWF154_Gpr2_TGJ68930.1_AF2.pdb",
        "TWF154_Gpr2_TGJ68930.1_full_transformed_to_SRBC64.pdb",
    ),
    (
        "04_TWF154_Gpr3_vs_SRBC64",
        "inputs/structures/TWF154_Gpr3_TGJ67963.1_AF2.pdb",
        "TWF154_Gpr3_TGJ67963.1_full_transformed_to_SRBC64.pdb",
    ),
)


def read_matrix(matrix_path: Path):
    rows = []
    for line in matrix_path.read_text().splitlines():
        if re.match(r"^\s*[012]\s+", line):
            fields = line.split()
            if len(fields) == 5:
                rows.append(tuple(float(value) for value in fields[1:]))
    if len(rows) != 3:
        raise ValueError(f"Expected three transform rows in {matrix_path}; found {len(rows)}")
    translation = tuple(row[0] for row in rows)
    rotation = tuple(tuple(row[index] for index in range(1, 4)) for row in rows)
    return translation, rotation


def transform_pdb(source: Path, matrix_path: Path, destination: Path):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {destination}")

    translation, rotation = read_matrix(matrix_path)
    output_lines = [
        f"REMARK 950 RIGID-BODY TRANSFORM FROM {matrix_path.name}\n",
        "REMARK 950 TM-ALIGN MATRIX APPLIED TO ALL ATOM AND HETATM COORDINATES\n",
    ]
    transformed_atoms = 0

    for line in source.read_text().splitlines(keepends=True):
        if line.startswith(("ATOM  ", "HETATM")) and len(line) >= 54:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coordinates = (x, y, z)
            transformed = tuple(
                translation[row]
                + sum(rotation[row][column] * coordinates[column] for column in range(3))
                for row in range(3)
            )
            line = (
                f"{line[:30]}"
                f"{transformed[0]:8.3f}{transformed[1]:8.3f}{transformed[2]:8.3f}"
                f"{line[54:]}"
            )
            transformed_atoms += 1
        output_lines.append(line)

    if transformed_atoms == 0:
        raise ValueError(f"No coordinates found in {source}")
    destination.write_text("".join(output_lines))
    return transformed_atoms


def main():
    for comparison_directory, source_relative, output_name in JOBS:
        result_directory = ALIGNMENT_ROOT / "alignments" / comparison_directory
        source = ALIGNMENT_ROOT / source_relative
        matrix = result_directory / "rotation_matrix.txt"
        destination = result_directory / output_name

        if not source.is_file():
            raise FileNotFoundError(f"Missing full structure: {source}")
        if not matrix.is_file():
            raise FileNotFoundError(f"Missing TM-align matrix: {matrix}")

        count = transform_pdb(source, matrix, destination)
        print(f"Created: {destination.name} ({count} transformed atoms)")


if __name__ == "__main__":
    main()
