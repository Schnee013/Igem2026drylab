---
purpose: NotebookLM source brief for drylab progress presentation
status: draft_for_slide_generation
last_updated: 2026-06-03
---

# DryLab Engineering Progress Presentation Brief

This file is designed to be uploaded directly into NotebookLM as a source.
NotebookLM cannot access local filesystem paths, so every instruction needed for
slide generation is included in this file. Local paths below are provenance
labels for the human operator, not links that NotebookLM can open.

This brief is for generating a presentation structure. It is not the scientific
authority for the project. If a factual conflict appears after additional files
are uploaded, prefer the manually uploaded source document over older deck
material.

## How To Use This With NotebookLM

Recommended upload set:

1. Upload this file first and treat it as the controlling source for slide
   organization and guardrails.
2. If NotebookLM needs more supporting context, manually upload the source
   documents listed in "Provenance Files For Human Upload" below.
3. Do not expect NotebookLM to read local directory paths such as
   `docs/modeling/...`; those paths are only here so the human operator knows
   which files to upload.
4. Do not upload every old deck unless you want style comparison. Old decks are
   reference material and may contain stale structure or weaker visual choices.

Minimal source set for NotebookLM:

- Upload this brief as the main source.
- Copy the NotebookLM prompt from `docs/presentation/notebooklm-prompt.md` into
  the NotebookLM chat or slide-generation instruction box; it does not need to
  be uploaded as a source.
- Optional: `P0-signal-pathway-ode.md`, `004-reporter-output-architecture.md`,
  `P2-economic-benefit.md`, and `P2-economic-benefit-validation.md`, uploaded
  manually as separate sources.

## Provenance Files For Human Upload

- Current project router: `docs/INDEX.md`
- ODE pathway and parameter boundary: `docs/modeling/P0-signal-pathway-ode.md`
- Reporter output architecture: `docs/decisions/004-reporter-output-architecture.md`
- Economic model scope and guardrails: `docs/modeling/P2-economic-benefit.md`
- Economic validation boundary: `docs/modeling/P2-economic-benefit-validation.md`
- Existing presentation/reference materials: `docs/presentation/reference-materials/`

These local paths should not be used as slide text. They only identify where the
project source material came from.

## Audience And Goal

Audience: iGEM team members, instructors, and drylab/wetlab/HP collaborators.

Goal: explain the drylab engineering progress in a professional meeting style:
what problem each modeling direction solves, the basic principle, current
progress, and what remains to be calibrated by wetlab or HP data.

The deck should not sound like a story recap. Use direct technical statements.

## Product Form Must Be Clear

The intended product concept is a field-deployable biosensor based on yeast
color readout. In visuals, represent it as a lyophilized yeast test strip,
paper strip, or paper card with visible color development.

Do not represent the product as a professional electronic detector, calculator,
laboratory instrument, boxed analyzer, or test tube-only assay. A phone or
simple color scale may appear only as optional readout support.

## Title Rules

Do not use internal priority labels such as P0, P1, P2, or P3 as slide titles.
Those labels are internal routing tags, not audience-facing titles.

Use audience-facing titles such as:

- Signal Pathway Model Defines What The Sensor Must Prove
- ODE Work Separates Fixed Topology From Parameters Still Needing Calibration
- Economic Model Converts Early Detection Into Break-even And ROI Scenarios
- Wetlab And HP Data Are The Remaining Calibration Inputs

The internal labels may appear only as small source tags in footnotes if needed.

## Core Message

Drylab is connecting molecular design, signal pathway modeling, and economic
decision support into one engineering loop:

1. Molecular work identifies receptor and chimeric G protein design candidates.
2. The signal pathway model defines how ligand response should propagate through
   yeast GPCR/MAPK signaling into a color reporter.
3. The ODE work currently organizes topology, parameter states, and calibration
   needs; it has not yet produced a final solver/config/plot package.
4. The economic model is deterministic cost accounting; it can validate public
   examples and break-even logic, but final project ROI still requires HP,
   wetlab, local market, and product-cost data.
5. The final presentation should make the calibration gaps explicit rather than
   hiding them.

## Scientific Boundary Statements

Use these statements consistently:

- Reporter architecture is confirmed as:
  `heterologous Gpr2/Gpr3 -> chimeric Gpa1 -> MAPK cascade -> sTF -> GAL amplification -> pigment color readout`.
- Concrete pigment choice, integration site, actual copy number, reporter gain,
  basal leakage, Kc/EC50-like value, Hill coefficient, Emax, and color
  development time are not final. They are wetlab-required or scenario-scan
  variables.
- Docking output can provide candidate labels, channel direction, relative
  ranking, and interaction clues.
- Docking Delta G or docking score must not be converted into Kd, EC50, Emax,
  Hill coefficient, basal leak, reporter gain, or economic inputs.
- ODE currently has evidence organization and calibration design, not a final
  implemented solver.
