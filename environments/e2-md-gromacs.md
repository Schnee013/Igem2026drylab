# E2 MD GROMACS Environment Matrix

> Last verified: 2026-05-29
> Scope: NKULiulab E2 GROMACS environment evidence for the unified chimeric MD rerun. Site-level E2 + Slurm policy is tracked in `environments/md-production-sites.md`.
> Authority: this file stores environment decisions and exact package pins. Raw runtime evidence remains in preflight logs, conda package snapshots, and GROMACS production logs.

## Production Environment Decision

| Role | Decision |
|---|---|
| Recommended env | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda` |
| Recommended GROMACS pin | `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` |
| Expected command | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` |
| Build family | conda-forge `linux-64`, external OpenMPI, CUDA runtime/toolkit from conda |
| Rerun scope | Clean-start chctrl + Ch-1 + Ch-2 + Ch-4, 3 reps each, after gates below pass |
| Install status | Installed on E2 after user approval on 2026-05-29 |
| Root CUDA/driver changes | Not recommended; use personal conda runtime on E2 |

For cross-site production policy, use `environments/md-production-sites.md`. This file remains the E2 package/evidence matrix and analysis-env recommendation.

Rationale:

- chctrl is now also rerun, so matching the historical Slurm/chctrl environment is no longer the controlling objective.
- `2025.4` stays in the already-used 2025 series while taking post-`2025.2` fixes that matter for GPU/CUDA and barostat/PME behavior.
- conda-forge has an exact `linux-64` CUDA/OpenMPI build for `2025.4`, and local dry-run resolution against E2-like virtual packages succeeded.
- `mpi_openmpi_cuda` preserves the current repo script contract around `gmx_mpi`, MPI provenance, and future multi-rank compatibility.

## Production Candidate Matrix

| Candidate | Status | Exact build / command | Resolved key deps from dry-run | Decision notes |
|---|---|---|---|---|
| GROMACS 2025.4 MPI CUDA | Recommended | `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0`; command `gmx_mpi` | `cuda-version 12.9`, `cuda-toolkit 12.9.2`, `cuda-cudart 12.9.79`, `openmpi 5.0.8`, `fftw 3.3.11`, `libhwloc 2.12.1` | Best conservative conda-forge production pin for a unified E2 rerun. |
| GROMACS 2026.0 MPI CUDA | Backup | `gromacs=2026.0=mpi_openmpi_cuda_h56f47eb_1`; command `gmx_mpi` | `cuda-version 12.9`, `cuda-toolkit 12.9.2`, `cuda-cudart 12.9.79`, `openmpi 5.0.10`, `fftw 3.3.11`, `libhwloc 2.12.2` | Valid backup if 2025.4 smoke fails, but crosses a major release and changes OpenMPI minor build. |
| Current installed E2 test env | Historical / do not extend for new unified rerun | `/ifs1/User/dengwei/igem/envs/gromacs-2025.2-mpi-cuda`; `gromacs=2025.2=mpi_openmpi_cuda_h550cf53_0` | Snapshot shows `cuda-version 12.6`, `cuda-toolkit 12.6.3`, `openmpi 5.0.8`, `fftw 3.3.11`, `libhwloc 2.11.2` | Useful preflight proof that conda CUDA GROMACS works on E2, but no longer best once chctrl is rerun. |
| `nompi_cuda` variants | Rejected for production | e.g. `gromacs=2025.4=nompi_cuda_h39c90b0_0`; command `gmx` | Same CUDA/FFTW family, no OpenMPI dependency | Breaks `gmx_mpi` script/provenance contract; changing MPI vs non-MPI is an avoidable build difference for production. |
| Official current GROMACS 2026.2 | Watch only | official source tarball, no conda-forge exact env selected here | not dry-run locked in this repo session | Official current release, but not the chosen conda-forge production pin for this rerun. |

## MPI vs nompi_cuda Impact

