#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-10.40.4.5}
SLURM_BASE=${SLURM_BASE:-/home/guest/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$SLURM_BASE/md-simulation}
REMOTE_LOG_DIR=${REMOTE_LOG_DIR:-$SLURM_BASE/logs}
LOCAL_LOG_DIR=${LOCAL_LOG_DIR:-experiments/md-simulation/results/slurm_preflight}
RUN_ID=${RUN_ID:-${1:-$(date +%Y%m%d_%H%M%S)}}
SLURM_ENV_PREFIX=${SLURM_ENV_PREFIX:-$SLURM_BASE/envs/gromacs-2025.4-mpi-cuda}
SLURM_REQUIRE_GMX=${SLURM_REQUIRE_GMX:-0}

SSH_OPTS_ARR=()
if [[ -n "${SLURM_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$SLURM_SSH_OPTS"
fi
mkdir -p "$LOCAL_LOG_DIR"

REMOTE_ENV=$(printf "SLURM_BASE=%q REMOTE_MD_BASE=%q REMOTE_LOG_DIR=%q RUN_ID=%q SLURM_ENV_PREFIX=%q SLURM_REQUIRE_GMX=%q" \
  "$SLURM_BASE" "$REMOTE_MD_BASE" "$REMOTE_LOG_DIR" "$RUN_ID" "$SLURM_ENV_PREFIX" "$SLURM_REQUIRE_GMX")
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
  | tee "$LOCAL_LOG_DIR/slurm_chimeric_preflight_${RUN_ID}.log"
set -euo pipefail

mkdir -p "$REMOTE_LOG_DIR" "$REMOTE_MD_BASE"
LOG="$REMOTE_LOG_DIR/slurm_chimeric_preflight_${RUN_ID}.log"
GMX_ENV="$REMOTE_MD_BASE/.chimeric_gmx.env"
TMP_VERSION="$REMOTE_LOG_DIR/.slurm_gmx_version_${RUN_ID}.txt"

{
  echo "== Slurm chimeric MD read-only preflight =="
  echo "run_id=$RUN_ID"
  echo "timestamp=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "user=$(whoami)"
  echo "pwd=$(pwd)"
  echo "slurm_base=$SLURM_BASE"
  echo "remote_md_base=$REMOTE_MD_BASE"
  echo "target_env=$SLURM_ENV_PREFIX"
  echo

  echo "== Directory and storage =="
  if [[ -d "$SLURM_BASE" ]]; then
    echo "SLURM_BASE exists: $SLURM_BASE"
  else
    echo "SLURM_BASE missing, parent state:"
    ls -ld "$(dirname "$SLURM_BASE")" || true
  fi
  df -h "$HOME" "$SLURM_BASE" 2>/dev/null || df -h "$HOME" || true
  quota -s 2>/dev/null || true
  echo

  echo "== Slurm scheduler =="
  if command -v sinfo >/dev/null 2>&1; then
    sinfo -o "%P %N %G %m %c %t" || true
  else
    echo "sinfo=not_found"
  fi
  if command -v squeue >/dev/null 2>&1; then
    squeue -u "$(whoami)" || true
  else
    echo "squeue=not_found"
  fi
  if command -v scontrol >/dev/null 2>&1; then
    scontrol show node node3 || true
  else
    echo "scontrol=not_found"
  fi
  echo

  echo "== Login-node GPU/CUDA visibility =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi -L || true
    nvidia-smi || true
  else
    echo "nvidia-smi not found on login node"
  fi
  if command -v nvcc >/dev/null 2>&1; then
    nvcc --version || true
  else
    echo "nvcc not found in PATH"
  fi
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
  echo

  echo "== Environment tools =="
  for tool in conda mamba micromamba spack module sbatch sacct; do
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
  if [[ -x "$SLURM_ENV_PREFIX/bin/gmx_mpi" ]]; then
    candidates+=("$SLURM_ENV_PREFIX/bin/gmx_mpi")
  fi
  for candidate in gmx_mpi gmx; do
    if command -v "$candidate" >/dev/null 2>&1; then
      candidates+=("$(command -v "$candidate")")
    fi
  done

  chosen=""
  gpu_line=""
  status=0
  : > "$TMP_VERSION"
  if [[ ${#candidates[@]} -eq 0 ]]; then
    echo "No gmx/gmx_mpi command found. This is acceptable for read-only preflight only."
    if [[ "$SLURM_REQUIRE_GMX" == "1" ]]; then
      status=1
    fi
  fi

  for candidate in "${candidates[@]}"; do
    echo "-- candidate: $candidate"
    read -r -a candidate_cmd <<< "$candidate"
    if "${candidate_cmd[@]}" --version > "$TMP_VERSION" 2>&1; then
      cat "$TMP_VERSION"
      if grep -Eiq 'GROMACS version:[[:space:]]*2025\.4' "$TMP_VERSION" \
        && grep -Eiq 'GPU support[[:space:]]*:[[:space:]]*(CUDA|SYCL|OpenCL|enabled|yes)' "$TMP_VERSION"; then
        gpu_line=$(grep -Ei 'GPU support' "$TMP_VERSION" | head -n 1)
        chosen="$candidate"
        break
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
    echo "gpu_support=$gpu_line"
  else
    echo "chosen_gmx=none"
    echo "gmx_env=not_written"
    if [[ "$SLURM_REQUIRE_GMX" == "1" ]]; then
      status=1
    fi
  fi

  rm -f "$TMP_VERSION"
  echo
  echo "remote_log=$LOG"
  exit "$status"
} 2>&1 | tee "$LOG"
REMOTE_SCRIPT

echo "[preflight] local log: $LOCAL_LOG_DIR/slurm_chimeric_preflight_${RUN_ID}.log"
