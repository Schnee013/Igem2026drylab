# DOCMAP: drylab 文档治理与路由

> 本文件是 drylab 项目的文档治理规则和目录路由。它不承载项目现状、完成度、候选排名、job id、运行阶段或具体结果。
>
> 当前项目状态只看 [docs/INDEX.md](INDEX.md)。详细经过只看 [docs/logs/](logs/)。领域事实、方法和证据边界回到对应领域文档、结果文件和代码。

---

## 1. 入口链

非平凡 drylab 任务先按以下顺序建立入口：

1. [AGENTS.md](../AGENTS.md)
2. [docs/DOCMAP.md](DOCMAP.md)

然后按任务画像读取最小必要上下文。事实源来自仓库权威文件、代码、结果或日志；Codex native/global memory 只保存用户偏好和仓库入口指针。`codex/docs/memory/` 是冻结的历史快照，不是活跃入口或当前状态源。

| 任务画像 | 默认读取 | 继续读取条件 |
|---|---|---|
| 进度汇报 / PPT / 对外说明 | [docs/INDEX.md](INDEX.md)，再按主题读取 `docs/modeling/`、`docs/decisions/`、`docs/logs/` 或结果文件 | 需要交接时读取对应 repo-owned plan 和相关日志 |
| 审查 / truth / censor / 路由治理 | 本文件、被审查文件、必要的权威指针 | 需要当前状态时读 INDEX；需要历史经过时读对应日志 |
| Git commit / push / PR 查看、审查、复审或合并 | [ops/git-role-and-pr-governance.md](ops/git-role-and-pr-governance.md)，再读取 staged/outgoing diff 或 PR 完整净 diff、checks、review 状态和受影响文件 | 只有涉及当前项目状态时读 INDEX；每个写操作按 ops 文档重新确认本次操作角色与精确目标 |
| payload / manifest / Git tracking / commit 分类 | 本文件、`.gitignore`、[ops/payload-tracking-policy.md](ops/payload-tracking-policy.md)、被分类的 changed files | 只有需要当前项目状态时读 INDEX；只有需要具体经过时读对应日志；普通 MD/文献/状态任务沿各自任务画像加载上下文 |
| 机械编辑 / 指定文件修复 | 本文件和指定文件 | 只有编辑影响路由、状态或权威边界时读 INDEX |
| MD / 远程计算 / 运行状态 | INDEX 当前优先入口；任何 MD / GROMACS 任务必须读取 [ops/md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)，再按需读 `environments/`、`codex/docs/plans/`、对应结果和日志 | 新服务器或远程计算任务同时读取 [ops/nkuliulab-e2-cloud-server.md](ops/nkuliulab-e2-cloud-server.md)；服务器、job、checkpoint 或运行完成状态由当前结果、日志或 ops 文档确认 |
| 文献 / 论文证据 | [papers/literature-matrix.md](papers/literature-matrix.md)，再读指定 summary 或数据源 | 先用矩阵缩小范围，再读取指定 summary、数据源或必要 PDF |
| handoff / 踩坑复盘 | [docs/INDEX.md](INDEX.md)、[codex/docs/plans/README.md](../codex/docs/plans/README.md) 和相关日志 | INDEX 给当前状态，plans 给执行顺序，日志给发生经过 |

## 2. 单一权威源

治理单位是会影响行动的具体主张。每条事实、规则、范围边界、验证命令、项目状态或结果解释只能有一个规范写入权威和一条冲突裁决规则。其他位置只能是路由指针、可追溯派生视图或有明确时间边界的历史快照，不得成为可独立修改的第二权威。

| 信息类型 | 权威位置 | 非权威位置的做法 |
|---|---|---|
| 项目级当前状态投影、优先级、阻塞项、活跃入口 | [docs/INDEX.md](INDEX.md) | 详细领域状态回领域权威源 |
| gate / run 的原始状态与终态 | validator 输出或 run-local machine-readable artifact | `PACKAGE_STATUS.md` 和 INDEX 只作带来源、时间和用途边界的派生视图 |
| package 详细状态 | 对应 system-local `PACKAGE_STATUS.md` 派生视图 | 必须指向原始 gate / run artifact，不独立改写原始结论 |
| 具体经过、当天判断、踩坑 | 维护者规范日志 [docs/logs/YYYY-MM-DD.md](logs/)；贡献者 PR 过程日志 `docs/logs/YYYY-MM-DD-<contributor>.md` | 规范日志只给日期指针；贡献者日志不得承载跨 PR 当前状态 |
| 领域方法、边界、解释 | `docs/modeling/`, `docs/prd/`, `docs/ops/`, `docs/papers/` | 只链接对应小节 |
| 原始数据、数值结果、图表 | `experiments/` 结果文件、代码输出 | 不复制数值表 |
| 可复用执行计划、handoff | `codex/docs/plans/` | 不复制计划正文或项目当前状态 |
| 代码行为 | `src/`, `scripts/`, tests | 文档描述必须指向代码或测试 |