| Dimension | `mpi_openmpi_cuda` | `nompi_cuda` |
|---|---|---|
| Command | `gmx_mpi` | `gmx` |
| Repo script compatibility | Matches current E2 scripts and historical chctrl command shape | Requires command/script adjustments |
| Performance | Good default for single GPU with OpenMP; preserves MPI route for multi-rank tests | Could be simpler for single-process use, but no clear benefit for this workflow |
| Reproducibility | Keeps one command/build family across all rerun systems | Adds a build-family difference not needed by the scientific design |
| Rerun implication | Recommended for chctrl + Ch-1/Ch-2/Ch-4 | If adopted, rerun all systems under it; do not mix with MPI results |

## E2 CUDA / Driver Compatibility

| Local E2 evidence | Pointer |
|---|---|
| A100-SXM4-80GB, driver `590.48.01`, `nvidia-smi` CUDA `13.1`, system `nvcc 13.1.115` | `experiments/md-simulation/results/e2_preflight/chimeric_preflight_20260529_gromacs_2025_2_mpi_cuda.log` |
| Current conda test env reports GROMACS `2025.2-conda_forge`, Open MPI `5.0.8`, GPU support `CUDA`, CUDA runtime `12.60` | same preflight log |
| Current conda test env package snapshot includes `gromacs 2025.2 mpi_openmpi_cuda_h550cf53_0`, `cuda-version 12.6`, `cuda-toolkit 12.6.3` | `experiments/md-simulation/results/e2_preflight/gromacs_2025.2_mpi_cuda_conda_list_20260529.txt` |
| Recommended env preflight reports GROMACS `2025.4-conda_forge`, Open MPI `5.0.8`, GPU support `CUDA`, CUDA runtime `12.90`, CUDA driver `13.10` | `experiments/md-simulation/results/e2_preflight/chimeric_preflight_20260529_gromacs_2025_4_mpi_cuda.log` |

Conclusion: CUDA 12.x conda runtime/toolkit under E2 driver `590.48.01` is reasonable. Do not request root-level CUDA/driver changes unless a later preflight or smoke `mdrun` produces a concrete CUDA compatibility error.

## Installed Production Env Evidence

