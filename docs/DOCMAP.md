# DOCMAP: drylab 文档治理与路由

> 本文件是 drylab 项目的文档治理规则和目录路由。它不承载项目现状、完成度、候选排名、job id、运行阶段或具体结果。
>
> 当前项目状态只看 [docs/INDEX.md](INDEX.md)。详细经过只看 [docs/logs/](logs/)。领域事实、方法和证据边界回到对应领域文档、结果文件和代码。

---

## 1. 入口链

非平凡 drylab 任务先按以下顺序建立入口：

1. [AGENTS.md](../AGENTS.md)
2. [docs/DOCMAP.md](DOCMAP.md)

然后按任务画像读取最小必要上下文。事实源来自仓库权威文件、代码、结果或日志；Codex native/global memory 与 `codex/docs/memory/` 只提供路由和警示线索。

| 任务画像 | 默认读取 | 继续读取条件 |
|---|---|---|
| 进度汇报 / PPT / 对外说明 | [docs/INDEX.md](INDEX.md)，再按主题读取 `docs/modeling/`、`docs/decisions/`、`docs/logs/` 或结果文件 | 只有需要跨会话警示或 handoff 时才读 `codex/docs/memory/README.md` 和相关 memory |
| 审查 / truth / censor / 路由治理 | 本文件、被审查文件、必要的权威指针 | 需要当前状态时读 INDEX；需要历史经过时读对应日志 |
| payload / manifest / Git tracking / commit 分类 | 本文件、`.gitignore`、[ops/payload-tracking-policy.md](ops/payload-tracking-policy.md)、被分类的 changed files | 只有需要当前项目状态时读 INDEX；只有需要具体经过时读对应日志；普通 MD/文献/状态任务沿各自任务画像加载上下文 |
| 机械编辑 / 指定文件修复 | 本文件和指定文件 | 只有编辑影响路由、状态或权威边界时读 INDEX 或 memory README |
| MD / 远程计算 / 运行状态 | INDEX 当前优先入口，再读 `docs/ops/`、`environments/`、`codex/docs/plans/`、对应结果和日志 | 服务器、job、checkpoint 或运行完成状态由当前结果、日志或 ops 文档确认 |
| 文献 / 论文证据 | [papers/literature-matrix.md](papers/literature-matrix.md)，再读指定 summary 或数据源 | 先用矩阵缩小范围，再读取指定 summary、数据源或必要 PDF |
| memory / handoff / 踩坑复盘 | [codex/docs/memory/README.md](../codex/docs/memory/README.md)，再读相关 memory 文件 | memory 只给路由、警示和交接；事实仍回权威源验证 |

## 2. 单一权威源

每条事实、规则、范围边界、验证命令、项目状态或结果解释只能有一个权威位置。其他文件只放指针，不并行复述。

| 信息类型 | 权威位置 | 非权威位置的做法 |
|---|---|---|
| 项目现状、阻塞项、活跃入口 | [docs/INDEX.md](INDEX.md) | 只链接 INDEX |
| 具体经过、当天判断、踩坑 | [docs/logs/YYYY-MM-DD.md](logs/) | 只给日志日期指针 |
| 领域方法、边界、解释 | `docs/modeling/`, `docs/prd/`, `docs/ops/`, `docs/papers/` | 只链接对应小节 |
| 原始数据、数值结果、图表 | `experiments/` 结果文件、代码输出 | 不复制数值表 |
| 可复用执行计划 | `codex/docs/plans/` | 不复制计划正文 |
| 跨会话索引、警示、handoff | `codex/docs/memory/` | 只写摘要和指针 |
| 代码行为 | `src/`, `scripts/`, tests | 文档描述必须指向代码或测试 |

如果同一信息已经在权威位置存在，新文档只能链接它。需要改变事实时，先改权威位置，再更新路由指针。

## 3. 目录路由

