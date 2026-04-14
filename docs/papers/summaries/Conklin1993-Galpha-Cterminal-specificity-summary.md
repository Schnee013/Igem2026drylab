# Conklin et al. 1993 — 文献总结

> **完整标题**: Substitution of three amino acids switches receptor specificity of Gqα to that of Giα
> **期刊**: Nature, Vol.363, pp.274–276
> **DOI**: 10.1038/363274a0
> **作者**: Bruce R. Conklin, Zvi Farfel, Kevin D. Lustig, David Julius, Henry R. Bourne
> **机构**: University of California, San Francisco; Chaim Sheba Medical Center, Tel Aviv University

## 核心发现

1. **3 个 C-terminal 氨基酸足以切换 Gα 受体特异性**: 将 Gαq 的 C-terminal 最后 3 个氨基酸替换为 Gαi2 对应残基（qi3 chimera），即可将 Gαq 的受体偶联特异性从 Gq-coupled 受体切换到 Gi-coupled 受体（α2-AR, A1R, D2R）。

2. **最小替换单元为 3 aa**: qi3（3 aa）和 qi5（5 aa）效果相当，说明最后 3 个氨基酸是特异性决定的核心。这是当时报道的最小有效替换。

3. **-3 位 glycine 是关键**: 所有 αi 家族成员的 -3 位均为 glycine（PTX 靶位），替换后使嵌合体获得 PTX 敏感性。NMR 显示 C-terminus 在此 glycine 处形成 β-turn，此三维构象对受体识别至关重要。

4. **αs C-terminal 替换无效**: 将 Gαq 末端替换为 Gαs 对应残基的嵌合体无法偶联 Gs-coupled 受体——因为 Gαs 和 Gα13 的 C-terminus 不属于 αi 家族，缺乏保守 glycine。

## 实验方法

### 实验体系
- **细胞系**: HEK-293 (human embryonic kidney)
- **信号读数**: PLC (phospholipase C) 活性 → InsP (inositol phosphates) 积累
  - Gαq 天然激活 PLC → 测量 InsP 产生即可读取偶联
- **受体**: α2-AR（Gi-coupled）, A1R adenosine receptor（Gi-coupled）, D2R dopamine receptor（Gi-coupled）

### 嵌合体设计
| Chimera | C-terminal 序列 (-5 到 -1) | 来源 |
|---------|--------------------------|------|
| qWT | E Y N L V | Gαq wild-type |
| qi3 | E Y **G L F** | 最后 3 aa 来自 Gαi2 |
| qi5 | **D C G L F** | 最后 5 aa 来自 Gαi2 |
| qo5 | **G C G L Y** | 最后 5 aa 来自 Gαo |
| qz5 | **Y I G L C** | 最后 5 aa 来自 Gαz |
| qs5 | **Q Y E L L** | 最后 5 aa 来自 Gαs |

### 检测手段
1. **InsP accumulation assay** — 转染受体 + 嵌合 Gα → 加激动剂 → 测 [³H]InsP
2. **PTX 处理** — 百日咳毒素 ADP-ribosylation，检测 -4 位 cysteine 是否存在（Gi 家族标志）
3. **NMR** — C-terminal 肽段结构分析（companion paper 中描述）

## 关键数据

### 受体偶联结果
| Chimera | α2-AR | A1R | D2R | 解读 |
|---------|-------|-----|-----|------|
| qWT | + | - | - | 仅偶联 α2-AR（Gq-coupled） |
| qi3 | + | + | + | 偶联全部三个 Gi-coupled 受体 |
| qi5 | + | + | + | 与 qi3 相当 |
| qo5 | + | 弱 | - | 部分偶联 |
| qz5 | + | - | - | 未获得新偶联 |
| qs5 | - | - | - | 未显示（无法偶联 Gi 受体） |

### 关键观察
- **qi3 vs qi5**: 效果无显著差异，表明位置 -1, -2, -3 是核心
- **PTX 敏感性**: qi3/qi5 中 α2-AR 和 D2R 的 PLC 刺激被 PTX 抑制（-4 位 cysteine 来自 Gαi2），但 qz5 不被抑制（Gαz -4 位为 isoleucine，非 PTX 靶标）
- **αi 家族特异**: qo5 实现部分偶联（Go 与 Gi 同属 Gi/o 家族），但 qs5/qz5 无效
- **浓度-响应曲线**: qi3 对三种 Gi-coupled 受体的 dose-response 与 wild-type Gαi 类似（Fig. 2）

### NMR 结构洞见
- C-terminal 肽段的 αi 序列在溶液中形成 **β-turn**，转折点在 -3 位 glycine
- 此 β-turn 结构在所有 αi 家族成员中保守
- 作者提出 C-terminal 的三维构象（β-turn）而非仅线性序列决定受体识别

## 与项目的关系

### 对嵌合 Gpa1 设计的启示

1. **最小替换基准**: 本文证明 3 个 C-terminal 氨基酸即可切换受体特异性（哺乳动物系统）。项目中使用的 5 aa（C5）替换已覆盖此最小单元，理论上应足以转移偶联特异性。

2. **C5 vs C10 vs C15 的文献定位**: 本文仅测试了 3 aa 和 5 aa（在 Gαq→Gαi 系统中），未测试更长替换。项目中的 C10/C15 设计超出了本文验证范围，但本文确立了 **C-terminus 是特异性决定区**的原理基础。

3. **β-turn 结构的重要性**: C-terminus 的三维构象（而非仅序列）影响受体识别。AF3 预测嵌合 Gpa1 时，C-terminal 区域的折叠质量（pLDDT）直接关系到偶联预测的可靠性。

4. **跨系统适用性**: 本文在哺乳动物 HEK-293 中验证，Hara2012 和 Brown2000 在酵母中验证了类似原理。但酵母 Gpa1 的 C-terminal boundary 可能不同——Hara2012 证明酵母中 37 aa 可用但 44 aa 失败。

5. **奠基性引用**: 几乎所有后续嵌合 Gα 文献（Brown2000, Hara2012, Ueda2003, Ladds2005）均引用本文。项目 wiki 中讨论嵌合策略时**必须引用**此文。

## 关键引用

- **先前 chimeric Gα 工作**: Sullivan et al. 1987; Masters et al. 1988; Conklin et al. 1992 (qi21 chimera)
- **受体-Gα 界面**: Hamm et al. 1988 (rhodopsin-transducin); Garcia et al. 1995
- **NMR C-terminal 结构**: Dratz et al. (companion paper, same issue)
- **PTX 机制**: Burns & Bhargava 1986 (ADP-ribosylation at -4 cysteine)
