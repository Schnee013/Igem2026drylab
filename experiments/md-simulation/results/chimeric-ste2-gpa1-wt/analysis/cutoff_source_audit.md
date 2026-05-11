# chctrl operational cutoff + Ste2 interface source audit

> Scope: `chimeric-ste2-gpa1-wt` Phase C5 only.
> Status: executed source audit on 2026-04-29; DOI/URL pointer supplement added on 2026-05-06.
> Rule applied: no DOI / exact title / method section / official tool documentation / exact data pointer = not accepted as authoritative literature evidence.
> Related selection audit: `selection_audit/selection_audit_report.md`

## 1. Executive conclusion

The chctrl selections are now source-audited enough for **caveated interpretation**, but most numeric go/no-go cutoffs are **not** literature-authoritative.

- **Ste2 interface selection** is now traceable as a **project-derived 7AD3 geometry selection**:
  - primary structure source: Velazhahan et al. 2021, *Nature*, “Structure of the class D GPCR Ste2 dimer coupled to two G proteins”, DOI `10.1038/s41586-020-2994-1`, PDB `7AD3`;
  - exact project derivation: continuous Ste2 residue ranges covering the 7AD3 Ste2 residues within 8 Å of Gpa1 alpha5/eCT residues 450–472, then confirmed in the project `step5_input.pdb`.
  - therefore these ranges are **not quoted from the paper as exact ranges**; they are a reproducible structural derivation from PDB 7AD3 plus project geometry.
- **Alpha5 iRMSD <3 Å / >5 Å**: the local “Bauer 2022” citation could not be verified from current local files or web search. Treat as **project operational heuristic / pending source**, not literature cutoff.
- **BSA fraction ≥0.80 / drop <20%**: FreeSASA as a SASA/BSA method is supported, but the 20% pass/fail threshold is **project operational heuristic / pending source**.
- **Contact persistence >0.50**: GPCRsignal supports interaction-frequency analysis and explicitly defines frequency 0.5 as present in 50% of frames, but it does **not** make >0.50 a universal stability pass threshold. Treat as **project majority-retention heuristic**.
- **H-bond geometry 3.0 Å / 150°**: supported by MDAnalysis HydrogenBondAnalysis documentation. **H-bond occupancy >10%** remains a **project heuristic / pending source**.

Decision implication: current chctrl can still be summarized as **usable with alpha5 caveat**, but the phrase “passes literature thresholds” must not be used for the unresolved operational cutoffs.

## 2. Source-audited cutoff table

