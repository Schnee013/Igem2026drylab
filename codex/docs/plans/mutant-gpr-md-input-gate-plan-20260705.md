# Mutant GPR MD Input-Gate Material Plan

> Date: 2026-07-05
>
> Status: first local material audit, first repair/provenance pass, AF3 local sanity, both package designs, package-local ligand topology scaffolds, clean receptor PDBs, manual PPM 2.0 submission packages, local PPM-output ingestion, raw/clean PPM output, CHARMM-GUI manual submission packages, local CHARMM-GUI return validator, Gpr3 ASCR3 coordinate-completion work order, standalone Gpr3 ASCR3 46-atom ligand coordinate layer, and mutant GPR metric pre-registration are complete for `Gpr2_R59C + ASCR18` and `Gpr3_R167Y + ASCR3`. Both systems still need CHARMM-GUI output packages, receptor-frame final ligand insertion/alignment, final topology, package-local index, and warning review before any smoke/benchmark command plan.
>
> Scope: convert the refreshed docking handoff into MD-ready local input decisions for `Gpr2_R59C` and `Gpr3_R167Y`.
>
> This is not an E2 launch plan, not a full-production plan, and not a replacement for a later smoke/benchmark decision.
>
> Current execution pointer: `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md` is the active work order for the next manual CHARMM-GUI output acquisition and archive step. Each system now has a package-local return intake template under `gromacs/`; fill it and run `experiments/md-simulation/scripts/validate_mutant_gpr_charmm_gui_return.py` before ligand insertion.

## 项目意义

本计划只把 refreshed docking 推荐的两个首选受体突变体推进到 MD 输入门禁。

这一步要回答一个实际问题：

```text
Gpr2_R59C + ASCR18 和 Gpr3_R167Y + ASCR3 能不能形成本地可审计、可估算体系大小、可进入后续 smoke/benchmark 决策的 MD input package？
```

## iGEM2026 drylab 接力路线

这份计划的用途不是把 PPM 或 CHARMM-GUI 当成单独任务收尾，而是把 `docking -> mutant GPR MD -> 湿实验解释 -> Wiki/答辩材料` 接起来。当前最短可执行路线如下：

| 阶段 | 要拿到的材料 | 完成后立刻接什么 | 面向 iGEM 的产出 |
|---|---|---|---|
| 1. PPM orientation | 两个 mutant receptor 的 PPM raw output、clean output、manifest、status | 进入 CHARMM-GUI single-chain package | 证明首选突变体可以进入膜体系构建，而不是停在 AF3/对接结构 |
| 2. CHARMM-GUI package | `topol.top`、`step5_input.gro`、`index.ndx`、`step6*.mdp`、`toppar/` 和下载记录 | 插入/补齐 ASCR18 或 ASCR3 final coordinates | 把 refreshed docking 首选组合变成真实 MD 输入材料 |
| 3. final coordinate/topology/index | final coordinate、`topol_phase3.top` 或等价文件、package-local `index.ndx`、molecule-count check | 做 system-specific warning review | 得到可估算 atom count 和可写短测计划的 package |
| 4. warning review | `grompp_warning_gate.txt`、atom count、与 WT resource baseline 的一阶比较 | 写 Gpr2-only 或 dual-system local smoke/benchmark command plan | 给 E2 排程和 A100 占用提供具体输入，不再靠泛估 |
| 5. smoke/benchmark plan | 本地命令计划、输入清单、预期输出、失败处理 | 经用户确认后再进入 E2 短测/benchmark 执行 | 决定 mutant GPR 能不能进入 production pilot |
| 6. production decision | short benchmark 速率、warning、sanity、初始结构稳定性检查 | 决定 200/300/500 ns、rep 数、是否保留 WT/apo 对照 | 形成 Wiki 可写的机制验证路线和湿实验优先级支持材料 |
| 7. MD analysis package | ligand pose RMSD、关键残基 contact occupancy/lifetime、protein RMSD/RMSF、trajectory sanity | 写湿实验交接解释和 Wiki 图表需求 | 回答 R59C/ASCR18、R167Y/ASCR3 是否在动态体系中支撑 docking 推荐 |

如果 PPM 或 CHARMM-GUI 网页步骤等待人工处理，当前 drylab 不暂停：并行准备两件不会浪费的材料。