```
drylab/
├── AGENTS.md              # Agent 启动 shim；只放加载规则和指针
├── CLAUDE.md              # Claude Code 兼容 shim
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
│   ├── docs/plans/        # repo-owned execution plans
│   └── docs/memory/       # repo-scoped project memory；索引/警示/交接层
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
- 每次发生 durable 状态变更时，同步审视 INDEX。

### codex/docs/memory/

repo-scoped project memory 是时间戳索引、警示和 handoff 层，不是事实权威。

- `current-state.md` 只写 `last_reviewed`、`latest_snapshot`、`state_timeline`、`source_pointers`。
- `latest_snapshot` 只保留 5-8 条现状摘要，每条必须带日志或领域文档指针。
- 旧时间线条目标为 historical；当前状态回 `latest_snapshot` 和对应 source pointers。
- 普通任务只写日志；只有 durable 状态变更才更新 memory。

Codex native/global memory 和 Claude 私有 memory 只能保存用户偏好、入口规则或指向本仓库的路由，不复制 drylab 科学结论。

### docs/logs/

日志记录“做了什么、为什么、依据是什么、踩了什么坑、下一步不要重复什么”。日志是过程权威，不承担跨天当前状态；跨天状态回 INDEX，状态摘要指针回 memory。

人工维护的日志正文默认使用中文书写，措辞必须专业、严谨、可审计。命令、路径、代码符号、错误信息、工具输出、英文论文标题等字面证据保留原文，并用中文说明其上下文和含义。历史日志如需语言归一化，只做表达层翻译，不改变事实、时间、数值、路径或证据指针。

### docs/modeling/ 与 docs/prd/

领域文档承载方法、范围、证据边界、依赖关系和当前权威指针。容易老化的进展表、候选列表和运行状态应压缩为日志/结果指针。

策略或 PRD 类文档若含历史分析，必须在顶部标明历史边界，并把当前现状指回 INDEX。

### docs/ops/

当前操作规范留在 `docs/ops/` 根目录；旧服务器、旧工具链、旧事故复盘放入 `docs/ops/archives/`。归档材料只用于追溯旧结果、理解旧日志或访问历史文件；新任务默认入口使用当前 `docs/ops/` 规范。

新服务器/远程计算任务先读 [ops/nkuliulab-e2-cloud-server.md](ops/nkuliulab-e2-cloud-server.md)。MD/GROMACS 的服务器中立踩坑见 [ops/md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)。

Payload / manifest / Git tracking 规则见 [ops/payload-tracking-policy.md](ops/payload-tracking-policy.md)。该文件是条件加载的 commit/tracking 分类规则，用于 payload、manifest、checksum、ignore 或 staging 风险审查；普通 MD 状态或科学解释入口仍按本 DOCMAP 的任务画像选择。

### docs/papers/

文献采用稳定 ID。需要文献时，先查 [papers/literature-matrix.md](papers/literature-matrix.md)，再按需读取单篇 summary、数据源或必要 PDF。

### docs/presentation/

汇报资料、旧 deck 和参考材料放在 `docs/presentation/`。该目录服务于表达、排版和材料组织，不是 ODE、P2、reporter、MD 或 docking 的事实权威；涉及事实、状态、数值或边界时必须回到 `docs/INDEX.md`、`docs/modeling/`、`docs/decisions/`、`docs/logs/`、代码和结果文件。

## 5. 代码、结果与文档联动

- 代码路径、配置路径和实验产出路径必须由领域文档指明。
- 代码或结果改变后，先写日志；若改变跨 session 的状态，再更新 INDEX 和必要的 memory 指针。
- 结果文件是数值权威；文档只解释使用边界和指针。
- 脚本不得硬编码 `experiments/` 下的可配置路径；优先从配置文件或项目根解析。

## 6. 远程与部署边界

- 本地 repo 的 `src/`、`scripts/`、`docs/` 是源头；服务器工作目录是部署或运行目标。
- 服务器端不得反向成为脚本或文档权威源。
- 需要修改脚本、配置或流程时，先改 repo，再同步到服务器。
- 任何例外路线必须有 repo 内计划、环境矩阵或 gate script 指针支撑。

位于 `~/.claude/projects/{project-hash}/memory/`。每个文件 10-20 行，存储行为指导，不复制 docs/ 的内容。如果信息在 docs/ 有完整版本，memory 只放指针。

### 文献管理 — 三文件架构 + 稳定 ID

文献采用 **Author-Year 稳定 ID**（如 `Hu2024`、`Huang2023a/b`、`FanC2023`、`iGEM-BITChina2017`），废弃全局序号——插入新文献不再触发下游重编号，跨文档引用永不失效。

| 文件 | 角色 | 读者 |
|------|------|------|
| `literature-matrix.md` | 本地权威矩阵，按 Tier 分层 | AI 助手、dry lab |
| `literature-quick-ref.csv` | 扁平 CSV，导入飞书多维表格 | 组员（通过多维表格） |
| `literature-review-feishu.md` | 详细总结汇编，贴入飞书云文档 | 组员（通过云文档） |
| `summaries/{ID}-{Topic}-summary.md` | 单篇按需加载总结 | AI 助手 |

组员使用流程（多维表格新增、AI 读文献 prompt 模板、ID 命名规则）详见 **[papers/README.md](papers/README.md)**。

### 当日日志 — 跨会话粘合剂

日志（`docs/logs/YYYY-MM-DD.md`）捕获其他文件无法记录的内容：决策的叙事上下文。

**踩坑记录是知识**："踩坑"章节是日志中对后续会话最有价值的部分。记录根因而非仅记修复方法。

**日志 → 操作规范的晋升路径**：
```
Day 1: 遇到问题，记录在日志
Day 2: 遇到类似问题，再次记录
Day 3: 识别模式 → 提升为 docs/ops/ 操作规范
       → 添加到 memory 作为行为规则
       → 可选：创建 hook 自动提醒