| Item | Current value in chctrl analysis | Source-audit status | Exact accepted pointer | Updated allowed wording |
|---|---:|---|---|---|
| Alpha5/eCT selection | Gpa1 `PROA resid 448:472 backbone` | **Supported as structure/sequence region**, not as a numeric cutoff | Hara et al. 2012 DOI [`10.1271/bbb.110820`](https://doi.org/10.1271/bbb.110820) for Gpa1 C-terminal/eCT coupling importance; Velazhahan et al. 2021 DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1) / PDB [`7AD3`](https://www.rcsb.org/structure/7AD3) for Ste2-Gpa1 structural interface | “Biologically motivated Gpa1 C-terminal alpha5/eCT selection” |
| Alpha5 iRMSD stable/warn/fail bands | mean <3 Å stable, >5 Å severe/dissociation | **Not verified** | Local files cite “Bauer 2022”, but no exact title/DOI/method passage was found in local grep or web queries | “Project operational alpha5 displacement bands; pending source audit” |
| BSA method | BSA = SASA(Gpa1)+SASA(Ste2)-SASA(complex) | **Method supported** | Mitternacht 2016 FreeSASA DOI [`10.12688/f1000research.7931.1`](https://doi.org/10.12688/f1000research.7931.1); FreeSASA implements Lee-Richards and Shrake-Rupley approximations | “FreeSASA-derived BSA time series” |
| BSA cutoff | after100 mean fraction ≥0.80 / drop <20% | **Not verified** | No accepted exact pointer found | “Project operational interface-retention heuristic” |
| Contact definition | heavy-atom residue pair distance ≤4.0 Å | **Tool-style geometry supported only generically; exact 4.0 Å is project-defined** | [MDAnalysis contacts docs](https://docs.mdanalysis.org/stable/documentation_pages/analysis/contacts.html) define fraction of native contacts and mention all-atom cutoff 4.5 Å; our implementation uses 4.0 Å as a stricter project choice | “Project heavy-atom residue-contact definition, 4.0 Å” |
| Contact persistence cutoff | retained initial contacts >0.50 | **Not literature-authoritative** | GPCRsignal DOI [`10.1093/nar/gkab434`](https://doi.org/10.1093/nar/gkab434) defines interaction frequency 0–1 and Freq=0.5 as present in 50% frames; does not define >0.50 as pass/fail | “Project majority-retention heuristic” |
| H-bond geometry | donor-acceptor 3.0 Å, D-H-A 150° | **Tool-doc supported** | [MDAnalysis HydrogenBondAnalysis docs](https://docs.mdanalysis.org/stable/documentation_pages/analysis/hydrogenbonds.html): `d_a_cutoff` default 3.0 Å; `d_h_a_angle_cutoff` default 150° | “MDAnalysis-style H-bond geometry” |
| H-bond occupancy cutoff | >10% notable/effective | **Not verified** | No accepted exact pointer found | “Project reporting threshold; pending source audit” |
| COM distance trend | not monotonically increasing | **Descriptive metric** | No numeric pass/fail source needed if not used as hard cutoff. If citing GPCR/G-protein interface biology, use explicit structural sources such as Velazhahan 2021 DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1), not a numeric COM cutoff paper. | “Qualitative rule-out of gross separation” |
| RMSF baseline | comparable to WT/chctrl baseline | **Comparative project metric** | Project design; no universal cutoff | “Baseline comparison only” |
| MM-PBSA | optional qualitative ranking | **Not used in chctrl C5** | Existing MD tech-stack docs cite MM-PBSA limitations; Slurm dependency unavailable | “Deferred / not go-no-go required here” |

## 3. Ste2 interface selection source audit

### 3.1 Primary structural source

Accepted primary source:

- Velazhahan et al. 2021, *Nature*, **“Structure of the class D GPCR Ste2 dimer coupled to two G proteins”**, DOI `10.1038/s41586-020-2994-1`, PDB `7AD3`.

This paper establishes the Ste2 active-state G-protein-bound structure and states that Ste2 is coupled to heterotrimeric Gpa1-Ste4-Ste18. It is therefore the correct primary structural source for Ste2-Gpa1 interface anchoring.

### 3.2 Exact project derivation

Audit files:

- `selection_audit/ste2_interface_7ad3_alpha5_contacts.csv`
- `selection_audit/ste2_interface_7ad3_cluster_coverage.csv`
- `selection_audit/ste2_interface_geometry_step5.csv`

Procedure:

1. Use PDB `7AD3`.
2. Use Ste2 protomer chain A as receptor.
3. Use Gpa1 chain E residues 450–472 as alpha5/eCT structural reference.
4. Select Ste2 residues with any heavy atom within 8 Å of those Gpa1 alpha5/eCT heavy atoms.
5. Convert the resulting non-contiguous contact residues into four continuous project ranges for robust trajectory selections:
   - `69:84`
   - `145:160`
   - `222:251`
   - `288:304`
6. Confirm the same ranges are geometrically close to Gpa1/alpha5 in the project `step5_input.pdb`.

Coverage from `selection_audit/ste2_interface_7ad3_cluster_coverage.csv`:

| Project range | 7AD3 alpha5/eCT-contact residues within 8 Å | Interpretation |
|---|---|---|
| `69:84` | 73 74 75 77 78 79 80 81 82 83 84 | Covers 7AD3 contact cluster |
| `145:160` | 145 147 148 149 150 151 152 153 154 155 156 157 158 159 | Covers 7AD3 contact cluster |
| `222:251` | 222 225 226 228 229 230 231 232 233 234 235 236 237 238 242 243 244 246 247 251 | Covers 7AD3 contact cluster |
| `288:304` | 288 289 290 291 292 293 294 295 296 297 298 300 | Covers 7AD3 contact cluster |

Updated status:

- The interface selection is **not** an exact residue list quoted from Velazhahan et al.
- It is an **auditable project structural selection derived from PDB 7AD3 contact geometry**, then checked against the simulated chctrl starting structure.
- This is acceptable for chctrl interface monitoring, provided the report states the derivation honestly.

## 4. “Bauer 2022” audit result

Local grep hits:

- `experiments/md-simulation/README.md`
- `docs/modeling/P0-md-simulation.md`
- `experiments/md-simulation/analysis/pymol_chimeric_c4/README.md`

Problem:

- These files cite only “Bauer 2022” with no title, DOI, paper, figure, method section, or quote.
- Local project files contain no matching paper summary.
- Web queries for combinations of `Bauer`, `alpha5`, `iRMSD`, `GPCR`, `G protein`, `BSA`, and `molecular dynamics` did not identify a verifiable source that gives the exact <3 Å / >5 Å alpha5 iRMSD bands or BSA drop <20% rule.

Action:

- Replace “Bauer 2022” in project-facing tables with **“pending source audit; project operational heuristic”** unless a user supplies the exact paper.
- Do not use “Bauer 2022” as evidence in reports until DOI/title/method passage is provided and checked.

## 5. Updated go/no-go wording

Allowed:

- “chctrl shows no strong complete-dissociation signal across BSA/contact/COM, but has alpha5 displacement caveat.”
- “selection definitions are source-audited and usable for caveated interpretation.”
- “numeric cutoffs are operational heuristics unless listed above as tool-supported geometry.”

Not allowed:

- “chctrl passed Bauer 2022 thresholds.”
- “BSA ≥0.80 is literature-authoritative.”
- “contact persistence >0.50 is a GPCRsignal pass cutoff.”
- “H-bond occupancy >10% is a universal MD threshold.”

## 6. Sources accepted in this audit

- Velazhahan et al. 2021, *Nature*, “Structure of the class D GPCR Ste2 dimer coupled to two G proteins”, DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1), PDB [`7AD3`](https://www.rcsb.org/structure/7AD3).
- Hara et al. 2012, *Bioscience, Biotechnology, and Biochemistry*, “Chimeric Yeast G-Protein alpha Subunit Harboring a 37-Residue C-Terminal Gustducin-Specific Sequence Is Functional in Saccharomyces cerevisiae”, DOI [`10.1271/bbb.110820`](https://doi.org/10.1271/bbb.110820).
- Mitternacht 2016, *F1000Research*, “FreeSASA: An open source C library for solvent accessible surface area calculations”, DOI [`10.12688/f1000research.7931.1`](https://doi.org/10.12688/f1000research.7931.1).
- [MDAnalysis HydrogenBondAnalysis documentation](https://docs.mdanalysis.org/stable/documentation_pages/analysis/hydrogenbonds.html), official docs page for `d_a_cutoff=3.0` and `d_h_a_angle_cutoff=150`.
- [MDAnalysis contacts documentation](https://docs.mdanalysis.org/stable/documentation_pages/analysis/contacts.html), official docs page for native-contact fraction and all-atom radius examples.
- Miszta et al. 2021, *Nucleic Acids Research* 49(W1):W247–W256, “GPCRsignal: webserver for analysis of the interface between G-protein–coupled receptors and their effector proteins by dynamics and mutations”, DOI [`10.1093/nar/gkab434`](https://doi.org/10.1093/nar/gkab434).
- Sandhu et al. 2022, *Nature Communications*, “Dynamic spatiotemporal determinants modulate GPCR:G protein coupling selectivity and promiscuity”, DOI [`10.1038/s41467-022-34055-5`](https://doi.org/10.1038/s41467-022-34055-5). Used only as background support that GPCR:Gα interface contact duration/frequency is biologically meaningful; not used as a direct pass/fail threshold source.

## 7. Pointer supplement status, 2026-05-06

Added exact links for the accepted sources above. Remaining unresolved project citations are intentionally **not** “filled in by guess”:

- “Bauer 2022” for alpha5 iRMSD bands and BSA 20% remains rejected until an exact title/DOI/method passage is provided.
- H-bond occupancy `>10%` remains a project reporting threshold.
- Contact persistence `>0.50` remains a majority-retention heuristic.
- COM distance trend remains descriptive. Casiraghi et al. 2025 DOI `10.1126/sciadv.adq3971` is now source-audited as GPCR coupling-specificity background, but it is **not** a numeric COM-distance pass/fail source.
