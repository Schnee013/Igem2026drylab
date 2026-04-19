#!/bin/bash
#SBATCH --job-name=md_phase4
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:rtx5090:1
#SBATCH --mem=128G
#SBATCH --time=72:00:00
#SBATCH --output=phase4_%j.log
#SBATCH --error=phase4_%j.err

# Usage: sbatch run_phase4.sh <SYSTEM_DIR> [OPTIONS]
#
# Modes:
#   Full pipeline (mutants):
#     sbatch run_phase4.sh Gpr3_F170E
#     sbatch run_phase4.sh Gpr3_F170E --genion np 1    # add 1 POT
#     sbatch run_phase4.sh Gpr3_V138R --genion nn 1    # add 1 CLA
#
#   Step7-only (WT extended eq):
#     sbatch run_phase4.sh Gpr2_WT --step7-only
#
# Input structure: step5_mutant.gro (full pipeline) or step6.6.gro (step7-only)

set -euo pipefail

SYSTEM=${1:?Usage: sbatch run_phase4.sh <SYSTEM_DIR> [--genion np|nn N] [--step7-only]}
shift

# Parse options
GENION_TYPE=""
GENION_COUNT=0
STEP7_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --genion)
            GENION_TYPE="$2"
            GENION_COUNT="$3"
            shift 3
            ;;
        --step7-only)
            STEP7_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

WORK=$HOME/md-simulation/${SYSTEM}/gromacs
cd "$WORK" || exit 1

echo "=== Phase 4: ${SYSTEM} ==="
echo "Working dir: $WORK"
echo "Mode: $(if $STEP7_ONLY; then echo 'step7-only'; else echo 'full pipeline'; fi)"
echo "Started: $(date)"

# Load GROMACS
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen2/gromacs-2025.2-3isv4kzjxtnsk32oq56gzceluac7k6uc
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u
echo "GROMACS: $(gmx_mpi --version 2>&1 | head -1 || true)"

if $STEP7_ONLY; then
    # ── Step7-only mode: run extended eq from step6.6.gro ──
    echo ""
    echo "=== Step 7: Extended equilibration (20 ns) ==="
    gmx_mpi grompp -f step7_extended_eq.mdp \
        -c step6.6.gro -r em.gro \
        -p topol.top -n index.ndx \
        -o step7.tpr -maxwarn 2

    gmx_mpi mdrun -v -deffnm step7 -ntomp 16 -gpu_id 0

    echo ""
    echo "=== Step 7 complete ==="
    echo "Final structure: step7.gro"
    echo "Finished: $(date)"
    exit 0
fi

# ── Full pipeline mode ──

INPUT_GRO="step5_mutant.gro"

# ── Step 1: Genion (conditional) ──
if [ -n "$GENION_TYPE" ] && [ "$GENION_COUNT" -gt 0 ]; then
    echo ""
    echo "=== Step 1: Genion (${GENION_TYPE} x${GENION_COUNT}) ==="
    gmx_mpi grompp -f step6.0_minimization.mdp \
        -c "$INPUT_GRO" -r "$INPUT_GRO" \
        -p topol.top -n index.ndx \
        -o genion.tpr -maxwarn 2

    GENION_ARGS=""
    if [ "$GENION_TYPE" = "np" ]; then
        GENION_ARGS="-pname POT -np $GENION_COUNT"
    elif [ "$GENION_TYPE" = "nn" ]; then
        GENION_ARGS="-nname CLA -nn $GENION_COUNT"
    else
        echo "ERROR: genion type must be 'np' or 'nn', got '$GENION_TYPE'"
        exit 1
    fi

    echo "TIP3" | gmx_mpi genion -s genion.tpr -p topol.top -n index.ndx \
        -o step5_mutant_ion.gro $GENION_ARGS

    # Rebuild index after genion (Phase 3 lesson #6)
    python3 assemble_complex.py --rebuild-index step5_mutant_ion.gro

    INPUT_GRO="step5_mutant_ion.gro"
fi

# ── Step 2: Energy Minimization ──
echo ""
echo "=== Step 2: Energy Minimization ==="
gmx_mpi grompp -f step6.0_minimization.mdp \
    -c "$INPUT_GRO" -r "$INPUT_GRO" \
    -p topol.top -n index.ndx \
    -o em.tpr -maxwarn 2

gmx_mpi mdrun -v -deffnm em -ntomp 16 -gpu_id 0

echo "EM final energy:"
tail -20 em.log | grep "Maximum force"

# ── Step 3: 6-step Equilibration ──
echo ""
echo "=== Step 3: 6-step Equilibration ==="

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

# ── Step 4: Extended Equilibration (20 ns) ──
echo ""
echo "=== Step 4: Extended Equilibration (20 ns) ==="
gmx_mpi grompp -f step7_extended_eq.mdp \
    -c step6.6.gro -r em.gro \
    -p topol.top -n index.ndx \
    -o step7.tpr -maxwarn 2

gmx_mpi mdrun -v -deffnm step7 -ntomp 16 -gpu_id 0

echo ""
echo "=== Phase 4 complete ==="
echo "Final structure: step7.gro"
echo "Finished: $(date)"
