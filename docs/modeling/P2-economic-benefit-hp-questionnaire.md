# P2 早期检测经济效益模型 HP 访谈/问卷材料

日期：2026-05-21

用途：为 P2 早期检测经济效益模型收集 Human Practice（社会实践）一手参数。模型目标是量化“早期检测 + 及时干预”相对“无检测/晚发现”的成本收益。本材料不假设传感器已经有效，也不把 docking ΔG、ODE Kd 或未验证湿实验假设作为经济输入。

建议开场说明：本访谈关注线虫检测和防治决策的真实成本、时效和采用障碍。所有问题都可以回答“不清楚”或给出区间估计；我们会把定量回答用于情景模型，把经验性回答用于解释模型假设和使用场景。

## 访谈目标和参数映射表

### 访谈目标

1. 明确优先建模场景：作物、地区、种植规模、常见线虫类型、典型发现时间。
2. 估算“晚发现”情景：症状出现时的产量损失、防治成本、补救效果和决策延迟。
3. 估算“早期检测 + 干预”情景：提前获得结果后可执行的行动、成本、效果和时间收益。
4. 建立现有检测基线：送检成本、采样密度、送检周期、重复检测、抽样误差和假阴性经验。
5. 收集产品采用参数：可接受检测价格、部署点数、重复检测意愿、误报/漏报容忍度、监管和操作障碍。

### 参数映射表

| 模型参数 | 定义 | 优先来源对象 | 题目来源 | 可直接入模形式 |
|---|---|---|---|---|
| `crop_scenario` | 作物-线虫-地区组合 | 种植户、农技推广人员、合作企业 | G1-G4, E1-E3, P1-P3 | 分类变量 |
| `area` | 种植面积 | 种植户、合作企业 | G2, P2 | 亩、公顷、英亩 |
| `baseline_yield` | 无明显线虫问题时的基准产量 | 种植户、农技推广人员 | G5, E4 | kg/亩、t/ha |
| `crop_price` | 作物销售价格 | 种植户、经销/服务商、合作企业 | G6, S1, P4 | 元/kg、元/吨、区间 |
| `current_detection_cost` / `test_cost` | 当前实验室或第三方检测总成本；未来可比较的单次检测成本 | 种植户、实验室、经销/服务商、合作企业 | G13-G17, L3-L7, S6-S8, P8 | 元/样本、元/地块、元/亩 |
| `deployment_density` | 每亩/每公顷需要的采样或检测点数 | 种植户、农技推广人员、实验室、服务商 | G14, E8, L8-L9, S7, P9 | 点/亩、点/ha、样本/地块 |
| `lab_turnaround` | 当前检测从采样到结果的时间 | 种植户、实验室、服务商 | G15, L5, S9 | 小时、天、周 |
| `early_time_gain` | 早期检测相对晚发现提前的时间 | 种植户、农技推广人员、服务商 | G20-G22, E10-E12, S10 | 天、周、生育期阶段 |
| `intervention_cost` | 早期或晚期干预的实际成本 | 种植户、农技推广人员、经销/服务商 | G23-G29, E13-E15, S2-S5 | 元/亩、元/ha、元/次 |
| `intervention_efficacy` | 干预后损失或线虫压力降低比例 | 种植户、农技推广人员、实验室、服务商 | G30-G32, E16-E18, L12, S4 | 百分比、低/中/高、置信区间 |
| `late_loss_rate` | 晚发现时的产量或收入损失 | 种植户、农技推广人员、合作企业 | G9-G12, E5-E7, P5 | %、kg/亩、元/亩 |
| `false_negative_cost` | 漏检或抽样不准导致的损失 | 种植户、实验室、农技推广人员 | G18-G19, L10-L11, E9 | 元/亩、损失比例、案例 |
| `farmer_wtp` | 种植户或服务端愿意支付的检测价格 | 种植户、经销/服务商、合作企业 | G37-G39, S11-S13, P10-P12 | 元/次、元/亩、元/季 |
| `decision_threshold` | 触发行动的检测结果阈值 | 全部对象 | G33-G36, E19-E21, L13-L15, S14, P13 | 阴/阳性、密度等级、实验室确认需求 |
| `adoption_barrier` | 采用障碍 | 全部对象 | G40-G45, E22-E24, L16-L18, S15-S18, P14-P18 | 分类变量、排序、叙事 |

