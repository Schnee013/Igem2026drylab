# NotebookLM Prompt For Revised DryLab PPT

Use this prompt after manually uploading `notebooklm-source-brief.md` into
NotebookLM. NotebookLM cannot access local filesystem paths, so do not ask it to
"open" or "read" local paths. If more context is needed, manually upload the
extra source files named in the brief.

```text
Create a 10-12 slide professional technical presentation in Chinese for an iGEM drylab progress meeting.

Primary source: use the uploaded drylab presentation brief as the controlling source. Treat any local filesystem paths inside the brief as provenance labels only; do not assume you can access them. Use other manually uploaded project documents only to support or verify the brief. If sources conflict, follow the brief's source-boundary instructions and do not invent missing results.

Core task:
- Explain the drylab engineering progress through "问题 / 原理 / 进度 / 缺口".
- The deck should be direct, technical, and suitable for a meeting presentation. Do not write it like a story recap.
- Make the audience understand how molecular design, signal pathway ODE modeling, wetlab calibration, HP inputs, and economic cost-accounting fit into one engineering loop.

Critical title rule:
- Do NOT use P0, P1, P2, P3, or other internal priority labels as slide titles.
- Use audience-facing slide titles such as "信号通路模型定义传感器需要证明什么", "ODE 建模区分已固定拓扑与待校准参数", and "经济模型把早期检测转化为 break-even 与 ROI 情景".
- Internal labels may appear only as small source tags or footnotes if absolutely needed.

Critical product-form rule:
- The final product concept is a field-use lyophilized yeast test strip / paper strip / paper card with visible color readout.
- Do NOT represent the final product as an electronic detection instrument, calculator-like detector, lab analyzer, or test-tube-only assay.
- A phone or simple color scale may be shown only as optional readout support.

Image placeholder rule:
- Leave four large blank dashed placeholders for externally generated image2 figures.
- Do NOT generate diagrams inside these placeholders.
- Each placeholder should have only an ID and a one-line caption:
  1. IMAGE2-01 Product Workflow
  2. IMAGE2-02 Signal Pathway
  3. IMAGE2-03 Parameter State Matrix
  4. IMAGE2-04 Cost Accounting Model
- Make sure the slide layout leaves enough whitespace for these images to be inserted later.

Scientific boundary rules:
- Reporter architecture is confirmed as: heterologous Gpr2/Gpr3 -> chimeric Gpa1 -> MAPK cascade -> sTF -> GAL amplification -> pigment color readout.
- Concrete pigment, integration site, actual copy number, reporter gain, basal leak, Kc/EC50-like value, Hill coefficient, Emax, and color-development time are not final. They are wetlab-required or scenario-scan variables.
- Docking output can provide candidate labels, channel direction, relative ranking, and interaction clues.
- Docking Delta G or docking score must NOT be converted into Kd, EC50, Emax, Hill coefficient, basal leak, reporter gain, or economic inputs.
- ODE currently has evidence organization and calibration design, not a final implemented solver/config/CSV/plot package.
- P2 economics is deterministic cost-accounting, not a biological dynamic model.
- Current P2 work supports arithmetic validation, public example reproduction, break-even structure, and HP parameter collection. It does NOT prove final ROI for the target deployment region.

Suggested slide spine:
1. DryLab Engineering Progress: From GPCR Sensor Design To Field-use Decision Support
2. One-system overview with IMAGE2-01 placeholder
3. Detection problem and lyophilized yeast strip product concept
4. Molecular design input: receptor candidates and chimeric Gpa1
5. Signal pathway model with IMAGE2-02 placeholder
6. ODE model role: dose response, copy number, leakage, dynamic range
7. ODE parameter status with IMAGE2-03 placeholder
8. ODE next calibration plan: dose-response, time-course, basal leak, Emax, Hill, expression/localization, reporter dynamic range, chimeric Gpa1 coupling
9. Economic model role with IMAGE2-04 placeholder
10. Economic progress and guardrail: MVP arithmetic validation, public example, benchmark extraction, no final ROI claim
11. Wetlab and HP feedback loop
12. Closing summary and next actions

Visual style:
- Professional technical deck, not a cartoon explainer.
- White or very light background.
- Thin technical line art, clean hierarchy, generous whitespace.
- Palette: dark navy, muted purple, green, and orange; red only for blocked/do-not-use edges.
- Use concise titles and 3-5 bullets per slide.
- Avoid generic AI visuals, full-slide busy images, and one-hue templates.

Export preference:
- If the tool provides any option for editable text/shapes rather than full-slide images, prefer editable slide components.
- Do not flatten source text into inaccessible image-only pages if avoidable.
```
