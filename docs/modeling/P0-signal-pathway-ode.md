---
direction: P0-signal-pathway-ode
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-05-25
---

# P0: 信号通路 ODE 建模（酵母 STE2）

> 来源: PRD v3 §3.2 | iGEM 评审定位: 直接支撑湿实验设计
>
> **底盘已锁定**: *S. cerevisiae* + 内源 STE2 通路 + 嵌合 Gpa1 + **基因组单拷贝整合**（2026-04-11，PI 确认）。详见 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md) / [overview-v4](../prd/overview-v4.md)。
>
> 本方向走**完整酵母 STE2 ODE 模型**，参数源 Shaw 2019 / Kofahl 2004 / Yi 2003 / Brown 2000 / Ladds 2005 / Lengger 2020-2022 / Fan 2024 / Fan & Yuan 2023。丝状真菌 ODE 表格（下方）保留为**历史备选 / 已不激活**。
>
> **2026-05-20 输入接口校准**：P0 docking 线已提供刷新后的候选标签、双通道方向和相对排序；ODE 不直接使用 Vina ΔG 换算 Kd。配体结合/激活参数先作为文献校准或参数扫描变量，待 Hu2024/Kuo2024/酵母 GPCR 文献与后续湿实验剂量响应确认后再固定。
>
> **2026-05-24 Stage 3 exact extraction**：抽取进展写入 `tmp_papers/ode_api_refresh_20260521/stage2_value_extraction_matrix.md` 的 Stage 3 addendum；它仍是证据包，不是最终参数表。Fan 2024 DOI/title 已与 `literature-matrix.md`、本地 summary、Zotero `WJVMJSNS` 和 API 记录一致；官方 Elsevier Supplementary Table 3-4 已解决 Fan 源上下文 Kc 冲突，但这些行只作为 CaSte2/GAL biosensor source-context `fixed from source`，项目 Gpr-ascr reporter gain/Kc/Hill/Emax 仍是 `wet-lab required`。Shaw/Kofahl 官方 BioModels SBML 已记录 species/reaction/parameter 指针，但速率值仍因单位/source-table 映射未完成而 `do-not-use`；Yi 速率表、Tehseen 全文仍在 full-text/Zotero queue。
>
> **2026-05-25 reporter 架构更新**：按用户确认和实验方案附件，输出层拓扑更新为 `异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色`。这确认的是架构，不固定具体色素、整合位点、实际 copy number、gain、Kc/Hill/Emax 或显色时间；这些仍是 `wet-lab required` 或 ODE 扫参变量。

## 解决什么问题

信号链路的定量预测:
- 系统能检测的最低 ascr 浓度是多少？
- 放大倍数如何选择？
- 背景泄漏对假阳性的影响？

**iGEM 价值**: 预测放大回路参数范围 → 湿实验据此选择 GAL4 promoter 强度 → 测量实际输出 → 用数据校准模型 → 完成 DBTL cycle。

## 当前形态、缺口与完整形态

### 当前已完成

- 文献证据与参数状态整理：`tmp_papers/ode_api_refresh_20260521/stage2_value_extraction_matrix.md` 作为证据包，`fixed from source` / `literature prior` / `scenario prior` / `wet-lab required` / `do-not-use` 标签已进入本文。
- docking 输入接口整理：docking 只提供候选标签、Channel A/B 方向、相对排序和 IFP 线索；不把 docking ΔG 换算 Kd/EC50。
- 湿实验校准需求整理：dose-response、time-course、basal leak、Emax、Hill、表达/膜定位、reporter dynamic range 和 chimeric Gpa1 coupling 都已列为替换条件。
- reporter 输出层架构已确认：sTF -> GAL 多拷贝放大 -> 色素显色。

### 当前缺口

- 未写 ODE solver；当前仓库没有 `src/modeling/ode/` 下的 Python 求解器、模型模块或 runner。
- 未生成 ODE 参数 config、模拟 CSV、剂量响应图、拷贝数敏感性图或泄漏/动态范围图。
- 未生成最终参数表；Shaw/Kofahl/Yi 等速率常数仍需 source-table、unit 和 kinetic-law 映射后才能决定是否进入数值模型。
- 未完成项目自身 wet-lab calibration；Gpr-ascr 的 Kd/EC50-like、Emax、Hill、basal leak、coupling efficiency 和 reporter gain 仍不能固定。

