# AutoDL Gpr3 R167Y + ASCR3 production rep1 资格验证与执行计划

> Date: 2026-07-17
>
> Scope: 为 AutoDL 环境资格验证、`Gpr3_R167Y + ASCR3` 200 ns
> production rep1、checkpoint/resume、同环境后处理、结果回收和站点决策提供
> repo-native 执行合同。
>
> Status: `Gpr3_R167Y + ASCR3` AutoDL attempt3 200 ns rep1、postprocess 和
> 七 driver 分析已完成；当前项目状态见 `docs/INDEX.md`。

## 0. 执行摘要与当前结论

### 0.1 当前 Gpr3 runnable status

执行前从以下当前权威入口校准 Gpr3 package 状态：

- 原始 gate：
  `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv`
- 详细派生视图：
  `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`

截至 2026-07-20，`Gpr3_R167Y + ASCR3` AutoDL attempt3 200 ns rep1 已完成；
`Gpr3_WT + ASCR3` E2 route 为 `BLOCKED_E2_GPU_BUSY`。

### 0.2 首选建议

1. 以已通过的 Gpr3 WT/R167Y local runnable-input gate 为冻结输入；传输前复核
   terminal status 与双臂 final manifest/checksum 身份。
2. AutoDL 首先只取得 `qualification candidate` 身份：完成 live preflight、
   persistent-storage 规则确认、E2 exact-pin dry-run、exact-pin environment
   validation、同一冻结 TPR 的 smoke/100 ps benchmark。
3. exact pin 和 qualification 通过后仍停在 production launch decision。若 Roy
   要正式 WT/R167Y matched comparison，优先把 `Gpr3_WT + ASCR3` 与
   `Gpr3_R167Y + ASCR3` 对应 replicate 放到同一套已接受的 AutoDL
   environment/site/command contract 下运行；或者两者都留在 E2。
4. 如果只先跑 R167Y，则该 run 首先只能记为 AutoDL
   qualification/exploratory evidence。它只有在后续 WT rep1 使用同一已接受的
   AutoDL build、GPU model、命令结构和 frozen protocol 补跑后，才可进入
   AutoDL-batch matched comparison；如果环境发生不可消除的漂移，R167Y 仍保持
   exploratory。
5. exact E2 pin 不可满足时不得自动退化到 `nompi_cuda`、其他 GROMACS 版本或系统
   GROMACS。停下，把“整个 matched pair 迁到一个独立 AutoDL batch”作为 fallback
   交 Roy 决定。

### 0.3 合法终态

执行阶段只有以下两类合法终态：

- 成功终态：`Gpr3_R167Y + ASCR3 production rep1 completed`；200 ns production
  正常终止，XTC/EDR 到 `200000 ps`，archive checksum 完成，并使用该 run 记录的
  AutoDL GROMACS 环境完成 GROMACS-side postprocess，产生
  `processed/rep1/protein_ref.pdb` 和 `processed/rep1/prod_protein.xtc`。
- 阻塞终态：输入、连接/持久化、环境、transfer、smoke、benchmark、launch、
  early-runtime、resume 或 completion gate 失败；保留完整证据，写
  `BLOCKED_<GATE>` terminal status 和 fallback 决策包，等待 Roy，不自行换环境或
  改路线。

技术成功不自动升级为科学 matched-comparison 成功。若只有 R167Y 在 AutoDL
完成，成功状态必须同时保留 `qualification/exploratory only` 科学边界。

## 1. 权威、范围与已核对证据

### 1.1 Repo authority

| 作用 | 当前权威 | 本计划采用方式 |
|---|---|---|
| 文档与状态路由 | `AGENTS.md` → `docs/DOCMAP.md` → `docs/INDEX.md` | INDEX 只作当前状态路由；本计划不把 AutoDL 写成已批准站点 |
| Gpr3 local runnable-input 原始状态 | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv` | 本地 gate 的规范写入权威 |
| Gpr3 package 详细状态 | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md` | 带 source/as_of/allowed_use/update_trigger 的派生视图 |
| Gpr3 输入顺序 | `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` | 每次执行前按原始 gate 和 package 视图校准前提 |
| E2 environment pin | `environments/e2-md-gromacs.md:7-19,28-44,56-77` | AutoDL exact-pin target 与 binary-output 规则 |
| 站点经验 | `environments/md-production-sites.md:7-34,47-61` | 只提取环境一致性、benchmark、completion 与 confounding 经验；不把历史 chimeric scope 当成 AutoDL 当前权威 |
| MD 操作 guardrail | `docs/ops/md-gromacs-operational-pitfalls.md` | 二进制、topology/index、GPU、replicate、postprocess 硬规则 |
| Payload/Git 边界 | `docs/ops/payload-tracking-policy.md` | canonical input/compact provenance 进 Git；runtime payload 外置 |
| E2 运维参考 | `docs/ops/nkuliulab-e2-cloud-server.md` | E2 共享资源、个人路径、传输、tmux 与备份边界 |

### 1.2 Gpr2 模板审查结论

以下脚本只提供控制结构：

- `e2_run_gpr2_r59c_ascr18_preproduction.sh:126-158,362-407`：
  run-root、防覆盖、GPU idle gate、tmux launch 与 terminal-status 结构可复用；
  `rsync --delete` 不可用于未知 AutoDL 目录。
- `e2_run_gpr2_r59c_ascr18_preproduction.sh:159-357`：
  assembly → genion → EM → step6.1-step6.6 → 100 ps → `gmx check` →
  issue scan → checksum 的顺序可复用。
- `e2_run_gpr2_r59c_ascr18_production.sh:213-372`：
  launch/resume 分支、防覆盖、active-process gate、GPU sampler、
  `-cpi ... -append`、normal-completion check 和 archive manifest 可复用。
- `e2_postprocess_gpr2_r59c_ascr18_rep1.sh:15-158`：
  只有 production terminal status 完成后才 postprocess、使用 run-recorded
  GROMACS、拒绝覆盖 processed outputs、生成 processed checksums 的控制结构可复用。

以下内容禁止复用为 Gpr3 合同：

- `MAXWARN=11` 和 duplicate-type-9 的 11 条 warning contract；
- `REMOVE_POPC=410`；
- `130638` atoms、`200 POPC / 88 POT / 100 CLA / 32404 TIP3`；
- `SOLU=6438`、`SOLU_BACKBONE=1623`；
- ASCR18 的 54 atoms、include 名称、molecule name 和 selections。

`assemble_complex.py` 当前也不能直接称为 Gpr3-safe：

- `modify_topol()` 写死 `cgenff_ASCR18.itp`、`ASCR18.itp`、
  `posre_ASCR18.itp` 和 `ASCR18 1`；
- 输出标题写死 ASCR18；
- 没有覆盖不同 ligand/topology/index contract 的测试；
- index 的变宽整数写法和 `TIP3` group 修复可保留，但 molecule/include/expected
  counts 必须参数化。

### 1.3 执行前状态校准

执行者先核对 local gate `terminal_status.tsv`、WT/R167Y final manifests 和
system-local `PACKAGE_STATUS.md`。三者的 checksum 身份与 source/as_of 边界一致
后，本计划才可消费 `WAITING_AUTHORIZATION` 作为起始状态；本计划中的执行步骤
不构成并行状态写入点。

## 2. 科学设计：资格测试不等于 matched production

### 2.1 为什么不以逐帧一致为环境 PASS

即使输入、软件版本和硬件表面相同，floating-point 加法顺序、MPI reduction、动态
负载均衡、FFTW runtime choice 与 GPU reduction 都会改变最低位；MD 是 chaotic
system，轨迹会快速分叉。GROMACS 官方 `Managing long simulations` 的
`Are continuations exact?` 与 `Reproducibility` 两节明确列出这些来源，并指出
individual trajectory 不可复现，而科学 observables 才是目标。

因此：

- 不把 XTC 逐帧坐标 byte-identical 或逐原子完全相同设为跨站点门禁；
- checksum 必须用于 **输入、TPR、脚本、environment snapshot、archive
  integrity**，不能用于要求跨站点 trajectory body 相同；
- 短程资格测试比较运行完整性、初始量、有限/合理的 thermodynamic signals、
  约束/issue scan、checkpoint、资源使用与性能，不把短程轨迹分叉解释成环境失败。

### 2.2 Site/environment confounding

