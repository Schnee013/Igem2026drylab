# 文献主矩阵 · MD 突变体判据锚点（29 篇，去重后 28 条）

字段：**ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 项目关联度 | DOI**

Channel 编码：
- **C1** = ΔΔG_sel 选择性阈值
- **C2** = 配体 pose RMSD 分箱
- **C3** = watchdog 早退阈值（Cα RMSD / COM 漂移 / 检查间隔）
- **C4** = 误差棒方法（bootstrap / block averaging）
- **C5** = GPCR 突变体 MD 协议模板（时长 / reps / 指标组合）

---

## Channel 1：ΔΔG_sel 选择性阈值（MM-PBSA / FEP / RBFE）

| ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 关联度 | DOI |
|---|---|---|---|---|---|---|---|
| Hauser2018 | C1 | Hauser K et al. | Commun Biol 1:70 | 2018 | ΔΔG > 1.36 kcal/mol 判抗性（= RT·ln10，对应 10× 亲和力下降）；FEP+ RMSE 1.07 kcal/mol | ★★★ | 10.1038/s42003-018-0075-x |
| Aldeghi2017 | C1 | Aldeghi M et al. | JACS 139(2):946–957 | 2017 | ABFE 做跨亚家族选择性的方法学 parent paper；ΔΔG_sel = ΔG_target − ΔG_offtarget | ★★★ | 10.1021/jacs.6b11467 |
| Wang2022 | C1 | Wang S, Sun X, Cui W, Yuan S | Front Pharmacol 13:1018351 | 2022 | GPCR 膜蛋白 MM-PBSA 误差上限 ≈ 2 kcal/mol（GPBAR R=0.70–0.79；OX1 R=0.82–0.91） | ★★★ | 10.3389/fphar.2022.1018351 |
| Yau2019 | C1 | Yau MQ et al. | J Comput Aided Mol Des 33(5):487–496 | 2019 | 20 个 Class A GPCR × 934 配体 benchmark；全体平均 r=0.183，显式警告"系统特异、不要照搬通用阈值" | ★★☆ | 10.1007/s10822-019-00201-3 |
| Moore2023 | C1 | Moore JH et al. | Commun Chem 6:82 | 2023 | RBFE 自动化流水线 RMSE 0.4–1.7 kcal/mol；"1 kcal/mol = 金标，2 kcal/mol = 半定量排序可接受" | ★★☆ | 10.1038/s42004-023-00859-9 |

**C1 判据综合建议**（从 5 篇可构造）：
- Pass：\|ΔΔG_sel(ascr18 vs ascr3)\| > 1.36 kcal/mol（[Hauser2018]）
- Fail：\|ΔΔG_sel\| < 1.0 kcal/mol（< 金标精度，[Moore2023]）
- Gray zone：1.0–1.36 kcal/mol → 加 replica / 延长采样
- Buffer：±2 kcal/mol（MM-PBSA 膜蛋白上限，[Wang2022]）；若用 MM-PBSA 而非 FEP，阈值放宽至 ~2.7 kcal/mol
- 反向锚点：[Yau2019] 支撑"为何要留 buffer"的论证

---

## Channel 2：配体 pose RMSD 分箱

| ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 关联度 | DOI |
|---|---|---|---|---|---|---|---|
| Warren2006 | C2 | Warren GL et al. | J Med Chem 49(20):5912–5931 | 2006 | **RMSD ≤ 2.0 Å** 的 docking pose 黄金标准（10 程序 × 37 scoring × 8 靶点 benchmark） | ★★★ | 10.1021/jm050362n |
| Fusani2020 | C2 / C3 | Fusani L, Palmer DS, Somers DO, Wall ID | J Chem Inf Model 60(3):1528–1539 | 2020 | BPMD PoseScore ≤ 2 Å 判 stable；PersScore ≥ 0.6 保留起始 H-bond；蛋白对齐取配体 3 Å 内残基 | ★★★ | 10.1021/acs.jcim.9b00843 |
| GuterresIm2020 | C2 | Guterres H, Im W | J Chem Inf Model 60(4):2189–2198 | 2020 | HTMD pose 稳定性分箱：<1 Å 高稳 / 2–3 Å intermediate / ≥3 Å drift；native pose 94% stable vs decoy 56–62% | ★★★ | 10.1021/acs.jcim.0c00057 |
| Liu2017 | C2 | Liu K, Kelley L, Tresadern G, Friesner RA et al. | J Chem Inf Model 57(11):2514–2522 | 2017 | 交叉对接 MD：stable pose RMSD 波动 1–2 Å；non-stable > 3 Å 持续漂移；推荐筛选窗口 ≥10–20 ns | ★★☆ | 10.1021/acs.jcim.7b00412 |
| Sakano2016 | C2 | Sakano T, Mahamood MI, Yamashita T, Fujitani H | Biophys Physicobiol 13:181–194 | 2016 | **β2AR (GPCR!) 1 µs MD**：正确 pose L-RMSD <2 Å 全程 / 错误 pose >6 Å 持续漂移 | ★★★ | 10.2142/biophysico.13.0_181 |

