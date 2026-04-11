# Lesson 5：结果解读 —— IFP 热图、PyMOL 可视化、V138R 的诚实边界

> **这一课回答什么**：ProLIF 的 IFP 到底在量什么？接触频率为什么不等于结合贡献？热图怎么读？PyMOL 怎么打开 Top 6 候选看结构？V138R 的"Arg 胍基盐桥"到底算不算实证？F170E 的"GLU170 接触 ascr3 更多却削弱结合"为什么反直觉？
>
> **前置**：Lesson 4（三大新发现、Top 6 证据强度、AF3 信任度、Hu2024 对照分层）。本课假定你已经知道 Top 6 都是什么、每一条的证据强度分级——这里不重复，直接进"怎么看结果"的层面。
>
> **这一课的核心姿态**：结构可视化不是装饰——它是"我们怎么把一个 ΔΔG_sel 数字翻译成一个可以讲的机制故事"的桥梁。V138R 的诚实叙事是本课的重头戏，**学完这一课你应该有能力对着一张 PyMOL 截图主动讲出 "这个 pose 告诉我们什么、不告诉我们什么"**。

---

## 1. IFP 是什么：从 ΔG 到"接触指纹"

Vina 给出的是一个数字（ΔG），你可以知道"这个 pose 的结合能有多好"，但这个数字不告诉你**结合是通过哪些残基发生的**、**哪几个残基在两个配体之间接触频率差别最大**。要回答这些问题，你需要一个层面更细的工具——**Interaction Fingerprint（IFP）**。

IFP 的思路：

1. 把一次 docking pose 拆成"受体的每一个口袋残基" × "配体原子"的所有配对
2. 对每个配对检查它的几何关系 —— 距离 / 角度 / 受体残基的化学性质 / 配体原子的类型
3. 根据预定义的规则判断这个配对属于哪一类相互作用：**HBond 供体 / HBond 受体 / VdWContact / Cationic / Anionic / Ionic / Aromatic / Hydrophobic** 等
4. 把所有配对的分类结果聚合成一个向量——这就是这一次 pose 的 IFP

用 ProLIF 这类工具跑一遍 Top 6 的 ascr18 和 ascr3 pose，你得到的是一张"每个残基对每个配体的接触类型 × 接触次数"的矩阵。这张矩阵就是我们做机制假说的原始证据——它让你能说"M327 在 ascr3 上接触 8 次 / 在 ascr18 上接触 3 次"这种具体到残基的话，而不是笼统地说"这个位点重要"。

### 关键警告：接触频率 ≠ 结合贡献

读 IFP 最容易犯的错误是把"接触次数多"等同于"对 ΔG 贡献大"。**这两件事在 Vina + 单 pose 的框架下没有严格对应关系**：

- Vina 的 ΔG 是一个综合打分函数，把 vdW / H-bond / 溶剂化 / 熵惩罚等加权合成一个数字
- IFP 的"接触次数"只是在这个 pose 上几何上满足某个规则的配对数量
- 同一个残基可能接触次数很多但每次的几何参数都很差（几何上能算作"接触"但能量贡献接近零），也可能接触次数很少但每次都刚好卡在最优几何上（能量贡献显著）

正确的读法是：**IFP 是提出机制假说的起点，不是 ΔΔG_sel 数字的等价替代**。你用 IFP 找到"这个残基在两个配体上的接触差别很大"之后，还要回到 Vina ΔG 和 pose 本身去确认 "这个差别是不是真的反映在能量打分里"。

---

## 2. 为什么是 ProLIF 不是 PLIP：切换的故事

我们一开始用的不是 ProLIF，是 **PLIP**（Protein-Ligand Interaction Profiler）。PLIP 的优势是有一个交互式 web 端，出图漂亮。但在 docking-repro v2 阶段的一次 Truth Audit 里我们发现了一个问题：

**v2 阶段用 PLIP 从 Gpr3 WT pose 里提取的 8 个"高频接触残基"，拿去做 alanine scan 之后 ΔΔG_sel 全部落在噪声区**。换句话说，PLIP 标出的那 8 个"和 ascr18 频繁接触"的残基里，没有一个是真正的选择性关键位点。

第一反应是以为这 8 个位点是真的不重要——然后我们做了一次交叉验证：把同一份 Gpr3 pose 分别丢给 PLIP 和 ProLIF，两个工具得到的"高频接触残基列表"**是完全不同的两套残基**。这说明问题不在"残基不重要"，而在 **PLIP 对我们这份 pose 的处理有条件失效**——它报告的"高频接触"在几何上不成立。

