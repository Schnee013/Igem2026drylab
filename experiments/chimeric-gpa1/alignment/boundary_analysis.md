# C 端结构域边界分析

> 基于 MUSCLE 5.3 + ClustalΩ 1.2.4 交叉验证的多序列比对结果

## 比对一致性

MUSCLE 和 ClustalΩ 在 C 端最后 28 列**完全一致**，差异仅出现在 -40 位（gap placement），与切割位点无关。

## C 端保守性图谱

基于 5 条 Gα 序列（Sc Gpa1, Ao Gpa2, Af GasA, Rn GNAT3, Rn Gsα）的比对：

```
位置(从C端):  -30        -20        -10        -1
              |          |          |          |
Sc_Gpa1:  ...CATDTQTMKFVLSAVTDLIIQQNLKKIGII
Ao_Gpa2:  ...QATDTSNIRLVFAAVKETILQNALKDSGIL
Af_GasA:  ...CATDTTQIKFVMAAVNDIIIQENLRNCGLI
Rn_GNAT3: ...CATDTQNVKFVFDAVTDIIIKENLKDCGLF
Rn_Gsα:   ...CAVDTENIRRVFNDCRDIIQRMHLRQYELL
保守性:       :*****..:.**..:::.:*..:**...:::.
              ←── α5 helix 核心 ──→←─ eCT ─→
```

- `***` = 全保守 (5/5 identical)
- `::` = 保守替换 (≤2 unique residues)
- `..` = 可变

### 关键保守位点

| 位置 | 残基 (5 seq) | 保守性 | 结构意义 |
|------|-------------|--------|---------|
| -27 | D,D,D,D,D | **5/5** | α5 helix 起始标志 |
| -26 | T,T,T,T,T | **5/5** | α5 helix |
| -20 | V,V,V,V,V | **5/5** | α5 helix 核心 |
| -12 | I,I,I,I,I | **5/5** | α5 helix 中段 |
| -7  | L,L,L,L,L | **5/5** | α5 helix C 端终止 |

## 切割位点设计理由

### Chimera-5（替换 eCT）

```
切割点: Gpa1 残基 468 后
        ...QQNLK | graft(5 aa)
```

- 仅替换 eCT（受体偶联特异性决定区）
- 保留 α5 helix 完整（包括 conserved L at -7）
- **最保守方案**，类比 Hara 2012 的 gust4（last 4 aa），已实验验证功能正常
- 风险最低，但偶联效率可能不足

### Chimera-10（延伸至 α5 tail）

```
切割点: Gpa1 残基 463 后
        ...TDLII | graft(10 aa)
```

- 包含 eCT + α5 helix 末端 5 残基
- 切在 conserved I (-12) 之后，位点本身 (-10 Q/R/Q/Q/K) 可变
- 增加了受体识别表面，可能提升偶联效率
- 风险适中

### Chimera-15（深入 α5 helix）

```
切割点: Gpa1 残基 458 后
        ...VLSAV | graft(15 aa)
```

- 替换 α5 helix 的后半段
- 切在 -15 位 (T/R/K/N/T) —— **非保守位点**，结构扰动最小化
- 提供最大的受体识别表面
- Hara 2012 的 gust37 (last 37 aa) 功能正常 → 15 aa 替换远在安全范围内
- 风险仍可控

### Chimera-25（覆盖完整 α5 helix + eCT）— v2 新增

```
切割点: Gpa1 残基 447 后
        ...TDT | graft(25 aa)
```

- 切在 -26 (T, conserved) 之后，-25 开始替换
- 覆盖完整 α5 helix body + eCT
- 保留 α5 起始锚点 DT (-27/-26)
- Ueda2003 中 gust23 (23 aa) 失败（仅 α5 + eCT，缺 β6），C25 略长但同一区间
- **测试假说**: α5 helix 完整替换是否足以偶联真菌 GPCR

### Chimera-37（覆盖 β6 + α5 + eCT）— v2 新增

```
切割点: Gpa1 残基 435 后
        ...TNK | graft(37 aa)
```

- 位于 β6 sheet 上游，Gpa1 关键残基 T433 保留在骨架中
- 覆盖 β6 sheet + α5 helix + eCT
- 匹配 Ueda2003 (G16/gust37) 和 Hara2012 (GPA1/gust37) 双重验证的功能阈值
- **测试假说**: β6 sheet 是真菌 GPCR 偶联的必需界面

## 文献边界参考

| 文献 | 嵌合体 | 替换残基数 | 系统 | 功能 | 对我们的意义 |
|------|--------|-----------|------|------|------------|
| Conklin1993 | qi3 | 3 (eCT) | 哺乳动物 HEK-293 | ✓ | 最小替换单元 |
| Hara2012 | gust4 | 4 (eCT) | 酵母 Ste2 | ✓ | → C5 安全 |
| Brown2000 | 多种 | 5 (eCT) | 酵母 + 哺乳动物 GPCR | ✓ | → C5 安全 |
| Ueda2003 | G16/gust5 | 5 | 哺乳动物 T2R | ✗ | C5 可能不足 |
| Ueda2003 | G16/gust11 | 11 | 哺乳动物 T2R | ✗ | C10 可能不足 |
| Ueda2003 | G16/gust23 | 23 | 哺乳动物 T2R | ✗ | C25 可能不足 |
| Hara2012 | gust31-37 | 31-37 | 酵母 Ste2 | ✓ | → C37 功能阈值 |
| Ueda2003 | G16/gust37 | 37 | 哺乳动物 T2R | ✓ | → C37 功能阈值 |
| Ueda2003 | G16/gust44 | 44 | 哺乳动物 T2R | ✓ | — |
| Hara2012 | gust44 | 44 (侵入 α4) | 酵母 Ste2 | ✗ | → 上限约束，不追加 C44 |