**C2 判据综合建议**：
- stable：<2 Å（[Warren2006] + [Fusani2020] + [Sakano2016] 三方锚定，[Sakano2016] 为 GPCR 实测）
- intermediate：2–5 Å（[GuterresIm2020] 给出 2–3 Å 细化阈值，项目可细分或保留 2–5 Å）
- drift：>5 Å（[Sakano2016] β2AR 实测 >6 Å 漂移；[GuterresIm2020] ≥3 Å 为 unstable，项目的 >5 Å 更保守）

---

## Channel 3：Watchdog 早退阈值

| ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 关联度 | DOI |
|---|---|---|---|---|---|---|---|
| RodriguezEspigares2020 | C3 | Rodríguez-Espigares I et al. | Nat Methods 17(8):777–787 | 2020 | GPCRmd 标准：**3 reps × 500 ns** per receptor（项目 200 ns × 3 reps 的源流）；Cα RMSD 为 QC 指标 | ★★★ | 10.1038/s41592-020-0884-y |
| Clark2016 | C3 | Clark AJ, Tiwary P, Borrelli K, Feng S, Miller EB, Abel R, Friesner RA, Berne BJ | J Chem Theory Comput 12(6):2990–2998 | 2016 | BPMD 原始论文；**10 ns × 10 replicas** metadynamics pose triage；ligand RMSD ≤ 2 Å 判 native（88% 命中） | ★★★ | 10.1021/acs.jctc.6b00201 |
| Fusani2020 | C2 / C3 | Fusani L et al. | J Chem Inf Model 60(3):1528–1539 | 2020 | 见 C2；BPMD extension，监控间隔、H-bond persistence 窗口（last 2 ns）、配体 3 Å 内对齐 | ★★★ | 10.1021/acs.jcim.9b00843 |
| Lukauskis2022 | C3 | Lukauskis D, Samways ML, Aureli S, Cossins BP, Taylor RD, Gervasio FL | J Chem Inf Model 62(23):6209–6216 | 2022 | OpenBPMD 双阈值：**2 Å 严判（88% 命中）/ 3 Å 宽判（97% 命中）**；bias 沉积间隔 **100 ps**；ContactScore 取 last 2 ns | ★★★ | 10.1021/acs.jcim.2c01142 |
| Doerr2016 | C3 | Doerr S, Harvey MJ, Noé F, De Fabritiis G | J Chem Theory Comput 12(4):1845–1852 | 2016 | HTMD adaptive sampling 框架：MSM 聚类权重驱动 early termination / reseed；epoch 级检查 | ★★☆ | 10.1021/acs.jctc.6b00049 |

**C3 判据综合建议**（替换先前估计值 "5 Å / 50 ns"）：
- 配体 COM 漂移：**3 Å marginal / 5 Å 确认 unbinding**（[Lukauskis2022] 双阈值思路，比单点 5 Å 更有区分度）
- Cα RMSD：GPCR 常规 1–3 Å，**>5 Å 判体系崩**（[RodriguezEspigares2020] GPCRmd 通用行为）
- 检查间隔：**50 + 100 ns 双检查点**（[Lukauskis2022] 的 100 ps 是 metadynamics 场景；本项目 unbiased 200 ns，50/100 ns 对应 25%/50% 进度节点，单点决策风险太高）
- Early-termination 框架引用：[Doerr2016] HTMD（工程问题的文献层最接近锚点）

