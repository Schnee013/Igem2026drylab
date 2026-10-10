# 当前六组输入选择：两组 ascr3 采用各自的 lid 重构起点

> Source: 2026-10-05 本会话用户最新决定；原始身份回 `retained-20261005/cases.json`、manifest 和各自坐标。
> As of: 2026-10-06，两组各自母体/pose 的候选已生成并完成静态筛选。
> Allowed use: 当前输入选择、来源及候选入口；不证明结构最终验收、几何问题完全解除或新体系已平衡。
> Update trigger: 新候选生成/验收、准备完成或用户改变输入选择。

用户明确：V368R–ascr3、独立 WT–ascr3 在预热后仍存在配体穿过 lid 开口的问题，后续起始受体采用 lid 重构版。`V3682 / ASR3 / ASR18` 在本次对话按既有体系名 `V368R / ascr3 / ascr18` 记录。

规范选择表为 [selection.json](selection.json)。原始保留包不覆盖、不改名，其 `cases.json` 仍是原始六组的历史来源，而不是本次变更后的待运行清单。

**最终来源审查（2026-10-05）**：[逐组文件与坐标核对](audit-20261005/README.md)。六个原始装配的母体、lid 和各自 pose 均吻合；W174 修复前后实际文件确认只改变该侧链。该次审查时两组新坐标尚未生成；随后按用户授权完成了 [两组各自母体/pose 的候选生成与静态检查](../lid-rebuild-own-pose-20261005/README.md)。当前沿用四组的来源核对与两组候选的静态检查，均不能当作六组已准备完成。审查另单列 C 末端氧的局部准备变化。

下表当前文件均相对于保留包 `sources/`。更早来源路径、原始 CIF/完整 Vina 输出、转换记录与校验和见 [provenance.json](provenance.json)。`H` 指 `/Users/roy/Downloads/md-handoff-n84v-v368r/`；`D` 指 `/Users/roy/Documents/docking/`。

| 比较组合 | 受体母体文件 | 配体 pose 文件 | 当前 lid 选择 | 溯源 |
|---|---|---|---|---|
| N84V–ascr18 | `n84v/af3_original/raw_model0.pdb` | `n84v/ascr18/top1.sdf` | 自身原始 lid | 母体：交接包 `H/05_n84v/af3_original/fold_gpr2_b05_fl_n84v_model_0.cif` 转 PDB。配体：原 Docking 批次 `05-af3-saturation-combinations/run-01/05_n84v/ascr18/poses.pdbqt` 的 MODE 1，经交接包传入。 |
| V368R–ascr3 | `v368r/af3_original/raw_model0.pdb` | `v368r/ascr3/top1.sdf` | 从自身母体局部重构；已有待审候选 | 母体：交接包 `H/05_v368r/af3_original/fold_gpr2_b05_fl_v368r_model_0.cif` 转 PDB。配体：原批次 `05-af3-saturation-combinations/run-01/05_v368r/ascr3/poses.pdbqt` 的 MODE 1，经交接包传入。 |
| N84V–ascr3 | `n84v/af3_original/raw_model0.pdb` | `n84v/ascr3/top1.sdf` | 自身原始 lid | 母体：同一 N84V AF3 model 0。配体：原批次 `05-af3-saturation-combinations/run-01/05_n84v/ascr3/poses.pdbqt` 的 MODE 1，经交接包传入。 |
| V368R–ascr18 | `v368r/af3_original/raw_model0.pdb` | `v368r/ascr18/top1.sdf` | 自身原始 lid | 母体：同一 V368R AF3 model 0。配体：原批次 `05-af3-saturation-combinations/run-01/05_v368r/ascr18/poses.pdbqt` 的 MODE 1，经交接包传入。 |
| 独立 WT–ascr18 | `native_wt/full_length.pdb` | `native_wt/ascr18/top1.sdf` | 自身 lid，保留 W174 侧链修复 | 母体：`D/inputs/receptors/af3/original_cif/gpr2_twf154_wt/fold_gpr2_twf154_wt_model_0.cif` → 独立 WT 全长 PDB。配体：`D/outputs/af3/gpr2_twf154_wt/deltaN_aligned/…/ligands/ascr18_deprotonated/run_20260823_223248_3240812/poses.pdbqt` 的 MODE 1；转换保留重原子坐标并补氢。 |
| 独立 WT–ascr3 | `native_wt/full_length.pdb` | `native_wt/ascr3/top1.sdf` | 从自身母体局部重构；已有待审候选 | 母体：同一独立 WT AF3 model 0。配体：独立 WT 对应 `ascr3_deprotonated/run_20260823_223248_3240812/poses.pdbqt` 的 MODE 1；转换保留重原子坐标并补氢。 |

