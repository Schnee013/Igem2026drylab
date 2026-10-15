# 双通道校准交付入口

当前可审阅交付为三系数接口、湿实验模板，以及[ODE联合模拟训练](ode-linked/README.md)。科学解释和适用边界以[方法文档](../../docs/modeling/P1-dual-channel-calibration.md)为准；后续写作从[上下文交接](../../codex/docs/plans/dual-channel-writing-handoff-20261013.md)进入。

- [27行采集模板](templates/paired_samples.csv)：每行一个独立样本，均为planned_not_measured。
- [待确认protocol](templates/protocol.json)：实际虫龄、密度档位、空白、显色时间等等待湿实验确认，模拟值不自动填入。
- [ODE联合输入和结果](ode-linked/README.md)：当前以固定的ODE配对输出复现三系数校准。
- [早期通用演示生成器](../../src/modeling/dual_channel/demo.py)：任意单位线性混合、噪声和批次偏移的接口演示，属于历史示例；重跑结果另存本地目录，不与当前吸光度系数混用。

从仓库根目录检查接口：

```sh
python -m unittest tests.modeling.test_dual_channel tests.modeling.test_eco_model -q
```

NumPy、SciPy用于回归与区间；ODE联合重放作图另需Matplotlib。当前无自动接纳实测CSV的入口；实际计数、密度换算、技术重复汇总和protocol/QC核对见方法文档。
