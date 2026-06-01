# Draft: `/meta-audit` 命令

> **状态**：草案。用户审核通过后移至 `~/.claude/commands/meta-audit.md`。

---

## 命令说明

对项目防过时信息与规范漏洞机制做一次元审计。**只诊断不治疗**。

目标：找出 memory / rules / audit 机制**本身**的失效模式，不审查业务代码/数据。
输出：一份结构化 findings 清单，供后续 `/rules-cleanup` 或人工修复参考。

---

## 何时运行

触发条件（任一满足即可运行，**禁止**定期自动运行）：

- **(a)** 连续两次 truth-audit 出现同一维度的违反（例如两次都是"推断冒充事实"或"选择性引用"）
- **(b)** memory 文件、CLAUDE.md、DOCMAP.md 发生大规模改动后（> 20% 行数变动，或一次性新增 ≥ 3 条 feedback）

没有真实信号触发的 meta-audit 会产生噪声 findings，浪费 token 且稀释下次的信号敏感度。是否跑由用户决定。

---

## 范围

必须覆盖以下 6 类对象，缺一视为本次审查不完整：

1. `CLAUDE.md`（项目根 + 全局 `~/.claude/CLAUDE.md`）和 `docs/DOCMAP.md`
2. `~/.claude/projects/{project-hash}/memory/` 下所有 memory 文件 + `MEMORY.md`
3. `docs/INDEX.md`
4. `docs/logs/truth-audits/*.md` 和 `docs/logs/censor-audits/*.md` 全部历史
5. `~/.claude/commands/` 下 `truth.md`、`censor.md`、`meta-audit.md`（本命令自己）、`rules-cleanup.md` 的定义文件。若命令定义在项目内，用项目路径
6. `~/.claude/rules/*.md` 全部（被 `@rules/...` 自动加载进 CLAUDE.md 的规则片段，属于 D6 预算）

**不得扩展到** `src/`、`experiments/`、`docs/modeling/`、`docs/papers/` 等业务内容。违反范围即视为审查失败。

---

## 维度（D1-D7，必须全部覆盖）

| # | 维度 | 想检测什么 |
|---|---|---|
| **D1** | 规则覆盖盲区 | truth-audits 中反复出现但未进 memory 的违反模式 |
| **D2** | 规则老化 | memory 指向的结论已在 docs/ 或更新的日志中被推翻，但 memory 未同步 |
| **D3** | 规则不可执行 | feedback 只有抽象告诫，无 (触发条件, 检查步骤, 判据) 三元组 |
| **D4** | 规则间冲突/重叠 | 同一行为规则在多个 memory/rules 文件中措辞不一致或重复 |
| **D5** | 元命令自污染 | /truth、/censor、/meta-audit 自身在执行时会犯它们所审查的同类错误 |
| **D6** | 自动加载预算超限 | CLAUDE.md + MEMORY.md + DOCMAP.md 跨文件总量 + 重复条款 + 最近 trigger-quarterly 的 ✗ 条目 |
| **D7** | 历史 audit 未归因升级 | truth-audit 的"待修复"条目未升级为可 lint 的规则 |

D6 的**行为证据**来源：最近一份 `docs/logs/meta-audits/trigger-quarterly-*.md`（见 `docs/ops/quarterly-trigger-audit.md` SOP）。没有 trigger audit 记录时 D6 只能做 token 统计和重复计数，证据强度 LOW，必须在输出中明示。

---

## 方法

### 阶段 1 — 基线建立（主 Claude，串行）

逐个 Read 以下文件，建立基线快照。**必须真读最新版本，不依赖上下文缓存**：

- `CLAUDE.md`（项目）+ `~/.claude/CLAUDE.md`（全局）
- `~/.claude/rules/*.md` 全部
- `docs/DOCMAP.md`
- `docs/INDEX.md`
- `~/.claude/projects/{hash}/memory/MEMORY.md`

