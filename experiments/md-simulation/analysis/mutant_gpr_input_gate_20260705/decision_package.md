# Mutant GPR MD Input-Gate Decision Package

> Date: 2026-07-05
>
> Last updated: 2026-07-06
>
> Scope: local input-gate decision for `Gpr2_R59C + ASCR18` and `Gpr3_R167Y + ASCR3`.

## 结论

现在仍不要写 smoke/benchmark command plan。Gpr2 和 Gpr3 都已经从 PPM submission package 推进到 CHARMM-GUI 手工提交包：raw/clean PPM output 在各自 `receptor/ppm_submission/output/`，CHARMM-GUI upload/readme/settings/manifest 在各自 `receptor/charmm_gui_submission/`。下一步分两条线推进：

1. 按 `charmm_gui_output_work_order_20260706.md` 人工提交两个 CHARMM-GUI upload file、保存 job id/page warnings/download archive，先填写两个 system-local return intake/manifest 模板，再归档和验收 GROMACS output。
2. Gpr3 的本地补料已从工作单推进到坐标层产出：`ascr3_coordinate_completion_status.md` 记录 46-atom ASCR3 ligand coordinate、heavy-atom mapping 和 checksum。下一步是在 CHARMM-GUI output 回收后做 receptor-frame alignment/insertion、protein/POPC clash sanity、topology/index/warning。两体系后续分析继续按 `mutant_gpr_md_metric_preregistration_20260706.md` 固定指标。

之后再做 ASCR18/ASCR3 final coordinate insertion/alignment、final topology molecule-count check、package-local index 和 warning review。只有 final coordinates、topology、index、warning policy 都能具体命名后，才写 smoke/benchmark command plan；如果只有一个体系先完整，就先写对应 single-system 计划。

这一步对 iGEM2026 drylab 的意义很直接：它把 refreshed docking 的首选双通道突变体变成可审计、可估算资源、可再决定短测的 MD package。

## 2026-07-06 采样收缩与执行队列决策

本轮不按 `Gpr2/Gpr3 WT x ASCR3/ASCR18` 全矩阵加 Channel A/B top3 mutant candidates 的方式直接铺开。全量方案会接近 30 个 200 ns 级 replicate，超出当前 E2 共享 A100 的合理默认队列，也会在没有 rep1 triage 的情况下把算力投入到可能很快被淘汰的体系。

采样策略改为 staged funnel：

1. 等待并完成当前运行中的 `Gpr2_WT + ASCR18` 200 ns rep1，下载/归档 raw outputs、sanity logs 和 checksum manifest。
2. 随后优先推进 `Gpr2_R59C + ASCR18`：CHARMM-GUI output -> ASCR18 receptor-frame insertion -> final topology/index/warning review -> smoke/benchmark -> 200 ns rep1。
3. `Gpr2_WT + ASCR18` 与 `Gpr2_R59C + ASCR18` 先形成 matched WT/mut analysis，用于判断 Gpr2 Channel A 首选突变体是否值得补 rep2/3 或转 backup。
4. Gpr2 matched analysis 后再启动 Gpr3 线两个 matched ASCR3 system：`Gpr3_WT + ASCR3` 与 `Gpr3_R167Y + ASCR3`，同样先走 package gate、smoke/benchmark 和 200 ns rep1 triage。
5. rep1 稳定时暂停 rep2/3 是允许且推荐的省算力策略；rep1 只能作为 package sanity、初步稳定性和机制读出，不写成最终 3-rep 统计结论。rep2/3 只在最终 candidate 被保留后补齐。

反配体系（例如 `Gpr2 + ASCR3` 或 `Gpr3 + ASCR18`）和 Channel backup candidates 暂不进入第一轮 production 队列。它们保留为后续选择性对照或故障回退路线，而不是当前 benchmark 的替代项。

## 已经可以用的材料

| 项 | 当前可用性 | 用法 |
|---|---|---|
| 候选组合 | `Gpr2_R59C + Gpr3_R167Y` 是当前 docking handoff 的首选双通道组合。 | 固定为本轮 mutant GPR MD input gate 主线。 |
| AF3 结构 | AF3 local sanity 已完成：Gpr2 model_0 为 primary；Gpr3 model_0 为 primary，model_2 作为 backup comparator。两个选定模型的突变位点在 CIF 中分别为 CYS59 和 TYR167，且 `has_clash=0.0`；clean receptor PDB 已从选定 CIF 生成。 | PPM 2.0 orientation 和 CHARMM-GUI input 转入 package material preparation。 |
| 配体拓扑 | ASCR18、ASCR3 去质子化 CGenFF topology 均已存在，总电荷 -1，max penalty 5.500。 | 分别用于 `Gpr2_R59C + ASCR18` 和 `Gpr3_R167Y + ASCR3`。 |
| WT 资源基线 | `Gpr2_WT + ASCR18` 已有 100 ps E2 short benchmark：132,478 atoms，139.222 ns/day。 | 只用于资源估算和排程，不用来解释突变体稳定性。 |
| IFP 机制目标 | R59C、R167Y 的差异接触残基已经在 IFP 输出中可追踪。 | 用于后续 MD 指标预注册，例如 pose RMSD、关键残基 contact occupancy、contact lifetime。 |
| Gpr2 pose provenance | `Gpr2_R59C_ascr18_poses.sdf` first pose 已选为 local package pose source；对应 `VINA RESULT -5.698`。ratio `-6.227` 只保留为候选排名分数。 | `Gpr2_R59C + ASCR18` package preparation 可以继续，不再卡在 pose score mismatch。 |
| Gpr2 package design | `gpr2_r59c_ascr18_package_design.md` 已定义 planned directory、source inputs、clean-PDB/PPM/CHARMM-GUI/pose-insertion workflow、ASCR18 include requirements、package-local index、warning gate 和 smoke readiness gate。 | Gpr2 进入 package-preparation contract 阶段；仍没有 runnable package files。 |
| Gpr3 WT package-only index | 已从 `Gpr3_WT/gromacs/step6.6.gro` 生成 `gpr3_wt_package_index/index.fixed.ndx`；group sizes 已记录。 | 可作为 Gpr3 WT-derived planning input；最终 R167Y+ASCR3 package 仍需重新生成 package-local index。 |
| Gpr3 ASCR3 replacement checklist | 已写明 ASCR18 include、WT coordinate `ASCR1` resname、ASCR3 topology source、`cgenff_ASCR3.itp` / `posre_ASCR3.itp` 生成要求和 stop conditions。 | `Gpr3_R167Y + ASCR3` 不再直接继承 WT ASCR18 topology。 |
| Gpr3 package design | `gpr3_r167y_ascr3_package_design.md` 已定义 planned directory、source inputs、clean-PDB/PPM/CHARMM-GUI/ASCR3 coordinate workflow、ASCR3 include requirements、package-local index、warning gate 和 smoke readiness gate。 | Gpr3 进入 package-preparation contract 阶段；仍没有 runnable package files。 |
| Gpr2 package-local ligand topology scaffold | `systems/gpr2-R59C-ascr18/` 已有 `gromacs/ASCR18.itp`、`gromacs/toppar/cgenff_ASCR18.itp`、`gromacs/posre_ASCR18.itp`、`PACKAGE_STATUS.md`、`ligand_topology_manifest.tsv` 和 `source_files.sha256`。 | Gpr2 不再卡在 ASCR18 topology 文件组；clean receptor PDB、PPM output 和 CHARMM-GUI submission package 已补，下一步补 CHARMM-GUI output、pose insertion、index 和 warning review。 |
| Gpr3 package-local ligand topology scaffold | `systems/gpr3-R167Y-ascr3/` 已有 `gromacs/ASCR3.itp`、`gromacs/toppar/cgenff_ASCR3.itp`、`gromacs/posre_ASCR3.itp`、`PACKAGE_STATUS.md`、`ligand_topology_manifest.tsv` 和 `source_files.sha256`。 | Gpr3 不再卡在 ASCR3 package-local topology 文件组；clean receptor PDB、PPM output、CHARMM-GUI submission package 和 standalone ASCR3 46-atom coordinate layer 已补，下一步补 CHARMM-GUI output、receptor-frame ligand insertion、index 和 warning review。 |
| Clean receptor PDB | `systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb` 校验为 chain A、406 residues、3,153 atoms、406 CA、CYS59；`systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb` 校验为 chain A、401 residues、3,158 atoms、401 CA、TYR167。 | 作为 PPM submission provenance 保留；两个体系已生成 clean PPM output 和 CHARMM-GUI handoff，但仍不是 runnable GROMACS package。 |
| PPM submission package | 两个体系都已有 `receptor/ppm_submission/README.md`、`manifest.tsv` 和 hyphen-free PPM 2.0 input PDB；Gpr2 input SHA256 与 clean receptor PDB 同为 `aeaafa1fb325dc3853496cfd6bd8411c5207d2f711580132085774aab7ac4f22`，Gpr3 同为 `32dd45cb114e8a59f9ced2d90215315929f01b4a821c2b57be47bdaf8b3b06e5`；两个 input 均记录 HETATM 0、DUM 0。 | 作为 PPM provenance 保留；两个体系的 actual PPM output 已回收。这个 package 本身不是 runnable GROMACS package。 |
| Gpr2 PPM output | Gpr2 raw PPM output SHA256 `25d08326b95cf306096879da415fb7be12cea127a94d7af7e89b34390bcdfdd2`，clean output SHA256 `a7f5dbe776a862091a76d10b872bf0a1c31eb396df612e00897d0c7ad05ac2ef`；raw output 3153 ATOM / 406 residues / CYS59 / 1946 DUM HETATM，clean output 3153 ATOM / 406 residues / CYS59 / 0 HETATM / 0 DUM。PPM record: thickness `33.4 +/- 2.1 A`, tilt `3 +/- 1 deg`, transfer energy `-74.9 kcal/mol`, 7 TM segments, warning `heteroatoms excluded`。 | Use `systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` as the CHARMM-GUI input for Gpr2. |
| Gpr2 CHARMM-GUI submission package | `systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/` 已有 `Gpr2R59CASCR18_charmmgui_input.pdb`、`README.md`、`manifest.tsv` 和 `settings.tsv`；upload copy SHA256 `a7f5dbe776a862091a76d10b872bf0a1c31eb396df612e00897d0c7ad05ac2ef`，校验为 3153 ATOM / 406 residues / 406 CA / chain A / CYS59 / HETATM 0 / DUM 0；settings 固定为 `Use PDB Orientation`、rectangular、water `22.5 A`、XY `90 A`、POPC `1/1`、KCl `0.15 M`、neutralizing ions、CHARMM36m、GROMACS-only、NPT、`303.15 K`。 | 用该 upload file 做人工 CHARMM-GUI Membrane Builder submission；下一步回收 `download.tgz` 并归档 GROMACS output。 |
| Gpr3 PPM output | Gpr3 raw PPM output SHA256 `9ac74c80ecb24b1b580fe0863607683de4e50dc2eca5724589e4ca7f9e83d4ce`，clean output SHA256 `488c633f6850ad03d0ddb2c9f6ea203353d41b061db571572c9433ed77d91b45`；raw output 3158 ATOM / 401 residues / TYR167 / 1450 DUM HETATM，clean output 3158 ATOM / 401 residues / TYR167 / 0 HETATM / 0 DUM。PPM record: thickness `31.6 +/- 1.1 A`, tilt `7 +/- 1 deg`, transfer energy `-77.4 kcal/mol`, 7 TM segments, warning `heteroatoms excluded`。 | Use `systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` as the CHARMM-GUI input for Gpr3. |
| Gpr3 CHARMM-GUI submission package | `systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/` 已有 `Gpr3R167YASCR3_charmmgui_input.pdb`、`README.md`、`manifest.tsv` 和 `settings.tsv`；upload copy SHA256 `488c633f6850ad03d0ddb2c9f6ea203353d41b061db571572c9433ed77d91b45`，校验为 3158 ATOM / 401 residues / 401 CA / chain A / TYR167 / HETATM 0 / DUM 0；settings 固定为 `Use PDB Orientation`、rectangular、water `22.5 A`、XY `90 A`、POPC `1/1`、KCl `0.15 M`、neutralizing ions、CHARMM36m、GROMACS-only、NPT、`303.15 K`。 | 用该 upload file 做人工 CHARMM-GUI Membrane Builder submission；下一步回收 `download.tgz` 并归档 GROMACS output，再把已生成的 ASCR3 46-atom coordinate layer 对齐/插入到 receptor/membrane package。 |
| CHARMM-GUI return intake templates | `systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv` 与 `systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_intake_20260706.md` / `charmm_gui_return_manifest_template.tsv` 已就位。 | 用于收到 CHARMM-GUI download archive 后记录 job id、page warnings、archive SHA256、extracted directory 和 required-file checklist；模板本身不代表 output 已返回。 |
| Gpr3 ASCR3 coordinate-completion layer | `ascr3_coordinate_completion_status.md` 记录已生成 `ASCR3_pose_completed.pdb`、`ASCR3_pose_completed.gro`、heavy-atom mapping、mapping alternatives 和 coordinate source table；final atom count `46`，heavy atom count `21`，topology charge `-1.000`，completed heavy-atom pose delta `0.0000 A`。 | 该层解决 24-atom docking SDF 不能直接入包的问题；后续仍必须等 CHARMM-GUI output 后做 receptor-frame alignment/insertion、protein/POPC clash sanity、topology/index/warning。 |
| Mutant GPR metric pre-registration | `mutant_gpr_md_metric_preregistration_20260706.md` 已把 package sanity、short-run sanity、ligand pose RMSD、readout contact occupancy/lifetime、carboxylate contacts、receptor RMSD/RMSF 和 membrane sanity 写成后续 smoke/benchmark 的指标骨架。 | 后续 single-system 或 dual-system local smoke/benchmark plan 直接继承这些 readouts，不再临时定义分析目标。 |
| PPM output ingestion helper | `experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py` 可用 `--check` 检查 raw/clean/manifest/status slots；raw output 保存到约定路径后，可生成 DUM-free clean PDB、`ppm_output_manifest.tsv` 和 `ppm_output_status.md`，并记录 backend/results URL。 | Gpr2 和 Gpr3 已用该 helper 生成 CHARMM-GUI handoff input。 |

