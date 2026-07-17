# CHARMM-GUI return intake: Gpr3 R167Y matched-backbone receptor-membrane base

> Intake date: 2026-07-17
>
> CHARMM-GUI job ID: `8426884163`
>
> Gate result: `RETURN_RECEIVED_MATCHED_BACKBONE_BASE_ONLY`; this is the
> WT-oriented exact-backbone/local-EM R167Y package, not the independent-AF3/PPM
> mutant route. The receptor-membrane package is present and internally
> inventory-consistent, but ASCR3 is absent by design and neither matched arm is
> runnable yet.

## Provenance and storage

- Original manual download path: `/Users/roy/Downloads/charmm-gui (1).tgz`
  (no longer present at the 2026-07-17 matched-label re-audit; the verified
  system-local archive below is now the local recovery source).
- System-local archive copy:
  `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone.tgz`.
- Archive SHA256:
  `822b6ce3669da94c198f0424856399aa9c8505b7d5034ff223456fbbcbc5d595`.
- Archive size: `44,897,978` bytes.
- Extracted payload:
  `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/`.
- Tracking class: ignored local-only operation payload. The compact manifest
  beside this file is the Git-visible recovery and validation record.

The byte-identical archive retains CHARMM-GUI's internal top-level directory
name `charmm-gui-8426884163`; the system-local archive filename and extracted
directory are explicitly labeled `gpr3-r167y-matched-backbone` to prevent
confusion with the retained independent-AF3/PPM sensitivity route. The archive
has one top-level directory and 160 entries. The extracted tree has the same
160 entries plus its root. A fresh extraction compared with the system-local
tree using `diff -qr` produced no differences.

The archived upload PDB has SHA256
`6b79e0353379eb9bce9bf7d28b896e64e6b74e7b8bd3e5e888ce3222382c4d0f`,
which is byte-identical to the accepted matched submission input
`Gpr3R167YASCR3_matched_charmmgui_input.pdb`. The independent-AF3/PPM upload
`Gpr3R167YASCR3_charmmgui_input.pdb` has a different SHA256,
`6ff4497787bef8105dd0db378667df67833531b536161a94ebc18da96f5c3c63`;
it is not the input archived by job `8426884163`.

## Builder configuration and base composition

`input.config.dat` records a `90.1752515 x 90.1752515 x 184.305 A` builder
cell, CHARMM36m, GROMACS-only output, and no HMR. The GROMACS production
template uses a 2 fs step, `303.15 K`, and semi-isotropic pressure coupling.

The returned receptor-membrane base contains:

| Component | Count |
|---|---:|
| `PROA` | 1 |
| POPC | 203 (`102` upper + `101` lower) |
| `POT` | 96 |
| `CLA` | 98 |
| `TIP3` | 35,364 |

`step5_input.gro` declares 139,798 atoms and a
`9.01753 x 9.01753 x 18.43050 nm` orthorhombic box. `PROA.itp` contains 401
unique residue numbers and 6,310 protein atoms; residue 167 is `TYR`,
confirming the requested matched R167Y receptor identity at this intake layer.

## Ligand boundary

ASCR3 is not present in the returned coordinates or topology:

- `[ molecules ]` contains only `PROA`, `POPC`, `POT`, `CLA`, and `TIP3`.
- No ASCR3 coordinate or topology file exists inside the returned GROMACS
  package.
- The archived matched upload contains receptor atoms only.

This is expected. The canonical 46-atom `ASCR3_pose_completed.gro` remains in
the independent docking-receptor frame. It must first be transformed through
the docking-receptor-to-matched-WT alignment and then inserted separately into
the WT and R167Y receptor-membrane bases.

## Builder-log intake

The inspected CHARMM stages from PDB reader through `step5_input.out` all end
with `NORMAL TERMINATION BY NORMAL STOP`. `step4_lipid_pentest.out` contains
only the lipid-ring and protein-surface section labels and lists no penetration
candidate. These checks establish builder-base integrity only; ASCR3 insertion
requires a new clash and warning review.

## Remaining gate

1. Derive the docking-receptor-to-matched-WT transform for the selected ASCR3
   pose.
2. Insert the transformed 46-atom ASCR3 separately into the reused WT job
   `7628627163` receptor-only base and this matched R167Y base.
3. Review ASCR3-protein and ASCR3-POPC clashes independently for both arms.
4. Merge ligand includes and exactly one ASCR3 molecule into each final
   topology.
5. Generate each final holo index from its final coordinates.
6. Run pair-specific `grompp` warning gates before any smoke or benchmark
   command is accepted.

## References / 所引

- `gromacs/charmm_gui_return_manifest.tsv`
- `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone.tgz`
- `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/gromacs/step5_input.gro`
- `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/gromacs/topol.top`
- `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/gromacs/toppar/PROA.itp`
- `receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- `gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro`

## Referenced by / 被引

- `PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-17.md`
