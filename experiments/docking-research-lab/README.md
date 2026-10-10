# Docking Research Lab工作交付

本项目整理受体对接研究的文献、基础比较和Gpr2突变结果。交付重点是批次01–08：从结构路线比较和单点筛选，逐步发展为四位点饱和面板及18个双突变的亲本比较。

原始结构、pose、日志及输入通过飞书附件恢复；直接阅读说明与分析表可从下列任务开始。详见[数据恢复](DATA_DELIVERY.md)。

## 推荐阅读顺序

先读[突变研究总览](05-mutant-research/README.md)，沿01–08查看各批README；需要理解输入、口袋和方法来源时，再查前四项基础任务。

| 任务 | 阅读入口 | 主要内容 |
|---|---|---|
| 1 文献与方法 | [方法调研](01-literature-and-methods/README.md) | 证据、方法提取和早期方案 |
| 2 SwissDock | [复现与输入](02-swissdock-reproduction/README.md) | 受体配体检查、返回结果及复现资料 |
| 3 结构与口袋 | [结构比较](03-structure-and-pocket/README.md) | 拓扑、六组TM-core比对及空间检查 |
| 4 WT与删段 | [Vina基础对照](04-vina-baseline/README.md) | 按来源和协议区分WT/删段、多模型与接触资料 |
| 5 早期突变 | [01–03](05-mutant-research/analysis/01-03-initial-screen/README.md) | 两种结构路线、组合及7个单点Ala |
| 6 扩展与饱和 | [04–07](05-mutant-research/analysis/04-07-single-mutants/README.md) | 99条单突变记录、87种设计及76种四位点饱和替换 |
| 7 双突变 | [08](05-mutant-research/analysis/08-double-mutants/README.md) | 18个组合、14种亲本及评分/接触比较 |

## 主要工作如何衔接

01/02提示组合评分依赖结构准备路线；03将组合拆为单点；04扩展替换；05系统扫描N84/V110/V368；06补充R181/T106/W338；07补齐W338面板；08检验不同单点作用方式在组合中是否保留。详细发现、WT选择和限制在各批README中说明。

资料保留原作者、运行位置和来源记录。外部导入包与本地突变结果按任务分别标注，交付文件数量不等于新增实验或计算次数。

## 文件与交付状态

- [共享工具与输入](shared/README.md)。
- [制图及MD结构交付](05-mutant-research/handoff/README.md)。
- [来源与核验](provenance/README.md)：文件迁移、哈希和只读验证入口。
- [飞书附件恢复](DATA_DELIVERY.md)：六个附件、校验和接收步骤。
- [数据发布范围审查](provenance/PUBLICATION_SCOPE.md)：Git与附件的逐文件建议及依赖。
- [七组提交计划](provenance/COMMIT_PLAN.md)：供后续人工Git操作使用。
- [发布前事项](provenance/RELEASE_READINESS.md)：数据体积、历史脚本路径与验证范围。

整理日期为2026-10-10。当前为GitHub待提交内容；完整数据通过飞书附件交付，恢复步骤见[DATA_DELIVERY.md](DATA_DELIVERY.md)。目标为Schnee013/Igem2026drylab的experiments/docking-research-lab目录。结果用于计算评分及结构比较，实验亲和力、选择性和协同结论需要独立证据。