## 按对象分组的问题清单

标记说明：

- 【必问】：所有访谈尽量覆盖。
- 【定量填空】：请记录单位、年份、地区和回答来源。
- 【可选追问】：时间允许时展开。

### A. 种植户

#### 基本生产信息

1. 【必问】【定量填空】您目前主要种植哪些作物？分别在哪个地区种植？各自面积大约是多少？（参数：`crop_scenario`, `area`）
2. 【必问】【定量填空】这些作物通常一季或一年种几茬？每茬大概持续多久？（参数：`crop_scenario`, `early_time_gain`）
3. 【必问】这些地块中，哪些地块过去更容易出现土传病害或线虫问题？（参数：`crop_scenario`, `late_loss_rate`）
4. 【可选追问】您会按地块、棚室、品种或批次分别记录产量和病害吗？（参数：`baseline_yield`, `late_loss_rate`）
5. 【必问】【定量填空】正常年份、没有明显线虫问题时，目标作物平均产量大约是多少？请说明单位。（参数：`baseline_yield`）
6. 【必问】【定量填空】最近一个销售季，目标作物的销售价格大约是多少？价格波动范围是多少？（参数：`crop_price`）
7. 【可选追问】如果价格按等级、收购渠道或上市时间变化，请分别说明。（参数：`crop_price`）

#### 线虫问题经验

8. 【必问】您是否遇到过根结线虫、胞囊线虫或其他植物寄生线虫问题？如果不确定，当时是怎样判断的？（参数：`crop_scenario`, `late_loss_rate`）
9. 【必问】通常在什么阶段发现问题：播前、定植前、苗期、生长中后期、采收后，还是看到根瘤/黄化/萎蔫后才发现？（参数：`early_time_gain`, `late_loss_rate`）
10. 【必问】发现症状时，您认为是否已经造成产量或商品性损失？依据是什么？（参数：`late_loss_rate`）
11. 【定量填空】如果有损失经验，请估计损失比例或损失金额：约 __% 产量、__ 元/亩、或 __ kg/亩。（参数：`late_loss_rate`, `false_negative_cost`）
12. 【可选追问】过去最严重的一次，问题从发现到影响产量大约经历了多久？（参数：`early_time_gain`, `late_loss_rate`）

#### 当前检测方式

13. 【必问】目前遇到类似问题时，您会不会送实验室检测或请第三方诊断？为什么？（参数：`current_detection_cost`, `lab_turnaround`, `adoption_barrier`）
14. 【必问】【定量填空】如果送检，通常怎么采样？一个地块取多少点、混合多少土、送几个样？（参数：`deployment_density`, `current_detection_cost`）
15. 【必问】【定量填空】从采样到拿到结果通常需要多久？包括运输和排队时间。（参数：`lab_turnaround`）
16. 【必问】【定量填空】一次检测的费用是多少？是否还包括快递、人工、服务费或上门费？（参数：`current_detection_cost`, `test_cost`）
17. 【可选追问】一个季节会重复检测吗？在什么阶段重复？（参数：`deployment_density`, `test_cost`, `early_time_gain`）
18. 【必问】是否遇到过检测阴性但后来仍然发生线虫问题，或不同采样点结果差异很大的情况？（参数：`false_negative_cost`, `deployment_density`）
19. 【定量填空】如果发生过类似情况，最后大约造成了多少损失或额外成本？（参数：`false_negative_cost`, `late_loss_rate`）

#### 早期检测价值

20. 【必问】如果在播前、定植前或早期生长期当天/数小时内得到一个现场检测结果，您会把它用于哪些决策？（参数：`early_time_gain`, `decision_threshold`, `intervention_cost`）
21. 【必问】与现在的发现方式相比，这样的结果大约能提前多久？（参数：`early_time_gain`）
22. 【定量填空】如果提前 __ 天/周发现，您估计可减少多少损失？可用百分比、产量或金额回答。（参数：`intervention_efficacy`, `late_loss_rate`）