## 现在挡住 benchmark plan 的具体问题

| 问题 | 影响 | 处理顺序 |
|---|---|---|
| 两个体系已有 CHARMM-GUI 手工提交包和 return intake 模板，但还没有 CHARMM-GUI output/final system coordinates。 | Gpr2/Gpr3 仍不是 runnable package；当前 package 不能用于 smoke。 | 第 1 优先：用 `Gpr2R59CASCR18_charmmgui_input.pdb` 和 `Gpr3R167YASCR3_charmmgui_input.pdb` 提交 CHARMM-GUI，保存 job id/page warnings/download archive，填 intake/manifest 并归档 GROMACS output；Gpr3 已有 standalone ASCR3 46-atom ligand coordinate layer，等待 output 后插入。 |
| `Gpr3_R167Y + ASCR3` 还没有 receptor/membrane-inserted ASCR3 final coordinate。 | ASCR3 standalone ligand coordinate 已经匹配 46 atoms / ASCR3 naming / topology charge，但尚未对齐进 CHARMM-GUI receptor/membrane package。 | 第 2 优先：CHARMM-GUI output 到位后，用 `ASCR3_pose_completed.gro` 或 PDB equivalent 做 receptor-frame alignment/insertion、protein/POPC clash sanity、topology molecule-count check、package-local index 和 warning review。 |
| `Gpr3_WT/gromacs/step6.6.gro` ligand coordinate residue name 是 `ASCR1`，而 target 是 ASCR3。 | 简单继承 WT coordinate/topology 命名会把 Channel B package 搞混。 | 第 3 优先：final package coordinate 必须使用 ASCR3-compatible naming，并且 46 atoms 对齐 `ASCR3.itp`。 |
| 后续 MD 指标未提前固定会拖慢 smoke/benchmark 计划。 | 如果等 trajectory 之后再选指标，会把 docking IFP、短测 sanity 和 Wiki 输出拆散。 | 使用 `mutant_gpr_md_metric_preregistration_20260706.md` 作为后续 single-system 或 dual-system smoke/benchmark plan 的分析骨架。 |
| Gpr2 WT benchmark 的 `-maxwarn 11` 是 ASCR18 duplicate type-9 dihedral 专用审查结果。 | 不能迁移成突变体通用 `grompp` 策略。 | 每个新体系单独审 warning；先不写 smoke 命令。 |
| package-local index 和 warning gate 仍不存在。 | 没有 final coordinate 就不能生成 final index，也不能审核真实 `grompp` warnings。 | final coordinate/topology 完成后再做 index 和 warning review；若 Gpr2 先完成，可先评估 Gpr2-only smoke/benchmark plan。 |

