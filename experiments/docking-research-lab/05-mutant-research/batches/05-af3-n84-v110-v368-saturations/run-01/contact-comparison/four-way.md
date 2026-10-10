# 批次05：最低分pose四格接触比较

58个受体×两种配体，共116个最低分pose。核验来源哈希、最低分MODEL、ProLIF 2.1.0参数与IFP/残基表一致性。

D＝ΔS18−ΔS3，单位kcal/mol。每个突变体与本轮WT比较；新增/丢失按原残基编号＋接触类型统计，突变导致的残基名称变化另记。

接触残基数按一个残基有任意类型接触计一次；残基–类型条目单独计数。6 Å为邻域筛选范围。接触数量变化不等同于能量贡献。

本轮为model_0、seed=1919的一次筛选；候选解释需结合pose可视化与追加seed复核。V368L/P/K局部结构可视化尚待用户确认。

| 突变 | ΔS3 | ΔS18 | D | #3残基数 WT→突变 | #18残基数 WT→突变 |
|---|---:|---:|---:|---|---|
| V368R | -0.388 | 0.199 | 0.587 | 8→8 | 11→9 |
| V110M | -0.004 | 0.426 | 0.430 | 8→11 | 11→11 |
| V110R | -0.009 | 0.405 | 0.414 | 8→11 | 11→12 |
| N84Y | -0.281 | 0.110 | 0.391 | 8→9 | 11→9 |
| V110P | -0.384 | -0.050 | 0.334 | 8→13 | 11→12 |
| V368Q | -0.108 | 0.208 | 0.316 | 8→11 | 11→12 |
| V110K | -0.114 | 0.174 | 0.288 | 8→9 | 11→11 |
| N84L | -0.440 | -0.175 | 0.265 | 8→14 | 11→12 |
| V110G | -0.330 | -0.113 | 0.217 | 8→10 | 11→10 |
| V368P | 0.307 | 0.516 | 0.209 | 8→8 | 11→9 |
| V110F | -0.261 | -0.100 | 0.161 | 8→9 | 11→14 |
| V368W | 0.124 | 0.277 | 0.153 | 8→10 | 11→13 |
| V110Q | -0.609 | -0.471 | 0.138 | 8→11 | 11→14 |
| V368H | 0.219 | 0.343 | 0.124 | 8→10 | 11→10 |
| V110N | -0.090 | 0.001 | 0.091 | 8→9 | 11→13 |
| V368A | -0.645 | -0.554 | 0.091 | 8→10 | 11→11 |
| V368L | 0.048 | 0.136 | 0.088 | 8→11 | 11→11 |
| V110T | -0.318 | -0.259 | 0.059 | 8→12 | 11→12 |
| N84A | 0.025 | 0.083 | 0.058 | 8→8 | 11→11 |
| V368C | -0.086 | -0.030 | 0.056 | 8→9 | 11→11 |
| V368F | -0.120 | -0.067 | 0.053 | 8→11 | 11→11 |
| N84C | -0.026 | 0.026 | 0.052 | 8→8 | 11→10 |
| V368E | -0.171 | -0.168 | 0.003 | 8→11 | 11→12 |
| V110A | -0.012 | -0.016 | -0.004 | 8→10 | 11→11 |
| V368N | -0.656 | -0.660 | -0.004 | 8→11 | 11→11 |
| N84K | 0.119 | 0.101 | -0.018 | 8→9 | 11→9 |
| V110L | 0.151 | 0.130 | -0.021 | 8→9 | 11→11 |
| N84G | -0.267 | -0.305 | -0.038 | 8→13 | 11→12 |
| N84P | -0.215 | -0.263 | -0.048 | 8→13 | 11→13 |
| V368T | -0.100 | -0.152 | -0.052 | 8→9 | 11→12 |
| V110Y | -0.007 | -0.063 | -0.056 | 8→9 | 11→11 |
| V368S | -0.347 | -0.415 | -0.068 | 8→11 | 11→14 |
| N84F | 0.096 | 0.016 | -0.080 | 8→10 | 11→13 |
| N84Q | -0.263 | -0.343 | -0.080 | 8→12 | 11→13 |
| N84R | -0.087 | -0.191 | -0.104 | 8→13 | 11→11 |
| V368M | 0.197 | 0.091 | -0.106 | 8→10 | 11→11 |
| N84D | -0.321 | -0.433 | -0.112 | 8→10 | 11→11 |
| V110H | -0.136 | -0.252 | -0.116 | 8→7 | 11→11 |
| N84M | -0.021 | -0.142 | -0.121 | 8→9 | 11→11 |
| N84I | -0.045 | -0.171 | -0.126 | 8→9 | 11→11 |
| V368K | 0.151 | 0.012 | -0.139 | 8→10 | 11→12 |
| V368D | -0.405 | -0.556 | -0.151 | 8→9 | 11→9 |
| V368Y | 0.155 | -0.014 | -0.169 | 8→14 | 11→12 |
| V368G | 0.241 | 0.056 | -0.185 | 8→9 | 11→11 |
| V368I | -0.180 | -0.411 | -0.231 | 8→11 | 11→11 |
| V110E | -0.249 | -0.485 | -0.236 | 8→8 | 11→11 |
| N84S | -0.174 | -0.451 | -0.277 | 8→9 | 11→11 |
| N84E | -0.050 | -0.342 | -0.292 | 8→12 | 11→12 |
| V110I | 0.050 | -0.254 | -0.304 | 8→11 | 11→10 |
| V110W | 0.163 | -0.163 | -0.326 | 8→10 | 11→9 |
| N84W | 0.116 | -0.212 | -0.328 | 8→9 | 11→12 |
| N84H | 0.029 | -0.307 | -0.336 | 8→8 | 11→13 |
| V110D | -0.133 | -0.472 | -0.339 | 8→8 | 11→12 |
| N84T | 0.116 | -0.227 | -0.343 | 8→10 | 11→8 |
| V110S | -0.103 | -0.464 | -0.361 | 8→11 | 11→11 |
| V110C | -0.094 | -0.561 | -0.467 | 8→10 | 11→10 |
| N84V | 0.361 | -0.364 | -0.725 | 8→7 | 11→13 |