#### 干预动作和成本

23. 【必问】线虫风险较高时，您实际会采取哪些措施：施药、轮作、抗性品种、覆盖作物、生物防治、换地块、专家咨询，还是其他？（参数：`intervention_cost`, `intervention_efficacy`, `decision_threshold`）
24. 【定量填空】施药成本大约是多少？请分别说明药剂、人工、机械、水肥系统或服务费。（参数：`intervention_cost`）
25. 【定量填空】如果用抗性品种或特殊种苗，种子/种苗成本比常规方案高多少？（参数：`intervention_cost`）
26. 【定量填空】如果轮作或改种非寄主作物，收益差异大约是多少？（参数：`intervention_cost`, `late_loss_rate`）
27. 【定量填空】如果使用生物防治或土壤改良产品，单季成本和使用次数是多少？（参数：`intervention_cost`）
28. 【定量填空】如果请专家或服务商上门，通常收费模式是什么？（参数：`intervention_cost`, `farmer_wtp`）
29. 【可选追问】哪些措施只有在早期知道风险时才来得及做？哪些症状出现后仍然能做？（参数：`early_time_gain`, `intervention_efficacy`）
30. 【必问】您对这些措施的实际效果怎么判断？通常能减少多少损失，或只是控制继续恶化？（参数：`intervention_efficacy`）
31. 【定量填空】请给常用措施一个效果估计：低、中、高，或减少损失约 __%。如果不确定，可给范围。（参数：`intervention_efficacy`）
32. 【可选追问】哪些因素会让同一种措施效果变化很大？例如土壤、天气、品种、施用时期、线虫种类。（参数：`intervention_efficacy`, `adoption_barrier`）

#### 决策阈值和产品假设

33. 【必问】如果检测结果只有“阴性/阳性/疑似阳性”，您会分别怎么处理？（参数：`decision_threshold`, `false_negative_cost`）
34. 【必问】如果结果是密度等级，例如低/中/高，什么等级会触发行动？（参数：`decision_threshold`, `intervention_cost`）
35. 【必问】阳性结果后，您是否还需要实验室确认才会采取较高成本行动？（参数：`decision_threshold`, `lab_turnaround`, `adoption_barrier`）
36. 【可选追问】什么情况下您会接受先做低成本措施，等实验室确认后再做高成本措施？（参数：`decision_threshold`, `intervention_cost`）
37. 【必问】【定量填空】如果现场检测只作为参考，您可接受的单次价格大约是多少？（参数：`farmer_wtp`, `test_cost`）
38. 【定量填空】如果按面积收费，您可接受的价格大约是 __ 元/亩/季或 __ 元/亩/次？（参数：`farmer_wtp`, `deployment_density`）
39. 【可选追问】如果检测速度更快、准确度更高或能减少送检次数，支付意愿会怎样变化？（参数：`farmer_wtp`, `lab_turnaround`, `false_negative_cost`）
40. 【必问】您能接受怎样的误报？例如结果提示有风险但后来确认没有明显线虫问题。（参数：`adoption_barrier`, `decision_threshold`）
41. 【必问】您能接受怎样的漏报？例如结果未提示风险但后来发生问题。（参数：`false_negative_cost`, `adoption_barrier`）
42. 【必问】如果检测材料涉及活体酵母传感器，您最关心什么：安全、监管、残留、保存运输、操作、解释结果，还是其他？（参数：`adoption_barrier`）
43. 【必问】您是否愿意自己操作，还是更倾向由农技人员/经销商/实验室人员提供服务？（参数：`adoption_barrier`, `farmer_wtp`）
44. 【定量填空】您认为一次检测从取样到读数，最多可接受多长操作时间？（参数：`lab_turnaround`, `adoption_barrier`）
45. 【可选追问】如果需要冷藏、避光、培训或专门废弃处理，会如何影响采用？（参数：`adoption_barrier`, `farmer_wtp`）

### B. 农技推广人员