### 完整完成后的形态

完整 ODE v0.1 不只是一个 `.py` 脚本，而应包含：

- Python solver：用 SciPy/NumPy 实现 pathway ODE、dose-response sweep、copy-number sweep 和 leakage sweep。
- 参数 config：分离文献先验、scenario prior 和 wet-lab calibrated 参数，避免把证据状态硬编码进 solver。
- 输出数据：`experiments/ode-model/` 下保存模拟 CSV 和参数扫描结果。
- 可视化：ascr 浓度 vs reporter 输出的剂量响应曲线、1/2/4 copy 拷贝数敏感性图、basal leak/动态范围图、检测限或可判读窗口图。
- model-experiment feedback 表：把每个 `wet-lab required` 参数对应到实验 readout 和替换条件。

## 通路结构（已锁定酵母）

```
异源 Gpr 受体（Gpr2/Gpr3；GprC 仅作探索备选）
    │ ascr#18 / ascr#3 结合（Kd/EC50 为文献校准或参数扫描变量）
    ▼
嵌合 Gpa1（C 端嫁接真菌 Gα C 端，由 P0-chimeric-gprotein 提供 5/10/15 三档候选）
    │ GTP 结合 → Gβγ 释放
    ▼
Ste20 → Ste11 → Ste7 → Fus3 (MAPK 级联)
    │ 磷酸化
    ▼
Ste12（转录因子）
    │ 驱动 sTF 输出层
    ▼
sTF（Ste12 PRD-Gal4DBD 类融合转录因子）
    │ GAL 多拷贝放大
    ▼
色素显色 reporter
```

**基线假设**：所有可调元件按**基因组单拷贝**整合于同一位点；不使用 CEN/2μ 质粒（避免拷贝数漂移破坏下游线性度）。

> **GAL 输出层警告**：Fan et al. 2024 的 GAL4 级联放大方案与 Fan & Yuan 2023 的 GAL regulon 输出层均在不同构建背景下定量验证。在本项目单拷贝底盘下，GAL 多拷贝放大的实际增益、背景泄漏和显色时间必须重新校准；“多拷贝放大”是输出层设计变量，不等同于已经决定使用 2μ 质粒或某个固定拷贝数。

## 历史备选（已不激活）

> 2026-04-11 底盘锁定酵母后，丝状真菌方案不再使用。下表保留为历史记录。

| 维度 | 酵母方案（策略 B，**已选**） | ~~丝状真菌方案（策略 A）~~ |
|------|-------------------|---------------------|
| 通路结构 | Gpr → 嵌合 Gpa1 → Ste11/Ste7/Fus3 MAPK → 报告基因 | ~~Gpr → 内源 Gα → MAPK/PKA → 内源响应启动子~~ |
| 参数可获取性 | ★★★★★ | ★★☆☆☆ |
| 建模可行性 | 高: 详细定量 ODE | 低: 粗粒度 Hill 函数 |
| 关键参考 | Shaw 2019 / Fan 2024 / Fan & Yuan 2023 / Ladds 2005 | ~~Hu 2024（间接推断）~~ |

## 方法路线

1. 将信号通路拆解为生化反应网络（Gpr → Gpa1 → MAPK → Ste12 → sTF → GAL 输出层 → 色素 reporter）
2. 用质量作用定律和 Hill 函数建立 ODE 模型，**显式包含拷贝数变量** N（基线 N=1）
3. 参数从文献获取或设为先验（Shaw 2019 / Kofahl 2004 / Yi 2003 / Brown 2000 / Ladds 2005 / Lengger 2020-2022 / Fan 2024 / Fan & Yuan 2023）
4. **拷贝数敏感性分析**：N=1（基线）/ N=2（异源单倍体复制）/ N=4（双 cassette 整合），评估线性度与动态范围
5. 灵敏度分析：哪些参数对最终输出影响最大？
6. 优化下游 reporter 输出层接口（sTF/GAL/色素架构已确认；具体 gain、copy number、leakage 和 time-course 待湿实验回填）
7. **与 P0-docking 联动**：读取刷新后的候选标签、Channel A/B 方向、D/balance 和相对排序；不要把 Vina ΔG 直接换算成 Kd。ODE 中的配体结合/激活参数用文献校准范围、湿实验剂量响应或敏感性扫描定义。

