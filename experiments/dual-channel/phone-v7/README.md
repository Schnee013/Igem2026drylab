# v7：色素—模拟手机颜色—Mi 密度

本包保存 2026-10-17 的 v7 / ODE r07 / 双通道 r04 冻结输入与精简结果。
所有样本为无噪声模拟；用途是复现既定假设下的内部估计能力。原始研究材料、参数搜索和图表的恢复位置见 [provenance.json](provenance.json)。

## 方法与本轮变化

Mi 为南方根结线虫 J2，Ce 为秀丽隐杆线虫 L4，密度单位为每 100 cm³ 土样。
两虫每虫每小时 ascr#3+#18 合计释放 1 fmol，Mi 谱为 1:10、Ce 为 10:1。
收集 1 h、有效体积 1 mL、回收率与稀释因子为 1。这些精确分泌量与比例是理想模拟假设。
两路传感器对 #3/#18 的输入权重分别为 2:1、1:2，归一化后行和相同，保留交叉响应。
预测时只需两个颜色读数，Ce 密度仅用于生成背景干扰与检验。

Mi 六档 0、5、10、40、80、120 与 Ce 三档 0、80、200 构成 18 个 ODE 校准终点。
前一版固定公共通路与末端 K、n、δ，拟合各通道 K_L、a。
本版将预设 8 h 总色素调整为 0.07–0.56 mg/mL indicaxanthin 等效量：固定原 K_L，
将 a 解析放大 309.991813 倍，按新空白重新计算 b，再运行完整 ODE 核对。
这是原拟合解的等价尺度变换，未进行新的 K_L 搜索，也未改善原动力学拟合形状。
冻结参数与来源见 [参数登记](ode-r07/parameters.csv)，目标与输出见 [18 组终点](ode-r07/endpoints.csv)。

**空白 0.07 mg/mL 约为 227.06 μM，不能沿用前版“0.05 μM 低背景”的说法。**
它只是把此情景置于文献非零标准区间内的项目选择，不能据此证明酵母真实基础产色或可达到的产量。
实际 ODE 终点范围及拟合误差以 [summary.json](summary.json) 为准。

## 手机接口

Stücheli et al. (2020), *Nucleic Acids Research* 48:e67，
[DOI 10.1093/nar/gkaa342](https://doi.org/10.1093/nar/gkaa342)，方法
“Smartphone-based betaxanthin quantification”（PDF 第 4 页）与 Figure 4：
iPhone、蓝背景、遮光盒、比色皿；indicaxanthin 非零标准为 0.07、0.14、0.28、0.56、1.12、2.24 mg/mL，
水空白；蓝通道表观吸光指数斜率 0.36±0.01，R²=0.99。
[PubChem Indicaxanthin](https://pubchem.ncbi.nlm.nih.gov/compound/Indicaxanthin) 的分子量 308.29 g/mol
用于 μM 与 mg/mL 换算。这些文献值沿用本地 v7 来源登记。

本次假设文献斜率可迁移，样本与传感器空白共用标定，截距通过相减抵消：

```text
c[mg/mL] = C[μM] × 0.00030829
x_j = 0.36 × (c_sample,j − c_sensor_blank,j)
r_j = B_sample,j / B_sensor_blank,j = 10^(−x_j)
x_j = −log10(r_j)
```

x3、x18 是两个传感器各自相对空白的蓝通道对数比值，并非配体浓度或仪器 A480。
未生成绝对 RGB，未计入曝光、量化、散射、手机噪声及斜率不确定性。
真实设备、基质、色素组成与实验空白仍须实测标定；范围声明仅适用于本次 8 h 终点。

## 双通道与风险分级

固定 ODE 后生成 [45 组训练](dual-r04/calibration-pairs.csv) 和
[19 组检验](dual-r04/heldout-pairs.csv)，选点见 [sampling-plan.json](dual-r04/sampling-plan.json)。
回归使用 ODE 实际输出转出的 x3、x18，不直接使用预设线性显色目标。
[回归系数](dual-r04/model.json) 为最小二乘结果；检验组合未用于拟合。
训练与检验来自同一个确定性生成器，不能解释为真实照片或湿实验性能。

双通道检验 RMSE 为 3.008 J2/100 cm³，两个单通道分别为 36.591 与 28.429。
v7 与前版密度预测差异约为数值舍入量级，说明手机观测尺度已衔接，不代表检测准确度提高。
例：Mi=40、Ce=80，两路蓝通道比值约 0.853711、0.878831，预测 Mi≈39.716，条件性中档。

19 组检验集中于零目标和阈值附近：点估计 12 组同档、6 组跨档、1 组为负；
实际接口 7 组被范围保护拦截，其余 12 组形式 OLS 区间跨阈值。
完整输出见 [heldout-predictions.json](dual-r04/heldout-predictions.json)。
部分密度位于设计矩形内的样本落在弯曲颜色映射的有限训练凸包之外，这表示现有门限保守，不是自然适用范围的实测结论。
Eco 沿用仓库示例的 10、80 分界；保留负值、超域及不确定分级处理，OLS 区间无实测覆盖率依据。

## 复现

在仓库根目录使用安装了项目 NumPy、SciPy 依赖的 Python，输出目录须不存在。
本入口直接导入仓库 ODE、回归及 Eco 实现；不依赖个人工作区。

```sh
python -m src.modeling.dual_channel.phone_demo regenerate \
  --package experiments/dual-channel/phone-v7 \
  --source experiments/ode-model/configs/literature_core_source.json \
  --eco-config experiments/economic/configs/eco_model_example_model.json \
  --output temp/phone-v7-replay

python -m src.modeling.dual_channel.phone_demo predict \
  --model experiments/dual-channel/phone-v7/dual-r04/model.json \
  --eco-config experiments/economic/configs/eco_model_example_model.json \
  0.853710699910313 0.878830804046674
```

`regenerate` 从冻结参数积分 18+45+19 组终点、重新拟合三个回归系数，并比较已接纳参考数据。
本次仓库复现证据见 [validation.json](validation.json)。文件身份与本地图表恢复入口见
[payload-manifest.tsv](payload-manifest.tsv)；历史版本保留。