1. 【必问】本地区哪些作物和线虫问题最值得优先建模？（参数：`crop_scenario`）
2. 【必问】根结线虫、胞囊线虫或其他线虫通常在哪些生产体系中更常见？（参数：`crop_scenario`, `late_loss_rate`）
3. 【定量填空】典型农户或基地的种植面积、产量和销售价格范围是多少？（参数：`area`, `baseline_yield`, `crop_price`）
4. 【定量填空】正常年份和线虫高风险年份的产量差异大约是多少？（参数：`baseline_yield`, `late_loss_rate`）
5. 【必问】农户通常在哪个阶段意识到线虫问题？症状出现时是否已经错过最佳干预窗口？（参数：`early_time_gain`, `late_loss_rate`）
6. 【定量填空】从早期风险到明显症状，通常相隔多久？（参数：`early_time_gain`）
7. 【必问】当地常用的线虫检测或诊断流程是什么？（参数：`lab_turnaround`, `current_detection_cost`）
8. 【定量填空】您建议一个地块取多少采样点？面积扩大后如何增加采样数？（参数：`deployment_density`）
9. 【必问】抽样误差或假阴性在实际推广中常见吗？主要原因是什么？（参数：`false_negative_cost`, `deployment_density`）
10. 【必问】如果播前或定植前拿到检测结果，哪些措施最可能改变？（参数：`early_time_gain`, `intervention_cost`, `intervention_efficacy`）
11. 【定量填空】这些措施一般需要提前多少天做才有意义？（参数：`early_time_gain`）
12. 【可选追问】哪些措施适合低风险、中风险、高风险分别采用？（参数：`decision_threshold`, `intervention_cost`）
13. 【定量填空】施药、轮作、抗性品种、生物防治、专家服务的典型成本范围是多少？（参数：`intervention_cost`）
14. 【定量填空】每类措施在当地的实际效果通常能达到什么范围？（参数：`intervention_efficacy`）
15. 【可选追问】哪些措施在法规、登记作物或农残要求上有限制？（参数：`adoption_barrier`, `intervention_cost`）
16. 【必问】什么检测结果会让您建议农户行动？（参数：`decision_threshold`）
17. 【必问】阳性现场结果是否足够建议行动，还是需要实验室确认？（参数：`decision_threshold`, `lab_turnaround`）
18. 【可选追问】如果检测结果和田间症状不一致，通常如何处理？（参数：`decision_threshold`, `false_negative_cost`）
19. 【必问】对活体酵母传感器的田间使用，推广端最可能担心哪些问题？（参数：`adoption_barrier`）
20. 【必问】如果要推广，谁更适合作为操作主体：农户、合作社、农资店、植保服务队、实验室，还是推广站？（参数：`adoption_barrier`, `farmer_wtp`）
21. 【定量填空】您认为按样本、按亩或按服务包收费，哪个更容易被接受？可接受价格范围是多少？（参数：`farmer_wtp`, `test_cost`）
22. 【可选追问】哪些证据会提高您推荐这种检测方式的意愿？（参数：`adoption_barrier`, `intervention_efficacy`）
23. 【可选追问】哪些情景下即使检测便宜，农户也可能不采取行动？（参数：`adoption_barrier`, `farmer_wtp`）
24. 【可选追问】如果用于示范田或合作社统一服务，最小可行流程应是什么？（参数：`deployment_density`, `lab_turnaround`, `farmer_wtp`）

### C. 植保/线虫检测实验室

