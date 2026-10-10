# PyMOL pocket comparison guide

## 目的和证据范围

本指南用于比较 TWF154 Gpr2/Gpr3 与 GprC、SRBC-64 的胞外候选口袋。四个 `target` PDB 已经应用各自的 TM-align 刚体变换；PyMOL 负责显示、空间邻居筛选和人工判读。

这些 `target` 已处在对应参考受体的坐标系中。主流程加载后保持坐标不变，直接进行口袋观察。若使用后文的可选 CEalign 路线，应先运行 `reinitialize`，再加载原始完整结构。

本流程能够支持以下判断：

- 候选口袋是否位于相同的胞外七跨膜束区域；
- 该空间是否主要由 TM2、TM3、TM5、TM6、TM7 和 ECL2 构成；
- 空间对应残基的化学类型是否相似；
- ATCC–TWF154 差异位点是否靠近候选口袋；
- 判断是否依赖低置信结构区域。

这些结果属于结构相似性证据。直接配体结合和功能效应需要独立证据。

## 固定颜色

| 对象 | 颜色 |
|---|---|
| 参考受体 `reference` | 灰色 |
| 已变换的 TWF154 受体 `target` | 青色 |
| 已验证的参考口袋残基 | 黄色 |
| 暂定或未唯一解决的参考位置 | 橙色 |
| TWF154 空间邻居残基 | 洋红色 |
| TWF154 菌株差异位点 | 绿色 |

## 第 1 步：选择一组并加载

每次只处理一组。先运行 `reinitialize`，再从下面四个入口中选择一个。所有入口都将参考受体命名为 `reference`，将已变换的 TWF154 受体命名为 `target`。

### 01：TWF154 Gpr2 与 GprC

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Aflagrans_GprC_A0A437AGY2_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/01_TWF154_Gpr2_vs_GprC/TWF154_Gpr2_TGJ68930.1_full_transformed_to_GprC.pdb, target
```

### 02：TWF154 Gpr3 与 GprC

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Aflagrans_GprC_A0A437AGY2_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/02_TWF154_Gpr3_vs_GprC/TWF154_Gpr3_TGJ67963.1_full_transformed_to_GprC.pdb, target
```

### 03：TWF154 Gpr2 与 SRBC-64

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Celegans_N2_SRBC64_G5ECV4_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/03_TWF154_Gpr2_vs_SRBC64/TWF154_Gpr2_TGJ68930.1_full_transformed_to_SRBC64.pdb, target
```

### 04：TWF154 Gpr3 与 SRBC-64

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Celegans_N2_SRBC64_G5ECV4_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/04_TWF154_Gpr3_vs_SRBC64/TWF154_Gpr3_TGJ67963.1_full_transformed_to_SRBC64.pdb, target
```

## 可选路线：在 PyMOL 中直接运行 CEalign

CEalign 适合快速、独立地复核叠合结果：加载两个原始完整结构，在 PyMOL 内完成拟合，然后继续执行第 2—7 步。为了让拟合集中于七跨膜束，下面只使用 DeepTMHMM 定义的 TM-core 计算变换；CEalign 会把整个 `target` 对象一起移动，所以环区和口袋仍可正常观察。

每次只运行下面一组。这里加载的是 `alignment/inputs/structures/` 中未经变换的原始结构。

### CE-01：TWF154 Gpr2 与 GprC

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Aflagrans_GprC_A0A437AGY2_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/TWF154_Gpr2_TGJ68930.1_AF2.pdb, target
select reference_tmcore, reference and chain A and (resi 9-34+45-65+84-107+125-145+168-188+374-397+406-427)
select target_tmcore, target and chain A and (resi 30-50+62-83+101-126+144-164+182-201+326-346+358-380)
cealign reference_tmcore, target_tmcore, object=ce_tmcore
```

### CE-02：TWF154 Gpr3 与 GprC

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Aflagrans_GprC_A0A437AGY2_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/TWF154_Gpr3_TGJ67963.1_AF2.pdb, target
select reference_tmcore, reference and chain A and (resi 9-34+45-65+84-107+125-145+168-188+374-397+406-427)
select target_tmcore, target and chain A and (resi 15-37+48-68+87-112+129-149+169-189+295-315+328-349)
cealign reference_tmcore, target_tmcore, object=ce_tmcore
```

