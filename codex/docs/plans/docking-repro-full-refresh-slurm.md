# Docking-repro Full Refresh Plan (Slurm)

> Created: 2026-05-19
> Scope: docking-repro refresh only. ODE pipeline is parked until literature review settles Kd/calibration strategy.
> Primary sources to re-check before execution: `docs/INDEX.md`, `docs/modeling/P0-molecular-docking.md`, `docs/logs/2026-04-23.md`, `docs/logs/2026-04-27.md`, and current result JSON/CSV files under `experiments/docking-repro/`.

## Summary

- This plan advances docking-repro from the current `reanalysis` state to a refreshed, versioned docking release.
- Include existing Gpr3 scheme F Ala/Sat results and the new batch01+batch02 AF3 predictions, then refresh ratio, IFP, and wet-lab candidate handoff.
- Historical note: this 2026-05-19 refresh plan used Slurm. For new server/remote-compute work, first read `docs/ops/nkuliulab-e2-cloud-server.md`; Slurm and Windows 7500F remain historical context only unless a missing old artifact or old run log must be recovered.
- Do not start ODE, do not export ODE parameter tables, and do not convert Vina scores to Kd in this plan.
- Preserve enough provenance in docking outputs for a later ODE session to consume them after the literature review defines the Kd/calibration policy.

## Inputs And Authority

- Project routing and status:
  - `docs/INDEX.md`
  - `docs/modeling/P0-molecular-docking.md`
  - `codex/docs/memory/current-state.md`
  - `codex/docs/memory/pitfalls.md`
- Historical private-plan lookup, if needed:
  - `codex/docs/memory/plan-index.md`
  - Use this only as a repo-local index to old assistant plans; do not treat private plan files as execution authorities.
- Gpr2/Gpr3 repair history:
  - `docs/logs/2026-04-23.md`
  - `docs/logs/2026-04-27.md`
- New AF3 downloads:
  - `/Users/roy/Downloads/Arc/folds_2026_04_24_08_43`
  - `/Users/roy/Downloads/Arc/folds_2026_05_19_02_03`
- Batch JSONs:
  - `experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json`
  - `experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json`

## Phase 1: Import AF3 Batch Outputs

1. Copy the two AF3 download batches into `experiments/docking-repro/mutagenesis/af3_downloads/`.
2. Verify the batch JSONs and download folders match:
   - batch01: 29 jobs
   - batch02: 25 jobs
   - total: 54 jobs
   - expected supplemental sites: Gpr3 D100, R164, R167, 18 non-WT/non-Ala substitutions each
3. Write a provenance manifest in the docking-repro mutagenesis area with:
   - source download path
   - batch JSON path
   - job count
   - file count
   - import timestamp
   - any missing or extra job names
4. Do not overwrite historical AF3-derived files without an archive or versioned output path.

## Phase 2: Structure Processing

1. Run the existing AF3 processing chain after import:
   - best model CIF selection with `process_af3_structures.py`
   - CIF to PDB with `cif_to_pdb.py`
   - TM extraction with `extract_mutant_tm.py`
   - ADFR PDBQT preparation with `run_adfr_mutants.py`
2. Generalize `run_adfr_mutants.py` before Slurm use:
   - add `--adfr-bin` or config/env support
   - remove the hard dependency on `D:/ADFRsuite/bin`
   - keep the Windows path usable only as an explicit override, not the default
3. Verify all 54 supplemental mutants have the expected CIF/PDB/TM/PDBQT artifacts.
4. Treat D100A as already covered by the existing Gpr3 F Ala result; the new batch is for supplemental saturation completion.

## Phase 3: Slurm Migration

1. Add a full docking-repro Slurm deployment path under `experiments/docking-repro/slurm/`.
2. Replace the current Gpr2-only deployment assumptions with a general sync of:
   - `src/modeling/docking-repro/`
   - `experiments/docking-repro/prepared/`
   - relevant `experiments/docking-repro/mutagenesis/` AF3 structures/prepared mutants
   - required result baselines
3. Add a Slurm preflight job that checks:
   - `~/bin/vina --version`
   - ADFR `prepare_receptor`
   - Python imports required by the docking scripts
   - expected project paths under `~/drylab-docking`
4. Submit long-running compute through `sbatch`; do not run docking, ADFR batch prep, or long Python jobs on the login node.
5. Run one supplemental mutant as a Slurm smoke test before submitting all 54.

## Phase 4: Supplemental Docking

1. Keep the existing Gpr3 scheme F geometry:
   - manual ECL2 box center `[0.42, 7.16, -17.11]`
   - box size `20.0`
