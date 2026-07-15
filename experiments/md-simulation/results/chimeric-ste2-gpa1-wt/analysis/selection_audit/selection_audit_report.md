# chctrl selection audit report

> Status: executed diagnostic audit. This report does not restart Ch-1/Ch-2/Ch-4 and does not by itself validate all operational cutoffs.
>
> Source-audit update: operational cutoff and Ste2 interface provenance were audited separately in `../cutoff_source_audit.md`.

## Bottom line

- Chain/segment identity check: PASS — PROA maps to clean Chain A / intended Gpa1-WT; PROB maps to clean Chain B / intended Ste2.

- Alpha5 selection exists in all three processed replicates and maps to PROA residues 448–472; no missing-residue evidence was found in topology-level checks.

- Ste2 interface ranges are geometrically close to Gpa1/alpha5 in `step5_input.pdb`; a follow-up source audit traced them to project-derived 7AD3 alpha5/eCT contact clusters, not paper-quoted exact residue ranges.

- Alpha5 warning is reproduced to floating-point precision by an independent full-protein-backbone-fit calculation; it is unlikely to be a CSV/script transcription error.

- Under Ste2-backbone and Gpa1-core alternative fits, alpha5 displacement remains visible, so the rep1/rep2 warning is not explained away by whole-complex translation/rotation alone.

- Contact persistence remains partly sensitive to the frame-0 initial contact set; rep2 low minimum should stay as a caveat.


## Evidence files

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/chain_summary.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/source_to_processed_mapping.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_counts.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/ste2_interface_geometry_step5.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/alpha5_reproduction_check.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/alpha5_event_timing.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/alpha5_alt_fit_summary_after100.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshot_metrics.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/contact_bias_summary.csv`

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/exported_snapshots.csv`


## Chain identity

| rep | segid | intended | n_atoms | n_residues | min_resid | max_resid | first10 | last25 | unique_resnames |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rep1 | PROA | Gpa1-WT | 7612 | 472 | 1 | 472 | MGCTVSTQTI | QTMKFVLSAVTDLIIQQNLKKIGII | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |
| rep1 | PROB | Ste2 | 6753 | 431 | 1 | 431 | MSDAAPSLSN | VDMYTPDTAADEEARKFWTEDNNNL | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |
| rep2 | PROA | Gpa1-WT | 7612 | 472 | 1 | 472 | MGCTVSTQTI | QTMKFVLSAVTDLIIQQNLKKIGII | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |
| rep2 | PROB | Ste2 | 6753 | 431 | 1 | 431 | MSDAAPSLSN | VDMYTPDTAADEEARKFWTEDNNNL | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |
| rep3 | PROA | Gpa1-WT | 7612 | 472 | 1 | 472 | MGCTVSTQTI | QTMKFVLSAVTDLIIQQNLKKIGII | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |
| rep3 | PROB | Ste2 | 6753 | 431 | 1 | 431 | MSDAAPSLSN | VDMYTPDTAADEEARKFWTEDNNNL | ALA ARG ASN ASP CYS GLN GLU GLY HSD ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL |


## Source-to-processed mapping

| source_clean_chain | processed_segid | intended | source_n_residues | processed_n_residues | sequence_exact_match | source_first10 | processed_first10 | source_last25 | processed_last25 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | PROA | Gpa1-WT | 472 | 472 | True | MGCTVSTQTI | MGCTVSTQTI | QTMKFVLSAVTDLIIQQNLKKIGII | QTMKFVLSAVTDLIIQQNLKKIGII |
| B | PROB | Ste2 | 431 | 431 | True | MSDAAPSLSN | MSDAAPSLSN | VDMYTPDTAADEEARKFWTEDNNNL | VDMYTPDTAADEEARKFWTEDNNNL |


Source pointers: `docs/ops/charmm-gui-membrane-builder.md` records Ch-ctrl PROA=Gpa1-WT and PROB=Ste2; `docs/logs/2026-04-17.md` records clean Chain A=Gpa1-WT, Chain B=Ste2.


## Selection counts

| selection_name | n_atoms | n_residues |
| --- | --- | --- |
| ALPHA5 | [99] | [25] |
| BACKBONE | [3610] | [903] |
| BSA_GPA1 | [7612] | [472] |
| BSA_STE2 | [6753] | [431] |
| GPA1 | [7612] | [472] |
| GPA1_LAST5 | [87] | [5] |
| STE2 | [6753] | [431] |
| STE2_INTERFACE | [1322] | [79] |
| STE2_INTERFACE_HEAVY | [637] | [79] |


## Ste2 interface geometry in step5_input.pdb

| range | n_residues | ca_z_minus_membrane_mid_A | min_dist_to_gpa1_alpha5_A | min_dist_to_gpa1_last5_A | min_dist_to_all_gpa1_A |
| --- | --- | --- | --- | --- | --- |
| 69:84 | 16 | 14.209 | 3.212 | 3.212 | 3.212 |
| 145:160 | 16 | 14.798 | 3.947 | 3.610 | 2.732 |
| 222:251 | 30 | 20.377 | 3.641 | 3.233 | 2.708 |
| 288:304 | 17 | 18.965 | 2.917 | 2.683 | 2.683 |


Interpretation: all four Ste2 ranges have atoms within contact distance of all Gpa1, and ranges 69:84 / 222:251 / 288:304 are especially close to alpha5/last5. Range 145:160 is interface-proximal to Gpa1 but farther from alpha5, so it should be described as a broader interface cluster rather than an alpha5-only contact patch.


## Alpha5 alternative-fit summary after 100 ns

