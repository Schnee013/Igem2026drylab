# chctrl selection audit plan

> Scope: `chimeric-ste2-gpa1-wt` Phase C5 selection audit plan only.
> Status: **executed diagnostic audit on 2026-04-29**. Use the report below, not this plan, as the audit evidence.
> Created: 2026-04-29 after user confirmation.
> Main upstream summary: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/chctrl_phase_C5_batch1_batch2_summary.md`
> Audit report: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
> Cutoff/source audit: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/cutoff_source_audit.md`

## 1. Why this audit is needed

The current chctrl readout is decision-relevant: it may decide whether Ch-1/Ch-2/Ch-4 should resume. Batch 1+2 metrics are supportive overall, but alpha5 iRMSD is a caveat in rep1/rep2. Before using the metrics for a go/no-go decision, this audit checks whether the atom selections and fitting route measure the intended biology rather than a naming, chain, residue-numbering, or alignment artifact.

**Go/no-go in this context** means: an engineering decision on whether chctrl evidence is sufficient to proceed to Ch-1/Ch-2/Ch-4 restart/continue decisions. It is not a claim that the biological system is fully proven.

## 2. Current selections to audit

These definitions are from `src/modeling/md-analysis/common.py` and related chctrl scripts. They must be verified against the processed topology/reference before being treated as final.

| Symbol / metric use | Current selection | Intended meaning | Audit question |
|---|---|---|---|
| `GPA1` | `segid PROA` | Gpa1 / Gα chain | Does `PROA` contain Gpa1, not Ste2 or another protein chain? |
| `STE2` | `segid PROB` | Ste2 receptor chain | Does `PROB` contain Ste2? |
| `ALPHA5` | `(segid PROA) and resid 448:472 and backbone` | Gpa1 alpha5 / extreme C-terminal helix backbone | Do residues 448–472 correspond to the intended Gpa1 alpha5/eCT region after any model/CHARMM-GUI renumbering? |
| `GPA1_LAST5` | `(segid PROA) and resid 468:472` | Gpa1 C-terminal last five residues | Are these the intended C-terminal residues used for receptor coupling inspection? |
| `STE2_INTERFACE` | `(segid PROB) and (resid 69:84 or resid 145:160 or resid 222:251 or resid 288:304)` | Putative intracellular Ste2 interface clusters near Gpa1 alpha5 | Are these residues actually intracellular GPCR-Gα interface regions in this model? |
| BSA groups | `segid PROA` vs `segid PROB` | Gpa1-Ste2 buried surface area | Are only the intended protein chains included? Are waters/lipids excluded as intended? |
| Contact groups | heavy atoms in `STE2_INTERFACE` vs `GPA1` | residue contact retention | Is the interface selection too broad, too narrow, or biased by initial-frame choice? |

## 3. Visual inspection frames

These frames are chosen to check the reported alpha5 iRMSD warning events rather than to sample uniformly.

| Replicate | Frames / times to inspect | Reason |
|---|---:|---|
| rep1 | 0 ns, 100 ns, 252.4 ns, 333.5 ns | baseline, after100 window start, first after100 >5 Å event, max alpha5 iRMSD event |
| rep2 | 0 ns, 100 ns, 250.6 ns, 484.6 ns | baseline, after100 window start, first >5 Å event, max alpha5 iRMSD event |
| rep3 | 0 ns, 32.6 ns, 100 ns, 400–500 ns representative frame | early max event, later recovery / stable after100 behavior |

Expected outputs after execution, if user confirms the audit run later:

- static snapshots or exported PDBs for selected frames;
- a short visual report explaining whether alpha5 movement appears real, fitting-related, or selection-related;
- optional NGLView / ChimeraX / PyMOL snippets for manual replay.

## 4. Technical checks

1. **Chain identity check**
   - Count residues and atom names under `segid PROA` and `segid PROB`.
   - Confirm residue-name patterns and sequence spans correspond to Gpa1 and Ste2.

2. **Residue numbering check**
   - Confirm `resid 448:472` and `468:472` exist in `PROA`.
   - Map these residues to the original Gpa1 sequence / model numbering.
   - If numbering changed during CHARMM-GUI or preprocessing, record the mapping explicitly.

3. **Interface-side check**
   - Confirm Ste2 residue ranges 69–84, 145–160, 222–251, 288–304 are on the intended intracellular side / coupling interface in the current model.
   - If any range is extracellular or membrane-facing rather than Gα-facing, revise the selection before interpreting contact/H-bond metrics.

4. **Fitting/reference check**
   - Confirm alpha5 iRMSD is computed after an appropriate backbone fit and not dominated by whole-complex rotation/translation.
   - Compare alpha5 local motion against global protein RMSD and COM distance.

5. **Initial-frame contact bias check**
   - For contact persistence, record how the initial contact set was defined.
   - Verify that low rep2 minimum retained fraction is not an artifact of a transient initial-frame contact set.

## 5. Threshold/source audit status

The following table deliberately separates **method/tool geometry definitions** from **project go/no-go cutoffs**. A value without DOI, official tool documentation, page/section, or another exact pointer must not be treated as a validated literature cutoff.

