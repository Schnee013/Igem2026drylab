# R4 chctrl Payload Policy

> Date: 2026-07-06
>
> Status: historical/supporting R4-GAP-04 payload policy.
>
> Scope: durable pointer policy for exact `chctrl` full-system inputs that a future R4 contact-map or dry-build validation phase would need.
>
> Role: pointer/checksum policy for future approved validation phases.

## Working Conclusion

R4 can cite exact `chctrl` full-system inputs only through a tracked pointer/manifest layer unless a later archive decision explicitly creates a durable external payload package.

For this 2026-07-06 policy record, the R4 payload model is:

1. Track small text manifests and policy files in git.
2. Keep large raw GROMACS/PDB payloads ignored unless the user explicitly approves a separate archive route.
3. Treat protein-only snapshots and contact-anchor TSVs as design/validation anchors, not as full-system build inputs.
4. Require checksum verification before any later contact-map generation, CG conversion, or CG-to-AA validation attempt.

This closes R4-GAP-04 enough for planning discipline: a future approved R4 work
order could name exact required payloads and stop if they are missing or
mismatched, without pretending ignored local files are durable repo artifacts.

## Payload Inventory

Machine-readable inventory:

```text
experiments/chimeric-gpa1/literature/r4_chctrl_payload_inventory_20260706.tsv
```

Key local facts checked on 2026-07-06:

| Payload | Local status | Size / line count | SHA-256 | Git ignore rule |
|---|---|---:|---|---|
| Original `chctrl` full-system `step5_input.pdb` | present | `20M`; `263911` lines | `0382a7f654522688cf057e57495d940e739483fdb027f1483b485a55c5891306` | `.gitignore:71 experiments/md-simulation/results/**/raw/` |
| Early-gate copy of same `step5_input.pdb` | present | `20M`; `263911` lines | `0382a7f654522688cf057e57495d940e739483fdb027f1483b485a55c5891306` | `.gitignore:71 experiments/md-simulation/results/**/raw/` |
| R1 reduced full-system `step5_input.pdb` | present | `19M`; `257135` lines | `f2a2d1b9e484fcf162dcd0a95b703326ac384e253344914e2fd59835c59c8446` | `.gitignore:84 experiments/md-simulation/results/**/input/gromacs/` |
| Early-gate raw rep1 trajectory package | checksum manifest present | raw dir `140M` | `prod.tpr`, `prod.xtc`, `prod.edr`, `prod.cpt`, `prod.log` hashes recorded in `raw/rep1/SHA256SUMS.txt` | `.gitignore:71 experiments/md-simulation/results/**/raw/` |
| Selection-audit protein snapshots | present | snapshots dir `13M` | per-file hashes available through existing audit/material records | `.gitignore:81 experiments/md-simulation/results/**/analysis/**/snapshots/*.pdb` |

The broader `chimeric-ste2-gpa1-wt/raw` directory is about `949M`; normal source-control handling should retain manifests, checksums, and route records instead of the raw directory.

## Allowed Payload References

| Reference type | Allowed use | Gate |
|---|---|---|
| Tracked checksum manifest | Name exact required raw file, expected SHA-256, size/line-count, and local or external archive pointer. | Durable raw-payload claims require a named archive source. |
| Ignored local path plus checksum | Local feasibility checks and future local validation if the file exists and checksum matches. | Cross-session build claims require current availability and checksum verification. |
| External archive pointer | Durable payload route if a later user-approved archive stores the raw package outside git. | Archive claims require a recorded source. |
| Protein-only snapshot pointer | Atomistic metric recomputation, visual anchors, contact-anchor design. | Full-system build use requires membrane/ion/topology inputs. |
| Derived R4 anchor TSV | Contact-policy design and later validation checklist. | Generated contact files or full-system payloads remain separate required inputs. |

## Conditional Payload Gate

Before any future R4 contact-map generation or dry-build package, a separately
approved R4 validation decision would have to pass this gate:

| Gate item | Required evidence |
|---|---|
| Exact payload identity | Path or archive ID, SHA-256, size, and file class. |
| Availability | File exists locally or is recoverable from a named archive source. |
| Checksum match | Fresh `shasum -a 256` result matches the tracked inventory. |
| Object suitability | The payload has the required chain/residue identities and full-system context for the intended task. |
| Tool compatibility | The chosen tool can read that file class without remote-only assumptions. |
| Derived output traceability | Any contact map, CG model, or AA conversion output records the input payload hash. |

If any gate item fails in a future approved phase, no build/run plan should be
written from that payload.

## Recommended Policy For Each Payload Class

### Full-system original `chctrl` input

Use the original full-system `step5_input.pdb` as the preferred future
atomistic reference candidate only after a future approved phase verifies:

- the file exists;
- SHA-256 equals `0382a7f654522688cf057e57495d940e739483fdb027f1483b485a55c5891306`;
- chain mapping still matches `PROA = Gpa1-WT` and `PROB = Ste2`;
- the future contact generator can consume the selected atomistic/protein subset without silently dropping needed membrane or chain context.

This payload remains under ignored `raw/`; tracked use goes through checksum and
archive pointers.

### Early-gate raw trajectory

Use the early-gate raw trajectory package only as a post-start full-system frame source if a later phase defines how to extract a frame with a verified GROMACS environment.

Current tracked-safe evidence is the checksum list:

```text
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/raw/rep1/SHA256SUMS.txt
```

The existing early-gate report records the raw XTC coverage and file hashes; a future R4 phase must re-verify payload availability before using it.

### Selection-audit protein snapshots

Use selection-audit snapshots as contact/metric anchors only. They are useful because they preserve `PROA`/`PROB` protein geometry at selected times, but they do not include membrane, solvent, or ions.

They are acceptable inputs for:

- contact-class design;
- alpha5/eCT metric recomputation;
- visual sanity checks;
- validating that a future CG-to-AA output can be compared to the same metric family.

Full-system build input status requires membrane, solvent, ion, and topology
context.

### R1 reduced full-system payload

Use R1 reduced `step5_input.pdb` as historical chctrl build/run evidence or a
comparison object. The default R4 atomistic reference still requires a future
approved payload choice.

Reason: the existing R4 material matrix records R1-Z as an exploratory evidence
point with insufficient atom-count benefit.

## What This Enables

This policy lets a future R4 artifact be precise if the lane is reopened:

- R4-GAP-05 can cite exact anchor classes and stop short of generating contact maps.
- A later tool-validation phase can require a matching payload checksum before touching `chctrl`.
- A future archive decision can be made explicitly instead of creeping large ignored payloads into git.

## Historical R4 Evidence Classification

```text
historical_continue_gap_queue_with_payload_policy
```

At the time of this record, R4 had a usable payload policy, a contact-map
feasibility spec, and a CG-to-AA route candidate. Local executable tool
validation, actual `chctrl` contact maps, and a tested CG-to-AA conversion
remained required before any buildable `chctrl` route.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_map_feasibility_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_anchor_spec_20260706.tsv`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/shared/step5_input.pdb`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/raw/shared/step5_input.pdb`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/raw/rep1/SHA256SUMS.txt`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/exported_snapshots.csv`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/input/gromacs/step5_input.pdb`
- `.gitignore`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
