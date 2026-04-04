# Hu et al. (2024) — GprC 文献总结

> **原文**: Hu, X., Hoffmann, D.S., Wang, M., Schuhmacher, L., Stroe, M.C., Schreckenberger, B., Elstner, M. & Fischer, R. (2024). GprC of the nematode-trapping fungus *Arthrobotrys flagrans* activates mitochondria and reprograms fungal cells for nematode hunting. *Nature Microbiology*, 9, 1752–1763.
> **DOI**: https://doi.org/10.1038/s41564-024-01731-9
> **物种**: *Arthrobotrys flagrans* (CBS 349.94)

---

## 核心发现

GprC 是 *A. flagrans* 中的一个双功能 GPCR：
1. **在细胞质膜上**：感知线虫来源的 ascaroside，与 G 蛋白 alpha 亚基 GasA 偶联，传导信号至细胞核调控基因表达
2. **在线粒体上**：GprC 和 GasA 也定位于线粒体，激活线粒体呼吸、产生 ROS

这种双定位与人类大麻素受体 CB1 的双定位相似。

---

## 受体鉴定与功能表征

### 六个 GPCR 候选基因 (gprA–F)

- 作者通过蛋白质 BLAST 在 *A. flagrans* 基因组中鉴定了 14 个推定受体编码基因
- 排除了与已知非 ascaroside 受体相似的 GPCR 后，聚焦于 6 个候选基因：**gprA–F**
- 序列分析显示 GprC 含有：
  - N 端前 30 个氨基酸的信号肽
  - 第 82 位氨基酸后的线粒体靶向信号（MTS），线粒体定位概率 98.41%
  - GprD、E、F 的线粒体定位概率很低（分别为 2.58、43.86、34.12%）

### 基因敲除实验结果

| 突变体 | 捕陷器数量变化 | 结论 |
|--------|------------|------|
| ΔgprC | **最显著减少** | GprC 在捕陷器形成中发挥关键作用 |
| ΔgprB, ΔgprD | 较小影响 | 可能参与信号过程 |
| ΔgprA, ΔgprE, ΔgprF | 无显著影响 | 不参与 ascaroside 感应 |

- **gprC** 在线虫诱导后 RT-qPCR 显示显著上调（约 3 倍）
- 过表达 gprC（使用 *A. nidulans* oliC 启动子）显著增加捕陷器数量
- GprC 回补实验恢复了 ΔgprC 突变表型

---

## G 蛋白下游信号

### 三个 G 蛋白 alpha 亚基

- *A. flagrans* 基因组编码三个 Gα 亚基：**GasA** (dfl_009501)、**GasB** (dfl_000801)、**GasC** (dfl_009358)
- **ΔgasA**：完全丧失捕陷器形成能力；回补可恢复
- **ΔgasB**：也影响捕陷器形成（但 gasC 无明显影响）
- 用 8'-Br-cAMP（cAMP 类似物）可以挽救 ΔgasA 突变表型 → 说明 GasB 使用 cAMP 通路
- 8'-Br-cAMP 不能挽救 ΔgprC 突变体，且对 WT 无影响 → 说明 **GprC–GasA 信号通过 MAP kinase 通路**而非 cAMP 通路

### 信号通路归属

| 受体-G蛋白对 | 信号通路 |
|-----------|--------|
| GprC–GasA | **MAPK 通路**（Fus3, Slt2, Hog1 磷酸化） |
| GasB | **cAMP–PKA 通路** |

---

## GprC 的双定位

### 细胞质膜定位

- GprC-GFP 融合蛋白（使用强 oliC 启动子或原生启动子）在菌丝中可视化
- 过表达时：定位于丝状结构（菌丝内隔室）和细胞质膜
- 原生表达时：菌丝顶端主要在线粒体，远离顶端在细胞质膜
- 在捕陷器中：同时存在于细胞质膜和线粒体

### 线粒体定位

- 使用 Mitotracker 共染证实 GprC 与线粒体共定位
- 亚细胞分级分离实验：
  - GprC-GFP（~90 kDa）在线粒体组分（P1, P2）和细胞质膜组分（P3）中均检测到
  - 蛋白酶 K 处理后所有组分中融合蛋白均被降解 → GprC 位于线粒体外膜
- **Split-GFP 双荧光互补实验**：仅在线虫诱导后（+N），GprC 和 GasA 互补产生荧光信号，证实二者在活体中物理互作

