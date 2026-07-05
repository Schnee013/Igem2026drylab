# E2 Chimeric MD Restart Plan

> **2026-06-26 execution status**: paused/superseded for new chimeric candidate production by [决策 005](../../../docs/decisions/005-md-compute-triage-after-chctrl.md). Do not use this plan to launch Ch-1/Ch-2/Ch-4 full-production MD without a new decision. Keep it as historical execution guidance, script inventory, and provenance reference for the partial E2 route; E2 has chctrl rep1 evidence only, not 3 completed control replicates.

> Status: reviewed E2 primary-site restart plan implemented as repo-owned scripts/config on 2026-05-28. As of 2026-05-30, the recommended E2 GROMACS 2025.4 MPI-CUDA environment has passed preflight, four-system inputs have been synced, rep1 smoke runs have completed, and chctrl rep1 full production was checkpoint-gated interrupted at 2026-05-30 02:14 CST for a same-GPU benchmark. The benchmark showed lower best 2-job aggregate throughput than the single-job baseline. Site-level integration with old Slurm RTX 5090 is tracked separately in `codex/docs/plans/chimeric-md-unified-rerun-sites.md`. This plan is execution guidance, not final scientific evidence.

## Decision Position

- 2026-06-26 update: the former unified rerun route is paused after clarifying that control/chctrl 3 completed replicates belong to the old Slurm route, while E2 has chctrl rep1 evidence only. The next chimeric action is protocol optimization to reduce compute load, not direct continuation of Ch-1/Ch-2/Ch-4 full production.
- Historical route: rerun `chimeric-ste2-gpa1-wt` chctrl together with Ch-1/Ch-2/Ch-4 under a unified clean-start provenance. E2 remains the primary site under `/ifs1/User/dengwei/igem/md-simulation/`; Slurm RTX 5090 is only a validated secondary candidate, with gates tracked in `codex/docs/plans/chimeric-md-unified-rerun-sites.md`.
- Use one production GROMACS environment family for all rerun systems: see `environments/e2-md-gromacs.md` for the E2 package evidence and `environments/md-production-sites.md` for site-level targets. The current required pin is `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0`.
- Do not resume Ch-1 rep1 from the old ~28 ns production checkpoint, and do not treat old chctrl production as the accepted baseline. Start all 12 replicates cleanly from audited C3 outputs so server/software provenance is consistent.
- Treat old Slurm `2025.2-spack` paths, jobs, and scripts as historical evidence only. New Slurm work must use the new `slurm_*` wrapper scripts and pass the same-pin gates before production.
- Use a tiered full-system validation protocol: 500 ns/replicate remains the final production target, while 100-150 ns is only an early stability gate on the same full-system trajectory. Do not replace the unified rerun with local pocket/interface-only production MD.
- Keep MM-PBSA optional; it is not a go/no-go blocker for restarting or accepting these production trajectories.

## Implemented Artifacts

- `experiments/md-simulation/scripts/e2_chimeric_preflight.sh`
  - SSHes to E2 and records hostname, user, quota/filesystem state, GPU/CUDA state, conda/mamba/apptainer availability, GROMACS discovery, `gmx --version`, GPU-support line, chosen command, and `.chimeric_gmx.env`.
  - Returns nonzero if no usable GROMACS command with detected GPU support is found, so the preflight gate cannot silently pass.
- `experiments/md-simulation/scripts/e2_sync_chimeric_inputs.sh SYSTEM...`
  - Audits local canonical inputs before rsync.
  - Requires `step6.6.gro`, `step6.6.cpt`, `topol.top`, `index.ndx`, `step7_production.mdp`, `toppar/`, required nonempty index groups, and final C3/phase3 log evidence.
  - Writes SHA256 manifests and syncs only to `/ifs1/User/dengwei/igem/md-simulation/<system>/gromacs/`.
  - Retries short SSH/rsync transfers with `E2_IO_RETRIES` to tolerate transient E2 connection resets.
- `experiments/md-simulation/scripts/e2_run_chimeric_phase3.sh SYSTEM...`
  - Rebuilds missing Phase C3 terminal outputs on E2 from local CHARMM-GUI/GROMACS inputs.
  - Requires the preflight-selected GPU-enabled GROMACS command and refuses to overwrite existing terminal C3 outputs unless explicitly allowed after audit.
- `experiments/md-simulation/scripts/e2_sync_chimeric_phase3_outputs.sh RUN_ID SYSTEM...`
  - Pulls compact rebuilt Phase C3 evidence back to local canonical inputs: terminal logs, final structures, checkpoints, TPR/EDR where needed, and source/output SHA256 manifests.
  - Does not pull equilibration trajectories and does not create production evidence.
- `experiments/md-simulation/scripts/e2_make_chimeric_prod_mdp.py`
  - Generates per-replicate production MDPs from local CHARMM-GUI `step7_production.mdp`.
  - Patches `dt = 0.002`, 500 ns `nsteps = 250000000`, deterministic replicate seed, output cadence, `continuation = no`, `gen-vel = yes`, and `compressed-x-grps = SOLU`.
