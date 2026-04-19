#!/usr/bin/env bash
# Batch pdb2gmx for 5 in-place mutants (Mac local, chimeric environment).
# Generates processed.gro + PROA.itp per mutant under systems/{mutant}/pdb2gmx/.
#
# Dependencies: gmx (conda-forge/gromacs in chimeric env), python3
# Usage: conda activate chimeric && bash experiments/md-simulation/scripts/run_pdb2gmx_batch.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SYSTEMS_DIR="$PROJECT_ROOT/experiments/md-simulation/systems"
PREPARE_SCRIPT="$SCRIPT_DIR/prepare_pdb2gmx_output.py"

# 5 mutant definitions: DIR PDB WT EXPECTED_ATOMS MUT_RESID MUT_RESNAME
# Expected atoms from CHARMM36m rtp: WT count - (old_res_atoms - new_res_atoms)
# Gpr3 WT=6313, Gpr2 WT=6397
MUTANTS=(
  "gpr3-F170E-ascr18 Gpr3_F170E_protein.pdb Gpr3 6308 170 GLU"
  "gpr3-I141A-ascr18 Gpr3_I141A_protein.pdb Gpr3 6304 141 ALA"
  "gpr2-M327A-ascr18 Gpr2_M327A_protein.pdb Gpr2 6390 327 ALA"
  "gpr2-M327D-ascr18 Gpr2_M327D_protein.pdb Gpr2 6392 327 ASP"
  "gpr2-R59F-ascr18  Gpr2_R59F_protein.pdb  Gpr2 6393 59  PHE"
)

FAIL_COUNT=0

for spec in "${MUTANTS[@]}"; do
  read -r DIR PDB WT EXPECTED_ATOMS MUT_RESID MUT_RESNAME <<< "$spec"

  echo ""
  echo "================================================================"
  echo "Processing: $DIR ($PDB)"
  echo "================================================================"

  SYS_DIR="$SYSTEMS_DIR/$DIR"
  PDB_FILE="$SYS_DIR/$PDB"
  WORK_DIR="$SYS_DIR/pdb2gmx"

  if [ ! -f "$PDB_FILE" ]; then
    echo "ERROR: PDB not found: $PDB_FILE"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi

  mkdir -p "$WORK_DIR"

  # ── Step 1: HIS → HSD safety check ──
  echo "--- Step 1: HIS → HSD safety check ---"
  if grep -q "^ATOM.\{12\} HIS " "$PDB_FILE" 2>/dev/null; then
    echo "  Found HIS residues, converting to HSD..."
    sed -i.bak 's/ HIS / HSD /g' "$PDB_FILE"
    rm -f "$PDB_FILE.bak"
  else
    echo "  No HIS found (all HSD already) — no-op"
  fi

  # ── Step 2: Run pdb2gmx ──
  # -ter: interactive terminal selection (charmm36m ethers.n.tdb defines MET1
  #   ether patch as option 0; we need option 1 = NH3+ for proteins)
  # Input: "1" = NH3+ N-terminus, "0" = COO- C-terminus
  echo "--- Step 2: gmx pdb2gmx ---"
  if ! printf "1\n0\n" | gmx pdb2gmx \
    -f "$PDB_FILE" \
    -o "$WORK_DIR/processed.gro" \
    -p "$WORK_DIR/topol.top" \
    -i "$WORK_DIR/posre.itp" \
    -ff charmm36m -water tip3p -ignh -ter \
    > "$WORK_DIR/pdb2gmx.log" 2>&1; then
    echo "  ERROR: pdb2gmx failed"
    tail -20 "$WORK_DIR/pdb2gmx.log"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi
  echo "  pdb2gmx completed"

  if [ ! -f "$WORK_DIR/topol.top" ]; then
    echo "  ERROR: no topol.top produced"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi

  # ── Step 3: Convert topol.top → PROA.itp ──
  echo "--- Step 3: Convert topol.top → PROA.itp ---"
  if ! python3 "$PREPARE_SCRIPT" \
    --topol "$WORK_DIR/topol.top" \
    --output-itp "$WORK_DIR/PROA.itp"; then
    echo "  ERROR: prepare_pdb2gmx_output.py failed"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi

  # ── Step 4: Verification ──
  echo "--- Step 4: Verification ---"
  ERRORS=0

  # 4a. GRO atom count
  GRO_ATOMS=$(sed -n '2p' "$WORK_DIR/processed.gro" | tr -d ' ')
  if [ "$GRO_ATOMS" -eq "$EXPECTED_ATOMS" ]; then
    echo "  ✓ GRO atoms: $GRO_ATOMS (expected $EXPECTED_ATOMS)"
  else
    echo "  ✗ GRO atoms: $GRO_ATOMS (expected $EXPECTED_ATOMS)"
    ERRORS=$((ERRORS + 1))
  fi

  # 4b. moleculetype = PROA
  if grep -q "^PROA" "$WORK_DIR/PROA.itp"; then
    echo "  ✓ moleculetype = PROA"
  else
    echo "  ✗ moleculetype ≠ PROA"
    ERRORS=$((ERRORS + 1))
  fi

  # 4c. POSRES macros
  if grep -q 'POSRES_FC_BB' "$WORK_DIR/PROA.itp" && \
     grep -q 'POSRES_FC_SC' "$WORK_DIR/PROA.itp"; then
    echo "  ✓ POSRES_FC_BB + POSRES_FC_SC macros present"
  else
    echo "  ✗ Missing POSRES macros"
    ERRORS=$((ERRORS + 1))
  fi

  # 4d. cmap section (CHARMM36m signature)
  if grep -q '^\[ cmap \]' "$WORK_DIR/PROA.itp"; then
    echo "  ✓ [ cmap ] section present"
  else
    echo "  ✗ Missing [ cmap ] section"
    ERRORS=$((ERRORS + 1))
  fi

  # 4e. Exactly 1 posres section (negative check: no stray pdb2gmx water posres)
  POSRES_COUNT=$(grep -c '^\[ position_restraints \]' "$WORK_DIR/PROA.itp" || true)
  if [ "$POSRES_COUNT" -eq 1 ]; then
    echo "  ✓ Exactly 1 [ position_restraints ] section"
  else
    echo "  ✗ Found $POSRES_COUNT [ position_restraints ] sections (expected 1)"
    ERRORS=$((ERRORS + 1))
  fi

  # 4f. Mutation residue in [ atoms ]
  MUT_COUNT=$(grep -cE "[[:space:]]${MUT_RESID}[[:space:]]+${MUT_RESNAME}[[:space:]]" "$WORK_DIR/PROA.itp" || true)
  if [ "$MUT_COUNT" -gt 0 ]; then
    echo "  ✓ Residue $MUT_RESID = $MUT_RESNAME ($MUT_COUNT atoms)"
  else
    echo "  ✗ Residue $MUT_RESID ≠ $MUT_RESNAME"
    ERRORS=$((ERRORS + 1))
  fi

  if [ "$ERRORS" -gt 0 ]; then
    echo "  ** $ERRORS verification errors **"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    echo "  All verifications passed ✓"
  fi
done

echo ""
echo "================================================================"
echo "Summary: $(( ${#MUTANTS[@]} - FAIL_COUNT ))/${#MUTANTS[@]} succeeded"
echo "================================================================"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi
