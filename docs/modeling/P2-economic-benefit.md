---
direction: P2-economic-benefit
status: framework_mvp_validated + spain_tomato_demo_comparison_hardened
priority: P2
chassis_dependent: false
last_updated: 2026-10-15
---

# P2: 早期检测经济效益模型

> 来源: PRD v3 §3.5c + §2B | iGEM 评审定位: 完成"检测→预防"闭环，直接支撑 HP 和 Proposed Implementation
>
> **决策结论 (§2B.3)**: 本方向为防治建模的**最高优先**选择。

## 解决什么问题

量化"早期检测省了多少钱"。建立"无检测 vs 早期检测+干预"两种情景的成本-收益对比，为项目叙事提供经济论证。

**为什么是最高优先**: 数据可获取性极好、建模难度极低（纯算术）、对 HP 叙事价值最高、与检测系统耦合度最高。是完成"检测→预防"闭环叙事的最短路径。

## 与 ODE 建模的区别

P2 经济效益模型和 P0 ODE 的建模原理不同：

- ODE 是动态反应网络模型：输入 ascr 浓度、配体-受体激活、G protein/MAPK/reporter 参数，求解随时间变化的 pathway/reporter 输出。
- P2 是 deterministic cost-accounting 模型：输入作物、线虫密度、损失函数、作物价格、早期检测/干预成本和干预效果，直接计算 gross loss、break-even early-program cost、net benefit 和 ROI。
- P2 当前已有 `src/modeling/economic/` 的公开框架 MVP，以及固定为“西班牙设施番茄—南方根结线虫”的文献支持演示。后者分别报告“检测＋防治整套项目相对无防治”的收益和“检测分级相对未检测统一处理”的条件增量价值，并给出各自的净收益、增量成本、ROI 和密度盈亏平衡。它仍是简化示例，不是田间处方、种植前期望信息价值或对其他地区/作物的最终 ROI 校准；不能把 docking Delta G、ODE Kd 或未验证 wet-lab 假设当作经济确定输入。

## 双通道密度输入

[双通道校准接口](P1-dual-channel-calibration.md)将配对显色读数转换为目标南方根结线虫 J2 密度，并检查单位、协议、QC、饱和及校准范围后生成 Eco 条件情景。当前输入与验证均为模拟；形式预测区间尚无实测覆盖率保证，跨阈值时保留分档不确定性。复现与证据回到[ODE 联合模拟包](../../experiments/dual-channel/ode-linked/README.md)，不改变本方向对当地参数与实际检测性能的校准要求。

## 方法路线

1. 收集作物损失函数数据: 线虫密度 vs 产量损失百分比
   - 经典来源: Sasser & Freckman (1987) 综述 + 后续更新
   - 按作物类型分类（大豆、马铃薯、小麦等）
2. 建立两种情景模型:
   - **情景 A（无检测）**: 农户在症状出现后才发现 → 线虫已建立种群 → 防治成本高、效果差
   - **情景 B（早期检测）**: 使用你们的传感器 → 种植前/早期发现 → 及时干预 → 损失减少
3. 计算各情景成本:
   - 检测试剂成本估算
   - 各防治手段成本（化学/生物/轮作）文献值
   - 作物产量损失的经济价值
4. 产出: ROI 曲线，"每提前 X 天检测可减少 Y% 经济损失"

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (NumPy, Pandas) | 数据处理和计算 |
| Matplotlib / Plotly | 可视化（ROI 曲线、成本对比图） |

## 参数与数据来源

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| 作物损失函数（密度 vs 产量损失%） | Sasser & Freckman 1987; Nicol et al. 2011 | ★★★★★ |
| 化学杀线虫剂成本（$/ha） | 农药市场报告、推广站数据 | ★★★★☆ |
| 生物防治菌剂成本 | 商业产品价格 | ★★★☆☆ |
| 抗性品种种子溢价 | 种子公司数据 | ★★★☆☆ |
| 作物市场价格 | FAO / USDA | ★★★★★ |
| 检测试剂成本估算 | 团队自估（材料成本） | 需团队提供 |

## 产出定义