## V368R

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.013 | 1 | 8 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.293 | 1 | 9 | 16 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；ASN84.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；ARG368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110M

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.629 | 1 | 11 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.066 | 1 | 11 | 16 |

ascr3 新增：LEU31.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact。
ascr3 丢失：无。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'MET110.A'}]

ascr18 新增：LEU31.A:Hydrophobic；ASN84.A:VdWContact；ASN102.A:VdWContact；GLY103.A:VdWContact；THR106.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110R

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.634 | 1 | 11 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.087 | 1 | 12 | 19 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:HBDonor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；LYS364.A:VdWContact；ILE367.A:Hydrophobic。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'ARG110.A'}]

ascr18 新增：ASP24.A:HBDonor；ASP24.A:VdWContact；LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；ASN84.A:VdWContact；LEU90.A:VdWContact；LYS364.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## N84Y

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.906 | 1 | 9 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.382 | 1 | 9 | 15 |

ascr3 新增：LEU31.A:VdWContact；SER80.A:HBAcceptor；ARG181.A:HBAcceptor。
ascr3 丢失：无。

ascr18 新增：LEU31.A:Hydrophobic；ASN102.A:HBDonor；ASN102.A:VdWContact；GLY103.A:VdWContact；THR106.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110P

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.009 | 1 | 13 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.542 | 1 | 12 | 15 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；ARG189.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'PRO110.A'}]

ascr18 新增：VAL368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'PRO110.A'}]

## V368Q

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.733 | 1 | 11 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.284 | 1 | 12 | 20 |

ascr3 新增：LEU31.A:VdWContact；ALA81.A:HBAcceptor；ALA81.A:VdWContact；ARG181.A:HBAcceptor；GLN368.A:Hydrophobic；GLN368.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；GLN368.A:Hydrophobic；GLN368.A:VdWContact。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110K

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.739 | 1 | 9 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.318 | 1 | 11 | 18 |

ascr3 新增：ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact；SER80.A:VdWContact；THR106.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'LYS110.A'}]

ascr18 新增：ASP24.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU90.A:VdWContact；LYS110.A:Anionic；LYS110.A:HBAcceptor；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：PHE77.A:VdWContact；SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'LYS110.A'}]

## N84L

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.065 | 1 | 14 | 20 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.667 | 1 | 12 | 22 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ARG181.A:HBAcceptor；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；LEU84.A:VdWContact；ASN102.A:HBDonor；ASN102.A:VdWContact；ARG181.A:Anionic；ARG181.A:HBAcceptor；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact。