决策：**整条 pipeline 的 IFP 从 PLIP 切到 ProLIF**。切换之后重新跑 Gpr3 的 scan_residues 列表，最关键的结果是 **I141A 这个候选第一次被发现**——I141A 的 ΔΔG_sel = −0.786，是 Tier 1 候选，但它在 PLIP 的残基列表里压根不存在，所以 v2 阶段完全没扫过它。

这一段故事的结论不是"PLIP 不行、ProLIF 更好"——它是一个更通用的教训：**任何一个可能影响扫描覆盖面的工具，在信任它的输出之前要做独立交叉验证**。ProLIF 对我们这份 pose 能工作，不代表它对所有蛋白都没有条件失效；同理，PLIP 在别的项目里可能工作得很好。这一层不确定性是 drylab 方法学内核的一部分——把每个工具的输出当成"需要被另一个工具交叉验证的候选"，不要当成"已经定论的事实"。

完整的 Truth Audit 记录在 `docs/logs/` 下（2026-04-08 左右），后续切换决策在 `docs/logs/2026-04-09.md` 的 v2.7 版本记录里。

---

## 3. 怎么读 IFP 热图

IFP 的聚合结果被画成热图：**横轴 = 受体残基（按序列号排），纵轴 = 配体类型（ascr18 / ascr3 / ascr7），色深 = 接触次数**（或归一化的接触频率）。一张热图就是一个受体在三个配体下的完整接触指纹。

全套热图的权威源：
- `experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png` — 三受体总览
- `experiments/docking-repro/analysis/ifp_heatmap_Gpr2.png`、`ifp_heatmap_Gpr3.png`、`ifp_heatmap_GprC.png` — 单受体细节

Top 6 突变体的 IFP 矩阵源文件在 `experiments/docking-repro/results/ifp_analysis_mutants/`，包括 `mutant_contacts.csv`——每个突变的每次接触的**分类标签**（是 HBond / VdWContact / 还是其他指纹类型）就在这个 CSV 里。这是 V138R 诚实叙事的原始证据文件。

### 读图的三步法

**第一步：找"两个配体之间差异最大的残基"**
对每个残基比较 ascr18 和 ascr3 的接触次数差值。差值大的残基是候选"选择性关键位点"——这些残基解释了为什么受体能区分两个配体。但不要只挑差值大的，还要看差值的方向（哪个配体接触更多）是否和 ΔΔG_sel 一致。

**第二步：定位 Hu2024 对照残基的位置**
在热图上把 Hu2024 的 4 个对照残基（N60A / R395A / S44A / N56A）用记号笔标出来。这 4 个位点的接触模式是你检查 pipeline 是否自洽的交叉验证点。Lesson 4 已经讲过它们的 Tier 分层结果——**在热图层面你应该看到：三个真阳性（N60 / R395 / S44）在 ascr18 上的接触频率是非零的（说明它们确实是接触残基）；N56（真阴性）的接触频率相对低**——这是对 Lesson 4 §Hu2024 对照分层里"GprC 口袋几何特异可能是假阳性根因之一"这个解释假说的一个旁证。

**第三步：对 Top 6 候选做"WT vs Mutant"前后对比**
每个 Top 6 候选都有 WT 和 mutant 两张热图。对比它们就能看到"这个突变改变了哪些接触、没改变哪些接触"。Gpr2 M327 的 WT vs M327A 对比会告诉你：Ala 替换之后"M327 对 ascr3 的接触从 X 降到 0，对 ascr18 的接触从 Y 基本不变"——这正是 Lesson 4 讲的"丢失路径"的直观 IFP 证据。

---

## 4. PyMOL 实操：打开 Top 6 候选看结构

IFP 是数值层面的指纹，PyMOL 是可视层面的结构。两层要一起看才能讲清楚机制——数值告诉你"哪个残基差别大"，结构告诉你"这个差别在空间上长什么样"。

### 为什么不用 complex PDB：分开存 receptor + ligand 的理由

你可能会想："我能不能把 receptor 和 ligand 合并成一个 complex PDB，一次 load 完？" 我们一开始就是这么做的。**2026-04-11 我们改成了"receptor 和 ligand 分开存"**，理由是：

