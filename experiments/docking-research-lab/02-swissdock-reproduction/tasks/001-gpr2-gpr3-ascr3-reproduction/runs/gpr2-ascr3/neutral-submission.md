# Gpr2 WT–neutral ascr#3 SwissDock AC result

- Result received: 2026-08-11
- Engine: Attracting Cavities 2.0
- Receptor: `inputs/receptors/Gpr2_TGJ68930.1_AF2_rank1_unrelaxed.pdb`
- Server-returned ligand: neutral carboxylic acid (`C(=O)O`)
- Search-box center (Å): `-11.8, 13.0, 17.0`
- Search-box size (Å): `94.3, 81.2, 120.8`
- Parameters: RIC 1; medium sampling (90°); buried cavity prioritization (70)
- Raw archive: `Gpr2_AF2_ascr3_neutral_AC_WT.zip`
- Extracted result: `swissdock-neutral-rerun-20260811/`
- SHA-256: `06a615be7afae72a0c5edfe7b7ad817ef853dcacd80c1c8c7bf1803c8322b891`
- Role: primary Gpr2 run for comparison with the neutral Gpr3 run

The earlier nominal-carboxylate submission is preserved separately, but SwissDock
actually parameterized it as a neutral ligand (H14 present; total charge 0). It is
therefore a preparation/conformer/sampling sensitivity result, not a protonation-state
comparison, and is not used as the primary representative pose.
