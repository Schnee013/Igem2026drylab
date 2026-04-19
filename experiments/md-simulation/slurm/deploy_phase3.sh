#!/bin/bash
# Deploy Phase 3 files to Slurm server and submit jobs.
#
# Usage: bash experiments/md-simulation/slurm/deploy_phase3.sh
#
# Prerequisites:
#   - SSH config for 10.40.4.5 already set up
#   - Ligand GRO files generated (prepare_ligand_gro.py)
#   - CGenFF delta files generated (generate_cgenff_delta.py)

set -euo pipefail

SERVER="guest@10.40.4.5"
LOCAL_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
REMOTE_BASE="~/md-simulation"

echo "=== Phase 3 Deployment ==="
echo "Local root: $LOCAL_ROOT"
echo ""

# ── Create remote directories ──
echo "Creating remote directories..."
ssh "$SERVER" "mkdir -p $REMOTE_BASE/Gpr2_WT/gromacs/toppar $REMOTE_BASE/Gpr3_WT/gromacs/toppar"

# ── Deploy Gpr2_WT ──
echo ""
echo "--- Deploying Gpr2_WT ---"
LOCAL_GPR2="$LOCAL_ROOT/experiments/md-simulation/systems/Gpr2_WT/gromacs"
REMOTE_GPR2="$REMOTE_BASE/Gpr2_WT/gromacs"

# Core system files
scp "$LOCAL_GPR2/step5_input.gro" "$SERVER:$REMOTE_GPR2/"
scp "$LOCAL_GPR2/topol.top" "$SERVER:$REMOTE_GPR2/"
scp "$LOCAL_GPR2"/step6.*.mdp "$SERVER:$REMOTE_GPR2/"
scp -r "$LOCAL_GPR2/toppar/" "$SERVER:$REMOTE_GPR2/"

# Ligand files
scp "$LOCAL_ROOT/experiments/md-simulation/structures/docking_poses/Gpr2_ASCR18_aligned.gro" \
    "$SERVER:$REMOTE_GPR2/ligand.gro"
scp "$LOCAL_GPR2/ASCR18.itp" "$SERVER:$REMOTE_GPR2/"
scp "$LOCAL_GPR2/posre_ASCR18.itp" "$SERVER:$REMOTE_GPR2/"

# Scripts
scp "$LOCAL_ROOT/experiments/md-simulation/scripts/assemble_complex.py" "$SERVER:$REMOTE_GPR2/"
scp "$LOCAL_ROOT/experiments/md-simulation/slurm/run_phase3.sh" "$SERVER:$REMOTE_GPR2/"

echo "Gpr2_WT deployed."

# ── Deploy Gpr3_WT ──
echo ""
echo "--- Deploying Gpr3_WT ---"
LOCAL_GPR3="$LOCAL_ROOT/experiments/md-simulation/systems/Gpr3_WT/gromacs"
REMOTE_GPR3="$REMOTE_BASE/Gpr3_WT/gromacs"

scp "$LOCAL_GPR3/step5_input.gro" "$SERVER:$REMOTE_GPR3/"
scp "$LOCAL_GPR3/topol.top" "$SERVER:$REMOTE_GPR3/"
scp "$LOCAL_GPR3"/step6.*.mdp "$SERVER:$REMOTE_GPR3/"
scp -r "$LOCAL_GPR3/toppar/" "$SERVER:$REMOTE_GPR3/"

scp "$LOCAL_ROOT/experiments/md-simulation/structures/docking_poses/Gpr3_ASCR18_aligned.gro" \
    "$SERVER:$REMOTE_GPR3/ligand.gro"
scp "$LOCAL_GPR3/ASCR18.itp" "$SERVER:$REMOTE_GPR3/"
scp "$LOCAL_GPR3/posre_ASCR18.itp" "$SERVER:$REMOTE_GPR3/"

scp "$LOCAL_ROOT/experiments/md-simulation/scripts/assemble_complex.py" "$SERVER:$REMOTE_GPR3/"
scp "$LOCAL_ROOT/experiments/md-simulation/slurm/run_phase3.sh" "$SERVER:$REMOTE_GPR3/"

echo "Gpr3_WT deployed."

# ── Summary ──
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To submit jobs, SSH to server and run:"
echo ""
echo "  # Gpr2 (no POPC collision)"
echo "  cd $REMOTE_BASE/Gpr2_WT/gromacs"
echo "  sbatch run_phase3.sh Gpr2"
echo ""
echo "  # Gpr3 (remove POPC resid 514)"
echo "  cd $REMOTE_BASE/Gpr3_WT/gromacs"
echo "  sbatch run_phase3.sh Gpr3 514"
echo ""
echo "Monitor: squeue -u \$USER"
