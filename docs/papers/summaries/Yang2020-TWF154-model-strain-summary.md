# Yang et al. 2020 — 文献总结

> **完整标题**: Natural diversity in the predatory behavior facilitates the establishment of a robust model strain for nematode-trapping fungi
> **期刊**: Proceedings of the National Academy of Sciences of the United States of America (PNAS), Vol. 117, No. 12, pp. 6762–6770
> **DOI**: 10.1073/pnas.1919726117
> **发表日期**: 2020-03-24
> **作者**: Ching-Ting Yang\*, Guillermo Vidal-Diez de Ulzurrun\*, A. Pedro Gonçalves, Hung-Che Lin, Ching-Wen Chang, Tsung-Yu Huang, Sheng-An Chen, Cheng-Kuo Lai, Isheng J. Tsai, Frank C. Schroeder, Jason E. Stajich, Yen-Ping Hsueh（\* 共同第一作者）
> **机构**: Institute of Molecular Biology, Academia Sinica, Nanjing, Taiwan；National Taiwan University；Cornell University；UC Riverside 等

---

## 核心发现（5–10 bullets，含数据）

- **自然多样性调查**: 在台湾采集 178 份土壤样本（69 个采样地点），在 >60% 的样本中检出线虫，在 ~35% 的样本中检出 NTF（nematode-trapping fungi），两者共存率 >63%，表明它们在自然环境中密切共生。
- **NTF 物种多样性**: 共鉴定 16 种已知 NTF 物种；其中 11 种属于 *Arthrobotrys* 属，*A. oligospora* 为最常见物种（26 个采样点），其次为 *A. thaumasia*（11 个）和 *A. musiformis*（11 个）。
- **模式菌株 TWF154 的确立**: 从 38 个野生 *A. oligospora* 分离株中筛选，TWF154 对 *C. elegans* N2（~145 个捕食陷阱/盘）和 ascr#18（~50 个陷阱/盘）的诱捕响应均为最高，且陷阱形成最早（~3 h），显著优于现用实验室菌株 ATCC24927（陷阱数低约 20 倍）。
- **捕食行为高度多态**: 不同 *A. oligospora* 野生分离株对 N2 和 ascaroside 的捕食响应差异极大（Tukey 检验显著），表明捕食能力是高度多样的数量性状，与系统发育距离无明显相关。
- **ascaroside 诱捕特异性**: 对 ascr#18 的响应与对 N2 的响应不完全重合，不同分离株对两种刺激的应答存在独立变异，TWF132 对 ascr#18 应答最强，TWF154 则对两者均强。
- **竞争适合度**: 在有 *C. elegans* 存在时，TWF154 产生的分生孢子比例显著高于 TWF106（敏感性弱的分离株），直接证明强诱捕能力带来繁殖适合度优势（配对 t 检验 \*\*，p<0.01）。
- **基因组组装与质量**: TWF154 基因组大小 39,619,008 bp，10 个 scaffold，N90=2,932,219 bp，BUSCO 完整性 97.7%，编码 12,107 个 tRNA，是迄今质量最高的 *A. oligospora* 基因组。线粒体基因组 100,961 bp，含 NADH 复合体、细胞色素 c 氧化酶/复合体 IV、ATP 合酶/复合体 V 等亚单位。
- **G 蛋白信号通路必需**: 靶向删除 G 蛋白 β-亚基基因 *GPB1*（EYR41_009480）的两个独立同源重组突变体，对 *C. elegans* 和 ascaroside 的捕食陷阱形成均严重缺陷，表明 G 蛋白信号传导是 NTF 感应线虫并形成捕食陷阱所必需的，且 ascaroside 受体可能是 GPCR。
- **HEG（homing endonuclease genes）富集**: TWF154 基因组含大量 LAGLI-DADG 和 GIY-YIG 家族内含子和基因间区域的 HEGs（共 25–32 个），显著多于其他 NTF 物种，这一特征与线粒体基因组进化密切相关。

---

## 实验方法（表格）

| 方法 | 详情 |
|------|------|
| 土壤样本采集 | 台湾 69 个地点，178 份土壤样本；低营养培养基（LNM）富集后传代 |
| 菌株鉴定 | ITS rDNA PCR 扩增（引物 G1854a/DF185-8），NCBI BLAST 比对（≥97% = 种级鉴定）|
| 线虫鉴定 | SSU rDNA PCR 扩增，>97% 阈值鉴定 |
| 诱捕实验定量 | NGM 培养板（5 cm），加 30 *C. elegans* L4 幼虫或 ascr#18（2 μM），24 h 后计数陷阱数；n=6，Tukey 检验 |
| 捕食动力学 | 记录第一个陷阱出现时间；6 株代表性菌株，n=4 |
| 杀线虫效率 | 12 h 线虫存活率曲线，6 株代表性菌株，n=9–21 |
| 竞争适合度 | TWF154 vs TWF106 混合培养，统计有/无 N2 时各菌株产孢比例，配对 t 检验，n=7 |
| 基因组测序组装 | PacBio 长读长（~1.5 Gb，500 bp 读段），Falcon 组装，Funannotate 注释，BUSCO 评估 |
| 系统发育分析 | 500 个随机单拷贝直系同源基因，ML 树 |
| 靶向基因删除 | 同源重组，*GPB1* 删除，潮霉素抗性标记（HygR），两个独立转化株验证 |
| 线虫培养 | *C. elegans* WT N2，标准 NGM + *E. coli* OP50；各 nematode 物种以单蠕虫 PCR 验证 |

