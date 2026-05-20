#!/bin/bash
# Install ADFR Suite from a pre-downloaded tarball on a Slurm compute node.
# Login-node work before this script: upload the tarball to
# /home/guest/installers/ADFRsuite_x86_64Linux_1.1dev.tar.gz.

#SBATCH --job-name=install_adfr
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=install_adfr_suite_%j.log
#SBATCH --error=install_adfr_suite_%j.err

set -euo pipefail

TARBALL="/home/guest/installers/ADFRsuite_x86_64Linux_1.1dev.tar.gz"
EXPECTED_MD5="59d6872b568ef7a2b23107c760465d7b"
INSTALL_PARENT="/home/guest/opt"
ADFR_BIN="${INSTALL_PARENT}/bin"
STAGE="/home/guest/tmp/adfr-install-${SLURM_JOB_ID:-manual}"
ENV_FILE="/home/guest/drylab-docking/experiments/docking-repro/slurm/adfr_env.sh"

echo "== Host =="
hostname
date

echo "== Input =="
test -f "$TARBALL"
actual_md5="$(md5sum "$TARBALL" | awk '{print $1}')"
echo "md5=$actual_md5"
if [[ "$actual_md5" != "$EXPECTED_MD5" ]]; then
  echo "ERROR: unexpected MD5 for $TARBALL" >&2
  exit 2
fi

echo "== Install =="
if [[ -x "$ADFR_BIN/prepare_receptor" || -f "$ADFR_BIN/prepare_receptor4.py" ]]; then
  echo "Existing ADFR install found: $INSTALL_PARENT"
else
  echo "== Extract =="
  mkdir -p "$INSTALL_PARENT" "$STAGE"
  tar -xzf "$TARBALL" -C "$STAGE"

  source_root="$(find "$STAGE" -maxdepth 1 -type d -name 'ADFRsuite_*' | head -n 1)"
  if [[ -z "$source_root" || ! -x "$source_root/install.sh" ]]; then
    echo "ERROR: ADFR install.sh not found after extraction" >&2
    exit 3
  fi

  (
    cd "$source_root"
    ./install.sh -d "$INSTALL_PARENT" -c 0 -l
  )
fi

if [[ ! -d "$ADFR_BIN" ]]; then
  echo "ERROR: expected ADFR bin missing: $ADFR_BIN" >&2
  exit 4
fi

cat > "$ENV_FILE" <<EOF
export ADFR_BIN="$ADFR_BIN"
export PATH="\$ADFR_BIN:\$PATH"
EOF

echo "== Verify =="
source "$ENV_FILE"
echo "ADFR_BIN=$ADFR_BIN"
test -x "$ADFR_BIN/prepare_receptor" || test -f "$ADFR_BIN/prepare_receptor4.py"
ls -l "$ADFR_BIN"/prepare_receptor*
echo "ADFR install PASS"
