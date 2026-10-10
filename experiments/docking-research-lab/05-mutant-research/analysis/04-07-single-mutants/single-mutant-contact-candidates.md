# 单突变候选筛选与WT接触对照

2026-09-18。目的：先筛选值得深入检查的单突变，再决定二维接触图的制作顺序。依据为原单突变分析第2节（原引用 `single-mutant-analysis.md#2-按位点解读` 在源目录未定位）四个位点表格中明确列出的41种替换；N84/V110/V368采用05批、W338采用07批。其他饱和结果仍保留在[完整统计表](saturation-statistics.md)。

## 1．筛选标准

本轮采用 **|D05|≥0.300 kcal/mol** 作为工作阈值，得到16个候选。D05统一以05-WT计算，D=ΔS18−ΔS3。这个阈值用来控制报告和作图规模，是对已有结果的筛选规则，不是统计显著性界限。阈值内还要看目标配体评分、接触是否提供新信息及结构来源。

其余25种暂不进入候选作图清单。小|D|表示本次对接中两种配体的相对变化较接近，并不能据此排除实验中的特异响应；V368N这样的共同改善型突变，也仍有机制对照价值。

评分筛选和接触对照使用两个明确口径：评分统一用05-WT；接触增减使用同批WT，即05突变对05-WT、07突变对07-WT。这样既能比较D，又能看清各自结构来源下的接触变化。

| WT | S3 | S18 | #3接触残基 | #18接触残基 |
|---|---:|---:|---:|---:|
| 05-WT | -6.625 | -6.492 | 8 | 11 |
| 07-WT | -6.551 | -6.52 | 10 | 12 |

07-WT相对05-WT的评分零点不同：同一个07突变的D05=D07−0.102。因此W338F/H/M虽然在原报告中|D07|小于0.300，统一到05-WT后进入本轮清单。所有16个候选在05/07两种WT下的D方向一致；是否跨过0.300阈值仍会随参照改变。

## 2．16个候选及选择理由

下表ΔS3、ΔS18、D均以05-WT计算，负ΔS表示评分降低。作图顺序综合作用方式和信息量，不按|D|机械排序。

| 突变 | ΔS3 | ΔS18 | D05 | D本批WT | 选择理由 | 作图顺序 |
|---|---:|---:|---:|---:|---|---|
| N84T | +0.116 | -0.227 | -0.343 | -0.343 | 与N84V同方向，作为同位点替换对照。 | 后续备选 |
| N84V | +0.361 | -0.364 | -0.725 | -0.725 | 改善#18并削弱#3，负D幅度突出。 | 首批 |
| N84Y | -0.281 | +0.110 | +0.391 | +0.391 | 改善#3并削弱#18，正D清楚。 | 后续备选 |
| V110C | -0.094 | -0.561 | -0.467 | -0.467 | #18改善较多，#3也略有改善。 | 首批 |
| V110D | -0.133 | -0.472 | -0.339 | -0.339 | #18改善幅度与S接近，接触方式不同。 | 后续备选 |
| V110I | +0.050 | -0.254 | -0.304 | -0.304 | 刚超过工作阈值，#18评分改善；历史来源差异需先解释。 | 暂缓作图 |
| V110M | -0.004 | +0.426 | +0.430 | +0.430 | #3评分基本保留，主要削弱#18。 | 首批 |
| V110P | -0.384 | -0.050 | +0.334 | +0.334 | 主要改善#3，D达到工作阈值。 | 暂缓作图 |
| V110R | -0.009 | +0.405 | +0.414 | +0.414 | 主要削弱#18，可与M比较。 | 后续备选 |
| V110S | -0.103 | -0.464 | -0.361 | -0.361 | 与C同方向，提供相近侧链的替换对照。 | 后续备选 |
| V368Q | -0.108 | +0.208 | +0.316 | +0.316 | 改善#3并削弱#18，可与R作同位点对照。 | 后续备选 |
| V368R | -0.388 | +0.199 | +0.587 | +0.587 | 改善#3并削弱#18，正D幅度突出。 | 首批 |
| W338F | +0.070 | -0.280 | -0.350 | -0.248 | 主要改善#18，两批D方向一致，突变位点有直接接触。 | 首批扩展 |
| W338H | -0.139 | -0.526 | -0.387 | -0.285 | 两配体均改善，#18改善更多。 | 后续备选 |
| W338L | -0.227 | -0.854 | -0.627 | -0.525 | 07批#18评分改善幅度大，但06/07结果翻转。 | 首批扩展，带来源检查 |
| W338M | +0.086 | -0.238 | -0.324 | -0.222 | 主要改善#18，提供F之外的同位点对照。 | 后续备选 |

