# drylab CLAUDE.md

## 项目背景

iGEM 2026 干实验（Dry Lab）计算建模仓库。涵盖分子对接（Vina 两阶段）、信号通路 ODE、嵌合 G 蛋白设计。

## 文档规范

项目文档管理的完整规范（信息分层、目录结构、命名规范、环境管理、生命周期、反模式等）：**[docs/DOCMAP.md](docs/DOCMAP.md)**

核心原则：每条信息只有一个权威源，其他地方只放指针，不复制内容。

## 代码改动后强制更新文档

**每次修改 `src/` 或 `scripts/` 下的文件后，必须同步：**

1. **当日日志** `docs/logs/YYYY-MM-DD.md`
   - 写在对应「已完成」小节，说明改了什么、为什么
   - 如果日志不存在，创建它

2. **memory 文件**（如果改动影响跨会话理解）
   - 路径：`~/.claude/projects/-Users-roy-Documents-drylab/memory/`
   - 涉及 pipeline 状态/结果 → `project_docking_pipeline.md`
   - 涉及 SSH/Windows 操作规范 → `feedback_ssh_windows.md`

3. **DOCMAP** `docs/DOCMAP.md` §3 目录结构（如有新文件或删除文件）

> 这条规则存在是因为：跨会话记忆依赖日志 + memory，不更新则下个会话看不到本次改动。

## Windows 计算节点

**任何 SSH Windows 操作前必读**：[docs/ops/ssh-windows-compute.md](docs/ops/ssh-windows-compute.md)（含所有踩坑快查和正确模板，已通过 PreToolUse hook 强制提醒）

## 目录约定

| 路径 | 说明 |
|------|------|
| `src/modeling/docking-repro/` | docking-repro pipeline 代码（权威） |
| `experiments/docking-repro/prepared/` | ADFR 准备的受体/配体 PDBQT（**单一来源**，config `prepared_dir`） |
| `experiments/docking/prepared/` | v2 pipeline 专用，docking-repro 脚本**不引用** |
| `experiments/docking-repro/results/` | 对接结果 JSON |
| `experiments/docking-repro/logs/` | 运行日志 |
| `docs/logs/` | 每日工作日志 |
| `docs/ops/` | 操作规范（SSH、环境配置等） |
| `environments/` | conda 环境定义和锁定，详见 [DOCMAP §5](docs/DOCMAP.md#5-计算环境管理) |