| rep | full_after100_mean | full_after100_max | ste2_after100_mean | ste2_after100_max | gpa1_core_after100_mean | gpa1_core_after100_max |
| --- | --- | --- | --- | --- | --- | --- |
| rep1 | 4.264 | 7.461 | 6.067 | 11.928 | 5.562 | 9.484 |
| rep2 | 3.793 | 6.400 | 3.959 | 8.989 | 5.209 | 10.327 |
| rep3 | 2.970 | 5.269 | 3.935 | 8.163 | 3.481 | 8.867 |


Interpretation: full-protein fit reproduces the prior metric; Ste2-frame values test receptor-relative alpha5 movement; Gpa1-core-frame values test alpha5 motion relative to the rest of Gpa1. Because rep1/rep2 remain elevated under alternative fits, the warning should be treated as a real local/relative-motion caveat unless visual inspection proves otherwise.


## Event timing

| rep | event | time_ns | alpha5_irmsd_A |
| --- | --- | --- | --- |
| rep1 | first_ge3 | 2.700 | 3.095 |
| rep1 | first_ge5 | 41.500 | 5.027 |
| rep1 | first_after100_ge5 | 252.400 | 5.241 |
| rep1 | max | 333.500 | 7.461 |
| rep2 | first_ge3 | 1.700 | 3.013 |
| rep2 | first_ge5 | 250.600 | 5.054 |
| rep2 | first_after100_ge5 | 250.600 | 5.054 |
| rep2 | max | 484.600 | 6.400 |
| rep3 | first_ge3 | 1.400 | 3.124 |
| rep3 | first_ge5 | 5.600 | 5.012 |
| rep3 | first_after100_ge5 | 100.000 | 5.070 |
| rep3 | max | 32.600 | 6.720 |


## Exported snapshot metrics

| rep | label | time_ns | frame | pdb | full_protein_backbone_fit_alpha5_rmsd_A | ste2_backbone_fit_alpha5_rmsd_A | gpa1_core_backbone_fit_alpha5_rmsd_A | nearest_contact_time_ns | retained_contact_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rep1 | baseline | 0.000 | 0 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep1_baseline_0.0ns.pdb | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| rep1 | after100_start | 100.000 | 1000 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep1_after100_start_100.0ns.pdb | 3.296 | 4.657 | 4.871 | 100.000 | 0.821 |
| rep1 | first_after100_ge5 | 252.400 | 2524 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep1_first_after100_ge5_252.4ns.pdb | 5.241 | 8.376 | 6.945 | 250.000 | 0.571 |
| rep1 | max_alpha5 | 333.500 | 3335 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep1_max_alpha5_333.5ns.pdb | 7.461 | 11.645 | 8.270 | 335.000 | 0.571 |
| rep2 | baseline | 0.000 | 0 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep2_baseline_0.0ns.pdb | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| rep2 | after100_start | 100.000 | 1000 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep2_after100_start_100.0ns.pdb | 2.333 | 2.605 | 4.702 | 100.000 | 0.643 |
| rep2 | first_ge5 | 250.600 | 2506 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep2_first_ge5_250.6ns.pdb | 5.054 | 5.213 | 6.735 | 250.000 | 0.500 |
| rep2 | max_alpha5 | 484.600 | 4846 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep2_max_alpha5_484.6ns.pdb | 6.400 | 7.790 | 7.525 | 485.000 | 0.393 |
| rep3 | baseline | 0.000 | 0 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep3_baseline_0.0ns.pdb | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| rep3 | early_max | 32.600 | 326 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep3_early_max_32.6ns.pdb | 6.720 | 11.239 | 12.813 | 35.000 | 0.786 |
| rep3 | after100_start | 100.000 | 1000 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep3_after100_start_100.0ns.pdb | 5.070 | 8.163 | 7.823 | 100.000 | 0.714 |
| rep3 | late_representative | 450.000 | 4500 | experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/snapshots/rep3_late_representative_450.0ns.pdb | 3.263 | 4.668 | 4.230 | 450.000 | 0.536 |


## Contact initial-set caveat

| rep | initial_contacts | after100_mean_retained_fraction | after100_min_retained_fraction | after100_min_time_ns | contacts_occupancy_ge_0_5 | contacts_occupancy_ge_0_2 | median_initial_contact_occupancy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rep1 | 28 | 0.640 | 0.500 | 200.000 | 21 | 25 | 0.678 |
| rep2 | 28 | 0.546 | 0.250 | 425.000 | 17 | 24 | 0.614 |
| rep3 | 28 | 0.670 | 0.536 | 235.000 | 21 | 25 | 0.777 |


Interpretation: rep2 has a pronounced retained-fraction dip after 100 ns. Because the metric is defined relative to frame-0 contacts, it is useful for interface-retention screening but should not be over-interpreted as a literature-grade persistence cutoff.


## Cutoff/source status

- This audit checks selections and metric implementation; the separate source audit is `../cutoff_source_audit.md`.

- Current decision bands (`alpha5 iRMSD <3/>=5 Å`, `BSA fraction >=0.80`, `contact persistence >0.50`, `H-bond occupancy >10%`) were audited there and remain project operational heuristics; only H-bond geometry 3.0 Å / 150° is supported as an MDAnalysis-style tool geometry.

- Therefore, the audit supports selection validity, but does not convert operational heuristics into authoritative literature thresholds.


## Decision implication

- Selection definitions are usable for chctrl caveated interpretation.

- chctrl remains `usable with alpha5 caveat`, not clean all-metric pass.

- Recommended pause gate: review this report before deciding whether to resume Ch-1/Ch-2/Ch-4.
