# NKULiulab E2 共享云服务器使用规范

> 适用范围: 南开大学刘杏忠课题组已购基因学苑 E2 共享云服务器
> 采购周期: 2026-05-20 至 2027-05-19
> 整理日期: 2026-05-27
> 来源: `docs/ops/archives/sources/NKULiulab_CloudServer_Notice.pdf` 与 `docs/ops/archives/sources/基因学苑生物云平台使用说明（2026版）.md`

本文件只整理课题组实际使用入口、目录规范、资源约束和常见操作。密码、API key、个人 token 不写入本仓库；首次登录密码以邮件或管理员单独发送的信息为准。

**项目内强制规则**：新服务器/远程计算任务默认使用本 E2 服务器；登录、传输、远程 IDE、软件环境、长任务或 AI CLI 上机前必须先阅读本文。Slurm、HBU SGE 和 Windows 7500F 操作指南只作为历史归档参考，不作为默认入口。例外：2026-05-30 起，chimeric MD 统一 rerun 允许旧 Slurm RTX 5090 作为 validated secondary candidate，但必须走 `environments/md-production-sites.md` 和新的 `experiments/md-simulation/scripts/slurm_*` gate scripts。

GROMACS / MD 任务在确认服务器入口后，另读 `docs/ops/md-gromacs-operational-pitfalls.md`；该索引只保留服务器中立的 MD 操作坑。旧 Slurm 节点和调度命令不得照搬到 E2；当前 Slurm secondary route 也不得复用旧 Slurm 2025.2-spack production 脚本或结果 provenance。

## 服务器信息

| 项目 | 值 |
|---|---|
| 平台 | 基因学苑生物云平台 |
| 型号 | E2 共享云 |
| 主机 | `e2.tongyuangene.com` |
| SSH/SFTP 端口 | `40042` |
| 用户名 | `dengwei` |
| CPU | 256 线程 |
| 内存 | 2 TB |
| GPU | NVIDIA A100 80G |
| 磁盘 | 5 TB，共享 |
| 网络 | 100M 国际专线，可访问 GitHub、Docker Hub、NCBI、zenodo.org 等 |

2026-05-27 免密登录后实测:

| 项目 | 实测值 |
|---|---|
| 主机名 | `almalinux10` |
| 系统 | AlmaLinux 10.0 |
| Kernel | `6.12.0-124.27.1.el10_1.x86_64` |
| 当前用户 | `dengwei`，组 `bio` |
| HOME | `/ifs1/User/dengwei` |
| CPU | AMD EPYC 7763，2 sockets，256 CPUs |
| 内存 | 约 1.8 TiB 可见内存 |
| GPU | NVIDIA A100-SXM4-80GB，81920 MiB，driver `590.48.01` |
| `/ifs1` 底层挂载 | 50T，总用量约 23% |
| `dengwei` quota | 5000G quota，5072G hard limit |

注意区分底层 `/ifs1` 挂载容量和当前用户 quota；日常可用空间按 `quota -uvs` 为准。

## 快速登录

命令行登录:

```bash
ssh -p 40042 dengwei@e2.tongyuangene.com
```

推荐在本机 `~/.ssh/config` 增加别名，避免每次手打端口，也方便 Codex、VS Code、Positron 和 `rsync` 复用同一个入口:

```sshconfig
Host nkuliulab-e2
    HostName e2.tongyuangene.com
    User dengwei
    Port 40042
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
```

之后直接登录:

```bash
ssh nkuliulab-e2
```

如果本机还没有 SSH key，先生成:

```bash
ssh-keygen -t ed25519 -C "nkuliulab-e2"
```

如果本机已有 `~/.ssh/id_ed25519.pub`，不要重复生成；直接把公钥上传到服务器。首次上传需要输入一次服务器密码:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p 40042 dengwei@e2.tongyuangene.com
```

如果 `ssh-copy-id` 不可用，用手动追加方式:

```bash
cat ~/.ssh/id_ed25519.pub | ssh -p 40042 dengwei@e2.tongyuangene.com 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

验证免密是否生效:

```bash
ssh -o BatchMode=yes nkuliulab-e2 'hostname && whoami'
```

如果出现 `Permission denied`，说明公钥还没有装到服务器端 `~/.ssh/authorized_keys`，需要先执行一次上面的上传公钥命令。

不要把私钥、密码、API key 放入 drylab 仓库或服务器共享目录的明文文件。

## Codex 常用远程操作边界

Codex 以后优先使用 SSH config 别名操作服务器:

```bash
ssh nkuliulab-e2
ssh nkuliulab-e2 'cd /ifs1/User/dengwei/<your_pinyin> && pwd && hostname'
rsync -avP ./scripts/ nkuliulab-e2:/ifs1/User/dengwei/<your_pinyin>/scripts/
```

