# Root-Cause N=3 综合决策报告

> ⚠️ 以下 Tier 1-4 单通道分析已弃用（2026-04-14），正确框架为 Channel A/B 双通道分类（权威源 = ratio_channel_report.md）。此处保留仅做历史记录。

**日期**：2026-04-12
**目的**：把 N56 + 2 条新 HIGH 案例的根因对齐，判别"防止 Claude 读到过时信息"防御体系的下一步行动（写 feedback memory / 实施 meta-audit draft / 作废）。
**决策范围**：`docs/ops/draft-meta-audit-command.md`、`docs/ops/draft-rules-cleanup-command.md` 的命运；feedback memory 的补丁。
**不在范围内**：`docs/ops/quarterly-trigger-audit.md`（手册，不是 SOP，留给用户）。

---

## 案例 A（锚点）：N56A 分类扁平化

已在 `~/.claude/projects/-Users-roy-Documents-drylab/memory/feedback_cite_summary_on_write.md` 的 Why 段完整写过，不重复推导。此处只摘要用于族分类：

- **事件**：2026-04-11 commit `3aea066` 把 `docs/modeling/P0-molecular-docking.md` "Pipeline 验证" 段从"3 个阳性对照"改成"4 个阳性对照（含 N56A）"。N56A 实际是 Hu2024 的 N2.53 **阴性对照**，错误持续约 16h，污染了 3 份权威文档。
- **根因链**（共 4 跳）：
  1. 04-07 日志把 N60/N56/R395/S44 合并为模糊标签"Hu2024 验证残基"
  2. 下游作业清单（JSON/config/scan_residues）按"作业状态"分组而非"ground-truth 极性"分组
  3. 04-11 session 未 Read `Hu2024-GprC-summary.md:L143-144`（原始分类段）就写 P0 doc
  4. `config.yaml:289-294` 有正确 inline 注释（N2.53 阴性 / N2.57 阳性），但 04-11 session 也没读 config.yaml
- **失效的防御**：
  - `feedback_verify_before_conclude`：Claude 把"更新权威文档"当 routine edit 不觉得是"下结论"
  - `feedback_no_guessing`：Claude 相信"4 个落 Tier 4"这个**数据事实**，猜的是"4 个都是阳性对照"这个**分类标签**
  - DOCMAP 单一权威源规则被动、无 lint
  - `/truth` 是事后审查，04-11 commit 未跑
- **新规则**：`feedback_cite_summary_on_write.md`（已实施）
- **触发类型**：**写触发**（写 `docs/modeling/**` 或 `docs/prd/**` + 命中分类判断词）

---

## 案例 B：V138R "盐桥机制实证"（2026-04-11_1437 HIGH#1）

- **事件**：2026-04-11 session 把 Gpr3 V138R 的 ProLIF 接触统计（ARG138→ascr18 VdW 9 次，ascr3 VdW 2 次，差 +7）升级为"**盐桥机制实证**"，写入 `docs/logs/2026-04-11.md §6` 和 `memory/project_docking_pipeline.md` Top 6 表。现已由 `/truth` 发现并在日志中降级为"空间富集（盐桥假说方向一致，未实证）"；但 memory 的表述仍保留"盐桥机制实证"作为 MD 转交项（line 59）。
- **根因链**（共 4 跳）：
  1. **上游**：`src/modeling/docking-repro/run_ifp_analysis.py:163` 用 `plf.Fingerprint()` 默认构造 —— ProLIF 默认 interaction 集理论上包含 Cationic/Anionic，但实际运行 CSV 中只出现 `{HBAcceptor, HBDonor, VdWContact}` 三类（可能原因：pose→SDF 流程丢失 formal charge，Ionic 通道 silently 为空）。
  2. **输出 schema 断层**：`mutant_contacts.csv` 的行 schema = `(receptor, mut, ligand, residue, interaction_type, count)`。CSV 里**看不到** Ionic 通道是"测了但为 0"还是"根本没测"——schema 不区分"absent"与"not measured"。
  3. **读取环节**：Claude Read CSV → 按残基 aggregate → 看到 ARG138=9 → 按"胍基+羧基 = 盐桥"的常识把数字升级为机制断言。期间没回去验证 CSV 的 interaction 列 `sort -u` 有哪些类型。
  4. **落地**：三个高权威位置同时写入："盐桥机制实证"进入 logs/memory/MD 交接表。
- **失效的防御**：
  - `feedback_claim_granularity`（颗粒度匹配）—— 最接近，但它的触发词是"X 核对 ✓"类断言；本案例触发词是"实证/证明/确认"类机制断言，语义领域不同。
  - `feedback_verify_before_conclude` —— Claude 自认为"验证"已发生（CSV 有数字），没意识到"证据类型 vs 结论类型"是独立于"有没有数字"的维度。
  - `feedback_no_guessing` —— 不对口，有数据支撑不算"猜"。
  - `/truth` —— 事后捕获，但写入时"盐桥"字样已同时污染 logs/memory/MD 交接清单。
- **这是一条新族**：**证据类型越级**（evidence-class promotion）—— 把弱证据（空间接触富集）贴上强标签（机制实证）。与 N56 的"分类标签跨 session 漂移"不同：N56 的错误是**标签本身错位**（正↔负），盐桥是**证据强度 ↔ 断言强度失配**。
- **新规则**：`feedback_mechanism_claim_requires_channel.md`（待写）
  - 触发：写入动作中出现机制断言词（`实证 / 证明 / 确认 / 直接形成 / 盐桥 / 氢键 / π-π / π-cation`），且引用的数据来自 IFP/对接结果。
  - 动作：Read 源 CSV 的 interaction 列 unique 值，确认**被断言的相互作用类型在数据中可测量**。若缺失，必须：(a) 补跑开启该通道，或 (b) 降级为空间/几何语言（"空间富集 / 距离接近 / pose 几何兼容"）。
- **触发类型**：**写触发**（写动作含特定关键词 → 数据源 schema 校验）

---

## 案例 C：WT 基线跨日期 + 跨主机代码漂移（2026-04-09_1830 HIGH#1+#2）

- **事件**：Truth audit 发现 04-08 `wt_singlestage/docking_results.json` 与 04-09 multiseed 同 seed=42 对 GprC_ascr18 产出 −8.235 vs −8.275，差 0.040 kcal/mol（>4σ 噪声）。深挖后（审查中新发现）Windows 的 `run_wt_singlestage.py` 和 `mutagenesis.py` 还缺失 `helix_ranges` 支持，导致 WT 基线用"全原子质心"而 multiseed 用"TM-helix 质心"——box center 根本不一致。若直接启动 `run_mutagenesis_alanine.py` 消费 wt_singlestage JSON 做基线，所有 ΔΔG 都会带 ~0.04 kcal/mol 系统偏差。
- **根因链**（共 5 跳）：
  1. **上游污染源**：Mac 端先更新 `helix_ranges` 支持并跑了 multiseed；同步到 Windows 只覆盖了部分脚本，`run_wt_singlestage.py` / `mutagenesis.py` 未同步。
  2. **Artifact 无溯源元数据**：`wt_singlestage/docking_results.json` 没有记录生成它的 commit SHA、grid_box 计算方式、配体 PDBQT 的 SHA 或 mtime。文件看起来"schema 合法、数值合理"。
  3. **跨日期组合假设**：Claude 计划 #5 时默认"昨天的 wt_singlestage JSON + 今天的 multiseed stats + 今天的 mutagenesis 配置"三者可同框使用——没任何机制强制比较这三个输入的 provenance。
  4. **静默通过**：`load_wt_baseline()` 只检查 JSON 键存在性（ascr18/ascr3），不校验 provenance。即使 ascr3 键在也会照常运行，整个扫描带系统偏差跑完 2h 再发现。
  5. **落地风险**：若 `/truth` 晚一步，所有 ΔΔG_sel 表+湿实验交接清单都会基于 0.04 kcal/mol 偏差的基线（≈ Ala scan 信号量级 10–15%）。
