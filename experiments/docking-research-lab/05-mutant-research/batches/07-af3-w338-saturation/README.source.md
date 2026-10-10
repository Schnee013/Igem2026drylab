# 批次07：W338完整饱和单突变

本批重新预测W338其余19种天然氨基酸替换（含A/F/L），加全长WT，共20个独立AF3任务。批次06的F/L及WT保留为历史来源对照。

原406 aa序列及338=W已核验。manifest为manifests/w338-saturation.json，同时记录批次06的F/L和WT来源映射。各任务名称为07_w338a等，WT为07_baseline。每个任务一条全长蛋白、单拷贝；全长AF后才删除柔性段。

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI=outputs/batches/07-af3-w338-saturation/cli
"$DOCKING_PYTHON" "$CLI/prepare_fastas.py" generate &&
"$DOCKING_PYTHON" "$CLI/prepare_fastas.py" validate
```

输出目录：vina/inputs/receptors/fasta/07-af3-w338-saturation/。individual/中每份文件名与FASTA标题均为AF job名；submission_jobs.tsv为提交对照；all_20.fasta用于汇总查阅，不作为单个多链任务提交。

预期FASTA PASS: 20 unique full-length sequences。校验全长、准确单点差异、覆盖与唯一性、job名和哈希。拒绝覆盖已有目录；遇STOP保留现场并返回输出。

用户生成并提交，下载后返回ZIP路径，再提供归档、转换删段、对齐、受体制备、Vina和最低分pose接触分析CLI。当前仅完成manifest、脚本和只读预检。

19种突变均使用本批WT进行批内比较。跨批次复查F/L时另列06-WT与07-WT敏感性，保留来源标记。D=ΔS18−ΔS3；每次只取最低分pose，多pose为参考。
