# Phase2分析：阅读报告、完整数据与补充证据

这里汇总批次04–08的分析结果，原始对接输出在outputs/batches。顶层Markdown报告供日常阅读；data保存完整汇总，supporting-evidence保存专项证据。

## 从哪里开始看

| 文件 | 回答的问题 |
|---|---|
| [双突变模块分析](double-mutant-analysis.md) | 08轮组合相对两个亲本新增了什么？接触和姿态怎样解释收益或抵消？ |
| [双突变评分与亲本比较](double-mutant-scores.md) | 18个组合的评分、统一WT、亲本差值、非加和残差与配体坐标变化是多少？ |
| [单突变候选与WT接触对照](single-mutant-contact-candidates.md) | 哪些单突变值得进一步检查？相对同批WT增加、丢失哪些接触？先画哪些二维图？ |
| [突出单突变的实验角色](single-mutant-roles.md) | 哪些单点承担改善目标、削弱另一配体或共同改善的作用？如何选组合母本？ |
| [单突变结果分析](single-mutant-analysis.md) | 哪些突变值得关注？评分与接触变化如何解释？ |
| [全部单突变评分](single-mutant-scores.md) | 某个突变具体得分多少？不同批次结果分别是什么？ |
| [四位点饱和统计](saturation-statistics.md) | N84、V110、V368、W338各19种替换表现如何？ |
| [已有组合数据](data/combination-mutants.json) | 已完成的组合结果是什么？保留04批三突变，并纳入08批18个双突变。 |

全部单突变表含99条结构记录、87种设计及4个来源WT；相同设计跨批次分别保留。饱和统计从中选05的三个核心位点和07的W338，共76种替换。它是同一完整数据中的选定范围。

## 需要查细节时

- [data/single-mutants.json](data/single-mutants.json)：完整单突变评分、逐残基接触、相对WT变化、基线敏感性、模型和来源哈希。
- [data/combination-mutants.json](data/combination-mutants.json)：已有组合的完整记录。
- [多pose补充证据](supporting-evidence/multi-pose-contacts/README.md)：04批已有pose评分、接触频次及逐pose配体/指纹文件。
- [R181A原子级核验](supporting-evidence/r181a-atomic-contacts/audit.json)：04批232行原子接触及来源校验，原表为同目录atomic_contacts.csv。

这些补充证据用于追查分析依据；主统计仍为每次最低分pose，其他pose不作为独立重复。

## 汇总脚本与使用范围

[summarize.py](summarize.py)读取04–07各批run-01已完成的受体结果，生成单突变评分/统计报告并维护历史组合JSON；保留08批已汇总组合记录。解释稿由人工维护。`--check-only`仅核验，无此参数则更新派生汇总。它不运行AF、结构制备、Vina或ProLIF；遇到缺失或校验失败的结果会停止。新增run或多seed前需扩展显式运行选择。

主键保留batch/run/variant/AF_model/seed，来源WT分开；D=ΔS18−ΔS3。04使用cpu=16，05–07使用cpu=4；W338C使用AF model_1的结构质量例外保留。历史绝对路径保持在原始输出中，当前脚本从实际批次目录读取。

路径迁移见[整理清单](../file-organization/analysis-reorganization.json)；后续组合方案见[设计讨论入口](../phase2-design/README.md)。


[analyze_double_mutants.py](analyze_double_mutants.py)读取08批18个组合及既有14个亲本、05/07-WT，核验原始评分/接触与来源哈希，更新`data/combination-mutants.json`和`double-mutant-scores.md`。它只汇总已有结果、计算评分差值及既有SDF重原子坐标差，不调用AF、制备、Vina或ProLIF；`double-mutant-analysis.md`为解释报告。08批统一以05-WT为主参照、07-WT为敏感性参照，组合相对亲本差值不依赖共同WT。历史04组合仍保留自己的WT定义。