本次直接核对三套原始 CIF 与各自 PDB 的重原子坐标一致；WT 原始 PDB 与保留的 aligned PDB 字节校验和相同。四个突变体原工作站输出路径来自 `selection.json`，其完整 `poses.pdbqt` 在本机交接包中的副本哈希逐项一致；没有声称访问原工作站。交接包未提供更早的 AF3 服务器任务 ID，因此不补写未知的生成者或提交时间。

## 两组的明确命名

已建立两个实际输入合同文件，文件名直接标出 lid 重构、各自 pose 和版本：

- [gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1.input.json](gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1.input.json)
- [gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1.input.json](gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1.input.json)

本轮生成的待审受体文件分别命名为：

- `gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb`
- `gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb`

这两个 PDB 已实际生成，保存在 [候选生成结果](../lid-rebuild-own-pose-20261005/README.md) 的 `review_candidates/` 中，合同记录了路径和 SHA256；两者均为静态筛选通过、尚待结构与能量复核的候选。`accepted_receptor_path` 与新 TPR 字段仍为空。配体文件沿同一 stem 保存；复合物和生产前缀属于后续命名规则，本轮尚未生成生产体系。

现存旧 `rebuilt_*` 曾使用共同 N84V 母体或跨组合 pose，不满足用户此前明确保留各自受体与 pose 的要求，继续停用。两组从各自母体重新进行局部 lid 建模，固定本组合配体和 lid 外坐标，保留全长序列、突变侧链及既定二硫键连接；具体约束见 [局部重建方法](../../../../../docs/modeling/gpr2-twf154-lid-local-rebuild.md)。

新候选须核对连接、手性、二硫键、接触及开口穿越，再重新最小化与平衡，生成新生产 TPR。原始版的检查点/轨迹不能接到新坐标上，也不抵扣新重构版生产时长。原始 E2 文件保留为历史证据；本次未修改远端作业。

两个合同已补全共同坐标系规则：V368R 原始 PDB 必须先按自己 `alignment.json` 的刚体变换恢复到该 pose 的 docking 坐标系；独立 WT 来源 PDB 已对齐。不能直接拼接处于不同坐标系的文件，也不能以“对齐”为名更换母体或挪动配体来消除冲突。

## WT–ascr18 保留的侧链修复

对象是 **Trp174（W174）侧链的朝向**。既有程序扫描 1,296 个 χ1/χ2 旋转组合，选中的变化为 χ1 **+160°**、χ2 **−30°**。这一步只改变 Trp174 的 17 个侧链原子（含氢）；主链、配体与其余 145,759 个原子的坐标保持不变。选择目的为减小起始非键合重叠，并非按配体亲和力选构象。

记录明确将其视为离散几何修复，随后仍需原力场最小化；它不是配体物理穿出 lid 的动力学过程，也不是整段 lid 主链重构。保留的是该修复后经 `attempt6_trp174_orientation/em.gro` 最小化及预热的分支。后续最小化/预热中原子当然会正常运动，不能把“修复步骤主链/配体不变”扩展到整个准备过程。

直接证据：[原始修复 JSON](../retained-20261005/provenance/trp174_orientation_repair.json)、[已选准备分支](../retained-20261005/cases.json)、[修复代码](../../../scripts/repair_twf154_trp_orientation.py)。

## 对测速与比较的影响

立即可做的调优先用 N84V–ascr18 原生产 TPR；双任务比较使用它的两个隔离副本，只测硬件吞吐，不称为独立科学重复。两组 ascr3 的新 lid 重构版准备好后，再用真实新 TPR 复核配置，不能把原始 V368R 速度标成新重构版实测。

原三档预算没有包含重新 lid 建模，其时间成本需另计；新输入的生产速度也需复核。在正式方法与比较中明确记录这两组采用重构 lid、WT–ascr18 做过侧链修复，避免把起点处理差异全部解释成突变或配体偏好效应。

所引：用户最新选择、原保留包、WT 修复 provenance、局部建模方法。被引：当前结果入口、INDEX、当天日志、下一轮上卡测速方案。
