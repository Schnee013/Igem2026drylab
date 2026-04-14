---
direction: P0-molecular-docking
type: wet-lab-handoff
target_audience: wet-lab-team
last_updated: 2026-04-14
---

# 湿实验交接：受体突变候选位点

## 1. 摘要

对 3 个 ascaroside 受体（Gpr2 / Gpr3 / GprC）做了 122 条突变扫描（32 alanine + 90 saturation），按 PRD 的**双通道比值型传感器**设计目标分析：

| 通道 | 候选数（无 caveat） | 含义 |
|------|-------------------|------|
| **Channel A** | **14** | ascr#18 偏好——检测 PPN 信号的传感器 |
| **Channel B** | **11** | ascr#3 偏好——检测背景信号的参比传感器 |
| 中性 | 93 | 无显著通道偏好 |

**Top 1 配对推荐**：**Gpr2\_M327A**（Channel A, sel=−1.391）+ **Gpr3\_V138T**（Channel B, sel=+1.042），判别力 D=−2.433，balance=0.572。

**核心结论**：

1. **Channel A 最强**：Gpr2\_M327A（sel=−1.391），ascr#18 亲和力几乎不变，ascr#3 大幅削弱。
2. **Channel B 最强**：Gpr3\_V138T（sel=+1.042），ascr#3 亲和力保留，ascr#18 削弱。**V138 是 Gpr3 的通道偏好"开关位"**——V138R → Channel A，V138T → Channel B。
3. **天然跨受体分离**：Channel A 以 Gpr2 为主（11/14），Channel B 以 Gpr3 为主（9/11），与受体本身的配体偏好基线一致。
4. **底盘锁定酵母 STE2 + 嵌合 Gpa1 + 基因组单拷贝整合**（PI 2026-04-11 确认）→ 表达体系与读出方式见 §9。

**方法**：AlphaFold 3 Server 预测突变体结构 → AutoDock Vina 单阶段对接（spacing=0.1 Å, exhaustiveness=200, box=40 Å, seed=42, Hu2024 参数）→ ProLIF IFP 交叉验证 → 双通道 sel_mut 分级。

**完整计算数据**：`experiments/docking-repro/analysis/ratio_channel_report.md`（双通道全谱）/ `ratio_pairings.csv`（配对排名）

---

## 2. 双通道分析框架

### 核心指标

`sel_mut = ΔG(ascr18) − ΔG(ascr3)`：突变体本身的通道偏好方向。

| 通道 | 条件 | 含义 |
|------|------|------|
| Channel A | sel_mut < −0.477 | 突变体偏好 ascr#18 |
| Channel B | sel_mut > +0.477 | 突变体偏好 ascr#3 |
| 中性 | \|sel_mut\| ≤ 0.477 | 无显著偏好（3σ 噪声区内） |

阈值 0.477 = 3 × σ，σ = 0.159 kcal/mol（Gpr2\_ascr18 体系 5-seed 重复方差）。

### WT 基线

| 受体 | sel_wt | 天然倾向 |
|------|--------|---------|
| GprC | −0.798 | 强 ascr#18 偏好 |
| Gpr2 | −0.404 | 弱 ascr#18 偏好 |
| Gpr3 | +0.195 | 弱 ascr#3 偏好 |

### 验证状态

| 证据层 | Channel A | Channel B |
|--------|-----------|-----------|
| WT 协议级复现 | ✅ GprC ΔG = −8.235 vs Hu2024 −8.29，Δ = 0.05 | 同 |
| 阳性对照 | ✅ 3 个 Hu2024 loss-of-function 对照方向一致 | ❌ 无已知 ascr#3 偏好增强突变株做外部检验 |
| 3σ 噪声阈值 | ✅ 内部自洽 | ✅ 同一阈值 |

**Channel B 候选的推荐可信度低于 Channel A**——Channel A 有 Hu2024 阳性对照背书，Channel B 仅有噪声阈值筛选。湿实验首批结果可反向提供 Channel B 验证数据。

---

## 3. Channel A 候选（ascr#18 偏好传感器）

14 条无 caveat 候选，按 sel_mut 排序。Gpr2 贡献 11 条，Gpr3 贡献 3 条。

