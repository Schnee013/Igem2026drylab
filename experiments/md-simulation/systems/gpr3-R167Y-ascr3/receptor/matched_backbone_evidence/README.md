# Gpr3 R167Y matched-backbone local-EM evidence

> Scope: compact reproducibility evidence for the accepted receptor-only,
> pre-CHARMM-GUI local energy minimization.

This directory contains the two small artifacts explicitly promoted from the
local run. The method and coordinate-audit authority remains
`receptor/matched_backbone_status.md`; the canonical submission body remains
`receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`.

| File | Role | SHA256 |
|---|---|---|
| `prepare_gpr3_matched_em.py` | exact-backbone restoration, frozen-index generation, minimized-sidechain merge, and coordinate audit | `1163acd3d69dca678043f4b01aea6da29995db1ed28fe680fea199f6b939da53` |
| `em_local.log` | complete accepted CHARMM36m/GROMACS 2025.2 local-EM run log | `b322474268587a668b0095a6ea62244da2bae321ad27842b1e4c79e41f7abb93` |

The full log is the authority for the executable, command, minimizer settings,
and convergence record. Runtime `TPR/TRR/EDR/GRO`, generated topology, and
temporary working files are not duplicated into Git. ASCR3 was absent from this
local EM, so this evidence cannot describe a ligand-pose change.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`
- `docs/ops/payload-tracking-policy.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `docs/logs/2026-07-17.md`
