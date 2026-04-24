# Channel 4 · 误差棒方法（详版）

**检索目标**：bootstrap / block averaging 处理 MD 时间序列 / 多 replica 自由能估计置信区间的方法学锚点。

---

## [1] GenhedenRyde2015 ★★★

- **DOI**：10.1517/17460441.2015.1032936
- **引文**：Genheden S, Ryde U. *Expert Opin Drug Discov* **10**(5):449–461 (2015)
- **标题**：The MM/PBSA and MM/GBSA methods to estimate ligand-binding affinities
- **核心发现**：MM/PBSA/GBSA 端点法权威综述；明确指出**多次独立短 MD 优于单次长 MD**，标准误 SE ∝ σ/√n。
- **方法/数据**：建议 20–50 次独立 MD（生产 100–200 ps 即可），快照间隔 1–10 ps 可视为统计独立；avidin-biotin 案例 SE ≈ σ/√n ≈ 11–14 kJ/mol (σ = 47–62 kJ/mol, n = 20)。
- **对项目迁移**：seed 数 n 与 SE 的显式公式；父计划 `P0-md-simulation.md:408` 已引用（无阈值），本文补齐其方法学内容。

## [2] Mey2020 ★★★

- **DOI**：10.33011/livecoms.2.1.18378
- **引文**：Mey ASJS, Allen BK, Bruce Macdonald HE, Chodera JD, Hahn DF, Kuhn M, Michel J, Mobley DL, Naden LN, Prasad S, Rizzi A, Scheen J, Shirts MR, Tresadern G, Xu H. *Living J Comput Mol Sci* **2**(1):18378 (2020)
- **标题**：Best Practices for Alchemical Free Energy Calculations
- **核心发现**：Mobley + Chodera 牵头的 alchemical FE "Best Practices v1.0"；重复运行（不同初速度即独立 replica）为评估 precision 的必要条件。
- **方法**：同 perturbation **至少 2–3 次** 不同初速度评 precision；hydration FE 期待 SD < 0.01 kcal/mol，复杂结合 FE 可重复性显著更差。
- **对项目迁移**：seed 数下限 (≥2–3, 与 [Knapp2018] ≥5 互补)；protocol 引用模板。

## [3] Grossfield2018 ★★★

- **DOI**：10.33011/livecoms.1.1.5067
- **引文**：Grossfield A, Patrone PN, Roe DR, Schultz AJ, Siderius DW, Zuckerman DM. *Living J Comput Mol Sci* **1**(1):5067 (2018)
- **标题**：Best Practices for Quantification of Uncertainty and Sampling Quality in Molecular Simulations
- **核心发现**：MD 不确定度量化 LiveCoMS Best Practices；系统讲 bootstrap + block averaging + 多 replica **三件套**；明确推荐报 **95% CI (2.5–97.5 百分位)**。
- **方法**：
  - block size 自适应：加大 block 直至 s(x̄_b) plateau
  - bootstrap：sampling-with-replacement；推荐敏感性测试确定迭代数（项目 n=10000 合理）
  - 多 replica：s(x̄) = s(x)/√n
- **对项目迁移**：误差棒计算 protocol 的最硬单篇锚点。

## [4] Knapp2018 ★★★

- **DOI**：10.1021/acs.jctc.8b00391
- **引文**：Knapp B, Ospina L, Deane CM. *J Chem Theory Comput* **14**(12):6127–6138 (2018)
- **标题**：Avoiding False Positive Conclusions in Molecular Simulation: The Importance of Replicas
- **核心发现**：基于 310,000 ns benchmark (100 × 3000 ns 小系统 + 100 × 100 ns TCR/MHC 大系统)；证明单次长 MD 结论不可复现；**经验法则 ≥ 5–10 replicas**；多短不如单长在绝大多数观测量上表现更好。
- **对项目迁移**：**seed ≥ 5 的硬锚点**。项目若计划 3 reps 需论证（或扩至 5）。

## [5] FlyvbjergPetersen1989 ★★☆

- **DOI**：10.1063/1.457480
- **引文**：Flyvbjerg H, Petersen HG. *J Chem Phys* **91**(1):461–466 (1989)
- **标题**：Error estimates on averages of correlated data
- **核心发现**：**Block averaging 源头文献**；重整化群思路处理时序自相关。N = M·n 长度轨迹二分迭代合并成越来越长的 block，记录合并后方差，直至 plateau → plateau 处即为校正后真实 SE。
- **对项目迁移**：项目处理单 seed 时序数据（非 seed 间独立样本）自相关时直接调用。若 seed 间本已独立则用处有限 (★★)；若对单 seed 内 ΔG(t) 做 block bootstrap 则 ★★★。

---

## 综合方法建议（项目 ΔΔG_sel 误差棒计算）

| 任务 | 方法 | 主要引用 |
|---|---|---|
| Seed 间 ΔΔG 点估计的 95% CI | seed-level bootstrap (n=10000 resamples) | [Grossfield2018] + [GenhedenRyde2015] |
| 单 seed 时序 ΔG(t) 自相关校正 | block averaging（plateau 法） | [FlyvbjergPetersen1989] + [Grossfield2018] |
| ΔΔG_sel 显著性 (ascr18 vs ascr3) | seed-level Welch t-test | [Mey2020] + [Grossfield2018] |
| Seed 数下限 | **≥5**（理想 ≥10） | [Knapp2018] |
| 每 seed 长度 | 200 ns（> [GenhedenRyde2015] 的 ps 级，可自论证保守） | [GenhedenRyde2015] + [Knapp2018] |
| 报告格式 | 95% CI (2.5–97.5 百分位) | [Grossfield2018] |

---

## 检索盲区

- **5 seeds × 200 ns 的 ΔΔG 选择性 95% CI benchmark 单篇**：未找到直接对照。项目可靠 [Knapp2018] 5–10 replica 经验 + [Grossfield2018] bootstrap 通用流程自行给 CI——方法学合法。
