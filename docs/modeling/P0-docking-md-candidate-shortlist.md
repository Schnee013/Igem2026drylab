---
direction: P0-molecular-docking
type: md-candidate-shortlist
target_audience: drylab-md-team; post-MD candidate discussion
last_updated: 2026-07-09
---

# MD 前候选体系清单：P0 docking/IFP

## 1. 当前结论

本版已纳入 Gpr2 3D offset 重跑、Gpr3 方案 F、Gpr3 D100/R164/R167 supplemental docking、refreshed ratio analysis 和 Top 候选 ProLIF IFP。当前用途是为 MD input gate 固化候选标签、Channel A/B 方向、相对排序、关键结合残基和机制线索；通过 MD gate 后，再进入更高置信度的湿实验候选构建讨论。

当前 MD 候选组合优先级：

| 优先级 | Channel A（ascr#18 偏好） | Channel B（ascr#3 偏好） | D | balance | MD 输入用途 |
|---|---|---:|---:|---:|---|
| 1 | **Gpr2_R59C** | **Gpr3_R167Y** | -2.286 | 0.604 | 当前 MD 主线：`Gpr2_R59C + ASCR18` 与 `Gpr3_R167Y + ASCR3` |
| 2 | **Gpr2_R59C** | **Gpr3_V138M** | -2.218 | 0.622 | B 端备选候选体系 |
| 3 | **Gpr2_R59C** | **Gpr3_R167P** | -2.192 | 0.630 | B 端备选候选体系 |
| 4 | **Gpr2_R59C** | **GprC_Q411S** | -2.139 | 0.645 | 探索性候选体系，保留 GprC caveat |
| 5 | **Gpr2_R59C** | **Gpr3_R167C** | -2.092 | 0.660 | B 端备选候选体系 |

数据源：

- Ratio 报告：`../../experiments/docking-repro/analysis/ratio_channel_report.md`
- 配对排名：`../../experiments/docking-repro/analysis/ratio_pairings.csv`
- IFP 刷新结果：`../../experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`

## 2. 双通道判据

`sel_mut = ΔG(ascr18) - ΔG(ascr3)`。

| 通道 | 条件 | 含义 |
|---|---|---|
| Channel A | sel_mut < -0.477 | 突变体偏好 ascr#18 |
| Channel B | sel_mut > +0.477 | 突变体偏好 ascr#3 |
| neutral | abs(sel_mut) <= 0.477 | 处在 3 sigma 噪声区内 |

阈值 0.477 来自 5-seed 方差评估的项目 operational threshold；Vina 分数仅支持排序。Kd/EC50 需要独立 binding/calibration 证据，本项目 ODE/Kd 校准仍在单独文献计划之后。

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

当前 MD 候选池至少包含 `Gpr2_R59C + ASCR18`。`R59F` 和 `R59T` 是同位点备选标签，可在主线 MD gate 或后续容量评估后讨论。IFP 显示 R59C/R59T 在同一局部口袋残基群上产生 ascr18/ascr3 接触差异；R59F 则保留较强双配体接触但仍在 docking ratio 上偏 ascr18。

## 4. Channel B 候选

当前 Channel B 前 3 均来自 Gpr3：

| 排名 | 突变体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | 备注 |
|---:|---|---:|---:|---:|---|
| 1 | **Gpr3_R167Y** | +0.906 | -5.715 | -4.809 | 当前首选 B 端 |
| 2 | **Gpr3_V138M** | +0.838 | -5.495 | -4.890 | B 端备选 |
| 3 | **Gpr3_R167P** | +0.812 | -5.662 | -4.850 | B 端备选 |

`Gpr3_R167C` 也进入 Top 5 clean pairings，可作为扩展备选。`GprC_Q411S` 在 ratio 中进入 Top 5 clean pairings，IFP 对 ascr3 的接触数明显高于 ascr18；GprC 线保留历史 pipeline 分辨力 caveat，当前 B 端主线仍为 Gpr3。

