# DOCMAP: 文档管理规范

> 本文件是项目文档体系的"元规则"，指导 Claude Code 和项目成员如何创建、更新和组织文档。
>
> **方法论来源**: Agile-PM-Workflow（双向联动、物理版本隔离、功能切片）+ Claude Code Skill 指南（INDEX 中心化索引、SKILL 自动加载）

---

## 1. 文档层级结构

```
INDEX.md（灵魂文件，项目全局状态）
  │
  ├── prd/（需求与策略层）
  │   ├── overview.md          项目全貌、信号链路、团队
  │   ├── dry-lab-strategy.md  干实验总策略、痛点调研、防治决策
  │   └── chassis-decision.md  底盘选择分析、决策树、阻塞项
  │
  ├── modeling/（建模方向层 — 每个方向一个独立文件）
  │   ├── P0-*.md              直接支撑湿实验的建模
  │   ├── P1-*.md              增强叙事完整性的建模
  │   ├── P2-*.md              完成检测→预防闭环的建模
  │   └── P3-*.md              加分项
  │
  ├── learning/
  │   └── roadmap.md           学习路线图、硬件需求、工具环境
  │
  ├── papers/（文献与总结）
  │   ├── pdf/                               原始文献 PDF
  │   │   └── {Author}{Year}-{Topic}.pdf
  │   ├── summaries/                         文献总结（供 Claude Code 读取）
  │   │   └── {Author}{Year}-{Topic}-summary.md
  │   ├── literature-matrix.md               文献矩阵（47 条目, 6 Tiers）
  │   └── search-log.md                      搜索日志
  │
  ├── archive/（归档文件 — 原始 PRD、参考指南等）
  │   └── *.md                 已拆分/不再直接使用的源文件
  │
  ├── decisions/（技术决策记录）
  │   └── NNN-title.md         每个重大决策一个文件
  │
  └── logs/（工作日志）
      └── YYYY-MM-DD.md        每天一个文件
```

**原则**: INDEX.md 是唯一的"全局视图"。其他文件只包含自己领域的内容，通过相对路径链接互相引用。

---

## 2. 命名规范

### 文件名
- 建模方向: `{优先级}-{英文短名}.md`，如 `P0-molecular-docking.md`
- PRD 子文档: `{主题}.md`，如 `chassis-decision.md`
- 决策记录: `{三位数编号}-{短标题}.md`，如 `001-chassis-selection.md`
- 工作日志: `YYYY-MM-DD.md`

### 方法变体（同方向多 Pipeline）

当同一建模方向存在多条方法线（如不同工具链的对接 pipeline）时：

- **代码**: `src/modeling/{方向}-{变体名}/`，如 `docking-repro/`
- **实验产出**: `experiments/{方向}-{变体名}/`，如 `experiments/docking-repro/`
- **共享数据**: 原始输入文件（PDB/SDF 等）通过 **symlink** 引用主线目录，不复制
- **独立配置**: 每条方法线有自己的 `config.yaml`，不跨线共享
- **文档**: 在对应方向文档中新增"方法变体"小节，列明各变体的路径、工具链、状态
- **目的标注**: 每个变体需注明为什么存在（如"精确复现 Hu2024"），而非只写工具差异

### Frontmatter（建模方向文档必须包含）

```yaml
---
direction: P0-molecular-docking
status: not_started | learning | in_progress | blocked | completed
priority: P0 | P1 | P2 | P3
chassis_dependent: false | true
last_updated: YYYY-MM-DD
---
```

---

## 3. 交叉引用规则

### 文档间引用
使用 markdown 相对路径链接：
```markdown
详见 [底盘决策分析](../prd/chassis-decision.md)
本方向产出的灵敏度极限被 [贝叶斯推断](P1-bayesian-inference.md) 使用
```

### 方向间依赖标注
每个建模方向文档底部必须有"与其他方向的依赖关系"章节，标明：
- **输出到**: 本方向产出被谁消费
- **依赖于**: 本方向需要谁的产出

### 代码-文档联动
借鉴 Agile-PM-Workflow 的 PRD-原型联动思想：
- 建模方向文档中标明对应代码路径 `src/modeling/{方向}/`
- 建模方向文档中标明实验产出路径 `experiments/exp-XXX/`
- 代码或实验产出变更时，更新对应文档的"进展记录"和"版本记录"