## ODE 输入接口（2026-05-20）

P0 docking 当前能提供：

- 候选集合与优先级：首选 `Gpr2_R59C + Gpr3_R167Y`；B 端备选 `Gpr3_V138M/R167P/R167C`；A 端备选 `Gpr2_R59F/R59T`；`GprC_Q411S` 仅作探索性备选并保留 GprC caveat。
- 每个候选的双通道方向：Channel A 偏 ascr#18，Channel B 偏 ascr#3。
- 相对排序证据：`sel_mut`、D、balance、IFP 接触差异，用于设定模型场景和优先级。
- WT Gpr2 / WT Gpr3 baseline 标签，用于湿实验和模型校准对照。

P0 docking 当前不能直接提供：

- 真实 Kd、kon/koff、EC50、Emax 或受体激活效率。
- Vina ΔG 到 Kd 的可直接套用换算因子。
- 异源 Gpr 与嵌合 Gpa1 在酵母中的偶联效率。

ODE 当前应这样消费 docking 输出：

1. 用 docking handoff 选定 receptor-ligand 场景集合，而不是生成固定 Kd 表。
2. 对每个 receptor-ligand pair 设置待校准参数：`K_L`/EC50-like half activation、ligand efficacy、basal activity、最大输出比例。
3. 用文献或湿实验剂量响应给这些参数设定先验范围；文献不足时做 log-scale 参数扫描。
4. 在报告中明确区分“docking 排名假设”和“ODE 数值参数假设”。

## 参数证据矩阵与校准计划（2026-05-23/24）

本节来自 API-first 二阶段抽取文件：`tmp_papers/ode_api_refresh_20260521/stage2_value_extraction_matrix.md`。它是 ODE 准备证据包，不是最终参数表。

状态标签：

- `fixed from source`：可固定模型结构、变量定义、方法或来源内定义，不代表可迁移所有数值。
- `literature prior`：可作为先验范围、情景倍率或工程边界，进入敏感性分析。
- `scenario prior`：文献不足时的操作性扫描范围，必须标注为假设。
- `wet-lab required`：必须由本项目 dose-response、time-course、表达/定位或偶联实验校准。
- `do-not-use`：不得进入 ODE 数值参数。

### Stage 3 exact pointer checkpoint（2026-05-24）

| 模块 | exact pointer | 状态 | 用法/队列 |
|------|---------------|------|-----------|
| 酵母 GPCR-MAPK 拓扑 | Shaw 2019 `10.1016/j.cell.2019.02.023`, "Engineering a Model Cell for Rational Tuning of GPCR Signaling", Fig. 1-4 / Fig. S1-S4 / BioModels `MODEL1901300001` and `MODEL1901300002`; Kofahl 2004 `10.1002/yea.1122`, "Modelling the dynamics of the yeast pheromone pathway", BioModels `BIOMD0000000032` | topology and SBML species/reaction/parameter names `fixed from source`; rate constants `do-not-use` until unit/source-table mapping | 可固定模块顺序和状态变量类别；速率常数留在 full-text/SBML queue，不进入当前 ODE 参数 |
| G protein cycle | Yi 2003 `10.1073/pnas.1834247100`, "A quantitative characterization of the yeast heterotrimeric G protein cycle" | source candidacy `literature prior`; rate constants `do-not-use` until full-text extraction | API exact run有 rate-limit caveat，本地 Zotero 未命中；保留全文队列 |
| 异源 GPCR-Gpa1 偶联 | Brown 2000 `10.1002/(SICI)1097-0061(20000115)16:1<11::AID-YEA497>3.0.CO;2-K`, Table 3; Ladds 2005 `10.1016/j.tibtech.2005.05.007`, Fig. 1/Fig. 3; Tehseen 2014 `10.1371/journal.pone.0111429` | `literature prior`; project coupling `wet-lab required` | 只能给偶联和 basal leak 宽先验；不能转移成项目 EC50 |
| reporter / GAL 放大 | Fan 2024 `10.1016/j.bios.2024.116058`, Methods 2.3-2.6 / Fig. 1-4 / official Supplementary Table 3-4; Fan C & Yuan 2023 `10.1016/j.crmeth.2023.100647`, Fig. 2F; Miettinen 2022 `10.1038/s41467-022-31357-6`, Fig. 1b/Fig. 2 | equations and Fan source-context S4 rows `fixed from source`; gains/time scales `literature prior`; project output/reporter parameters `wet-lab required` | 可用 Hill/LOD/LOQ 定义和输出层结构；Fan S4 只作 CaSte2/GAL source-context，不固定项目 Gpr-ascr Kc/Hill/Emax |
| native fungal Gpr identity / docking boundary | Kuo 2024 `10.1038/s41564-024-01679-w`, Methods co-IP/docking and Fig. 3c; Hu 2024 `10.1038/s41564-024-01731-9`, Methods p.1760 / Extended Data Tables 2-3 | receptor identity `fixed from source`; docking scores `do-not-use`; project affinity `wet-lab required` | 支持受体身份/机制背景，不提供可迁移 `Kd/EC50/kon/koff/Emax` |
| identifiability / scan strategy | Simpson & Maclaren 2023 `10.1371/journal.pcbi.1011515`, Fig. 1; Gutenkunst 2007 `10.1371/journal.pcbi.0030189`, Fig. 1; Raue 2009 `10.1093/bioinformatics/btp358` | `literature prior` for method | 只支持校准/可识别性 workflow，不提供生物参数 |