- P2 economics is not a biological dynamic model. It is deterministic
  cost-accounting using crop loss, crop value, early detection cost,
  intervention cost, and intervention effect.
- Current P2 work supports arithmetic validation, public example reproduction,
  break-even structure, and HP parameter collection. It does not prove final ROI
  for the target deployment region.

## Suggested Deck Structure

Use 10 to 12 slides. Recommended structure:

1. Title slide
   - Title: DryLab Engineering Progress: From GPCR Sensor Design To Field-use
     Decision Support
   - Subtitle: Signal pathway ODE modeling and economic model calibration
   - No P0/P2 title.

2. One-system overview
   - Show the engineering loop from molecular candidates to pathway model,
     wetlab calibration, and HP/economic decision support.
   - Leave an image placeholder for `IMAGE2-01 Product Workflow`.

3. Detection problem and product concept
   - Problem: plant-parasitic nematodes cause yield loss and are hard to detect
     early from field symptoms.
   - Principle: detect ascaroside-related signals using engineered yeast and a
     visible color readout.
   - Product form: lyophilized yeast strip or paper card.
   - Gap: field protocol, color threshold, and product cost need calibration.

4. Molecular design input
   - Explain receptor candidates and chimeric Gpa1 as upstream design inputs.
   - State that docking ranks and mechanism clues guide scenarios but do not
     become direct affinity constants.

5. Signal pathway model
   - Leave an image placeholder for `IMAGE2-02 Signal Pathway`.
   - Required pathway label:
     `Gpr2/Gpr3 -> chimeric Gpa1 -> G beta/gamma -> Ste20/Ste11/Ste7/Fus3 -> Ste12/sTF -> GAL -> pigment color`.
   - State: topology is usable; numerical rates and project-specific reporter
     parameters still need calibration.

6. ODE model role
   - Problem: estimate detectable concentration range, dynamic range, leakage,
     and amplification choices.
   - Principle: represent pathway/reporter modules as an ODE with dose-response,
     copy-number, and leakage sweeps.
   - Progress: topology and parameter-state matrix are organized.
   - Gap: solver/config/CSV/plots are not yet implemented.

7. ODE parameter status
   - Leave an image placeholder for `IMAGE2-03 Parameter State Matrix`.
   - Separate fixed topology, literature prior, scenario scan, wetlab required,
     and do-not-use.
   - Make the blocked edge from docking score or Delta G to Kd/EC50 visible.

8. ODE next calibration plan
   - Show wetlab replacement conditions: dose response, time course, basal leak,
     Emax, Hill, expression/localization, reporter dynamic range, chimeric Gpa1
     coupling.
   - Present this as a test plan, not a completed result.

9. Economic model role
   - Leave an image placeholder for `IMAGE2-04 Cost Accounting Model`.
   - Explain deterministic cost-accounting inputs and outputs:
     crop loss, crop value, detection cost, intervention cost/effect,
     gross loss, avoided loss, break-even cost, net benefit, ROI scenario.

10. Economic progress and boundary
    - Progress: MVP framework, public example arithmetic validation, benchmark
      extraction, HP questionnaire route.
    - Gap: sensor cost, deployment density, performance, local market, and
      intervention assumptions are not final.
    - Avoid saying final ROI is proven.

11. Integrated wetlab/HP feedback loop
    - Wetlab provides calibration data for the signal model.
    - HP provides local economic inputs and deployment assumptions.
    - Drylab turns both into design constraints and decision-support outputs.

12. Closing summary
    - Use three concise points:
      1. The sensor pathway architecture is defined.
      2. ODE and economic models are organized around calibration boundaries.
      3. Next progress depends on wetlab and HP parameter recovery.

## Required Image Placeholders

NotebookLM must leave blank space for four externally generated images:

- `IMAGE2-01 Product Workflow`: field-use lyophilized yeast test strip workflow.
- `IMAGE2-02 Signal Pathway`: Gpr2/Gpr3 to pigment reporter pathway.
- `IMAGE2-03 Parameter State Matrix`: ODE evidence and parameter boundary.
- `IMAGE2-04 Cost Accounting Model`: deterministic economic model flow.

Do not auto-generate illustrations inside these placeholders. Use an empty
dashed rectangle with the placeholder ID and a one-line caption only.

## Visual Style Direction

Professional technical meeting deck. Avoid cartoon-heavy, generic AI, or
one-color template style.

Preferred style:

- White or very light background.
- Thin technical line art and clean diagrams.
- Palette: dark navy, muted purple, green, and orange; use red only for
  explicit "do-not-use" or blocked edges.
- Use concise titles and 3-5 bullets per slide.
- Leave enough whitespace for the four image placeholders.
- Use clear section rhythm: overview, pathway/ODE, economics, integration.

Avoid:

- Full-slide busy screenshots.
- P0/P2 as main title text.
- Electronic analyzer, calculator, or professional detector as the final product.
- Claiming final Kd, EC50, Emax, Hill, sensor performance, or ROI.
- Treating NotebookLM-generated visuals as scientific evidence.
