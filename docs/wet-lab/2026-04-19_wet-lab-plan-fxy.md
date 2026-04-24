---
type: wet-lab-plan
source: 实验方案.pdf
author: 付欣雅 (NKU iGEM 2026)
date: 2026-04
last_updated: 2026-04-19
purpose: 湿实验组提供的最新实验方案（5 周期），干实验汇报对齐用
---

# 湿实验方案（2026-04 版） — 付欣雅

> **来源**：附件 `实验方案.pdf`（13 页），2026-NKU-iGEM 湿&干实验联席。
> **干实验用途**：对齐湿实验五周期路线图，确认干实验交付物（Top 突变 / 嵌合 Gpa1 / ODE 参数）落在哪一周期。

## 总览

**信号链路**：土壤 ascr → 异源 Gpr2/3 → 嵌合 Gpa1 → MAPK 级联 → sTF（Ste12-Gal4 融合）→ Gal 多拷贝放大 → 色素显色

**最终目标**：冻干酵母试纸条 — 通过 ascr#18 与 ascr#3 相对强度判断土壤是否存在害虫线虫。

## 五周期路线

| 周期 | 内容 | 干实验对应 |
|------|------|------------|
| **第一周期** | 底盘菌株构建（CEN.PK2-1C MATa Δgal80 Δgal4）+ 色素显色测试 + Gpr 插膜验证 | — |
| **第二周期** | GPCR-Gal 系统偶联复现（构建 Ste12 PRD + Gal4 DBD 融合 sTF；α-factor 验证 MAPK→色素） | — |
| **第三周期** | Gpr2/3 蛔苷素特异性改造 + 嵌合 Gpa1 改造 + Gpr2/3-Gpa1 相互作用验证 | **干实验主交付**：Top 突变 + 嵌合方案 |
| **第四周期** | Gpr2/3 突变体特异性验证 + 全通路验证与定量分析（ascr#18/ascr#3 双配体梯度） | **干实验交付**：Channel A/B 双通道配对 + ODE 预测 |
| **第五周期** | 试剂盒制作（冻干酵母试纸） | — |

## 关键资源

- **菌株**：CEN.PK2-1C（MATa ura3-52 his3Δ1 leu2-3,112 trp1-289），需敲 Δgal80/Δgal4，可选 Δsst2
- **质粒**：pRS313/314/315（HIS3/TRP1/LEU2 三种营养标记）+ p406TEF1（URA3+TEF1 启动子）+ pScCEN-ADH1（G418 抗性）
- **色素候选**：甜菜黄素（Betaxanthin，2 基因 CYP76AD1+DOD）vs 番茄红素（Lycopene，3 基因 CrtE/B/I）
- **报告基因策略**：PGAL1/PGAL10 双向启动子 / 2A 肽自切割 / 全诱导型 vs 混合诱导型（参考 Ostrov 2017）
- **信号肽**：α-factor prepro 序列引导异源 GPCR 入 ER → 质膜
- **荧光标签**：mCherry + 共聚焦显微镜验证插膜
- **互作验证**：BiFC（备选 pull-down / 酵母双杂交）

## 蛔苷素来源

含 PPN 土壤粗提液 / 商业合成标准品 / 同行赠予；浓度梯度 10⁻⁹–10⁻⁴ M（建议 8–10 个点）。

## 第三/四周期干实验明确分工

**第三周期 — 嵌合 Gpa1 改造**：
- 干：AlphaFold-Multimer 预测 Gpa1-Gpr2 复合体；序列比对找保守偶联残基；设计 C 端嫁接
- 湿：联系公司合成 Gpa1 + Gpr2/3（WT + 突变型）；BiFC 验证蛋白互作；接入底盘菌

**第四周期 — Gpr2 特异性 + 全通路**：
- 干：确认 Gpr2/3 ascr-binding 改造不破坏 Gpr2/3-Gpa1 偶联界面（变构干扰预测）
- 湿：双 ascr 剂量响应 → 色素显色定量

## 干实验需补充的内容（湿实验未明示）

1. **Top 突变体筛选清单**：湿实验提到"Gpr2/3 突变体"但未指定具体位点 → 干实验交付 Top 6（M327A/V138R/M327D/R59F/V138T/F170N）+ 双通道配对推荐
2. **MD 动力学实证**：湿实验仅 AlphaFold 静态结构 → 干实验补 MD 500 ns × 6 体系做 V138R 盐桥实证
3. **嵌合 Gpa1 长度档位**：湿实验未指定嫁接残基数 → 干实验交付 5 档（C5/C10/C15/C25/C37 × 2 真菌供体）+ Top 3 候选
4. **ODE 通路定量**：湿实验未涉及 → 干实验提供 STE2 通路 ODE 模型，预测剂量响应曲线 EC50 / 拷贝数敏感性

## 引用

- 底盘 + Δgal 敲除：Fan et al., Biosensors and Bioelectronics, 250 (2024) 116058
- Ste12 PRD + Gal4 DBD：Cong Fan, Jifeng Yuan, Cell Reports Methods 3, December 18, 2023, 100647
- 番茄红素 + Yeast biosensor：Ostrov et al., Sci. Adv. 2017;3:e1603221
- 甜菜黄素 + RUBY：He et al., Horticulture Research, (2020) 7:152