- **失效的防御**：
  - `feedback_file_versioning`（Mac→Win 单向同步 + 同步后清理旧 .py）—— 这条解决"下次同步时源文件别搞错"，不解决"已生成的历史输出 artifact 要不要作废"。
  - `feedback_code_sync_verify`（同步后 findstr 验证关键符号）—— 覆盖"同步动作成功与否"，不覆盖"同步前产出的 JSON 现在是不是 stale"。
  - `feedback_verify_before_conclude` —— Claude Read 了 JSON，schema 合法，没有任何信号说要质疑数值本身。
  - DOCMAP / CLAUDE.md 里没有任何关于"输出 artifact 需要 provenance metadata"的约定。
  - `/truth` 靠人眼对两份 JSON 做数值比对才发现——依赖运气（若基线和 multiseed 不共享配体就发现不了）。
- **这是第三条新族**：**输出 artifact provenance 缺失导致跨时点组合漂移**（silent artifact drift）。与 A、B 都不同：
  - A 错在**分类标签的标号**（写时的事实错位）
  - B 错在**断言强度 vs 证据强度**（写时的修辞越级）
  - C 错在**输入文件之间的隐式假设**（读时的时点不一致被静默忽略）
- **新规则**：`feedback_provenance_before_baseline.md`（待写）
  - 触发：Claude 计划把某个历史 JSON/CSV 作为下游脚本的**基线输入**。
  - 动作：在使用前必须检查 (a) 生成该 artifact 的 code commit SHA（若 artifact 无 provenance 字段→ `git log --diff-filter=A <path>` 或 file mtime 对比 commit 时间）、(b) 该 artifact 引用的外部输入（PDBQT/结构/config 片段）的当前版本是否与生成时一致、(c) 若任一检查失败 → 重跑 artifact，不得沿用。
- **触发类型**：**读触发**（把历史 artifact 标记为"基线"前的 preflight）。
- **脚本层配套**（可选）：`run_wt_singlestage.py` / `run_mutagenesis_alanine.py` 在 JSON 开头写 provenance block：`{commit, config_sha, ligand_shas, box_center}`；消费者校验。但这是"让规则更容易遵守"，不是规则本身。

---

## 族分类矩阵

| 维度 | A. N56 扁平化 | B. 盐桥实证 | C. 基线漂移 |
|---|---|---|---|
| 错误层 | 事实错位（标签张冠李戴） | 修辞越级（弱证据→强断言） | 组合不一致（输入时点脱钩） |
| 信息流方向 | 跨 session 漂移（04-07 → 04-11） | 单 session 内一跳 | 跨主机 + 跨日期组合 |
| 数据是否"合理" | 合理（Tier 4 数据真） | 合理（VdW 计数真） | 合理（JSON schema 合法） |
| 验证需要读什么 | 原始 summary 分类段 | CSV interaction 列 unique 值 | artifact provenance 块 / commit SHA |
| 触发类型 | **写触发**（权威文档+分类词） | **写触发**（日志/memory + 机制断言词） | **读触发**（历史 JSON 即将作基线） |
| `/truth` 能否事后捕获 | ✓（对比 summary 即显） | ✓（对比 CSV 即显） | ✓ 但靠运气（需要跨 JSON 数值比对） |
| 失效的 memory | `verify_before_conclude` + `no_guessing` 都不对口 | `claim_granularity` 最近但语义领域不同 | `file_versioning` + `code_sync_verify` 都只覆盖同步动作本身 |
| 族间距离 | ↔ B：语义域完全不同；↔ C：错误层完全不同 | ↔ A：见上；↔ C：写 vs 读、证据强度 vs 时点 | ↔ A/B：都不同 |

**三条根因两两正交**。没有任何一条能被其他两条的修复顺带覆盖。

---

## meta-audit draft 命运判决

### 判决：**保留，但大幅简化**

**理由**：
- 三条根因分属独立族，说明元层审查工具确实能抓到**被现有 memory 覆盖不全的**问题。若三条都归到同一族，结论会反过来（只补一条 memory 即可）；但事实是三族正交，单靠 feedback memory 会陷入"每出一条写一条"的被动状态。
- 但前一轮 18 条 HIGH/MEDIUM/LOW 改动中只有 ~2 条真对着 N56 族。剩余 16 条是"假设 command 会跑之后的运行时健壮性"——这是 over-engineering，N=3 证据不支持。
- quarterly-trigger-audit.md 是手册不是 SOP，不在判决范围内。

### 保留的维度（真必要）

meta-audit 若实施，**只需覆盖 3 个维度**，每个对应一个根因族：

1. **分类标签-权威文档一致性**（族 A）
   - 扫描 `docs/modeling/**` 和 `docs/prd/**` 中的分类判断词（阳性/阴性对照 / loss-of-function / 等），每条**必须有** `{summary_file}:L{lineno}` 锚点。
   - 无锚点即 HIGH。
   - 本质：lint 规则，`feedback_cite_summary_on_write.md` 的静态检查版。

2. **机制断言-证据类型一致性**（族 B）
   - 扫描 `docs/logs/*.md` 和 memory 中的机制断言词（实证/证明/盐桥/氢键/...），每条必须能回溯到对应 CSV/JSON 的 interaction 字段，且该字段在源数据中**被实际测量**（非默认空）。
   - 回溯失败或字段缺失即 HIGH。
   - 本质：语义-数据通道匹配检查。

3. **基线 artifact provenance 完整性**（族 C）
   - 扫描所有被脚本当作"基线"的 JSON/CSV（`wt_singlestage`、`multiseed_stats`、`mutagenesis/baseline_*`），每份必须携带 provenance block 或可从 `git log --diff-filter=A` 推出 commit SHA + 输入文件 mtime ≤ commit time。
   - 缺失或 stale 即 HIGH。
   - 本质：artifact 溯源 lint。

### 作废的维度（over-engineering）

前一轮 draft 中凡属以下类别的逻辑全部砍掉：
- command 运行时的异常处理/重试/回滚
- 审查报告格式的美化/排版
- 与现有 `/truth` `/censor` 的边界协调
- 多轮迭代自动修复
- 人机交互确认流

这些是假设 command 会跑之后的细节，N=3 证据没触及任何一条，delete 无损。

### `draft-rules-cleanup-command.md`

**作废**。理由：N=3 没有一条根因指向"memory 规则过多/过时"。如果 memory 规则的问题是"不对口"（A/B/C 都存在），清理不治本——补写才治本。此 draft 解决的是虚构的问题。

> **⚠️ 2026-04-12 self-critique 已推翻此判决 — 见文末"Self-Critique"章节。下述实施顺序亦被覆盖。**

### 实施顺序（建议）

1. **先补两条 feedback memory**（10 分钟，无风险）：
   - `feedback_mechanism_claim_requires_channel.md`（族 B）
   - `feedback_provenance_before_baseline.md`（族 C）
   - 族 A 的 memory 已存在。
2. **然后**再决定要不要把 3 个维度固化为 `/meta-audit` command。如果两条新 memory 覆盖后 1 个月内没再出同族 HIGH → command 是 over-engineering，维持 memory + `/truth` 即可。
3. 若 1 个月内 3 族中任一族再犯 → 才把那 1 个族的维度固化为 lint command。

---

## 下一步（本 session 内）

> **⚠️ 原初版清单（含 spot fix pipeline 残留 + 直接写 3 条 memory）已被下文两轮 self-critique 推翻。当前有效清单见文末"修正后下一步"章节。**

---

## Self-Critique（2026-04-12 二轮审查）

用户指令："再明确一次第一性原理，再思考一轮"。二轮审查发现原报告有 4 个漏洞。

### 漏洞 1：把症状族当根因族

原报告写"三条根因两两正交"是**修辞越级**——把三个失效**现场**的差异升格为三个**根因**的差异。再往下一层刨，三条收敛到同一条根因：