---

## 4. 文档生命周期

### 创建
1. 新建模方向 → 创建 `modeling/P{N}-{name}.md`，填充标准模板
2. 新增到 `INDEX.md` 的方向状态表
3. 如果涉及重大技术选择 → 同时创建 `decisions/NNN-title.md`

### 迭代（借鉴 Agile-PM-Workflow 的物理版本隔离）
- **文档内版本记录**: 每个文档内维护"版本记录"表，记录每次重大变更
- **不删除历史**: 方法路线变更时，在文档内标注"v1.0 → v1.1"并说明变更原因，而非直接覆盖
- **重大方向调整**: 如果底盘决策导致策略切换（A→B），在文档中保留旧策略作为"历史记录/备选"

### 归档
- 已放弃的建模方向：status 改为 `archived`，文件保留不删除
- 已完成的方向：status 改为 `completed`，在进展记录中标注最终产出

---

## 5. Claude Code 按需加载策略

### 功能切片思想（借鉴 Agile-PM-Workflow 的 focus mode）

Claude Code 不需要每次读取全部文档。加载策略：

1. **每次对话启动**: SKILL.md（自动）→ INDEX.md（必读）→ 最新日志（如有）
2. **按用户需求加载**:
   - 用户提到某个建模方向 → 只加载对应的 `modeling/P{N}-*.md`
   - 用户提到底盘决策 → 加载 `prd/chassis-decision.md`
   - 用户提到项目全貌 → 加载 `prd/overview.md`
3. **依赖跟随**: 如果加载的文档标注了"依赖于"其他方向，提示用户是否需要一并加载
4. **文献按需加载**（重要，节省 token）:
   - **绝不批量读取** `summaries/` 目录下的所有总结文件，也**绝不直接读取 PDF**
   - 需要某篇文献信息时 → 先查 `literature-matrix.md` 确认编号和总结链接 → 只读取对应的 `summaries/{Author}{Year}-*-summary.md`
   - 每次最多同时加载 2-3 篇总结，用完即释放
   - 文献矩阵本身即包含每篇文献的一句话摘要，多数场景无需打开总结全文

### INDEX.md 是路由表
INDEX.md 的方向状态表提供足够信息让 Claude Code 判断：
- 哪些方向正在进行（优先关注）
- 哪些方向被阻塞（需要解除阻塞）
- 哪些方向已完成（一般不需要加载）

---

## 6. 版本管理规范

### 文档内版本记录表

每个建模方向文档必须包含：

```markdown
## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 提取初始内容 | 文档体系搭建 |
```

### INDEX.md 更新规则
- 任何建模方向的 status 变化 → 同步更新 INDEX.md 的状态表
- 新增或删除方向 → 同步更新 INDEX.md
- 每日工作结束 → 更新 INDEX.md 的"最近进展"区域

---

## 7. 模板索引

| 模板 | 用途 | 位置 |
|------|------|------|
| 建模方向文档 | 每个 §3.x 方向 | 见本文件 Step 5 标准结构 |
| 技术决策记录 | 重大技术选择 | `decisions/NNN-title.md` |
| 工作日志 | 每日记录 | `logs/YYYY-MM-DD.md` |

### 技术决策模板

```markdown
# 决策 NNN：[标题]

- **日期**: YYYY-MM-DD
- **状态**: 讨论中 | 已决定 | 已废弃
- **关联方向**: [链接到相关建模方向文档]

## 背景
为什么需要做这个决策？

## 选项
1. **方案A**: — 优点 / 缺点
2. **方案B**: — 优点 / 缺点

## 决定
选择方案 X，因为...

## 后果
这个决定意味着...需要更新哪些文档...
```

### 工作日志模板

```markdown
# YYYY-MM-DD 工作日志

## 今日目标
- [计划做什么]

## 完成的工作
### [工作标题]
- 做了什么
- 关键发现/结果
- 相关文件: `path/to/file`

## 实验记录（如有）
- 实验名称: exp-XXX
- 配置: `configs/xxx.yaml`
- 关键指标: [数值]
- 观察: [现象和初步分析]

## 遇到的问题
- [问题描述 + 是否解决 + 解决方案]

## 明日计划
- [下一步做什么]
```
