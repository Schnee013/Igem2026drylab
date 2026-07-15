# Payload Tracking Policy

> Status: repo-local Git tracking policy.
>
> Scope: payload bodies, manifests, checksums, storage pointers, and Git ignore
> rules for drylab workflows.
>
> Loading rule: read this file when classifying payload/manifests/checksums,
> reviewing `.gitignore`, running a tracking gate, or preparing a commit that
> touches generated/runtime/archive material. Ordinary project-status, MD
> interpretation, literature, and modeling tasks use `DOCMAP`, `INDEX`, and
> domain evidence files as their entry points.

## Principle

Git tracks source-of-truth contracts and compact provenance. Operation-produced
payload bodies stay in external/local storage unless a workflow explicitly
promotes a file to a repo-owned canonical input.

Classify by ownership and recoverability first:

1. Who produced the file: repo source, manual session, E2, CHARMM-GUI, PPM,
   GROMACS, validator, repair step, return intake, or archive import.
2. Whether the file body is the durable source of truth, or whether it can be
   recovered from an external/local storage pointer plus checksum.
3. Whether consumer work needs the body itself or only the route, checksum,
   producer, consumer, and validator result.
4. Whether a similar extension is actually a canonical repo input or template.

Decision basis: ownership, recoverability, and canonical-use status come before
extension, size, or binary/text status.

## Tracking Classes

| Class | Track in Git | Keep as pointer or external/local storage |
|---|---|---|
| Repo-owned canonical inputs/templates | MDP templates, accepted topology/ITP inputs, small source configs, scripts, tests, docs, stable handoff settings | Runtime copies and repair outputs generated from them |
| Workflow contracts | command plans, work orders, package status, source pointers, decision packages, validator gate summaries | Raw package bodies duplicated from E2/CHARMM-GUI/PPM |
| Provenance and recovery | manifests, checksums, storage location, producer/consumer, restore route | Payload bodies that are recoverable from the recorded route |
| Operation payload bodies | only when explicitly promoted as a canonical input | raw trajectories, `.tpr/.xtc/.edr/.cpt`, runtime logs, copied input packages, repaired indexes, PPM raw/clean outputs |
| Local-only literature/source payload | README, source ledger, checksums, DOI/source pointers | local PDF/ZIP binaries and research-run state |
| Validator evidence | compact pass/fail files and parsed summaries when they are the reviewed result | full raw logs unless a workflow names them as compact evidence |

## Current Repo Patterns

- Repaired `index.fixed.ndx` bodies stay local/E2. Track a route file with
  checksum, producer, consumer, storage location, and restore instructions.
- CHARMM-GUI returned archives or extracted packages are payload bodies until a
  specific file is promoted as the accepted canonical system input.
- PPM raw and clean output PDB bodies are operation-produced payloads. Track
  status/manifest/checksum and the CHARMM-GUI upload handoff material when that
  handoff is the manual submission contract.
- E2 raw outputs and machine-state files stay in local ignored storage or E2.
  Track README/source pointers, checksum manifests, parsed summaries, and
  reviewed gate files.
- Literature attachments use README plus `source_files.sha256`; local PDF/ZIP
  bodies stay ignored.

## Manifest Schema

Use `docs/ops/templates/payload_manifest.schema.tsv` for new payload manifests.
At minimum, payload rows need:

- `path`
- `role`
- `owner`
- `tracked_policy`
- `bytes`
- `sha256`
- `storage_location`
- `producer`
- `consumer`
- `stage`
- `required_for`
- `recovery_pointer`

Use `unknown` or `pending` explicitly for fields that still lack evidence, rather
than leaving a payload row ambiguous.

## Commit And Gate Rules

Before staging payload or tracking-rule changes, run a report-only pass:

```bash
python3 scripts/check_payload_tracking_policy.py
git ls-files -ci --exclude-standard
```

The gate must flag tracked payload bodies that match this policy's forbidden
classes. It may warn, rather than fail, on legacy manifests that predate the
full schema.

Stage only explicit paths after classifying each changed file as source,
contract, manifest, validator result, payload body, local-only archive, or
unrelated work. Broad staging commands such as `git add .`, `git add -A`, and
`git add --all` are outside this policy.

## Linking Boundary

`docs/INDEX.md`, daily logs, and modeling documents may link here for
payload/tracking governance. Long tracking-policy explanations stay in this
file.