如果同一信息已经在权威位置存在，新文档只能链接它。需要改变事实时，先改权威位置，再更新路由指针。

可追溯派生视图必须给出：

- `source`：规范写入权威或直接证据；
- `as_of`：本视图核验到的时间；
- `allowed_use`：本视图可以支持的决策；
- `update_trigger`：什么上游变化会使本视图需要更新。

派生视图只支持 `allowed_use` 范围内的决策。上游已变化、`as_of` 早于最新证据、来源身份不清或同步证据失效时，派生视图降级为 `stale` 或 `unresolved`，不得继续冒充当前事实。历史快照以日期和当时来源为边界，不参与当前冲突裁决。

### 运行状态与新鲜度

- 每个 run 使用一个 append-only `run_state_events.tsv` 作为 heartbeat 与 terminal-state 的机器可读写入权威；每行至少包含 `observed_at`、`state`、`source`、`detail`。兼容性 `terminal_status.tsv` 只能是由该事件流生成的当前快照。
- 状态使用 `RUNNING_VERIFIED`、`TERMINAL_NORMAL`、`TERMINAL_ABNORMAL`、`WAITING_AUTHORIZATION`、`UNRESOLVED`。`RUNNING_VERIFIED` 必须来自当前进程和运行产物核验，不能由“曾启动”推断。
- `RUNNING_VERIFIED` 的当前视图有效期为 6 小时；超过 6 小时没有新事件时，派生视图自动降级为 `UNRESOLVED`。
- 启动、停止、续跑、覆盖、finalize 或 postprocess 等会改变行动的操作，必须使用 15 分钟内的 live verification 和相应 gate。较早 heartbeat 只能说明历史观察。
- `TERMINAL_NORMAL` / `TERMINAL_ABNORMAL` 在事件及其引用输出的 checksum 身份未变化时保持有效；身份变化或终态证据不完整时降级为 `UNRESOLVED`。

## 3. 目录路由

```
drylab/
├── AGENTS.md              # Agent 启动 shim；只放加载规则和指针
├── CLAUDE.md              # Claude Code 兼容 shim；只指向活跃入口
├── docs/
│   ├── DOCMAP.md          # 本文件；治理规则和目录路由
│   ├── INDEX.md           # 当前项目路由表；现状、阻塞项、活跃入口
│   ├── prd/               # 项目策略、底盘/输出架构等决策背景
│   ├── modeling/          # 各干实验建模方向的方法、边界和证据入口
│   ├── decisions/         # 技术决策记录
│   ├── ops/               # 当前操作规范；archives/ 只作历史追溯
│   ├── logs/              # 每日工作日志和审查记录
│   ├── papers/            # 文献矩阵、单篇总结、领域证据包
│   ├── presentation/      # 汇报/PPT 资料、旧 deck 和参考材料；不承载科学事实权威
│   ├── learning/          # 学习路线和工具准备
│   └── archive/           # 旧 PRD、通用指南等不再活跃的历史材料
├── codex/
│   ├── docs/plans/        # repo-owned execution plans 与 handoff
│   └── docs/memory/       # 冻结历史快照；保留追溯，不参与当前路由
├── src/                   # 源代码
├── tests/                 # 自动化测试
├── experiments/           # 结果、输入、分析产物和运行证据
├── environments/          # 环境定义、生产站点矩阵和版本证据
└── scripts/               # 环境和辅助脚本
```

目录注释只说明“这里放什么”和“权威边界”。不要在 DOCMAP 的目录树中写方向状态、运行进度、候选编号、服务器 job id 或结果摘要。

## 4. 关键文件职责

### docs/INDEX.md

项目当前路由表。它可以列方向状态、阻塞项、活跃入口、最近少量进展和待办，但不放详细结果数值、长时间线或领域方法正文。

