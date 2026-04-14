# REF-D：SSH / 远程操作
> 需要在服务器上跑计算时查这份速查。完整操作手册见 `docs/ops/ssh-windows-compute.md`。
## 远程工作模式
```
你的 Mac（开发端）  ──SSH──▶  服务器（计算端）
     │                              │
     ├── 写代码、改代码              ├── 跑计算（对接/MD）
     ├── 看结果、做分析              ├── 存原始输出
     └── Git 版本控制               └── 不改 .py 源码
```
## 连接步骤
1. `ssh user@server-ip` 确认能登录
2. VS Code Remote-SSH：`Cmd+Shift+P` → "Remote-SSH: Connect to Host"
3. 在 VS Code 里打开服务器上的工作目录
4. 终端里 `conda activate docking` + 运行脚本
## 文件同步纪律
**核心原则**：Mac 端 `src/` 是代码的**唯一权威源**。
```
Mac src/  ──单向推送──▶  服务器 src/
        （唯一允许的方向）
```
- **不在服务器上改 `.py`** — 两端版本不一致是最难排查的问题
- **同步后验证**：在服务器端用 `grep` 检查关键函数名，确认文件确实更新
- 结果文件（JSON / PNG / PDB）用 `scp` 或 VS Code 拖拽复制回 Mac
## 长时间任务
对接和 MD 是长时间任务。**不要直接在 SSH 终端运行**——SSH 断开后进程会被杀掉。
```bash
# 推荐：tmux（可以断开后重新接回）
tmux new -s docking
python run_mutagenesis_saturation.py
# Ctrl+B, D 断开
# tmux attach -t docking 重新接入
# 或者：nohup
nohup python run_mutagenesis_alanine.py > alanine.log 2>&1 &
tail -f alanine.log    # 查看进度
```
## 已完成工作参考
docking 阶段的计算在 Windows 7500F 节点上完成（已归档）。完整操作手册：`docs/ops/ssh-windows-compute.md`。后续 MD 将在 Linux 服务器上执行。
