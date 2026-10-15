---
direction: P1-dual-channel-calibration
status: exploratory_interface_simulation_only
priority: P1
chassis_dependent: true
last_updated: 2026-10-15
---

# 双通道读数 → 南方根结线虫密度 → Eco

交付：最小混合实验设计、27 行配对数据模板、三系数回归接口及模拟链路。真实系数、抗背景性能和分级准确性均待实测。目标为南方根结线虫（Meloidogyne incognita）J2；秀丽隐杆线虫（Caenorhabditis elegans）作为背景干扰，数量不计入 Eco 密度。

## 权威与复核

- `source`：本次核验 main `da408f407802aa2c0df8dc11346cad4638c1375e` 的 [Eco 配置](../../experiments/economic/configs/eco_model_example_model.json)、[配置读取](../../src/modeling/economic/eco_model_pkg/config.py)、[经济计算](../../src/modeling/economic/eco_model_pkg/economics.py)和[密度范围检查](../../src/modeling/economic/eco_model_pkg/loss.py)。2026-10-15已只读核对远端提交；后续远端变化须重新核验。
- `as_of`：2026-10-15（任务于 10 月 10 日开始）。
- `allowed_use`：设计标定实验、检查数据接口、演示条件性 Eco 情景。
- `update_trigger`：Eco 配置/实现或实验 protocol 改变时，重新检查接口与范围。
- 机制与运行来源：[ODE联合情景来源清单](../../experiments/dual-channel/ode-linked-v5/provenance.json)。六状态实现和 Eco 采用该清单记录的仓库版本，双通道阶段消费冻结参数生成的两路 ODE 输出。

## 1. 最小实验：3 × 3 × 3

| 目标 J2 密度＼背景密度 | 0 | 低（待确认） | 高（待确认） |
|---|---|---|---|
| 0 | 基质空白 | 仅背景 | 仅背景 |
| 低（待确认） | 仅目标 | 混合 | 混合 |
| 高（待确认） | 仅目标 | 混合 | 混合 |

9 个组合各 3 份独立制备，共 27 份，每份同一提取液分成两份，加入两个独立传感器，得到 54 个通道端点测量。推荐 3 个实验批次，每批完整覆盖 9 个组合；每批内随机化制备顺序及孔位，保留实际孔位/原始文件。模板 B1、B2 拟合，B3 完全留出验证。B3 不用于选择读色时间、变换或模型项。后续修改方案后须另取新验证样本。

这 27 份是探索起点，包含每批一个 0/0 样本；额外空白重复、技术重复、预实验和配体对照不计在 54 次内。用于验证的 0/0 样本须用独立批次 QC 空白校正，不能用自身读数把自身强制变成零。空白重复数与汇总方法待确认。

先用少量空白、仅目标、仅背景、高混合样本观察时间曲线，冻结一个“可测且未普遍饱和”的读色时间及饱和判据。再决定低/高密度，避免完全共线或普遍饱和。不得直接沿用 ODE 的 8 小时演示设定。

若两个物种引起的双通道变化方向近似重合，两个读数仍可能无法区分目标与背景。检查双通道散点、残差、设计矩阵秩与标准化条件数；秩不足直接拒绝拟合，接近共线需依据噪声、区间宽度及留出性能判断，接受界限待预注册。

### 虫龄、单位和参照真值

- 目标固定 J2，并记录孵化后的小时窗口、同步/鉴定方法；窗口待确认。
- 背景第一轮固定单一发育阶段及同步方法，具体阶段待确认。不能混用幼虫、成虫或混龄培养物后仍声称同一适用范围。
- 参照密度 `d = 100 × target_count / soil_volume_cm3`，单位严格为 `J2/100 cm^3 soil`。背景独立记录为 `individuals/100 cm^3 soil`。
- 只有土壤质量时，须有同批实测容重才能换算体积；不能直接将 J2/g 当作 J2/100 cm³。模板保留质量列作追溯。
- 首轮建议规定土壤体积中加已知虫数，走完整条件化、提取、分样流程；此时 `reference_basis=spike_count`，标签表示实验加样密度。
- 提取后计数须明确抽样比例、鉴定及回收率；不能把回收虫数直接当作原土全部虫数。自然土样须用独立参考计数验证，并记录其不确定性，才可评价田间迁移。
- 提取体积、稀释倍数、条件化时间、酵母接种量、温度、培养基和读色时间均固定到 protocol。当前模型输入采用固定 protocol 下的读数，不擅自乘以稀释倍数或提取体积；改变条件须重新标定或验证换算。

### 小型配体交叉响应对照

