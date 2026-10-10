# 批次08：18个双突变的AF3与Vina流程

当前方案：[v3](../../phase2-design/combination-plan-v3.md)。16个核心组合＋2个探索组合；WT及亲本单点复用已有结果。序列定义为`manifests/double-mutants.json`，归档后实际输入记录为`manifests/received-af3.json`。`af-inputs.json`及`cli/add_baseline.py`保留为历史补WT提案，当前运行使用18个双突变。

ZIP：`/Users/yangruoxi/Downloads/folds_2026_09_18_08_05.zip`。已完成只读检查：18任务、90份全长模型，序列/编号/CRC均通过。以下归档与科研计算由用户执行。遇到STOP即停止，保留现场；脚本拒绝覆盖既有输出。

## 0. 设置环境

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI="$PWD/outputs/batches/08-af3-double-mutants/cli"
```

## 1. 校验并归档AF3结果

保存ZIP、全部CIF、job请求和提交FASTA，生成接收清单。归档目录为`vina/inputs/receptors/af3/08-af3-double-mutants/`。

```bash
"$DOCKING_PYTHON" "$CLI/archive_results.py"
```

预期：`ZIP AUDIT PASS: 18 jobs, 90 full-length models; sequences, numbering and CRC verified.`，然后`ARCHIVE PASS: 18 jobs, 90 full-length models; all sequences and numbering verified.`。

## 2. model_0转PDB并删段

核验406 aa全长，再删除原1–21、164–178，保留370残基及原编号。输出到本批`run-01/08_<组合>/`。

```bash
"$DOCKING_PYTHON" "$CLI/convert_received.py" all-mutants
```

预期：`PREFLIGHT PASS: 18 jobs`，18行`CONVERT/TRIM PASS: 08_<组合>; 406 -> 370 residues; original numbering retained`。

## 3. 刚体对齐并检查

以既定七段TM的153个CA对齐共同参考，不改变蛋白内部几何；复用同一对接盒坐标系。

```bash
"$DOCKING_PYTHON" "$CLI/align_received.py" all-mutants &&
"$DOCKING_PYTHON" "$CLI/check_alignments.py"
```

预期18行`ALIGN PASS: ...; CA=153; RMSD=... A`；`ALIGNMENT AUDIT PASS: 18 receptors; 153 matched CA each; all hashes verified`。RMSD是检查线索，不设自动合格阈值。查看偏差较大者及双突变局部。

PyMOL示例（其他组合替换目录名；脚本标记该组合的两个突变位点）：

```pml
@/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_n84y_v368r/alignment_review.pml
zoom target_sites, 10
```

## 4. 制备受体

Meeko/Gasteiger生成receptor.pdbqt、receptor.json、prepared.pdb，校验序列、原编号、重原子坐标。

```bash
"$DOCKING_PYTHON" "$CLI/prepare_received.py" all-mutants
```

预期Meeko 0.7.1、RDKit 2025.9.5；`PREFLIGHT PASS: 18 preparation jobs`；18行`PREPARE PASS: ...; 370 residues; sequence, numbering and heavy-atom coordinates verified`。失败时查看指出的preparation.log，不跳过错误继续配置。`--resume`只跳过哈希仍匹配的成功任务，失败残留需检查后处理。

## 5. 生成并校验36份配置

两配体均使用历史−1电荷PDBQT；中心(20,−20,5)，尺寸26³ Å，exhaustiveness=8、num_modes=9、energy_range=3、seed=1919。

```bash
"$DOCKING_PYTHON" "$CLI/configure_received.py" generate &&
"$DOCKING_PYTHON" "$CLI/configure_received.py" validate
```

两次均预期`PREFLIGHT PASS: 18 receptors, 2 ligands, 36 configurations`和`CONFIG PASS: 36 configurations; absolute input paths, frozen parameters and hashes verified`。

## 6. 运行Vina

2任务并行、每任务4CPU，最多8线程；Vina v1.2.5，spacing=0.375、min_rmsd=1、max_evals=0。保存全部pose，主统计取最低分，同分取最小MODEL。

```bash
"$DOCKING_PYTHON" "$CLI/dock_received.py" all-mutants --workers 2 --cpu 4
```

预期`PREFLIGHT PASS: 36 docking tasks; workers=2; cpu/task=4; max threads=8; Vina v1.2.5`；36行`DOCK PASS: ...; poses=...; best=...; MODEL=...`；`BATCH PASS: 36 docking tasks completed`。pose数可为1–9；分数与MODEL以实际结果为准。

## 7. 最低分pose接触分析

每次对接只分析一个最低分pose，按Meeko元数据恢复配体化学信息，使用ProLIF 2.1.0和既定9类接触。

```bash
"$DOCKING_PYTHON" "$CLI/contacts_received.py" &&
"$DOCKING_PYTHON" "$CLI/audit_results.py"
```

预期`PREFLIGHT PASS: 36 mutant contact tasks; ProLIF 2.1.0; one minimum-score pose each`；36行`CONTACTS PASS`；`BATCH PASS: 36 mutant minimum-pose contact analyses completed`；最终`FINAL AUDIT PASS: 18 double mutants; 36 docking results; 36 minimum-pose contact analyses; hashes verified`。

每种配体的`top1_contacts/`保存最低分pose、接触表与`view_contacts.pml`。AF model_0和Vina的MODEL编号独立记录。D=ΔS18−ΔS3的汇总使用明确的既有WT来源，并保留来源敏感性；运行阶段保留原始评分。