---

## 关键数据（分小节）

### NTF 多样性与分布
- 178 份样本中，线虫检出率 ~92%（仅 NTF 4%，仅线虫 29%，两者共存 64%，均无 3%）。
- 2 个采样点（澎湖岛海岸线）不含线虫和 NTF，归因于极端环境（高温/高盐）。
- *A. oligospora* 在 ~35% 采样点出现；*Monacrosporium* 和 *Drechslerella* 属各仅在 1 个采样点出现。

### 诱捕表型多态性
- 对 N2 的陷阱数范围：~10–145（跨 38 株）；TWF145、TWF154 最高（~145），ATCC24927 最低组。
- 对 ascr#18 的陷阱数范围：~5–80；TWF132 最高（~80），ATCC24927 最低组之一。
- 第一个陷阱出现时间：TWF154 最快（~3 h），ATCC24927 最慢（~8 h），差异显著（p<0.05）。
- 12 h 存活率：TWF154 中 *C. elegans* 存活率最低（<20%），ATCC24927 中 >80%。

### 基因组特征（TWF154 vs ATCC24927）
| 特征 | ATCC24927 | TWF154 |
|------|-----------|--------|
| 组装大小 (bp) | 40,072,829 | 39,619,008 |
| Scaffold 数 | 215 | 10 |
| N90 大小 (bp) | 691,077 | 2,932,219 |
| GC 含量 (%) | 44.45 | 43.96 |
| 基因数 | 11,472 | 12,107 |
| BUSCO 完整性 (%) | 97.4 | 97.7 |

### G 蛋白实验
- *gpb1* 突变体陷阱数：对 N2、ascr#7、ascr#18 均接近 0（vs WT TWF154 ~150–200）。
- 互补株（导入 WT *GPB1* 拷贝）完全恢复陷阱形成（~160–200 个陷阱）。
- 5 d 菌落生长：WT、*gpb1* 突变体、互补株无显著差异（PDA 培养基，5 cm 直径），排除生长缺陷影响。

---

## 与项目的关系

本论文建立了 *A. oligospora* 野生型高性能模式菌株 **TWF154**，这正是 Kuo et al. 2024 研究 GprC/Gpr2/Gpr3 受体的起点菌株。具体关联如下：

1. **菌株来源**: Kuo 2024 及 Hu 2024 使用的 *A. oligospora* 背景菌株 TWF154 正是本文筛选并验证的高响应野生分离株，是后续所有受体遗传功能研究的宿主背景。

2. **G 蛋白信号轴**: 本文用 *gpb1* 敲除证明 G 蛋白信号是 ascaroside 感应所必需，并推断 ascaroside 受体是 GPCR——这为 Kuo 2024 后续鉴定具体受体（GprC、Gpr2、Gpr3）提供了直接的遗传框架。

3. **配体体系**: 本文已使用 **ascr#18**（2 μM）和 **ascr#7** 作为诱捕陷阱形成的标准化刺激，与本项目研究的核心配体完全吻合。

4. **基因组资源**: TWF154 高质量基因组（10 个 scaffold，BUSCO 97.7%）是后续 Gpr 受体基因鉴定、BW 编号映射、同源性分析的基础参考基因组。

> 注意：本论文本身不涉及 GprC（*A. flagrans*）；TWF154 仅是 *A. oligospora* 菌株。项目中 GprC 的研究属于独立平行线索。

---

## 关键引用（7 条）

1. **Hsueh et al., 2013**: Ascaroside pheromones signal nematode population density and mediate predation by nematode-trapping fungi. — 首次证明 ascaroside 是 NTF 形成捕食陷阱的化学信号。

2. **Maguire et al., 2011**: *C. elegans* Gαq (EGL-30) activates diacylglycerol synthesis. — 为 C. elegans 中 G 蛋白信号在线虫 pheromone 感知中的基础背景。

3. **Kim & Borkovich, 2006**: Two chemoreceptors mediate developmental effects of dauer pheromone in *C. elegans*. — G 蛋白偶联受体响应 ascaroside 的先导文献。

4. **Thi et al., 2019**: Heterotrimeric G-protein and signal transduction in the nematode-trapping fungus *Arthrobotrys oligospora*. — 在 *A. oligospora* 中 G 蛋白通路的直接研究背景。

5. **Yang et al., 2020 (本文)**: 建立 TWF154 模式菌株，证明 Gpb1 为 ascaroside 感应必需，ascaroside 受体可能为 GPCR。

6. **Vidal-Diez de Ulzurrun et al., 2019**: Fungal predator-prey interactions. — NTF 捕食行为分子机制相关综述背景。

7. **Fay & Bender, 1993; Brenner, 1974**: *C. elegans* 遗传学经典工作，为本文使用 N2 标准株提供背景。