```

---

## 7. 上下文窗口经济学

### 文献按需加载

```
绝不：批量读取 summaries/ 目录或直接读 PDF
总是：先查 literature-matrix.md → 只读取具体某篇 summary
限制：同时最多加载 2-3 篇总结
```

文献矩阵的一句话摘要足以回答多数问题，无需打开全文。

### 按需加载策略

```
会话启动 → CLAUDE.md（自动）→ SKILL.md（自动）→ INDEX.md
用户问方向 A → 加载 modeling/P0-direction-a.md
用户要跑 SSH/Slurm → 加载 ops/slurm-md-server.md（Windows 节点已弃用）
用户问文献 → 查矩阵 → 加载单篇 summary
```

---

## 8. 文档生命周期

### 创建

1. 新建方向文档放入 `docs/modeling/`，并补充 frontmatter、范围、方法、依赖和证据边界。
2. 新增方向或入口时同步更新 [docs/INDEX.md](INDEX.md)。
3. 重大技术选择同时创建 `docs/decisions/NNN-title.md`。

### 迭代

- 改事实先改权威文件，再改路由。
- 方法路线变化时保留历史边界和原因，但不要保留会被误读成当前行动的旧待办。
- 不把日志中的具体经过复制到 PRD、DOCMAP 或 memory。

### 归档

- 停用材料进入对应 archive 目录，或按用户明确要求删除。
- 活跃路由不得继续指向已删除或停用目录。
- 历史日志中的旧路径记录可保留，除非用户明确要求重写历史引用。

## 8. 命名与引用规则

| 类型 | 命名模式 | 示例 |
|---|---|---|
| 建模方向文档 | `P{0-3}-{english-name}.md` | `P0-molecular-docking.md` |
| 技术决策记录 | `{NNN}-{short-title}.md` | `003-chassis-yeast-ste2-integration.md` |
| 工作日志 | `YYYY-MM-DD.md` | `2026-06-02.md` |
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
