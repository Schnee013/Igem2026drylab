# 批次06：补充单突变

设计：R181K/Q、T106S/V、W338F/L，加全长WT baseline，共7个独立AF3任务。命名为06_r181k、06_r181q、06_t106s、06_t106v、06_w338f、06_w338l、06_baseline。原406 aa序列及R181/T106/W338已只读核验。

R181成对替换比较保留正电荷与中性侧链，T106比较保留/去掉羟基，W338比较保留/去掉芳香环；各替换同时改变几何，结果结合结构与接触解释。理由与历史证据见[分析建议](../../phase2-design/saturation-review-20260917.md)。

## 用户生成与校验

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI=outputs/batches/06-af3-supplement-singles/cli/prepare_fastas.py
"$DOCKING_PYTHON" "$CLI" generate && "$DOCKING_PYTHON" "$CLI" validate
```

输出：vina/inputs/receptors/fasta/06-af3-supplement-singles/。individual/含7份独立FASTA，文件名和标题均为06_名称；submission_jobs.tsv列出job名与路径；all_7.fasta为汇总查阅文件；checksums.json保留文件与manifest哈希。

预期FASTA PASS，核验406 aa、每个单突变仅一处指定替换、baseline与原序列相同、7个序列唯一、job命名和文件哈希。拒绝覆盖已有目录；报STOP时先返回输出。

每条全长蛋白独立提交，单拷贝。AF3网页Job name照submission_jobs.tsv填写；不要将汇总FASTA作为一个多链复合物。下载后返回ZIP路径，再生成归档、model_0转换、删段、对齐、制备、配置、Vina与最低分pose接触分析的分步CLI。

本批WT用于新增6个单点的批内比较。与批次05联合分析时保留两批WT及来源信息；在共同条件下比较主WT与来源WT敏感性，不能把两批不同WT得到的ΔS直接当作同一基准。历史R181A/T106A/W338A保留为锚定来源，若纳入统一比较需要同条件重对接。

状态：manifest、脚本已编写，来源预检通过；FASTA生成及AF3提交由用户执行。
