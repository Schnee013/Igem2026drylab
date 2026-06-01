#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: slurm_run_chimeric_prod.sh [--smoke|--benchmark] SYSTEM REP LENGTH_NS

Submit a chimeric GROMACS job to the validated Slurm RTX 5090 rerun area:
  /home/guest/igem/md-simulation/<system>/gromacs/prod_repN/

The script uses the same MDP generator as the E2 route and writes an sbatch file
into the replicate directory. Full production is gated by SLURM_PROD_CONFIRMED=1.

Environment:
  REMOTE=10.40.4.5
  SLURM_BASE=/home/guest/igem
  REMOTE_MD_BASE=$SLURM_BASE/md-simulation
  SLURM_ENV_PREFIX=$SLURM_BASE/envs/gromacs-2025.4-mpi-cuda
  SLURM_THREADS=24
  SLURM_PARTITION=gpu
  SLURM_NODELIST=node3
  SLURM_GRES=gpu:rtx5090:1
  SLURM_MEM=128G
  SLURM_TIME_SMOKE=02:00:00
  SLURM_TIME_BENCHMARK=02:00:00
  SLURM_TIME_PROD=168:00:00
  GMX_MDRUN_FLAGS="-nb gpu -pme gpu -bonded gpu"
  MAXWARN=0
  SMOKE_NS=0.02
  BENCHMARK_NS=0.1
  SLURM_PROD_CONFIRMED=0
  SLURM_ALLOW_OVERWRITE=0
  SLURM_IO_RETRIES=3
EOF
}

MODE=prod
if [[ "${1:-}" == "--smoke" ]]; then
  MODE=smoke
  shift
elif [[ "${1:-}" == "--benchmark" ]]; then
  MODE=benchmark
  shift
fi
if [[ $# -ne 3 ]]; then
  usage
  exit 2
fi

SYSTEM=$1
REP=$2
LENGTH_NS=$3

REMOTE=${REMOTE:-10.40.4.5}
SLURM_BASE=${SLURM_BASE:-/home/guest/igem}
REMOTE_MD_BASE=${REMOTE_MD_BASE:-$SLURM_BASE/md-simulation}
SLURM_ENV_PREFIX=${SLURM_ENV_PREFIX:-$SLURM_BASE/envs/gromacs-2025.4-mpi-cuda}
RSYNC_RSH=${RSYNC_RSH:-ssh ${SLURM_SSH_OPTS:-}}
SLURM_THREADS=${SLURM_THREADS:-24}
SLURM_PARTITION=${SLURM_PARTITION:-gpu}
SLURM_NODELIST=${SLURM_NODELIST:-node3}
SLURM_GRES=${SLURM_GRES:-gpu:rtx5090:1}
SLURM_MEM=${SLURM_MEM:-128G}
SLURM_TIME_SMOKE=${SLURM_TIME_SMOKE:-02:00:00}
SLURM_TIME_BENCHMARK=${SLURM_TIME_BENCHMARK:-02:00:00}
SLURM_TIME_PROD=${SLURM_TIME_PROD:-168:00:00}
GMX_MDRUN_FLAGS=${GMX_MDRUN_FLAGS:--nb gpu -pme gpu -bonded gpu}
MAXWARN=${MAXWARN:-0}
SMOKE_NS=${SMOKE_NS:-0.02}
BENCHMARK_NS=${BENCHMARK_NS:-0.1}
SLURM_PROD_CONFIRMED=${SLURM_PROD_CONFIRMED:-0}
SLURM_ALLOW_OVERWRITE=${SLURM_ALLOW_OVERWRITE:-0}
RUN_ID=${RUN_ID:-$(date +%Y%m%d_%H%M%S)}
SLURM_IO_RETRIES=${SLURM_IO_RETRIES:-3}

SSH_OPTS_ARR=()
if [[ -n "${SLURM_SSH_OPTS:-}" ]]; then
  read -r -a SSH_OPTS_ARR <<< "$SLURM_SSH_OPTS"
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
    if [[ "$attempt" -ge "$SLURM_IO_RETRIES" ]]; then
      echo "ERROR: $label failed after $attempt attempts" >&2
      return "$status"
    fi
    attempt=$((attempt + 1))
    echo "WARNING: $label failed with exit $status; retrying attempt $attempt/$SLURM_IO_RETRIES" >&2
    sleep "$((attempt * 2))"
  done
}

case "$MODE" in
  smoke)
    EFFECTIVE_NS=$SMOKE_NS
    PREFIX="smoke_${RUN_ID}"
    MDP_NAME="${PREFIX}.mdp"
    SLURM_TIME=$SLURM_TIME_SMOKE
    ;;
  benchmark)
    EFFECTIVE_NS=$BENCHMARK_NS
    PREFIX="benchmark_${RUN_ID}"
    MDP_NAME="${PREFIX}.mdp"
    SLURM_TIME=$SLURM_TIME_BENCHMARK
    ;;
  prod)
    if [[ "$SLURM_PROD_CONFIRMED" != "1" ]]; then
      echo "ERROR: production launch is gated. Run Slurm preflight, same-pin env validation, smoke, benchmark, review outputs, then set SLURM_PROD_CONFIRMED=1." >&2
      exit 1
    fi
    EFFECTIVE_NS=$LENGTH_NS
    PREFIX="prod"
    MDP_NAME="production.mdp"
    SLURM_TIME=$SLURM_TIME_PROD
    ;;
