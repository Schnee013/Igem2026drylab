# Gpr2 WT + ASCR18 E2 Short Benchmark Command Plan

> Date: 2026-07-05
>
> Scope: one short E2 benchmark for `Gpr2_WT + ASCR18` from the locally archived post-step6 structure.

## Purpose

Measure the E2 A100 short-production GPU utilization and practical production speed for the WT single-GPR holo system before expanding mutant GPR MD work from Decision 005.

This plan is a benchmark/resource gate only. It is not a full production run and is not a scientific stability conclusion.

## Authority Chain

- `docs/decisions/005-md-compute-triage-after-chctrl.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/ops/nkuliulab-e2-cloud-server.md`
- `environments/e2-md-gromacs.md`
- `docs/logs/2026-04-16.md`

## Selected System

Use `experiments/md-simulation/systems/Gpr2_WT/gromacs/` first because it has the complete local short-benchmark input set:

- `step6.6.gro`
- `topol_phase3.top`
- `index.ndx`
- `step7_production.mdp`
- `ASCR18.itp`
- `posre_ASCR18.itp`
- `toppar/`

`Gpr3_WT` is not included in this first package because its local `gromacs/` directory lacks `index.ndx`; it needs a separate input-gate repair before an equivalent benchmark.

## Remote Location

- Host: `nkuliulab-e2`
- Run root: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705`
- Input package: `input/gromacs/`
- Outputs: `production_smoke/`, `logs/`, `sanity/`

## Resource Gate

Before running `mdrun`, check `nvidia-smi`. Do not launch if another GPU process is active or if GPU utilization/memory indicate current use by another user.

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

## Acceptance Evidence

Required local result evidence after download:

- GROMACS version log
- `grompp` log with no fatal error
- `mdrun` log with `Performance:` line
- `nvidia_smi_production_short.csv`
- parsed `production_short_summary.tsv`
- `.tpr`, `.log`, `.edr`, `.xtc`, `.cpt`, `.gro`
- `gmx check` logs for trajectory and energy
- energy extraction log
- checksum manifest

## Interpretation Boundary

The endpoint metric is practical E2 benchmark evidence for this WT holo system: GPU utilization and short-production speed. It should not be used as a mutant stability result, production-length recommendation, or full E2 scheduling decision without follow-up gates.
