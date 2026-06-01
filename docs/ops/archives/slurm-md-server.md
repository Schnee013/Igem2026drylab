# MD 模拟服务器操作指南（Slurm 集群）

> ⚠️ **[已归档 — 2026-05-27]** 本文仅保留 10.40.4.5 Slurm 集群历史操作记录和既有 MD 运行证据。新服务器/远程计算任务默认使用 [NKULiulab E2 共享云服务器使用规范](../nkuliulab-e2-cloud-server.md)，操作前必须先阅读该规范。2026-05-30 起，chimeric MD 统一 rerun 可把旧 Slurm RTX 5090 作为 validated secondary candidate，但只能走 `environments/md-production-sites.md` 和新的 `experiments/md-simulation/scripts/slurm_*` gate scripts；不要复用本文的旧 production provenance。
>
> 适用环境: Mac → Ubuntu 22.04 login 节点 → Slurm GPU 计算节点  
> 更新日期: 2026-04-16  

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

GROMACS 已由 spack 预装，但 **计算节点无法运行 `spack load`**（见踩坑 #1）。必须通过 `source GMXRC.bash` 直接加载：

```bash
# ⚠ 计算节点唯一可靠方式（spack load 在计算节点会失败）
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen2/gromacs-2025.2-3isv4kzjxtnsk32oq56gzceluac7k6uc

# GMXRC.bash 内部引用未初始化变量，必须临时关闭 nounset（见踩坑 #2）
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u

gmx_mpi --version   # ⚠ 此集群只有 MPI 编译，命令是 gmx_mpi 不是 gmx（见踩坑 #3）
```

> 登录节点仍可用 `spack load gromacs@2025.2 target=zen2`，但 sbatch 脚本中**禁止使用**。

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
#SBATCH --ntasks=1              # ⚠ 单 MPI rank（不是 8！见踩坑 #3）
#SBATCH --cpus-per-task=8       # OpenMP 线程数
#SBATCH --gres=gpu:rtx4090:1
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=md_%j.log
#SBATCH --error=md_%j.err

set -euo pipefail

# 加载 GROMACS（见上方"加载 GROMACS 环境"）
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen2/gromacs-2025.2-3isv4kzjxtnsk32oq56gzceluac7k6uc
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u

# ⚠ 用 gmx_mpi（MPI 编译），不能加 -ntmpi（见踩坑 #3）
gmx_mpi mdrun -v -deffnm md -ntomp 8 -gpu_id 0
```

### 大体系 / 多副本（RTX 5090，node3）

```bash
#!/bin/bash
#SBATCH --job-name=gromacs_md_large
#SBATCH --partition=gpu
#SBATCH --nodelist=node3
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:rtx5090:1
#SBATCH --mem=128G
#SBATCH --time=168:00:00
#SBATCH --output=md_%j.log
#SBATCH --error=md_%j.err

set -euo pipefail

# ⚠ node3 RTX 5090 (sm_120) 必须用 zen4 路径；zen2 路径只兼容 RTX 4090
GMXPREFIX=/opt/softwares/spack/opt/spack/linux-zen4/gromacs-2025.2-v5xhhnf3iroo56vaxpp77aqr27xkkykx
set +u
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u

gmx_mpi mdrun -v -deffnm md -ntomp 16 -gpu_id 0
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

## 踩坑记录（Phase 3 部署，2026-04-16）

> 来源：jobs 6581→6596，7 轮迭代修复 6 个 bug。完整叙事 → `docs/logs/2026-04-16.md` §Phase 3 部署

### #1 — spack load 在计算节点失败（jobs 6581/6582）

**现象**：`spack load gromacs` 在计算节点超时，日志显示尝试 `git clone https://github.com/spack/spack`。  
**根因**：计算节点无互联网。`spack load` 需要下载包索引元数据，即使软件已安装。  
**修复**：绕过 spack，直接 source GMXRC：