- **独立操作**：合并成一个文件之后，PyMOL 里只能看到一个对象。如果你想单独隐藏 ligand、单独给 receptor 上色、单独 align 两个 receptor 而不带 ligand——都做不到
- **样式脚本复用**：两个 `.pml` 样式脚本（`style_detail.pml` / `style_overview.pml`）用 `polymer.protein` / `organic` 这种**通用选择子**，不依赖对象名。这意味着你可以随意加载任何 receptor/ligand 组合，样式脚本都能正确工作——合并成 complex 之后这种"无关对象名"的选择子就失效了
- **pose 对齐的精确控制**：`align rec_mut, rec_wt` 只会动 receptor 本身，不会带动 ligand。如果你想让 ligand 跟着 receptor 一起变换（这是常用的"把 mutant 的 pose 叠到 WT 坐标系下"），需要显式 `matrix_copy rec_mut, lig_mut_18`。complex 合并之后这一层控制就没了

权威 PyMOL 资源目录 `experiments/docking-repro/analysis/pymol_top6/` 的完整结构和使用方法见它自己的 README——这里只讲**组员第一次打开 PyMOL 时的基本流程**，复杂的渲染出图留给 Lesson 7 讲接手任务时展开。

### 第一次打开：V138R vs WT 的 ascr18 对比

```pml
cd /Users/roy/Documents/drylab/experiments/docking-repro/analysis/pymol_top6

# 加载 WT + mutant 的 receptor 和 ligand 各一份
load receptors/Gpr3_WT.pdb,       rec_wt
load ligands/Gpr3_WT_ascr18.pdb,  lig_wt_18
load receptors/Gpr3_V138R.pdb,    rec_mut
load ligands/Gpr3_V138R_ascr18.pdb, lig_mut_18

# 把 mutant 的 receptor 叠到 WT 的坐标系
align rec_mut, rec_wt

# 关键：align 只动 receptor，不动 ligand。
# 必须手动把 rec_mut 的变换矩阵复制给它的 ligand，
# 否则 ligand 还在旧坐标系里——画面上会看起来 ligand 飞在 receptor 外面。
matrix_copy rec_mut, lig_mut_18

# 应用细节样式（氢键 + 残基 label + 表面云朵）
@style_detail.pml
```

**第一次打开新手最容易犯的错误**是 `align` 之后忘记 `matrix_copy`——画面上看起来 ligand 飘在 receptor 外面几埃，这时千万不要直觉地"重新对接"或者"换一个 pose"——**问题不在 pose 本身，问题在坐标变换没传递**。`matrix_copy` 之后 ligand 会回到原位。

### pose 可靠性检查 vs align 错误

在 PyMOL 里看 pose 的时候，你可能会看到"配体和某个残基空间上重叠"的情况。这里有两种完全不同的解释，必须分开：

- **情况 A：真的是 pose 里配体和残基碰在一起** — Vina 的搜索结果确实给出了这样一个 pose，对接本身就有问题（可能是 box 太小、exh 太低、或者残基侧链被 flexible 处理得不好）
- **情况 B：align 变换没传递到 ligand** — 几何上"重叠"只是屏幕坐标系下的错觉，实际上 mutant 的 ligand 还在旧坐标系里

**区分的办法**：先用 `label /lig_mut_18///LIG`901`/C1, "%.2f %.2f %.2f" % (x, y, z)` 看一下 ligand 的坐标；再对 receptor 做同样的坐标检查。如果两边的坐标范围完全不重叠（比如 receptor 在 [10, 30] 而 ligand 在 [50, 70]），那就是情况 B，`matrix_copy` 一下就解决；如果坐标范围重叠但你看到的是真的原子间距 < 1 Å，那才是情况 A，需要回去看对接参数或换一个 pose。

这个排查 flow 是组员用 PyMOL 看结果时最常碰到的第一个坑——**碰到看起来不对的画面先怀疑坐标变换，再怀疑对接本身**。

---

## 5. V138R 盐桥机制：完整的诚实叙事

这是本课最重要的一节，也是 docking 方向被评委追问最频繁的一个点。下面这一整段讲的是一件事：**"我们在 V138R 上到底观察到了什么、没观察到什么、接下来怎么补"**。

### 5.1 我们观察到什么：空间富集是事实

在 V138R 的 mutant IFP 上：

- **ARG138 对 ascr18 的接触次数：9 次**
- **ARG138 对 ascr3 的接触次数：2 次**
- **差值 +7**（是全 Top 6 里残基-配体接触差值最大的一个）

