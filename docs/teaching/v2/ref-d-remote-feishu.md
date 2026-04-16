# REF-D：服务器使用规范 + SSH 操作速查

> 需要在服务器上跑计算时**必读本文**。违规操作可能导致进程被 kill、影响其他用户、甚至被取消使用权限。

---

## ⛔ 铁律（违反即取消权限）

| # | 规则 | 为什么 |
| --- | ------ | -------- |
| 1 | **登录节点禁止运行任何计算** | 登录节点内存上限 ~10 GB，跑计算会被 OOM kill 并影响所有人登录 |
| 2 | **所有计算必须通过 `sbatch` 提交** | Slurm 调度器负责分配资源，直接跑会抢占别人的 GPU |
| 3 | **不在服务器上改 `.py` 源码** | 本地 `src/` 是唯一权威源，两端版本不一致是最难排查的 bug |
| 4 | **不要自行安装软件或修改系统环境** | 环境由 spack 统一管理，私自装包可能破坏其他人的依赖 |
| 5 | **不占用超出需要的资源** | 申请 1 张 GPU 够用就不要申请 2 张；`--time` 按实际需要设置 |

> **怎么判断自己是不是在登录节点？** 在终端里输入 `hostname` 按回车。如果显示的不是 `node1`/`node2`/`node3`，你就在登录节点上——**不要在这里跑任何程序**。

### 什么算"计算"？

以下操作**全部禁止在登录节点运行**：

- `gmx mdrun`、`vina`、任何对接/MD 程序
- `python xxx.py`（包括"只是跑个分析"——分析脚本也可能占大量内存）
- 大文件解压（`tar`/`unzip` 大于 1 GB 的文件）

**登录节点只允许做这些事**：看文件（`ls`、`cat`）、编辑小文件（`vim`/`nano`）、传文件（`scp`）、管理作业（`sbatch`/`squeue`/`scancel`）。

---

## 连接服务器

### 第一步：SSH 登录

打开你本地的终端（Mac 的 Terminal / WSL 的终端），输入：

```bash
# ssh = 远程登录命令；-p 10022 = 指定端口号（这台服务器不用默认的 22 端口）
# guest = 用户名；10.40.4.5 = 服务器 IP 地址
ssh -p 10022 guest@10.40.4.5
```

第一次连接会提示 `Are you sure you want to continue connecting (yes/no)?`，输入 `yes` 回车。然后输入密码（向我获取）。

> **注意**：输入密码时屏幕不会显示任何字符（没有 `***`），这是正常的，盲打完按回车即可。

登录成功后，你的终端提示符会变成类似 `guest@login:~$` 的样子——这说明你已经在服务器的**登录节点**上了。

### 第二步（可选）：配置免密登录

每次都输密码很烦。可以配置 SSH 密钥，之后就不用输密码了：

```bash
# 第 1 步：在本地生成密钥对（如果之前已经生成过，跳过这步）
# 一路按回车用默认设置即可，不需要设置密码短语（passphrase 直接回车留空）
ssh-keygen -t ed25519

# 第 2 步：把公钥传到服务器上
# 执行后会要求输入一次服务器密码，之后就不需要了
ssh-copy-id -p 10022 guest@10.40.4.5

# 第 3 步：验证——应该直接登录成功，不再要求输密码
ssh -p 10022 guest@10.40.4.5
```

### 第三步（可选）：配置 SSH 快捷方式

每次输 `-p 10022 guest@10.40.4.5` 太长了。可以在本地配置一个快捷名：

```bash
# 用文本编辑器打开（或创建）SSH 配置文件
# Mac 用 nano，WSL 也用 nano
nano ~/.ssh/config
```

在文件里加入以下内容（复制粘贴即可）：

```
Host slurm # slurm即为你起的alias，后续可用别名代替ip
    HostName 10.40.4.5
    Port 10022
    User guest
    ProxyCommand none # 绕开vpn的网络代理
```

保存退出（nano 里按 `Ctrl+O` 保存，`Ctrl+X` 退出）。之后登录只需要：

```bash
# 配置快捷方式后，ssh slurm 等价于 ssh -p 10022 guest@10.40.4.5
ssh slurm
```

---

## 服务器基本信息

| 项目 | 值 |
|------|-----|
| 登录地址 | `guest@10.40.4.5`，端口 `10022` |
| OS | Ubuntu 22.04 |
| 调度系统 | **Slurm**（作业排队系统，你提交任务，它安排到空闲的机器上跑） |
| 环境管理 | **spack**（软件已预装，不要自己装） |

