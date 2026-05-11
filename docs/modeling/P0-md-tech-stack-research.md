---
direction: P0-md-simulation
doc_type: research-report
scope: tech-stack (software + force field + membrane builder)
status: draft
last_updated: 2026-04-16
---

# P0-MD 技术栈调研报告（软件 / 力场 / 膜构建）

> 本文件是 [P0-md-simulation.md](P0-md-simulation.md) 第一优先级"技术栈调研"的产出（前 3 维度）。
>
> **调研方法**：`everything-claude-code:deep-research` skill + 3 个并行研究子代理（WebSearch + WebFetch），每维度 10-15 个独立来源，优先 2023-2026 文献。本环境未配置 firecrawl/exa MCP，使用内置 WebSearch/WebFetch 完成。
>
> **调研时间**：2026-04-12
>
> **尚未覆盖的维度**（后续调研）：配体参数化细节（已在 §2 涉及 CGenFF/GAFF2/OpenFF 但需 ascaroside 专题深入）、时间尺度惯例、盐桥/HBond 分析工具、MM-PBSA/自由能。

---

## Executive Summary

针对 iGEM 2026 真菌 GPCR + ascaroside 的 MD 需求，三维度调研一致指向**单一主流栈**：

| 维度 | 推荐 | 备选 | 淘汰 |
|---|---|---|---|
| MD 引擎 | **GROMACS**（主生产）+ **OpenMM**（Python 原型/分析） | AMBER（若做 alchemical FEP） | Desmond（闭源 + 公开披露条款）、NAMD（工具链脱节）、g_membed |
| 力场组合 | **CHARMM36m + CGenFF + CHARMM36 lipid + TIP3P** | ff19SB + GAFF2 + Lipid21 + OPC | OPLS-AA/M（膜生态弱） |
| 膜构建 | **CHARMM-GUI Membrane Builder**（PPM 2.0 对齐） | PACKMOL-Memgen（仅 Amber pipeline） | g_membed（官方已推荐用 CHARMM-GUI 替代） |
| 膜组分 | **POPC 纯膜主力** + POPC:ergosterol (80:20) 二轮敏感性 | — | 复杂 4-5 组分酵母质膜（时间预算不可承受） |

**科学问题对齐度**：C36m 的 Arg-Asp/Glu 盐桥 LJ 修正**正好对症本项目的 V138R 胍基-ascaroside 羧基盐桥假说**——这是力场层面对 Top 1 科学问题最强的证据支持。

**最关键风险**：ascaroside（α-L-ascarylose 糖环 + C7 脂肪酸末端羧基）在 CGenFF 下**糖环 penalty 很可能超过 50**，必须做 QM 审计与重拟合；尤其 C7 羧基的 charge/dihedral 是 V138R 盐桥判定的药效团，不审计直接跑 = 垃圾进垃圾出。

**信心度**：High（3 维度主流趋势明确，来源交叉互证）。

---

## 1. MD 软件选型

### 1.1 候选对比表

| 软件 | 2023-2026 GPCR 使用频率 | 教程/学习曲线 | 授权 | CUDA 性能 (单 GPU) | 膜工具集成 | 社区 | 综合 |
|---|---|---|---|---|---|---|---|
| **GROMACS** | 最高 (~57% of engine-identified deposits; 主导 GPCRmd/近期 JCIM GPCR 论文)[1][8] | 官方 membrane-protein tutorial + JPCB 2024 零基础入门系列; CHARMM-GUI 直接出 `.top/.itp`[2][9] | LGPL 2.1, 完全开源, 商业亦免费[3] | 中高; RTX 4090 上中等体系百-数百 ns/day 量级; CPU 敏感[4] | 一流; CHARMM-GUI 原生支持 | BioExcel 论坛 + GitLab issues 活跃[5] | **首选** |
| **OpenMM** | 上升中；2024 OpenMMDL 论文推广 protein-ligand 流程[6] | 极平缓；Python API，Cookbook + 2024 workshop; `addMembrane()` 一行建膜[7] | MIT + LGPL，完全开源 | 单 GPU 与 GROMACS 相当；小体系甚至更快；8.5.1 (2026-04)[11] | CHARMM-GUI 原生 PSF + OPM+`addMembrane`[7] | GitHub 1.8k stars, 400 open issues；Chodera lab 推动[11] | **并列首选** |
| **AMBER** | 中；在脂质/配体自由能类 GPCR 研究中常见 | 中等；AmberTools 免费；Amber Book 需付费[12] | AmberTools = GPL 免费；pmemd 源码对学术 US$0 申请[12] | 单 GPU 最高；RTX 4090 DHFR ≈ 1639, FactorIX ≈ 466, STMV ≈ 79 ns/day[10] | CHARMM-GUI 出 `.prmtop/.inpcrd`；PACKMOL-Memgen 官方首选 | 邮件列表强，GitHub 能见度低 | 备选 |
| **NAMD** | 中（历史膜蛋白占比高，近年被 GROMACS 蚕食） | 中等；UIUC 经典 tutorial；tcl config 风格 | 免费学术，Illinois 许可 | NAMD 3.0 GPU-resident 比 2.x 快 2×[13] | CHARMM-GUI 原生；VMD 配套 | UIUC 邮件列表活跃 | 备选 |
| **Desmond** | 低–中；学术版存在但商业版主导制药界 | 陡；强依赖 Maestro GUI[14][15] | 免费学术版, **结果必须公开披露**, 商业转化需补差价[14][15] | 未在 2024 公开基准中直接对比 | Maestro 自有膜 setup | 社区小，闭源 | **不推荐** |

### 1.2 推荐（Top 2 + tradeoffs）

**首选：GROMACS**。原因：(a) MDverse 大规模调研显示 GROMACS 占 engine-identified 轨迹约 57%（87,204 文件）[1]，最新 *Nat Commun* 2025 GPCR MD 数据集及近年 JCIM GPCR 论文亦以 GROMACS 为主[8][17]。(b) 膜蛋白官方教程成熟、CHARMM-GUI 一键出 `.top/.itp`，**对零基础团队 1–2 周可跑通一个 7-TM 体系**[2][9]。(c) LGPL 完全开源，iGEM wiki freeze 无 license 风险[3]。**风险**：CPU 性能敏感；RTX 4090 单卡对 ~100k 原子膜体系约数百 ns/day 量级，5 个月跑 Top 6 × 3 复制 × 200 ns 需排队规划。

**并列首选：OpenMM**。原因：(a) Python-first，对零基础团队 onboarding 曲线最平缓（Cookbook + 2024 workshop + `Modeller.addMembrane()` 一行建膜）[7][11]；(b) 与 CHARMM-GUI、OpenFF、ProLIF 生态最亲和；(c) MIT/LGPL 完全开源[11]。**风险**：GPCR 历史文献量少于 GROMACS，答辩时 reviewer 可能期望"标准工具"。

**混合策略建议**：CHARMM-GUI 生成 GROMACS + OpenMM 双格式输入；主生产跑 GROMACS（文献可比性），补充跑 OpenMM（快速原型 + Python 分析链接 ProLIF）。两者在 CHARMM36m 下能量可互校验[16]。

### 1.3 警示

- **Desmond**：学术许可要求结果**公开披露**且后续不得用于未披露的商业用途[14][15]。闭源 + 对 iGEM 复现不友好。
- **AMBER pmemd.cuda**：虽免费，但注册流程 + 许可文本有学术限制；脂质力场 (Lipid21) + ascaroside 参数化需走 GAFF2/antechamber，boilerplate 比 GROMACS+CHARMM36m 多一步[12]。
- **NAMD 3.0 GPU-resident**：NAMD 3.0.1 曾出现 pressure tensor bug 影响膜体系面积/脂质[13]；tcl config 风格与现代 Python 栈脱节。
- **GROMACS RTX 4090 陷阱**：社区报告低利用率 issue，需要 `-update gpu -bonded gpu -pme gpu` 并保证 CPU ≥ 8 核[4]。
- **pmemd.cuda DHFR 数字 ≠ GPCR 数字**：官方 1639 ns/day 是 23k 原子裸 DHFR；膜 GPCR (~100k 原子) 实际掉到 ~200–400 ns/day 量级[10]。

### 1.4 iGEM 团队历史使用

iGEM 过去 3 年的 MD 使用以 **GROMACS 为压倒性主流**：NAU-CHINA 2023/2024、PekingHSC 2023/2024（GROMACS + PLUMED REMD）、HKU-HongKong 2024（GROMACS + MM/GBSA）、Genehackers 2024、UBC-Vancouver 2023、IISER-Pune2 2022 均用 GROMACS[18][19][20]。Tsinghua 2024 muscone 项目涉及 GPCR 通路 ODE 但未做全原子 MD[21]。

**明确的"iGEM 团队做真菌/7-TM GPCR 全原子 MD"先例：insufficient data found**——未检索到同时满足"iGEM wiki + 膜 GPCR + 显式脂质双层 + ns 级全原子 MD"的公开案例。reviewer 参照物稀缺（需自证方法合理），同时也是本项目的方法学亮点。

### 1.5 引用来源