## 3．与同批WT相比，接触发生了什么变化？

以下均来自每次最低分pose。按原残基编号＋接触类型比较；同一编号、同一类型保留时，即使残基身份因突变改变，也不重复算作新增，身份变化另列。新增/丢失指本次pose相对WT的检出变化。

“接触作用力变化”在这里具体指ProLIF接触类型和几何关系的变化，没有进行逐接触能量分解。HA/HDon保留软件对配体受体对的类型定义，不据标签直接判断表中蛋白残基的供受体身份。

| 简写 | 原始类型 | 阅读方式 |
|---|---|---|
| 离子 | Anionic | 离子类型接触；不是说列出的Arg/Lys带负电 |
| HA | HBAcceptor | 氢键类型，具体原子和方向需在制图时核对 |
| HDon | HBDonor | 氢键类型，具体原子和方向需在制图时核对 |
| 疏水 | Hydrophobic | 疏水接触 |
| VdW | VdWContact | 近距离范德华接触条目 |

每个候选分开列出氢键、离子、疏水接触与VdW变化。表中“无”表示该类没有变化；突变位点栏的“未检出”表示该pose没有该位点的直接接触。共同保留的完整接触见链接中的原表。

### N84T

比较T与V的#18接触和口袋几何，判断较小的D是否对应另一种配体定位。

原始评分：#3 -6.509、#18 -6.719；相对05-WT的ΔS3=+0.116、ΔS18=-0.227、D=-0.343。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 疏水：L31；HDon：Q107 | 无 |
| #18 | HDon：S80；离子：R189；疏水：W338 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, A81, V368 | VdW：V110 | 未检出 | 8→10 |
| #18 | VdW：N28 | VdW：A81, T106, Q107, V110, R181, N185 | 未检出 | 11→8 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84t/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84t/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### N84V

重点看#18的R189/W338接触，以及#3为何失去110位近距离接触；84位自身没有直接接触。

原始评分：#3 -6.264、#18 -6.856；相对05-WT的ΔS3=+0.361、ΔS18=-0.364、D=-0.725。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：R181 | 无 |
| #18 | 疏水：F186, W338；离子：R189；HA：R189 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | 无 | VdW：V110 | 未检出 | 8→7 |
| #18 | VdW：L90, N102, R189, V368 | VdW：A81, Q107, R181, N185 | 未检出 | 11→13 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84v/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84v/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### N84Y

检查#3新增S80、R181氢键条目的几何；Y84自身没有直接接触。

原始评分：#3 -6.906、#18 -6.382；相对05-WT的ΔS3=-0.281、ΔS18=+0.110、D=+0.391。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：S80, R181 | 无 |
| #18 | 疏水：L31；HDon：N102；HA：T106 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31 | 无 | 未检出 | 8→9 |
| #18 | VdW：N102, G103, V368 | VdW：S80, Q107, V110, R181, N185 | 未检出 | 11→9 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84y/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_n84y/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110C

检查C110近距离接触和#18的R189/W338接触组合，确定配体两部分如何定位。

原始评分：#3 -6.719、#18 -7.053；相对05-WT的ΔS3=-0.094、ΔS18=-0.561、D=-0.467。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 疏水：L31；HDon：Q107；HA：R181 | 无 |
| #18 | HA：N28, K364；疏水：F186, W338；离子：R189 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, N185 | 无 | VdW | 8→10 |
| #18 | VdW：L27, N28, N84, R189, W338 | VdW：L31, S80, A81, T106, Q107, R181, N185 | VdW | 11→10 |

保留接触中的残基身份变化：V110→C110。

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110c/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110c/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110D

检查R181/R345/K364相关接触；与C/S比较相似评分收益是否来自不同配体位置。

原始评分：#3 -6.758、#18 -6.964；相对05-WT的ΔS3=-0.133、ΔS18=-0.472、D=-0.339。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 无 | 无 |
| #18 | HA：N28, R345, K364；离子：R181, R345, K364 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, W338 | VdW：T106, Q107 | VdW | 8→8 |
| #18 | VdW：L27, N28, N84, L90, R345 | VdW：T106, Q107, V110, N185 | 未检出 | 11→12 |

