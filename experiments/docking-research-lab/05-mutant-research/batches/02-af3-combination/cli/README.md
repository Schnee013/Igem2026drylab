# Gpr2：全长 AF3 预测后删除柔性片段，再做 Vina

## 当前实验定义（用户于 2026-09-10 澄清）

三组全部使用 **406 aa 全长序列**进行 AF3 预测：未作点突变的基线、N84A/L90A/R345A、V110A/R181A/W338A/V368A。
预测时保留所有残基，让模型在完整序列背景下生成结构。获得预测结构后，为对接移除原编号 1–21、164–178；剩余 370 个残基保留原编号和其余原子坐标。
这里 deltaN 是对接前的结构处理，不是提交 AF3 的截短序列构建体。全长预测也不意味着已经验证这些柔性片段的真实构象作用。

## 当前归档状态

当前原始数据位于 `vina/inputs/receptors/af3/gpr2_combination_20260909_1620/`，来自 `folds_2026_09_09_16_20.zip`。
`original_archives/` 保存 ZIP 和 SHA256；`original_cif/` 完整保留压缩包内容；`input_audit.json` 保存按本协议重新核对的结果。

- 三个任务均为正确的 406 aa 全长序列，全部 15 个模型的结构序列已核对通过。
- 正确输入位于 `fasta_full_length/`。三份 FASTA 均为 406 aa，仅指定位置发生点突变。
- 本批基线 model_0 与上一批逐字节相同。旧压缩包完整保留在独立目录；本命令默认使用最新这批。

## 用户运行的阶段

已有 `vina/src/` 继续负责 CIF 转换、刚体对齐、Meeko 制备、配置、Vina 和汇总。
本目录的 `trim_after_full_length_af3.py` 核对 job_request 与完整 406 aa 结构序列，再删除两个区段；不重新编号，不再次点突变。

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export AF3_OUT="$PWD/outputs/batches/02-af3-combination/run-01"
export AF3_ARCHIVE="$PWD/vina/inputs/receptors/af3/gpr2_combination_20260909_1620"
export DOCKING_PYTHON="/Users/yangruoxi/miniconda3/envs/docking/bin/python"
export VINA_EXE="/Users/yangruoxi/miniconda3/envs/docking/bin/vina"
unset AF3_CIF AF3_REQUEST
group="baseline"
```

各阶段分别执行：

```bash
bash outputs/batches/02-af3-combination/cli/commands.sh convert "$group"
bash outputs/batches/02-af3-combination/cli/commands.sh align "$group"
# 在 PyMOL 检查 alignment_review.pml，然后继续。
bash outputs/batches/02-af3-combination/cli/commands.sh prepare "$group"
bash outputs/batches/02-af3-combination/cli/commands.sh config "$group"
bash outputs/batches/02-af3-combination/cli/commands.sh dock "$group"
# 在 PyMOL 逐个 state 检查 review.pml。
bash outputs/batches/02-af3-combination/cli/commands.sh contacts "$group"
```

convert 输出 raw_model0.pdb（全长）、trimmed.pdb（删除后）、trimming.json。
align 将 trimmed.pdb 对齐到归档中原 deltaN model_0 的坐标系，输出 input.pdb、alignment.json 和 alignment_review.pml。
使用共同的 153 个 TM CA：30–50、62–83、101–126、144–163、182–201、326–346、358–380。刚体变换保留新预测模型的内部构象。
prepare 以各组自身 input.pdb 为几何参考，统一 Meeko/Gasteiger 制备。
dock 才启动 Vina，依次运行当前组的两种配体。基线可先独立完成，但比较须等待两个全长突变预测及对应对接结果。

## 处理两个组合突变体

基线各阶段完成后，将 group 改为另外两组，分别执行相同阶段。默认路径已指向本批全长预测，无需手动指定 CIF：

```bash
group="N84A_L90A_R345A"
# 完成后改为：group="V110A_R181A_W338A_V368A"
```

输入检查会拒绝任何不匹配预期全长序列的任务。若以后使用其他批次，可通过 AF3_ARCHIVE 或 AF3_CIF/AF3_REQUEST 指定；后两者必须指向同一组任务，当前应保持 unset。

## 参数与比较

三组固定使用 model_0，不依据 Vina 分数选择 AF3 模型。全部模型和任务种子保留备查。
Vina 参数与本轮固定侧链路线一致：center=(20,−20,5) Å，size=26³ Å，exhaustiveness=8，num_modes=9，energy_range=3，seed=1919，cpu=16，spacing=0.375，min_rmsd=1，max_evals=0。配体使用归档中的去质子化 PDBQT。
新模型对齐后需要人工检查共同框是否覆盖目标区域。num_modes 是输出上限。

六组对接及接触计算完成后：

```bash
bash outputs/batches/02-af3-combination/cli/commands.sh compare
bash outputs/batches/02-af3-combination/cli/commands.sh compare_contacts
```

AF3 路线比较各突变体相对自身全长预测后删减的基线；固定侧链路线保留独立结果。残基/pose 按任意接触 OR 后计一次。
组合实验不能分离单个位点贡献；AF3 结构差异还受预测采样影响，Vina 分数差不等于实验结合自由能变化。
