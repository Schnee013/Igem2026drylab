# Velazhahan et al. 2021 — 文献总结

> **完整标题**: Structure of the class D GPCR Ste2 dimer coupled to two G proteins
> **期刊**: Nature, Vol.589, pp.148–153
> **DOI**: 10.1038/s41586-020-2994-1
> **作者**: Vaithish Velazhahan, Ning Ma, Gáspár Pándy-Szekeres, Albert J. Kooistra, Yang Lee, David E. Gloriam, Nagarajan Vaidehi, Christopher G. Tate
> **机构**: MRC Laboratory of Molecular Biology, Cambridge, UK; City of Hope, Duarte, CA; University of Copenhagen; Aarhus University
> **PDB**: 7AD3

## 核心发现

1. **首个 Class D GPCR 实验结构**: Ste2 是 *Saccharomyces cerevisiae* 的 α-factor pheromone receptor，属于 Class D GPCR（真菌专属），此前无实验结构。Cryo-EM 分辨率 3.3 Å。

2. **Ste2 以同源二聚体形式偶联两个 G 蛋白三聚体**: 复合物组成为 Ste2₂ dimer + 2× mini-Gpa1 + 2× Ste4 (Gβ) + 2× Ste18 (Gγ) + 2× α-factor。每个 Ste2 protomer 独立结合一个完整 G 蛋白三聚体。

3. **Ste2 与 Class A GPCR 拓扑相似但更薄**: Ste2 具有 7 跨膜螺旋（H1–H7），N-terminus 胞外、C-terminus 胞内，与 Class A GPCR 整体拓扑一致。但 Ste2 跨膜区厚度约 20 Å（Class A 为 ~40 Å），且配体结合位点在胞外表面而非膜内腔。

4. **mini-Gpa1 是工程化截短版本**: 基于 mini-Gs 设计（Nehme et al. 2017），截断了 Gpa1 的 N-terminus 和 α-helical domain，保留 Ras domain（含 α5 helix）。mini-Gpa1 用于稳定活性状态复合物，**并非全长 WT Gpa1**。

5. **G 蛋白界面位于 ICL2 和 TM 螺旋**: Gpa1 的 α5 helix C-terminus 插入 Ste2 胞内腔，主要接触 ICL2（H4-ECL2 loop）、H3 和 H6。Ste2 与 Gpa1 之间有 24 个 van der Waals 接触和 23 个氢键（mini-Gpa1 的 α5 helix 贡献大部分）。

6. **Ste2₂ dimer 界面极大**: 二聚体界面 ~12,930 Å²，由 H1、H4-ECL2、H5 的接触组成。Ste4/Ste18 (Gβγ) 不与 Ste2 直接接触。

7. **MD 模拟揭示无 G 蛋白时的构象变化**: 分子动力学模拟显示，移除 G 蛋白后 Ste2 的 H5–H6 向 G 蛋白结合位点移动，阻塞 Gpa1 结合。这与 Class A GPCR 的活化机制不同。

## 实验方法

### 样品制备
- **Ste2 表达**: Codon-optimized *S. cerevisiae* Ste2 (残基 1–421) 在 *E. coli* 中重组表达（TEV cleavable GFP + decahistidine tag），LDAO/CHS 增溶
- **mini-Gpa1**: 基于 mini-Gs 设计，含 S. cerevisiae Gpa1 Ras domain，加 4× 突变稳定活性状态 + HA tag + TEV site
- **复合物组装**: Ste2 + mini-Gpa1 + Ste4 + Ste18 + α-factor，1:1.3 摩尔比孵育，SEC 纯化
- **Cryo-EM**: Titan Krios 300 kV，K3 detector，3.3 Å 分辨率

### 结构建模与验证
- Ste2 从头建模（无同源结构）
- mini-Gpa1 用 Gpa1 Ras domain 晶体结构 (PDB 6DGV) 作为起始模型
- Ste4/Ste18 用 Gβγ 同源模型
- MD 模拟: 4 个独立 25 ns 模拟（有/无 G 蛋白，2D/3D 条件）