#### BioModels/SBML exact pointer checkpoint

| 模型 | exact file pointer | 已抽取内容 | 当前状态 |
|------|--------------------|------------|----------|
| Shaw `MODEL1901300001` | Official download `https://www.ebi.ac.uk/biomodels/model/download/MODEL1901300001`; main `Yeast_Ternary.xml`, sha256 `b92d287bc9d21460052960ffda0083ca362a3e1097057dcc3951efcefba3bde4`; BioModels name "Shaw 2018 - Yeast GPCR Ternary Complex Model", SBML L2V4, `NON_CURATED` | `xmllint`: 18 species, 0 reactions, 23 global parameters, 1 compartment. Species: `R`, `LR`, `Rstar`, `LRstar`, `RG`, `LRG`, `RstarG`, `LRstarG`, `G`, `aGDP`, `bg`, `aGTP`, `bgstar`, `Ste5`, `bgstarSte5`, `bgSte5`, `L`, `observable`. Parameter ids include `kLp`, `kLm`, `kactp`, `kactm`, `kGp`, `kGm`, `kGRAp`, `kGRAm`, `khydp`, `khydm`, `kGTPp`, `kEp1`, `kEp2`, `kEm1`, `kEm2`. | Names/source pointer `fixed from source`; numerical values `do-not-use` until Shaw tables/methods/unit mapping are extracted. |
| Shaw `MODEL1901300002` | Official download `https://www.ebi.ac.uk/biomodels/model/download/MODEL1901300002`; main `Yeast_Hillslope.xml`, sha256 `3f4a2b218a64b066f9db75cf1a9044ee27cff71b6a5a0340707de9d2c7879e52`; SBML model name "Shaw2019 - Digital biosensor model from Yeast" | `xmllint`: 24 species, 0 reactions, 29 global parameters, 1 compartment. Species include `R1`, `Rstar1`, `Goff1`, `Gon1`, `Effector1`, `Gon1Effector1`, `preafactor`, `afactor`, `R2`, `Rstar2`, `Goff2`, `Gon2`, `Effector2`, `Gon2Effector2`, `preGFP`, `L`, `Bar1`, `inactiveBar1`, `GFP`. Parameter ids include `k11`, `k21`, `k31`, `k41`, `k51`, `k61`, `k71`, `a1`, `a11`, `a21`, `b1`, `b11`, `b21`, `k8`, `k9`, `k10`. | Names/source pointer `fixed from source`; numerical values `do-not-use` until equation/unit/source-note extraction is complete. |
| Kofahl `BIOMD0000000032` | Official download `https://www.ebi.ac.uk/biomodels/model/download/BIOMD0000000032`; master `BIOMD0000000032_url.xml`, sha256 `45cec22aefca6b49e78fd3ad5105748559df3e1dcc3bf5ffd787fda8bc6e60df`; model id/name `Kofahl2004_PheromonePathway` | `xmllint`: 37 species, 47 reactions, 0 global parameters, 2 compartments; species include `alpha`, `Ste2`, `Ste2a`, `Gabc`, `GaGTP`, `Gbc`, `GaGDP`, `Ste5`, `Ste11`, `Ste7`, `Fus3`, `Ste20`, `Fus3PP`, `Ste12`, `Ste12a`, `Bar1`, `Far1`, `Sst2`; reaction ids `v1`-`v47`. `curation_notes.txt`: model units are nanoMolar while publication plots are microMolar; WT parameters encoded and mutant variants require Table 5 changes. | Species/reaction topology `fixed from source`; kinetic-law constants `do-not-use` until Fig. 1, kinetic laws, units, and Table 5 are mapped. |