使用 Codex 或其他 AI CLI 在服务器上执行命令时，仍按共享服务器规则处理:

- 先进入个人拼音目录，不在 `/ifs1/User/dengwei/` 顶层直接运行分析。
- 启动长任务前先开 `tmux`，并明确线程数、输出目录和日志路径。
- 不让 AI 自动删除公共目录、他人目录、数据库、公共软件或未确认的大目录。
- 不让 AI 自动写入、提交或同步密码、API key、token、私钥和含凭据的配置。
- 资源重的分析命令必须显式限制线程数，默认不要超过 16-32 线程；确需更大资源时仍不得超过单人 128 线程边界。

## 首次登录必须做

课题组工作目录为:

```text
/ifs1/User/dengwei/
```

首次登录后立即创建以自己姓名拼音命名的个人目录，并在其中分出常用子目录。当前本项目个人目录命名为 `igem`；后续 Codex、VS Code、RStudio、tmux 任务都应进入这个个人目录操作:

```bash
cd /ifs1/User/dengwei
mkdir -p igem/{data,scripts,results,logs,tmp}
cd /ifs1/User/dengwei/igem
pwd
```

使用规则:

- 自己的数据、脚本、结果只放在 `/ifs1/User/dengwei/igem/` 下。
- 不要把个人数据放到别人的目录或公共位置。
- 不要修改、移动、删除他人的文件、环境或软件安装。
- 由于当前课题组入口使用 `dengwei` 账号，个人拼音目录是组内操作边界；不要把它当作独立系统账号级别的权限隔离。

## 文件传输

命令行上传本地目录:

```bash
scp -P 40042 -r ./data dengwei@e2.tongyuangene.com:/ifs1/User/dengwei/<your_pinyin>/
```

命令行下载结果:

```bash
scp -P 40042 -r dengwei@e2.tongyuangene.com:/ifs1/User/dengwei/<your_pinyin>/results ./results_e2
```

使用 SFTP:

```bash
sftp -P 40042 dengwei@e2.tongyuangene.com
sftp> cd /ifs1/User/dengwei/<your_pinyin>
sftp> put -r data
sftp> get -r results
```

使用 `rsync` 断点/增量同步:

```bash
rsync -avP -e "ssh -p 40042" ./data/ dengwei@e2.tongyuangene.com:/ifs1/User/dengwei/<your_pinyin>/data/
rsync -avP -e "ssh -p 40042" dengwei@e2.tongyuangene.com:/ifs1/User/dengwei/<your_pinyin>/results/ ./results_e2/
```

图形工具:

- Windows 可用 Xshell + Xftp、Termius、MobaXterm、FileZilla。
- macOS 可用 Termius、Tabby、FileZilla；Termius 需从官网安装，App Store 版本可能没有文件传输能力。
- FileZilla 主机写 `sftp://e2.tongyuangene.com`，端口写 `40042`。

跨服务器或云服务器迁移:

- 优先在 `tmux` 中运行传输，避免 SSH 断开导致迁移中断。
- 可用 `sftp`、`scp` 或 `rsync`；大目录同步优先用 `rsync -avP`，如果两端 `rsync` 版本不兼容，再退回 `sftp`。
- 同一云平台内迁移时，可在源服务器用 `hostname -I` 查看内网地址，再用内网地址传输；具体内网连通性以当时服务器实际情况为准。
- VS Code 的第三方 SFTP 插件只适合小脚本、小配置同步，不适合大数据集或大量结果传输；大文件仍用 FileZilla、`rsync` 或命令行 SFTP。

## 资源使用规范

这是共享服务器，多人同时使用。单人不要长期占据全部资源。

硬性边界:

- 单人总线程数不超过 128，即总线程数的一半。
- 一次任务不要占满全部 CPU、内存或 GPU。
- 避免长时间占用大内存。
- 长任务必须放进 `tmux`、`nohup` 或类似不间断会话中；推荐优先使用 `tmux`。
- 定期清理临时文件，尤其是中间 FASTQ/BAM/SAM、临时索引、容器镜像、解压目录和失败任务残留。

常见线程参数:

```bash
# 常见软件
tool -t 16
tool --threads 16
tool -p 16
tool --process 16
```

提交或运行前先估算资源。共享云服务器没有 root 权限，也不能按独享服务器方式独占整机。

选型和升级经验:

- 共享云不提供 root 权限，也不能给组内每个人开独立系统账号；组内边界主要靠个人目录和操作纪律维护。
- 因共享服务器不能独占全部资源，官方建议选择配置时至少覆盖任务峰值需求的 2 倍以上。
- 购买后如资源不够可以升级，但共享云升级通常涉及数据迁移，应提前规划，避免频繁升级。