1. 【必问】贵机构目前可检测哪些植物寄生线虫？能否区分根结线虫、胞囊线虫及具体种？（参数：`crop_scenario`, `decision_threshold`）
2. 【必问】常规方法包括形态学、计数、qPCR 或其他方法吗？各自适用场景是什么？（参数：`current_detection_cost`, `lab_turnaround`, `decision_threshold`）
3. 【定量填空】不同检测项目的收费是多少？是否按样本、作物、检测对象或方法收费？（参数：`current_detection_cost`, `test_cost`）
4. 【定量填空】样本从收到到出结果通常需要多久？旺季和淡季是否不同？（参数：`lab_turnaround`）
5. 【定量填空】如果考虑采样、运输、登记和报告，客户实际等待时间通常是多少？（参数：`lab_turnaround`）
6. 【必问】送检样本通常来自哪些对象：种植户、农资商、合作社、企业、监管部门？（参数：`adoption_barrier`, `farmer_wtp`）
7. 【定量填空】一个地块建议取多少土样或根样？每个样本代表多大面积？（参数：`deployment_density`）
8. 【定量填空】如果要提高检测可靠性，需要增加多少采样点或重复检测？（参数：`deployment_density`, `test_cost`）
9. 【必问】实际工作中导致假阴性或结果不稳定的主要原因是什么？（参数：`false_negative_cost`, `deployment_density`）
10. 【定量填空】在您经验中，抽样不准或送检过晚会造成怎样的经济后果？如果无法量化，请描述典型案例。（参数：`false_negative_cost`, `late_loss_rate`）
11. 【必问】检测报告一般如何表达结果：有/无、密度、种类、风险等级，还是防治建议？（参数：`decision_threshold`）
12. 【可选追问】哪些结果水平通常会建议客户采取措施？（参数：`decision_threshold`, `intervention_efficacy`）
13. 【必问】现场快速检测如果为阳性，是否仍建议送实验室确认？在哪些情况下必须确认？（参数：`decision_threshold`, `lab_turnaround`）
14. 【必问】如果快速检测只作为初筛，您认为它应满足哪些最低性能或操作条件？（参数：`adoption_barrier`, `false_negative_cost`）
15. 【定量填空】您认为假阳性和假阴性的相对成本哪个更高？能否给出比例或案例？（参数：`false_negative_cost`, `decision_threshold`）
16. 【必问】活体酵母传感器样本处理、保存、废弃、运输和实验室合规方面有哪些潜在要求？（参数：`adoption_barrier`）
17. 【可选追问】实验室是否可能作为这种检测产品的验证、培训或售后节点？（参数：`adoption_barrier`, `farmer_wtp`）
18. 【可选追问】如果要和现有实验室检测互补，最合理的服务流程是什么？（参数：`lab_turnaround`, `decision_threshold`, `test_cost`）

### D. 农资经销/植保服务商

1. 【必问】客户最常咨询哪些作物的线虫或土传病害问题？（参数：`crop_scenario`）
2. 【定量填空】常见防治方案有哪些？产品成本、人工或服务成本大约是多少？（参数：`intervention_cost`）
3. 【定量填空】客户通常按亩、按棚、按套餐还是按产品购买？（参数：`intervention_cost`, `farmer_wtp`）
4. 【必问】这些方案在不同发生程度下效果差异如何？（参数：`intervention_efficacy`, `decision_threshold`）
5. 【可选追问】哪些方案需要在播前或早期使用，哪些可以症状出现后补救？（参数：`early_time_gain`, `intervention_efficacy`）
6. 【必问】您是否提供或代办线虫检测？收费和流程是什么？（参数：`current_detection_cost`, `lab_turnaround`）
7. 【定量填空】如果作为服务商部署现场检测，一个客户/地块通常需要检测多少点？（参数：`deployment_density`, `test_cost`）
8. 【定量填空】您认为单次检测、按亩检测或服务包的可接受价格分别是多少？（参数：`farmer_wtp`, `test_cost`）
9. 【定量填空】客户通常能接受多快出结果？当天、24 小时、3 天、一周的价值差异如何？（参数：`lab_turnaround`, `early_time_gain`, `farmer_wtp`）
10. 【必问】如果早期检测提示风险，客户最可能采取哪些行动？（参数：`intervention_cost`, `intervention_efficacy`, `decision_threshold`）
11. 【必问】什么检测结果足以让您建议客户购买或采取防治服务？（参数：`decision_threshold`）
12. 【必问】客户对误报和漏报通常怎样反应？哪一种更影响信任？（参数：`false_negative_cost`, `adoption_barrier`）
13. 【可选追问】如果出现阳性结果，您会建议先做低成本措施、直接综合防治，还是送实验室确认？（参数：`decision_threshold`, `intervention_cost`）
14. 【必问】活体酵母传感器在门店或上门服务中可能遇到哪些问题？（参数：`adoption_barrier`）
15. 【必问】保存、运输、保质期、培训和废弃处理会如何影响服务成本？（参数：`test_cost`, `adoption_barrier`）
16. 【可选追问】如果产品要通过经销/服务渠道推广，您希望获得哪些证明材料或售后支持？（参数：`adoption_barrier`, `farmer_wtp`）
17. 【可选追问】哪些客户群体最可能先采用？大户、合作社、设施农业、种苗企业，还是普通散户？（参数：`crop_scenario`, `farmer_wtp`）
18. 【可选追问】如果检测结果不直接带来购买转化，您是否仍愿意提供该服务？为什么？（参数：`farmer_wtp`, `adoption_barrier`）

