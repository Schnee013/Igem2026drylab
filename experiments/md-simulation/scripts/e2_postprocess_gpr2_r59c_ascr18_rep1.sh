#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE=${REMOTE:-nkuliulab-e2}
RUN_ROOT=${RUN_ROOT:-/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716}
GMX_CMD=${GMX_CMD:-/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi}
PREFIX=${PREFIX:-gpr2_r59c_ascr18_rep1_200ns}
SESSION=${SESSION:-gpr2_r59c_postprocess_20260716}

PREPROD_DIR="$RUN_ROOT/preproduction/gromacs"
PROD_DIR="$RUN_ROOT/production"
PROD_LOG="$RUN_ROOT/logs/production"
OUT_DIR="$RUN_ROOT/processed/rep1"

verify_production_terminal() {
  local actual_manifest_sha detail expected_manifest_sha latest
  if [[ ! -s "$PROD_LOG/run_state_events.tsv" ]]; then
    echo "ERROR: missing production run_state_events.tsv" >&2
    return 66
  fi
  if ! latest=$(awk -F '\t' 'NR == 1 {
      if ($0 != "observed_at\tstate\tsource\tdetail") {
        invalid=1
      }
      next
    }
    NF != 4 {
      invalid=1
      next
    }
    {
      observed_at=$1; state=$2; source=$3; detail=$4
    }
    END {
      if (invalid) {
        exit 2
      }
      if (state != "") {
        printf "%s\t%s\t%s\t%s\n", observed_at, state, source, detail
      }
    }' "$PROD_LOG/run_state_events.tsv"); then
    echo "ERROR: malformed production run-state event stream" >&2
    return 66
  fi
  if [[ -z $latest ]]; then
    echo "ERROR: no valid production run-state event" >&2
    return 66
  fi
  IFS=$'\t' read -r _ latest_state _ detail <<< "$latest"
  if [[ $latest_state != TERMINAL_NORMAL ]]; then
    echo "ERROR: latest production state is $latest_state, not TERMINAL_NORMAL" >&2
    return 66
  fi
  expected_manifest_sha=$(awk -v RS=';' -F= \
    '$1 == "archive_manifest_sha256" { print $2; exit }' <<< "$detail")
  if [[ ! $expected_manifest_sha =~ ^[0-9a-f]{64}$ ]] \
      || [[ ! -s "$RUN_ROOT/production_archive.sha256" ]]; then
    echo "ERROR: terminal event lacks a valid production archive identity" >&2
    return 66
  fi
  actual_manifest_sha=$(sha256sum "$RUN_ROOT/production_archive.sha256" | awk '{print $1}')
  if [[ $actual_manifest_sha != "$expected_manifest_sha" ]]; then
    echo "ERROR: production archive identity changed after terminal event" >&2
    return 66
  fi
}