### 硬件

| 节点 | GPU | 显存 | 适合 |
|------|-----|------|------|
| node1, node2 | RTX 4090 × 2 | 24 GB × 2 | 常规 MD、对接 |
| node3 | RTX 5090 × 3 + RTX Pro 6000 × 1 | 32 GB × 3 + 96 GB × 1 | 大体系、多副本 |

---

## 远程工作模式

```
你的电脑（本地） ──SSH──▶ 登录节点 ──sbatch──▶ 计算节点
      │                      │                      │
      ├── 写代码、改代码      ├── 传文件              ├── 跑计算（对接/MD）
      ├── 看结果、做分析      ├── 提交/管理作业        ├── 存原始输出
      └── Git 版本控制       └── ⛔ 不跑计算          └── ⛔ 不改源码
```

你在本地写好代码 → 用 `scp` 传到服务器 → 在登录节点用 `sbatch` 提交作业 → 计算节点自动运行 → 跑完后用 `scp` 把结果拉回来。

---

## 文件同步纪律

**核心原则**：本地 `src/` 是代码的**唯一权威源**。

```
本地 src/  ──scp 单向推送──▶  服务器 ~/drylab-docking/src/
           （唯一允许的方向）
```

- **不在服务器上改 `.py`** — 两端版本不一致是最难排查的问题
- **同步后验证**：在服务器端用 `grep` 检查关键函数名，确认文件确实更新
- 结果文件（JSON / log）用 `scp` 复制回本地

### 部署代码到服务器

```bash
# 在本地终端执行。这个脚本会自动把代码和数据传到服务器
bash experiments/docking-repro/slurm/deploy_to_slurm.sh
```

或手动 scp：

```bash
# scp = 通过 SSH 复制文件的命令
# 格式：scp 本地文件 用户名@服务器:远程目录
# -P 10022 = 指定端口（注意 scp 用大写 -P，ssh 用小写 -p）
scp -P 10022 src/modeling/docking-repro/*.py src/modeling/docking-repro/config.yaml \
    guest@10.40.4.5:~/drylab-docking/src/modeling/docking-repro/
```

### 拉回结果

```bash
# 在本地终端执行
# scp -r = 递归复制整个目录；方向是 服务器:远程路径 → 本地路径
scp -r -P 10022 guest@10.40.4.5:~/drylab-docking/experiments/docking-repro/results/ \
    experiments/docking-repro/results/
```

---

## 用 sbatch 提交计算任务

### 什么是 sbatch？

`sbatch` 是 Slurm 的"提交作业"命令。你写一个 `.sh` 脚本（bash 脚本），里面告诉 Slurm "我需要多少资源、跑什么命令"，然后 `sbatch` 把它丢进队列，Slurm 找到空闲的计算节点自动执行。

### Slurm 作业管理速查

| 你想做什么 | 命令 | 解释 |
|-----------|------|------|
| 提交作业 | `sbatch my_job.sh` | 把脚本丢进队列 |
| 看我的作业在不在跑 | `squeue -u $USER` | 显示你所有排队中/运行中的作业 |
| 取消作业 | `scancel 12345` | 12345 是 job_id，从 squeue 里看到 |
| 看节点忙不忙 | `sinfo` | 显示哪些节点空闲、哪些在用 |
| 看历史作业 | `sacct -u $USER` | 看之前跑过的作业状态（成功/失败） |

### sbatch 脚本模板（对接用）

sbatch 脚本就是一个普通的 `.sh` 文件（bash 脚本），开头用 `#SBATCH` 注释行告诉 Slurm 资源需求。在服务器上用 `nano` 创建：

```bash
# 在服务器上执行。nano = 文本编辑器，创建一个叫 my_docking.sh 的文件
nano my_docking.sh
```

粘贴以下内容：