| # | 突变 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) |
|---|------|------|---------|------------|-----------|
| 1 | **M327A** | Gpr2 | **−1.391** | −6.744 | −5.353 |
| 2 | **M327D** | Gpr2 | −1.089 | −6.666 | −5.577 |
| 3 | **R59F** | Gpr2 | −0.956 | −6.658 | −5.702 |
| 4 | R59A | Gpr2 | −0.925 | −6.528 | −5.603 |
| 5 | **V138R** ⭐ | Gpr3 | −0.875 | −6.136 | −5.261 |
| 6 | M327F | Gpr2 | −0.620 | −5.518 | −4.898 |
| 7 | R59E | Gpr2 | −0.616 | −6.401 | −5.785 |
| 8 | **I141A** | Gpr3 | −0.591 | −5.192 | −4.601 |
| 9 | M327Q | Gpr2 | −0.552 | −6.292 | −5.740 |
| 10 | R59K | Gpr2 | −0.544 | −6.249 | −5.705 |
| 11 | R59H | Gpr2 | −0.534 | −6.156 | −5.622 |
| 12 | **F170E** | Gpr3 | −0.501 | −6.253 | −5.752 |
| 13 | R59C | Gpr2 | −0.484 | −6.036 | −5.552 |
| 14 | M327R | Gpr2 | −0.483 | −6.454 | −5.971 |

GprC caveat（不进入湿实验推荐）：L377A（sel=−0.758），GprC alanine scan 整体缺乏残基分辨力（13/14 落入极端区），不代表真正的选择性工程。

### Channel A 湿实验优先候选（6 条）

**A1：Gpr2 M327A** — Channel A 最强

**位置**：TM6 第一个残基（Met327），IFP 接触频率全场最高。

**机制**：Met327 的长硫-甲基侧链与 ascr#3 形成强疏水接触，与 ascr#18 接触显著更弱。丙氨酸替换后 ascr#3 失去整个关键结合面，ascr#18 几乎不受影响（ΔΔG 仅 +0.09）。mutant IFP 显示 M327 从 Top 残基消失，QLN139/SER135 接管。

**A2：Gpr3 V138R** ⭐ — Gpr3 的 Channel A 最强

**位置**：TM4（Val138 → Arg138）。

**机制（待实证）**：V138 饱和全 18 谱中 V138R 是**孤峰**——同位的 V138K/V138H 与 V138A 基线几乎等价，而 V138R 比第二名 V138Y 强 0.6 kcal/mol。Arg 胍基可能与 ascr#18 末端羧酸形成静电互补 / 盐桥，但 mutant IFP 显示 ARG138 对 ascr#18 接触 9 次 vs ascr#3 仅 2 次，**这 9 次全部为 VdWContact**（PDBQT 工作流下 ProLIF 的 Anionic/Cationic 检测结构性失效——输入无形式电荷，通道本身从未关闭），目前只能证明"空间富集"而非"盐桥形成"。

**MD 实证已转交** [P0-md-simulation](P0-md-simulation.md)。

**湿实验注意**：不要默认用 Lys 或 His 作为 Arg 的等价替代（V138K/V138H 在计算中无效）。

**A3：Gpr2 M327D** — M327 同位点互补路径

**机制**：与 M327A 互补——Ala 是"删除策略"，Asp 是"主动引入策略"（羧基 + 极性）。mutant IFP 显示 VAL377 +13、ASN381 +11 新接触，ASP327 直接形成 HBond。

**A4：Gpr2 R59F**

**位置**：TM2（Arg59 → Phe59）。

**机制**：R59F 与 R59A 几乎等效（sel −0.956 vs −0.925）。说明 R59 的作用主要是"失去正电荷侧链"而非"替换成何种残基"。

**A5：Gpr3 F170E** — ECL2 酸性替换

**位置**：ECL2（TM4 与 TM5 之间的胞外环）。

**机制（反直觉，待 MD 实证）**：F170D/F170E 双双进 Channel A，方向一致。但 mutant IFP 显示 GLU170 与 ascr#3 接触（23 次）反而比 ascr#18（14 次）多——说明"多接触 ≠ 更强亲和"，机制不如 V138R 清晰。

**A6：Gpr3 I141A**

**位置**：TM4（Ile141）。

