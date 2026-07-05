# MD Production Sites Matrix

> Last verified: 2026-06-26
> Scope: historical site matrix for the paused unified chimeric MD clean-start rerun; future MD work must follow [决策 005](../docs/decisions/005-md-compute-triage-after-chctrl.md) and pass fresh resource/benchmark gates.
> Authority: this file records site-level environment targets and provenance gates. Runtime evidence remains in preflight logs, conda snapshots, Slurm logs, GROMACS logs, checksums, and synced result directories.

## Current Decision

2026-06-26: chimeric candidate full-production is paused after clarifying that control/chctrl 3 completed replicates belong to the old Slurm route, while E2 has chctrl rep1 evidence only. E2 is the only practical current compute route and prior A100 usage was too disruptive for a shared server. Do not launch new Ch-1/Ch-2/Ch-4 full-production jobs from this matrix without a new decision.

Historical 2026-05-30 route: use E2 as the primary production site and add the old Slurm RTX 5090 server only as a validated secondary site. Both sites must use the same clean-start inputs, the same GROMACS conda-forge production pin, the same production MDP generator, and the same smoke/benchmark/completion gates.

Old Slurm `2025.2-spack` production logs remain historical evidence pointers only. They are not part of the new rerun provenance and must not be merged with the new `2025.4` rerun outputs.

## Site Matrix

| Site | Role | Remote base | Production env target | Command | Status | Evidence pointers |
|---|---|---|---|---|---|---|
| NKULiulab E2 A100 | Historical primary production site; current shared-resource MD test site | `/ifs1/User/dengwei/igem/md-simulation` | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda`; `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` | Chimeric candidate full-production paused 2026-06-26; E2 has chctrl rep1 evidence only; future mutant GPR or optimized chimeric tests require resource estimate and short benchmark first | `environments/e2-md-gromacs.md`; `experiments/md-simulation/results/e2_preflight/`; `docs/logs/2026-05-29.md`; `docs/logs/2026-05-30.md`; `docs/logs/2026-06-02.md`; `docs/logs/2026-06-26.md` |
| Old Slurm RTX 5090 | Validated secondary candidate | default target `/home/guest/igem/md-simulation` | `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda`; target pin `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` | `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` after validation | Read-only preflight found node3 RTX5090 schedulable and target env absent/clean, but `conda`/`mamba`/`micromamba` are not available; blocked before same-pin env validation, smoke, benchmark, or production | `experiments/md-simulation/results/slurm_preflight/slurm_chimeric_preflight_20260530_slurm5090_readonly.log`; `docs/logs/2026-05-30.md`; `docs/ops/archives/slurm-md-server.md` for historical-only hardware and pitfall pointers |

## Uniform Production Pin

| Field | Required value |
|---|---|
| GROMACS package | `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` |
| Build family | conda-forge `linux-64` `mpi_openmpi_cuda` |
| Command contract | `gmx_mpi`, not `gmx` |
| Key solved dependency family | CUDA runtime/toolkit 12.9, OpenMPI 5.0.8, FFTW 3.3.11, hwloc 2.12.x |
| MDP generator | `experiments/md-simulation/scripts/e2_make_chimeric_prod_mdp.py` |
| Full production length | Historical rerun plan: 500 ns per replicate unless a later gate changes it |
| Replicates | Historical rerun plan: chctrl + Ch-1 + Ch-2 + Ch-4, 3 reps each; E2 evidence currently covers chctrl rep1 only |

If Slurm cannot run this exact pin on RTX 5090 without CUDA/PTX errors, Slurm stays out of production unless a separate異環境 batch is explicitly approved.

## Result Layout Rule

Rerun outputs must include a site/run id under each system's `raw/` directory:

| Site | Required result run id pattern | Example |
|---|---|---|
| E2 | `YYYYMMDD_e2_rerun` | `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/20260529_e2_rerun/rep1/` |
| Slurm RTX 5090 | `YYYYMMDD_slurm5090_rerun` | `experiments/md-simulation/results/chimeric-gpr3-aogpa2-c37/raw/20260530_slurm5090_rerun/rep1/` |

The old chctrl Slurm outputs remain at `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/rep{1,2,3}/prod.*` as historical evidence only.

## Gates For Slurm Admission

1. Read-only preflight records login host, scheduler state, node3/GPU availability, storage, environment tools, and any existing GROMACS command without submitting jobs. Current evidence: login/scheduler preflight passed, `sbatch --test-only` accepted an RTX5090 request, and no real Slurm job was submitted.
2. Same-pin environment validation records the exact conda package list and `gmx_mpi --version` output. Current blocker: no conda-family package manager is available in the Slurm user environment, so this gate has not started. Later options such as user-local micromamba bootstrap, Apptainer, or source build require a separate decision before any Slurm production admission.
3. RTX 5090 smoke confirms `grompp`, GPU selection, final coordinates, checkpoint writing, and XTC readability.
4. Benchmark writes a comparable `summary.tsv` with system, atoms, GPU, threads, GROMACS build, and ns/day.
5. First production replicate is accepted only after 10-30 minutes of step progression, checkpoint/log updates, GPU use, and no fatal/error lines.
6. Completion acceptance requires normal termination, nonempty `prod.log/cpt/gro/xtc/edr/tpr`, checksums, `gmx check`, and site/env provenance in the result directory.

## Production Scheduling Rule

- 2026-06-26 后不要从本历史矩阵直接启动新的 chimeric full-production；任何新 MD 先做资源估算和短程 benchmark。
- Slurm may run only replicates that have not started on E2.
- Do not place all replicates of one system on the same hardware when avoidable; interleave E2 and Slurm so site effects are not perfectly confounded with system effects.
- Run at most one full MD job per GPU.