这个差值在 V138 位点上是突变后才出现的——V138 WT 是 Val，短疏水侧链，没有能够形成差异化接触的长距离相互作用。突变成 Arg 之后，Arg 的长柔性侧链（从 Cα 到末端胍基约 7 Å）伸进口袋的方式让它在 ascr18 pose 附近出现了显著的空间富集。这个"空间富集"是我们观察到的事实，没有水分。

### 5.2 我们没观察到什么：接触类型全部是 VdWContact

关键的限定来自 `mutant_contacts.csv` 里每次接触的**分类标签**。当我们查 ARG138 的那 9 次接触各自属于哪一类时，答案是：

**全部 9 次接触的类型都是 `VdWContact`**。

没有一次被 ProLIF 归类为 HBond、也没有一次被归类为 Cationic / Anionic / Ionic 这些跟盐桥有关的指纹。**这意味着什么？**

如果 V138R 真的形成了 Arg 胍基和 ascr18 末端羧基的盐桥，你应该会看到至少一部分接触被分类成 Ionic 或者 Cationic/Anionic——因为盐桥的本质就是正电荷和负电荷在短距离上的静电互作，ProLIF 的 Ionic 通道就是用来抓这种模式的。

但我们看到的 9 次全部是 VdWContact。

### 5.3 为什么是 VdWContact：根因是采样盲区

这里必须区分**"没看到"**和**"不存在"**：

- "不存在" = "在我们跑的这个 pose 上 Arg 胍基和 ascr18 羧基之间几何上不满足 Ionic 的条件"
- "没看到" = "我们跑 ProLIF 时没开启 Ionic 这个通道，所以即使几何上满足条件，工具也不会报告"

**真相是后者**。

本轮 ProLIF 只开启了两个指纹通道：**HBond** 和 **VdW**。`Cationic` / `Anionic` / `Ionic` 通道**没有启用**。这是一个我们在 ProLIF 配置里做的主动选择（目的是控制计算量和输出文件大小），但它带来了一个具体后果：**即使 V138R 的 pose 里真的有盐桥几何，我们这一轮也看不到**。

所以 9 次全部是 VdWContact 不等于"没有盐桥"——它等于"**这一轮的 ProLIF 配置不可能报告盐桥**"。这是一个**采样盲区**，不是一个"没有信号"。

### 5.4 结论边界：我们能说什么、不能说什么

把上面三层合起来，V138R 当前的结论边界是精确的：

> **能说**：Arg 胍基在 ascr18 pose 附近**空间上富集**（9 次接触 vs ascr3 的 2 次），而且这个空间富集是 V138→R 突变带来的新现象（V138 WT 不具备这种接触模式）。
>
> **不能说**：Arg 胍基和 ascr18 末端羧基**形成了盐桥**——盐桥是一个带几何约束的相互作用类型，需要 Ionic 通道实证，本轮没开。
>
> **同样不能说的是**：V138R **没有**形成盐桥——因为"没开 Ionic 通道"不能证伪盐桥，只能说明这一轮没给盐桥一个被观察到的机会。

这种"三层都要说清"的精确度听起来像是在咬文嚼字，但它是 docking 方向最重要的诚实姿态：**把"观察事实"和"机制解释"严格分开**。空间富集是观察事实；盐桥是机制假说；机制假说需要一条独立的实证路径才能升级为结论。

### 5.5 三条实证路径

**路径 A：重跑 ProLIF 开启 Ionic 通道**（成本低、信息量最小）
- 只需要改 ProLIF 配置，把 Cationic / Anionic / Ionic 这些指纹加进去，然后在同一份 pose 上重跑一次
- 能回答"在当前 pose 的几何下，ARG138 胍基和 ascr18 羧基是不是满足 Ionic 的几何条件"
- 局限：只看一个 pose。如果 Vina 的最优 pose 不是真实结合构象，这一次 Ionic 检查的结论对动态行为说明不了什么

**路径 B：对 pose 做几何测量**（成本更低，直接看几何）
- 在 PyMOL 里对 ARG138 的胍基 N 原子（Nε / NH₁ / NH₂）和 ascr18 末端羧基的 O 原子做距离 + 角度测量
- 盐桥的几何判据：N-O 距离通常 < 4 Å，胍基和羧基平面之间有合理的方向性
- 能回答和路径 A 几乎相同的问题，但更直观
- 局限：和路径 A 一样，只在一个 pose 上