1. [MDverse: Shedding Light on the Dark Matter of MD Simulations (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11364437/)
2. [GROMACS Tutorial: Membrane Protein (官方)](https://tutorials.gromacs.org/docs/membrane-protein.html)
3. [GROMACS Preface & License (manual 2024.3)](https://manual.gromacs.org/2024.3/reference-manual/preface.html)
4. [Low GROMACS performance on RTX 4090 (forum)](https://gromacs.bioexcel.eu/t/low-gromacs-performance-on-rtx-4090/6083)
5. [GROMACS GitHub mirror](https://github.com/gromacs/gromacs)
6. [OpenMMDL: Simplifying Protein–Ligand Systems in OpenMM (JCIM 2024)](https://pubs.acs.org/doi/10.1021/acs.jcim.4c02158)
7. [OpenMM Cookbook: Getting Started](https://openmm.github.io/openmm-cookbook/latest/notebooks/tutorials/getting_started.html)
8. [Large scale investigation of GPCR MD data (Nat Commun 2025)](https://www.nature.com/articles/s41467-025-57034-y)
9. [CHARMM-GUI Input Generator (JCTC 2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4712441/)
10. [AMBER pmemd.cuda GPU Performance](https://ambermd.org/GPUPerformance.php)
11. [OpenMM GitHub](https://github.com/openmm/openmm)
12. [AMBER 24 License & Download](https://ambermd.org/GetAmber.php)
13. [NAMD 3.0 Performance (UIUC)](https://www.ks.uiuc.edu/Research/namd/benchmarks/)
14. [Schrödinger EULA](https://www.schrodinger.com/eula/)
15. [Desmond academic free version (TAMU HPRC)](https://hprc.tamu.edu/kb/Software/Desmond/)
16. [Introductory Tutorials for GROMACS Protein Dynamics (JPCB 2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11457149/)
17. [pKa Calculations of GPCRs (JCIM 2024)](https://pubs.acs.org/doi/10.1021/acs.jcim.4c01125)
18. [NAU-CHINA iGEM 2023 Molecular Modeling](https://2023.igem.wiki/nau-china/molevular-modeling)
19. [PekingHSC iGEM 2024 Molecular Dynamics](https://2024.igem.wiki/pekinghsc/md)
20. [HKU-HongKong iGEM 2024 Modeling](https://2024.igem.wiki/hku-hongkong/modeling)
21. [Tsinghua iGEM 2024 muscone Model](https://2024.igem.wiki/tsinghua/model)

---

## 2. 力场选型

### 2.1 蛋白力场对比表

| 力场 | 2023-2026 GPCR 使用 | MD 软件兼容性 | 脂质参数配套 | 已知坑 | 综合 |
|---|---|---|---|---|---|
| **CHARMM36m** | 主流；CHARMM-GUI 默认为 GPCR+POPC 体系提供 C36m+CGenFF+C36-lipid 一键式 workflow[^1][^4]；CB1/CB2 等 class A GPCR MD 普遍采用[^10] | GROMACS/OpenMM/NAMD 均支持；OpenMM 仅支持 potential-based switching（非 C36 推荐的 force-based）[^2]；`charmm2gmx` 自动化移植[^2] | 与 CHARMM36 lipid（POPC/POPE/POPS/胆固醇/**ergosterol**）原生配套[^4] | IDP 偏紧致；但对折叠蛋白差异很小；αL helix 过采样从 20%→5.7%[^7] | **首选** |
| **Amber ff19SB** | 2024 GPCR FEP（A2A/β1/δ-opioid/CXCR4）采用 ff19SB+GAFF2+Lipid21+OPC via CHARMM-GUI[^6][^8]；总体使用量少于 C36m | AMBER 原生；NAMD 官方支持；**GROMACS 移植有坑**：ParmEd 不能正确转换 ff19SB 的 per-residue CMAP，会静默损失 ff19SB 相对 ff14SB 的核心改进[^3] | 官方 Lipid21 (2022 JCTC)；POPC 面/脂与实验吻合[^5] | 必须用 OPC 水模型才能发挥作用，与 TIP3P 组合会退化；ParmEd→GROMACS CMAP bug | **次选**（做 alchemical FEP 时） |
| **OPLS-AA/M** | 2022 JCTC 才专门为 GPCR+膜蛋白扩展[^11]；2023-2026 GPCR MD 占比低 | 通过 LigParGen/Jorgensen GROMACS port[^11][^12] | PL/胆固醇扭转新扩展；膜力场生态远不如 C36 lipid/Lipid21 | GROMACS 支持依赖第三方 port；社区膜蛋白教程/案例少 | 不推荐 |

**CHARMM36 vs CHARMM36m**：C36m 只改 CMAP（αL 过采样 20%→5.7%）和 Arg-Asp/Glu 盐桥的 LJ 参数，对 7-TM GPCR 差异小但只会更好——**更关键的是对本项目核心科学问题"ARG 胍基-ascaroside 羧基盐桥"，C36m 的盐桥 LJ 修正正好对症**[^7]。**结论：无理由选 C36，直接 C36m**。

**POPC 脂质力场选择**：C36 lipid 与实验吻合度高（CHARMM-GUI 标配），Lipid21 性能相当[^5]，Slipids 2020 重优化对头基顺序参数改善[^9]。**警告**：一项 β2AR/POPC 对比研究发现**不同脂质力场会戏剧性改变 GPCR ionic lock 开闭动力学**（R3.50-E6.30）即使盐桥远离脂质界面[^9]——这对评估 Gpr3 ARG-ascaroside 盐桥稳定性是**警告**：脂质力场本身就能引入 ns 级别"假信号"。

### 2.2 配体参数化管线对比表

| 工具 | 糖环支持 | 糖脂配体支持 (ascaroside 类) | 工作流成熟度 | 诊断工具 | 综合 |
|---|---|---|---|---|---|
| **GAFF2 (Antechamber)** | 可做，常见做法是糖部分改用 **GLYCAM**[^13] | 可行但需 antechamber + parmchk2 + 手动合并 GLYCAM 片段；α-L-ascarylose 是 deoxy pyranose，未必被 GLYCAM 直接 cover | 极成熟，AmberTools 标准 | parmchk2 报缺失参数；无正式 penalty score | 与 ff19SB+Lipid21 同源；糖环保真度需验证 |
| **CGenFF (ParamChem / SilcsBio)** | penalty score 定量诊断。pyranose 环社区报告常见高 penalty (>50 警告，>200 强制优化)[^14] | 糖环风险已知；C7 脂肪酸链属于舒适区；**羧基电荷对 ARG-COO⁻ 盐桥是关键**，penalty>10 的 COO⁻ 相关 charge/dihedral 需 LSFitPar QM 重拟合 | 成熟。CHARMM-GUI Ligand Reader & Modeler 一键生成 | penalty 分数是黄金标准 | **首选，但需预算 1-2 天做糖环 penalty 审计** |
| **OpenFF 2.x (Sage)** | 覆盖 drug-like 空间，**无糖脂 benchmark**[^15] | 未经糖脂验证；SMIRNOFF 版 ff14SB 仅 proof-of-concept[^16] | Python-first 但对零基础陡 | 无 penalty 诊断，需自己做 QM validation | **暂不推荐用于 ascaroside 正式 runs** |

### 2.3 推荐组合（蛋白 + 配体 + 脂质）

**组合 A（主力推荐，CHARMM 栈）**：**CHARMM36m + CGenFF + CHARMM36 lipid (POPC) + TIP3P**

这是 CHARMM-GUI Membrane Builder + Ligand Reader & Modeler 的默认路径，也是 2023-2025 class A GPCR + 有机小分子配体 MD 的主流组合（如 CB1 与 AEA/anandamide）[^10]。**优势**：(a) 工具链一键式降低团队门槛；(b) C36m 的 Arg 盐桥修正正好对症 V138R 假说；(c) GROMACS/OpenMM/NAMD 都能跑[^2][^4]。

**组合 B（备选，AMBER 栈）**：**ff19SB + GAFF2 + Lipid21 + OPC**

2024 Mondal 等 alchemical FEP 基准采用此栈[^6][^8]。**优势**：做结合自由能（TI）时 AMBER GPU-TI 成熟度高于 GROMACS。**劣势**：ff19SB 要用 OPC 而非 TIP3P；Lipid21+ff19SB 的 GPCR 经验少于 C36m 栈；GROMACS 走 ParmEd 有 CMAP bug[^3]。

**组合 C（不推荐，仅对照）**：OPLS-AA/M 栈——GPCR 扩展刚出[^11]，膜生态弱，团队零基础不建议。

### 2.4 ascaroside 专题

**直接证据不足**：WebSearch 未检索到任何公开发表的文献对 ascr#3/ascr#18 做 MD 模拟，也未看到针对 α-L-ascarylose 糖环的专门力场参数化工作。最接近参照是 CB1 的 anandamide（N-acyl ethanolamine，长链脂肪酸+极性头）——该类统一使用 CHARMM36 + CGenFF via CHARMM-GUI[^10]。

**结论**：ascaroside MD 对本团队是**新工作**，参数要自己做并必须审计。具体建议：
- 用 CGenFF 参数化 ascr#18 完整分子，对 α-L-ascarylose 环上 penalty>50 的 charge/bond/dihedral 做 QM 参考（B3LYP/6-31G* + LSFitPar 回拟）[^14]
- 对 C7 末端羧基及其旋转异构体专门审计（V138R 盐桥药效团）
- Sanity check：把 ascr#18 放进水盒子跑 100 ns，比较 α-L-ascarylose 环的 ⁴C₁/¹C₄ 椅式分布
- 如无 NMR：跑 GAFF2+GLYCAM hybrid 作为独立第二套参数 cross-check

### 2.5 警示与已知坑

- **ff19SB → GROMACS ParmEd CMAP bug**[^3]：走 AMBER 栈请用 AMBER 原生或 `gmx_ffconv` 并验证每个残基
- **OpenMM + CHARMM36 switching**：OpenMM 不支持 force-based switching，与 CHARMM 原生有 kJ 级偏差[^2]；稳定性可接受，FEP 需谨慎
- **C36m 对 IDP 仍偏紧致**：Gpr3 ICL3 等长 IDR 的采样要做 cluster/RMSF 分析
- **ff19SB 必须配 OPC**：默认 TIP3P 会退化改进[^1]
- **CGenFF 高 penalty 糖环**：pyranose 常见问题[^14]；不审计 = 垃圾进垃圾出
- **脂质力场影响 ionic lock 动力学**[^9]：脂质力场本身就是受控变量
- **CHARMM-GUI 是黑盒**：git commit 全部 `toppar/` + `step*.inp` 输入防止不可复现
- **不要跨栈混搭**：CGenFF 配体 ≠ ff19SB 蛋白 prmtop；Sage OpenFF 配体 + ff14SB 蛋白官方明确 proof-of-concept[^16]

### 2.6 引用来源

[^1]: [CHARMM-GUI high-throughput simulator for protein-ligand with different force fields (Guterres 2022)](https://onlinelibrary.wiley.com/doi/full/10.1002/pro.4413)
[^2]: [charmm2gmx: Automated Method to Port CHARMM to GROMACS (JCIM 2023)](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00860)
[^3]: [CMAPTYPES bug converting ff19SB to GROMACS (ParmEd #1292)](https://github.com/ParmEd/ParmEd/issues/1292) + [gmx_ffconv (JCIM 2024)](https://pubs.acs.org/doi/10.1021/acs.jcim.5c02200)
[^4]: [CHARMM-GUI Membrane Builder Past/Current/Future (JCTC 2023)](https://pubs.acs.org/doi/10.1021/acs.jctc.2c01246)
[^5]: [Lipid21: Complex Lipid Membrane Simulations with AMBER (JCTC 2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9007451/)
[^6]: [Ligand Binding Affinity Prediction for Membrane Proteins with Alchemical FEP (JCIM 2024)](https://pubs.acs.org/doi/10.1021/acs.jcim.4c00764)
[^7]: [CHARMM36m: Improved FF for Folded and IDPs (Nat Methods 2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5199616/)
[^8]: [AMBER-Membrane_protein_tutorial (callumjd GitHub)](https://github.com/callumjd/AMBER-Membrane_protein_tutorial)
[^9]: [Influence of Lipid Bilayer on GPCR Structure (BCSJ 2021)](https://academic.oup.com/bcsj/article/94/10/2569/7334943) + [Slipids 2020 headgroup (JPCB)](https://pubs.acs.org/doi/10.1021/acs.jpcb.0c06386)
[^10]: [CB1R Activation MD (PMC9963961)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9963961/) + [CB1 MD (Front Mol Biosci 2022)](https://www.frontiersin.org/articles/10.3389/fmolb.2022.860035/full)
[^11]: [OPLS-AA/M for GPCRs and Membrane Proteins (JCTC 2022)](https://pubs.acs.org/doi/10.1021/acs.jctc.2c00015)
[^12]: [Jorgensen Lab OPLS-AA/M for Proteins](https://zarbi.chem.yale.edu/oplsaam.html)
[^13]: [Glycomimetics Design Pipeline (JCIM 2025)](https://pubs.acs.org/doi/10.1021/acs.jcim.5c02282)
[^14]: [CGenFF Program — SilcsBio Guide](https://docs.silcsbio.com/2024/cgenff/usage.html) + [Automation of CGenFF I (PMC3528824)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3528824/)
[^15]: [Open Force Field 2.0.0 Sage (JCTC 2023)](https://pubs.acs.org/doi/10.1021/acs.jctc.3c00039)
[^16]: [OpenFF Toolkit Protein-ligand-water](https://docs.openforcefield.org/en/latest/examples/openforcefield/openff-interchange/protein_ligand/protein_ligand.html)

---

## 3. 膜体系构建

### 3.1 工具对比表

| 工具 | 学习曲线 | 输出兼容性 | GPCR TM 对齐 | 授权 | 2023-2026 使用 | 综合 |
|---|---|---|---|---|---|---|
| **CHARMM-GUI Membrane Builder** | 低（Web GUI, 5-9 步向导）[1][4] | 最广：Amber/CHARMM/Desmond/GENESIS/**GROMACS**/LAMMPS/NAMD/**OpenMM**/TINKER[1] | 原生调用 **PPM 2.0** 自动对齐 Z 轴；可从 **OPM** 拉已定向结构[4][5] | 免费，学术邮箱注册[6] | GPCR MD 事实标准[8][12] | **推荐首选** |
| **PACKMOL-Memgen** | 中（CLI + 大量 flag，tutorial38）[2][3] | 仅 Amber (.pdb/.top/.crd)，**无 GROMACS/OpenMM 输出**[2] | 内部用 **memembed** 粗定向，不如 PPM 严谨[2] | 免费，AmberTools ≥23 分发[2][3] | Amber 用户群常用 | 备选（Amber pipeline） |
| **GROMACS membed** | 高（需预构建纯膜 + topology）[7][9] | 仅 GROMACS 原生 | 无 OPM/PPM 集成，靠"压扁再长回"消 clash[7][9] | GROMACS 内置 | 使用频率下降；官方文档已推荐 CHARMM-GUI 替代[9][13] | **不推荐新手** |

### 3.2 推荐

**首选：CHARMM-GUI Membrane Builder**。对零基础 iGEM 团队几乎是唯一能在 5 个月窗口跑通"PDB → MD-ready"的选项：

1. Web 向导 5-9 步完成全流程，每步可视化回退[1][4]
2. 内置 PPM 2.0 自动把 TM helix 对齐膜法向 Z 轴——对 AlphaFold3 预测的 7-TM GPCR 尤其关键（AlphaFold 结构无膜取向先验）[5][10]
3. 输出覆盖 GROMACS/OpenMM/AMBER/NAMD 全部候选[1]
4. 2024 年 A2A、Class B1 GPCR MD 大规模研究直接使用[8][12]

**备选：PACKMOL-Memgen**——仅当团队坚定走 Amber/Lipid21 pipeline。优势是脚本化、AmberTools tutorial38 + Callum Dickson GitHub 教学仓库质量高[2][3]。劣势：不出 GROMACS/OpenMM，定向依赖 memembed，AlphaFold 兜底弱。

**不推荐：g_membed**——GROMACS 官方 how-to 已推荐 CHARMM-GUI 替代[7][13]。

### 3.3 膜组分选择

**近年 GPCR MD 默认仍是 POPC，但加 10-30 mol% 胆固醇正成为"生物相关性"新底线**。2024 Biochemistry 综述明确 Class A GPCR 的胆固醇调控功能性[8][11][14]，Class B1 GPCR 2025 研究以 POPC:CHOL 为起点[12]。POPC:POPE 多见于细菌，对真核 GPCR 不是主流。

**真菌 GPCR 关键差别**：真菌质膜以**麦角固醇 (ergosterol)** 而非胆固醇为主要甾醇，磷脂以 PC/PE/PI/PS 为主[15][16]。**CHARMM36 已包含 ergosterol 参数，CHARMM-GUI Membrane Builder 原生支持**，并有专门的酵母膜应用论文[4][15]。

**本项目具体建议（iGEM + 5 月窗口 + 零基础）**：

- **第一轮主体系：纯 POPC 膜**（benchmark、易收敛、对照大多数 GPCR MD 文献）
- **第二轮（如有余力）：POPC:ergosterol (80:20)** 作为"真菌质膜近似"敏感性验证
- **不要在第一轮就上**复杂的 4-5 组分酵母质膜（PC/PE/PI/PS/ergosterol）——每 leaflet 数百脂质、5-10× 更长平衡时间，iGEM 时间预算不可承受[4][15][16]

### 3.4 AlphaFold3 结构 → 膜体系工作流

- **Step 0 结构净化**：剪掉 pLDDT<70 的 N/C 端无结构尾巴和 flexible ICL/ECL 环——CHARMM-GUI 会把这些当有序处理，常导致步骤 4 报 "undefined coordinate"[17][10]
- **Step 1 补全与质子化**：先过 CHARMM-GUI **PDB Reader & Manipulator**，用 IC 表补齐缺失原子/氢[17]
- **Step 2 定向**：进入 Membrane Builder 第一步即点 **"Run PPM 2.0"**——不要信任 AlphaFold 原坐标方向[5][10]
- **Step 3 膜搭建**：Rectangular box、POPC、17.5 Å 水层、0.15 M KCl、上下叶对称；"by ratio" 估算→"by number" 微调避免 leaflet 面积不匹配[4]
- **Step 4 输出**：选 **GROMACS + CHARMM36m**（官方 CHARMM-GUI→GROMACS workflow 成熟度最高）；OpenMM 是可行 plan B[1][13]
- **Step 5 平衡**：直接用 CHARMM-GUI 生成的 6 步 NVT/NPT 逐步释放约束脚本（step6.1-6.6）[4]

### 3.5 警示

- **不要跳过 PPM**：AlphaFold3 原坐标方向任意，跳过 PPM 会在 production 阶段才发现 TM helix 倾角 30°+ 灾难[5][10]
- **AlphaFold 活性态偏向**：AF 预测对 inactive state 明显更准，active state 容易 TM6 不打开[10]；报告需明确声明"基于 inactive-like 预测结构"
- **CHARMM-GUI 注册延迟**：学术账号审批可能延迟数小时-一天[6]，**提前一周注册**
- **g_membed 已边缘化**：GROMACS 官方 how-to 已推荐 CHARMM-GUI[7][13]
- **PACKMOL-Memgen ≠ GROMACS 直出**：后期切 GROMACS 要过 parmed/acpype 转换[2]
- **ergosterol ≠ cholesterol**：CHARMM36 里两者参数不同，对膜厚/order parameter/侧向扩散影响定量不同[15][16]
- **真菌膜不要第一轮做复杂配方**：多组分非对称酵母质膜平衡时间数百 ns-μs[4][15]

### 3.6 引用来源

1. [CHARMM-GUI Membrane Builder: Past/Current/Future (JCTC 2023, PMC10174225)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10174225/)
2. [PACKMOL-Memgen (JCIM 2019)](https://pubs.acs.org/doi/abs/10.1021/acs.jcim.9b00269)
3. [AmberTools Tutorial 38: Membrane System Setup](https://ambermd.org/tutorials/advanced/tutorial38/index.php)
4. [Preparing Membrane Proteins for Simulation Using CHARMM-GUI (PMC8158057)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8158057/)
5. [Building protein membrane system using CHARMM-GUI (Compchems)](https://www.compchems.com/building-a-protein-membrane-system-using-charmm-gui/)
6. [CHARMM-GUI 官方账号提示 (x.com)](https://x.com/CharmmGui/status/1375899837799956483)
7. [Running Membrane Simulations in GROMACS (manual 2026.1)](https://manual.gromacs.org/current/how-to/special.html)
8. [Effects of Membrane Cholesterol on Class A GPCRs (Biochemistry 2024/25)](https://pubs.acs.org/doi/10.1021/acs.biochem.5c00145)
9. [g_membed (Wolf et al. 2010, PubMed 20336801)](https://pubmed.ncbi.nlm.nih.gov/20336801/)
10. [Characterizing GPCR Conformational States with AlphaFold (arXiv 2502.17628)](https://arxiv.org/html/2502.17628v1)
11. [Dual Mechanisms of Cholesterol-GPCR Interactions (PMC10330489)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10330489/)
12. [Human Class B1 GPCR Modulation by Plasma Membrane Lipids (PMC12936092)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12936092/)
13. [Memprot.GPCR-ModSim (Bioinformatics 2024, btae662, DOI 10.1093/bioinformatics/btae662)](https://doi.org/10.1093/bioinformatics/btae662)
14. [Split Membrane model on A2A (JCIM 2024)](https://pubs.acs.org/doi/full/10.1021/acs.jcim.4c01664)
15. [CHARMM-GUI Yeast Membranes (PMC2711372)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2711372/)
16. [Ergosterol effect on fungal membrane (PubMed 29122611)](https://pubmed.ncbi.nlm.nih.gov/29122611/)
17. [CHARMM-GUI PDB Reader Q (forum t=9427)](https://forums-academiccharmm.org/viewtopic.php?t=9427)

---

## 4. 整合推荐栈

基于 3 维度一致性结论 + 本项目科学问题匹配度：

### 4.1 生产栈（Production Stack）

| 层 | 选择 | 一句话理由 |
|---|---|---|
| **MD 引擎** | GROMACS（最新稳定版）| 2023-2026 GPCR MD 文献占比 ~57%；iGEM 团队压倒性主流；LGPL 开源 |
| **蛋白力场** | CHARMM36m | Arg-Asp/Glu 盐桥 LJ 修正对症 V138R 胍基-羧基假说 |
| **配体参数化** | CGenFF（via CHARMM-GUI Ligand Reader & Modeler）| penalty score 定量诊断；与 C36m 同源；1-2 天糖环审计必做 |
| **脂质力场** | CHARMM36 lipid | 与 C36m 原生配套；POPC + ergosterol 均原生支持 |
| **水 + 离子** | TIP3P + 0.15 M KCl | C36m 默认；与 CHARMM-GUI 流程无缝 |
| **膜构建** | CHARMM-GUI Membrane Builder + PPM 2.0 | 唯一满足零基础 + 5 月窗口 + 全 MD 引擎输出的选项 |
| **膜组分（第一轮）** | 纯 POPC | Benchmark；易收敛；对照主流 GPCR MD |
| **膜组分（第二轮）** | POPC:ergosterol (80:20) | 真菌质膜近似；CHARMM36 原生 ergosterol |
| **分析工具** | MDAnalysis + mdtraj + ProLIF（链接上游 IFP）| Python-first 与 OpenMM 生态亲和 |

### 4.2 原型/备份栈

- **OpenMM**：Python 原型 + 快速 sanity check + 与 ProLIF/mdtraj 分析管道直连；CHARMM-GUI 同时出双格式输入
- **AMBER ff19SB + GAFF2 + Lipid21 + OPC**：仅当后期做 alchemical FEP 时切换

### 4.3 淘汰选项（不考虑）

- Desmond（闭源 + 公开披露条款）
- NAMD（工具链脱节）
- g_membed（官方已弃用）
- OPLS-AA/M（膜生态弱，案例少）
- OpenFF Sage 做 ascaroside 生产 runs（糖脂 benchmark 缺失）

---

## 5. 关键风险与前置工作

排序按严重程度：

1. **ascaroside CGenFF 糖环 penalty 审计** ⭐⭐⭐
   - 不审计直接跑 = V138R 盐桥占比数字不可信
   - 预算 1-2 天：ParamChem 生成 → 扫描 penalty>50 的 charge/dihedral → QM (B3LYP/6-31G*) 参考 → LSFitPar 回拟
   - 重点：α-L-ascarylose 环的 ⁴C₁/¹C₄ 椅式稳定性 + C7 末端羧基 charge

2. **AlphaFold3 结构必须过 PPM 2.0 对齐** ⭐⭐⭐
   - 跳过会在 production 阶段发现 TM 倾角 30°+ 灾难
   - 顺带明确声明"基于 inactive-like 预测"

3. **脂质力场本身引入 ionic lock 假信号** ⭐⭐
   - β2AR+POPC 对比研究显示不同脂质力场让 R-E ionic lock 动力学完全不同
   - 对策：锁定 CHARMM36 lipid，不中途切换；若要对比只换同一家族内版本

4. **CHARMM-GUI 学术账号审批** ⭐
   - 可能延迟数小时-一天
   - **提前一周注册**，不要卡在里程碑前一天

5. **RTX 4090 / 一般 GPU 上 GROMACS 性能陷阱** ⭐
   - 需 `-update gpu -bonded gpu -pme gpu` + CPU ≥ 8 核
   - 服务器配置确认后做一次水盒子 benchmark

---

## 6. 时间尺度与复制数（第二轮）

### 6.1 近 3 年 GPCR+配体 MD 生产时长分布

2023–2026 GPCR+ligand 全原子 MD 的主流生产时长已从早期 50–100 ns 升到 **200–500 ns × 3 replicas** 作为"标准交付"。最具代表性的基线是 2025 Nature Communications 的大规模 GPCRmd-2 工作，对每个系统做 **3 × 500 ns = 1.5 μs**，累计 556.5 μs ([Mayol et al., Nat Commun 2025](https://www.nature.com/articles/s41467-025-57034-y))。同一协议可追溯到 2021 PLOS Comp Biol GPCR refinement（3 × 500 ns，CHARMM36m + POPC + TIP3）([Heo & Feig, PLOS CB 2021](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008936)) — **"3 × 500 ns"** 已固化为 class A GPCR refinement 惯例。

**≥1 μs 单 replica** 在 drug-design 类研究也常见：2024 Nat Commun CB1 + THC 类似物用 **1000 ns single-run** ([Kumar et al., Nat Commun 2024](https://www.nature.com/articles/s41467-024-55808-4))；μOR 最新 Nature 2025 用 GROMACS 2024.5 + CHARMM36 ([Qu et al., Nature 2025](https://www.nature.com/articles/s41586-025-09677-6))；β2AR biased agonism 采 **12 × 100 ns = 1.2 μs** 切分式 ([Fleetwood et al., JCIM 2024](https://pubs.acs.org/doi/10.1021/acs.jcim.3c01481))；A2A 早期 **600 ns**（100 ns eq + 500 ns analysis）([Bruzzese et al., Sci Rep 2019](https://www.nature.com/articles/s41598-019-41980-x))。

| 论文 | 受体 | 生产时长 | Replicas | 软件/力场 |
|---|---|---|---|---|
| [Mayol Nat Commun 2025](https://www.nature.com/articles/s41467-025-57034-y) | 371 class A/B/C GPCR | 500 ns | **3** | ACEMD, CHARMM36, POPC |
| [Heo & Feig PLOS CB 2021](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008936) | GPCR homology | 500 ns | **3** | GROMACS, CHARMM36m |
| [Kumar Nat Commun 2024](https://www.nature.com/articles/s41467-024-55808-4) | CB1 | 1000 ns | 1 | GROMACS, CHARMM36m |
| [Qu Nature 2025](https://www.nature.com/articles/s41586-025-09677-6) | μOR | ≥500 ns | — | GROMACS 2024.5, CHARMM36 |
| [Fleetwood JCIM 2024](https://pubs.acs.org/doi/10.1021/acs.jcim.3c01481) | β2AR biased | 100 ns | **12** | CHARMM36m |
| [Bruzzese Sci Rep 2019](https://www.nature.com/articles/s41598-019-41980-x) | A2A | 500 ns (+100 ns eq) | ≥3 | CHARMM36 |

**档次分布**：50 ns = 过时；100 ns × 3–5 = 方法论 refinement；200 ns = 快速筛选；**500 ns × 3 = 发表级主流**；1 μs+ = top-journal drug design / activation 机理。

### 6.2 稳定性分析的最小可接受时长

从方法论文献归纳的最小地板：**80–100 ns per replica × ≥ 3 replicas**。Heo & Feig 明确建议"multiple replicas around 100–200 ns is suitable for model refinement"，且"100 ns 内才均匀分布信息" ([PLOS CB 2021](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008936))。ligand pose drift 观察上"前 50 ns 爬升到 3–4 Å 然后 plateau" — **<50 ns 是 equilibration artifact，不能作为稳定性证据**。对 salt bridge occupancy / HBond lifetime，2024 OpenMMDL 和 Galaxy HTMD 把 100 ns+ 作为可分析下限 ([Schroeder JCIM 2024](https://pubs.acs.org/doi/10.1021/acs.jcim.4c02158)，[Galaxy HTMD](https://training.galaxyproject.org/training-material/topics/computational-chemistry/tutorials/htmd-analysis/tutorial.html))。

**一句话共识**：对 WT vs mutant salt-bridge fraction 差异，单 replica <100 ns 无说服力；<3 replicas 无法报 p 值。**200 ns × 3 是"可审稿"地板，500 ns × 3 是"舒服"中位数**。

### 6.3 复制数与统计显著性

单 replica 不够用已是审稿常识。主流做法：
- **Refinement / dynamics characterization**：3 × 500 ns（GPCRmd-2 协议）
- **WT vs mutant 对照**：三因子 ANOVA 或 Welch t-test（p < 0.001 / 0.005）配合 3–5 seeds ([Pándy-Szekeres Sci Rep 2020](https://www.nature.com/articles/s41598-020-77072-4))
- **Activation transitions**：3 × 20 μs (Anton 级)，iGEM 不可及
- **Enhanced sampling**：LiGaMD 5 × 4500 ns ([Miao JCTC 2020](https://pubs.acs.org/doi/10.1021/acs.jctc.0c00395))

**本项目场景**（盐桥 fraction V138R vs WT）：≥ 3 seeds × ≥ 200 ns 用于 Welch t-test / Mann-Whitney U；bootstrap CI 需 ≥ 5 seeds。effect size 大（0.1→0.8）时 3 seeds 即显著；接近阈值（0.4 vs 0.6）必须 5 seeds。

### 6.4 Enhanced sampling 的必要性

**对本项目不必要，但可作加速器**。GaMD / metadynamics / REST2 主解决 μs–ms 罕见事件（ligand binding、activation transition）；本项目 3 个科学问题（盐桥占比、pose drift、RMSD/RMSF）本质是 **bound-state 局部稳定性**，unbiased MD 200–500 ns 可直接读出 ([Ribeiro Curr Opin Struct Biol 2019](https://pubmed.ncbi.nlm.nih.gov/31100549/))。

**唯一值得引入的是 BPMD**（Schrödinger 式 10 × 10 ns metadynamics）作为 Top-6 mutant 快速 pre-filter：10 ns × 10 × 6 = 600 ns 几天跑完，从 6 个里选 3 个进入深度 unbiased MD ([Clark JCIM 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7145342/))。LiGaMD2 需 μs 量级，对 5 月窗口过重。

### 6.5 性能估算

**权威 benchmark**：NHR@FAU 2024 GROMACS 2024.1，**80,289-atom protein-in-membrane** 单卡 ns/day ([NHR@FAU 2024](https://hpc.fau.de/2024/08/13/gromacs-2024-1-on-brand-new-gpgpus/)):

| GPU | ns/day @ 80k | ~120k 缩放 | 500 ns 单 replica |
|---|---|---|---|
| A100 80GB | **265.8** | ~175 | ~3 天 |
| H100 | 400.4 | ~267 | ~1.9 天 |
| L40 | 463.3 | ~309 | ~1.6 天 |
| L40S | **472.4** | ~315 | ~1.6 天 |
| RTX 4090 | ≈ A100 ([Exxact](https://www.exxactcorp.com/blog/benchmarks/gromacs-gpu-benchmark-and-hardware-recommendations)) | ~200 | ~2.5 天 |

命令：`gmx mdrun -nb gpu -pme gpu -bonded gpu -update gpu -ntmpi 1 -ntomp 16`。CHARMM-GUI 默认 2 fs timestep；HMR (4 fs) 可额外 ×1.6–1.8，但对 CHARMM36m + CGenFF 首次交付**不推荐** ([Guterres Protein Sci 2022](https://onlinelibrary.wiley.com/doi/full/10.1002/pro.4413))。

### 6.6 本项目采样方案（核心建议）

**体系清单**：WT + Top 6 mutant × {apo, holo} = 14 systems；仅 holo（问题 1–3 都是 bound state）= **7 systems**。

| 方案 | 体系数 | 时长/rep | Reps | 总 ns | 单 A100 天数 | 说明 |
|---|---|---|---|---|---|---|
| **最小 MVP** | 7 holo | 200 ns | 3 | 4200 | ~24 GPU-day | t-test 可做；前 50 ns 当 eq 丢掉 |
| **标准** | 7 holo + 1 WT-apo | 300 ns | 3 | 7200 | ~41 GPU-day | p 值稳定，bootstrap CI 可做 |
| **理想** | 14 (holo + apo) | 500 ns | 3 | 21000 | ~120 GPU-day | 匹配 GPCRmd-2 协议 |
| **激进** | 14 | 1 μs | 3 | 42000 | ~240 GPU-day | 5 月窗口不推荐 |

**取舍逻辑**：
1. 盐桥 fraction（V138R 问题 1）是高 effect-size 度量，3 × 200 ns 足以区分
2. F170E pose drift（问题 2）需 side-chain χ1/χ2 时序，300–500 ns 才避免 rotamer trap 假象
3. RMSD/RMSF（问题 3）是便宜副产物
4. **AF3 起始结构**对比晶体需要更长分阶段 restraint release：借鉴 mwSuMD 的 2→60→80→20 ns schedule ([Deganutti eLife 2024](https://elifesciences.org/articles/96513))；额外损耗 50–100 ns
5. **推荐路径**：先跑"最小 MVP"出初稿 → 剩余时间把 V138R、F170E 升级到 500 ns × 5 seeds 做 publication-grade

假设 PI 服务器 2× A100 并行：MVP ~12 天、标准 ~21 天、理想 ~60 天。

### 6.7 警示

- **Single replica 审稿/iGEM Judging 都会被质疑**：即便 1 μs 单 run 不如 3 × 200 ns 有说服力
- **AF3 起始 ≠ 晶体**：侧链 rotamer 和 loop 比实验结构更需平衡；首 50 ns 扣除是项目 operational burn-in heuristic；Memprot.GPCR-ModSim 2024 仅支持自动化 membrane setup/equilibration 背景，不再作为该数值来源
- **CGenFF ascr#18 糖环 penalty 必须先查**：>50 的参数必须 refine，否则盐桥占比数字不可信
- **GaMD / metadynamics 在 iGEM 5 月窗口是"诱惑陷阱"**：学习曲线 + 重权重 + debug 吃 2–4 周
- **HMR 4 fs 留给后期**：放大某些 CGenFF 数值不稳定性
- **CHARMM-modified TIP3P (TIPS3P) ≠ standard TIP3P**，不要混用
- **AF3 真菌 GPCR 不在 training set**：置信度比人源 GPCR 低

---

## 7. 盐桥 / HBond / 接触分析工具（第二轮）

### 7.1 工具对比表

| 工具 | 盐桥占比 | HBond 时间序列 | Contact lifetime | Python 生态 | GROMACS 轨迹 | 综合 |
|---|---|---|---|---|---|---|
| **MDAnalysis** | 无专用类，用 `AtomGroup` + `analysis.contacts` [[1]](https://userguide.mdanalysis.org/1.1.1/examples/analysis/distances_and_contacts/contacts_within_cutoff.html)[[2]](https://docs.mdanalysis.org/stable/documentation_pages/analysis/contacts.html) | `HydrogenBondAnalysis`（d_HA 3.0 Å / DHA 150°，含 `lifetime()` 自相关）[[3]](https://docs.mdanalysis.org/stable/documentation_pages/analysis/hydrogenbonds.html) | `lifetime()` + `count_by_time` 布尔序列 | 原生 pandas/numpy | `.xtc/.trr/.tpr` 一等公民 | **最佳通用** |
| **mdtraj** | 无内置，需手写 | `baker_hubbard` (θ>120°, r_HA<2.5 Å)[[4]](https://mdtraj.readthedocs.io/en/latest/notebook-examples/hbonds.html) | 无内置 | pandas 友好 | `.xtc/.trr` OK，**不支持 `.tpr`** | 快速脚本化 |
| **PLUMED** | COORDINATION CV（连续数值，非布尔占比）[[6]](https://www.plumed.org/doc-v2.9/user-doc/html/_c_o_o_r_d_i_n_a_t_i_o_n.html) | 间接 | driver 事后重放 | pycv 绑定 | 支持 `.xtc` | 过度工程化 |
| **VMD saltbr** | 直接输出，默认 3.2 Å (N↔O)[[8]](https://www.ks.uiuc.edu/Research/vmd/plugins/saltbr/) | `hbonds` 插件 | 仅 occupancy | Tcl，Python 弱 | 需 `.gro` + `.xtc` | 快速 look |
| **gmx hbond** (2024 重写) | 无盐桥命令 | d≤3.5 Å, DHA≤30°, `-ac` 自相关[[10]](https://manual.gromacs.org/2024.1/onlinehelp/gmx-hbond.html) | 自相关→τ_HB | 纯 C，需后处理 | 原生最好 | 大规模 screen |
| **ProLIF** (dynamic) | `Cationic`/`Anionic` 类 (3.5–4.5 Å + 电荷原子组)[[12]](https://prolif.readthedocs.io/en/latest/source/modules/interaction-fingerprint.html)[[13]](https://prolif.readthedocs.io/en/stable/notebooks/md-ligand-protein.html) | `HBDonor`/`HBAcceptor` | DataFrame groupby + itertools | 原生 RDKit/MDAnalysis/pandas | 通过 MDAnalysis Universe | **最贴合 iGEM 用例** |
| **GetContacts** | 默认 N(K/R/H) ↔ O(D/E) < 4.0 Å[[15]](https://getcontacts.github.io/) | `-itypes hb sb` | flareplot / TICC | numpy/pandas | VMD 后端 | **GPCRmd 社区标准** |
| **CPPTRAJ** | `hbond`/`contacts`/`nativecontacts` + `lifetime`[[16]](https://amberhub.chpc.utah.edu/nativecontacts/)[[17]](https://amberhub.chpc.utah.edu/lifetime/) | `hbond series` → `lifetime` | 一等公民 | 需后处理 | 需转拓扑 | Amber 生态首选 |

### 7.2 判据共识与警示

- **盐桥判据**：VMD 默认 3.2 Å、GetContacts / CHARMM-GUI / GPCRmd 2023–2025 论文普遍用 **d(N_basic–O_acidic) < 4.0 Å**，**不强制角度判据**（盐桥静电主导非方向性）。MDAnalysis 用户手册的 6 Å 示例仅教学用，**不推荐发表直接采用** ([MDAnalysis UG](https://userguide.mdanalysis.org/1.1.1/examples/analysis/distances_and_contacts/contacts_within_cutoff.html))
- **HBond 判据**：MDAnalysis 3.0 Å/150° vs mdtraj 2.5 Å/120° vs GROMACS 2024 3.5 Å/30° — **各工具数值不一致，跨工具直接对比占比毫无意义**；V138R 分析必须从头到尾用同一套判据
- **ARG 胍基**：Nε/NH1/NH2 三个等价质子供体，必须取 `min()` 而非 `mean()`；ProLIF `Cationic` 默认用 guanidinium 中心，手写脚本易踩坑
- **Contact lifetime ≠ occupancy**：100 帧中 50 帧 ON 可以是"稳定 50 帧"或"闪烁 25 次"，物理意义完全不同，必须**同时**汇报 occupancy 和 lifetime histogram
- **PBC**：`gmx trjconv -pbc mol -center` 预处理，否则盐桥距离全是伪影
- **ProLIF 内存**：10^4 帧 × 数百列 OK，若 1 ps 采样需分段 `run()` + HDF5

### 7.3 V138R 盐桥分析推荐管线（端到端）

**主栈 = MDAnalysis + ProLIF + pandas**。ProLIF **已原生覆盖** `Cationic`/`Anionic`（即 ionic/salt bridge 指纹），且 `run()` 直接接受 MDAnalysis trajectory，输出 MultiIndex DataFrame — 直接把现有 docking-repro ProLIF 逻辑迁到 trajectory 即可。

```python
import MDAnalysis as mda, prolif as plf, pandas as pd
import itertools

# 1. 加载 (WT 和 V138R 各一次)
u = mda.Universe("md.tpr", "md.xtc")
prot = u.select_atoms("protein")
lig  = u.select_atoms("resname ASC18")

# 2. ProLIF 一把梭（推荐）
fp = plf.Fingerprint(interactions=["Cationic","Anionic","HBDonor","HBAcceptor"])
fp.run(u.trajectory[::1], lig, prot)
df = fp.to_dataframe()       # MultiIndex: (ligand, protein_res, interaction)

# 3. 盐桥占比
sb = df.xs(("ARG138","Cationic"), level=(1,2), axis=1)
occupancy = sb.mean().iloc[0]

# 4. Contact lifetime histogram (run-length-encode)
states = sb.astype(int).values.flatten()
lifetimes = [sum(1 for _ in g) for k,g in itertools.groupby(states) if k==1]
pd.Series(lifetimes).hist(bins=30)
```

**方案 B（严格几何判据）**：用 MDAnalysis `distances.distance_array` 对 ARG138 `name NH1 NH2 NE` 与 ascr#18 羧基 `name O1 O2` 逐帧算最小距离，阈值 4.0 Å 输出布尔矩阵 — 可与 ProLIF 结果交叉验证。

**F170E 侧链**：`analysis.dihedrals.Janin(u.select_atoms("resid 170")).run()` 给 χ1/χ2 时序；rotamer 跳变 = χ1 vs time 折线 + 密度图 [[18]](https://docs.mdanalysis.org/stable/documentation_pages/analysis/dihedrals.html)。

**Top 6 RMSD/RMSF**：MDAnalysis `analysis.rms.RMSD` / `RMSF`；6 mutant × 3 rep 用 PMDA 或 joblib 并行 [[14]](https://www.mdanalysis.org/pmda/api/hbond_analysis.html)。

**不推荐**：PLUMED（overkill）、VMD saltbr（GUI 批量差、判据 3.2 Å 偏严）。

### 7.4 与 docking-repro 衔接

ProLIF **已经原生**覆盖动态 IFP + Cationic/Anionic — **不需要另写外部盐桥脚本**。现有 `run_ifp_mutants.py` 逻辑直接可迁移（参数只需从 `Fingerprint(interactions=["VdWContact", ...])` 扩展到加 `Cationic/Anionic`）。唯一缺口：ProLIF 默认**不给 contact lifetime histogram**，用 `itertools.groupby` 或 `scipy.ndimage.label` 在布尔列上 run-length encoding 即可（≤10 行代码）。

**关键参考 notebook**：
- [ProLIF ligand-protein MD tutorial](https://prolif.readthedocs.io/en/stable/notebooks/md-ligand-protein.html) — 端到端最贴合 V138R 用例
- [ProLIF protein-protein MD tutorial (GPCR demo)](https://prolif.readthedocs.io/en/stable/notebooks/md-protein-protein.html) — GPCR 7TM 分段示例
- [MDAnalysis Native contacts](https://docs.mdanalysis.org/stable/documentation_pages/analysis/contacts.html)
- [GetContacts](https://getcontacts.github.io/) — GPCR 社区 cross-check
- [Nat Commun 2025 GPCRmd-2](https://www.nature.com/articles/s41467-025-57034-y) — 181 ligand-GPCR × 3×500 ns，GetContacts + MDAnalysis/mdtraj 混合栈

---

## 8. MM-PBSA / 自由能工具（第二轮）

### 8.1 主流工具对比

| 工具 | 2023-2026 GPCR 使用 | 学习曲线 | 与 CHARMM-GUI 兼容 | 综合 |
|---|---|---|---|---|
| **gmx_MMPBSA** ([JCTC 2021](https://pubs.acs.org/doi/abs/10.1021/acs.jctc.1c00645), [GitHub](https://github.com/Valdes-Tresanco-MS/gmx_MMPBSA)) | 活跃，GROMACS 2024.1 集成 | 中低：官方 tutorial 覆盖膜蛋白 + CHARMM-ff 专门示例 | **原生支持**，v1.5.0 起内置 `charmm_radii` ([示例](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/examples/Protein_ligand_CHARMMff/)) | **本项目首选** |
| g_mmpbsa ([JCIM 2014](https://pubs.acs.org/doi/10.1021/ci500020m)) | 过时 | 低 | 仅 GROMOS/AMBER | 放弃 |
| AmberTools MMPBSA.py ([JCTC 2012](https://pubs.acs.org/doi/10.1021/ct300418h)) | 广泛 | 中 | 间接 | 次选 |
| alchemlyb + GROMACS FEP ([PyPI](https://pypi.org/project/alchemlyb/)) | 事实标准后处理库 | 中高 | 兼容（后处理 dhdl.xvg） | 做 FEP 必备 |
| BFEE2 ([JCIM 2021](https://pubs.acs.org/doi/10.1021/acs.jcim.1c00269)) | 增长中，**绝对**结合 ΔG | 中 | 支持 CHARMM ff，alchemical 仅 NAMD | 备选 |
| GROMACS FEP + AWH ([docs](https://www.gromacs.org/topic/awh-fep.html)) | 活跃，2024 GPU FEP 加速 ([ACS Omega 2025](https://pubs.acs.org/doi/full/10.1021/acsomega.5c00151)) | 高 | 原生 | 最硬核 |

### 8.2 MM-PBSA 精度共识

Genheden-Ryde 基准给出 **RMSE 10–43 kJ/mol（≈2.4–10.3 kcal/mol）**，Pearson 0.59–0.93，标准差 11–15 kcal/mol — **比较亲和力接近的配体时精度不足** ([PMC4487606](https://pmc.ncbi.nlm.nih.gov/articles/PMC4487606/))。2024 年 Roux & Chipot JPCB 社评直言 MM-PBSA 需 "wisely" 使用，构象熵涨落大、**内介电常数敏感**是两大痛点 ([JPCB 2024](https://pubs.acs.org/doi/10.1021/acs.jpcb.4c06614))。膜蛋白上 ε_in 从 1 升到 20 时，相关系数 0.60→0.81 ([JCIM 2021](https://pubs.acs.org/doi/abs/10.1021/acs.jcim.1c00410))。class A GPCR 20 靶点 / 934 配体评估里，MM-PBSA 仅在 **8/20** 靶点好于对接评分（4 个更差）([Vega JCAMD 2019](https://link.springer.com/article/10.1007/s10822-019-00201-3)) — **对 ranking 有用，对绝对值不可轻信**。

### 8.3 Alchemical FEP 对 iGEM 时间窗口的可行性

Class A GPCR 上 FEP+ 能达到 **RMSE ≈ 0.8–1.1 kcal/mol**，优于 MM-PBSA ([JCIM 2020](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00449), [ChemRxiv 2023 8 GPCRs](https://chemrxiv.org/doi/10.26434/chemrxiv-2023-mhp2x))。单 λ 窗 1–5 ns，总体 **~60 ns / ΔG 估计**（12–24 λ × 3–5 ns × 3 rep）([Mobley 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4420631/))。GROMACS 2024 AWH 自适应 λ 可提升 ~10×；GPU-FEP 把 400 h→48 h。对 "V138R vs WT" 单个 ΔΔG，RBFE 两条腿（合-离）总 ~500–800 ns 膜蛋白采样 — **5 月预算内可行但紧张**，需先过"稳定膜系统 + 配体参数化"两道关。零背景团队学习曲线明显高于 gmx_MMPBSA。

### 8.4 本项目决策：V138R 盐桥贡献如何估算

**推荐路径 = (b) + (d) 为主，(c) 做 stretch goal**：

- **主路径 (b) gmx_MMPBSA**：WT 与 V138R binding ΔG 差，打开 **per-residue decomposition**（gmx_MMPBSA 原生支持），把贡献定位到 ARG138。两套体系各 3×500 ns holo，**ε_in = 4–8 范围 + charmm_radii**，论文明确声明作为"定性 ranking"使用
- **主路径 (d) IFP 占比**：同样轨迹抽 ARG138-ascr#18 羧基盐桥占比（<4.0 Å）+ ProLIF Cationic/Anionic 追踪 → **结构 + 能量分解 + 占比三角**，避免把单一数字当真理
- **Stretch (c) alchemical**：若 7 月前膜系统稳定，做 "WT → V138R" 蛋白侧单点突变 relative ΔΔG（配体不动，比 ligand RBFE 简单）：10–15 λ × 4 ns × 3 rep ≈ 120–180 ns/腿，双腿 ~360 ns
- **避坑**：不要只靠 MM-PBSA ranking — ±2 kcal/mol 误差窗容易把真实盐桥贡献（典型 2–4 kcal/mol）吞掉

### 8.5 近年 GPCR + ligand MM-PBSA 样本

| 论文 | 体系 | 精度/用途 |
|---|---|---|
| [Vega JCAMD 2019](https://link.springer.com/article/10.1007/s10822-019-00201-3) | 20 class A × 934 ligand | MM-PBSA 击败 docking 仅 8/20，system-specific |
| [Frontiers Pharmacol 2022](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2022.1018351/full) | 可溶+膜 | 膜蛋白无 >2 kcal/mol 偏差（样本小） |
| [CB1 ZCZ011 ACS Bio Med Chem Au 2025](https://pubs.acs.org/doi/10.1021/acsbiomedchemau.5c00169) | CB1 别构 | CHARMM36m + CGenFF + gmx_MMPBSA 端到端模板 |
| [CB1 single-point mutation ACS Omega 2022](https://pubs.acs.org/doi/10.1021/acsomega.2c04980) | CB1 突变 | MD + MM-PBSA 结构/能量耦合 |

---

## 9. ascaroside 参数化：类比链（第二轮）

### 9.1 6-deoxyhexose 糖环参数化现状

ascarylose = **3,6-dideoxy-L-mannose** ([MDPI 2019 review](https://www.mdpi.com/1422-0067/20/16/3898))。最近类比 = **fucose (6-deoxy-galactose) 和 rhamnose (6-deoxy-mannose)**。CHARMM 碳水力场（[Guvench PMC3224046](https://pmc.ncbi.nlm.nih.gov/articles/PMC3224046/)）**已原生覆盖 fucose/rhamnose/xylose**：参数由 hexopyranose + alkane/ether term 类比迁移，晶体 MD 验证全部一致（除 fucose C5-O5 外）。**这意味着 ascarylose 的环可以直接用 CHARMM36 carbohydrate par_all36_carb + CGenFF 的 3,6-dideoxy 替换，不需要从零 QM 重拟**（重大红利）。

GLYCAM06 同样覆盖 ([JCC 2008](https://pubmed.ncbi.nlm.nih.gov/17849372/))，但与 CHARMM36m 蛋白/脂不兼容，不推荐混用。GAFF2 碳水表现一般，通常混合 GLYCAM + GAFF2。

### 9.2 脂肪酸链 + 糖苷键处理

C7-C9 脂肪酸羧基末端是 CGenFF 日常覆盖的 drug-like 片段。CB1 + anandamide 报道明确："**all parameters have very low penalties**" ([ACS Omega 2022 CB1](https://pubs.acs.org/doi/10.1021/acsomega.2c04980), [bioRxiv 2024](https://www.biorxiv.org/content/10.1101/2024.10.25.620304v1.full))。α-O-glycoside 的 φ (O5-C1-O'-C') / ψ (C1-O'-C'-C'') 扭转由 ParamChem 派生（[Sci Rep 2022 glycopeptide](https://www.nature.com/articles/s41598-022-10735-6) 同协议），anomeric/exo-anomeric 效应在 ⁴C₁ 椅式下被 CGenFF 捕捉。

**可能的高 penalty 位点**：(a) C3 脱氧带来的非标准原子型组合，(b) 糖的 1-O-alkyl 到 ω-1 羟基的异常连接 — 需 ParamChem 跑出后逐键审计。

### 9.3 CB1 + anandamide 类比路径

anandamide = "长脂肪链 + 极性头"的 GPCR 配体，**距离 ascaroside 最近的公开 MD 范式**：

1. [ACS Omega 2022 CB1 allosteric mutation](https://pubs.acs.org/doi/10.1021/acsomega.2c04980) — CHARMM36m + C36 lipid + CGenFF（ParamChem，"all very low penalties"），使用 CHARMM-GUI Ligand Reader & Modeler
2. [bioRxiv 2024 Endocannabinoid subtype](https://www.biorxiv.org/content/10.1101/2024.10.25.620304v1.full) — 相同栈，长链采样问题
3. [ACS Bio Med Chem Au 2025 CB1 ZCZ011](https://pubs.acs.org/doi/10.1021/acsbiomedchemau.5c00169) — CHARMM36m + CGenFF + gmx_MMPBSA **端到端模板**
4. [Nat Commun 2023 CB1 + EC analog](https://www.nature.com/articles/s41467-023-37864-4) / [PMC9963961](https://pmc.ncbi.nlm.nih.gov/articles/PMC9963961/) — 同栈

**类比要点**：长脂肪链的 torsion 是**采样问题而非参数问题**；配体 entry 可能通过膜-受体界面（类比 [S1P1R Sci Rep 2016](https://www.nature.com/articles/srep22639)）— ascaroside 也可能从膜进入 Gpr3，**起始构象放置需测试 "直接 orthosteric dock" 与 "膜内预平衡再入" 两种方案**。

### 9.4 CGenFF penalty 审计最佳实践

权威标准：[CGenFF II JCIM 2012](https://pubs.acs.org/doi/10.1021/ci3003649) / [SilcsBio docs](https://docs.silcsbio.com/2025/cgenff/optimizer.html)

| penalty | 动作 |
|---|---|
| < 10 | 直接使用 |
| 10–50 | 基本验证：geom/vib/dipole vs QM (B3LYP/6-31G*) |
| 50–100 | 需优化：torsion scan 重拟；CGenFF Optimizer 默认阈值 50 |
| > 100 | 必须重拟；[ffTK](https://pmc.ncbi.nlm.nih.gov/articles/PMC3874408/) 或 LSFitPar |
| > 200 | 通常原子型选错 |

**关键警告**：penalty 只度量与 CGenFF 库的**类比程度**，不是物理精度；低 penalty 不等于对、高 penalty 不等于错 ([CGenFF docs](https://docs.silcsbio.com/2019.2/cgenff/cgenff.html))。

推荐工具链：ParamChem → 高 penalty torsion 清单 → Gaussian/ORCA B3LYP/6-31G* relaxed scan（环糖建议 MP2/cc-pVTZ 单点校正）→ ffTK Torsion Explorer 可视化拟合 → crystal / 纯液相性质验证。

### 9.5 Sanity check 方案（无 NMR 参考）

1. **糖环椅式分布**：Cremer-Pople (Q, θ, φ) 投影 MD 轨迹；应主要落 ⁴C₁（θ ≈ 0）。若 ¹C₄ 或 skew-boat 超 5%，说明环内扭转能垒被低估，需 QM 重拟 C-C-O-C
2. **糖苷键 φ/ψ 分布**：Ramachandran-like 热力图，与蛋白糖基化 GalNAc-Ser/Thr 分布做形状对比（绝对位置会因 α/β 位移）
3. **液相密度 / 溶剂化 ΔG**：methyl α-ascaroside 小片段，对比 ffTK 目标 ≤15% / ±0.5 kcal/mol

### 9.6 ascaroside 参数化分阶段行动计划

| 阶段 | 动作 | 预估 | 产出 |
|---|---|---|---|
| 1. ParamChem | ascr#18 mol2 → CGenFF stream；分离糖头和脂肪链分别跑便于审计 | **1–2 天** | `ascr18.str` + penalty 报告 |
| 2. Penalty 扫描分级 | 按 9.4 表归类所有 bond/angle/dihedral/charge penalty；标记 >50 项 | **2–3 天** | 审计电子表格 |
| 3. QM 重拟（必要时） | Gaussian B3LYP/6-31G*：(a) 环内 C-C-O-C、(b) 糖苷键 φ/ψ、(c) penalty >100 项 relaxed scan；ffTK Torsion Explorer 重拟 | **1–2 周**（含 QM 排队） | 修订版 `ascr18.str` |
| 4. Sanity check | (1) 纯水 200 ns MD + Cremer-Pople；(2) 糖苷键 φ/ψ 分布；(3) 液相密度/ΔG；若与 fucose/rhamnose 一致即锁定 | **1 周** | 验证报告 |
| 5. 并入生产栈 | CHARMM-GUI Ligand Reader & Modeler 读 stream → 与 Gpr3 + POPC 组装 | **2–3 天** | 可进 MD 拓扑 |
| **总计** | | **3–5 周**（含 QM） | |

**关键权衡**：阶段 3 的 QM 重拟是最大风险。**若阶段 2 发现所有项 < 50，可跳过阶段 3 直接进 4，总时长缩至 ~2 周**。建议立即跑阶段 1–2，用 penalty 决定是否触发阶段 3。

### 9.7 insufficient data found

- C. elegans ascaroside 的公开 MD 参数化文献 = 0
- 短链脂肪酸（C7-C9）的专门 CGenFF 验证论文未找到独立样本，需靠 anandamide 类工作间接背书

---

## 10. 第二轮决策摘要（增量）

| 维度 | 选择 | 关键理由 |
|---|---|---|
| **采样协议（MVP）** | 7 holo × 200 ns × 3 rep = 4200 ns | A100 ~24 GPU-day，首 50 ns eq，t-test 可做 |
| **采样协议（理想）** | 14 × 500 ns × 3 rep = 21 μs | 匹配 GPCRmd-2，PCA/FEL 对比 |
| **分析主栈** | MDAnalysis + ProLIF + pandas | ProLIF Cationic/Anionic 原生覆盖盐桥，直接迁移 docking-repro 管线 |
| **分析 cross-check** | GetContacts | GPCRmd 社区标准 4.0 Å 判据 |
| **自由能主路径** | gmx_MMPBSA + per-residue + IFP 占比三角 | ε_in = 4–8 + charmm_radii；论文声明定性 ranking |
| **自由能 stretch** | GROMACS 蛋白侧 alchemical RBFE (AWH) | 10–15 λ × 4 ns × 3 rep × 2 腿 ≈ 360 ns |
| **ascaroside 参数** | ParamChem → penalty 分级 → 条件 QM → Cremer-Pople | 2–5 周；红利：CHARMM 碳水已原生覆盖 fucose/rhamnose |

### 淘汰 / 推迟

- **HMR 4 fs**：对 CGenFF 数值不稳定，首次交付不用
- **GaMD / metadynamics / LiGaMD**：μs 量级 + 学习曲线，5 月窗口吃不下
- **g_mmpbsa**：过时无 CHARMM 支持
- **PLUMED 盐桥 CV**：场景不匹配
- **VMD saltbr**：GUI 批量差、3.2 Å 判据偏严
- **GLYCAM06**：与 CHARMM36m 生态不兼容

### 前置强制动作（按时间紧迫度）

1. ⭐⭐⭐ **ascaroside ParamChem penalty 扫描**（1–2 天）：立即做，决定是否触发 QM 重拟；不做 = V138R 盐桥占比数字不可信
2. ⭐⭐⭐ **CHARMM-GUI 学术账号**：本周内注册（审批 0.5–1 天）
3. ⭐⭐⭐ **AlphaFold3 结构 PPM 2.0 对齐**：生产前必做；跳过 → TM 倾角 30°+ 灾难
4. ⭐⭐ **水盒子 benchmark**：如后续更换 GPU/Slurm 节点，再跑一次，验证 `-update gpu -bonded gpu -pme gpu` 是否开到位
5. ⭐⭐ **体系清单 pre-register**：在跑之前写死 7 或 14 个体系，防止中途增加导致统计比较不公
6. ⭐ **分阶段 equilibration schedule**：借鉴 mwSuMD 2→60→80→20 ns restraint release，AF3 起始首 50 ns 扣除

---

## 12. GPCR-Gα 蛋白复合物 MD 文献调研（第三轮；2026-05-06 source-audited）

> **调研背景**：前两轮调研（§1–§10）覆盖 GPCR-配体 MD 体系的技术栈选型，但**未覆盖 GPCR-Gα 蛋白-蛋白复合物 MD**。P3 嵌合 Gpa1 设计已完成 Phase 4（Top 3 候选选定），Phase 5 MD 验证需要独立的文献支撑。
>
> **初始调研时间**：2026-04-16；**来源审查修订**：2026-05-06。
>
> **2026-05-06 审查规则**：没有 DOI / 标题 / 原文方法段落 / 官方工具文档 / exact data pointer 的文献引用，不作为权威依据。旧版“only/首篇/充分支撑”等强断言在完成完整重新枚举前降级为 **pending source audit**。本节只保留已核到 exact pointer 的事实。

### 12.1 GPCR-Gα 复合物 MD 关键文献（source-audited status）

| # | 文献 | exact pointer | 核验到的方法/体系 | 本项目可用性 | 审查状态 |
|---|------|---------------|------------------|--------------|----------|
| 1 | **Tawfeeq et al. 2025** | *Biochemistry* 64(11):2439–2454, DOI [`10.1021/acs.biochem.4c00779`](https://doi.org/10.1021/acs.biochem.4c00779) | D1R/D2R 与 Gαs/Gαi WT + Gα C 端 18 aa 交换嵌合体（G_i18s/G_s18i）；GDP-bound 与 nucleotide-free/Empty 两类 G 蛋白状态；CHARMM-GUI 建系，AMBER PMEMD；AMBER ff19SB/Lipid17/OPC/GAFF2；每个模型 4 × 500 ns | **直接支持“Gα C 端交换嵌合体可做 MD 验证”和 500 ns/rep 量级** | 已核验；但**不是** GROMACS/CHARMM36m 来源，也**不支持**本项目 empty-only 作为文献必然选择 |
| 2 | **Velazhahan et al. 2021** | *Nature* 589:148–153, DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1), PDB [`7AD3`](https://www.rcsb.org/structure/7AD3) | Ste2 dimer coupled to two heterotrimeric G proteins；cryo-EM 结构来源；论文含 Ste2/G protein 相关 MD 背景 | **Ch-ctrl 结构/界面几何锚点**；Ste2-Gpa1 阳性对照的最强结构来源 | 已核验；本项目主要用作结构锚点，不把其所有 MD 参数直接迁移 |
| 3 | **Mohanty et al. 2025**（旧文档误作 Ramasamy） | *eLife* 14:RP106397, DOI [`10.7554/eLife.106397.3`](https://doi.org/10.7554/eLife.106397.3) | Gcoupler；Ste2p-Gpa1p interface allosteric/metabolite study；Ste2p–metabolite MD + miniGpa1 docking/ΔG/Kd 分析；eLife assessment 标注证据强度为 incomplete | 可作为 **Ste2p-Gpa1p interface/allosteric context**，不是完整 Ste2-Gpa1 production MD protocol | 已核验并降级：不再称为“唯一 Ste2-Gpa1 MD 研究”或“MD 交叉验证锚点” |
| 4 | **Renault et al. 2019**（旧文档误作 Ranganathan） | *Scientific Reports* 9:5495, DOI [`10.1038/s41598-019-41980-x`](https://doi.org/10.1038/s41598-019-41980-x) | A2A receptor + Mini-Gs / α5 helix；CHARMM-GUI；POPC；CHARMM36 + CGenFF；GROMACS 5.1.4；2 independent replicas × 600 ns，discard first 100 ns；selected systems extended to 2 μs | 支持 **GPCR + engineered Gα/α5、GROMACS、CHARMM36、POPC、500 ns 分析窗口** 的协议类比 | 已核验并替换旧错误引用 |
| 5 | **Casiraghi et al. 2025** | *Science Advances* 11(12):eadq3971, DOI [`10.1126/sciadv.adq3971`](https://doi.org/10.1126/sciadv.adq3971) | β2AR coupling specificity；Gαs/Gαi；结构和生物物理证据指向 ICL2/TM6 构象差异 | 可作为 **G protein coupling specificity 背景** | 已核验；不作为 COM distance 阈值、ICL2↔α5 数值指标或 ms-timescale cutoff 的来源 |
| 6 | **van den Broek et al. 2024**（Memprot.GPCR-ModSim） | *Bioinformatics* 40(11):btae662, DOI [`10.1093/bioinformatics/btae662`](https://doi.org/10.1093/bioinformatics/btae662) | Memprot.GPCR-ModSim web server；membrane-protein modelling、embedding、solvation、equilibration；GROMACS-based output ready for further simulations | 可支持 **自动化膜蛋白建系/平衡化工具链背景** | 已核验；**不支持**旧文档“CHARMM36m + 500 ns + 303.15 K 标准协议”表述 |
| 7 | **Miszta et al. 2021**（GPCRsignal；旧文档误作 Jakowiecki 一作） | *Nucleic Acids Research* 49(W1):W247–W256, DOI [`10.1093/nar/gkab434`](https://doi.org/10.1093/nar/gkab434) | GPCR-effector interface webserver；implicit water-membrane MD；FlarePlots、interaction frequency heatmaps/difference analysis | 支持 **interaction frequency / interface-contact frequency 分析思想** | 已核验；不支持 `>0.50` 作为 universal pass/fail cutoff |

### 12.2 Chimeric Gα MD 先例分析：Tawfeeq et al. 2025

**Tawfeeq et al. 2025** 是本节目前已核到 exact pointer 的最直接 chimeric Gα MD 先例，但不是本项目协议的“一比一模板”。

- **设计**：Gαs 与 Gαi 的 α5/C 端 18 残基交换，构建 G_i18s 与 G_s18i。
- **体系组成**：D1R/D2R + Gα 模型；同时包含 GDP-bound 与 nucleotide-free/Empty 状态；D1R/D2R 还带 dopamine ligand。旧版“与本项目一样不含核苷酸”是错误迁移，已撤回。
- **模拟协议**：16 个 receptor–G protein 模型；每个模型 4 independent replicas × 500 ns；总计 64 条 500 ns trajectories。
- **软件/力场**：CHARMM-GUI 用于建系；生产 MD 是 AMBER PMEMD，不是 GROMACS；力场为 AMBER ff19SB / Lipid17 / OPC / GAFF2，不是 CHARMM36m。
- **分析重点**：MMPBSA/thermodynamic analysis、结构和接触/α5 相关比较。旧版“直接提供 α5 iRMSD、BSA、contact persistence 三阈值模板”的说法没有 exact method pointer，不能保留。

**可迁移到本项目的只有两点**：

1. “Gα C 端/α5 残基交换的 chimeric Gα 可以用 receptor–G protein complex MD 评价”这一研究设计逻辑。
2. “500 ns × multiple independent replicas”这一采样量级。

**不可迁移/不可引用为依据**：GROMACS/CHARMM36m 技术栈、empty-only 体系组成、BSA/α5 iRMSD/contact persistence 的数值阈值。

### 12.3 技术栈兼容性确认（修订版）

| 维度 | 本项目选择 | source-audited 支撑 | 当前解释 |
|------|------------|--------------------|----------|
| MD 引擎 | GROMACS 2025.2 | Renault 2019 使用 GROMACS 5.1.4；Memprot.GPCR-ModSim 输出 GROMACS-ready membrane systems | 支持“GROMACS 可用于 GPCR/engineered Gα 或膜蛋白复合物”，不是版本等同 |
| 蛋白/脂质力场 | CHARMM36m / CHARMM-GUI stack | Renault 2019 使用 CHARMM36/CGenFF + CHARMM-GUI；本项目 production 输入来自 CHARMM-GUI | 支持 CHARMM-family 技术栈合理；Tawfeeq 不再作为 CHARMM36m 依据 |
| 膜组分 | POPC | Tawfeeq 2025、Renault 2019 均有 POPC bilayer；Velazhahan 结构背景与膜 GPCR 体系一致 | POPC 是合理简化，不等于所有 Ste2/Gpa1 生物膜组分 |
| 膜构建 | CHARMM-GUI | Tawfeeq 2025 与 Renault 2019 均用 CHARMM-GUI；本项目 CHARMM-GUI 输出已实际运行 | 充分支持继续沿用 |
| 多链/复合物支持 | GPCR + Gα / engineered Gα | Renault 2019 的 A2A–Mini-Gs；Tawfeeq 2025 的 D1R/D2R–Gα chimeras；Velazhahan 2021 的 Ste2–G protein 结构 | 支持本项目 receptor–Gα complex 建系，但物种/类别差异仍需在解释中声明 |

**结论（修订）**：现有 GROMACS + CHARMM36m + CHARMM-GUI + POPC 栈仍可继续使用；但旧版“所有引用共同充分支撑同一技术栈”的说法过强。正确说法是：**多个 exact-pointer 文献分别支撑建系、GROMACS/CHARMM-family、POPC、engineered Gα complex 这些子层；它们不是一个完全相同的协议模板。**

### 12.4 模拟时长推荐（修订版）

| 来源 | 核验到的时长 | 可迁移含义 |
|------|--------------|------------|
| Tawfeeq 2025 | 每个 receptor–G protein 模型 4 × 500 ns | chimeric Gα 直接先例支持 500 ns/rep 量级 |
| Renault 2019 | 2 replicas × 600 ns，discard first 100 ns；selected systems extended to 2 μs | GPCR–Mini-Gs/α5 系统中 500 ns 分析窗口可观察 allosteric/contact-network effects；2 μs 可作为更深采样参考 |
| Memprot.GPCR-ModSim 2024 | 提供 membrane embedding / equilibration / GROMACS-ready setup | 不再作为 500 ns production 时长来源 |
| Casiraghi 2025 | coupling specificity 的结构/生物物理背景 | 不再作为本项目 ns–μs 时长判据来源 |

**采纳（项目 operational choice）**：500 ns × 3 reps 仍保留为最小可行采样方案；依据是 Tawfeeq 2025 和 Renault 2019 的同量级先例 + 项目 GPU/时间约束。它不是文献定义的 universal threshold。分析窗口起点 100 ns 继续标为项目 operational burn-in heuristic，不再归因于 Memprot 2024。

### 12.5 关键缺口（2026-05-06 降级说明）

旧版 §12.5 曾写“真菌 GPCR-Gα 复合物 MD 仅 2 篇”“Chimeric Gα + GPCR MD 仅 1 篇”。这些是 **only-N / 首创类强断言**，需要重新枚举完整文献集合后才能用于 wiki/paper。当前处理如下：

1. **保留可证实 anchor**：Velazhahan 2021 是 Ste2-Gpa1/G protein 结构与 chctrl 几何锚点；Tawfeeq 2025 是 chimeric Gα MD 设计先例；Renault 2019 是 engineered Gα/Mini-Gs + GROMACS/CHARMM/POPC 协议类比。
2. **降级 Mohanty 2025**：其研究聚焦 Ste2p-Gpa1p interface allosteric modulators 和 Gcoupler，不再作为“完整 Ste2-Gpa1 complex MD protocol”。
3. **暂停 only-N claim**：在完成系统检索矩阵重审前，不写“仅 2 篇”“仅 1 篇”“首个”等最终表述；可写成“在当前已核 exact-pointer 文献中，尚未找到非酿酒酵母真菌 chimeric Gα–GPCR complex MD 的直接先例”。
4. **ascaroside-bound GPCR-Gα MD**：本轮未找到 exact-pointer 直接先例；继续标为 pending source audit，而不是绝对“零篇”。
5. **MD 解释边界**：本项目 MD 评价的是结构/界面稳定性，不等价于完整 G protein activation 或 GDP/GTP exchange 机制；Tawfeeq 2025 也明确区分 early association 与 GDP release/activation。

### 12.6 引用来源（source-audited）

1. Tawfeeq C, Hilibrand AS, Smith JS, Portillo J, Kruse AC, Abrol R (2025). “G Protein Selectivity in Dopamine Receptors is Determined before GDP Release.” *Biochemistry* 64(11):2439–2454. DOI [`10.1021/acs.biochem.4c00779`](https://doi.org/10.1021/acs.biochem.4c00779). （旧文档已从 “Tsai et al.” 勘误为 Tawfeeq；本轮进一步纠正其方法栈和 nucleotide-state 迁移。）
2. Velazhahan V, Ma N, Pándy-Szekeres G, Kooistra AJ, Lee Y, Gloriam DE, Vaidehi N, Tate CG (2021). “Structure of the class D GPCR Ste2 dimer coupled to two G proteins.” *Nature* 589:148–153. DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1); PDB [`7AD3`](https://www.rcsb.org/structure/7AD3).
3. Mohanty SK, Mittal A, Farooqi N, Gaur A, et al. (2025). “Deep learning reveals endogenous sterols as allosteric modulators of the GPCR–Gα interface.” *eLife* 14:RP106397. DOI [`10.7554/eLife.106397.3`](https://doi.org/10.7554/eLife.106397.3). （旧文档误作 “Ramasamy et al.”。）
4. Renault P, Louet M, Marie J, Labesse G, Floquet N (2019). “Molecular Dynamics Simulations of the Allosteric Modulation of the Adenosine A2a Receptor by a Mini-G Protein.” *Scientific Reports* 9:5495. DOI [`10.1038/s41598-019-41980-x`](https://doi.org/10.1038/s41598-019-41980-x). （旧文档 “Ranganathan et al. / Sci Rep 9:11265 / Allosteric coupling across...” 未找到 exact pointer，已替换。）
5. Casiraghi M, Wang H, Brennan PC, Habrian C, Hübner H, Schmidt MF, Maul L, Pani B, Bahriz SMFM, Xu B, Staffen N, Assafa TE, Chen B, White E, Sunahara RK, Inoue A, Xiang YK, Lefkowitz RJ, Isacoff EY, Nucci N, Gmeiner P, Lerch MT, Kobilka BK (2025). “Structure and dynamics determine G protein coupling specificity at a class A GPCR.” *Science Advances* 11(12):eadq3971. DOI [`10.1126/sciadv.adq3971`](https://doi.org/10.1126/sciadv.adq3971).
6. van den Broek RL, Bello X, Küpper RV, van Westen GJP, Jespers W, Gutiérrez-de-Terán H (2024). “Memprot.GPCR-ModSim: modelling and simulation of membrane proteins in a nutshell.” *Bioinformatics* 40(11):btae662. DOI [`10.1093/bioinformatics/btae662`](https://doi.org/10.1093/bioinformatics/btae662).
7. Miszta P, Pasznik P, Niewieczerzał S, Jakowiecki J, Filipek S (2021). “GPCRsignal: webserver for analysis of the interface between G-protein–coupled receptors and their effector proteins by dynamics and mutations.” *Nucleic Acids Research* 49(W1):W247–W256. DOI [`10.1093/nar/gkab434`](https://doi.org/10.1093/nar/gkab434).

### 12.7 本轮纠错摘要

- `Ramasamy et al. 2025` → **Mohanty et al. 2025**；保留为 Ste2p-Gpa1p interface / allosteric-metabolite context，降级为非 full-complex MD protocol。
- `Ranganathan et al. 2019 / Sci Rep 9:11265 / Allosteric coupling across...` → 未找到 exact pointer；替换为 **Renault et al. 2019 / Sci Rep 9:5495 / DOI 10.1038/s41598-019-41980-x**。
- `Casiraghi & Kobilka 2025` → 作者列表与题名纠正为 **Casiraghi et al. 2025, “Structure and dynamics determine G protein coupling specificity at a class A GPCR”**；只作 specificity 背景，不作 COM/时标阈值来源。
- `Pandy-Szekeres et al. 2024 Memprot` → 纠正为 **van den Broek et al. 2024**；不再声称其给出 CHARMM36m + 500 ns + 303.15 K 标准协议。
- `Jakowiecki et al. 2021 GPCRsignal` → 一作纠正为 **Miszta et al. 2021**；页码纠正为 W247–W256。
- Tawfeeq 2025：保留 C-terminal 18-aa chimeric Gα + 4×500 ns 直接先例；撤回“CHARMM/GROMACS 支撑”“empty-only 支撑”“BSA/iRMSD/contact-persistence 阈值模板”三类过度迁移。

## 11. Methodology

- **检索框架**：两轮 deep-research，每轮 3 个并行研究子代理
- **工具**：WebSearch + WebFetch（本环境未配置 firecrawl/exa MCP）
- **检索深度**：每维度 10–15 个独立来源，每个子问题 3–5 次关键词搜索 + 3–5 次 WebFetch 深读
- **时间偏好**：2023–2026 优先，最低 2022
- **引用纪律**：所有陈述 inline URL，缺数据明确标 "insufficient data found"
- **限制**：WebSearch 语义检索弱于 exa/firecrawl；ascaroside 直接文献为零，结论基于类比糖脂文献
- **信心度**：
  - §1–§3（软件/力场/膜）High：3 维度主流趋势一致，交叉互证
  - §6（时间尺度）High：GPCRmd-2 + PLOS CB 双权威
  - §7（分析工具）High：ProLIF 官方 tutorial 直接覆盖用例
  - §8（MM-PBSA / FEP）Medium：精度警告充分，iGEM 窗口里 alchemical 需谨慎
  - §9（ascaroside）Medium-Low：直接证据为零，但 CHARMM 碳水原生覆盖 fucose/rhamnose 是重大红利

## 版本记录

- **v1.0（2026-04-12）**：前 3 维度（§1–§5）落地
- **v2.0（2026-04-12）**：第二轮 4 维度追加（§6–§10），含完整采样方案 + 分析栈 + 自由能决策 + ascaroside 行动计划；Methodology 更新至 §11
- **v3.0（2026-04-16）**：第三轮新增 §12 GPCR-Gα 蛋白复合物 MD 文献调研，覆盖 chimeric Gα MD 先例（Tawfeeq 2025）+ 酵母 GPCR-Gα MD（Ramasamy 2025）+ 技术栈兼容性确认 + 模拟时长推荐 + 关键缺口声明
- **v3.1（2026-04-17）**：§12 引用勘误（Tsai→Tawfeeq）+ §12.1 补充 Velazhahan 2021 MD（此前仅作结构来源引用）+ §12.5 "零篇"声明修正为"仅 2 篇 Ste2-Gpa1 + 仅 1 篇 chimeric Gα"（后续 2026-05-06 已降级为 pending source audit）
- **v3.2（2026-05-06）**：§12 source audit：Ramasamy→Mohanty，Ranganathan→Renault，Jakowiecki→Miszta，Memprot/Casiraghi/Tawfeeq 方法迁移降级；only-N novelty claim 暂停使用。