如果 R167Y 只在 AutoDL，matched WT 在 E2 或另一个环境，site/environment 与
genotype 完全混杂。单 replicate 下尤其无法区分 genotype effect 与 site effect。
exact package pin 可以降低可控差异，但不能消除 GPU、CPU、driver、parallel
reduction、storage interruption 和 runtime scheduling 差异。

本计划定义两种证据等级：

| 等级 | 目的 | 可以支持 | 不能支持 |
|---|---|---|---|
| `Q1 AutoDL qualification` | 证明 AutoDL 可重建、可运行、可恢复、成本/性能可接受 | AutoDL 作为候选算力环境；R167Y exploratory run 的工程可行性 | WT/R167Y genotype matched conclusion |
| `S1 matched scientific production` | WT 与 R167Y 在同一 accepted batch contract 下完成对应 rep | 同站点、同环境、同 protocol 的 matched single-rep comparison，仍保留 single-rep 边界 | 3-rep population-level conclusion |

若先跑 R167Y，后续 WT 必须满足以下条件才可把它们组成同一 AutoDL batch：

- 相同 exact GROMACS package/build family 与 precision；
- 相同 GPU model；GPU UUID 可以不同，但必须记录，且不能跨到未批准的新架构；
- 相同 rank/thread 与 `mdrun` offload command contract；
- 同一套 accepted MDP family、equilibration/production length、output cadence；
- 各自 package 的 topology/index/warning gates 都通过；
- 没有 unresolved driver/CUDA/conda environment drift；
- Roy 明确批准将先行 R167Y 从 exploratory 纳入 matched batch。

若上述条件不能满足，补跑 WT 不会自动“挽救”先行 R167Y；应在新的一致环境中重建
完整 pair。

## 3. 环境与站点权威策略

### 3.1 AutoDL 目前的身份

AutoDL 在 repo 内没有 live-verified environment authority。以下全部是
`NEEDS_LIVE_CHECK`：

- host、port、user；
- GPU model、UUID、compute capability、显存、driver；
- hourly price、data-disk price、traffic price；
- OS、CPU、RAM；
- system disk 与 persistent data disk 路径；
- 关机、释放实例、欠费、抢占时的数据保留规则；
- 可用 conda-family package manager；
- exact E2 pin 是否能 resolve、install 和 runtime-load。

密码、token、私钥、dashboard URL/截图和 billing credential 不进入仓库。

### 3.2 Environment authority recommendation

当前不修改 `environments/md-production-sites.md`。该文件顶部已经限定为历史
chimeric unified-rerun matrix，直接追加 AutoDL 会把历史范围误写为当前权威。

推荐顺序：

1. live preflight 后，如 AutoDL 环境证据稳定，新增
   `environments/autodl-md-gromacs.md`，只承载 AutoDL hardware、storage、
   exact package/build、dependency、binary hash 和 run evidence；
2. qualification 阶段保持 `docs/INDEX.md` 与
   `environments/md-production-sites.md` 不变；
3. 只有 Roy 批准 AutoDL 的正式站点角色后，才把
   `environments/md-production-sites.md` 重构为“current site roles + explicit
   historical chimeric section”，并更新 `docs/INDEX.md`；
4. 不另建第二个并行 site matrix，避免 E2/AutoDL 角色出现双重权威。

## 4. AutoDL / E2 环境一致性矩阵

> E2 证据来自 2026-05-29 snapshot；如果要做 E2/AutoDL 同 TPR Level 2
> qualification，应在执行当日重新采集 E2 snapshot。AutoDL 列目前不是事实，只是
> target 或 `NEEDS_LIVE_CHECK`。

| 维度 | E2 repo evidence / target | AutoDL target / 当前状态 | Gate |
|---|---|---|---|
| 站点角色 | 当前参考环境；共享 A100，production 需 fresh resource/benchmark gate | qualification candidate only | Roy 批准前不升级 |
| GPU model | NVIDIA A100-SXM4-80GB | `NEEDS_LIVE_CHECK` | 保存 model + UUID |
| Compute capability | 当前 repo environment authority 未单列；执行时刷新 | `NEEDS_LIVE_CHECK` | 与 CUDA build/runtime compatibility 一起审计 |
| 显存 | 81920 MiB | `NEEDS_LIVE_CHECK` | 必须覆盖同 TPR smoke/benchmark 峰值并留余量 |
| Driver | `590.48.01`（2026-05-29） | `NEEDS_LIVE_CHECK` | 不改 system driver；先诊断具体 CUDA/PTX 错误 |
| `nvidia-smi` supported CUDA | `13.1`（snapshot） | `NEEDS_LIVE_CHECK` | 不是 run 的 toolkit version |
| GROMACS package | `gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0` | exact same target；未验证 | exact build string 必须相同 |
| GROMACS version | `2025.4-conda_forge` | target same；未验证 | `"$GMX_CMD" --version` |
| Command family | `gmx_mpi` | 必须 `gmx_mpi` | 禁止静默换 `gmx` |
| Precision | mixed | target mixed；未验证 | `--version` 一致 |
| MPI | external MPI; OpenMPI 5.0.8 | target same；未验证 | `--version` + conda snapshot |
| OpenMP | enabled; max 128 | target enabled；未验证 | 记录 max 与实际 `NTHREADS` |
| CUDA runtime/toolkit | runtime 12.90; toolkit 12.9 family | target 12.9 family；未验证 | binary output 与 package snapshot |
| FFTW | 3.3.11 | target 3.3.11；未验证 | `conda list` + `ldd` |
| hwloc | 2.12.1 | target same exact solve if exact pin；未验证 | `conda list` |
| SIMD | AVX2_256 | `NEEDS_LIVE_CHECK`，可能因 CPU 不同而不同 | 记录，不假装 exact pin 可消除 |
| Compiler/build | GNU 14.3.0 conda build; exact build hash `h56f47eb_0` | target exact package；runtime host `NEEDS_LIVE_CHECK` | package/build + binary SHA256 |
| Rank/thread | 当前 Gpr2 template 是 1 rank direct `gmx_mpi` + 24 OpenMP threads；不是 Gpr3 固定值 | `QUAL_NTHREADS` / production `NTHREADS` 待 benchmark 冻结 | matched pair 使用相同 command contract |
| GPU offload | template: `-nb gpu -pme gpu -bonded gpu` | 候选同形状；需 smoke 与 bounded tuning | 不未经 benchmark 改成新 contract |
| Persistent storage | E2 `/ifs1` + quota/备份规则 | `NEEDS_LIVE_CHECK` | 明确关机/释放/欠费/抢占数据规则 |
| Interruption risk | shared-resource interference/opportunity cost | `NEEDS_LIVE_CHECK` | checkpoint + incremental recovery |
| Hourly price | 非按小时 AutoDL 同类报价；机会成本另计 | `NEEDS_LIVE_CHECK` | 由实际实例账单记录 |

## 5. 最小脚本与配置架构

### 5.1 原则

- 本地 repo 是脚本、文档、canonical input 和 compact provenance 权威；
  AutoDL 只是 deployment/run target。
- 不修改仍作为 Gpr2 active-run evidence 的三份 Gpr2 脚本；未来 generic driver
  从其控制结构提取，Gpr2-specific 数字不进入默认值。
- site 信息由 `SITE_ID`、`REMOTE`、`PERSISTENT_ROOT`、`ENV_PREFIX`、
  `GMX_CMD` 参数化；system 信息由 reviewed run-contract JSON 提供。
- warning whitelist、atom/molecule counts、index groups、output groups、final time
  都由 accepted Gpr3 package 的真实输出冻结；没有默认 `MAXWARN`。
- postprocess 与 sync 分离；分析复用 chctrl 七 driver 和 system config，不新建
  per-system analyzer。

### 5.2 建议文件清单

