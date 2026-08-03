# Gpr2_R59C + ASCR18 ligand input

This directory is the system-local historical authority for the exact ligand
coordinate used by the completed `Gpr2_R59C + ASCR18` MD input package. It is
not a current docking-ranking or candidate authority.

## Historical MD input

- `Gpr2_R59C_ascr18_pose1.sdf` contains exactly one molecule: model 1 from the
  20-pose docking result.
- The retained pose score is `VINA RESULT: -5.698`. The candidate-ranking value
  `dg_ascr18=-6.227` comes from the ratio report and is not assigned to this
  coordinate; the score and ranking value are not the same source identity.
- `manifest.tsv` records ownership, source, checksum, consumer, recovery, and
  validation. The SDF body is explicitly promoted as a repo-owned canonical
  input because downstream MD assembly needs this exact selected coordinate.

## Boundary

The full PDBQT pose set and IFP-generated multi-pose SDF are withdrawn
docking-analysis outputs. The promoted SDF remains authoritative only for
auditing the actual historical MD starting coordinate; it cannot validate the
frame-repaired ranking or define a future candidate. Package consumers must not
replace this historical input through `results/**/tmp/`.

## References / 所引

- `experiments/docking-repro/results/ifp_analysis_mutants/poses/Gpr2_R59C_ascr18_poses.pdbqt`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/manifest.tsv`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/source_files.sha256`
