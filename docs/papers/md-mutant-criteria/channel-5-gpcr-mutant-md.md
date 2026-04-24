# Channel 5 · GPCR 突变体 MD 协议参考（详版）

**检索目标**：Class A GPCR / 嗅觉受体 / *C. elegans* 化感受器 / 真菌 GPCR 的突变体 MD 实验设计模板（时长 / reps / 体系 / 指标 / 统计）。

**本通道价值**：C1–C4 只给阈值和方法学，本通道给**协议模板**——别人怎么跑的，项目怎么抄。

---

## 方向 A · Class A GPCR 点突变 MD（协议模板）

### [1] Verma2018 ★★★

- **DOI**：10.1371/journal.pcbi.1005948
- **引文**：Verma RK, Abramyan AM, Michino M, Free RB, Sibley DR, Javitch JA, Lane JR, Shi L. *PLOS Comput Biol* **14**(1):e1005948 (2018)
- **标题**：The E2.65A mutation disrupts dynamic binding poses of SB269652 at the dopamine D2 and D3 receptors
- **MD 设置**：**145 条独立轨迹 / 累计 ~76.5 μs**；4 体系（D2 WT / D2 mut / D3 WT / D3 mut）；Desmond + POPC + 显式水
- **指标**：Markov State Model 亚稳态占比、H-bond 频率、TM2e–TM7e / TM1e–TM3e 距离、N-term 簇 RMSD、MM/GBSA 逐残基分解
- **关键数字**：WT 两亚稳态 52/48%；E2.65A 下 dominant 态升至 60%；N-term 簇占比偏移 ~70%
- **对项目迁移**：**"突变如何改变 pose 动态分布"最佳模板**。MSM + MM/GBSA 逐残基的组合比单点 ΔΔG 更严谨，适合回答 A 层"突变是否改变选择性"。

### [2] Keranen2014 ★★★

- **DOI**：10.1371/journal.pone.0108492
- **引文**：Keränen H, Gutiérrez-de-Terán H, Åqvist J. *PLoS ONE* **9**(10):e108492 (2014)
- **标题**：Structural and energetic effects of A2A adenosine receptor mutations on agonist and antagonist binding
- **MD 设置**：FEP；**30 个 alanine scan 突变 × 2 配体**（NECA agonist + ZM241385 antagonist）；**7 次独立重复/体系**，单次 3.5–5.6 ns，累计 50–80 ns/mutation；球形 25/34 Å 水盒
- **指标**：FEP ΔΔG_bind；精度 0.7 kcal/mol；hysteresis 0.25 kcal/mol
- **关键数字**：正确预测 8 个"结合信号消失"突变；水介导接触关键
- **对项目迁移**：**饱和扫描 FEP 协议直接模板**。Gpr2 saturation scan（M327 + R59 等）可照搬 "7 reps × 50 ns" 格式；FEP 比 MM-PBSA 更严谨做突变能量排序。

### [3] Billesbolle2023 ★★★

- **DOI**：10.1038/s41586-023-05798-y
- **引文**：Billesbølle CB, de March CA, van der Velden WJC, Ma N, Tewari J, Liu Q, Vaidehi N, Matsunami H, Manglik A. *Nature* **615**(7953):742–749 (2023)
- **标题**：Structural basis of odorant recognition by a human odorant receptor
- **MD 设置**：**5 × 1 μs 重复**（propionate-bound / apo / Q181D 三态）
- **指标**：contact frequency、残基距离、rotamer 分析、RMSD、0.8 Å cutoff 簇聚；实验 EC50 交叉
- **关键数字**：Q181D 组成性激活；ECL3 构象为激活枢纽
- **对项目迁移**：**最接近项目情境**——短链配体（propionate ≈ ascaroside 极性头）+ Class A orphan 受体 + 多突变 + μs 级 + 实验-计算闭环。**5 × 1 μs 可作项目突变 MD 下限**。

### [4] Choi2023 ★★★

- **DOI**：10.1038/s41467-023-43983-9
- **引文**：Choi C, Bae J, Kim S, Lee S, Kang H, Kim J, Bang I, Kim K, Huh WK, Seok C, Park H, Im W, Choi HJ. *Nat Commun* **14**(1):8105 (2023)
- **标题**：Structure and activation mechanism of an odorant receptor (OR52 consensus)
- **MD 设置**：**5 × 1 μs 重复**（apo + octanoate-bound）
- **指标**：TM 间距、关键残基接触网络；实验 cAMP dose-response EC50
- **关键数字**：TM5/6 "opening" 为 odorant entry 通路；TM6 双向运动
- **对项目迁移**：**F14A / F96A / F170A 组合突变正对应项目 F170 位点**；5 μs 重复 + apo/holo 配对是可直接复用的设计。与 [3] 一起确立 2023 后嗅觉受体 MD 协议新标准。

---

## 方向 B · 嗅觉 / 化感 GPCR

### [5] Ahmed2018 ★★☆

- **DOI**：10.1073/pnas.1713026115
- **引文**：Ahmed L, Zhang Y, Block E et al. *PNAS* **115**(17):E3950–E3958 (2018)
- **标题**：Molecular mechanism of activation of human musk receptors OR5AN1 and OR1A1
- **方法**：同源建模 + MD + QM/MM；Tyr260 (TM6) + Phe105/Phe194/Phe207 突变
- **关键数字**：疏水 77% + H-bond 13% 贡献分解；Tyr260→Ala 消除 muscone 响应
- **对项目迁移**：QM/MM 疏水/极性贡献分解；对 ascaroside 疏水核 + 极性头基双组分模式有参考价值。

