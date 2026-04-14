# Ueda et al. 2003 — 文献总结

> **完整标题**: Functional Interaction between T2R Taste Receptors and G-Protein α Subunits Expressed in Taste Receptor Cells
> **期刊**: The Journal of Neuroscience, Vol.23(19), pp.7376–7380
> **DOI**: 10.1523/JNEUROSCI.23-19-07376.2003
> **作者**: Takashi Ueda, Shinya Ugawa, Hisao Yamamura, Yuji Imaizumi, Shoichi Shimada
> **机构**: Nagoya City University, Japan

## 核心发现

1. **系统性 C-terminal 长度滴定**: 构建了 5 种不同 C-terminal 替换长度的 G16/gust 嵌合体（5, 11, 23, 37, 44 aa），测试与 T2R 苦味受体的偶联。**仅 37 aa 和 44 aa 版本功能化**，5/11/23 aa 版本均失败。

2. **β6 sheet + α5 helix + extreme C-terminus 缺一不可**: 37 aa 替换恰好涵盖 β6 sheet、α5 helix 和极端 C-terminus (eCT) 三个结构域。23 aa 仅覆盖 α5 helix + eCT，不包含 β6 sheet，功能丧失——说明 β6 sheet 是必需的。

3. **跨 Gα 家族验证**: 除 gustducin 外，还测试了 Gαt2（transducin）和 Gαi2 的 44 aa 嵌合体。G16/t2 和 G16/i2 能偶联 T2R，但 G16/z 不能——证明 T2R 与 gustducin/transducin/Gαi 家族有特异性偶联。

4. **关键区分残基**: gustducin 与 Gαz 在 β6 sheet 和 α5 helix 区域有 5 个关键差异残基（V333, K346, D350, C351, F354），这些位置在 gustducin 中保守但在 Gαz 中不同，可能决定偶联差异。

## 实验方法

### 实验体系
- **细胞系**: HEK293/Gα15 cells（稳定表达 mouse Gα15 = human Gα16 同源物）
- **Gα15/16 特性**: promiscuous Gα，能将多种 GPCR 信号导入 PLC → Ca²⁺ 通路
- **信号读数**: [Ca²⁺]ᵢ 变化（Fura-2 calcium imaging）

### 嵌合体设计
| Chimera | 替换长度 | 覆盖结构域 | 结果 |
|---------|---------|----------|------|
| G16/gust5 | 5 aa | eCT only | ✗ 无响应 |
| G16/gust11 | 11 aa | eCT + α5 partial | ✗ 无响应 |
| G16/gust23 | 23 aa | eCT + α5 helix | ✗ 无响应 |
| **G16/gust37** | **37 aa** | **eCT + α5 + β6 sheet** | **✓ dose-dependent** |
| **G16/gust44** | **44 aa** | **eCT + α5 + β6 + L9 loop + α4/β5 partial** | **✓ dose-dependent** |

### 受体与配体
- **mT2R5**: mouse bitter taste receptor，配体 cycloheximide（EC₅₀ ~0.5 μM）
- **hT2R16**: human bitter taste receptor，配体 salicin（EC₅₀ ~0.2 mM）
- 两种受体对 G16/gust37 和 G16/gust44 均有 dose-dependent 响应

### 跨 Gα 验证
| Chimera | 44 aa 来源 | mT2R5 | hT2R16 |
|---------|----------|-------|--------|
| G16/gust44 | gustducin | ✓ | ✓ |
| G16/t2 (44 aa) | transducin α₂ | ✓ (specific T2R responses) | - |
| G16/i2 (44 aa) | Gαi2 | ✓ (specific T2R responses) | - |
| G16/z (44 aa) | Gαz | ✗ | ✗ |

### 检测手段
1. **Calcium imaging** — Fura-2 AM 加载 → 激动剂刺激 → 340/380 nm ratio
2. **Western blot** — anti-FLAG M2 antibody 确认所有嵌合体表达水平一致
3. **Dose-response curves** — cycloheximide / salicin 浓度梯度

