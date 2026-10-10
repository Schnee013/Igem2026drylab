# 分析目录整理审查与最小重排方案

状态：用户确认“继续，没有问题”后，已完成重排及清理。当前入口：[phase1分析](../../05-mutant-research/analysis/01-03-initial-screen/README.md)、[phase2分析](../../05-mutant-research/analysis/04-07-single-mutants/README.md)、[设计讨论](../../05-mutant-research/design/README.md)。

## 执行结果

- 已生成99条单突变/87种设计/4个WT的统一汇总，另列04的1个组合；63条旧汇总及76条饱和视图均完成分数、接触和统计对账。
- phase1保留01–03的11条评分、22条接触增减、324行四格及03的36条pose参考。04的18条记录纳入phase2，144条pose与232行原子级证据已迁入。
- 10个过时或被替代的活动文件已清理，详见[迁移清单](analysis-reorganization.json)的deleted；原1287份分析/设计文件全部保存在[可恢复备份](analysis-reorganization-backup.zip)，逐份哈希验证通过。
- 1262个移动的逐pose/原子证据文件字节保持一致；batches的5863个文件路径和内容哈希保持一致。
- 活动分析文档链接核验通过。batches内历史README仍有指向旧分析位置的引用及CLI硬编码旧目录名；按用户要求未改写批次文件。对应现行入口和路径映射写入整理清单，批次旧CLI若需复用，须在后续运行前处理路径。

以下第1–6节为迁移前审查和获准方案，保留其当时判断；其中“待确认/未移动”等状态描述不再代表当前执行状态。

## 1. 优先级

1. **先确定阶段归属和记录身份。** phase1对应批次01–03；phase2对应04–07。同一突变在不同批次的结果分别保留，主键至少包含batch/run/variant/AF_model/seed，WT按来源记录；固定骨架侧链结果保留历史身份，不混入AF3候选统计。
2. **建立可持续补充的phase2汇总。** 单突变评分/接触只维护一个完整数据入口，饱和四位点是其一个统计视图；文件名不绑定批次范围。先并入06补充及04记录，再退役旧汇总。
3. **整理分析文稿和引用。** 当前四位点分析从design移回analysis，保留补充单点、跨批比较和方法限制。更新活动脚本及Markdown链接；原始结果中的历史路径用映射解析，不批量改写。
4. **最后清理旧计划及冗余输出。** 完成内容覆盖核对、路径核验、记录数与数值对账后，再按用户确认的逐项清单删除。

## 2. 实际盘点与关键发现

| 当前目录 | 文件数（含隐藏文件） | 内容与判断 |
|---|---:|---|
| phase1-analysis | 1273 | 大部分为逐pose证据；目录实际覆盖01–04，不是纯01–03 |
| phase2-analysis | 8 | 两套有重叠但互不包含的汇总，以及两个不同入口的统计脚本 |
| phase2-design | 6 | 当前分析稿、历史分析稿、旧设计、旧续聊提示和README；分析与计划混放 |
| file-organization | 4（本审查写入前） | 先前整理的映射、哈希、验证和原入口ZIP；保留以追溯迁移 |

这些目录均只有KB至约2MB量级，优先解决入口和归属，不以节省磁盘为清理目标。当前没有证据证明某份科学结果仅因位置不合理就是错误或无用数据。

### phase1中混入的phase2证据

- top1-contacts/mutation_scores.csv：29条，其中01批2条、02批2条、03批7条、04批18条。
- top1-contacts/contact_change_summary.csv：58行，其中04批36行。
- top1-contacts/four_way_contacts.csv：777行，其中04批453行。
- candidate-allposes/pose_summary.csv：180条pose，其中03批36条、04批144条。contact_frequencies.csv共711行，其中03批135、04批576行。
- r181a-atomic-contacts/audit.json明确指向原gpr2-round2-af3-run01，即现批次04，应归入phase2。
- statistics.md和residue-priorities.md使用了04批替换与组合证据，不能只换标题就视作纯phase1报告。现有两文的最低分pose统计仍有价值；新的阶段划分也不意味着把phase1已有最低分统计改成多pose主统计。

### phase2应有的覆盖范围

| 批次 | 单突变结构记录 | 其他 |
|---|---:|---|
| 04 | 17 | 1个组合N84A_V110A_V368A，另有WT |
| 05 | 57 | 另有WT |
| 06 | 6 | 另有WT |
| 07 | 19 | 另有WT；W338C使用model_1例外 |
| 合计 | **99条，87种唯一单突变** | 4个来源WT；04的1个组合应另列 |

重复设计共有12种：N84Q/S、V110A/I/L/T、V368A/I/L、W338A/F/L。它们是不同批次的独立结构记录，不是可删除的重复文件。

目前combined-scores.json有63条（05/06），four-site-saturation/statistics.json有76条（05/07）。两者重合05的57条，但前者含R181K/Q、T106S/V和06版W338F/L，后者不能取代这些记录。两者合起来是82条记录、80种单突变；并入04的17条后才得到上表99条/87种。

