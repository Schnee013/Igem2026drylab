# E2 Chimeric MD Restart Plan

> **2026-06-26 execution status**: paused/superseded for new chimeric candidate production by [决策 005](../../../docs/decisions/005-md-compute-triage-after-chctrl.md). Current use: historical execution guidance, script inventory, and provenance reference for the partial E2 route. Ch-1/Ch-2/Ch-4 full-production MD requires a new decision; E2 has chctrl rep1 evidence only, with 3-replicate control completion belonging to the old Slurm route.

> Status: reviewed E2 primary-site restart plan implemented as repo-owned scripts/config on 2026-05-28. As of 2026-05-30, the recommended E2 GROMACS 2025.4 MPI-CUDA environment has passed preflight, four-system inputs have been synced, rep1 smoke runs have completed, and chctrl rep1 full production was checkpoint-gated interrupted at 2026-05-30 02:14 CST for a same-GPU benchmark. The benchmark showed lower best 2-job aggregate throughput than the single-job baseline. Site-level integration with old Slurm RTX 5090 is tracked separately in `codex/docs/plans/chimeric-md-unified-rerun-sites.md`. Scientific interpretation requires result files, logs, and analysis outputs.

## Decision Position

- 2026-06-26 update: the former unified rerun route is paused after clarifying that control/chctrl 3 completed replicates belong to the old Slurm route, while E2 has chctrl rep1 evidence only. The next chimeric action is protocol optimization to reduce compute load; Ch-1/Ch-2/Ch-4 full production requires a new work order.
- Historical route: rerun `chimeric-ste2-gpa1-wt` chctrl together with Ch-1/Ch-2/Ch-4 under a unified clean-start provenance. E2 remains the primary site under `/ifs1/User/dengwei/igem/md-simulation/`; Slurm RTX 5090 is a validated secondary candidate only after the gates tracked in `codex/docs/plans/chimeric-md-unified-rerun-sites.md`.
- Use one production GROMACS environment family for all rerun systems: see `environments/e2-md-gromacs.md` for the E2 package evidence and `environments/md-production-sites.md` for site-level targets. The current required pin is `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0`.
- Clean-start provenance requires all 12 replicates to start from audited C3 outputs; old Ch-1 checkpoint material and old chctrl production logs remain historical evidence.
- Treat old Slurm `2025.2-spack` paths, jobs, and scripts as historical evidence only. New Slurm work must use the new `slurm_*` wrapper scripts and pass the same-pin gates before production.
- Use a tiered full-system validation protocol: 500 ns/replicate remains the final production target, while 100-150 ns is an early stability gate on the same full-system trajectory. Local pocket/interface-only production MD requires a separate provenance and interpretation plan.
- MM-PBSA remains optional for restarting or accepting these production trajectories.

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
  - Pulls compact rebuilt Phase C3 evidence only; production evidence comes from production/smoke result syncs.
- `experiments/md-simulation/scripts/e2_make_chimeric_prod_mdp.py`
  - Generates per-replicate production MDPs from local CHARMM-GUI `step7_production.mdp`.
  - Patches `dt = 0.002`, 500 ns `nsteps = 250000000`, deterministic replicate seed, output cadence, `continuation = no`, `gen-vel = yes`, and `compressed-x-grps = SOLU`.
- `experiments/md-simulation/scripts/e2_run_chimeric_prod.sh SYSTEM REP LENGTH_NS`
  - Runs in isolated `prod_repN/` directories on E2, with `--smoke` support.
  - Uses the preflight-selected GROMACS command by default; missing `.chimeric_gmx.env` is a hard error unless deliberately overridden for debugging.
  - Runs on the E2 route.
  - Full production is hard-gated by `E2_PROD_CONFIRMED=1`; smoke mode remains available before that gate.
  - Retries setup-only SSH/rsync operations; `mdrun` retry requires explicit operator action.
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
| `chimeric-gpr3-aogpa2-c37` | Ch-1 | audited C3 `step6.6` | Recover final C3 checkpoint/log evidence if missing locally; production starts from audited C3 inputs. |
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
   - Confirm `SOLU` is protein-only and compatible with the protein-only trajectory analysis route.

4. Smoke gate
   - 2026-05-29 rep1 smoke evidence is archived for chctrl, Ch-1, Ch-2, and Ch-4.
   - Smoke outputs are archived under `experiments/md-simulation/results/<system>/raw/20260529_e2_smoke/rep1/`.
   - Verified smoke evidence includes `grompp`/`mdrun` logs, GPU assignment, final coordinate writing, nonempty checkpoint/final structure files, and `gmx check` readability of protein-only XTC.
   - Smoke XTC contains only the time-0 protein frame because `SMOKE_NS=0.02` gives 10,000 steps while `nstxout-compressed=50000`; final full-system coordinates and checkpoints were written.
   - Stop for user review after smoke results. `E2_PROD_CONFIRMED=1` is set only after this review is accepted.