| 并行动作 | 直接文件 | 用途 |
|---|---|---|
| Gpr3 ASCR3 坐标补全工作单 | `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md` | 把 24-atom docking pose 转成 46-atom ASCR3 coordinate workflow，避免 Gpr3 后面卡在 ligand 坐标 |
| MD 指标预注册草案 | `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md` | CHARMM-GUI/output/package 完成后直接知道要量什么，不临时改指标 |
| CHARMM-GUI return 验收脚本与测试 | `experiments/md-simulation/scripts/validate_mutant_gpr_charmm_gui_return.py` 与 `tests/modeling/test_charmm_gui_return_validator.py` | output 回传后能先做文件/checksum manifest 和缺失/重复文件检查，不把未验收材料直接拼进 package |

## 当前补资料执行版

两个 refreshed docking 首选体系现在都已经推进到 receptor-only CHARMM-GUI handoff；Gpr3 的 ASCR3 46-atom ligand coordinate layer 也已经生成。下一步是提交/回收 CHARMM-GUI output，并把 Gpr3 已生成的 ASCR3 coordinate layer 插入后续 receptor/membrane package。哪个体系先完整，就先写对应 single-system local smoke/benchmark plan；两个都完整时再写 dual-system plan。

CHARMM-GUI 的具体提交、记录和归档要求已经单独写成工作单：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`。两个体系的回传接收单也已经放到 system-local `gromacs/` 目录：`systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv`，以及 `systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv`。后续会话先运行 `experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py --system all` 做本地 submission preflight，再照该工作单回收 output package，填 intake，并用 `experiments/md-simulation/scripts/validate_mutant_gpr_charmm_gui_return.py` 生成本地文件/checksum manifest，再回到本计划判断是否进入 final coordinate/topology/index/warning。

Gpr3 的 ASCR3 坐标补全要求已经单独写成工作单：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md`，并已执行到 ligand-coordinate 层。输出状态见 `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`：已生成 `ASCR3_pose_completed.gro` / `.pdb`、heavy-atom mapping、mapping alternatives 和 coordinate source table。后续 package-frame alignment 和 clash sanity 等 CHARMM-GUI output 到位后再做。

后续 MD 指标预注册已经写入：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md`。后面的 single-system 或 dual-system smoke/benchmark plan 应继承这里的 package sanity、short-run sanity、ligand pose RMSD、readout contact occupancy/lifetime、carboxylate contacts、receptor RMSD/RMSF 和 membrane sanity。

| 顺序 | 资料块 | 直接输入 | 必须产出 | 通过条件 | 失败后动作 |
|---|---|---|---|---|---|
| 1 | PPM 2.0 raw output | `systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`; `systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` | `output/Gpr2R59CASCR18_ppm2_output_raw.pdb`; `output/Gpr3R167YASCR3_ppm2_output_raw.pdb`; PPM thickness/tilt/transfer-energy/TM/warning record | raw PDB 保存到约定路径；提交时间、server/version、输出摘要可追溯 | 若 PPM 页面或下载失败，记录失败截图/页面文字和提交文件 SHA256，然后重试或改人工获取，不进入 CHARMM-GUI |
| 2 | PPM output ingestion | 两个 raw PPM output | `*_ppm2_output_clean.pdb`; `ppm_output_manifest.tsv`; `ppm_output_status.md` | clean PDB 保持 chain/residue/CA/mutation 计数，且 HETATM/DUM 为 0；manifest/status 记录 SHA256 和 PPM 摘要 | 若有非 DUM HETATM 或计数不符，停在 raw-output 审查，不手工改成 CHARMM-GUI 输入 |
| 3 | CHARMM-GUI single-chain output package | `*_ppm2_output_clean.pdb`; `docs/ops/charmm-gui-membrane-builder.md` 单链设置；两个体系均已有 `receptor/charmm_gui_submission/` handoff | package-local `gromacs/` 输出，至少含 `topol.top`、`step5_input.gro`、`index.ndx`、`step6*.mdp`、`toppar/`、下载来源记录和 validator manifest | 使用 `Use PDB Orientation`、POPC、KCl `0.15 M`、XY `90 A`、water `22.5 A`、CHARMM36m、GROMACS-only、NPT `303.15 K`；`validate_mutant_gpr_charmm_gui_return.py` 最小文件检查通过；总原子数进入 package status | 若 protein extent、packing、penetration、缺文件或下载失败，记录具体 CHARMM-GUI step/validator 缺口和页面错误，不继续拼配体 |
| 4 | ligand final coordinates | Gpr2: selected ASCR18 SDF first pose；Gpr3: selected ASCR3 SDF first pose + deprotonated ASCR3 46-atom topology | Gpr2 final ASCR18 coordinate aligned to receptor package；Gpr3 final ASCR3 46-atom coordinate aligned to receptor package | Gpr2 molecule name/atom count/topology charge 对齐 ASCR18；Gpr3 final coordinate 是 `ASCR3` 且 46 atoms，不再继承 WT `ASCR1`/ASCR18 | 若 pose 与膜/蛋白 clash 不可接受，记录 clash 和替代需求，不静默换 pose |
| 5 | final topology + index | CHARMM-GUI output + package-local ligand `.itp`/`posre`/`toppar` | `topol_phase3.top` 或等价 topology；package-local `index.ndx`; group-size record | molecule counts 与 final coordinate 一致；index group 至少记录 `SOLU`、`MEMB`、`SOLV`、`SOLU_MEMB`、`SYSTEM`、`TIP3` | 若 include、molecule count 或 index group 不一致，先修 package，不写 smoke 命令 |
| 6 | warning review and next plan | final topology/coordinate/index | system-specific `grompp_warning_gate.txt`; Gpr2-only 或 dual-system local smoke/benchmark command plan | warning 来源逐条可解释；atom count 可和 WT resource baseline 做一阶比较 | warning 来源不清时只写 warning repair note，不进入 E2 或 benchmark |

### PPM 2.0 提交工作单

PPM 2.0 的“人工提交”不再只是一句待办；当前使用下面 work order 执行。2026-07-06 已完成 Gpr2 和 Gpr3 fallback backend submission、raw/clean output 回收，并为两个体系生成 CHARMM-GUI manual submission package。

```text
experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/ppm2_submission_work_order_20260706.md
```

执行要点：

| 项 | Gpr2 | Gpr3 |
|---|---|---|
| Upload file | `systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` | `systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| UI route | `https://opm.phar.umich.edu/ppm_server2` | `https://opm.phar.umich.edu/ppm_server2` |
| Settings | N-ter `in`, heteroatoms `no` | N-ter `in`, heteroatoms `no` |
| Raw output path | `systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb` | `systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb` |
| Ingest command | `PYTHONPYCACHEPREFIX=/private/tmp/drylab_pycache python3 experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py --system gpr2` | `PYTHONPYCACHEPREFIX=/private/tmp/drylab_pycache python3 experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py --system gpr3` |