**路径 C：MD 模拟测时间序列**（成本最高，信息量最大，首选）
- 把 Gpr3 V138R × ascr18 的 mutant-ligand 复合体作为初始构象，跑 50-100 ns 的 MD 模拟（溶剂 + 膜 + 力场按 CHARMM36m/CGenFF/POPC 配置）
- 对整条轨迹计算 ARG138 胍基 N 到 ascr18 羧基 O 的距离时间序列
- 用盐桥占比（"距离 < 4 Å 的帧数 / 总帧数"）作为盐桥稳定性的定量指标
- 能同时回答两件事：**(1)** 盐桥在动力学上是否形成 **(2)** Top 6 的 pose 本身在 ns 级时间尺度上稳不稳
- 这是为什么 V138R 的机制问题**直接驱动 P0-md-simulation 方向启动**——MD 就是唯一能在一次实验里同时回答"机制" + "pose 稳定性"的工具

### 5.6 为什么 V138R 仍然推荐给湿实验

这里有一个看起来矛盾的点：如果机制未证实，为什么我们仍然把 V138R 放进 Top 6 交给湿实验组？

答案是：**湿实验测的是结合活性和选择性本身，不依赖机制解释是什么**。

湿实验组会构建 V138R 突变体、做表达、做结合实验、做 dose-response 曲线——拿到的是"V138R 突变体对 ascr18 的 EC₅₀ 是多少 / 对 ascr3 的 EC₅₀ 是多少"。这组数据的价值不取决于盐桥假说是不是真的：

- **如果 V138R 湿实验显示选择性增强** → 工程目标达成，不管机制是盐桥还是空间富集。wiki 上把机制描述为"Arg 胍基空间富集（可能伴随盐桥形成，待 MD 实证）"即可
- **如果 V138R 湿实验显示选择性没变或反向** → 我们学到两件事：**(1)** 当前 pipeline 对"Arg 胍基空间富集"这类信号的权重可能偏高 **(2)** Gpr3 上的选择性工程可能需要换位点。这是 DBTL 循环 Learn 阶段的数据，和"预测对不对"同样有价值

所以"机制未证实"**不是不推荐的理由**，只是"wiki 上讲 V138R 时不能把盐桥说成已经发生的事"的理由。推荐和机制解释是两件独立的事——这是 Lesson 4 §证据强度分级里讲的"推荐候选不等于机制已证实"的具体展开。

### 5.7 V138R 作为 MD 驱动力的叙事价值

最后一层：**V138R 的局限性正是 P0-md-simulation 方向启动的直接驱动力**。这不是"事后为 MD 找借口"——时间线上，MD 方向的启动文件`docs/modeling/P0-md-simulation.md` 里第一条写的就是"V138R 盐桥假说待实证"；04-12 的 MD 调研日志里技术栈选择 CHARMM36m 的核心理由就是"Arg-Asp/Glu 盐桥 LJ 修正**正好对症 V138R 胍基-羧基假说**"。

这给组员一个具体的叙事姿态：**把"docking 做不到"讲成"MD 要做什么"**。不要把 V138R 的局限性当成"弱点被动承认"，要把它当成"DBTL 循环 Learn → Design 的触发器的具体例子"。你把这层讲出来，评委对你的可信度评分会高于一个假装"我们什么都证实了"的回答。

---

## 6. F170E 反直觉：同一个 GLU 接触 ascr3 更多，却削弱 ascr3 的结合

Top 6 里还有一条看起来违反直觉的观察。F170E 在 IFP 上表现为：

- **突变后的 GLU170 对 ascr3 的接触次数更多**
- **但 ΔG(ascr3) 反而上升**（结合变弱，ΔΔG(ascr3) = +0.17）

直觉上你会想："如果 GLU170 和 ascr3 接触更多，它们之间的相互作用应该更强，ΔG 应该更负才对啊？" 但数字明确显示相反的方向。怎么解释？

这个现象静态对接 + IFP 解释不了。几种假说都有可能：

- **入口路径静电排斥**：F170 在 ECL2，位于配体进入路径的入口处。GLU 的负电可能对 ascr3 的某个部位形成了**排斥**而不是吸引——"接触多"是因为几何上 ascr3 经过这个位点，但能量上是不利的
- **构象重排**：GLU170 的引入可能让 ECL2 本身的构象发生了细微变化，改变了整个结合腔的几何，对 ascr3 的整体 pose 品质打了折扣。"接触多"只是 ascr3 在新腔里的 pose 的一个副作用
- **溶剂网络变化**：GLU 和 Phe 对水分子的组织方式不同。ECL2 的水桥网络变化可能影响 ascr3 的去水化代价

