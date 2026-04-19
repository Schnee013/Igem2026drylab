#!/bin/bash
#SBATCH --job-name=md_phase3
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:rtx4090:1
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=phase3_%j.log
#SBATCH --error=phase3_%j.err

# Usage: sbatch run_phase3.sh <SYSTEM> [REMOVE_POPC_RESID]
# e.g.:  sbatch run_phase3.sh Gpr2
#        sbatch run_phase3.sh Gpr3 514

set -euo pipefail

SYSTEM=${1:?Usage: sbatch run_phase3.sh <SYSTEM> [REMOVE_POPC_RESID]}
REMOVE_POPC=${2:-}

WORK=$HOME/md-simulation/${SYSTEM}_WT/gromacs
cd "$WORK" || exit 1

echo "=== Phase 3: ${SYSTEM} ==="
echo "Working dir: $WORK"
echo "Started: $(date)"

# Load GROMACS directly via GMXRC (spack broken on compute nodes)
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen2/gromacs-2025.2-3isv4kzjxtnsk32oq56gzceluac7k6uc
# GMXRC.bash reads many env vars that may be unset; disable nounset temporarily
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u
echo "GROMACS: $(gmx_mpi --version 2>&1 | head -1 || true)"

# ── Step 1: Assemble complex ──
echo ""
echo "=== Step 1: Assembly ==="
ASSEMBLE_ARGS="--system $SYSTEM --work-dir . --ligand ligand.gro"
if [ -n "$REMOVE_POPC" ]; then
    ASSEMBLE_ARGS="$ASSEMBLE_ARGS --remove-popc $REMOVE_POPC"
fi
python3 assemble_complex.py $ASSEMBLE_ARGS

# ── Step 2: Charge neutralization (genion) ──
echo ""
echo "=== Step 2: Genion (add 1 K+) ==="
# Use EM mdp for grompp (just need a tpr for genion)
gmx_mpi grompp -f step6.0_minimization.mdp \
    -c step5_complex.gro -r step5_complex.gro \
    -p topol.top -n index.ndx \
    -o genion.tpr -maxwarn 2

# Replace 1 TIP3 with K+. Group name must match moleculetype in topol.top
echo "TIP3" | gmx_mpi genion -s genion.tpr -p topol.top -n index.ndx \
    -o step5_complex_ion.gro -pname POT -np 1

# Rebuild index after genion
python3 assemble_complex.py --rebuild-index step5_complex_ion.gro

# ── Step 3: Energy Minimization ──
echo ""
echo "=== Step 3: Energy Minimization ==="
gmx_mpi grompp -f step6.0_minimization.mdp \
    -c step5_complex_ion.gro -r step5_complex_ion.gro \
    -p topol.top -n index.ndx \
    -o em.tpr -maxwarn 2

gmx_mpi mdrun -v -deffnm em -ntomp 8 -gpu_id 0

# Check EM convergence
echo "EM final energy:"
tail -20 em.log | grep "Maximum force"

# ── Step 4: 6-step Equilibration ──
echo ""
echo "=== Step 4: Equilibration ==="

PREV_GRO="em.gro"
REF_GRO="em.gro"

for STEP in 1 2 3 4 5 6; do
    MDP="step6.${STEP}_equilibration.mdp"
    if [ ! -f "$MDP" ]; then
        echo "WARNING: $MDP not found, skipping step $STEP"
        continue
    fi

    echo ""
    echo "--- Equilibration step $STEP ---"
    gmx_mpi grompp -f "$MDP" \
        -c "$PREV_GRO" -r "$REF_GRO" \
        -p topol.top -n index.ndx \
        -o "step6.${STEP}.tpr" -maxwarn 2

    gmx_mpi mdrun -v -deffnm "step6.${STEP}" -ntomp 8 -gpu_id 0

    PREV_GRO="step6.${STEP}.gro"
    echo "Step $STEP done: $(date)"
done

echo ""
echo "=== Phase 3 complete ==="
echo "Final structure: step6.6.gro"
echo "Finished: $(date)"