| 建议路径 | 动作 | 角色 |
|---|---|---|
| `experiments/md-simulation/scripts/prepare_gpr3_ascr3_matched_inputs.py` | 新增 | 本地生成 docking-receptor→matched-WT transform、共享 transformed ASCR3，并对 WT/R167Y 两臂分别做 clash/coordinate evidence |
| `experiments/md-simulation/scripts/assemble_complex.py` | 参数化，不复制 | 通用 ligand include/molecule/POPC-removal/index assembly；移除 ASCR18 hard-code |
| `experiments/md-simulation/scripts/validate_md_run_contract.py` | 新增 | 统一解析 topology/index/warnings/TPR/CPT/XTC/EDR/completion，写 machine-readable gate TSV |
| `experiments/md-simulation/scripts/md_site_preflight.sh` | 新增 | read-only host/GPU/storage/environment snapshot；本地保存并可同步到新 run root |
| `experiments/md-simulation/scripts/sync_md_run_inputs.sh` | 新增 | manifest-first staging/upload/remote verify/atomic promote；拒绝覆盖 |
| `experiments/md-simulation/scripts/run_gpr_md_preproduction.sh` | 新增 | EM、step6.1-step6.6、smoke/100 ps benchmark、GPU sampler、sanity |
| `experiments/md-simulation/scripts/run_gpr_md_production.sh` | 新增 | 200 ns launch/resume/early gate/completion/checksum |
| `experiments/md-simulation/scripts/postprocess_gpr_md_rep.sh` | 新增 | 用 run-recorded GROMACS 生成 processed rep inputs |
| `experiments/md-simulation/scripts/sync_md_run_outputs.sh` | 新增 | incremental checkpoint/log recovery 与 final raw/processed archive pull |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/run_contracts/gpr3_r167y_ascr3_rep1.json` | gate 后新增 | R167Y package/run immutable contract |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/run_contracts/gpr3_wt_ascr3_rep1.json` | matched production 前新增 | WT matched arm immutable contract |
| `experiments/md-simulation/results/gpr3-r167y-ascr3/chimeric_systems.gpr3_r167y_ascr3_rep1.json` | postprocess 前新增 | chctrl 七 driver 的 system config；不是 analyzer |

### 5.3 各脚本合同

#### A. `prepare_gpr3_ascr3_matched_inputs.py`

- 输入：
  canonical 46-atom `ASCR3_pose_completed.gro`、selected-pose SDF、docking
  receptor、PPM-oriented matched WT receptor、WT job `7628627163` receptor-only
  base、R167Y job `8426884163` return。
- 输出：
  `receptor_alignment.tsv`、rotation/translation、transformed ASCR3 GRO、每臂
  `clash_audit.tsv`、proposed POPC-removal list、coordinate manifest 和
  `terminal_status.tsv`。最终 full assembly 交参数化 `assemble_complex.py`，不在
  此脚本复制 topology/index implementation。
- 必填参数：
  `--dock-receptor`、`--matched-wt-receptor`、`--ligand-gro`、
  `--wt-base`、`--r167y-base`、`--alignment-selection`、`--output-root`。
- 本地/远程：只在本地 canonical-input preparation lane 运行。
- launch/resume：只有 `--create`; 输出已存在即拒绝。失败后写新 evidence
  directory，不做 in-place resume。
- Stop：
  common residue/atom mapping 不唯一、alignment selection 未冻结、任何 46 atoms
  丢失/重排、ligand 超出 box、protein clash、POPC decision 未审查、WT/R167Y
  transform 不一致。
- 可复用：
  `prepare_gpr2_r59c_ascr18_input.py` 的 Kabsch、checksum、clash TSV 和 manifest
  结构；`align_docking_pose_to_membrane.py` 的 transform 思路。
- 不可复用：
  Gpr2 residue 59 check、26→54 mapping、`0.25 A/1.0 A` package heuristic、
  “必须找到一个 POPC overlap”、201 POPC、54 atoms 和 Gpr2 paths。

#### B. 参数化 `assemble_complex.py`

- 新必填：
  `--ligand-moltype ASCR3`、`--ligand-itp ASCR3.itp`、
  `--cgenff-itp toppar/cgenff_ASCR3.itp`、`--posre-itp posre_ASCR3.itp`、
  `--remove-popc-from <reviewed.tsv>`、`--expected-contract <json>`。
- 输出：
  arm-specific final coordinate/topology/index、pre/post-genion molecule tables、
  include audit、index counts 和 terminal status。
- Stop：
  output 已存在；include 已重复；ligand atom order/count 与 ITP 不同；POPC
  removal list 未 reviewed；molecule table 与实际 final coordinates 不一致；
  index group 为空/粘连；任何 expected field 未由 package evidence 提供。
- 可复用：
  variable-width index writing、TIP3 group、protein→ligand→membrane ordering。
- 不可复用：
  ASCR18 includes/name/title、单个 `--remove-popc` 数字、任何 Gpr2 counts。
- 测试：
  后续实现必须补 synthetic >99999 atom index、ASCR3 include/molecule、
  duplicate include、empty group、refuse-overwrite 与 WT/R167Y config tests。

#### C. `validate_md_run_contract.py`

- 输入：
  run-contract JSON + gate type
  (`input|warning|smoke|benchmark|resume|completion|postprocess`) + named files。
- 输出：
  `<gate>_summary.tsv`、normalized warning inventory、issue scan、parsed final
  time/atoms/checkpoint step 和 `terminal_status.tsv`。
- 必填：
  expected values 全在 JSON；缺项即拒绝，不以内置 Gpr2 默认补齐。
- 本地/远程：
  可在两端运行纯 Python validator；GROMACS binary parsing 仍调用
  run-recorded `GMX_CMD`。
- Stop：
  unexpected warning、Fatal/LINCS/NaN/OOM/Killed/CUDA/PTX/segfault、checkpoint
  不可解析、XTC/EDR time/atoms 不符、normal marker 缺失。

#### D. `md_site_preflight.sh`

- 输入/环境变量：
  `REMOTE`、`SITE_ID=autodl`、`RUN_ID`、`LOCAL_EVIDENCE_DIR`；候选环境阶段另需
  `GMX_CMD`、`ENV_PREFIX`、`CONDA_FAMILY_CMD`。
- 输出：
  本计划第 8 节列出的 preflight files、`preflight_summary.tsv` 和独立
  `terminal_status.tsv`。
- 本地/远程：
  本地 launch；remote commands 全部是 inspection。首次 storage path 未确认前，
  evidence 先写本地；确认 persistent root 后再复制到新 run root。
- launch/resume：
  `--host-only`、`--candidate-env`; 同一 `RUN_ID` 已存在即拒绝，无 resume。
- Stop：
  连接参数缺失、`nvidia-smi` 不存在/失败、GPU/driver/存储信息不完整、persistent
  policy 未确认、候选 `GMX_CMD` 不是 exact `gmx_mpi` build。
- 可复用：
  `e2_chimeric_preflight.sh` 的 discovery/snapshot 结构。
- 不可复用：
  E2 paths、自动写 `.chimeric_gmx.env`、自动选择“第一个有 GPU 的 GROMACS”。

#### E. `sync_md_run_inputs.sh`

- 输入/环境变量：
  `REMOTE`、`RUN_ROOT`、`LOCAL_BUNDLE`、`INPUT_MANIFEST`、`RUN_CONTRACT`。
- 输出：
  remote `input.staging.<RUN_ID>/`、remote checksum verification log、atomically
  promoted `input/`、transfer terminal status。
- 本地/远程：
  本地控制 `rsync`; remote 只创建新 run root/staging、校验和 `mv`。
- launch/resume：
  `--stage` 后必须显式 `--promote`; `--stage` 可用 `--partial` 重传；
  `--promote` 不可重复。
- Stop：
  manifest 不完整、local hash 失败、remote hash 失败、`RUN_ROOT` 指向非新 root、
  `input/` 已存在、任何 production output 已存在。
- 可复用：
  `e2_sync_chimeric_inputs.sh` 的 external-payload guard、audit-only、retry、
  manifest-first 思路。
- 不可复用：
  chimeric system layout 和未知目录上的 `--delete`。

#### F. `run_gpr_md_preproduction.sh`

- 输入：
  promoted `input/`、run-contract、exact `GMX_CMD`。
- 输出：
  `preproduction/`、`benchmark_100ps/`、`logs/preproduction/`、processed MDP、
  GPU sampler、`gmx check`、energy sanity、`benchmark_summary.tsv`。
- 必填：
  `RUN_ROOT GMX_CMD NTHREADS RUN_CONTRACT PREFIX SESSION`。
- launch/resume：
  `--launch`; 默认不自动续接半成品。后续若实现 `--start-at`，必须先由 validator
  证明上一 stage 完成且下一 stage 输出不存在。
- Stop：
  package gate 未 PASS、GPU busy、warning whitelist 不匹配、stage output 已存在、
  checkpoint/XTC/EDR 不可读或 issue scan 命中。
- 可复用：
  step6.1-step6.6、sampler、processed MDP、gmx check、terminal status 顺序。