## Tmux 长任务模板

新建会话:

```bash
tmux new -s <task_name>
```

在 tmux 里运行任务。临时退出但保持任务运行:

```text
Ctrl-b d
```

查看会话:

```bash
tmux ls
```

重新进入:

```bash
tmux attach -t <task_name>
```

结束任务和会话时，在 tmux 内正常 `exit`，或确认任务已完成后:

```bash
tmux kill-session -t <task_name>
```

## 存储和备份

5 TB 磁盘是多人共享空间。本服务器主要用于运行数据分析，不是长期数据仓库。

必须遵守:

- 原始数据、未发表结果和关键分析产物必须在实验室本地服务器或其他受控位置另做备份。
- 分析完成后，把结果和必要中间文件下载回本地或实验室存储。
- 下载确认后，清理云服务器上的重复副本和临时文件。
- 不要把云服务器作为唯一副本。

查看空间:

```bash
quota -uvs
ncdu
```

如果 `ncdu` 不存在，可先用:

```bash
du -h --max-depth=1 /ifs1/User/dengwei/<your_pinyin> | sort -h
```

## 公共目录规范

课题组在 `/ifs1/User/dengwei/` 下设两个公共目录:

```text
/ifs1/User/dengwei/DB/
/ifs1/User/dengwei/biosoftware/
```

2026-05-27 实测这两个课题组公共目录尚未创建；首次需要使用公共数据库或公共软件区时，先创建目录，再按下面 README 规则登记。

向这两个目录添加公共数据库或软件时，必须在对应子目录下放 `README.md`，至少写清:

- 安装人
- 日期
- 版本
- 来源链接
- 安装方式
- 使用方法

没有 `README.md` 的公共安装视为未完成安装。不要修改或删除他人安装的内容。

## 软件和 Conda

平台采用公共 conda + 个人环境模式。

公共环境规则:

- 公共 base 和公共虚拟环境只读，只能使用，不能往里面安装软件。
- 公共环境常见路径包括 `/share/Software/miniforge3`、`/share/Software/miniforge3/envs/`。
- 官方通用手册也列出过 `/ifs1/Software/miniforge3`、`/ifs1/Software/miniforge3/envs/`；首次登录后以实际存在路径为准。

首次确认路径:

```bash
ls -ld /share/Software/miniforge3 /ifs1/Software/miniforge3 2>/dev/null
mamba env list
```

激活公共环境时用完整路径:

```bash
mamba activate /share/Software/miniforge3/envs/kraken2
```

如果实际路径是 `/ifs1/Software/miniforge3`，则相应改为:

```bash
mamba activate /ifs1/Software/miniforge3/envs/kraken2
```

采购通知列出的公共环境包括 R、busco、kraken2、prokka、qiime2、rnaseq 等。

个人软件规则:

- 需要安装自己的软件时，创建个人 conda 环境。
- 个人环境命名格式: `姓名_用途`，例如 `zhangsan_rnaseq`。
- 不再使用的个人环境及时删除。
- 不要向公共 base 或公共 env 安装包。
- 缺少软件时，优先在个人 conda/bioconda 环境安装；conda 难以解决或需要可重复封装时，再考虑 Apptainer。

示例:

```bash
conda create -n <name>_<purpose> -y python=3.11
conda activate <name>_<purpose>
```

如果使用管理员 conda 但希望把个人 env/cache 放到自己目录，可设置:

```bash
conda config --add envs_dirs ~/.conda/envs
conda config --add pkgs_dirs ~/.conda/pkgs
```

## R 和 RStudio 包管理

RStudio Server 使用管理员配置的 R 版本。网页端 RStudio 不一定能直接切换到个人安装的 R 版本；需要个人 R 或 Python 解释器时，优先使用 Positron/VS Code Remote SSH 或命令行。

R 包规则:

- 不要向公共 R 环境或公共 library 写入个人包。
- 网页端缺少 R 包时，优先安装到个人 R library；复杂 R 包可用个人 bioconda/conda 环境管理。
- 如需让 RStudio 识别特定 library，可在自己的 `~/.Rprofile` 中追加个人 library 路径；不要把公共环境路径误改成可写公共配置。
- 修改 `~/.Rprofile` 前先备份，避免影响后续 R/RStudio 启动。

## 数据库

平台共享数据库目录:

```text
/ifs1/Database/
```

已知常见数据库包括 nr、nt、swissprot、GTDB、kraken2、eggnog、humann、metaphlan、taxonomy 等。官方手册说明付费数据库无法提供。

课题组额外新增数据库应放在:

```text
/ifs1/User/dengwei/DB/
```

并按公共目录规范写 `README.md`。

