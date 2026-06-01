# Chimeric MD Unified Rerun Sites Plan

> Status: implemented as repo-owned environment matrix and Slurm wrapper scripts on 2026-05-30. This plan is execution guidance, not final scientific evidence. Verify current status against logs, preflight outputs, Slurm scheduler state, and result files before acting.

## Decision Position

- Run the clean-start chimeric MD rerun as one provenance family: chctrl + Ch-1 + Ch-2 + Ch-4, 3 replicates each, under the same GROMACS `2025.4` MPI-CUDA conda-forge pin.
- E2 A100 remains the primary production site. The old Slurm RTX 5090 server is admitted only as a validated secondary site after it passes preflight, same-pin environment validation, smoke, benchmark, and early production checks.
- Do not interrupt the currently running E2 chctrl rep1.
- Do not mix old Slurm `2025.2-spack` chctrl production outputs into the new rerun. Those logs remain historical performance/provenance pointers only.
- If Slurm cannot run `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` on RTX 5090 without CUDA/PTX errors, it does not enter production unless a separate異環境 batch is explicitly approved.

## Implemented Artifacts

- `environments/md-production-sites.md`
  - Site-level matrix for E2 primary + Slurm validated secondary.
  - Records exact env targets, command contracts, result layout rules, and admission gates.
- `experiments/md-simulation/scripts/slurm_chimeric_preflight.sh`
  - Read-only Slurm login preflight: host, storage, scheduler, node3 state, environment tools, and any existing GROMACS command.
  - Does not submit jobs.
- `experiments/md-simulation/scripts/slurm_sync_chimeric_inputs.sh`
  - Audits the same clean-start C3 inputs as the E2 route and syncs to `/home/guest/igem/md-simulation/<system>/gromacs/`.
  - Uses SHA256 manifests and refuses missing C3/phase3 evidence.
- `experiments/md-simulation/scripts/slurm_run_chimeric_prod.sh`
  - Submits Slurm smoke, benchmark, or full production jobs through `sbatch`.
  - Uses `e2_make_chimeric_prod_mdp.py` for MDP generation.
  - Requires GROMACS `2025.4` with GPU support inside the job.
  - Full production is hard-gated by `SLURM_PROD_CONFIRMED=1`.
- `experiments/md-simulation/scripts/slurm_sync_chimeric_results.sh`
  - Pulls Slurm outputs into `raw/<RESULTS_RUN_ID>/repN/`, defaulting to `YYYYMMDD_slurm5090_rerun`.

## Slurm Admission Gates

1. Read-only preflight
   - Run `slurm_chimeric_preflight.sh`.
   - Stop if node3/RTX5090 is unavailable or the scheduler cannot allocate GPU work.

2. Same-pin environment validation
   - Target env: `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda`.
   - Required pin: `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0`.
   - Required command: `/home/guest/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi`.
   - Save `gmx_mpi --version`, conda package snapshot, and preflight log before any smoke/benchmark production gate.

3. Input sync
   - Use only audited local C3 inputs: `step6.6.gro`, `step6.6.cpt`, `topol.top`, `index.ndx`, `toppar/`, and `step7_production.mdp`.
   - Do not reuse old Slurm working directories or old `prod_repN` outputs.

4. Smoke and benchmark
   - Smoke chctrl, Ch-1, Ch-2, and Ch-4 rep1 before any Slurm full production.
   - Benchmark at least chctrl and one large system.
   - Benchmark evidence must include a comparable `summary.tsv` with system, atoms, GPU, threads, GROMACS build, job id, and ns/day.

5. Production admission
   - First Slurm production replicate should be one not already running on E2, default Ch-1 rep1.
   - Check 10-30 minutes after launch for step progression, GPU utilization, checkpoint/log updates, and no fatal/error lines.
   - Run at most one full MD job per GPU.

6. Completion
   - Accept a replicate only after normal termination, nonempty `prod.log/cpt/gro/xtc/edr/tpr`, checksums, `gmx check`, and site/env provenance in the result directory.

## Scheduling Rule

- Keep E2 chctrl rep1 on E2 until completion.
- Use Slurm for not-yet-started replicates only after gates pass.
- Interleave systems and sites where possible so one system's replicates are not all assigned to one hardware site.
- Sync outputs with explicit run ids:
  - E2: `20260529_e2_rerun`
  - Slurm: `YYYYMMDD_slurm5090_rerun`

## Historical Pointers

- Old Slurm ops archive: `docs/ops/archives/slurm-md-server.md`
- Old chctrl production logs: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/rep{1,2,3}/prod.log`
- Current E2 plan: `codex/docs/plans/e2-chimeric-md-restart.md`
- Site matrix: `environments/md-production-sites.md`
