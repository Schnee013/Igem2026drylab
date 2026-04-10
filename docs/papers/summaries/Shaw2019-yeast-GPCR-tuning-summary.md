# Shaw et al. 2019 — 文献总结

> **完整标题**: Engineering a Model Cell for Rational Tuning of GPCR Signaling
> **期刊**: *Cell* 177:782–796, April 18, 2019
> **DOI**: https://doi.org/10.1016/j.cell.2019.02.023
> **作者**: William M. Shaw, Hitoshi Yamauchi, Jack Mead, Glen-Oliver F. Gowers, Niklas Larsson, Mark Wigglesworth, Graham Ladds, Tom Ellis
> **机构**: Imperial College London; University of Cambridge; SynbiCITE Innovation and Knowledge Centre; AstraZeneca R&D (Mölndal, Sweden)

---

## 核心发现（5–10 bullets，含数据）

- **基因组重构（Genomic Refactoring）建立了极简 GPCR 模型菌株**：通过 9 轮 CRISPR/Cas9 编辑，从 BY4741 出发敲除 15 个基因（包括 SST2、FAR1、BAR1、STE2、GPR1/2、MF(ALPHA)1/2、MFA1/2、STE3），仅保留 MAPK 级联核心五基因（*STE2、GPA1、STE4、STE18、STE12*），生成模型菌株 yWS1922。
- **数学模型（三元复合物 cubic ternary complex model）指导实验**：对 GPCR（Ste2）、Gα（Gpa1）、Gβγ（Ste4-Ste18）表达量分别进行 in silico 扫描，预测最优启动子范围；实验验证与模型预测高度一致——Gα 和 Gβγ 均存在使信号折叠变化最大的最优表达量（非单调关系）。
- **Gβγ 升高会降低最大输出**：模型预测并实验证实，高水平 Gβγ 因竞争性结合导致 Ste5 错误转运，使最大信号输出降低；这揭示了 G 蛋白化学计量精密调控的必要性。
- **合成转录因子（sTF）将输出动态范围提高至 ≥250 倍**：用细菌 LexA DBD 与 Ste12 PRD 融合，驱动含可替换 UAS 和核心启动子的合成启动子，实现 GFP 最大表达高于 pCCW12 原生启动子驱动 Ste12 的约 250 倍；TetR-PRD 融合体系引入 anhydrotetracycline（aTc）化学控制层。
- **迭代重构设计空间（Design 1–4）优化剂量–响应曲线**：依次重构 Ste2（GPCR）、Gpa1（Gα）、Ste12（报告基因）、sTF 报告输出；最终 Design 4 与 Quasi-WT 相比，灵敏度、动态范围、最大输出和操作范围均获改善。
- **工程微生物联合体（Consortia）突破单菌株操作范围限制**：将三株对腺苷敏感度不同（但最大输出相同）的 A2BR 传感菌株等比混合，将操作范围从 1.56 个数量级（单株）扩展至 3.27 个数量级（50 倍提升）；MTNR1A（褪黑素）双株扩增-报告系统将操作范围从 3.79 扩展至 3.8（同时产生数字化响应）。
- **感知褪黑素应用**：用 MTNR1A 传感菌株读取 88 株微生物发酵产褪黑素的产量，LC-MS 定量与传感器读数线性相关（R²=0.91）；说明传感器可用于代谢物定量。
- **异源 GPCR 表达（>50 种 GPCR 可在酵母中功能性偶联）**：模型菌株提供了快速（<1 周）domestication 新 GPCR 的平台；以 *S. pombe* Mam2 受体为例，在 yWS677 中3周优化、<1周移植至传感器菌株，实现对 P-factor 的高灵敏度检测（logEC50 = −8.88）。

---

## 实验方法（表格）

| 方法 | 描述 |
|------|------|
| CRISPR/Cas9 多重编辑 | 使用 ScaI/MscI 切割的打靶质粒，9 轮编辑共修改 18 个基因组位点；每轮 PCR + 纳米孔长读测序验证 |
| 启动子文库 | 来自文献报道的 S. cerevisiae 天然启动子，驱动 Ste2、Gpa1、STE4-24A-STE18 融合、Ste12、stGFP |
| 流式细胞术（Flow Cytometry） | 三联株单细胞 sfGFP 测量，Mean ± SD；剂量-响应曲线用 GraphPad Prism 四参数 nonlinear regression 拟合 |
| 数学建模 | 三元复合物（cubic ternary complex）ODE 模型，MATLAB 数值求解；参数由启动子强度文献和实验数据估算 |
| 合成转录因子（sTF） | LexA-PRD、TetR-PRD、Z3E-PRD 分别驱动含 UAS×N + 核心启动子的合成启动子 |
| 微生物联合体 | 等比混合不同灵敏度（不同启动子驱动 GPCR）的菌株；流式细胞仪读取总体荧光 |
| LC-MS 褪黑素定量 | 对 88 株产褪黑素菌株发酵上清进行 LC-MS 定量，与传感器荧光对照 |
| 板读仪（Plate Reader）检测 | P. brasiliensis PbPeptide 和 褪黑素实验中使用 β-半乳糖苷酶（sxa2 启动子）作为替代报告基因 |

---

## 关键数据（分小节）

### 模型菌株构建

- BY4741 中共删除 15 个基因（11 个来自交配信息素通路，4 个来自葡萄糖感应通路），最终保留 STE2–GPA1–STE4–STE18–STE12 核心五基因，余下基因组由纳米孔测序全程验证。

