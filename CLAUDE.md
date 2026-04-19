# drylab Claude Code compatibility

This repository is managed with agent-neutral project rules so Claude Code and
Codex read the same source of truth.

## Startup

For any non-trivial drylab task:

1. Read `docs/DOCMAP.md` first.
2. Read `docs/INDEX.md` unless the task is purely local/mechanical and the exact file or scope is already specified.
3. Read `codex/docs/memory/README.md`, then only task-relevant project memory files.

## Core Rules

- Project memory under `codex/docs/memory/` is an index, not an authority.
- Verify facts against source docs, logs, configs, code, paper summaries, or result files before making strong claims.
- If modifying `src/` or `scripts/`, update `docs/logs/YYYY-MM-DD.md` in the same session.
- If adding or moving durable project files, update `docs/DOCMAP.md` and any affected `docs/INDEX.md` pointers.

## References

1. **当日日志** `docs/logs/YYYY-MM-DD.md`
   - 写在对应「已完成」小节，说明改了什么、为什么
   - 如果日志不存在，创建它

2. **memory 文件**（如果改动影响跨会话理解）
   - 路径：`~/.claude/projects/-Users-roy-Documents-drylab/memory/`
   - 涉及 pipeline 状态/结果 → `project_docking_pipeline.md`
   - 涉及 SSH/Windows 操作规范 → `feedback_ssh_windows.md`

3. **DOCMAP** `docs/DOCMAP.md` §3 目录结构（如有新文件或删除文件）

> 这条规则存在是因为：跨会话记忆依赖日志 + memory，不更新则下个会话看不到本次改动。

## Windows 计算节点（已弃用）

Windows 7500F 节点已停用，计算任务迁移至 Slurm 集群（见 [docs/ops/slurm-md-server.md](docs/ops/slurm-md-server.md)）。  
部分 docking 结构文件仍存于 Windows 节点，需访问时参考历史存档：[docs/ops/archives/ssh-windows-compute.md](docs/ops/archives/ssh-windows-compute.md)。

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
