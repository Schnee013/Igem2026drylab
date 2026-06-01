# Draft: `/rules-cleanup` 命令

> **状态**：草案。用户审核通过后移至 `~/.claude/commands/rules-cleanup.md`。

---

## 命令说明

基于 `/meta-audit` 的 findings，对 memory / CLAUDE.md / DOCMAP 做严格清理与合并。**执行治疗，但只处理 meta-audit 已诊断的问题**，不自行发现新 finding。

是 `/meta-audit` 的下游命令，不是独立审查机制。

---

## 前置条件

1. **必须指定一份 meta-audit 报告**（`docs/logs/meta-audits/YYYY-MM-DD_HHmm.md`，默认最新一份）
   - 没有任何 meta-audit 报告 → 命令终止，要求先跑 `/meta-audit`
2. **报告消费前必须做新鲜度检查**：对比报告中列出的"扫描文件清单 + 最后修改时间"与当前 repo 状态
   - 若 `memory/` / `CLAUDE.md` / `DOCMAP.md` / `rules/` 下任一文件在报告生成后被修改过 → 命令终止，要求重新跑 `/meta-audit`（规则已变动，旧 findings 不可信）
   - 这条取代了任何按小时计的时效窗口
3. **meta-audit 报告必须包含 "启动建议" 段**
   - 建议 "是" 或 "部分" → 本命令正常启动
   - 建议 "否" → 命令警告并要求用户显式 confirm 才启动
4. **命令启动前必须创建安全回滚点**
   - 使用 `git stash push -u -m pre-cleanup-YYYY-MM-DD_HHmm` 覆盖以下 scope：`memory/`、`~/.claude/rules/`、`CLAUDE.md`、`DOCMAP.md`、`MEMORY.md`、`docs/logs/meta-audits/example-archive.md`
   - 创建失败 → 终止。**scope 必须涵盖 example-archive.md**，否则 R5 归档无法回滚
   - 回滚点 ID 必须写入 cleanup-runs 报告

---

## 输入契约

命令读取的唯一输入是 meta-audit 报告中 **D3、D4 findings**（加少量 D2 中被标为 R5 的条目）。

- **不得读取 meta-audit 报告以外的 findings 源**
- **不得扫描未被 meta-audit 标记的 memory 条目**自行发现新问题
- 如果用户希望处理 meta-audit 未发现的问题 → 要求先重跑 `/meta-audit`

---

## 五类分类（R1-R5）

每条 finding 必须落入以下五类之一，否则打标 SKIP 跳过不处理：

| 类 | 定义 | 处理动作 |
|---|---|---|
| **R1** 完全重复 | 字面级或同义复述，触发条件、检查步骤、判据全部相同 | 删除副本，保留原件。**保留判据**：优先保留 Why 段字符数更多（更具体）的一条；若相等，保留 frontmatter `originSessionId` 对应 session 更早的一条；仍相等则看 git log 首次提交时间 |
| **R2** 本质相同措辞不同 | 触发条件相同，结论相同，但文字表述差异 | 合并为一条，在被合并位置留 `→ 指针 + 2 行摘要`；原条目的 Why 案例 append 到目标条目的 Why 段。**目标条目判据**：同 R1 保留判据（Why 字符数 > originSessionId 更早 > git 首次提交更早） |
| **R3** 部分重叠 | 触发条件有交集但不完全相同 | **不合并**。只在两条规则底部加 `**See also**: [其它规则名](file.md)` 一行。不改动规则主体 |
| **R4** 抽象告诫无触发条件 | D3 findings 指向的规则，只有"要注意 X"无可执行动作 | 改写为 (触发条件, 检查步骤, 判据) 三元组。Why 段完整保留不改动 |
| **R5** 规则正确但 example/Why 过时 | 规则主体仍有效，但 Why 段引用的文件路径 / 数据 / 残基名已不存在或被重构 | 替换 Why 的 example 为最近同类案例，旧 example **完整**归档到 `docs/logs/meta-audits/example-archive.md` 保留追溯性。新 example 三种来源按优先级：(a) 用户手动提供（最优，用户更清楚哪些案例最切题） (b) 近期 truth-audit findings (c) logs/ 里同类事件 |