- 不可复用：
  Gpr2 atom/molecule/POPC/warning 数值和 seed。

#### G. `run_gpr_md_production.sh`

- 输入：
  accepted `step6.6.gro`、topology/index、production MDP family、
  `benchmark_summary.tsv=status PASS`、frozen checksums。
- 输出：
  200 ns TPR/MDP/log/edr/xtc/cpt/gro、attempt ledger、GPU sampler、completion
  summary 和 `production_archive.sha256`。
- 必填：
  `RUN_ROOT GMX_CMD NTHREADS NSTEPS=100000000 PREFIX SESSION RUN_CONTRACT`；
  `dt=0.002 ps` 必须由 processed MDP/TPR 验证，不能只由 `NSTEPS` 推断 200 ns。
- launch：
  `--launch`; run root/output/prefix/session 含 system+site+rep+date。
- resume：
  `--resume --cpi "$PROD_DIR/$PREFIX.cpt" --append`；保持原 TPR、env、command、
  `-deffnm` 和 provenance。
- Stop：
  launch approval 缺失、active `gmx_mpi`、GPU busy、output 已存在、TPR/CPT
  不可解析、run 已完成、checkpoint 期待的 output 被修改/删除、任何 env/command
  drift。
- 可复用：
  Gpr2 launch/resume/attempt/sampler/final sanity 控制结构。
- 不可复用：
  `MAXWARN=11`、atoms、output selection counts。

#### H. `postprocess_gpr_md_rep.sh`

- 输入：
  production `terminal_status=COMPLETE`、run-recorded TPR/XTC/index、run-recorded
  `GMX_CMD`。
- 输出：
  `processed/rep1/protein_ref.pdb`、
  `processed/rep1/prod_protein.xtc`、processing logs/checksums/status。
- 必填：
  `RUN_ROOT GMX_CMD PREFIX REP=1 RUN_CONTRACT`。
- launch/resume：
  `--launch`; processed output 已存在即拒绝，不做自动 resume。
- Stop：
  production completion gate 未通过、GROMACS environment 不同、group
  definitions/counts 未冻结、processed final time/atoms 不符。
- 可复用：
  Gpr2 three-stage `trjconv` 和 processed sanity 的结构。
- 不可复用：
  `SOLU=6438`、`SOLU_BACKBONE=1623` 与 ASCR18 selection。Gpr3 selections
  必须由新 system config 实测。

#### I. `sync_md_run_outputs.sh`

- 输入/环境变量：
  `REMOTE RUN_ROOT LOCAL_PAYLOAD_ROOT RUN_ID MODE=incremental|final`。
- 输出：
  外部 payload store 中 timestamped recovery snapshots 或 final raw/processed
  archive；local pull checksum；compact provenance candidate set。
- incremental：
  只拉 `*.cpt`、`*_prev.cpt`、production logs、terminal status、attempts、
  sampler 和 manifests 到新 timestamp directory；不修改 remote output，不把
  local copy 当作 remote resume source。
- final：
  completion gate 后拉完整 raw + processed + sanity + logs + manifests。
- Stop：
  `LOCAL_PAYLOAD_ROOT` 在 Git worktree 内、目标 snapshot 已存在、remote
  manifest 校验失败；final 模式下 production/postprocess 未完成。
- 可复用：
  `e2_sync_chimeric_results.sh` 的 external-root guard、retry、run-id layout。
- 不可复用：
  chimeric filename patterns、默认 rep1/2/3 和允许覆盖开关。

## 6. Remote run root 与传输合同

### 6.1 SSH 与 run naming

Roy 提供实际实例参数后，在本机私有 `~/.ssh/config` 建议增加：

```sshconfig
Host autodl-gpr3
    HostName <AUTODL_HOST>
    User <AUTODL_USER>
    Port <AUTODL_PORT>
    IdentityFile <LOCAL_PRIVATE_KEY_PATH>
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
```

直接连接模板：

```bash
ssh -p <AUTODL_PORT> <AUTODL_USER>@<AUTODL_HOST>
```

不要把真实密码、token、私钥、dashboard 信息或完整 `~/.ssh/config` 复制到 repo。

确认 persistent path 后定义：

```bash
export REMOTE=autodl-gpr3
export SITE_ID=autodl
export RUN_DATE=<YYYYMMDD>
export AUTODL_PERSISTENT_ROOT=<NEEDS_LIVE_CHECK>
export RUN_ID="gpr3_r167y_ascr3_rep1_${SITE_ID}_${RUN_DATE}"
export RUN_ROOT="${AUTODL_PERSISTENT_ROOT}/igem/md-simulation/${RUN_ID}"
export PREFIX="gpr3_r167y_ascr3_rep1_200ns_${SITE_ID}_${RUN_DATE}"
export SESSION="gpr3_r167y_ascr3_rep1_prod_${SITE_ID}_${RUN_DATE}"
```

### 6.2 Remote tree

```text
<AUTODL_PERSISTENT_ROOT>/igem/md-simulation/
└── gpr3_r167y_ascr3_rep1_autodl_<YYYYMMDD>/
    ├── input/
    ├── preproduction/
    ├── benchmark_100ps/
    ├── production/
    ├── processed/
    │   └── rep1/
    ├── sanity/
    ├── logs/
    │   ├── preflight/
    │   ├── preproduction/
    │   └── production/
    └── manifests/
```

传输期间只允许额外出现：

```text
input.staging.<RUN_ID>/
```

`input/` 不存在且 remote checksum 全部通过后，才在同一 filesystem 内执行
`mv input.staging.<RUN_ID> input`。`production/` 一旦出现任何 mdrun output，input
不得重新 promote，run root 不得复用。

### 6.3 Local bundle 与 manifest

只打包 accepted runnable input、reviewed scripts、run-contract 和 manifest。禁止
上传整个 dirty worktree、`Downloads/`、CHARMM-GUI archive 全树或无关结果。

模板：

```bash
export LOCAL_BUNDLE=<EXTERNAL_OR_TMP_STAGING>/gpr3_r167y_ascr3_rep1_autodl_<YYYYMMDD>
test -d "$LOCAL_BUNDLE/input"
test -d "$LOCAL_BUNDLE/scripts"
test -f "$LOCAL_BUNDLE/config/run_contract.json"
mkdir -p "$LOCAL_BUNDLE/manifests"
(
  cd "$LOCAL_BUNDLE"
  find input scripts config -type f -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 \
    > manifests/input_manifest.sha256
)
(
  cd "$LOCAL_BUNDLE"
  shasum -a 256 -c manifests/input_manifest.sha256
)
```

上传与断点重传：

```bash
ssh "$REMOTE" \
  "test ! -e '$RUN_ROOT' && mkdir -p '$RUN_ROOT/input.staging.$RUN_ID' '$RUN_ROOT/manifests'"

rsync -avP --partial \
  "$LOCAL_BUNDLE/" \
  "$REMOTE:$RUN_ROOT/input.staging.$RUN_ID/"

ssh "$REMOTE" \
  "cd '$RUN_ROOT/input.staging.$RUN_ID' && sha256sum -c manifests/input_manifest.sha256"

ssh "$REMOTE" \
  "test ! -e '$RUN_ROOT/input' &&
   test ! -e '$RUN_ROOT/production' &&
   mv '$RUN_ROOT/input.staging.$RUN_ID' '$RUN_ROOT/input'"
```

实际脚本应让 `manifests/` 位于 bundle root，并在 promote 后复制一份到 run-root
`manifests/`。上述命令是 execution template，不是本 session 已执行记录。

硬规则：

- 不对任何未知 AutoDL 目录使用 `rsync --delete`；
- 不通过 rsync 覆盖 live production outputs；
- checksum 失败则保留 staging 与失败日志，不 promote；
- staging 与 final input 必须在同一 filesystem，确保 `mv` 是原子 rename；
- 如果 `RUN_ROOT` 在本 workflow 首次创建前已经存在，先停止并由 Roy 决定新 run
  id，不自行复用；由本 workflow 创建后则只允许按 stage → verify → promote
  状态机继续。

### 6.4 Incremental recovery 与 final archive

production 期间只做只读 pull，优先保全 checkpoint/log：