#### API caveats kept with the matrix

- Shaw exact API run: target Cell article is P0002; P0001 is a Faculty Opinions recommendation DOI, so citations must use `10.1016/j.cell.2019.02.023`.
- Yi 2003 exact API run: Crossref returned HTTP 429 and the target was not recovered as a usable top record; all G protein-cycle values remain `do-not-use`.
- `gpcr_gpa1_coupling`, `parameter_strategy`, and `heterologous_gpa1_exact` runs have Crossref 429 or empty-result caveats; use seed/title/Zotero/full-text extraction before promoting values.
- Hu/Kuo exact API run: Hu 2024 appears, but P0001 is irrelevant "DOI reserve for Community Guide 024" and Kuo 2024 was not recovered as a top usable record; local DOI-verified summaries remain the current pointer, and docking scores stay `do-not-use`.

| 问题 | 参数/模块 | 主要来源 | 当前状态 | ODE 使用方式 |
|------|-----------|----------|----------|--------------|
| 酵母 GPCR-MAPK 通路拓扑是否可先固定？ | GPCR → Gpa1/Gbetagamma → Ste20/Ste11/Ste7/Fus3 → Ste12/reporter | Shaw 2019 `10.1016/j.cell.2019.02.023`; Kofahl 2004 `10.1002/yea.1122`; Yi 2003 `10.1073/pnas.1834247100` | topology `fixed from source`; rate constants `do-not-use` until SBML/full-text extraction | 先固定模块顺序和状态变量类别；SBML/补充表未抽完前不固定具体速率 |
| Gpr2/Gpr3/GprC 配体结合和激活强度能否由文献固定？ | `Kd`, `kon`, `koff`, EC50/Kc, Emax, Hill | Hu 2024 `10.1038/s41564-024-01731-9`; Kuo 2024 `10.1038/s41564-024-01679-w` | `wet-lab required`; docking constants `do-not-use` | Hu/Kuo 支持受体身份、机制和 native 条件，不提供可迁移 wet `Kd/EC50`；本项目只能先扫参 |
| 异源 Gpr 与嵌合 Gpa1 偶联如何处理？ | 偶联效率、basal leak、G protein cycle | Brown 2000 `10.1002/(SICI)1097-0061(20000115)16:1<11::AID-YEA497>3.0.CO;2-K`; Ladds 2005 `10.1016/j.tibtech.2005.05.007`; Lengger 2020 `10.1093/femsyr/foz087`; Lengger 2022 `10.1021/acssensors.1c02061`; Tehseen 2014 `10.1371/journal.pone.0111429` | `literature prior`; project coupling `wet-lab required` | 用作偶联效率和 basal leak 的宽先验；Gpr2/Gpr3 与项目 chimeric Gpa1 必须实测 |
| reporter / promoter / GAL4 放大能否迁移？ | reporter gain、pFUS1/GAL4/sTF 输出、LOD/LOQ、T50、copy-number effect | Fan 2024 `10.1016/j.bios.2024.116058`; Fan & Yuan 2023 `10.1016/j.crmeth.2023.100647`; Miettinen 2022 `10.1038/s41467-022-31357-6`; Shaw 2019 | `literature prior`; single-copy gain `wet-lab required` | 用作输出层结构和增益/时间尺度先验；单拷贝整合下必须重新标定 |
| 缺少 binding 参数时如何建模？ | log-scale scan、profile likelihood、sloppy sensitivity | Simpson & Maclaren 2023 `10.1371/journal.pcbi.1011515`; Gutenkunst 2007 `10.1371/journal.pcbi.0030189`; Raue 2009 `10.1093/bioinformatics/btp358` | `literature prior` for method | 第一版只输出参数接口、扫描范围和可识别性计划；数据到位后做 profile likelihood |
| docking 刷新结果如何进入 ODE？ | candidate label、Channel A/B、relative rank、IFP clue | `ratio_channel_report.md`; `ratio_pairings.csv`; `wet-lab-handoff-P0-docking.md`; 2026-05-19/20 logs | constants `do-not-use`; labels/ranking usable | 只定义场景集合和优先级；严禁把 Vina Delta G 换算为 `Kd/EC50` |