**R5 的判定来源**：Subagent B 在 meta-audit 阶段 2 里 Grep example 中的文件路径/残基名，命中失效则标记 R5 候选。

---

## 处理流程

### 阶段 1 — 输入验证与预分类

1. Read meta-audit 报告
2. 执行新鲜度检查：按 meta-audit 输出段"扫描文件清单"的格式 parse 每行 `path — mtime — sha256[:8]`，对每个文件 `stat` 当前 mtime + 重新计算 sha256[:8]，任一不一致 → 终止
3. **续跑检查**：扫描 `docs/logs/cleanup-runs/` 最新一份报告，若存在 partial success 且输入的 meta-audit 报告路径与本次相同 → 自动跳过已标 ✓ 的 findings，从中断点继续处理；否则正常开始
4. 提取 D3、D4 findings + D2 中标为 R5 的条目
5. **过滤已拒绝条目**：Read `docs/logs/cleanup-runs/rejected-findings.md`，跳过历史已拒绝的 finding（meta-audit 应已在报告中标过，但此处兜底）
6. 对每条 finding 预分类 R1-R5
   - 无法分类的条目打标 SKIP 并在最终报告里列出
   - **meta-audit 已标注类别的直接沿用**，不重新分类
7. 创建安全回滚点（按前置条件 4 的 `git stash` 策略）
8. 创建 `docs/logs/cleanup-runs/YYYY-MM-DD_HHmm.md`（UTC+8），记录输入报告路径 + 回滚点 ID + 使用的方案 + 续跑起点（若有）

### 阶段 2 — 逐条预览生成

对每条 R1 / R2 / R4 / R5 生成一份"变更预览表"。
**R3 不生成预览**，直接在两条规则底部加 see-also 链接，不需要用户审批。

预览表格式：

```markdown
### Finding #N — [类别 R1-R5] [简述]

**目标文件**: path/to/memory.md

**Before**:
> 原文引用（含行号）

**After**:
> 建议措辞

**风险评估**:
- 合并/改写后可能丢失的情境: ...
- 是否影响下游调用: ...
- 是否会和现有 see-also 冲突: ...

**交叉引用扫描**（Grep 命中）:
- path/to/file1.md:L42 → 引用本规则作 X
- path/to/file2.md:L88 → 引用本规则作 Y
- [是否存在失效指针风险: 有/无]

**R5 特有字段**（仅 R5）:
- 旧 example 归档位置: `docs/logs/meta-audits/example-archive.md#YYYY-MM-DD_entry-N`
- 旧 example 摘要: [不摘要，完整引用]
- 新 example 来源: `用户手动提供` / `docs/logs/truth-audits/YYYY-MM-DD_HHmm.md#findN` / `docs/logs/YYYY-MM-DD.md`
- 新 example 是否真实对应同一规则: 是/否（需用户判断）
- **若无自动可用 example**：在预览表中明示"自动检索无果，请手动提供或确认 Why 段标注'案例待更新'"

