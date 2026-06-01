# MD Production Sites Matrix

> Last verified: 2026-05-30
> Scope: unified chimeric MD clean-start rerun for chctrl + Ch-1 + Ch-2 + Ch-4.
> Authority: this file records site-level environment targets and provenance gates. Runtime evidence remains in preflight logs, conda snapshots, Slurm logs, GROMACS logs, checksums, and synced result directories.

## Current Decision

Use E2 as the primary production site and add the old Slurm RTX 5090 server only as a validated secondary site. Both sites must use the same clean-start inputs, the same GROMACS conda-forge production pin, the same production MDP generator, and the same smoke/benchmark/completion gates.

Old Slurm `2025.2-spack` production logs remain historical evidence pointers only. They are not part of the new rerun provenance and must not be merged with the new `2025.4` rerun outputs.

## Site Matrix

| Site | Role | Remote base | Production env target | Command | Status | Evidence pointers |
|---|---|---|---|---|---|---|
| NKULiulab E2 A100 | Primary production site | `/ifs1/User/dengwei/igem/md-simulation` | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda`; `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` | Installed, preflight passed, four-system rep1 smoke passed, chctrl rep1 running as single full MD job | `environments/e2-md-gromacs.md`; `experiments/md-simulation/results/e2_preflight/`; `docs/logs/2026-05-29.md`; `docs/logs/2026-05-30.md` |
| Old Slurm RTX 5090 | Validated secondary candidate | default target `/home/guest/igem/md-simulation` | `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda`; target pin `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` | `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` after validation | Read-only preflight found node3 RTX5090 schedulable and target env absent/clean, but `conda`/`mamba`/`micromamba` are not available; blocked before same-pin env validation, smoke, benchmark, or production | `experiments/md-simulation/results/slurm_preflight/slurm_chimeric_preflight_20260530_slurm5090_readonly.log`; `docs/logs/2026-05-30.md`; `docs/ops/archives/slurm-md-server.md` for historical-only hardware and pitfall pointers |

## Uniform Production Pin

| Field | Required value |
|---|---|
| GROMACS package | `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` |
| Build family | conda-forge `linux-64` `mpi_openmpi_cuda` |
| Command contract | `gmx_mpi`, not `gmx` |
| Key solved dependency family | CUDA runtime/toolkit 12.9, OpenMPI 5.0.8, FFTW 3.3.11, hwloc 2.12.x |
| MDP generator | `experiments/md-simulation/scripts/e2_make_chimeric_prod_mdp.py` |
| Full production length | 500 ns per replicate unless a later gate changes it |
| Replicates | chctrl + Ch-1 + Ch-2 + Ch-4, 3 reps each |

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

- Do not interrupt the current E2 chctrl rep1.
- Slurm may run only replicates that have not started on E2.
- Do not place all replicates of one system on the same hardware when avoidable; interleave E2 and Slurm so site effects are not perfectly confounded with system effects.
- Run at most one full MD job per GPU.