```bash
export LOCAL_PAYLOAD_ROOT=<OUTSIDE_GIT_WORKTREE>
export SNAPSHOT_ID=$(date +%Y%m%d_%H%M%S)
export LOCAL_RECOVERY="$LOCAL_PAYLOAD_ROOT/gpr3-r167y-ascr3/raw/${RUN_ID}/recovery/${SNAPSHOT_ID}"
mkdir -p "$LOCAL_RECOVERY"

rsync -avP --partial \
  --include="${PREFIX}.cpt" \
  --include="${PREFIX}_prev.cpt" \
  --exclude="*" \
  "$REMOTE:$RUN_ROOT/production/" \
  "$LOCAL_RECOVERY/production/"

rsync -avP --partial \
  "$REMOTE:$RUN_ROOT/logs/production/" \
  "$LOCAL_RECOVERY/logs/production/"
```

每次 snapshot 使用新目录；不把本地 recovered CPT 自动上传回去。remote resume 只用
原 run root 的 TPR+CPT，除非另有灾难恢复决策。

正常 completion + postprocess 后：

```bash
rsync -avP --partial \
  "$REMOTE:$RUN_ROOT/" \
  "$LOCAL_PAYLOAD_ROOT/gpr3-r167y-ascr3/raw/${RUN_ID}/"
```

拉取后在 local archive root 运行 remote manifest check，并生成独立
`local_pull_<timestamp>.sha256`。raw payload、XTC/EDR/CPT/TPR/runtime logs 放
external/local ignored payload；Git-visible 层只保留 reviewed summaries、
environment/run provenance、manifest/checksum、recovery pointer、system config 和
analysis summaries。

## 7. 分阶段命令模板

> 所有命令都是未来 execution template。当前 plan session 不执行。
>
> `<...>` 是必须先替换的占位符，不能按字面粘贴到 shell。未来 driver 应在 launch
> 前拒绝任何仍含占位符、空值或 `NEEDS_LIVE_CHECK` 的参数。

### Phase 0 — runnable-input gate（本地）

```bash
python3 experiments/md-simulation/scripts/prepare_gpr3_ascr3_matched_inputs.py \
  --dock-receptor <ACCEPTED_GPR3_DOCKING_RECEPTOR> \
  --matched-wt-receptor experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb \
  --ligand-gro experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro \
  --wt-base experiments/md-simulation/systems/Gpr3_WT/gromacs \
  --r167y-base experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/gromacs \
  --alignment-selection <REVIEWED_ALIGNMENT_SELECTION> \
  --output-root <NEW_PACKAGE_EVIDENCE_ROOT>

python3 experiments/md-simulation/scripts/assemble_complex.py \
  --config <R167Y_ASCR3_ASSEMBLY_CONTRACT_JSON>

python3 experiments/md-simulation/scripts/validate_md_run_contract.py \
  input \
  --contract <R167Y_RUN_CONTRACT_JSON>
```

同样对 WT arm 运行 assembly/input validation。所有数值由输出写入 contract，再
人工 review；不得从 Gpr2 脚本预填。

### Phase 1 — 首次 read-only preflight

```bash
date -Is
hostname
hostnamectl || true
uname -a
cat /etc/os-release
id
pwd
ulimit -a
lscpu
free -h
df -hT
mount
lsblk
nvidia-smi -L
nvidia-smi
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,compute_cap,temperature.gpu,power.limit --format=csv
nvcc --version || true
ldd --version | head -1
command -v micromamba || command -v mamba || command -v conda || true
python3 --version
tmux -V
rsync --version | head -1
sha256sum --version | head -1
```

建议由 `md_site_preflight.sh --host-only` 逐项通过 SSH 执行并把 stdout/stderr 写到
本地独立 evidence files；不要先假设 remote persistent path。dashboard/policy 中的
关机、释放、欠费、抢占和 data-disk retention 规则需由 Roy 提供或 live 核对，不能
从 shell 输出推断。

### Phase 2 — exact-pin dry-run 与候选环境证据

```bash
export AUTODL_ENV_PREFIX="<AUTODL_PERSISTENT_ROOT>/igem/envs/gromacs-2025.4-mpi-cuda"
export CONDA_FAMILY_CMD=<micromamba_or_mamba_or_conda>

"$CONDA_FAMILY_CMD" create --dry-run --json \
  -p "$AUTODL_ENV_PREFIX" \
  -c conda-forge \
  'gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0' \
  > exact_pin_dry_run.json
```

只有 dry-run exact build 成功且 Roy 批准安装后，执行阶段才可运行：

```bash
"$CONDA_FAMILY_CMD" create -y \
  -p "$AUTODL_ENV_PREFIX" \
  -c conda-forge \
  'gromacs=2025.4=mpi_openmpi_cuda_h56f47eb_0'
```

候选环境快照：

```bash
export GMX_CMD="$AUTODL_ENV_PREFIX/bin/gmx_mpi"
"$GMX_CMD" --version > gmx_version.log 2>&1
ldd "$GMX_CMD" > gmx_binary_ldd.txt 2>&1
"$CONDA_FAMILY_CMD" list -p "$AUTODL_ENV_PREFIX" > conda_list.txt
"$CONDA_FAMILY_CMD" list --explicit -p "$AUTODL_ENV_PREFIX" > conda_explicit.txt
sha256sum "$GMX_CMD" > gmx_binary.sha256
```

不得把 `"$GMX_CMD" --version` 直接 pipe 到 `grep/head`；先保存完整日志，再解析。
exact pin 无法 resolve/install/load 时停在 fallback B，不执行替代安装。不得为此
改 system CUDA/driver。

### Phase 3 — transfer

```bash
REMOTE=autodl-gpr3 \
RUN_ROOT="$RUN_ROOT" \
LOCAL_BUNDLE="$LOCAL_BUNDLE" \
INPUT_MANIFEST="$LOCAL_BUNDLE/manifests/input_manifest.sha256" \
bash experiments/md-simulation/scripts/sync_md_run_inputs.sh --stage

REMOTE=autodl-gpr3 \
RUN_ROOT="$RUN_ROOT" \
bash experiments/md-simulation/scripts/sync_md_run_inputs.sh --promote
```

### Phase 4 — smoke / preproduction / 100 ps benchmark

同 TPR Level 2 qualification 优先使用一个冻结的 100 ps TPR：

```bash
OMP_NUM_THREADS="$QUAL_NTHREADS" "$GMX_CMD" mdrun \
  -s "$RUN_ROOT/benchmark_100ps/frozen_qualification_100ps.tpr" \
  -deffnm "$RUN_ROOT/benchmark_100ps/${RUN_ID}_qualification_100ps" \
  -ntomp "$QUAL_NTHREADS" \
  -pin on \
  -nb gpu \
  -pme gpu \
  -bonded gpu \
  -cpt 5
```

正式 Gpr3 preproduction driver：

```bash
RUN_ROOT="$RUN_ROOT" \
GMX_CMD="$GMX_CMD" \
NTHREADS="$NTHREADS" \
RUN_CONTRACT="$RUN_ROOT/input/config/run_contract.json" \
PREFIX="$PREFIX" \
SESSION="gpr3_r167y_ascr3_rep1_preprod_autodl_<YYYYMMDD>" \
bash "$RUN_ROOT/input/scripts/run_gpr_md_preproduction.sh" --launch
```

`QUAL_NTHREADS` 与 production `NTHREADS` 在实际 CPU/GPU inventory 后冻结。必要时做
小型 bounded grid（例如若硬件允许，比较多个 thread count），但每个 variant 必须
写独立 summary；选中 command 后 WT/R167Y matched batch 不再静默改变。

### Phase 5 — production launch 与 early gate

```bash
RUN_ROOT="$RUN_ROOT" \
GMX_CMD="$GMX_CMD" \
NTHREADS="$NTHREADS" \
NSTEPS=100000000 \
RUN_CONTRACT="$RUN_ROOT/input/config/run_contract.json" \
PREFIX="$PREFIX" \
SESSION="$SESSION" \
bash "$RUN_ROOT/input/scripts/run_gpr_md_production.sh" --launch
```

启动 10–30 分钟后只读 early gate：

```bash
tmux ls
pgrep -ax gmx_mpi
nvidia-smi
"$GMX_CMD" dump -cp "$RUN_ROOT/production/${PREFIX}.cpt" \
  > "$RUN_ROOT/logs/production/checkpoint_early_dump.log" 2>&1
tail -n 80 "$RUN_ROOT/logs/production/mdrun_${PREFIX}.log"
```

validator 必须确认 step/time 前进、CPT 可解析、GPU 使用、log/XTC/EDR 增长且 issue
scan 无命中。此时只记录 `production_running_early_gate_pass`，不能写
`production completed`。

