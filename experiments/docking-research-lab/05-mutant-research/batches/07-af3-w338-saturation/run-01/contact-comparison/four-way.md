# 批次07：最低分pose四格接触比较

20个受体×两种配体，共40个最低分pose。核验来源哈希、最低分MODEL、ProLIF 2.1.0参数与IFP/残基表一致性。

D＝ΔS18−ΔS3，单位kcal/mol。每个突变体与本轮WT比较；新增/丢失按原残基编号＋接触类型统计，突变导致的残基名称变化另记。

接触残基数按一个残基有任意类型接触计一次；残基–类型条目单独计数。6 Å为邻域筛选范围。接触数量变化不等同于能量贡献。

AF受体模型：W338C使用AF model_1（结构质量例外）；其余使用model_0。 AF模型编号与Vina pose MODEL分别记录。
本轮为seed=1919的一次筛选；候选W338替换的局部结构需结合可视化检查。

| 突变 | ΔS3 | ΔS18 | D | #3残基数 WT→突变 | #18残基数 WT→突变 |
|---|---:|---:|---:|---|---|
| W338G | -0.218 | 0.121 | 0.339 | 10→8 | 12→10 |
| W338Y | -0.046 | 0.275 | 0.321 | 10→8 | 12→9 |
| W338Q | -0.250 | -0.010 | 0.240 | 10→10 | 12→10 |
| W338E | -0.235 | -0.009 | 0.226 | 10→10 | 12→12 |
| W338R | -0.344 | -0.124 | 0.220 | 10→10 | 12→10 |
| W338S | -0.274 | -0.063 | 0.211 | 10→9 | 12→9 |
| W338P | -0.328 | -0.120 | 0.208 | 10→13 | 12→8 |
| W338T | -0.106 | 0.071 | 0.177 | 10→6 | 12→9 |
| W338K | -0.231 | -0.073 | 0.158 | 10→12 | 12→11 |
| W338V | -0.171 | -0.046 | 0.125 | 10→9 | 12→9 |
| W338D | -0.112 | -0.047 | 0.065 | 10→11 | 12→11 |
| W338N | -0.117 | -0.070 | 0.047 | 10→7 | 12→10 |
| W338C | -0.097 | -0.101 | -0.004 | 10→10 | 12→9 |
| W338I | -0.064 | -0.094 | -0.030 | 10→9 | 12→13 |
| W338A | 0.023 | -0.125 | -0.148 | 10→8 | 12→12 |
| W338M | 0.012 | -0.210 | -0.222 | 10→13 | 12→14 |
| W338F | -0.004 | -0.252 | -0.248 | 10→12 | 12→12 |
| W338H | -0.213 | -0.498 | -0.285 | 10→9 | 12→10 |
| W338L | -0.301 | -0.826 | -0.525 | 10→11 | 12→13 |

## W338G

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.769 | 1 | 8 | 14 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.399 | 1 | 10 | 14 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；THR106.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact。

## W338Y

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.597 | 1 | 8 | 13 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.245 | 1 | 9 | 13 |

ascr3 新增：ARG181.A:HBAcceptor；ASN185.A:HBDonor；ASN185.A:VdWContact。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；VAL110.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；PHE77.A:VdWContact；SER80.A:VdWContact；ASN84.A:VdWContact；ARG345.A:Anionic；LYS364.A:Anionic。

## W338Q

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.801 | 1 | 10 | 15 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.53 | 1 | 10 | 17 |

ascr3 新增：ALA81.A:VdWContact；ARG181.A:HBAcceptor。
ascr3 丢失：SER80.A:HBAcceptor；VAL110.A:VdWContact。

ascr18 新增：THR106.A:VdWContact；VAL110.A:VdWContact；ARG181.A:Hydrophobic；ARG181.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338E

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.786 | 1 | 10 | 18 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.529 | 1 | 12 | 15 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:HBAcceptor；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；THR106.A:VdWContact；VAL110.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338R

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.895 | 1 | 10 | 15 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.644 | 1 | 10 | 14 |

ascr3 新增：ASN28.A:VdWContact；ALA81.A:VdWContact；VAL110.A:Hydrophobic；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:VdWContact；ARG338.A:Anionic；ARG338.A:VdWContact；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；PHE77.A:VdWContact；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic；VAL368.A:VdWContact。

ascr18 新增：THR106.A:VdWContact；VAL110.A:Hydrophobic；VAL110.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338S

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.825 | 1 | 9 | 14 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.583 | 1 | 9 | 17 |

