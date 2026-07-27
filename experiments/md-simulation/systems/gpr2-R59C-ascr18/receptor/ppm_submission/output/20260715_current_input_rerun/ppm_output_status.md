# Gpr2_R59C + ASCR18 current-input PPM 2.0 rerun

> Date: 2026-07-15
>
> Status: this versioned rerun binds the current package-local PPM input to a
> new PPM 2.0 result. It supersedes the old checksum-migration hold for the
> Gpr2 CHARMM-GUI handoff. The statement that it did not make the MD package
> runnable describes the 2026-07-15 handoff boundary only; current package and
> analysis status is maintained in the system-local
> [`PACKAGE_STATUS.md`](../../../../PACKAGE_STATUS.md).

## Provenance

| Field | Value |
|---|---|
| Submitted input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| Submitted input SHA256 | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` |
| PPM server/version | `PPM 2.0` |
| Result job key | `20260715_121304156_5202956` |
| Results page | `https://ppm-results.s3.us-east-2.amazonaws.com/20260715_121304156_5202956/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260715_121304156_5202956/Gpr2R59CASCR18_ppm2_inputout.pdb` |
| Retrieval date | `2026-07-15 Asia/Shanghai` |
| Raw output SHA256 | `4dd57202ff3e95cc24d08be624ee09ef9c6b6eea43713e86a14a0fdba1b24bc2` |
| Clean output SHA256 | `5e3105a86a865ce962e46902d772ddf841f1124680d381e53cb75ffb3c09fe56` |
| Manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_manifest.tsv` |

The remote output was downloaded again during verification and matched the
archived raw body byte-for-byte. The clean body was derived by removing the
`1946` PPM membrane-marker records matching `HETATM ... DUM`; the `3153`
protein `ATOM` records were retained.

## PPM Result

| Field | Value |
|---|---|
| Full membrane thickness | `33.4 +/- 2.1 A` |
| Transfer energy | `-74.9 kcal/mol` |
| Tilt angle | `3 +/- 1 deg` |
| TM segments | `7; A: 1(26-51), 2(61-85), 3(97-123), 4(142-163), 5(180-201), 6(326-350), 7(357-380)` |
| PPM warning | `heteroatoms excluded` |

These are membrane-orientation handoff values, not MD stability or functional
evidence.

## Validation

| Field | Raw output | Clean output / upload copy |
|---|---:|---:|
| Atom count | `3153` | `3153` |
| Residue count | `406` | `406` |
| CA count | `406` | `406` |
| Chain | `A` | `A` |
| Mutation check | `59=CYS` | `59=CYS` |
| HETATM count | `1946` | `0` |
| DUM count | `1946` | `0` |

The accepted CHARMM-GUI upload contract is the byte-identical copy at
`experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`.

## Supersession Boundary

The 2026-07-05 result and its historical-input checksum remain historical
provenance. They are not rewritten as if they had used the current input. This
2026-07-15 job is the new operational chain because its submitted input is the
current package-local body with SHA256 `5d8c537b...`.

The Gpr2 provenance gate was therefore cleared for manual CHARMM-GUI submission
on 2026-07-15. At that dated handoff, the package was still non-runnable until
the returned CHARMM-GUI output, final ligand coordinates, topology molecule
counts, package-local index, and `grompp` warning review were complete. Those
downstream stages later completed; this PPM record remains historical
provenance, while current state routes through the system-local
`PACKAGE_STATUS.md`.

## References / 所引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/Gpr2R59CASCR18_ppm2_output_raw.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/Gpr2R59CASCR18_ppm2_output_clean.pdb`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-15.md`