### Phase 6 — resume

只有非正常停止且 resume gate 全部通过：

```bash
RUN_ROOT="$RUN_ROOT" \
GMX_CMD="$GMX_CMD" \
NTHREADS="$NTHREADS" \
RUN_CONTRACT="$RUN_ROOT/input/config/run_contract.json" \
PREFIX="$PREFIX" \
SESSION="${SESSION}_resume_<ATTEMPT>" \
bash "$RUN_ROOT/input/scripts/run_gpr_md_production.sh" --resume
```

底层命令必须保留：

```bash
"$GMX_CMD" mdrun \
  -s "$RUN_ROOT/production/${PREFIX}.tpr" \
  -deffnm "$RUN_ROOT/production/$PREFIX" \
  -cpi "$RUN_ROOT/production/${PREFIX}.cpt" \
  -append \
  -ntomp "$NTHREADS" \
  -pin on \
  -nb gpu \
  -pme gpu \
  -bonded gpu \
  -cpt 30
```

### Phase 7 — completion / postprocess / analysis

```bash
python3 "$RUN_ROOT/input/scripts/validate_md_run_contract.py" \
  completion \
  --contract "$RUN_ROOT/input/config/run_contract.json"

RUN_ROOT="$RUN_ROOT" \
GMX_CMD="$GMX_CMD" \
PREFIX="$PREFIX" \
REP=1 \
RUN_CONTRACT="$RUN_ROOT/input/config/run_contract.json" \
bash "$RUN_ROOT/input/scripts/postprocess_gpr_md_rep.sh" --launch
```

processed payload 回收后，Python-side analysis 复用共享七 driver：

```bash
export CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr3-r167y-ascr3/chimeric_systems.gpr3_r167y_ascr3_rep1.json
export CHIMERIC_MD_REPS=1

python3 experiments/md-simulation/analysis/chctrl/analyze_convergence.py
python3 experiments/md-simulation/analysis/chctrl/analyze_selection_rmsd.py
python3 experiments/md-simulation/analysis/chctrl/analyze_hbond.py
python3 experiments/md-simulation/analysis/chctrl/analyze_com_distance.py
python3 experiments/md-simulation/analysis/chctrl/analyze_rmsf.py
python3 experiments/md-simulation/analysis/chctrl/analyze_bsa.py
python3 experiments/md-simulation/analysis/chctrl/analyze_contacts.py
```

只有七 driver 审查证明存在真实 metric gap 且 Roy 同意，才考虑新增共享 driver。

## 8. 日志与 evidence 合同

### 8.1 Preflight

`logs/preflight/` 至少包括：

- `hostname.txt`
- `os_release.txt`
- `lscpu.txt`
- `memory_storage.txt`（`ulimit/free/df/mount/lsblk` 的完整分段输出）
- `nvidia_smi.log`
- `nvidia_smi_query.csv`
- `nvcc_version.txt`
- `tool_discovery.txt`
- `gmx_version.log`
- `gmx_binary_ldd.txt`
- `gmx_binary.sha256`
- `conda_list.txt`
- `conda_explicit.txt`
- `exact_pin_dry_run.json`
- `preflight_summary.tsv`
- `terminal_status.tsv`

`preflight_summary.tsv` 还必须有人工/政策字段：

- `persistent_root`
- `persistent_after_poweroff`
- `persistent_after_instance_release`
- `arrears_retention_rule`
- `preemption_rule`
- `hourly_gpu_price`
- `data_disk_price`
- `traffic_price`
- `policy_evidence_pointer`

未知值一律为 `NEEDS_LIVE_CHECK`，不能留空或套用 AutoDL 常见默认值。

### 8.2 Input / preproduction / benchmark

- `input_manifest.sha256`
- remote `sha256sum -c` log
- transform/alignment/clash evidence
- molecule-count/topology-include/index-group gate logs
- normalized warning inventory + reviewed whitelist
- 每一 `grompp` log 与 processed MDP (`-po`)
- EM、step6.1-step6.6 TPR/log/gro/cpt/edr
- benchmark `.mdp/.tpr/.log/.edr/.xtc/.cpt/.gro`
- XTC/EDR/CPT `gmx check`/`gmx dump`
- energy sanity XVG/log/parsed TSV
- GPU utilization sampler
- `benchmark_summary.tsv`

`benchmark_summary.tsv` 至少包含：

- system、site、run id、input/TPR checksum；
- atoms、GPU model/UUID、driver；
- GROMACS version/build/binary hash；
- precision、MPI/OpenMPI、CUDA runtime、FFTW、SIMD；
- rank、threads、offload flags；
- ns/day、hour/ns；
- GPU utilization/memory/power/temperature summary；
- issue-scan、checkpoint、XTC/EDR readability；
- energy/temperature/pressure/density sanity result；
- hourly price、estimated 200 ns time/cost；
- 每一个 PASS criterion 的 source 或 `OPERATIONAL_HEURISTIC_REQUIRES_ROY_APPROVAL`。

### 8.3 Production

- `run_start_time.txt`
- `mdrun_attempts.tsv`（header、attempt id、mode、start/end、exit、TPR/CPT hash、
  env/binary hash、command）
- stage-local `terminal_status.tsv`
- production MDP、processed MDP、TPR checksum
- `grompp` log + warning gate
- 完整 `mdrun` log + GROMACS `prod.log`
- `nvidia_smi_mdrun_sampler.csv`
- periodic/early/final checkpoint dump 或 check 证据
- issue scan
- energy sanity
- `production_rep1_summary.tsv`
- `production_archive.sha256`
- XTC/EDR `gmx check`
- normal termination marker、`200000 ps` XTC/EDR endpoint、final structure
- processed `processing_summary.tsv` 与 processed checksum

### 8.4 Stage status 不能混写

各目录维护独立 status：

| Stage | 允许状态示例 |
|---|---|
| preflight | `NEEDS_LIVE_CHECK` / `PASS` / `BLOCKED_CONNECTION_OR_STORAGE` |
| environment | `DRY_RUN_PASS` / `EXACT_PIN_VALIDATED` / `BLOCKED_EXACT_PIN` |
| transfer | `STAGED` / `PROMOTED` / `BLOCKED_CHECKSUM` |
| benchmark | `RUNNING` / `PASS` / `BLOCKED_BENCHMARK` |
| production | `RUNNING` / `INTERRUPTED_RESUMABLE` / `COMPLETE` / `BLOCKED` |
| postprocess | `NOT_STARTED` / `RUNNING` / `COMPLETE` / `BLOCKED` |

“方案完成”不能等价于“环境安装”，“环境安装”不能等价于“benchmark 通过”，
“benchmark 通过”不能等价于“production 完成”。

每次 durable 推进写 `docs/logs/YYYY-MM-DD.md`，但 raw logs/trajectory 不复制进
day log。

## 9. 有序门禁与 stop conditions

| # | Gate | PASS evidence | Stop condition / blocker status |
|---:|---|---|---|
| 1 | Gpr3 runnable input | ASCR3 transform；WT/R167Y final coordinates；molecule/topology；package-local index；pair-specific warnings | 任一 arm 未完成；`BLOCKED_RUNNABLE_INPUT` |
| 2 | Connection/storage | 实际 host/port/user；persistent root；容量；关机/释放/欠费/抢占规则 | 任一为 unknown 或不可靠；`BLOCKED_CONNECTION_OR_STORAGE` |
| 3 | Environment equivalence | exact pin resolve/install/load；`gmx_mpi`；build/deps/precision/GPU compatible | exact pin 不成立或 PTX/CUDA fail；`BLOCKED_EXACT_PIN` |
| 4 | Transfer integrity | local manifest PASS；remote `sha256sum -c` PASS；atomic input promote | hash mismatch、existing root/output；`BLOCKED_TRANSFER` |
| 5 | Smoke | `grompp`；GPU detected；step progress；CPT；XTC/EDR readable；issue scan clean | Fatal/LINCS/NaN/OOM/Killed/PTX/CUDA/segfault；`BLOCKED_SMOKE` |
| 6 | 100 ps benchmark | production parameter family；energy/thermo sanity；performance/GPU/cost；criterion sources | technical issue 或 Roy 未批准 operational criteria/budget；`BLOCKED_BENCHMARK` |
| 7 | Production launch | Roy 已批准路线；new run root；无 active gmx；GPU idle；TPR/MDP/top/index/input hash frozen | 任何 approval/resource/frozen-input 条件缺失；`BLOCKED_LAUNCH` |
| 8 | Early runtime | 10–30 min step/time/log/CPT/GPU/output growth 正常 | 不推进、CPT 不可读或 issue hit；`BLOCKED_EARLY_RUNTIME` |
| 9 | Resume | 非正常停机；TPR+CPT 可解析；未完成；无 active process；原 provenance 一致 | completed、active process、output 被改、env drift；`BLOCKED_RESUME` |
| 10 | Completion/postprocess | normal marker；XTC/EDR `200000 ps`；issue clean；archive hash；same-env postprocess | final time/marker/archive/env 任一失败；`BLOCKED_COMPLETION_OR_POSTPROCESS` |

