# Gpr3_R167Y + ASCR3 current-input PPM 2.0 rerun

> Date: 2026-07-16
>
> Status: this versioned rerun binds the current package-local PPM input to a
> new PPM 2.0 result. It supersedes the old checksum-migration hold for the
> independent-AF3 Gpr3 receptor. A 2026-07-17 route decision retained this
> chain as starting-structure sensitivity evidence and selected the
> WT-oriented matched backbone as the primary CHARMM-GUI handoff. Current
> package status is routed by
> `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`.

## Provenance

| Field | Value |
|---|---|
| Submitted input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| Submitted input SHA256 | `5116e802a87b4b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` |
| PPM server/version | `PPM 2.0` |
| Submission backend | `https://cgopm.cc.lehigh.edu/ppm` |
| Submission fields | `pdbFile`; `topologyIn=true`; `heteroatoms=false` |
| Result job key | `20260716_092235699_8004174` |
| Results page | `https://ppm-results.s3.us-east-2.amazonaws.com/20260716_092235699_8004174/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260716_092235699_8004174/Gpr3R167YASCR3_ppm2_inputout.pdb` |
| Retrieval date | `2026-07-16 Asia/Shanghai` |
| Raw output SHA256 | `035c53d4c96d4e1369fa59953320b81ab6797d64e2c02ceb05136f9c334a26a6` |
| Clean output SHA256 | `6ff4497787bef8105dd0db378667df67833531b536161a94ebc18da96f5c3c63` |
| Manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_manifest.tsv` |

The remote output was downloaded again during verification and matched the
archived raw body byte-for-byte. The clean body was derived by removing the
`1450` PPM membrane-marker records matching `HETATM ... DUM`; the `3158`
protein `ATOM` records were retained unchanged and in the same order.

Both bodies preserve the submitted input remark
`Package-local receptor PDB; PPM/CHARMM-GUI not run here.` This is inherited
input-layer metadata describing the independent-AF3 receptor before
submission. The PPM result is determined by the result job key/page and
byte-identical raw-output checksum above; current repository package state is
determined by the system-local `PACKAGE_STATUS.md`.

## PPM Result

| Field | Value |
|---|---|
| Full membrane thickness | `31.6 +/- 1.1 A` |
| Transfer energy | `-77.4 kcal/mol` |
| Tilt angle | `7 +/- 1 deg` |
| TM segments | `7; A: 1(12-37), 2(47-69), 3(86-109), 4(128-149), 5(166-187), 6(294-315), 7(326-349)` |
| PPM warning | `heteroatoms excluded` |

These are membrane-orientation handoff values, not MD stability or functional
evidence.

## Validation

| Field | Raw output | Clean output / upload copy |
|---|---:|---:|
| Bytes | `335917` | `256167` |
| Atom count | `3158` | `3158` |
| Residue count | `401` | `401` |
| CA count | `401` | `401` |
| Chain | `A` | `A` |
| Mutation check | `167=TYR` | `167=TYR` |
| HETATM count | `1450` | `0` |
| DUM count | `1450` | `0` |

The preserved independent-AF3 sensitivity upload is the byte-identical copy at
`experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`.

## Supersession Boundary

The 2026-07-05 result and its historical-input checksum remain historical
provenance. They are not rewritten as if they had used the current input. This
2026-07-16 job is the versioned independent-AF3 provenance chain because its
submitted input is the current package-local body with SHA256 `5116e802...`.

This clears the provenance question for the independent-AF3 sensitivity
structure; it no longer selects the primary upload. The primary route is
`experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`.
Later local package gates and remote-stage authorization are maintained through
the system-local `PACKAGE_STATUS.md` and their direct gate artifacts.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/Gpr3R167YASCR3_ppm2_output_raw.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/Gpr3R167YASCR3_ppm2_output_clean.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-16.md`