- `experiments/md-simulation/scripts/e2_run_chimeric_prod.sh SYSTEM REP LENGTH_NS`
  - Runs in isolated `prod_repN/` directories on E2, with `--smoke` support.
  - Uses the preflight-selected GROMACS command by default; missing `.chimeric_gmx.env` is a hard error unless deliberately overridden for debugging.
  - Does not use Slurm.
  - Full production is hard-gated by `E2_PROD_CONFIRMED=1`; smoke mode remains available before that gate.
  - Retries setup-only SSH/rsync operations; it does not automatically retry `mdrun`.
- `experiments/md-simulation/scripts/e2_sync_chimeric_results.sh SYSTEM...`
  - Pulls production/smoke outputs, generated MDPs, checksums, and run logs.
  - Use `RESULTS_RUN_ID=<id>` for E2 rerun outputs, which stores files under `experiments/md-simulation/results/<system>/raw/<id>/repN/` and prevents overwriting historical chctrl `raw/repN/prod.*` evidence.
- Slurm secondary-site artifacts are tracked in `codex/docs/plans/chimeric-md-unified-rerun-sites.md`:
  - `slurm_chimeric_preflight.sh`
  - `slurm_sync_chimeric_inputs.sh`
  - `slurm_run_chimeric_prod.sh`
  - `slurm_sync_chimeric_results.sh`
- `experiments/md-simulation/analysis/chimeric_systems.json`
  - Defines receptor/Galpha roles, alpha5/eCT selections, receptor interface selections, and junction RMSF regions for chctrl and Ch-1/Ch-2/Ch-4.
- `src/modeling/md-analysis/common.py` and chctrl analysis drivers
  - Main metric scripts accept `--system` and load selections from `chimeric_systems.json` instead of assuming chctrl `PROA=Gpa1` / `PROB=Ste2`.

## System Scope

| System ID | Short name | Clean-start input | Notes |
|---|---:|---|---|
| `chimeric-ste2-gpa1-wt` | chctrl | audited C3 `step6.6` | Rerun as the positive-control baseline in the same E2 environment as Ch-1/Ch-2/Ch-4. Historical production logs remain raw evidence only. |
| `chimeric-gpr3-aogpa2-c37` | Ch-1 | audited C3 `step6.6` | Do not resume old production `prod.cpt`; recover final C3 checkpoint/log evidence if missing locally. |
| `chimeric-gpr3-aogpa2-c15` | Ch-2 | audited C3 `step6.6` | Phase C3 was rebuilt and synced on E2; EM did not reach `Fmax < 1000` within 5001 steps, so keep this caveat attached to production interpretation. |
| `chimeric-gpr2-aogpa2-c10` | Ch-4 | audited C3 `step6.6` | Phase C3 was rebuilt and synced on E2; early EM LINCS warnings occurred, but EM converged below `Fmax < 1000`. |

## Execution Gates

1. Preflight gate
   - Run `e2_chimeric_preflight.sh`.
   - Accept only if E2 shows A100 visibility, quota/filesystem state, `/ifs1/User/dengwei/igem`, and a working GROMACS command with GPU support.
   - Use the environment pin in `environments/e2-md-gromacs.md`; if the env is newly created, save a matching conda package snapshot and preflight log before any input sync.

2. Input recovery gate
   - Recover missing Ch-2/Ch-4 C3 outputs from old archive before E2 sync.
   - For every chctrl/Ch-1/Ch-2/Ch-4 system, locally audit:
     - `step6.6.gro`
     - `step6.6.cpt`
     - final C3/phase3 logs
     - `topol.top`
     - `index.ndx`
     - `toppar/`
     - `step7_production.mdp`
   - Check `index.ndx` contains `SOLU`, `SOLU_MEMB`, `SOLV`, `MEMB`, and `SYSTEM`.
   - Generate and retain checksums before and after sync.

3. MDP/index gate
   - Generate the production MDP with `e2_make_chimeric_prod_mdp.py`.
   - Confirm 500 ns production has `dt = 0.002`, `nsteps = 250000000`, and `compressed-x-grps = SOLU`.
   - Confirm `SOLU` is protein-only and compatible with downstream protein-only trajectory analysis.

4. Smoke gate
   - 2026-05-29 rep1 smoke runs completed for chctrl, Ch-1, Ch-2, and Ch-4.
   - Smoke outputs are archived under `experiments/md-simulation/results/<system>/raw/20260529_e2_smoke/rep1/`.
   - Verified smoke evidence includes `grompp`/`mdrun` logs, GPU assignment, final coordinate writing, nonempty checkpoint/final structure files, and `gmx check` readability of protein-only XTC.
   - Smoke XTC contains only the time-0 protein frame because `SMOKE_NS=0.02` gives 10,000 steps while `nstxout-compressed=50000`; final full-system coordinates and checkpoints were written.
   - Stop for user review after smoke results. Do not set `E2_PROD_CONFIRMED=1` until this review is accepted.