### E. 潜在合作企业

1. 【必问】贵方关注的目标作物、地区和客户类型是什么？（参数：`crop_scenario`, `area`）
2. 【定量填空】典型客户的种植规模、产量和销售价格范围是多少？（参数：`area`, `baseline_yield`, `crop_price`）
3. 【必问】客户目前最常遇到的线虫类型或土传病害问题是什么？（参数：`crop_scenario`）
4. 【定量填空】相关作物的平均产值、毛利或损失敏感度大约是多少？（参数：`crop_price`, `baseline_yield`, `late_loss_rate`）
5. 【定量填空】晚发现线虫问题时，客户常见损失范围是多少？（参数：`late_loss_rate`, `false_negative_cost`）
6. 【必问】现有检测服务、植保服务或产品组合中，哪些环节可能与早期检测结合？（参数：`lab_turnaround`, `intervention_cost`, `farmer_wtp`）
7. 【定量填空】目前客户获得诊断结果通常需要多久？各环节成本是多少？（参数：`lab_turnaround`, `current_detection_cost`）
8. 【定量填空】如果作为产品或服务，单次检测成本和终端价格需要控制在什么范围才有商业可行性？（参数：`test_cost`, `farmer_wtp`）
9. 【定量填空】面向不同客户，合理的检测密度或服务频次是什么？（参数：`deployment_density`）
10. 【必问】如果早期检测结果为阳性，企业端可提供哪些后续方案？（参数：`intervention_cost`, `intervention_efficacy`, `decision_threshold`）
11. 【定量填空】这些方案的成本、毛利、实施周期和效果证据如何？（参数：`intervention_cost`, `intervention_efficacy`）
12. 【必问】客户愿意为检测本身付费，还是更愿意把检测包含在综合服务包里？（参数：`farmer_wtp`, `test_cost`）
13. 【必问】什么结果会触发企业端推荐行动？阴/阳性、风险等级、密度阈值，还是实验室确认？（参数：`decision_threshold`）
14. 【必问】对活体酵母传感器，企业端最关注哪些合规、品牌、客户接受度或供应链风险？（参数：`adoption_barrier`）
15. 【必问】保存运输、保质期、批间稳定性、培训和废弃处理会如何影响商业化？（参数：`adoption_barrier`, `test_cost`）
16. 【必问】如果现场检测可能出现误报或漏报，企业能接受的责任边界是什么？（参数：`false_negative_cost`, `adoption_barrier`）
17. 【可选追问】需要哪些验证数据，企业才会考虑小规模试点？（参数：`adoption_barrier`, `intervention_efficacy`）
18. 【可选追问】最适合试点的作物、地区、客户类型和季节窗口是什么？（参数：`crop_scenario`, `early_time_gain`, `deployment_density`）

## 适合面对面访谈的开放式问题