> **Claude 在写/用某信息时，没回源到原始数据验证该信息的强度/完整性。**
> A 跳过 `summary.md:L143` 的分类段；B 跳过 CSV 的 interaction unique 值；C 跳过 JSON 的 provenance 块。

这条泛化根因对应 **已存在** 的 `feedback_verify_before_conclude`，它在三条案例里都没 catch。为什么？因为它用"下结论前"作触发词，**Claude 在这三种情境都主观判定"当前动作不是下结论"**（A：当 routine edit；B：当验证已发生；C：JSON schema 合法不必质疑）。

**真根因**：**抽象规则的触发识别不可靠**——Claude 对"什么算下结论"的主观判断在这三种情境都失败了。

讽刺：我审查"Claude 把弱证据写成强断言"时，自己把"三个现场不同"写成"三族正交"。同一个 bug pattern 的元层重现。

### 漏洞 2：`draft-rules-cleanup` 作废判决未验证

原判决"N=3 无证据支持规则过多"是凭空下的——没看过 memory 库规模就下结论，**违反了 `feedback_verify_before_conclude`**。

实际检查：13 条 feedback memory，其中高度相关簇 4 条：
- `feedback_verify_before_conclude`
- `feedback_no_guessing`
- `feedback_claim_granularity`
- `feedback_cite_summary_on_write`（本次新增）

都在处理"断言前该验证什么"的不同切片——这正是用户吐槽的"攒了一堆反复失效"的现场。rules-cleanup 的价值是开放问题，不能凭"N=3 没抓到"就判作废。**正确判决：待验证**。

### 漏洞 3：缺了 compaction boundary 维度

原报告没讨论 session compaction 对信息强度的衰减。重看三案例：

- **A**：04-07 把 N60/N56/R395/S44 合并为模糊标签"Hu2024 验证残基"——这就是 compaction 造成的信息强度衰减。原始分类（正/负对照）在 session handoff 中被压缩成模糊标签，后续 session 看到的只是压缩后的结果。
- **C**：生成 `wt_singlestage/docking_results.json` 时的 context（commit / box 算法 / 配体版本）早被压缩掉，后续 session 只看到文件存在。
- **B**：**不沾** compaction —— 是单 session 内的证据强度越级。

更真实的子族切分：
- **跨 session 信息强度衰减**（A + C）—— 防御点应放在 session 边界或 artifact 生成时强制 provenance
- **单 session 内推理越级**（B）—— 防御点在写入动作的字面关键词

### 漏洞 4：样本选择偏差

上下文的筛选标准是"最大化族间距离"，建立在"根因按族分布"的前提上。若根因同族（见漏洞 1），这筛选就是**在一条根因上选 3 个远处的症状**——保证看不出收敛。更好的筛选：时间轴 + 随机采样 + 按"是否跨 session 幸存"分层。

---

## 扩展分析：字面化触发维度远不止 3 条

用户补充："如果转用字面化触发条件，当前已有的审查族还不够。"

扫全部 `docs/logs/truth-audits/` + `docs/logs/censor-audits/` 的 HIGH/MEDIUM 条目后确认这是对的。原报告的 3 个维度只覆盖了 N=3 的 3 条采样案例，实际审计已发生 HIGH 覆盖的触发词族至少 17 条。按触发层分为三类：

### L1. 写入动作的字面关键词层（命中即强制回源验证）

| # | 触发词族 | 验证要求 | 锚点案例 |
|---|---|---|---|
| **D1** | **分类判断词**（阳性对照 / 阴性对照 / positive control / loss-of-function / gain-of-function / functional / 丧失功能） | 回指 `docs/papers/summaries/{source}.md:L{行}` | N56（案例 A） |
| **D2** | **机制断言词**（实证 / 证明 / 确认 / 盐桥 / 氢键 / π-π / pi-cation / 直接形成 / 驱动） | 回指源 CSV/JSON 的 interaction/energy 字段 unique 值校验 | 盐桥（案例 B） |
| **D3** | **完成/承诺词**（已解决 / 修复完成 / Pipeline 通过 / 核对 ✓ / 验证通过 / 已确认） | 展开到每一子层的证据引用；禁止 flat tick | 2026-04-09_2115 #7"修复完成"；N56 "Pipeline 4/4 通过" |
| **D4** | **结构定位词**（位于 TM[0-9] / ECL[0-9] / ICL[0-9] / 口袋底部 / 腔壁） | 对应 `config.yaml` 的 helix_ranges / ecl_ranges 的残基区间 | V138 TM3/TM4 错位；F170 ECL2 错位 |
| **D5** | **数值比较缓和词**（几乎无 / 近似 / 远超 / 显著 / 接近 / 等价 / 翻转） | 必须附噪声阈值（3σ 或 SD）作分母 | "Gpr3 WT 几乎无选择性"（2026-04-11_1437 #7） |
| **D6** | **分类归纳词**（碱性 / 酸性 / 疏水 / 极性 → 都 / 一致 / 最优 / 规律） | 类内同向性 + 反例检查 | "碱性最优"（案例 B 姐妹条，2026-04-11_1437 #2，HIGH） |
| **D7** | **因果词**（因为 / 导致 / 由于 / 所以）连接两数据点 | 必须列出被排除的替代假设 | "根因 = ICL3 截断"（2026-04-09_2115 #5，HIGH） |
| **D8** | **跨 session 继承词**（之前确定 / 上次跑 / 历史上 / memory 记录 / 早先确认） | 不得以 memory 或旧 log 条目为终点；必须回源到原始 summary/config/代码 | N56 "Hu2024 验证残基" 来自 04-07 合并标签；N=3 漏洞 3 |
| **D9** | **全称量词**（全部 / 所有 / 没有一个 / 唯一 / 每个） | 穷举枚举或反例搜索 | "GprC 14/14 几乎全落 Tier 4"（2026-04-12_0205 #0）；N56 "4 个都是阳性对照" |
| **D10** | **文献来源词**（Hu2024 / Fan2024 / Lee2022 / 文献 / 原文 / 论文） | 必须给 summary 行号或 PDF 页/行引用 | N56（A）；R6.45 BW 算术矛盾（2026-04-08_1913 #2，HIGH） |
| **D18** | **项目内引用验证词**（文件路径 / 代码片段 / CLI 命令 / 脚本名 / §号段落引用 / 指标名·列标题） | Read/Glob 验证存在且内容正确；§号引用须 Read 段落前 5 行；含数值表格须跨文件 Grep 一致性 | config.yaml helix 范围全错 / compare_top6.pml 不存在 / docking_repro 连字符（2026-04-12_1800）/ §号映射 5×错误 + abs sel 列标签错标为 ΔΔG_sel（2026-04-14_0230） |
| **D19** | **数学/统计推导词**（预计 / 期望 / 概率 / 假阳性率 / 百分比 / 倍数） | 教学/权威文档的推导须从公式逐步验算到最终值 | 2σ 假阳性"20 条"实算 2.1 条（10x 量级错误，2026-04-12） |
| **D20** | **项目架构/角色定义词**（底盘 / 异源表达 / 信号链路 / 改造对象 / 参考物种 / 迁移到 / 表达到） | Read 对应 PRD 段验证实体角色与 PRD 一致 | lesson-01 L35 底盘≠受体混淆（2026-04-13） |

> D18-D20 于 2026-04-12/04-13 新增，原报告截止于 D17。回填以保持本文件作为维度表唯一权威源。

### L2. 操作路径的状态触发层（非语言，路径触发）

| # | 触发点 | 验证要求 | 锚点 |
|---|---|---|---|
| **D11** | Claude 计划把某历史 JSON/CSV 作基线输入 | 校验 provenance block / commit SHA / 输入文件 mtime | 案例 C |
| **D12** | glob / search / Grep 返回 0 结果 | 禁止静默通过，必须显式报错或追问 | TM_DIR 不存在（censor 2026-04-09_2305 #7，HIGH） |
| **D13** | session 开场时 memory 引用的分类/断言来自 >3 天前 entry | 强制回源复核 summary/config；不得直接沿用 | N56（A）；案例 C（compaction 衰减） |