保留接触中的残基身份变化：V110→D110。

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110d/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110d/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110I

先对照04/05既有结构与WT，再决定是否画图；详细图不是当前首要工作。

原始评分：#3 -6.575、#18 -6.746；相对05-WT的ΔS3=+0.050、ΔS18=-0.254、D=-0.304。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：N28, K364；离子：R181, R345, K364 | 无 |
| #18 | HA：N28, K364；离子：R181, R345, K364 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：N28, L31, A81, L90, V368 | VdW：T106, Q107, V110, R181 | 未检出 | 8→11 |
| #18 | VdW：N28, N84, L90 | VdW：S80, T106, Q107, V110, R181, N185 | 未检出 | 11→10 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110i/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110i/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110M

优先查#18失去的Q107氢键条目和其他近距离接触，解释非目标评分损失。

原始评分：#3 -6.629、#18 -6.066；相对05-WT的ΔS3=-0.004、ΔS18=+0.426、D=+0.430。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 无 | 无 |
| #18 | 疏水：L31；HA：T106 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, N185, F186 | 无 | VdW | 8→11 |
| #18 | VdW：N84, N102, G103, V368 | VdW：Q107, V110, R181, N185 | 未检出 | 11→11 |

保留接触中的残基身份变化：V110→M110。

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110m/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110m/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110P

先检查110附近局部骨架；二维接触图难以独立解释P替换可能伴随的构象变化。

原始评分：#3 -7.009、#18 -6.542；相对05-WT的ΔS3=-0.384、ΔS18=-0.050、D=+0.334。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 疏水：L31 | 无 |
| #18 | 无 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, A81, N185, R189, V368 | VdW：F77 | VdW | 8→13 |
| #18 | VdW：V368 | 无 | VdW | 11→12 |

保留接触中的残基身份变化：V110→P110。

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110p/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110p/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110R

两者评分作用相近，但接触增减不同；检查R110是否直接参与以及配体位置是否改变。

原始评分：#3 -6.634、#18 -6.087；相对05-WT的ΔS3=-0.009、ΔS18=+0.405、D=+0.414。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 疏水：L31；HDon：N185 | 疏水：I367 |
| #18 | HDon：D24；HA：N28, K364；疏水：L31 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, A81, N185, V368 | VdW：S80, K364 | VdW | 8→11 |
| #18 | VdW：D24, L27, N28, N84, L90, V368 | VdW：A81, Q107, V110, R181, N185 | 未检出 | 11→12 |

保留接触中的残基身份变化：V110→R110。

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110r/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110r/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V110S

S110在两配体中均无直接接触；对照C，检查收益与间接定位变化的关系。

原始评分：#3 -6.728、#18 -6.956；相对05-WT的ΔS3=-0.103、ΔS18=-0.464、D=-0.361。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | 疏水：L31 | 无 |
| #18 | HA：N28, R189, K364；疏水：F186, W338；离子：R189 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, A81, N185, F186, W338 | VdW：T106, V110 | 未检出 | 8→11 |
| #18 | VdW：N28, N84, R189, V368 | VdW：S80, A81, T106, Q107, V110, R181 | 未检出 | 11→11 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110s/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v110s/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V368Q

#18新增离子类型接触却评分变差，值得检查接触位置和整体姿态。

原始评分：#3 -6.733、#18 -6.284；相对05-WT的ΔS3=-0.108、ΔS18=+0.208、D=+0.316。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：A81, R181；疏水：Q368 | 无 |
| #18 | HA：N28, K364；离子：R181, R345, K364；疏水：Q368 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：L31, A81, Q368 | 无 | 疏水, VdW | 8→11 |
| #18 | VdW：D24, N28, L90, R345, Q368 | VdW：T106, Q107, V110, R181, N185 | 疏水, VdW | 11→12 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v368q/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v368q/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### V368R

R368自身未检出离子类型接触；检查N28/K364相关变化，避免把收益直接归给新增Arg。

原始评分：#3 -7.013、#18 -6.293；相对05-WT的ΔS3=-0.388、ΔS18=+0.199、D=+0.587。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：N28, K364；HDon：N28；疏水：L31；离子：K364 | 无 |
| #18 | HA：N28, K364；疏水：L31；离子：K364 | HDon：Q107 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：N28, L31, A81, L90 | VdW：T106, Q107, V110, R181 | 未检出 | 8→8 |
| #18 | VdW：L27, N28, N84, R368 | VdW：A81, T106, Q107, V110, R181, N185 | VdW | 11→9 |

