#!/bin/bash
# Narrow redock for missing Phase 6 IFP pose artifacts only.

#SBATCH --job-name=ifp_pose_redock
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=ifp_missing_pose_redock_%j.log
#SBATCH --error=ifp_missing_pose_redock_%j.err

set -euo pipefail

cd /home/guest/drylab-docking
export PATH="/home/guest/bin:${PATH}"
export PYTHONPATH="/home/guest/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}"
export VINA_CPU="${SLURM_CPUS_PER_TASK:-8}"

if [[ -f experiments/docking-repro/slurm/adfr_env.sh ]]; then
  source experiments/docking-repro/slurm/adfr_env.sh
fi

mkdir -p experiments/docking-repro/mutagenesis/af3_prepared/GprC
if [[ ! -f experiments/docking-repro/mutagenesis/af3_prepared/GprC/Q411S_tm.pdbqt ]]; then
  prepare_receptor \
    -r experiments/docking-repro/mutagenesis/af3_structures/GprC/Q411S_tm.pdb \
    -o experiments/docking-repro/mutagenesis/af3_prepared/GprC/Q411S_tm.pdbqt \
    -A hydrogens \
    -U nphs_lps_waters_nonstdres
fi

python3 - <<'PY'
from pathlib import Path

from dock import (
    dock_pair_singlestage,
    get_box_center_offset,
    get_manual_box_center,
    get_receptor_box_size,
    get_tm_helix_ranges,
)
from utils import load_config

root = Path("/home/guest/drylab-docking")
config = load_config(root / "src/modeling/docking-repro/config.yaml")
config["paths"]["project_root"] = str(root)
config["remote"]["vina_bin"] = "/home/guest/bin/vina"

jobs = [
    ("Gpr2", "R59C"),
    ("Gpr2", "R59T"),
    ("GprC", "Q411S"),
]
ligands = ["ascr18", "ascr3"]

for rec_name, label in jobs:
    rec_cfg = config["receptors"][rec_name]
    tm_pdb = root / config["paths"]["prepared_dir"] / "receptors" / f"{Path(rec_cfg['pdb_file']).stem}_tm.pdb"
    receptor_pdbqt = root / config["paths"]["mutagenesis_dir"] / "af3_prepared" / rec_name / f"{label}_tm.pdbqt"
    helix_ranges = get_tm_helix_ranges(config, rec_name)
    box_offset = get_box_center_offset(config, rec_name)
    rec_box_size = get_receptor_box_size(config, rec_name)
    manual_center = get_manual_box_center(config, rec_name)

    for lig_name in ligands:
        ligand_pdbqt = root / config["paths"]["prepared_dir"] / "ligands" / f"{lig_name}_optimized.pdbqt"
        out_dir = root / "experiments/docking-repro/results/ifp_missing_pose_redock_20260520" / rec_name / label / "docking"
        pair_name = f"{rec_name}_{label}_{lig_name}"
        result = dock_pair_singlestage(
            receptor_pdbqt=receptor_pdbqt,
            ligand_pdbqt=ligand_pdbqt,
            pair_name=pair_name,
            tm_pdb=tm_pdb,
            output_dir=out_dir,
            config=config,
            tm_helix_ranges=helix_ranges,
            box_center_offset=box_offset,
            receptor_box_size=rec_box_size,
            manual_box_center=manual_center,
        )
        print(f"{pair_name}\t{result.best_affinity:.3f}\t{result.poses_path}")
PY