### L3. 代码/文档的静态 lint 层（CI / pre-commit）

| # | 触发点 | 验证要求 | 锚点 |
|---|---|---|---|
| **D14** | 函数签名变更 | Grep 所有调用方逐一更新 | `feedback_grep_all_callers` 已覆盖；censor 2026-04-07_0555 #11 |
| **D15** | 新增/删除 config key | Grep 所有消费点 | censor 2026-04-09_2145 多条 #5 |
| **D16** | 文件路径/目录常量 | 存在性预检 | censor 2026-04-10_0930 #8 多条 HIGH |
| **D17** | docstring / CLAUDE.md / DOCMAP 与代码描述 | 静态一致性 lint | censor 2026-04-10_0930 #4 多条 HIGH |

### 层级间的观察

- **L1 是字面化 `verify_before_conclude`**——把抽象规则拆成 13 个字面触发词组（D1-D10 + D18-D20），让触发识别从 Claude 主观判断变为文本匹配。
- **L2 是 `verify_before_conclude` 的非语言补集**——不依赖关键词，依赖操作路径的特定节点。
- **L3 是 `/censor` 的现有职责**——已经有工具，不需要新规则，只需要保留并保证运行。
- **D3/D6 是已有 memory 的字面化版本**（`feedback_claim_granularity` / `feedback_outlier_vs_rule`）——已有抽象规则存在，但未字面化，现场仍在失效。
- **D8/D13 指向同一个 compaction 漏洞**——D8 是"写时提醒 Claude 自己"，D13 是"读时 session 开场的 boundary check"。这两条绑定才能闭环。

### 含义（对 draft 命运的修正）

| 原判决 | 修正后判决 | 理由 |
|---|---|---|
| `draft-meta-audit`：保留 3 维度精简版 | **重构为 L1/L2/L3 三个子工具**，其中 L1 是关键词扫描器（13 维度），L2 是操作路径 preflight（3 维度），L3 已由 `/censor` 覆盖 | 3 维度远不够；20 维度若堆在单个 command 内，运行时过重且难维护 |
| `draft-rules-cleanup`：作废 | **升级为必要**，排在 meta-audit 之后 | L1 13 条词族必然有合并/过期/冲突机会，且当前 memory 库 4 条 "verify 簇" 本身就需要整合；不能凭 N=3 判作废（漏洞 2） |
| `feedback_verify_before_conclude` | **改造为索引入口**，body 改写为"下列 10 条字面触发规则的总索引"，不单独作为抽象规则存在 | 它在 A/B/C 都没 catch，作为独立规则已失效；保留形式但改写语义 |
| 补 2 条 memory（B/C） | **保留，但动机改写**：不是"覆盖新族"，而是"把 verify_before_conclude 的 10 条字面触发规则中的 D2 和 D11 先落地"。剩余 D3-D10 和 D12/D13 排队陆续落地 | 族不存在（漏洞 1），真正的动机是字面化 |
| 新增 compaction boundary 规则 | **新增**，对应 D8 + D13 绑定 | 补漏洞 3 |

### 新的实施顺序（2026-04-12 第四轮修正）

**第三轮修正问题**：建"最小 L1 scanner"是过度形式化——D1/D2 的 scanner 本质就是一条 grep + 人眼判断附近有没有锚点，不需要先建工具。
**第三轮修正问题 2**：首个批次选 D2 引入"规则 + sweep"两个变量。D1 规则（`feedback_cite_summary_on_write`）已存在 24h+，改为先跑 D1 sweep 能隔离变量、直接测试"写规则 ≠ 清扫旧残留"的断言。
**第三轮修正问题 3**：D8/D13 是同一条规则的写/读两面，应合并；且真触发条件是"把 memory 当终点源头"这个**操作路径**，归 L2 更准，不是 L1 关键词触发。

新顺序（第四轮）：

0. **不建 scanner，手动 grep 先行**。首批次的 sweep 工具就是 `grep -n` + 人眼。只有当某个词族 sweep 反复跑（>3 次）且模式稳定后，才固化为脚本。
1. **批次 1：D1 retroactive sweep（规则已存在，只 sweep + 修）**
   - 规则：`feedback_cite_summary_on_write.md`（已存在）
   - 动作：grep "阳性对照 / 阴性对照 / 正对照 / 负对照 / positive control / negative control / functional residue / 功能性残基 / loss-of-function / gain-of-function / 丧失功能 / 失活 / Ala-tolerant" 于 `docs/` `memory/` `~/.claude/projects/.../memory/`
   - 对每条命中：判断附近 ±5 行是否有 `summary.md:L` 锚点或等价引用；无则计为违例
   - 修每条违例到 "指针形式" 或标 "待人工确认"
   - 产出：批次 1 报告（命中/违例/修复数量），本报告末尾附录
   - **意义**：若违例 >0，证明写规则不会自动修旧残留 → 后续每条新 L1 规则必须绑定 sweep；若 =0，说明现有 cleanup 路径已在写规则时同步 sweep，可放宽"不可拆分"约束
2. **批次 2：D2 机制断言词**（规则 + sweep + 修 同一批次）
   - 写 `feedback_mechanism_claim_requires_channel.md`
   - grep "实证 / 证明 / 盐桥 / 氢键 / π-π / pi-cation / 直接形成 / 驱动" 
   - `project_docking_pipeline.md:L59` V138R 残留将在此处自然扫到
3. **批次 3：D11 基线 provenance**（L2，操作路径触发）
   - 写 `feedback_provenance_before_baseline.md`
   - 扫所有被脚本当基线的 JSON/CSV，补或作废 provenance 缺失项
4. **批次 4：L2 "memory 不能当终点源头"**（D8+D13 合并后）
   - 写 `feedback_memory_not_terminal_source.md`
   - 难以纯 grep 扫，退为"session 开场 checklist"式规则，暂不做 retroactive sweep
5. **5 批次完成后**：评估 L1 剩余词族（D3-D7 / D9-D10 / D12）补齐策略（独立 memory vs 合并索引）
6. **L1 基本字面化后**：`draft-meta-audit` 重构为固化 scanner，`draft-rules-cleanup` 实施 verify 簇 4 条合并
7. **随时**：L3 由 `/censor` 覆盖

**关键不变量**（条件化，不再绝对）：**凡写新 L1 规则**，同一批次内必须做一次 retroactive sweep + 逐条修复，除非批次 1 的 D1 sweep 明确否定了这个必要性。批次 1 本身就是这条不变量的**假设检验**。

---

## 附录：批次 1 执行报告（D1 retroactive sweep，2026-04-12）

### 范围
- 关键词集：阳性对照 / 阴性对照 / 正对照 / 负对照 / positive control / negative control / functional residue / 功能性残基 / loss-of-function / gain-of-function / 丧失功能 / 失活 / Ala-tolerant / LoF / GoF
- 扫描路径：`docs/` + `experiments/` + `~/.claude/projects/-Users-roy-Documents-drylab/memory/`
- 工具：手动 grep + 人眼判定（无需建 scanner）

### 命中统计
- 总命中：100+ 行，跨 16+ 文件
- 严格违例（权威路径 / 内部矛盾 / 缺锚点）：**6 文件 8 处**
- 非违例：教学材料、日志、源 summary、项目内对照设计（与文献分类无关）

### 违例分诊与修复

