#!/usr/bin/env bash
set -Eeuo pipefail

# Generate chctrl-compatible processed inputs using the run-recorded GROMACS.

: "${RUN_ROOT:?set RUN_ROOT}"
: "${GMX_CMD:?set GMX_CMD}"
: "${PREFIX:?set PREFIX}"

REP=${REP:-1}
PROD_DIR=${PROD_DIR:-"$RUN_ROOT/production/rep$REP"}
PROD_LOG_DIR=${PROD_LOG_DIR:-"$RUN_ROOT/logs/production/rep$REP"}
OUT_DIR=${OUT_DIR:-"$RUN_ROOT/processed/rep$REP"}
PYTHON_CMD=${PYTHON_CMD:-"$(dirname "$GMX_CMD")/python3"}
SOURCE_IDENTITY_MANIFEST=${SOURCE_IDENTITY_MANIFEST:-"$PROD_DIR/production_source_inputs.sha256"}
INDEX_FILE=${INDEX_FILE:-}
SOLUTION_GROUP=${SOLUTION_GROUP:-SOLU}
RECEPTOR_GROUP=${RECEPTOR_GROUP:-PROA}
FIT_GROUP=${FIT_GROUP:-PROA_BACKBONE}
EXPECTED_SOLUTION_ATOMS=${EXPECTED_SOLUTION_ATOMS:?set EXPECTED_SOLUTION_ATOMS}
EXPECTED_FIT_ATOMS=${EXPECTED_FIT_ATOMS:?set EXPECTED_FIT_ATOMS}
EXPECTED_FRAMES=${EXPECTED_FRAMES:-2001}
EXPECTED_FINAL_TIME_PS=${EXPECTED_FINAL_TIME_PS:-200000}
ATTEMPT_ID=${ATTEMPT_ID:-"postprocess_attempt3_$(date -u '+%Y%m%dT%H%M%SZ')"}

STATE_EVENTS="$PROD_LOG_DIR/run_state_events.tsv"
PROD_STATUS="$PROD_LOG_DIR/terminal_status.tsv"
ATTEMPT_DIR="$OUT_DIR/$ATTEMPT_ID"
ATTEMPT_STATUS="$ATTEMPT_DIR/postprocess_status.tsv"
TPR=${TPR_INPUT:-"$PROD_DIR/$PREFIX.tpr"}
XTC=${XTC_INPUT:-"$PROD_DIR/$PREFIX.xtc"}
PRODUCTION_GATE_MODE=${PRODUCTION_GATE_MODE:-archive}
PBC_ROUTE=${PBC_ROUTE:-cluster}
ANALYSIS_INDEX="$ATTEMPT_DIR/analysis_index.ndx"
CLUSTER_XTC="$OUT_DIR/prod_cluster.xtc"
PROTEIN_XTC="$OUT_DIR/prod_protein.xtc"
REFERENCE_PDB="$OUT_DIR/protein_ref.pdb"
CURRENT_STAGE=preflight

