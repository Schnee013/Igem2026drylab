# Gpr3_R167Y clean receptor PDB status

> Date: 2026-07-05
>
> Status: independent-AF3 receptor provenance record retained for
> starting-structure sensitivity only. The primary matched-backbone route is
> defined in `matched_backbone_status.md`.

## Output

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb`

## Validation

| Field | Value |
|---|---|
| Source CIF | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif` |
| AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json` |
| Selected model | `1` |
| Chain | `A` |
| Residue count | `401` |
| Atom count | `3158` |
| CA count | `401` |
| Mutation check | residue `167` = `TYR` |
| Output SHA256 | `5116e802a87b4b8b8b67f5c29b8ff574b7917962ab1cb90a7a18ce21dd3e1d21` |

## Gate Status

- [x] independent-AF3 PPM 2.0 oriented receptor PDB retained
- [x] independent-AF3 CHARMM-GUI upload PDB retained as sensitivity input
- [x] matched-backbone primary CHARMM-GUI upload prepared separately
- [ ] CHARMM-GUI Membrane Builder output package
- [ ] ligand coordinate insertion/completion
- [ ] final topology molecule-count check
- [ ] package-local `index.ndx`
- [ ] system-specific warning review

## References / 所引

- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-05.md`