---

## Channel 4：误差棒方法

| ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 关联度 | DOI |
|---|---|---|---|---|---|---|---|
| GenhedenRyde2015 | C4 | Genheden S, Ryde U | Expert Opin Drug Discov 10(5):449–461 | 2015 | MM/PBSA 权威综述：多次独立短 MD > 单次长 MD；SE ∝ σ/√n；avidin-biotin SE ≈ 11–14 kJ/mol (n=20) | ★★★ | 10.1517/17460441.2015.1032936 |
| Mey2020 | C4 | Mey ASJS, Allen BK, Bruce Macdonald HE, Chodera JD, Hahn DF, Kuhn M, Michel J, Mobley DL, Naden LN, Prasad S, Rizzi A, Scheen J, Shirts MR, Tresadern G, Xu H | Living J Comput Mol Sci 2(1):18378 | 2020 | Alchemical FE "Best Practices v1.0"：同 perturbation ≥ 2–3 次（不同初速度）评 precision | ★★★ | 10.33011/livecoms.2.1.18378 |
| Grossfield2018 | C4 | Grossfield A, Patrone PN, Roe DR, Schultz AJ, Siderius DW, Zuckerman DM | Living J Comput Mol Sci 1(1):5067 | 2018 | MD 不确定度 LiveCoMS Best Practices：bootstrap + block averaging + 多 replica 三件套；block size plateau 自适应 | ★★★ | 10.33011/livecoms.1.1.5067 |
| Knapp2018 | C4 | Knapp B, Ospina L, Deane CM | J Chem Theory Comput 14(12):6127–6138 | 2018 | 310,000 ns benchmark；单次长 MD 结论不可复现；经验法则 **≥5–10 replicas** | ★★★ | 10.1021/acs.jctc.8b00391 |
| FlyvbjergPetersen1989 | C4 | Flyvbjerg H, Petersen HG | J Chem Phys 91(1):461–466 | 1989 | **Block averaging 源头文献**；重整化群二分迭代至方差 plateau = 真实 SE | ★★☆ | 10.1063/1.457480 |

**C4 判据综合建议**：
- 首选：seed-level bootstrap（对独立 seed 重采样，n ≥ 10000）—— [Grossfield2018] + [GenhedenRyde2015]
- 单 seed 内时序自相关：block averaging（plateau 法，[FlyvbjergPetersen1989] 源头 + [Grossfield2018] 现代 best practice）
- 显著性检验：seed-level Welch t-test（[Mey2020] + [Grossfield2018]）
- Seed 数下限：**≥5**（[Knapp2018] 硬锚点）；理想 ≥10；每 seed 200 ns 优于 [GenhedenRyde2015] 的 ps 级示例
- 报告格式：95% CI（2.5–97.5 百分位），[Grossfield2018] 推荐

---

## Channel 5：GPCR 突变体 MD 协议模板（2026-04-23 补检）

