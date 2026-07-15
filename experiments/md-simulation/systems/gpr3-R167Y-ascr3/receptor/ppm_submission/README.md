# Gpr3_R167Y + ASCR3 PPM 2.0 submission package

> Date: 2026-07-06
>
> Last audited: 2026-07-12
>
> Status: PPM output and current DUM-free handoff bodies are present, but the
> historical-to-current checksum migration is unresolved. CHARMM-GUI upload is
> on provenance hold until the migration is reconciled or replaced by a new,
> versioned PPM/cleaning run.

## What This Contains

This directory contains the current local hyphen-free PPM 2.0 input copy plus the retrieved raw PPM output, DUM-free clean PPM-oriented receptor PDB, manifest, and status record. The historical log records a different input checksum for the completed PPM submission, so the current local input must not be presented as the byte-identical historical submission body. The current clean output is byte-identical to the intended Git-tracked CHARMM-GUI handoff copy, but both remain on provenance hold because their checksum differs from the 2026-07-06 log.

| Field | Value |
|---|---|
| Manual PPM input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| Clean receptor source | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb` |
| Clean receptor status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md` |
| Manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/manifest.tsv` |
| Current local input SHA256 | `5116e802a87b4b8b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` |
| Historical submitted input SHA256 | `32dd45cb114e8a59f9ced2d90215315929f01b4a821c2b57be47bdaf8b3b06e5` |
| Atom count | `3158` |
| Residue count | `401` |
| CA count | `401` |
| Chain | `A` |
| Mutation check | `167=TYR` |
| HETATM count | `0` |
| DUM count | `0` |

## Manual PPM 2.0 Record Template

Use PPM 2.0 for this single-chain GPCR package. Upload only:

```text
experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb
```

The settings below record the manual PPM submission route used for this package.
The current raw and clean PPM outputs already exist under `output/`.

Current PPM 2.0 settings for this package:

| Setting | Value |
|---|---|
| UI route | `https://opm.phar.umich.edu/ppm_server2` |
| Fallback UI route | `https://opm.phar.umich.edu/ppm_server2_cgopm` |
| Upload field | `pdbFile` |
| Topology (N-ter) | `in` / `topologyIn=true` |
| Include heteroatoms | `no` / `heteroatoms=false` |
| Optional email | leave blank unless intentionally used |

After the manual submission, save the downloaded/raw PPM output under:

```text
experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb
```

The DUM-free clean output for CHARMM-GUI is retained under:

```text
experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb
```

If a future resubmission changes the raw output, update `output/ppm_output_manifest.tsv`
and `output/ppm_output_status.md` from the new raw/clean files before using the
package for CHARMM-GUI. No active repo helper script is retained for this one-off
ingestion route.

The retrieved PPM values are recorded in `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md`:

| Field | Value |
|---|---|
| PPM server/version | PPM 2.0 |
| Historical submitted file SHA256 | `32dd45cb114e8a59f9ced2d90215315929f01b4a821c2b57be47bdaf8b3b06e5` |
| Current local input SHA256 | `5116e802a87b4b8b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` |
| Submission date/time | `2026-07-05 17:47:57.017 result-url timestamp; retrieved 2026-07-06 Asia/Shanghai` |
| Output file SHA256 | `580400cc55ab8a6b08b3777b77f8b4974be74c46331915e347df1b4db0235cad` |
| Full membrane thickness | `31.6 +/- 1.1 A` |
| Tilt angle | `7 +/- 1 deg` |
| Transfer energy | `-77.4 kcal/mol` |
| TM segments | `7; A: 1(12-37), 2(47-69), 3(86-109), 4(128-149), 5(166-187), 6(294-315), 7(326-349)` |
| Any PPM warnings | `heteroatoms excluded` |

## Checksum Provenance Boundary

The 2026-07-05 log records the submitted/input body as `32dd45cb...`, while
the current local input and clean-receptor bodies hash to `5116e802...`. The
2026-07-06 log records the clean/upload body as `488c633f...`, while the
current clean and upload-copy bodies hash to `4db73a51...`. The repository
does not retain the old bodies or evidence that explains either replacement.
These are unresolved migrations, not corrected historical values. Do not use
the current upload body until the old-to-current transition is reconciled or a
new PPM/cleaning run is recorded under new checksums.

WT context for comparison only: WT Gpr3 PPM thickness `30.6 +/- 1.0 A`, tilt `6 +/- 1 deg`, transfer energy `-73.5 kcal/mol`, 7 TM segments. Current package values come from the mutant PPM output recorded above.

## Processed Output

| Field | Value |
|---|---|
| Raw PPM output | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` |
| Output manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_manifest.tsv` |
| Output status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md` |

## CHARMM-GUI Handoff Template

After the PPM output is available and cleaned, use the single-chain GPCR Membrane Builder settings from `docs/ops/charmm-gui-membrane-builder.md`:

| Setting | Value |
|---|---|
| Input class | PPM-oriented clean PDB, no DUM `HETATM` |
| Orientation | `Use PDB Orientation` |
| Box | Rectangular |
| Water thickness | `22.5 A` |
| Length of X and Y | `90 A` for Gpr2/Gpr3 single-chain systems |
| Lipid | POPC, upper/lower ratio `1` / `1` |
| Ions | KCl `0.15 M`, neutralizing ions enabled |
| Force field/output | CHARMM36m, GROMACS only |
| Ensemble/temperature | NPT, `303.15 K` |

## Use Gates

- Provenance gate: resolve or supersede both historical-to-current checksum migrations before manual CHARMM-GUI submission.
- PPM-oriented PDB source: the DUM-free clean output or the prepared CHARMM-GUI upload copy; the current local `Gpr3R167YASCR3_ppm2_input.pdb` is retained only for future resubmission and is not claimed as the historical submitted body.
- CHARMM-GUI submission source: the DUM-free clean output or prepared upload copy.
- Smoke/benchmark command planning waits for final coordinates, topology, index, and warning review.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
