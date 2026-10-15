# PR #20 复现材料与联合验证

- 对应评审：[联合 review](https://github.com/Schnee013/Igem2026drylab/pull/20#pullrequestreview-5516372285)，原 head `2e8c9db16fbfcc340453a2cb05264190219ee41b`。
- 两路r04参数按既有来源SHA256核验后作为规范重算输入保存。新增样本设计和[生成器](../../src/modeling/dual_channel/generate_inputs.py)，从冻结参数、释放率与协议重新计算18个端点、9个训练配对和36个评价配对；命令、单位、容差见[复现入口](../../experiments/dual-channel/ode-linked/README.md)。
- [生成回归测试](../../tests/modeling/test_dual_channel_generation.py)只向生成器提供JSON配置，逐字段核对固定CSV，再重放系数和误差指标。PR #20单独检出时28项原测试通过，依赖PR #19的1项生成测试明确跳过；联合源码候选82项全部通过，0跳过。逐项证据见[review-validation.json](../../experiments/dual-channel/ode-linked/review-validation.json)。
- 原双通道早期日志更名为[2026-10-11-yrx-dual-channel.md](2026-10-11-yrx-dual-channel.md)，正文完整保留，避免与PR #19同日ODE日志发生add/add冲突。
- 已对照INDEX：本次只补齐候选工作的复现性，模拟证据边界和项目级状态保持不变；已有INDEX工作区修改保留，未纳入本修复。接纳时仍由集成者核对两个PR原有权威更新建议及最终合并提交。