## V110G

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.955 | 1 | 10 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.605 | 1 | 10 | 13 |

ascr3 新增：GLN107.A:HBDonor；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；MET73.A:VdWContact；ARG189.A:VdWContact；TRP338.A:VdWContact。
ascr18 丢失：PHE77.A:VdWContact；ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'GLY110.A'}]

## V368P

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.318 | 1 | 8 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -5.976 | 1 | 9 | 12 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；PHE186.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact；ILE367.A:VdWContact。

## V110F

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.886 | 1 | 9 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.592 | 1 | 14 | 19 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；LEU31.A:VdWContact；ASN84.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；PHE186.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'PHE110.A'}]

## V368W

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.501 | 1 | 10 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.215 | 1 | 13 | 20 |

ascr3 新增：ASN28.A:HBDonor；ASN28.A:VdWContact；LEU90.A:VdWContact；VAL110.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；GLN107.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic；ILE367.A:Hydrophobic。

ascr18 新增：ASP24.A:VdWContact；LEU27.A:VdWContact；ASN28.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；ASN84.A:VdWContact；ASN102.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP368.A:Hydrophobic；TRP368.A:VdWContact。
ascr18 丢失：LEU31.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact；LYS364.A:Hydrophobic；LYS364.A:VdWContact。

## V110Q

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.234 | 1 | 11 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.963 | 1 | 14 | 20 |

ascr3 新增：SER80.A:HBAcceptor；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'GLN110.A'}]

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor；GLN107.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'GLN110.A'}]

## V368H

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.406 | 1 | 10 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.149 | 1 | 10 | 14 |

ascr3 新增：LEU31.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；ALA81.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；HIS368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic。

ascr18 新增：SER80.A:HBAcceptor；PHE186.A:Hydrophobic；PHE186.A:VdWContact；TRP338.A:Hydrophobic；HIS368.A:HBAcceptor；HIS368.A:VdWContact。
ascr18 丢失：LEU31.A:VdWContact；PHE77.A:Hydrophobic；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ILE367.A:Hydrophobic。

## V110N

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.715 | 1 | 9 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.491 | 1 | 13 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；ASN185.A:HBDonor；ASN185.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ASN84.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：PHE77.A:VdWContact；GLN107.A:HBDonor。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'ASN110.A'}]

## V368A

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.27 | 1 | 10 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -7.046 | 1 | 11 | 16 |

ascr3 新增：LEU31.A:VdWContact；SER80.A:HBAcceptor；ASN185.A:VdWContact；ALA368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ARG181.A:HBAcceptor；ALA368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor；ASN185.A:VdWContact。

## V368L

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.577 | 1 | 11 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.356 | 1 | 11 | 18 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；LEU368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；VAL110.A:VdWContact；LYS364.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ARG181.A:HBAcceptor；LEU368.A:Hydrophobic；LEU368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor；ASN185.A:VdWContact。

## V110T

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.943 | 1 | 12 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.751 | 1 | 12 | 18 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；GLN107.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'THR110.A'}]

ascr18 新增：ALA81.A:HBAcceptor；ARG181.A:HBAcceptor；PHE186.A:VdWContact；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'THR110.A'}]

## N84A

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.6 | 1 | 8 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.409 | 1 | 11 | 17 |

ascr3 新增：ASN28.A:VdWContact；LEU31.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；THR106.A:HBDonor；VAL110.A:Hydrophobic；ARG189.A:Anionic；TRP338.A:Hydrophobic；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V368C

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.711 | 1 | 9 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.522 | 1 | 11 | 21 |

ascr3 新增：SER80.A:HBAcceptor；GLN107.A:HBDonor；CYS368.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG181.A:HBAcceptor；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；CYS368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## V368F

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.745 | 1 | 11 | 19 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.559 | 1 | 11 | 19 |

ascr3 新增：ASN28.A:HBDonor；ASN28.A:VdWContact；LEU31.A:VdWContact；SER80.A:HBAcceptor；SER80.A:HBDonor；ALA81.A:VdWContact；VAL110.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；PHE368.A:Hydrophobic；PHE368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；ARG181.A:VdWContact；LYS364.A:Hydrophobic；LYS364.A:VdWContact；ILE367.A:Hydrophobic。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；PHE368.A:Hydrophobic；PHE368.A:VdWContact。
ascr18 丢失：LEU31.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact；LYS364.A:Hydrophobic。

