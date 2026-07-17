# Gpr3_R167Y + ASCR3 PPM 2.0 submission package

> Last updated: 2026-07-17
>
> Status: the current package-local input has a versioned PPM 2.0 rerun. The
> former checksum-provenance hold is superseded for the independent-AF3
> receptor. After the matched-backbone decision, this package is retained as
> starting-structure sensitivity evidence and is not the primary submission.

## Independent-AF3 sensitivity route

| Layer | Path |
|---|---|
| PPM input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| Input manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/manifest.tsv` |
| Current PPM evidence | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md` |
| Current output manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_manifest.tsv` |
| Output router / historical boundary | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md` |
| Preserved sensitivity upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` |
| Primary matched route | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md` |

The current input SHA256 is
`5116e802a87b4b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21`.
The current DUM-free PPM output and the upload contract are byte-identical at
SHA256 `6ff4497787bef8105dd0db378667df67833531b536161a94ebc18da96f5c3c63`.

## Submission boundary

Do not submit the independent-AF3 PPM upload above for the primary WT/R167Y
comparison. Submit
`receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
using the adjacent `settings.tsv` and
`docs/ops/charmm-gui-membrane-builder.md`. Do not upload ASCR3 in this
Membrane Builder step.

This handoff is not a runnable MD package.

## Historical Boundary

The 2026-07-05 raw/clean bodies and root output manifest remain historical
provenance. Their old-to-current checksum migration was never reconstructed.
The 2026-07-16 versioned rerun replaces that operational chain without
rewriting the earlier record.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-16.md`
