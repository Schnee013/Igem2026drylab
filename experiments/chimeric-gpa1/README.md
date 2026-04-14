# 嵌合 Gpa1 设计实验

> 方向文档: [docs/modeling/P3-chimeric-gprotein.md](../../docs/modeling/P3-chimeric-gprotein.md)

## Gα 偶联关系（文献验证）

| 受体 | 来源物种 | 偶联 Gα | Gα 分类 | 下游通路 | 文献依据 |
|------|---------|---------|---------|---------|---------|
| **Gpr2** | *A. oligospora* | **Gpa2** (TGJ64397.1) | Class III | cAMP-PKA | Kuo 2024 + Chen 2022 |
| **Gpr3** | *A. oligospora* | **Gpa2** (TGJ64397.1) | Class III | cAMP-PKA | Kuo 2024 |
| **GprC** | *A. flagrans* | **GasA** (A0A436ZRX2) | Group I (Gαi-like) | MAPK | Hu 2024 |

### 偶联证据链

**Gpr2/Gpr3 → Gpa2**:
- Kuo 2024: Gpr2/Gpr3 属 carbon receptor family, 敲除后对 ascr#3/ascr#7 响应显著降低
- Chen 2022: Δgpa2 trap 严重受损; 外源 cAMP 可 rescue → Gpa2 通过 cAMP-PKA 通路
- Chen 2022 明确指出: "Kuo 2024 确定了 Gpr2 是感知 nematode ascaroside 信号的 GPCR, 并通过遗传学证据提出 Gpr2 与 Gpa2 偶联"

**GprC → GasA**:
- Hu 2024: ΔgprC 和 ΔgasA 均完全丧失 trap 形成; Split-GFP 实验证实 GprC 与 GasA 物理互作
- Hu 2024: 8'-Br-cAMP 不能 rescue ΔgprC → GprC-GasA 通过 **MAPK 通路**而非 cAMP

### 对嵌合设计的意义

在酵母 STE2 通路中, 信号通过 **Gβγ 释放**传导 (Gpa1 释放 Ste4/Ste18 → MAPK 级联)。
嵌合 Gpa1 的 C 端需要被异源 GPCR 识别, 催化 GTP 交换, 从而释放酵母 Gβγ。

因此 C 端供体序列:
- **Gpr2/Gpr3 的嵌合体**: 使用 A. oligospora **Gpa2** C 端
- **GprC 的嵌合体**: 使用 A. flagrans **GasA** C 端

## 序列清单

| 文件 | 蛋白 | 来源 | 长度 | 用途 |
|------|------|------|------|------|
| `yeast_Gpa1_P08539.fasta` | 酵母 Gpa1 | UniProt P08539 | 472 aa | 嵌合骨架 |
| `Ao_Gpa2_TGJ64397.fasta` | A. oligospora Gpa2 | NCBI TGJ64397.1 | 346 aa | C 端供体 (Gpr2/Gpr3) |
| `Af_GasA_A0A436ZRX2.fasta` | A. flagrans GasA | UniProt A0A436ZRX2 | 353 aa | C 端供体 (GprC) |
| `rat_GNAT3_P29348.fasta` | 大鼠 gustducin | UniProt P29348 | 354 aa | 对照模板 (Hara 2012) |
| `rat_Gsa_P63095.fasta` | 大鼠 Gsα | UniProt P63095 | 394 aa | 对照模板 (Medici 1997) |
| `all_Galpha_for_alignment.fasta` | 以上 5 条合并 | — | — | MUSCLE 比对输入 |

## C 端序列速览

| 蛋白 | Last 5 | Last 10 | Last 15 |
|------|--------|---------|---------|
| Sc Gpa1 | KIGII | QQNLKKIGII | TDLIIQQNLKKIGII |
| Ao Gpa2 | DSGIL | QNALKDSGIL | KETILQNALKDSGIL |
| Af GasA | NCGLI | QENLRNCGLI | NDIIIQENLRNCGLI |
| Rn GNAT3 | DCGLF | KENLKDCGLF | TDIIIKENLKDCGLF |
| Rn Gsα | QYELL | RMHLRQYELL | RDIIQRMHLRQYELL |

## 目录结构

```
experiments/chimeric-gpa1/
├── README.md                 ← 本文件
├── sequences/                ← 源序列 + 比对输入
│   ├── all_Galpha_for_alignment.fasta
│   ├── yeast_Gpa1_P08539.fasta
│   ├── Ao_Gpa2_TGJ64397.fasta
│   ├── Af_GasA_A0A436ZRX2.fasta
│   ├── rat_GNAT3_P29348.fasta
│   └── rat_Gsa_P63095.fasta
├── alignment/                ← (Phase 1) MUSCLE + ClustalΩ 比对结果
├── chimeras/                 ← (Phase 2) 6 个嵌合候选 FASTA
├── af3_predictions/          ← (Phase 3) AF3 Server 结果
└── scoring/                  ← (Phase 4) iPAE/pLDDT 评分矩阵
```
