#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: e2_run_chimeric_prod.sh [--smoke] SYSTEM REP LENGTH_NS

Run chimeric production on E2 in:
  /ifs1/User/dengwei/igem/md-simulation/<system>/gromacs/prod_repN/

Run inside tmux for full production. This script does not use Slurm.

Environment:
  REMOTE=nkuliulab-e2
  E2_BASE=/ifs1/User/dengwei/igem
  E2_THREADS=24
  GMX_MDRUN_FLAGS="-nb gpu -pme gpu -bonded gpu"
  MAXWARN=0
  SMOKE_NS=0.02
  E2_PROD_CONFIRMED=0   # must be 1 for non-smoke production after gate review
  E2_REQUIRE_PREFLIGHT_GMX=1
  E2_ALLOW_OVERWRITE=0
  E2_IO_RETRIES=3       # retry short SSH/rsync setup transfers on transient resets
EOF
}

MODE=prod
if [[ "${1:-}" == "--smoke" ]]; then
  MODE=smoke
  shift
fi
if [[ $# -ne 3 ]]; then
  usage
  exit 2
fi

SYSTEM=$1
REP=$2
LENGTH_NS=$3

REMOTE=${REMOTE:-nkuliulab-e2}
E2_BASE=${E2_BASE:-/ifs1/User/dengwei/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$E2_BASE/md-simulation}
RSYNC_RSH=${RSYNC_RSH:-ssh ${E2_SSH_OPTS:-}}
E2_THREADS=${E2_THREADS:-24}
GMX_MDRUN_FLAGS=${GMX_MDRUN_FLAGS:--nb gpu -pme gpu -bonded gpu}
MAXWARN=${MAXWARN:-0}
SMOKE_NS=${SMOKE_NS:-0.02}
E2_PROD_CONFIRMED=${E2_PROD_CONFIRMED:-0}
E2_REQUIRE_PREFLIGHT_GMX=${E2_REQUIRE_PREFLIGHT_GMX:-1}
E2_ALLOW_OVERWRITE=${E2_ALLOW_OVERWRITE:-0}
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}
E2_IO_RETRIES=${E2_IO_RETRIES:-3}

SSH_OPTS_ARR=()
if [[ -n "${E2_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$E2_SSH_OPTS"
  SSH_CMD=(ssh "${SSH_OPTS_ARR[@]}")
else
  SSH_CMD=(ssh)
fi
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MAKE_MDP="$SCRIPT_DIR/e2_make_chimeric_prod_mdp.py"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

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

if [[ "$MODE" == "smoke" ]]; then
  EFFECTIVE_NS=$SMOKE_NS
  PREFIX="smoke_${RUN_ID}"
  MDP_NAME="${PREFIX}.mdp"
else
  if [[ "$E2_PROD_CONFIRMED" != "1" ]]; then
    echo "ERROR: production launch is gated. Run preflight, input audit, grompp/smoke mdrun, review outputs, then set E2_PROD_CONFIRMED=1." >&2
    exit 1
  fi
  EFFECTIVE_NS=$LENGTH_NS
  PREFIX="prod"
  MDP_NAME="production.mdp"
fi

python3 "$MAKE_MDP" "$SYSTEM" "$REP" "$EFFECTIVE_NS" --output "$TMP_DIR/$MDP_NAME"

REMOTE_GMX="$REMOTE_MD_BASE/$SYSTEM/gromacs"
REMOTE_REP="$REMOTE_GMX/prod_rep${REP}"
echo "[e2-run] preparing $REMOTE:$REMOTE_REP"
retry_cmd "remote mkdir $REMOTE_REP" "${SSH_CMD[@]}" "$REMOTE" "mkdir -p '$REMOTE_REP'"
retry_cmd "rsync $MDP_NAME for $SYSTEM rep$REP" rsync -avP -e "$RSYNC_RSH" "$TMP_DIR/$MDP_NAME" "$REMOTE:$REMOTE_REP/$MDP_NAME"

"${SSH_CMD[@]}" "$REMOTE" \
  "SYSTEM='$SYSTEM' REP='$REP' PREFIX='$PREFIX' MDP_NAME='$MDP_NAME' REMOTE_GMX='$REMOTE_GMX' REMOTE_REP='$REMOTE_REP' REMOTE_MD_BASE='$REMOTE_MD_BASE' E2_THREADS='$E2_THREADS' GMX_MDRUN_FLAGS='$GMX_MDRUN_FLAGS' MAXWARN='$MAXWARN' E2_REQUIRE_PREFLIGHT_GMX='$E2_REQUIRE_PREFLIGHT_GMX' E2_ALLOW_OVERWRITE='$E2_ALLOW_OVERWRITE' RUN_ID='$RUN_ID' bash -s" <<'REMOTE_SCRIPT'
set -euo pipefail

GMX_ENV="$REMOTE_MD_BASE/.chimeric_gmx.env"
if [[ -f "$GMX_ENV" ]]; then
  set +u
  source "$GMX_ENV"
  set -u
fi
if [[ -z "${GMX_CMD:-}" ]]; then
  if [[ "$E2_REQUIRE_PREFLIGHT_GMX" == "1" ]]; then
    echo "ERROR: missing preflight-selected GROMACS command: $GMX_ENV" >&2
    echo "Run e2_chimeric_preflight.sh after activating/installing GPU-enabled GROMACS." >&2
    exit 1
  fi
  if command -v gmx_mpi >/dev/null 2>&1; then
    GMX_CMD=$(command -v gmx_mpi)
  elif command -v gmx >/dev/null 2>&1; then
    GMX_CMD=$(command -v gmx)
  else
    echo "ERROR: no GMX_CMD, gmx_mpi, or gmx found. Run e2_chimeric_preflight.sh after activating GROMACS." >&2
    exit 1
  fi
fi
read -r -a GMX_ARR <<< "$GMX_CMD"
read -r -a MDRUN_FLAGS_ARR <<< "$GMX_MDRUN_FLAGS"

cd "$REMOTE_REP"
if [[ "$PREFIX" == "prod" && "$E2_ALLOW_OVERWRITE" != "1" ]]; then
  for existing in prod.tpr prod.log prod.cpt prod.xtc prod.gro; do
    if [[ -e "$existing" ]]; then
      echo "ERROR: $existing already exists in $REMOTE_REP; set E2_ALLOW_OVERWRITE=1 only after auditing." >&2
      exit 1
    fi
  done
fi

for required in ../step6.6.gro ../topol.top ../index.ndx "$MDP_NAME"; do
  if [[ ! -s "$required" ]]; then
    echo "ERROR: required file missing or empty: $required" >&2
    exit 1
  fi
done

echo "[e2-run] $(date -Is) grompp $SYSTEM rep$REP prefix=$PREFIX"
"${GMX_ARR[@]}" grompp \
  -f "$MDP_NAME" \
  -c ../step6.6.gro \
  -p ../topol.top \
  -n ../index.ndx \
  -o "${PREFIX}.tpr" \
  -po "${PREFIX}_out.mdp" \
  -maxwarn "$MAXWARN" \
  2>&1 | tee "${PREFIX}_grompp_${RUN_ID}.log"

echo "[e2-run] $(date -Is) mdrun $SYSTEM rep$REP prefix=$PREFIX threads=$E2_THREADS"
OMP_NUM_THREADS="$E2_THREADS" "${GMX_ARR[@]}" mdrun \
  -deffnm "$PREFIX" \
  -ntomp "$E2_THREADS" \
  -pin on \
  "${MDRUN_FLAGS_ARR[@]}" \
  2>&1 | tee "${PREFIX}_mdrun_${RUN_ID}.log"

if command -v sha256sum >/dev/null 2>&1; then
  files=("$MDP_NAME" "${PREFIX}.tpr" "${PREFIX}.log" "${PREFIX}.cpt" "${PREFIX}.gro" "${PREFIX}.xtc" "${PREFIX}_out.mdp")
  existing=()
  for file in "${files[@]}"; do
    [[ -f "$file" ]] && existing+=("$file")
  done
  sha256sum "${existing[@]}" > "${PREFIX}_checksums.sha256"
fi

echo "[e2-run] done $SYSTEM rep$REP prefix=$PREFIX"
REMOTE_SCRIPT