```bash
#!/bin/bash
# ↑ 第一行固定写法，告诉系统这是 bash 脚本

#SBATCH --job-name=docking_v138r       # 作业名（随便起，方便你在队列里认出来）
#SBATCH --partition=gpu                # 分区（这台服务器的计算节点都在 gpu 分区）
#SBATCH --nodes=1                      # 申请 1 个节点（通常不需要多个）
#SBATCH --ntasks=8                     # 申请 8 个 CPU 核心
#SBATCH --mem=16G                      # 申请 16 GB 内存
#SBATCH --time=2:00:00                # 最长运行 2 小时（超时会被自动杀掉）
#SBATCH --output=docking_%j.log        # 标准输出写到这个文件（%j 会被替换成 job_id）
#SBATCH --error=docking_%j.err         # 错误输出写到这个文件

# --- 以下是实际要执行的命令 ---

# 切换到代码目录
cd ~/drylab-docking

# 运行对接脚本
python3 src/modeling/docking-repro/run_mutagenesis_saturation.py \
    --project-root ~/drylab-docking \
    --vina-bin ~/bin/vina \
    --receptors Gpr3
```

保存退出（`Ctrl+O` 保存，`Ctrl+X` 退出），然后提交：

```bash
# 提交作业。Slurm 会返回一个 job_id（比如 "Submitted batch job 12345"）
sbatch my_docking.sh

# 查看作业状态。ST 列：PD=排队中，R=运行中
squeue -u $USER
```

### sbatch 脚本模板（MD 用）

```bash
#!/bin/bash
# ↑ 第一行固定写法，告诉系统这是 bash 脚本

#SBATCH --job-name=gromacs_md          # 作业名
#SBATCH --partition=gpu                # 分区
#SBATCH --nodes=1                      # 1 个节点
#SBATCH --ntasks=8                     # 8 个 CPU 核心
#SBATCH --gres=gpu:rtx4090:1           # 申请 1 张 RTX 4090 GPU（MD 必须用 GPU）
#SBATCH --mem=64G                      # 64 GB 内存
#SBATCH --time=48:00:00               # 最长 48 小时
#SBATCH --output=md_%j.log             # 标准输出日志
#SBATCH --error=md_%j.err              # 错误日志

# 加载 GROMACS 软件（spack 是服务器的软件管理工具，类似 conda）
spack load gromacs@2025.2 target=zen2

# 运行 MD 模拟
# -v = 显示进度；-deffnm md = 输入输出文件都叫 md.*
# -ntmpi 1 -ntomp 8 = 1 个 MPI 进程 × 8 个 OpenMP 线程
# -gpu_id 0 = 用第 0 号 GPU
gmx mdrun -v -deffnm md -ntmpi 1 -ntomp 8 -gpu_id 0
```

> 完整模板和 GPU 型号选择见 `docs/ops/slurm-md-server.md`。

### 用 AI 辅助写 sbatch 脚本

如果你不确定怎么写 sbatch 脚本，可以让 AI（ChatGPT / Claude 都行）帮你生成。关键是把服务器信息喂给它，否则 AI 会瞎猜分区名和 GPU 型号。

**复制下面这整段 prompt，只改 `【】` 里的内容，发给 AI：**

````
我需要在 Slurm 集群上提交一个计算任务。请帮我写一个 sbatch 脚本（.sh 文件）。

## 服务器环境（固定，不要改）

- OS: Ubuntu 22.04
- 调度系统: Slurm
- 唯一可用分区: gpu
- 计算节点:
  - node1, node2: RTX 4090 × 2（每张 24 GB 显存），80 CPU 核，208 GB 内存
  - node3: RTX 5090 × 3 + RTX Pro 6000 × 1，384 CPU 核，1 TB 内存
- 软件管理: spack（不是 conda/module）
  - GROMACS 加载方式: `spack load gromacs@2025.2 target=zen2`
  - Python 3 可直接使用: `python3`
  - AutoDock Vina 路径: `~/bin/vina`
- 工作目录: ~/drylab-docking

## 我的任务

- 我要跑的命令: 【写你要执行的完整命令，比如 python3 xxx.py --arg1 value1】
- 预计运行时间: 【写你的估计，比如"大约 30 分钟"或"不确定"】
- 是否需要 GPU: 【是/否。对接用 Vina 不需要 GPU，MD 用 GROMACS 需要】
- 如果需要 GPU，指定型号: 【rtx4090 / rtx5090 / pro6000，不确定就写 rtx4090】

## 输出要求

1. 在每一行 #SBATCH 后面加中文注释说明这行的含义
2. 在每条实际执行的命令前加中文注释说明它在做什么
3. --time 根据我的预计运行时间设置（留 50% 余量，向上取整到小时）
4. --mem 对接任务给 16G，MD 任务给 64G
5. 输出文件名包含 %j（会被替换成 job_id）
````

