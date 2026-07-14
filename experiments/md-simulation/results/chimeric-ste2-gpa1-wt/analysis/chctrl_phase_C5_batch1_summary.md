# chctrl Phase C5 batch 1 summary

> Generated 2026-04-28 by Codex. Source trajectory: chimeric-ste2-gpa1-wt production rep1-3. Current processed trajectory uses remote GROMACS 2025.2 `-pbc nojump` because local GROMACS 2024.5 cannot read 2025.2 TPR and `prod.xtc` is protein-only.
>
> Source-audit update 2026-04-29: numeric labels such as `<3 Å`, `>5 Å`, and `H-bond occupancy >10%` are project operational heuristics unless explicitly tool-supported. H-bond geometry 3.0 Å / 150° is MDAnalysis-style; occupancy >10% is not source-verified. See `cutoff_source_audit.md`.

## Outputs

- convergence: `convergence/rmsd_summary.csv`, `convergence/rg_summary.csv`, `convergence/*.png`
- alpha5 iRMSD: `alpha5_irmsd/a5_irmsd.csv`, `alpha5_irmsd/a5_irmsd_3rep.png`
- H-bond: `hbond/hbond_summary.csv`, `hbond/occupancy_top10.png`
- COM distance: `com_distance/com.csv`, `com_distance/*_3rep.png`
- RMSF baseline: `rmsf/rmsf.csv`, `rmsf/rmsf_baseline.png`
- dashboard: `summary_dashboard.png`

## Batch 1 judgement snapshot

### convergence

- rep1: final100/after100 RMSD slope = -0.00836 A/ns; mean RMSD = 10.45 A
- rep2: final100/after100 RMSD slope = 0.01655 A/ns; mean RMSD = 8.86 A
- rep3: final100/after100 RMSD slope = 0.001325 A/ns; mean RMSD = 9.49 A

### alpha5_irmsd

- rep1: after100 mean=4.26 A, max=7.46 A => WARN by project operational 3-5 A band
- rep2: after100 mean=3.79 A, max=6.40 A => WARN by project operational 3-5 A band
- rep3: after100 mean=2.97 A, max=5.27 A => PASS-like by project operational <3 A band

### hbond

- rep1: top pair occupancy=0.492; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5
- rep2: top pair occupancy=0.453; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5
- rep3: top pair occupancy=0.459; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride=5

### com_distance

- rep1 ste2_cluster_A_222_251: after100 slope=-0.001351 A/ns; mean=14.82 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)
- rep1 ste2_cluster_B_288_304: after100 slope=0.001162 A/ns; mean=11.29 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)
- rep2 ste2_cluster_A_222_251: after100 slope=0.0008752 A/ns; mean=15.76 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)
- rep2 ste2_cluster_B_288_304: after100 slope=-0.002787 A/ns; mean=11.39 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)
- rep3 ste2_cluster_A_222_251: after100 slope=0.0006395 A/ns; mean=15.29 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)
- rep3 ste2_cluster_B_288_304: after100 slope=0.001297 A/ns; mean=11.36 A (descriptive; sustained monotonic increase warrants inspection; no categorical cutoff)

### rmsf

- RMSF baseline generated for future Ch-1/2/4 junction comparison; chctrl itself has no junction threshold.

## Current interpretation

- The signed COM slopes are descriptive context only. Sustained monotonic increase would warrant inspection; no categorical COM cutoff is configured.
- H-bond analysis finds top interface H-bond occupancy above 10% in all three replicates. This script uses manual donor-H/acceptor geometry because the PDB topology lacks charge data required by MDAnalysis HBA auto-guessing.
- Alpha5 iRMSD is borderline under project operational bands: rep3 is just under the <3 A band, while rep1/rep2 are in the 3-5 A warning band. This is not a clean positive-control failure by the project >5 A mean heuristic, but it should be interpreted together with batch 2 BSA/contact persistence before restarting Ch-1/2/4.
- The first attempted `-pbc mol` processing produced artificial large separations and has been quarantined as `analysis_mol_invalid/`; do not use it for decisions.

## Next step

Run batch 2: BSA, contact persistence, and optional MM-PBSA; then integrate all 7 indicators into the Ch-1/2/4 restart decision.
