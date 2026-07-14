# Gpr3_R167Y + ASCR3 PPM 2.0 output status

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
| Manual PPM input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| Raw PPM output | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` |
| Output manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_manifest.tsv` |
| Historical submitted input SHA256 | `32dd45cb114e8a59f9ced2d90215315929f01b4a821c2b57be47bdaf8b3b06e5` |
| Current local input SHA256 | `5116e802a87b4b8b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` |
| Raw output SHA256 | `580400cc55ab8a6b08b3777b77f8b4974be74c46331915e347df1b4db0235cad` |
| Clean output SHA256 | `4db73a5168dfc396872fc24b791556456d8f59b46dd332a6d30b31262e6ebe11` |
| Removed DUM HETATM records | `1450` |

## Checksum Migration Audit

| Layer | Historical log SHA256 | Current body SHA256 | Status |
|---|---|---|---|
| PPM input / clean receptor | `32dd45cb114e8a59f9ced2d90215315929f01b4a821c2b57be47bdaf8b3b06e5` | `5116e802a87b4b8b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` | unresolved replacement |
| DUM-free clean / CHARMM-GUI upload copy | `488c633f6850ad03d0ddb2c9f6ea203353d41b061db571572c9433ed77d91b45` | `4db73a5168dfc396872fc24b791556456d8f59b46dd332a6d30b31262e6ebe11` | unresolved replacement |

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
| Submission date/time | `2026-07-05 17:47:57.017 result-url timestamp; retrieved 2026-07-06 Asia/Shanghai` |
| Results URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_174757017_9935109/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_174757017_9935109/Gpr3R167YASCR3_ppm2_inputout.pdb` |
| Full membrane thickness | `31.6 +/- 1.1 A` |
| Tilt angle | `7 +/- 1 deg` |
| Transfer energy | `-77.4 kcal/mol` |
| TM segments | `7; A: 1(12-37), 2(47-69), 3(86-109), 4(128-149), 5(166-187), 6(294-315), 7(326-349)` |
| Any PPM warnings | `heteroatoms excluded` |

## Validation

| Field | Raw output | Clean output |
|---|---:|---:|
| Atom count | `3158` | `3158` |
| Residue count | `401` | `401` |
| CA count | `401` | `401` |
| Chain | `A` | `A` |
| Mutation check | `167=TYR` | `167=TYR` |
| HETATM count | `1450` | `0` |
| DUM count | `1450` | `0` |

## CHARMM-GUI Handoff

After the checksum-provenance hold is resolved, use `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` as the single-chain GPCR input for CHARMM-GUI Membrane Builder with the package settings in `docs/ops/charmm-gui-membrane-builder.md`: `Use PDB Orientation`, rectangular box, water thickness `22.5 A`, X/Y `90 A`, POPC upper/lower `1`/`1`, KCl `0.15 M`, neutralizing ions, CHARMM36m, GROMACS-only, NPT, `303.15 K`.

## Still Missing

- [ ] historical-to-current input and clean/upload checksum migration resolved or superseded by a versioned rerun
- [ ] CHARMM-GUI Membrane Builder package
- [ ] ligand coordinate insertion/completion aligned to the final receptor package
- [ ] `step6.6.gro` or equivalent final coordinate
- [ ] `topol_phase3.top` or equivalent topology with molecule counts checked
- [ ] package-local `index.ndx` regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt` warning review

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-06.md`