老化规则：

- 最近进展只保留少量高价值条目；完整历史回日志。
- 已完成的待办在下一次维护时移除或转到日志。
- 非平凡任务在完成声明前必须对照 INDEX 审视已验证结果；若改变项目级状态、优先级、阻塞项或活跃入口，须在同一任务中更新 INDEX。最终交接须说明 INDEX 已更新，或说明为何没有项目级字段变化。

### codex/docs/plans/

repo-owned plans 承载可复用执行顺序、已记录决策的工作计划和跨 session handoff。

- plans 是执行指导，不是项目状态或科学事实权威。
- 启动或续接计划前，必须用 INDEX、领域文档、日志、代码和结果文件校准其前提。
- 当前状态回 INDEX；发生经过回日志；数值和结果回原始输出。

Codex native/global memory 只能保存用户偏好、入口规则或指向本仓库的路由，不复制 drylab 科学结论。

### codex/docs/memory/（冻结）

该目录仅保留停用前的 repo-scoped memory 快照，用于历史追溯和旧引用兼容；它不是启动入口、当前状态源或可继续维护的治理层。任何直接进入该目录的旧链接都必须先回到 DOCMAP 重新路由，并用 INDEX、领域文档、日志、代码和结果文件校准。

### docs/logs/

日志记录“做了什么、为什么、依据是什么、踩了什么坑、下一步不要重复什么”。日志是过程权威，不承担跨天当前状态；跨天状态回 INDEX。

无后缀 `YYYY-MM-DD.md` 是维护者维护的当日规范日志。`YYYY-MM-DD-<contributor>.md` 是贡献者随 PR 提交的详细过程日志，只在该 PR 和作者范围内成立；合并时由维护者在规范日志中给最小指针，不复制其正文。

人工维护的日志正文默认使用中文书写，措辞必须专业、严谨、可审计。命令、路径、代码符号、错误信息、工具输出、英文论文标题等字面证据保留原文，并用中文说明其上下文和含义。历史日志如需语言归一化，只做表达层翻译，不改变事实、时间、数值、路径或证据指针。

### docs/modeling/ 与 docs/prd/

领域文档承载方法、范围、证据边界、依赖关系和当前权威指针。容易老化的进展表、候选列表和运行状态应压缩为日志/结果指针。

策略或 PRD 类文档若含历史分析，必须在顶部标明历史边界，并把当前现状指回 INDEX。

### docs/ops/

当前操作规范留在 `docs/ops/` 根目录；旧服务器、旧工具链、旧事故复盘放入 `docs/ops/archives/`。归档材料只用于追溯旧结果、理解旧日志或访问历史文件；新任务默认入口使用当前 `docs/ops/` 规范。

任何 MD/GROMACS 任务必须先读 [ops/md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)。新服务器/远程计算任务还要读 [ops/nkuliulab-e2-cloud-server.md](ops/nkuliulab-e2-cloud-server.md)。

Payload / manifest / Git tracking 规则见 [ops/payload-tracking-policy.md](ops/payload-tracking-policy.md)。该文件是条件加载的 commit/tracking 分类规则，用于 payload、manifest、checksum、ignore 或 staging 风险审查；普通 MD 状态或科学解释入口仍按本 DOCMAP 的任务画像选择。

Git commit、push、PR review/integration 或 merge 的角色确认、文件边界和授权门见 [ops/git-role-and-pr-governance.md](ops/git-role-and-pr-governance.md)。该文件只在 Git/PR 任务中条件加载；普通写作、建模或状态读取不加载其中的操作角色规则。

### docs/papers/

文献采用稳定 ID。需要文献时，先查 [papers/literature-matrix.md](papers/literature-matrix.md)，再按需读取单篇 summary、数据源或必要 PDF。

### docs/presentation/

汇报资料、旧 deck 和参考材料放在 `docs/presentation/`。该目录服务于表达、排版和材料组织，不是 ODE、P2、reporter、MD 或 docking 的事实权威；涉及事实、状态、数值或边界时必须回到 `docs/INDEX.md`、`docs/modeling/`、`docs/decisions/`、`docs/logs/`、代码和结果文件。

## 5. 代码、结果与文档联动

