# Fan C & Yuan 2023 — 文献总结

> **完整标题**: Reshaping the yeast galactose regulon via GPCR signaling cascade
> **期刊**: *Cell Reports Methods* 3, 100647, December 18, 2023
> **DOI**: 10.1016/j.crmeth.2023.100647
> **作者**: Cong Fan, Jifeng Yuan
> **机构**: State Key Laboratory of Cellular Stress Biology, School of Life Sciences, Faculty of Medicine and Life Sciences, Xiamen University, Fujian 361102, China

---

## 核心发现（5–10 bullets，含数据）

- **设计合成转录因子（sTF）桥接 GPCR 信号至 GAL 调控子**：将 Ste12 的 pheromone response domain (PRD, aa 216–688) 与 Gal4 的 DNA binding domain (DBD, aa 1–147) 融合，生成 sTF（Gal4-Ste12）。该 sTF 在 α-factor 激活 GPCR 通路后，通过 Fus3 磷酸化 PRD 域被激活，进而驱动 GAL 启动子（*P_PRE*）控制的基因表达。
- **基础菌株设计**：在 CEN.PK2-1C 背景上构建 *Δfar1 Δgal80 Δgal4* 三缺失菌株（Sc-Base），其中 *far1* 缺失防止 α-factor 诱导的 G1 细胞周期停滞，*gal80* 和 *gal4* 缺失消除 GAL 原生调控网络，防止超过 100 个 mating 相关基因被非特异性激活。
- **Gpa1 过表达降低信号泄漏**：Sc-Base 菌株初始 sTF 表达有泄漏（高基础 EGFP）；通过在组成型中强度启动子 *P_TEF2* 下过表达 Gpa1（Sc-B1 菌株），显著降低基础活性，机制为过量 Gα 快速封存游离 Gβγ，抑制下游信号激活。
- **Ste2 过表达增强最大输出**：在 Sc-B1 基础上过表达 Ste2（Sc-B2），6 h 培养后最大 EGFP 信号明显增强，表明受体表达量是信号通量的限速因素之一。
- **Bar1 缺失提高灵敏度**：Bar1 是分泌型 aspartyl protease，降解 α-factor；敲除 *BAR1*（Sc-B3 菌株）后，检测限大幅提高，可在更低 α-factor 浓度下激活信号。
- **组合优化菌株性能参数**：Figure 2F 报道了不同设计的性能比较。Sc-B1 菌株 Hill 系数 = 0.59 ± 0.11，EC₅₀ = 0.47 ± 0.05 nM，动态范围 = 4.99 倍。
- **群体感应（Quorum-Sensing）行为实现**：通过葡萄糖抑制性启动子（*P_ADH2* 或 *P_HXT7*）驱动 *MFα1*（编码 α-factor 前体），使酵母在批次培养阶段不分泌 α-factor，进入补料阶段（葡萄糖耗尽）后自动分泌，α-factor 积累至阈值触发邻近细胞的 GPCR 信号 → GAL 基因表达。Sc-ADH2α 菌株在约 36–48 h 出现 EGFP 延迟表达。
- **热激信号感知应用扩展**：选用热休克响应启动子 *P_SSA3* 驱动 α-factor 分泌（Sc-SSA3α 菌株），在 30°C 培养 6 h 后施加 37°C 热激 2 h，α-factor 积累 → GPCR 信号 → EGFP 表达升高并持续至 48 h，实现了对瞬时物理刺激的持久记忆功能。
- **GAL 调控子的优势**：与直接使用 *FUS1* 启动子相比，GAL 系统仅控制少数基因（GAL1、GAL2、GAL7、GAL10），避免了原生 mating 通路激活 >100 个基因的副作用；且所有已商业化的 GAL 表达质粒可直接 "plug in" 到该系统。

---

## 实验方法（表格）

| 方法 | 用途 | 关键细节 |
|------|------|---------|
| sTF 构建 | 桥接 GPCR 信号至 GAL 系统 | Ste12 PRD (216–688) + Gal4 DBD (1–147)；*P_STE12* 启动子驱动 sTF 表达 |
| CRISPR/Cas9 基因组编辑 | 菌株构建 | *Δfar1 Δgal80 Δgal4* 三缺失 + *STE2* DBD 替换为 Gal4 DBD |
| Gpa1 过表达 | 降低信号泄漏 | *P_TEF2*-GPA1 整合，组成型中强度表达 |
| EGFP 荧光报告 | 定量信号输出 | *P_PRE*（GAL 启动子）驱动 EGFP；微孔板读数仪和流式细胞术 |
| 剂量-响应曲线 | EC₅₀ 和动态范围测定 | α-factor 浓度梯度 0.01–10,000 nM；EGFP/OD₆₀₀ |
| 葡萄糖抑制性启动子 | 群体感应回路 | *P_ADH2* 和 *P_HXT7* 分别驱动 *MFα1*；批次/补料两相表达 |
| 热休克启动子 | 物理刺激感知 | *P_SSA3*、*P_HSP104*、*P_CPR6*、*P_HSP82* 筛选，Sc-SSA3α 背景最低泄漏 |
| 荧光显微镜 | 群体感应空间分布可视化 | 亮场 + 荧光拍摄，4/8/12/24 h 时间序列 |

