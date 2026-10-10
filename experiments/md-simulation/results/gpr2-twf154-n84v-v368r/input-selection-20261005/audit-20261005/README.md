# 六组受体、lid 与配体 pose 的文件和坐标审查

> Source: 当前 selection/两个重构合同，保留包的原始结构、pose、装配坐标、拓扑、已选 EM/预热末态、manifest、W174 修复前后坐标及制备源码。
> As of: 2026-10-05，本地逐文件与坐标审查；本次没有新的远端运行观察。
> Allowed use: 判断输入身份、骨架/lid 来源、配体相对位置与文件可用性；不证明几何合理、平衡完成或机制成立。
> Update trigger: 新重构坐标生成/验收、当前选用文件或来源发生变化。

**当前四组沿用的原始输入来源匹配；两组新选的 lid 重构版尚无坐标文件，六组不能整体宣布准备完成。** 对保留的六个原始装配文件逐原子核对，受体均来自各自母体，lid 也来自同一母体；各配体均对应本组合指定的 top1。旧混杂 `rebuilt_*` 的确曾借用 N84V 骨架和共享 pose，当前选择表已排除，不能改名作为新候选。

## 1. 六组到底引用什么文件

下面所有相对路径的 `R` 表示 [retained-20261005](../../retained-20261005/README.md)。三套完整受体均为 406 位、model 0，N 端和 lid 都存在：

- **N84V 母体**：[sources/n84v/af3_original/raw_model0.pdb](../../retained-20261005/sources/n84v/af3_original/raw_model0.pdb)，对应同目录 `fold_gpr2_b05_fl_n84v_model_0.cif`；序列相对本轮 WT 仅 N84V。
- **V368R 母体**：[sources/v368r/af3_original/raw_model0.pdb](../../retained-20261005/sources/v368r/af3_original/raw_model0.pdb)，对应同目录 `fold_gpr2_b05_fl_v368r_model_0.cif`；序列相对本轮 WT 仅 V368R。
- **独立 WT 母体**：[sources/native_wt/full_length.pdb](../../retained-20261005/sources/native_wt/full_length.pdb)，实际软链接目标为 Docking 的 `inputs/receptors/af3/pdb/gpr2_twf154_wt/wt_aligned/gpr2_twf154_wt_model_0_aligned.pdb`；序列与本轮 FASTA 一致，不是 N84V 回变，也不是旧 200 ns WT。

| 比较组合 | 当前受体选择 | 自己的配体文件，均为 top1 / MODE 1 | 本次结论 |
|---|---|---|---|
| N84V–ascr18 | N84V 母体，原始 lid | [n84v/ascr18/top1.sdf](../../retained-20261005/sources/n84v/ascr18/top1.sdf) | 原始装配来源吻合 |
| V368R–ascr3 | V368R 母体，仅重构自身 lid；新 PDB 未生成 | [v368r/ascr3/top1.sdf](../../retained-20261005/sources/v368r/ascr3/top1.sdf) | 母体/pose 已锁定；新 lid 待验收 |
| N84V–ascr3 | N84V 母体，原始 lid | [n84v/ascr3/top1.sdf](../../retained-20261005/sources/n84v/ascr3/top1.sdf) | 原始装配来源吻合 |
| V368R–ascr18 | V368R 母体，原始 lid | [v368r/ascr18/top1.sdf](../../retained-20261005/sources/v368r/ascr18/top1.sdf) | 原始装配来源吻合 |
| 独立 WT–ascr18 | 独立 WT 母体；沿既有 W174 侧链修复分支，lid 主链未重构 | [native_wt/ascr18/top1.sdf](../../retained-20261005/sources/native_wt/ascr18/top1.sdf) | 原始装配与侧链修复范围均核实 |
| 独立 WT–ascr3 | 独立 WT 母体，仅重构自身 lid；新 PDB 未生成 | [native_wt/ascr3/top1.sdf](../../retained-20261005/sources/native_wt/ascr3/top1.sdf) | 母体/pose 已锁定；新 lid 待验收 |

原始装配文件统一为 `R/data/preparation_inputs/<原组合标识>/dry.gro`，包含受体、该组配体与膜；并非直接把来源 PDB 作为生产坐标。当前保存的最小化和预热分支如下：