## 关键数据

### 长度-功能关系
- **5 aa (eCT)**: 不足——仅有极端 C-terminus，无法提供足够的受体识别界面
- **11 aa**: 不足——覆盖 α5 helix 部分 + eCT，仍不够
- **23 aa**: 不足——覆盖完整 α5 helix + eCT，**缺少 β6 sheet**
- **37 aa**: 功能化——覆盖 β6 + α5 + eCT，EC₅₀ 和响应幅度与 44 aa 相当
- **44 aa**: 功能化——额外包含 L9 loop 和 α4/β5 部分，无显著增益

### 与 Hara2012 的对比
- Hara2012（酵母 Gpa1 系统）: 37 aa ✓, 44 aa ✗（44 aa 侵入 alpha4 导致折叠缺陷）
- Ueda2003（哺乳动物 G16 系统）: 37 aa ✓, 44 aa ✓（哺乳动物 Gα 对 44 aa 替换更耐受）
- **功能下界一致**: 两个独立系统均显示 37 aa 是最小功能替换单元

### Gustducin 特异性残基
- gustducin C-terminal 37 aa 中 5 个残基（V333, K346, D350, C351, F354）在 Gαz 中不同
- 这些残基位于 β6 sheet 和 α5 helix 界面区域
- G16/z 的失败可能归因于此

## 与项目的关系

### 对嵌合 Gpa1 C-terminal 长度选择的启示

1. **5 aa 可能不够**: 本文直接证明在 G16/gustducin 系统中 5 aa 替换完全失败。这与 Brown2000（酵母中 5 aa 对多种哺乳动物 GPCR 有效）看似矛盾——可能因为 T2R 对 Gα C-terminal 界面的依赖比传统 Class A GPCR 更广。

2. **项目 C5/C10/C15 设计的文献定位**:
   - C5 (5 aa): 在 Conklin1993（3 aa）和 Brown2000（5 aa）中有效，但在 Ueda2003 中失败
   - C10 (10 aa): 介于 Ueda 的 gust11（11 aa, 失败）和 gust5（5 aa, 失败）之间，**无直接文献先例**
   - C15 (15 aa): 介于 gust11 和 gust23 之间，同样**无直接先例**
   - **关键阈值在 23→37 aa 之间**（β6 sheet 的加入）

3. **β6 sheet 是关键**: 如果目标 GPCR（Gpr2/3/GprC）与 Gα 的偶联界面涉及 β6 sheet（如 T2R），那么项目中最长的 C15 (15 aa) 替换仍**不足以覆盖 β6 sheet**（需 ~37 aa）。这可能解释 AF3 预测中 cognate 信号未优于 cross 的原因。

4. **系统差异警告**: 本文在哺乳动物味觉系统中验证，酵母系统的最小替换长度可能不同。Brown2000 证明酵母中 5 aa 即可偶联多种哺乳动物 Class A GPCR，但真菌 GPCR（非 Class A）可能需要更长替换——这需要实验验证。

5. **唯一的系统性长度滴定**: 在所有嵌合 Gα 文献中，Ueda2003 是**唯一一篇系统测试 5 种不同长度**的论文（5/11/23/37/44 aa）。虽然系统不同（哺乳动物 vs 酵母），但其长度-功能关系对实验设计有重要参考价值。

## 关键引用

- **Gustducin 功能**: McLaughlin et al. 1992 (gustducin 发现); Wong et al. 1996 (gustducin KO 小鼠)
- **T2R 受体**: Adler et al. 2000; Matsunami et al. 2000 (T2R 家族鉴定)
- **Chimeric Gα 策略**: Conklin et al. 1993 (3 aa 替换); Kostenis et al. 2001 (Gα16 作为通用适配器)
- **hT2R16 salicin**: Bufe et al. 2002 (hT2R16 配体鉴定)
- **Gα-受体界面结构**: Noel et al. 1993 (transducin 结构); Lichtarge et al. 1996 (evolutionary trace)