```bash
# ❌ 计算节点无网络，spack load 会超时
spack load gromacs@2025.2 target=zen2

# ✅ 直接 source 预装路径
source /opt/softwares/spack/opt/spack/linux-zen2/gromacs-2025.2-3isv4kzjxtnsk32oq56gzceluac7k6uc/bin/GMXRC.bash
```

**规则**：sbatch 脚本中禁止使用 `spack load`，一律 source GMXRC.bash。

---

### #2 — GMXRC.bash + set -u 不兼容（jobs 6583/6585）

**现象**：`set -u`（nounset）下 source GMXRC.bash 报 `unbound variable: GMXLDLIB`，然后是 `LD_LIBRARY_PATH`。  
**第一次错误修复**：在 source 前预初始化 `GMXLDLIB="" GMXBIN=""` → 不够，GMXRC.bash 还引用了更多未初始化变量。  
**正确修复**：临时关闭 nounset：

```bash
set +u                             # 关闭 nounset
source "${GMXPREFIX}/bin/GMXRC.bash"
set -u                             # 恢复 nounset
```

**规则**：第三方 `.bash` 脚本（GMXRC、conda activate 等）通常不兼容 `set -u`，应临时 `set +u` 而非逐个预初始化变量。

---

### #3 — gmx vs gmx_mpi + Slurm 资源声明（job 6583）

**现象**：`gmx: command not found`；改为 `gmx_mpi` 后 `-ntmpi 1` 报错 `Setting the total number of thread-MPI ranks is only supported with thread-MPI and target is not compatible with thread-MPI`。  
**根因**：此集群的 GROMACS 是 **MPI 编译**（命令 = `gmx_mpi`），不支持 thread-MPI 参数 `-ntmpi`。MPI rank 数由 Slurm `--ntasks` 控制。  
**修复**：

```bash
# ❌ thread-MPI（集群不存在此编译）
gmx mdrun -ntmpi 1 -ntomp 8

# ✅ MPI 编译：用 gmx_mpi，不加 -ntmpi，线程数用 -ntomp
#SBATCH --ntasks=1           # 单 MPI rank
#SBATCH --cpus-per-task=8    # OpenMP 线程数
gmx_mpi mdrun -ntomp 8 -gpu_id 0
```

**规则**：提交前 `gmx_mpi --version` 确认编译类型；MPI build 禁用 `-ntmpi`，rank 数走 Slurm `--ntasks`。

---

### #4 — 管道 SIGPIPE 触发 MPI_ABORT（job 6587）

**现象**：`gmx_mpi grompp ... | tail -5` → grompp 输出超过 5 行 → tail 关闭管道 → SIGPIPE → MPI 运行时将 SIGPIPE 视为致命错误 → `MPI_ABORT` → `set -o pipefail` 检测到管道失败 → 整个脚本退出。实际上 grompp 计算已成功完成，脚本在输出截断阶段死掉。  
**修复**：移除所有 `| tail` / `| head` / `| grep` 管道，让 `gmx_mpi` 直接输出到 stdout：

```bash
# ❌ SIGPIPE → MPI_ABORT → pipefail → 脚本退出
gmx_mpi grompp -f em.mdp -c input.gro -o em.tpr | tail -5

# ✅ 不对 MPI 程序的 stdout 加管道
gmx_mpi grompp -f em.mdp -c input.gro -o em.tpr
```

**规则**：**永远不要对 `gmx_mpi` 的输出加管道过滤**（`tail`/`head`/`grep`）。如需截取输出，重定向到文件后处理。

---

### #5 — index.ndx 原子编号粘连（jobs 6590/6591）

**现象**：index.ndx 用固定宽度 `f"{idx:6d}"`（6 位），体系有 ~140k 原子。当原子编号 >99999 时，相邻编号粘在一起（如 `100000100001`），GROMACS 解析为 `negative index -2`。  
**根因**：GRO 文件的固定宽度约定**不适用于** index.ndx。ndx 格式要求空白分隔，不是固定列宽。  
**修复**（`assemble_complex.py` `build_index()`）：

