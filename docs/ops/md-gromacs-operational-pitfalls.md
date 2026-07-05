# GROMACS / MD 操作踩坑索引（服务器中立）

> 整理日期：2026-05-28
> 适用范围：drylab MD / GROMACS 任务的可复用操作 guardrails。
> 当前默认服务器入口仍是 `docs/ops/nkuliulab-e2-cloud-server.md`；本文不替代 E2 手册。2026-05-30 起，chimeric MD 可把旧 Slurm RTX 5090 作为 validated secondary candidate，但必须走新的 site matrix 和 gate scripts，不复活旧 Slurm production provenance。

## 使用规则

- 新服务器或远程计算任务默认先读 `docs/ops/nkuliulab-e2-cloud-server.md`，确认个人目录、资源上限、tmux、备份和凭据边界。
- 本文只保留服务器中立的 GROMACS / MD 操作坑；旧 Slurm 的历史 `sbatch`、`sacct`、节点名、旧路径和旧硬件选择只在 `docs/ops/archives/slurm-md-server.md` 中追溯。当前 chimeric rerun 如使用 Slurm，只能使用 `environments/md-production-sites.md` 和 `experiments/md-simulation/scripts/slurm_*`。
- 每次重启、续跑、改硬件或改二进制前，先读当前脚本、`.log` / `.err`、`.mdp`、`.tpr`、`.top`、`.ndx` 和真实输出文件；不要只凭 memory 或文件存在判断成功。

## 1. GROMACS 二进制、版本和环境

- 先确认实际命令和编译类型：`gmx --version` 或 `gmx_mpi --version`。MPI build 不接受 thread-MPI 专用参数；thread-MPI / MPI / GPU support 必须按当前服务器实测结果写入脚本。
- 严格 shell 模式下，第三方环境脚本可能不兼容 `set -u`。需要 source `GMXRC.bash`、conda activate 等脚本时，优先使用局部 `set +u` / source / 恢复 `set -u`，不要逐个猜测未初始化变量。
- 不要把 MPI/GROMACS 命令 stdout 直接接到 `tail`、`head`、`grep` 这类可能提前关闭管道的过滤器；需要截取输出时先重定向到日志，再对日志做文本处理。
- `.tpr` 和 trajectory 处理要匹配 GROMACS 版本。旧记录中，本地 GROMACS 2024.5 无法读取远端 GROMACS 2025.2 生成的 production `prod.tpr`；正式处理应使用同版本或兼容版本验证。
- 远程站点产出的 GROMACS binary outputs 必须使用该站点/该 run 记录的 GROMACS 环境处理，除非另有单独兼容性验证文件。E2 产出的 `.tpr`、`.cpt`、`.edr`、`.trr`、`.xtc` 和用于证据的 `gmx` 预处理输出，权威规则见 `environments/e2-md-gromacs.md`；本地 `chimeric*`、Homebrew 或其他本地 `gmx` 环境不能作为 E2 输出的证据生成环境。

## 2. topology / index / solvation

- 写 `index.ndx` 时用空白分隔的变宽整数，不能用 GRO 固定列宽思路。大体系原子编号超过 99999 后，固定宽度会把相邻编号粘在一起，导致 GROMACS 解析出非法 index。
- `genion` 选择的 solvent group 必须匹配当前 `topol.top` 的 `[ molecules ]` / moleculetype 名称。CHARMM-GUI 旧体系是 `TIP3`，不是通用的 `Water`；其他力场或体系要现场检查，不要硬编码。
- 任何自动生成的 `.ndx`、`.top`、`.itp` 修复都要回到实际 `grompp` / `genion` 日志验证，不能只看脚本 diff。

## 3. production trajectory 处理

- 先确认 production `.mdp` 的 `compressed-x-grps` 和 XTC 实际原子集合。旧 chctrl production 的 `prod.xtc` 是 protein-only，不是 full-system trajectory；用 `System` 作为输出组会产生 `.tpr` / `.xtc` 原子数不匹配。
- protein-only XTC 的历史有效路线是：兼容版本 GROMACS、protein-only 输出组、`-pbc nojump`、center protein、backbone fit。旧记录中直接对 protein-only XTC 做 `-pbc mol` 产生了人工大分离，不可作为科学判断依据。
- PBC 修正后的文件要用结构数量、原子数量、RMSD/COM sanity plot 或同等低成本检查验证，再进入正式指标解释。

## 4. 多体系 / 多 replicate 运行卫生

- 每个 system / replicate 必须有独立工作目录、脚本、日志和输出前缀。不同 replicate 共享 `Command` / `WorkDir` 会产生覆盖风险，即使调度系统临时限制并发也不能依赖这个偶然保护。
- 作业名、tmux 窗口名、日志名和输出目录都应带 system + replicate 标识，便于他人区分真实重复提交和合法并行任务。
- 调度器相关写法不可跨服务器照搬。旧 Slurm 的 `#SBATCH --job-name=${VAR}` 不会做运行时变量插值；E2 或新的 Slurm secondary route 都必须按当前脚本和真实 scheduler 状态重新验证。

## 5. GPU / 二进制兼容

- GPU 启动即崩溃时，先按二进制 / CUDA target / driver / GPU 架构兼容问题排查，不要把它解释成科学 MD 失败。
- `cudaErrorInvalidPtx` 这类错误的 durable rule 是：检查当前 `.err`、GROMACS build、CUDA target 和 GPU 架构是否匹配。旧集群的节点选择和 GPU 型号结论只适用于旧环境；当前 Slurm RTX 5090 必须用 GROMACS 2025.4 MPI-CUDA pin 重新 smoke/benchmark，不能靠旧 2025.2-spack 结论放行。

## 6. 追溯来源

- 旧 Slurm / GROMACS 环境坑：`docs/ops/archives/slurm-md-server.md`
- 当前统一 rerun 站点矩阵：`environments/md-production-sites.md`
- production job-name 冲突：`docs/logs/2026-04-20.md`
- replicate `Command` / `WorkDir` 覆盖风险：`docs/logs/2026-04-22.md`
- chctrl trajectory / PBC / GROMACS version 处理坑：`docs/logs/2026-04-28.md`
