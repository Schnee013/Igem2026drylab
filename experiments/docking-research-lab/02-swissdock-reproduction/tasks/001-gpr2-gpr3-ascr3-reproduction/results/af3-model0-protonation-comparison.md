# AF3 model_0–ascr#3 docking 核对

## 结论

三次 SwissDock AC 作业均通过完成性验收：服务器状态为 `Calculation is finished`、原始 ZIP 无压缩错误，且 `result.dock4` 可解析。Gpr2 去质子化作业确实使用了净电荷 −1 的 ascr#3；它的全局 top pose 接触 Y168，而 Gpr2 中性作业的全局 top pose 距 Y168 很远。

建议补跑 **Gpr3 AF3 model_0–去质子化 ascr#3（pH 7）**。这是当前最小的补充作业，用于判断配体电荷对 Gpr3 优先结合区域的影响。

## 作业验收

| 作业 | Session | 服务器状态 | 实际拓扑 | Poses / clusters | Top AC | Top SP-dG |
|---|---:|---|---|---:|---:|---:|
| Gpr2 AF3 model_0 + 中性 ascr#3 | 96443616 | finished | 0，含羧基 O–H | 69 / 50 | −6.714069 | −6.8236 |
| Gpr2 AF3 model_0 + 去质子化 ascr#3 | 93592351 | finished | −1，无羧基 O–H | 87 / 50 | −17.020316 | −6.4959 |
| Gpr3 AF3 model_0 + 中性 ascr#3 | 32488314 | finished | 0，含羧基 O–H | 121 / 50 | −15.911252 | −7.1991 |

去质子化 Gpr2 作业的拓扑证据：

- `files/extra.rtf`: `RESI LIG1 -1.000`；
- 所有部分电荷之和为 −1.0000；
- 羧基使用 `CO2M/O2CM` 原子类型；
- 配体比中性作业少 1 个氢，且没有羧基 O–H 键；
- `result.dock4` 中每个 pose 均含 46 个配体原子，与该拓扑一致。

## Gpr2 中性与去质子化结果

| 指标 | 中性 | 去质子化 | 解读 |
|---|---:|---:|---|
| 全局 top pose 至 Y168 最短距离 | 29.830 Å | 2.989 Å | 去质子化 top pose 复现 Y168 位置锚点 |
| 接触 Y168 的 cluster leaders | 14/50 | 18/50 | 两种状态都能到达该区域，去质子化更常见 |
| 接触 Y168 的最佳 cluster rank | 2 | 1 | 电荷改变了 AC 的区域排序 |
| Top AC | −6.714069 | −17.020316 | 跨电荷状态不作定量亲和力差值解读 |
| Top-pose SP-dG | −6.8236 | −6.4959 | 去质子化 top pose 未显示更优 SP-dG |
| 全体 poses 中最优 SP-dG | −7.2327 | −7.1551 | 数值接近，中性略优 0.0776 kcal/mol |

Gpr2 两个作业的 prepared receptor 原子坐标完全相同（6400 atoms，RMSD 0 Å），搜索盒和 AC 参数也相同。可观察差异主要来自配体质子化状态及随机采样。

两种状态各自 SP-dG 最优的 pose 分别距 Y168 32.20 Å 和 31.77 Å。这两个 pose 只支持全局 SP-dG 排名，不支持 Y168 位置复现。

中性作业并非没有文献区域 pose：其第 2 名 cluster leader 距 Y168 3.775 Å，与去质子化 top pose 的配体质心相距约 2.94 Å。因此，去质子化的主要效果是将已可采样的 Y168 区域提升到 AC 首位，而非创造一个中性配体无法到达的新口袋。

## 是否补跑 Gpr3 去质子化作业

值得，理由为：

1. pH 7 去质子化流程已由 Gpr2 的 −1 拓扑验证；
2. Gpr2 显示电荷能改变全蛋白搜索中的优先结合区域；
3. Gpr3 中性作业的前 10 个 cluster leaders 接触残基高度重复，已形成可比较的稳定基线；
4. 只需新增 1 个作业即可完成受体间的质子化效应对照。

该补充作业允许判断 pose 区域、cluster 重复性和排名变化。结合强弱结论还需要更高重复数、统一重打分或实验证据。

## 归档位置

- Gpr2 中性：`runs/gpr2-ascr3/swissdock-af3-model0-neutral-96443616/`
- Gpr2 去质子化：`runs/gpr2-ascr3/swissdock-af3-model0-deprot-ph7-93592351/`
- Gpr3 中性：`runs/gpr3-ascr3/swissdock-af3-model0-neutral-32488314/`

每个目录均保留原始 ZIP、CLI 回执、`parameters`、`files/` 和 `result.dock4`。
