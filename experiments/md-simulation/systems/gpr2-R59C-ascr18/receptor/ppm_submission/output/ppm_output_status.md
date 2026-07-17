# Gpr2_R59C + ASCR18 PPM output route

> Last updated: 2026-07-15
>
> Status: the 2026-07-15 current-input PPM 2.0 rerun supersedes the prior
> checksum-migration hold for Gpr2. The CHARMM-GUI handoff is provenance-ready;
> the MD package remains non-runnable.

## Current Authority

| Layer | Current pointer |
|---|---|
| Submitted input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| Versioned rerun status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md` |
| Versioned rerun manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_manifest.tsv` |
| Accepted upload contract | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` |

The submitted input SHA256 is
`5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4`.
The new PPM result job key is `20260715_121304156_5202956`; the accepted
DUM-free output and upload copy hash to
`5e3105a86a865ce962e46902d772ddf841f1124680d381e53cb75ffb3c09fe56`.
Detailed URLs, PPM orientation values, record counts, and validation live only
in the versioned rerun status above.

## Historical Boundary

The root-level raw/clean PDB bodies and `ppm_output_manifest.tsv` record the
pre-rerun 2026-07-05 chain. Their historical checksum mismatch is not silently
rewritten. It is operationally superseded by the explicitly versioned
2026-07-15 job that used the current input body.

## Remaining Gate

- [x] current Gpr2 input bound to a versioned PPM 2.0 result
- [x] DUM-free upload contract regenerated and checksum-validated
- [ ] CHARMM-GUI Membrane Builder returned package
- [ ] final ASCR18 receptor-frame insertion and clash review
- [ ] final topology and molecule-count review
- [ ] package-local index regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt`

## References / 所引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-15.md`
