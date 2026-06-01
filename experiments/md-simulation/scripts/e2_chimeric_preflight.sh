#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-nkuliulab-e2}
E2_BASE=${E2_BASE:-/ifs1/User/dengwei/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$E2_BASE/md-simulation}
REMOTE_LOG_DIR=${REMOTE_LOG_DIR:-$E2_BASE/logs}
LOCAL_LOG_DIR=${LOCAL_LOG_DIR:-experiments/md-simulation/results/e2_preflight}
RUN_ID=${RUN_ID:-${1:-$(date +%Y%m%d_%H%M%S)}}

SSH_OPTS_ARR=()
if [[ -n "${E2_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$E2_SSH_OPTS"
fi
mkdir -p "$LOCAL_LOG_DIR"

REMOTE_ENV=$(printf "E2_BASE=%q REMOTE_MD_BASE=%q REMOTE_LOG_DIR=%q RUN_ID=%q" \
  "$E2_BASE" "$REMOTE_MD_BASE" "$REMOTE_LOG_DIR" "$RUN_ID")
if [[ -n "${GMX_CMD:-}" ]]; then
  REMOTE_ENV+=" $(printf "GMX_CMD=%q" "$GMX_CMD")"
fi

if [[ ${#SSH_OPTS_ARR[@]} -gt 0 ]]; then
  SSH_CMD=(ssh "${SSH_OPTS_ARR[@]}" "$REMOTE")
else
  SSH_CMD=(ssh "$REMOTE")
fi

"${SSH_CMD[@]}" \
  "$REMOTE_ENV bash -s" <<'REMOTE_SCRIPT' \
  | tee "$LOCAL_LOG_DIR/chimeric_preflight_${RUN_ID}.log"
set -euo pipefail

mkdir -p "$REMOTE_LOG_DIR" "$REMOTE_MD_BASE"
LOG="$REMOTE_LOG_DIR/chimeric_preflight_${RUN_ID}.log"
GMX_ENV="$REMOTE_MD_BASE/.chimeric_gmx.env"
TMP_VERSION="$REMOTE_LOG_DIR/.gmx_version_${RUN_ID}.txt"

{
  echo "== E2 chimeric MD preflight =="
  echo "run_id=$RUN_ID"
  echo "timestamp=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "user=$(whoami)"
  echo "pwd=$(pwd)"
  echo "e2_base=$E2_BASE"
  echo "remote_md_base=$REMOTE_MD_BASE"
  echo

  echo "== Directory and quota =="
  if [[ -d "$E2_BASE" ]]; then
    echo "E2_BASE exists: $E2_BASE"
  else
    echo "ERROR: E2_BASE missing: $E2_BASE"
  fi
  df -h "$E2_BASE" || true
  quota -uvs "$(whoami)" || quota -s || true
  echo

  echo "== GPU and CUDA =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi -L || true
    nvidia-smi || true
  else
    echo "nvidia-smi not found"
  fi
  if command -v nvcc >/dev/null 2>&1; then
    nvcc --version || true
  else
    echo "nvcc not found in PATH"
  fi
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
  echo

  echo "== Environment tools =="
  for tool in conda mamba micromamba apptainer singularity; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "$tool=$(command -v "$tool")"
      "$tool" --version 2>/dev/null | head -n 1 || true
    else
      echo "$tool=not_found"
    fi
  done
  echo

  echo "== GROMACS discovery =="
  candidates=()
  if [[ -n "${GMX_CMD:-}" ]]; then
    candidates+=("$GMX_CMD")
  fi
  for candidate in gmx_mpi gmx; do
    if command -v "$candidate" >/dev/null 2>&1; then
      candidates+=("$(command -v "$candidate")")
    fi
  done

  chosen=""
  gpu_line=""
  first_working=""
  preflight_status=0
  : > "$TMP_VERSION"
  if [[ ${#candidates[@]} -eq 0 ]]; then
    echo "No gmx/gmx_mpi command found in PATH."
    preflight_status=1
  fi

  for candidate in "${candidates[@]}"; do
    echo "-- candidate: $candidate"
    read -r -a candidate_cmd <<< "$candidate"
    if "${candidate_cmd[@]}" --version > "$TMP_VERSION" 2>&1; then
      cat "$TMP_VERSION"
      if [[ -z "$first_working" ]]; then
        first_working="$candidate"
      fi
      if grep -Eiq 'GPU support[[:space:]]*:[[:space:]]*(CUDA|SYCL|OpenCL|enabled|yes)' "$TMP_VERSION"; then
        gpu_line=$(grep -Ei 'GPU support' "$TMP_VERSION" | head -n 1)
        chosen="$candidate"
        break
      else
        echo "candidate has no detected GPU support; continuing discovery"
      fi
    else
      cat "$TMP_VERSION" || true
      echo "candidate failed: $candidate"
    fi
  done

  if [[ -n "$chosen" ]]; then
    printf 'GMX_CMD=%q\n' "$chosen" > "$GMX_ENV"
    echo "chosen_gmx=$chosen"
    echo "gmx_env=$GMX_ENV"
    if [[ -n "$gpu_line" ]]; then
      echo "gpu_support=$gpu_line"
    else
      echo "gpu_support=not_detected_in_version_output"
      preflight_status=1
    fi
  else
    rm -f "$GMX_ENV"
    if [[ -n "$first_working" ]]; then
      echo "first_working_gmx_without_detected_gpu=$first_working"
    fi
    echo "chosen_gmx=none"
    echo "gmx_env=not_written"
    preflight_status=1
  fi

  rm -f "$TMP_VERSION"
  echo
  echo "remote_log=$LOG"
  exit "$preflight_status"
} 2>&1 | tee "$LOG"
REMOTE_SCRIPT

echo "[preflight] local log: $LOCAL_LOG_DIR/chimeric_preflight_${RUN_ID}.log"