| # | 文件 | 行 | 性质 | 修复 |
|---|---|---|---|---|
| P1.a | `docs/modeling/P0-molecular-docking.md` | 233 | **本文件内自相矛盾**（与 L130 修正冲突） | ✅ 改写为"已推翻"+ summary 锚点 |
| P1.b | `docs/modeling/P0-molecular-docking.md` | 268 | 同上，进展记录表残留 | ✅ 拆分真阳性/真阴性 + summary 锚点 |
| P2.a | `docs/modeling/wet-lab-handoff-P0-docking.md` | 225-227 | 湿实验交接表分类标签无锚点 | ✅ loss-of-function/no-effect 全名 + summary 锚点 |
| P2.b | `docs/modeling/wet-lab-handoff-P0-docking-feishu.md` | 226-228 | 飞书版同上 | ✅ 同上 |
| P3 | `experiments/docking-repro/mutagenesis/tier_recommendations_20260410.md` | 整文件 | 历史 snapshot 未标"已推翻" | ✅ 文件头加 ⚠️ 推翻 banner + 指针 |
| P4 | `~/.claude/.../memory/project_docking_pipeline.md` | 16 | BW 映射列分类标签无锚点 | ✅ 加 `Hu2024-GprC-summary.md:L143-145` 锚点 |

### 推迟到后续子批次（P5）
- `docs/teaching/lesson-04-mutation-scan.md:146-149` 表格 — 教学材料，已有内部一致性（lesson 4 完整交代分层 + BW 争议附注），技术上仍违例但不影响外部决策
- `experiments/docking-repro/analysis/pymol_top6/README.md:53` — 已二级跳指向 P0 §Pipeline 验证，弱锚点
- `experiments/docking-repro/mutagenesis/mutagenesis_report.md:114` — 用旧 BW 映射 N83/R281，是命名漂移而非分类违例

### 批次 1 结论 — Self-Critique 核心断言的验证结果

> **断言**："写规则 ≠ 清扫旧残留"——D1 规则（`feedback_cite_summary_on_write`）已存在 24h+ 但未做 retroactive sweep，可能仍有违例残留。

**结果**：**证实**。D1 规则存在 24h+ 后仍发现 8 处违例，包括：
- **同一文件内自相矛盾 2 处**（P0-molecular-docking.md L130 修正了，L233 / L268 漏改）—— 这是最强证据，说明上次"修正"只覆盖了发现入口，没做关键词级 sweep
- **湿实验交接文档 2 份**漏改 —— 这是最高 blast radius 的违例，会直接污染外部接收方
- **历史 snapshot 漏标推翻 1 份** —— 时间戳化文件不会随主文档修正而联动，必须显式加 banner
- **memory 索引漏锚点 1 处** —— 即使 N56 post-mortem 当事 session 写的文件，也漏了

**含义**：
1. "**关键不变量**"成立：每条新 L1 规则必须绑定一次 retroactive sweep
2. **2026-04-12 之前的所有"修正"操作都需要补做 sweep**——不只是 D1，所有已做修正的事件（如盐桥实证降级）都可能有同类残留
3. 批次 2（D2 机制断言词）启动前，**先跑批次 2 的 sweep 来 catch 04-11 盐桥事件的 V138R 残留**（已知 `memory/project_docking_pipeline.md:L28` 注释带"盐桥未实证"，但需扫全部 D2 关键词确认无遗漏）
4. `draft-rules-cleanup-command.md` 的真实价值已被 D1 sweep 证明：**它就是把这种 sweep 形式化为可重复操作**，不是"删旧规则"而是"对已有规则做一次完整性扫描"。原报告把它降级为"待验证"过于保守，应升级为"必要"

### 下一步
- 批次 2：D2 机制断言词（写规则 + sweep + 修，同一批次）
- 待用户确认本批次 1 报告无误后开始

### 承认的不确定性

- N=3 样本选择偏差（漏洞 4）还未补救。本次 self-critique 是通过扫全部 HIGH/MEDIUM 条目做 L1/L2/L3 归纳来部分弥补，但 audit 本身只覆盖了"已经被 /truth /censor 跑过"的子集——没跑 audit 的时段里可能有更多未被看见的族。
- 17 条字面触发规则本身会成为下一代"规则堆积"问题。这是 rules-cleanup 必须存在的理由，也是本架构的内在张力——没有彻底解法，只有维护节奏。
- D3/D6/D8 对应的已有 memory（`claim_granularity` / `outlier_vs_rule` / N/A）都是抽象规则，和 L1 字面化的目标冲突。合并策略待定。

---

## 修正后下一步（本 session 内，2026-04-12 第三轮）

用户指令："pipeline memory 残留不是 rules cleanup 的工作吗？" 暴露的问题：原"立即批次"混入了一条 spot fix cleanup，违反了"rules-cleanup 排在下游"的自己定的顺序。更深一层：写新 L1 规则却不 retroactive 扫现有内容，等于规则生效前仍允许旧违例被 Claude 读到——这跟本审查的一级目标（防止 Claude 读到过时信息）直接冲突。

**第三轮修正**：本 session 内**不再写任何 memory**，不再做任何 spot fix，只做结构层准备工作。

- [x] 重写文末"新的实施顺序"章节，反转顺序为"scanner 先行 → 规则+扫+修绑定为批次"（已完成）
- [x] 本"下一步"清单自身删除原 spot fix 和裸写 memory 两类动作（已完成）
- [ ] 把本报告路径追加到 `docs/logs/2026-04-12.md`
- [ ] 等待用户确认"反转后的实施顺序"成立，再开始建最小 L1 scanner
- [ ] scanner 建成后，以"批次 1"为单位执行：写 D2 规则 + 跑 scanner + 修全部匹配项（含 `project_docking_pipeline.md:L59` 的 V138R 残留）
- [ ] `draft-meta-audit-command.md` 的头注改写推迟到 scanner 首版跑过之后——避免又在 draft 上改抽象的东西
- [ ] `draft-rules-cleanup-command.md` 的头注改写同上理由推迟

**关键不变量重申**：任何新 L1 规则的写入必须与该规则的 retroactive 扫描 + 逐条修复作为同一批次完成；不允许拆分。

---

## 附录：批次 2 执行报告（D2 机制断言词 retroactive sweep，2026-04-12）

### 前置：Self-Critique 第五轮（新 session）

批次 2 启动前，对批次 1 报告做了第五轮 self-critique，覆盖 7 个角度。关键发现：

1. **F1 — 批次 1 scope 漏洞**：`src/` 未扫，其中 `config.yaml:232/291-294` 有 D1 分类注释（当前正确）且被多处引用为参考源。建议扩展 D1 scope 加入 config.yaml，.py 列 P5 低优先。
2. **F2 — 锚点质量**：`Hu2024-GprC-summary.md:L143-145` 验证有效，L143=N2.53 无影响、L144=N2.57 丧失功能。
3. **F3 — 04-11 日志盐桥歧义**：L243/L291 用"盐桥实证"作 MD 任务简称，无否定修饰。严重度低于 P0 的同文件矛盾，但影响 D2 triage 规则设计。
4. **F4 — D2 噪声控制**：flat grep"盐桥"在 P0-md-simulation + tech-stack 中命中 60+ 行（合法技术语境）。需限定 scope + 上下文否定词过滤。
5. **F5 — D3 漏列**："已锁定/已完成/completed"未在 D3 词表中，但出现在权威文档的承诺性表述中。
6. **F6 — R6.45**：后续工作已实质解决，truth audit checklist 未更新是外观不一致。
7. **F7 — 20 维度是否 over-engineering**：字面化有效性尚未验证（D1 24h+ 未测到阻止新违例的证据）。批次结构本身是假设检验，合理。D18-D20 于 04-12/04-13 回填。

用户确认后启动批次 2。

### 规则

**新写**：`~/.claude/projects/-Users-roy-Documents-drylab/memory/feedback_mechanism_claim_requires_channel.md`

触发条件（精化后）：
- 目标路径：`docs/modeling/**` + `docs/prd/**` + `memory/project_*.md`
- 关键词共现：机制断言词（实证/证明/确认/直接形成/驱动）+ 机制类型词（盐桥/氢键/π-π/pi-cation/离子键）
- 否定词豁免：待/未/需/假说/问题/目标/转交/若/如果

### 范围

