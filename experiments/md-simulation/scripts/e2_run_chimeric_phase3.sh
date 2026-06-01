#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: e2_run_chimeric_phase3.sh SYSTEM...

Rebuild chimeric Phase C3 on E2 from local CHARMM-GUI/GROMACS inputs:
  step5_input.gro topol.top index.ndx step6.*.mdp toppar/

Outputs are written on E2 under:
  /ifs1/User/dengwei/igem/md-simulation/<system>/gromacs/

Environment:
  REMOTE=nkuliulab-e2
  E2_BASE=/ifs1/User/dengwei/igem
  REMOTE_MD_BASE=$E2_BASE/md-simulation
  SYSTEM_ROOT=experiments/md-simulation/systems
  E2_THREADS=24
  GMX_EM_MDRUN_FLAGS="-nb cpu -pme cpu -bonded cpu"
  GMX_MDRUN_FLAGS="-nb gpu -pme gpu -bonded gpu"
  MAXWARN=2
  E2_PHASE3_ALLOW_OVERWRITE=0
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

REMOTE=${REMOTE:-nkuliulab-e2}
E2_BASE=${E2_BASE:-/ifs1/User/dengwei/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$E2_BASE/md-simulation}
RSYNC_RSH=${RSYNC_RSH:-ssh ${E2_SSH_OPTS:-}}
SYSTEM_ROOT=${SYSTEM_ROOT:-experiments/md-simulation/systems}
E2_THREADS=${E2_THREADS:-24}
GMX_EM_MDRUN_FLAGS=${GMX_EM_MDRUN_FLAGS:--nb cpu -pme cpu -bonded cpu}
GMX_MDRUN_FLAGS=${GMX_MDRUN_FLAGS:--nb gpu -pme gpu -bonded gpu}
MAXWARN=${MAXWARN:-2}
E2_PHASE3_ALLOW_OVERWRITE=${E2_PHASE3_ALLOW_OVERWRITE:-0}
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}

