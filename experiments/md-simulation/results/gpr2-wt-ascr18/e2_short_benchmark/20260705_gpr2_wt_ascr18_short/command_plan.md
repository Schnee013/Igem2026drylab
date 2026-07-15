# Gpr2 WT + ASCR18 E2 Short Benchmark Command Plan

> Date: 2026-07-05
>
> Scope: one short E2 benchmark for `Gpr2_WT + ASCR18` from the locally archived post-step6 structure.

## Purpose

Measure the E2 A100 short-production GPU utilization and practical production speed for the WT single-GPR holo system before expanding mutant GPR MD work from Decision 005.

This plan produces benchmark/resource-gate evidence only. Full production status and scientific stability conclusions require independent production trajectories and analysis.

## Authority Chain

- `docs/decisions/005-md-compute-triage-after-chctrl.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/ops/nkuliulab-e2-cloud-server.md`
- `environments/e2-md-gromacs.md`
- `docs/logs/2026-04-16.md`

## Selected System

Use `experiments/md-simulation/systems/Gpr2_WT/gromacs/` first because it has the required local short-benchmark input set:

- `step6.6.gro`
- `topol_phase3.top`
- `index.ndx`
- `step7_production.mdp`
- `ASCR18.itp`
- `posre_ASCR18.itp`
- `toppar/`

This first package covers only `Gpr2_WT + ASCR18`. An equivalent `Gpr3_WT` benchmark requires a separate input-gate repair because its local `gromacs/` directory lacks `index.ndx`.

The repaired benchmark index is generated locally as `index.fixed.ndx` from
`step6.6.gro` with `experiments/md-simulation/scripts/assemble_complex.py::build_index`,
then installed in the remote benchmark package as `input/gromacs/index.ndx`.
Scope: benchmark-package repair only; the archived source
`Gpr2_WT/gromacs/index.ndx` remains unchanged.

## Remote Location

- Host: `nkuliulab-e2`
- Run root: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705`
- Input package: `input/gromacs/`
- Outputs: `production_smoke/`, `logs/`, `sanity/`

## Resource Gate

Before running `mdrun`, check `nvidia-smi`. Launch only when no other GPU process is active and GPU utilization/memory show an available shared-GPU window.

Resource settings:

- one `gmx_mpi` process
- `OMP_NUM_THREADS=24`
- `-ntomp 24`
- `-pin on`
- `-nb gpu -pme gpu -bonded gpu`

## Short Production Settings

Create `production_smoke/gpr2_wt_ascr18_short.mdp` from local `step7_production.mdp` with these benchmark-only changes:

- `nsteps = 50000`
- `continuation = no`
- `gen-vel = yes`
- `gen-temp = 303.15`
- `gen-seed = 20260705`

Nominal duration: `100 ps` at `dt = 0.002 ps`.

## Grompp Warning Gate

`grompp` is allowed `-maxwarn 11` only for the reviewed CHARMM-GUI/CGenFF
`cgenff_ASCR18.itp` duplicate type-9 dihedral parameter warnings. The run script
checks the post-`grompp` log before any `mdrun` launch and accepts launch only when:

- `grompp` reports no fatal error;
- the warning count is exactly 11;
- every warning source is `cgenff_ASCR18.itp`;
- every warning body is the known duplicate type-9 dihedral parameter warning.

Gate scope: this WT ASCR18 short benchmark only. Mutant production inputs require
a separate package-specific warning review.

## Acceptance Evidence

Required local result evidence after download:

- GROMACS version log
- `grompp` log with no fatal error
- `grompp_warning_gate.txt`
- `mdrun` log with `Performance:` line
- `nvidia_smi_production_short.csv`
- parsed `production_short_summary.tsv`
- `.tpr`, `.log`, `.edr`, `.xtc`, `.cpt`, `.gro`
- `gmx check` logs for trajectory and energy
- energy extraction log
- checksum manifest

## Interpretation Boundary

Allowed use: practical E2 benchmark evidence for this WT holo system, limited to GPU utilization and short-production speed. Mutant stability, production length, and full E2 scheduling decisions require follow-up gates.