5. Production gate
   - 2026-05-29: user approved the first full production launch, `chimeric-ste2-gpa1-wt` rep1 under `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1/`.
   - 2026-05-29: after rep1 had progressed without fatal errors and showed low GPU memory use, user approved evaluating A100 80G parallel MD while leaving some shared-resource headroom. `chimeric-ste2-gpa1-wt` rep2 was briefly launched under `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep2/` in tmux `e2_chctrl_rep2_20260529`.
   - The 2-job same-GPU probe was interrupted because both logs stopped advancing, instantaneous GPU SM utilization dropped, and rep1 resumed only after rep2 stopped. The partial rep2 probe was preserved remotely as `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep2_concurrency_probe_20260529_1714/`.
   - 2026-05-30: user requested waiting for the next rep1 checkpoint, then interrupting and benchmarking same-GPU parallelism in separate benchmark directories. Rep1 wrote checkpoint step `13437400` at 2026-05-30 02:14:06 CST, then received INT and stopped within 200 steps. The canonical checkpoint remains `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1/prod.cpt`.
   - 2026-05-30 benchmark evidence is in `/ifs1/User/dengwei/igem/md-simulation/benchmarks/chctrl_concurrency_20260530_checkpoint_stop/run2_fixed_benchmark/summary.tsv` and `docs/logs/2026-05-30.md`: single `ntomp=24` baseline was `66.429 ns/day`; best tested same-GPU 2-job total was `52.505 ns/day`.
   - Current production cap is one full GPU MD job. chctrl rep1 was resumed in tmux `e2_chctrl_rep1_resume_20260530` from `prod.cpt` with `-cpi prod.cpt -append` after confirming no active `mdrun`. Same-GPU full-production concurrency needs a new benchmark plan.
   - Use 16-32 CPU threads by default.
   - Launch E2 full production only with explicit confirmation and `E2_PROD_CONFIRMED=1`; use `RESULTS_RUN_ID=20260529_e2_rerun` when syncing results so old Slurm/chctrl raw logs stay pointer-only historical evidence.

6. Early stability gate
   - This is a mid-run full-system gate. The final production target remains 500 ns/replicate; the default review point is 150 ns, with 100 ns as the minimum early screen when compute or scheduling pressure requires an earlier decision.
   - Trigger only after a correctly written checkpoint, readable trajectory, and no fatal/error evidence in `prod.log`. Interrupting a running replicate for this gate requires an approved checkpoint/sync plan.
   - Analyze the same full-system production trajectory with the project metric set: alpha5/eCT iRMSD, BSA, contact persistence, interface H-bond occupancy, COM distance, junction RMSF, global RMSD, and membrane/system sanity checks.
   - If the replicate passes the early gate, continue from the same `prod.cpt` to the 500 ns final target. A clear failure by gross separation, persistent interface collapse, unreadable trajectory, or system instability is archived as `early-gate failed` outside the final evidence set.
   - If the gate is ambiguous or only one metric is concerning, mark it `early-gate ambiguous` and either extend the same replicate or wait for replicate/site cross-checks.
   - Local pocket/interface-only MD may be planned later as supporting mechanism/refinement analysis, with separate provenance and interpretation.

7. Slurm secondary-site gate
   - Slurm RTX 5090 enters production only after the gate sequence in `codex/docs/plans/chimeric-md-unified-rerun-sites.md` passes.
   - The same package pin, same clean-start inputs, and same generated MDP logic are mandatory.

8. Completion gate
   - Accept a replicate only after normal `prod.log` termination, updated `prod.cpt`, nonzero `prod.tpr/gro/xtc`, synced checksums, and `gmx check` or equivalent sanity checks.

## Analysis Route

- After each accepted replicate, sync raw outputs back locally.
- Use one PBC/protein-only processing route for chctrl and chimeric systems, passing the system ID through analysis drivers.
- Run convergence, alpha5 iRMSD, H-bond, COM distance, RMSF, BSA, and contact persistence with selections from `experiments/md-simulation/analysis/chimeric_systems.json`.
- Compare Ch-1/Ch-2/Ch-4 against the new E2 chctrl rerun baseline; universal pass/fail thresholds require exact source pointers.
- Treat alpha5 3/5 A, BSA 20%, contact >0.50, and H-bond >10% as project operational heuristics unless exact source pointers are added.

## Documentation Rules

- Log implementation and verified milestones in the relevant `docs/logs/YYYY-MM-DD.md` file first.
- Update `docs/INDEX.md` and `docs/modeling/P0-md-simulation.md` only after durable status changes, such as recovered inputs, accepted smoke tests, or accepted production replicates.
- Keep `codex/docs/memory/` pointer-based; detailed procedure remains in this plan.
