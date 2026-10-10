#!/bin/bash
set -euo pipefail

ALIGNMENT_ROOT="/Users/yangruoxi/Projects/Docking-Research-Lab/alignment"
TMALIGN_BIN="$ALIGNMENT_ROOT/tools/tmalign/bin/TMalign"
TMCORE_DIR="$ALIGNMENT_ROOT/tm_core"
RESULTS_DIR="$ALIGNMENT_ROOT/alignments"

if [[ ! -x "$TMALIGN_BIN" ]]; then
    echo "TM-align executable is missing or not executable: $TMALIGN_BIN" >&2
    exit 1
fi

run_pair() {
    local pair_id="$1"
    local mobile_name="$2"
    local reference_name="$3"
    local mobile="$TMCORE_DIR/$mobile_name"
    local reference="$TMCORE_DIR/$reference_name"
    local outdir="$RESULTS_DIR/$pair_id"

    if [[ ! -f "$mobile" ]]; then
        echo "Missing mobile TM-core: $mobile" >&2
        exit 1
    fi
    if [[ ! -f "$reference" ]]; then
        echo "Missing reference TM-core: $reference" >&2
        exit 1
    fi
    if [[ -e "$outdir/tmalign.stdout.txt" || -e "$outdir/rotation_matrix.txt" ]]; then
        echo "Existing result detected; refusing to overwrite: $outdir" >&2
        exit 1
    fi

    mkdir -p "$outdir"

    "$TMALIGN_BIN" \
        "$mobile" \
        "$reference" \
        -a T \
        -m "$outdir/rotation_matrix.txt" \
        -o "$outdir/superposition" \
        > "$outdir/tmalign.stdout.txt" \
        2> "$outdir/tmalign.stderr.txt"

    if [[ -s "$outdir/tmalign.stderr.txt" ]]; then
        echo "TM-align wrote to stderr: $outdir/tmalign.stderr.txt" >&2
        exit 1
    fi
    if ! grep -q "Aligned length=" "$outdir/tmalign.stdout.txt"; then
        echo "TM-align summary is missing: $outdir/tmalign.stdout.txt" >&2
        exit 1
    fi

    echo "Completed: $pair_id"
}

mkdir -p "$RESULTS_DIR"

run_pair \
    "01_TWF154_Gpr2_vs_GprC" \
    "TWF154_Gpr2_TGJ68930.1_TMcore.pdb" \
    "Aflagrans_GprC_A0A437AGY2_TMcore.pdb"

run_pair \
    "02_TWF154_Gpr3_vs_GprC" \
    "TWF154_Gpr3_TGJ67963.1_TMcore.pdb" \
    "Aflagrans_GprC_A0A437AGY2_TMcore.pdb"

run_pair \
    "03_TWF154_Gpr2_vs_SRBC64" \
    "TWF154_Gpr2_TGJ68930.1_TMcore.pdb" \
    "Celegans_N2_SRBC64_G5ECV4_TMcore.pdb"

run_pair \
    "04_TWF154_Gpr3_vs_SRBC64" \
    "TWF154_Gpr3_TGJ67963.1_TMcore.pdb" \
    "Celegans_N2_SRBC64_G5ECV4_TMcore.pdb"

run_pair \
    "06_TWF154_Gpr3_vs_ATCC24927_Gpr3" \
    "TWF154_Gpr3_TGJ67963.1_TMcore.pdb" \
    "ATCC24927_Gpr3_G1XJN1_TMcore.pdb"

echo "All five remaining TM-align comparisons completed."
