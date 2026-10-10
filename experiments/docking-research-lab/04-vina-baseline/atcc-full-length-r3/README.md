# ATCC full-length WT r3 PyMOL review export

Local source run: `/Users/roy/Documents/drylab/temp/docking_full_length_wt_20260813_e2_atcc_correct_ligand_seed44_r3`

E2 source run: `/ifs1/User/dengwei/igem/docking-frame-repair/docking_full_length_wt_20260813_e2_atcc_correct_ligand_seed44_r3`

This package contains the chemically correct deprotonated carboxylate (-1) r3 results. Run one notebook under `Pymol ipynb/`; each starts a new local PyMOL app and loads one full-length prepared receptor plus all independently numbered poses. Only the first pose is enabled initially. Return decisions only by `ATCCFLR3-*` stable ID. The older `ATCC results` package belongs to the superseded wrong-ligand r2 lineage and must not be reviewed.

For the fastest review, run one notebook under `Pymol ipynb/`. Each notebook
opens a separate local PyMOL process. In PyMOL, enable exactly one
`ATCCFLR3_*` pose object at a time; all other poses remain available but are
disabled initially. Record `include` or `exclude` by the stable
`ATCCFLR3-*` ID in `wt_pose_review_template.json` or report the IDs back to
Codex. `pose_index.tsv` binds every ID to affinity, the combined source pose
file SHA256, and pose-body SHA256. Do not use r2 IDs or historical MODEL
numbers.

Each job folder contains the prepared full-length receptor PDBQT, 20 separate
pose PDBQT files, the fixed search-box helper, and the pearl-style PML. The
`fixed_search_box.py` file is visualization-only: it draws the frozen Vina box
and does not alter receptor or ligand coordinates.