## Docker、Apptainer 和网络

服务器有 100M 国际专线，可直接访问 GitHub、Docker Hub、NCBI、zenodo.org 等，通常无需配置 conda 镜像源。

可使用 Docker 或 Apptainer 管理复杂软件，但要注意:

- 镜像和容器会快速占用磁盘，用完及时清理。
- 镜像、sandbox、输出文件放在个人目录或明确的公共软件目录下。
- 公共目录中的容器化软件也必须写 `README.md`。

常用清理检查:

```bash
docker ps -a
docker images
docker rm <container_id>
docker rmi <image_id>
```

如果没有 Docker 权限，优先尝试 Apptainer:

```bash
apptainer pull tool.sif docker://biocontainers/blast:2.2.31
```

## AI 工具

平台可使用 Claude Code、Codex、Gemini CLI、Qwen Coder 等 AI 工具，但 API key 需要个人自己提供并承担对应费用。

安全规则:

- API key 不写入 Git 仓库。
- API key 不写入共享目录中的明文配置。
- 如需在服务器上配置，优先放在自己 home 下的私有 shell 配置或工具专用凭据文件，并确认不会被同步到仓库。

## Positron、VS Code 和 RStudio

Positron 或 VS Code Remote SSH 可直接使用:

```text
dengwei@e2.tongyuangene.com:40042
```

如果使用 SSH config，则连接 `nkuliulab-e2`。

远程开发规则:

- Positron 和 VS Code 适合编辑脚本、跑轻量交互、管理项目文件和查看日志。
- 长任务仍应在服务器 `tmux` 中运行，不依赖本地 IDE 窗口常开。
- VS Code Remote Development 插件走 SSH；第三方 SFTP 插件只能用于小文件同步，不负责大数据传输。
- 使用 Jupyter 或远程 Python/R kernel 时，解释器应来自个人环境或只读公共环境，不要污染公共 base。

RStudio Server:

- 官方手册说明网页端使用 `http://`，不要使用 `https://`。
- 网页端口与 SSH 端口不是同一个端口，具体地址以邮件或服务器欢迎界面给出的网页端为准。
- 登录账户密码与服务器 SSH 账户密码一致。

当前仅已知 SSH/SFTP 端口为 `40042`；未在本仓库记录或验证 RStudio 网页端口。

## 生信数据下载工具

官方手册给出 `iseq`、NCBI `datasets`、`lftp` 等下载示例。这些属于可选工具，不是课题组固定规范。使用时遵守:

- 在个人 conda 环境中安装下载工具。
- 下载目录放在个人拼音目录或明确的公共数据库子目录。
- 大型数据库或公共数据放入 `/ifs1/User/dengwei/DB/` 前必须写 `README.md`。
- 下载完成后校验文件，删除压缩包、中间缓存和失败残留。
- 不把服务器作为原始数据唯一副本。

## 审查覆盖和不纳入范围

本文件已覆盖采购通知和官方手册中与服务器实际使用直接相关的规范: 登录、免密 SSH、传输、个人目录、共享目录、资源上限、tmux、存储备份、公共软件、个人 conda、R/RStudio、数据库、Docker/Apptainer、AI 工具、远程开发、磁盘检查和常见故障。

未纳入正文的内容包括平台营销、购买流程、发票、历史统计、用户文章列表、截图式 GUI 教程和示例账号命令。这些内容不属于课题组服务器操作规范；如需查看，回到原始官方手册。

## 常见故障

### 登录不上

先排查四项:

- 网络是否可达。
- 主机是否写对: `e2.tongyuangene.com`。
- 端口是否写对: SSH/SFTP 用 `40042`。
- 用户名和密码是否正确，密码区分大小写。

如果本地网络、VPN 或端口限制可疑，可换手机热点测试网页端或 SSH 连接。不要把排障密码写进聊天记录、日志或仓库。

### SSH 连接一段时间后断开

本机 SSH config 里保留:

```sshconfig
ServerAliveInterval 30
```

长任务必须在 tmux/nohup/screen 中运行，避免断线导致任务中断。

### RStudio 网页端一直转圈

只处理自己的 RStudio 会话缓存。先 SSH 登录后执行:

```bash
pkill -9 rsession
rm -rf .local/share/rstudio/sessions/*
```

这会结束当前账号下的 RStudio session 并删除 session 缓存；执行前确认没有重要未保存对象只存在于 RStudio session 里。

### 传输速度慢

100 Mbps 理论上约 12.5 MB/s，实际速度会受本地上传带宽、运营商、无线网络、目标站点带宽影响。官方手册提到国内上传常见约 3-5 MB/s；如果明显低于预期，可改用有线网络、换网络环境或使用 `rsync -avP` 断点续传。