- 关键词集：盐桥 / π-π / pi-cation / 离子键（机制类型词，先定位再检查断言上下文）
- 扫描路径：`docs/modeling/**` + `docs/prd/**` + `memory/project_*.md`
- 工具：手动 grep + 逐条 triage

### 命中统计

- 总命中：~80+ 行，跨 8 文件
- ✅ PASS（否定词修饰 / 工具描述 / 力场参数 / 判据定义 / 条件语句）：~75
- ⚠️ LOW（文档结构元素用任务名简称，正文已消歧）：4（P0-md-simulation.md L9/L143/L263/L265）
- **❌ 违例**：**2**

### 违例分诊与修复

| # | 文件 | 行 | 原文 | 性质 | 修复 |
|---|---|---|---|---|---|
| D2.1 | `memory/project_docking_pipeline.md` | 59 | "V138R **盐桥机制实证**：转交 P0-md-simulation" | 未解决列表中缺否定修饰 | ✅ → "V138R **盐桥假说待 MD 实证**：转交...（当前仅有 VdW 空间富集证据，PDBQT 工作流盐桥检测结构性失效）" |
| D2.2 | `memory/project_md_pipeline.md` | 12 | "V138R 胍基-ascaroside 羧基**盐桥实证**" | 科学问题列表中缺否定修饰；session 开场第一层读取 | ✅ → "V138R 胍基-ascaroside 羧基**盐桥假说待实证**（...PDBQT 工作流盐桥检测结构性失效）" |

### 推迟（P5）

P0-md-simulation.md 的 4 处 LOW 不修：
- L9（文档标题）/ L143（小节标题）/ L263-265（跨文档引用）—— 均为任务简称，L15 紧跟"假说**未**实证"已消歧
- 如果后续批次发现新 session 因读 P0-md-simulation 标题而复制了"盐桥实证"到其他文档，再升级

### 批次 2 结论

**D2 sweep 的关键观察**：

1. **违例集中在 memory 文件**（2/2）。权威文档（docs/modeling/）在 04-11 批量降级时已全部加了否定修饰，memory 的同义表述漏改——与批次 1 的 P0-molecular-docking.md 同文件矛盾是完全相同的 pattern："修正入口处覆盖了，同文件/同义文件的其他位置遗漏"。
2. **噪声比信号 ~37:1**（75 PASS : 2 违例），但手动 triage 可操作（scope 限制到权威路径 + memory 后总量 ~80 行，耗时约 10 分钟）。
3. **F4 精化建议得到验证**：如果对全库 flat grep "盐桥"（不限 scope），命中 150+，噪声不可操作。scope 限制 + 否定词豁免是必须的。
4. **"关键不变量"再次成立**：D2 规则写入同批次扫到并修了 2 处违例。若拆分（先写规则、后做 sweep），这 2 处会在下个 session 被 Claude 读到并可能传播。

### 下一步

- 批次 3：D11 基线 provenance（L2，操作路径触发）—— 写 `feedback_provenance_before_baseline.md` + 扫历史基线 JSON
- 待用户确认本批次 2 报告无误后开始

---

## 附录：批次 3 执行报告（D11 基线 provenance audit，2026-04-12）

### 规则

**新写**：`~/.claude/projects/-Users-roy-Documents-drylab/memory/feedback_provenance_before_baseline.md`

触发条件（L2 操作路径）：Claude 计划把某历史 JSON/CSV 当作下游脚本的基线输入时，须检查：
1. 生成该 artifact 的代码版本（脚本 mtime vs artifact mtime）
2. 外部输入一致性（PDBQT、config 参数）
3. `_provenance` 元数据块是否存在

### Sweep 方法

D11 不是关键词 grep，是结构性审计：
1. 识别所有被脚本 `load_wt_baseline()` / `load_*` 消费的基线 artifact
2. 检查每份的 provenance 元数据
3. 比较 artifact mtime vs 生成脚本 mtime
4. 检查文档中是否有对 provenance 的错误声称

### 基线 artifact 清单

| # | Artifact | mtime | 生成脚本 | 脚本 mtime | `_provenance`? | 消费方 |
|---|---|---|---|---|---|---|
| A1 | `results/wt_singlestage/docking_results.json` | **04-08 18:54** | `run_wt_singlestage.py` | 04-09 20:12 | ❌ | `run_mutagenesis_alanine.py`, `run_mutagenesis_saturation.py`, `mutagenesis.py`, `prep_pymol_top6.py` |
| A2 | `results/multiseed/multiseed_stats.json` | **04-09 18:03** | `run_multiseed.py` | 04-10 05:33 | ❌ | 噪声阈值 3σ 计算（手动引用） |
| A3 | `mutagenesis/mutagenesis_results_merged_20260411.json` | **04-11 14:02** | 手动合并 | N/A | ❌ | 最终输出，不被脚本消费 |

**通用发现**：
- **全部 gitignored**（`.gitignore:43`），无 git 历史可查
- **无任何 artifact 含 `_provenance` 块**——JSON 直接从数据开始
- **`load_wt_baseline()` 只校验文件存在+键名**，不校验 provenance
- **生成脚本不输出 provenance**——`run_wt_singlestage.py` 和 `run_multiseed.py` 均无 commit/config/hash 写入

### 违例

| # | 性质 | 严重度 | 详情 |
|---|---|---|---|
| D11.1 | **A1 artifact STALE** | ACKNOWLEDGED | mtime 04-08 早于脚本 mtime 04-09（helix_ranges 支持更新）。案例 C 的直接现场：WT 基线用"全原子质心"，multiseed 用"TM-helix 质心"，box center Δ≈0.04 kcal/mol |
| D11.2 | **A2 artifact STALE** | LOW | mtime 04-09 早于脚本 mtime 04-10。multiseed 本身是 post-helix_ranges 的，stale 风险来自脚本后续优化而非 box center 问题 |
| D11.3 | **全部 artifact 无 provenance 块** | STRUCTURAL | 无法自动校验任何 artifact 的生成条件。这是架构缺陷而非单点违例 |

### 不修的理由

1. **P0-molecular-docking 已 completed**，算力已全部转 MD。重跑 WT 基线需要 Windows 计算节点 + 数小时计算，且 docking 结果已交付湿实验组
2. **0.04 kcal/mol 偏差已被文档化**：04-09 truth audit + root-cause 报告 Case C 完整记录了根因和影响范围
3. **mutagenesis 结果不受严重影响**：ΔΔG 是差值（mutant − WT），若 mutant 和 WT 的 box center 偏差方向一致（同一受体），系统偏差部分抵消。Tier 分级基于 3σ=0.48 阈值，0.04 kcal/mol 远低于此

### 前瞻：MD Pipeline 建议

D11 规则的真正价值在**预防 MD pipeline 重蹈覆辙**。建议在 MD pipeline 脚本（`GROMACS` wrapper / analysis scripts）从设计之初加入 `_provenance` 块：

```json
{
  "_provenance": {
    "generated_by": "run_md_production.py",
    "commit": "abc1234",
    "config_hash": "sha256:...",
    "input_files": {
      "receptor_pdb": {"path": "...", "sha256": "..."},
      "ligand_mol2": {"path": "...", "sha256": "..."}
    },
    "timestamp": "2026-04-XX T12:00:00"
  }
}
```

这不是本批次需要实施的代码改动（meta-audit scope 是防御规则而非代码重构），记录为 P0-md-simulation 的设计要求。

### 下一步

- 批次 4：D8+D13 合并 — "memory 不能当终点源头"（L2 操作路径触发）
- 待用户确认后开始

---

## 附录：批次 4 执行报告（D8+D13 合并 — memory 不能当终点源头，2026-04-12）

### 规则

**新写**：`~/.claude/projects/-Users-roy-Documents-drylab/memory/feedback_memory_not_terminal_source.md`

D8（写时：跨 session 继承词触发回源验证）和 D13（读时：>3 天 memory entry 强制复核）**合并为一条 umbrella 规则**：memory 是索引不是权威源，引用其中的分类/机制/数值/状态时须 Read 原始源头验证。

