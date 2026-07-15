# CHARMM-GUI Reduced Chctrl Build Request

> Date: 2026-07-03
>
> Scope: R1 `tight-full-rebuild` exploratory prototype for `chimeric-ste2-gpa1-wt` / `chctrl` only.
>
> Status: human/manual CHARMM-GUI Membrane Builder checklist. Candidate-transfer rule status and E2 approval require separate gates.

## Purpose

Generate one reduced full-system `chctrl` GROMACS package with CHARMM-GUI Membrane Builder while preserving the full receptor-Galpha protein complex, POPC membrane, explicit water, ions, and membrane-compatible full-system evidence.

The only intended reduction is avoidable XY membrane/box padding, and optionally avoidable Z solvent padding if recorded as a separate exploratory attempt. No protein atom, receptor scaffold, Galpha region, POPC class, explicit-solvent model, or ions may be removed manually.

## Authority And Guardrails

References / 所引:

- `docs/ops/charmm-gui-membrane-builder.md`: existing drylab CHARMM-GUI operation guide and historical chctrl settings.
- `docs/ops/md-gromacs-operational-pitfalls.md`: GROMACS/index/topology/output pitfalls.
- `docs/ops/nkuliulab-e2-cloud-server.md`: E2 transfer, resource, tmux, and cleanup boundary.
- `environments/e2-md-gromacs.md`: E2 GROMACS binary-output analysis rule.
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`: current exploratory R1 padding rule.
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/build_notes.md`: current prototype blocker and evidence boundary.

Referenced by / 被引:

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/source_pointers.md`
- Expected next records: future `build_notes.md`, `source_files.sha256`, atom-count delta, and Package B E2 approval after a reduced build exists.

## Input Choice

Use the original chimeric PPM-oriented protein-only submit file:

```text
experiments/md-simulation/structures/chimeric/Chctrl_Ste2_Gpa1_WT_submit.pdb
```

This is the correct web-upload class for Membrane Builder because the existing ops guide records the chimeric upload file as `*_submit.pdb`: pure `ATOM`, no `DUM` `HETATM`, filename without hyphens.

Upload source excludes the current historical system file:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.pdb
```

That file is useful as comparison/source evidence but is already a CHARMM-GUI assembled full system with POPC, TIP3, K+, and Cl-. Uploading it as a new Membrane Builder protein input would confound the rebuild.

If CHARMM-GUI rejects the original filename, copy it locally to a short hyphen-free name before upload, for example:

```text
R1chctrlsubmit.pdb
```

The copied upload file must remain byte-identical except for filename unless a separate documented cleaning step is made.

## Web Session Setup

1. Open CHARMM-GUI Membrane Builder:

   ```text
   https://www.charmm-gui.org/?doc=input/membrane
   ```

2. Turn off network proxy before submitting if possible; the existing drylab guide records lower reliability with proxy enabled.
3. Create or use a CHARMM-GUI account normally. Keep account credentials, email tokens, and passwords outside this repo.
4. Use a job note/name such as:

   ```text
   R1_chctrl_tight_full_rebuild_exploratory_20260703
   ```

## Step 1: PDB Reader

1. Choose `Membrane Builder -> Bilayer Builder`.
2. Upload `Chctrl_Ste2_Gpa1_WT_submit.pdb` or its documented hyphen-free copy.
3. `Membrane Only System`: unchecked.
4. `Check pKa`: unchecked.
5. Chain selection: keep both chains selected.
6. Terminal patching for both protein chains: keep default `NTER/CTER`.
7. Disulfide bonds: if CHARMM-GUI auto-detects a GPCR disulfide, confirm it; otherwise keep the site default.
8. Keep remaining options at default and continue with `Generate PDB and Orient Molecule`.

Record:

- upload filename;
- whether CHARMM-GUI altered chain IDs or residue numbering;
- any warnings, missing residues, disulfide prompts, ligand/cofactor prompts, or protonation prompts.

## Step 2: Orientation

1. Select `Use PDB Orientation`.
2. Keep other settings at default.
3. Confirm visually that the existing PPM-oriented membrane normal/orientation is preserved.

Important chctrl chain mapping from the drylab guide:

- Chain A / `PROA`: `Gpa1-WT`
- Chain B / `PROB`: `Ste2`
- chctrl PPM N-terminal option: `IN`

Record:

- whether `Use PDB Orientation` was selected;
- any orientation warning or visible unexpected rotation;
- screenshot or saved page text if the site reports transformed dimensions.

## Step 3: System Size

Historical chctrl settings were `Length of X and Y = 120 Å` and `Water thickness = 22.5 Å`, producing the current full chctrl system. R1 is exploratory because no source-backed numeric minimum padding rule is accepted.

Live manual-build observation from 2026-07-03:

- `110 Å` produced CHARMM-GUI warning: `The system is smaller than the protein extent. If there are errors on the next page, the XY system size may need to be increased.`
- `115 Å` produced the same warning.
- `120 Å` produced no protein-extent warning, matching the historical drylab chctrl guide.
- Z-only exploratory attempt `120 Å XY + 20.0 Å water` was started as CHARMM-GUI Job ID `8305210188`.
- Job `8305210188` Step 4 penetration checks reported no protein surface penetration and no lipid ring penetration. The job reached the `Building Ion and Waterbox` prompt.
- Job `8305210188` was later downloaded as `charmm_gui_8305210188_xy120_w20_download.tgz`, moved into the R1 prototype `source_archives/` directory, and extracted only into the R1 prototype `gromacs/` directory.
- The downloaded archive SHA256 is `486963899f9522767492e87aead931ddd8398755d08d950bf1d1d9913918745e`.