**没有一种假说能在静态对接框架内被证伪**。这一条和 V138R 的盐桥问题一起构成 Gpr3 两个候选"机制待实证"的来源——它们都需要 MD 的时间序列才能真正说清。

这里有一个额外的限定：F170 在 Gpr3 的 **ECL2**（TM4 和 TM5 之间的胞外环），不在 TM 螺旋内部。ECL2 的 AF3 pLDDT 普遍比 TM 内部低，静态对接对 ECL 残基的解读**本身就比 TM 内部弱一截**。所以 F170E 的证据强度在 Lesson 4 的分级里比 M327 低——不是因为数值信号不强（ΔΔG_sel = −0.696 其实很强），是因为位置可靠度本身打了折扣。

---

## 7. 动手：给一个 Top 6 候选出一张可讲的截图

读完本课之后，你应该能做到：

1. `conda activate docking` 之后打开 PyMOL
2. `cd` 到 `experiments/docking-repro/analysis/pymol_top6/`
3. 选一个 Top 6 候选（建议选 Gpr2 M327A 作为入门练习——它是 Top 1、机制最干净、不涉及 V138R 的那套诚实边界）
4. 按 `pymol_top6/README.md` 的"手动加载"段落把 WT 和 mutant 加载好、`align` 然后 `matrix_copy`
5. 应用 `style_detail.pml` 样式
6. 旋转视角找到"M327 残基 + ligand + 附近几个 hydrogen bond 虚线"都能同时入镜的角度
7. `ray 1600 1200` 渲染
8. `png out/M327A_detail.png, dpi=300` 保存

拿到截图之后，**口头向自己讲一遍这张图在说什么**——"这是 Gpr2 M327A 的 ascr18 pose，蓝色是 ligand、紫色是 mutant receptor、灰色是 WT receptor 叠加；M327A 把 WT Met 的长侧链替换成了 Ala，腔的空间多出来一块，ascr3 失去了原来和 Met 侧链的接触。"

你能流畅说出这一段之后，你就掌握了本课要传达的核心能力：**把一张结构图翻译成一段可以讲的故事**。这个能力会在 Lesson 6（迭代叙事）和 Wiki 写作阶段反复用到。

---

## 8. 学完这一课你该能回答的问题

1. **IFP 和 ΔG 的关系是什么？接触频率高是不是就等于结合贡献大？**
2. **为什么从 PLIP 切到 ProLIF？切换前后发现了什么具体候选？**
3. **V138R 观察到了什么、没观察到什么？为什么"9 次全是 VdWContact"不等于"没有盐桥"？**
4. **V138R 机制未证实为什么仍然推荐给湿实验？**
5. **F170E 的"GLU170 接触 ascr3 更多但 ΔG(ascr3) 削弱"为什么反直觉？这个反直觉指向什么后续工作？**
6. **PyMOL 里看到 ligand "飘在 receptor 外面" 的时候，先怀疑什么？**
7. **为什么 receptor 和 ligand 分开存而不合并成 complex PDB？**

第 3、4 两个问题是整门课的诚实叙事锚点——Q28 是题库里最重要的一题，V138R 这一段是你讲这题的主要素材。

---

**本课引用的权威源**：

- `experiments/docking-repro/analysis/pymol_top6/README.md` — PyMOL 使用手册
- `experiments/docking-repro/analysis/pymol_top6/style_detail.pml` / `style_overview.pml` — 样式脚本
- `experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png` 及 `ifp_heatmap_Gpr2/3/GprC.png` — IFP 热图
- `experiments/docking-repro/results/ifp_analysis_mutants/` — Top 6 mutant IFP 矩阵和 `mutant_contacts.csv`（ARG138 的 9 次接触类型的原始证据）
- `docs/modeling/P0-molecular-docking.md` §机制假说未实证（V138R 盐桥）
- `docs/modeling/P0-md-simulation.md` §前置风险 — CHARMM36m 选型与 V138R 假说的直接对应
- `docs/logs/2026-04-09.md` — PLIP → ProLIF 切换记录（v2.7 版本）

**本课和其他 Lesson 的分工**：
- ΔΔG_sel 统计辩护和 Hu2024 对照分层 → Lesson 4（本课不重复）
- 三次迭代的时间线骨架（含"PLIP → ProLIF 切换"的上一层叙事） → 附录 F
- Pipeline 代码细节和 IFP 跑法的脚本层面 → Lesson 3
- MD 方向的具体技术栈和前置风险 → `docs/modeling/P0-md-tech-stack-research.md`
