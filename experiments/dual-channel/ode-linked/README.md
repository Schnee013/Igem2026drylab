# 固定 ODE 输出上的双通道模拟校准

- `source`：[provenance.json](provenance.json)固定研究工作区v4、ODE r04、双通道r01及上游实现的身份；本目录仅导入精简配对快照。
- `as_of`：2026-10-13。
- `allowed_use`：复现三系数训练、单/双通道比较、固定参数下的比例变化检查与Eco条件情景；供方法叙事和审阅使用。
- `update_trigger`：输入样本、ODE参数、读数单位、校准代码或Eco配置变化时另建版本并重新核验。

## 文件角色

| 文件 | 角色 |
|---|---|
| [inputs/scenario.json](inputs/scenario.json) | 接纳为规范输入的Mi 1∶10、Ce 10∶1、等两配体总量假设与协议快照 |
| [inputs/ode-endpoints.csv](inputs/ode-endpoints.csv) | 接纳为规范输入的上游18个通道端点，用于追溯预设与ODE实际显色 |
| [inputs/calibration.csv](inputs/calibration.csv) | 接纳为规范输入的9行配对ODE颜色；列x3/x18为空白校正A480，target为Mi J2/100 cm³ |
| [inputs/evaluation.csv](inputs/evaluation.csv) | 接纳为规范输入的36行新组合；三个Mi比例各12行，同一套固定ODE与回归配置 |
| [results/model.json](results/model.json) | 已审阅的精简模型结果；仅对应上述模拟协议 |
| [results/summary.json](results/summary.json) | 已审阅的精简误差与范围结果；所有数值报告以此为源 |
| [provenance.json](provenance.json) | 上游提交、本地恢复路径、原始文件字节数与SHA256 |
| [payload-manifest.tsv](payload-manifest.tsv) | 规范输入、精简结果与本地运行产物的跟踪分类 |
| [validation.json](validation.json) | PR准备时的模板、接口和重放检查记录 |

科学背景、Ce的作用、文献支持范围及实测替换流程见[方法文档](../../../docs/modeling/P1-dual-channel-calibration.md)。Mi J2与Ce L4在本次模拟中只定义样本标签，单虫释放率没有按虫龄作实测差异设定。

## 可复现的范围与命令

从仓库根目录执行，输出目录必须尚不存在：

```sh
python -m src.modeling.dual_channel.replay \
  --input-dir experiments/dual-channel/ode-linked/inputs \
  --output /tmp/dual-channel-replay \
  --eco-config experiments/economic/configs/eco_model_example_model.json \
  --protocol-id SIM_V4_MI1TO10_CE10TO1_Q1_8H_A480
```

命令调用现有fit/predict/eco_scenarios，输出重放摘要、逐样本诊断和一张图。它复现从已保存ODE读数到密度/Eco的阶段；重新求解或拟合ODE需使用来源清单中的上游实现、配置与运行脚本。文献PDF、完整轨迹和搜索历史保留于原研究目录；本PR不要求复制这些运行材料。

校准点和新组合均为确定性模拟，评价点不是独立生物学验证。负预测及越界结果保留并阻止Eco调用。形式预测区间来自OLS残差，不具有已验证的实测95%覆盖率；区间跨阈值时仅返回条件情景。当前比例变化检查不包含全部生物学或仪器不确定性。

## 迭代边界

先由固定的配体到色素映射设置显色终点，再拟合ODE的K_L和a；随后固定ODE，用其实际输出训练三个回归系数。用户确认Mi比例从1∶100改为1∶10后产生v4/r04/r01，本目录以该组为审阅快照。最后的收束与PR整理仅迁移输入、结果、解释和复现入口，没有再次选择参数或改写性能数值。

湿实验的27行采集计划独立于此处9行模拟校准点，模板中的待确认项继续保留。未来实测训练另建版本，按独立样本或批次留出验证。
