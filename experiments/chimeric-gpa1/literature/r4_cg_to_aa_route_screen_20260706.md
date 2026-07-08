# R4 CG-to-AA Route Screen

> Date: 2026-07-06
>
> Status: historical/supporting R4-GAP-03 screen result.
>
> Scope: source-level screen for a Martini 3-compatible coarse-grained to atomistic route that could later support an R4 `chctrl` material addendum.
>
> Role: source-level route screen for future approved validation design.

## Working Conclusion

CG2AT was the best source-level route candidate found in this R4-GAP-03 screen
if a future dated decision record through `docs/INDEX.md` reopens the R4
CG-to-AA row.

The reason is practical: its official repository documents fragment-based conversion from coarse-grained systems such as Martini to atomistic systems, requires Python 3 and GROMACS greater than v5, and its fragment database includes multiple Martini 3 entries. That is more directly useful for this R4-GAP-03 evidence row than Backward or sinceCG.

The R4 buildability gate remains open. This screen records a conditional
validation question: whether CG2AT can be version-pinned, installed or otherwise
source-pinned later, and validated on a low-risk example before any exact
`chctrl` payload is touched.

## Source-Faithful Screen

| Route | Source checked | Source-faithful details captured | Immediate read |
|---|---|---|---|
| CG2AT / CG2AT2 | Official GitHub repo `owenvickery/cg2at`, release API, README, `database/fragments`, `database/forcefields` | Latest GitHub release checked in this session: `v0.9`, published `2021-07-06`, release page `https://github.com/owenvickery/cg2at/releases/tag/v0.9`. README describes CG2AT2 as fragment-based conversion of coarse-grained systems such as Martini to atomistic outputs for further atomistic simulation; install route is `conda install -c stansfeld_rg cg2at`; requirements are Python 3, GROMACS > v5, numpy, scipy; required input flag is `-c`; optional flags include `-a`, `-ff`, `-fg`, `-w`, `-group`, `-gmx`, `-compare`. `database/fragments` includes `martini_3-0_charmm36`, `martini_3-0_charmm36-VS`, `martini_3-0_charmm36_Jul2021`, `martini_3-0_oplsaa`, `martini_3-0_slipids`, and `martini_3_beta_charmm36`. `database/forcefields` includes CHARMM36 variants through Jul2022, OPLS-AA, Amber, and SLIPIDS-related force fields. | Strongest candidate route for R4-GAP-03. It names a real Martini 3 fragment layer and atomistic force-field targets, but it is not installed locally and has not been tested on `chctrl`. |
| Backward | Official GitHub repo `Tsjerk/Backward`, README, root contents, `Mapping` contents | GitHub latest-release endpoint returned HTTP 404 in this session. The repository root contains `backward.py`, `initram.sh`, `qfit.py`, and `Mapping`. README is only a title in the raw file checked here. Mapping names include amino-acid `*.charmm36.map` entries and lipid entries such as `popc.charmm36.map`, `pope.charmm36.map`, `popg.charmm36.map`, and `pops.charmm36.map`. | Usable as historical/source-visible backmapping context, but weaker than CG2AT for this R4-GAP-03 evidence row because local docs are sparse and Martini 3 scope was not confirmed from the repo files checked here. |
| sinceCG | Repo extraction from Lopez2022 | `r4_cg_method_extraction_20260704.md` records sinceCG as a modified Backward-style Martini 2.2 to CHARMM36 AA conversion protocol in a MuMMI RAS-RBDCRD membrane workflow. The extracted paper reports staged minimization/short MD, stereochemistry controls, distance-restraint networks, failure handling, and higher success than Backward in that system. | Validation vocabulary for stereochemistry, failure handling, and interface-loss checks. Immediate R4 routing remains with source-pinned Martini 3-compatible candidates because this source is Martini 2.2/RAS-RBDCRD and the repo lacks a local/general sinceCG tool route. |
| Sahoo2023 Backward/CG2AT-style comparison | Repo extraction from Sahoo2023 | The R4 extraction records Martini 3 TM-dimer simulations followed by Backward/CG2AT-style atomistic comparison for NMR/PREDDIMER/AlphaFold comparison. | Supports the expectation that atomistic comparison is needed after Martini 3 CG sampling, but it does not provide an exact transferable `chctrl` conversion workflow. |