| ID | Channel | 文献 | 期刊 | 年份 | 核心阈值/方法 | 关联度 | DOI |
|---|---|---|---|---|---|---|---|
| Verma2018 | C5-A | Verma RK, Abramyan AM, Michino M, Free RB, Sibley DR, Javitch JA, Lane JR, Shi L | PLOS Comput Biol 14(1):e1005948 | 2018 | D2/D3 E2.65A；145 轨迹 / ~76.5 μs；MSM + MM/GBSA；WT 两亚稳态 52/48% → mut 60% | ★★★ | 10.1371/journal.pcbi.1005948 |
| Keranen2014 | C5-A | Keränen H, Gutiérrez-de-Terán H, Åqvist J | PLoS ONE 9(10):e108492 | 2014 | A2A **30 alanine scan × 2 ligand**；FEP 7 reps × 50–80 ns/mut；精度 0.7 kcal/mol | ★★★ | 10.1371/journal.pone.0108492 |
| Billesbolle2023 | C5-A | Billesbølle CB, de March CA, van der Velden WJC, Ma N, Tewari J, Liu Q, Vaidehi N, Matsunami H, Manglik A | Nature 615(7953):742–749 | 2023 | OR51E2 (orphan OR + 短链 propionate) 34+ 突变；**5 × 1 μs**（apo/holo/Q181D）；EC50 交叉 | ★★★ | 10.1038/s41586-023-05798-y |
| Choi2023 | C5-A | Choi C, Bae J, Kim S, Lee S, Kang H, Kim J, Bang I, Kim K, Huh WK, Seok C, Park H, Im W, Choi HJ | Nat Commun 14(1):8105 | 2023 | OR52cs **F14A/F96A/F170A 组合突变**；5 × 1 μs（apo + octanoate）；TM5/6 opening | ★★★ | 10.1038/s41467-023-43983-9 |
| Ahmed2018 | C5-B | Ahmed L, Zhang Y, Block E et al. | PNAS 115(17):E3950–E3958 | 2018 | OR5AN1/OR1A1 musk；同源建模 + MD + QM/MM；疏水 77% + H-bond 13% | ★★☆ | 10.1073/pnas.1713026115 |
| Wang2024-OR | C5-B | Wang J et al. | Front Mol Biosci 11:1498796 | 2024 | OR 结合机制综述（背景参考） | ★☆☆ | 10.3389/fmolb.2024.1498796 |
| Milletti2021 | C5-C | Milletti F et al. | J Comput Aided Mol Des 35:133–144 | 2021 | *C. elegans* olfactory GPCR 结合位点识别（3D Zernike + homology，无 MD） | ★★☆ | 10.1007/s10822-021-00434-1 |
| Gao2024 | C5-D | Gao Y et al. | Cell Mol Life Sci 81(1):241 | 2024 | *A. ochraceus* **GprC + AF2 + Vina**（无 MD）；glucose/9-HODE 同为 −4.6 kcal/mol 不同位点 | ★★☆ | 10.1007/s00018-024-05160-z |
| LamimRibeiroFilizola2019 | C5-E | Lamim Ribeiro JM, Filizola M | Curr Opin Struct Biol 55:121–128 | 2019 | GPCR 变构 MD 综述；百 μs 才收敛；推荐 ligand RMSD + H-bond + Trp6.48 χ 角 | ★★☆ | 10.1016/j.sbi.2019.03.016 |

**C5 可直接复用的协议模板**：

- 重复数：5 × 1 μs × (apo + holo)（[Billesbolle2023] [Choi2023]）
- 饱和扫描：每突变 7 reps × 50–80 ns + FEP（[Keranen2014]）
- 动态 pose：累计 ~75 μs + MSM + MM/GBSA（[Verma2018]）
- 指标组合：ligand RMSD + H-bond 频率 + TM5–6 距离 + contact frequency（[Billesbolle2023] [Choi2023] [LamimRibeiroFilizola2019]）
- 实验交叉：MD → EC50/cAMP dose-response（[Billesbolle2023] [Choi2023] [Ahmed2018]）
- 空白确认：**OR-ascaroside MD 全检索无命中**——项目本身即方法学新颖性

---

## 交叉引用

- **Fusani2020** (10.1021/acs.jcim.9b00843) 同时被 C2、C3 命中 → 单一权威源，内容分区放置。
- **Clark2016** (C3, BPMD 原始) 与 **Fusani2020** (C2/C3, BPMD extension) 是方法学同一谱系。
- **GenhedenRyde2015** 在父计划 `P0-md-simulation.md:408` 已引用（无阈值），本矩阵补齐其方法学阈值内容。
- **Choi2023** F14A/F96A/F170A 与项目 Gpr3 F170 位点直接对应 → A 线判据表引用权重最高。
- **Gao2024** *A. ochraceus* GprC 为项目直系亲缘工作，仅到 docking；项目 MD 即方法学推进。

---

## 待补（由用户提供）

1. Zotero 本地库（`mcp__zotero__zotero_search_items` 已尝试）返回的 PDF attachment 均无 parent item 元数据（"No authors"），无法自动提取 DOI。建议用户将 PDF 挂到 parent item 或手动提供 DOI 清单。
2. 原计划提及的 **Souza 等 GPCR selectivity MD 工作**——检索未命中，需用户确认原始出处。
