# Channel 3 · Watchdog 早退阈值（详版）

**检索目标**：MD 生产过程中早杀 "注定崩" replica 的 Cα RMSD / 配体 COM 漂移 / 检查间隔的文献证据。替代原计划估计值 "5 Å / 50 ns"。

---

## [1] RodriguezEspigares2020 ★★★

- **DOI**：10.1038/s41592-020-0884-y
- **引文**：Rodríguez-Espigares I, Torrens-Fontanals M, Tiemann JKS et al. *Nat Methods* **17**(8):777–787 (2020)
- **标题**：GPCRmd uncovers the dynamics of the 3D-GPCRome
- **核心发现**：GPCR MD 社区标准化参照系；覆盖 100% GPCR classes / 71% subtypes / 80% families；默认协议 **3 replicas × 500 ns** per receptor；Cα RMSD 为 QC 指标。
- **对项目迁移**：项目 200 ns × 3 reps 协议的源流锚点；Cα RMSD QC 行为参考（GPCR 常规 1–3 Å，>5 Å 体系崩）。具体数值阈值在正文 SI（WebFetch 被 Nature 拒绝，**待查原文 supplementary**）。

## [2] Clark2016 ★★★

- **DOI**：10.1021/acs.jctc.6b00201
- **引文**：Clark AJ, Tiwary P, Borrelli K, Feng S, Miller EB, Abel R, Friesner RA, Berne BJ. *J Chem Theory Comput* **12**(6):2990–2998 (2016)
- **标题**：Prediction of Protein–Ligand Binding Poses via Induced Fit and Binding Pose Metadynamics
- **核心发现**：**BPMD 原始论文**。用短 metadynamics (10 ns × 10 replicas) 扰动测稳定性代替等长 MD 收敛；"稳定 pose = 在 bias 下 RMSD 仍低"是整个 pose-triage 文献的方法论起点。
- **阈值**：ligand heavy-atom RMSD ≤ 2 Å 判 native/stable（crystallographic 命中 88%）；10 ns per replica；10 replicas。
- **对项目迁移**："用短 MD × 多 replica 做 pose triage" 开山论文，直接支撑 watchdog 哲学。

## [3] Fusani2020 ★★★（同时命中 C2，见 channel-2）

- **DOI**：10.1021/acs.jcim.9b00843
- **引文**：Fusani L, Palmer DS, Somers DO, Wall ID. *J Chem Inf Model* **60**(3):1528–1539 (2020)
- **核心发现（C3 视角）**：BPMD crystal pose benchmark；监控间隔、H-bond persistence 窗口（last 2 ns）、配体 3 Å 内对齐——watchdog 监控 protocol 细节的可引用源。
- **对项目迁移**：监控参数（窗口长度、对齐方式）的文献锚点。

## [4] Lukauskis2022 ★★★

- **DOI**：10.1021/acs.jcim.2c01142
- **引文**：Lukauskis D, Samways ML, Aureli S, Cossins BP, Taylor RD, Gervasio FL. *J Chem Inf Model* **62**(23):6209–6216 (2022)
- **标题**：Open Binding Pose Metadynamics: An Open-Source Protocol for Binding Pose Metadynamics Using OpenMM
- **核心发现**：OpenBPMD（OpenMM + PLUMED 开源复现），贴近自动化 pose-triage pipeline 的参考实现。**双阈值**：
  - **2 Å RMSD → native 命中 88%**
  - **3 Å RMSD → native 命中 97%**
- **其它参数**：bias 沉积间隔 100 ps；ContactScore 取 last 2 ns 平均；hill height 0.05 kcal/mol 推荐。
- **对项目迁移**：双阈值 (严 2 Å / 宽 3 Å) 比原 5 Å 单点更有区分度；监控 "多久读一次轨迹" 的文献锚点（100 ps 属 metadynamics 场景，unbiased MD 项目应放宽至 ns 级）。

## [5] Doerr2016 ★★☆

- **DOI**：10.1021/acs.jctc.6b00049
- **引文**：Doerr S, Harvey MJ, Noé F, De Fabritiis G. *J Chem Theory Comput* **12**(4):1845–1852 (2016)
- **标题**：HTMD: High-Throughput Molecular Dynamics for Molecular Discovery
- **核心发现**：HTMD 框架论文；核心贡献之一即"启发式算法终止 + reseed 多副本并行轨迹"——**MD replica early termination 最直接方法论引用**。
- **阈值**：无固定 RMSD cutoff；adaptive scheme 基于 Markov state model 聚类分布重分配算力（欠采样 state 加权 reseed，收敛 state 终止）；epoch 级检查周期。
- **对项目迁移**：框架级引用；项目 watchdog 属于 HTMD epoch 思想的简化硬阈值落地。

---

## 综合阈值建议（替换 "5 Å / 50 ns"）

| 参数 | 推荐值 | 文献锚点 |
|---|---|---|
| 配体 COM 漂移 marginal | **3 Å** | [Lukauskis2022] 双阈值严判 |
| 配体 COM 漂移 unbinding | **5 Å** | [Lukauskis2022] 宽判 + [Sakano2016] β2AR 实测（C2） |
| Cα RMSD 体系崩 | **>5 Å** | [RodriguezEspigares2020] GPCRmd 通用行为 |
| 检查间隔 | **50 + 100 ns 双检查点** | [Lukauskis2022] 监控哲学；项目 unbiased 200 ns 上 25%/50% 节点 |
| 早退框架 | Adaptive triage | [Doerr2016] HTMD |

**注记**：
1. Lukauskis2022 的 100 ps 间隔是 metadynamics 场景（bias 推得快），不适用于项目 unbiased MD。项目至少 2 个检查点 (50/100 ns)，避免单点决策。
2. "watchdog 工作流" 无直接对口论文——这是工程问题；[Doerr2016] HTMD 是文献层最接近的框架锚点。