### 已发生的批次目录改名

| 历史路径 | 当前实际路径 |
|---|---|
| batches/04-af3-round2/ | batches/04-af3-more-single-alanine/ |
| batches/05-af3-saturation-combinations/ | batches/05-af3-n84-v110-v368-saturations/ |

本次不调整这两个实际目录。分析脚本、部分Markdown及JSON中的来源地址仍有旧名。将两个汇总JSON的来源路径映射到实际目录后，四位点汇总7/7、05/06汇总4/4来源SHA256均一致：目前确认的是路径过时，而非源文件内容损坏。

在phase-analysis/design的Markdown链接中发现6处目标不存在，分布于05/06 interpretation、当前饱和分析和历史分析，均指向旧05目录。两个汇总脚本也写死旧05目录；其中summarize_single_mutants.py还限制输出为05/06、断言63种唯一设计。它不能通过只改文件夹名升级为持续汇总。

## 3. 建议的最小目标结构

将phase2主分析直接放在phase2-analysis根目录，减少层级；不再创建按05-06、05-07、04-07命名的分析目录。

```text
outputs/
  phase1-analysis/
    README.md
    residue-priorities.md       # 校正为01–03证据及当时筛选结论
    statistics.md              # 01–03；侧链/AF3来源分开
    top1-contacts/              # 按阶段拆分后只留01–03
    candidate-allposes/         # 保留03的多pose参考
  phase2-analysis/
    README.md                  # 唯一阅读入口、来源批次与数据口径
    interpretation.md          # 单突变综合解读，含饱和与补充单点
    single-mutants.md           # 所有单突变结构记录；持续追加批次
    single-mutants.json         # 唯一完整单突变汇总数据及溯源
    saturation-statistics.md    # 从完整数据生成的四位点统计视图
    summarize.py               # 一个汇总入口，按来源批次识别和校验
    combination-mutants.md     # 纳入已有04组合；以后追加新组合结果
    combination-mutants.json   # 组合证据独立于单点排序
    r181a-atomic-contacts/      # 从phase1原样迁入，已有04原子级证据
    pose-reference/             # 04已有多pose参考，主统计仍只取最低分
  phase2-design/
    README.md                  # 当前设计状态和分析入口
    ...                        # 保留待确认旧文件；新方案确定后再写具体计划
  file-organization/
    analysis-layout-review.md  # 本次审查、后续迁移/删除清单
    ...                        # 既有映射与校验记录
  batches/                     # 原样保留
```

phase2新增的两个证据子目录承接现有数据，而非复制多份；同时移除两个按覆盖范围命名的旧分析子目录须等迁移核验与删除批准。未来追加批次更新同一数据源和视图，批次编号只出现在记录字段和来源映射中。日期放正文更新信息，不作为活动分析入口文件名。组合文件承接已存在的04结果，并非预建空任务。

统计视图必须声明其记录选择：例如四位点饱和视图继续使用05的N84/V110/V368与07的W338；06的W338F/L作为跨批对照保留。不能把同设计不同批次记录平均掉、挑最优值去重，或把所有来源D混排成统一排名。model_1例外和来源WT都保留在记录中。

## 4. 保留、整合与迁移清单

