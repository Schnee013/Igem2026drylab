# Gpr2突变研究

这部分是本次交付的重点：从早期组合和结构路线比较，经过单点Ala、扩展替换与四位点饱和筛选，再到18个双突变及亲本比较。按批次01–08阅读，可以同时看到设计如何演进，以及哪些预期得到了支持、哪些在组合中发生改变。

## 按研究顺序阅读

| 批次 | 问题 | 受体条目 | 双配体运行组数 |
|---|---|---:|---:|
| [01](batches/01-sidechain-combination/README.md) | 固定骨架侧链组合探索 | 3 | 6 |
| [02](batches/02-af3-combination/README.md) | 全长AF3组合与结构路线比较 | 3 | 6 |
| [03](batches/03-af3-single-alanine/README.md) | 七个位点的单点Ala筛选 | 8 | 16 |
| [04](batches/04-af3-more-single-alanine/README.md) | 扩展单点替换与组合检查 | 19 | 38 |
| [05](batches/05-af3-n84-v110-v368-saturations/README.md) | N84 V110 V368三位点饱和筛选 | 58 | 116 |
| [06](batches/06-af3-supplement-singles/README.md) | R181 T106 W338补充替换 | 7 | 14 |
| [07](batches/07-af3-w338-saturation/README.md) | W338完整饱和筛选 | 20 | 40 |
| [08](batches/08-af3-double-mutants/README.md) | 十八个双突变及亲本比较 | 18 | 36 |

这些条目包含WT、重复设计和不同结构来源。逐次结果见[运行清单](run-inventory.csv)，数量不能直接当作独立突变数或实验重复数。

## 三个阶段的工作与发现

**01–03：先认识结构路线和位点差异。** 两种结构路线下四突变的D方向不同；03批逐点Ala结果将N84/V110/V368作为初始核心线索，并保留W338/R181探索价值。见[初筛分析](analysis/01-03-initial-screen/README.md)。

**04–07：从少数替换扩展到系统筛选。** 统一单突变表保留99条结构记录、87种设计和4个来源WT；其中05与07构成76种四位点饱和替换。N84V、V368R、V110C、V110M、V368N等体现不同评分作用方式，W338L的跨批翻转提醒候选依赖结构来源。见[单突变分析](analysis/04-07-single-mutants/README.md)。

**08：检验单点作用能否组合。** 18个双突变复用14种亲本；多数组合没有超过较好亲本的目标评分。N84Y_V368N相对N84Y改善整体评分并基本保留差异，体现需要同时检查两项评分、D和亲本比较。见[双突变分析](analysis/08-double-mutants/README.md)。

## 设计 证据与交付

- [设计版本](design/README.md)：v1的模块理由、v2的历史补WT提案及实际执行的v3。
- [统一比较口径](analysis/README.md)：WT、亲本、模型和seed的处理。
- [结构与制图交付](handoff/README.md)：5个受体的10项接触制图材料及N84V/V368R的4组MD结构起点。
- [共享输入](../shared/README.md)：AF3原始集合、序列、配体与参考结构的位置。

评分支持当前协议内的相对比较；接触变化帮助提出结构解释。单次Vina搜索、静态AF结构和不同来源WT限制了机制推断，实验结合、选择性和协同作用仍需独立验证。