## 关键数据

### Ste2 dimer 界面
- 两个 Ste2 protomer 形成广泛的二聚体界面
- 界面涉及 H1, H4-ECL2, H5 的跨膜和胞外区域
- Class D1 受体（包括 Ste2 同源物）中 ≥65% 保守的界面残基标注于 Fig. 2d

### G 蛋白结合位点
- Gpa1 α5 helix 插入 Ste2 胞内腔
- 主要接触残基:
  - Ste2 侧: ICL2 区域残基（Pro183, Leu211, Tyr213 等）, H3 胞内端, H6 胞内端
  - Gpa1 侧: α5 helix 残基 + β6-α5 loop 残基
- Ste4/Ste18 不与 Ste2 直接接触，仅通过 Gpa1 间接连接

### α-factor 结合位点
- 正构结合位点位于 Ste2 胞外半段
- α-factor 关键残基: Tyr13 与 Ste2 形成最多接触，His94^CD1.56^ 形成氢键
- Trp residues (Trp1, Trp3) 在胞外区域形成 cation-π 相互作用

### 与其他 GPCR 的比较
- Ste2 G 蛋白结合面与 Class A GPCR 类似但 H5-H6 运动模式不同
- Class A 中 ICL2 插入 Gα 疏水口袋，Ste2 中 ICL2 形成更扁平的接触面
- Ste2 结构提示 Class D GPCR 可能用不同机制激活 G 蛋白

### CD1 编号系统
- 作者引入 Class D1 numbering system（类似 BW 编号），用于跨物种 Class D 受体残基对齐

## 与项目的关系

### 对 AF3 嵌合 Gpa1 预测结果解读的意义

1. **AF3 训练集包含 Ste2-Gpa1 模板**: PDB 7AD3 于 2020 年 12 月发表，在 AF3 训练截止日期之前。因此 AF3 预测 Ste2-WT 复合物时有实验结构模板可供学习。Ste2-WT ipTM=0.60（勉强达标）**不能用"无模板"解释**。

2. **mini-Gpa1 vs 全长 Gpa1**: 实验结构中使用的是 mini-Gpa1（截短了 N-terminus 和 α-helical domain），而我们的 AF3 预测使用全长 Gpa1。AF3 可能因全长 Gpa1 的额外 domain 产生更多不确定性，导致 ipTM 偏低。

3. **G 蛋白界面特征**: Gpa1 α5 helix 是 Ste2 识别的核心界面。嵌合 Gpa1 的 C-terminal 替换（5/10/15 aa）恰好覆盖 α5 helix 末端区域——这是决定受体偶联特异性的关键位点。

4. **Ste2 二聚体**: 实验证明 Ste2 以同源二聚体形式与 G 蛋白偶联。AF3 预测中我们只提交了 Ste2 单体 + Gpa1，这可能影响预测质量。

5. **Class D 特殊性**: Ste2 属于 Class D GPCR（真菌专属），与哺乳动物 Class A GPCR 的 G 蛋白激活机制存在差异。真菌 GPCR（Gpr2/3/GprC）可能也有类似差异，这对 AF3 预测的可靠性有影响。

## 关键引用

- **mini-G 蛋白设计**: Nehme et al. 2017 (*PLoS ONE* 12:e0175642)
- **Ste2 先前研究**: Naider & Becker 2004 (factor-receptor interaction model); Lee et al. 2006, 2007 (TM domain function)
- **Class D 受体分类**: Atwood & Findlay 1994; Kolakowski 1994 (GCRDb)
- **Ste2 二聚体**: Overton & Blumer 2000; Kim et al. 2009 (TM glycine zippers)
- **G 蛋白结构**: Flock et al. 2017 (universal allosteric mechanism for Gα activation)