### 启动子扫描与信号调控

- GPCR（Ste2）：启动子强度越高，EC50（灵敏度）越低（越敏感），最大输出随启动子强度增大；实验验证与 ODE 模型预测一致。
- Gα（Gpa1）：存在使配体/无配体信号比最大的最优 Gpa1 水平，过高或过低均降低信噪比；模型正确预测了该非单调关系。
- Gβγ（Ste4-Ste18）：同样存在最优 Gβγ 水平；过高的 Gβγ 因竞争性 Ste5 转运而降低最大输出（最高约 25 倍，对应最低启动子强度时最佳）。

### 合成转录因子输出

- LexA-PRD 驱动含 5× LexA UAS + pCCW12 核心的合成启动子：最大 GFP ≈ 250 倍背景（pCCW12 原生 Ste12 系统约 50–100 倍）。
- TetR-PRD + pTet（7× TetO + LEU2 最小启动子）：aTc 剂量依赖性（0–100 ng/mL）调控基础活性；加 aTc 后 EC50 右移至 pCCW12 水平（约 100 nM α-factor），去除 aTc 后左移，EC50 约 1 nM。
- Z3E-PRD + pZ3（β-雌二醇诱导型）：50 µM β-雌二醇激活后，100 nM α-factor 诱发约 50 倍信号；可在单菌株中实现双配体"AND gate"逻辑。

### 联合体操作范围

| 系统 | logEC50 | Hill slope | 操作范围（orders of magnitude） |
|------|---------|-----------|-------------------------------|
| A2BR 单株 | −6.18 ± 0.02 | 1.41 | 1.56 |
| A2BR 三株混合 | −6.05 ± 0.02 | 0.78 | 3.27 |
| MTNR1A 单株 | −6.59 ± 0.03 | 0.69 | 3.79 |
| MTNR1A 双株扩增-报告 | −6.50 ± 0.08 | 1.65 | 1.48（数字化）|

### 异源 GPCR domestication 速度

- Mam2（*S. pombe* P-factor 受体）：yWS677 背景下 3 周优化 → yWS1922 移植 <1 周；logEC50 = −8.88 ± 0.05（vs. 原生 *S. pombe* 背景 −6.88 ± 0.05）。
- PbSte2（*P. brasiliensis* 受体）：单株 logEC50 = −8.43 ± 0.02，双株混合 logEC50 = −10.55 ± 0.02，操作范围从 2.33 扩展至 1.59（但 Hill slope 从 0.73 升至 1.45）。

---

## 与项目的关系

iGEM 2026 干实验计划在酵母中异源表达线虫 GPCR（GPR3 homologs 等），利用酵母信号通路感知 ascaroside 类配体。本文提供以下直接参考：

1. **底盘设计基础**：本文的极简 GPCR 模型菌株（15 基因敲除 + CRISPR 多重编辑策略）为项目的酵母底盘选择提供了最成熟的文献依据；其"只保留 MAPK 核心"的思路与项目的工程设计目标高度吻合。
2. **异源 GPCR 表达协议**：Mam2 domestication 的流程（直接替换 STE2 ORF + 条件优化 + 移植）是项目将线虫 GPCR 导入酵母底盘的可操作模板。
3. **剂量-响应调控策略**：启动子文库扫描 GPCR/Gα/Gβγ 的表达量 → ODE 模型预测最优点 → 实验验证，这套"建模优先"流程可直接应用于项目的信号通路 ODE 建模模块。
4. **灵敏度调控**：GPCR 启动子越强 → EC50 越低的规律，可指导项目在 ascaroside 浓度范围未知时选择启动子强度以覆盖生理浓度区间。
5. **传感器验证指标**：本文明确定义了 sensitivity（EC50）、dynamic range（max/basal）、operational range（5%–95% 激活区间）和 Hill slope 四个核心参数，可作为项目评估传感器性能的标准框架。

---

## 关键引用（3–8 条）

1. **Versele and Thorner (2001)** — 酵母 G 蛋白信号通路综述，本文用于介绍 GPCR 信号在 *S. cerevisiae* 中的天然背景。
2. **Bashor et al. (2008); Galloway et al. (2013); Ingolia and Murray (2007)** — 通过合成反馈回路调控酵母信号通路剂量-响应特性的先前尝试（本文指出这些方法对极简底盘无效，因为外源 sTF 不具备 Ste12 的自调控反馈）。
3. **Kofahl and Klipp (2004); Poritz et al. (2001)** — 酵母信号通路数学建模经典文献，本文用于构建 ODE 模型框架。
4. **Germann et al. (2016)** — 酵母微生物联合体产褪黑素的代谢工程研究，本文用该数据验证 MTNR1A 传感器的定量应用（R²=0.91）。
5. **Ostrov et al. (2017)** — *P. brasiliensis* PbPeptide/PbSte2 系统，本文用于展示双株联合体对真菌病原体信号肽的传感。
6. **McIsaac et al. (2014)** — Z3E（Zif268-雌激素受体 LBD 融合）合成转录因子，本文用于构建 β-雌二醇控制的第三层调控模块。
7. **Dong et al. (2010); Ladds et al. (2005a)** — 异源 GPCR-G 蛋白嵌合体在酵母中表达的方法，本文的 GPCR domestication 平台建立于此基础之上。