Interpretation for this R1 pass: `110 Å` and `115 Å` are abandoned XY-reduction attempts. The current minimum no-warning XY value is `120 Å`; carry-forward R1 prototypes use no-warning jobs.

Recommended exploratory strategy:

1. Keep `Heterogeneous Lipid -> Rectangular` box.
2. Keep `Lipid: PC -> POPC`; set upper and lower leaflet ratios to `1` and `1`.
3. Set `Length of X and Y = 120 Å` for the carried-forward no-warning build.
4. Keep `Water thickness = 22.5 Å` for the first carried-forward build to preserve the historical hydration setting and avoid mixing XY and Z changes.
5. Click `Show the system info`.
6. If `120 Å` unexpectedly produces a protein-extent warning, protein-image warning, or later Step 4 hard error in a fresh job, stop and record the discrepancy; carry-forward status requires a no-warning job.
7. If an actual atom-count reduction is still required after the no-warning XY floor is established, make any Z-water reduction a separate exploratory job with `Length of X and Y = 120 Å`; keep it separate from the abandoned `110 Å` or `115 Å` XY attempts.
8. Values below the smallest no-warning XY value require a separate written justification and a new attempt record.
9. The first carried-forward attempt should preserve water thickness. If Z reduction is later explored, run it as a second job, for example `120 Å XY + 20.0 Å water`, and label it separately from the `120 Å / 22.5 Å` no-warning reference rebuild.

Record for every attempted job:

- requested XY length;
- requested water thickness;
- CHARMM-GUI reported A/B/C box dimensions;
- POPC count per leaflet and total POPC count;
- water count if reported;
- ion count if reported;
- every warning/hard error;
- whether the attempt was abandoned or carried forward.

Carry forward only a job with no protein-extent warning and no Step 4 protein-size hard error.

## Step 4: Build Components

1. Building method: `Replacement method`.
2. `Check lipid ring penetration`: checked.
3. Include ions: checked.
4. Ion type: `KCl`.
5. Concentration: `0.15`.
6. Neutralizing: checked.
7. Ion placing method: `Distance`.
8. Continue and wait for packing.

Required pass condition:

- no unresolved penetration warning;
- no protein-size larger-than-bilayer hard error;
- no manual lipid, water, or ion deletion.

If penetration or size errors occur, retry with a larger XY value and record the failed attempt.

## Step 5: Assembly

1. Wait for the system assembly page to finish.
2. Record the CHARMM-GUI Job ID.
3. Record the total atom count and molecule counts shown by CHARMM-GUI.
4. Check that the job still contains both protein chains, POPC, water, K+, and Cl-.
5. Continue only if the assembled system contains the required protein chains, POPC, water, K+, and Cl-.

Atom-count reduction is an input to later `grompp`, smoke, benchmark, and physical sanity gates.

## Step 6: Generate Inputs

1. Force field: `CHARMM36m`.
2. Leave WYF, HMR, and multi-site calcium options unchecked.
3. Input generation: select `GROMACS` only.
4. `More CHARMM minimization`: unchecked.
5. Equilibration: select `NPT`; other ensembles require a CHARMM-GUI-forced change and a recorded reason.
6. Temperature: `303.15 K`.
7. Generate grid info for PME FFT automatically: checked.
8. Generate and download `download.tgz`.

Record:

- generated MD engine package: GROMACS;
- force-field family;
- temperature;
- whether any option differed from the drylab guide;
- downloaded archive filename and local path.

## Local Placement After Download

Unpack the downloaded CHARMM-GUI archive in a temporary location first. Preserve the historical system directory:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/
```

Copy only the generated reduced GROMACS package into:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/
```

The reduced package should include, as available from CHARMM-GUI:

- `topol.top`
- `index.ndx`
- `toppar/`
- `step5_input.*`
- `step6*.mdp`
- `step6*.gro`
- `step6*.tpr` if generated by CHARMM-GUI
- `step7_production.mdp` or the production MDP equivalent
- CHARMM-GUI readme/job files, if present

Keep the original `download.tgz` and a short manual note of the CHARMM-GUI job settings until checksums are recorded.

Current placement for job `8305210188`:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_archives/charmm_gui_8305210188_xy120_w20_download.tgz
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/
```

Static follow-up record:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv
```

## Handoff Back To Codex

After the download is placed under the R1 prototype `gromacs/` directory, the next Codex pass should:

1. checksum the downloaded archive and generated files;
2. compute atom-count delta against current chctrl `263906` atoms;
3. inspect `topol.top` `[ molecules ]` counts;
4. inspect `index.ndx`, especially `SOLU`, `MEMB`, `SOLV`, `SOLU_MEMB`, and `SYSTEM`;
5. compare MDP settings against the current production MDP;
6. update `build_notes.md`, `route.json`, `source_files.sha256`, and source pointers;
7. prepare Package B E2 approval only if the reduced system contains the required files and components.

Any E2 `grompp`, smoke `mdrun`, output preprocessing, or binary-output evidence analysis must use:

```text
/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
```

E2 command approval requires a separate package.

## Stop Conditions

Stop and report the issue before continuing if any of the following occurs:

- CHARMM-GUI rejects the input structure or changes chain/residue identity unexpectedly;
- either protein chain disappears or is truncated;
- `Use PDB Orientation` cannot be preserved;
- the smallest attempted reduced XY value gives protein-extent warnings or Step 4 hard errors;
- packing reports unresolved penetration;
- generated GROMACS package lacks `topol.top`, `index.ndx`, `toppar/`, or coordinate/MDP files;
- CHARMM-GUI forces force-field, water/ion, ensemble, or temperature changes outside this checklist;
- any candidate system or Ch-1/Ch-2/Ch-4 file is accidentally selected.