**真实示例——你想跑 Gpr3 的突变体对接：**

你发给 AI 的 prompt（只改了 `【】` 部分）：

> ...（前面的服务器环境部分不变）...
>
> ## 我的任务
>
> - 我要跑的命令: `python3 src/modeling/docking-repro/run_mutagenesis_saturation.py --project-root ~/drylab-docking --vina-bin ~/bin/vina --receptors Gpr3`
> - 预计运行时间: 大约 30 分钟
> - 是否需要 GPU: 否（Vina 用 CPU）

AI 应该给你生成类似这样的脚本：

```bash
#!/bin/bash
# ↑ 第一行固定写法，告诉系统这是 bash 脚本

#SBATCH --job-name=dock_gpr3           # 作业名（在 squeue 里显示，方便辨认）
#SBATCH --partition=gpu                # 分区名（这台服务器只有 gpu 分区）
#SBATCH --nodes=1                      # 申请 1 个计算节点
#SBATCH --ntasks=8                     # 申请 8 个 CPU 核心
#SBATCH --mem=16G                      # 申请 16 GB 内存（对接任务够用）
#SBATCH --time=1:00:00                # 最长运行 1 小时（预估 30 分钟 + 余量）
#SBATCH --output=dock_gpr3_%j.log      # 标准输出写到这个文件（%j = job_id）
#SBATCH --error=dock_gpr3_%j.err       # 错误信息写到这个文件

# 切换到项目目录
cd ~/drylab-docking

# 运行 Gpr3 突变体饱和扫描对接
python3 src/modeling/docking-repro/run_mutagenesis_saturation.py \
    --project-root ~/drylab-docking \
    --vina-bin ~/bin/vina \
    --receptors Gpr3
```

**拿到 AI 生成的脚本后，检查这几项再提交：**

1. `--partition=gpu` — 必须是 `gpu`，其他分区名都是错的
2. `--time` — 不要超过 72 小时（`72:00:00`），否则提交会报错
3. `cd ~/drylab-docking` — 确认工作目录对不对
4. 实际命令 — 和你手动在终端里输的应该完全一样

---

## 加载软件环境

服务器用 **spack** 管理软件（不是 conda）。你不需要自己安装任何东西，只需要在 sbatch 脚本里"加载"已有的软件。

```bash
# 加载 GROMACS（在 sbatch 脚本里写，不要在登录节点执行）
spack load gromacs@2025.2 target=zen2

# 验证是否加载成功
gmx --version
```

Vina 不在 spack 里，已手动装在 `~/bin/vina`：

```bash
# 验证 Vina 是否可用
~/bin/vina --version    # 应输出 AutoDock Vina v1.2.5
```

Python 依赖（`pyyaml`、`numpy`）已通过 `pip install --user` 安装，无需额外操作。

---

## 查看作业进度

```bash
# 看队列状态：你的作业还在不在跑？
squeue -u $USER

# 看实时日志：tail -f 会持续输出新内容，按 Ctrl+C 退出
# 把 <job_id> 替换成 sbatch 返回的数字（如 12345）
tail -f docking_<job_id>.log

# 看结果文件是否生成
ls -lt ~/drylab-docking/experiments/docking-repro/results/
```

---

## 常见问题

**Q: 作业一直 PENDING（排队中）？**
运行 `squeue` 看 REASON 列：`Resources` = GPU 被别人占了，等释放；`Priority` = 排队中，等前面的人跑完。

**Q: 作业状态是 FAILED？**
看错误日志：`cat docking_<job_id>.err`。常见原因：路径写错、文件没传上来、内存不够。

**Q: `spack load` 报错？**
先运行 `spack find gromacs` 看服务器上装了哪些版本。

**Q: Python 报 `ModuleNotFoundError`？**
在 sbatch 脚本开头加一行：`export PATH=$HOME/.local/bin:$PATH`

**Q: 忘了是不是在登录节点？**
运行 `hostname`——显示 `node1`/`node2`/`node3` 才是计算节点，其他都是登录节点。

---

## 已弃用：Windows 计算节点

> 早期 docking 阶段的计算在 Windows 7500F 节点上完成，该节点**已弃用**。所有计算统一迁移到 Slurm 集群。历史操作手册归档在 `docs/ops/ssh-windows-compute.md`，仅供参考，不再使用。
