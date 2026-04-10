# Fan et al. 2024 — 文献总结

> **完整标题**: Cascaded amplifying circuit enables sensitive detection of fungal pathogens
> **期刊**: *Biosensors and Bioelectronics* 250 (2024) 116058
> **DOI**: https://doi.org/10.1016/j.bios.2024.116058
> **作者**: Cong Fan, Nike He, Jifeng Yuan（通讯）
> **机构**:
> - a State Key Laboratory of Cellular Stress Biology, School of Life Sciences, Faculty of Medicine and Life Sciences, Xiamen University, Fujian 361102, China
> - b Key Laboratory for Synthetic Biology of Xiamen City, Xiamen University, Fujian 361005, China
> - c Shenzhen Research Institute of Xiamen University, Shenzhen 518057, China
> **收稿/接受/在线**: 2023-12-06 / 2024-01-18 / 2024-01-20

---

## 核心发现（Bullets）

- 在酿酒酵母（*Saccharomyces cerevisiae*）中构建 GPCR 信号通路与 GAL 系统的级联放大回路，用于检测真菌病原体分泌的交配信息素。
- 设计杂合转录因子（sTF）：融合 Ste12 的信息素响应域（PRD，aa 216–688）与 Gal4 的 DNA 结合域（DBD，aa 1–147），将 MAPK 信号路由至 GAL 系统，使酵母生物传感器的输出信号提升约 7 倍。
- 进一步将 Gal4 置于 GAL 系统自身的正反馈启动子（P_GAL1）控制下，形成"自激活转录正反馈回路（sTF）"，使 LOD 降至 **0.25 pM**，LOQ 降至 **1 pM**（以 2h 孵育为标准）。
- Sst2（GTPase 激活蛋白，抑制 Gpa1 的 GTP 水解）的靶向敲除（Δsst2）进一步将 Kc（半最大有效浓度）降低超过 50 倍（从 Sc-G1.0-Ca 的 0.083 nM → Sc-G2.0-Ca 的 0.083 nM，Sc-G3.0-Ca 的 Kc ≈ 3.322 pM，Sc-G4.0-Ca 的 Kc ≈ 15 pM）。
- 与传统设计（Sc-Base-Ca，LOD = 1 nM）相比，Sc-G4.0-Ca 的 LOD 下降了 **4000 倍**（1 nM → 0.25 pM）；Kc 下降了 **9700 倍**（32.55 nM → 3.323 pM）。
- 生物传感器在 20–40°C 和 pH 4.4–9 范围内信号稳定；传代实验中（10 轮），信号重现性在线性范围内保持在理论值的 **±20%** 以内（CV ≤ 10%）。
- 开发了基于甜菜色素（betaxanthin）的比色视觉输出模块：异源表达 *Beta vulgaris* BvCYP76AD5（酪氨酸羟化酶/环化酶）和 *Mirabilis jalapa* MjDOD（L-DOPA 双加氧酶），Ca 信息素 ≥ 100 pM 时可见肉眼可辨的橙色。
- 添加胺供体（6-氨基吲哚 6AI 和 o-二氨苯 oDDA）可显著增加甜菜色素颜色强度，并在 2h 孵育后可视化 Ca 信息素。
- 该系统以 *Candida albicans* 交配信息素（Ca peptide，即 α-factor 的 *C. albicans* 版本）为检测靶标，证明了原理可扩展至其他病原真菌（通过替换相应 GPCR）。

---

## 实验方法

| 模块 | 方法/材料 | 关键细节 |
|------|-----------|----------|
| 宿主菌株 | *S. cerevisiae* CEN.PK2–1C（背景） | 标准实验室菌株，含内源 MAPK 信号系统 |
| GPCR | 异源 Ste2（来自 *C. albicans*，CaSte2）替换原生 ScSte2 | 特异识别 Ca 信息素；P_FUS1 驱动报告模块 |
| 杂合转录因子 sTF | PRD（Ste12 aa 216–688）+ DBD（Gal4 aa 1–147） | 以 Gal4DBD-Ste12AD 命名；亚克隆到 P_GAL1 启动子下 |
| GAL 正反馈回路 | P_GAL1 驱动 Gal4（自激活）+ P_GAL1 驱动 EGFP | sTF 激活 GAL 系统，GAL 系统反过来进一步激活 sTF |
| Sst2 敲除 | CRISPR-Cas9 靶向 Sst2 DBD 结构域 | Δsst2 菌株（Sc-G2.0-Ca 系列） |
| 报告模块 | EGFP（荧光）/ BvCYP76AD5+MjDOD（甜菜色素比色） | EGFP 荧光（Fluor/OD_600 × 1000，a.u.）；比色板 4h–8h 孵育读值 |
| 数学模型 | Hill 函数拟合剂量-响应曲线（Hill equation） | 参数：Kc（EC50）、n（Hill 系数）、k（最大输出） |
| LOD 计算 | LOD = LOB + 1.645 × SD_low；LOB 通过空白样品估算 | LOD 是信号超过背景 95% 置信水平时的最低浓度 |
| LOQ 计算 | LOQ ≥ 5 × LOD；CV_LOQ = SD_LOQ/mean_LOQ ≤ 10% | LOQ 是可被可靠定量的最低浓度（测量精度 ≤10% CV） |
| 培养条件 | SC-Leu 培养基（2% 葡萄糖），摇床培养，6h 后读数 | 比色输出模块的最大信号在 8h 后出现 |
| 稳定性测试 | 温度（20/30/40°C）、pH（4.4/7/9）、传代（5+10 轮） | 最优温度 30°C，T_50（达 50% 最大输出时间）= 2.5h |
| 环境样品检测 | 添加 *C. albicans* 滤液至样品中，测试夹杂物影响 | 确认系统在复杂样品中仍可信号输出 |