每个基线文件必须记录 sha256 前 8 位到输出报告"范围"段，作为"真读"的可验证证据。基线建立后不再回读这些文件。后续任何引用必须来自 subagent 的结构化返回。

### 阶段 2 — 4 路并行 subagent（深度审查，不考虑 token）

**所有 subagent 必须返回结构化列表（JSON-like 或 markdown 表格），不得返回叙事段落**。

**Retry / 降级协议**（主 Claude 检测到以下任一情形时触发）：
- subagent 返回叙事段落而非结构化列表
- subagent 返回项缺必填字段（A: 缺维度/首末日期；B: 缺触发条件/检查步骤判定；C: 缺 token 估算或重复指数；D: 缺自污染点清单）
- subagent 返回项彼此矛盾或字段类型不符

处理流程：
1. 通过 SendMessage 给同一 subagent 发送 "请严格按如下 schema 返回 [粘贴 schema]，之前返回的 [具体问题]"，最多重试 **2 次**
2. 2 次后仍不合格 → 停止重试，在 findings 文件里对应维度标 `[Subagent X 返回不合格 × N 次，本维度证据强度降级 LOW]`，继续合并其它 subagent 结果
3. 不因单个 subagent 失败终止整轮 meta-audit

#### Subagent A — 历史 audit 聚类（Explore, thorough）

范围：`docs/logs/truth-audits/*.md` + `docs/logs/censor-audits/*.md` 全部

任务：

