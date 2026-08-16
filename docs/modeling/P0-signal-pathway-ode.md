---
direction: P0-signal-pathway-ode
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-08-16
---

# P0: 信号通路 ODE 建模（酵母 STE2）

> 来源: PRD v3 §3.2 | iGEM 评审定位: 建立模型分析、证据缺口与后续 DBTL handoff 的可追溯链路
>
> **底盘已锁定**: *S. cerevisiae* + 内源 STE2 通路 + 嵌合 Gpa1 + **基因组单拷贝整合**（2026-04-11，PI 确认）。详见 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md) / [overview-v4](../prd/overview-v4.md)。
>
> 本方向走**完整酵母 STE2 ODE 模型**，参数源 Shaw 2019 / Kofahl 2004 / Yi 2003 / Brown 2000 / Ladds 2005 / Lengger 2020-2022 / Fan 2024 / Fan & Yuan 2023。丝状真菌 ODE 表格（下方）保留为**历史备选 / 已不激活**。
>
> **2026-07-30 docking 输入暂停**：旧 P0 docking mutant shortlist、双通道排序和 IFP 因 AF3 mutant/WT frame 缺陷已撤回，ODE 当前不得消费这些 mutant 标签或优先级。WT Gpr2/Gpr3、ascr#18/ascr#3 的场景结构与参数扫描框架可继续维护；mutant 场景必须等待 frame-repaired 全量排名。配体结合/激活参数仍作为文献校准或参数扫描变量，待独立文献与湿实验剂量响应确认后再固定。
>
> **2026-05-24 Stage 3 exact extraction**：当时抽取的来源和状态保留在本文 Stage 3 checkpoint；它们不是最终参数表。Fan 2024 DOI/title 已与 `literature-matrix.md`、本地 summary、Zotero `WJVMJSNS` 和 API 记录一致；官方 Elsevier Supplementary Table 3-4 已解决 Fan 源上下文 Kc 冲突，但这些行只作为 CaSte2/GAL biosensor source-context `fixed from source`，项目 Gpr-ascr reporter gain/Kc/Hill/Emax 仍是 `wet-lab required`。Shaw/Kofahl 官方 BioModels SBML 已记录 species/reaction/parameter 指针，但速率值仍因单位/source-table 映射未完成而 `do-not-use`；Yi 速率表、Tehseen 全文仍在 full-text/Zotero queue。
>
> **2026-05-25 reporter 架构更新**：按用户确认和实验方案附件，输出层拓扑更新为 `异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色`。这确认的是架构，不固定具体色素、整合位点、实际 copy number、gain、Kc/Hill/Emax 或显色时间；这些仍是 `wet-lab required` 或 ODE 扫参变量。
>
> **2026-07-28 可执行原型更新**：仓库现已有归一化 Phase 0 solver/time-course 和 Phase 1 工程情景扫描。当前结果只支持显式 `scenario_prior` 下的条件比较；真实 `Kd/EC50`、动力学常数、检测限、最佳 copy number 和最终构建推荐仍未校准。
>
> **2026-08-10 Phase 2A 边界校准**：机器合同固定 18 个模型字段的筛选范围、主/诊断 ligand contexts、输出指标，以及参数—潜在可观测量—证据缺口映射。`ratio_color_8h` 对零/近零计算对照 denominator 使用 `NaN`、显式 validity flag 和 reason；正 ligand 计算情景缺失 matched control 时 runner fail closed。Phase 2A 仍是 `scenario_prior` 分析合同；Phase 2B 负责模型侧敏感性，Phase 2C 负责可识别性，具体实验接口进入后续 DBTL handoff gate。
>
> **Phase 2B 实现与证据边界（核验至 2026-08-16）**：局部时变敏感性、Morris、条件性 Sobol 和重点双参数曲面的 runner、配置、测试及设计预检已具备，允许用于 `scenario_prior` 技术诊断。完整长运行数值尚缺仓库内紧凑结果包与恢复指针；候选冻结需在来源哈希、输出校验和、生成命令、软件身份和恢复入口完成审查后接纳。实现经过见 [2026-08-07-yrx 日志](../logs/2026-08-07-yrx.md)，项目当前状态回 [INDEX](../INDEX.md)。

## 解决什么问题