### 建议扫描范围（非定论）

| 参数 | 初始建议 | 状态 | 替换条件 |
|------|----------|------|----------|
| `K_L` / EC50-like ligand half activation | 主扫描 `1e-9` 到 `1e-3` M；压力测试 `1e-12` 到 `1e-2` M | `scenario prior` | 本项目 dose-response 给出 EC50/Kc 后替换 |
| Hill coefficient | `0.5` 到 `3` | `scenario prior` | 本项目剂量响应拟合后替换 |
| ligand efficacy / Gpr-Gpa1 coupling efficiency | 归一化 `1e-3` 到 `1` | `scenario prior` | chimeric Gpa1 functional coupling 数据后替换 |
| basal leak | 归一化 `1e-4` 到 `0.2` | `scenario prior` | no-ligand reporter 和阴性对照后替换 |
| reporter amplification gain | `1` 到 `100`，按 pFUS1 direct 或 GAL4/sTF 方案分情景 | `scenario prior` | reporter 构型、copy number 和 time-course 数据后替换 |

### 湿实验需求表

| 对象/决定 | assay | ligand / control panel | readout | ODE 替换条件 | 状态 |
|-----------|-------|------------------------|---------|---------------|------|
| WT Gpr2、WT Gpr3、`Gpr2_R59C`、`Gpr3_R167Y` | 同一 chassis/reporter 背景下的 dose-response | ascr#18 与 ascr#3；无配体、低 nM、uM、mM 点 | 选定 reporter 输出 + OD/growth 归一化 | 替换 `K_L`/EC50-like、Emax、Hill、basal leak、A/B 通道分离的 `scenario prior` | `wet-lab required` |
| 备选突变：`Gpr3_V138M/R167P/R167C`、`Gpr2_R59F/R59T`、探索性 `GprC_Q411S` | 与 WT 完全同版 dose-response panel | 同上；GprC 只作探索，除非湿实验有响应 | 同上 | 验证/降级 docking 场景标签和相对优先级；不从 docking score 换算 affinity | `wet-lab required` |
| reporter 方案：pFUS1 直连、GAL4/sTF、荧光、lacZ、NanoLuc 或显色模块 | reporter-specific dose-response、basal/no-ligand、dynamic range、noise floor、饱和区 | 至少包含 alpha-factor 正控和选定 ascaroside panel | fluorescence/lacZ/luminescence/color + OD；记录仪器设置和 incubation time | 替换 reporter gain、Emax、noise、degradation/dilution、LOD/LOQ 假设 | `wet-lab required` |
| 底盘编辑：`Δsst2`、`Δbar1`、Gpa1 过表达、GAL4 feedback | 每项编辑的阳性/阴性对照矩阵 | pathway 正控 + selected ascaroside panel | matched reporter output + growth/viability | 区分灵敏度提升、basal leak、生长惩罚和 reporter artifact | `wet-lab required` |
| time-course | 早期 pathway/reporter 激活和 2-8 h 稳态输出 | 无配体、正控、每构建至少一个低/近 EC50/高 ascaroside 浓度 | minutes-hours early points + 2-8 h reporter window；尽量包含 OD/growth | 替换 response delay、reporter production/degradation/dilution 和稳态假设 | `wet-lab required` |
| 表达/定位 | WT/mutant Gpr2/Gpr3/GprC 膜定位和表达量 | 无配体 + 代表性 ligand 条件（若 ligand 影响 trafficking） | tagged receptor imaging/flow/western as available | 区分 trafficking/expression failure 与 ligand activation / G protein coupling failure | `wet-lab required` |
| chimeric Gpa1 coupling | 同一 reporter/chassis 的功能偶联 assay；可选 co-IP/BRET-like 相互作用验证 | yeast MAPK 正控 + selected ascaroside panel | reporter output、basal/no-ligand、可选 protein interaction readout | 替换 coupling efficiency 和 basal Gbetagamma leak；决定 Gpr2/Gpr3 native Gpa2 coupling 能否迁移 | `wet-lab required` |

