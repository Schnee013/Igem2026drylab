# 批次07：用户分步执行全流程

20受体=19个W338单突变＋baseline；40次双配体对接。原始ZIP已只读检查20任务/100模型。新增脚本已通过语法/导入检查，以下科研步骤由用户执行。每个代码块成功后才进入下一步；STOP、Traceback或非零退出时保留现场。明确完成并核验过的步骤可跳过；已有部分输出不能直接当作完成，也不要加覆盖参数。

## 0. 终端环境

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI=outputs/batches/07-af3-w338-saturation/cli
CONTACTS=outputs/batches/03-af3-single-alanine/cli/top1_contacts.py
BASE=outputs/batches/07-af3-w338-saturation/run-01/07_baseline
```

## 1. 归档

核验ZIP、406 aa序列和model_0–4后归档，保留原ZIP、CIF、请求和FASTA副本。

```bash
"$DOCKING_PYTHON" "$CLI/archive_results.py"
```

预期：ARCHIVE PASS: 20 jobs, 100 full-length models。目录：vina/inputs/receptors/af3/gpr2_batch07_20260918/。

## 2. 转换与删段

默认取model_0转PDB；W338C按下述已记录的恢复流程改用model_1。核验全长后删除原1–21、164–178，保留370残基及原编号。

```bash
"$DOCKING_PYTHON" "$CLI/convert_received.py" baseline &&
"$DOCKING_PYTHON" "$CLI/convert_received.py" all-mutants
```

预期预检分别1/19 jobs，共20条CONVERT/TRIM PASS，均406 -> 370。

## 3. 统一坐标

选既定七段跨膜区153个CA，刚体对齐至共同参考，保留对齐前后文件。

```bash
"$DOCKING_PYTHON" "$CLI/align_received.py" baseline &&
"$DOCKING_PYTHON" "$CLI/align_received.py" all-mutants &&
"$DOCKING_PYTHON" "$CLI/check_alignments.py"
```

预期20条ALIGN PASS，CA=153；末尾检查显示ALIGNMENT AUDIT PASS: 20 receptors并按RMSD由大到小列出结果。RMSD不是自动合格阈值。

在PyMOL检查baseline、偏差最大者及W338G/P。每次加载会清空上个视图；灰色参考、青色本批结构、黄色338位。不要再次align。若明显错位或局部变形，返回截图后再继续该结构的处理。

```pymol
@/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_baseline/alignment_review.pml
```

将路径中的07_baseline替换为相应名称，例如07_w338p、07_w338g。

## 4. 受体制备

Meeko/Gasteiger生成PDBQT、receptor.json和prepared.pdb，并核验序列、编号、重原子坐标。

```bash
"$DOCKING_PYTHON" "$CLI/prepare_received.py" baseline &&
"$DOCKING_PYTHON" "$CLI/prepare_received.py" all-mutants
```

预期20条PREPARE PASS，370 residues。环境应与前批一致：Meeko 0.7.1、RDKit 2025.9.5；若版本变化先返回输出。出错检查对应受体的preparation.log。

## 5. 对接配置

每个受体分别配置ascr3/ascr18。固定中心(20,-20,5)、尺寸26³ Å、exhaustiveness=8、num_modes=9、energy_range=3、seed=1919。

```bash
"$DOCKING_PYTHON" "$CLI/configure_received.py" generate &&
"$DOCKING_PYTHON" "$CLI/configure_received.py" validate
```

预期CONFIG PASS: 40 configurations，输入绝对路径及哈希一致。

## 6. Vina

Vina 1.2.5，2任务并行×每任务4线程；spacing=0.375、min_rmsd=1、max_evals=0。保持电脑唤醒。每次保留stdout/stderr、run.json、poses、summary及校验记录。报错后停止分派新任务，已在运行的任务会收尾。

```bash
"$DOCKING_PYTHON" "$CLI/dock_received.py" baseline --workers 2 --cpu 4 &&
"$DOCKING_PYTHON" "$CLI/dock_received.py" all-mutants --workers 2 --cpu 4
```

预期BATCH PASS: 2 docking tasks completed以及BATCH PASS: 38 docking tasks completed。每次1–9个poses，实际最低分及MODEL以输出为准。

## 7. 评分核验

核验40个任务的哈希、参数、日志与pose评分一致性；按最低评分选pose，同分取最低MODEL。以本批WT计算ΔS3、ΔS18、D=ΔS18−ΔS3。

```bash
"$DOCKING_PYTHON" "$CLI/audit_scores.py" --write-report
```

预期AUDIT PASS: 40 runs；Nonempty stderr logs: 0。如非零，检查所列日志再继续。报告：run-01/score-audit/scores.md及scores.json。该写报告命令拒绝覆盖；重复只读核验去掉--write-report。

## 8. 最低分pose接触

先分析两个WT pose，再处理38个突变体pose。ProLIF 2.1.0、vicinity_cutoff=6 Å、九种既定接触类型。6 Å是邻域范围。配体从Meeko元数据恢复，核对电荷−1及序列化坐标保持。

```bash
"$DOCKING_PYTHON" "$CONTACTS" --run-dir "$BASE/ascr3" &&
"$DOCKING_PYTHON" "$CONTACTS" --run-dir "$BASE/ascr18" &&
"$DOCKING_PYTHON" "$CLI/contacts_received.py"
```

预期baseline各输出Selected Vina mode ...; analyzed one pose；突变体最后BATCH PASS: 38 mutant minimum-pose contact analyses completed。MDAnalysis的已知DeprecationWarning可伴随成功输出；其他报错应检查。结果位于各配体目录top1_contacts/，突变体日志为top1_contacts.log。

## 9. 四格比较

核验40个最低分pose和接触表，按原编号＋接触类型比较WT/突变体×#3/#18，残基身份变化另列。

```bash
"$DOCKING_PYTHON" "$CLI/compare_contacts_received.py"
```

预期CONTACT AUDIT PASS: 40 lowest-pose analyses; 19 four-way comparisons。报告：run-01/contact-comparison/four-way.md及four-way.json。此步骤拒绝覆盖已有报告。

## 10. 候选pose可视化与返回

在PyMOL使用某个结果生成的view_contacts.pml检查配体位置；例如W338F–#18：

```pymol
reinitialize
@/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338f/ascr18/top1_contacts/view_contacts.pml
deselect
```

完成后返回AUDIT PASS、CONTACT AUDIT PASS以及任何警告或结构异常。评分与接触数是待计算结果，本说明不预设数值。随后结合本批全部W338替换与既有单点结果分析，保留跨批WT敏感性。

## W338C制备失败后的恢复（2026-09-18）

model_0的ARG181 NH1–ARG345 NH1距离1.5568 Å，Meeko报告异常跨残基键。model_1全长406 aa序列一致，该距离3.1838 Å；非相邻残基间重原子距离<1.8 Å筛查未发现其他近接触。该筛查不替代完整结构质量验证。model_1按结构质量在对接前选取，不按对接分数挑选。

以下由用户执行：保存失败model_0目录至diagnostics/07_w338c-failed-model0，并生成独立模型选择记录manifests/w338c-model-selection.json。原received-af3.json和原始AF文件保留；失败报告原有路径仅表示历史位置，迁移映射和文件哈希记录在模型选择文件中。

```bash
"$DOCKING_PYTHON" "$CLI/recover_w338c.py" --check-only &&
"$DOCKING_PYTHON" "$CLI/recover_w338c.py" &&
"$DOCKING_PYTHON" "$CLI/convert_received.py" W338C &&
"$DOCKING_PYTHON" "$CLI/align_received.py" W338C
```

预期RECOVERY PREFLIGHT PASS、RECOVERY STAGED、CONVERT/TRIM PASS（406 -> 370）、ALIGN PASS（153 CA；RMSD以实际结果为准）。检查新alignment_review.pml后执行：

```bash
"$DOCKING_PYTHON" "$CLI/prepare_received.py" W338C &&
"$DOCKING_PYTHON" "$CLI/prepare_received.py" baseline --resume --check-only &&
"$DOCKING_PYTHON" "$CLI/prepare_received.py" all-mutants --resume --check-only
```

预期W338C PREPARE PASS，随后20个SKIP VERIFIED，待制备数均为0。然后从第5步继续，仍为20受体、40次对接。评分报告单独记录af_model；AF model_1与Vina最低分pose的MODEL互不相同。任一步STOP则保留现场，不进入下一步。
