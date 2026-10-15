---
direction: P0-signal-pathway-ode
status: source_grounded_prototype_uncalibrated
priority: P0
chassis_dependent: true
last_updated: 2026-10-11
---

# 文献公共核心 ODE 原型

本版为异源受体—酵母通路—显色链提供机制解释，保留原Phase 0/1及Phase 2入口，新增独立运行入口。五个公共核心方程采用Supady Model B / Delft对应反应，一条显色方程由原版输出代数合并。来源参数在本版固定，项目输入输出采用有标记的假设值；当前结果用于结构演示和后续校准接口设计。

## 代码与运行

- [模型](../../src/modeling/ode/literature_core.py)、[运行器](../../src/modeling/ode/run_literature_core.py)、[作图](../../src/modeling/ode/plot_literature_core.py)。
- [来源速率及初值](../../experiments/ode-model/configs/literature_core_source.json)、[项目端点配置](../../experiments/ode-model/configs/literature_core_project.json)。
- [测试](../../tests/modeling/test_ode_literature_core.py)、[验证摘要](../../experiments/ode-model/literature-core/verification.json)。依赖NumPy、SciPy，作图另需Matplotlib；实际版本见验证摘要。

在仓库根运行：

```sh
python -m src.modeling.ode.run_literature_core --output temp/ode-literature-core
python -m src.modeling.ode.plot_literature_core temp/ode-literature-core/timecourses.csv
python -m unittest discover -s tests/modeling -p 'test_ode*.py' -v
```

每次运行的 `--output` 必须为尚不存在的目录。运行器在计算前原子创建该目录，已有目录（包括空目录）或文件会被拒绝，确保 CSV、图片、`run.json` 和事件记录保持同一运行身份。失败运行保留其目录；重试时使用新路径。

运行器支持`--parameters`、`--source`、`--ligand`、`--hours`、`--output`。默认归一化输入0、0.1、1、10，8小时；结果包含全部重建分子状态及颜色，run.json绑定参数、软件版本、输入和CSV校验和。时间曲线、图片和原始运行日志可重新生成并保存在本地；仓库只保存规范输入与紧凑验证。

## 六个独立方程

H为G三聚体，A为Gα-GTP，Q为有效支架复合物，F*为活化Fus3，Z*为来源模型的活化Sst2状态，C为颜色。核心时间用秒、浓度用µM。

| 方程 | 生物学解释 |
|---|---|
| H' = -uH + k5 DB | G蛋白解离与重新组装 |
| A' = uH - (k4+k41 Z*)A | 活化Gα产生和GTP水解 |
| Q' = k6 SB - (k7+k71 Z*)Q | 支架模块装配与反馈调节的解离 |
| F*' = k8 QF - (k9+k91 Z)F* | 来源模型的Fus3活化和失活 |
| Z*' = k10 F*Z - k11 Z* | 来源模型的反馈状态形成与消退 |
| C' = [b+a m^n/(K^n+m^n)-delta C]/3600 | 有效产色及损失；小时速率换算为秒 |

代数接口：`u=u_max*L/(K_L+L)`、`m=F*/Tf`。固定池Ta、Tb、Ts、Tf、Tz从来源初始浓度计算；`D=Ta-H-A`、`B=Tb-H-Q`、`S=Ts-Q`、`F=Tf-F*`、`Z=Tz-Z*`。从10个核心状态消去5个重复状态是守恒下的等价变换，未新增快平衡假设。跨小时维持固定蛋白总量则是来源迁移假设。

## 复用与参数接口

原模型是3个ODE和3个代数关系、18个配置字段。此版以整套公共核心替换原G/M有效速率；固定11个内部速率条目（含k9=0）与来源初值。原来源k3和初始受体量只用于给u_max设演示尺度。

两端7个有效参数为u_max、K_L、b、a、K、n、delta，当前均为假设。n默认固定2，留下6个潜在校准量；仅凭终点颜色不保证可分别识别，来源池大小和内部速率可迁移性也仍需适用性判断。

固定N后，将原TF=bT+E*M^n/(KT^n+M^n)、Prod=l+N*g*TF/(D+TF)、C'=p*Prod-delta*C精确合并：

`b=p*(l+N*g*bT/(D+bT))`

`a=p*N*g*D*E/((D+bT)*(D+bT+E))`

`K=KT*((D+bT)/(D+bT+E))^(1/n)`

n、delta沿用原值。新Fus3比例代替原M另属项目适配假设；不再分别解释拷贝数、转录增益和酶表达贡献。输入固定指数1、基础驱动0且持续恒定，未保留来源受体下调；输出未独立追踪转录、酶积累和色素成熟延迟。

## 证据边界和版本记录

[来源核对](../papers/ode-literature-core/source-evidence.md)记录Delft原图中的Fus3符号及k91单位冲突、修正理由、Supady原图缺口，以及带日期的构建适用性。来源反应重建不等于原作者软件原样复现，也不证明内部参数已在项目菌株测定。

| 版本 | 修改理由 | 实现与验证 |
|---|---|---|
| 原最小模型 | 给完整链提供工作起点 | 原solver/config保持原样，继续运行既有测试 |
| 来源核心及有效输出 | 降低需自行确定的内部速率数量 | 来源反应守恒重建；输出合并等价测试 |
| 六状态可配置实现 | 消去守恒导致的重复状态，提供清晰校准入口 | 与独立11状态反应实现逐状态比较；零输入解析解；CLI异目录运行 |

默认非零输入的长期颜色接近饱和，当前示例不能证明浓度分辨能力。数值测试支持计算一致性；实验验证、实际响应时间和检测限尚未完成。

本ODE解释ascr刺激如何产生颜色。线虫丰度与混合样本背景的反推属于双通道实验校准，Eco接收的是有害线虫密度；此版不将颜色或ODE参数直接转换为风险或收益。

## 依赖关系

- 依赖于：来源参数配置、证据表、当前构建确认；项目数据优先约束背景、有效剂量尺度和整体输出。
- 输出到：机制解释、后续端点校准及Wiki建模方法；代码和验证材料可供其他队伍复用。