```python
# ❌ 固定宽度，>99999 原子时粘连
f.write(f"{idx:6d}")

# ✅ 空格前缀 + 变宽，保证任何大小的编号间有分隔
f.write(f" {idx}")
```

**规则**：index.ndx 写入用空格分隔变宽格式，不用固定宽度。对 >100k 原子的体系尤其关键。

---

### #6 — genion 组名必须匹配 topol.top moleculetype（jobs 6592/6593）

**现象**：`echo "Water" | gmx_mpi genion -n index.ndx ...` → `Fatal error: Group Water not found in index file`。  
**根因**：CHARMM-GUI 输出的 topol.top 中，水的 moleculetype 是 `TIP3`（不是 `Water` 也不是 `SOL`）。genion 的 `-n` 组名必须与 topol.top `[ molecules ]` 条目完全匹配。  
**修复**：

```bash
# ❌ "Water" 不是 CHARMM-GUI 体系的 moleculetype 名
echo "Water" | gmx_mpi genion -s genion.tpr -n index.ndx ...

# ✅ 匹配 topol.top 中的 moleculetype 名
echo "TIP3" | gmx_mpi genion -s genion.tpr -n index.ndx ...
```

同时修改 `assemble_complex.py` 中的 index.ndx 组名：`"Water"` → `"TIP3"`。

**规则**：genion 前先 `grep -A5 '\[ molecules \]' topol.top` 确认水的 moleculetype 名。CHARMM-GUI = `TIP3`，AMBER/通用 = `SOL`。

---

## 常见问题

**Q: `spack load` 报错找不到包？**  
登录节点：运行 `spack find gromacs` 确认已安装的版本和 hash。  
计算节点：**不要用 `spack load`**，见踩坑 #1。

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

### ADFR Suite / ADFR_BIN

> 新增: 2026-05-19, docking-repro Gpr3 F supplemental refresh
> 证据: `experiments/docking-repro/logs/install_adfr_suite_8850.log:4`、`:9`、`:11`; preflight 见 `experiments/docking-repro/logs/docking_preflight_8855.log:6`、`:15`。

当前 Slurm 用户目录配置:

```bash
export ADFR_BIN="/home/guest/opt/bin"
export PATH="$ADFR_BIN:$PATH"
```

项目部署后，环境文件位于:

```bash
/home/guest/drylab-docking/experiments/docking-repro/slurm/adfr_env.sh
```

安装入口为仓库脚本 `experiments/docking-repro/slurm/install_adfr_suite.sh`。登录节点只允许上传已校验 tarball、同步脚本和提交 `sbatch`；ADFR 解包安装、`prepare_receptor` 验证、批量 PDBQT preparation 都必须通过 Slurm 作业执行。

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

---

## 踩坑记录（Chimeric Phase C3，2026-04-18）

### #7 — RTX 5090 与 GROMACS 2025.2 不兼容

**现象**：job 6678/6679 在 step6.1 mdrun 启动时立即崩溃：

```
CUDA error #218 (cudaErrorInvalidPtx): a PTX JIT compilation failed.
GPU kernel (k_pruneonly) failed to launch.
```

**根因**：RTX 5090 = Blackwell 架构（sm_100）。node3 上安装的 GROMACS 2025.2-spack 二进制未包含 sm_100 PTX/cubin，运行时 JIT 编译失败。EM（CPU 阶段）正常完成，仅 mdrun GPU 加速核失败。

**修复**：改用 node1/node2 的 RTX 4090（Ada Lovelace，sm_89），已验证兼容。

```bash
# ❌ node3 RTX 5090（Blackwell sm_100，GROMACS 2025.2 不支持）
#SBATCH --nodelist=node3
#SBATCH --gres=gpu:rtx5090:1

# ✅ node1/2 RTX 4090（Ada Lovelace sm_89，正常运行）
#SBATCH --nodelist=node[1-2]
#SBATCH --gres=gpu:rtx4090:1
```

**规则**：在 node3 提交 GROMACS 作业前，先确认该二进制是否包含 Blackwell 支持。目前所有 GROMACS MD 作业改用 node1/node2。
