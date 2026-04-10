---
direction: P0-molecular-docking
type: wet-lab-handoff
target_audience: wet-lab-team
last_updated: 2026-04-10
---

# 湿实验交接：受体突变候选位点

## 1. 摘要

计算预测了 **3 个强候选突变（Tier 1）** 和 **2 个次选候选（Tier 2）**，可增强 Gpr2/Gpr3 对 ascr#18（相对于 ascr#3）的识别选择性。

**核心结论**：优先验证 **Gpr2 M327A** — 该突变几乎不影响 ascr#18 亲和力，但大幅削弱 ascr#3 结合。

**方法**：AlphaFold 3 Server 预测突变体结构 → AutoDock Vina 单阶段对接（spacing=0.1 Å, exhaustiveness=200, box=40 Å, seed=42, Hu2024 参数） → ProLIF IFP 交叉验证 → Tier 1-4 分级。

**完整计算数据**：`experiments/docking-repro/mutagenesis/tier_recommendations_20260410.md`

---

## 2. 候选突变位点

### 评级标准

ΔΔG_sel = ΔΔG(ascr18) − ΔΔG(ascr3)。**负值 = 增强 ascr18 偏好**。

| Tier | ΔΔG_sel 范围 | 含义 |
|------|-------------|------|
| 1 | ≤ −0.48 kcal/mol | 强选择性增强（>3σ, σ=0.159） |
| 2 | −0.48 ~ −0.16 | 中度选择性增强（1~3σ） |

### P1（最高优先级）：Gpr2 M327A

| 指标 | 数值 |
|------|------|
| ΔΔG_sel | **−0.99 kcal/mol**（Tier 1 最强） |
| mutant ΔG(ascr18) | −6.74 kcal/mol（WT: −6.83, 几乎保留） |
| mutant ΔG(ascr3) | −5.35 kcal/mol（WT: −6.43, 大幅削弱） |
| ΔΔG(ascr18) | +0.09（微弱影响） |
| ΔΔG(ascr3) | +1.08（强烈削弱） |

**位置**：TM6 第一个残基（Met327），IFP 接触频率全场最高（51 次/18+16+17 across ascr18/3/7）。

**机制**：Met327 的侧链硫-甲基与 ascr#3 形成的疏水接触远强于与 ascr#18 的接触。丙氨酸替换后，ascr#3 失去关键结合面，ascr#18 几乎不受影响。

### P2：Gpr2 R59A

| 指标 | 数值 |
|------|------|
| ΔΔG_sel | **−0.52 kcal/mol** |
| ΔΔG(ascr18) | +0.31 |
| ΔΔG(ascr3) | +0.83 |

**位置**：TM2（Arg59），IFP 45 次（16/14/15）。

**机制**：ascr#3 比 ascr#18 更依赖 Arg59 的正电荷侧链。此结果与 v2 独立 pipeline 的分析一致（加强可信度）。

### P3：Gpr3 I141A

| 指标 | 数值 |
|------|------|
| ΔΔG_sel | **−0.79 kcal/mol** |
| ΔΔG(ascr18) | +0.53 |
| ΔΔG(ascr3) | +1.32 |

**位置**：TM4（Ile141），IFP 12 次（4/7/1）。

**机制**：双配体亲和力均下降，但 ascr#3 损失显著更大。Gpr3 WT 本身对 ascr#3 略有偏好（ΔG_sel=+0.20），该突变可**扭转偏好方向**，使 Gpr3 转为 ascr#18 偏好。

**注意**：Gpr3 整体对接亲和力偏弱（WT ΔG(ascr18)=−5.72），实验信号可能不如 Gpr2 突变体明显。

### 次选（Tier 2）：Gpr3 F170A 和 V138A

| 突变 | ΔΔG_sel | 位置 | 备注 |
|------|---------|------|------|
| F170A | −0.36 | ECL2（Phe170） | ascr18 亲和力略升（ΔΔG=−0.32），ascr3 不变 |
| V138A | −0.26 | TM4（Val138） | ascr3 削弱（ΔΔG=+0.23），ascr18 不变 |

---

## 3. 结构位置

### TM 螺旋归属

各候选位点在跨膜螺旋中的位置（来源：DeepTMHMM + UniProt 交叉验证）：

**Gpr2**（UniProt G1X9E2）：