### 建模建议

- 可固定：酵母 pheromone/MAPK 拓扑、状态变量类别、reporter 方程形式、LOD/LOQ/Hill fitting 定义，以及 docking 刷新后的候选标签集合。
- 可作为文献先验：异源 GPCR-Gpa1 偶联效率量级、basal leak 风险、reporter/GAL4 放大和时间尺度。
- 只能作为 scenario prior：Gpr-ascr 半激活浓度、efficacy、Hill、basal leak、reporter gain 的项目数值。
- 必须等待湿实验：每个 mutant/ascr pair 的 `Kd/kon/koff/EC50/Kc/Emax/Hill`、表达/定位、chimeric Gpa1 coupling、单拷贝 reporter gain。
- 禁用：Vina 或 SwissDock Delta G 到 `Kd/EC50` 的直接换算，旧 `Gpr2_M327A + Gpr3_V138T` Top 说法，以及未刷新 IFP 机制解释。

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (SciPy, NumPy, Matplotlib) | ODE 求解与可视化 |
| COPASI | 反应网络建模 GUI（快速原型） |
| PySB | Python 代码构建生化模型 |
| BioCRNpyler + AutoReduce | 从详细反应到简化 ODE 的自动化 |

## 参数与数据来源

### 酵母方案参数接口（状态化）

| 参数 | 来源 | 状态 | 备注 |
|------|------|------|------|
| 异源 Gpr 配体结合/激活参数 | [P0-molecular-docking](P0-molecular-docking.md) 提供候选标签与相对排序；Kuo 2024 / Hu 2024 支持受体身份和 docking 边界 | `wet-lab required`; docking constants `do-not-use` | 不直接由 Vina/SwissDock Delta G 换算；先做参数范围/敏感性扫描 |
| 嵌合 Gpa1/G protein cycle 速率 | Shaw 2019 / Kofahl 2004 / Yi 2003 | source candidacy `literature prior`; numeric rates `do-not-use` until full-text/SBML unit mapping | C 端嫁接对 GTPase 域速率的影响不能从文献直接固定；coupling 效率需湿实验 |
| Gβγ 释放 / Sst2 RGS | Shaw 2019 / Kofahl 2004 / Yi 2003 | topology and source variable names `fixed from source`; rates `do-not-use` until SBML/full-text mapping | 可先固定变量类别；速率等 SBML/补充表抽取后再决定 |
| MAPK 级联动力学（Ste20/Ste11/Ste7/Fus3） | Shaw 2019 / Kofahl 2004 | topology and Kofahl reaction ids `fixed from source`; rates `do-not-use` until SBML/full-text mapping | 不在本轮写 solver 或最终 rate table |
| Ste12 转录与 reporter 方程 | Shaw 2019 / Fan C & Yuan 2023 / Lengger 2020 | `literature prior` | 具体输出增益依赖 reporter 构型和单拷贝整合 |
| sTF / GAL / 色素输出层 | Fan 2024 / Fan C & Yuan 2023 / Miettinen 2022 / Shaw 2019；2026-05-25 用户确认实验方案附件 | topology and Fan source-context Table S4 rows `fixed from source`; project gains/Kc/Hill/Emax `wet-lab required` | sTF -> GAL 多拷贝放大 -> 色素显色作为结构进入模型；Fan S4 不迁移为项目 Gpr-ascr 参数 |
| GAL4 正反馈参数（若使用） | Fan 2024 / Fan C & Yuan 2023 | `literature prior`; single-copy gain `wet-lab required` | **拷贝数敏感**：单拷贝下增益需重新评估 |
| 拷贝数 N | 决策 003 / overview-v4 的单拷贝底盘背景；ODE 扫描 N=1/2/4 | baseline `fixed from source`; variants `scenario prior` | 基线 1 copy；2/4 copy 只做灵敏度情景 |