**阻断信号**:
- 交叉引用 Grep 命中失效指针: 是 → 自动转 SKIP
- R1 两条规则触发条件/检查步骤/判据字面不完全一致: 是 → 自动降级为 R2；若连 R2 都不符合 → 降级为 R3
- R2 合并但触发条件不完全相同: 是 → 自动降级为 R3
- R5 自动检索无果且用户未手动提供: 是 → 本条只归档旧 example，Why 段留标注 "案例待更新"
```

### 阶段 3 — 用户逐条审批

对每条预览要求用户选择：

- **Y** — 批准，应用变更
- **N** — 拒绝，写入 `docs/logs/cleanup-runs/rejected-findings.md`（持久化列表，下次 meta-audit 阶段 4 必读；已列入的 finding ID 在 meta-audit 输出中仍列出但标 `[历史已拒绝 YYYY-MM-DD，跳过类别标注]`）
- **DEFER** — 推迟，仅写入本次 cleanup-runs 报告，不进 rejected-findings.md

**不允许批量 Y**。每条必须独立确认。

如果用户在审批过程中断（Ctrl+C / 关闭会话），已批准部分的状态写入 cleanup-runs 报告，未审批部分标 DEFER。

### 阶段 4 — 应用

- 只对 Y 条目执行 Edit
- **每条 finding 的 Edit 严格顺序**（任意中断点都不得出现"index 指向不存在的文件"）：
  1. 先 Edit `MEMORY.md` 更新或删除 index 指针
  2. 再 Edit / 删除目标 memory 文件本身
  3. R2 合并时：先 append Why 到目标条目 → 再删被合并条目 → 最后更新 MEMORY.md
  4. R5 归档时：先 write 旧 example 到 `docs/logs/meta-audits/example-archive.md` → 再 Edit 目标 memory 的 Why 段 → MEMORY.md 若条目未重命名则无需改动
- 应用过程中如任何一步 Edit 失败：
  - 停止后续条目处理
  - 不回滚已成功的条目
  - 在 cleanup-runs 报告中标 "partial success" 并列未应用条目及中断点

### 阶段 5 — 验收与归档

在 `docs/logs/cleanup-runs/YYYY-MM-DD_HHmm.md` 中写入：

```markdown
# Rules Cleanup Run — YYYY-MM-DD HH:mm

## 输入
- meta-audit 报告: docs/logs/meta-audits/YYYY-MM-DD_HHmm.md
- 报告时间戳: YYYY-MM-DD HH:mm
- 间隔: Nh

## 新鲜度检查
- 报告生成时间: YYYY-MM-DD HH:mm
- 检查时各规则文件最后修改时间（全部 ≤ 报告时间）: ✓

## 安全回滚点
- 方案: git stash
- ID: pre-cleanup-YYYY-MM-DD_HHmm
- Scope: memory/, ~/.claude/rules/, CLAUDE.md, DOCMAP.md, MEMORY.md, docs/logs/meta-audits/example-archive.md
- 回滚命令: `git stash apply stash@{N}`