### [6] Wang2024 ★☆☆

- **DOI**：10.3389/fmolb.2024.1498796
- **引文**：Wang J et al. *Front Mol Biosci* **11**:1498796 (2024)
- **类型**：综述 — odor 分子-OR 结合机制汇总
- **对项目迁移**：背景参考，未给具体协议。

---

## 方向 C · *C. elegans* / Ascaroside 受体计算

### [7] Milletti2021 ★★☆

- **DOI**：10.1007/s10822-021-00434-1
- **引文**：Milletti F et al. *J Comput Aided Mol Des* **35**:133–144 (2021)
- **方法**：3D Zernike polynomial 结合位点识别 + homology model（**无 MD**）
- **对项目迁移**：唯一检索到的 *C. elegans* 化感 GPCR 计算工作；对 SRX/SRG 家族背景有用。建议 Read fulltext 确认是否触及 ascaroside。

**[方向 C 其它盲区]**：SRBC-64/66、SRX-43/44、icas#9 相关——**无合适 MD 或大规模 docking 文献**。Park et al. 2012 (10.1073/pnas.1202216109) 仅遗传学 + 光亲和标记，无 3D 建模。**这是项目真正的新颖性落点**。

---

## 方向 D · 真菌 GPCR

### [8] Gao2024 ★★☆

- **DOI**：10.1007/s00018-024-05160-z
- **引文**：Gao Y et al. *Cell Mol Life Sci* **81**(1):241 (2024)
- **靶点**：*Aspergillus ochraceus* GprC；glucose + 9-HODE
- **方法**：AF2 + AutoDock Vina，**无 MD**
- **关键数字**：两配体同为 −4.6 kcal/mol，绑定位点不同（ALA335 vs SER28）
- **对项目迁移**：**项目近亲**——同样真菌 GprC + AF 建模 + Vina 对接。项目补 MD 即是方法学推进。注意：该文靶配体是 glucose/oxylipin，非 ascaroside。

---

## 方向 E · 综述（方法学约束）

### [9] LamimRibeiroFilizola2019 ★★☆

- **DOI**：10.1016/j.sbi.2019.03.016
- **引文**：Lamim Ribeiro JM, Filizola M. *Curr Opin Struct Biol* **55**:121–128 (2019)
- **内容**：GPCR 变构 MD 综述（enhanced sampling、MSM、FEP）；指出"百微秒级才能收敛 free energy"；推荐指标组合：ligand RMSD + H-bond network + Trp6.48 χ 角
- **对项目迁移**：方法论约束参考，帮判断项目时长是否充分。

---

## 项目可直接借鉴的协议模板（汇总）

| 维度 | 可采用设计 | 出处 |
|------|-----------|------|
| **重复数** | 5 × 1 μs 独立 replica（apo + holo 配对） | [Billesbolle2023] [Choi2023] |
| **多突变扫描** | 每突变 7 reps × 50–80 ns（FEP） | [Keranen2014] |
| **动态 pose 分析** | 累计 ~75 μs + MSM | [Verma2018] |
| **能量分解** | MM/GBSA 逐残基 / QM/MM 疏水+极性比 | [Verma2018] [Ahmed2018] |
| **指标组合** | ligand RMSD + H-bond 频率 + TM5-6 距离 + contact frequency | [Billesbolle2023] [Choi2023] [LamimRibeiro2019] |
| **实验交叉** | MD 预测 → EC50/cAMP dose-response 验证 | [Billesbolle2023] [Choi2023] [Ahmed2018] |

---

## 关键结论（针对原 plan TODO "用户 Zotero GPR 突变体 MD" 盲区）

1. **时长标定**：μs 级 × 3–5 reps 是 2023 年后嗅觉 GPCR 新标准（[3][4]）。项目 C4 嵌合 MD 500 ns × 3 reps × 4 体系属"够用但偏短"；A 层突变体 MD 建议向此看齐。
2. **配对设计**：WT + mutant × apo + holo 四态配对是主流 ([3][4])。项目现有设计已覆盖 apo/holo，补 WT 对照 replica 即完备。
3. **饱和扫描统计范式**：[Keranen2014] A2A alanine scan 的 "30 突变 × 7 reps × 50–80 ns + FEP" 可直接照搬到 Gpr2 M327/R59 saturation scan。
4. **OR-ascaroside 空白性**：方向 C 仅 [Milletti2021] 一条半相关，意味着项目本身即是**方法学新颖性所在**。不必硬套前人协议，可自定义指标组合。
5. **真菌侧进展**：[Gao2024] 到 docking 为止，项目 MD 即可宣告方法学推进。

---

## Zotero 库查询结果

用户 Zotero 本地库以 `mcp__zotero__zotero_search_items` 查询 "GPCR mutant molecular dynamics" / "ascaroside receptor" 均返回**孤立 PDF attachment**（"No authors" / "No Date"，无 parent item 元数据）。**无法自动提取 DOI**。建议用户：

- 在 Zotero 中将这些 PDF 挂到 parent item 并补元数据；或
- 手动提供"做过 GPR 突变体 MD 的文章"的 DOI 清单（按原 plan 约定）
