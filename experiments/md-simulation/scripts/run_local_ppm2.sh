#!/usr/bin/env bash
# Build the official downloaded PPM2 source and orient one fixed parent.
set -euo pipefail
cd "$1"
export OMP_NUM_THREADS=1
sha256sum ./*.f res.lib input.inp Gpr2parent.pdb > input.sha256
gfortran --version > compiler_version.txt
gfortran -O2 -std=legacy -fallow-argument-mismatch -o immers \
  opm.f min.f rmsd.f solva.f readpdb.f read_small.f watface.f \
  tilting.f locate.f profile.f hbcor.f deftm.f orient.f find_segm.f \
  > compile.log 2>&1
printf 'time_utc\tstate\tsource\tdetail\n' > run_state_events.tsv
printf '%s\tRUNNING_VERIFIED\tinput.sha256\tPPM2 parent orientation started\n' "$(date -u +%FT%TZ)" >> run_state_events.tsv
./immers < input.inp > ppm.log 2>&1
test -s Gpr2parentout.pdb
sha256sum Gpr2parentout.pdb ppm.log > output.sha256
printf '%s\tTERMINAL_NORMAL\toutput.sha256\tPPM2 output present; orientation audit still required\n' "$(date -u +%FT%TZ)" >> run_state_events.tsv