## N84C

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.651 | 1 | 8 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.466 | 1 | 10 | 13 |

ascr3 新增：ASN28.A:VdWContact；LEU31.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；LEU90.A:VdWContact；TRP338.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact。

## V368E

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.796 | 1 | 11 | 19 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.66 | 1 | 12 | 19 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor；GLU368.A:Hydrophobic；GLU368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：VAL110.A:Hydrophobic；ARG181.A:Hydrophobic；ASN185.A:Hydrophobic；PHE186.A:Hydrophobic；TRP338.A:Hydrophobic；TRP338.A:VdWContact；GLU368.A:HBDonor；GLU368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ILE367.A:Hydrophobic。

## V110A

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.637 | 1 | 10 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.508 | 1 | 11 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；GLN107.A:HBDonor；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Hydrophobic；ARG189.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact。

## V368N

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.281 | 1 | 11 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -7.152 | 1 | 11 | 19 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ARG181.A:HBAcceptor；ASN185.A:VdWContact；ASN368.A:Hydrophobic；ASN368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；ASN368.A:Hydrophobic。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## N84K

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.506 | 1 | 9 | 18 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.391 | 1 | 9 | 15 |

ascr3 新增：LEU31.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；ALA81.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；LYS364.A:HBAcceptor。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：LEU27.A:VdWContact；ASN28.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## V110L

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.474 | 1 | 9 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.362 | 1 | 11 | 15 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ARG181.A:HBAcceptor；VAL368.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact；SER80.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'LEU110.A'}]

ascr18 新增：ARG181.A:HBAcceptor。
ascr18 丢失：GLN107.A:HBDonor。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'LEU110.A'}]

## N84G

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.892 | 1 | 13 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.797 | 1 | 12 | 19 |

ascr3 新增：LEU31.A:VdWContact；ALA81.A:HBAcceptor；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；TRP338.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；ASN102.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## N84P

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.84 | 1 | 13 | 18 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.755 | 1 | 13 | 20 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG345.A:HBAcceptor；ARG345.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：SER80.A:HBAcceptor；ASN102.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；ARG345.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact。

## V368T

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.725 | 1 | 9 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.644 | 1 | 12 | 17 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；THR368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110Y

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.632 | 1 | 9 | 12 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.555 | 1 | 11 | 18 |

ascr3 新增：GLN107.A:HBDonor；ASN185.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'TYR110.A'}]

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；TYR110.A:Hydrophobic；ARG181.A:Anionic；ARG181.A:HBAcceptor；PHE186.A:VdWContact；ARG345.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：SER80.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'TYR110.A'}]

## V368S

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.972 | 1 | 11 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.907 | 1 | 14 | 21 |

ascr3 新增：LEU31.A:Hydrophobic；ALA81.A:VdWContact；GLN107.A:HBDonor；SER368.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；ASN102.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；SER368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact。

## N84F

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.529 | 1 | 10 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.476 | 1 | 13 | 21 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：LYS364.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；SER80.A:HBDonor；ASN102.A:VdWContact；ARG181.A:Anionic；ARG181.A:Hydrophobic；PHE186.A:Hydrophobic；PHE186.A:VdWContact；TRP338.A:Hydrophobic；ARG345.A:Anionic；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact。

## N84Q

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.888 | 1 | 12 | 18 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.835 | 1 | 13 | 20 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；SER80.A:HBAcceptor；ALA81.A:VdWContact；ASN185.A:HBDonor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：ASP24.A:VdWContact；LEU27.A:VdWContact；ASN28.A:HBDonor；ASN28.A:VdWContact；GLN84.A:HBAcceptor；GLN84.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic。
ascr18 丢失：LEU31.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## N84R

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.712 | 1 | 13 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.683 | 1 | 11 | 19 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；ARG189.A:VdWContact；ARG345.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；SER80.A:HBDonor；ASN102.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V368M

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.428 | 1 | 10 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.401 | 1 | 11 | 21 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor；MET368.A:Hydrophobic。
ascr3 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：SER80.A:HBDonor；VAL110.A:Hydrophobic；ARG181.A:Anionic；ARG181.A:Hydrophobic；PHE186.A:Hydrophobic；PHE186.A:VdWContact；TRP338.A:Hydrophobic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact；LYS364.A:Hydrophobic。