信号链路的定量预测:
- 系统能检测的最低 ascr 浓度是多少？
- 放大倍数如何选择？
- 背景泄漏对假阳性的影响？

当前 Phase 0/1 原型只建立回答这些问题所需的可执行接口和条件性扫描，
不把归一化轴解释成真实浓度，也不输出真实检测限或最终优化结论。

**iGEM 价值**: 建立可复现参数空间 → 分析敏感性和可识别性 → 与团队实验方案共同形成 DBTL handoff → 用项目证据校准模型。

## 当前形态、缺口与完整形态

### 当前已完成

- 文献证据与参数状态整理：Stage 3 来源 checkpoint 保留在本文，`fixed from source` / `literature prior` / `scenario prior` / `wet-lab required` / `do-not-use` 标签已进入当前参数登记。
- docking 输入接口边界已整理：旧 mutant 候选标签、Channel A/B 排序和 IFP 暂停消费；WT 场景结构可用，Kd/EC50 由独立 binding/calibration 证据或参数扫描定义。
- 参数已映射到潜在可观测量类别和证据缺口；当前合同不规定 assay、实验对照、采样设计或实验优先级。
- reporter 输出层架构已确认：sTF -> GAL 多拷贝放大 -> 色素显色。
- Phase 0 已实现 `src/modeling/ode/` 最小 solver、runner、严格 config 校验、161 点归一化 time-course CSV 和由 CSV 渲染的 PNG。
- Phase 1 已实现剂量 × 半响应、偶联 × 泄漏、1/2/4 copy × gain × 观察时间三组扫描；当前固定网格为 143 个情景（74 ligand + 69 一对一无 ligand controls）和 23,023 条完整 time-course。
- Phase 1 紧凑结果包已保存 scenario manifest、final metrics、共置 suite/base config 快照、代码/输入 hash、软件版本、摘要图和外部完整 time-course 的 payload manifest。
- Phase 2A 已固定 18 字段参数空间、输出指标、主/诊断 ligand contexts、潜在可观测量/证据缺口和 guarded ratio 合同；正 ligand 计算情景必须有 matched no-ligand control。
- Phase 2B 已实现局部时变敏感性、Morris、条件性 Sobol 和重点双参数曲面的 runner、配置、测试及设计预检。
- ODE 单元/合同测试覆盖严格 schema、有限数/整数、control effective-input 身份、一对一配对、零分母与缺失 control 防护、结果 scenario 集合一致、snapshot-only replay 和 `color_8h` 端点身份。

### 当前缺口

- 未生成最终参数表；Shaw/Kofahl/Yi 等速率常数仍需 source-table、unit 和 kinetic-law 映射后才能决定是否进入数值模型。
- 项目校准证据尚未进入模型；Gpr-ascr 的 Kd/EC50-like、Emax、Hill、basal leak、coupling efficiency 和 reporter gain 仍不能固定。
- 旧 docking mutant shortlist 已撤回；尚未把 frame-repaired 全量排名展开成逐 receptor-ligand 的可校准配置，当前归一化 suite 不代表具体 Gpr2/Gpr3–ascr 构建。
- Phase 2B 完整长运行结果尚缺仓库内紧凑结果包；结果接纳需要可恢复的来源与输出身份。
- Phase 2C 可识别性、校准拟合、不确定性传播和必要的逐级 pathway kinetic model 尚未实现；具体实验接口仍需通过后续 DBTL handoff gate。

### 完整完成后的形态

Phase 0/1 已交付可运行原型；走向校准 ODE v0.1 仍需：

- 把当前 lumped 原型与具体 receptor-ligand 场景、可追溯文献映射和项目校准证据连接。
- 在 config 中继续分离文献先验、scenario prior 和项目 calibrated 参数，任何状态升级都附带数据、单位、构建和拟合 provenance。
- 增加正式灵敏度/可识别性分析、校准拟合、不确定性传播和必要时的逐级通路结构。
- 只有在有单位的 calibration 数据进入后，才生成真实 ascr 浓度 dose-response、检测限或可判读窗口。
- DBTL handoff：在 Phase 2C 及适用的模型比较完成后，将模型证据与团队确认的方案、可行性、成本和资源共同转化为实验接口。

## 通路结构（已锁定酵母）

