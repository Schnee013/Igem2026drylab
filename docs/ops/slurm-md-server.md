# MD 模拟服务器操作指南（Slurm 集群）

> 适用环境: Mac → Ubuntu 22.04 login 节点 → Slurm GPU 计算节点  
> 更新日期: 2026-04-15  

---

## 服务器基本信息

| 项目 | 值 |
|------|-----|
| 登录地址 | `guest@10.40.4.5`（非标准端口，见下方 SSH 配置） |
| OS | Ubuntu 22.04.5 LTS |
| 调度系统 | **Slurm** |
| 环境管理 | **spack**（软件已预装，无需自行安装） |
| /home 存储 | 58 TB，当前剩余 ~19 TB |

---

## SSH 登录

端口非 22，需用 `-p` 指定（具体端口确认后填入）：

已在`~/.ssh/config`配置端口和内网ip豁免（绕过vpn代理）

---

## 硬件配置

### 登录节点（login）

| 项目 | 值 |
|------|-----|
| CPU | AMD EPYC 7K62（虚拟机分配 24 核） |
| 内存 | 47 GB（**可用上限约 10 GB**，见警告） |
| GPU | 无 |

### 计算节点

| 节点 | GPU | 显存 | 内存 | CPU核 |
|------|-----|------|------|-------|
| node1, node2 | RTX 4090 × 2 | 24 GB × 2 | 208 GB | 80 |
| node3 | RTX 5090 × 3 + RTX Pro 6000 × 1 | 32GB×3 + 96GB×1 | 1 TB | 384 |

> RTX Pro 6000 为 Blackwell 架构专业卡，96 GB 显存，适合超大体系或多副本并行。

---

## ⚠️ 登录节点禁止运行程序

**登录节点有内存限制（约 10 GB），禁止直接运行计算任务。**

包括但不限于：
- `gmx mdrun`
- Python 脚本（数据处理、分析等）
- 大文件解压/转换

所有计算必须通过 `sbatch` 提交到计算节点。违反可能导致进程被 kill 或影响其他用户。

---

## 加载 GROMACS 环境

环境已由 spack 预装，登录后无需自行安装。根据节点 CPU 架构选择：

```bash
# node1-2（AMD EPYC 7K62，Zen2 架构）
spack load gromacs@2025.2 target=zen2

# node3（AMD EPYC，Zen4 架构，需确认）
spack load gromacs@2025.2 target=zen4
```

> 如果不确定目标节点架构，优先用 `zen2`，通用性更好。

验证加载成功：

```bash
gmx --version
```

---

## Slurm 基本命令

| 操作 | 命令 |
|------|------|
| 提交作业 | `sbatch job.sh` |
| 查看队列 | `squeue -u $USER` |
| 取消作业 | `scancel <job_id>` |
| 查看节点状态 | `sinfo -o "%P %N %G %m %c"` |
| 查看作业详情 | `scontrol show job <job_id>` |
| 查看历史作业 | `sacct -u $USER --format=JobID,JobName,State,Elapsed` |

---

## GROMACS sbatch 脚本模板

### 标准 MD（RTX 4090，node1 或 node2）

```bash
#!/bin/bash
#SBATCH --job-name=gromacs_md
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --gres=gpu:rtx4090:1
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=md_%j.log
#SBATCH --error=md_%j.err

spack load gromacs@2025.2 target=zen2

gmx mdrun -v -deffnm md -ntmpi 1 -ntomp 8 -gpu_id 0
```

### 大体系 / 多副本（RTX 5090 或 Pro 6000，node3）

```bash
#!/bin/bash
#SBATCH --job-name=gromacs_md_large
#SBATCH --partition=gpu
#SBATCH --nodelist=node3
#SBATCH --ntasks=16
#SBATCH --gres=gpu:rtx5090:1
#SBATCH --mem=128G
#SBATCH --time=72:00:00
#SBATCH --output=md_%j.log
#SBATCH --error=md_%j.err

spack load gromacs@2025.2 target=zen4

gmx mdrun -v -deffnm md -ntmpi 1 -ntomp 16 -gpu_id 0
```

---

## MD 性能估算（参考）

| GPU | 体系规模 | 估算速度 | 200 ns 耗时 |
|-----|---------|---------|------------|
| RTX 4090 | ~80k 原子（膜蛋白） | ~200 ns/day | ~1 天 |
| RTX 5090 | ~80k 原子 | ~280 ns/day | ~17 小时 |
| RTX Pro 6000 | ~120k 原子 | ~200 ns/day | ~1 天 |

> 以上为估算值，实际速度受体系大小、力场、PME 设置影响。首次运行建议先跑 1 ns 测速。

---

## 常见问题

**Q: `spack load` 报错找不到包？**  
先运行 `spack find gromacs` 确认已安装的版本和 hash。

**Q: 作业一直在 pending？**  
运行 `squeue` 看 REASON 列，`Resources` = 等资源，`Priority` = 排队中。

**Q: node3 的 Pro 6000 如何申请？**  
```bash
#SBATCH --gres=gpu:pro6000:1
```

---

## Docking（Vina）首次运行

> 新增: 2026-04-16, Gpr2 WT 重对接  
> → 根因: `docs/logs/2026-04-16.md` §Gpr2 Docking Pose 朝向验证

### 部署方式

Mac 本地运行部署脚本:

```bash
bash experiments/docking-repro/slurm/deploy_to_slurm.sh
```

会自动 SCP 代码（6 文件）+ 数据（受体+配体 PDBQT）到 `~/drylab-docking/`。

### Vina 安装

服务器上未通过 spack 安装 Vina。手动下载:

```bash
# ⚠ 必须用 curl -L（GitHub releases 有 302 重定向，wget 默认不跟随会下载 HTML）
curl -fSL -o ~/bin/vina 'https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64'
chmod +x ~/bin/vina
~/bin/vina --version   # 应输出 AutoDock Vina v1.2.5
```

> **踩坑**：`wget -O` 下载 GitHub releases 会得到 ~1MB HTML 而非 ~4MB ELF binary。
> 症状：`file ~/bin/vina` 显示 "missing section headers"，`Permission denied` 即使 chmod 后。

### sbatch 提交

```bash
cd ~/drylab-docking
sbatch gpr2_redock.sh
squeue -u $USER
```

### 拉回结果

```bash
# 在 Mac 端
scp -r 10.40.4.5:~/drylab-docking/experiments/docking-repro/results/wt_singlestage/ \
    experiments/docking-repro/results/wt_singlestage_gpr2_redock/
```

### Python 依赖

脚本需要 `pyyaml` 和 `numpy`（grid_box.py 计算质心使用）。

> **踩坑**：服务器无 pip/pip3/conda/spack。需先引导安装 pip：

```bash
# Step 1: 引导 pip（一次性）
wget -q -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
python3 /tmp/get-pip.py --user
export PATH=$HOME/.local/bin:$PATH

# Step 2: 安装依赖
pip3 install --user numpy pyyaml
python3 -c "import numpy; import yaml; print('OK')"
```

> 已安装版本：numpy 2.2.6, PyYAML 5.4.1（系统自带）。