| 螺旋 | 残基范围 | 候选位点 |
|------|---------|---------|
| TM2 | 62–82 | **R59**（TM2 前，N端侧） |
| TM6 | 327–347 | **M327**（TM6 第一个残基） |

**Gpr3**（UniProt G1XJN1）：

| 螺旋 | 残基范围 | 候选位点 |
|------|---------|---------|
| TM4 | 129–149 | **I141**, **V138** |
| ECL2 | ~170 | **F170**（ECL2 环区） |

### IFP 热图参考

- Gpr2 全残基接触热图：`experiments/docking-repro/analysis/ifp_heatmap_Gpr2.png`
- Gpr3 全残基接触热图：`experiments/docking-repro/analysis/ifp_heatmap_Gpr3.png`
- 三受体汇总热图：`experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png`

---

## 4. 实验建议

### 4.1 定点突变（Site-Directed Mutagenesis）

**优先构建顺序**（按信号强度和可行性）：

1. **Gpr2 M327A** — 信号最强，ascr18 亲和力保留最好
2. **Gpr2 R59A** — 强信号，两套独立计算均支持
3. **Gpr3 I141A** — Gpr3 最强候选，但整体亲和力偏弱

建议使用标准 SDM（如重叠延伸 PCR 或 Gibson Assembly）将目标密码子替换为 GCT/GCC（Ala）。

### 4.2 功能验证

**推荐读出体系**：BRET 或 cAMP 检测（取决于实验室已有平台）。

**实验设计**：

| 构建体 | ascr#18 剂量响应 | ascr#3 剂量响应 | 预期结果 |
|--------|-----------------|----------------|---------|
| WT Gpr2 | EC50 基线 | EC50 基线 | 两配体均有响应 |
| Gpr2 M327A | EC50 ≈ WT | EC50 右移 ≫ WT | ascr18 保留，ascr3 显著减弱 |
| Gpr2 R59A | EC50 轻微右移 | EC50 明显右移 | ascr3 减弱程度 > ascr18 |
| WT Gpr3 | EC50 基线 | EC50 基线 | ascr3 轻微偏好 |
| Gpr3 I141A | EC50 右移 | EC50 大幅右移 | 偏好翻转为 ascr18 |

**配体浓度**：建议 10⁻⁹ ~ 10⁻⁴ M 梯度（8-10 个点），覆盖预期 EC50 范围。

### 4.3 对照实验

| 对照 | 目的 |
|------|------|
| **WT 受体** | 正常响应基线 |
| **空载体** | 排除内源信号 |
| **GprC N60A**（可选） | Hu2024 已验证的功能丧失突变，Pipeline 阳性对照 |
| **GprC S44A**（可选） | Hu2024 阳性对照，ΔΔG_sel=+1.03，预期 ascr18 响应大幅下降 |

---

## 5. 计算局限性

| 局限性 | 影响 | 缓解措施 |
|--------|------|---------|
| **单 seed Vina** | 噪声 SD=0.159 kcal/mol；ΔΔG_sel < 0.48 不可信 | Tier 划分以 3σ 为阈值；Tier 1 均 > 3σ |
| **刚性受体** | 构象选择限于 AF3 单预测 | 单点突变对骨架影响通常 < 0.1 Å RMSD |
| **AF3 预测精度** | pLDDT > 90 区域可信，loop 区不确定 | 仅在 TM helix 域内对接 |
| **Vina 评分精度** | 绝对 ΔG 误差 ±1 kcal/mol | 仅用**排名**，不用绝对值做决策 |
| **alanine-only** | 仅测试丙氨酸替换，非全部 20 AA | 后续饱和扫描（5 位点 × 18 AA）已提交 AF3 |

**重要提醒**：所有 ΔΔG_sel 数值仅反映**相对排名趋势**，不是热力学精确值。实验验证是确认效果的唯一途径。

---

## 6. 饱和扫描结果（待补充）

已为 5 个 Tier 1/2 位点（Gpr2 M327/R59, Gpr3 I141/F170/V138）生成 90 个突变体（每位点 × 18 非 WT/非 Ala 氨基酸）的 AF3 提交文件。

**当前状态**：AF3 Server 结构预测已提交，等待返回后运行对接和分析。

**目的**：在确认丙氨酸替换有效的位点上，找到**最优替换氨基酸**（可能比 Ala 更好）。

结果将在本节补充。