| 原组合标识 | 已选 EM，位于 `R/data/preheat/<标识>/` | 预热末态 | 当前用途 |
|---|---|---|---|
| raw_n84v_ascr18 | `attempt2_double/em.gro` | `heating_v4/hold.gro` | 沿原来源 |
| raw_v368r_ascr3 | `em.gro` | `heating_v4/hold.gro` | 原始版历史证据，不能代替新重构版 |
| raw_n84v_ascr3 | `attempt4_ligand_constraints/em.gro` | `heating_v4/hold.gro` | 沿原来源 |
| raw_v368r_ascr18 | `attempt5_frozen_ligand/em.gro` | `heating_v4/hold.gro` | 沿原来源 |
| native_wt_ascr18 | `attempt6_trp174_orientation/em.gro` | `heating_v4/hold.gro` | 沿 W174 侧链修复来源 |
| native_wt_ascr3 | `em.gro` | `heating_v4/hold.gro` | 原始版历史证据，不能代替新重构版 |

这些 EM 分支名称记录的是准备历史，不能据此推定生产阶段仍有同名限制。已选 EM/hold 坐标哈希均符合原 `cases.json`，蛋白和配体原子顺序、身份及完整序列一致。最小化/预热后的正常坐标变化没有被错误地要求等于母体。125 ps 预热仍不等于完成生产前平衡；本次没有重新验收生产 TPR 或检查远端当前进度。

## 2. 骨架与 lid 是否匹配：实际坐标证据

对照对象为自己的完整受体与最小化前的 `dry.gro`。按 lid 外共同主链原子作一次刚体拟合，将**同一变换**用于 lid 和配体，不分别拟合它们。否则可能掩盖环被替换或配体位置被挪动。

| 原始装配组合 | lid 外主链 RMSD，Å | lid 主链 RMSD，Å | 指定 pose 的配体重原子 RMSD，Å |
|---|---:|---:|---:|
| N84V–ascr18 | 0.005050 | 0.004841 | 0.004733 |
| V368R–ascr3，原始版 | 0.005014 | 0.005442 | 0.004336 |
| N84V–ascr3 | 0.005050 | 0.004841 | 0.005164 |
| V368R–ascr18 | 0.005014 | 0.005442 | 0.004856 |
| 独立 WT–ascr18，侧链修复前 | 0.004956 | 0.004927 | 0.004875 |
| 独立 WT–ascr3，原始版 | 0.004956 | 0.004927 | 0.005220 |

每组比较 1,563 个 lid 外共同主链原子、60 个 lid 主链原子；排除下面单列的 C 末端两个氧后，也比较了全部受体重原子，最大偏差小于 0.009 Å。配体全部原子建立一一对应，拓扑的键连接图也与 SDF 一致。这里只验证连接关系，没有重新据此判定配体能量或起点几何合格。

约 0.005 Å 的差异符合 GRO 以 0.001 nm 写坐标的舍入量级。程序使用 0.02 Å 作为文件身份核对的操作容差，不是文献支持的科学几何验收阈值。换用另一个母体作同样的主链拟合，RMSD 为 6.84–9.25 Å；这里只作为排除错误来源的对照，不能解释为功能差异。

**保留的例外：C 末端氧有局部变化。** GLY406 的 PDB `O/OXT` 对应 GRO `OT1/OT2`。N84V 的偏移约 0.421/0.408 Å，V368R 为 0.378/0.345 Å，WT 为 0.425/0.374 Å。它们明确从“坐标不变”统计中分出；其余重原子均吻合。该现象与 [蛋白拓扑脚本](../../../../scripts/prepare_twf154_protein_topologies.sh) 中的 `pdb2gmx -ter` 端基处理相容，但保留包没有该步原始日志，因此具体生成机制属于推断，不当作已重现的日志事实。这项局部差异不支持整个骨架或 lid 被另一个母体替换。

蛋白原子来自输入合同指定的分子块，配体来自其后的独立分子块；没有仅按 GRO 残基号选取，因为膜分子会重复使用某些残基号。残基 ILE 的 `CD1→CD` 等命名变化有显式映射。

## 3. 坐标系检查与新合同补全

突变体来源 `raw_model0.pdb` 是 AF3 原始坐标，自己的 `top1.sdf` 已经位于 docking 坐标系。先按本突变体的 `alignment.json` 对整个原始全长受体作 `xyz_docking = xyz_AF3 @ R + t`，再与配体共同放入膜中。独立 WT 的来源 PDB 已对齐，初始变换为恒等。

按记录恢复后，两个突变体与各自实际 docking receptor 的共享重原子最大误差小于 0.00084 Å；独立 WT 共享原子完全相同。Docking 受体相对全长母体缺少的残基正好为 1–21 与 164–178。**恢复自己原来被删掉的 lid 证明来源匹配，不等于恢复后与 pose 的空间关系合理。** 尤其两组 ascr3 的已知穿过开口问题没有因本次身份核对而消失。

