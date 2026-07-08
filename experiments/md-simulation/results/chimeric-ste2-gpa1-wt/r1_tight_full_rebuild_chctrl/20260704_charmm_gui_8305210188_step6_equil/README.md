# R1 Reduced Chctrl Step6 And Short Production Result

> Date: 2026-07-04
>
> Route: `R1-tight-full-rebuild`
>
> System: `chimeric-ste2-gpa1-wt` / `chctrl`
>
> CHARMM-GUI job: `8305210188`
>
> Status: E2 step6 minimization/equilibration outputs and a 100 ps short production test are archived for the exploratory reduced `chctrl` prototype.

## Scope

This result root records the reduced `chctrl` exploratory prototype generated from CHARMM-GUI job `8305210188` with `120 A` XY and `20.0 A` water thickness.

Candidate smoke tests, candidate benchmarks, and candidate production belong to separate result roots after transfer gates pass.

The padding rule remains `exploratory`: this run is evidence that the chctrl prototype can be built and run briefly on E2. Source-backed rule status and candidate transfer require separate gates.

## Provenance

| Field | Value |
|---|---|
| Remote host | `nkuliulab-e2` |
| Remote directory | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704` |
| Local result root | `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/` |
| E2 GROMACS command | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` |
| GROMACS version | `2025.4-conda_forge` |
| GPU | NVIDIA A100-SXM4-80GB |
| Thread settings | one `gmx_mpi` process, `OMP_NUM_THREADS=24`, `-ntomp 24`, GPU nonbonded/PME/bonded offload for dynamics |

E2-produced `.tpr`, `.cpt`, `.edr`, `.xtc`, and `gmx`-processed evidence in this result root were checked with the recorded E2 GROMACS command, following `environments/e2-md-gromacs.md`.

## Package B: Step6 Gate

Package B ran CHARMM-GUI `step6.0_minimization` through `step6.6_equilibration`.

Key evidence:

- Final step6.6 files exist under `work/`: `.gro`, `.cpt`, `.tpr`, `.edr`, `.xtc`.
- Final step6.6 atom count from `work/step6.6_equilibration.gro`: `257130`.
- `step6.6_equilibration` performance: `39.920 ns/day`, `0.601 hour/ns`.
- E2-side sanity used `gmx dump -s` for `.tpr`, `gmx check -f` for `.xtc`, `gmx check -e` for `.edr`, and `.gro` existence/checksum.
- Step6.6 energy summary from `logs/sanity_energy.log`: temperature `303.201 K`, pressure `0.704 bar`, density `1028.91 kg/m^3`.

Caveat:

- `mdrun_step6.0_minimization.log` contains `86` `LINCS WARNING` matches but the minimization converged to `Fmax < 1000` in `4523` steps. No LINCS/fatal/CUDA/nan matches were found in step6.1-step6.6 equilibration logs.

## Package C: Short Production Test

Package C ran a short production test from Package B step6.6 outputs:

- `-nsteps 50000`
- nominal duration `100 ps` at `dt=0.002 ps`
- output prefix: `production_smoke/r1_chctrl_short_prod`

Key evidence:

- Short production files exist under `production_smoke/`: `.gro`, `.cpt`, `.tpr`, `.edr`, `.xtc`, `.log`, and `_out.mdp`.
- Short production atom count from final `.gro`: `257130`.
- Performance from `logs/mdrun_r1_chctrl_short_prod.log`: `74.362 ns/day`, `0.323 hour/ns`.
- GPU sampling from `logs/nvidia_smi_production_short.csv`: 25 samples, average all-sample GPU utilization `84.36%`, average nonzero utilization `91.70%`, max utilization `99%`, max memory `575 MiB`.
- Short production energy summary from `logs/sanity_short_prod_energy.log`: temperature `303.192 K`, pressure `7.549 bar`, density `1029.21 kg/m^3`.
- No LINCS/fatal/CUDA/nan matches were found in the short production `mdrun` log.

## Checksums

| File | Role |
|---|---|
| `local_download.sha256` | Local checksum manifest after Package B/C download. |
| `logs/manifest_sha256.txt` | E2-side checksum manifest after Package B. |
| `logs/manifest_sha256_after_production_short.txt` | E2-side checksum manifest after Package C. |

Manifest line counts after adding result-root README/source pointers and refreshing the non-self-referential local checksum manifest:

- `local_download.sha256`: `116`
- `logs/manifest_sha256.txt`: `97`
- `logs/manifest_sha256_after_production_short.txt`: `114`

## Interpretation Boundary

This run supports the narrow conclusion that the exploratory reduced `chctrl` prototype can be built through CHARMM-GUI step6 and can produce a short 100 ps production test on E2 with recorded performance and GPU utilization.

Source-backed numeric padding, compute-saving success, candidate-transfer status, and full physical sanity remain pending gates. Candidate systems remain blocked.

Post-comparison update:

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md` records the public/local atom-count comparison.
- The current `120 A` XY / `20 A` water instantiation is Z-only and saves only `-6776` atoms (`-2.57%`) versus the baseline chctrl atom count.
- This result root remains useful as chctrl build/run evidence. Current compute-constraint resolution and candidate-transferable rule status require separate evidence.

## References / 所引

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/route.json`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/build_notes.md`
- `environments/e2-md-gromacs.md`

## Referenced by / 被引

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/source_pointers.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/source_pointers.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`
- `docs/logs/2026-07-04.md`