- 代码路径、配置路径和实验产出路径必须由领域文档指明。
- 代码或结果改变后，先写日志；若改变项目级当前状态、优先级、阻塞项或活跃入口，在完成声明前同步更新 INDEX；最终交接须报告该检查结果。
- 结果文件是数值权威；文档只解释使用边界和指针。
- 使用历史 JSON/CSV 作为基线前，核对输入身份、生产代码与配置版本，并确认产物是否早于已知修复。
- `done`、`fixed`、`verified`、`passed`、外部提交或部署等状态声明必须有直接文件、日志或工具证据；开放问题需先检索近期权威材料。
- 引用项目路径、代码符号、命令、章节、指标或列名之前必须核验；全称或最高级判断需要枚举完整相关集合，数学与统计推导需要重新计算。
- 修改函数签名或影响行为的参数时必须检索并逐一审视所有 caller；runner 日志使用带时间戳的 run ID；脚本注释和 docstring 只描述依赖与调用，完整流程进入 plans、docs 或 logs。
- 脚本不得硬编码 `experiments/` 下的可配置路径；优先从配置文件或项目根解析。

## 6. 远程与部署边界

- 本地 repo 的 `src/`、`scripts/`、`docs/` 是源头；服务器工作目录是部署或运行目标。
- 服务器端不得反向成为脚本或文档权威源。
- 需要修改脚本、配置或流程时，先改 repo，再同步到服务器。
- 任何例外路线必须有 repo 内计划、环境矩阵或 gate script 指针支撑。

## 7. 文档生命周期

### 创建

1. 新建方向文档放入 `docs/modeling/`，并补充 frontmatter、范围、方法、依赖和证据边界。
2. 新增方向或入口时同步更新 [docs/INDEX.md](INDEX.md)。
3. 重大技术选择同时创建 `docs/decisions/NNN-title.md`。

### 迭代

- 改事实先改权威文件，再改路由。
- 方法路线变化时保留历史边界和原因，但不要保留会被误读成当前行动的旧待办。
- 不把日志中的具体经过复制到 PRD、DOCMAP 或 INDEX。

### 归档

- 停用材料进入对应 archive 目录，或按用户明确要求删除。
- 活跃路由不得继续指向已删除或停用目录。
- 历史日志中的旧路径记录可保留，除非用户明确要求重写历史引用。

## 8. 命名与引用规则

| 类型 | 命名模式 | 示例 |
|---|---|---|
| 建模方向文档 | `P{0-3}-{english-name}.md` | `P0-molecular-docking.md` |
| 技术决策记录 | `{NNN}-{short-title}.md` | `003-chassis-yeast-ste2-integration.md` |
| 维护者规范工作日志 | `YYYY-MM-DD.md` | `2026-06-02.md` |
| 贡献者 PR 过程日志 | `YYYY-MM-DD-<contributor>.md` | `2026-07-30-yrx.md` |
| 文献总结 | `{Author}{Year}-{Topic}-summary.md` | `Hu2024-GprC-summary.md` |
| 运行日志 | `run_{script}_{YYYYMMDD}_{HHMMSS}.log` | `run_multiseed_20260406_072954.log` |

文档间引用使用相对路径：

```markdown
详见 [底盘决策记录](decisions/003-chassis-yeast-ste2-integration.md)。
```

方向文档底部保留依赖关系：

- 输出到：本方向产出被谁消费。
- 依赖于：本方向需要哪些上游材料。

## 9. 常见反模式

- **DOCMAP 变成项目状态页**：把方向状态、运行阶段、候选编号或 job id 写进目录树。
- **INDEX 变成百科全书**：把详细结果、长时间线、原始数值表写进路由表。
- **Memory 膨胀**：把领域文档、计划或日志内容搬进 memory。
- **PRD 冒充现状**：策略文档保留旧进展表，却没有历史边界和当前指针。
- **重复结果数值**：同一指标同时出现在结果 CSV、日志、handoff、PRD 和 memory。
- **猜测文件名**：查运行日志时不用通配符和排序。
- **批量加载文献**：未先查矩阵就打开大量 summaries 或 PDF。

## 10. Frontmatter 模板

建模方向文档使用：

```yaml
---
direction: P0-example
status: <lifecycle-state>
priority: P0
chassis_dependent: false
last_updated: YYYY-MM-DD
---
```

状态枚举与具体含义由 [docs/INDEX.md](INDEX.md) 和方向文档共同约束，不在 DOCMAP 维护项目状态。