## 下一步执行顺序

1. **`Gpr2_R59C + ASCR18` 本地 system package design 已完成**
   - package-design 文件：`gpr2_r59c_ascr18_package_design.md`。
   - receptor source 使用 `af3_tm_sanity_20260705.md` 选定的 `fold_gpr2_r59c_model_0.cif`。
   - pose source 使用 `gpr2_r59c_ascr18_pose_provenance.md` 选定的 IFP SDF first pose。
   - clean receptor PDB、PPM-oriented clean output 和 CHARMM-GUI 手工提交包已生成并通过计数/突变位点校验；后续 package preparation 需要 CHARMM-GUI output package、ASCR18 pose insertion、package-local index 和 Gpr2-specific warning review。

2. **`Gpr3_R167Y + ASCR3` 本地 system package design 已完成**
   - package-design 文件：`gpr3_r167y_ascr3_package_design.md`。
   - receptor source 使用 `af3_tm_sanity_20260705.md` 选定的 `fold_gpr3_r167y_model_0.cif`；model_2 只保留为 backup comparator。
   - 使用 `Gpr3_R167Y_ascr3_poses.sdf` 的 first pose / `VINA RESULT -5.715` 作为 traceable pose source。
   - ASCR3 docking SDF first pose 是 24 atoms，只作 pose/orientation source；final package coordinate 必须匹配 deprotonated ASCR3 46 atoms。
   - clean receptor PDB、PPM-oriented clean output、CHARMM-GUI 手工提交包和 standalone ASCR3 46-atom coordinate layer 已生成并通过记录；后续 package preparation 仍需 CHARMM-GUI output package、ASCR3 receptor-frame alignment/insertion、package-local index 和 ASCR3-specific warning review。

