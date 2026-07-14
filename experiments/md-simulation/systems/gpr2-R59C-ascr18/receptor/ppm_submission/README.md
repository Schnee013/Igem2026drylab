# Gpr2_R59C + ASCR18 PPM 2.0 submission package

> Date: 2026-07-06
>
> Last audited: 2026-07-12
>
> Status: PPM output and current DUM-free handoff bodies are present, but the
> historical-to-current checksum migration is unresolved. CHARMM-GUI upload is
> on provenance hold until the migration is reconciled or replaced by a new,
> versioned PPM/cleaning run.

## What This Contains

This directory contains the current local hyphen-free PPM 2.0 input copy and the processed Gpr2_R59C PPM output. The historical log records a different input checksum for the completed PPM submission, so the current local input must not be presented as the byte-identical historical submission body. The DUM-free `output/Gpr2R59CASCR18_ppm2_output_clean.pdb` is byte-identical to the intended Git-tracked CHARMM-GUI handoff copy, but both remain on provenance hold because their current checksum differs from the 2026-07-06 log.

| Field | Value |
|---|---|
| Manual PPM input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| Clean receptor source | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb` |
| Clean receptor status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md` |
| Manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/manifest.tsv` |
| Current local input SHA256 | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` |
| Historical submitted input SHA256 | `aeaafa1fb325dc3853496cfd6bd8411c5207d2f711580132085774aab7ac4f22` |
| Atom count | `3153` |
| Residue count | `406` |
| CA count | `406` |
| Chain | `A` |
| Mutation check | `59=CYS` |
| HETATM count | `0` |
| DUM count | `0` |

## Manual PPM 2.0 Record Template

Use PPM 2.0 for this single-chain GPCR package. Upload only:

```text
experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb
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
experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb
```

The DUM-free clean output for CHARMM-GUI is retained under:

```text
experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb
```

If a future resubmission changes the raw output, update `output/ppm_output_manifest.tsv`
and `output/ppm_output_status.md` from the new raw/clean files before using the
package for CHARMM-GUI. No active repo helper script is retained for this one-off
ingestion route.

The processed output metadata is recorded in `output/ppm_output_status.md`:

| Field | Value |
|---|---|
| PPM server/version | PPM 2.0 |
| Historical submitted file SHA256 | `aeaafa1fb325dc3853496cfd6bd8411c5207d2f711580132085774aab7ac4f22` |
| Current local input SHA256 | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` |
| Submission backend | `cgopm fallback endpoint https://cgopm.cc.lehigh.edu/ppm` |
| Submission date/time | `2026-07-05 16:55:23.485 result-url timestamp; retrieved 2026-07-06 Asia/Shanghai` |
| Output file SHA256 | `770d02cccac7eae8a29d9afe979e034c16726690d94d07b6f939c795691e5657` |
| Clean output SHA256 | `bde78fd766f1825d13e8285ecac2ea533556d70be273ac78c4af1219e9298997` |
| Full membrane thickness | `33.4 +/- 2.1 A` |
| Tilt angle | `3 +/- 1 deg` |
| Transfer energy | `-74.9 kcal/mol` |
| TM segments | `7; A: 1(26-51), 2(61-85), 3(97-123), 4(142-163), 5(180-201), 6(326-350), 7(357-380)` |
| Any PPM warnings | `heteroatoms excluded` |

## Checksum Provenance Boundary

The 2026-07-05 log records the submitted/input body as `aeaafa1f...`, while
the current local input and clean-receptor bodies hash to `5d8c537b...`. The
2026-07-06 log records the clean/upload body as `a7f5dbe7...`, while the
current clean and upload-copy bodies hash to `bde78fd7...`. The repository
does not retain the old bodies or evidence that explains either replacement.
These are unresolved migrations, not corrected historical values. Do not use
the current upload body until the old-to-current transition is reconciled or a
new PPM/cleaning run is recorded under new checksums.

WT context for comparison only: WT Gpr2 PPM thickness `33.0 +/- 2.0 A`, tilt `3 +/- 2 deg`, transfer energy `-77.8 kcal/mol`, 7 TM segments.

## Processed Output

| Field | Value |
|---|---|
| Raw PPM output | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` |
| Output manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_manifest.tsv` |
| Output status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md` |

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
- PPM-oriented PDB source: `output/Gpr2R59CASCR18_ppm2_output_clean.pdb`; the current local `Gpr2R59CASCR18_ppm2_input.pdb` is retained only for future resubmission and is not claimed as the historical submitted body.
- CHARMM-GUI submission source: the DUM-free clean output. Raw PPM output with DUM `HETATM` records is retained as provenance.
- Smoke/benchmark command planning waits for final coordinates, topology, index, and warning review.

## References / 所引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