---

## 关键数据（分小节）

### 菌株性能参数（Figure 2F）

| 菌株 | 基因型特征 | Hill 系数 | EC₅₀ (nM) | 动态范围 |
|------|---------|---------|----------|--------|
| Sc-B1 | Δfar1 Δgal80 Δgal4 + P_TEF2-Gpa1 | 0.59 ± 0.11 | 0.47 ± 0.05 | 4.99 |
| Sc-B3 | Sc-B1 + ΔBar1 | — | — | — |
| Sc-B4 | Sc-B3 + HIS-function | 1.28 ± 0.05 | 0.97 ± 0.05 | 25.23 ± 0.55 |

> 注：Sc-B2 和 Sc-B3 部分参数在正文和补充图中报道，但 Figure 2F 仅列出 Sc-B1 和 Sc-B4 完整参数。

### GPCR 通路组件调控效果

| 改造 | 效果 | 机制 |
|------|------|------|
| *P_TEF2*-Gpa1 过表达 | 基础 EGFP 从 ~4.5 降至 ~1 AU | 过量 Gα 封存游离 Gβγ |
| Ste2 过表达 | 最大 EGFP 从 ~25 增至 ~40 AU | 增加受体密度→更多信号转导 |
| *ΔBar1* | 左移剂量-响应曲线（更灵敏） | 阻止 α-factor 蛋白酶降解 |
| Sst2 过表达 | 降低灵敏度 + 增加群体感应延迟 | RGS 蛋白加速 Gα-GTP 水解 |

### 群体感应行为

- *P_ADH2*-MFα1：批次阶段（葡萄糖 >0.1%）无表达 → 葡萄糖耗尽后去抑制 → α-factor 累积 → EGFP 延迟表达（~36 h 起）
- *P_HXT7*-MFα1：更强的葡萄糖抑制，延迟更明显
- Sst2 过表达进一步延长延迟并降低最大输出
- Sst2 敲除则导致早期泄漏和群体感应行为消失

### 热激记忆

- Sc-SSA3α：30°C → 37°C（2 h）→ 30°C
- EGFP 在热激后持续升高至 48 h（α-factor 形式的信号记忆）
- 对照菌株（30°C 全程）无 EGFP 升高

---

## 与项目的关系

本文提供了一种将 GPCR 信号重定向至 GAL 调控子的策略，对项目的下游信号放大和读出设计有以下参考价值：

1. **sTF 设计原理**：Ste12 PRD + Gal4 DBD 的融合策略，提供了一种替代直接使用 *FUS1* 启动子的方案——GAL 系统仅调控少数基因，避免了 mating 通路全激活带来的细胞毒性和副反应。

2. **Gpa1 过表达降低泄漏**：*P_TEF2*-Gpa1 的策略可直接应用于项目中降低传感器基础信号，提高信噪比。

3. **Bar1 缺失提高灵敏度**：对于需要高灵敏度检测低浓度 ascaroside 的应用场景，Bar1 类 protease 的缺失可显著左移 EC₅₀。

4. **群体感应行为**：葡萄糖抑制性启动子驱动 α-factor 分泌的策略，展示了利用 GPCR 通路实现自主代谢控制的可能性。

5. **GAL 系统兼容性**：所有已商业化的 GAL 表达载体（pYES 系列等）可直接在该系统中使用，降低了构建下游输出模块的技术壁垒。

> 注：以上为文献内容与项目的关系分析，不含项目实验数据。

---

## 关键引用（原文 References 节选）

1. **Shaw et al. 2019 *Cell*** (ref 16) — 底盘菌株设计的直接基础；sTF 中 Ste12 PRD 的使用受此工作启发。
2. **Gal4 DBD** (ref 18, Bardwell 2005) — Gal4 DBD (1–147) 的来源和 yeast mating pathway walk-through 综述。
3. **Ingolia and Murray 2007** (ref 50) — 正反馈回路作为灵活生物模块的参考。
4. **Yu et al. 2008 *IET Syst. Biol.*** (ref 43) — Alpha Project 系统生物学模型，本文用于信号通路建模讨论。
5. **Fan C, Zhang D, et al. 2022 *Microb. Biotechnol.*** (ref 58) — 同一实验室先前工作（酵母 GPCR 铜离子传感器）。
6. **Song J, Fan J, et al. 2023 *ACS Synth. Biol.*** (ref 59) — 同一实验室的后续工作（氰胺响应的分层遗传设计），展示 GAL 调控子的进一步应用。