| 现有文件/目录（相对outputs） | 处理建议 | 应保留的信息/核验条件 |
|---|---|---|
| phase2-design/saturation-review-20260917.md | 移入phase2-analysis/interpretation.md作为主稿基础 | 完整四位点解释、W338C例外、W338F/L跨批分解、单点角色；整合06补充结论 |
| phase2-analysis/single-mutants-05-06/interpretation.md | 合并入主稿后待批准删除旧副本 | R181/T106六单点表、06-WT差异、当时W338解释；追加seed提案标为历史建议，非已执行结果 |
| phase2-analysis/single-mutants-05-06/combined-scores.md/.json | 并入single-mutants.md/.json；旧副本待覆盖核验后列删 | 63条来源记录、两个WT的完整ΔS与D敏感性、接触变化及来源哈希 |
| phase2-analysis/four-site-saturation/statistics.md/.json | 完整记录并入单一JSON；Markdown改名为saturation-statistics.md | 76条主饱和记录、三WT敏感性、接触频数/Jaccard、AF模型与RMSD；派生统计可再生成 |
| phase2-analysis/summarize_single_mutants.py与four-site-saturation/summarize.py | 合为summarize.py后，旧脚本待批准删除 | 不只替换硬编码名单；保留每来源记录与校验，支持重复设计、阶段/单双突变筛选 |
| phase1-analysis/top1-contacts/三个CSV | 按batch字段拆分/纳入各阶段汇总 | 01–03共11条评分记录、22条接触变化、324行四格；04共18/36/453；总量和逐行内容需守恒 |
| phase1-analysis/candidate-allposes/ | 03留原目录；04证据移至phase2的pose-reference | 逐pose文件、频数表和audit一起管理；混合汇总按batch拆分，原audit保留来源映射 |
| phase1-analysis/r181a-atomic-contacts/ | 原样移动至phase2 | 232行原子接触和audit；其来源为04而非03 |
| phase1-analysis/statistics.md、residue-priorities.md | 校正阶段范围，04相关结论迁入phase2 | 迁移前逐节对照，保留当时筛选依据；跨阶段对照需明确标注，不能静默改成当前结论 |
| outputs/README.md及各阶段README | 统一阅读入口、阶段边界及实际目录名 | 分析→原始批次有可用链接；设计目录不再承担活动结果稿 |
| file-organization/*、user-run-vina.md | 保留 | 路径迁移历史、证据完整性与用户执行约定 |

暂不移动projects-done、vina输入、src或gpr2-route-comparison。后者是否属于已完成独立任务可另作目录归档判断，不纳入本次分析目录清理。

## 5. 待用户确认的删除候选

### A. 已过时且可单独退役的入口

| 文件 | 原因 | 删除前条件 |
|---|---|---|
| phase2-design/next-session-prompt.md | 仍要求开始批次05、称第二阶段尚未生成FASTA/manifest，下一步指向已完成工作；还引用旧04路径 | 当前README能明确定位现有分析和真实下一步；用户确认删除 |

### B. 先提取有用内容，再确认删除

| 文件 | 原因 | 删除前必须保留的内容 |
|---|---|---|
| phase2-design/parallel-screen.md | 旧66份新AF输入/81条结构及复用方案已被实际独立预测批次替代；原12组合也尚未按此执行 | 对照原则、评分/非加和比较约束和实际已完成模块的来源；待讨论组合假说如有保留价值，应列为历史候选而非当前任务 |
| phase2-design/history/saturation-review-20260917-before-w338.md | 结果部分被当前四位点主稿覆盖，但仍含旧10核心＋2条件组合提案及复核设想 | 未定稿假说的理由、ε_i=ΔS_i(AB)−ΔS_i(A)−ΔS_i(B)、ε_D=ε18−ε3等比较方法；提取完成后再判断是否删除历史全文 |
| phase2-analysis/single-mutants-05-06/interpretation.md | 与主稿部分重叠，仍有06补充独有解释 | 将R181/T106及两WT解释完整并入新主稿后，再确认删除旧副本 |
| phase2-analysis/single-mutants-05-06/combined-scores.md/.json | 有重叠但当前尚非冗余 | 99条汇总覆盖其63条且分数、WT敏感性、接触变化、来源哈希核验一致 |
| phase2-analysis/four-site-saturation/statistics.json | 可成为单一完整JSON中的记录及派生统计，避免并行维护两个来源 | 在新JSON中覆盖76条主面板及三WT、接触、模型字段，并可重建统计视图 |
| 两个旧汇总脚本 | 分别硬编码覆盖范围且路径过时 | 一个新入口通过全部记录及派生视图对账后，再删除旧脚本；移动后的主脚本须重新校正项目根目录定位 |

上述“待删除”不等于已经批准或已完成整合。本次未删除任何文件。统计Markdown若以改名/移动方式保留，不再作为额外删除对象。

### C. 不建议删除的数据

- 同设计跨批次记录（尤其W338F/L、W338A、N84Q等），以及每批WT。
- 多pose原始派生文件、接触频数和原子级核验。当前主统计不使用它们，不等于它们无复用价值。
- W338C失败现场与模型选择记录；均在batches，本次不调整。
- 既有迁移映射、SHA256清单与原入口备份。

隐藏的.DS_Store不属于科学结果；本次不将清除这类系统自动生成文件作为整理目标。

## 6. 迁移执行顺序与验收

1. 固定本清单涉及文件的原路径/目标路径/哈希，追加到已有file-organization体系；不创建另一套分散归档目录。
2. 在汇总层建立历史→当前路径映射，用哈希验证来源内容。只改活动分析脚本和文档链接；不改batches内日志、JSON、配置、科学输出或历史audit字节。
3. 建立99条单突变＋4个WT的完整汇总，另接入04的1个组合。保留旧汇总直到记录覆盖和数值对账通过。此步只处理已有输出，不重新运行AF、结构制备、Vina或ProLIF。
4. 主稿迁入analysis，整合06补充及04历史结果；按01–03/04–07校正phase1/2文稿、证据归属与多pose参考。为迁移后的原audit保留路径解释，避免改写历史哈希链。
5. 校验：条目数守恒、来源记录唯一、D公式一致、来源WT明确、76条饱和视图不混入重复记录、04组合不进入单点排名、W338C例外保留、活动链接可用、汇总脚本可复现。
6. 对batches做迁移前后内容/路径清单对比，确认无变更；向用户呈现实际迁移结果和最终可删清单。用户确认具体删除项后再删除，并更新入口引用。

本轮结论：先做phase2统一汇总和分析稿归位，其次按记录拆分phase1混入的04证据，最后清理计划。单纯给single-mutants-05-06改名，或只把W338分析挪位置，均不能解决现有覆盖缺口和阶段混杂。