- 列出所有违反条目，按 D1-D7 维度标签聚类
- 对每个聚类返回：
  - 维度
  - 出现次数
  - 首次日期 / 最近日期
  - 涉及的规则 memory 文件（若有）
  - 是否被后续 audit 关闭（关键：检索该问题关键词在**整个 logs/** 里的最后一次出现）

#### Subagent B — Memory 逐条体检（Explore, thorough）

范围：`~/.claude/projects/{hash}/memory/` 下所有 `feedback_*.md` + `project_*.md`

任务：对每条文件返回：

- 触发条件是否明确（有/无）
- 检查步骤是否可执行（有/无/部分）
- Why 段 example 的健康度（三档判据，不得合并）：
  - **健康** = Grep 命中 example 中的路径/符号/残基名 **且** 命中处的语义仍与规则本体指向一致
  - **人工判定** = Grep 命中，但命中处语义已变（文件存在但含义变了、残基名存在但结论已被推翻、日期存在但引用上下文已被重写）→ 不自动降级为 R5，交最终 finding 让用户判断
  - **R5 候选** = Grep 未命中（路径/符号/残基名已不存在）
  - 特例：example 内容本身描述的是"过去的错误"（如 feedback_claim_granularity 里的 ASN56 误判），只要错误事实未被推翻，即使残基名仍存在也视为"健康"
- 最后修订日期（从 frontmatter 或 git log）
- 与其它 memory 条目的重叠关系：列 see-also 候选，并标注触发条件是否完全相同

#### Subagent C — 加载预算与跨文件重复（Explore, medium）

范围：`CLAUDE.md`（项目+全局）、`~/.claude/rules/*.md`、`docs/DOCMAP.md`、`memory/MEMORY.md` + 其展开的全部 memory 文件

任务：

- 估算自动加载总 token（按会话启动时会被读到的范围）
- 找出跨文件重复条款：同一行为规则在 ≥ 2 个文件中出现（不限措辞一致）
- 计算重复指数 = 重复条款数 / 总条款数
- 检索最近一份 `docs/logs/meta-audits/trigger-quarterly-*.md` 的 ✗ 条目，关联到具体规则名

#### Subagent D — 元命令自污染（Explore, medium）

范围：`~/.claude/commands/truth.md`、`censor.md`、`meta-audit.md`（本命令）、`rules-cleanup.md`（若存在）

任务：

- 对每个命令 prompt 做静态分析：它的方法/维度/自我约束是否自洽
- 识别命令 prompt 是否会让 Claude 犯它所审查的错误，例如：
  - `/truth` 是否要求审查者自己 grep 后续日志（防选择性引用）
  - `/meta-audit` 是否要求自己真读最新版规则（防规则缓存污染）
- 返回每个命令的潜在自污染点清单

### 阶段 3 — 合并（主 Claude）

只做合并，不再打开任何原文。subagent 返回的结构化列表直接汇总成 findings by 维度。

### 阶段 4 — 修复建议（主 Claude）

对每条 finding 输出：

- **证据**：audit 引用 / memory 条目 / grep 输出（必须有路径 + 行号）
- **root cause**：为什么现有规则没 catch 到
- **修复方案**：(触发条件, 检查步骤, 通过判据) **三元组**。只有"建议注意 X"的条目不被接受
- **归档位置建议**：新建 memory 文件 / 追加到哪个现有条目 / 删除哪条
- **是否属于 /rules-cleanup 可处理范围**：标注 R1/R2/R3/R4/R5 或 "需人工处理"

### 阶段 5 — 输出（主 Claude）

写入 `docs/logs/meta-audits/YYYY-MM-DD_HHmm.md`（文件名时间戳为 UTC+8 本地时区）。

**写入前自检**（阶段 4 输出落盘前强制运行一次）：
- 每条 finding 是否链接 ≥ 1 条历史 audit / grep 输出（路径 + 行号）
- 每条修复方案是否是 (触发条件, 检查步骤, 通过判据) 三元组
- 是否存在纯推断 finding（无证据段）
- 任一项不合规 → 退回阶段 4 重写，直到全部合规才允许写入

**启动建议字段判据**（写入 "## /rules-cleanup 启动建议" 段时强制使用）：
- `是` = D3 + D4 + D2(R5) findings ≥ 1 条，且全部 finding 已标 R 类别
- `部分` = 有部分 finding 标了类别，另一部分为"需人工处理"
- `否` = 无 findings 或全部为"需人工处理"

**本轮不修改任何文件**（除了最终的 findings 文件本身）。

---

## 自我约束（防止 meta-audit 自污染，固化在 prompt 里）

1. **范围冻结**：阶段 1 后不得新增维度。阶段 2 后发现的新维度写入"下次审查待办"，本轮不处理
2. **阶段 1 必须真读最新版**：不得使用会话中已加载的任何规则文件内容作为事实来源。每一个被引用的规则都必须在本命令启动后重新 Read 过一次。**即使 CLAUDE.md 已经在会话启动时被自动加载过**
3. **证据强制链接**：每条 finding 必须链接 ≥ 1 条历史 audit 或 grep 输出。纯推断的 finding 不允许写入
4. **三元组强制**：每条修复建议必须给出 (触发条件, 检查步骤, 通过判据)。只有"建议注意 X"的条目退回重写
5. **只诊断不治疗**：本轮不允许对除"最终 findings 文件"以外的任何文件执行 Edit/Write。任何 Edit 调用都是违约信号
6. **subagent 结构化返回强制**：任一 subagent 返回叙事段落必须拒绝合并并要求重新返回结构化列表
7. **本命令自己必须进 D5 审查对象**：本命令 prompt 本身也要被 subagent D 分析是否自污染，不得豁免

---

## 输出格式

```markdown
# Meta Audit — YYYY-MM-DD HH:mm

## 范围
- 报告生成时间: YYYY-MM-DDTHH:MM:SS+08:00（UTC+8 本地时区）
- 扫描文件清单（下游 rules-cleanup 按本格式 parse 做新鲜度检查）:
  - `path/to/file1.md` — mtime `YYYY-MM-DDTHH:MM:SS+08:00` — sha256[:8] `xxxxxxxx`
  - `path/to/file2.md` — mtime `YYYY-MM-DDTHH:MM:SS+08:00` — sha256[:8] `xxxxxxxx`
  - ...
- 触发原因: (a) / (b) / 手动强制
- 4 个 subagent 启动时间与完成时间（UTC+8）

## Findings by 维度

### D1 规则覆盖盲区
- **Finding #1**: [简述]
  - 证据: [引用 + 行号]
  - root cause: ...
  - 修复方案:
    - 触发条件: ...
    - 检查步骤: ...
    - 通过判据: ...
  - 归档位置: ...
  - /rules-cleanup 类别: R1/R2/R3/R4/R5/人工

### D2 规则老化
[同格式]

### D3 规则不可执行
[同格式]

### D4 规则间冲突/重叠
[同格式]

### D5 元命令自污染
[同格式]

### D6 自动加载预算超限
- Token 统计: ...
- 重复指数: ...
- trigger-quarterly 证据引用: ...
- [同格式 findings]

### D7 历史 audit 未归因升级
[同格式]

## 本轮确认健康的维度
- [明示无问题的维度，避免漏审错觉]

## 下次审查待办（本轮发现但 scope 外的新维度）
- ...

## /rules-cleanup 启动建议
- 建议启动: 是 / 否 / 部分
- 若部分: 处理类别 R1 / R2 / R4 / R5 中的 [具体]（R3 默认无审批直接应用 see-also，不列入此清单）
- 理由: ...
```

---

## 下游消费字段契约

本命令输出会被 `/rules-cleanup` 消费。下游依赖的字段：

| 字段 | 位置 | 用途 | 格式定义见 |
|---|---|---|---|
| 扫描文件清单 | `## 范围` 段 | 新鲜度检查 parse | 本命令"输出格式"段 |
| 启动建议 | `## /rules-cleanup 启动建议` 段 | 决定是否启动下游 | 本命令阶段 5 判据 |
| R 类别标签 | 每条 finding 末尾 | 下游分类与降级 | 本命令阶段 4 + rules-cleanup 阻断信号段 |
| rejected-findings 列表读取 | 阶段 4 预处理 | 跳过历史已拒绝条目 | `docs/logs/cleanup-runs/rejected-findings.md`（rules-cleanup 维护） |

修改任一字段的格式前必须同步两份命令文件。

---

## Arguments

- `/meta-audit` — 全量审查（D1-D7 全覆盖）
- `/meta-audit focus:D5` — 聚焦单一维度
- `/meta-audit scope:memory` — 聚焦单一对象类别（memory / claudemd / audits / commands）

聚焦模式仍然必须满足所有自我约束（真读、三元组、只诊断）。聚焦模式下未审查的维度在输出中明示为"本次未扫描"。

---

## 不适用场景

- 审查业务代码/数据 → 用 `/truth` 或 `/censor`
- 一次性修复单个 memory 条目 → 手动 Edit
- 规则变动后立即验证是否生效 → 用季度 trigger audit（`docs/ops/quarterly-trigger-audit.md`），不用 meta-audit
- 清理/合并冗余规则 → 用 `/rules-cleanup`（消费本命令的输出）

---

## 中止路径（遇到以下情况直接终止并在 findings 文件头部记录原因）

- 两个 subagent 返回的证据彼此矛盾且主 Claude 无法通过 grep 仲裁
- 基线文件数量 < 范围清单要求的最小集（如 `docs/INDEX.md` 不存在）
- 阶段 5 自检反复不合规超过 2 轮（说明 subagent 返回的 raw data 就有问题）
- 主 Claude 发现自己已经在本轮 meta-audit 过程中对基线文件以外的任何文件做过 Edit（违反"只诊断不治疗"硬约束）

中止时在 `docs/logs/meta-audits/YYYY-MM-DD_HHmm.md` 头部写 `## STATUS: ABORTED` + 原因 + 完成到哪个阶段，不删除已有 partial 结果。下次重跑前用户可参考中止原因调整触发条件。
