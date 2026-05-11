# chctrl Phase C5 batch 1+2 summary

> Generated 2026-04-29 by Codex. This summarizes chctrl (`chimeric-ste2-gpa1-wt`) protein-only trajectory analysis. MM-PBSA was not run because Slurm dependency check found `gmx_MMPBSA` unavailable and it is not required for the current go/no-go evidence layer.
>
> Source-audit update 2026-04-29: numeric labels such as `<3 Å`, `>5 Å`, `BSA >=0.80`, `contact >0.50`, and `H-bond occupancy >10%` are **project operational heuristics unless explicitly tool-supported**. Do not cite them as “Bauer 2022” or universal literature thresholds. See `cutoff_source_audit.md`.

## Processing route

- Source: three completed chctrl production MD replicates.
- Effective trajectory route: Slurm GROMACS 2025.2, protein-only `prod.xtc`, `-pbc nojump`, protein centering, backbone fit.
- Invalid first-route outputs from `-pbc mol` were deleted and are not used.
- Batch 2 used stride=50 (one frame per 5 ns) for BSA/contact trend analysis after the stride=5 BSA attempt exceeded 30 min.

## Outputs

- Batch 1 report: `chctrl_phase_C5_batch1_summary.md`
- BSA: `bsa/bsa.csv`, `bsa/bsa_3rep.png`, `bsa/bsa_fraction_3rep.png`
- Contact persistence: `contacts/contact_persistence.csv`, `contacts/initial_contact_occupancy.csv`, `contacts/contact_persistence_3rep.png`

## Judgement snapshot

### Batch 1 convergence

- rep1: final100/after100 RMSD slope = -0.00836 A/ns; mean RMSD = 10.45 A
- rep2: final100/after100 RMSD slope = 0.01655 A/ns; mean RMSD = 8.86 A
- rep3: final100/after100 RMSD slope = 0.001325 A/ns; mean RMSD = 9.49 A

### Batch 1 alpha5 iRMSD

- rep1: after100 mean=4.26 A, max=7.46 A => WARN by project operational 3-5 A band
- rep2: after100 mean=3.79 A, max=6.40 A => WARN by project operational 3-5 A band
- rep3: after100 mean=2.97 A, max=5.27 A => PASS-like by project operational <3 A band

### Batch 1 H-bond

- rep1: top pair occupancy=0.492; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5
- rep2: top pair occupancy=0.453; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5
- rep3: top pair occupancy=0.459; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5

### Batch 1 COM distance

- rep1 ste2_cluster_A_222_251: after100 slope=-0.001351 A/ns; mean=14.82 A (non-monotonic/near-zero slope preferred)
- rep1 ste2_cluster_B_288_304: after100 slope=0.001162 A/ns; mean=11.29 A (non-monotonic/near-zero slope preferred)
- rep2 ste2_cluster_A_222_251: after100 slope=0.0008752 A/ns; mean=15.76 A (non-monotonic/near-zero slope preferred)
- rep2 ste2_cluster_B_288_304: after100 slope=-0.002787 A/ns; mean=11.39 A (non-monotonic/near-zero slope preferred)
- rep3 ste2_cluster_A_222_251: after100 slope=0.0006395 A/ns; mean=15.29 A (non-monotonic/near-zero slope preferred)
- rep3 ste2_cluster_B_288_304: after100 slope=0.001297 A/ns; mean=11.36 A (non-monotonic/near-zero slope preferred)

### Batch 1 RMSF baseline

- RMSF baseline generated for future Ch-1/2/4 junction comparison; chctrl itself has no junction threshold.

### Batch 2 BSA

- rep1: after100 mean fraction=1.026, min fraction=0.902; above project operational >=0.80 heuristic
- rep2: after100 mean fraction=1.119, min fraction=0.928; above project operational >=0.80 heuristic
- rep3: after100 mean fraction=1.197, min fraction=1.075; above project operational >=0.80 heuristic

### Batch 2 contact persistence

- rep1: initial residue contacts=28; after100 mean retained=0.640, min=0.500; above project majority-retention heuristic >0.50
- rep2: initial residue contacts=28; after100 mean retained=0.546, min=0.250; above mean heuristic but low minimum remains caveat
- rep3: initial residue contacts=28; after100 mean retained=0.670, min=0.536; above project majority-retention heuristic >0.50

## Current interpretation

- BSA supports retention in all three replicates under the project operational 0.80 heuristic; the 0.80 value is not yet literature-authoritative.
- Contact persistence passes by mean retained fraction in all three replicates, but rep2 has a low minimum retained fraction (0.250), so the result is supportive but not perfectly uniform.
- Together with batch 1 COM distance and H-bond results, chctrl does not show strong evidence of complete Ste2-Gpa1 dissociation.
- The main caveat remains alpha5 iRMSD: rep1/rep2 were in the 3-5 A warning band while rep3 passed. Treat chctrl as usable with caveat, not as a clean all-metric pass.

## Decision needed before downstream work

Do not automatically restart Ch-1/2/4 from this file alone. Next step should be a user-confirmed decision on whether the chctrl evidence is sufficient to resume Ch-1/2/4, or whether to inspect figures/selection definitions first.
