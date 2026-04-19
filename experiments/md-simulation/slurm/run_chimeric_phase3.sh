#!/bin/bash
#SBATCH --job-name=chim_em_eq
#SBATCH --partition=gpu
#SBATCH --nodelist=node3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:rtx5090:1
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --output=phase3_%j.log
#SBATCH --error=phase3_%j.err

# Chimeric Gpa1 Phase C3: Energy Minimization + 6-step CHARMM-GUI Equilibration
#
# Usage: sbatch run_chimeric_phase3.sh <SYSTEM_DIR>
#
# Example:
#   sbatch run_chimeric_phase3.sh chimeric-gpr3-aogpa2-c37
#   sbatch run_chimeric_phase3.sh chimeric-ste2-gpa1-wt
#
# Input: CHARMM-GUI Membrane Builder output (step5_input.gro + topol.top + step6.*.mdp)
# Output: step6.6.gro (equilibrated structure ready for production)
#
# Differences from run_phase4.sh (mutant pipeline):
#   - No ligand assembly / genion steps (chimeric systems have no small-molecule ligand)
#   - Starts from step5_input.gro directly (not step5_mutant.gro)
#   - No step7 extended equilibration (goes straight to production)
#
# Pipeline context: chimeric-md-execution.md Phase C3

set -euo pipefail

SYSTEM=${1:?Usage: sbatch run_chimeric_phase3.sh <SYSTEM_DIR>}

WORK=$HOME/md-simulation/${SYSTEM}/gromacs
cd "$WORK" || exit 1

echo "=== Chimeric Phase C3: ${SYSTEM} ==="
echo "Working dir: $WORK"
echo "Started: $(date)"

# Load GROMACS (踩坑 #1/#2: spack load fails on compute nodes; GMXRC needs set +u)
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen4/gromacs-2025.2-v5xhhnf3iroo56vaxpp77aqr27xkkykx
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u
echo "GROMACS: $(gmx_mpi --version 2>&1 | head -1 || true)"

# ── Energy Minimization ──
echo ""
echo "=== Step 1: Energy Minimization ==="

INPUT_GRO="step5_input.gro"
if [ ! -f "$INPUT_GRO" ]; then
    echo "ERROR: $INPUT_GRO not found in $WORK"
    exit 1
fi

gmx_mpi grompp -f step6.0_minimization.mdp \
    -c "$INPUT_GRO" -r "$INPUT_GRO" \
    -p topol.top -n index.ndx \
    -o em.tpr -maxwarn 2

gmx_mpi mdrun -v -deffnm em -ntomp 16 -gpu_id 0

echo "EM final energy:"
tail -20 em.log | grep "Maximum force"

# ── 6-step Equilibration ──
echo ""
echo "=== Step 2: 6-step Equilibration ==="

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

    gmx_mpi mdrun -v -deffnm "step6.${STEP}" -ntomp 16 -gpu_id 0

    PREV_GRO="step6.${STEP}.gro"
    echo "Step $STEP done: $(date)"
done

# ── Verification ──
echo ""
echo "=== Verification ==="

if [ -f "step6.6.gro" ]; then
    echo "step6.6.gro exists"
else
    echo "ERROR: step6.6.gro not found — equilibration incomplete"
    exit 1
fi

echo ""
echo "=== Chimeric Phase C3 complete: ${SYSTEM} ==="
echo "Next: production MD (run_production.sh)"
echo "Finished: $(date)"