原表：[突变体#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v368r/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_v368r/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/05-af3-n84-v110-v368-saturations/run-01/05_baseline/ascr18/top1_contacts/contact_residues.csv)。

### W338F

检查F338的VdW接触与R189相关条目；同时看#3和#18的接触几何差别。

原始评分：#3 -6.555、#18 -6.772；相对07-WT的ΔS3=-0.004、ΔS18=-0.252、D=-0.248。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HDon：S80；HA：A81, K364；疏水：V110, F186；离子：R189 | 疏水：L31, K364；HA：S80 |
| #18 | HA：S80；HDon：S80；疏水：F186；离子：R189 | HA：N28；离子：R181, R345, K364 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：N28, A81, R189, F338 | VdW：Q107, R181, V368 | VdW | 10→12 |
| #18 | VdW：N102, T106, V110, F186, R189, F338 | VdW：D24, L31, N84, L90 | VdW | 12→12 |

原表：[突变体#3](../../batches/07-af3-w338-saturation/run-01/07_w338f/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/07-af3-w338-saturation/run-01/07_w338f/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr18/top1_contacts/contact_residues.csv)。

### W338H

H338本身无直接接触，重点看#18的R189/F186/K364变化；与F或L比较。

原始评分：#3 -6.764、#18 -7.018；相对07-WT的ΔS3=-0.213、ΔS18=-0.498、D=-0.285。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：N28, R181, K364；离子：R181, R345, K364 | 疏水：L31；HA：S80 |
| #18 | 疏水：F186；离子：R189；HA：R189, K364 | HA：N28；离子：R181, R345, K364 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：N28, N84 | VdW：S80, T106, Q107, V110 | 未检出 | 10→9 |
| #18 | VdW：V110, R189 | VdW：D24, S80, A81 | 未检出 | 12→10 |

原表：[突变体#3](../../batches/07-af3-w338-saturation/run-01/07_w338h/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/07-af3-w338-saturation/run-01/07_w338h/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr18/top1_contacts/contact_residues.csv)。

### W338L

先比较两批L的配体位置及R345接触，再画07-L/WT；它优先需要解释，尚非优先采用。

原始评分：#3 -6.852、#18 -7.346；相对07-WT的ΔS3=-0.301、ΔS18=-0.826、D=-0.525。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：R181 | HA：S80 |
| #18 | 疏水：L31；HA：R345 | HA：N28；离子：R181, R345, K364 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：A81, N185, R189, R345 | VdW：T106, Q107, V110 | 未检出 | 10→11 |
| #18 | VdW：V110, R181, N185, F186, R189, R345, V368 | VdW：D24, N28, N84, L90 | 未检出 | 12→13 |

原表：[突变体#3](../../batches/07-af3-w338-saturation/run-01/07_w338l/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/07-af3-w338-saturation/run-01/07_w338l/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr18/top1_contacts/contact_residues.csv)。

### W338M

#18新增R189等接触，M338自身直接接触情况见下表；与F比较是否需要保留芳香侧链。

原始评分：#3 -6.539、#18 -6.73；相对07-WT的ΔS3=+0.012、ΔS18=-0.210、D=-0.222。

| 配体 | 新增氢键/离子/疏水 | 丢失氢键/离子/疏水 |
|---|---|---|
| #3 | HA：A81 | 疏水：L31；HA：S80 |
| #18 | HDon：S80；HA：A81, R189；疏水：V110, F186；离子：R189 | HA：N28；离子：R181, R345, K364 |

| 配体 | 新增VdW | 丢失VdW | 突变位点直接接触 | 接触残基数：WT→突变体 |
|---|---|---|---|---|
| #3 | VdW：A81, N185, F186 | 无 | 未检出 | 10→13 |
| #18 | VdW：L27, T106, V110, R189, V368 | VdW：D24, L90 | 未检出 | 12→14 |

原表：[突变体#3](../../batches/07-af3-w338-saturation/run-01/07_w338m/ascr3/top1_contacts/contact_residues.csv) · [WT#3](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr3/top1_contacts/contact_residues.csv) · [突变体#18](../../batches/07-af3-w338-saturation/run-01/07_w338m/ascr18/top1_contacts/contact_residues.csv) · [WT#18](../../batches/07-af3-w338-saturation/run-01/07_baseline/ascr18/top1_contacts/contact_residues.csv)。

## 4．先画哪些二维接触图？

建议分两步制作，先完成能回答不同问题的少数图。每个候选同时比较两种配体，避免只展示改善的一侧。

| 顺序 | 突变体 | 这张图主要回答什么 |
|---|---|---|
| 第一组 | V368R | #3改善与#18变差分别对应什么接触？R368未直接形成离子接触时，K364/N28如何变化？ |
| 第一组 | N84V | R189/W338相关接触与#18改善如何对应？#3又失去了什么？ |
| 第一组 | V110M | #3基本保留而#18变差，主要接触差异在哪里？ |
| 第一组 | V110C | #18改善较多时，C110直接接触与R189/W338接触如何共同安排？ |
| 第二组 | W338F | F338有直接接触时，两种配体的接触几何有什么不同？ |
| 第二组 | W338L | 无L338直接接触时，07批较好评分对应什么模式？与06批为何不同？ |

第一组4个突变体共8张配体图，加05-WT的2张，共10张独立图。第二组增加F/L的4张和07-WT的2张，再增加6张；共16张即可覆盖四个位点及主要作用方式。WT图复用，并排版式不重复计算图数。

W338L先对照06/07现有三维姿态和接触表。若需要用二维图解释翻转，再增加06-L及06-WT各两张，共4张；这4张是来源比较扩展，不必在首批制作。

其余候选中，N84Y/T、V110S/D、V368Q适合在对应主候选图出现明确问题时补充；V110R、W338H/M提供作用相近或同位点对照。V110I、V110P先处理历史来源或局部骨架问题，再决定作图。

制图时统一残基编号、配体原子标识和颜色；氢键/离子接触核对具体原子与距离，WT与突变体采用相同显示规则。只有接触表有差异的条目应突出标注。图展示结构解释，最终候选仍需结合两项评分和D判断。

## 5．暂不进入本轮候选作图的25种替换

以下均为原报告四个位点表格中的受体，本轮因|D05|<0.300暂不优先制图。保留原始结果；这里不作实验功能淘汰。

| 突变 | D05 | D本批WT |
|---|---:|---:|
| N84A | +0.058 | +0.058 |
| N84L | +0.265 | +0.265 |
| N84Q | -0.080 | -0.080 |
| V110L | -0.021 | -0.021 |
| V110T | +0.059 | +0.059 |
| V368A | +0.091 | +0.091 |
| V368I | -0.231 | -0.231 |
| V368L | +0.088 | +0.088 |
| V368N | -0.004 | -0.004 |
| V368P | +0.209 | +0.209 |
| W338A | -0.250 | -0.148 |
| W338C | -0.106 | -0.004 |
| W338D | -0.037 | +0.065 |
| W338E | +0.124 | +0.226 |
| W338G | +0.237 | +0.339 |
| W338I | -0.132 | -0.030 |
| W338K | +0.056 | +0.158 |
| W338N | -0.055 | +0.047 |
| W338P | +0.106 | +0.208 |
| W338Q | +0.138 | +0.240 |
| W338R | +0.118 | +0.220 |
| W338S | +0.109 | +0.211 |
| W338T | +0.075 | +0.177 |
| W338V | +0.023 | +0.125 |
| W338Y | +0.219 | +0.321 |

V368N/A、N84Q仍可作为共同改善对照；W338R可作为直接离子类型接触的机制对照。W338G/Y在07本批WT下的|D|超过0.300，但换算05-WT后分别为0.237/0.219，因此在这条统一工作规则下暂缓。这里的取舍说明阈值依赖分析目的和参照，不是对这些突变永久否定。

## 6．核验与阅读入口

本报告重新读取并核验16个候选及05/07-WT的36份最低分pose接触结果：评分与pose选择一致，接触表与IFP一致，接触增减与原汇总一致。没有重新运行Vina、ProLIF或生成二维图。HA/HDon等条目仍需制图时检查原子级几何。

每设计仅一次最低分pose；跨批结构来源分别保留。当前结果用于安排候选检查顺序，响应特异性需由功能测定判断。

- 单突变原分析（原引用 `single-mutant-analysis.md` 在源目录未定位）
- [四位点饱和统计](saturation-statistics.md)
- [完整评分与接触数据](data/single-mutants.json)
