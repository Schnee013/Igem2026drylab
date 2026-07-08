# Gpr2 WT + ASCR18 Rep1 Repaired Index Route

> Scope: route record for the repaired `index.fixed.ndx` used by E2 `grompp` for `Gpr2_WT + ASCR18` production rep1.

## Decision

The full `index.fixed.ndx` file is intentionally not tracked in the local git repository. It is a 2.4 MB generated text index. The local repository tracks this route record and the launch/gate evidence instead.

The E2 copy below is the authoritative retained file for this production package.

## E2 Locations

| Role | Path |
|---|---|
| Active E2 input used by `grompp` | `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705/input/gromacs/index.fixed.ndx` |
| E2 backup copy | `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705/backups/index_fixed_ndx_20260706T160230+0800/index.fixed.ndx` |
| E2 backup checksum manifest | `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705/backups/index_fixed_ndx_20260706T160230+0800/index.fixed.ndx.sha256` |

## Checksum

```text
e31c78d9679af56c9a701e467cb1be694af15ecaa705789337d2581c808f1cec  index.fixed.ndx
```

The checksum was verified on E2 for both the active input file and the backup copy.

## Use

`index.fixed.ndx` was used only at the `grompp` stage:

```text
step6.6.gro + topol_phase3.top + production.mdp + index.fixed.ndx
  -> grompp
  -> gpr2_wt_ascr18_rep1_200ns.tpr
  -> mdrun
```

The file must not be confused with the archived source `index.ndx`, which was rejected for production because fixed-width atom numbering becomes unsafe past atom `99999`.

## Restore Route

If the active E2 input path is missing but the backup remains available:

```bash
ssh nkuliulab-e2 'cp -p /ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705/backups/index_fixed_ndx_20260706T160230+0800/index.fixed.ndx /ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705/input/gromacs/index.fixed.ndx'
```

If both E2 copies are missing, regenerate a repaired index from `step6.6.gro` and verify it against the checksum above before claiming it is the same input.

## References / 所引

- `experiments/md-simulation/analysis/gpr2_wt_ascr18_production_rep1_20260705/pre_production_audit.md`
- `experiments/md-simulation/analysis/gpr2_wt_ascr18_production_rep1_20260705/command_plan.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260705_rep1_preproduction/grompp_gpr2_wt_ascr18_rep1_200ns.log`

## Referenced by / 被引

- `experiments/md-simulation/analysis/gpr2_wt_ascr18_production_rep1_20260705/command_plan.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260705_rep1_preproduction/README.md`
