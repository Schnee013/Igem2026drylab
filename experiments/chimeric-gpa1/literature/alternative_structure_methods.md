# 替代起始结构生成方法评估

> **调研日期**: 2026-04-17
> **调研来源**: Phase 0B-2

---

## 背景

AF3 对已知实验复合物 Ste2×Gpa1 (PDB 7AD3) 的 ipTM=0.60，我们的嵌合体候选 ipTM 0.38-0.50。评估是否有更好的起始结构方法。

## 方法评估

### 1. AF3 + Template 修复 ⭐ 最高推荐

| 维度 | 评估 |
|------|------|
| 可行性 | **高** |
| 时间投入 | 1-3 天（修改 JSON + 重新提交，受每日限额约束） |
| 预期收益 | 合理的 ipTM 提升空间（之前可能缺少 `useStructureTemplate: true`） |
| 风险 | AF3 仅支持单链 template，不能直接传入复合物 template |

**关键发现**: 2026-04-13 truth audit 发现 chimeric Gpa1 batch 提交中 `useStructureTemplate` 字段缺失（severity HIGH）。如果确认之前 runs 未用 template，启用后是修复 ipTM 偏低的最低成本操作。

**操作方案**: 回查 `experiments/chimeric-gpa1/af3_predictions/` 下 JSON 输入文件，确认 template 设置；如缺失，重新提交 Top 候选。

### 2. Boltz-1 交叉验证 ⭐ 推荐

| 维度 | 评估 |
|------|------|
| 可行性 | **中高** |
| 时间投入 | 1-2 周（环境搭建 + 运行 + 比较） |
| 预期收益 | 独立验证；CASP15 protein-protein LDDT-PLI 65% |
| 风险 | 不太可能显著优于 AF3 |

Boltz-1 开源，可本地运行无限额限制。ABCFold 提供统一接口同时运行 AF3 + Boltz-1 + Chai-1。可作为 ensemble 策略：取多预测器共识或最佳结构。

### 3. Template-based 同源建模 (SWISS-MODEL / MODELLER) ❌ 不推荐

| 维度 | 评估 |
|------|------|
| 可行性 | **低** |
| 时间投入 | 2-3 周 |
| 预期收益 | 低于 AF3（AF3 已内化模板信息） |
| 风险 | Gpr2/Gpr3 与 Ste2 序列 identity <25%，低于可靠区 |

核心问题：GPCR-Gα 耦合界面涉及 ICL2/ICL3 loop 区域，恰好是同源建模最弱的环节。

### 4. 蛋白-蛋白对接 (HADDOCK / ClusPro) ❌ 不推荐

| 维度 | 评估 |
|------|------|
| 可行性 | **低** |
| 时间投入 | 3-4 周 |
| 预期收益 | 精度几乎确定低于 AF3 |
| 风险 | 膜蛋白性能差，我们无实验 restraints (crosslinking / HDX-MS) |

HADDOCK MemCplxDB benchmark 显示膜蛋白对接成功率低于可溶性蛋白。GPCR-Gα 界面涉及 TM6 大幅构象变化，rigid-body docking 无法捕捉。

### 5. ColabFold (AF2-Multimer) ❌ 不推荐

AF2-Multimer 在 GPCR-Gα 上已被 AF3 超越（CASP16 数据）。

## 推荐行动方案

| 优先级 | 行动 | 时间 | 前提 |
|--------|------|------|------|
| **P0** | 检查 AF3 template 设置 + 修复 + 重新提交 Top 候选 | 1-3 天 | 确认 JSON 中缺少 template |
| P1 | Boltz-1 交叉验证（至少 Top 3 候选 + Ste2-Gpa1 对照） | 1-2 周 | 有 GPU 空闲时间 |
| — | 同源建模 / 对接 | 不推荐 | — |

## 底线判断

AF3（启用 template）仍是当前最佳起始结构来源。ipTM 0.38-0.50 更可能反映真菌 GPCR-Gα 界面本身的预测难度（零实验结构、低同源性），而非方法选择问题。

---

## 引用来源

- SWISS-MODEL: PMC6030848
- GPCR 同源建模 ICL/loop 精度: PMC5571978
- AF3 custom templates: GitHub Issues #415, #416
- ABCFold: PMC12287924
- MemCplxDB (HADDOCK benchmark): Sci Dir 10.1016/j.jmb.2018.11.005
- Boltz-1: MIT jclinic
- ColabFold: Nature Methods 10.1038/s41592-022-01488-1
