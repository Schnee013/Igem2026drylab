# Gpr2 WT + ASCR18 E2 Short Benchmark

## 结论

本目录保存 `Gpr2_WT + ASCR18` 在 E2 A100 上的 100 ps 短时 MD benchmark 证据包。允许用途：Decision 005 后 mutant GPR MD 前测的 WT holo 资源基线。突变体稳定性和 full-production 排程需要后续 production 轨迹、completion archive 和 matched analysis。

核心结果：

| metric | value |
|---|---:|
| nominal duration | 100 ps |
| steps | 50,000 |
| performance | 139.222 ns/day |
| wall cost | 0.172 hour/ns |
| GPU utilization avg | 80.50% |
| GPU utilization nonzero avg | 86.69% |
| GPU utilization max | 97% |
| GPU memory max | 509 MiB / 81920 MiB |
| GPU power avg | 209.31 W |
| GPU temperature max | 86 C |

## 运行条件

- Remote host: `nkuliulab-e2`
- Remote run root: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705`
- GROMACS: `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi`
- Command shape: one MPI process, `OMP_NUM_THREADS=24`, `-ntomp 24 -pin on -nb gpu -pme gpu -bonded gpu`
- Successful run window: `2026-07-05T17:23:04+08:00` to `2026-07-05T17:24:36+08:00`

The successful benchmark launch condition is the final pre-run `nvidia_smi_before.log`, which showed no running GPU processes and 0 MiB memory use. `logs/gpu_busy_before_mdrun.log` is retained as an earlier same-directory busy-GPU preflight record.

## Input Repair

The archived source `experiments/md-simulation/systems/Gpr2_WT/gromacs/index.ndx` remains unchanged. For this benchmark package only, `input/gromacs/index.ndx` was regenerated from `step6.6.gro` using `experiments/md-simulation/scripts/assemble_complex.py::build_index`, because the older index had fixed-width atom-number concatenation past 99999.

The repaired index validation before upload:

| group | atoms |
|---|---:|
| SOLU | 6,451 |
| MEMB | 26,532 |
| SOLV | 99,495 |
| SOLU_MEMB | 32,983 |
| SYSTEM | 132,478 |
| TIP3 | 99,300 |

`grompp` was allowed `-maxwarn 11` only after review of the known `cgenff_ASCR18.itp` duplicate type-9 dihedral parameter warnings. `logs/grompp_warning_gate.txt` confirms exactly 11 accepted warnings from that source and no fatal error.

## Sanity Checks

- `logs/sanity_short_prod_xtc_check.log`: 2 coordinate frames, time 0 and 100 ps, 132,478 atoms.
- `logs/sanity_short_prod_edr_check.log`: 51 energy frames, 2 ps spacing, last frame at 100 ps.
- `logs/sanity_short_prod_energy.log`: temperature average 303.457 K, pressure average 9.51098 bar, density average 1025.98 kg/m^3.
- `logs/mdrun_issue_scan.log` only matches the `cuda` substring in the GROMACS environment path; no runtime fatal/error/LINCS/NaN issue was found in the mdrun completion block.

## Key Files

- `command_plan.md`: benchmark command plan and interpretation boundary.
- `run_gpr2_wt_short_benchmark.sh`: script used on E2.
- `logs/production_short_summary.tsv`: parsed endpoint metrics.
- `logs/nvidia_smi_production_short.csv`: 14 GPU samples at 5 s spacing.
- `logs/grompp_gpr2_wt_ascr18_short.log`: preprocessing evidence.
- `logs/grompp_warning_gate.txt`: warning acceptance gate.
- `logs/mdrun_gpr2_wt_ascr18_short.log`: mdrun stdout/stderr with `Performance:` line.
- `production_smoke/gpr2_wt_ascr18_short.{tpr,xtc,edr,cpt,gro,log}`: short benchmark binary and trajectory outputs.
- `logs/manifest_sha256_after_short_benchmark.txt`: checksum manifest for copied evidence files.

## Checksum And Recovery

The checksum manifest intentionally excludes itself. The original producer used
an unrestricted `find` over `logs/`, which created an impossible self-checksum.
The runner now excludes
`logs/manifest_sha256_after_short_benchmark.txt`, and the repaired manifest
validates all 40 listed files.

The recorded E2 recovery root is
`/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705`.
Its current availability was not checked during the local-only 2026-07-12
repair. After restoring a copy, validate it from the benchmark root with:

```bash
sha256sum -c logs/manifest_sha256_after_short_benchmark.txt
```

The copied `input/gromacs/` and `production_smoke/` bodies remain operation
payloads and are not promoted to repo-owned canonical inputs by this manifest.

## Interpretation Boundary

This result answers the operational benchmark endpoint for the WT holo system on E2: practical GPU occupancy and short-run production speed. Allowed use is sizing and scheduling the next mutant GPR prework; ligand stability, receptor activation, mutant performance, and production-length convergence require independent trajectory evidence.

## References / 所引

- `docs/decisions/005-md-compute-triage-after-chctrl.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/ops/nkuliulab-e2-cloud-server.md`
- `docs/ops/md-gromacs-operational-pitfalls.md`
- `environments/e2-md-gromacs.md`
- `docs/logs/2026-04-16.md`
- `experiments/md-simulation/scripts/assemble_complex.py`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/step6.6.gro`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/topol_phase3.top`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/step7_production.mdp`

## Referenced by / 被引

- `docs/logs/2026-07-05.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- Future mutant GPR MD input-gate and E2 scheduling decisions for `Gpr2_R59C` / `Gpr3_R167Y`.
- `experiments/md-simulation/results/gpr2-wt-ascr18/payload_manifest.tsv`