esac

python3 "$MAKE_MDP" "$SYSTEM" "$REP" "$EFFECTIVE_NS" --output "$TMP_DIR/$MDP_NAME"

REMOTE_GMX="$REMOTE_MD_BASE/$SYSTEM/gromacs"
REMOTE_REP="$REMOTE_GMX/prod_rep${REP}"
REMOTE_BENCH="$REMOTE_MD_BASE/benchmarks/chimeric_${RUN_ID}"
SBATCH_NAME="${PREFIX}_${SYSTEM}_rep${REP}.sbatch"

echo "[slurm-run] preparing $REMOTE:$REMOTE_REP"
retry_cmd "remote mkdir $REMOTE_REP" "${SSH_CMD[@]}" "$REMOTE" "mkdir -p '$REMOTE_REP' '$REMOTE_BENCH'"
retry_cmd "rsync $MDP_NAME for $SYSTEM rep$REP" rsync -avP -e "$RSYNC_RSH" "$TMP_DIR/$MDP_NAME" "$REMOTE:$REMOTE_REP/$MDP_NAME"

"${SSH_CMD[@]}" "$REMOTE" \
  "SYSTEM='$SYSTEM' REP='$REP' PREFIX='$PREFIX' MDP_NAME='$MDP_NAME' REMOTE_GMX='$REMOTE_GMX' REMOTE_REP='$REMOTE_REP' REMOTE_MD_BASE='$REMOTE_MD_BASE' REMOTE_BENCH='$REMOTE_BENCH' SLURM_ENV_PREFIX='$SLURM_ENV_PREFIX' SLURM_THREADS='$SLURM_THREADS' SLURM_PARTITION='$SLURM_PARTITION' SLURM_NODELIST='$SLURM_NODELIST' SLURM_GRES='$SLURM_GRES' SLURM_MEM='$SLURM_MEM' SLURM_TIME='$SLURM_TIME' GMX_MDRUN_FLAGS='$GMX_MDRUN_FLAGS' MAXWARN='$MAXWARN' SLURM_ALLOW_OVERWRITE='$SLURM_ALLOW_OVERWRITE' RUN_ID='$RUN_ID' MODE='$MODE' SBATCH_NAME='$SBATCH_NAME' bash -s" <<'REMOTE_SCRIPT'
set -euo pipefail

mkdir -p "$REMOTE_REP" "$REMOTE_BENCH"
cd "$REMOTE_REP"

cat > "$SBATCH_NAME" <<SBATCH_EOF
#!/usr/bin/env bash
#SBATCH --job-name=chmd_${MODE}_${SYSTEM}_r${REP}
#SBATCH --partition=${SLURM_PARTITION}
#SBATCH --nodelist=${SLURM_NODELIST}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${SLURM_THREADS}
#SBATCH --gres=${SLURM_GRES}
#SBATCH --mem=${SLURM_MEM}
#SBATCH --time=${SLURM_TIME}
#SBATCH --output=${PREFIX}_%j.out
#SBATCH --error=${PREFIX}_%j.err

set -euo pipefail

echo "[slurm-job] started \$(date -Is)"
echo "system=${SYSTEM}"
echo "rep=${REP}"
echo "mode=${MODE}"
echo "run_id=${RUN_ID}"
echo "host=\$(hostname)"
echo "workdir=\$(pwd)"
echo "cuda_visible_devices=\${CUDA_VISIBLE_DEVICES:-unset}"
echo "slurm_job_id=\${SLURM_JOB_ID:-unset}"
echo "slurm_cpus_per_task=\${SLURM_CPUS_PER_TASK:-unset}"

GMX_ENV="${REMOTE_MD_BASE}/.chimeric_gmx.env"
if [[ -f "\$GMX_ENV" ]]; then
  set +u
  source "\$GMX_ENV"
  set -u
fi
if [[ -z "\${GMX_CMD:-}" ]]; then
  GMX_CMD="${SLURM_ENV_PREFIX}/bin/gmx_mpi"
fi
if [[ ! -x "\$GMX_CMD" ]]; then
  echo "ERROR: GMX_CMD is not executable: \$GMX_CMD" >&2
  exit 1
fi
read -r -a GMX_ARR <<< "\$GMX_CMD"
read -r -a MDRUN_FLAGS_ARR <<< "${GMX_MDRUN_FLAGS}"

if [[ "${MODE}" == "prod" && "${SLURM_ALLOW_OVERWRITE}" != "1" ]]; then
  for existing in prod.tpr prod.log prod.cpt prod.xtc prod.gro prod.edr; do
    if [[ -e "\$existing" ]]; then
      echo "ERROR: \$existing already exists in ${REMOTE_REP}; set SLURM_ALLOW_OVERWRITE=1 only after auditing." >&2
      exit 1
    fi
  done