## 5. MD 验证输入清单

MD 执行顺序和实时状态由 [INDEX](../INDEX.md)、对应 system-local
`PACKAGE_STATUS.md` 和直接 gate/run artifact 路由；本清单只维护候选体系身份和
MD gate 的科学目的。

当前最小 MD 输入集合：

| 顺序 | 体系 | 角色 | MD gate 目的 |
|---:|---|---|---|
| 1 | WT Gpr2 + ASCR18 | baseline | Gpr2 holo 资源基线和结构 caveat 检查 |
| 2 | **Gpr2_R59C + ASCR18** | Channel A | 验证 R59C/ascr18 pose stability、关键接触持续性和受体局部构象 |
| 3 | WT Gpr3 + ASCR3 | baseline | Gpr3 matched pair baseline |
| 4 | **Gpr3_R167Y + ASCR3** | Channel B | 验证 R167Y/ascr3 pose stability、关键接触持续性和受体局部构象 |

后续容量允许时讨论：

| 候选体系 | 用途 |
|---|---|
| Gpr2_R59F + ASCR18 | A 端备选，验证 R59 同位点规律 |
| Gpr2_R59T + ASCR18 | A 端备选，验证 R59 同位点规律 |
| Gpr3_R167C + ASCR3 | B 端扩展备选 |
| GprC_Q411S + ASCR3 | 探索性 B 端，保留 GprC caveat |

通过 MD gate 后的候选构建讨论前置要点：

- 同一表达盒、同启动子、同 tag、同整合位点、同嵌合 Gpa1 版本。
- 每个突变体分别测 ascr#18 与 ascr#3 剂量响应；优先看同一受体内相对 EC50/响应强度变化；Kd/EC50 解释使用独立 binding/calibration 证据。
- 对双通道系统，优先比较 `Gpr2_R59C` 与 `Gpr3_R167Y/V138M/R167P` 的响应比值分离度。

## 6. IFP 机制约束

本次 IFP 用于解释、pose 选择和 MD 指标设计；ratio 排名仍是候选优先级来源。关键接触是否持续存在由 MD occupancy/lifetime 验证。

| 突变体 | IFP 提示 |
|---|---|
| Gpr2_R59C | ascr18 在 VAL119/ILE122 等局部接触高于 ascr3；总体接触数 ascr18 154、ascr3 139 |
| Gpr3_R167Y | ascr3 偏好来自 docking ratio；IFP 显示 PHE170/ASN171 等接触差异；总接触数只作为局部接触线索，亲和力解释回到 ratio、MD 与独立 binding evidence |
| Gpr3_V138M | ascr3 在 PHE170/ASN171/ALA97 等残基接触更高；机制语言限于这些接触差异 |
| Gpr3_R167P | ascr3 在 ASP100/PRO174/ALA97/ASN171 等接触更高 |
| GprC_Q411S | ascr3 接触数明显高于 ascr18，ARG39/TYR32/ARG121/SER44 是主要差异残基；仍需 GprC caveat |

当前 Gpr3 机制来源为本次 F-pose WT 与 refreshed mutant IFP；pre-F Gpr3 groove IFP 只作历史方法背景。

## 7. 后续讨论对照与证据边界

| 对照 | 角色 |
|---|---|
| 空载体 | 背景响应 |
| WT Gpr2 / WT Gpr3 | 同受体 baseline |
| GprC N60A / S44A / N56A | Hu2024 assay 校准参考 |

限制：

- AutoDock Vina 是刚性对接，绝对 ΔG 不等于真实结合自由能。
- Channel B 缺少文献阳性突变对照，后续 dose-response 会反向校准 Channel B 可信度。
- 静态 docking/IFP 的动态稳定性证据来自 MD：pose RMSD、关键接触 occupancy/lifetime、受体局部构象和 trajectory sanity。
- ODE 仍暂停；Kd/calibration 需要单独文献审查后再进入通路模型。