ascr3 新增：ARG181.A:HBAcceptor。
ascr3 丢失：SER80.A:HBAcceptor；VAL110.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBDonor；ARG181.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；SER80.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact。

## W338P

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.879 | 1 | 13 | 22 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.64 | 1 | 8 | 13 |

ascr3 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：SER80.A:HBAcceptor；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；VAL110.A:Hydrophobic；VAL110.A:VdWContact；ARG189.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；PHE77.A:VdWContact；SER80.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338T

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.657 | 1 | 6 | 12 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.449 | 1 | 9 | 13 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ILE367.A:Hydrophobic；ILE367.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；THR106.A:VdWContact；VAL110.A:Hydrophobic；VAL110.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG345.A:Anionic；LYS364.A:Anionic。

## W338K

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.782 | 1 | 12 | 16 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.593 | 1 | 11 | 20 |

ascr3 新增：ALA81.A:VdWContact；PHE186.A:VdWContact。
ascr3 丢失：SER80.A:HBAcceptor。

ascr18 新增：ASN28.A:HBDonor；LEU31.A:Hydrophobic；VAL110.A:Hydrophobic；VAL110.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338V

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.722 | 1 | 9 | 15 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.566 | 1 | 9 | 15 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ILE367.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact。

## W338D

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.663 | 1 | 11 | 15 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.567 | 1 | 11 | 18 |

ascr3 新增：ASN28.A:VdWContact；ALA81.A:VdWContact；VAL110.A:Hydrophobic；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:VdWContact。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；GLN107.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic；VAL368.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；ARG181.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：SER80.A:VdWContact；ASN84.A:VdWContact。

## W338N

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.668 | 1 | 7 | 12 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.59 | 1 | 10 | 17 |

ascr3 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ILE367.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：ASN28.A:HBDonor；ALA81.A:HBAcceptor；VAL110.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338C

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.648 | 1 | 10 | 16 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.621 | 1 | 9 | 16 |

ascr3 新增：ASN102.A:VdWContact；ARG181.A:Anionic；ARG181.A:HBAcceptor；ARG345.A:Anionic；LYS364.A:Anionic。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：ARG181.A:VdWContact；LYS364.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；SER80.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact。

## W338I

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.615 | 1 | 9 | 14 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.614 | 1 | 13 | 18 |

ascr3 新增：ALA81.A:HBAcceptor；ALA81.A:VdWContact；GLN107.A:HBDonor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；VAL110.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；THR106.A:VdWContact；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:HBDonor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338A

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.528 | 1 | 8 | 13 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.645 | 1 | 12 | 17 |

ascr3 新增：ARG181.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；LEU31.A:VdWContact；VAL368.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:HBAcceptor；ARG181.A:VdWContact；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338M

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.539 | 1 | 13 | 17 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.73 | 1 | 14 | 22 |

ascr3 新增：ALA81.A:HBAcceptor；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor。

ascr18 新增：LEU27.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；THR106.A:VdWContact；VAL110.A:Hydrophobic；VAL110.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338F

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.555 | 1 | 12 | 19 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -6.772 | 1 | 12 | 19 |

ascr3 新增：ASN28.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；ALA81.A:VdWContact；VAL110.A:Hydrophobic；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:VdWContact；PHE338.A:VdWContact；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；GLN107.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic；VAL368.A:VdWContact。

ascr18 新增：SER80.A:HBAcceptor；SER80.A:HBDonor；ASN102.A:VdWContact；THR106.A:VdWContact；VAL110.A:VdWContact；PHE186.A:Hydrophobic；PHE186.A:VdWContact；ARG189.A:Anionic；ARG189.A:VdWContact；PHE338.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；LEU31.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338H

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.764 | 1 | 9 | 17 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -7.018 | 1 | 10 | 16 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；ARG181.A:Anionic；ARG181.A:HBAcceptor；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：VAL110.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；SER80.A:VdWContact；ALA81.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。

## W338L

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.551 | 1 | 10 | 15 |
| mutant ascr3 | -6.852 | 1 | 11 | 16 |
| wt ascr18 | -6.52 | 1 | 12 | 17 |
| mutant ascr18 | -7.346 | 1 | 13 | 18 |

ascr3 新增：ALA81.A:VdWContact；ARG181.A:HBAcceptor；ASN185.A:VdWContact；ARG189.A:VdWContact；ARG345.A:VdWContact。
ascr3 丢失：SER80.A:HBAcceptor；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:VdWContact；ARG345.A:HBAcceptor；ARG345.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic。