如果后续需要重跑 PPM，primary UI 失败时先按 work order 记录 failure note，再试 `https://opm.phar.umich.edu/ppm_server2_cgopm`。没有 raw PPM output 时不进入 CHARMM-GUI；当前两个体系已经有 DUM-free clean PPM output。

Gpr2 当前 PPM 结果：

| Field | Value |
|---|---|
| Backend | `cgopm fallback endpoint https://cgopm.cc.lehigh.edu/ppm` |
| Results URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_165523485_8819042/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_165523485_8819042/Gpr2R59CASCR18_ppm2_inputout.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` |
| Status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md` |
| PPM values | thickness `33.4 +/- 2.1 A`; tilt `3 +/- 1 deg`; transfer energy `-74.9 kcal/mol`; 7 TM segments; warning `heteroatoms excluded` |

Gpr2 当前 CHARMM-GUI handoff：

| Field | Value |
|---|---|
| Submission package | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/README.md` |
| Upload file | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` |
| Settings table | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv` |
| Upload validation | 3153 ATOM / 406 residues / 406 CA / chain A / CYS59 / HETATM 0 / DUM 0 |
| Next action | submit CHARMM-GUI manually, record job id/page warnings/download archive, then archive GROMACS output under `systems/gpr2-R59C-ascr18/gromacs/` |

Gpr3 当前 PPM 结果：

| Field | Value |
|---|---|
| Backend | `cgopm fallback endpoint https://cgopm.cc.lehigh.edu/ppm` |
| Results URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_174757017_9935109/ppm_results.html` |
| Output PDB URL | `https://ppm-results.s3.us-east-2.amazonaws.com/20260705_174757017_9935109/Gpr3R167YASCR3_ppm2_inputout.pdb` |
| Clean CHARMM-GUI input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` |
| Status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md` |
| PPM values | thickness `31.6 +/- 1.1 A`; tilt `7 +/- 1 deg`; transfer energy `-77.4 kcal/mol`; 7 TM segments; warning `heteroatoms excluded` |

Gpr3 当前 CHARMM-GUI handoff：

