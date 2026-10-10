# 六组输入与出处

数据入口为 `compute/cases/<case_id>/case.json`；母体在 `compute/sources/`，各自 pose 为 case 内 `pose.sdf`。最初路径和 SHA256 在 `context/source_provenance.json`；该文件是来源快照，运行不依赖其本地路径。

| case_id | 母体 / pose 原始来源 | 接管时的材料与必要准备 |
|---|---|---|
| raw_n84v_ascr18 | N84V AF3 model 0；Docking 批次 05-af3-saturation-combinations/run-01/05_n84v/ascr18 的 MODE 1 | 原 lid；zero_start_100ns 为平衡后从零生产起点，prepared 保存原准备参考；先复核 |
| raw_n84v_ascr3 | 同一 N84V 母体；本组 ascr3 MODE 1 | 原 lid；prepared/hold.gro + hold.cpt，125 ps 预热后仍需 NPT |
| raw_v368r_ascr18 | V368R AF3 model 0；本组 05_v368r/ascr18 MODE 1 | 原 lid；prepared 的 125 ps 末态，仍需 NPT |
| native_wt_ascr18 | 独立 WT AF3 model 0；独立 WT ascr18_deprotonated/run_20260823_223248_3240812 MODE 1 | 自身 lid，实际采用 W174 侧链修复分支；prepared 的 125 ps 末态，仍需 NPT |
| v368r_ascr3_lid_rebuilt_own_pose_v1 | 自己的 V368R 母体；自己的 05_v368r/ascr3 MODE 1 | 新 lid candidate 12 精修第 3 轮；candidate/ 中 PDB，重新完整准备 |
| native_wt_ascr3_lid_rebuilt_own_pose_v1 | 独立 WT 自己的母体；独立 WT ascr3_deprotonated 对应运行 MODE 1 | 新 lid candidate 24 精修第 3 轮；candidate/ 中 PDB，重新完整准备 |

突变体来源交接包为 md-handoff-n84v-v368r，原母体 CIF 已带入 compute/sources。独立 WT 来自独立 AF3 CIF，不是从突变体回变。所有母体 406 aa，N 端和 lid 均保留。原 docking 使用删去 1–21、164–178 的受体，因此恢复全长后的几何问题必须复核。旧共享 N84V 骨架 rebuilt、回变 WT 和另一个旧 WT 200 ns 均不参与。

新 lid 仅重构 164–178，固定 163/179 与其余受体重原子；99–173 二硫键为沿用的建模假设；自己的配体 SDF 字节未变。静态初筛、原始几何和主链大幅改动的解释限制见 `context/lid_generation_snapshot.md`、各自 `evidence/candidate_manifest.json`。仅不碰撞和 linking number 为 0 不构成完整验收；不得为通过检查换骨架、换 pose 或扩大可动区域。

WT–ascr18 的修复是 W174 侧链旋转 χ1 +160° / χ2 −30°，修复步骤只改变 17 个侧链原子；后续最小化/预热正常允许原子运动。此组必须沿用已选 prepared 分支，不能拿母体 PDB 直接重做来抹掉修复。它与整段 lid 主链重构不同。

## 新 lid 重建支持材料

每组 `reference/original_dry.gro` 只用于自身母体到原膜坐标系的刚体映射、自己的配体和 POPC 参考；其中旧蛋白不能作为新生产输入。`reference/docking_to_dry.json` 来自蛋白 lid 外主链拟合，未对配体单独拟合。`reference/parent_docking_frame.pdb` 是固定区比较基准。

`rebuild_support/` 的拓扑来自该组自己的原体系，序列与化学模型一致，可用于原子身份对照；新坐标必须重新补氢/校验拓扑。不能把原预热末态的 lid 替换几个坐标后称为已平衡，更不能接原始版的生产检查点。

`compute/configs/ligand_geometry_contract.json` 是为自包含交接重新导出的检查合同：由各自原 SDF、已核对的一对一 SDF→ITP 原子映射、键图和手性生成。原六组坐标核对的映射见各组 reference/pose_atom_map.json。它不是丢失的旧远端文件的冒名副本。

注意 GRO 残基编号会在不同分子块复用，必须按 PROA 原子数与配体 ITP 原子数定位，不能简单用 residue ≤406 把脂质一起选成蛋白。蛋白 ILE CD1/CD 和 C 末端 O/OXT 与 OT1/OT2 的命名需显式映射；末端氧的常规建模位移须记录，不能藏在整体 RMSD 中。
