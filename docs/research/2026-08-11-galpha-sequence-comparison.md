# ScGpa1、ScGpa2、AoGpa2 与 AfGasA 的实序列定量比较

## Findings

### 结论先行

四条实际下载的蛋白序列显示：**AoGpa2 在全长、Gα 核心和 GPCR-contacting C-terminal α5 region 三个口径下都更接近 ScGpa2，而不是 ScGpa1。**差异在 α5/C 端最明显：AoGpa2–ScGpa2 为 23/28（82.143%）identity，AoGpa2–ScGpa1 为 11/27（40.741%）。

新增的 AfGasA（`DFL_009501`）呈现不同模式：相对两条酵母 Gα，它在全长、Gα 核心和 α5/C 端都更接近 ScGpa1；但四条序列中，AfGasA 的最高全长 identity 实际是对 AoGpa2（168/359，46.797%）。这说明“全长最接近谁”与“受体接触 C 端最接近谁”必须分别计算，不能由蛋白名或系统发育关系代替。

AoGpa2–ScGpa2 的结果足以把 “AoGpa2 或 AoGpr2/AoGpr3 与酵母内源 G-protein machinery 存在 sequence compatibility” 当作需要实验排除的假说；AfGasA 来自 Hu et al. 2024 的另一物种系统，不属于 Kuo Fig. 4a 的构建。

### Summary table

| Protein | Species | Accession | Length | Source database |
|---|---|---|---:|---|
| ScGpa1 | *Saccharomyces cerevisiae* S288c | P08539 | 472 aa | UniProtKB/Swiss-Prot, reviewed |
| ScGpa2 | *Saccharomyces cerevisiae* S288c | P10823 | 449 aa | UniProtKB/Swiss-Prot, reviewed |
| AoGpa2 | *Arthrobotrys oligospora* TWF154；NCBI record 写作 *Orbilia oligospora* | TGJ64397.1；locus tag EYR41_010456 | 356 aa | NCBI Protein/GenBank |
| AfGasA | *Arthrobotrys flagrans*；sequence record 标为 CBS H-5679，Hu2024 实验株标为 CBS 349.94（两编号等同性未确认） | A0A436ZRX2；locus tag DFL_009501；NCBI RVD81648.1 | 353 aa | UniProtKB/Swiss-Prot, reviewed；NCBI 交叉核验 |

