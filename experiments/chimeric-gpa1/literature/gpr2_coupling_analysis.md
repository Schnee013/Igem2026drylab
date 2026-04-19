# Gpr2-AoGpa2 偶联评估与 AF3 ipTM 反常分析

> **调研日期**: 2026-04-17
> **调研来源**: Phase 0B-1 (偶联机制) + Phase 0B-3 (AF3 校准)

---

## 1. 问题

AF3 预测 Gpr2 × AoGpa2 (cognate) 的 ipTM = 0.44-0.46，反低于 Gpr2 × AfGasA (cross) 的 0.55-0.56（Δ = -0.082）。这是否意味着 Gpr2-AoGpa2 偶联不可行？

## 2. Kuo 2024 / Chen 2022 中 Gpr2-Gpa2 偶联证据

### 证据强度：中等

| 证据类型 | 来源 | 内容 | 强度 |
|---------|------|------|------|
| Co-IP (酵母异源表达) | Kuo 2024 | Gpr2-3xHA 与 Gpa2-Myc pull-down 确认物理互作；Gpr2 不与 Gpa1 或 Gpa3 互作 | 中（证明选择性结合，但 co-IP 不报告亲和力强弱） |
| 遗传互作 | Kuo 2024 | 显性活化 Gpa2(Q208L) 可在 Δgpr2 背景下 rescue 表型 | 强（遗传互作明确） |
| cAMP 测量 | Kuo 2024 | Δgpr2 突变体 cAMP 不升高 | 中（间接支持 Gpr2→Gpa2→AC 通路） |
| 通路定位 | Chen 2022 | Δgpa2 trap 数减少，外源 cAMP 可 rescue | 中（确认 Gpa2 在 cAMP-PKA 通路上游，但未研究 Gpr2） |

**关键缺失**: 两篇文献均无 GTPγS binding assay、BRET/FRET、SPR 或任何直接测量 Gpr2-Gpa2 偶联动力学的实验。Kuo 2024 原文用 "strongly interact" 描述 co-IP 结果。

## 3. ICL2/ICL3 在 Class D GPCR 偶联中的角色

### 3.1 Ste2 结构证据 (Velazhahan 2021/2022)

- Gpa1 的 α5 helix C 端插入 Ste2 胞内腔，主要接触 **ICL2** (Asn158 等) + H3 + H6
- Ste2 激活时 **H7 胞内端 20 Å 外摆**解除对 G 蛋白结合位点的封锁
- **ICL3 内移** + ICL2 侧向平移 1-2 Å 重新定位关键残基

### 3.2 哺乳动物体系平行证据

- Nature 2023: ICL3 通过构象平衡调控 G 蛋白选择性（"负选择"机制）
- 多个 cryo-EM 综述：G 蛋白选择性 = α5 helix + ICL2 + ICL3 协同，非单一界面决定
- Dominant G protein subtypes 与 ICL2 展现更多互作

### 3.3 Gpr2 的 ICL3 特殊性

**Kuo 2024 明确指出 Gpr2 的 ICL3 (残基 217-336, ~120 aa) 被 AlphaFold 预测为 random coil / 无序区域。** 这一长无序 ICL3 在 AF3 预测中很可能无法正确折叠。

## 4. AF3 ipTM 校准基准

### 4.1 哺乳动物 GPCR-Gα AF3 ipTM 分布

来自组胺受体研究 (PMC11946611, 2025)，12 个 H1R-H4R × Gs/Gi/Gq 复合物：
- **范围: 0.67-0.79，均值 ~0.72**
- RMSD 与实验结构仅 0.67-1.19 Å

### 4.2 Ste2×Gpa1 ipTM=0.60 偏低原因

三重叠加：
1. **GPCR-Gα 复合物的结构性 ipTM 压低**：全长 Gpa1 大量非界面残基参与 d0 归一化（ipSAE 论文 PMC11844409 证明此效应）。GproteinDb 将 GPCR-Gα ipTM 准入阈值降至 **≥ 0.2**
2. **Class D 训练不足**：AF3 训练集中 Class D 仅有 PDB 7AD3 (Ste2-Gpa1) 一个实验结构（2020-12 发表，在 AF3 cutoff 之前）。但 AoGpa2 与 Gpa1 属不同 Gα 亚型，7AD3 模板对 Gpr2-AoGpa2 的帮助有限
3. **单体 vs 二聚体**：Ste2 实验为同源二聚体偶联 G 蛋白，我们提交单体

### 4.3 嵌合体 ipTM 0.38-0.50 的正确解读

- 以 WT 归一化：Top1 = 0.50/0.60 = **83%**，保留大部分界面信号
- cognate vs cross Δ 比绝对值更可信
- 在 GproteinDb 框架下（≥ 0.2）全部合格
- 须 MD 验证而非依赖绝对阈值

## 5. 结论：Gpr2 × AoGpa2 cognate ipTM 低 = AF3 假阴性

**判断：高概率 AF3 假阴性**，三重机制叠加：

| 机制 | 证据 |
|------|------|
| (a) 无序 ICL3 (~120 aa) | Kuo 2024 Fig.3c; AF3 无法建模无序区的 G 蛋白接触 |
| (b) 训练集偏差 | AF3 训练集含 PDB 7AD3 (Ste2-Gpa1)，但 AoGpa2 是 Class III Gα（与 Gpa1 不同亚型），无直接模板；即便有模板的 Ste2-WT ipTM 也仅 0.60 |
| (c) AfGasA 评分虚高 | AfGasA 属 Group I Gα，序列与训练集模板更相似 |

**不支持"偶联本身弱"**：Kuo 2024 co-IP 显示 "strongly interact"，Gpa2(Q208L) 遗传互作明确。

## 6. 建议

1. **不应因 AF3 ipTM 低放弃 Gpr2-AoGpa2 cognate 配对**
2. 加入 Ch-4 (Gpr2 × AoGpa2-C10, ipTM=0.46) 作为 chimeric MD 核心体系
3. MD 分析时特别关注 ICL2/ICL3 界面残基动态
4. 修复 AF3 template 设置后重新提交 Gpr2 系列（可能提升 ipTM）

---

## 引用来源

1. Kuo CY et al. (2024). Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors. *Nature Microbiology*. DOI: 10.1038/s41564-024-01679-w
2. Chen SA et al. (2022). [Arthrobotrys G protein signaling]. 
3. Velazhahan V et al. (2021). Structure of the class D GPCR Ste2 dimer coupled to two G proteins. *Nature* 589:148-153.
4. Velazhahan V et al. (2022). Activation mechanism of the class D fungal GPCR dimer Ste2. *Nature* 603:743-748.
5. Autoregulation of GPCR signalling through ICL3 (2023). *Nature*.
6. Histamine receptor-G protein AF3 benchmark (2025). PMC11946611.
7. ipSAE: ipTM score correction for multidomain complexes (2025). PMC11844409.
8. GproteinDb (2024). PMC10767870.