## N84D

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.946 | 1 | 10 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.925 | 1 | 11 | 16 |

ascr3 新增：LEU31.A:Hydrophobic；SER80.A:HBAcceptor；ASN185.A:HBDonor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ALA81.A:HBAcceptor；ARG181.A:HBAcceptor。
ascr18 丢失：GLN107.A:HBDonor。

## V110H

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.761 | 1 | 7 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.744 | 1 | 11 | 17 |

ascr3 新增：ARG181.A:HBAcceptor。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ARG181.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：GLN107.A:HBDonor；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'HIS110.A'}]

## N84M

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.646 | 1 | 9 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.634 | 1 | 11 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；ASN102.A:VdWContact；ARG181.A:Hydrophobic；PHE186.A:Hydrophobic；ARG189.A:Anionic；TRP338.A:Hydrophobic；TRP338.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## N84I

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.67 | 1 | 9 | 12 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.663 | 1 | 11 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；VAL110.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V368K

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.474 | 1 | 10 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.48 | 1 | 12 | 20 |

ascr3 新增：ASN185.A:HBDonor；ASN185.A:VdWContact；LYS368.A:Anionic；LYS368.A:HBAcceptor；LYS368.A:VdWContact。
ascr3 丢失：无。

ascr18 新增：ASN28.A:VdWContact；ASN84.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；LYS368.A:HBAcceptor；LYS368.A:Hydrophobic；LYS368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V368D

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -7.03 | 1 | 9 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -7.048 | 1 | 9 | 17 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:Hydrophobic；LEU31.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；ASP368.A:Hydrophobic；ASP368.A:VdWContact。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ILE367.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ASN102.A:HBDonor；ASN102.A:VdWContact；GLY103.A:VdWContact；THR106.A:HBAcceptor；ASP368.A:Hydrophobic；ASP368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V368Y

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.47 | 1 | 14 | 20 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.506 | 1 | 12 | 19 |

ascr3 新增：ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；PHE186.A:VdWContact；ARG345.A:Anionic；ARG345.A:VdWContact；TYR368.A:HBAcceptor；TYR368.A:Hydrophobic；TYR368.A:VdWContact。
ascr3 丢失：GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；PHE186.A:Hydrophobic；PHE186.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；ARG345.A:Anionic；TYR368.A:HBAcceptor；TYR368.A:Hydrophobic；TYR368.A:VdWContact。
ascr18 丢失：LEU31.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ASN185.A:VdWContact；LYS364.A:Hydrophobic。

## V368G

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.384 | 1 | 9 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.436 | 1 | 11 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ASN185.A:HBDonor；ASN185.A:VdWContact；LYS364.A:Anionic。
ascr3 丢失：SER80.A:VdWContact。

ascr18 新增：LEU31.A:Hydrophobic；ALA81.A:HBAcceptor；ASN185.A:HBDonor。
ascr18 丢失：GLN107.A:HBDonor。

## V368I

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.805 | 1 | 11 | 21 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.903 | 1 | 11 | 20 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:HBDonor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；ILE368.A:Hydrophobic；ILE368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor；ILE368.A:Hydrophobic；ILE368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## V110E

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.874 | 1 | 8 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.977 | 1 | 11 | 18 |

ascr3 新增：ASN185.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN102.A:VdWContact；GLU110.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'GLU110.A'}]

## N84S

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.799 | 1 | 9 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.943 | 1 | 11 | 15 |

ascr3 新增：SER80.A:HBAcceptor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN28.A:HBDonor；ASN28.A:VdWContact；SER84.A:VdWContact；ARG189.A:Anionic；TRP338.A:Hydrophobic；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## N84E

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.675 | 1 | 12 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.834 | 1 | 12 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：PHE77.A:VdWContact；THR106.A:VdWContact；GLN107.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBAcceptor；ASN102.A:VdWContact；ASN185.A:Hydrophobic；PHE186.A:Hydrophobic；TRP338.A:Hydrophobic；TRP338.A:VdWContact。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110I

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.575 | 1 | 11 | 17 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.746 | 1 | 10 | 16 |

ascr3 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU31.A:VdWContact；ALA81.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor；VAL368.A:VdWContact。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：SER80.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110W

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.462 | 1 | 10 | 14 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.655 | 1 | 9 | 15 |