### GprC–GasA 互作验证

- 酵母双杂交（Y2H）证实 GprC 的 C 端尾部（111 个氨基酸）与 GasA 互作
- C 端尾部与 GasA 的互作甚至略强于全长 GprC

---

## GprC–GasA 信号控制基因表达与线粒体呼吸

### 基因表达调控

- *A. flagrans* 通过 6-甲基水杨酸（6-MSA）和小分子挥发物引诱 *C. elegans* 进入捕陷器
- Ascaroside 抑制 artA 基因簇（聚酮合酶，负责 6-MSA 和 arthrosporol 合成）的表达
- artA 启动子-reporter 实验：WT 中线虫/ascr#18 处理后 artA 表达下降（核内 mCherry 信号消失）
- ΔgasA 和 ΔgprC 突变体中 artA 启动子不响应

### MAP kinase 磷酸化

- 线虫诱导 3h 后，WT 中 HogA 和 MakB 被磷酸化；MakA 磷酸化水平在 WT 和突变体中一致
- ΔgasA 和 ΔgprC 中 HogA 和 MakB 磷酸化缺失
- → GprC–GasA 信号独立于 MakA，通过 HogA 和 MakB

### 线粒体呼吸

- CellROX 染色：WT 菌丝顶端在线虫诱导后 ROS 信号显著增加
- ΔgprC 和 ΔgasA 中 ROS 信号微弱且不显著
- 氧消耗率（OCR）测量：WT 在线虫诱导后氧消耗增加；ΔgprC 和 ΔgasA 不增加
- → GprC–GasA 在线粒体处直接激活呼吸

---

## 分子对接结果（与本项目直接相关）

### 方法

- 使用 AlphaFold 预测结构，pLDDT > 0.85（跨膜螺旋区域）
- 突变受体使用 AF2 web server 建模（5 models per output, 24 max_recycles, 2 num_ensemble）
- 配体使用 Avogadro 构建，Orca 在 B3LYP/def2-TZVP 水平优化
- 配体使用 ADFR suite 的 'prepare_ligand' 工具处理：ascarylose 环上非环内的单键设为可旋转，产生 7–11 DOFs
- 原子电荷使用 Gasteiger 电荷模型
- **AutoDock Vina** 对接参数：box size 40 Å，以受体质心为中心，exhaustiveness = 200，spacing = 0.1 Å
- 分析前 5 个结合位姿（binding poses）

### 结合位点特征

所有三个受体（GprC、SRBC64、DAF37）的正构结合位点（orthosteric binding site）位于**胞外侧**：

- **结合口袋位置**：位于跨膜螺旋之间的锥形空间，胞外侧开口，胞内侧受空间位阻限制
- **7 个跨膜结构域中**，TM1 和 TM4 不参与配体结合，其余 5 个（TM2, 3, 5, 6, 7）活跃参与
- **ECL2**（连接 TM4 和 TM5 的胞外环 2）在 GprC 和 SRBC64 中参与配体结合，但 DAF37 中该环更长且不参与结合

### 保守残基（使用 Ballesteros-Weinstein 编号系统）

| 位置 | GprC | SRBC64 | DAF37 | 说明 |
|------|------|--------|-------|------|
| Pro2.53 | 有 | 有 | 有 | TM2 中最保守残基后第 3 位 |
| **Asp2.50** | **有** | **有** | **有** | **三个受体中高度保守** |
| TM6 保守位 | Pro（GprC, SRBC64） | Pro | Trp（DAF37） | |

### 关键突变实验

| 受体 | 突变 | 位置 | 效果 | 结论 |
|------|------|------|------|------|
| GprC | **N2.53→Ala** | 胞内侧 | 无影响 | 胞内侧结合位点不重要 |
| GprC | **N2.57→Ala** | 胞外侧 | **丧失功能** | 胞外侧为正构结合位点 |
| SRBC64 | **N2.60→Ala** | 胞外侧 | 影响功能 | 与 GprC 一致 |
| GprC | **R6.45→Ala** | R-motif | **结合亲和力剧烈下降** | R-motif 对功能关键 |
| GprC | **S2.41→Ala** | S-motif | 实验确认对功能关键 | S-motif 参与信号传导 |

### S-motif 和 R-motif

