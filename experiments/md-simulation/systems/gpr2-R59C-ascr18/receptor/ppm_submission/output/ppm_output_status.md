# Gpr2_R59C + ASCR18 PPM 2.0 output status

> Date: 2026-07-06
>
> Last audited: 2026-07-12
>
> Status: PPM raw output and current DUM-free handoff body are present. The
> historical-to-current input and clean/upload checksum migrations remain
> unresolved, so CHARMM-GUI submission is on provenance hold.

## Files

| Field | Value |
|---|---|
| Manual PPM input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| Raw PPM output | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` |
| Output manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_manifest.tsv` |
| Historical submitted input SHA256 | `aeaafa1fb325dc3853496cfd6bd8411c5207d2f711580132085774aab7ac4f22` |
| Current local input SHA256 | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` |
| Raw output SHA256 | `770d02cccac7eae8a29d9afe979e034c16726690d94d07b6f939c795691e5657` |
| Clean output SHA256 | `bde78fd766f1825d13e8285ecac2ea533556d70be273ac78c4af1219e9298997` |
| Removed DUM HETATM records | `1946` |

## Checksum Migration Audit

| Layer | Historical log SHA256 | Current body SHA256 | Status |
|---|---|---|---|
| PPM input / clean receptor | `aeaafa1fb325dc3853496cfd6bd8411c5207d2f711580132085774aab7ac4f22` | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` | unresolved replacement |
| DUM-free clean / CHARMM-GUI upload copy | `a7f5dbe776a862091a76d10b872bf0a1c31eb396df612e00897d0c7ad05ac2ef` | `bde78fd766f1825d13e8285ecac2ea533556d70be273ac78c4af1219e9298997` | unresolved replacement |

The old bodies and an old-to-new migration record are absent. The historical
PPM result remains associated with the historical submitted-input hash; the
current local input is not asserted to be that body. The current clean body is
byte-identical to the package's CHARMM-GUI upload copy, but this only proves
current internal consistency. Resolve the transition or perform a new,
versioned PPM/cleaning run before submission.

## PPM Record

| Field | Value |
|---|---|
| PPM server/version | `PPM 2.0` |
| Submission backend | `cgopm fallback endpoint https://cgopm.cc.lehigh.edu/ppm` |
| Submission date/time | `2026-07-05 16:55:23.485 result-url timestamp; retrieved 2026-07-06 Asia/Shanghai` |
| Results URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_165523485_8819042/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_165523485_8819042/Gpr2R59CASCR18_ppm2_inputout.pdb` |
| Full membrane thickness | `33.4 +/- 2.1 A` |
| Tilt angle | `3 +/- 1 deg` |
| Transfer energy | `-74.9 kcal/mol` |
| TM segments | `7; A: 1(26-51), 2(61-85), 3(97-123), 4(142-163), 5(180-201), 6(326-350), 7(357-380)` |
| Any PPM warnings | `heteroatoms excluded` |

## Validation

| Field | Raw output | Clean output |
|---|---:|---:|
| Atom count | `3153` | `3153` |
| Residue count | `406` | `406` |
| CA count | `406` | `406` |
| Chain | `A` | `A` |
| Mutation check | `59=CYS` | `59=CYS` |
| HETATM count | `1946` | `0` |
| DUM count | `1946` | `0` |

## CHARMM-GUI Handoff

After the checksum-provenance hold is resolved, use `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` as the single-chain GPCR input for CHARMM-GUI Membrane Builder with the package settings in `docs/ops/charmm-gui-membrane-builder.md`: `Use PDB Orientation`, rectangular box, water thickness `22.5 A`, X/Y `90 A`, POPC upper/lower `1`/`1`, KCl `0.15 M`, neutralizing ions, CHARMM36m, GROMACS-only, NPT, `303.15 K`.

## Still Missing

- [ ] historical-to-current input and clean/upload checksum migration resolved or superseded by a versioned rerun
- [ ] CHARMM-GUI Membrane Builder package
- [ ] ligand coordinate insertion/completion aligned to the final receptor package
- [ ] `step6.6.gro` or equivalent final coordinate
- [ ] `topol_phase3.top` or equivalent topology with molecule counts checked
- [ ] package-local `index.ndx` regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt` warning review

## References / 所引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-06.md`