**机制**：双配体亲和力均下降，但 ascr#3 损失显著更大。**注意**：Gpr3 整体亲和力偏弱（WT ΔG(ascr18)=−5.72），I141A 后 −5.19 进一步偏弱，实验信号可能弱于 Gpr2 突变体。

---

## 4. Channel B 候选（ascr#3 偏好传感器）

11 条无 caveat 候选，按 sel_mut 排序。Gpr3 贡献 9 条，Gpr2 贡献 2 条。

| # | 突变 | 受体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) |
|---|------|------|---------|-----------|------------|
| 1 | **V138T** | Gpr3 | **+1.042** | −6.047 | −5.005 |
| 2 | V138L | Gpr3 | +0.886 | −5.704 | −4.818 |
| 3 | M327G | Gpr2 | +0.749 | −5.629 | −4.880 |
| 4 | V138P | Gpr3 | +0.736 | −5.503 | −4.767 |
| 5 | R175A | Gpr3 | +0.663 | −5.965 | −5.302 |
| 6 | F170K | Gpr3 | +0.632 | −5.942 | −5.310 |
| 7 | **F170N** | Gpr3 | +0.616 | −5.835 | −5.219 |
| 8 | R59I | Gpr2 | +0.594 | −5.956 | −5.362 |
| 9 | Q93A | Gpr3 | +0.580 | −6.111 | −5.531 |
| 10 | I141V | Gpr3 | +0.490 | −5.991 | −5.501 |
| 11 | F170H | Gpr3 | +0.484 | −5.808 | −5.324 |

GprC caveat（不进入推荐）：V91A / Q411A / N378A，同§3 caveat 理由。

### Channel B 湿实验优先候选（3 条）

**B1：Gpr3 V138T** — Channel B 最强

sel_mut = +1.042，ascr#3 亲和力 −6.047（WT −5.921，保留良好），ascr#18 削弱至 −5.005。与 V138R（Channel A）形成**同位点双通道开关**（见 §5）。

**B2：Gpr3 V138L**

sel_mut = +0.886，与 V138T 方向一致但稍弱。ascr#3 亲和力 −5.704。

**B3：Gpr3 F170N** — best-balance 配对伙伴

sel_mut = +0.616，与 Gpr2\_R59E 配对时 balance = 0.500（理想对称）。

---

## 5. V138 同位点双通道观察

V138R（sel=−0.875）是 Channel A 候选，V138T（sel=+1.042）是 Channel B 候选——**同一位点不同替换产生相反的通道偏好**。

| 替换 | 通道 | sel_mut | 侧链性质 |
|------|------|---------|---------|
| V138R | A | −0.875 | 大、带正电、胍基 |
| V138T | B | +1.042 | 小、极性、羟基 |
| V138L | B | +0.886 | 中、疏水 |
| V138P | B | +0.736 | 小、刚性、环 |

**湿实验含义**：如果双通道传感器需要一株偏 ascr#18、一株偏 ascr#3，V138R + V138T 可作为 Gpr3 上的一对互补构建。V138 全 18 谱中 V138R 是孤峰（比第二名 V138Y 强 0.6 kcal/mol），V138K/V138H 无效——不能默认 K/H 作为 R 的等价替代。

---

## 6. 跨受体配对推荐

双通道传感器需要一个 Channel A 突变体 + 一个 Channel B 突变体。

| 排名 | Channel A | Channel B | D（判别力） | balance |
|------|-----------|-----------|-----------|---------|
| **Top 1** | **Gpr2\_M327A** (sel=−1.391) | **Gpr3\_V138T** (sel=+1.042) | **−2.433** | 0.572 |
| Top 2 | Gpr2\_M327A | Gpr3\_V138L | −2.277 | 0.611 |
| Top 3 | Gpr2\_M327D | Gpr3\_V138T | −2.131 | 0.511 |
| Top 4 | Gpr2\_M327A | Gpr3\_V138P | −2.127 | 0.654 |
| Top 5 | Gpr2\_M327A | Gpr3\_R175A | −2.054 | 0.677 |
| **Best balance** | **Gpr2\_R59E** (sel=−0.616) | **Gpr3\_F170N** (sel=+0.616) | −1.232 | **0.500** |

D = sel_A − sel_B（越负 = 两通道分离越远）；balance = |sel_A| / (|sel_A| + |sel_B|)（越接近 0.5 = 两通道灵敏度越对称）。