ascr3 新增：LEU31.A:VdWContact；ARG181.A:HBAcceptor；ASN185.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：THR106.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'TRP110.A'}]

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；TRP110.A:Hydrophobic；ARG181.A:Anionic；ARG345.A:Anionic；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：LEU31.A:VdWContact；SER80.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'TRP110.A'}]

## N84W

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.509 | 1 | 9 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.704 | 1 | 12 | 22 |

ascr3 新增：LEU31.A:VdWContact；VAL368.A:VdWContact。
ascr3 丢失：SER80.A:VdWContact；ILE367.A:VdWContact。

ascr18 新增：ASP24.A:HBDonor；ASP24.A:VdWContact；LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:HBAcceptor；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## N84H

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.596 | 1 | 8 | 13 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.799 | 1 | 13 | 21 |

ascr3 新增：ASN28.A:VdWContact；LEU31.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:VdWContact；LYS364.A:Anionic。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

ascr18 新增：ASP24.A:VdWContact；ASN28.A:VdWContact；SER80.A:HBDonor；ALA81.A:HBAcceptor；LEU90.A:VdWContact；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；VAL368.A:VdWContact。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110D

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.758 | 1 | 8 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.964 | 1 | 12 | 21 |

ascr3 新增：LEU31.A:VdWContact；TRP338.A:VdWContact。
ascr3 丢失：THR106.A:VdWContact；GLN107.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'ASP110.A'}]

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；LEU90.A:VdWContact；ARG181.A:Anionic；ARG345.A:Anionic；ARG345.A:HBAcceptor；ARG345.A:VdWContact；LYS364.A:Anionic；LYS364.A:HBAcceptor。
ascr18 丢失：THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ASN185.A:VdWContact。

## N84T

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.509 | 1 | 10 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.719 | 1 | 8 | 12 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；GLN107.A:HBDonor；VAL368.A:VdWContact。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：ASN28.A:VdWContact；SER80.A:HBDonor；ARG189.A:Anionic；TRP338.A:Hydrophobic。
ascr18 丢失：ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。

## V110S

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.728 | 1 | 11 | 15 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.956 | 1 | 11 | 18 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；ALA81.A:VdWContact；ASN185.A:VdWContact；PHE186.A:VdWContact；TRP338.A:VdWContact。
ascr3 丢失：THR106.A:VdWContact；VAL110.A:VdWContact。

ascr18 新增：ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；LYS364.A:HBAcceptor；VAL368.A:VdWContact。
ascr18 丢失：SER80.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；VAL110.A:VdWContact；ARG181.A:VdWContact。

## V110C

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.719 | 1 | 10 | 16 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -7.053 | 1 | 10 | 17 |

ascr3 新增：LEU31.A:Hydrophobic；LEU31.A:VdWContact；GLN107.A:HBDonor；ARG181.A:HBAcceptor；ASN185.A:VdWContact。
ascr3 丢失：无。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'CYS110.A'}]

ascr18 新增：LEU27.A:VdWContact；ASN28.A:HBAcceptor；ASN28.A:VdWContact；ASN84.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:VdWContact；TRP338.A:Hydrophobic；TRP338.A:VdWContact；LYS364.A:HBAcceptor。
ascr18 丢失：LEU31.A:VdWContact；SER80.A:VdWContact；ALA81.A:VdWContact；THR106.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
同编号接触残基名称变化：[{'number': 110, 'wt': 'VAL110.A', 'mutant': 'CYS110.A'}]

## N84V

| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |
|---|---:|---:|---:|---:|
| wt ascr3 | -6.625 | 1 | 8 | 11 |
| mutant ascr3 | -6.264 | 1 | 7 | 11 |
| wt ascr18 | -6.492 | 1 | 11 | 15 |
| mutant ascr18 | -6.856 | 1 | 13 | 18 |

ascr3 新增：ARG181.A:HBAcceptor。
ascr3 丢失：VAL110.A:VdWContact。

ascr18 新增：LEU90.A:VdWContact；ASN102.A:VdWContact；PHE186.A:Hydrophobic；ARG189.A:Anionic；ARG189.A:HBAcceptor；ARG189.A:VdWContact；TRP338.A:Hydrophobic；VAL368.A:VdWContact。
ascr18 丢失：ALA81.A:VdWContact；GLN107.A:HBDonor；GLN107.A:VdWContact；ARG181.A:VdWContact；ASN185.A:VdWContact。