- [ ] 作物损失函数图（西班牙设施番茄示例已实现；推广到至少 2-3 种主要作物仍待完成）
- [x] 西班牙设施番茄示例的双基线成本-收益对比（未检测无防治、常规统一处理、检测后预设分级处理）
- [x] 双基线净收益曲线、密度盈亏平衡、单因素敏感性和预设方案/经济最优方案差异
- [ ] ROI 曲线: "每提前 X 天检测可减少 Y% 经济损失"
- [ ] 可用于 HP 组访谈的定量摘要
- [ ] 产出文件位置: `experiments/economic/`

## 代码与实验关联

- **代码路径**: `src/modeling/economic/`；西班牙示例入口为 `src/modeling/economic/eco_model.py`
- **产出路径**: `experiments/economic/`；双语示例报告默认写入 `experiments/economic/results/eco_model/`
- **HP 组对接**:
  - 本方向产出 → HP 组: 经济论据用于与农业专家、政策制定者访谈
  - 本方向产出 → Proposed Implementation: 量化检测系统的实际价值
  - HP 组反馈 → 本方向: 访谈中获得的真实成本数据可校准模型

## 学习成本与依赖

- **难度**: ★☆☆☆☆（基础算术建模，无需高级数学）
- **前置知识**: 基础 Python、简单的经济学概念
- **预计时间**: 1-2 周（含文献收集）

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-10-07 | v1.9 | TXT 补齐敏感性结果及外推/高密度警告；外推检查纳入经济比较中的未选方案，并分别核验支持范围不同的统一处理基线 | 交付复核发现 TXT 信息遗漏及未选高等级方案缺少外推警告 |
| 2026-10-07 | v1.8 | 敏感性分析同时覆盖检测后预设方案和未检测统一处理基线；共享处理参数同步变化；防效外推检查覆盖所有参与比较的方案 | PR #17 复审指出低密度时统一处理基线的成本、防效及外推对“是否值得检测”结论有决定性影响 |
| 2026-10-07 | v1.7 | 区分整套防治项目收益与检测分级的条件增量价值；为两条比较增加独立 ROI/盈亏平衡，结构化防效适用范围、配置驱动双语文本与检测收费，增加方案经济比较和敏感性分析 | 修复收益归因、固定防效外推、预设阈值与经济选择、配置/报告不同步及“是否值得检测”结果不足 |
| 2026-10-04 | v1.6 | 集成西班牙设施番茄—南方根结线虫的文献支持示例、三级处理、EUR/ha 核算和中英文报告；入口命名为 `eco_model.py` | 将外部演示代码纳入仓库权威路径并提供可复现运行入口 |
| 2026-05-25 | v1.5 | 增补 P2 与 ODE 的模型性质区别：P2 是 fixed-input deterministic cost-accounting，不是动态反应网络；保留最终 ROI guardrail | 缺口更新与总览图填充说明 |
| 2026-05-23 | v1.4 | 新增 Stage 3 外部 benchmark 抽取：PCN/Koehler、USDA ERS VOI、cucumber-RKN Bragantia、Barker tomato-RKN | 把公式结构从自洽算术推进到外部方法/密度-产量证据支撑，同时保持 ROI guardrail |
| 2026-05-23 | v1.3 | 新增 framework validation 文档与自动化测试，确认 UC IPM golden baseline 和成本核算公式可复现 | 防止把 smoke run 误读为最终 ROI；为 HP 参数回填前建立可靠性底线 |
| 2026-05-23 | v1.2 | 将 P2 文献/参数矩阵从 `tmp_papers/` 提升到 `docs/papers/p2-economic-benefit/`，并补充 HP 问卷路由与示例分析边界 | 长期留存与 DOCMAP 路由规范 |
| 2026-04-03 | v1.0 | 从 PRD v3 §3.5c + §2B 提取初始内容 | 文档体系搭建 |

## 进展记录

### 2026-10-07：收益归因与配置一致性加固

