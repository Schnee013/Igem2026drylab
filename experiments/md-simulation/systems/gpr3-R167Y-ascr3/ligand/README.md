# Gpr3_R167Y + ASCR3 ligand input

This directory is the system-local historical authority for the exact ligand
coordinate used by the completed `Gpr3_R167Y + ASCR3` MD input package. Its
allowed use is MD input provenance and recovery.

## Historical MD input

- `Gpr3_R167Y_ascr3_pose1.sdf` contains exactly one molecule: model 1 from the
  20-pose docking result.
- The retained pose score is `VINA RESULT: -5.715`. The historical
  candidate-ranking value `dg_ascr3=-5.715` has the same displayed value, while
  the system-local SDF remains the coordinate identity authority.
- `manifest.tsv` records ownership, source, checksum, consumer, recovery, and
  validation. The SDF body is explicitly promoted as a repo-owned canonical
  input because downstream ASCR3 coordinate completion and receptor-frame
  insertion need this exact selected orientation.

## Boundary

The promoted SDF, completed 46-atom GRO, and their manifests are the coordinate
and identity authority for this MD package. The full PDBQT pose set and
IFP-generated multi-pose SDF remain historical provenance.

## References / 所引

- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf`
- `experiments/docking-repro/results/ifp_analysis_mutants/poses/Gpr3_R167Y_ascr3_poses.pdbqt`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/manifest.tsv`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/source_files.sha256`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