SSH_OPTS_ARR=()
if [[ -n "${E2_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$E2_SSH_OPTS"
  SSH_CMD=(ssh "${SSH_OPTS_ARR[@]}")
else
  SSH_CMD=(ssh)
fi
shopt -s nullglob

for system in "$@"; do
  gmx_dir="$SYSTEM_ROOT/$system/gromacs"
  remote_dir="$REMOTE_MD_BASE/$system/gromacs"
  manifest=$(mktemp)
  trap 'rm -f "$manifest"' EXIT

  echo "[phase3] auditing source inputs: $system"
  if [[ ! -d "$gmx_dir" ]]; then
    echo "ERROR: missing local gromacs directory: $gmx_dir" >&2
    exit 1
  fi

  required_files=(
    "$gmx_dir/step5_input.gro"
    "$gmx_dir/topol.top"
    "$gmx_dir/index.ndx"
    "$gmx_dir/step6.0_minimization.mdp"
    "$gmx_dir/step6.1_equilibration.mdp"
    "$gmx_dir/step6.2_equilibration.mdp"
    "$gmx_dir/step6.3_equilibration.mdp"
    "$gmx_dir/step6.4_equilibration.mdp"
    "$gmx_dir/step6.5_equilibration.mdp"
    "$gmx_dir/step6.6_equilibration.mdp"
  )
  for path in "${required_files[@]}"; do
    if [[ ! -s "$path" ]]; then
      echo "ERROR: required Phase C3 input is missing or empty: $path" >&2
      exit 1
    fi
  done
  if [[ ! -d "$gmx_dir/toppar" ]] || ! find "$gmx_dir/toppar" -type f -print -quit | grep -q .; then
    echo "ERROR: missing or empty topology directory: $gmx_dir/toppar" >&2
    exit 1
  fi

  {
    echo "# Phase C3 source manifest for $system"
    echo "# generated $RUN_ID on $(hostname)"
    (
      cd "$gmx_dir"
      files=(README topol.top index.ndx step5_input.gro step5_input.pdb step5_input.psf)
      files+=(step6.*.mdp)
      for file in "${files[@]}"; do
        [[ -f "$file" ]] && shasum -a 256 "$file"
      done
      find toppar -type f -print | sort | while read -r file; do
        shasum -a 256 "$file"
      done
    )
  } > "$manifest"

  echo "[phase3] syncing source inputs to $REMOTE:$remote_dir"
  "${SSH_CMD[@]}" "$REMOTE" "mkdir -p '$remote_dir'"

  sync_files=(
    "$gmx_dir/topol.top"
    "$gmx_dir/index.ndx"
    "$gmx_dir/step5_input.gro"
    "$gmx_dir"/step6.*.mdp
  )
  optional_files=(
    "$gmx_dir"/README
    "$gmx_dir"/step5_input.pdb
    "$gmx_dir"/step5_input.psf
  )
  for path in "${optional_files[@]}"; do
    [[ -f "$path" ]] && sync_files+=("$path")
  done

  rsync -avP -e "$RSYNC_RSH" "${sync_files[@]}" "$REMOTE:$remote_dir/"
  rsync -avP -e "$RSYNC_RSH" "$gmx_dir/toppar/" "$REMOTE:$remote_dir/toppar/"
  rsync -avP -e "$RSYNC_RSH" "$manifest" "$REMOTE:$remote_dir/phase3_source_manifest_${RUN_ID}.sha256"
  rm -f "$manifest"
  trap - EXIT

  echo "[phase3] running E2 Phase C3: $system"
  "${SSH_CMD[@]}" "$REMOTE" \
    "SYSTEM='$system' REMOTE_MD_BASE='$REMOTE_MD_BASE' REMOTE_DIR='$remote_dir' E2_THREADS='$E2_THREADS' GMX_EM_MDRUN_FLAGS='$GMX_EM_MDRUN_FLAGS' GMX_MDRUN_FLAGS='$GMX_MDRUN_FLAGS' MAXWARN='$MAXWARN' E2_PHASE3_ALLOW_OVERWRITE='$E2_PHASE3_ALLOW_OVERWRITE' RUN_ID='$RUN_ID' bash -s" <<'REMOTE_SCRIPT'
set -euo pipefail

GMX_ENV="$REMOTE_MD_BASE/.chimeric_gmx.env"
if [[ -f "$GMX_ENV" ]]; then
  set +u
  source "$GMX_ENV"
  set -u
fi
if [[ -z "${GMX_CMD:-}" ]]; then
  echo "ERROR: missing preflight-selected GROMACS command: $GMX_ENV" >&2
  exit 1
fi
read -r -a GMX_ARR <<< "$GMX_CMD"
read -r -a EM_MDRUN_FLAGS_ARR <<< "$GMX_EM_MDRUN_FLAGS"
read -r -a MDRUN_FLAGS_ARR <<< "$GMX_MDRUN_FLAGS"

cd "$REMOTE_DIR"
if [[ "$E2_PHASE3_ALLOW_OVERWRITE" != "1" ]]; then
  for existing in em.tpr em.log em.cpt em.gro step6.6.tpr step6.6.log step6.6.cpt step6.6.gro; do
    if [[ -e "$existing" ]]; then
      echo "ERROR: $existing already exists in $REMOTE_DIR; set E2_PHASE3_ALLOW_OVERWRITE=1 only after auditing." >&2
      exit 1
    fi
  done
fi

{
  echo "=== E2 Chimeric Phase C3: $SYSTEM ==="
  echo "run_id=$RUN_ID"
  echo "started=$(date -Is)"
  echo "working_dir=$REMOTE_DIR"
  echo "gromacs=$GMX_CMD"
  "${GMX_ARR[@]}" --version

  echo
  echo "=== Step 1: Energy Minimization ==="
  "${GMX_ARR[@]}" grompp \
    -f step6.0_minimization.mdp \
    -c step5_input.gro \
    -r step5_input.gro \
    -p topol.top \
    -n index.ndx \
    -o em.tpr \
    -po em_out.mdp \
    -maxwarn "$MAXWARN"
  OMP_NUM_THREADS="$E2_THREADS" "${GMX_ARR[@]}" mdrun \
    -deffnm em \
    -ntomp "$E2_THREADS" \
    -pin on \
    "${EM_MDRUN_FLAGS_ARR[@]}"

  prev_gro=em.gro
  ref_gro=em.gro
  echo
  echo "=== Step 2: 6-step Equilibration ==="
  for step in 1 2 3 4 5 6; do
    mdp="step6.${step}_equilibration.mdp"
    echo
    echo "--- Equilibration step $step ---"
    "${GMX_ARR[@]}" grompp \
      -f "$mdp" \
      -c "$prev_gro" \
      -r "$ref_gro" \
      -p topol.top \
      -n index.ndx \
      -o "step6.${step}.tpr" \
      -po "step6.${step}_out.mdp" \
      -maxwarn "$MAXWARN"
    OMP_NUM_THREADS="$E2_THREADS" "${GMX_ARR[@]}" mdrun \
      -deffnm "step6.${step}" \
      -ntomp "$E2_THREADS" \
      -pin on \
      "${MDRUN_FLAGS_ARR[@]}"
    prev_gro="step6.${step}.gro"
    echo "step_${step}_done=$(date -Is)"
  done

  echo
  echo "=== Verification ==="
  for required in step6.6.gro step6.6.cpt step6.6.log; do
    if [[ ! -s "$required" ]]; then
      echo "ERROR: missing or empty final C3 output: $required" >&2
      exit 1
    fi
    ls -lh "$required"
  done
  sha256sum em.* step6.?.* phase3_source_manifest_"$RUN_ID".sha256 > "phase3_outputs_${RUN_ID}.sha256"
  echo "finished=$(date -Is)"
  echo "=== E2 Chimeric Phase C3 complete: $SYSTEM ==="
} 2>&1 | tee "phase3_${RUN_ID}.log"
REMOTE_SCRIPT
done
