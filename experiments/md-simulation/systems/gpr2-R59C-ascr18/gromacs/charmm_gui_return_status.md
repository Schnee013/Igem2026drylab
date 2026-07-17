# CHARMM-GUI return intake: Gpr2_R59C receptor-membrane base

> Intake date: 2026-07-16
>
> CHARMM-GUI job ID: `8417129094`
>
> Gate result: `RETURN_RECEIVED_BASE_ONLY`; the receptor-membrane package is
> present and internally inventory-consistent, but ASCR18 is absent and the
> system is not runnable as the intended holo candidate.

## Provenance and storage

- Manual download source: `/Users/roy/Downloads/charmm-gui.tgz`.
- System-local archive copy:
  `gromacs/charmm_gui_returned/charmm-gui-8417129094.tgz`.
- Archive SHA256: `9a1a97593ea96fc36ffc52362c2b9a69902b2b98e38b7d7b39e3bfaf199d9cb7`
- Archive size: `42,850,469` bytes
- Exact result URL: `pending`; job ID is known, but no URL is inferred from it.
- Extracted payload: `gromacs/charmm_gui_returned/charmm-gui-8417129094/`
- Tracking class: ignored local-only operation payload. The compact manifest
  beside this file is the Git-visible recovery and validation record.

The system-local archive copy is byte-identical to the manual download. The
archive has one top-level directory and 162 entries. A fresh extraction
compared with the existing system-local tree using `diff -qr` produced no
differences. Key GROMACS files include `step5_input.gro`, `topol.top`,
`index.ndx`, all six `step6.*.mdp` files, `step7_production.mdp`, and
`toppar/`.

## Receptor-membrane base composition

The returned package is not a protein-only vacuum system. It contains:

| Component | Count |
|---|---:|
| `PROA` | 1 |
| POPC | 201 (`99` upper + `102` lower) |
| `POT` | 87 |
| `CLA` | 100 |
| `TIP3` | 32,405 |

`step5_input.gro` declares 130,720 atoms and a
`9.02432 x 9.02432 x 17.21910 nm` orthorhombic box. `PROA.itp` contains 406
unique residue numbers and 6,384 protein atoms; residue 59 is `CYS`, confirming
the requested R59C receptor identity at this intake layer.

The user-reported builder area record is: protein area
`1378.19826 / 1181.16163 A^2` (upper/lower), lipid area
`6761.7 / 6966.6 A^2`, total area `8139.89826 / 8147.76163 A^2`, protein X/Y
extent `35.28 / 37.46 A`, and builder A/B `90.24 / 90.24 A`.

## Ligand finding

ASCR18 is not present in the returned coordinates or topology:

- `[ molecules ]` contains only `PROA`, `POPC`, `POT`, `CLA`, and `TIP3`.
- No ASCR18 coordinate or topology file exists inside the returned GROMACS
  package.
- Text hits for `ASCR` are limited to the uploaded filename and an unrelated
  substring in the generic CGenFF library, not an ASCR18 molecule.

This matches the staged pipeline: CHARMM-GUI received the oriented receptor
only and built the membrane/solvent base. The package-local canonical ligand
pose and topology exist separately as
`../ligand/Gpr2_R59C_ascr18_pose1.sdf`, `ASCR18.itp`,
`posre_ASCR18.itp`, and `toppar/cgenff_ASCR18.itp`. They still need
receptor-frame coordinate completion/insertion, clash review, and topology
merge before any minimization or benchmark.

## Builder-log intake

The main CHARMM stages inspected at intake end with
`NORMAL TERMINATION BY NORMAL STOP` and report maximum warning level 1.
`step4_lipid_pentest.out` contains only the lipid-ring and protein-surface
section labels and no listed penetration candidate. This is builder-base
evidence only; ligand insertion can introduce new protein/POPC clashes and
must be reviewed separately.

## Remaining gate

1. Complete and align ASCR18 coordinates into the returned receptor frame.
2. Review ASCR18-protein and ASCR18-POPC clashes; remove lipids only if the
   coordinate evidence requires it.
3. Merge ligand includes and exactly one ASCR18 molecule into the final
   topology.
4. Generate the final holo index from the final coordinates; do not reuse the
   ligand-free builder index as final evidence.
5. Run the mutant-specific `grompp` warning gate, then the matched WT
   smoke/100 ps benchmark route.

## References / 所引

- `gromacs/charmm_gui_return_manifest.tsv`
- `gromacs/charmm_gui_returned/charmm-gui-8417129094.tgz`
- `gromacs/charmm_gui_returned/charmm-gui-8417129094/gromacs/step5_input.gro`
- `gromacs/charmm_gui_returned/charmm-gui-8417129094/gromacs/topol.top`
- `gromacs/charmm_gui_returned/charmm-gui-8417129094/gromacs/toppar/PROA.itp`
- `ligand/Gpr2_R59C_ascr18_pose1.sdf`
- `gromacs/ASCR18.itp`

## Referenced by / 被引

- `PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-16.md`
- `docs/logs/2026-07-17.md`