两个传感器分别接受溶剂空白、ascr#3、ascr#18、两者混合刺激；先选择未饱和剂量，浓度、重复与溶剂控制待确认。用于解释交叉响应，独立于 27 份虫样矩阵。通道名称表示设计靶标，不表示物种专一性。

[Manosalva et al., 2015，Results: Plant-parasitic nematodes produce ascarosides](https://www.nature.com/articles/ncomms8795)明确记载 C. elegans 也产生 ascr#18。因此不能把 C18 直接解释成南方根结线虫专属信号。

## 2. 配对数据模板

[paired_samples.csv](../../experiments/dual-channel/templates/paired_samples.csv)是一行一个独立样本的宽表。27 行均为 `planned_not_measured`；数值空格表示缺失，实际零值须明确填 `0`。配套 [protocol.json](../../experiments/dual-channel/templates/protocol.json)把固定条件集中记录，所有 null/TO_CONFIRM 项均待确认。

| 字段组 | 内容与填写规则 |
|---|---|
| 身份与分组 | `sample_id` 全局唯一；`batch_id`、`independent_replicate`、`date_iso`；`planned_split` 在实验前冻结 |
| 因子 | `target_level/background_level` 为计划档位；具体数值以实际计数为准 |
| 物种与虫龄 | `target_species/target_stage` 固定为目标 J2；`background_species/background_stage` 记录背景实际阶段 |
| 真值口径 | `reference_basis` 为 spike_count 或 independent_field_count；`target_count/background_count` 为原土体积对应的参照个体数，参考方法及回收规则写 protocol |
| 基质与提取 | `soil_volume_cm3` 必填正数；`soil_mass_g` 可选；`extract_volume_ml/dilution_factor` 必填正数；基质批次在 protocol 按 batch 映射 |
| 端点配对 | `raw_c3/blank_c3/blank_id_c3` 与 `raw_c18/blank_c18/blank_id_c18`；同 sample_id、同读色时刻；保存各通道空白来源 |
| 质控 | `saturated_c3/saturated_c18` 填 true/false，缺失不能解释成 false；`qc_status` 待核验后填 pass/fail；原始技术重复及孔位在 `raw_data_path` |
| 追溯 | `protocol_id` 对应冻结的 protocol；`evidence_status` 实测填写 measured_unvalidated；`notes` 记录偏差与排除原因 |

固定校正：`x3=raw_c3-blank_c3`、`x18=raw_c18-blank_c18`。空白必须匹配批次、基质、传感器、时间与仪器流程。负的空白校正信号可以保留；负的虫密度预测须标记失败。技术重复先按预注册规则汇总到独立样本，同时保留原始值。不同样本不能因为读数接近而合并。

读数可以是固定波长吸光度或冻结图像流程的颜色指标。只有有独立标准曲线时才称“色素浓度”。两个通道允许各自采用固定单位，其单位必须写入 protocol，系数随单位变化。

## 3. 三系数回归接口

### 方程冻结 v1（2026-10-13）

本轮固定模型形式与接口，已在ODE模拟配对数据上拟合三个系数；真实实验系数仍待实测标定：

$$
x_3=C_3(t_*)-C_{3,\mathrm{blank}}(t_*),\qquad
x_{18}=C_{18}(t_*)-C_{18,\mathrm{blank}}(t_*)
$$

$$
\boxed{\widehat d_{\mathrm{Mi,J2}}=\beta_0+\beta_3x_3+\beta_{18}x_{18}}
$$

- 输入：同一混合样本、同一固定读色时间的两个独立传感器输出，经各自匹配空白校正。通道对应传感器，不对应两个物种；背景虫数不作为预测输入。
- 输出：南方根结线虫 J2 密度，单位 `J2/100 cm^3 soil`；秀丽隐杆线虫为背景干扰。
- 参数：仅拟合 `beta0、beta3、beta18`，采用带截距普通最小二乘，允许负系数。本版保持双变量线性形式。
- 读数单位：当前ODE联合情景使用空白校正的A480，固定8 h终点、1 cm有效光程及A480=0.048C的工作近似，C为μM色素等效量；这些条件是模拟设定，实际湿实验仍按第1节确认protocol。
- 标定状态：当前ODE配对读数已完成模拟训练，固定输入与结果见[ODE联合情景](../../experiments/dual-channel/ode-linked-v5/README.md)。早期任意单位演示与本轮吸光度模型的系数不可混用。
- 下游：沿用现有 Eco 适配与配置分级，保留范围检查和区间跨阈值时的不确定性标记。

当前状态为模拟训练完成；系数和误差的数值权威为[模型参数](../../experiments/dual-channel/ode-linked-v5/results/model.json)与[结果摘要](../../experiments/dual-channel/ode-linked-v5/results/summary.json)。

实现：[calibration.py](../../src/modeling/dual_channel/calibration.py)。依赖 NumPy、SciPy 和既有 Eco 模块；本次运行版本见实验说明。

`d_hat = beta0 + beta3*x3 + beta18*x18`，采用带截距普通最小二乘，不先取比值、不强制系数为正。三个系数是待拟合量。当前无实测系数。

调用示意（先检查模板完整性、protocol 一致性及样本 QC）：

```python
from src.modeling.dual_channel.calibration import fit, predict, eco_scenarios
from src.modeling.economic.eco_model_pkg.config import load_model

# x: n×2 空白校正读数；d: 按原土体积换算的 J2 密度；IDs: 独立样本 ID
cal = fit(x, d, sample_ids=IDs, protocol_id='冻结的protocol版本',
          evidence_status='measured_unvalidated', reference_basis='spike_count')
p = predict(cal, [x3, x18], protocol_id='冻结的protocol版本',
            saturated=任一通道是否饱和, qc_pass=样本质控是否通过)
eco = load_model('experiments/economic/configs/eco_model_example_model.json')
scenarios = eco_scenarios(p, eco)
```

这是 Python 数值接口；CSV 是原始采集模板，当前没有自动清洗或自动接纳实测 CSV 的命令。调用者必须先核对必填字段、虫龄和 protocol，并完成上述密度换算与空白校正。模板空值不可转换为零。

输出包括原始点估计、单位、95% 单样本预测区间、密度校准范围、联合颜色范围标志、失败原因、protocol 和证据状态。联合颜色范围采用训练读数二维凸包，边缘样本可能被保守拒绝；不将两个单独的 min/max 当成充分条件。背景物种、虫龄、基质与背景范围等外部条件不能从颜色自动验证，需由 protocol/QC 人工核对。

预测区间由 OLS 残差方差、系数协方差及 t 分位数计算，包含单次预测残差项；这不是均值置信区间。假设独立、同方差、近似正态误差及固定输入。空白误差、参考计数误差、未知批次漂移尚未传播。用留出数据检查覆盖率；若残差结构明显不满足假设，当前区间只能作诊断，须补数据或换区间方法。

饱和、QC 失败、protocol 不符、非有限输入、联合颜色或目标密度超范围、负密度预测，均阻止 Eco 调用。原始负预测保留以便审计，不裁成 0 后宣称准确。


### ODE联合训练的数据背景与解释

本轮模拟将Mi的#3∶#18设为1∶10、Ce设为10∶1，并令单虫两配体合计释放量相同。这里的总量仅涵盖#3与#18，精确比例和绝对释放量都是项目假设。采样条件与生成公式见[scenario.json](../../experiments/dual-channel/ode-linked-v5/inputs/scenario.json)。

两物种分别向S3、S18贡献信号；同一混合提取液作用于两个独立传感器。两路均使用480 nm吸光度，通道名表示设计靶标而非波长或物种专一性。固定交叉响应为L3=(2S3/3+S18/3)/(1 nM)、L18=(S3/3+2S18/3)/(1 nM)。预设色素终点用于上游ODE的K_L、a拟合；本轮回归使用ODE实际算出的8 h颜色，保留ODE近似偏差。

[校准输入](../../experiments/dual-channel/ode-linked-v5/inputs/calibration.csv)由9个两物种独立变化组合构成。Ce密度参与样本设计和分层解释，预测目标为Mi：相同Mi、不同Ce的样本拥有相同目标标签，要求同一组三系数尽量抵抗背景变化。以Ce真实密度作为预测必需输入会要求额外背景计数，故当前接口只接收两路颜色。

[评价输入](../../experiments/dual-channel/ode-linked-v5/inputs/evaluation.csv)包含未用于拟合的新组合及Mi比例变化情景。它们仍由同一ODE和假设生成，无测量噪声或生物学重复，不能当作独立湿实验验证。邻近比例检查保持ODE与回归参数固定，检查输入假设改变的影响。

文献依据：Manosalva 2015的[Supplementary Fig. 1（S1页）及Supplementary Table 1（S10页）](https://pure.mpg.de/rest/items/item_2175401_5/component/file_3032827/content)支持Mi分泌#18且其在报告谱中占优；Mi栏未列#3，不足以给出#3/#18配对定量比，也不能证明#3绝对为零。[Choe 2012 Fig. 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC3360977/)中的根结线虫是M. hapla，不能直接作为Mi比例。完整检索记录的本地路径及校验值见来源清单。

适合写作的结论是：在明确的理想化输入情景下，双通道比单通道更好地恢复目标密度；低信号、负预测、阈值附近错档和比例敏感性仍需保留。不能将当前模拟优势表述为真实特异性、检测限或现场准确率。将来用真实配对颜色及独立Mi参考密度重新拟合，经验回归不必显式输入1∶10，但仍须验证两路真实信号具有足够区分信息。

## 4. 最小验证与接受门

相同 B1/B2 样本分别拟合仅 C3、仅 C18、双通道三个模型；B3 使用完全相同的独立样本比较。报告：

1. MAE、RMSE、偏差，以及按目标/背景分层的误差；同时报样本数、拒绝率与拒绝原因，避免只保留易预测样本。
2. 仅背景样本的预测分布与误报：可单独报告跨 Eco 中档阈值的比例；“检测阳性”的阈值仍待湿实验预注册，不能用任意大于 0 代替检测限。
3. 相同目标在不同背景下的偏差及波动，残差随背景/批次/信号强度的趋势。
4. 原始预测区间覆盖率和宽度；分级混淆矩阵及跨阈值区间占比。

27 份设计的 B3 仅有 9 个独立样本（仅背景且非空白 2 个；含空白的目标零样本 3 个），只能初步诊断，不能提供稳定灵敏度/特异度。冻结模型后，在 Eco 阈值两侧补独立样本，示例候选为 8/12 和 70/90 J2/100 cm³，各覆盖无、低、高背景；这些是待确认设计档位，须先验证动态范围。具体样本量及允许 MAE、误报率、区间宽度待确认。

若双通道未改善，应报告无改善；明显曲率先检查饱和与协议偏差，再在训练数据考虑一个简单非线性项，并用新留出数据验证。

## 5. Eco 适配与范围

main 的输入为 `{"density": 数值, "density_unit": "J2/100 cm^3 soil"}`；Eco 自身接收点值，区间由适配层展开为多个条件情景。阈值和上限直接读取 model 对象，不在校准代码硬编码。当前配置是西班牙设施番茄、种植前南方根结线虫：低 `<10`、中 `[10,80)`、高 `>=80`，模型可计算密度 `0–869.6`。实际还须落在校准支持域内。

`eco_scenarios` 仅返回 `conditional_demo_only` 或 `blocked`。即使未来传入实测拟合，其结果仍须独立验证后才能作现场判断。跨 10 或 80 时保留端点、点估计及每个跨越阈值的左右两侧；同时跨两个阈值会展示全部三档。费用分段跳变，不能只用区间两端推定收益上下界。结果中的收益是场景值，不是收益置信区间。

原始预测区间下界若小于 0，展示物理部分时明确标记截至 0；原始区间保留。区间上界超校准或 Eco 支持范围则整体拦截。Eco 输出保留“相对统一处理的检测增益”口径，不与“相对不防治的项目收益”混用。现有示例价格、成本及效果假设仍以 Eco 配置为准；本轮没有将其升级为通用农业阈值或田间收益证据。

## 6. 待确认与适用范围

必须确认：目标 J2 孵化时间窗口；背景固定阶段；低/高档位；基质/提取及回收方法；条件化时间；两种构建体；接种量/温度；读色时间与单位；空白/饱和/重复汇总规则；独立参考计数；误差与误报接受界限。

首版适用范围仅覆盖固定 protocol 下、已标定密度与背景范围内的两物种混合样本。其他线虫、混龄、不同土壤、自然残留信号、不同稀释/时间/构建体都需要外部验证。颜色同时承载历史分泌、基质和生物状态信息，因此加样密度模型的成功不能直接证明真实土壤虫口可反推。

- 输出到：湿实验配对标定、Eco 条件情景接口。
- 依赖于：固定实验 protocol、独立参照计数、[Eco 权威配置与实现](P2-economic-benefit.md)、既有 ODE 研究入口。

## 2026-10-15 互补权重迭代

[v5 模拟包](../../experiments/dual-channel/ode-linked-v5/README.md)统一了预设显色与 ODE 入口的权重：
P3 使用 (2/3, 1/3)，P18 使用 (1/3, 2/3)，共同显色尺度为 1 μM/nM。
冻结的 r05 两路 ODE 参数及 r02 回归模型随版本保存；三系数回归形式保持不变。
Docking 仅约束偏好方向，精确权重属于模拟假设。历史 v4 结果见
[原模拟包](../../experiments/dual-channel/ode-linked/README.md)。