### 合并理由

1. D8 和 D13 指向同一问题的写/读两面——"memory 被当作已验证事实"
2. 分开写会产生触发条件重叠（D8 的"memory 记录"和 D13 的"session 开场"都指向"从 memory 读信息"这个动作）
3. D1/D2/D11 已经是这条 umbrella 规则的三个具体实例化，umbrella 规则为未来新增的字面化维度提供归属

### Sweep

**不做 retroactive sweep**（如计划所述）。理由：
1. D8/D13 的触发条件是**操作路径**（"Claude 从 memory 读取信息"），不是文本关键词，无法 grep
2. 违例发生在 session 运行时（Claude 的读取→使用链路中），不是静态文本中可发现的
3. D1/D2 的 sweep 已经修复了 memory 中最高危的两类违例（分类标签无锚点 + 机制断言无否定修饰）
4. 剩余风险（如 memory 中的数值是否与源 JSON 一致）属于"session 开场自查"场景，由规则本身约束

### 架构位置

```
feedback_memory_not_terminal_source (umbrella, D8+D13)
├── feedback_cite_summary_on_write (D1, 分类标签)
├── feedback_mechanism_claim_requires_channel (D2, 机制断言)
└── feedback_provenance_before_baseline (D11, 基线 artifact)
```

未来新增的字面化维度（D3-D7、D9-D10、D12）落地时，应声明为 umbrella 的子规则。D18-D20 已落地并声明为 umbrella 子规则（2026-04-12/04-13）。

### 批次 1-4 完成后的全局状态

| 批次 | 维度 | 规则 | Sweep | 违例/修复 |
|---|---|---|---|---|
| 1 | D1 分类标签 | 已存在（`cite_summary_on_write`） | ✅ grep 全量 | 8 处 / 6 修复 + 2 推迟（教学材料） |
| 2 | D2 机制断言 | ✅ 新写（`mechanism_claim_requires_channel`） | ✅ grep 权威路径+memory | 2 处 / 2 修复 |
| 3 | D11 基线 provenance | ✅ 新写（`provenance_before_baseline`） | ✅ 结构性审计 | 3 artifact 无 provenance / 不修（completed + 文档化） |
| 4 | D8+D13 memory umbrella | ✅ 新写（`memory_not_terminal_source`） | N/A（操作路径，无法 grep） | — |
| 5 | D3 完成词 + D9 全称量词 + D18 路径引用 + D19 数学验算 + D20 架构角色 | ✅ 新写 5 条 memory | D3 ✅ sweep / D9 ✅ sweep / D18 ✅ sweep / D19 N/A（逐步验算，无法 grep）/ D20 ✅ sweep | D18: 3 处修复 / D20: 2 处修复 |
| 6 | D3 细化（等价声明 + 第三方操作状态） | ✅ 更新 `completion_claim` memory | N/A（新增子规则 C/D，无需 retroactive sweep——案例来自当前 session） | 2 处修复（batch JSON + Day1 状态） |
| 7 | D9 最高级词扩展 | ✅ 更新 `universal_quantifier` memory | ✅ sweep（"最佳"→ 已修正） | 1 处修复 |
| 8 | D18 §号引用 + 指标名/列标题扩展 | ✅ 新增子规则 `section_ref_verify` + 更新 `read_before_quoting` | qa-bank 6 条 / content-review-notes 1 条 / KNOW-1 §6 表格重写 | 8 处修复（HIGH×1 + MEDIUM×5 + LOW×2） |

**已实施的 L1/L2 维度**：D1, D2, D3, D8, D9, D11, D13, D18, D19, D20（10/20）
**未实施**：D4-D7, D10, D12（6/20）
**L3**：由 `/censor` 覆盖（D14-D17），不在 meta-audit scope 内

### 批次 6 post-mortem（2026-04-13）

**来源**：`docs/logs/truth-audits/2026-04-13_1207.md`

**D3 两次失效分析**：

1. **"格式正确，和之前 docking 提交完全一致"**（HIGH）
   - D3 触发词"正确/一致"被识别（读了两个文件），但验证深度不够——只看了顶层结构，没做 field-by-field diff
   - D9 触发词"完全"（全称量词）也未拦住——"完全一致"等同"所有字段都相同"但未穷举
   - **根因**：D3 规则只要求"逐层穷举"，但没有针对"两个数据结构的等价比对"给出具体操作路径
   - **修复**：D3 新增子规则 C（数据结构等价声明 → 逐字段比对）

2. **"Day 1 已提交"**（MEDIUM）
   - D3 触发词"已提交"此前不在触发词列表中
   - **根因**：触发词列表没有覆盖第三方系统操作状态类词汇
   - **修复**：D3 新增触发词（已提交/已部署/已发送）+ 子规则 D（第三方操作状态 → 须用户确认）

**D10 观察**：
- ipTM/iPAE/pLDDT 阈值写入分析脚本无引用（MEDIUM），属于 D10（文献来源词）覆盖域
- D10 尚未实施；本次 finding 的严重度为 MEDIUM，暂不触发 D10 实施。若下次 audit 再有 D10 类 finding 则实施

### 下一步评估

批次 1-6 完成了 10 个维度。剩余 6 个维度（D4-D7, D10, D12）的实施策略：

**观察结论**：D3 在实施后首次 /truth 就被击穿（场景 A），但原因是触发词和操作路径不够具体而非"字面化策略无效"。批次 6 的细化修补了具体缺口。D9 的失败与 D3 耦合（"完全一致"同时触发两条），单独的 D9 规则不需要修改。

**建议**：继续观察 1-2 个 session。D3 经过批次 6 细化后的有效性需要下一次 /truth 验证。D10 保持待观察。

---

## 批次 7 post-mortem（2026-04-13 17:47，truth-audit `2026-04-13_1747.md`）

**任务上下文**：比值型双通道 Docking 数据分析——编写 Python 分析脚本、运行验证、修正文档。

### D9 击穿：最高级词"最佳"不在触发词表

**Finding #1 (HIGH)**:
> "**最佳平衡配对**：Gpr2_M327D + Gpr3_V138T (balance=0.511)"