```
异源 Gpr 受体（Gpr2/Gpr3）
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
4. **拷贝数敏感性分析**：按 N=1/2/4 的分析分层评估线性度与动态范围；这些分层不构成实际构建选择
5. 灵敏度分析：哪些参数对最终输出影响最大？
6. 分析下游 reporter 输出层的参数影响、条件依赖和可识别性；具体实现进入后续 DBTL handoff gate
7. **与 P0-docking 联动**：当前只保留 WT Gpr2/Gpr3 与双配体的场景接口；mutant 候选标签、Channel A/B 方向、D/balance、相对排序和 IFP 等待 frame-repaired 全量结果。Vina ΔG 即使修复后也只支持相对排序；ODE 中的配体结合/激活参数用文献校准范围、湿实验剂量响应或敏感性扫描定义。

## ODE 输入接口（2026-07-30 withdrawal boundary）

P0 docking 当前允许提供：

- WT Gpr2 / WT Gpr3 与 ascr#18 / ascr#3 的场景标签，用于模型结构和未来校准对照。
- 已撤回的 mutant shortlist/ratio/IFP 只作历史 provenance，不用于当前场景优先级。

P0 docking 后续参数仍需独立证据：

- 真实 Kd、kon/koff、EC50、Emax 或受体激活效率。
- Kd/EC50 的 binding/calibration 映射。
- 异源 Gpr 与嵌合 Gpa1 在酵母中的偶联效率。

ODE 当前应这样消费 docking 输出：

1. 在 repaired shortlist 形成前，只建立 WT Gpr2/Gpr3 × ascr#18/ascr#3 的中性场景结构，不设置 mutant 候选优先级。
2. 新 mutant shortlist 通过全量 frame/geometry/ratio/IFP 审计后，再把合格 receptor-ligand pair 加入场景集合。
3. 用可追溯文献或项目校准证据设定先验范围；证据不足时做 log-scale 参数扫描。
4. 固定 Kd 表等待独立 binding/calibration 证据；报告中明确区分“docking 排名假设”和“ODE 数值参数假设”。

## 参数证据状态与分析边界（2026-05-23/24）

本节保留 API-first 二阶段抽取形成的来源 checkpoint。当前参数数值、范围和证据缺口分别回到配置、Phase 2A 机器合同和参数登记表。

状态标签：

- `fixed from source`：可固定模型结构、变量定义、方法或来源内定义；数值迁移需要匹配单位、体系条件和校准来源。
- `literature prior`：可作为先验范围、情景倍率或工程边界，进入敏感性分析。
- `scenario prior`：文献不足时的操作性扫描范围，必须标注为假设。
- `wet-lab required`：现有配置中的项目证据缺口标签，不指定 assay，也不代表逐参数独立测量；Phase 2C 评估候选观测类别的识别价值，是否测量及实施方式由后续 DBTL handoff 结合团队方案、可行性、成本和资源确定。
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
- Yi 2003 exact API run: Crossref returned HTTP 429; exact retrieval remains pending for the target record, and all G protein-cycle values remain `do-not-use`.
- `gpcr_gpa1_coupling`, `parameter_strategy`, and `heterologous_gpa1_exact` runs have Crossref 429 or empty-result caveats; use seed/title/Zotero/full-text extraction before promoting values.
- Hu/Kuo exact API run: Hu 2024 appears, but P0001 is irrelevant "DOI reserve for Community Guide 024"; Kuo 2024 exact top-record retrieval remains pending. Local DOI-verified summaries remain the current pointer, and docking scores stay `do-not-use`.

| 问题 | 参数/模块 | 主要来源 | 当前状态 | ODE 使用方式 |
|------|-----------|----------|----------|--------------|
| 酵母 GPCR-MAPK 通路拓扑是否可先固定？ | GPCR → Gpa1/Gbetagamma → Ste20/Ste11/Ste7/Fus3 → Ste12/reporter | Shaw 2019 `10.1016/j.cell.2019.02.023`; Kofahl 2004 `10.1002/yea.1122`; Yi 2003 `10.1073/pnas.1834247100` | topology `fixed from source`; rate constants `do-not-use` until SBML/full-text extraction | 先固定模块顺序和状态变量类别；SBML/补充表未抽完前不固定具体速率 |
| Gpr2/Gpr3 配体结合和激活强度能否由文献固定？ | `Kd`, `kon`, `koff`, EC50/Kc, Emax, Hill | Hu 2024 `10.1038/s41564-024-01731-9`（机制背景）；Kuo 2024 `10.1038/s41564-024-01679-w` | `wet-lab required`; docking constants `do-not-use` | 文献支持受体/机制背景，但不提供可迁移 wet `Kd/EC50`；本项目只能先扫参 |
| 异源 Gpr 与嵌合 Gpa1 偶联如何处理？ | 偶联效率、basal leak、G protein cycle | Brown 2000 `10.1002/(SICI)1097-0061(20000115)16:1<11::AID-YEA497>3.0.CO;2-K`; Ladds 2005 `10.1016/j.tibtech.2005.05.007`; Lengger 2020 `10.1093/femsyr/foz087`; Lengger 2022 `10.1021/acssensors.1c02061`; Tehseen 2014 `10.1371/journal.pone.0111429` | `literature prior`; project coupling `wet-lab required` | 用作偶联效率和 basal leak 的宽先验；Gpr2/Gpr3 与项目 chimeric Gpa1 必须实测 |
| reporter / promoter / GAL4 放大能否迁移？ | reporter gain、pFUS1/GAL4/sTF 输出、LOD/LOQ、T50、copy-number effect | Fan 2024 `10.1016/j.bios.2024.116058`; Fan & Yuan 2023 `10.1016/j.crmeth.2023.100647`; Miettinen 2022 `10.1038/s41467-022-31357-6`; Shaw 2019 | `literature prior`; single-copy gain `wet-lab required` | 用作输出层结构和增益/时间尺度先验；单拷贝整合下必须重新标定 |
| 缺少 binding 参数时如何建模？ | log-scale scan、profile likelihood、sloppy sensitivity | Simpson & Maclaren 2023 `10.1371/journal.pcbi.1011515`; Gutenkunst 2007 `10.1371/journal.pcbi.0030189`; Raue 2009 `10.1093/bioinformatics/btp358` | `literature prior` for method | 第一版只输出参数接口、扫描范围和可识别性计划；数据到位后做 profile likelihood |
| docking 修复结果如何进入 ODE？ | candidate label、Channel A/B、relative rank、IFP clue | frame-repaired run manifest、未来 ranking/IFP release；旧 `ratio_channel_report.md` / `ratio_pairings.csv` / shortlist 仅作历史边界 | 当前 mutant labels/ranking `withdrawn`; constants `do-not-use` | 修复后合格标签才可定义 mutant 场景；`Kd/EC50` 仍需独立 binding/calibration 证据 |

### 当前分析范围

[Phase 2A 参数空间](../../experiments/ode-model/configs/phase2a_parameter_space.csv) 是当前数值范围和分布的机器可读权威。ligand 轴保持归一化，当前范围不解释为有单位的实验浓度。

### 潜在可观测量与证据缺口

[Phase 2A 参数空间](../../experiments/ode-model/configs/phase2a_parameter_space.csv) 是参数—潜在可观测量—证据缺口映射的机器可读权威。Phase 2B 仅产生模型侧敏感性结果；Phase 2C 检查候选观测类别下的可识别性。具体 assay、实验对照、采样设计和实验优先级进入后续 DBTL handoff，并结合团队确认的实验方案、可行性、成本和资源。

### 建模建议

- 可固定：酵母 pheromone/MAPK 拓扑、状态变量类别、reporter 方程形式、LOD/LOQ/Hill fitting 定义，以及 WT Gpr2/Gpr3 场景结构。
- 可作为文献先验：异源 GPCR-Gpa1 偶联效率量级、basal leak 风险、reporter/GAL4 放大和时间尺度。
- 只能作为 scenario prior：Gpr-ascr 半激活浓度、efficacy、Hill、basal leak、reporter gain 的项目数值。
- 项目证据缺口：receptor-ligand 激活、通路偶联、层间转移和输出动力学仍缺少项目特异的可校准证据。
- 独立证据队列：Vina 或 SwissDock Delta G 到 `Kd/EC50` 的映射、旧 `Gpr2_M327A + Gpr3_V138T` Top 说法、未刷新 IFP 机制解释。

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
| 异源 Gpr 配体结合/激活参数 | [P0-molecular-docking](P0-molecular-docking.md) 当前只提供 WT 场景结构，mutant 标签/排序等待 repaired release；Kuo 2024 / Hu 2024 支持受体身份和 docking 边界 | `wet-lab required`; docking constants `do-not-use` | Vina/SwissDock Delta G 仅作排序背景；先做参数范围/敏感性扫描 |
| 嵌合 Gpa1/G protein cycle 速率 | Shaw 2019 / Kofahl 2004 / Yi 2003 | source candidacy `literature prior`; numeric rates `do-not-use` until full-text/SBML unit mapping | C 端嫁接对 GTPase 域速率的影响不能从文献直接固定；coupling 效率需湿实验 |
| Gβγ 释放 / Sst2 RGS | Shaw 2019 / Kofahl 2004 / Yi 2003 | topology and source variable names `fixed from source`; rates `do-not-use` until SBML/full-text mapping | 可先固定变量类别；速率等 SBML/补充表抽取后再决定 |
| MAPK 级联动力学（Ste20/Ste11/Ste7/Fus3） | Shaw 2019 / Kofahl 2004 | topology and Kofahl reaction ids `fixed from source`; rates `do-not-use` until SBML/full-text mapping | 当前 solver 将其压缩为一个 lumped MAPK 状态；未写逐级 kinetic model 或最终 rate table |
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

- [x] 归一化 Phase 0 单情景 time-course、CSV 和 PNG（`scenario_prior`）
- [x] 归一化 Phase 1 工程情景扫描、1/2/4 copy 条件比较、紧凑结果包和外部 payload 合同（`scenario_prior`）
- [x] Phase 2A 参数空间、输出指标、分析 contexts 和参数—潜在可观测量—证据缺口合同（`scenario_prior`）
- [x] Phase 2B 局部敏感性、Morris、条件性 Sobol 和重点双参数曲面的 runner、配置、测试与设计预检
- [ ] 系统剂量-响应曲线（ascr 浓度 vs 报告基因输出；先用 WT 场景，mutant 待 repaired shortlist）
- [ ] 灵敏度极限预测（最低可检测浓度）
- [ ] 动态范围与放大倍数优化建议
- [ ] **拷贝数敏感性分析（1/2/4 copy 对比）** —— 基线整合策略下的核心交付
- [ ] Phase 2B 仓库内紧凑结果包与正式参数灵敏度分析报告
- [ ] Phase 2C 后结合团队方案形成 DBTL model-experiment handoff
- [ ] 产出文件位置: `experiments/ode-model/`

## 代码与后续证据接口

- **代码路径**: `src/modeling/ode/`（Phase 0/1 原型、Phase 2A 合同与 Phase 2B 分析 runner 已实现）
- **产出路径**: `experiments/ode-model/`
- **DBTL handoff gate**：Phase 2B 提供模型侧敏感性，Phase 2C 提供可识别性；后续接口由这些分析结果与团队确认的方案、可行性、成本和资源共同确定。

## 学习成本与依赖

- **难度**: ★★☆☆☆（有 Python 基础，主要学 ODE 建模思路）
- **学习资源**: 见 [学习路线图 阶段一 + 阶段三](../learning/roadmap.md)
- **关键参考**: Shaw et al. 2019 *Cell* 中的模型可作为直接起点

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.2 提取，含双底盘策略 | 文档体系搭建 |
| 2026-04-11 | **v2.0** | status not_started → in_progress；锁定酵母 STE2 路径；新增基因组单拷贝整合基线 + 拷贝数敏感性分析；丝状真菌表保留为历史；与 P0-docking 双通道分析联动 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |
| 2026-05-20 | **v2.1** | 修正 docking→ODE 输入接口：docking 提供候选标签/方向/排序，Kd/EC50/efficacy 进入文献校准或参数扫描门控 | docking-repro full refresh 完成；Vina ΔG 仅支持排序 |
| 2026-05-23 | **v2.2** | 新增参数证据矩阵与校准计划；按 `fixed from source` / `literature prior` / `scenario prior` / `wet-lab required` / `do-not-use` 标注 ODE 参数状态 | API-first ODE 文献二阶段抽取完成，进入建模准备但不生成定论参数表 |
| 2026-05-24 | **v2.3** | 同步 Stage 3 exact pointer checkpoint、湿实验需求拆分和状态化参数接口；继续保留 Vina Delta G 仅排序、`Kd/EC50` 需独立证据的 gate | 文献抽取进入 exact pointer/manual queue 阶段；未写 ODE 代码，未生成定论参数表 |
| 2026-05-25 | **v2.4** | 增补当前形态/缺口/完整形态说明；更新 reporter 输出架构为 sTF -> GAL 多拷贝放大 -> 色素显色；明确未写 ODE solver | 用户确认实验方案附件中的 reporter 路径，需同步总览图缺口说明 |
| 2026-07-09 | **v2.5** | 正向校准 docking 输出消费口径：候选标签、Channel A/B、相对排序和 IFP 线索用于场景集合；Kd/EC50 需要独立 binding/calibration 证据 | 本次 docking authority 口径修订 |
| 2026-07-28 | **v2.6** | 增加可执行 Phase 0/1 原型、严格 schema/身份合同、紧凑结果与外部 payload 路由；保留全部未校准边界 | 从最新主线重建旧 ODE PR 的可用内容并通过本地合同验证 |
| 2026-07-30 | **v2.7** | 暂停消费旧 mutant shortlist/ranking/IFP；保留 WT 场景结构、已验证 Phase 0/1 原型和参数扫描框架，等待 frame-repaired 全量排名 | mutant/WT docking frame 缺陷导致旧候选撤回 |
| 2026-08-04 | **v2.8** | 登记 Phase 2A 机器合同、18 字段参数/实验接口和 guarded ratio；缺失 matched control 时 fail closed | Phase 2A 合同与指标有效性边界完成验证 |
| 2026-08-10 | **v2.9** | 将 Phase 2A 收缩为参数空间、输出指标、潜在可观测量和证据缺口合同；具体实验接口移至 Phase 2C 后的 DBTL gate | 修正阶段权威与实验设计边界 |
| 2026-08-16 | **v2.10** | 登记 Phase 2B runner/test 完成与结果包待审边界；当前状态统一路由到 INDEX，详细经过统一路由到贡献者日志 | 集成审查要求区分实现验证与完整数值结果接纳 |

## 进展记录

- 2026-05-24：Stage 3 exact extraction 已补入证据矩阵；P0 ODE 文档只同步证据状态、手动队列和湿实验需求，不输出 solver、rate table 或最终参数表。
- 2026-05-25：同步 reporter 输出架构和 ODE v0.1 完整形态定义；本轮仍未写 ODE solver、config、CSV 或 plots。
- 2026-07-28：Phase 0 solver/config/CSV/PNG 和 Phase 1 归一化情景扫描已实现。当前网格为 143 scenarios（74 ligand + 69 controls）和 23,023 条完整 time-course；所有数值仍为 `scenario_prior`，完整 time-course 按 payload policy 外置并由 manifest/checksum 路由。
- 2026-07-30：旧 docking mutant shortlist/ranking/IFP 撤回后，ODE 仅保留 WT Gpr2/Gpr3 × ascr#18/ascr#3 场景接口；Phase 0/1 已验证实现不回退，mutant 场景等待 repaired release。
- 2026-08-04：Phase 2A 分析合同已固定 18 字段参数空间、输出/实验接口和 ratio denominator guard；正 ligand 缺失 matched control 时拒绝生成指标，Phase 2B 灵敏度结果尚未开始。
- 2026-08-10：Phase 2A 当前合同已收缩为分析与证据缺口框架；参数数值、范围、分析 contexts、输出指标和 ratio guard 保持不变，具体实验接口等待 Phase 2C 后的 DBTL gate。
- 2026-08-16：Phase 2B 的实现、运行和贡献者验收经过统一见 [2026-08-07-yrx 日志](../logs/2026-08-07-yrx.md)；当前可接纳状态由本文顶部证据边界与 [INDEX](../INDEX.md) 裁决。

## 与其他方向的依赖关系

- **输出到**:
  - [P1-soil-diffusion](P1-soil-diffusion.md): 灵敏度极限 → 检测有效距离计算
  - [P1-bayesian-inference](P1-bayesian-inference.md): 剂量-响应曲线 → 正向模型组件
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): 当前只消费 WT Gpr2/Gpr3 场景结构；mutant 标签、Channel A/B、相对排序和 IFP 等待 repaired release；Kd/EC50/efficacy 需文献或湿实验校准
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 偶联效率 → ODE 中 Gpr-Gpa1 偶联速率
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
