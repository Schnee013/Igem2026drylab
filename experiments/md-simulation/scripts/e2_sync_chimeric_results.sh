#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: e2_sync_chimeric_results.sh SYSTEM...

Pull E2 chimeric production outputs into:
  experiments/md-simulation/results/<system>/raw/repN/

Environment:
  REMOTE=nkuliulab-e2
  E2_BASE=/ifs1/User/dengwei/igem
  REMOTE_MD_BASE=$E2_BASE/md-simulation
  REPS="1 2 3"
  RESULTS_RUN_ID=       # optional: store under raw/$RESULTS_RUN_ID/repN
  E2_ALLOW_LOCAL_OVERWRITE=0
  E2_IO_RETRIES=3          # retry short SSH/rsync transfers on transient resets
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
RESULTS_ROOT=${RESULTS_ROOT:-experiments/md-simulation/results}
REPS=${REPS:-1 2 3}
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}
RESULTS_RUN_ID=${RESULTS_RUN_ID:-}
E2_ALLOW_LOCAL_OVERWRITE=${E2_ALLOW_LOCAL_OVERWRITE:-0}
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
  for rep in $REPS; do
    remote_dir="$REMOTE_MD_BASE/$system/gromacs/prod_rep${rep}"
    if [[ -n "$RESULTS_RUN_ID" ]]; then
      local_dir="$RESULTS_ROOT/$system/raw/$RESULTS_RUN_ID/rep${rep}"
    else
      local_dir="$RESULTS_ROOT/$system/raw/rep${rep}"
      if [[ "$E2_ALLOW_LOCAL_OVERWRITE" != "1" ]] && compgen -G "$local_dir/prod.*" >/dev/null; then
        echo "ERROR: existing local production files found in $local_dir." >&2
        echo "Set RESULTS_RUN_ID for E2 rerun outputs, or set E2_ALLOW_LOCAL_OVERWRITE=1 after archiving/auditing." >&2
        exit 1
      fi
    fi
    mkdir -p "$local_dir"
    echo "[result-sync] $system rep$rep"

    for pattern in \
      'prod.xtc' 'prod.gro' 'prod.tpr' 'prod.log' 'prod.cpt' \
      'production.mdp' 'prod_out.mdp' 'prod_*_*.log' 'prod_checksums.sha256' \
      'smoke_*'; do
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
      echo "[result-sync] warning: no files pulled for $system rep$rep" >&2
    fi
  done
done
