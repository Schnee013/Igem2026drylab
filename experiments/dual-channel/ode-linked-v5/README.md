# 双通道互补权重模拟 v5（2026-10-15）

- source：`inputs/scenario.json`、两路参数配置及 `results/`；源运行身份见 `provenance.json`。
- as_of：2026-10-15。
- allowed_use：复现冻结参数产生的双通道信号、模拟密度回归和 Eco 条件情景。
- update_trigger：分泌谱、权重、显色尺度、采样协议或 ODE 参数改变时建立新版本并重新拟合。

## 本次改动

此前 P3 的预设显色斜率为 (5, 0.1)，P18 为 (0.5, 0.4)，两路总增益不同。
v5 按用户确认，将 P3（V368R）设为 #3:#18=2:1，P18（N84V）设为 1:2，
归一化后每行权重和均为 1。共同显色尺度 G=1 μM/nM 是模拟设定。
Docking 只提供偏好方向的建模线索，精确权重与受体激活仍待实验标定。

令 S3、S18 为 nM 配体浓度，预设色素端点为：

```text
P3  = 0.5 + G × (2/3 S3 + 1/3 S18)
P18 = 0.5 + G × (1/3 S3 + 2/3 S18)
L3  = (2/3 S3 + 1/3 S18) / (1 nM)
L18 = (1/3 S3 + 2/3 S18) / (1 nM)
```

前两式是 ODE 拟合目标，后两式是 ODE 入口。公共通路及出口其他参数固定，
每通道重新寻找 K_L 与 a；b 由相同空白端点确定。拟合数值见
[ODE 摘要](results/ode-fit-summary.json)，冻结参数见 `inputs/channel3.json` 与 `inputs/channel18.json`。
K_L 是有效刺激尺度，不是由 docking 得出的结合常数。

## 数据与接口

Mi J2 密度取 0、40、120，Ce L4 背景取 0、80、200，单位均按每 100 cm³ 土壤定义，
构成 9 个独立变化的模拟组合。Mi 的 #3:#18=1:10，Ce=10:1；每虫两配体合计
Q=1 fmol/h，收集 1 h、有效体积 1 mL，回收率和稀释因子均为 1。
这些释放量与精确比例均为理想情景假设，两个虫龄标签不提供跨虫龄定量比较依据。
具体每行配体浓度及预设色素端点保存在 [scenario.json](inputs/scenario.json)。

ODE 在 8 h 的实际色素输出 C（μM 等效量）按 A480=0.048 C 换算；
各通道扣除其零输入 ODE 输出得到 x3、x18。三个回归系数通过最小二乘估计：

```text
d_Mi = beta0 + beta3*x3 + beta18*x18
```

Ce 用于生成背景干扰，预测接口只接收两个颜色。训练采用 ODE 实际输出，
不直接使用预设线性色素端点。Mi 密度输出接入 main 的 Eco 实现及示例配置；
超域、负预测和跨阈值区间沿用现有处理。

结果权威为 [回归模型](results/model.json) 与 [评价摘要](results/summary.json)。
另取 12 个新密度组合，并在固定 ODE/回归参数下检查 Mi 比例 1:5 和 1:20。
这些数据来自同一模拟生成器，未包含测量噪声或生物学重复；误差仅说明此假设下的数值表现。
本次也改变了共同显色尺度，不能将与 v4 的性能差异单独归因于权重比例。
正式经验校准需要真实配对读数与独立参考密度，并验证通道确实具有可区分信息。

## 复现

在仓库根目录运行；输出目录须尚不存在：

```bash
python -m src.modeling.dual_channel.generate_inputs \
  --input-dir experiments/dual-channel/ode-linked-v5/inputs \
  --source experiments/ode-model/configs/literature_core_source.json \
  --output temp/dual-v5-generated
python -m src.modeling.dual_channel.replay \
  --input-dir temp/dual-v5-generated \
  --output temp/dual-v5-replay \
  --eco-config experiments/economic/configs/eco_model_example_model.json \
  --protocol-id SIM_V5_MI1TO10_CE10TO1_SENSOR2TO1_1TO2_G1_8H_A480
python -m unittest tests.modeling.test_dual_channel_generation -v
```

以上从冻结参数重新积分并拟合回归，生成诊断图；原始 ODE 参数搜索脚本、轨迹与图的恢复指针和哈希见
`provenance.json`、`payload-manifest.tsv`。参数重新搜索使用本地研究工作区，仓库复现入口从冻结参数开始。
[v4](../ode-linked/README.md) 保留为历史基线。验证记录见 `validation.json`。