remote_run() {
  mkdir -p "$OUT_DIR"
  cd "$RUN_ROOT"
  if ! verify_production_terminal; then
    printf 'status\tproduction_not_finished\n' > "$OUT_DIR/terminal_status.tsv"
    exit 66
  fi
  for required in \
    "$PROD_DIR/$PREFIX.tpr" \
    "$PROD_DIR/$PREFIX.xtc" \
    "$PREPROD_DIR/index.fixed.ndx"; do
    [[ -s "$required" ]]
  done
  for output in "$OUT_DIR/prod_cluster.xtc" "$OUT_DIR/prod_protein.xtc" "$OUT_DIR/protein_ref.pdb"; do
    if [[ -e "$output" ]]; then
      printf 'status\trefuse_existing_output\npath\t%s\n' "$output" \
        > "$OUT_DIR/terminal_status.tsv"
      exit 66
    fi
  done

  stage=make_analysis_index
  trap 'rc=$?; printf "status\tfailed\nstage\t%s\nexit_code\t%s\n" "$stage" "$rc" > "$OUT_DIR/terminal_status.tsv"' ERR
  printf 'status\trunning\nstarted\t%s\n' "$(date -Is)" > "$OUT_DIR/terminal_status.tsv"

  printf 'a N | a CA | a C | a O\n0 & 6\nname 7 SOLU_BACKBONE\nq\n' | \
    "$GMX_CMD" make_ndx \
      -f "$PROD_DIR/$PREFIX.tpr" \
      -n "$PREPROD_DIR/index.fixed.ndx" \
      -o "$OUT_DIR/analysis_solu_backbone.ndx" \
      > "$OUT_DIR/make_analysis_index.log" 2>&1

  python3 - "$OUT_DIR/analysis_solu_backbone.ndx" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
groups = {}
current = None
for raw in path.read_text().splitlines():
    line = raw.strip()
    if line.startswith("[") and line.endswith("]"):
        current = line[1:-1].strip()
        groups[current] = []
    elif current and line:
        groups[current].extend(int(value) for value in line.split())
expected = {"SOLU": 6438, "SOLU_BACKBONE": 1623}
for name, count in expected.items():
    observed = len(groups.get(name, []))
    if observed != count:
        raise SystemExit(f"index group {name} has {observed} atoms; expected {count}")
PY

  stage=trjconv_cluster
  printf 'SOLU\nSOLU\n' | "$GMX_CMD" trjconv \
    -s "$PROD_DIR/$PREFIX.tpr" \
    -f "$PROD_DIR/$PREFIX.xtc" \
    -n "$OUT_DIR/analysis_solu_backbone.ndx" \
    -o "$OUT_DIR/prod_cluster.xtc" \
    -pbc cluster \
    > "$OUT_DIR/trjconv_1_cluster.log" 2>&1

  stage=trjconv_backbone_fit
  printf 'SOLU_BACKBONE\nSOLU\n' | "$GMX_CMD" trjconv \
    -s "$PROD_DIR/$PREFIX.tpr" \
    -f "$OUT_DIR/prod_cluster.xtc" \
    -n "$OUT_DIR/analysis_solu_backbone.ndx" \
    -o "$OUT_DIR/prod_protein.xtc" \
    -fit rot+trans \
    > "$OUT_DIR/trjconv_2_fit.log" 2>&1

  stage=trjconv_reference
  printf 'SOLU\n' | "$GMX_CMD" trjconv \
    -s "$PROD_DIR/$PREFIX.tpr" \
    -f "$OUT_DIR/prod_protein.xtc" \
    -n "$OUT_DIR/analysis_solu_backbone.ndx" \
    -o "$OUT_DIR/protein_ref.pdb" \
    -dump 0 \
    > "$OUT_DIR/trjconv_3_ref.log" 2>&1

  stage=processed_sanity
  "$GMX_CMD" check -f "$OUT_DIR/prod_protein.xtc" \
    > "$OUT_DIR/gmx_check_protein.txt" 2>&1
  python3 - "$OUT_DIR/gmx_check_protein.txt" "$OUT_DIR/protein_ref.pdb" <<'PY'
from pathlib import Path
import re
import sys

check = Path(sys.argv[1]).read_text(errors="replace").replace("\r", "\n")
pdb_lines = [
    line for line in Path(sys.argv[2]).read_text(errors="replace").splitlines()
    if line.startswith(("ATOM  ", "HETATM"))
]
atoms = re.search(r"# Atoms\s+(\d+)", check)
last = re.findall(r"Last frame\s+\d+\s+time\s+([0-9.]+)", check)
if not atoms or int(atoms.group(1)) != 6438:
    raise SystemExit(f"unexpected processed XTC atoms: {atoms.group(1) if atoms else 'missing'}")
if not last or abs(float(last[-1]) - 200000.0) > 0.01:
    raise SystemExit(f"unexpected processed XTC final time: {last[-1] if last else 'missing'}")
if len(pdb_lines) != 6438:
    raise SystemExit(f"unexpected reference PDB atom records: {len(pdb_lines)}")
PY

  {
    printf 'key\tvalue\n'
    printf 'remote_root\t%s\n' "$RUN_ROOT"
    printf 'gmx\t%s\n' "$GMX_CMD"
    printf 'processed_group\tSOLU (Gpr2_R59C receptor + ASCR18 ligand)\n'
    printf 'fit_group\tSOLU_BACKBONE (SOLU atoms named N/CA/C/O)\n'
    printf 'output_topology\tprocessed/rep1/protein_ref.pdb\n'
    printf 'output_trajectory\tprocessed/rep1/prod_protein.xtc\n'
    printf 'processed_atoms\t6438\n'
    printf 'completed_at_remote\t%s\n' "$(date -Is)"
  } > "$OUT_DIR/processing_summary.tsv"
  find "$OUT_DIR" -maxdepth 1 -type f \
    ! -name 'SHA256SUMS_processed_rep1.txt' ! -name 'terminal_status.tsv' \
    -print0 | sort -z | xargs -0 sha256sum > "$OUT_DIR/SHA256SUMS_processed_rep1.txt"
  find production logs/production sanity/production processed/rep1 \
    -type f \
    ! -path 'logs/production/terminal_status.tsv' \
    ! -path 'logs/production/run_state_events.tsv' \
    ! -path 'logs/production/run_state.lock' \
    ! -path 'processed/rep1/terminal_status.tsv' \
    ! -path 'processed/rep1/SHA256SUMS_processed_rep1.txt' \
    -print0 | sort -z | xargs -0 sha256sum > "$RUN_ROOT/final_archive.sha256"
  trap - ERR
  printf 'status\tfinished\nfinished\t%s\n' "$(date -Is)" > "$OUT_DIR/terminal_status.tsv"
}

local_launch() {
  rsync -a "$0" "$REMOTE:$RUN_ROOT/e2_postprocess_gpr2_r59c_ascr18_rep1.sh"
  ssh "$REMOTE" "mkdir -p '$RUN_ROOT/processed/rep1'"
  if ssh "$REMOTE" "tmux has-session -t '$SESSION' 2>/dev/null"; then
    echo "ERROR: tmux session already exists: $SESSION" >&2
    exit 66
  fi
  ssh "$REMOTE" \
    "tmux new-session -d -s '$SESSION' 'RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD PREFIX=$PREFIX bash $RUN_ROOT/e2_postprocess_gpr2_r59c_ascr18_rep1.sh --remote-run >> $RUN_ROOT/processed/rep1/launcher.log 2>&1'"
  printf 'launched_session\t%s\nrun_root\t%s\n' "$SESSION" "$RUN_ROOT"
}

case ${1:-} in
  --remote-run) remote_run ;;
  --verify-production-terminal) verify_production_terminal ;;
  "") local_launch ;;
  *) echo "ERROR: unsupported argument $1" >&2; exit 64 ;;
esac