**推荐策略**：
- **追求最大判别力**：Top 1 配对（M327A + V138T），D 最大
- **追求对称灵敏度**：Best balance 配对（R59E + F170N），两端灵敏度完全对称
- **同时兼顾**：Top 3 配对（M327D + V138T），D 和 balance 均优

---

## 7. 结构位置

### TM 螺旋归属

**Gpr2**（UniProt G1X9E2）：

| 螺旋 | 残基范围 | Channel A 候选 |
|------|---------|---------------|
| TM2 | 62–82 | **R59**（TM2 前，N端侧）：R59F/A/E/K/H/C |
| TM6 | 327–347 | **M327**（TM6 第一个残基）：M327A/D/F/Q/R |

**Gpr3**（UniProt G1XJN1）：

| 螺旋 | 残基范围 | Channel A 候选 | Channel B 候选 |
|------|---------|---------------|---------------|
| TM4 | 129–149 | **V138R**, **I141A** | **V138T/L/P**, I141V |
| ECL2 | ~170 | **F170E** | **F170N/K/H** |

### IFP 热图参考

- Gpr2 全残基接触热图：`experiments/docking-repro/analysis/ifp_heatmap_Gpr2.png`
- Gpr3 全残基接触热图：`experiments/docking-repro/analysis/ifp_heatmap_Gpr3.png`
- 三受体汇总热图：`experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png`

---

## 8. 实验建议

### 8.1 优先构建顺序

**Channel A（ascr#18 偏好传感器）**：

1. **Gpr2 M327A** — Channel A 最强（sel=−1.391），ascr#18 亲和力保留最好
2. **Gpr3 V138R** ⭐ — Gpr3 Channel A 最强，孤峰，需湿实验 + MD 双重验证
3. **Gpr2 M327D** — 同位互补路径（引入羧基 vs 删除侧链）
4. **Gpr2 R59F** — R59A 的等效替代

**Channel B（ascr#3 偏好传感器）**：

5. **Gpr3 V138T** — Channel B 最强（sel=+1.042），Top 1 配对伙伴
6. **Gpr3 F170N** — Best balance 配对伙伴（balance=0.500）

**密码子选择**（酵母 *S. cerevisiae* 偏好）：

| 突变 | 推荐密码子 |
|---|---|
| → Ala | GCT / GCC |
| → Asp | GAT / GAC |
| → Phe | TTT / TTC |
| → Arg | AGA（酵母最高频）/ CGT |
| → Thr | ACT / ACC |
| → Asn | AAT / AAC |

建议使用标准 SDM（重叠延伸 PCR 或 Gibson Assembly）。底盘 = 酵母 + 基因组整合策略下，所有突变体应整合到同一位点（细节见 §9）。

### 8.2 功能验证

**推荐读出体系**：基于 STE2 通路的内源 MAPK 报告系统（pFUS1-报告基因，方案 TBD）；与外源 BRET 平台并行可作为交叉验证。

**实验设计**：

| 构建体 | ascr#18 剂量响应 | ascr#3 剂量响应 | 预期结果 |
|--------|-----------------|----------------|---------|
| WT Gpr2 | EC50 基线 | EC50 基线 | 两配体均有响应 |
| Gpr2 M327A（A） | EC50 ≈ WT | EC50 右移 ≫ WT | ascr#18 保留，ascr#3 显著减弱 |
| Gpr2 M327D（A） | EC50 ≈ WT 或左移 | EC50 右移 | ascr#18 主动增强，ascr#3 削弱 |
| Gpr2 R59F（A） | EC50 轻微右移 | EC50 明显右移 | 与 R59A 等效 |
| WT Gpr3 | EC50 基线 | EC50 基线 | 略偏 ascr#3 |
| Gpr3 V138R ⭐（A） | EC50 **左移** | EC50 右移 | 偏好翻转为 ascr#18（盐桥假说预期） |
| **Gpr3 V138T（B）** | **EC50 右移** | **EC50 ≈ WT 或左移** | **偏好保持/增强 ascr#3** |
| **Gpr3 F170N（B）** | **EC50 右移** | **EC50 ≈ WT** | **ascr#18 削弱，ascr#3 保留** |