- 将 `17,028.48 EUR/ha` 明确为当前 100 J2/100 cm³ 输入下“检测＋防治整套项目相对无防治”的净收益；将 `496.26 EUR/ha` 明确为“检测分级相对未检测统一处理”的条件增量价值。两者分别核算增量成本、ROI 和密度盈亏平衡。
- 固定 `10/80 J2/100 cm³` 分级保留为预设演示策略，不再暗示为成本或防效变化后自动更新的经济最优阈值；报告同时比较低、中、高方案的预计净收入，并标识当前参数下的经济最优方案。
- 文献虫口降低率仍在 `100 J2/100 cm³` 参考密度下转换为固定避免损失比例，因为来源研究不足以支持完整的密度依赖防效曲线；配置现记录虫口降低率、参考密度、研究密度支持和管理上限，报告突出低密度外推及高密度边界。
- 方案中英文名称、剂量、实施说明、检测方法公开收费、每公顷代表样品数和敏感性范围均由 JSON 配置驱动；修改团队试纸成本或样品数后，费用与“便宜多少”结论会同步重算。
- 敏感性分析分别标明参数作用于检测后预设方案还是未检测统一处理基线；两侧使用同一中等级处理时保持成本和防效共享。防效外推提示同时检查所有参与比较的方案。
- 当前“检测价值”仍是给定密度且视检测准确时的条件比较；缺少密度先验分布、采样误差和诊断性能时，不得解释为种植前的期望信息价值。

### 2026-10-04：西班牙设施番茄演示集成

- 运行入口：`src/modeling/economic/eco_model.py`。
- 核心包：`src/modeling/economic/eco_model_pkg/`。
- 配置：`experiments/economic/configs/eco_model_example_model.json` 与 `eco_model_example_input.json`。
- 测试：`tests/modeling/test_eco_model.py`。
- 模型固定采用西班牙设施番茄、南方根结线虫、种植前检测、`J2/100 cm³ soil`、`EUR/ha`；密度—产量损失使用 Expósito 等（2020）的 Seinhorst 拟合，处理与经济参数及其证据类型记录在模型配置中。
- 页面并列展示未检测无防治、常规统一处理和检测后分级处理，生成中文与英文 HTML；报告用于展示试纸可能带来的单位面积利润变化，不构成田间防治处方。
- 试纸成本 `5 EUR/ha` 是团队定价；处理效果在共同参考密度下固定化，低密度区域含外推；输入密度被视为已知且准确。最终商业结论仍需目标市场、采样、产品性能与田间验证。

### 2026-05-21：Stage 1/2 文献参数矩阵 + MVP 框架

- Stage 1/2 调研产物已提升为长期文档：
  - `docs/papers/p2-economic-benefit/stage1-paper-data-matrix.md`
  - `docs/papers/p2-economic-benefit/stage2-parameter-extraction.md`
  - `docs/papers/p2-economic-benefit/stage2-model-parameters.csv`
  - `docs/papers/p2-economic-benefit/stage2-source-evidence.csv`
  - 原始 API/checkpoint 工作区仍保留在 `tmp_papers/p2_economic_benefit_20260521/`
- 最小 deterministic cost-accounting 框架已落地：
  - 代码：`src/modeling/economic/`
  - 示例配置：`experiments/economic/configs/public_mvp_framework.json`
  - 示例输出：`experiments/economic/results/public_mvp_framework_results.csv`
  - 示例解读：`experiments/economic/results/public_mvp_framework_summary.md`
- HP 参数回收材料：
  - `docs/modeling/P2-economic-benefit-hp-questionnaire.md`
- 当前可用公开参数：
  - tomato-RKN：UC IPM J2/kg soil → % normal yield piecewise table，可直接做 MVP 示例。
  - potato-PCN：EPPO/AHDB/APHIS 阈值与损失范围，可做归一化或占位场景。
  - soybean-SCN：UMN/Iowa 阈值、采样误差和 lab cost 可用，但密度-产量损失函数仍需全文抽取。
- 仍不可作为确定输入：
  - biosensor 单次成本、部署密度、灵敏度/特异性；
  - 当地作物价格、施药成本、人工/设备成本、抗性品种溢价、轮作机会成本；
  - docking Delta G、ODE Kd 或未验证 wet-lab 假设。

### 原公开框架 MVP 的分析边界