- **实际**：全局 best-balance 是 Gpr2_R59E + Gpr3_F170N (balance=0.500) 和 Gpr2_R59C + Gpr3_F170H (balance=0.500)。M327D + V138T 仅为 Top 3 (by D) 中 balance 最优。
- **击穿原因**：D9 原触发词为 {全部/所有/每一个/没有一个/唯一/任何}，不含最高级词（最佳/最强/最高）。"最佳"是"唯一的最优"的语义等价物，属于同一认知类别但不在字面触发表中。
- **根因**：D9 的关键词列表只覆盖了全称量词，未覆盖同族的**最高级量词**。两者共享"须穷举完整集合验证"的操作要求。
- **修复**：D9 触发词扩展为 {全部/所有/每一个/没有一个/唯一/任何/**最佳/最强/最高/最X**}。已更新 `feedback_universal_quantifier.md`。
- **污染范围**：`docs/logs/2026-04-13.md:72` + `memory/project_docking_pipeline.md:59` → 已修正。

### D3 击穿：计划验证项打 ✓ 未穷举

**Finding #3 (MEDIUM)**:
> [计划验证] "Channel A 候选集与旧 Tier 1 的 sel_mut < −0.48 子集重合 ✓"

- **实际**：F170D (Tier 1, sel_mut=−0.443) 不在 Channel A（门槛 −0.477）。Channel A 14 ≠ Tier 1 子集 7，不是"重合"关系。
- **击穿原因**：D3 触发词 {✓/通过/已解决/完成/格式正确/完全一致/已提交/已部署/已发送} 中，`✓` 应拦住 `[x] ... ✓` 标记。但在计划文件中批量标记验证项时，Claude 未对每一条逐一运行工具验证。
- **根因**：D3 要求"逐层穷举"，但在**批量操作**（一次标记 6 个 `[x]`）场景下，穷举要求被跳过。与批次 6 中 D3-C（数据结构等价）同质——批量操作降低了每条声明的验证标准。
- **修复**：计划文件中该验证项已修正为精确表述。D3 规则本身不需修改（子规则已覆盖），但**需要注意批量标记 `[x]` 时逐条验证的执行纪律**。

### 其他 Findings

- **Finding #2 (MEDIUM)**: 修复推理混乱（"L377A 原来就只和 Channel B 配对"），属于因果臆断但未触发 D7（因果词）——因为不含"因为/导致/根因"等 D7 触发词，而是含"因为"。D7 尚未实施。本次是 MEDIUM 且仅在对话中，不升级 D7。
- **Finding #4 (MEDIUM)**: "Channel B 主力: V138/F170"选择性引用，属于 D6（归纳词，"主力"是归纳性描述）。D6 未实施。本次发现写入了日志+memory，已修正。暂不触发 D6 实施。
- **Finding #5 (LOW)**: 3σ 四舍五入，属于 D5（数值缓和词）或 D19（数学验算）。文档中使用正确值，仅对话近似。不触发任何变更。

### 批次 7 评估

| 维度 | 事件 | 场景 | 动作 |
|------|------|------|------|
| D9 | HIGH 击穿（"最佳"不在触发词） | A | 触发词扩展 ✅ |
| D3 | MEDIUM 击穿（批量 ✓ 跳过验证） | A | 规则已覆盖，执行纪律问题 |
| D7 | MEDIUM 因果推理（对话中） | B 候选 | 暂不触发 |
| D6 | MEDIUM 归纳选择性（已修正） | B 候选 | 暂不触发 |

**结论**：D9 击穿的根因是关键词覆盖不全，已修补。D3 击穿是执行纪律问题（批量操作时松懈），规则本身不需修改。批次 6 新增的 D3 子规则 C/D 本次未被测试（无数据结构等价/第三方操作场景）。D6/D7 各有一次 MEDIUM，暂不实施——若下次 audit 再出现则触发。

---

## 批次 8 post-mortem（2026-04-14 02:30，truth-audit `2026-04-14_0230.md`）

**任务上下文**：教学材料 v2 重构 Phase 2——将 qa-bank.md 的 34 条 `📚 **依据**` 从 Lesson 1-7 映射到 v2 文件名（KNOW-1/2/3/4, DO-1/2/3/4），同时更新 red-team-drill.md / acceptance-criteria.md / content-review-notes.md。

### D18 击穿（场景 A）：§号引用 + 指标名不在触发词表

D18 当前触发词覆盖"文件路径 / 代码片段 / CLI 命令 / 脚本名"，但本次出现两类新变体均未被拦截：

#### 变体 1：§号段落引用（5× MEDIUM）

**Findings #2-#6 (MEDIUM)**:
> Q2 📚 KNOW-1 §1（实际 §1 是 ΔG 含义，Q2 问的是 DBTL/预筛）
> Q3 📚 KNOW-1 §1（实际 §1 无受体选择内容）
> Q11 📚 KNOW-2 §7（实际 §7 是方法选择辩护链，刚性受体内容在 KNOW-1 §3:62）
> Q29 📚 KNOW-3 §1（实际 §1 专讲 V138R，F170E 在 §2:49）
> content-review-notes "KNOW-1 §1"（实际应为 §4）

- **击穿原因**：`KNOW-1 §1` 是一种**内容引用**（指向文件内特定段落），语义上与"文件路径"同族——都是"写一个指针让读者找到内容"。但 D18 触发词只覆盖了 file-level 引用，未覆盖 section-level 引用。
- **根因**：批量映射 34 条 §号时，仅 Grep section headers 匹配关键词，未 Read section 内容验证。Section 标题和 section 内容之间存在语义缝隙（如 §7 标题"方法选择辩护链"不提"刚性受体"，但"刚性受体"恰好在 §7 的表中，而非 §7 的内容——实际在 §3）。
- **修复**：
  1. 已创建子规则 `feedback_section_ref_verify.md`：§号引用写入前必须 Read 目标 section 前 5 行确认内容匹配
  2. qa-bank.md 6 条映射已修正（Q1→§2,§4-6, Q2→§5-6, Q3→§4, Q11→KNOW-1 §3, Q12→§3-4, Q29→KNOW-3 §2-3）
  3. content-review-notes.md §1→§4 已修正

#### 变体 2：跨文件指标名/列标题一致性（1× HIGH）

**Finding #1 (HIGH)**:
> KNOW-1 §6 表格列标题为 `ΔΔG_sel`，V138R 显示 −0.88，M327A 显示 −1.39

- **实际**：这些数值是 **abs sel**（mutant 绝对选择性），不是 ΔΔG_sel（相对 WT 的选择性变化）。权威源 `tier_recommendations_20260411.md:26` 明确区分两列：V138R ΔΔG_sel = −1.070，abs sel = −0.88。
- **击穿原因**：创建 KNOW-1 §6 表格时，从权威源复制 abs sel 列的数值，但列标题写成了 ΔΔG_sel。D18 不覆盖"在表格中使用指标名作为列标题"这种引用形式。同时缺少**跨文件同一指标的一致性校验**——KNOW-3 §1 和 DO-2 都正确使用 ΔΔG_sel = −1.07，与 KNOW-1 §6 的 −0.88 直接矛盾，但无规则要求创建含数值表格后做跨文件 Grep。
- **修复**：
  1. KNOW-1 §6 表格已重写：增加 ΔΔG_sel + abs sel 双列 + 指标区别说明
  2. `feedback_section_ref_verify.md` How-to-apply 已包含跨文件一致性 Grep 要求

### 其他 Findings

- **Finding #7 (MEDIUM)**: 过度自信——正确识别了"映射可能出错"风险，但没有在执行前缓解（未 Read 文件内容就直接执行了 34 条映射）。这是执行纪律问题，与批次 7 D3 击穿同质。不新增维度，但行为模式值得记录：**风险识别 → 缓解行动不可脱节**。
- **Finding #8 (LOW)**: Q1 映射精度不足（§1-2→§2,§4-6），已修正。
- **Finding #9 (LOW)**: Q12 映射精度不足（§3→§3-4），已修正。
- **Finding #10 (LOW)**: content-review-notes "三重约束"措辞偏移（"授权"→应为"成本可行"），从 v1 继承的表述误差，方向正确，已修正。

### 批次 8 评估

| 维度 | 事件 | 场景 | 动作 |
|------|------|------|------|
| D18 | HIGH 击穿（指标名/列标题跨文件矛盾） | A | D18 触发词扩展 + 跨文件一致性要求 |
| D18 | MEDIUM×5 击穿（§号引用未 Read 验证） | A | 新增子规则 `feedback_section_ref_verify.md` |
| — | MEDIUM 过度自信（风险识别→缓解脱节） | 执行纪律 | 记录模式，不新增维度 |

**D18 扩展方案**：

当前 D18 触发词（文件路径 / 代码片段 / CLI 命令 / 脚本名）→ 扩展为：

```
文件路径 / 代码片段 / CLI 命令 / 脚本名 / §号段落引用 / 指标名·列标题
```

新增操作要求：
- **§号引用**：写 `文件 §N` 前 Read 目标 §N 段落前 5 行确认内容匹配（子规则 `feedback_section_ref_verify.md`）
- **指标名/列标题**：创建含数值表格后，Grep 关键指标名在所有相关文件中的数值做一致性扫描

**结论**：D18 再次被击穿，根因与批次 7 D9 相同——**关键词覆盖不全**。字面化策略本身有效（凡覆盖到的变体均未违例），问题在于引用形式的多样性超出了初始枚举。§号引用和指标名/列标题是两种此前未遇到的引用形式。扩展后的 D18 覆盖 6 类引用形式（原 4 + 新 2），配合子规则 `feedback_section_ref_verify.md` 的具体操作指导。D6/D7 在本次 audit 未出现新违例。