## Project Interpretation

### What changed for R4

This screen sharpens the local R4 material decision into tool-specific status:

- `CG2AT` is a concrete external route candidate with Martini 3 fragment database entries.
- `Backward` is source-visible and historically relevant but under-documented for the immediate R4 need.
- `sinceCG` remains a Lopez2022/MuMMI validation bridge rather than a ready local Martini 3 route.

This supports a later material-boundary review if R4 is explicitly reopened.
Dry-build package status still requires local executable validation and `chctrl`
conversion evidence.

### How CG2AT would affect a future R4 object contract

If a future approved R4 review uses CG2AT, the object contract would need
additional fields:

| Required field | Why it matters |
|---|---|
| `cg_to_aa_tool` | Must name CG2AT version/source, command interface, and fragment/force-field pair. |
| `fragment_database` | Must choose the Martini 3 fragment family, for example `martini_3-0_charmm36` or another explicit directory, rather than saying only "Martini 3". |
| `atomistic_forcefield_target` | Must choose and record the atomistic force field target, because downstream comparison to existing `chctrl` atomistic metrics depends on it. |
| `original_atomistic_input` | CG2AT can use an atomistic input with `-a`; for `chctrl`, the future policy must decide which exact atomistic reference is allowed. |
| `grouping_policy` | Multichain fitting can use `-group` patterns; receptor and Galpha handling must be explicit. |
| `membrane_lipid_water_handling` | The route must preserve or reconstruct protein, POPC, ions, and solvent consistently enough for AA relaxation and metric recomputation. |
| `post_conversion_checks` | Stereochemistry, residue completeness, chain identity, membrane embedding, periodicity, receptor-Galpha interface contacts, alpha5/eCT geometry, and short AA relaxation sanity must be checked before interpretation. |

### Historical classification

At the time of this screen, `R4-GAP-03` was recorded as a historical evidence
classification:

```text
historical_reopen_for_material_decision_pending_tool_validation
```

Meaning: the source-route gap was no longer blank, but the repo still lacked a
local executable/tool-pinned route and no `chctrl` conversion had been
validated.

## Conditional R4 Follow-Up

If a future dated R4 decision record is routed through `docs/INDEX.md`, it should use
`r4_local_toolchain_inventory_20260706.tsv` as the R4-GAP-06 inventory for
CG2AT, Backward, martinize2/vermouth, Go/contact generation, `insane.py`, Yang
tutorial archive files, and local `gmx`. CG2AT or Backward installation
requires separate approval. Any approved validation phase would
need to start with source/version pinning and a non-`chctrl` smoke check from
official/example material before touching any `chctrl` full-system payload.

R4-GAP-04 and R4-GAP-05 are recorded in
`r4_chctrl_payload_policy_20260706.md` and
`r4_chctrl_contact_map_feasibility_20260706.md` as supporting evidence for a
future review.

## Local Checks Used

```text
rg --files | rg -i '(cg2at|backward|sincecg|martinize|vermouth|insane|govirt|goVirt|ContactMap|olives|oligomers)'
python3 -B -c 'import shutil; ... shutil.which(...) ...'
```

The local repo/PATH checks found zero installed or repo-expanded `cg2at`, `backward`, `sinceCG`, `martinize2`, `vermouth`, `gmx`, `insane.py`, `create_goVirt.py`, or `create_goVirt_for_multimer.py` executables. Yang tutorial source files remain inside the archived zip; repo expansion requires an explicit extraction step.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-tutorial.zip`
- CG2AT official repository: `https://github.com/owenvickery/cg2at`
- CG2AT release `v0.9`: `https://github.com/owenvickery/cg2at/releases/tag/v0.9`
- CG2AT fragments directory: `https://github.com/owenvickery/cg2at/tree/master/database/fragments`
- CG2AT forcefields directory: `https://github.com/owenvickery/cg2at/tree/master/database/forcefields`
- Backward official repository: `https://github.com/Tsjerk/Backward`
- vermouth-martinize release `v0.15.0`: `https://github.com/marrink-lab/vermouth-martinize/releases/tag/v0.15.0`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_local_toolchain_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_policy_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_map_feasibility_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
