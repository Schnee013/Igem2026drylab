# Gpr3_R167Y + ASCR3 PPM output route

> Last updated: 2026-07-17
>
> Status: the 2026-07-16 current-input PPM 2.0 rerun superseded the prior
> checksum-migration hold for the independent-AF3 receptor. After the
> 2026-07-17 matched-backbone decision, this lineage is retained as
> starting-structure sensitivity evidence rather than the primary CHARMM-GUI
> handoff. The MD package remains non-runnable.

## Independent-AF3 sensitivity authority

| Layer | Current pointer |
|---|---|
| Submitted input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| Versioned rerun status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md` |
| Versioned rerun manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_manifest.tsv` |
| Preserved sensitivity upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` |

The submitted input SHA256 is
`5116e802a87b4b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21`.
The new PPM result job key is `20260716_092235699_8004174`; the accepted
DUM-free output and upload copy hash to
`6ff4497787bef8105dd0db378667df67833531b536161a94ebc18da96f5c3c63`.
Detailed URLs, PPM orientation values, record counts, and validation live only
in the versioned rerun status above.

The primary matched input now reuses the accepted WT PPM frame and is routed by
`experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`.
Do not submit the independent-AF3 upload for the primary WT/R167Y comparison.

## Historical Boundary

The root-level raw/clean PDB bodies and `ppm_output_manifest.tsv` record the
pre-rerun 2026-07-05 chain. Their historical checksum mismatch is not silently
rewritten. It is operationally superseded by the explicitly versioned
2026-07-16 job that used the current input body.

## Remaining Gate

- [x] current Gpr3 input bound to a versioned PPM 2.0 result
- [x] DUM-free upload contract regenerated and checksum-validated
- [ ] CHARMM-GUI Membrane Builder returned package
- [ ] final ASCR3 receptor-frame insertion and clash review
- [ ] final topology and molecule-count review
- [ ] package-local index regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt`

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-16.md`
