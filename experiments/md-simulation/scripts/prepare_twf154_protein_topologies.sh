#!/usr/bin/env bash
# Build full-length protein topologies from explicitly selected frozen parents.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
export OMP_NUM_THREADS=1
shift
NAMES=("$@")
if (( ${#NAMES[@]} == 0 )); then
  NAMES=(raw_n84v raw_v368r rebuilt_n84v rebuilt_v368r)
fi
mkdir -p "$ROOT/inputs/protein_topologies02"
"$GMX" --version > "$ROOT/logs/gromacs_identity.txt" 2>&1
for name in "${NAMES[@]}"; do
  mkdir "$ROOT/inputs/protein_topologies02/$name"
  cd "$ROOT/inputs/protein_topologies02/$name"
  ln -s ../../charmm36-jul2022.ff charmm36-jul2022.ff
  # Uniform neutral delta-protonated histidine; record this model assumption.
  sed 's/ HIS / HSD /g' "../../matrix02/receptors/$name.pdb" > receptor_hsd.pdb
  printf '1\n0\n' > termini.inp
  "$GMX" pdb2gmx -f receptor_hsd.pdb -o protein.pdb -p protein.top \
    -i default_posre.itp -ff charmm36-jul2022 -water tip3p -ignh -ter \
    > pdb2gmx.log 2>&1 < termini.inp
  sha256sum receptor_hsd.pdb protein.pdb protein.top > topology.sha256
done