## 处理汇总
| # | 类别 | 目标文件 | 审批 | 应用状态 |
|---|---|---|---|---|
| 1 | R1 | feedback_a.md | Y | ✓ |
| 2 | R2 | feedback_b.md → feedback_c.md | Y | ✓ |
| 3 | R4 | feedback_d.md | N | — |
| 4 | R5 | feedback_e.md | Y | ✓ (旧 example 归档 archive.md#entry-3) |
| 5 | R2 | feedback_f.md | DEFER | — |

## 拒绝/推迟列表
- Finding #3 (R4 feedback_d.md): 用户判断触发条件不能抽象 → 追加到 `docs/logs/cleanup-runs/rejected-findings.md`
- Finding #5 (R2 feedback_f.md): DEFER，仅本报告记录

## Partial Success（如有）
- 无 / 列出中断位置

## 回滚历史
- 无 / [时间] 回滚到 stash，原因: ...
```

---

## 硬约束

1. **不得删除任何有具体 Why 案例的 feedback 条目**。R1 判定时，如果副本的 Why 段比原件更具体，Why 内容必须先 append 到原件再删副本
2. **不得合并触发条件不同的规则**，即使结论相同。触发条件不同 → 自动降级为 R3，加 see-also 不合并
3. **合并前必须 Grep 全仓库找所有引用**。任何失效指针都是阻断信号，该条 finding 自动转为 SKIP
4. **每次 cleanup 前必须创建 `git stash` 回滚点**。创建失败 → 终止
5. **R3 不产生变更预览，不需要审批**。只在两条规则底部加 `**See also**: ...` 一行
6. **R5 的旧 example 必须完整保留**到 example-archive.md，不得摘要或简化。追溯性高于文件大小
7. **R5 找不到新 example 且用户未提供时不得编造**。Why 段标注 "案例待更新（来源: meta-audit YYYY-MM-DD #findN）" 即可
8. **不得越过 meta-audit 自行发现 finding**。本命令是 meta-audit 的下游
9. **不得处理 meta-audit 中未标类别的 finding**。打标 SKIP
10. **新鲜度检查失败即终止**。不接受"就这一次"的豁免

---

## 失败回滚

如果应用阶段中断或用户中途放弃、或事后发现规则变差：

```bash
# 查看 stash 列表
git stash list

# 回滚到 cleanup 前状态
git stash apply stash@{N}
```

回滚后必须在 `docs/logs/cleanup-runs/YYYY-MM-DD_HHmm.md` 的"回滚历史"段追加记录（日期 UTC+8 + 原因）。

**注意**：追加回滚记录不是本命令某次执行的一部分，而是事后手动操作。cleanup-runs 报告归档后若未来发生回滚，手动打开对应报告追加即可，不需要重跑命令。

---

## Arguments

- `/rules-cleanup` — 处理最新一份 meta-audit 报告的全部 D3/D4 + R5 findings
- `/rules-cleanup dry-run` — 只生成全部预览表，不创建 stash 回滚点、不要求审批、不做任何 Edit。用于首次使用或不确定 findings 质量时先看一眼
- `/rules-cleanup filter:R1,R2` — 只处理指定类别（R3 不受 filter 影响，永远只加 see-also）
- `/rules-cleanup report:<path>` — 指定 meta-audit 报告路径（默认用最新一份，仍需通过新鲜度检查）

---

## 不适用场景

- **日常单条 memory 修改** → 手动 Edit
- **meta-audit 未发现的规则问题** → 重新跑 `/meta-audit`，不得本命令自行扫描
- **删除过时的 `project_*.md` memory 字段**（如 "R6.45 待 GPCRdb" 这种状态过时） → 手动 Edit。本命令只处理 `feedback_*.md`
- **规则新增** → 手动创建 memory 文件，不是 cleanup 的工作
- **跨项目的规则清理** → 本命令 scope 限定在单项目 memory

---

## 中止路径（遇到以下情况直接终止并在 cleanup-runs 报告头部记录原因）

- 新鲜度检查失败（规则文件在 meta-audit 报告生成后被修改）
- 回滚点创建失败（git stash 创建失败）
- meta-audit 报告中存在无法归入 R1-R5 的 finding 数量 > 50%（说明 meta-audit 质量问题）
- 同一条 R 类别在 2 次重试预览后主 Claude 都无法自动处理（例如 R2 合并方向判据无法确定两条 Why 字符数 + originSessionId 全相等）
- 用户在预览审批阶段连续 3 次选 DEFER（说明本次 cleanup 时机不合适）

中止时在 `docs/logs/cleanup-runs/YYYY-MM-DD_HHmm.md` 头部写 `## STATUS: ABORTED` + 原因 + 完成到哪个阶段。已创建的回滚点保留，用户可按失败回滚段手动处理。

---

## 与 `/meta-audit` 的契约总结

| 关系 | 说明 |
|---|---|
| 上下游 | meta-audit 诊断 → cleanup 治疗 |
| 输入 | cleanup 必须消费 meta-audit 的 findings 文件 |
| 新鲜度 | 报告中列出的规则文件自报告生成后未被修改 |
| scope | cleanup 只处理 D3/D4 + R5，其它维度需人工 |
| 禁止 | cleanup 不得自行发现 finding；meta-audit 不得自行治疗 |
