#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: e2_sync_chimeric_inputs.sh [--audit-only] SYSTEM...

Sync audited local canonical CHARMM-GUI/GROMACS inputs to E2:
  /ifs1/User/dengwei/igem/md-simulation/<system>/gromacs/

Required local files per system:
  canonical root: topol.top index.ndx step7_production.mdp toppar/
  payload root: step6.6.gro step6.6.cpt and final C3/phase3 log evidence

Environment:
  REMOTE=nkuliulab-e2
  E2_BASE=/ifs1/User/dengwei/igem
  REMOTE_MD_BASE=$E2_BASE/md-simulation
  SYSTEM_ROOT=experiments/md-simulation/systems
  DRYLAB_PAYLOAD_ROOT=/absolute/path/outside/repo
  SYSTEM_PAYLOAD_ROOT=$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/systems
  E2_SSH_OPTS="-p 40042"   # optional when REMOTE is not an ssh-config alias
  E2_IO_RETRIES=3          # retry short SSH/rsync transfers on transient resets
EOF
}

AUDIT_ONLY=0
if [[ "${1:-}" == "--audit-only" ]]; then
  AUDIT_ONLY=1
  shift
fi

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

REMOTE=${REMOTE:-nkuliulab-e2}
E2_BASE=${E2_BASE:-/ifs1/User/dengwei/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$E2_BASE/md-simulation}
RSYNC_RSH=${RSYNC_RSH:-ssh ${E2_SSH_OPTS:-}}
SYSTEM_ROOT=${SYSTEM_ROOT:-experiments/md-simulation/systems}
if [[ -z "${SYSTEM_PAYLOAD_ROOT:-}" ]]; then
  if [[ -z "${DRYLAB_PAYLOAD_ROOT:-}" ]]; then
    echo "ERROR: set DRYLAB_PAYLOAD_ROOT or SYSTEM_PAYLOAD_ROOT to an external payload store." >&2
    exit 2
  fi
  SYSTEM_PAYLOAD_ROOT="$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/systems"
fi
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}
E2_IO_RETRIES=${E2_IO_RETRIES:-3}

REPO_ROOT=$(git rev-parse --show-toplevel)
SYSTEM_PAYLOAD_ROOT=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$SYSTEM_PAYLOAD_ROOT")
case "$SYSTEM_PAYLOAD_ROOT/" in
  "$REPO_ROOT/"*)
    echo "ERROR: SYSTEM_PAYLOAD_ROOT must be outside the Git worktree: $SYSTEM_PAYLOAD_ROOT" >&2
    exit 2
    ;;
esac

