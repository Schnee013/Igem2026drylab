# AutoDL 执行顺序

本文件是当前本地 agent 的执行入口。工作单以本目录 WORK_ORDER.json 为准；bundle/ 为冻结材料快照，部署时使用独立工作副本并记录与快照的差异。旧方法脚本用于核对物理参数，不直接启动旧服务器任务。当前范围回 WORK_ORDER；下面的检查通过后，执行 agent可以自主启动已授权的六条 rep1，不需逐条再问权限。

## 1. 接管与环境

先检查自己能否实际使用 SSH/SFTP 和长期执行；随后核对实例、进程、磁盘挂载和空间、GPU UUID/型号/驱动、cgroup CPU/内存配额及其他任务。动作前 15 分钟内刷新现场证据。曾实测的是 RTX 5090 32607 MiB、16 核配额、90 GiB 内存、50 GB 数据盘；这不是当前资源保证。数据目录使用 `/root/autodl-tmp/gpr2-twf154-dots-20261006/`，先核实该路径确实在数据盘。软件/通用脚本放系统盘，不更改宿主驱动。

优先核验 `/opt/drylab/gromacs-2025.4/bin/gmx_mpi` 与 `/usr/local/bin/gmx`；具体锁定、链接库和历史 sm_120 证据见 compute/environment 与 context/environment_evidence。A 是 2025.4 external MPI + OpenMP / CUDA runtime 12.9 / mixed precision；一个任务一个 rank，不传 `-ntmpi`。`nvidia-smi` 的 CUDA 版本仅代表驱动能力。当前镜像 ID 与保存状态未知，不能从环境目录推断镜像已保存。

入口缺失才安装，不覆盖现有 prefix；安装脚本、65 包显式锁都在包中。例如有原 conda 时：

```bash
/root/miniconda3/bin/python compute/environment/install_environment.py \
  --lock compute/environment/a-runtime-explicit.txt \
  --prefix /opt/drylab/gromacs-2025.4 \
  --cache /root/autodl-tmp/drylab-install-cache
```

安装后实际核验版本、动态库、sm_120 代码与真实 TPR；自行建立默认入口并锁包，不能只写成功标记。无需安装本机 macOS PyRosetta 环境：两个候选坐标已带入。辅助环境需要 Python 3、NumPy；重新做配体化学核对时用 RDKit。固定新安装版本并留记录。B 未完成实测，不为追新版本反复安装。

## 2. 固定输入与路径

先运行 verify_bundle。保留原包只读；每组在独立 `runs/<case>/rep1/` 中工作。将该组 prepared 或 rebuild_support 中拓扑复制到工作目录；力场复制为工作目录 `ff/`，仅把第一条 forcefield include 改为 `ff/forcefield.itp`，记录新旧哈希。不得修改受体/配体/力场数值来“提速”。

N84V–ascr18 的 zero_start_100ns 是生产从零起点：不带 E2 生产进度 CPT，不抵扣任何旧 ns。它的 TPR 已内嵌完整体系，可以独立短跑；正式采用前仍需结构用途与环境数值复核。若重新 grompp，从该目录 npt05.gro/cpt 与原 production.mdp 重建；核对 tinit/step，生产计时从 0 到 100000 ps。

另三组已有 prepared/hold.gro、hold.cpt、hold.tpr 与 ionized.gro/selected_em.gro。确认 GRO/TPR/CPT 的体系、原子顺序及预热末态时间匹配；这是 125 ps 预热，不是生产前平衡完成。对应目录的 input_contract.json 用于本组检查，旧绝对路径合同仅在 evidence 内供溯源。

## 3. 两组新 lid 的正式准备

先比较 candidate 与自己的 parent_docking_frame：全长序列、固定区和 pose 不变；检查 lid 两端、二硫键、主链构象、接触、开放盖子关系和共价环。复核三维关系及能量后，写清接受该几何作为探索起点的依据与限制；不能用一张无碰撞图代替验收。

使用该组合 forcefield 的残基模板，在候选自身 docking 坐标系做 pdb2gmx，按原模型使用中性 delta 质子化 HIS（HSD）、原 N/C 端处理、99–173 二硫键；记录实际交互菜单和选择，不盲用旧脚本中的菜单数字。得到本候选的 protein.gro 和含蛋白 atoms/bonds 的 protein.top/ITP。逐项对照原 PROA：原子名、类型、质量、电荷、键连接。pdb2gmx 补氢不能暗改新候选重原子；末端氧的常规处理变化显式记录。

可用以下工具恢复到本组原膜坐标系：

```bash
python3 compute/scripts/assemble_new_lid_dry.py \
  --case-dir compute/cases/实际新lid组合ID \
  --protein-gro /绝对路径/protein.gro \
  --protein-top /绝对路径/实际蛋白拓扑文件 \
  --output /新建的工作目录
```

工具校验拓扑身份，把同一刚体变换用于本候选，保留原组配体及 POPC 坐标；若出现新 lid/POPC 重叠会停止，不自行删除脂质。该支持路线沿用的是膜 slab 和原组配体，不是旧蛋白。若膜容纳不下，记录问题再做同方法的膜打包审查；不能换 receptor 或 pose、减少体系规模来绕过。

然后按原方法重新溶剂化、0.15 M POT/CLA 加中和离子，创建 System/SOLU/MEMB/SOLV 索引、最小化、50 ps 升温和 75 ps 恒温。MDP 与 twf154_preheat_support.py 已带入；原完整操作顺序在 context/reference_scripts/run_twf154_preheat_case.sh，需按本工作目录改写实际脚本并留档。临时带净电荷的 genion 前 grompp 只能在 helper 确认唯一警告就是净电荷后接受一次；中和后的最终 grompp 必须无 warning，不用全局 maxwarn。

