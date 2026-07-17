# Gpr2_R59C + ASCR18 PPM 2.0 submission package

> Last updated: 2026-07-15
>
> Status: the current package-local input has a versioned PPM 2.0 rerun. The
> former checksum-provenance hold is superseded for Gpr2, and the current
> DUM-free upload contract is ready for manual CHARMM-GUI submission.

## Current Route

| Layer | Path |
|---|---|
| PPM input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| Input manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/manifest.tsv` |
| Current PPM evidence | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md` |
| Current output manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_manifest.tsv` |
| Output router / historical boundary | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md` |
| CHARMM-GUI upload PDB | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` |
| CHARMM-GUI settings | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv` |

The current input SHA256 is
`5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4`.
The current DUM-free PPM output and the upload contract are byte-identical at
SHA256 `5e3105a86a865ce962e46902d772ddf841f1124680d381e53cb75ffb3c09fe56`.

## Manual Handoff

Submit only the upload PDB above through CHARMM-GUI Membrane Builder using the
adjacent `settings.tsv` and `docs/ops/charmm-gui-membrane-builder.md`.

The accepted settings are `Use PDB Orientation`, rectangular `90 A` X/Y box,
`22.5 A` water thickness, POPC upper/lower `1/1`, KCl `0.15 M` with
neutralization, CHARMM36m, GROMACS-only output, NPT, and `303.15 K`.

This handoff is not a runnable MD package. After CHARMM-GUI returns the GROMACS
output, archive the returned package and complete ASCR18 receptor-frame
insertion, clash review, topology molecule counts, package-local index, and
the system-specific `grompp` warning gate before benchmark planning.

## Historical Boundary

The 2026-07-05 raw/clean bodies and root output manifest remain historical
provenance. Their old-to-current checksum migration was never reconstructed.
The 2026-07-15 versioned rerun replaces that operational chain without
rewriting the earlier record.

## References / 所引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-15.md`
