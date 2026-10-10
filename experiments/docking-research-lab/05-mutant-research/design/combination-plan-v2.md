# 双突变方案 v2：18个组合＋新WT，复用单点结果

状态：用户已确定08轮执行范围。v1的18个双突变及模块A–F保持不变；本版替代v1中重新预测14种单点母本的建议。

## 本轮计算范围

- 新增16个核心双突变＋2个探索双突变＋08_baseline，共19个全长AF任务。
- 本轮首个seed需38次双配体对接；单点不新增AF或对接任务。
- N84/V110/V368母本沿用05批已完成结果，W338母本沿用07批已完成结果。06的W338F/L仅保留为历史敏感性参照。
- 序列均为406 aa全长；AF预测后按既定协议删段、对齐、制备。主统计仍只取最低分pose，D=ΔS18−ΔS3。

完整18个组合的名单和模块理由见[方案v1第2节](combination-plan-v1.md#2-完整双突变名单)。当前执行清单以[08批af-inputs.json](../batches/08-af3-double-mutants/manifests/af-inputs.json)为准，其中记录母本复用来源；旧double-mutants.json保留以验证已生成的18份FASTA。

## 结果比较

组合主结果以08-WT计算ΔS和D。母本保留原始评分和来源WT结果，并可另列按08-WT换算的算术敏感性；不把来源WT不同的ΔS直接相加计算非加和残差。

若计算ε_i，应在明确的共同WT基准下使用S_i(AB)−S_i(A)−S_i(B)+S_i(WT)，并标明A/B是复用的历史结构和结果。该值用于探索评分非加和性，包含结构来源差异；新WT不能消除这些差异。评价同时呈现目标配体评分和两配体差异，不强制重跑单点作为下一步前提。

## FASTA补充方式

已有18份FASTA及checksums.json保留。用户运行add_baseline.py添加individual/08_baseline.fasta、all_19.fasta、submission_jobs_19.tsv及checksums_19.json。每份individual文件单独提交单体AF任务。

版本历史：v1保留最初完整重预测对照提案；v2记录用户确定的复用方案。后续有实质修改再新增版本。