fi

for required in ../step6.6.gro ../topol.top ../index.ndx "${MDP_NAME}"; do
  if [[ ! -s "\$required" ]]; then
    echo "ERROR: required file missing or empty: \$required" >&2
    exit 1
  fi
done

"\${GMX_ARR[@]}" --version > "${PREFIX}_gmx_version_${RUN_ID}.log" 2>&1
if ! grep -Eq 'GROMACS version:[[:space:]]*2025\.4' "${PREFIX}_gmx_version_${RUN_ID}.log"; then
  echo "ERROR: GROMACS version is not 2025.4. See ${PREFIX}_gmx_version_${RUN_ID}.log" >&2
  exit 1
fi
if ! grep -Eiq 'GPU support[[:space:]]*:[[:space:]]*(CUDA|SYCL|OpenCL|enabled|yes)' "${PREFIX}_gmx_version_${RUN_ID}.log"; then
  echo "ERROR: GROMACS command does not report GPU support. See ${PREFIX}_gmx_version_${RUN_ID}.log" >&2
  exit 1
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi -L > "${PREFIX}_nvidia_smi_${RUN_ID}.log" 2>&1 || true
  nvidia-smi >> "${PREFIX}_nvidia_smi_${RUN_ID}.log" 2>&1 || true
fi

echo "[slurm-job] grompp \$(date -Is)"
"\${GMX_ARR[@]}" grompp \
  -f "${MDP_NAME}" \
  -c ../step6.6.gro \
  -p ../topol.top \
  -n ../index.ndx \
  -o "${PREFIX}.tpr" \
  -po "${PREFIX}_out.mdp" \
  -maxwarn "${MAXWARN}" \
  > "${PREFIX}_grompp_${RUN_ID}.log" 2>&1

echo "[slurm-job] mdrun \$(date -Is)"
OMP_NUM_THREADS="${SLURM_THREADS}" "\${GMX_ARR[@]}" mdrun \
  -deffnm "${PREFIX}" \
  -ntomp "${SLURM_THREADS}" \
  -pin on \
  "\${MDRUN_FLAGS_ARR[@]}" \
  > "${PREFIX}_mdrun_${RUN_ID}.log" 2>&1

if [[ -s "${PREFIX}.xtc" ]]; then
  "\${GMX_ARR[@]}" check -f "${PREFIX}.xtc" > "${PREFIX}_gmx_check_${RUN_ID}.log" 2>&1 || true
fi

if command -v sha256sum >/dev/null 2>&1; then
  files=("${MDP_NAME}" "${PREFIX}.tpr" "${PREFIX}.log" "${PREFIX}.cpt" "${PREFIX}.gro" "${PREFIX}.xtc" "${PREFIX}.edr" "${PREFIX}_out.mdp" "${PREFIX}_grompp_${RUN_ID}.log" "${PREFIX}_mdrun_${RUN_ID}.log" "${PREFIX}_gmx_version_${RUN_ID}.log")
  existing=()
  for file in "\${files[@]}"; do
    [[ -f "\$file" ]] && existing+=("\$file")
  done
  sha256sum "\${existing[@]}" > "${PREFIX}_checksums.sha256"
fi

if [[ "${MODE}" == "benchmark" ]]; then
  ns_day=\$(awk '/Performance:/ {print \$2}' "${PREFIX}_mdrun_${RUN_ID}.log" | tail -n 1)
  atoms=\$(awk '/atoms in the system/ {print \$1}' "${PREFIX}_grompp_${RUN_ID}.log" | tail -n 1)
  gpu=\$(awk -F': ' '/Device Name:/ {print \$2; exit}' "${PREFIX}.log" 2>/dev/null || true)
  gmx_version=\$(awk -F': ' '/GROMACS version:/ {print \$2; exit}' "${PREFIX}_gmx_version_${RUN_ID}.log")
  summary="${REMOTE_BENCH}/summary.tsv"
  if [[ ! -f "\$summary" ]]; then
    printf "system\trep\tmode\tatoms\tgpu\tthreads\tgromacs\tbuild\tjob_id\tns_per_day\tworkdir\n" > "\$summary"
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "${SYSTEM}" "${REP}" "${MODE}" "\${atoms:-unknown}" "\${gpu:-unknown}" "${SLURM_THREADS}" "\${gmx_version:-unknown}" "${SLURM_ENV_PREFIX}" "\${SLURM_JOB_ID:-unknown}" "\${ns_day:-unknown}" "\$(pwd)" >> "\$summary"
fi

echo "[slurm-job] done \$(date -Is)"
SBATCH_EOF

job_output=$(sbatch "$SBATCH_NAME")
echo "$job_output"
echo "$job_output" > "${PREFIX}_sbatch_${RUN_ID}.txt"
REMOTE_SCRIPT