3. **实际 package material preparation 已推进到两个体系的 CHARMM-GUI submission handoff**
   - 已用 `prepare_mutant_gpr_package_materials.py` 生成两个 planned system directory 的 ligand topology 文件组、manifest 和 source checksums。
   - 已用 `prepare_mutant_gpr_receptor_pdbs.py` 从选定 AF3 CIF 生成两个 package-local clean receptor PDB 和 status record。
   - 已用 `prepare_mutant_gpr_ppm_submission_packages.py` 为两个 clean receptor PDB 生成 hyphen-free manual PPM 2.0 input、manifest 和 README。
   - 已新增并更新 `ingest_mutant_gpr_ppm_outputs.py`，用于 raw PPM output 下载后的 DUM-free clean output、output manifest、status、backend 和 URL 记录。
   - 已新增并运行 `prepare_mutant_gpr_charmm_gui_submission_packages.py --system gpr2/gpr3`，在两个 system 的 `receptor/charmm_gui_submission/` 生成 CHARMM-GUI upload copy、README、manifest 和 settings。
   - Gpr2 和 Gpr3 都已保存 raw PPM output、生成 clean CHARMM-GUI input，并形成手工 CHARMM-GUI submission package；两个体系的 return intake/manifest 模板也已放到各自 `gromacs/`。下一步是回收 CHARMM-GUI output package、填 intake/manifest、ligand coordinate insertion/completion、final topology、package-local index 和 warning review。
   - Gpr3 的额外本地材料任务已完成 ligand-coordinate 层：`ASCR3_pose_completed.gro` / `.pdb`、heavy-atom mapping 和 status 已在 `gromacs/ascr3_coordinate_completion/`；后续不再直接用 24-atom docking SDF first pose，而是等 CHARMM-GUI output 后把该 46-atom coordinate layer 插入 receptor/membrane package。
   - 后续 smoke/benchmark 计划的指标骨架已写入 `mutant_gpr_md_metric_preregistration_20260706.md`，包含 ligand pose RMSD、readout contact occupancy/lifetime、carboxylate contacts、receptor RMSD/RMSF 和 package sanity。
   - 若任一体系后续材料先齐，可以先写对应 single-system local smoke/benchmark command plan；另一个体系继续补 final coordinate/topology/index/warning。
   - 若两个体系都齐，再写 dual-system local smoke/benchmark command plan。