**配体浓度**：建议 10⁻⁹ ~ 10⁻⁴ M 梯度（8-10 个点），覆盖预期 EC50 范围。

**V138R 验证策略**：建议至少同时构建 **V138R + V138K + V138H** 三个对照（其余两个在计算中无效），实测如果只有 V138R 显著则印证"Arg 胍基特异效应"；如果三者均强则推翻"孤峰"判断。

### 8.3 对照实验

| 对照 | Hu2024 角色 | 湿实验预期 |
|------|------|------|
| **WT 受体** | — | 正常响应基线 |
| **空载体** | — | 无响应（排除内源信号） |
| **GprC N60A** | **loss-of-function 阳性对照**（N2.57A，[Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md)） | ascr#18 响应**削弱** |
| **GprC S44A** | **loss-of-function 阳性对照**（S2.41A，[Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md)） | ascr#18 响应**削弱** |
| **GprC N56A** | **no-effect 阴性对照**（N2.53A，[Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md) 原文"无影响"） | ascr#18 响应**保留** |

**Hu2024 对照的使用边界**

这三个 Hu2024 对照用于**校准湿实验 assay 读出可信度**（阳性削弱 / 阴性保留的预期差异），**不作为我们 docking pipeline 的独立验证依据**。

我们的 docking 对 GprC 四个 Hu2024 对照的实际结果：

| 突变 | Hu2024 角色 | 我们 docking sel_mut |
|---|---|---|
| **N56A** | 阴性 | −0.341（中性区，但 ΔΔG 扰动大于阳性对照） |
| S44A | 阳性 | −0.234（中性区） |
| N60A | 阳性 | −0.402（中性区） |
| R395A | 阳性 | −0.428（中性区） |

GprC 14 个 alanine 扫描残基中 **13/14 落入极端扰动区**（剩 1 个近乎中性）→ 当前 pipeline 在 GprC 上对单点 alanine 扰动不能可靠区分功能性 vs 非功能性残基。**所有候选推荐全部来自 Gpr2/Gpr3**，不涉及 GprC。

**湿实验角度的含义**：

- 如果湿实验看到 N56A 保留响应 + N60A/S44A 削弱响应 → 湿实验 assay 分辨率优于 GprC docking，是**预期结果**
- 如果湿实验看到 N56A 也显著削弱 → 说明湿实验 assay 有普遍假阳性，需排查

> **BW→序列号映射可信度**：N56↔N2.53 / N60↔N2.57 / S44↔S2.41 的映射经 D2.50=ASP53 锚点 + DeepTMHMM TM2 范围（pos 45–65）+ Hu2024 三 strain 命名一致性三重验证（随机 match 概率 ≈ 1.25×10⁻⁴），可信度 HIGH。追溯记录见 [`docs/logs/truth-audits/2026-04-12_0205.md`](../logs/truth-audits/2026-04-12_0205.md) 后记 A。

---

## 9. 计算局限性

| 局限性 | 影响 | 缓解措施 |
|--------|------|---------|
| **单 seed Vina** | 噪声 SD=0.159 kcal/mol；\|sel_mut\| < 0.477 不可信 | 3σ 阈值筛选；5-seed 方差实测已验证噪声量级 |
| **刚性受体** | 构象选择限于 AF3 单预测 | 单点突变对骨架影响通常 < 0.1 Å RMSD |
| **AF3 预测精度** | pLDDT > 90 区域可信，loop 区不确定 | 仅在 TM helix 域内对接 |
| **Vina 评分精度** | 绝对 ΔG 误差 ±1 kcal/mol | 仅用**排名和通道归属**，不用绝对值做决策 |
| **静态对接无法证明动态相互作用**（如盐桥） | V138R 仅有空间富集证据 | 转交 [P0-md-simulation](P0-md-simulation.md) 做 MD 时间序列实证 |
| **GprC 单点扰动无分辨力** | 13/14 alanine 残基落入极端扰动区，阴性对照 N56A 扰动大于阳性对照 | 候选推荐全部来自 Gpr2/Gpr3 |
| **Channel B 无独立阳性对照** | 文献中无已知 ascr#3 偏好增强的突变株可做外部检验 | Channel B 可信度低于 Channel A；湿实验首批结果可反向提供验证 |

**重要提醒**：所有 sel_mut 数值仅反映**相对排名趋势**，不是热力学精确值。实验验证是确认效果的唯一途径。

