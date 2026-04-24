# Channel 1 · ΔΔG_sel 选择性阈值（详版）

**检索目标**：MM-PBSA / FEP / RBFE 在 GPCR 或其他受体-配体系统里判 selective vs non-selective 的 ΔΔG 数值 cutoff。

---

## [1] Hauser2018 ★★★

- **DOI**：10.1038/s42003-018-0075-x
- **引文**：Hauser K, Negron C, Albanese SK, Ray S, Steinbrecher T, Abel R, Wang L, Chodera JD. *Commun Biol* **1**:70 (2018)
- **标题**：Predicting resistance of clinical Abl mutations to targeted kinase inhibitors using alchemical free-energy calculations
- **核心发现**：FEP+ 在 Abl 激酶-抑制剂耐药突变预测中给出 RMSE = 1.07 kcal/mol (95% CI 0.89–1.26)，分类准确率 0.88；用明确 ΔΔG 阈值把突变分为"抗性 vs 敏感"。
- **阈值**：ΔΔG > 1.36 kcal/mol 判抗性（= RT·ln10 @ 298K = 1.363，对应 10× 亲和力下降）；≤ 1.36 kcal/mol 判敏感。
- **对项目迁移**：A 层 pass/fail 数值阈值最硬锚点。分类框架（"突变是否改变 ΔΔG"）与项目"突变是否改变 ascr18 vs ascr3 选择性"完全同构。

## [2] Aldeghi2017 ★★★

- **DOI**：10.1021/jacs.6b11467
- **引文**：Aldeghi M, Heifetz A, Bodkin MJ, Knapp S, Biggin PC. *J Am Chem Soc* **139**(2):946–957 (2017)
- **标题**：Predictions of ligand selectivity from absolute binding free-energy calculations
- **核心发现**：ABFE (alchemical MD) 预测溴结构域抑制剂跨亚家族选择性，对比 ITC 实验。
- **阈值**：未提硬 cutoff，但确立 "ΔΔG_sel = ΔG_target − ΔG_offtarget" 框架。
- **对项目迁移**：方法学 parent paper，常被引作 selectivity-by-FEP 奠基。A 线判据表写方法学段落时必须引用。

## [3] Wang2022 ★★★

- **DOI**：10.3389/fphar.2022.1018351
- **引文**：Wang S, Sun X, Cui W, Yuan S. *Front Pharmacol* **13**:1018351 (2022)
- **标题**：Safely lowering dose of MM-PBSA/MM-GBSA using cluster analysis
- **核心发现**：3 个膜蛋白系统（含 GPBAR、OX1 两个 GPCR）的 MM-PBSA/GBSA 系统 benchmark。
- **阈值**：优化参数后 "no studied ligands deviated from their experimental free energies by more than **2 kcal/mol**"；GPBAR R=0.70 (GBSA) / 0.79 (PBSA)；OX1 R=0.91 (GBSA) / 0.82 (PBSA)。
- **对项目迁移**：GPCR 膜蛋白 MM-PBSA 误差上限 ≈ 2 kcal/mol 的唯一明确 benchmark。用于"判据要留多大 buffer"的论证。

## [4] Yau2019 ★★☆

- **DOI**：10.1007/s10822-019-00201-3
- **引文**：Yau MQ, Emtage AL, Chan NJY, Doughty SW, Loo JSE. *J Comput Aided Mol Des* **33**(5):487–496 (2019)
- **标题**：Evaluating the performance of MM/PBSA for binding affinity prediction using class A GPCR crystal structures
- **核心发现**：20 个 Class A GPCR 晶体 × 934 配体 benchmark；r 范围 −0.334 (CB1 inactive) 至 0.781 (CB1 active)，全体 r=0.183。
- **阈值**：无；显式警告 GPCR MM/PBSA 高度系统特异，**不能照搬通用阈值**。
- **对项目迁移**：反向锚点——论证 "为什么要设宽 buffer、为什么要在项目体系 local calibration"。

## [5] Moore2023 ★★☆

- **DOI**：10.1038/s42004-023-00859-9
- **引文**：Moore JH, Margreitter C, Janet JP, Engkvist O, de Groot BL, Gapsys V. *Commun Chem* **6**:82 (2023)
- **标题**：Automated relative binding free energy calculations from SMILES to ΔΔG
- **核心发现**：RBFE 自动化流水线多靶点 benchmark。
- **阈值**：最佳 RMSE = 0.4 kcal/mol (TNKS2)，整体 0.8–1.7 kcal/mol；"1 kcal/mol 偏差"作精度靶标（correlation plot shaded region）；"qualitative agreement"（排序正确）为早期药发可接受。
- **对项目迁移**："1 kcal/mol = 金标精度，2 kcal/mol = 半定量 ranking 可接受" 分层标准。

---

## 检索盲区

- **Souza 等 GPCR selectivity MD** (plan 原提及)：未找到一作为 Souza 的对口文献。Powers/Khan/Souza 2024 *Nat Commun* 10.1038/s41467-024-54103-6 是 FFA1 activation 机制，非选择性阈值。
- **ascaroside-GPCR MM-PBSA 专文**：无。只能靠 [1][2][3] 方法学泛化。
