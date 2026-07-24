# Gpr3 R167Y + ASCR3 AutoDL clone attempt3 input-promotion HOLD

> Source: clone-host qualification artifacts under
> `/root/autodl-tmp/igem/md-simulation/gpr3_r167y_ascr3_rep1_20260717/qualification/attempt3_clone_20260719T141646Z/`.
>
> As of: `2026-07-19T22:21:28+08:00`.
>
> Allowed use: clone-host preflight/smoke qualification and the attempt3
> input-promotion terminal state. This does not establish preproduction,
> benchmark, launch-gate, or production readiness.
>
> Update trigger: a newly frozen input manifest/bundle that resolves the
> same-path conflict and is independently rechecked before promotion.

## Terminal state

`HOLD`

The clone host passed an independently recorded preflight and GPU smoke. The
frozen staging bundle also passed its full manifest check. Promotion stopped
before copying any attempt3 input because one existing destination file had a
different SHA256 from the frozen manifest:

`input/provenance/terminal_status.tsv`

| Gate | Result | Evidence |
|---|---|---|
| Clone preflight | PASS | RTX 5090; no GPU compute process, `gmx_mpi`, `mdrun`, or tmux session; exact-pin GROMACS 2025.4 / mixed / OpenMPI 5.0.8 / FFTW 3.3.11 / CUDA runtime 12.90 |
| Clone GPU smoke | PASS | synthetic water box; 10,000 steps / 20 ps; checkpoint parseable; peak sampled GPU utilization 68%; issue scan empty |
| Frozen staging manifest | PASS | manifest SHA256 `01e5a8e1dbaf679d6f88f57bd081ece7cd52c91354943bcd263ff20e6151dab9`; 37/37 entries checked |
| Destination path audit | HOLD | 27 `EXISTING_SAME`, 9 `MISSING`, 1 `CONFLICT` |
| Input promotion | NOT_RUN | stopped before copying because the conflict contract is fail-closed |
| Preproduction | NOT_RUN | no attempt3 preproduction directory or tmux session created |
| 100 ps benchmark | NOT_RUN | preproduction gate did not open |
| Production | NOT_RUN | launch gate did not open |

## Conflict

| Copy | SHA256 | Content role |
|---|---|---|
| Frozen expected | `a7025692bdb4774f4832b69385505b82c54b351543ca42e4e54b800fe9cc6d47` | two-line aggregate input PASS |
| Existing destination | `00fccf065300609934bdfa49db71acef28c57e106d157f3f4666078ad10855b5` | eight-line component gate PASS inventory |

Both bodies report a local input PASS, but they are not byte-identical.
The transfer contract requires every existing same-path body to match the
frozen manifest, so semantic similarity cannot authorize promotion.

## Payload and recovery

The complete operation-produced evidence stays outside Git:

- local verified snapshot:
  `/private/tmp/autodl_gpr3_clone_attempt3_qualification_20260719/`
- remote source:
  `/root/autodl-tmp/igem/md-simulation/gpr3_r167y_ascr3_rep1_20260717/qualification/attempt3_clone_20260719T141646Z/`
- snapshot evidence manifest: 88 entries; local `sha256sum -c` PASS
- evidence-manifest SHA256:
  `b3710a52a7f94d2690d8b5b6c22844f77015988e850f85fcdd913324975361e4`

The local snapshot contains preflight logs, smoke inputs/outputs, checkpoint
dump, GPU sampler, staging check, complete 37-row destination audit, conflict
copies/diff, terminal state, and shutdown recommendation. Runtime binary bodies
remain external under the payload-tracking policy.

## Next gate

Create a new versioned frozen bundle and manifest that explicitly resolves the
destination `terminal_status.tsv` identity. Re-run the local manifest check,
upload to a new staging path, and repeat the same-path audit. Do not resume from
this HOLD directory and do not treat the completed clone smoke as permission to
skip the next input-promotion gate.

## References / 所引

- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- `experiments/md-simulation/contracts/gpr3-r167y-ascr3/autodl_preproduction_contract.json`
- `experiments/md-simulation/scripts/run_gpr_md_preproduction.sh`
- `docs/ops/md-gromacs-operational-pitfalls.md`
- `docs/ops/payload-tracking-policy.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `docs/INDEX.md`
- `docs/logs/2026-07-19.md`
