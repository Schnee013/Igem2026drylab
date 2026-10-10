# 批次06：最低分pose四格接触比较

7个受体×两种配体，共14个最低分pose。核验来源哈希、最低分MODEL、ProLIF 2.1.0参数与IFP/残基表一致性。

D＝ΔS18−ΔS3，单位kcal/mol。每个突变体与本轮WT比较；新增/丢失按原残基编号＋接触类型统计，突变导致的残基名称变化另记。

接触残基数按一个残基有任意类型接触计一次；残基–类型条目单独计数。6 Å为邻域筛选范围。接触数量变化不等同于能量贡献。

本轮为model_0、seed=1919的一次筛选；候选解释需结合pose可视化与追加seed复核。T106S局部结构需重点复核。

| 突变 | ΔS3 | ΔS18 | D | #3残基数 WT→突变 | #18残基数 WT→突变 |
|---|---:|---:|---:|---|---|
| W338L | 0.180 | 0.407 | 0.227 | 11→8 | 12→9 |
| T106S | 0.187 | 0.297 | 0.110 | 11→8 | 12→10 |
| R181K | 0.384 | 0.414 | 0.030 | 11→11 | 12→13 |
| T106V | 0.324 | 0.332 | 0.008 | 11→11 | 12→12 |
| R181Q | 0.439 | 0.410 | -0.029 | 11→11 | 12→9 |
| W338F | 0.293 | 0.118 | -0.175 | 11→10 | 12→11 |

## W338L

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.752 | 1 | 8 | 12 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.62 | 1 | 9 | 16 |

ascr3 新增：ARG181.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；ASN185.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASP24.A:HBDonor；ASP24.A:VdWContact；ASN28.A:HBAcceptor；VAL110.A:Hydrophobic；LYS364.A:HBAcceptor。
ascr18 丢失：LEU31.A:VdWContact；SER80.A:HBDonor；ASN84.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；VAL368.A:VdWContact。

## T106S

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.745 | 1 | 8 | 12 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.73 | 1 | 10 | 19 |

ascr3 新增：PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact。
ascr3 丢失：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；VAL110.A:Hydrophobic；LYS364.A:HBAcceptor。
ascr18 丢失：SER80.A:HBDonor；SER80.A:VdWContact；VAL368.A:VdWContact。

## R181K

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.548 | 1 | 11 | 16 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.613 | 1 | 13 | 19 |

ascr3 新增：ALA81.A:HBAcceptor；ALA81.A:VdWContact。
ascr3 丢失：SER80.A:HBAcceptor；THR106.A:VdWContact。
同编号接触残基名称变化：[{'number': 181, 'wt': 'ARG181.A', 'mutant': 'LYS181.A'}]

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ALA81.A:VdWContact；LYS181.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG345.A:HBAcceptor；ARG345.A:VdWContact。
ascr18 丢失：LEU27.A:VdWContact；ASN28.A:VdWContact；SER80.A:HBDonor；ASN84.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic。

## T106V

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.608 | 1 | 11 | 17 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.695 | 1 | 12 | 16 |

ascr3 新增：ALA81.A:VdWContact；GLN107.A:HBDonor。
ascr3 丢失：VAL368.A:VdWContact。
同编号接触残基名称变化：[{'number': 106, 'wt': 'THR106.A', 'mutant': 'VAL106.A'}]

ascr18 新增：ALA81.A:VdWContact；VAL106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
ascr18 丢失：LEU27.A:VdWContact；ASN28.A:VdWContact；SER80.A:HBDonor；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；VAL368.A:VdWContact。

## R181Q

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.493 | 1 | 11 | 19 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.617 | 1 | 9 | 14 |

ascr3 新增：ASP24.A:HBDonor；ASP24.A:VdWContact；LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ALA81.A:VdWContact；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

ascr18 新增：SER80.A:HBAcceptor；ASN102.A:VdWContact；PHE186.A:Hydrophobic。
ascr18 丢失：LEU27.A:VdWContact；ASN28.A:VdWContact；SER80.A:HBDonor；ASN84.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；VAL368.A:VdWContact。

## W338F

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.932 | 1 | 11 | 16 |
| mutant ascr3 | -6.639 | 1 | 10 | 17 |
| wt ascr18 | -7.027 | 1 | 12 | 19 |
| mutant ascr18 | -6.909 | 1 | 11 | 18 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；LEU90.A:VdWContact；PHE186.A:Hydrophobic；LYS364.A:HBAcceptor。
ascr18 丢失：LEU27.A:VdWContact；SER80.A:HBDonor；SER80.A:VdWContact；TRP338.A:Hydrophobic；VAL368.A:VdWContact。
同编号接触残基名称变化：[{'number': 338, 'wt': 'TRP338.A', 'mutant': 'PHE338.A'}]
