#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: e2_sync_chimeric_phase3_outputs.sh RUN_ID SYSTEM...

Pull E2 rebuilt Phase C3 terminal outputs back into local canonical inputs:
  experiments/md-simulation/systems/<system>/gromacs/

The script intentionally pulls logs/checkpoints/final structures/checksums,
not equilibration trajectories, to keep the local recovery artifact compact.

Environment:
  REMOTE=nkuliulab-e2
  E2_BASE=/ifs1/User/dengwei/igem
  REMOTE_MD_BASE=$E2_BASE/md-simulation
  SYSTEM_ROOT=experiments/md-simulation/systems
  E2_SSH_OPTS="-p 40042"   # optional when REMOTE is not an ssh-config alias
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

RUN_ID=$1
shift

REMOTE=${REMOTE:-nkuliulab-e2}
E2_BASE=${E2_BASE:-/ifs1/User/dengwei/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$E2_BASE/md-simulation}
SYSTEM_ROOT=${SYSTEM_ROOT:-experiments/md-simulation/systems}
RSYNC_RSH=${RSYNC_RSH:-ssh ${E2_SSH_OPTS:-}}
LOCAL_PULL_ID=${LOCAL_PULL_ID:-$(date +%Y%m%d_%H%M%S)}
E2_IO_RETRIES=${E2_IO_RETRIES:-3}

SSH_OPTS_ARR=()
if [[ -n "${E2_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$E2_SSH_OPTS"
  SSH_CMD=(ssh "${SSH_OPTS_ARR[@]}")
else
  SSH_CMD=(ssh)
fi

retry_cmd() {
  local label=$1
  shift
  local attempt=1
  local status=0
  while true; do
    if "$@"; then
      return 0
    fi
    status=$?
    if [[ "$attempt" -ge "$E2_IO_RETRIES" ]]; then
      echo "ERROR: $label failed after $attempt attempts" >&2
      return "$status"
    fi
    attempt=$((attempt + 1))
    echo "WARNING: $label failed with exit $status; retrying attempt $attempt/$E2_IO_RETRIES" >&2
    sleep "$((attempt * 2))"
  done
}

pull_pattern() {
  local remote_dir=$1
  local local_dir=$2
  local pattern=$3
  local matches
  local attempt=1
  local status=0
  while true; do
    if matches=$("${SSH_CMD[@]}" "$REMOTE" "find '$remote_dir' -maxdepth 1 -type f -name '$pattern' -printf '%f\n' 2>/dev/null"); then
      break
    fi
    status=$?
    if [[ "$attempt" -ge "$E2_IO_RETRIES" ]]; then
      echo "ERROR: remote find failed for $remote_dir/$pattern after $attempt attempts" >&2
      return "$status"
    fi
    attempt=$((attempt + 1))
    echo "WARNING: remote find failed for $remote_dir/$pattern with exit $status; retrying attempt $attempt/$E2_IO_RETRIES" >&2
    sleep "$((attempt * 2))"
  done
  if [[ -z "$matches" ]]; then
    return 0
  fi
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    retry_cmd "rsync $remote_dir/$file" rsync -avP -e "$RSYNC_RSH" "$REMOTE:$remote_dir/$file" "$local_dir/"
  done <<< "$matches"
}

for system in "$@"; do
  remote_dir="$REMOTE_MD_BASE/$system/gromacs"
  local_dir="$SYSTEM_ROOT/$system/gromacs"
  echo "[phase3-sync] auditing remote Phase C3 outputs: $system"

  if [[ ! -d "$local_dir" ]]; then
    echo "ERROR: missing local canonical gromacs directory: $local_dir" >&2
    exit 1
  fi

  required_remote=(
    "step6.6.gro"
    "step6.6.cpt"
    "step6.6.log"
    "phase3_${RUN_ID}.log"
    "phase3_outputs_${RUN_ID}.sha256"
    "phase3_source_manifest_${RUN_ID}.sha256"
  )
  for file in "${required_remote[@]}"; do
    if ! retry_cmd "remote required check $remote_dir/$file" "${SSH_CMD[@]}" "$REMOTE" "test -s '$remote_dir/$file'"; then
      echo "ERROR: missing or empty remote Phase C3 output: $remote_dir/$file" >&2
      exit 1
    fi
  done

  echo "[phase3-sync] pulling compact Phase C3 evidence: $system"
  for pattern in \
    "em.log" "em.gro" "em.cpt" "em.tpr" "em_out.mdp" \
    "step6.?.log" "step6.?_out.mdp" \
    "step6.6.gro" "step6.6.cpt" "step6.6.tpr" "step6.6.edr" \
    "phase3_${RUN_ID}.log" \
    "phase3_outputs_${RUN_ID}.sha256" \
    "phase3_source_manifest_${RUN_ID}.sha256"; do
    pull_pattern "$remote_dir" "$local_dir" "$pattern"
  done

  (
    cd "$local_dir"
    files=(
      em.log em.gro em.cpt em.tpr em_out.mdp
      step6.?.log step6.?_out.mdp
      step6.6.gro step6.6.cpt step6.6.tpr step6.6.edr
      "phase3_${RUN_ID}.log"
      "phase3_outputs_${RUN_ID}.sha256"
      "phase3_source_manifest_${RUN_ID}.sha256"
    )
    existing=()
    for file in "${files[@]}"; do
      [[ -f "$file" ]] && existing+=("$file")
    done
    shasum -a 256 "${existing[@]}" > "phase3_local_pull_${LOCAL_PULL_ID}.sha256"
  )
  echo "[phase3-sync] done: $system"
done