4. **再决定 smoke/benchmark command plan**
   - 只有 pose、model、topology、index、warning policy、system package 都能具体命名时，才写下一份本地 smoke/benchmark command plan。
   - 远程 E2 动作仍必须另行批准。

## Go/No-Go

| 条件 | 结果 |
|---|---|
| 只有 PPM submission input，没有 PPM output | 不进入 CHARMM-GUI、不写 smoke 命令；先手动提交 PPM 并存档输出。 |
| 有 Gpr2 clean PPM output，但缺 CHARMM-GUI submission package | 先生成 CHARMM-GUI handoff package，不写 smoke 命令。 |
| 有 CHARMM-GUI submission package 和空白 intake 模板，但缺 CHARMM-GUI output/final coordinate/topology/index/warning review | 可以提交 CHARMM-GUI；下载后先填 intake/manifest 并归档 output package，不写 smoke 命令。 |
| Gpr2 final coordinates + final topology + package-local index + warning policy 完成 | 可以先写 `Gpr2_R59C + ASCR18` local smoke/benchmark command plan。 |
| 当前 `Gpr2_WT + ASCR18` rep1 未完成 | 不启动 mutant production；先等待并归档 WT rep1。 |
| Gpr2 final coordinates + final topology + package-local index + warning policy 完成，且 WT rep1 已归档 | 先写 `Gpr2_R59C + ASCR18` smoke/benchmark -> 200 ns rep1 plan；不等 Gpr3。 |
| `Gpr2_WT + ASCR18` 与 `Gpr2_R59C + ASCR18` matched analysis 完成 | 再推进 Gpr3 matched ASCR3 pair：`Gpr3_WT + ASCR3` 与 `Gpr3_R167Y + ASCR3`。 |
| Gpr3 ASCR3 receptor-frame insertion + final topology + package-local index + warning policy 完成 | 可以写 Gpr3 matched pair 的 smoke/benchmark plan；仍先按 rep1 triage，不默认 rep2/3。 |
| 任一体系 warning 来源不能解释 | 不写 smoke 命令，先修 topology/MDP/input。 |
| 只有 AF3 model、ligand-topology scaffold 和 clean receptor PDB，缺 PPM/CHARMM-GUI/final coordinates/index/warning review | 不进入 benchmark plan。 |

## References / 所引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/wet-lab-handoff-P0-docking.md`
- `experiments/docking-repro/analysis/ratio_channel_report.md`
- `experiments/docking-repro/analysis/ratio_pairings.csv`
- `experiments/docking-repro/analysis/ratio_spectrum.csv`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/mutant_vs_wt_diff.md`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/mutant_contacts.csv`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/af3_tm_sanity_20260705.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_intake_20260706.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_manifest_template.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_intake_20260706.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest_template.tsv`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md`
- `experiments/md-simulation/parameters/ascr18/deprotonated/penalty_summary.md`
- `experiments/md-simulation/parameters/ascr3/deprotonated/penalty_summary.md`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/charmm36.itp`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_package_materials.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_receptor_pdbs.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_ppm_submission_packages.py`
- `experiments/md-simulation/scripts/ingest_mutant_gpr_ppm_outputs.py`
- `experiments/md-simulation/scripts/prepare_mutant_gpr_charmm_gui_submission_packages.py`
- `experiments/md-simulation/scripts/complete_gpr3_ascr3_coordinates.py`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md`
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
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand_topology_manifest.tsv`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/step6.6.gro`
- `experiments/md-simulation/systems/Gpr2_WT/gromacs/topol_phase3.top`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/step6.6.gro`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/topol_phase3.top`
- `experiments/md-simulation/scripts/assemble_complex.py`
- `experiments/md-simulation/scripts/generate_cgenff_delta.py`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/logs/grompp_warning_gate.txt`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_pose_provenance.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr2_r59c_ascr18_package_design.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_wt_package_index/README.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_topology_replacement_checklist.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_r167y_ascr3_package_design.md`

## Referenced by / 被引

- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/gpr3_ascr3_coordinate_completion_work_order_20260706.md`
- `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