### CE-03：TWF154 Gpr2 与 SRBC-64

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Celegans_N2_SRBC64_G5ECV4_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/TWF154_Gpr2_TGJ68930.1_AF2.pdb, target
select reference_tmcore, reference and chain A and (resi 11-31+45-65+85-105+126-146+178-193+218-238+246-266)
select target_tmcore, target and chain A and (resi 30-50+62-83+101-126+144-164+182-201+326-346+358-380)
cealign reference_tmcore, target_tmcore, object=ce_tmcore
```

### CE-04：TWF154 Gpr3 与 SRBC-64

```text
reinitialize
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/Celegans_N2_SRBC64_G5ECV4_AFDB_v6.pdb, reference
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/inputs/structures/TWF154_Gpr3_TGJ67963.1_AF2.pdb, target
select reference_tmcore, reference and chain A and (resi 11-31+45-65+85-105+126-146+178-193+218-238+246-266)
select target_tmcore, target and chain A and (resi 15-37+48-68+87-112+129-149+169-189+295-315+328-349)
cealign reference_tmcore, target_tmcore, object=ce_tmcore
```

CEalign 会在 PyMOL 日志中返回 `RMSD ... over ... residues`。该数值用于检查 CEalign 自身的叠合质量；其选中残基和优化方法与 TM-align 不同，因此不与 TM-align 的 RMSD 或 TM-score 直接作数值高低比较。

两条路线的用途：

- TM-align 主流程：保留可复现的命令行输出、TM-score、变换矩阵和已变换 PDB，是当前定量比较依据；
- CEalign 可选路线：在 PyMOL 内快速复核七跨膜束和候选口袋是否得到相同的空间结论。

若两条路线把候选口袋放到相同胞外腔体，结论更稳健。若定位明显不同，先检查两者实际采用的残基数、TM 对应关系和低置信环区，再解释口袋。

## 第 2 步：检查整体叠合

```text
hide everything
show cartoon, reference or target
color gray, reference
color cyan, target
set cartoon_transparency, 0.40, reference
set stick_radius, 0.18
bg_color white
orient reference or target
```

检查：

1. 七条主要跨膜螺旋是否一一对应；
2. 是否存在某条 TM 明显落到另一条 TM 的位置；
3. 两个受体的胞外开口是否朝向同一侧。

长环和胞内尾部不参与 TM-align 拟合，其构象差异单独记录，不据此否定 TM-core 叠合。

## 第 3 步：定义参考口袋

根据当前参考受体选择一套命令。

### GprC 参考口袋：用于 01 和 02

```text
select ref_pocket_verified, reference and resi 56+60+63+83+88+91+155+157+170+171+388+395+411+414+415
select ref_pocket_provisional, reference and resi 67+174
select ref_pocket_all, ref_pocket_verified or ref_pocket_provisional
show sticks, ref_pocket_all
color yellow, ref_pocket_verified
color orange, ref_pocket_provisional
```

说明：R67 和 R174 是当前 GprC 序列中最接近 Hu2024 `R2.63`、`R5.44` 的有序精氨酸，但 BW 编号与序列相差 1 aa，因此保留为暂定映射。

### SRBC-64 参考口袋：用于 03 和 04

```text
select ref_pocket_verified, reference and resi 56+60+63+64+86+89+90+94+96+173+176+177+180+181+224+228+232+251+254+255
select ref_pocket_provisional, reference and resi 161+169
select ref_pocket_all, ref_pocket_verified or ref_pocket_provisional
show sticks, ref_pocket_all
color yellow, ref_pocket_verified
color orange, ref_pocket_provisional
```

说明：Hu2024 只给出一个 SRBC-64 ECL2 位点 `F45.48`；当前序列的 F161 和 F169 都是可能候选，因此两者以橙色显示，不将任一位置视为已解决映射。

缩放到参考口袋：

```text
zoom ref_pocket_all, 10
```

## 第 4 步：寻找 TWF154 的空间对应残基

使用 5 Å 空间邻域寻找 `target` 中靠近参考口袋的完整残基：

```text
select target_pocket_neighbors, byres ((target and polymer.protein) within 5 of ref_pocket_all)
show sticks, target_pocket_neighbors
color magenta, target_pocket_neighbors
```

打印残基名、编号和 Cα 的 pLDDT：

```text
iterate target_pocket_neighbors and name CA, print(chain, resn, resi, b)
```

需要在图中显示标签时运行：

```text
label target_pocket_neighbors and name CA, "%s%s" % (resn,resi)
set label_color, magenta
```

清除标签：

```text
label all, ""
```

5 Å 邻域用于寻找结构对应候选，不是配体接触定义，也不是一对一残基配对。

## 第 5 步：判断候选残基属于哪个结构区域

根据 target 是 Gpr2 还是 Gpr3，运行一套区域定义。

### Gpr2 区域

```text
select target_tm2, target and resi 62-83
select target_tm3, target and resi 101-126
select target_ecl2, target and resi 165-181
select target_tm5, target and resi 182-201
select target_tm6, target and resi 326-346
select target_tm7, target and resi 358-380
```

### Gpr3 区域

```text
select target_tm2, target and resi 48-68
select target_tm3, target and resi 87-112
select target_ecl2, target and resi 150-168
select target_tm5, target and resi 169-189
select target_tm6, target and resi 295-315
select target_tm7, target and resi 328-349
```

逐区域打印候选残基：

```text
iterate target_pocket_neighbors and target_tm2 and name CA, print("TM2", resn, resi, b)
iterate target_pocket_neighbors and target_tm3 and name CA, print("TM3", resn, resi, b)
iterate target_pocket_neighbors and target_ecl2 and name CA, print("ECL2", resn, resi, b)
iterate target_pocket_neighbors and target_tm5 and name CA, print("TM5", resn, resi, b)
iterate target_pocket_neighbors and target_tm6 and name CA, print("TM6", resn, resi, b)
iterate target_pocket_neighbors and target_tm7 and name CA, print("TM7", resn, resi, b)
```

理想的共同口袋位置应位于胞外侧 TM 束内部，并由 TM2、TM3、TM5、TM6、TM7 中的多个区域共同围绕。ECL2 是否参与可以在 Gpr2、Gpr3 和两个参考受体之间不同。

## 第 6 步：检查菌株差异位点

### Gpr2：7 个 TWF154–ATCC 差异

```text
select strain_variants, target and resi 50+74+184+234+235+277+392
```

### Gpr3：6 个 TWF154–ATCC 差异

```text
select strain_variants, target and resi 72+178+180+228+240+241
```

显示全部差异位点，并筛选靠近参考口袋的位点：

```text
show sticks, strain_variants
color green, strain_variants
select pocket_near_variants, byres (strain_variants within 5 of ref_pocket_all)
iterate pocket_near_variants and name CA, print("POCKET_NEAR_VARIANT", resn, resi, b)
```

若 `pocket_near_variants` 为空，说明没有差异位点进入参考口袋的 5 Å 邻域。位于相同 TM 但超过 5 Å 的差异仍可记录为“同一区域、未直接邻近”。

## 第 7 步：保存结构图

先回到口袋视图：

```text
zoom ref_pocket_all or target_pocket_neighbors, 10
set ray_opaque_background, off
```

根据当前组替换输出文件名。例如 01：

```text
png /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/01_TWF154_Gpr2_vs_GprC/pocket_view.png, width=1800, height=1400, dpi=300, ray=1
```

每组至少保留一张能同时看到参考口袋残基、TWF154 空间邻居和周围 TM 的图。

## 如何分析

### 1. 先判断位置

回答：参考口袋投影到 `target` 后，是否仍位于胞外 TM 束中央？

- 支持：邻居主要来自 TM2、TM3、TM5、TM6、TM7，且位于同一胞外腔体周围；
- 部分支持：位置大致相同，但缺少部分 TM、ECL2 明显偏移或腔体形状改变；
- 不支持：邻居集中于膜外表面、胞内侧，或主要来自 TM1/TM4；
- 置信度不足：关键判断依赖 pLDDT 较低的 loop 或尾部。

### 2. 再判断化学类型

比较空间对应残基的性质，而不是要求氨基酸名称完全相同：

| 类型 | 常见残基 |
|---|---|
| 正电/可质子化 | K、R、H |
| 负电 | D、E |
| 极性不带电 | S、T、N、Q |
| 芳香 | F、Y、W、H |
| 疏水 | A、V、L、I、M，以及芳香疏水侧链 |

重点记录：

- 参考极性或带电位置在 target 中是否仍有可提供相似相互作用的侧链；
- 芳香残基是否仍位于口袋入口或 ECL2；
- target 是否出现明显伸入腔体的大侧链，造成静态空间封闭；
- 结论是否依赖单个侧链旋转方向。

AlphaFold 对主链和整体 TM 位置通常比单一侧链 rotamer 更可靠。单个侧链方向只作为提示。

### 3. 查看结构置信度

`iterate` 输出中的 `b` 是 AlphaFold/ColabFold PDB 的 pLDDT：

| pLDDT | 用法 |
|---:|---|
| ≥90 | 局部主链可信度高 |
| 70–90 | 通常可用于主链位置判断 |
| 50–70 | 结论降级并标注不确定性 |
| <50 | 不据此作精细口袋判断 |

### 4. 合并两个参考受体的证据

对每个 target 分别比较 GprC 和 SRBC-64：

- 两个参考都投影到相同胞外区域，且得到相似的 TM 组成和化学环境：支持共同口袋；
- 两个参考定位一致，但部分残基性质不同：部分支持，并记录差异；
- 两个参考给出明显不同的候选区域：检查局部 TM 对齐、ECL2 和 pLDDT 后再判断；
- 关键区域置信度不足：使用“结构置信度不足，无法判断”。

### 5. 最小记录字段

`pocket_mapping.tsv` 中每个 target 候选残基至少记录：

```text
comparison_id
target_receptor
target_residue
target_region
chemical_class
pLDDT
near_reference_verified_or_provisional
pocket_facing_manual_check
strain_variant
note
```

## 完成条件

每个 Gpr2/Gpr3–参考受体组合都有：

1. 一张口袋叠合图；
2. 一份 `target_pocket_neighbors` 残基列表；
3. TM/ECL2 区域分类；
4. 化学类型和 pLDDT 记录；
5. 菌株差异位点与口袋的空间关系；
6. 支持、部分支持、不支持或结构置信度不足四级判断。