| Evidence | Pointer |
|---|---|
| Official install command used after confirming target prefix was absent | `ssh nkuliulab-e2 'mamba create -y -p /ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda -c conda-forge gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0'` |
| Package snapshot | `experiments/md-simulation/results/e2_preflight/gromacs_2025.4_mpi_cuda_conda_list_20260529.txt` |
| Snapshot sha256 | `ae27483c773a049e7accd6548e50d3b792f8715c8406290186f00c5688640ed8` |
| Minimal command verification | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi --version` reported GROMACS `2025.4-conda_forge`, OpenMPI `5.0.8`, GPU support `CUDA`, CUDA runtime `12.90`, CUDA driver `13.10` |
| Preflight log | `experiments/md-simulation/results/e2_preflight/chimeric_preflight_20260529_gromacs_2025_4_mpi_cuda.log` |
| Preflight log sha256 | `e8a5548fc36fe81dd165044e9fbbc2f0acdbf5ff349391cf23706f7186d3991b` |
| Remote selected command file | `/ifs1/User/dengwei/igem/md-simulation/.chimeric_gmx.env` contains `GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` |

## Analysis Environments

Keep analysis environments separate from the production GROMACS environment.

| Env | Purpose | Recommended specs | Dry-run resolved key packages |
|---|---|---|---|
| `md-analysis-py311` | Core trajectory, contact, IFP, and tabular analysis | `python=3.11`, `mdanalysis=2.10.*`, `mdtraj=1.11.*`, `prolif=2.1.*`, `rdkit` | `python 3.11.15`, `mdanalysis 2.10.0`, `mdtraj 1.11.1`, `prolif 2.1.0`, `rdkit 2026.03.2`, `numpy 2.4.6`, `pandas 2.3.3` |
| `gmx-mmpbsa-py311` | Optional MM-PBSA only | `python=3.11`, `gmx_mmpbsa=1.6.5` | `gmx_mmpbsa 1.6.5`, `ambertools 23.6`, `parmed 4.3.1`, `mpi4py 4.0.1`, `numpy 1.26.4`, `pandas 1.5.3`, `matplotlib 3.7.3`, `scipy 1.14.1`, `seaborn 0.11.2` |

Do not merge `gmx_mmpbsa` into the core analysis environment unless a future dry-run and smoke analysis prove the combined solve is stable.

## Verification Commands Used Locally

These first commands were dry-run / repoquery checks; no E2 installation was performed during the environment decision step.

```bash
env CONDA_PKGS_DIRS=/private/tmp/conda-pkgs MAMBA_ROOT_PREFIX=/private/tmp/mamba-root CONDA_OVERRIDE_CUDA=13.1 CONDA_OVERRIDE_GLIBC=2.39 mamba repoquery search --json --platform linux-64 -c conda-forge gromacs=2025.4
env CONDA_PKGS_DIRS=/private/tmp/conda-pkgs MAMBA_ROOT_PREFIX=/private/tmp/mamba-root CONDA_OVERRIDE_CUDA=13.1 CONDA_OVERRIDE_GLIBC=2.39 mamba create --dry-run --json --platform linux-64 -p /private/tmp/e2-gmx-2025.4 -c conda-forge gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0
env CONDA_PKGS_DIRS=/private/tmp/conda-pkgs MAMBA_ROOT_PREFIX=/private/tmp/mamba-root CONDA_OVERRIDE_CUDA=13.1 CONDA_OVERRIDE_GLIBC=2.39 mamba create --dry-run --json --platform linux-64 -p /private/tmp/e2-gmx-2026.0 -c conda-forge gromacs=2026.0=mpi_openmpi_cuda_h56f47eb_1
env CONDA_PKGS_DIRS=/private/tmp/conda-pkgs MAMBA_ROOT_PREFIX=/private/tmp/mamba-root CONDA_OVERRIDE_GLIBC=2.39 mamba create --dry-run --json --platform linux-64 -p /private/tmp/md-analysis-py311 -c conda-forge python=3.11 'mdanalysis=2.10.*' 'mdtraj=1.11.*' 'prolif=2.1.*' rdkit
env CONDA_PKGS_DIRS=/private/tmp/conda-pkgs MAMBA_ROOT_PREFIX=/private/tmp/mamba-root CONDA_OVERRIDE_GLIBC=2.39 mamba create --dry-run --json --platform linux-64 -p /private/tmp/gmx-mmpbsa-py311 -c conda-forge python=3.11 gmx_mmpbsa=1.6.5
```

## Upstream Evidence Pointers

- GROMACS current download page: https://manual.gromacs.org/current/download.html
- GROMACS 2025.4 release notes: https://manual.gromacs.org/current/release-notes/2025/2025.4.html
- GROMACS 2026.2 release notes: https://manual.gromacs.org/current/release-notes/2026/2026.2.html
- GROMACS install guide, CUDA and MPI support: https://manual.gromacs.org/current/install-guide/index.html
- conda-forge GROMACS package page: https://anaconda.org/conda-forge/gromacs
- conda-forge GROMACS feedstock: https://github.com/conda-forge/gromacs-feedstock
- NVIDIA CUDA Toolkit release notes / minimum driver table: https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html
- NVIDIA CUDA compatibility guide: https://docs.nvidia.com/deploy/cuda-compatibility/index.html
- NVIDIA CUDA compatibility developer guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#cuda-compatibility-developer-s-guide

## Next Gate After Approval

1. Perform local input audit/recovery for chctrl + Ch-1 + Ch-2 + Ch-4.
2. Verify each system has the required C3/phase3 source files, index groups, topology, MDP, logs, and checksums before any E2 sync.
3. Do not sync inputs, run `grompp`, smoke `mdrun`, or production until the relevant gate is explicitly opened.
