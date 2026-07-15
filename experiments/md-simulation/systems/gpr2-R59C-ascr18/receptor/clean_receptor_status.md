# Gpr2_R59C clean receptor PDB status

> Date: 2026-07-05
>
> Status: clean receptor PDB provenance record. PPM output and CHARMM-GUI upload
> material now exist in the package-local receptor tree.

## Output

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb`

## Validation

| Field | Value |
|---|---|
| Source CIF | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif` |
| AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json` |
| Selected model | `1` |
| Chain | `A` |
| Residue count | `406` |
| Atom count | `3153` |
| CA count | `406` |
| Mutation check | residue `59` = `CYS` |
| Output SHA256 | `5d8c537b4c9fe40268a20098bb6b2b8a3ec40e9935771df25d086f2d5e10a6a4` |

## Gate Status

- [x] PPM 2.0 oriented receptor PDB
- [x] CHARMM-GUI upload PDB and `settings.tsv`
- [ ] CHARMM-GUI Membrane Builder output package
- [ ] ligand coordinate insertion/completion
- [ ] final topology molecule-count check
- [ ] package-local `index.ndx`
- [ ] system-specific warning review

## References / 所引

- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-05.md`
