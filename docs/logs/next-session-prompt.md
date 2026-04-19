# Next Session Prompt — 2026-04-18 续

## 当前状态

Chimeric MD Phase C2（CHARMM-GUI Membrane Builder）部分完成：

| 体系 | Job ID | 本地下载 | 状态 |
| --- | --- | --- | --- |
| Chctrl（Ste2+Gpa1-WT） | 7649276832 | `/Users/roy/Downloads/Arc/charmm-gui-7649276832/gromacs/` | ✅ 验证通过 |
| Ch-1（Gpr3+AoGpa2-C37） | 7650133176 | `/Users/roy/Downloads/Arc/charmm-gui-7650133176/gromacs/` | ✅ 验证通过 |
| Ch-2（Gpr3+AoGpa2-C15） | — | — | ⏳ CHARMM-GUI 进行中 |
| Ch-4（Gpr2+AoGpa2-C10） | — | — | ⏳ CHARMM-GUI 进行中 |

**CHARMM-GUI 实测时间：每个体系约 2.5 小时**（plan 原估算 30 min 严重低估，需更新 plan 文件）

## 任务清单

### 1. 更新 plan 文件时间估算
`~/.claude/plans/chimeric-md-execution.md` §Phase C2：将"每个体系约 30 min"改为"每个体系约 2.5 小时"

### 2. 移入本地 systems 目录
```bash
cp -r "/Users/roy/Downloads/Arc/charmm-gui-7649276832/gromacs/" \
  experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/

cp -r "/Users/roy/Downloads/Arc/charmm-gui-7650133176/gromacs/" \
  experiments/md-simulation/systems/chimeric-gpr3-aogpa2-c37/gromacs/
```
若目标目录不存在先 mkdir。

### 3. 部署 + 提交 SLURM（Chctrl + Ch-1）
```bash
cd experiments/md-simulation/slurm/
bash deploy_chimeric.sh Chctrl    # scp 到 guest@10.40.4.5
bash deploy_chimeric.sh Ch1
sbatch run_chimeric_phase3.sh Chctrl
sbatch run_chimeric_phase3.sh Ch1
```
部署脚本和 SLURM 脚本细节 → `~/.claude/plans/chimeric-md-execution.md` §Phase C3 + §5

**提交前必须验证**：`index.ndx` 中有 `SOLU_MEMB` 组（两个体系已验证 ✅）

### 4. Ch-2 / Ch-4 CHARMM-GUI 提交注意
- 建议直接从 **140 Å** 开始（跳过 120→130 试错）
- 操作细节 → `docs/ops/charmm-gui-membrane-builder.md`
- Ch-2/Ch-4 下载后同样执行步骤 2-3

### 5. 更新日志 + memory
- `docs/logs/2026-04-18.md` 补记 deploy + sbatch 结果
- `memory/project_chimeric_gpa1.md` 更新 Phase C2 → C3 进展

## 关键文件指针
- 执行计划：`~/.claude/plans/chimeric-md-execution.md`
- CHARMM-GUI 操作规范：`docs/ops/charmm-gui-membrane-builder.md`
- 服务器操作规范：`docs/ops/slurm-md-server.md`
- 当日日志：`docs/logs/2026-04-18.md` §Session 5