SSH_OPTS_ARR=()
if [[ -n "${E2_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$E2_SSH_OPTS"
  SSH_CMD=(ssh "${SSH_OPTS_ARR[@]}")
else
  SSH_CMD=(ssh)
fi
shopt -s nullglob

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

for system in "$@"; do
  gmx_dir="$SYSTEM_ROOT/$system/gromacs"
  payload_gmx_dir="$SYSTEM_PAYLOAD_ROOT/$system/gromacs"
  remote_dir="$REMOTE_MD_BASE/$system/gromacs"
  manifest=$(mktemp)
  trap 'rm -f "$manifest"' EXIT

  echo "[input-sync] auditing $system"
  if [[ ! -d "$gmx_dir" ]]; then
    echo "ERROR: missing repo-owned canonical gromacs directory: $gmx_dir" >&2
    exit 1
  fi
  if [[ ! -d "$payload_gmx_dir" ]]; then
    echo "ERROR: missing external payload gromacs directory: $payload_gmx_dir" >&2
    exit 1
  fi

  required_canonical_files=(
    "$gmx_dir/topol.top"
    "$gmx_dir/index.ndx"
    "$gmx_dir/step7_production.mdp"
  )
  required_payload_files=(
    "$payload_gmx_dir/step6.6.gro"
    "$payload_gmx_dir/step6.6.cpt"
  )
  for path in "${required_canonical_files[@]}" "${required_payload_files[@]}"; do
    if [[ ! -s "$path" ]]; then
      echo "ERROR: required input is missing or empty: $path" >&2
      echo "Restore and audit final C3 payloads outside the repo before syncing $system." >&2
      exit 1
    fi
  done
  c3_logs=(
    "$payload_gmx_dir"/phase3_*.log
    "$payload_gmx_dir"/step6.6*.log
    "$payload_gmx_dir"/equil*.log
    "$payload_gmx_dir"/eq*.log
  )
  if [[ ${#c3_logs[@]} -eq 0 ]]; then
    echo "ERROR: missing final C3/phase3 log evidence for $system" >&2
    echo "Recover and audit final equilibration logs before syncing $system." >&2
    exit 1
  fi
  if ! grep -Eiq 'Phase C3 complete|step6\.6\.gro exists|Finished mdrun|step6\.6\.cpt|Writing checkpoint' "${c3_logs[@]}"; then
    echo "ERROR: C3/phase3 logs lack a recognizable final-equilibration completion marker for $system" >&2
    echo "Audit the recovered final eq logs/checkpoints before syncing." >&2
    exit 1
  fi
  if [[ ! -d "$gmx_dir/toppar" ]]; then
    echo "ERROR: missing topology directory: $gmx_dir/toppar" >&2
    exit 1
  fi
  if ! find "$gmx_dir/toppar" -type f -print -quit | grep -q .; then
    echo "ERROR: topology directory has no files: $gmx_dir/toppar" >&2
    exit 1
  fi

  for group in SOLU SOLU_MEMB SOLV MEMB SYSTEM; do
    if ! grep -Eq "^[[:space:]]*\\[[[:space:]]*$group[[:space:]]*\\]" "$gmx_dir/index.ndx"; then
      echo "ERROR: index.ndx missing required group [$group] for $system" >&2
      exit 1
    fi
  done
  group_counts=$(
    awk '
      /^[[:space:]]*\[/ {
        group=$0
        gsub(/^[[:space:]]*\[[[:space:]]*/, "", group)
        gsub(/[[:space:]]*\][[:space:]]*$/, "", group)
        next
      }
      group == "SOLU" || group == "SOLU_MEMB" || group == "SOLV" || group == "MEMB" || group == "SYSTEM" {
        counts[group] += NF
      }
      END {
        for (g in counts) {
          print g, counts[g]
        }
      }
    ' "$gmx_dir/index.ndx"
  )
  for group in SOLU SOLU_MEMB SOLV MEMB SYSTEM; do
    count=$(awk -v g="$group" '$1 == g { print $2 }' <<< "$group_counts")
    if [[ -z "$count" || "$count" -le 0 ]]; then
      echo "ERROR: index group [$group] is empty or unreadable for $system" >&2
      exit 1
    fi
    echo "[input-sync] index group $group atoms=$count"
  done
  solu_count=$(awk '$1 == "SOLU" { print $2 }' <<< "$group_counts")
  system_count=$(awk '$1 == "SYSTEM" { print $2 }' <<< "$group_counts")
  if [[ "$solu_count" -ge "$system_count" ]]; then
    echo "ERROR: [SOLU] atoms ($solu_count) must be smaller than [SYSTEM] atoms ($system_count) for protein-only XTC." >&2
    exit 1
  fi

  {
    echo "# sha256 manifest for $system"
    echo "# generated $RUN_ID on $(hostname)"
    (
      cd "$gmx_dir"
      files=(README topol.top index.ndx step5_input.gro step5_input.pdb step5_input.psf step7_production.mdp)
      files+=(step6.*.mdp)
      for file in "${files[@]}"; do
        [[ -f "$file" ]] && shasum -a 256 "$file"
      done
      find toppar -type f -print | sort | while read -r file; do
        shasum -a 256 "$file"
      done
    )
    (
      cd "$payload_gmx_dir"
      files=(step6.6.gro step6.6.cpt em.log phase3_*.log step6.6*.log equil*.log eq*.log)
      for file in "${files[@]}"; do
        [[ -f "$file" ]] && shasum -a 256 "$file"
      done
    )
  } > "$manifest"

  if [[ "$AUDIT_ONLY" == "1" ]]; then
    echo "[input-sync] audit-only passed: $system"
    rm -f "$manifest"
    trap - EXIT
    continue
  fi

  echo "[input-sync] creating $REMOTE:$remote_dir"
  retry_cmd "remote mkdir $remote_dir" "${SSH_CMD[@]}" "$REMOTE" "mkdir -p '$remote_dir'"

  canonical_files=(
    "$gmx_dir/topol.top"
    "$gmx_dir/index.ndx"
    "$gmx_dir/step7_production.mdp"
  )
  optional_canonical_files=(
    "$gmx_dir"/README
    "$gmx_dir"/step5_input.*
    "$gmx_dir"/step6.*.mdp
  )
  payload_files=(
    "$payload_gmx_dir/step6.6.gro"
    "$payload_gmx_dir/step6.6.cpt"
  )
  optional_payload_files=(
    "$payload_gmx_dir"/em.log
    "$payload_gmx_dir"/phase3_*.log
    "$payload_gmx_dir"/step6.6*.log
    "$payload_gmx_dir"/equil*.log
    "$payload_gmx_dir"/eq*.log
  )
  for path in "${optional_canonical_files[@]}"; do
    [[ -f "$path" ]] && canonical_files+=("$path")
  done
  for path in "${optional_payload_files[@]}"; do
    [[ -f "$path" ]] && payload_files+=("$path")
  done

  retry_cmd "rsync canonical inputs for $system" rsync -avP -e "$RSYNC_RSH" "${canonical_files[@]}" "$REMOTE:$remote_dir/"
  retry_cmd "rsync external payload inputs for $system" rsync -avP -e "$RSYNC_RSH" "${payload_files[@]}" "$REMOTE:$remote_dir/"
  retry_cmd "rsync toppar for $system" rsync -avP -e "$RSYNC_RSH" "$gmx_dir/toppar/" "$REMOTE:$remote_dir/toppar/"
  retry_cmd "rsync input manifest for $system" rsync -avP -e "$RSYNC_RSH" "$manifest" "$REMOTE:$remote_dir/input_manifest_${RUN_ID}.sha256"
  echo "[input-sync] done: $system"
  rm -f "$manifest"
  trap - EXIT
done