- 基线不是“完全不损失”，而是“没有早期检测/晚发现时，在给定线虫密度下承受的产量收入损失”。
- 早期检测情景暂不使用真实传感器成本；当前用 `early_program_costs_per_area` 做 50/100/200 USD/acre 等占位成本扫参。
- `intervention_effect` 不是某个药剂的确定疗效，而是“早发现+及时干预避免晚发现损失的比例”扫参；正式值需要 HP/湿实验/文献全文回填。
- P2 ROI 未最终校准；当前 MVP 只能支撑公开示例算术、break-even 结构和 HP 参数回收，不代表本项目 biosensor 的目标地区商业回报。
- tomato-RKN 是唯一可直接货币化的公开示例：UC IPM 表给出 500 spring J2/kg soil 对应 72% normal yield，示例产量 30 tons/acre，价格 54 USD/ton，所以晚发现毛损失为 `30 * 54 * 0.28 = 453.6 USD/acre`。
- potato-PCN 目前只是归一化结构验证；soybean-SCN 目前只是阈值决策骨架，二者不能作为本地 ROI 结论。

### 2026-05-23：框架全量检验

- 验证文档：`docs/modeling/P2-economic-benefit-validation.md`
- 自动化测试：`tests/modeling/test_economic_model.py`
- 验证命令：

```bash
python3 -m unittest tests.modeling.test_economic_model -v
```

- 当前结果：14 个测试通过；重新生成 `public_mvp_framework_results.csv` 到临时文件后与仓库内 CSV 完全一致。
- 已验证范围：
  - UC IPM tomato-RKN `200 spring J2/kg soil` computed golden baseline：由 UC IPM 表格点位和示例产量/价格计算，`30 * 54 * 0.12 = 194.40 USD/acre`。
  - 当前 tomato-RKN `500 spring J2/kg soil` public example：`30 * 54 * 0.28 = 453.60 USD/acre`。
  - piecewise table 点位、线性插值、边界 clamp、PCN 归一化线性损失、SCN threshold-only 不货币化 guardrail，以及无效规则/零成本/干预效果越界等边界条件。
- 解释边界：这证明 deterministic cost-accounting framework 和 UC IPM public example 的算术可靠；仍不能证明本项目传感器在目标地区的最终 ROI。

### 2026-05-23：Stage 3 外部 benchmark 抽取

- 新增长期证据文档：
  - `docs/papers/p2-economic-benefit/stage3-benchmark-extraction.md`
  - `docs/papers/p2-economic-benefit/stage3-benchmark-evidence.csv`
- 原始工作区：
  - `tmp_papers/p2_economic_benefit_20260523_stage3/`
- 已抽取可用 benchmark：
  - PCN：Koehler et al. `10.1163/15685411-bja10138` 支持 PCN decision-support 的方法结构与局部参数校验，但不是完整 NemaDecide worked example。
  - VOI：USDA ERS soybean rust early-warning report 支持增强层公式 `E[cost_without_information] - E[cost_with_information]`，并提供信号质量/先验风险的数值例题。
  - cucumber-RKN：Mukhtar and Kayani 2020 `10.1590/1678-4499.20190359` 提供合法 OA 全文表格，可作为新增密度-产量函数 benchmark，但不能直接换算为田间 J2/kg soil。
  - tomato-RKN：Barker et al. 1976 PMID `19308228` 支持 UC IPM tomato-RKN 表格的外部合理性与环境敏感性，不替代 UC IPM golden baseline。
- 仍然 pending：
  - Contina 2019、Kayani 2017、Kayani/Mukhtar/Hussain 2018、Isik/Hudson/Coble 2005、Heydari/Tanha Maafi/Pourjam 2012、Been/Schomaker 1998 需要合法全文或补充表格。
- 本轮未修改 `public_mvp_framework.json` 或 `tests/modeling/test_economic_model.py`：Stage 3 证据足以指导增强模型结构，但尚未形成可自动回放的新 golden benchmark。

## 与其他方向的依赖关系

- **输出到**:
  - HP 组 Proposed Implementation（最直接的消费者）
  - iGEM wiki Modeling 页面（经济论证部分）
- **依赖于**:
  - [P1-bayesian-inference](P1-bayesian-inference.md)（可选）: 密度估计的不确定性 → 经济损失的不确定性区间
  - 基本可独立运行，不严格依赖其他建模方向
