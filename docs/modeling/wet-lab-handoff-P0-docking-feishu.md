# 湿实验交接：受体突变候选位点
> 方向：P0-molecular-docking | 读者：湿实验团队 | 更新：2026-05-20

## 1. 当前结论
本版已纳入 Gpr2 3D offset 重跑、Gpr3 方案 F、Gpr3 supplemental docking、refreshed ratio analysis 和 Top 候选 IFP。旧版 `Gpr2_M327A + Gpr3_V138T` 不再作为当前构建推荐。

当前主推组合：
| 优先级 | Channel A（ascr#18 偏好） | Channel B（ascr#3 偏好） | D | balance | 用途 |
|---|---|---|---:|---:|---|
| 1 | **Gpr2_R59C** | **Gpr3_R167Y** | -2.286 | 0.604 | 首选双通道组合 |
| 2 | **Gpr2_R59C** | **Gpr3_V138M** | -2.218 | 0.622 | B 端备选 |
| 3 | **Gpr2_R59C** | **Gpr3_R167P** | -2.192 | 0.630 | B 端备选 |
| 4 | **Gpr2_R59C** | **GprC_Q411S** | -2.139 | 0.645 | 探索性备选，需保留 GprC caveat |
| 5 | **Gpr2_R59C** | **Gpr3_R167C** | -2.092 | 0.660 | B 端备选 |

数据源：`experiments/docking-repro/analysis/ratio_channel_report.md`、`ratio_pairings.csv`、`results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`。

## 2. 判据
`sel_mut = ΔG(ascr18) - ΔG(ascr3)`。

| 通道 | 条件 | 含义 |
|---|---|---|
| Channel A | sel_mut < -0.477 | 突变体偏好 ascr#18 |
| Channel B | sel_mut > +0.477 | 突变体偏好 ascr#3 |
| neutral | abs(sel_mut) <= 0.477 | 3 sigma 噪声区 |

不要把 Vina 分数换算成 Kd；ODE/Kd 校准仍需单独文献审查。

本次刷新：266 条合并突变记录；Channel A 无 caveat 36 条；Channel B 无 caveat 13 条；无 caveat 跨受体配对 374 条；IFP 刷新 8 个突变体。

## 3. Channel A
| 排名 | 突变体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | 备注 |
|---:|---|---:|---:|---:|---|
| 1 | **Gpr2_R59C** | -1.380 | -6.227 | -4.847 | 当前首选 A 端 |
| 2 | **Gpr2_R59F** | -0.940 | -6.695 | -5.755 | A 端备选 |
| 3 | **Gpr2_R59T** | -0.940 | -5.798 | -4.858 | A 端备选 |

建议首批至少构建 `Gpr2_R59C`；容量允许时加 `R59F/R59T` 验证 R59 同位点稳健性。

## 4. Channel B
| 排名 | 突变体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | 备注 |
|---:|---|---:|---:|---:|---|
| 1 | **Gpr3_R167Y** | +0.906 | -5.715 | -4.809 | 当前首选 B 端 |
| 2 | **Gpr3_V138M** | +0.838 | -5.495 | -4.890 | B 端备选 |
| 3 | **Gpr3_R167P** | +0.812 | -5.662 | -4.850 | B 端备选 |

`Gpr3_R167C` 可作为扩展备选。`GprC_Q411S` 可探索，但不要替代 Gpr3 主线。

## 5. 推荐构建
首批最小集合：
| 顺序 | 构建体 | 角色 | 目的 |
|---:|---|---|---|
| 1 | WT Gpr2 | baseline | Gpr2 背景响应 |
| 2 | WT Gpr3 | baseline | Gpr3 背景响应 |
| 3 | **Gpr2_R59C** | Channel A | 主推 ascr18 偏好端 |
| 4 | **Gpr3_R167Y** | Channel B | 主推 ascr3 偏好端 |
| 5 | **Gpr3_V138M** | Channel B backup | 检查 B 端稳健性 |
| 6 | **Gpr3_R167P** | Channel B backup | 同位点备选 |

容量允许时增加：`Gpr2_R59F`、`Gpr2_R59T`、`Gpr3_R167C`、探索性 `GprC_Q411S`。

## 6. IFP 解释边界
IFP 只用于解释和排查，不替代 ratio 排名。

| 突变体 | IFP 提示 |
|---|---|
| Gpr2_R59C | ascr18 在 VAL119/ILE122 等局部接触高于 ascr3；总体接触数 ascr18 154、ascr3 139 |
| Gpr3_R167Y | IFP 显示 PHE170/ASN171 等接触差异，但总接触数不能直接解释亲和力 |
| Gpr3_V138M | ascr3 在 PHE170/ASN171/ALA97 等残基接触更高 |
| Gpr3_R167P | ascr3 在 ASP100/PRO174/ALA97/ASN171 等接触更高 |
| GprC_Q411S | ascr3 接触数明显高于 ascr18，ARG39/TYR32/ARG121/SER44 是主要差异残基；保留 GprC caveat |

不要复用 pre-F Gpr3 groove IFP 来解释 V138/F170/D100/R164/R167。当前 Gpr3 机制只引用本次 F-pose WT 与 refreshed mutant IFP。

## 7. 实验注意
- 同一表达盒、同启动子、同 tag、同整合位点、同嵌合 Gpa1 版本。
- 每个突变体分别测 ascr#18 与 ascr#3 剂量响应；优先看同一受体内相对变化。
- 空载体、WT Gpr2、WT Gpr3 是必需对照。
- Channel B 缺少文献阳性突变对照，首批湿实验结果会反向校准 Channel B 可信度。
- ODE 暂停；不要把 docking ΔG 直接转换为 Kd。
