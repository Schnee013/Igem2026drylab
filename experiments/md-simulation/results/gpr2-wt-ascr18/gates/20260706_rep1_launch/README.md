# Gpr2 WT + ASCR18 production rep1 launch gate

> Snapshot time: 2026-07-06.
>
> Scope: launch-time gate evidence for the running 200 ns `Gpr2_WT + ASCR18` production rep1 on E2.

## Decision

`Gpr2_WT + ASCR18` production rep1 was allowed to start only after the E2 shared GPU gate passed under streaming sampling.

The launch watcher first observed repeated non-idle single-shot GPU samples with no active compute apps and `memory.used=0`. The E2 launch gate then used one `nvidia-smi -l 1` sampling stream and required 5 consecutive idle samples before launch. This keeps the gate strict while avoiding a repeated first-sample utilization artifact.

The accepted watcher gate was:

- `2026-07-06T11:03:37+08:00`: `apps=none`, samples `s1=22,0; s2=0,0; s3=0,0; s4=0,0; s5=0,0; s6=0,0`, `streak=5`.

The production script's own just-in-time gate independently recorded:

- `2026-07-06T11:03:52+08:00` to `2026-07-06T11:03:57+08:00`: apps `none` for all samples; GPU samples `23,0` then five consecutive `0,0`.

`mdrun` started at `2026-07-06T11:03:57+08:00`. The included initial sampler snapshot then shows sustained production GPU use, with utilization around `95-98%` and `memory.used=509 MiB`.

This directory is a launch-gate evidence snapshot only. Production completion requires the final 200 ns raw/result archive and completion sanity/checksum evidence.

## Files

- `watch_gpu_idle_then_launch_rep1.log`: watcher polling history, streaming idle gate, and launch attempt.
- `nvidia_smi_compute_apps_before_mdrun_samples.tsv`: production script compute-app samples before `mdrun`.
- `nvidia_smi_gpu_state_before_mdrun_samples.tsv`: production script GPU util/memory samples before `mdrun`.
- `nvidia_smi_compute_apps_before_mdrun.csv`: final compute-app snapshot before `mdrun`.
- `nvidia_smi_gpu_state_before_mdrun.csv`: final GPU util/memory snapshot before `mdrun`.
- `mdrun_start_time.txt`: recorded `mdrun` start timestamp.
- `nvidia_smi_mdrun_sampler.csv`: initial sampler snapshot after `mdrun` launch.

## References / 所引

- `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260705_rep1_preproduction/README.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/mdrun_start_time.txt`
- E2 run root: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705`

## Referenced by / 被引

- `docs/logs/2026-07-06.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/`
