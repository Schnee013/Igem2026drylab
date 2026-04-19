#!/bin/bash
# Deploy chimeric Gpa1 systems to Slurm server.
#
# Usage: bash experiments/md-simulation/slurm/deploy_chimeric.sh [SYSTEM ...]
#   No args = deploy all 4 core systems
#   With args = deploy only specified systems
#
# Examples:
#   bash experiments/md-simulation/slurm/deploy_chimeric.sh
#   bash experiments/md-simulation/slurm/deploy_chimeric.sh chimeric-gpr3-aogpa2-c37
#
# Prerequisites:
#   - CHARMM-GUI Membrane Builder output in systems/<name>/gromacs/
#
# Pipeline context: chimeric-md-execution.md Phase C3

set -euo pipefail

SERVER="guest@10.40.4.5"
LOCAL_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
REMOTE_BASE="~/md-simulation"
SYSTEMS_DIR="$LOCAL_ROOT/experiments/md-simulation/systems"
SLURM_DIR="$LOCAL_ROOT/experiments/md-simulation/slurm"

# Core chimeric systems (local dir name = remote dir name)
CORE_SYSTEMS=(
    "chimeric-gpr3-aogpa2-c37"
    "chimeric-gpr3-aogpa2-c15"
    "chimeric-gpr2-aogpa2-c10"
    "chimeric-ste2-gpa1-wt"
)

echo "=== Chimeric Gpa1 Deployment ==="
echo "Local root: $LOCAL_ROOT"
echo ""

# Determine which systems to deploy
if [ $# -gt 0 ]; then
    TARGETS=("$@")
else
    TARGETS=("${CORE_SYSTEMS[@]}")
fi

echo "Systems to deploy: ${TARGETS[*]}"
echo ""

deploy_system() {
    local SYSTEM="$1"
    local GROMACS_DIR="$SYSTEMS_DIR/$SYSTEM/gromacs"
    local REMOTE_DIR="$REMOTE_BASE/$SYSTEM/gromacs"

    echo "--- Deploying $SYSTEM ---"
    echo "  Local: $GROMACS_DIR"
    echo "  Remote: $REMOTE_DIR"

    # Verify local files exist
    if [ ! -f "$GROMACS_DIR/step5_input.gro" ]; then
        echo "  WARNING: step5_input.gro not found — skipping (CHARMM-GUI not yet done?)"
        return 0
    fi

    # Create remote directory
    ssh "$SERVER" "mkdir -p $REMOTE_DIR/toppar"

    # Core CHARMM-GUI files (no ligand files for chimeric systems)
    scp "$GROMACS_DIR/step5_input.gro" "$SERVER:$REMOTE_DIR/"
    scp "$GROMACS_DIR/topol.top" "$SERVER:$REMOTE_DIR/"
    scp "$GROMACS_DIR/index.ndx" "$SERVER:$REMOTE_DIR/" 2>/dev/null || true
    scp -r "$GROMACS_DIR/toppar/" "$SERVER:$REMOTE_DIR/"

    # MDP files (EM + 6-step eq from CHARMM-GUI)
    scp "$GROMACS_DIR"/step6*.mdp "$SERVER:$REMOTE_DIR/"

    # SLURM scripts
    scp "$SLURM_DIR/run_chimeric_phase3.sh" "$SERVER:$REMOTE_DIR/"
    scp "$SLURM_DIR/run_production.sh" "$SERVER:$REMOTE_DIR/"

    echo "  $SYSTEM deployed."
    echo ""
}

for TARGET in "${TARGETS[@]}"; do
    deploy_system "$TARGET"
done

echo "=== Deployment Complete ==="
echo ""
echo "Submit Phase C3 jobs on server:"
echo ""

for TARGET in "${TARGETS[@]}"; do
    echo "  cd $REMOTE_BASE/$TARGET/gromacs"
    echo "  sbatch run_chimeric_phase3.sh $TARGET"
    echo ""
done

echo "After Phase C3 completes, submit production:"
echo ""
echo "  # Example: 500 ns, 3 replicas"
echo "  for REP in 1 2 3; do"
echo "    sbatch run_production.sh <SYSTEM> 500 \$REP"
echo "  done"
echo ""
echo "Monitor: squeue -u \$USER"