## 10. 两级环境资格测试

### Level 1 — 静态等价性

必须比较：

- input package 与 frozen TPR SHA256；
- raw MDP 与 `grompp -po` processed MDP；
- topology includes、`[ molecules ]`、index group names/counts；
- GROMACS version/build/binary SHA256/precision；
- MPI/OpenMPI、CUDA runtime/toolkit、FFTW、hwloc、SIMD、OpenMP、compiler；
- `gmx dump -s <same.tpr>` normalized semantic fields；
- 两站点都能读取同一 TPR/CPT/EDR/XTC（CPT 只读测试用副本）。

PASS 不要求 `ldd` 的所有 system paths 字符串完全相同，但每一差异必须分类为：

- expected host path difference；
- equivalent package/runtime identity；
- unresolved dependency difference；
- disqualifying build/precision/MPI/CUDA difference。

### Level 2 — 同输入短程资格测试

优先在 exact E2 environment 生成一次 frozen 100 ps TPR，然后把同一 TPR 以 checksum
验证传到 E2 与 AutoDL。两站点使用同一 command shape 和一个双方都支持的
`QUAL_NTHREADS`。

比较：

- run 是否正常；
- startup log 中 GPU detection/offload 与 rank/thread；
- initial potential/kinetic/total energy 等命名量；
- temperature/pressure/density 的 finite/sanity summary；
- constraint/LINCS、NaN、OOM、CUDA/PTX 与 fatal scan；
- checkpoint 写入与可解析性；
- XTC/EDR 可读、frame/final time；
- ns/day、hour/ns、GPU utilization/memory/power/temp。

预期数值分叉：

- floating-point 最低位差异；
- trajectory coordinates 很快不再逐帧一致；
- parallel reduction、GPU reduction、dynamic load balancing 导致的顺序差异。

说明环境/方法不一致的证据：

- input/TPR hash 不同；
- processed MDP/topology/index 语义不同；
- precision/MPI/build/CUDA family 未按批准合同；
- 一边使用 CPU fallback 或不同 offload path；
- 初始量出现无法由 rounding 解释的大差异；
- 只有一边出现 constraints/fatal/NaN/PTX/OOM；
- final time/frame/output group 不同。

GROMACS 官方材料没有为本 Gpr3 体系给出通用的 temperature/pressure/density/
energy 跨站点数值 PASS tolerance，也没有给出统一 GPU utilization 阈值。任何定量
tolerance 必须写入 decision package，标为
`OPERATIONAL_HEURISTIC_REQUIRES_ROY_APPROVAL`；不得伪装成官方 cutoff。

## 11. 性能与成本计算

### 11.1 必填输入

| 变量 | 含义 | 当前值 |
|---|---|---|
| `P_gpu` | AutoDL 实例小时价 | `NEEDS_LIVE_CHECK` |
| `P_disk` | data disk 单价（按实际计费单位） | `NEEDS_LIVE_CHECK` |
| `P_traffic` | 出站/流量单价 | `NEEDS_LIVE_CHECK` |
| `S_R` | R167Y benchmark ns/day | `NEEDS_BENCHMARK` |
| `S_W` | WT benchmark ns/day | `NEEDS_BENCHMARK` |
| `D_raw` | 单 rep raw archive GB | `NEEDS_BENCHMARK` |
| `D_processed` | 单 rep processed archive GB | `NEEDS_BENCHMARK` |
| `T_retention` | 远端保留天数 | Roy 决定 |
| `T_wait_e2` | E2 预计排队/共享干扰时间 | 记录实际，不猜 |

### 11.2 公式

```text
hour_per_ns = 24 / ns_per_day
cost_per_ns = hourly_price * hour_per_ns
estimated_200ns_hours = 200 * hour_per_ns
estimated_200ns_cost = hourly_price * estimated_200ns_hours
```

若 WT/R167Y atom count 或性能不同，pair 不使用一个平均 `S` 掩盖差异：

```text
R167Y_rep1_hours = 4800 / S_R
R167Y_rep1_gpu_cost = P_gpu * 4800 / S_R

WT_rep1_hours = 4800 / S_W
WT_rep1_gpu_cost = P_gpu * 4800 / S_W

pair_rep1_hours = 4800 / S_R + 4800 / S_W
pair_rep1_gpu_cost = P_gpu * pair_rep1_hours

pair_3rep_hours = 3 * pair_rep1_hours
pair_3rep_gpu_cost = P_gpu * pair_3rep_hours
```

附加成本：

```text
disk_cost = retained_GB * P_disk * billing_time
traffic_cost = downloaded_GB * P_traffic
total_cash_cost = gpu_cost + disk_cost + traffic_cost
```

### 11.3 评估表

| 场景 | GPU hours | GPU cost | Disk/traffic | 科学可用性 |
|---|---:|---:|---:|---|
| AutoDL qualification（smoke + 100 ps） | 从实测 walltime | 实价计算 | 小型 evidence | 只支持环境资格 |
| R167Y rep1 only | `4800/S_R` | `P_gpu*4800/S_R` | 实测 | exploratory，除非后补同 batch WT |
| WT + R167Y rep1 pair | `4800/S_R + 4800/S_W` | 分别计算 | 两套 archive | matched single-rep |
| WT + R167Y, 3 reps | `3 * pair_rep1_hours` | `3 * pair_rep1_gpu_cost` | 六套 archive | 多 rep 设计，仍需正式分析计划 |

站点决策还必须并列记录：

- AutoDL instance availability、重建难度、运行中断/欠费/释放风险；
- persistent data 是否独立计费与保留；
- checkpoint 间隔与最近可恢复损失；
- E2 shared GPU wait、资源干扰和团队 opportunity cost；
- AutoDL cash cost 与 E2 opportunity cost，不把“E2 无小时账单”写成“零成本”；
- 100 ps 到 200 ns 的线性外推不确定性；production 实际 ns/day 需持续更新。

## 12. Fallback 决策表

| 排序 | 情形 | 推荐动作 | 禁止动作 | 等待 Roy 的决定 |
|---:|---|---|---|---|
| 1 / A | AutoDL 可复现 E2 exact pin | 同 frozen TPR smoke/100 ps；通过后提交 environment+cost decision package | 直接从 install 跳到 production | 是否批准 qualification 后 production；只跑 R167Y 还是同站点 pair |
| 2 / C | exact pin 成功，AutoDL 显著更稳定/便宜且持久化可靠 | 优先提议 AutoDL 承载完整 Gpr3 pair，E2 备份；用实测 ns/day、cost、interruption、rebuild evidence 量化 | 未批准就更新 site authority 或迁移队列 | 是否提升为 Gpr3 pair/后续 mutant-GPR 主力站点 |
| 3 / B | exact pin 不可实现，但 AutoDL 有稳定、完整记录的不同环境 | 停；评估整个 `Gpr3_WT/R167Y + ASCR3` 在该 AutoDL env 形成独立 batch | 只把异环境 R167Y 与 E2 WT 合并；静默换 `nompi_cuda`/版本 | 停止，或批准独立 AutoDL pair batch |
| 4 / D | environment、storage、benchmark、cost 或 stability 不通过 | 停止 AutoDL production；归档 blocker；E2 保持当前参考路线 | 为“把任务跑起来”改 driver/system CUDA/忽略持久化风险 | 是否等待新实例/新价格，或回 E2 |

## 13. Roy 最少确认项

执行前只需要 Roy 先回答以下四组问题：

1. AutoDL 实例连接参数是什么：`AUTODL_HOST`、`AUTODL_PORT`、
   `AUTODL_USER`，以及本机应使用哪个私钥路径或登录方式？密码/token 不要发进
   repo 文件。