| Parameter / cutoff | Current use | Current authority status | Required action |
|---|---|---|---|
| H-bond geometry: distance 3.0 Å / angle 150° | Detect Gpa1-Ste2 H-bonds | **Audited tool-method supported** by MDAnalysis HydrogenBondAnalysis docs | Keep as MDAnalysis-style geometry |
| H-bond occupancy >10% | Mark notable H-bond pairs | **Project operational heuristic unless exact literature pointer is found** | Re-audit; do not call authoritative before exact source is recorded |
| alpha5 iRMSD <3 Å / >5 Å warning/dissociation style bands | chctrl alpha5 stability judgement | **Unverified project operational cutoff** until claimed Bauer 2022 source is rechecked | Re-check original Bauer 2022 paper; exact DOI/title/passage required |
| BSA after100 mean fraction ≥0.80 | Interface retention judgement | **Unverified project operational cutoff** until original source is rechecked | Re-check claimed source and method context; otherwise relabel as heuristic |
| Contact persistence >0.50 | Retained initial residue contacts | **Project majority-retention heuristic** unless exact source is found | Keep as operational heuristic or replace with literature-backed persistence definition |
| Heavy-atom residue contact cutoff 4.0 Å | Contact map simplification | **Audited as project-defined stricter contact geometry**, not GetContacts exact criteria | Describe as project heavy-atom residue-contact definition |
| COM distance slope “near zero preferred” | Rule-out gross dissociation trend | Qualitative stability screen, not a formal literature cutoff | Record as descriptive trend metric, not pass/fail threshold |
| RMSD/Rg convergence slope windows | Convergence screen | Needs project protocol pointer or literature/tool-method pointer | Re-audit before using for hard pass/fail decisions |

## 6. New project-wide TODO: operational cutoff source audit

Add a project-wide rule for current and future analyses:

- All pre-registered operational cutoffs must be re-audited before being used for go/no-go decisions.
- Every decision, technology choice, geometry definition, and numeric cutoff must record a clear authority chain.
- Literature citations without DOI, title, exact method/passage pointer, or other exact locator are **not accepted as evidence**.
- Until verified, such values must be labelled as `pending source audit` or `project operational heuristic`, not “literature-derived”.

This applies beyond chctrl C5 to docking, mutant MD, ODE, biosensor thresholds, and any future wet-lab recommendation gates.

## 7. Decision card for executing the audit

**Goal**: verify that current chctrl selections measure the intended Ste2-Gpa1 interface and that alpha5 warning events are not artifacts.

**Verified facts so far**:

- Current analysis scripts use `PROA` as Gpa1 and `PROB` as Ste2 selections.
- Current alpha5 selection is `PROA resid 448:472 backbone`.
- Current interface selection is four Ste2 residue ranges: 69–84, 145–160, 222–251, 288–304.
- Batch 1+2 summary reports chctrl as usable with alpha5 caveat, not clean all-metric pass.

**Missing information**:

- exact chain/residue mapping in the processed topology/reference;
- whether Ste2 selected ranges are all intracellular/interface-facing in this model;
- whether alpha5 warning reflects real displacement or selection/fitting artifact;
- verified source pointers for all operational cutoffs.

**Options**:

1. **Audit first, then decide Ch-1/Ch-2/Ch-4** — safest; adds a small analysis step before downstream restart.
2. **Accept current chctrl caveated pass now** — faster, but risks propagating a selection/cutoff artifact.
3. **Rebuild selections before auditing** — only if the current selection definitions are already suspected to be wrong.

**Recommendation**: choose option 1. Run selection audit first; keep Ch-1/Ch-2/Ch-4 paused until the audit report and cutoff-source status are reviewed.

**Pause gate**: do not run frame export, visualization, reanalysis, or Ch-1/Ch-2/Ch-4 restart until the user explicitly confirms the next execution step.

## 8. Execution result pointer

Executed on 2026-04-29 with:

```bash
conda run -n chimeric-md-2025 python experiments/md-simulation/analysis/chctrl/audit_selections.py
```

Primary output:

- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`

Short result:

- PROA/PROB identity and source-to-processed sequence mapping passed.
- Gpa1 alpha5/eCT residue selection exists and is consistent in all three processed replicates.
- Ste2 interface ranges are geometrically interface-proximal in `step5_input.pdb`, but exact residue-range provenance still needs source audit.
- Alpha5 warning is reproduced and remains visible under alternative fitting frames; it is not explained away as whole-complex translation/rotation alone.
- chctrl remains “usable with alpha5 caveat,” not a clean all-metric pass.

Cutoff-source audit result:

- Ste2 interface ranges are now traceable to project-derived 7AD3 alpha5/eCT contact clusters plus chctrl `step5_input.pdb` geometry.
- “Bauer 2022” did not pass exact-pointer audit; alpha5 3/5 Å and BSA 20% remain project operational heuristics.
- GPCRsignal supports interaction-frequency analysis but not `>0.50` as a universal pass cutoff.
- MDAnalysis supports H-bond geometry 3.0 Å / 150°, but not occupancy >10%.
