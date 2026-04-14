# REF-E：终端命令详解 + 硬件 101
> 遇到"这个命令是什么意思""为什么对接可以在 Mac 上跑"时查这里。
---
## 1. 终端命令详解
DO 轨用到的每个命令，一句话 + 示例。
### 目录导航
| 命令 | 含义 | 示例 |
|------|------|------|
| `pwd` | Print Working Directory——显示你当前所在的完整路径 | `pwd` → `/Users/you/drylab` |
| `cd 目录` | Change Directory——进入指定目录 | `cd src/modeling/docking-repro/` |
| `cd ..` | 回到上一级目录 | 从 `src/modeling/` 回到 `src/` |
| `cd ~` | 回到家目录（Mac: `/Users/你的用户名`；WSL: `/home/你的用户名`）| `cd ~` |
| `ls` | List——列出当前目录下的文件和子目录 | `ls` → `config.yaml  run_wt_singlestage.py  ...` |
| `ls *.pdbqt` | 只列出 `.pdbqt` 结尾的文件（`*` 是通配符，匹配任意字符）| `ls *.pdbqt` → `GprC_A0A437AGY2_tm.pdbqt` |
### 文件查看
| 命令 | 含义 | 示例 |
|------|------|------|
| `cat 文件名` | 一次显示文件全部内容（文件短时用）| `cat config.yaml` |
| `head -30 文件名` | 只显示前 30 行（文件长时用）| `head -30 ratio_channel_report.md` |
| `wc -l 文件名` | Word Count -lines——数文件有多少行 | `ls *.pdbqt \| wc -l` → `3`（统计 pdbqt 文件数量）|
### 目录操作
| 命令 | 含义 | 示例 |
|------|------|------|
| `mkdir -p 路径` | 创建目录，`-p` 表示自动创建中间目录 | `mkdir -p experiments/docking-repro/mutagenesis/af3_downloads/Gpr3_V138R` |
### 搜索
| 命令 | 含义 | 示例 |
|------|------|------|
| `grep 关键词 文件名` | 在文件中搜索包含关键词的行 | `grep "V138R" mutagenesis_results.json` |
### 环境管理
| 命令 | 含义 | 示例 |
|------|------|------|
| `conda activate docking` | 激活名为 `docking` 的 Python 环境 | 每次打开终端跑脚本前必须先执行 |
| `conda deactivate` | 退出当前环境 | 回到 base 环境 |
| `which python` | 显示当前用的是哪个 Python | 确认指向 conda 路径而非系统 Python |
### 管道符 `|`
命令之间用 `|` 连接，前一个命令的输出会变成后一个命令的输入：
```bash
ls experiments/docking-repro/prepared/receptors/*.pdbqt | wc -l
```
含义：先列出所有 `.pdbqt` 文件（`ls`），然后数有多少行（`wc -l`）。结果 = 文件数量。
---
## 2. 硬件 101
### 四个核心概念
| 组件 | 类比 | 做什么 |
|------|------|--------|
| **CPU**（处理器）| 厨师的双手 | 通用计算，一次做几件事（核心数 = 手数）|
| **GPU**（显卡）| 一千个实习生 | 每人只会一种简单操作，但同时做 → 大规模并行 |
| **RAM**（内存）| 案板大小 | 正在处理的数据必须放案板上；不够大就得来回搬 → 慢 |
| **存储**（硬盘/SSD）| 冰箱 | 长期存放数据；比案板大但取东西更慢 |
### 对接 vs MD：为什么对接可以在 Mac 上跑，MD 需要服务器
**对接（Vina）吃 CPU 不吃 GPU**。Vina 的搜索算法是蒙特卡洛 + 局部优化，跑在 CPU 上。一个 Vina 进程占 1 个核心，GPU 完全闲置。所以你的 MacBook 就能跑——每次 3-10 分钟。
**MD（GROMACS）必须 GPU**。分子动力学每一步要计算所有原子间的力 → 更新位置 → 重复几百万次。这种"大量重复简单计算"正好是 GPU 的优势场景。没有 GPU，50 ns 的 MD 可能从 1 天变成 1 个月。
**一句话**：docking 对硬件不挑，MD 必须有 GPU。
### 本地 vs 服务器的任务边界
| 在自己电脑上做 | 在服务器上做 |
|---------------|------------|
| PyMOL 可视化 | 完整突变体扫描（32+90 条）|
| 单次学习用对接 | 饱和扫描批量跑 |
| ProLIF 分析 | MD 模拟 |
| 写代码、读文档 | 长时间批量计算 |
**判断标准**：任务超过 30 分钟或需要 GPU → 放服务器。