2. 实例 GPU model、小时价、data-disk/traffic 价格，以及关机/释放/欠费/抢占后的
   数据保留规则是什么？
3. 当前意图是：
   - 只做 AutoDL qualification；还是
   - qualification 通过后准备把 `Gpr3_WT + ASCR3` 与
     `Gpr3_R167Y + ASCR3` matched pair 都放到 AutoDL？
4. exact E2 pin 无法实现时：
   - 立即停止 AutoDL 路线；还是
   - 允许先评估一个完整、独立的 AutoDL WT/R167Y batch（评估后仍需二次批准才
     production）？

另外，在 benchmark decision package 中 Roy 还需确认预算上限、可接受 walltime
和所有没有官方来源的 operational tolerance；这些值现在不能替 Roy 预填。

## 14. GROMACS 官方证据与审计

### Research Objective

- Decision/use: 为跨站点资格门禁、checkpoint/resume、GPU 环境记录和 benchmark
  方法提供官方证据；不替代 Gpr3 package-local 实测。
- Target question: 为什么跨站点门禁不能要求逐帧轨迹完全一致；checkpoint、
  append、backup 的官方行为是什么；GPU/CUDA/MPI 与性能选择为何必须记录并实测？
- Source scope: GROMACS 官方 manual 与 release notes。
- Exclusions: 论坛、搜索摘要、AutoDL 常见默认值，以及没有体系实测支持的数值阈值。
- Access date: 2026-07-17。

### Findings

- GROMACS 官方明确指出：有限精度、core count、processor type、compiler/
  optimization、FFTW runtime choice、dynamic load balancing、MPI reduction 与
  GPU reduction 都影响 trajectory reproducibility；individual trajectory
  不可复现不等于 observable 无科学意义。
- checkpoint 保存 full-precision positions/velocities 与 coupling state；
  `-cpi` 用于 continuation。append 时 checkpoint 会校验已有 output checksums；
  output 被修改/删除会阻止正常 append。
- 官方建议频繁备份，明确提到 `rsync` 可在 simulation 运行时安全复制 output 到
  remote storage；本计划因此把 incremental recovery 设计成只读、timestamped
  pull。
- NVIDIA GPU 的推荐 backend 是 CUDA；MPI/thread-MPI、precision、CUDA、
  architecture target 与 runtime environment 都需要显式记录。
- 官方 performance guide 明确指出，具体 GPU offload/parallel choice 只有在目标
  机器上测试性能才能确定；因此不从 GPU 型号直接宣称 AutoDL 更快。

### Gaps and Conflicts

- 官方文档不为本 Gpr3 membrane system 提供 temperature/pressure/density/energy
  的通用跨站点 numeric tolerance，也不提供统一 GPU-utilization PASS threshold。
- 当前官方 “current” manual 页面标题为 GROMACS 2026.3 documentation，而 repo
  production pin 是 2025.4。引用的 reproducibility/checkpoint/GPU principles 是
  current manual 的一般操作原则；2025.4 版本身份另由 2025.4 release-notes 页面
  与 repo exact-package evidence固定。
- exact conda package pin 能固定 package/build family，但不能消除 host CPU/SIMD、
  driver、GPU architecture、parallel reduction 和 storage/runtime 行为差异。

### Verified Source Ledger

| ID | URL | Authority | Status | Exact pointer | Relevance |
|---|---|---|---|---|---|
| G1 | [Managing long simulations](https://manual.gromacs.org/current/user-guide/managing-simulations.html) | GROMACS official | Accessible 2026-07-17 | `Managing long simulations`; `Appending to output files`; `Backing up your files`; `Are continuations exact?`; `Reproducibility` | checkpoint/append/backup/reproducibility |
| G2 | [Installation guide](https://manual.gromacs.org/current/install-guide/index.html) | GROMACS official | Accessible 2026-07-17 | `GPU support` → `CUDA`; `MPI support`; `CUDA GPU acceleration`; build precision/MPI options | CUDA/MPI/precision/build record |
| G3 | [Getting good performance from mdrun](https://manual.gromacs.org/current/user-guide/mdrun-performance.html) | GROMACS official | Accessible 2026-07-17 | `Performance considerations for GPU tasks` | target-machine benchmark required |
| G4 | [GROMACS 2025.4 release notes](https://manual.gromacs.org/current/release-notes/2025/2025.4.html) | GROMACS official | Accessible 2026-07-17 | `GROMACS 2025.4 release notes` | pinned release identity |
| G5 | [Validation](https://manual.gromacs.org/current/user-guide/validation.html) | GROMACS official | Accessible 2026-07-17 | `Validation`; `Features with validation pending` | validation across hardware/options is not exhaustive |

### Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| 跨站点 qualification 不要求 MD 轨迹逐帧完全一致 | G1 | `Are continuations exact?`; `Reproducibility` list | 最低位差异、MPI/GPU reduction 等可使 chaotic trajectory 快速分叉 | High | 该原则不免除对统计 observable 和方法一致性的审查 |
| resume 必须使用可解析的 checkpoint | G1 | `Managing long simulations` opening; `-cpi` paragraph | checkpoint 保存 full-precision state；`-cpi` 是 continuation 路径 | High | 仍须核对 TPR、CPT、环境与命令 provenance |
| append 前必须保持已有 output provenance | G1 | `Appending to output files` | append 会校验 checkpoint 中记录的 output-file checksum | High | output 被修改或删除时应停止并形成 blocker |
| production 期间可做只读增量回收 | G1 | `Backing up your files` | 官方备份建议明确提到运行时使用 `rsync` 复制 output | High | 本计划进一步限定为 timestamped pull，不在远端使用 `--delete` |
| 环境矩阵必须记录 CUDA、MPI 与 precision | G2 | `GPU support` → `CUDA`; `MPI support`; `GMX_DOUBLE` and `GMX_MPI` options | NVIDIA CUDA backend、MPI 和 precision 是不同 build/runtime 维度 | High | exact package pin 不能消除 host 与 driver 差异 |
| GPU task assignment 必须在目标实例实测 | G3 | `Performance considerations for GPU tasks`, final item | 性能选择依赖目标机器，不能从 GPU 型号直接推断 | High | 100 ps 结果只支持候选 command contract，不证明长期稳定性 |
| AutoDL exact-pin 路线保持 2025.4 release identity | G4 | Page title and `GROMACS 2025.4 release notes` heading | 2025.4 是可定位的官方 release | High | conda exact build identity仍由 repo package pin 与 live snapshot 固定 |
| exact pin 后仍需 smoke 与短程验证 | G5 | `Features with validation pending` | 官方 validation 对 hardware/backend 组合的覆盖并非穷尽 | High | qualification 不能替代本 Gpr3 package-local gate |

### Audit Notes

- 每个 decision-relevant web claim 已映射到 G1–G5。
- 每个 source 于 2026-07-17 可访问，并使用 page heading/section 作为 pointer。
- 没有把 current manual 的一般原则升级成 Gpr3-specific numeric cutoff。
- 没有用搜索 snippet、论坛或 AutoDL 常见默认目录/价格作为证据。
- 未解决项已保留为 `NEEDS_LIVE_CHECK` 或
  `OPERATIONAL_HEURISTIC_REQUIRES_ROY_APPROVAL`。

## 15. References / 所引

- `AGENTS.md`
- `docs/DOCMAP.md`
- `docs/INDEX.md`
- `docs/ops/md-gromacs-operational-pitfalls.md`
- `docs/ops/payload-tracking-policy.md`
- `docs/ops/nkuliulab-e2-cloud-server.md`
- `environments/e2-md-gromacs.md`
- `environments/md-production-sites.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `experiments/md-simulation/scripts/assemble_complex.py`
- `experiments/md-simulation/scripts/prepare_gpr2_r59c_ascr18_input.py`
- `experiments/md-simulation/scripts/e2_chimeric_preflight.sh`
- `experiments/md-simulation/scripts/e2_sync_chimeric_inputs.sh`
- `experiments/md-simulation/scripts/e2_sync_chimeric_results.sh`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_preproduction.sh`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_production.sh`
- `experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh`

## 16. Referenced by / 被引

- `codex/docs/plans/README.md`
- `docs/logs/2026-07-17.md`
- Future only after live evidence: `environments/autodl-md-gromacs.md`
- Future only after Roy approves formal site role: `environments/md-production-sites.md`,
  `docs/INDEX.md`