本次在两个新合同中补齐 `coordinate_frame_contract`，防止后续把 raw PDB 与已对齐 SDF 直接拼接。整体刚体对齐没有改变内部骨架，也没有移动 pose 来逃避冲突。后续候选的“lid 外与配体固定”以共同坐标系下的原始复合物为参考。

## 4. WT–ascr18 的 W174 修复已做前后文件对照

直接比较保留的 [修复前 ionized.gro](../../retained-20261005/data/preheat/native_wt_ascr18/attempt6_trp174_orientation/ionized.gro) 与 [sidechain_repaired.gro](../../retained-20261005/data/preheat/native_wt_ascr18/attempt6_trp174_orientation/sidechain_repaired.gro)，两者哈希都符合 [修复记录](../../retained-20261005/provenance/trp174_orientation_repair.json)。

145,776 个原子中，仅 W174 的 17 个侧链原子改变（9 个重原子、8 个氢），其余 145,759 个坐标逐项相同。主链、Cβ 和配体均不变。因此这一步不是借用其他骨架，也不是重构整段 lid。随后最小化/预热允许正常运动，不能将这一结论扩展为末态还保持原始侧链/主链坐标。

## 5. 是否发生过“拿别的骨架替换重建”

**旧分支发生过，当前原始六组坐标没有发现，两个新的重构版尚不能检验。**

- [旧矩阵生成代码](../../../../scripts/prepare_twf154_lid_matrix.py) 第 132–135 行：`raw_wt` 从 N84V 回变；`rebuilt_wt`、`rebuilt_v368r` 从共同 `rebuilt_n84v` 派生。这不是独立 WT/V368R 的各自母体。
- 同一代码第 145–148 行：旧重构分支的 ascr18 统一用 N84V pose，ascr3 统一用 V368R pose。与本轮“每组自己的 pose”不符的组合不能沿用。
- 这些旧文件不属于当前选择。错误经过见 [停用记录](../../../../../../docs/modeling/gpr2-twf154-input-design-error.md)。本次没有重新取得旧临时目录的实体坐标，旧分支判断依据为直接制备代码与保留记录；上面数值表只针对实际存在的六个原始装配。
- [膜装配代码](../../../../scripts/build_twf154_membrane_inputs.py) 只从旧膜模板提取 POPC，受体和配体由各自病例输入组成。复用膜并不等于复用旧受体；本次坐标核对亦支持这一点。

两个新版本的预定受体名为：

- `gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb`
- `gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb`

两者在当前输入目录均不存在，合同的 `accepted_receptor_path` 与生产 TPR 仍为空；本次没有生成空壳文件。应先各自重建 164–178，检查固定区与配体不变、两端连接、二硫键、手性、接触和穿越关系，再重新准备。现阶段不能批准这两组新结构为“骨架/lid 已匹配”，也不能拼接原始版的检查点。

## 6. 可复核产物

- [per_case.csv](per_case.csv)：六组实际来源、装配/EM/预热路径、当前选用状态及逐组数值，适合直接查表。
- [audit.json](audit.json)：完整坐标统计、原子映射、SHA256 与软链接实际目标、序列、跨母体对照、W174 前后差异、新文件缺失状态。
- [audit_inputs.py](audit_inputs.py)：本地只读来源核验，Python/NumPy 精确版本记录在 JSON；不运行 MD 或重建结构。

从仓库根目录复核（输出写临时目录）：

```bash
python3 experiments/md-simulation/results/gpr2-twf154-n84v-v368r/input-selection-20261005/audit-20261005/audit_inputs.py \
  --retained experiments/md-simulation/results/gpr2-twf154-n84v-v368r/retained-20261005 \
  --selection experiments/md-simulation/results/gpr2-twf154-n84v-v368r/input-selection-20261005 \
  --output /private/tmp/gpr2-input-audit-repeat
```

程序通过表示上述身份和缺失状态得到复核；JSON 明确保存 `all_six_selected_coordinates_ready: false`。它不是一个“六组可以立即生产”的通行判定。合同或新结构改变后，需要更新审查，不能继续引用旧结论。

所引：当前选择合同、原保留包、WT 修复前后文件、制备代码和旧分支停用记录。被引：输入选择 README、项目 INDEX、2026-10-05 日志。原始保留输入未覆盖；本次没有连接远端、运行付费任务、提交或推送 Git。
