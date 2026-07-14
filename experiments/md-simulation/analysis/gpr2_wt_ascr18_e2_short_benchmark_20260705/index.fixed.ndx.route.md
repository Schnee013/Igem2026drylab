# Gpr2 WT + ASCR18 Short Benchmark Repaired Index Route

> Scope: route record for the generated `index.fixed.ndx` used by the 2026-07-05 E2 short benchmark package.

## Decision

Git tracks this route record instead of the generated 2.4 MB `index.fixed.ndx`
file. The benchmark result package records the derived group sizes and
interpretation boundary.

The local repository tracks this route record and the result package README /
command plan instead.

## Checksum

```text
e31c78d9679af56c9a701e467cb1be694af15ecaa705789337d2581c808f1cec  index.fixed.ndx
```

## Generation

`index.fixed.ndx` was regenerated from:

- `experiments/md-simulation/systems/Gpr2_WT/gromacs/step6.6.gro`

using:

- `experiments/md-simulation/scripts/assemble_complex.py::build_index`

The archived source `experiments/md-simulation/systems/Gpr2_WT/gromacs/index.ndx`
remains the source-system index; this generated index belongs to the benchmark
package route.

## Recorded Group Sizes

The retained benchmark README records:

| Group | Atoms |
|---|---:|
| `SOLU` | 6,451 |
| `MEMB` | 26,532 |
| `SOLV` | 99,495 |
| `SOLU_MEMB` | 32,983 |
| `SYSTEM` | 132,478 |
| `TIP3` | 99,300 |

## References / 所引

- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/command_plan.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- `experiments/md-simulation/scripts/assemble_complex.py`

## Referenced by / 被引

- `docs/logs/2026-07-05.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