2. Extend `run_mutagenesis_saturation.py` with a residue override, for example:
   - `--residues Gpr3:100,164,167`
3. Write supplemental results to an isolated run file:
   - `mutagenesis_results_gpr3_supplemental_f_<run_id>.json`
4. Required output count:
   - 54 supplemental mutant records
   - each record has both ascr18 and ascr3 docking values
5. Fail the phase if any record has missing ligand output, NaN values, or an unmatched mutation label.

## Phase 5: Merge And Ratio Refresh

1. Build a new merged mutagenesis JSON using this precedence:
   - Gpr2 3D offset rerun records
   - Gpr3 scheme F existing Ala/Sat records
   - Gpr3 scheme F supplemental records
   - current GprC records
2. Expected final merged count:
   - Gpr2: 46
   - Gpr3: 116
   - GprC: 104
   - total: 266
3. De-duplicate by `(receptor, mutation)` and prefer the newest repaired route for any collision.
4. Update `ratio_channel_analysis.py` so it accepts:
   - `--input-json`
   - `--out-dir`
   - `--run-label`
5. Generate a versioned analysis release first; refresh canonical report files only after validation:
   - `ratio_channel_report.md`
   - `ratio_spectrum.csv`
   - `ratio_pairings.csv`

## Phase 6: IFP And Mechanism Refresh

1. Fix `run_ifp_mutants.py` so Markdown summary generation uses `active_mutants`, not the default `TOP_MUTANTS` constant.
2. Select IFP mutants from the refreshed ratio outputs:
   - all mutants involved in the top 5 clean pairings
   - plus top 3 clean Channel A candidates
   - plus top 3 clean Channel B candidates
3. Use Gpr3 F-pose WT IFP and refreshed mutant poses for Gpr3 mechanism statements.
4. Do not use pre-F Gpr3 groove IFP as evidence for V138/F170/D100/R164/R167 mechanism claims.
5. Mechanism language must be limited to what the refreshed interaction-channel CSVs show.

## Phase 7: Wet-lab Handoff And Docs

1. Historical note: this plan originally targeted the old P0 docking wet-lab handoff after ratio and IFP validation passed. The old handoff body has since been retired; current candidate routing uses `docs/modeling/P0-docking-md-candidate-shortlist.md`.
2. Update:
   - `docs/logs/2026-05-19.md`
   - `docs/modeling/P0-molecular-docking.md`
   - `docs/INDEX.md`
   - `docs/modeling/P0-docking-md-candidate-shortlist.md`
3. Keep ODE status explicit:
   - ODE is parked.
   - Kd/calibration depends on the separate literature review.
   - Do not present docking-derived Kd as available.
4. If a cross-session pointer is needed, update `codex/docs/memory/current-state.md` or `codex/docs/memory/pitfalls.md` with a pointer to this plan, not a duplicate of the plan.

## Validation Checklist

- Batch import:
  - 29 + 25 jobs found
  - job names match both batch JSON files
  - expected model/confidence files are present
- Structure processing:
  - 54 supplemental CIF/PDB/TM/PDBQT outputs exist
  - mutation labels and residue numbers are consistent
- Slurm:
  - preflight passes
  - one-mutant smoke test passes before full run
- Docking:
  - supplemental JSON contains 54 records
  - each record has ascr18 and ascr3 values
  - no missing ligand, NaN, or malformed mutation label
- Merge:
  - final count is 266
  - no duplicate `(receptor, mutation)` keys
  - old Gpr3 groove and old Gpr2 polluted records are excluded
- Ratio:
  - report, spectrum, and pairings come from the same input JSON
  - versioned release exists before canonical files are refreshed
- IFP:
  - selected mutant set matches refreshed ratio outputs
  - Markdown sections match actual `active_mutants`
- Docs:
  - wet-lab handoff no longer uses stale Top candidates
  - ODE remains parked pending literature review

## ODE Gate

This plan deliberately stops before ODE.

- Do not start `experiments/ode-model/`.
- Do not create ODE parameter CSV/JSON.
- Do not estimate or calibrate Kd from Vina scores.
- Preserve raw docking fields and provenance so a later ODE plan can decide how to consume them after literature review.

## Assumptions

- Slurm target remains `guest@10.40.4.5`.
- Remote working directory remains `~/drylab-docking`.
- Gpr3 supplemental docking uses scheme F without another box search.
- Wet-lab recommendation refresh requires both ratio and IFP validation.
- ODE Kd/calibration policy will be decided in a separate literature-backed plan.