- 比较 GprC 与 *C. elegans* ascaroside 感应 GPCR 的序列，发现两个保守序列基序：
  - **S-motif**：位于 TM2 的 S2.41 位置，仅存在于 GprC 和 SRBC64（DAF37 和 DAF38 中无）
  - **R-motif**：位于 R6.45，三个受体中均存在
- R-motif 中的 Arg 指向结合位点；突变为 Ala 后结合亲和力剧降，且实验确认功能丧失
- S-motif 虽远离结合位点但被实验确认为功能所必需，推测参与信号传导

---

## 嵌合受体实验（与本项目 §3.6 直接相关）

### 嵌合设计策略

- 为测试 *C. elegans* 受体能否回补 *A. flagrans* 的 ΔgprC 表型
- 从 *C. elegans* cDNA 成功克隆了 4 个候选基因：SRBC64/66、DAF37/38
- 全长 *C. elegans* 受体在 *A. flagrans* 中**均无法恢复**捕陷器形成 → 可能缺乏匹配的下游信号组分

### 嵌合蛋白设计

- 策略：**保留后 3 个跨膜螺旋（TM5-7）来自 *A. flagrans***（确保胞内信号传导），**前 4 个跨膜螺旋替换为 *C. elegans* 受体**
- 结果：
  - **SRBC64/66 前 4 TM + GprC 后 3 TM** → 功能性嵌合受体（恢复捕陷器形成）
  - **DAF38 前 4 TM + GprC 后 3 TM** → 功能性
  - **DAF37 前 4 TM + GprC 后 3 TM** → **不功能**
  - **Octr-1（非 ascaroside 受体，阴性对照）前 4 TM + GprC 后 3 TM** → 不功能

### 嵌合受体的对接分析

- SRBC64-GprC 嵌合体：ascaroside 结合位点位于 TM1, 2, 7 之间，S-motif（S2.41）仍在相同位置
- DAF37-GprC 嵌合体：结合位点完全不同（位于 TM3, 5, 6, 7 之间），且 S-motif 缺失 → 解释了为何不功能

---

## 进化意义

- GprC 与 *C. elegans* SRBC64/66 共享 ascaroside 结合位点，尽管序列相似性低
- SRBC66 也被预测具有线粒体双定位（82.92% 概率）
- 其他真菌的 GPCR 也被预测具有双定位（如 *A. nidulans* GprH，74% 线粒体定位概率）
- 提示 GPCR 双定位在真菌中可能是保守的，跨越 4 亿年的趋同进化

---

## Methods 中的对接参数细节

| 参数 | 值 |
|------|------|
| 结构来源 | AlphaFold Protein Structure Database |
| pLDDT 阈值 | > 0.85（跨膜区域） |
| 突变建模 | AF2 web server, 5 models, 24 max_recycles |
| 配体构建 | Avogadro |
| 配体优化 | Orca, B3LYP/def2-TZVP |
| 受体准备 | ADFR suite 'prepare_receptor' |
| 配体准备 | ADFR suite 'prepare_ligand'（ascarylose 环外单键设为可旋转，7–11 DOFs） |
| 原子电荷 | Gasteiger charge model |
| 对接软件 | **AutoDock Vina** |
| Grid box | 40 Å, 以受体质心为中心 |
| Exhaustiveness | 200 |
| Spacing | 0.1 Å |
| 分析 | 前 5 个结合位姿 |
| 配体 | ascaroside #1, #2, #3, #5, #18 |
| 对接受体 | GprC, SRBC64, DAF37 及嵌合体 |
| 结构比对工具 | TM-align (TM score > 0.7 表示结构相似) |

---

## 与本项目的关键关联

1. **GprC (A0A437AGY2)** 是 *A. flagrans* 中 ascaroside 感应的核心受体，功能已通过基因敲除/回补/过表达实验验证
2. **GprC 通过 MAPK 通路**（非 cAMP-PKA）传导信号，与 Kuo et al. 中 Gpr2/Gpr3 的 cAMP-PKA 通路**不同**
3. 对接参数（AutoDock Vina, box size 40 Å, exhaustiveness 200）可作为本项目的参考
4. **嵌合蛋白策略**：前 4 TM 替换 + 保留后 3 TM 的设计思路对 §3.6 有直接参考价值
5. S-motif 和 R-motif 是筛选/改造 ascaroside 受体特异性的潜在靶点
6. 对接用了 5 种 ascaroside（#1, #2, #3, #5, #18），而非仅 #3 和 #18

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-03 | v1.0 | 初始总结，忠实于原文内容 |
