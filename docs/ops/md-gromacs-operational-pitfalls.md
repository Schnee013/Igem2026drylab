# GROMACS / MD 操作 guardrails（服务器中立）

> 整理日期：2026-05-28
> 适用范围：drylab MD / GROMACS 任务的可复用操作 guardrails。
> 本文是任何 drylab MD / GROMACS 任务的必读前置。当前服务器入口、站点矩阵和历史计算路线只保留为指针，不在本文复述。

## 使用规则

- 执行、分析或解释任何 drylab MD / GROMACS 任务前必须先读本文。
- 新服务器或远程计算任务还要读取当前服务器手册，确认个人目录、资源上限、tmux、备份和凭据边界。
- 服务器路线、环境 pin、历史 Slurm 细节和站点 gate 从 `environments/`、`docs/ops/nkuliulab-e2-cloud-server.md`、`docs/ops/archives/slurm-md-server.md` 或当前 gate scripts 读取。
- 每次重启、续跑、改硬件或改二进制前，先读当前脚本、`.log` / `.err`、`.mdp`、`.tpr`、`.top`、`.ndx` 和真实输出文件；不要只凭 memory 或文件存在判断成功。

## 1. GROMACS 二进制、版本和环境

- 先确认实际命令和编译类型：`gmx --version` 或 `gmx_mpi --version`。MPI build 不接受 thread-MPI 专用参数；thread-MPI / MPI / GPU support 必须按当前服务器实测结果写入脚本。
- 严格 shell 模式下，第三方环境脚本可能不兼容 `set -u`。需要 source `GMXRC.bash`、conda activate 等脚本时，优先使用局部 `set +u` / source / 恢复 `set -u`，不要逐个猜测未初始化变量。
- 不要把 MPI/GROMACS 命令 stdout 直接接到 `tail`、`head`、`grep` 这类可能提前关闭管道的过滤器；需要截取输出时先重定向到日志，再对日志做文本处理。
- `.tpr`、`.cpt`、`.edr`、`.trr`、`.xtc` 等二进制输出默认用该 run 记录的 GROMACS 环境处理；换环境处理必须有单独兼容性验证。

## 2. topology / index / solvation

- 写 `index.ndx` 时用空白分隔的变宽整数，不能用 GRO 固定列宽思路。大体系原子编号超过 99999 后，固定宽度会把相邻编号粘在一起，导致 GROMACS 解析出非法 index。
- `genion` 选择的 solvent group 必须匹配当前 `topol.top` 的 `[ molecules ]` / moleculetype 名称。CHARMM-GUI 旧体系是 `TIP3`，不是通用的 `Water`；其他力场或体系要现场检查，不要硬编码。
- 任何自动生成的 `.ndx`、`.top`、`.itp` 修复都要回到实际 `grompp` / `genion` 日志验证，不能只看脚本 diff。

## 3. production trajectory 处理

- 先确认 production `.mdp` 的 `compressed-x-grps` 和 XTC 实际原子集合；`.tpr`、输出组和 XTC atom count 必须匹配。
- protein-only XTC 的默认处理路线是：兼容版本 GROMACS、protein-only 输出组、`-pbc nojump`、center protein、backbone fit。
- PBC 修正后的文件要用结构数量、原子数量、RMSD/COM sanity plot 或同等低成本检查验证，再进入正式指标解释。
- production 或 benchmark 轨迹具备进入正式指标分析的证据后，先生成 chctrl-compatible processed inputs：`processed/repN/protein_ref.pdb` 和 `processed/repN/prod_protein.xtc`。
- 正式分析默认复用 `experiments/md-simulation/analysis/chctrl/` 七个 driver family：`analyze_convergence.py`、`analyze_selection_rmsd.py`、`analyze_hbond.py`、`analyze_com_distance.py`、`analyze_rmsf.py`、`analyze_bsa.py`、`analyze_contacts.py`。运行入口是 `CHIMERIC_MD_CONFIG=<system config>` + replicate 编号选择器 `CHIMERIC_MD_REPS='1,2,3'`；不设时默认 rep1/rep2/rep3，单 rep 用 `CHIMERIC_MD_REPS=1`。该变量不是 replicate 数量，且不得重复编号。
- 新体系只新增或调整 system config 和必要语义解释，例如 selections、readout clusters、receptor-ligand 语义；`analyze_selection_rmsd.py` 可按 config 承载 alpha5/eCT iRMSD 或 ligand/readout selection RMSD，结果落在 `results/<system>/analysis/`。
- 只有审查七个 driver 后证明存在真实 metric gap，且用户明确同意时，才允许新增共享 driver。禁止默认写 per-system analyzer、`metric_mapping.md`、`postprocess_and_sync_after_completion.sh` 等临时实体。

## 4. 多体系 / 多 replicate 运行卫生

- 每个 system / replicate 必须有独立工作目录、脚本、日志和输出前缀。不同 replicate 共享 `Command` / `WorkDir` 会产生覆盖风险，即使调度系统临时限制并发也不能依赖这个偶然保护。
- 作业名、tmux 窗口名、日志名和输出目录都应带 system + replicate 标识，便于他人区分真实重复提交和合法并行任务。
- 调度器写法、变量插值和资源参数不可跨服务器照搬；必须按当前脚本、真实 scheduler 状态和 gate 日志验证。

## 5. GPU / 二进制兼容

- GPU 启动即崩溃时，先按二进制 / CUDA target / driver / GPU 架构兼容问题排查，不要把它解释成科学 MD 失败。
- `cudaErrorInvalidPtx` 这类错误的 durable rule 是：检查当前 `.err`、GROMACS build、CUDA target 和 GPU 架构是否匹配；放行依据必须来自当前环境的 smoke/benchmark。

## 6. 追溯来源

- 旧 Slurm / GROMACS 环境坑：`docs/ops/archives/slurm-md-server.md`
- 当前统一 rerun 站点矩阵：`environments/md-production-sites.md`
- 当前 E2 GROMACS 环境证据：`environments/e2-md-gromacs.md`
- production job-name 冲突：`docs/logs/2026-04-20.md`
- replicate `Command` / `WorkDir` 覆盖风险：`docs/logs/2026-04-22.md`
- chctrl trajectory / PBC / GROMACS version 处理坑：`docs/logs/2026-04-28.md`
