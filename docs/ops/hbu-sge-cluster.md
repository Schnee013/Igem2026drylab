# HBU SGE 集群操作手册

> 适用环境: Mac → HBU 校内 SGE 集群 via EasyConnect VPN
> 调度系统: **Sun Grid Engine (SGE) 8.1.9** — 与 Slurm 语法不同，提交/查询命令一套独立
> 创建日期: 2026-04-22
> 更新日期: 2026-04-22
> 参考: 集群管理员（刘菲 15131228271）提供的《服务器-集群操作手册》

---

## 服务器基本信息

| 项目 | 值 |
|------|-----|
| 登录地址 | `igem@10.51.13.70`（端口 22988） |
| 别名（SSH config） | `hbu-master` |
| 管理网段 | 10.51.13.70-77（70=master，其余=计算/GPU/fat 节点） |
| 主机名 | `master` |
| OS | CentOS 7（kernel 3.10.0-1160.el7.x86_64） |
| 调度系统 | **SGE 8.1.9** (`gridengine`) |
| 接入方式 | HBU 校园网 VPN（EasyConnect）→ SSH |
| 认证 | GSSAPI/Kerberos + 密码 |
| SGE 命令路径 | `/BiO/gridengine/bin/lx-amd64/`（已在默认 PATH） |

---

## VPN 接入（EasyConnect）

- Portal：`https://v03.hbu.cn:65422`
- macOS 客户端：Portal 登录后首页有 "For Mac" 下载；若按钮无效，DevTools → Network 抓实际 dmg URL
- 装好 EasyConnect → 输 HBU 统一认证账号 → 虚拟网卡起来后即可 SSH

---

## SSH 登录

端口非标准（22988），已在 `~/.ssh/config` 配好别名：

```text
Host hbu-master 10.51.13.70
  HostName 10.51.13.70
  User igem
  Port 22988
  IdentityFile ~/.ssh/id_ed25519
```

登录命令：

```bash
ssh hbu-master
# 或
ssh -p 22988 igem@10.51.13.70
```

首次登录必须改密码（管理员强制，密码须含大小写字母+数字+标点）：

```bash
passwd   # 先输旧密码，再输两次新密码
```

节点间跳转（在 master 上）：

```bash
ssh -p 22988 node1   # 示例；计算节点也走 22988
```

