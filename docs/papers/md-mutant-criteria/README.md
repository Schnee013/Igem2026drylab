# MD 突变体筛选判据 · 外部文献锚点

**用途**：为 `plan docking-md-chimeric-md-md-wt-gpr-chimer-nifty-falcon.md` §PRE-2（A 线判据表构建）提供外部文献锚点。承接计划文件里的 TODO 清单（line 55–61）。

**生成方式**：2026-04-23 并行四路 subagent 定向检索，DOI 均通过期刊官网 / PMC / CrossRef 验证。

**关联权威源**：
- 计划文件：`~/.claude/plans/docking-md-chimeric-md-md-wt-gpr-chimer-nifty-falcon.md`（父计划）
- 项目内既有判据：`docs/modeling/P0-md-simulation.md:139 / 165-167 / 247-255`
- 待构建落地文档：`experiments/md-simulation/analysis/mutants_criteria.md`（PRE-1 完成后写入）

**文件布局**：
| 文件 | 内容 |
|------|------|
| `README.md`（本文） | 索引与使用说明 |
| `matrix.md` | 20 篇文献 × 5 字段主矩阵，按四大检索通道分区 |
| `channel-1-selectivity-dG.md` | ΔΔG_sel MM-PBSA/FEP 阈值（5 篇） |
| `channel-2-pose-rmsd.md` | 配体 pose RMSD 分箱阈值（5 篇） |
| `channel-3-watchdog.md` | watchdog 早退阈值 / GPCR Cα RMSD / 检查间隔（5 篇） |
| `channel-4-error-bars.md` | bootstrap / block averaging / seed 数下限（5 篇） |
| `channel-5-gpcr-mutant-md.md` | GPCR 突变体 MD 协议模板 · 时长/reps/指标组合（9 篇，2026-04-23 补检） |
| `zotero_item_keys.json` | 28 条已写入 Zotero 的 item key 映射（审计用，不含 API key） |

**Zotero 同步状态**（2026-04-23 完成）：28 条全部写入用户 Zotero 个人库（userID=13152647）。

- 父 collection：`MD Mutant Criteria` (key=`RKSW6RF6`)
- 子 collection：
  - `C1 · Selectivity ΔΔG` (`W9CVVP36`) — 5 items
  - `C2 · Ligand Pose RMSD` (`RFHQCXDS`) — 5 items
  - `C3 · Watchdog Early-Abort` (`JK27GC7G`) — 5 items（含 Fusani2020 跨 C2/C3）
  - `C4 · Error Bars` (`92URPHVQ`) — 5 items
  - `C5 · GPCR Mutant MD Protocols` (`UQUN27HF`) — 9 items
- 元数据来源：Crossref（DOI → title/authors/journal/volume/issue/pages/year）
- 跨 collection：Fusani2020 (`M44GRHR7`) 同时挂在 C2 和 C3（Zotero 原生支持多 collection）

**已知去重**：Fusani/Clark et al. 2020 JCIM (DOI `10.1021/acs.jcim.9b00843`) 同时被 channel-2 与 channel-3 命中，属同一篇，按内容分区放入两处时明确标注"见另一 channel"。

**未覆盖方向（写回计划 TODO 清单）**：

- ~~用户 Zotero "GPR 突变体 MD"~~ → 2026-04-23 补检：Zotero 本地 PDF 无 parent item 元数据（"No authors"，无 DOI）；已用 web 检索在 C5 补 9 篇协议模板文献（[Verma2018] [Keranen2014] [Billesbolle2023] [Choi2023] 等，其中 [Choi2023] F170 位点直接对应项目）
- ascaroside-GPCR MM-PBSA 专文——检索未发现，方法学泛化依靠 [Hauser2018] [Aldeghi2017] [Wang2022]
- "Souza 等 GPCR selectivity MD 工作"——计划原文提及但检索未找到以 Souza 为一作的对口文献，**建议用户在 A 线判据表构建前确认原始出处**（可能笔误或指 Khan/Souza coarse-grain Martini 相关工作）
- OR-ascaroside MD 全检索无命中 → 项目本身即方法学新颖性所在，不需硬套前人协议
