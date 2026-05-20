---
direction: P0-molecular-docking
type: wet-lab-handoff
target_audience: wet-lab-team
last_updated: 2026-05-20
---

# 湿实验交接：受体突变候选位点

## 1. 当前结论

本版已纳入 Gpr2 3D offset 重跑、Gpr3 方案 F、Gpr3 D100/R164/R167 supplemental docking、refreshed ratio analysis 和 Top 候选 ProLIF IFP。旧版 `Gpr2_M327A + Gpr3_V138T` 配对不再作为当前构建推荐。

当前主推双通道组合：

| 优先级 | Channel A（ascr#18 偏好） | Channel B（ascr#3 偏好） | D | balance | 用途 |
|---|---|---:|---:|---:|---|
| 1 | **Gpr2_R59C** | **Gpr3_R167Y** | -2.286 | 0.604 | 首选双通道组合 |
| 2 | **Gpr2_R59C** | **Gpr3_V138M** | -2.218 | 0.622 | B 端备选 |
| 3 | **Gpr2_R59C** | **Gpr3_R167P** | -2.192 | 0.630 | B 端备选 |
| 4 | **Gpr2_R59C** | **GprC_Q411S** | -2.139 | 0.645 | 探索性备选，需保留 GprC caveat |
| 5 | **Gpr2_R59C** | **Gpr3_R167C** | -2.092 | 0.660 | B 端备选 |

数据源：

- Ratio 报告：`/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_report.md`
- 配对排名：`/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_pairings.csv`
- IFP 刷新结果：`/Users/roy/Documents/drylab/experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`

## 2. 双通道判据

`sel_mut = ΔG(ascr18) - ΔG(ascr3)`。

| 通道 | 条件 | 含义 |
|---|---|---|
| Channel A | sel_mut < -0.477 | 突变体偏好 ascr#18 |
| Channel B | sel_mut > +0.477 | 突变体偏好 ascr#3 |
| neutral | abs(sel_mut) <= 0.477 | 处在 3 sigma 噪声区内 |

阈值 0.477 来自 5-seed 方差评估的项目 operational threshold；不要把 Vina 分数换算为 Kd。本项目 ODE/Kd 校准仍在单独文献计划之后。

本次刷新规模：

| 项 | 数量 |
|---|---:|
| 合并突变记录 | 266 |
| Channel A 无 caveat | 36 |
| Channel B 无 caveat | 13 |
| 跨受体配对（无 caveat） | 374 |
| IFP 刷新突变体 | 8 |

## 3. Channel A 候选

当前 Channel A 前 3 均来自 Gpr2 R59 位点：

| 排名 | 突变体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | 备注 |
|---:|---|---:|---:|---:|---|
| 1 | **Gpr2_R59C** | -1.380 | -6.227 | -4.847 | 当前首选 A 端 |
| 2 | **Gpr2_R59F** | -0.940 | -6.695 | -5.755 | A 端备选 |
| 3 | **Gpr2_R59T** | -0.940 | -5.798 | -4.858 | A 端备选 |

建议首批构建至少包含 `Gpr2_R59C`，如果构建容量允许，同时做 `R59F` 和 `R59T` 作为同位点备选。IFP 显示 R59C/R59T 在同一局部口袋残基群上产生 ascr18/ascr3 接触差异；R59F 则保留较强双配体接触但仍在 docking ratio 上偏 ascr18。

## 4. Channel B 候选

当前 Channel B 前 3 均来自 Gpr3：

| 排名 | 突变体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | 备注 |
|---:|---|---:|---:|---:|---|
| 1 | **Gpr3_R167Y** | +0.906 | -5.715 | -4.809 | 当前首选 B 端 |
| 2 | **Gpr3_V138M** | +0.838 | -5.495 | -4.890 | B 端备选 |
| 3 | **Gpr3_R167P** | +0.812 | -5.662 | -4.850 | B 端备选 |

`Gpr3_R167C` 也进入 Top 5 clean pairings，可作为扩展备选。`GprC_Q411S` 在 ratio 中进入 Top 5 clean pairings，IFP 对 ascr3 的接触数明显高于 ascr18，但 GprC 线仍保留历史 pipeline 分辨力 caveat，因此不建议作为首批唯一 B 端。

## 5. 推荐构建顺序

首批最小集合：

| 顺序 | 构建体 | 角色 | 目的 |
|---:|---|---|---|
| 1 | WT Gpr2 | baseline | Gpr2 背景响应 |
| 2 | WT Gpr3 | baseline | Gpr3 背景响应 |
| 3 | **Gpr2_R59C** | Channel A | 主推 ascr18 偏好端 |
| 4 | **Gpr3_R167Y** | Channel B | 主推 ascr3 偏好端 |
| 5 | **Gpr3_V138M** | Channel B backup | 检查 B 端稳健性 |
| 6 | **Gpr3_R167P** | Channel B backup | 同位点备选 |

容量允许时增加：

| 构建体 | 目的 |
|---|---|
| Gpr2_R59F | A 端备选，验证 R59 同位点规律 |
| Gpr2_R59T | A 端备选，验证 R59 同位点规律 |
| Gpr3_R167C | B 端扩展备选 |
| GprC_Q411S | 探索性 B 端，不替代 Gpr3 主线 |

实验读出建议：

- 同一表达盒、同启动子、同 tag、同整合位点、同嵌合 Gpa1 版本。
- 每个突变体分别测 ascr#18 与 ascr#3 剂量响应；优先看同一受体内相对 EC50/响应强度变化，不要拿 Vina 分数换算 Kd。
- 对双通道系统，优先比较 `Gpr2_R59C` 与 `Gpr3_R167Y/V138M/R167P` 的响应比值分离度。

## 6. IFP 机制约束

本次 IFP 仅用于解释和排查，不替代 ratio 排名。

| 突变体 | IFP 提示 |
|---|---|
| Gpr2_R59C | ascr18 在 VAL119/ILE122 等局部接触高于 ascr3；总体接触数 ascr18 154、ascr3 139 |
| Gpr3_R167Y | ascr3 偏好来自 docking ratio；IFP 显示 PHE170/ASN171 等接触差异，但总接触数不能直接解释亲和力 |
| Gpr3_V138M | ascr3 在 PHE170/ASN171/ALA97 等残基接触更高；机制语言限于这些接触差异 |
| Gpr3_R167P | ascr3 在 ASP100/PRO174/ALA97/ASN171 等接触更高 |
| GprC_Q411S | ascr3 接触数明显高于 ascr18，ARG39/TYR32/ARG121/SER44 是主要差异残基；仍需 GprC caveat |

不要复用 pre-F Gpr3 groove IFP 来解释 V138/F170/D100/R164/R167。当前 Gpr3 机制只引用本次 F-pose WT 与 refreshed mutant IFP。

## 7. 对照与限制

| 对照 | 角色 |
|---|---|
| 空载体 | 背景响应 |
| WT Gpr2 / WT Gpr3 | 同受体 baseline |
| GprC N60A / S44A / N56A | Hu2024 assay 校准参考，不作为本轮 Top 推荐 |

限制：

- AutoDock Vina 是刚性对接，绝对 ΔG 不等于真实结合自由能。
- Channel B 缺少文献阳性突变对照，首批湿实验结果会反向校准 Channel B 可信度。
- ODE 仍暂停；Kd/calibration 需要单独文献审查后再进入通路模型。