### 免密登录

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub hbu-master
```

验证：`ssh hbu-master 'hostname && whoami'` 应直接返回，不再问密码。

---

## 硬件配置（qhost 汇总）

| 节点 | CPU（核） | 内存 | 用途 |
|------|-----------|------|------|
| master | 40 | 125G | **登录/提交节点**，禁跑任务 |
| fat1 | 96 | 2.0T | 大内存 fat 任务专用 |
| gpu1 | 40 | 251G | GPU 节点 ⚠️ **当前用开源驱动（nouveau），无 NVIDIA 官方驱动，CUDA 不可用**（师兄实测） |
| node1 | 80 | 251G | 通用计算 |
| node2 | 80 | 251G | 通用计算 |
| node3 | 80 | 251G | 通用计算 |
| node4 | 40 | 251G | 通用计算 |
| node5 | 40 | 251G | 通用计算 |

> GPU 型号/数量/CUDA 版本/驱动：待 probe 后补充。

---

## 队列映射（`qstat -f` 可查）

| 队列 | 覆盖节点 | 典型用途 |
|------|---------|---------|
| `all.q` | 全部计算节点 | 通用 |
| `sci.q` | node1, node2 | 科学计算 |
| `cns.q` | node1-5 + gpu1 | 通用（管理员默认） |
| `fat.q` | fat1 | **仅限大任务** |
| `gpu.q` | gpu1 | **GPU 任务专用** |

→ 提交 GPU 任务：`-q gpu.q`
→ 普通 CPU 任务：`-q sci.q` 或 `-q all.q`

---

## ⚠️ Master 节点行为规范

**master 节点禁止直接运行任何计算任务**（CPU/内存有限，违规可能导致 master down 掉）。包括但不限于：

- `gmx_mpi mdrun`、`vina`、`python` 长任务、大数据解压、`find /` 全盘扫描
- `nohup sh shell &` 背景任务
- `qrsh` 交互式进计算节点跑非 qsub 命令

**允许的 master 操作**：
- 文件编辑、`scp`/`rsync` 传输、`qsub`/`qstat`/`qdel`/`qhost`、短时 script/shell 操作
- `module`/`conda activate`（只加载环境，不跑任务）

所有计算必须 `qsub` 成 SGE 任务到计算节点执行。违反规则："节点由于又有本地任务又有 SGE 分发的任务，很容易卡死"（管理员原话）。

---

## 文件系统

| 路径 | 说明 |
|------|------|
| `/data` | 共享存储（117T 总，约 89% 已用，剩 ~13T）⚠️ 使用率已进入警戒区 |
| `/data/igem` | 本项目工作目录（`$HOME`） |
| `/opt/ohpc/pub/apps/` | OpenHPC 预装软件栈 |
| `/BiO/gridengine/` | SGE 本体 |

⚠️ `/data` 容量紧张，大轨迹/中间文件定期清理；长期归档拉回本地。

---

## 预装软件盘点

### `/opt/ohpc/pub/apps/` 下

| 软件 | 路径 | 备注 |
|------|------|------|
| Anaconda3 | `/opt/ohpc/pub/apps/anaconda3/` | 完整 conda，可建 env |
| Miniconda3 | `/opt/ohpc/pub/apps/miniconda3/` | 轻量 conda |
| R 4.1.1 | `/opt/ohpc/pub/apps/R-4.1.1/` | |
| RAxML-8.2.12 / mafft / gatk / sambamba 等 | `/opt/ohpc/pub/apps/` | 生信工具 |
| NCBI tools | `/opt/ohpc/pub/apps/ncbi/` | |

### MPI 栈（`/opt/ohpc/pub/mpi/`）

| Stack | 备注 |
|-------|------|
| `mpich-gnu8-ohpc` | MPICH + GCC 8 |
| `mvapich2-gnu8` | IB 优化 |
| `openmpi3-gnu8` | OpenMPI 3 |

### InfiniBand / RDMA

- `/opt/knem-1.1.4.90mlnx1/` + `/opt/mellanox/` → 节点间通信用 Mellanox IB 栈

### ⚠️ 未预装（本项目需自装）

| 软件 | 项目用途 | 安装方式建议 |
|------|---------|------------|
| ~~GROMACS（GPU 编译）~~ | ~~MD 生产~~ | **不在 HBU 装**：gpu1 开源驱动无 CUDA；MD 继续留 10.40.4.5 Slurm |
| AutoDock Vina | Docking（Gpr2 Ala + Sat scan） | 下载 `vina_1.2.7_linux_x86_64` 静态 binary，chmod +x 即用（CPU 队列足够） |
| ProLIF / RDKit / prepare_receptor | IFP 分析 + ADFR | conda env（docking-repro） |

`module` 命令在默认 shell 中**未加载**；需自行 `source /opt/ohpc/admin/lmod/lmod/init/bash`（路径待确认）或直接用绝对路径调用。

---

## SGE 常用命令

| 操作 | 命令 |
|------|------|
| 提交作业 | `qsub script.sh` |
| 查看我的作业 | `qstat -u $USER` |
| 查看完整队列 | `qstat -f` |
| 查看作业详情 | `qstat -j <jobid>` |
| 删除作业 | `qdel <jobid>` |
| 查看节点状态 | `qhost` |
| 查看队列配置 | `qconf -sq <queue>` |
| 查看用户列表 | `qconf -suserl` |

状态码：
- `qw` = queued waiting（排队中）
- `r` = running
- `Eqw` = error + queued（被标记错误；用 `qstat -j <id>` 查 `error reason`）
- `t` = transferring
- 队列名后缀 `E` = 队列本身异常（管理员处理）

---

## qsub 脚本语法（与 Slurm 对照）

SGE 指令用 `#$` 开头，和 Slurm 的 `#SBATCH` 对应：

| Slurm | SGE |
|-------|-----|
| `#SBATCH --job-name=foo` | `#$ -N foo` |
| `#SBATCH --partition=gpu` | `#$ -q gpu.q` |
| `#SBATCH --output=f.log` | `#$ -o f.log` |
| `#SBATCH --error=f.err` | `#$ -e f.err` |
| `#SBATCH --mem=16G` | `#$ -l vf=16G`（virtual_free） |
| `#SBATCH --cpus-per-task=8` | `#$ -pe smp 8`（parallel env，slots） |
| `#SBATCH --time=48:00:00` | `#$ -l h_rt=48:00:00` |
| `cd $SLURM_SUBMIT_DIR` | `#$ -cwd`（在 script 顶部指令，自动切到提交目录） |
| `echo $SLURM_JOB_ID` | `echo $JOB_ID` |
| `sbatch job.sh` | `qsub job.sh` |
| `squeue -u $USER` | `qstat -u $USER` |
| `scancel <id>` | `qdel <id>` |

### 基础模板（CPU 任务）

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -q sci.q
#$ -pe smp 4
#$ -l vf=16G
#$ -N my_cpu_job
#$ -o my_cpu_job.out
#$ -e my_cpu_job.err

echo "=== Start: $(date) on $HOSTNAME ==="

# 你的命令，这里示例
python3 my_script.py

