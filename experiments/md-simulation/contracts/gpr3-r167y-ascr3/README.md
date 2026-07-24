# Gpr3 R167Y + ASCR3 AutoDL run contracts

These files are the Git-visible control layer for the authorized AutoDL
preproduction and production-launch gate. They do not replace the canonical
accepted input package.

- `autodl_preproduction_contract.json` freezes the system identity, atom count,
  exact GROMACS family, pair-specific 11-warning step6 contract, 100 ps
  benchmark shape, and 200 ns production-TPR shape.
- `geometry_repair_contract.json` is the operational gate after the 500-step
  unconstrained small-step repair.
- `geometry_post_em_contract.json` is the stricter geometry gate after the
  package's original 5000-step constrained `step6.0` minimization.

For deployment, preserve this layout under `<RUN_ROOT>/input/`:

```text
input/
├── contracts/
│   └── *.json
├── gromacs/
│   ├── step5_complex_ion.gro
│   ├── topol.top
│   └── toppar/
└── scripts/
```

The geometry thresholds are labeled operational diagnostics. A geometry PASS
does not replace the GROMACS EM convergence gate or the issue scan.

## References / 所引

- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/r167y/final_input_contract.json`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/r167y/final_manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`

## Referenced by / 被引

- `experiments/md-simulation/scripts/run_gpr_md_preproduction.sh`
- `experiments/md-simulation/scripts/prepare_gpr_md_production_gate.sh`
- `codex/docs/plans/autodl-gpr3-r167y-md-plan-20260717.md`
