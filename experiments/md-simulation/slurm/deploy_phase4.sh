#!/bin/bash
# Deploy Phase 4 mutant systems to Slurm server.
#
# Usage: bash experiments/md-simulation/slurm/deploy_phase4.sh [SYSTEM ...]
#   No args = deploy all assembled systems
#   With args = deploy only specified systems (e.g., Gpr3_F170E Gpr2_M327A)
#
# Prerequisites:
#   - mutate_system.py has been run for each in-place mutant
#   - V138R system assembled via CHARMM-GUI Membrane Builder + assemble_complex.py
#   - step7_extended_eq.mdp exists in mdp/

set -euo pipefail

SERVER="guest@10.40.4.5"
LOCAL_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
REMOTE_BASE="~/md-simulation"
SYSTEMS_DIR="$LOCAL_ROOT/experiments/md-simulation/systems"
SLURM_DIR="$LOCAL_ROOT/experiments/md-simulation/slurm"
SCRIPTS_DIR="$LOCAL_ROOT/experiments/md-simulation/scripts"
MDP_DIR="$LOCAL_ROOT/experiments/md-simulation/mdp"

# System mapping: local_dir -> remote_dir
declare -A SYSTEM_MAP=(
    ["gpr3-V138R-ascr18"]="Gpr3_V138R"
    ["gpr3-F170E-ascr18"]="Gpr3_F170E"
    ["gpr3-I141A-ascr18"]="Gpr3_I141A"
    ["gpr2-M327A-ascr18"]="Gpr2_M327A"
    ["gpr2-M327D-ascr18"]="Gpr2_M327D"
    ["gpr2-R59F-ascr18"]="Gpr2_R59F"
)

# Genion requirements per system
declare -A GENION_ARGS=(
    ["Gpr3_V138R"]="--genion nn 1"
    ["Gpr3_F170E"]="--genion np 1"
    ["Gpr3_I141A"]=""
    ["Gpr2_M327A"]=""
    ["Gpr2_M327D"]="--genion np 1"
    ["Gpr2_R59F"]="--genion np 1"
)

echo "=== Phase 4 Deployment ==="
echo "Local root: $LOCAL_ROOT"
echo ""

# Determine which systems to deploy
if [ $# -gt 0 ]; then
    TARGETS=("$@")
else
    TARGETS=()
    for local_dir in "${!SYSTEM_MAP[@]}"; do
        gromacs_dir="$SYSTEMS_DIR/$local_dir/gromacs"
        if [ -f "$gromacs_dir/step5_mutant.gro" ] || [ -f "$gromacs_dir/step5_input.gro" ]; then
            TARGETS+=("${SYSTEM_MAP[$local_dir]}")
        fi
    done
fi

if [ ${#TARGETS[@]} -eq 0 ]; then
    echo "No assembled systems found. Run mutate_system.py first."
    exit 1
fi

echo "Systems to deploy: ${TARGETS[*]}"
echo ""

deploy_system() {
    local REMOTE_NAME="$1"
    local LOCAL_DIR=""

    # Find local directory for this remote name
    for local_dir in "${!SYSTEM_MAP[@]}"; do
        if [ "${SYSTEM_MAP[$local_dir]}" = "$REMOTE_NAME" ]; then
            LOCAL_DIR="$local_dir"
            break
        fi
    done

    if [ -z "$LOCAL_DIR" ]; then
        echo "ERROR: no local directory for $REMOTE_NAME"
        return 1
    fi

    local GROMACS_DIR="$SYSTEMS_DIR/$LOCAL_DIR/gromacs"
    local REMOTE_DIR="$REMOTE_BASE/$REMOTE_NAME/gromacs"

    echo "--- Deploying $REMOTE_NAME ---"
    echo "  Local: $GROMACS_DIR"
    echo "  Remote: $REMOTE_DIR"

    # Create remote directory
    ssh "$SERVER" "mkdir -p $REMOTE_DIR/toppar"

    # Core system files
    if [ -f "$GROMACS_DIR/step5_mutant.gro" ]; then
        scp "$GROMACS_DIR/step5_mutant.gro" "$SERVER:$REMOTE_DIR/"
    elif [ -f "$GROMACS_DIR/step5_input.gro" ]; then
        # V138R rebuild: uses step5_input.gro like Phase 3
        scp "$GROMACS_DIR/step5_input.gro" "$SERVER:$REMOTE_DIR/"
    fi

    scp "$GROMACS_DIR/topol.top" "$SERVER:$REMOTE_DIR/"
    scp "$GROMACS_DIR/index.ndx" "$SERVER:$REMOTE_DIR/" 2>/dev/null || true
    scp -r "$GROMACS_DIR/toppar/" "$SERVER:$REMOTE_DIR/"

    # MDP files
    scp "$GROMACS_DIR"/step6*.mdp "$SERVER:$REMOTE_DIR/"
    scp "$MDP_DIR/step7_extended_eq.mdp" "$SERVER:$REMOTE_DIR/"

    # Ligand files
    scp "$GROMACS_DIR/ASCR18.itp" "$SERVER:$REMOTE_DIR/"
    scp "$GROMACS_DIR/posre_ASCR18.itp" "$SERVER:$REMOTE_DIR/"

    # Scripts
    scp "$SCRIPTS_DIR/assemble_complex.py" "$SERVER:$REMOTE_DIR/"
    scp "$SLURM_DIR/run_phase4.sh" "$SERVER:$REMOTE_DIR/"

    echo "  $REMOTE_NAME deployed."
    echo ""
}

for TARGET in "${TARGETS[@]}"; do
    deploy_system "$TARGET"
done

# Deploy step7 MDP to WT systems for extended eq
echo "--- Deploying step7_extended_eq.mdp to WT systems ---"
for WT in Gpr2_WT Gpr3_WT; do
    scp "$MDP_DIR/step7_extended_eq.mdp" "$SERVER:$REMOTE_BASE/$WT/gromacs/"
    echo "  $WT: step7_extended_eq.mdp deployed"
done
scp "$SLURM_DIR/run_phase4.sh" "$SERVER:$REMOTE_BASE/Gpr2_WT/gromacs/"
scp "$SLURM_DIR/run_phase4.sh" "$SERVER:$REMOTE_BASE/Gpr3_WT/gromacs/"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Submit jobs on server:"
echo ""

for TARGET in "${TARGETS[@]}"; do
    GENION="${GENION_ARGS[$TARGET]:-}"
    echo "  cd $REMOTE_BASE/$TARGET/gromacs"
    echo "  sbatch run_phase4.sh $TARGET $GENION"
    echo ""
done

echo "  # WT extended eq (step7-only):"
echo "  cd $REMOTE_BASE/Gpr2_WT/gromacs && sbatch run_phase4.sh Gpr2_WT --step7-only"
echo "  cd $REMOTE_BASE/Gpr3_WT/gromacs && sbatch run_phase4.sh Gpr3_WT --step7-only"
echo ""
echo "Monitor: squeue -u \$USER"
