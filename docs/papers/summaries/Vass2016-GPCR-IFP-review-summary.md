# Vass et al. (2016) — GPCR 交互指纹综述

> **原文**: Vass, M., Kooistra, A.J., Ritschel, T., Leurs, R., de Esch, I.J.P. & de Graaf, C. (2016). Molecular interaction fingerprint approaches for GPCR drug discovery. *Current Opinion in Pharmacology*, 30, 59–68.
> **DOI**: https://doi.org/10.1016/j.coph.2016.07.007

---

## 核心内容

综述了交互指纹 (Interaction Fingerprint, IFP) 在 GPCR 药物发现中的应用。IFP 将 3D 蛋白-配体相互作用压缩为 1D 二进制向量，每个残基编码一组交互类型（如氢键、疏水、离子对等），从而实现跨配体、跨受体的系统比较。

---

## 方法学要点

### IFP 编码方案

- **SIFt (Structural Interaction Fingerprint)**：原始框架，每个残基 7 bit（任意接触、主链正面、主链侧面、侧链正面、侧链侧面、极性、非极性）
- **SPLIF**：原子对级别编码（原子类型 + 拓扑路径），更高分辨率
- **IFP (de Graaf 实现)**：每残基 9 种交互类型 × 配体-蛋白方向 = 最多 11 bit

### 应用领域（Table 1）

| 受体 | 应用 | 关键发现 |
|------|------|---------|
| H1 受体 | 结合模式预测 | IFP 可区分活性/非活性态相互作用 |
| β2 受体 | 选择性分析 | 差异 IFP 识别亚型选择性残基 |
| H3/H4 受体 | 选择性优化 | IFP 指导从 H3→H4 选择性迁移 |
| GCGR | 变构位点 | IFP 发现非竞争性结合口袋残基 |

### 与本项目的关系

1. **差异 IFP 分析**：比较不同配体（ascr18 vs ascr3）在同一受体的接触指纹差异，可识别选择性决定残基 — 正是我们需要的方法
2. **BW 编号跨受体对齐**：综述强调 GPCRdb BW 编号对跨受体 IFP 比较的重要性（对 GprC/Gpr2/Gpr3 跨受体分析有指导意义）
3. **接触 vs 能量**：IFP 是定性结构分析，不依赖 scoring function 精度，比 ΔΔG 更鲁棒

---

## 实施挑战

- **结合口袋定义**：需预定义哪些残基纳入 IFP 计算（通常取配体周围 4-6 Å 内残基）
- **结构准备**：加氢方式、质子化状态影响氢键判定
- **对接 pose 质量**：IFP 基于 pose，如 pose 不可靠则 IFP 也不可靠
- **指纹可比性**：跨受体比较需统一残基编号（BW 编号）

---

## 关键结论

> "IFPs can be used to objectively compare binding modes from different perspectives... and have proven their value for virtual screening, binding mode prediction, selectivity analysis, and off-target prediction."

IFP 已在 GPCR 领域广泛验证，可用于：
1. 结合模式预测与验证
2. 虚拟筛选后处理（重排名）
3. 亚型选择性分析 — **最相关**
4. 脱靶预测

---

## 对本项目的启示

- 使用 ProLIF 实现 IFP 分析，以差异接触指纹识别 ascr18/ascr3 选择性残基
- IFP 分析不替代 ΔΔG，而是提供独立的结构证据维度
- 阳性对照：Hu2024 已验证的 N83、R281 等残基应出现在 GprC-ascr18 的接触列表中
