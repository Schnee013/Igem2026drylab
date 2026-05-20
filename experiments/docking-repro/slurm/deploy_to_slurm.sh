#!/bin/bash
# Deploy docking-repro code and required inputs from Mac to the Slurm workspace.
# Usage: bash experiments/docking-repro/slurm/deploy_to_slurm.sh

set -euo pipefail

SERVER="${SERVER:-guest@10.40.4.5}"
REMOTE_DIR="${REMOTE_DIR:-/home/guest/drylab-docking}"
LOCAL_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
RSYNC_OPTS=(-az --exclude ".DS_Store")

echo "=== Step 1: create remote directory structure ==="
ssh "$SERVER" "mkdir -p \
	  '$REMOTE_DIR/src/modeling/docking-repro' \
	  '$REMOTE_DIR/experiments/docking-repro/prepared' \
	  '$REMOTE_DIR/experiments/docking-repro/results/wt_singlestage' \
	  '$REMOTE_DIR/experiments/docking-repro/results/wt_singlestage_gpr3_f_test' \
	  '$REMOTE_DIR/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation' \
  '$REMOTE_DIR/experiments/docking-repro/mutagenesis/af3_structures/Gpr3' \
  '$REMOTE_DIR/experiments/docking-repro/mutagenesis/af3_prepared/Gpr3' \
  '$REMOTE_DIR/experiments/docking-repro/logs' \
  '$REMOTE_DIR/experiments/docking-repro/slurm'"

echo "=== Step 2: sync docking-repro source code ==="
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/src/modeling/docking-repro/" \
  "$SERVER:$REMOTE_DIR/src/modeling/docking-repro/"

echo "=== Step 3: sync prepared WT receptors and ligands ==="
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/prepared/" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/prepared/"

echo "=== Step 4: sync WT baseline results ==="
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/results/wt_singlestage/" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/results/wt_singlestage/"
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/results/wt_singlestage_gpr3_f_test/" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/results/wt_singlestage_gpr3_f_test/"

echo "=== Step 5: sync Gpr3 supplemental AF3 structures and batch JSONs ==="
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/mutagenesis/af3_structures/Gpr3/" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/mutagenesis/af3_structures/Gpr3/"
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_"*.json \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/"
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/mutagenesis/af3_import_manifest_20260519.md" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/mutagenesis/"

echo "=== Step 6: sync Slurm scripts ==="
rsync "${RSYNC_OPTS[@]}" \
  "$LOCAL_ROOT/experiments/docking-repro/slurm/" \
  "$SERVER:$REMOTE_DIR/experiments/docking-repro/slurm/"

echo "=== Deploy complete ==="
echo "Remote workspace: $SERVER:$REMOTE_DIR"
echo "Next:"
echo "  ssh $SERVER 'cd $REMOTE_DIR && sbatch experiments/docking-repro/slurm/docking_preflight.sh'"
