# Hara et al. 2012 — 文献总结

> **完整标题**: Chimeric Yeast G-Protein alpha Subunit Harboring a 37-Residue C-Terminal Gustducin-Specific Sequence Is Functional in *Saccharomyces cerevisiae*
> **期刊**: Biosci. Biotechnol. Biochem., 76(3), 512-516
> **DOI**: 10.1271/bbb.110820
> **作者**: Keisuke Hara, Yuko Inada, Takuya Ono, Kouichi Kuroda, Yoshimi Yasuda-Kamatani, Masaji Ishiguro, Takaharu Tanaka, Takumi Misaka, Keiko Abe, Mitsuyoshi Ueda

> **注**: 文件名中的 "Ladds2005" 实际对应的是 Hara et al. 2012 这篇论文，内容如下。

## 核心发现

1. **Chimeric Galpha protein 在酵母中的功能边界**: 在 yeast Gpa1p 的 C-terminus 替换为 gustducin 序列时，替换 **37 个氨基酸** (GPA1/gust37) 的 chimera 在酵母中保持功能，而替换 **44 个氨基酸** (GPA1/gust44) 的 chimera 则丧失功能。这与哺乳动物系统中常用 C-terminal 44 aa chimera 的惯例形成对比。

2. **Full-length gustducin 无法替代 Gpa1p**: 尝试用全长 human gustducin 替代酵母内源 Gpa1p 失败 — gustducin 无法与酵母 Gbeta-gamma 亚基偶联，导致 free Gbeta-gamma 引发 constitutive signaling pathway activation 和 cell cycle arrest。

3. **C-terminus 的关键区域定义**: 包含 alpha4 helix、beta6 sheet、alpha5 helix 和 extreme C-terminus (eCT) 的 C-terminal 区域是 GPCR-Galpha 偶联的关键界面。其中 eCT 的最后 4-5 个氨基酸是 receptor coupling specificity 的主要决定因素。

4. **alpha4-beta6 loop 的结构重要性**: GPA1/gust44 失去功能可能因为 gustducin 序列替换侵入了 alpha4 helix 区域，导致蛋白质折叠缺陷。此外，Gpa1p 中的 T433 残基对功能至关重要，替换可能引起 structural conformational change。

## 实验方法

### 菌株与质粒构建
- **宿主菌株**: *S. cerevisiae* W303-1A 及其衍生株（WO-1: ste2 knockout; WO-3: ste2 gpa1 double knockout）
- **Chimeric Galpha 构建策略**: 以 yeast GPA1 为模板，将 C-terminus 的不同长度替换为 human gustducin (GNAT3) 对应序列
- **构建的 chimera 系列**:
  - **GPA1/gust4**: eCT 最后 4 aa 替换为 gustducin 序列 (CGLF)
  - **GPA1/G16-4**: eCT 最后 4 aa 替换为 promiscuous Galpha16 序列
  - **GPA1/deleted**: eCT 最后 4 aa 删除（阴性对照）
  - **GPA1/gust31 ~ gust37**: C-terminal 31-37 aa 逐一替换
  - **GPA1/gust44**: C-terminal 44 aa 替换（哺乳动物系统常用版本）
- **Mutagenesis**: QuickChange Site-Directed Mutagenesis Kit; KOD Plus DNA Polymerase

### 信号检测系统
- **Fluorescence yeast GPCR assay**: 使用 pYEX-fet reporter plasmid（FUS1 promoter 驱动 EGFP 表达）
- **Receptor**: 内源 yeast pheromone receptor Ste2p
- **Ligand**: alpha-factor（酵母 mating pheromone）
- **读数**: 加入 alpha-factor 后 2 h 测量 EGFP 荧光强度（Ex 485 nm / Em 527 nm）
- **Western blot**: 用 anti-Gpa1 antibody 确认 chimeric Galpha protein 的表达

## 关键数据

### Chimeric Galpha coupling efficiency 汇总

| Chimera | C-terminal 替换长度 | 与 Ste2p 偶联 | 对 alpha-factor 响应 |
|---------|-------------------|-------------|-------------------|
| GPA1 (wild-type) | 0 aa | + | dose-dependent |
| GPA1/gust4 | 4 aa (eCT) | + | + |
| GPA1/G16-4 | 4 aa (eCT, G16) | + | + |
| GPA1/deleted | 4 aa deleted | - | no response |
| GPA1/gust31 | 31 aa | + | + |
| GPA1/gust32 | 32 aa | + | + |
| GPA1/gust33 | 33 aa | + | + |
| GPA1/gust34 | 34 aa | + | + |
| GPA1/gust37 | 37 aa | + | + (dose-dependent, comparable to WT) |
| GPA1/gust44 | 44 aa | - | no response |

### 关键观察
- **GPA1/gust37 vs wild-type Gpa1**: 信号响应曲线高度相似，均呈 dose-dependent manner，证明 37 aa chimera 完全功能化
- **GPA1/gust44 失败原因分析**:
  - 44 aa 替换侵入 alpha4 helix 区域
  - Gustducin 序列在 alpha4-beta6 loop 处有额外 insertion（仅 G16 在人类 16 种 Galpha 中拥有此 insertion）
  - Gpa1p 的 T433 位点被替换可能导致关键构象变化
- **Western blot 确认**: 所有 chimera 均正常表达（~52 kDa），排除蛋白表达水平差异的影响

## 与项目的关系

本文对 iGEM DryLab 项目中 **chimeric Gpa1 design** 具有直接指导意义：

1. **Chimera 设计的长度选择**: 如果要在 yeast 中用 chimeric Gpa1 偶联异源 GPCR（如 Gpr2/Gpr3/GprC），应优先考虑 **C-terminal 37 aa 替换**而非 44 aa。44 aa chimera 虽在哺乳动物系统中广泛使用，但在酵母中可能因 alpha4 helix 区域的结构不兼容而失败。

2. **eCT 5 aa 是 coupling specificity 的核心**: 可作为最小替换单元进行初步筛选。如果仅替换 eCT 的 4-5 个氨基酸即可实现 receptor coupling，则可大幅降低对 Gpa1p 本身结构的扰动。

3. **Functional assay 参考**: 本文使用的 FUS1-EGFP fluorescence reporter system 是成熟的 yeast GPCR signaling readout，可直接用于验证我们的 chimeric Gpa1-nematode GPCR 偶联。

4. **Full-length 异源 Galpha 替换策略风险**: 全长替换（如直接表达 nematode Galpha）可能因与 yeast Gbeta-gamma 不兼容而失败，chimeric 策略更为稳健。

5. **结构建模辅助设计**: 文中基于 transducin (PDB: 1TND) 和 GPA1 (PDB: 1SCG) 的 3D modeling 提示，可对目标 nematode Galpha 的 C-terminal domain 进行类似建模，预测合适的替换边界。

## 关键引用

- Gladue & Konopka (2008) — Yeast GPCR assay 方法学综述 (*FEMS Yeast Res.*)
- Kostenis, Waelbroeck & Milligan (2005) — Chimeric Galpha 策略综述 (*Trends Pharmacol. Sci.*)
- Brown et al. (2000) — Yeast 中 C-terminal 5 aa 决定 heterologous GPCR coupling (*Yeast*)
- Ueda et al. (2003) — Gustducin 与 taste receptor 偶联的 C-terminal domain 研究 (*J. Neurosci.*)
- Hsu & Luo (2007) — Galpha C-terminus 与 receptor interface 的结构基础 (*Am. J. Physiol.*)
- Sakurai, Misaka et al. (2010) — G16/gust44 chimera 在哺乳动物味觉系统中的应用 (*J. Biol. Chem.*)
