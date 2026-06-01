#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: slurm_sync_chimeric_results.sh SYSTEM...

Pull Slurm chimeric outputs into:
  experiments/md-simulation/results/<system>/raw/<RESULTS_RUN_ID>/repN/

Environment:
  REMOTE=10.40.4.5
  SLURM_BASE=/home/guest/igem
  REMOTE_MD_BASE=$SLURM_BASE/md-simulation
  REPS="1 2 3"
  RESULTS_RUN_ID=$(date +%Y%m%d)_slurm5090_rerun
  SLURM_IO_RETRIES=3
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

REMOTE=${REMOTE:-10.40.4.5}
SLURM_BASE=${SLURM_BASE:-/home/guest/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$SLURM_BASE/md-simulation}
RSYNC_RSH=${RSYNC_RSH:-ssh ${SLURM_SSH_OPTS:-}}
RESULTS_ROOT=${RESULTS_ROOT:-experiments/md-simulation/results}
REPS=${REPS:-1 2 3}
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}
RESULTS_RUN_ID=${RESULTS_RUN_ID:-$(date +%Y%m%d)_slurm5090_rerun}
SLURM_IO_RETRIES=${SLURM_IO_RETRIES:-3}

SSH_OPTS_ARR=()
if [[ -n "${SLURM_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$SLURM_SSH_OPTS"
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
    if [[ "$attempt" -ge "$SLURM_IO_RETRIES" ]]; then
      echo "ERROR: $label failed after $attempt attempts" >&2
      return "$status"
    fi
    attempt=$((attempt + 1))
    echo "WARNING: $label failed with exit $status; retrying attempt $attempt/$SLURM_IO_RETRIES" >&2
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
    if [[ "$attempt" -ge "$SLURM_IO_RETRIES" ]]; then
      echo "ERROR: remote find failed for $remote_dir/$pattern after $attempt attempts" >&2
      return "$status"
    fi
    attempt=$((attempt + 1))
    echo "WARNING: remote find failed for $remote_dir/$pattern with exit $status; retrying attempt $attempt/$SLURM_IO_RETRIES" >&2
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
  for rep in $REPS; do
    remote_dir="$REMOTE_MD_BASE/$system/gromacs/prod_rep${rep}"
    local_dir="$RESULTS_ROOT/$system/raw/$RESULTS_RUN_ID/rep${rep}"
    mkdir -p "$local_dir"
    echo "[slurm-result-sync] $system rep$rep -> $local_dir"

    for pattern in \
      'prod.xtc' 'prod.gro' 'prod.tpr' 'prod.log' 'prod.cpt' 'prod.edr' \
      'production.mdp' 'prod_out.mdp' 'prod_*_*.log' 'prod_*.out' 'prod_*.err' 'prod_checksums.sha256' 'prod_sbatch_*.txt' \
      'smoke_*' 'benchmark_*'; do
      pull_pattern "$remote_dir" "$local_dir" "$pattern"
    done

    if compgen -G "$local_dir/*" >/dev/null; then
      (
        cd "$local_dir"
        find . -maxdepth 1 -type f ! -name 'local_pull_*.sha256' -print0 \
          | sort -z \
          | xargs -0 shasum -a 256 > "local_pull_${RUN_ID}.sha256"
      )
    else
      echo "[slurm-result-sync] warning: no files pulled for $system rep$rep" >&2
    fi
  done
done
