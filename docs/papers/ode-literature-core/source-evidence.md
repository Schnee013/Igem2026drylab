# ODE 公共核心来源与适用性

核对日期：2026-10-11。用于审阅文献反应重建及参数迁移假设。数值权威为[来源配置](../../../experiments/ode-model/configs/literature_core_source.json)，项目演示值见[端点配置](../../../experiments/ode-model/configs/literature_core_project.json)。

| 来源 | 可核查位置 | 本版用途与核验状态 |
|---|---|---|
| S1 Supady 2009本科论文 | [原件](https://rumo.biologie.hu-berlin.de/tbp/images/Theses/bsc_supady.pdf)，PDF p48 Model B反应，p49参数/初值，§5.1及§6.1 | 索引全文可读，p49数字与Delft逐项匹配；2026-10-11截图再次返回cache miss，原图未完成复核 |
| S2 Delft 2012 | [模型页](https://2012.igem.org/Team:TU-Delft/Modeling/SingleCellModel)、[附件](https://static.igem.org/mediawiki/2012/0/05/ReducedModelDetails.pdf)，Table 4.1–4.3 | 已保存PDF及其页面图像，2026-10-11重看第2、3页；反应、参数与导数冲突明确 |
| S3 原项目配置 | [minimal_normalized_scenario.json](../../../experiments/ode-model/configs/minimal_normalized_scenario.json) | 仅提供输出合并的scenario prior，不是文献或实验定值 |
| S4 项目构建记录 | memory-Aug/project-memory/wetlab/CURRENT_SYSTEM.md（2026-07-24）；PROJECT_MEMORY.md（2026-08-12整理，7月24/25日证据） | CEN.PK2-1C、Gpr2/3、嵌合Gpa1、sTF–GAL、BvCYP76AD5/MjDOD；本轮查阅未确认SST2状态或最终嵌合版本 |

[参数对应表](parameter-correspondence.csv)列Delft K1–K14与Supady Model B的14个非零速率匹配；共同12个初始浓度也相同。Supady另列k9=0，Delft未单列。匹配支持本版采用该核心，但不证明两个原始运行程序逐式相同。Supady参数来自模型估计；不能称为全部独立测量的普适常数。

## 冲突处理

| 问题 | 实际证据 | 本版处理 |
|---|---|---|
| Fus3活性态导数符号 | S2 Table 4.1 v11为活化、v12为失活；Table 4.3却将活性态写成v11+v12，未活化态为-v11+v12，二者总和不为0 | 使用v11-v12，按反应保持Fus3总量；这是本项目重建修正，不声称作者发布勘误 |
| k91单位 | S2 K12数值0.017打印为s^-1，但v12=k91*Sst2*Fus3_active乘两个浓度；Table 4.3初值单位µmol/l | 单位按反应推导为µM^-1 s^-1，数值保留0.017；其他双分子速率也统一按浓度形式解释，不能把单位推导写成独立实测 |
| 受体降解的正文/附件差异 | S2网页说忽略降解，Table 4.1与4.3含v3活化受体损失 | 本版前端明确采用持续Hill有效输入，不声称与来源受体动态等价 |
| Sst2/Fus3关联含义 | S1为候选反馈变体；S2列Sst2相关Fus3失活通量 | 保留来源有效机制，不将每个速率项解释为项目中已证实的直接分子作用 |

## 项目迁移边界

2026-10-11查阅S4及仓库通路/决策文档，未获得可确认当前SST2基因型及最终嵌合Gpa1构建的记录。模型按保留来源Sst2反馈的情景运行。若后续证据显示SST2删除或嵌合改变水解/复合物恢复，需审查内部结构或速率，不能保证只调整一个偶联系数足够。GAL80状态不用于推断SST2状态。

本版以活化Fus3为公共核心输出边界；原生Ste12和Delft GFP表达未迁移为项目sTF或甜菜黄素参数。Tsinghua 2024仅作此前结构参考，本版未采用其八状态受体方程或速率。

## 原件恢复

论文PDF、页面图及研究归档包保持本地，不进入Git。恢复地址、校验和和生产关系见[源文件清单](../../../experiments/ode-model/literature-core/source_manifest.tsv)。S1原始图像缺口已明确标记，不以无法打开的HTML响应冒充PDF。