1. 请您回忆一次印象最深的线虫或疑似线虫问题，从最早发现异常到采取措施，整个过程是怎样的？（参数：`early_time_gain`, `late_loss_rate`, `intervention_cost`）
2. 在您看来，线虫问题最难决策的环节是什么：是否检测、怎么采样、何时干预、选择措施、还是判断效果？（参数：`decision_threshold`, `deployment_density`, `adoption_barrier`）
3. 如果提前知道某块地存在较高线虫风险，您的实际决策会和现在有什么不同？（参数：`early_time_gain`, `intervention_cost`, `intervention_efficacy`）
4. 什么情况下，一个“快速但需要后续确认”的检测结果对您仍然有价值？（参数：`lab_turnaround`, `decision_threshold`, `farmer_wtp`）
5. 您如何权衡检测成本、误报风险和漏报风险？（参数：`test_cost`, `false_negative_cost`, `decision_threshold`）
6. 哪些现实因素会让一个技术上可行的检测方案难以在田间使用？（参数：`adoption_barrier`, `farmer_wtp`）
7. 如果要设计一个让您愿意试用的检测服务，它应该由谁来操作、多久出结果、怎么收费？（参数：`farmer_wtp`, `lab_turnaround`, `test_cost`）
8. 对您来说，什么证据最能说明早期检测确实改变了生产决策？（参数：`intervention_efficacy`, `early_time_gain`, `decision_threshold`）

## 5 分钟短问卷

适用：展会、电话初筛、短访谈。优先收集模型最小参数，不展开机制解释。

1. 【必问】【定量填空】您的主要作物、地区和面积是多少？（参数：`crop_scenario`, `area`）
2. 【必问】【定量填空】正常年份平均产量和销售价格是多少？（参数：`baseline_yield`, `crop_price`）
3. 【必问】是否遇到过根结线虫、胞囊线虫或其他线虫问题？通常什么时候发现？（参数：`crop_scenario`, `early_time_gain`, `late_loss_rate`）
4. 【定量填空】如果发生过，估计造成多少产量或收入损失？（参数：`late_loss_rate`, `false_negative_cost`）
5. 【必问】现在会不会送检？一次检测总成本和等待时间是多少？（参数：`current_detection_cost`, `lab_turnaround`）
6. 【定量填空】一个地块通常采多少点或送多少样？（参数：`deployment_density`）
7. 【必问】如果播前/定植前/早期当天得到结果，您会采取哪些行动？（参数：`early_time_gain`, `intervention_cost`, `decision_threshold`）
8. 【定量填空】这些行动大约花多少钱，预计能减少多少损失？（参数：`intervention_cost`, `intervention_efficacy`）
9. 【定量填空】您能接受的现场检测价格是多少：__ 元/次、__ 元/亩/次或 __ 元/亩/季？（参数：`farmer_wtp`, `test_cost`）
10. 【必问】采用这种检测最主要的顾虑是什么？（参数：`adoption_barrier`）

## 20-30 分钟深访提纲

### 0-3 分钟：背景和授权

- 说明访谈用途：用于早期检测经济模型参数化，不评价受访者做法对错。
- 确认是否可记录匿名信息：作物、地区、面积、价格、成本、经验案例。
- 说明不确定数值可给区间。

### 3-8 分钟：生产场景和晚发现损失

- 覆盖问题：A1-A12 或对应对象的基础场景题。
- 目标参数：`crop_scenario`, `area`, `baseline_yield`, `crop_price`, `late_loss_rate`, `early_time_gain`。
- 访谈重点：锁定 1 个最适合建模的作物-地区-线虫场景。

### 8-13 分钟：当前检测基线

- 覆盖问题：A13-A19、C1-C10 或服务商对应检测题。
- 目标参数：`current_detection_cost`, `test_cost`, `deployment_density`, `lab_turnaround`, `false_negative_cost`。
- 访谈重点：区分实验室收费、采样人工、运输、等待时间和重复检测。

### 13-19 分钟：早期检测改变什么决策

- 覆盖问题：A20-A22、B10-B12、D9-D13。
- 目标参数：`early_time_gain`, `decision_threshold`, `intervention_cost`, `intervention_efficacy`。
- 访谈重点：不要问“会不会省钱”，而问“提前知道后会不会做不同动作”。

### 19-24 分钟：干预成本、效果和限制

- 覆盖问题：A23-A32、B13-B18、D2-D5。
- 目标参数：`intervention_cost`, `intervention_efficacy`, `adoption_barrier`。
- 访谈重点：把药剂、人工、机械、服务费、机会成本分开记录。

### 24-28 分钟：产品假设和支付意愿