echo "=== Done: $(date) ==="
```

### GPU 任务模板

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -q gpu.q
#$ -pe smp 16
#$ -l vf=64G
#$ -N my_gpu_job
#$ -o my_gpu_job.out
#$ -e my_gpu_job.err

echo "=== Start: $(date) on $HOSTNAME ==="
nvidia-smi | head -20

# 你的 GPU 任务，例如 GROMACS
# source /path/to/GMXRC.bash
# gmx_mpi mdrun -v -deffnm prod -ntomp 16 -gpu_id 0

echo "=== Done: $(date) ==="
```

### 资源申请经验值（管理员建议）

> 管理员原话："CPU:内存 按 1:4 经验值申请（如 4 核:16G、8 核:32G），不要越多越好——占太多会降低优先级或排队更久。"

| 任务类型 | `-pe smp` | `-l vf` |
|---------|-----------|---------|
| 轻量 CPU | 4 | 16G |
| 中等 CPU | 8 | 32G |
| Vina 对接 | 8 | 16G |

> ⚠️ **GROMACS GPU MD 不在 HBU 执行**：gpu1 目前用开源驱动（nouveau），CUDA 不可用，本项目 MD 仍在 10.40.4.5 Slurm 上跑。

### 管理员封装 `qsub_sge_plus.pl`

管理员提供了 Perl 封装，自动分片 + 重试：

```bash
nohup /home/liufei/anaconda3/bin/perl \
    /home/liufei/Pipeline/Annotation/Annotation/makefile/../script/repeat/../qsub_sge_plus.pl \
    --interval 5 --maxproc 10 --convert no \
    --resource vf=100G --queue sci.q \
    $bash_shell &
```

- `--maxproc 10` 同时 10 个 slot
- `--queue sci.q` / `gpu.q`（GPU 任务换队列）
- `--resource vf=100G`
- `--interval 5` 每 5s 查一次状态

适合批量扫描（如 Vina Ala/Sat scan 72 个对接）。

---

## 文件同步

### Mac ↔ master

```bash
# Mac → master（上传脚本/PDBQT）
scp -P 22988 -r local_dir/ hbu-master:/data/igem/dest/

# master → Mac（拉回结果）
scp -P 22988 -r hbu-master:/data/igem/results/ ./local_results/
```

用别名 `hbu-master` 就无需 `-P`。

### 跨集群迁移（10.40.4.5 Slurm → HBU SGE）

如需从旧 Slurm 集群拉数据到 HBU，走 Mac 中转：
1. `scp 10.40.4.5:~/drylab-docking/... ./tmp/`
2. `scp ./tmp/ hbu-master:/data/igem/...`

---

## 项目目录约定

建议在 `/data/igem/` 下建两个顶层目录，分离 docking 与 MD：

```
/data/igem/
├── drylab-docking/             # Gpr2/Gpr3 docking 工作区
│   ├── src/modeling/docking-repro/
│   └── experiments/docking-repro/
└── drylab-md/                  # MD 工作区
    └── chimeric-gpr3-aogpa2-c37/
```

与 10.40.4.5 Slurm 上的 `~/drylab-docking` / `~/md-simulation/` 对应。

---

## 本项目任务投递预期

### Gpr2 Docking（CPU only，CPU 队列）

- Ala scan：10 残基 × 2 配体（ascr18/3）= 20 次 Vina → `-q sci.q`，`-pe smp 8`，`vf=16G`，估时 ~2-4h
- Sat scan：36 残基 × 2 配体 = 72 次 → `-q sci.q`，同上，估时 ~6-12h
- 提交方式可选：单 qsub 脚本串行，或 `qsub_sge_plus.pl` 并发

### MD 任务

**不在 HBU 执行**。gpu1 开源驱动无 CUDA，500 ns × ~260k 原子体系 CPU-only 不现实。后续 MD 安排待用户通知。

---

## 待办 / 未核实项

- [ ] GPU 型号（gpu1 有几张什么卡）+ CUDA 版本 + 驱动版本
- [ ] GROMACS 安装方案（源码 vs conda vs 找预装）
- [ ] Vina binary 放置路径（建议 `~/bin/vina`，参考 Slurm 集群）
- [ ] `module` 命令是否可用
- [ ] `/opt/ohpc/pub/apps/anaconda3` 中是否已有 docking 相关 env
- [ ] 项目 `/data/igem` 配额（和 `/data` 总使用率 89% 对比）
- [ ] SGE 任务是否支持 checkpoint/restart（对应 Slurm 的 `step7.cpt` 续跑）
- [ ] GPU 任务申请：`-q gpu.q` 是否已经独占 GPU，或需 `-l gpu=1` / `-l cuda=1` 等附加 request

这些待 probe job 能正常运行后补充。

---

## 踩坑记录

_（待补充。首个可能入库项：计算节点账号同步、qsub 常见 Eqw 处理）_