### ~~丝状真菌方案参数~~（已不激活）

> 历史备选，不再使用。原表保留：

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| ~~Gpr-Gα 偶联速率~~ | ~~Hu 2024（间接推断）~~ | ★★☆☆☆ |
| ~~MAPK/PKA 动力学~~ | ~~几乎无文献值~~ | ★☆☆☆☆ |

## 产出定义

- [ ] 系统剂量-响应曲线（ascr 浓度 vs 报告基因输出，覆盖 refreshed docking handoff 候选场景）
- [ ] 灵敏度极限预测（最低可检测浓度）
- [ ] 动态范围与放大倍数优化建议
- [ ] **拷贝数敏感性分析（1/2/4 copy 对比）** —— 基线整合策略下的核心交付
- [ ] 参数灵敏度分析报告（哪些参数的不确定性主导输出）
- [ ] 与湿实验的 model-experiment feedback loop 对照表
- [ ] 产出文件位置: `experiments/ode-model/`

## 代码与实验关联

- **代码路径**: `src/modeling/ode/`（当前未创建/未实现）
- **产出路径**: `experiments/ode-model/`
- **湿实验对接**:
  - 本方向产出 → 通路工程组: 推荐 GAL4 promoter 强度、放大回路参数
  - 湿实验反馈 → 本方向: 实际剂量-响应数据，校准模型参数

## 学习成本与依赖

- **难度**: ★★☆☆☆（有 Python 基础，主要学 ODE 建模思路）
- **学习资源**: 见 [学习路线图 阶段一 + 阶段三](../learning/roadmap.md)
- **关键参考**: Shaw et al. 2019 *Cell* 中的模型可作为直接起点

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.2 提取，含双底盘策略 | 文档体系搭建 |
| 2026-04-11 | **v2.0** | status not_started → in_progress；锁定酵母 STE2 路径；新增基因组单拷贝整合基线 + 拷贝数敏感性分析；丝状真菌表保留为历史；与 P0-docking 双通道分析联动 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |
| 2026-05-20 | **v2.1** | 修正 docking→ODE 输入接口：docking 只提供候选标签/方向/排序，Kd/EC50/efficacy 进入文献校准或参数扫描门控 | docking-repro full refresh 完成，但 Vina ΔG 不可直接换算 Kd |
| 2026-05-23 | **v2.2** | 新增参数证据矩阵与校准计划；按 `fixed from source` / `literature prior` / `scenario prior` / `wet-lab required` / `do-not-use` 标注 ODE 参数状态 | API-first ODE 文献二阶段抽取完成，进入建模准备但不生成定论参数表 |
| 2026-05-24 | **v2.3** | 同步 Stage 3 exact pointer checkpoint、湿实验需求拆分和状态化参数接口；继续保留 `Vina Delta G != Kd/EC50` gate | 文献抽取进入 exact pointer/manual queue 阶段；未写 ODE 代码，未生成定论参数表 |
| 2026-05-25 | **v2.4** | 增补当前形态/缺口/完整形态说明；更新 reporter 输出架构为 sTF -> GAL 多拷贝放大 -> 色素显色；明确未写 ODE solver | 用户确认实验方案附件中的 reporter 路径，需同步总览图缺口说明 |

## 进展记录

- 2026-05-24：Stage 3 exact extraction 已补入证据矩阵；P0 ODE 文档只同步证据状态、手动队列和湿实验需求，不输出 solver、rate table 或最终参数表。
- 2026-05-25：同步 reporter 输出架构和 ODE v0.1 完整形态定义；本轮仍未写 ODE solver、config、CSV 或 plots。

## 与其他方向的依赖关系

- **输出到**:
  - [P1-soil-diffusion](P1-soil-diffusion.md): 灵敏度极限 → 检测有效距离计算
  - [P1-bayesian-inference](P1-bayesian-inference.md): 剂量-响应曲线 → 正向模型组件
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): refreshed handoff 候选标签、Channel A/B 方向、相对排序和 WT baseline；Kd/EC50/efficacy 需文献或湿实验校准，不由 Vina ΔG 直接换算
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 偶联效率 → ODE 中 Gpr-Gpa1 偶联速率
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