- 覆盖问题：A33-A45、D7-D18、E8-E18。
- 目标参数：`farmer_wtp`, `test_cost`, `deployment_density`, `decision_threshold`, `adoption_barrier`, `false_negative_cost`。
- 访谈重点：分别记录“愿意试用价格”和“长期常规使用价格”。

### 28-30 分钟：确认和收尾

- 复述关键数值，请受访者确认单位和范围。
- 询问是否可后续补充缺失数字或推荐更合适的受访对象。
- 标记哪些回答是亲身经验，哪些是估计或行业听闻。

## 数据记录模板

| 字段 | 记录值 | 单位 | 来源对象 | 置信度 | 备注 |
|---|---|---|---|---|---|
| 作物-线虫-地区 |  |  |  | 高/中/低 |  |
| 面积 |  | 亩/ha |  | 高/中/低 |  |
| 基准产量 |  | kg/亩 或 t/ha |  | 高/中/低 |  |
| 销售价格 |  | 元/kg 或 元/t |  | 高/中/低 |  |
| 晚发现损失 |  | % 或 元/亩 |  | 高/中/低 |  |
| 当前检测总成本 |  | 元/样本 或 元/亩 |  | 高/中/低 |  |
| 当前检测周期 |  | 小时/天/周 |  | 高/中/低 |  |
| 采样/检测点数 |  | 点/亩 或 点/ha |  | 高/中/低 |  |
| 提前时间 |  | 天/周 |  | 高/中/低 |  |
| 干预动作 |  | 类别 |  | 高/中/低 |  |
| 干预成本 |  | 元/亩 或 元/ha |  | 高/中/低 |  |
| 干预效果 |  | % 或等级 |  | 高/中/低 |  |
| 可接受检测价格 |  | 元/次 或 元/亩 |  | 高/中/低 |  |
| 触发行动阈值 |  | 阴/阳性/等级/密度 |  | 高/中/低 |  |
| 采用障碍 |  | 类别/叙事 |  | 高/中/低 |  |

## 可直接进入模型的回答 vs 定性叙事

### 可直接进入模型或情景参数的回答

- 作物、地区、线虫类型：进入 `crop_scenario`。
- 面积：进入 `area`。
- 正常年份产量：进入 `baseline_yield`。
- 销售价格：进入 `crop_price`。
- 晚发现损失比例、损失产量或损失金额：进入 `late_loss_rate`，并可推导 `false_negative_cost`。
- 当前检测费用、采样人工、运输费、服务费：进入 `current_detection_cost` / `test_cost`。
- 当前检测等待时间：进入 `lab_turnaround`。
- 采样点数、样本数、建议代表面积：进入 `deployment_density`。
- 早期检测能提前的时间：进入 `early_time_gain`。
- 具体干预措施的药剂、人工、机械、服务、种子溢价、轮作机会成本：进入 `intervention_cost`。
- 干预后估计减少的损失比例或产量差：进入 `intervention_efficacy`。
- 可接受的检测价格或服务包价格：进入 `farmer_wtp`。
- 触发行动的结果等级、是否需要实验室确认：进入 `decision_threshold`。

### 只能作为定性叙事或模型假设解释的回答

- “感觉今年更严重”“某地块一直不好”等未量化经验。
- 对传感器有效性、准确度或成本的主观期待，除非有实测或明确价格。
- 对活体酵母传感器的接受度、监管顾虑、品牌顾虑和操作顾虑。
- 对误报/漏报的情绪反应或信任影响，除非可转化为经济损失或采用概率。
- 对某种防治措施“有效/没用”的笼统评价，除非能补充成本、时间、损失减少范围。
- 企业或经销端的商业合作意向，除非给出具体价格、部署密度、服务周期或客户规模。
- 文献或行业宣传中的收益声明，除非能够追溯来源并与本地作物、地区、成本口径匹配。

### 需要二次核实后才能入模的回答

- 受访者转述的市场价格、农药价格或实验室费用。
- 涉及法规、登记作物、活体材料运输和田间释放的判断。
- 某种干预措施的效果百分比，但没有样本数、地块条件或对照基准。
- 把单个失败/成功案例外推到全部地块的结论。
- 与中国本地场景相关但没有官方统计、推广站资料或多位受访者交叉验证的参数。