EM 要求原体系 Fmax≤1000 kJ mol⁻¹ nm⁻¹、有限坐标、正确水几何/手性/二硫键及无严重异常键。失败则分析，不自动强加新生产约束或跳过。新 prepared 参考必须用新 ionized.gro 和新 input_contract，不得拼旧预热数据。

## 4. NPT 与无约束准备

compute/mdp 含原生产流程的精确设置：NPT 125+500+500+500 ps 逐级减弱约束，随后 1000 ps 无位置/二面角约束准备。起始时间为 125 ps；当前 MDP 已分别写好。每阶段从上阶段 GRO/CPT 编译，带约束阶段使用同一 start.gro 作为 -r 参考；前几阶段保留原 lid 不加位置约束的规则。

每个工作目录保存 ionized.gro、input_contract.json、原子序正确的 index/toppar/ff。用本工作目录实际中和后的 topology 生成 em.processed.top；旧缓存不代替实际展开拓扑。之后使用：

```bash
python3 compute/scripts/check_twf154_snapshot.py \
  /绝对路径/体系工作目录 /绝对路径/阶段末态.gro \
  compute/configs/ligand_geometry_contract.json /绝对路径/阶段结构检查.json \
  --allow-box-change
```

检查每阶段日志、终点、温控组、势能/密度/盒面积/Box-Z，所有值有限。原流程最后 500 ps 的前后半窗口密度、面积、Box-Z 均变化<2%，作为准备期漂移初筛；这不是热力学或结合收敛证明。不满足时最多四次额外 1 ns 准备，并正确推进 tinit，仍不稳定则停该组检查。

## 5. 正确性、有限调优与生产门禁

已有 CPU/GPU 单点势能差未完全解释，最终差分见 context/cpu_gpu_consistency.json：不能只因力相近或未报 LINCS 就宣布关闭。固定坐标/拓扑/邻居表及实际 PME 参数，在多个帧比较势能分项和力；先复核已验证的 E2 式 offload 与 GPU update 配置。必要诊断在隔离目录，禁止将其额外力输出/步数设置用于生产。

单任务串行、8 线程为实測基线；CMAP 和邻居搜索仍走 CPU。只做有限线程/邻居表/双 worker 对照，最多 60 分钟性能调优；完整矩阵见 context/throughput_plan_snapshot.md。MPS 并发尚未实测，采用前须有共同计时窗口、两次稳定复测、正确性和检查点续跑证据，总吞吐改善超过波动才采用。GPU 利用率不作为完成量或性能指标。新 lid 必须用自己的新 TPR 复测。

生产 MDP：2 fs，50,000,000 步，原完整膜/水/离子；h-bonds/LINCS order 4/iter 2；303.15 K v-rescale、半各向同性 C-rescale 1 bar；XTC/日志 10 ps，EDR 1 ps。不改力场、删 CMAP、增加生产约束、加大时间步或降输出频率。

每条生产前写 production_gate.json：case_id、replicate=1、production_ns=100、tpr_sha256、15 分钟内 live_verified_at，以及 checks 中 source_identity、structure_purpose、preparation、numerical_compatibility、restart_test、resources、storage_and_recovery 的布尔结果；每项附实际证据路径和 SHA256。未通过不得写 true。先验证新起点短跑与 CPT 续跑，再放行生产。用户已授权生产范围，不需另一次形式许可；改变科学起点/重复数/长度或额外付费资源仍要向用户明确提出。

## 6. 执行、分段与回收

在独立 tmux/nohup 会话运行工具；SSH 断开不应杀掉 supervisor/mdrun。例如，实际路径与门禁准备好后：

```bash
python3 compute/scripts/run_stage.py \
  --case 实际case_id --stage production --workdir /绝对路径/该组rep1 \
  --tpr /绝对路径/该组production.tpr --prefix 带case和rep1的前缀 \
  --threads 8 --offload gpu --maxh 1 --expected-end-ps 100000 \
  --gate /绝对路径/production_gate.json
```

启动配置必须以本机通过的配置为准；准备阶段可选 compat，EM 用 cpu。工具不使用 -ntmpi、不覆盖已有运行。正常分段后，核对实际 GROMACS CPT 的 step/time、身份与输出，刷新现场检查，再加 `--cpi /绝对路径/最新有效检查点.cpt` 续跑；工具强制 -noappend，保留旧分段。不要把绝对终点误当成 -nsteps 的增量，本工具由原 100 ns TPR 控制终点。

正常段结束不等于 100 ns 完成。最终逐组核对 TPR 终点、CPT step/time、XTC/EDR 终点、所有分段覆盖/连续性、原子数、日志正常结束与 issue scan；分段不能当作独立重复。gmx check/dump/energy 均使用兼容环境，将完整输出存日志后再解析。最终生成 completion.json 和输出 SHA256 清单，给出实际推进量、有效 ns/day、耗时与费用。

每 100 ns 的历史 XTC 估计约 5.45 GB，六条约 33 GB；准备/缓存另计。保持至少下一运行阶段与回收所需余量，逐组或逐闭合分段回收到 AutoDL 之外并核验 SHA256。不能把数据盘或系统盘镜像当成唯一备份，不能把传输耗时藏在成本里。没有可持久的接收位置时，先向用户确认接收方式再启动将耗尽磁盘的队列。

验收通过且外部备份哈希一致后才可清理本任务明确不再需要的重复产物；不得删唯一轨迹/检查点。实例按用户约定不关机，完成后停止本任务进程并提醒继续计费。付费扩容或新租实例需用户另行授权。