---

## 关键数据

### 各代生物传感器性能比较（以 Ca peptide 检测为例）

| 菌株 | 基因修改 | LOD | LOQ | Kc | n | k |
|------|---------|-----|-----|----|---|---|
| Sc-Base-Ca | 内源 Ste2 → CaSte2（无 GAL 系统） | ~1 nM | — | 32.55 nM | — | — |
| Sc-G1.0-Ca | + sTF 接入 GAL 系统 | ~1 nM | — | 0.083 nM | — | 约 7× 输出提升 |
| Sc-G2.0-Ca | + Δsst2（Sst2 敲除） | 10 pM | — | 0.083 nM | ~50× Kc 改善 | — |
| Sc-G3.0-Ca | + 正反馈 Gal4（P_GAL1-Gal4） | 0.1 pM（~0.25 pM）| — | 3.322 pM | — | 41× 输出提升 vs G1.0 |
| Sc-G4.0-Ca | Sc-G3.0 + Δsst2 | **0.25 pM** | **1 pM** | **15 pM（3.323 pM by fit）** | — | — |

> 注：LOD 0.25 pM 和 LOQ 1 pM 均基于 2h 孵育后的数据。最大输出（k）在 Sc-G3.0 中为 Sc-G1.0 的 41 倍（at 0.1 nM Ca peptide）。

### Hill 函数拟合参数（部分代表性数据，原文 Table S4/Fig. 3C）

| 菌株 | Kc（nM） | n | k（a.u.） | R² |
|------|---------|---|-----------|-----|
| Sc-G1.0-Ca | ~83 | — | — | >0.99 |
| Sc-G2.0-Ca | ~0.083 | — | — | >0.99 |
| Sc-G3.0-Ca | ~3.322×10⁻³ | — | — | >0.99 |
| Sc-G4.0-Ca | ~3.323×10⁻³（fit）/ 15 pM（stated） | — | — | >0.99 |

> 文中不同位置报告值略有差异，以 Fig. 3D 回归方程为准。

### 甜菜色素视觉输出模块

- 基因：BvCYP76AD5（B. vulgaris，P450 酪氨酸羟化酶）+ MjDOD（M. jalapa，L-DOPA 双加氧酶）
- 均在 P_FAR1-101 启动子控制下，受 α-factor 诱导
- 肉眼可见橙色的阈值：Ca peptide ≥ **100 pM**（8h 孵育）
- 添加 6AI/oDDA（胺供体）后，颜色强度显著增加（Fig. 4B）
- 不依赖荧光仪器，适用于现场快速检测（point-of-care）

### Δsst2 的机理效果

- Sst2 是 Gpa1 的 GTPase 激活蛋白（GAP），负调控 MAPK 信号
- 敲除 Sst2 降低 Kc（提高亲和力/灵敏度）但不显著改变背景噪声和最大输出
- Kc 降低 > 50 倍（Sc-G1.0-Ca → Sc-G2.0-Ca），符合文献中 Sst2 负反馈的预期作用
- 不影响基础生长，与本文结果一致（Sc-G4.0-Ca 生长速率未受显著影响）

---

## 与项目的关系

本文为 iGEM 2026 干实验酵母 GPCR 生物传感器底盘设计提供了以下直接参考：

1. **信号放大架构**：GAL4 DBD 与 Ste12 PRD 的杂合转录因子（sTF）设计，以及 P_GAL1 自激活正反馈回路，是本项目信号放大模块的核心参考方案。
2. **LOD 基准**：经过三层优化（sTF + Δsst2 + 正反馈）后 LOD 可达 0.25 pM，为项目传感器性能目标提供了参照上限。
3. **可扩展性验证**：论文证明只需替换 GPCR（用异源 Ste2 替换原生 Ste2），即可将信号通路重定向至不同真菌病原体的交配信息素，支持本项目模块化底盘设计思路。
4. **Sst2 敲除策略**：作为提高 GPCR 信号灵敏度的负调控解除手段，可直接借鉴用于本项目底盘改造。
5. **比色输出模块**：BvCYP76AD5 + MjDOD 甜菜色素合成路径提供了一种无需荧光设备的可视化方案，适合 point-of-care 应用场景。
6. **数学建模框架**：Hill 函数（式 6）+ LOD/LOQ 定义（式 2–5）是本项目传感器性能评估和 ODE 建模的标准参考。

---

## 关键引用

1. **Ostrov et al. 2017** (Sci. Adv.) — 最初的 *C. albicans* GPCR 生物传感器设计（Sc-Base-Ca 的参照原型），LOD ~1 nM。
2. **Miettinen et al. 2022** (Nat. Commun. 13, 3664) — Sst2 敲除增加 GPCR 生物传感器灵敏度的先前报道。
3. **Shaw et al. 2019** (Nat. Commun.) — sTF/GAL 系统用于改善 GPCR 传感器性能的早期实现。
4. **St John & Davis 1981** (J. Mol. Biol. 152, 285–315) — GAL1 启动子在半乳糖诱导下可被激活 >1000 倍的经典文献。
5. **Gandia-Herrero et al. 2010** (Planta 232, 449–460) — 甜菜色素合成路径（betacyanin/betaxanthin）的生化基础。
6. **Fan & Yuan 2023** (Cell Rep. Methods 3, 100647) — 作者组前期工作，进一步证实 Sst2 负调控 GPCR 信号。
7. **Wang et al. 2011** (Biosens. Bioelectron. 40, 368–376) — Hill 函数拟合生物传感器剂量-响应曲线的方法学参考（式 6 来源）。

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-10 | v1.0 | 初始总结，基于 PDF 全文，忠实于原文内容 |