5. Production gate
   - 2026-05-29: user approved the first full production launch, `chimeric-ste2-gpa1-wt` rep1 under `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1/`.
   - 2026-05-29: after rep1 had progressed without fatal errors and showed low GPU memory use, user approved evaluating A100 80G parallel MD while leaving some shared-resource headroom. `chimeric-ste2-gpa1-wt` rep2 was briefly launched under `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep2/` in tmux `e2_chctrl_rep2_20260529`.
   - The 2-job same-GPU probe was interrupted because both logs stopped advancing, instantaneous GPU SM utilization dropped, and rep1 resumed only after rep2 stopped. The partial rep2 probe was preserved remotely as `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep2_concurrency_probe_20260529_1714/`.
   - 2026-05-30: user requested waiting for the next rep1 checkpoint, then interrupting and benchmarking same-GPU parallelism in separate benchmark directories. Rep1 wrote checkpoint step `13437400` at 2026-05-30 02:14:06 CST, then received INT and stopped within 200 steps. The canonical checkpoint remains `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1/prod.cpt`.
   - 2026-05-30 benchmark evidence is in `/ifs1/User/dengwei/igem/md-simulation/benchmarks/chctrl_concurrency_20260530_checkpoint_stop/run2_fixed_benchmark/summary.tsv` and `docs/logs/2026-05-30.md`: single `ntomp=24` baseline was `66.429 ns/day`; best tested same-GPU 2-job total was `52.505 ns/day`.
   - Current production cap is one full GPU MD job. chctrl rep1 was resumed in tmux `e2_chctrl_rep1_resume_20260530` from `prod.cpt` with `-cpi prod.cpt -append` after confirming no active `mdrun`. Do not retry same-GPU full-production concurrency under the tested launch patterns.
   - Use 16-32 CPU threads by default.
   - Launch E2 full production only with explicit confirmation and `E2_PROD_CONFIRMED=1`; use `RESULTS_RUN_ID=20260529_e2_rerun` when syncing results so old Slurm/chctrl raw logs stay pointer-only historical evidence.

6. Early stability gate
   - This is a mid-run full-system gate, not a shorter final production protocol. The default review point is 150 ns; 100 ns is the minimum early screen only when compute or scheduling pressure requires an earlier decision.
   - Trigger only after a correctly written checkpoint, readable trajectory, and no fatal/error evidence in `prod.log`. Do not interrupt a running replicate merely to create this gate unless the checkpoint/sync plan has been explicitly approved.
   - Analyze the same full-system production trajectory with the project metric set: alpha5/eCT iRMSD, BSA, contact persistence, interface H-bond occupancy, COM distance, junction RMSF, global RMSD, and membrane/system sanity checks.
   - If the replicate passes the early gate, continue from the same `prod.cpt` to the 500 ns final target. If it clearly fails by gross separation, persistent interface collapse, unreadable trajectory, or system instability, stop and archive it as `early-gate failed`; it does not enter the final evidence set.
   - If the gate is ambiguous or only one metric is concerning, do not discard the replicate solely on that signal. Mark it `early-gate ambiguous` and either extend the same replicate or wait for replicate/site cross-checks.
   - Local pocket/interface-only MD is not an equivalent rerun product. It may be planned later only as supporting mechanism/refinement analysis, with separate provenance and interpretation.

7. Slurm secondary-site gate
   - Slurm RTX 5090 is not part of production until the gate sequence in `codex/docs/plans/chimeric-md-unified-rerun-sites.md` passes.
   - The same package pin, same clean-start inputs, and same generated MDP logic are mandatory.

8. Completion gate
   - Accept a replicate only after normal `prod.log` termination, updated `prod.cpt`, nonzero `prod.tpr/gro/xtc`, synced checksums, and `gmx check` or equivalent sanity checks.

## Analysis Route

- After each completed replicate, sync raw outputs back locally.
- Use one PBC/protein-only processing route for chctrl and chimeric systems, passing the system ID through analysis drivers.
- Run convergence, alpha5 iRMSD, H-bond, COM distance, RMSF, BSA, and contact persistence with selections from `experiments/md-simulation/analysis/chimeric_systems.json`.
- Compare Ch-1/Ch-2/Ch-4 against the new E2 chctrl rerun baseline, not against universal pass/fail thresholds.
- Treat alpha5 3/5 A, BSA 20%, contact >0.50, and H-bond >10% as project operational heuristics unless exact source pointers are added.

## Documentation Rules

- Log implementation and verified milestones in the relevant `docs/logs/YYYY-MM-DD.md` file first.
- Update `docs/INDEX.md` and `docs/modeling/P0-md-simulation.md` only after durable status changes, such as recovered inputs, accepted smoke tests, or completed production replicates.
- Keep `codex/docs/memory/` pointer-based; do not duplicate this plan body there.