数据库入口：[ScGpa1 P08539](https://www.uniprot.org/uniprotkb/P08539/entry)、[ScGpa2 P10823](https://www.uniprot.org/uniprotkb/P10823/entry)、[AoGpa2 TGJ64397.1](https://www.ncbi.nlm.nih.gov/protein/TGJ64397.1)、[AfGasA A0A436ZRX2](https://www.uniprot.org/uniprotkb/A0A436ZRX2/entry)、[AfGasA NCBI RVD81648.1](https://www.ncbi.nlm.nih.gov/protein/RVD81648.1)。

### Pairwise table

全长分母包含所有 global-alignment columns，包括 gap columns。Similarity 定义为 BLOSUM62 score > 0 的 residue pair，并包含 exact matches。

| Pair | Global identity | Similarity | Gaps | C-terminal identity | Aligned length / score |
|---|---:|---:|---:|---:|---:|
| ScGpa1 vs ScGpa2 | 160/565 = **28.319%** | 229/565 = 40.531% | 209/565 = 36.991% | 8/28 = **28.571%** | 565 / 610.5 |
| ScGpa1 vs AoGpa2 | 145/472 = **30.720%** | 224/472 = 47.458% | 116/472 = 24.576% | 11/27 = **40.741%** | 472 / 640.5 |
| ScGpa2 vs AoGpa2 | 194/457 = **42.451%** | 275/457 = 60.175% | 109/457 = 23.851% | 23/28 = **82.143%** | 457 / 956.0 |
| ScGpa1 vs AfGasA | 178/473 = **37.632%** | 257/473 = 54.334% | 121/473 = 25.581% | 15/27 = **55.556%** | 473 / 865.5 |
| ScGpa2 vs AfGasA | 158/452 = **34.956%** | 229/452 = 50.664% | 102/452 = 22.566% | 9/28 = **32.143%** | 452 / 707.0 |
| AoGpa2 vs AfGasA | 168/359 = **46.797%** | 241/359 = 67.131% | 9/359 = 2.507% | 11/27 = **40.741%** | 359 / 877.5 |

软件与参数：Biopython 1.87 `PairwiseAligner`，`mode=global`，BLOSUM62，gap open −10.0，gap extension −0.5，左右端 gap 同样罚分。这是 Needleman–Wunsch affine-gap global alignment 的等价实现；未使用 BLAST local identity。每个输出 score 又从最终 gapped rows 独立重算，均与 aligner score 完全一致。四序列 MSA 使用 Clustal Omega 1.2.4，protein mode，1 thread，input order。

全长存在 score-tied optimal paths。表中固定报告 Biopython 返回的第一条最优路径；全部最优路径均已枚举：

- ScGpa1–ScGpa2 有 24 条同分路径；identity 范围为 160/565（28.319%）至 164/566（28.975%）。
- ScGpa2–AoGpa2 有 4 条同分路径，identity 都是 194/457（42.451%），仅 similarity 为 275 或 276。
- 另外四组分别有 4、4、12、4 条同分路径；每组内部的 aligned length、identity、similarity 和 gaps 均不变。

因此 AoGpa2 更接近 ScGpa2、AfGasA 更接近 ScGpa1 的相对结论都不依赖 tie-breaking。逐路径审计见 [`global_optimal_path_tie_audit.tsv`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/results/global_optimal_path_tie_audit.tsv)。

### A. 实际 FASTA、header 与 checksum

四个下载文件均保留数据库原始 header：

```text
>sp|P08539|GPA1_YEAST Guanine nucleotide-binding protein alpha-1 subunit OS=Saccharomyces cerevisiae (strain ATCC 204508 / S288c) OX=559292 GN=GPA1 PE=1 SV=3
>sp|P10823|GPA2_YEAST Guanine nucleotide-binding protein alpha-2 subunit OS=Saccharomyces cerevisiae (strain ATCC 204508 / S288c) OX=559292 GN=GPA2 PE=1 SV=2
>TGJ64397.1 Guanine nucleotide-binding protein alpha-2 subunit [Orbilia oligospora]
>sp|A0A436ZRX2|GASA_ARTFL Guanine nucleotide binding protein alpha subunit A OS=Arthrobotrys flagrans OX=97331 GN=gasA PE=1 SV=1
```

| Protein | FASTA | SHA256 |
|---|---|---|
| ScGpa1 | [`ScGpa1_P08539.fasta`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/ScGpa1_P08539.fasta) | `1737d0116e06108c4613f504e92ed747bf46dcbc86b62d362fda9668458387bb` |
| ScGpa2 | [`ScGpa2_P10823.fasta`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/ScGpa2_P10823.fasta) | `f6b1b72091c6dd0cb93109714556908a8e4d469f0c1f981c1a4ff2b93b7f47a0` |
| AoGpa2 | [`AoGpa2_TGJ64397.1.fasta`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/AoGpa2_TGJ64397.1.fasta) | `da014c9cde006fedac16398ec2cd149a9a3029a53c666b2a883e3fcf3dce2fc3` |
| AfGasA | [`AfGasA_A0A436ZRX2.fasta`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/AfGasA_A0A436ZRX2.fasta) | `872b7ea0fce717601ad315513b9b8b927704dae839631ca720527c6b7a252796` |

机器可核验清单：[`checksums.sha256`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/checksums.sha256)。现有旧路径 `experiments/chimeric-gpa1/sequences/Af_GasA_A0A436ZRX2.fasta` 的 residue sequence 与新下载 FASTA 相同，但旧 header 带人工功能描述，因此本分析只把新下载文件作为输入和 checksum 对象。

#### AoGpa2 accession identity 的追踪

这里没有按 “Gpa2” 名称选最像的序列。NCBI GenBank record `TGJ64397.1` 同时记录 product、gene `GPA2`、locus tag `EYR41_010456`、strain `TWF154`、356-aa protein、genomic CDS 和 G-alpha CDD domain。下载的 1,071-nt CDS 翻译为 356 aa 加 terminal stop；去掉 stop 后与 `TGJ64397.1` 逐残基一致。Kuo2024 Supplementary Table 3 的 GPA2–Myc primers 也精确匹配这条 CDS 两端。因此 `EYR41_010456 → TGJ64397.1` 由 locus tag、strain、CDS translation 和论文引物共同闭合。论文名 *Arthrobotrys oligospora* 与 NCBI record 名 *Orbilia oligospora* 的差异被保留。

#### AfGasA accession identity 的追踪

`DFL_009501 → AfGasA` 的闭环由三层独立记录组成：

1. Hu et al. 2024 正文 Results 的 `Par7` 段落（开头为 “Typically, GPCR-dependent signalling cascades...”）直接写 `gasA (dfl_009501)`，并在摘要中称其为 GasA G-protein alpha subunit。
2. UniProtKB reviewed entry `A0A436ZRX2 / GASA_ARTFL` 同时记录 gene `gasA`、ORF `DFL_009501`、353 aa，并交叉引用 EMBL scaffold `SAEB01000012`、NCBI protein `RVD81648.1` 和 `FungiDB:DFL_009501`。
3. NCBI `RVD81648.1` 的 definition、CDS feature 和 locus tag 都含 `DFL_009501`；其 1,062-nt genomic CDS 含一个 terminal stop，翻译后与 `RVD81648.1` 和 UniProt `A0A436ZRX2` 都逐残基一致。

NCBI 的旧 protein product 仍写 `hypothetical protein DFL_009501`，而 2026-08-12 访问的 UniProt record 已按 Hu2024 文献整理为 GasA；两条记录由相同 locus tag、scaffold、protein cross-reference 和相同翻译序列连接，不是按相似性挑选。

这里需要把 **protein accession identity** 与 **strain label identity** 分开。Hu2024 Methods 将实验用 *A. flagrans* 写为 `CBS 349.94`，Data Availability 又明确指定其使用的 genome database 为 `PRJNA494930`；`RVD81648.1/DFL_009501` 正属于该 BioProject。产生 `SAEB01000000` genome 的 Youssar et al. 2019 同样把实验株写为 `CBS 349.94`。但 NCBI Protein/BioSample `SAMN10185917` 把该 assembly 的 strain/culture collection 标为 `CBS H-5679`（BioSample note 另写 `A. Rubner, A.R. 9125`）。在已核查的论文、UniProt、NCBI record 和 BioSample 中，没有找到把 `CBS 349.94` 与 `CBS H-5679` 明确列为同一 isolate/同物异名的权威交叉记录。因此本报告不合并两个编号：前者保留为 Hu2024 experimental-strain label，后者保留为 sequence-database label。这个未决元数据冲突不切断 `gasA/DFL_009501 → A0A436ZRX2/RVD81648.1 → SAEB01000012 CDS` 的直接序列链，也不改变 alignment 数值。

### B. 序列身份与异常检查

四个 FASTA 都只含 20 种 canonical amino acids，长度与数据库 record 一致，无 `X`、无 stop、无手工补全。数据库 domain annotation 与序列 motif 检查共同支持它们是 heterotrimeric G-protein alpha subunits；AoGpa2 和 AfGasA 的 genomic CDS 还提供了 terminal stop 与逐残基翻译一致性。检查未见明显 sequence-level truncation 或异常 annotation；这不是对转录本或蛋白表达的实验验证。

| Feature | ScGpa1 P08539 | ScGpa2 P10823 | AoGpa2 TGJ64397.1 | AfGasA A0A436ZRX2 / RVD81648.1 |
|---|---|---|---|---|
| Gα domain | 40–472, UniProt | 122–448, UniProt | 37–350, NCBI CDD | 32–353, UniProt；34–347, NCBI CDD |
| G1 / P-loop | 43–56 `KLLLLGAGESGKST` | 125–138 `KVLLLGAGESGKST` | 43–50 `GSGESGKS`; aligned signature continues `T` at 51 | 40–47 `GAGESGKS`; continues `T` at 48 |
| Switch I / G2 | 292–300 `DILKGRIKT` | 268–276 `DILRSRQMT` | 180–188 `RARTKTTGI` | 176–184 `RSRVKTLGI` |
| G3 | 315–324 `FKVLDAGGQR` | 292–301 `MHIYDVGGQR` | 204–207 `DVGG` | 200–203 `DVGG` |
| Switch II | 320–336, MSA-mapped | 297–313, MSA-mapped | 205–221, NCBI CDD | 201–217, NCBI CDD |
| G4 | 384–391 `ILFLNKID` | 361–368 `VLFLNKID` | 273–276 `NKVD` | 269–272 `NKID` |
| G5 | 442–447 `TCATDT` | 418–423 `TQATDT` | 327–329 `QAT` | 324–326 `CAT` |

#### ScGpa1 的 109-aa insertion

UniProt 将 ScGpa1 residues 127–235 标为 “Insert; not present in other G proteins”，共 109 aa，其中 162–199 被预测为 disordered。它在四序列 MSA 中形成一整段仅 ScGpa1 有残基的区域，增加 global-alignment denominator 和 gap fraction。

为分开 whole-protein global identity 与 core 相似性，做了两个诊断；它们不能冒充新的全长 identity：

| Pair | Whole-protein global | 仅删 ScGpa1 127–235 后再 global | Gα-core estimate |
|---|---:|---:|---:|
| ScGpa1 vs ScGpa2 | 160/565 = 28.319% | 155/467 = 33.191% | 139/346 = 40.173% |
| ScGpa1 vs AoGpa2 | 145/472 = 30.720% | 140/382 = 36.649% | 133/343 = 38.776% |
| ScGpa1 vs AfGasA | 178/473 = 37.632% | 171/368 = 46.467% | 160/329 = 48.632% |

Gα-core estimate 从各数据库标注的 Gα-domain start（ScGpa1 40、ScGpa2 122、AoGpa2 37、AfGasA 32）取到 native C terminus，并删掉 ScGpa1 127–235。三组都显示 insertion 会使全长百分比低估 core similarity；ScGpa2 自己的 1–91 N-terminal disordered extension 也会压低涉及 ScGpa2 的 whole-protein global identity。

### C–D. 四序列 MSA 与功能区

完整输出：[`four_Galpha_clustalo.fasta`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/four_Galpha_clustalo.fasta)、[`four_Galpha_clustalo.clustal`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/four_Galpha_clustalo.clustal)、[`four_Galpha_key_regions.txt`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/four_Galpha_key_regions.txt)。以下坐标均为各自原始蛋白坐标，不是 MSA column number。

#### G1 / P-loop

```text
ScGpa1   39-60  KNEIKLLLLGAGESGKSTVLKQ
ScGpa2 121-142  DKELKVLLLGAGESGKSTVLQQ
AoGpa2   34-55  RRECKILLLGSGESGKSTIVKQ
AfGasA   31-52  RNEIKMLLLGAGESGKSTILKQ
```

#### Switch I / G2

```text
ScGpa1 288-307  CTDEDILKGRIKTTGITETE
ScGpa2 264-283  PTQQDILRSRQMTSGIFDTV
AoGpa2 173-192  PSEADVLRARTKTTGIYETR
AfGasA 169-188  PSDQDVLRSRVKTLGITETT
```

#### G3 与 Switch II

AoGpa2 Switch II 205–221 和 AfGasA Switch II 201–217 是 NCBI CDD direct features；两个 Sc 范围通过四序列 MSA 映射，不冒充数据库直接 annotation。

```text
G3
ScGpa1 312-328  S-SKFKVLDAGGQRSERK
ScGpa2 288-305  SDIKMHIYDVGGQRSERK
AoGpa2 197-213  Q-LNIHMFDVGGQRSERK
AfGasA 193-209  D-LTYRMFDVGGQRSERK

Switch II
ScGpa1 317-339  VLDAGGQRSERKKWIHCFEGITA
ScGpa2 294-316  IYDVGGQRSERKKWIHCFDNVTL
AoGpa2 202-224  MFDVGGQRSERKKWIHCFESVTS
AfGasA 198-220  MFDVGGQRSERKKWIHCFENVTT
```

#### G4 与 G5 / α5 transition

```text
G4
ScGpa1 380-395  DTPFILFLNKIDLFEE
ScGpa2 357-372  RTSVVLFLNKIDLFAE
AoGpa2 265-280  RTSIILFLNKVDLFRQ
AfGasA 261-276  KTSIILFLNKIDRFRE

G5 / alpha5 transition
ScGpa1 438-451  YVKRTCATDTQTMK
ScGpa2 414-427  YPHVTQATDTSNIR
AoGpa2 322-335  YPHLTQATDTSNIR
AfGasA 319-332  YTHFTCATDTTQIK
```

AoGpa2 的 NCBI CDD `putative receptor binding site` 是 319–330、332–335；AfGasA 对应 feature 是 316–327、329–332。定量 α5 region 采用同一个可对齐的结构操作边界：**三残基 G5 core（ScGpa1/AfGasA `CAT`；ScGpa2/AoGpa2 `QAT`）之后的 conserved Asp 起，到 native C terminus**。得到 ScGpa1 446–472（27 aa）、ScGpa2 422–449（28 aa）、AoGpa2 330–356（27 aa）、AfGasA 327–353（27 aa）。该边界把 G5 loop 与 α5 body 分开，同时保留 receptor-facing C-terminal tail；它不是机械截最后 20 aa。

#### C-terminal α5 region 的四序列 MSA

```text
ScGpa1  446-472  DTQTMKFVLSAVTDLIIQQNLKKIGII-
ScGpa2  422-449  DTSNIRLVFAAIKETILENTLKDSGVLQ
AoGpa2  330-356  DTSNIRLVFAAVKETILQNALKDSGIL-
AfGasA  327-353  DTTQIKFVMAAVNDIIIQENLRNCGLI-
```

#### C-terminal α5 region 的逐位点 pairwise alignment

`|` = identical；`:` = conservative/positive（BLOSUM62 > 0）；`.` = non-conservative；空格 = gap。

```text
ScGpa1   DTQTMKFVLSAVTDLIIQQNLKKIGII-
         ||..::.|.:|:.:.|::..||..|:: 
ScGpa2   DTSNIRLVFAAIKETILENTLKDSGVLQ
identity 8/28 = 28.571%; positive similarity 17/28 = 60.714%

ScGpa1   DTQTMKFVLSAVTDLIIQQNLKKIGII
         ||..::.|.:||.:.|:|..||..||:
AoGpa2   DTSNIRLVFAAVKETILQNALKDSGIL
identity 11/27 = 40.741%; positive similarity 17/27 = 62.963%

ScGpa2   DTSNIRLVFAAIKETILENTLKDSGVLQ
         |||||||||||:|||||:|.|||||:| 
AoGpa2   DTSNIRLVFAAVKETILQNALKDSGIL-
identity 23/28 = 82.143%; positive similarity 26/28 = 92.857%

ScGpa1   DTQTMKFVLSAVTDLIIQQNLKKIGII
         ||..:|||::||.|:|||:||:..|:|
AfGasA   DTTQIKFVMAAVNDIIIQENLRNCGLI
identity 15/27 = 55.556%; positive similarity 22/27 = 81.481%

ScGpa2   DTSNIRLVFAAIKETILENTLKDSGVLQ
         ||:.|:.|.||:.:.|::..|::.|:: 
AfGasA   DTTQIKFVMAAVNDIIIQENLRNCGLI-
identity 9/28 = 32.143%; positive similarity 19/28 = 67.857%

AoGpa2   DTSNIRLVFAAVKETILQNALKDSGIL
         ||:.|:.|.|||.:.|:|..|::.|::
AfGasA   DTTQIKFVMAAVNDIIIQENLRNCGLI
identity 11/27 = 40.741%; positive similarity 19/27 = 70.370%
```

完整区域输出：[`alpha5_C_terminal_alignment.txt`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/alpha5_C_terminal_alignment.txt)。

### E. 生物学问题的分层回答

1. **全长上 AoGpa2 更接近 ScGpa2。** Identity 为 42.451% 对 30.720%，positive similarity 为 60.175% 对 47.458%。Gα-core estimate 仍为 53.869% 对 38.776%，方向不变。

2. **GPCR-contacting α5/C 端上 AoGpa2 明显更接近 ScGpa2。** Identity 为 82.143% 对 40.741%；positive similarity 为 92.857% 对 62.963%。这来自四条实际 FASTA 的 region-global alignment，不是由同名 “Gpa2” 推出。

3. **ScGpa1 insertion 会使全长 identity 低估 conserved Gα core similarity。** 仅删除 127–235，ScGpa1–ScGpa2 从 28.319% 升至 33.191%，ScGpa1–AoGpa2 从 30.720% 升至 36.649%，ScGpa1–AfGasA 从 37.632% 升至 46.467%。进一步从 Gα-domain start 比较时分别为 40.173%、38.776% 和 48.632%。这些 core/删除诊断不能改写成 whole-protein identity。

4. **是否应认真考虑酵母宿主中的 cross-interaction？是，作为 sequence compatibility hypothesis 和实验混杂因素；不是作为 experimentally demonstrated coupling。**

   - AoGpa2 与 ScGpa2 的 core conservation 和 82.143% α5 identity，使 “AoGpa2 可被部分 yeast G-protein machinery 识别” 以及 “AoGpr2/AoGpr3 可能接触 endogenous ScGpa2 或其他 yeast components” 具备合理序列基础。
   - α5 高相似与 receptor-facing interface 的几何/化学兼容假说相关；但 coupling 还取决于 GPCR intracellular loops、Gα nucleotide cycle、Gβγ、膜定位、表达量、翻译后修饰和动力学，不能由 α5 identity 单独推出。
   - Kuo2024 Methods 写明 GPA1–Myc、GPA2–Myc、GPA3–Myc 和 GPCR constructs 来自 *A. oligospora* 并转入 *S. cerevisiae* YDX4；Fig. 4a 没有直接比较 AoGPCR–ScGpa1 或 AoGPCR–ScGpa2。
   - Supplementary Table 4 的 YDX4 genotype 未列出 `GPA1` 或 `GPA2` deletion。因此 endogenous yeast components 不能从实验背景中自动排除；但“未列为 deletion”也不证明它们参与了 co-IP、competition 或 signalling。
   - Fig. 4a 支持 tagged AoGpr2/AoGpr3 与 tagged AoGpa2 在异源酵母 lysate/IP 条件下的 physical association。Co-IP 不区分直接接触、宿主桥接、过表达 proximity 或 detergent-dependent complex retention，也不测量 ligand-dependent nucleotide exchange 或 downstream signalling。
   - *A. oligospora* 中的 cAMP、gpr mutant 和 `GPA2^Q208L` genetic data 支持 Gpr2/Gpr3 与 Gpa2–cAMP–PKA pathway association；它仍不能替代 native direct-coupling assay。

5. **新增 AfGasA 不改变上述 Kuo Fig. 4a 结论。** AfGasA 是 Hu2024 的 *A. flagrans* `gasA/DFL_009501`，不是 Kuo2024 的 *A. oligospora* `GPA2/EYR41_010456`。它提供的比较价值是：AfGasA 相对酵母更接近 ScGpa1（全长 37.632% vs 34.956%；α5 55.556% vs 32.143%），而 AoGpa2 的 α5 则强烈偏向 ScGpa2。这可用于提出不同 receptor/Gα 组合的 compatibility hypothesis，但不能证明 GprC–ScGpa1 或任何新的 cross-coupling。

最准确的总表述是：**序列结果提高了 host cross-coupling/competition 假说的先验可信度，也增强了对 Fig. 4a 做宿主背景控制的必要性；现有数据没有 experimentally demonstrate AoGpr2/AoGpr3–ScGpa2 coupling，也没有仅凭该异源 co-IP 单独证明原生 AoGPCR–AoGpa2 的直接功能性 coupling。**

### 实际执行与从零复现命令

一键重放脚本：[`reproduce.sh`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/reproduce.sh)。脚本保留已存在的 source artifacts，重建 derived alignments/results，并用硬编码预期 SHA256 与 `checksums.sha256` 双重检查四个 FASTA。

实际执行的 FASTA 与 CDS 下载命令：

```zsh
curl -fsSL 'https://rest.uniprot.org/uniprotkb/P08539.fasta' -o /private/tmp/ScGpa1_P08539.fasta
curl -fsSL 'https://rest.uniprot.org/uniprotkb/P10823.fasta' -o /private/tmp/ScGpa2_P10823.fasta
curl -fsSL 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=TGJ64397.1&rettype=fasta&retmode=text' -o /private/tmp/AoGpa2_TGJ64397.1.fasta
curl -fsSL 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=TGJ64397.1&rettype=fasta_cds_na&retmode=text' -o /private/tmp/TGJ64397.1_cds.fna
curl -fsSL 'https://rest.uniprot.org/uniprotkb/A0A436ZRX2.fasta' -o experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/AfGasA_A0A436ZRX2.fasta
curl -fsSL 'https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id=RVD81648.1&db=protein&report=fasta_cds_na&retmode=text' -o experiments/chimeric-gpa1/sequence-comparison-20260811/records/RVD81648.1_cds.fna
```

实际执行的 identity/annotation source 下载命令：

```zsh
curl -fsSL 'https://rest.uniprot.org/uniprotkb/P08539.txt' -o /private/tmp/P08539_uniprot.txt
curl -fsSL 'https://rest.uniprot.org/uniprotkb/P10823.txt' -o /private/tmp/P10823_uniprot.txt
curl -fsSL 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=TGJ64397.1&rettype=gb&retmode=text' -o /private/tmp/TGJ64397.1_genbank.txt
curl -fsSL 'https://rest.uniprot.org/uniprotkb/A0A436ZRX2.txt' -o experiments/chimeric-gpa1/sequence-comparison-20260811/records/A0A436ZRX2_uniprot.txt
curl -fsSL 'https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id=RVD81648.1&db=protein&report=fasta&retmode=text' -o experiments/chimeric-gpa1/sequence-comparison-20260811/records/RVD81648.1_ncbi.fasta
curl -fsSL 'https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id=RVD81648.1&db=protein&report=genbank&retmode=text' -o experiments/chimeric-gpa1/sequence-comparison-20260811/records/RVD81648.1_genbank.txt
curl -fsSL 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/?report=xml' -o experiments/chimeric-gpa1/sequence-comparison-20260811/sources/Hu2024_PMC11222155.html
curl -fsSL 'https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM4_ESM.xlsx' -o /private/tmp/Kuo2024_Supplementary_Tables_1-4.xlsx
curl -fsSL 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id=SAMN10185917&retmode=xml' -o /private/tmp/SAMN10185917.xml
curl -fsSL 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=6453484&retmode=xml' -o /private/tmp/Youssar2019_PMC6453484.xml
curl -fL 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11222155/supplementaryFiles' -o /private/tmp/PMC11222155_supplementary.zip
```

Pairwise global、core、α5 alignment 和统计的实际 command：

```zsh
/opt/homebrew/Caskroom/miniforge/base/envs/chimeric/bin/python \
  experiments/chimeric-gpa1/sequence-comparison-20260811/analyze_sequences.py \
  --clustalo /opt/homebrew/Caskroom/miniforge/base/envs/chimeric/bin/clustalo
```

脚本内部实际调用的 MSA command（记录见 [`clustalo_run.log`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/clustalo_run.log)）：

```zsh
/opt/homebrew/Caskroom/miniforge/base/envs/chimeric/bin/clustalo \
  --infile /Users/roy/Documents/drylab/experiments/chimeric-gpa1/sequence-comparison-20260811/sequences/four_Galpha_combined.fasta \
  --outfile /Users/roy/Documents/drylab/experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/four_Galpha_clustalo.clustal \
  --outfmt=clu --seqtype=Protein --threads=1 --output-order=input-order --force
```

从 checkout 重放和 checksum gate：

```zsh
experiments/chimeric-gpa1/sequence-comparison-20260811/reproduce.sh
```

结构化结果：[`sequence_comparison.json`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/results/sequence_comparison.json)、[`pairwise_stats.tsv`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/results/pairwise_stats.tsv)、[`motifs.tsv`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/results/motifs.tsv)。六组可读 global alignments 与区域/核心诊断位于 [`alignments/pairwise/`](../../experiments/chimeric-gpa1/sequence-comparison-20260811/alignments/pairwise/)。

## Gaps and Conflicts

- *Arthrobotrys oligospora* 与 AoGpa2 NCBI record 的 *Orbilia oligospora* 是可见名称差异；本报告通过 TWF154、`EYR41_010456`、TGJ64397.1、genomic CDS 和论文 primers 解决 accession identity，但不抹掉 taxonomy 差异。
- Hu2024 使用 *Arthrobotrys flagrans*，并说明该物种 formerly *Duddingtonia flagrans*；`DFL_` locus prefix 和旧 NCBI hypothetical-protein 名称被保留，但不构成 accession 冲突。
- **AfGasA strain provenance 未完全闭合。** Hu2024 和产生 `SAEB01000000` genome 的 Youssar2019 都写实验株 `CBS 349.94`；Hu2024 又把所用 genome 指向 `PRJNA494930`。同一 BioProject 下 `RVD81648.1` 的 NCBI record/BioSample 却写 `CBS H-5679`，BioSample note 为 `A. Rubner, A.R. 9125`。未找到权威 cross-reference 证明 `CBS 349.94 = CBS H-5679`，所以二者不得互换。由于论文 locus、BioProject、protein accession、scaffold、CDS translation 和 residue sequence 均直接闭合，该冲突限制的是 strain-level provenance 表述，不是本报告采用的 protein sequence identity。
- 本机没有 EMBOSS `needle` 或 MAFFT；pairwise 因此使用注明版本和参数的 Biopython Needleman–Wunsch equivalent，MSA 使用用户允许的 Clustal Omega。同分最优路径差异已逐条审计。
- α5 起点是 aligned G5 core 后 conserved Asp 的 operational structural boundary，不是四条蛋白各自实验结构的 DSSP assignment。AoGpa2/AfGasA 的 broader CDD receptor-binding features向上游延伸；若问题改为整个 β6–α5 neighborhood，需要另定义更长敏感性窗口。
- Kuo Fig. 4a 没有测 ScGpa1/ScGpa2 interaction、ligand-triggered GTP exchange、yeast reporter response 或 native *A. oligospora* receptor–Gα direct contact。
- Raw alignment score 受 sequence length 和 gap pattern 影响；跨 pair 的解释主要依据同一方法下的 identity/similarity 与区域比较，不单独用 score 排序。

## Research Objective

- Decision/use: 判断 AoGpa2、AfGasA 与两条 *S. cerevisiae* Gα 的真实序列接近程度，并界定 Kuo2024 Fig. 4a 异源 co-IP 的宿主背景解释边界。
- Target question: 四条实序列的 whole-protein global identity、BLOSUM62-positive similarity、gaps、Gα-core similarity 和 α5/C-terminal identity 分别是多少；AoGpa2 与 AfGasA 各自更接近哪条酵母 Gα。
- Source scope: UniProtKB reviewed records、NCBI Protein/GenBank/genomic CDS/BioSample、Kuo2024、Hu2024 与 Youssar2019 primary articles、publisher supplementary files、本地可重放 alignment outputs。
- Exclusions: 搜索摘要 identity、BLAST local identity、按 protein name 或 phylogeny 猜测、同源补全、未经实际 FASTA 计算的百分比、把 co-IP 自动升级为 functional coupling。
- Access date: 2026-08-11 至 2026-08-12, Asia/Shanghai.

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|---|---|---|---|---|---|---|
| S1 | UniProtKB P08539 / GPA1_YEAST | https://www.uniprot.org/uniprotkb/P08539/entry | official curated sequence database | 2026-08-11 | ScGpa1 sequence, species, length, motifs, insertion | used; FASTA and flat record saved |
| S2 | UniProtKB P10823 / GPA2_YEAST | https://www.uniprot.org/uniprotkb/P10823/entry | official curated sequence database | 2026-08-11 | ScGpa2 sequence, species, length, motifs, N-terminal disorder | used; FASTA and flat record saved |
| S3 | NCBI Protein TGJ64397.1 | https://www.ncbi.nlm.nih.gov/protein/TGJ64397.1 | official sequence database | 2026-08-11 | AoGpa2 sequence, locus tag, strain, CDD features, CDS mapping | used; FASTA and GenBank record saved |
| S4 | NCBI scaffold SOZJ01000007.1 | https://www.ncbi.nlm.nih.gov/nuccore/SOZJ01000007.1 | official sequence database | 2026-08-11 | AoGpa2 genomic CDS translation | used; CDS export saved |
| S5 | Kuo et al. 2024 article | https://pmc.ncbi.nlm.nih.gov/articles/PMC11724650/ | primary research article | 2026-08-11 | Fig. 4a design, Methods, native genetic/cAMP context | used; full text inspected |
| S6 | Kuo2024 Supplementary Tables 1–4 | https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM4_ESM.xlsx | primary publisher supplement | 2026-08-11 | GPA2 primers, YDX4 genotype, strains and plasmids | used; workbook saved and inspected |
| S7 | UniProtKB A0A436ZRX2 / GASA_ARTFL | https://www.uniprot.org/uniprotkb/A0A436ZRX2/entry | official curated sequence database | 2026-08-12 | AfGasA name, DFL_009501 mapping, sequence, motifs, NCBI cross-reference | used; FASTA and flat record saved |
| S8 | NCBI Protein RVD81648.1 | https://www.ncbi.nlm.nih.gov/protein/RVD81648.1 | official sequence database | 2026-08-12 | DFL_009501 locus, G-alpha CDD, scaffold and genomic CDS | used; FASTA, GenBank record and CDS saved |
| S9 | Hu et al. 2024 article | https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/ | primary research article | 2026-08-12 | direct `gasA (dfl_009501)` identity and biological context | used; full-text HTML saved and inspected |
| S10 | Youssar et al. 2019 genome article | https://pmc.ncbi.nlm.nih.gov/articles/PMC6453484/ | primary research article | 2026-08-12 | experimental strain label and `SAEB01000000` genome provenance | used; full-text XML inspected |
| S11 | NCBI BioSample SAMN10185917 | https://www.ncbi.nlm.nih.gov/biosample/SAMN10185917 | official sequence-sample metadata | 2026-08-12 | assembly strain/culture-collection label and submitter note | used; full BioSample XML inspected |
| S12 | Recomputed sequence comparison JSON | ../../experiments/chimeric-gpa1/sequence-comparison-20260811/results/sequence_comparison.json | reproducible derived computation | 2026-08-12 | all reported percentages, scores, motif checks and boundaries | used; locally inspectable |
| S13 | Reproduction script and checksum gate | ../../experiments/chimeric-gpa1/sequence-comparison-20260811/reproduce.sh | reproducible local workflow | 2026-08-12 | endpoints, commands, versions and rerun path | used; locally inspectable |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| ScGpa1 is the 472-aa *S. cerevisiae* Gpa1 used here | S1 | flat record `ID/AC/OS/FT DOMAIN/SQ`; FASTA header | P08539 is reviewed GPA1_YEAST from S288c and contains the saved 472-aa sequence | high | sequence/annotation evidence, not expression evidence |
| ScGpa2 is the 449-aa *S. cerevisiae* Gpa2 used here | S2 | flat record `ID/AC/OS/FT DOMAIN/SQ`; FASTA header | P10823 is reviewed GPA2_YEAST from S288c and contains the saved 449-aa sequence | high | sequence/annotation evidence, not expression evidence |
| TGJ64397.1 is EYR41_010456 / GPA2 from TWF154 | S3 | GenBank `FEATURES`: source, Region, CDS; gene/locus_tag/strain/coded_by | one record directly joins accession, gene, locus tag, strain and G-alpha feature | high | organism field uses *Orbilia* rather than the paper's *Arthrobotrys* name |
| AoGpa2 protein equals the translated genomic CDS | S4 | saved `fasta_cds_na`; 1,071 nt; terminal TAA | translation gives 356 aa plus terminal stop and equals TGJ64397.1 residue-for-residue | high | checks annotation consistency, not transcript expression |
| Kuo Fig. 4a used tagged *A. oligospora* constructs in *S. cerevisiae* | S5 | Results “Gpr2 and Gpr3 interact with Gpa2”; Fig. 4 caption; Methods “Co-IP assays” | article describes the heterologous yeast co-IP design and its association claim | high | does not directly test yeast Gα or functional nucleotide exchange |
| YDX4 genotype does not list GPA1/GPA2 deletion; AoGpa2 primers match the selected CDS | S6 | Supplementary Tables 3–4, primers 4207–4208 and YDX4 row | workbook links constructs/genotype to the reported host and CDS boundary checks | high | absence from genotype is not evidence of endogenous participation |
| A0A436ZRX2 directly maps gasA to DFL_009501 and RVD81648.1 | S7 | flat record `ID/AC/GN/DR EMBL/DR VEuPathDB/FT/SQ` | reviewed record joins protein name, ORF, sequence and NCBI/FungiDB cross-references | high | curation postdates the original 2019 NCBI product label |
| RVD81648.1 and its CDS carry DFL_009501 and equal A0A436ZRX2 | S8 | GenBank definition/source/CDS/coded_by; saved NCBI FASTA and `fasta_cds_na` | 353-aa protein and 1,062-nt CDS independently reproduce the UniProt residue sequence | high | NCBI product remains “hypothetical protein” |
| Hu2024 explicitly identifies GasA as gasA (dfl_009501) and points to PRJNA494930 | S9 | Results `Par7`; Methods `Par21`; Data Availability; PMID 38877225 | primary paper supplies the GasA/locus relation, calls the experimental strain CBS 349.94, and identifies the genome database used | high | biological function evidence is separate from sequence identity calculation |
| The original SAEB genome article calls its experimental strain CBS 349.94 | S10 | Methods “Cultivation of the organisms”; Data Availability | Youssar2019 states CBS 349.94 and identifies genome accession SAEB01000000 | high | does not explain the different BioSample culture-collection label |
| The sequence BioSample labels the assembly CBS H-5679 / A.R. 9125 | S11 | BioSample `Attributes`: strain, culture_collection, note | SAMN10185917 records CBS H-5679 and note `A. Rubner, A.R. 9125` | high | no inspected source explicitly equates this with CBS 349.94 |
| All six global and α5 percentages come from the four saved FASTA files | S12 | `global_pairwise`, `alpha5_C_terminal`, `G_alpha_core_diagnostic`, tie audit | JSON records numerator, denominator, percentage, gaps, score, boundaries and validation checks | high | values depend on the explicitly stated global scoring scheme |
| Workflow can be replayed while checking all four FASTA identities | S13 | `fetch_if_missing`, analysis invocation, hardcoded expected hashes, `shasum -c` | script records all source endpoints and regenerates the derived outputs | high | default executable paths are Mac-specific; environment variables can override them |

## Audit Notes

- Discover: candidate sequence records were restricted to records carrying the exact requested locus tags and direct database cross-references; no “most similar” substitution was allowed.
- Verify: AfGasA was checked through Hu2024, Youssar2019, UniProt A0A436ZRX2, NCBI RVD81648.1, BioSample SAMN10185917 and the genomic CDS; the UniProt and NCBI protein residues are identical. The strain-label conflict is retained because no inspected source supplied a cross-reference equating the two CBS numbers.
- Extract: lengths, headers, locus tags, features, CDS translations, paper paragraphs, strain labels, BioProject/BioSample links, Kuo primers and YDX4 genotype were read from full records/files rather than search-result summaries.
- Compute: every percentage comes from the four saved FASTA files. Every gapped pairwise row reconstructs both inputs, and every score was independently recalculated from BLOSUM62 plus affine gaps.
- Audit: all score-tied global paths were enumerated. Tie-breaking does not alter the AoGpa2–ScGpa2 or AfGasA–ScGpa1 relative conclusions.
- Final replay, four-file checksum gate, local-link check and strict Markdown evidence lint are reported after the final verification run.