on_error() {
  local rc=$?
  trap - ERR
  set +e
  {
    printf 'key\tvalue\n'
    printf 'status\tHOLD\n'
    printf 'stage\t%s\n' "$CURRENT_STAGE"
    printf 'exit_code\t%s\n' "$rc"
    printf 'observed_at\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  } > "$ATTEMPT_STATUS"
  exit "$rc"
}

mkdir -p "$ATTEMPT_DIR"
trap on_error ERR
{
  printf 'key\tvalue\n'
  printf 'status\tRUNNING\n'
  printf 'stage\tpreflight\n'
  printf 'started_at\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} > "$ATTEMPT_STATUS"

CURRENT_STAGE=production_terminal_gate
if [[ $PRODUCTION_GATE_MODE == verified_segments ]]; then
  : "${SOURCE_VALIDATION_JSON:?set SOURCE_VALIDATION_JSON for verified_segments}"
  "$PYTHON_CMD" - "$SOURCE_VALIDATION_JSON" "$TPR" "$XTC" \
    "$EXPECTED_FRAMES" "$EXPECTED_FINAL_TIME_PS" \
    > "$ATTEMPT_DIR/production_archive_check.log" 2>&1 <<'PY'
import hashlib, json, sys
from pathlib import Path
certificate, tpr, xtc, frames, end_ps = sys.argv[1:]
data = json.loads(Path(certificate).read_text())
assert data['status'] == 'PASS'
assert data['frames'] == int(frames)
assert data['unique_frames'] == int(frames)
assert data['first_ps'] == 0 and data['last_ps'] == float(end_ps)
assert data['missing_grid_points'] == 0
assert data['topology']['path'] == tpr and data['trajectory']['path'] == xtc
for item in [data['topology'], data['trajectory'], *data['evidence']]:
    h = hashlib.sha256()
    with Path(item['path']).open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            h.update(block)
    assert h.hexdigest() == item['sha256'], item['path']
    print('PASS', item['path'], item['sha256'])
PY
elif [[ $PRODUCTION_GATE_MODE == archive ]]; then
latest=$(
  awk -F '\t' '
    NR == 1 {
      if ($0 != "observed_at\tstate\tsource\tdetail") invalid=1
      next
    }
    NF != 4 { invalid=1; next }
    { observed=$1; state=$2; source=$3; detail=$4 }
    END {
      if (invalid || state == "") exit 2
      printf "%s\t%s\t%s\t%s\n", observed, state, source, detail
    }
  ' "$STATE_EVENTS"
)
IFS=$'\t' read -r terminal_observed terminal_state terminal_source terminal_detail <<< "$latest"
[[ $terminal_state == TERMINAL_NORMAL ]]
grep -Fxq $'production_completed\tYES' "$PROD_STATUS"
archive_manifest=$(
  awk -v RS=';' -F= '$1 == "archive_manifest" { print $2; exit }' \
    <<< "$terminal_detail"
)
expected_archive_sha=$(
  awk -v RS=';' -F= '$1 == "archive_manifest_sha256" { print $2; exit }' \
    <<< "$terminal_detail"
)
[[ -s "$archive_manifest" ]]
[[ $(sha256sum "$archive_manifest" | awk '{print $1}') == "$expected_archive_sha" ]]
(
  cd "$RUN_ROOT"
  sha256sum -c "$archive_manifest"
) > "$ATTEMPT_DIR/production_archive_check.log" 2>&1
else
  echo "ERROR: unknown PRODUCTION_GATE_MODE: $PRODUCTION_GATE_MODE" >&2
  exit 64
fi

CURRENT_STAGE=required_inputs
if [[ -z $INDEX_FILE ]]; then
  INDEX_FILE=$(
    awk '$2 ~ /\/index_final\.ndx$/ { print $2; exit }' \
      "$SOURCE_IDENTITY_MANIFEST"
  )
fi
for required in "$TPR" "$XTC" "$INDEX_FILE" "$PYTHON_CMD"; do
  [[ -s "$required" ]]
done
for output in "$CLUSTER_XTC" "$PROTEIN_XTC" "$REFERENCE_PDB"; do
  if [[ -e "$output" ]]; then
    printf '%s\n' "$output" > "$ATTEMPT_DIR/refused_existing_output.txt"
    echo "ERROR: processed output already exists: $output" >&2
    exit 66
  fi
done

CURRENT_STAGE=analysis_index
base_group_count=$(grep -c '^[[:space:]]*\[' "$INDEX_FILE")
backbone_group_number=$base_group_count
fit_group_number=$((base_group_count + 1))
printf 'a N | a CA | a C | a O\n"%s" & %s\nname %s %s\nq\n' \
  "$RECEPTOR_GROUP" "$backbone_group_number" "$fit_group_number" "$FIT_GROUP" | \
  "$GMX_CMD" make_ndx \
    -f "$TPR" -n "$INDEX_FILE" -o "$ANALYSIS_INDEX" \
    > "$ATTEMPT_DIR/make_analysis_index.log" 2>&1

"$PYTHON_CMD" - \
  "$ANALYSIS_INDEX" "$SOLUTION_GROUP" "$FIT_GROUP" \
  "$EXPECTED_SOLUTION_ATOMS" "$EXPECTED_FIT_ATOMS" \
  > "$ATTEMPT_DIR/index_gate.tsv" <<'PY'
from pathlib import Path
import sys

path, solution_group, fit_group, expected_solution, expected_fit = sys.argv[1:]
groups = {}
current = None
for raw in Path(path).read_text().splitlines():
    line = raw.strip()
    if line.startswith("[") and line.endswith("]"):
        current = line[1:-1].strip()
        groups[current] = []
    elif current and line:
        groups[current].extend(int(value) for value in line.split())
expected = {solution_group: int(expected_solution), fit_group: int(expected_fit)}
print("group\tactual\texpected\tstatus")
for name, wanted in expected.items():
    actual = len(groups.get(name, []))
    status = "PASS" if actual == wanted else "FAIL"
    print(f"{name}\t{actual}\t{wanted}\t{status}")
    if status == "FAIL":
        raise SystemExit(f"index group {name} has {actual} atoms; expected {wanted}")
PY

CURRENT_STAGE=trjconv_cluster
if [[ $PBC_ROUTE == whole_nojump ]]; then
  # This route requires SOLU to retain source atom order as a contiguous prefix.
  # The config-driven segmented-input validator checks that correspondence.
  printf '%s\n' "$SOLUTION_GROUP" | "$GMX_CMD" convert-tpr \
    -s "$TPR" -n "$ANALYSIS_INDEX" -o "$OUT_DIR/solution.tpr" \
    > "$ATTEMPT_DIR/convert_solution_tpr.log" 2>&1
  printf '%s\n%s\n' "$RECEPTOR_GROUP" "$SOLUTION_GROUP" | "$GMX_CMD" trjconv \
    -s "$TPR" -f "$XTC" -n "$ANALYSIS_INDEX" \
    -o "$OUT_DIR/prod_whole.xtc" -pbc mol -center \
    > "$ATTEMPT_DIR/trjconv_1_whole.log" 2>&1
  printf '%s\n' "$SOLUTION_GROUP" | "$GMX_CMD" trjconv \
    -s "$OUT_DIR/solution.tpr" -f "$OUT_DIR/prod_whole.xtc" -n "$ANALYSIS_INDEX" \
    -o "$CLUSTER_XTC" -pbc nojump \
    > "$ATTEMPT_DIR/trjconv_1_nojump.log" 2>&1
  PROCESSING_TPR="$OUT_DIR/solution.tpr"
elif [[ $PBC_ROUTE == cluster ]]; then
printf '%s\n%s\n' "$SOLUTION_GROUP" "$SOLUTION_GROUP" | \
  "$GMX_CMD" trjconv \
    -s "$TPR" -f "$XTC" -n "$ANALYSIS_INDEX" \
    -o "$CLUSTER_XTC" -pbc cluster \
    > "$ATTEMPT_DIR/trjconv_1_cluster.log" 2>&1
  PROCESSING_TPR="$TPR"
else
  echo "ERROR: unknown PBC_ROUTE: $PBC_ROUTE" >&2
  exit 64
fi

CURRENT_STAGE=trjconv_fit
printf '%s\n%s\n' "$FIT_GROUP" "$SOLUTION_GROUP" | \
  "$GMX_CMD" trjconv \
    -s "$PROCESSING_TPR" -f "$CLUSTER_XTC" -n "$ANALYSIS_INDEX" \
    -o "$PROTEIN_XTC" -fit rot+trans \
    > "$ATTEMPT_DIR/trjconv_2_fit.log" 2>&1

CURRENT_STAGE=trjconv_reference
printf '%s\n' "$SOLUTION_GROUP" | \
  "$GMX_CMD" trjconv \
    -s "$PROCESSING_TPR" -f "$PROTEIN_XTC" -n "$ANALYSIS_INDEX" \
    -o "$REFERENCE_PDB" -dump 0 \
    > "$ATTEMPT_DIR/trjconv_3_reference.log" 2>&1

CURRENT_STAGE=processed_sanity
"$GMX_CMD" check -f "$CLUSTER_XTC" \
  > "$ATTEMPT_DIR/gmx_check_cluster.log" 2>&1
"$GMX_CMD" check -f "$PROTEIN_XTC" \
  > "$ATTEMPT_DIR/gmx_check_protein.log" 2>&1
"$PYTHON_CMD" - \
  "$ATTEMPT_DIR/gmx_check_cluster.log" \
  "$ATTEMPT_DIR/gmx_check_protein.log" \
  "$REFERENCE_PDB" "$EXPECTED_SOLUTION_ATOMS" \
  "$EXPECTED_FRAMES" "$EXPECTED_FINAL_TIME_PS" \
  > "$ATTEMPT_DIR/processing_summary.tsv" <<'PY'
from pathlib import Path
import re
import sys

cluster_path, protein_path, pdb_path, expected_atoms, expected_frames, expected_time = sys.argv[1:]
expected_atoms = int(expected_atoms)
expected_frames = int(expected_frames)
expected_time = float(expected_time)

def inspect_check(path):
    text = Path(path).read_text(errors="replace").replace("\r", "\n")
    atoms = re.search(r"# Atoms\s+(\d+)", text)
    last = re.findall(r"Last frame\s+(\d+)\s+time\s+([0-9.]+)", text)
    if not atoms or not last:
        raise SystemExit(f"missing GROMACS check fields in {path}")
    return int(atoms.group(1)), int(last[-1][0]) + 1, float(last[-1][1])

cluster = inspect_check(cluster_path)
protein = inspect_check(protein_path)
for label, observed in (("cluster", cluster), ("protein", protein)):
    if observed[0] != expected_atoms:
        raise SystemExit(f"{label} XTC atom count mismatch")
    if observed[1] != expected_frames:
        raise SystemExit(f"{label} XTC frame count mismatch")
    if abs(observed[2] - expected_time) > 0.01:
        raise SystemExit(f"{label} XTC final time mismatch")

pdb_atoms = sum(
    line.startswith(("ATOM  ", "HETATM"))
    for line in Path(pdb_path).read_text(errors="replace").splitlines()
)
if pdb_atoms != expected_atoms:
    raise SystemExit("reference PDB atom count mismatch")

print("key\tvalue")
print("status\tPASS")
print(f"processed_atoms\t{expected_atoms}")
print(f"processed_frames\t{expected_frames}")
print(f"final_time_ps\t{expected_time:.3f}")
print(f"reference_pdb_atoms\t{pdb_atoms}")
PY

CURRENT_STAGE=archive
(
  cd "$RUN_ROOT"
  find "processed/rep$REP" -maxdepth 1 -type f -print0 \
    | sort -z | xargs -0 sha256sum \
    > "$ATTEMPT_DIR/processed_outputs.sha256"
  sha256sum -c "$ATTEMPT_DIR/processed_outputs.sha256" \
    > "$ATTEMPT_DIR/processed_outputs_check.log"
)
find "$ATTEMPT_DIR" -maxdepth 1 -type f \
  ! -name 'postprocess_evidence.sha256' \
  ! -name 'postprocess_status.tsv' \
  -print0 | sort -z | xargs -0 sha256sum \
  > "$ATTEMPT_DIR/postprocess_evidence.sha256"

CURRENT_STAGE=terminal_promotion
{
  printf 'key\tvalue\n'
  printf 'status\tPASS\n'
  printf 'stage\tpostprocess_complete\n'
  printf 'completed_at\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'topology\t%s\n' "$REFERENCE_PDB"
  printf 'trajectory\t%s\n' "$PROTEIN_XTC"
  printf 'processed_atoms\t%s\n' "$EXPECTED_SOLUTION_ATOMS"
  printf 'processed_frames\t%s\n' "$EXPECTED_FRAMES"
  printf 'final_time_ps\t%s\n' "$EXPECTED_FINAL_TIME_PS"
} > "$ATTEMPT_STATUS"
status_tmp=$(mktemp "$OUT_DIR/.terminal_status.tsv.XXXXXX")
{
  printf 'key\tvalue\n'
  printf 'status\tPOSTPROCESS_COMPLETE\n'
  printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
  printf 'completed_at\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'evidence_dir\t%s\n' "$ATTEMPT_DIR"
  printf 'topology\t%s\n' "$REFERENCE_PDB"
  printf 'trajectory\t%s\n' "$PROTEIN_XTC"
} > "$status_tmp"
mv -f "$status_tmp" "$OUT_DIR/terminal_status.tsv"
trap - ERR
printf 'status\tPASS\nattempt_id\t%s\nevidence_dir\t%s\n' "$ATTEMPT_ID" "$ATTEMPT_DIR"
