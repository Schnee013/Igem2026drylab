# Image2 Prompts For DryLab Presentation Figures

Use these prompts for GPT image2 or another image-generation model. They are
designed as four separate 16:9 figures to insert into the NotebookLM deck
placeholders.

General instruction for all four figures:

- Use a clean professional scientific infographic style.
- 16:9 aspect ratio.
- White or warm off-white background.
- Thin technical line art with restrained color.
- Palette: dark navy, muted purple, green, orange; red only for blocked or
  do-not-use relationships.
- Leave several blank dashed label boxes for later editing in PowerPoint.
- Avoid tiny dense text. Use short readable English labels only where needed.
- Do not include final quantitative values, final ROI, final Kd, final EC50,
  Emax, Hill coefficient, or uncalibrated parameter values.

## IMAGE2-01 Product Workflow

```text
Create a 16:9 scientific infographic for a field-use biosensor workflow.

Subject: a plant-parasitic nematode early detection workflow using a lyophilized engineered yeast colorimetric test strip.

Visual flow from left to right:
1. crop field and root-zone soil sample,
2. simple soil/root extract droplet,
3. droplet added onto a lyophilized yeast paper strip or paper card,
4. visible color development on the strip with a simple color scale,
5. early intervention decision: targeted management checklist, not a guaranteed outcome.

The final product must look like a low-cost paper strip or paper card containing freeze-dried yeast biosensor cells. It should be field-deployable, simple, and non-instrumental.

Include visual hints of the engineering mechanism in small side icons: ascaroside signal, engineered yeast cell, color reporter.

Leave blank dashed label boxes near each stage for later text insertion.

Strict negative constraints:
- Do not draw a professional electronic detector.
- Do not draw a calculator-like analyzer.
- Do not draw a benchtop laboratory instrument.
- Do not make a test tube or orange liquid vial the final product.
- Do not imply the system fully replaces pest management.
- Do not show final ROI or numeric performance claims.
```

## IMAGE2-02 Signal Pathway

```text
Create a 16:9 scientific pathway diagram in a clean technical line-art style.

Show the engineered yeast signal pathway:
ascaroside molecules -> heterologous fungal GPCR receptors Gpr2/Gpr3 in yeast membrane -> chimeric Gpa1 -> G beta/gamma release -> Ste20 -> Ste11 -> Ste7 -> Fus3/Kss1 MAPK cascade -> Ste12/sTF output -> GAL amplification module -> pigment reporter -> visible color readout on a lyophilized yeast paper strip.

Make the pathway scientifically clear:
- The receptor should be embedded in a yeast membrane.
- Label the receptor module as "Gpr2/Gpr3".
- Label the G protein module as "chimeric Gpa1 + G beta/gamma".
- Label the kinase cascade as "Ste20 / Ste11 / Ste7 / Fus3-Kss1".
- Label the output module as "sTF -> GAL -> pigment".
- The final readout should be a colorimetric paper strip, not a detection instrument and not a test tube-only assay.

Add small blank dashed callout boxes for:
- receptor-ligand calibration,
- chimeric coupling,
- MAPK dynamics,
- reporter gain/leakage,
- color readout threshold.

Strict negative constraints:
- Do not include uncalibrated numerical values.
- Do not show docking score becoming Kd or EC50.
- Do not draw a professional analyzer or electronic detector as the product.
- Do not make the diagram look like a medical diagnostic device.
```

## IMAGE2-03 Parameter State Matrix

```text
Create a 16:9 scientific infographic showing the ODE model evidence and parameter-state boundary.

Central layout: a five-column matrix with clear color-coded headings:
1. Fixed topology
2. Literature prior
3. Scenario scan
4. Wet-lab required
5. Do-not-use

Content concept:
- Fixed topology: yeast GPCR/MAPK module order and reporter architecture.
- Literature prior: broad prior ranges or method context only.
- Scenario scan: log-scale ligand half-activation, efficacy, basal leak, reporter gain, copy-number sensitivity.
- Wet-lab required: project dose-response, time-course, basal/no-ligand output, Emax, Hill, expression/localization, chimeric Gpa1 coupling.
- Do-not-use: docking score or docking Delta G as direct affinity parameter.

Show a red blocked arrow from "docking Delta G / docking score" to "Kd / EC50 / Emax / Hill" with a visible X or no-entry symbol.

Also show a safe green arrow from "docking candidate labels + relative ranking" to "ODE scenario set".

Include blank dashed label boxes at top and bottom for slide annotations.

Strict negative constraints:
- Do not place Kd or EC50 under "literature prior" as if final for this project.
- Do not show docking values converting to affinity constants.
- Do not include any final calibrated parameter table.
- Do not imply the ODE solver is already complete.
```

## IMAGE2-04 Cost Accounting Model

```text
Create a 16:9 professional economic model infographic for a field-use biosensor project.

Main idea: deterministic cost-accounting model, not a biological dynamic model.

Left input modules:
- nematode density / crop loss function,
- crop yield and crop price,
- lyophilized yeast strip cost and deployment density,
- intervention cost and intervention effect,
- local HP / market parameters.

Center module:
- deterministic cost-accounting model,
- simple formulas or calculator logic may be represented abstractly as a spreadsheet/model panel, but do not make it look like the biosensor product.

Right output modules:
- gross loss,
- avoided loss,
- break-even early-program cost,
- net benefit,
- ROI scenario,
- HP parameter recovery checklist.

Add a small icon of the actual product as a lyophilized yeast paper strip with color readout near the sensor-cost input. Make clear that this paper strip is the product, while the central model is only an analysis framework.

Use a professional technical style with blank dashed label boxes for later editing.

Strict negative constraints:
- Do not imply final ROI is proven.
- Do not use docking Delta G, Kd, EC50, or wetlab-unverified assumptions as economic inputs.
- Do not draw the central cost model as the physical detection product.
- Do not show a professional detector, boxed analyzer, or laboratory instrument as the product.
```
