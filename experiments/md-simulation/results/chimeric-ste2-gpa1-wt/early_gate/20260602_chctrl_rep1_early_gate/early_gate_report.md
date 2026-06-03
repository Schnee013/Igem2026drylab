# Chctrl rep1 early stability gate

Run id: `20260602_chctrl_rep1_early_gate`

System: `chimeric-ste2-gpa1-wt` (`chctrl`), replicate `rep1`

Gate scope: 150 ns full-system early stability gate, evaluated on a 194.8 ns snapshot. This is a mid-run project gate, not the 500 ns final production endpoint.

## Authority and interpretation boundary

- Primary route: `codex/docs/plans/e2-chimeric-md-restart.md`, sections `Early stability gate` and `Analysis Route`.
- Method summary: `docs/modeling/P0-md-simulation.md`, sections 4.3 and 4.4.
- Decision log: `docs/logs/2026-06-01.md`.
- Current router: `docs/INDEX.md`.
- Canonical selection config was read from `experiments/md-simulation/analysis/chimeric_systems.json`; it was not modified.
- Gate-local config: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/chimeric_systems.early_gate.json`.

All metric cutoffs in this report are project operational heuristics unless an exact method/source pointer is already present in the project docs. They are not treated as literature thresholds.

## Snapshot provenance

Source production directory:

`/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1`

Remote isolated snapshot directory:

`/ifs1/User/dengwei/igem/md-simulation/early_gate_snapshots/20260602_chctrl_rep1_early_gate/`

Local isolated early-gate directory:

`experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/`

Snapshot metadata from `raw/rep1/provenance.txt`:

| Field | Value |
|---|---|
| Copy begin | 2026-06-02 07:27:13 CST |
| Copy end | 2026-06-02 07:27:13 CST |
| Checkpoint line | `Writing checkpoint, step 97352300 at Tue Jun  2 07:22:20 2026` |
| Latest progress at copy start | step `97400000`, time `194.800 ns` |
| GROMACS binary | `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` |

Snapshot file hashes from `raw/rep1/SHA256SUMS.txt`:

| File | SHA256 |
|---|---|
| `prod.tpr` | `fccbbbcb604a94b18231c8b807063dfab698843817de06d86cd0953ace19295e` |
| `prod.log` | `e38478a4fec0f10738c0d1186a8bac3d4647464247c537387274a8f8e5183529` |
| `prod.cpt` | `808d7b3a52ea0c6c6561f1c7b4d058de965cefa95b40de0e1b70f1f80adfea17` |
| `prod.xtc` | `31ac1ed40c8965c0f4694257ac3ec747e070931eef3b640bd9c6f0a591e86e86` |
| `prod.edr` | `48d1fb44194f70f5a0f61550e20e7e8bc11f39e7771c45fa3bd24271ec90522b` |

Local checksum verification with `shasum -a 256 -c SHA256SUMS.txt` passed for all five raw snapshot files.

The isolated `raw/shared/step5_input.pdb` was copied from `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/shared/step5_input.pdb`; both files have SHA256 `0382a7f654522688cf057e57495d940e739483fdb027f1483b485a55c5891306`.

## Current production status

Read-only E2 recheck at 2026-06-02 07:51:40 CST:

- tmux session exists: `e2_chctrl_rep1_resume_20260530`.
- Active production process: PID `559051`, command `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin.AVX2_256/gmx_mpi mdrun -deffnm prod -cpi prod.cpt -append -ntomp 24 -pin on -nb gpu -pme gpu -bonded gpu`.
- GPU check: NVIDIA A100-SXM4-80GB, `gmx_mpi` using the GPU with high SM utilization at the time of sampling.
- `prod.log` latest parsed progress: step `97900000`, time `195.800 ns`.
- Latest checkpoint in live production log: `Writing checkpoint, step 97657800 at Tue Jun  2 07:37:20 2026`.
- Narrow scan of live `prod.log` found no hits for `Fatal error`, `LINCS WARNING`, `Constraint error`, `segfault`, `nan`, or `final coordinates`.

The running production was not interrupted. No `grompp` or new `mdrun` was started for this gate.

## Trajectory and checkpoint readability

Raw snapshot checks:

- `raw/rep1/gmx_check_xtc.txt`: XTC readable, 1949 frames, 100 ps timestep, time range 0 to 194800 ps. The XTC contains 14365 atoms.
- `raw/rep1/gmx_check_cpt.txt`: checkpoint readable, full-system checkpoint has 263906 atoms; last frame time `194704.594 ps`.
- `analysis/system_sanity/energy_sanity/gmx_energy_temp_pressure_potential.log`: EDR readable through 194800 ps.
- `analysis/system_sanity/energy_sanity/gmx_energy_box_density.log`: box and density terms readable through 194800 ps.

Processed protein trajectory:

- Local `gmx` and `gmx_mpi` were not available in PATH; no software was installed.
- Processing was done on the E2 snapshot with the verified GROMACS 2025.4 MPI-CUDA binary, then synced back locally.
- Final processed files:
  - `processed/rep1/protein_ref.pdb`
  - `processed/rep1/prod_protein.xtc`
  - `processed/rep1/gmx_check_protein.txt`
- `processed/rep1/gmx_check_protein.txt`: protein XTC readable, 1949 frames, 100 ps timestep, 14365 atoms.

Processing QC:

- The first `pbc whole -> center pbc mol -> fit` route is preserved under `qc/initial_pbc_mol_route/`.
- That route produced late-frame PBC artifacts, including COM distances near 105 A, alpha5 iRMSD near 56 A, and zero retained contacts at 193.0 and 194.5 ns.
- The final analysis therefore uses the cluster route in `processed/rep1/`. Tail-frame values after cluster processing remain in the expected local range: COM about 15.4-15.9 A / 11.6-11.9 A for the two receptor clusters at 194.5-194.8 ns, alpha5 iRMSD about 3.0-3.6 A, and final sampled contact retention 0.588 at 194.5 ns.

## Analysis execution

The gate was run with an isolated result directory and a gate-local config:

- `CHIMERIC_MD_CONFIG=experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/chimeric_systems.early_gate.json`
- `CHIMERIC_MD_REPS=1`
- `MPLCONFIGDIR=/private/tmp/mpl-drylab`

`src/modeling/md-analysis/common.py` now supports `CHIMERIC_MD_REPS`; the default behavior remains `rep1`, `rep2`, `rep3` when the environment variable is unset. The early gate used only `rep1`; no pseudo-replicates were created. Some plot filenames still contain `3rep` because the existing scripts use those names, but the CSV contents are `rep1` only.

## Metric summary

Primary summary table:

`analysis/early_gate_metrics_summary.csv`

| Metric | Result | File pointer | Gate read |
|---|---:|---|---|
| Raw XTC coverage | 1949 frames, 0-194.8 ns, 100 ps interval | `raw/rep1/gmx_check_xtc.txt` | Pass for >=150 ns gate |
| Protein XTC coverage | 1949 frames, 0-194.8 ns, 100 ps interval | `processed/rep1/gmx_check_protein.txt` | Pass for analysis input |
| Global backbone RMSD | after100 mean 7.979 A, final 8.450 A | `analysis/convergence/rmsd_summary.csv` | No gross instability by project trend review |
| Protein CA Rg | after100 mean 40.607 A, final 40.601 A | `analysis/convergence/rg_summary.csv` | Stable compactness trend |
| alpha5/eCT iRMSD | after100 mean 2.724 A, max 4.255 A, final 3.380 A | `analysis/alpha5_irmsd/a5_irmsd.csv` | Pass-like by project operational 3/5 A band |
| BSA fraction | after100 mean 1.0747, min 0.9460, final sampled 1.0908 | `analysis/bsa/bsa.csv` | Interface retained by project operational >=0.80 heuristic |
| Contact persistence | 34 initial contacts; after100 mean 0.6314, min 0.4118, final sampled 0.5882 | `analysis/contacts/contact_persistence.csv` | Mostly retained; transient low min is a caveat |
| Interface H-bond occupancy | top pair occupancy 0.6077; 7 pairs >=0.10 | `analysis/hbond/hbond_summary.csv` | Supports persistent interface contacts by reporting heuristic |
| COM distance cluster A | after100 mean 15.561 A, slope -0.000686 A/ns | `analysis/com_distance/com.csv` | No monotonic separation |
| COM distance cluster B | after100 mean 11.501 A, slope 0.002470 A/ns | `analysis/com_distance/com.csv` | No monotonic separation |
| Global RMSF | mean CA RMSF 3.164 A, max CA RMSF 18.356 A | `analysis/rmsf/rmsf.csv` | Baseline generated; no chctrl junction threshold configured |
| Energy sanity | temperature average 303.192 K; pressure average 0.782 bar; potential drift -953.834 kJ/mol | `analysis/system_sanity/energy_sanity/` | Coarse sanity acceptable |
| Box/density sanity | Box X/Y/Z averages 11.543/11.543/19.3096 nm; density average 1029 kg/m3 | `analysis/system_sanity/energy_sanity/` | Coarse sanity acceptable |

BSA method note:

- Local `mdtraj` and `freesasa` were not used for this gate.
- BSA was computed with E2 `gmx_mpi sasa` on the cluster-fixed protein trajectory, using 0.5 ns stride and `ndots=240`.
- The GROMACS `sasa` logs warn that masses and radii were guessed from PDB residue/atom names. This does not change the qualitative gate read, but BSA should remain a project operational retention metric here rather than an absolute physical surface-area claim.

## Gate judgement

Judgement: `pass` for the chctrl rep1 early stability gate.

Reasoning:

- The snapshot was taken after a correctly written checkpoint and covers 194.8 ns, exceeding the 150 ns default early gate.
- Raw snapshot files and processed protein trajectory are readable by GROMACS checks.
- Live production remained active after the snapshot and was still advancing at the 07:51 CST recheck.
- No fatal/error evidence was found in the narrow `prod.log` scan.
- alpha5 iRMSD, BSA, contact persistence, H-bond occupancy, COM distance, RMSD/Rg, RMSF baseline, and coarse energy/box/density checks do not show gross separation, persistent interface collapse, unreadable trajectory, or system instability.
- The only notable caveat is transient contact retention below the project majority-retention heuristic at one or more post-100 ns samples. Because BSA remains retained, final sampled contact retention remains above 0.50, COM distances do not separate, and H-bond occupancy is persistent, this caveat does not justify stopping the replicate at the early gate.

Recommendation:

- Continue the current E2 `mdrun` from the same live `prod.cpt` toward the 500 ns final production target.
- Do not restart, do not migrate checkpoint, and do not start a new production job based on this gate.
- Re-evaluate at final production completion with the normal completion gate: normal `prod.log` termination, updated `prod.cpt`, synced `prod.tpr/prod.gro/prod.xtc/prod.edr/prod.log`, checksums, and GROMACS readability checks.
