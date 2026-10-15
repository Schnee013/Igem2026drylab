# 双通道建模写作上下文入口

截至2026-10-13，当前可写作材料为明确假设下的ODE输出→Mi密度→Eco条件情景模拟校准，湿实验数据仍待采集。下列位置是写作证据入口，数值回源读取。

1. **研究任务、实验设计和单位**：[方法文档](../../../docs/modeling/P1-dual-channel-calibration.md)，第11、21、37行起。用于说明直接估计Mi密度、Ce作为背景，以及27份湿实验计划的参照口径。
2. **方程、两路输入和Ce为什么不作为预测输入**：同一[方法文档](../../../docs/modeling/P1-dual-channel-calibration.md)，第74、124行起。用于解释两种虫共同贡献两种配体，ODE输出如何形成两路A480，再由三系数估计目标。
3. **文献与项目假设的分界**：同一[方法文档](../../../docs/modeling/P1-dual-channel-calibration.md)，第126、134、136行；完整原始检索位置由[来源清单](../../../experiments/dual-channel/ode-linked/provenance.json)记录。用于区分#18占优的证据与精确分泌比例假设。
4. **当前输入、结果和重放命令**：[ODE联合情景](../../../experiments/dual-channel/ode-linked/README.md)，第8、24行起。系数与误差只从其链接的model.json、summary.json取值；训练点、新组合和比例变化情景分别说明。
5. **不确定性、拒绝输出和实际适用范围**：[方法文档](../../../docs/modeling/P1-dual-channel-calibration.md)，第117、138、151、159行起。负预测、阈值错档与区间假设须和模拟优势一起呈现。
6. **本轮经过和验证记录**：[贡献者日志](../../../docs/logs/2026-10-13-yrx.md)及[validation.json](../../../experiments/dual-channel/ode-linked/validation.json)。用于区分方程冻结、上游模拟拟合、双通道校准与PR整理；软件检查不代替实验验证。

写作顺序：提出背景干扰问题 → 独立改变两种虫数量 → 用明确假设连接ODE → 从配对颜色估计目标密度 → 比较单/双通道 → 报告局限及实测替换办法。早期任意单位demo是历史接口示例，当前结果使用固定ODE输出的A480快照。

下一步：按所需语料体裁从以上来源组织正文，保留模拟证据范围；数值或方法变更时先更新其权威文件，再核对本入口行号。