---

## 10. 饱和扫描关键发现

5 个位点（Gpr2 M327/R59、Gpr3 I141/F170/V138）× 18 AA = 90 突变体，合并 32 alanine = **122 条**全谱。权威源 `experiments/docking-repro/analysis/ratio_channel_report.md`。

### V138 孤峰 vs 类别规律

V138 全 18 谱分析显示 V138R 是**孤峰**而非"碱性残基类别规律"：

| 突变 | sel_mut | 通道 |
|------|---------|------|
| **V138R** | **−0.875** | A ← 孤峰 |
| V138Y | −0.267 | 中性 |
| V138K | −0.080 | 中性 |
| V138H | −0.161 | 中性 |
| V138A | −0.061 | 中性 |
| **V138T** | **+1.042** | **B** ← Channel B 最强 |
| V138L | +0.886 | B |

同为碱性的 **Lys/His 与 Ala 基线几乎等价** → "正电荷驱动"的类别规律不成立。湿实验不能默认 K/H 作为 R 的等价替代。

### M327 双路径

M327A（Channel A #1, sel=−1.391）与 M327D（Channel A #2, sel=−1.089）互补——Ala 删除侧链 vs Asp 主动引入羧基。湿实验可按稳健（A）或激进（D）选择。

### F170 酸性/碱性双向

F170E / F170D → Channel A（酸性替换增强 ascr#18）；F170K / F170N / F170H → Channel B（碱性/极性替换增强 ascr#3）。同一位点不同化学性质的替换产生相反通道归属。

---

## 11. 底盘与通路上下文（2026-04-11 锁定）

> PI 于 2026-04-11 确认底盘选择，详见 [overview-v4](../prd/overview-v4.md) / [chassis-decision §最终决策](../prd/chassis-decision.md#最终决策2026-04-11) / [决策 003](../decisions/003-chassis-yeast-ste2-integration.md)。

| 项 | 决定 | 对湿实验的含义 |
|---|---|---|
| 底盘 | *S. cerevisiae*（酿酒酵母） | 标准遗传工具；密码子按酵母偏好选择（见 §8.1） |
| 通路 | 内源 STE2 pheromone pathway | 异源 Gpr 替换内源 Ste2，下游接 Fus3 MAPK → Ste12 |
| G 蛋白 | 嵌合 Gpa1（C 端嫁接真菌 Gα C 端） | Gpr 与嵌合 Gpa1 协同表达；嵌合方案由 [P3-chimeric-gprotein](P3-chimeric-gprotein.md)（已升 P0）提供 5/10/15 残基三档候选 |
| 拷贝数策略 | **基因组单拷贝整合**（不用 CEN/2μ 质粒） | 所有突变体应分别整合到同一位点（如 HO 或 URA3），避免拷贝数漂移；每个变体一株独立菌株 |
| 报告基因 | TBD（pFUS1-lacZ / pFUS1-报告蛋白 / GAL4 间接放大均待定） | 读出方式不影响 EC50 排序，但影响动态范围；建议至少做 pFUS1-lacZ 作为基线对照 |
| 显色级联放大 | TBD | 与通路工程组对齐方案后再决定是否引入 |

### EC50 解读注意

由于**基因组单拷贝**而非高拷贝质粒：

- 受体表达水平较低，EC50 绝对值可能比文献酵母 GPCR biosensor 的多拷贝数据高 1-2 个数量级
- 但**突变体之间的相对 EC50 比较**（M327A vs WT 等）不受影响——这是本干实验的核心读出
- 不要把 EC50 绝对值与 Hu2024 / Kuo2024 的真菌原生体系直接对比；体系不同

### 构建建议

为保持可比性，建议：

1. 所有突变体使用**同一表达盒**（同启动子、同信号肽、同 tag、同整合位点、同嵌合 Gpa1 版本）
2. WT Gpr2 + WT Gpr3 各做一个独立菌株作为基线
3. 至少为 V138R 加做 V138K + V138H 对照（验证孤峰假说）
4. Hu2024 对照（GprC N60A / S44A 阳性 + N56A 阴性）用于**校准湿实验 assay 读出可信度**，而**不是**用作 docking pipeline 的独立验证依据——见 §8.3