| Field | Value |
|---|---|
| Submission package | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/README.md` |
| Upload file | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` |
| Settings table | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv` |
| Upload validation | 3158 ATOM / 401 residues / 401 CA / chain A / TYR167 / HETATM 0 / DUM 0 |
| Next action | submit CHARMM-GUI manually, record job id/page warnings/download archive, then archive GROMACS output under `systems/gpr3-R167Y-ascr3/gromacs/` |

如果后续替换 raw PPM output，重新运行：

```bash
PYTHONPYCACHEPREFIX=/private/tmp/drylab_pycache python3 experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py --system gpr2
PYTHONPYCACHEPREFIX=/private/tmp/drylab_pycache python3 experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py --system gpr3
```

补资料完成后的决策口径很简单：

| 结果 | 下一步 |
|---|---|
| 只有单个体系 final coordinate/topology/index/warning review 完整 | 写对应 single-system local smoke/benchmark command plan，用 WT Gpr2 benchmark 做资源估算。 |
| Gpr2 和 Gpr3 都完整 | 写 dual-system local smoke/benchmark command plan，并分开列 Gpr2/Gpr3 atom count、warning 和预计 E2 时间。 |
| Gpr3 卡在 receptor-frame ASCR3 insertion/clash sanity | 不等 Gpr3 阻塞 Gpr2；Gpr3 单独继续 CHARMM-GUI output 后的 ASCR3 insertion/alignment、clash sanity、topology/index/warning。 |
| 两个体系都卡在 CHARMM-GUI output | 回到 CHARMM-GUI 失败记录，不写任何 benchmark plan。 |

## 当前输入事实

| 项 | repo 状态 | 本计划使用方式 |
|---|---|---|
| 候选来源 | `docs/modeling/wet-lab-handoff-P0-docking.md` 把 `Gpr2_R59C + Gpr3_R167Y` 列为当前主推双通道组合。 | `Gpr2_R59C` 作为 Channel A / ASCR18 主线，`Gpr3_R167Y` 作为 Channel B / ASCR3 主线。 |
| docking ratio | `experiments/docking-repro/analysis/ratio_channel_report.md` 记录 `Gpr2_R59C` 为 Channel A #1，`Gpr3_R167Y` 为 Channel B #1。 | 只定义输入优先级；不把 Vina 分数当 Kd。 |
| IFP 机制材料 | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` 含 R59C/R167Y pose 和差异表。 | 选择 ligand pose 和后续 MD 指标时使用。 |
| AF3 结构材料 | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/` 与 `gpr3_r167y/` 各有 5 个 model CIF 和 summary JSON。 | 必须先选模型并记录理由；不能把下载目录直接当生产结构。 |
| WT 资源基线 | `Gpr2_WT + ASCR18` 100 ps E2 benchmark 已完成；132,478 atoms，139.222 ns/day。 | 作为后续资源估算基线，不作为突变体稳定性结论。 |
| Gpr3 WT 输入 | `experiments/md-simulation/systems/Gpr3_WT/gromacs/step6.6.gro` 有 139,899 atoms，但本地目录缺 `index.ndx`。 | 先做 Gpr3 WT index repair/input gate，才能做同类 benchmark 或 baseline。 |
| ligand 参数 | `ASCR18` 和 `ASCR3` 去质子化 CGenFF penalty 均全部 < 10，总电荷均为 -1。 | 用 deprotonated topology；不要回到 protonated 版本。 |

## 本轮交付

本轮只建立下一步资料补齐和输入门禁路线，不运行远程命令。

| 交付物 | 作用 |
|---|---|
| 本计划 | 指定 `Gpr2_R59C` / `Gpr3_R167Y` local input gate 的文件、顺序、停止条件。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv` | 记录结构、pose、topology、index、system size、warning policy 的逐项状态。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md` | 当前决定仍暂不写 smoke/benchmark command plan；下一步从两个体系的 CHARMM-GUI submission package 转 actual CHARMM-GUI output、final coordinate、index 和 warning review。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_pose_provenance.md` | 将 `Gpr2_R59C + ASCR18` 的 local package pose source 固定到 IFP SDF first pose 与 `VINA RESULT -5.698`；ratio `-6.227` 只保留为候选排名分数。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_wt_package_index/README.md` + `index.fixed.ndx` | 从 `Gpr3_WT/gromacs/step6.6.gro` 生成 package-only index 并记录 group sizes；不修改原始 WT 系统目录。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_topology_replacement_checklist.md` | 写清 ASCR18/ASCR1 当前命名状态与 ASCR3 topology/posre/delta 生成要求，阻止直接继承 WT topology。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/af3_tm_sanity_20260705.md` | 确认 Gpr2 model_0、Gpr3 model_0/model_2 的单链、残基数、突变位点、AF3 summary confidence 和本地 readout residues；把下一步推进到 package design。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_package_design.md` | 定义 `Gpr2_R59C + ASCR18` planned directory、source inputs、clean-PDB/PPM/CHARMM-GUI/pose-insertion workflow、ASCR18 include requirements、package-local index、warning gate 和 smoke readiness gate；仍不创建 runnable package files。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_package_design.md` | 定义 `Gpr3_R167Y + ASCR3` planned directory、source inputs、clean-PDB/PPM/CHARMM-GUI/ASCR3 coordinate workflow、ASCR3 include requirements、package-local index、warning gate 和 smoke readiness gate；仍不创建 runnable package files。 |
| 已产出：`experiments/md-simulation/scripts/prepare_mutant_gpr_package_materials.py` | 可重复生成两个 package scaffold 的 ligand topology files、manifest 和 source checksums。 |
| 已产出：`experiments/md-simulation/scripts/prepare_mutant_gpr_receptor_pdbs.py` | 可重复从选定 AF3 CIF 生成两个 package-local clean receptor PDB 和 status record。 |
| 已产出：`experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py` | 在人工下载 raw PPM output 后，本地生成 DUM-free clean PDB、`ppm_output_manifest.tsv` 和 `ppm_output_status.md`；`--check` 可在 raw output 缺失时列出 expected slots。 |
| 已产出：`experiments/md-simulation/scripts/prepare_mutant_gpr_charmm_gui_submission_packages.py` | 从 DUM-free PPM output 生成 hyphen-free CHARMM-GUI upload copy、settings、manifest 和 handoff README；当前已用于 Gpr2 和 Gpr3。 |
| 已产出：`experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py` + `tests/modeling/test_charmm_gui_submission_preflight.py` | 发送 CHARMM-GUI operator request 前，本地检查两个 upload PDB、source clean PDB、settings、manifest、README、return intake/template 和 manifest checksums 是否一致；不提交网络任务。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md` | 把两个 CHARMM-GUI upload file 的人工提交、job id/page warnings/download archive、GROMACS output 归档和后续 ligand/topology/index/warning 顺序写成执行工作单。 |
| 已产出：两个 system-local CHARMM-GUI return intake 模板 | `systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv` 与 `systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv`；用于收到 download archive 后记录 job id、page warnings、archive SHA256、extracted directory、required-file checklist 和 stop/go status。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md` 和 `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` | 把 `Gpr3_R167Y + ASCR3` 从 24-atom docking first pose 推进到 46-atom ASCR3 topology-compatible ligand coordinate layer；后续等待 CHARMM-GUI output 后做 receptor-frame insertion/alignment 和 clash sanity。 |
| 已产出：`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md` | 把后续短测/benchmark 要看的指标预先固定，直接服务后续 single-system 或 dual-system smoke/benchmark plan。 |
| 已产出：`experiments/md-simulation/systems/gpr2-R59C-ascr18/` | package-local ASCR18 ligand topology scaffold、clean receptor PDB、manual PPM submission package、Gpr2 PPM output handoff 和 CHARMM-GUI manual submission package：`ASCR18.itp`、`toppar/cgenff_ASCR18.itp`、`posre_ASCR18.itp`、`receptor/clean_receptor.pdb`、`receptor/clean_receptor_status.md`、`receptor/ppm_submission/README.md`、`receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`、`receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb`、`receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb`、`receptor/ppm_submission/output/ppm_output_manifest.tsv`、`receptor/ppm_submission/output/ppm_output_status.md`、`receptor/charmm_gui_submission/README.md`、`receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`、`receptor/charmm_gui_submission/manifest.tsv`、`receptor/charmm_gui_submission/settings.tsv`、`PACKAGE_STATUS.md`、`ligand_topology_manifest.tsv`、`source_files.sha256`；仍无 CHARMM-GUI output/final coordinate/index/warning gate。 |
| 已产出：`experiments/md-simulation/systems/gpr3-R167Y-ascr3/` | package-local ASCR3 ligand topology scaffold、clean receptor PDB、manual PPM submission package、Gpr3 PPM output handoff、CHARMM-GUI manual submission package 和 standalone ASCR3 coordinate-completion layer：`ASCR3.itp`、`toppar/cgenff_ASCR3.itp`、`posre_ASCR3.itp`、`receptor/clean_receptor.pdb`、`receptor/clean_receptor_status.md`、`receptor/ppm_submission/README.md`、`receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`、`receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb`、`receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb`、`receptor/ppm_submission/output/ppm_output_manifest.tsv`、`receptor/ppm_submission/output/ppm_output_status.md`、`receptor/charmm_gui_submission/README.md`、`receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`、`receptor/charmm_gui_submission/manifest.tsv`、`receptor/charmm_gui_submission/settings.tsv`、`gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro`、`gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb`、`gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`、`PACKAGE_STATUS.md`、`ligand_topology_manifest.tsv`、`source_files.sha256`；仍无 CHARMM-GUI receptor/membrane output、receptor-frame inserted final coordinate、index、warning gate。 |

## 工作块

| 顺序 | 要补的资料 | 打开/检查的文件 | 通过条件 | 停止条件 |
|---|---|---|---|---|
| 1 | 候选和 ligand pairing 固化 | `wet-lab-handoff-P0-docking.md`; `ratio_channel_report.md`; `ratio_pairings.csv` | 主线写成 `Gpr2_R59C + ASCR18` 与 `Gpr3_R167Y + ASCR3`；WT baseline 分开处理。 | 如果湿实验优先级已变，先更新 docking handoff，不能继续旧候选。 |
| 2 | AF3 模型选择 | `af3_downloads/gpr2_r59c/*summary_confidences_*.json`; `af3_downloads/gpr3_r167y/*summary_confidences_*.json`; `*_model_*.cif`; `af3_tm_sanity_20260705.md`; package-local `receptor/clean_receptor_status.md`; package-local `receptor/ppm_submission/README.md` | 已选 `Gpr2_R59C` model_0 和 `Gpr3_R167Y` model_0；model_2 作为 Gpr3 backup comparator；clean receptor PDB、manual PPM input package、PPM output 和 CHARMM-GUI handoff 已生成并校验突变位点。 | 后续 package design 仍需 CHARMM-GUI output/final coordinate/topology/index/warning review。 |
| 3 | docking pose 选择 | `ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/`; `poses/`; `mutant_vs_wt_diff.md` | 明确每个体系的初始 ligand pose、配体质子化态、坐标转换/对齐来源。 | pose 来源不能追溯到 refreshed handoff 时，先补 pose provenance。 |
| 4 | ligand topology | `parameters/ascr18/deprotonated/penalty_summary.md`; `parameters/ascr3/deprotonated/penalty_summary.md`; `systems/gpr2-R59C-ascr18/`; `systems/gpr3-R167Y-ascr3/` | `ASCR18`/`ASCR3` topology、cgenff delta、posre、molecule name、total charge、source checksums 都能指向 package-local 文件。 | 发现 topology 名称、charge 或 include 路径不一致时，先修拓扑清单。 |
| 5 | WT baseline repair | `systems/Gpr2_WT/gromacs/`; `systems/Gpr3_WT/gromacs/`; `assemble_complex.py::build_index` | Gpr2 WT benchmark 文件可复用为资源基线；Gpr3 WT 先生成/审计 index，不直接 benchmark。 | Gpr3 WT index 或 topology 不能自洽时，不进入 R167Y 计划。 |
| 6 | mutant system package preparation | `systems/gpr2-R59C-ascr18/`; `systems/gpr3-R167Y-ascr3/` | ligand topology scaffold、clean receptor PDB、manual PPM submission package、clean PPM output 和 CHARMM-GUI manual submission package 已存在于两个体系；Gpr3 另已有 standalone ASCR3 46-atom coordinate layer。下一步需要 CHARMM-GUI output package、receptor-frame final ligand insertion/alignment、final topology、index 和 warning review。 | final coordinates、index 或 warning review 缺失时，不写 smoke/benchmark command plan。 |
| 7 | warning and smoke policy | `grompp_warning_gate.txt`; `command_plan.md`; topology includes | `Gpr2_WT` 的 `-maxwarn 11` 不能自动迁移；每个新体系必须重新审查 warning 来源。 | warning 来源不是已知 duplicate type-9 dihedral，或 warning count 漂移时，不允许 smoke。 |
| 8 | 下一步决策 | 本计划输出和 material matrix | 通过后再写 local smoke/benchmark command plan；仍需单独批准 E2 动作。 | 任一输入字段不能命名，先补本地资料，不写远程计划。 |

## 输入门禁定义

一个 mutant GPR system 只有同时满足以下字段，才算过 input gate：

- candidate identity 和 ligand pairing 已从 refreshed docking handoff 固化；
- receptor model 文件、选择理由、残基编号和 mutation identity 可追溯；
- ligand pose 文件、配体拓扑、molecule name、charge 和 position restraints 可追溯；
- `topol.top` / `topol_phase3.top` include 关系清楚；
- `index.ndx` 或 regenerated index 的生成方式和 group sizes 已记录；
- `step6.6.gro` 或等价 post-equilibration source 已存在，或建系 request 明确列出缺口；
- warning policy 是本体系专用，不继承 WT benchmark 的 `-maxwarn`；
- system size 和资源估算能用 WT benchmark 做一阶比较。

## 推荐执行顺序

1. 已完成 AF3 local sanity：`Gpr2_R59C` 使用 model_0；`Gpr3_R167Y` 使用 model_0，model_2 作为 backup comparator。
2. 已写 `Gpr2_R59C + ASCR18` package design：使用已选 IFP SDF first pose、ASCR18 deprotonated topology、Gpr2 WT benchmark resource baseline，并定义 package-local index 和 warning policy requirements。
3. 已写 `Gpr3_R167Y + ASCR3` package design：使用 traceable ASCR3 first pose、ASCR3 deprotonated topology source、Gpr3 WT package-only index as planning context，并要求 final ASCR3 coordinate 匹配 46 atoms / charge -1.000 / molecule entry `ASCR3 1`。
4. 已启动 actual package material preparation：两个体系都已有 package-local ligand topology scaffold、checksum/manifest/status record、clean receptor PDB 和 clean receptor status。
5. 已补 manual PPM 2.0 submission package：两个体系都有 hyphen-free PPM input PDB、manifest 和 README。
6. 已完成两个体系的 PPM raw output archival 和 `ingest_mutant_gpr_ppm_outputs.py --system gpr2/gpr3`，生成 clean PPM output、manifest 和 status。
7. 已完成两个体系的 `prepare_mutant_gpr_charmm_gui_submission_packages.py --system gpr2/gpr3`，生成 CHARMM-GUI manual submission package。
8. 已新增两个体系的 package-local CHARMM-GUI return intake/manifest 模板，用于下载包回传时的 job/warning/archive/file-check 接收。
9. 下一步先运行 `experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py --system all` 做本地 submission packet preflight，再用 `receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` 和 `receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` 做人工 CHARMM-GUI submission；下载 GROMACS output 后先填 intake/manifest，再分别归档到两个 system 的 `gromacs/`。
10. Gpr3 ASCR3 heavy-atom mapping 和 46-atom coordinate completion 已按 `gpr3_ascr3_coordinate_completion_work_order_20260706.md` 执行，输出见 `systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`；按 `mutant_gpr_md_metric_preregistration_20260706.md` 固定后续短测指标。
11. 至少一个体系的 final coordinate、topology、index、warning policy 都能命名后，再写 local smoke/benchmark command plan；若只有一个体系先完成，则先写对应 single-system plan。
12. 2026-07-06 用户确认新的省算力采样队列：不铺开 WT 全矩阵或 Channel top3 全量 3 reps；先完成并归档 `Gpr2_WT + ASCR18` rep1，再推进 `Gpr2_R59C + ASCR18` smoke/benchmark -> 200 ns rep1；完成 Gpr2 WT/mut matched analysis 后，再启动 Gpr3 matched ASCR3 pair（`Gpr3_WT + ASCR3` 与 `Gpr3_R167Y + ASCR3`）。rep1 稳定时可暂停 rep2/3，待最终 candidate 保留后再补。

## 后续决策

| 结果 | 下一步 |
|---|---|
| `Gpr2_WT + ASCR18` rep1 未完成或未归档 | 不启动 mutant production；继续等待完成并下载 raw/sanity/checksum 证据。 |
| `Gpr2_R59C + ASCR18` 过 final coordinate/topology/index/warning gate | 写 Gpr2 mutant smoke/benchmark 计划；若通过，执行 200 ns rep1，并与 `Gpr2_WT + ASCR18` rep1 做 matched analysis。 |
| Gpr2 WT/mut matched analysis 完成且仍支持继续 Gpr3 线 | 启动 Gpr3 matched ASCR3 pair：`Gpr3_WT + ASCR3` 与 `Gpr3_R167Y + ASCR3` 的 package gate、smoke/benchmark 和 rep1 triage。 |
| `Gpr2_R59C + ASCR18` 或 `Gpr3_R167Y + ASCR3` rep1 稳定 | 暂停 rep2/3；只把 rep1 写成 triage evidence，待最终 candidate 保留后补 rep2/3。 |
| Gpr2 或 Gpr3 rep1 出现 ligand drift、energy/trajectory sanity 问题或关键 contact 不支持设计 | 回 backup candidate、反配控制或 package repair；不盲目补 rep2/3。 |
| `Gpr3_WT` repair 不通过 | 不做 `Gpr3_R167Y` benchmark，先补 WT baseline。 |
| ligand pose 或 topology provenance 不清 | 回 docking/parameter 文件补资料，不启动 MD。 |

本轮 material audit、第一轮补资料、AF3 local sanity、Gpr2/Gpr3 package design、package-local ligand topology scaffold、clean receptor PDB、manual PPM submission package、PPM output ingestion helper、两个体系的 PPM output handoff、两个体系的 CHARMM-GUI manual submission package、Gpr3 ASCR3 coordinate-completion work order、standalone ASCR3 46-atom coordinate layer 和 mutant GPR metric pre-registration 后的实际结果仍是 `input_gate_decision=not_ready_for_smoke`。已完成 Gpr2 pose provenance、Gpr3 WT package-only index、Gpr3 ASCR3 topology replacement checklist、AF3 sanity memo、两个 package design、`systems/gpr2-R59C-ascr18/` / `systems/gpr3-R167Y-ascr3/` 的 ligand topology scaffold、两个 `receptor/clean_receptor.pdb`、两个 `receptor/ppm_submission/output/` raw/clean output、两个 `receptor/charmm_gui_submission/` handoff，以及 Gpr3 `gromacs/ascr3_coordinate_completion/` 输出；下一步执行 Gpr2/Gpr3 CHARMM-GUI output archival 和 ASCR18/ASCR3 ligand coordinate insertion/alignment -> index/warning review，但 production 启动顺序按 2026-07-06 staged funnel 执行：Gpr2 WT rep1 完成后先接 `Gpr2_R59C + ASCR18`，Gpr2 matched analysis 后再接 Gpr3 matched ASCR3 pair。

## 执行纪律

- 不 SSH，不登录 E2，不跑远程命令。
- 不启动未经 gate 和队列确认的 mutant full production。
- 不把 100 ps WT benchmark 写成 mutant 稳定性或收敛结论。
- 不把单个 rep1 写成最终 3-rep 统计结论。
- 不把 Vina 分数转换为 Kd。
- 不复用旧 2026-04 historical mutant-holo 清单作为当前生产队列；当前候选以 refreshed handoff 为准。

## Next-Session Prompt

```text
Continue /Users/roy/Documents/drylab iGEM2026 drylab goal. Use drylab-project, read AGENTS.md and docs/DOCMAP.md, then open docs/INDEX.md, docs/modeling/P0-md-simulation.md, codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md, experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py, experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_intake_20260706.md, experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_manifest_template.tsv, experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_intake_20260706.md, experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest_template.tsv, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md, experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md, experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md, experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md, experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/README.md, experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md, experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md, experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/README.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/af3_tm_sanity_20260705.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_pose_provenance.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_package_design.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_wt_package_index/README.md, experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_topology_replacement_checklist.md, and experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_package_design.md. Do not SSH or run E2. Continue from the CHARMM-GUI output work order: both `Gpr2_R59C + ASCR18` and `Gpr3_R167Y + ASCR3` now have raw/clean PPM output, CHARMM-GUI manual submission packages, and package-local return intake templates; Gpr3 already has a standalone ASCR3 46-atom ligand coordinate layer. First run `PYTHONPYCACHEPREFIX=/private/tmp/drylab_pycache python3 experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py --system all`; if it passes, submit both upload files to CHARMM-GUI manually, record job id/page warnings/download archives, fill each system's intake/manifest, archive GROMACS output under each system's `gromacs/`; then insert/align ASCR18 and the generated ASCR3 coordinate layer into the final receptor/membrane packages, run topology/index/warning checks, and carry the metric pre-registration into any later smoke/benchmark plan. Only reassess a smoke/benchmark command plan after final coordinates, topology, index, package, and warning policy are all concrete; if only one system becomes concrete first, write a corresponding single-system local smoke/benchmark plan.
```

## References / 所引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P0-molecular-docking.md`
- `docs/modeling/wet-lab-handoff-P0-docking.md`
- `experiments/docking-repro/analysis/ratio_channel_report.md`
- `experiments/docking-repro/analysis/ratio_pairings.csv`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/mutant_vs_wt_diff.md`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `experiments/md-simulation/parameters/ascr18/deprotonated/penalty_summary.md`
- `experiments/md-simulation/parameters/ascr3/deprotonated/penalty_summary.md`
- `experiments/md-simulation/analysis/gpr2_wt_ascr18_e2_short_benchmark_20260705/command_plan.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_pose_provenance.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_package_design.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_wt_package_index/README.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_wt_package_index/index.fixed.ndx`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_topology_replacement_checklist.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_package_design.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/af3_tm_sanity_20260705.md`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_package_materials.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_receptor_pdbs.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_ppm_submission_packages.py`
- `experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_charmm_gui_submission_packages.py`
- `experiments/md-simulation/scripts/check_mutant_gpr_charmm_gui_submission_packet.py`
- `tests/modeling/test_charmm_gui_submission_preflight.py`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/ppm2_submission_work_order_20260706.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/manifest.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_manifest.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/README.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/manifest.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand_topology_manifest.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/source_files.sha256`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand_topology_manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/source_files.sha256`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-05.md`
- `docs/logs/2026-07-06.md`
- `codex/docs/plans/README.md`
