# DO-4：独立任务认领
> **前置条件**：DO-1/2/3 完成
> **预计耗时**：阅读 30 分钟，然后开始独立工作
> **学完能做**：选一个任务，说出第一步是什么，开始做
---
## 1. 你现在能做的四件事
### a) 跑一个新突变
从双通道全谱排名里选一个未做饱和扫描的 Channel A moderate 位点，或在已有位点上探索新替换组合。全流程就是 DO-2 再走一遍，换个位点。
**第一步**：打开 `experiments/docking-repro/analysis/ratio_channel_report.md` → 找 Channel A moderate 列表 → 选一个你感兴趣的位点 → 回到 DO-2 §1。
### b) PyMOL 渲染 Top 6 高质量截图
PI 需要的交付物：Top 6 的高质量 PyMOL 截图（PNG + PSE 场景文件）。6 个候选 × 2 视角（overview + detail）= 12 张图。
**第一步**：打开 `experiments/docking-repro/analysis/pymol_top6/` → 按 DO-3 §3 的流程渲染 → 每张图按出图规范标注。
### c) 双通道 Channel B 候选的阴性对照设计
研究型任务。Channel B 有 11 条候选但无独立阳性对照验证（KNOW-3 §3 局限性 #8）。你可以在 Gpr2/Gpr3 上选已知无影响残基，设计阴性对照实验来检验 Channel B 的 3σ 阈值是否能区分真信号和噪声。
> ⚠️ 此任务需要 KNOW-2 §4 的对照设计思路 + 独立实验设计能力，难度高于 task (a)/(b)，建议先和我讨论方案再动手。
**第一步**：读 `experiments/docking-repro/analysis/ratio_channel_report.md` → 理解 Channel B 的定义和候选列表 → 构思对照设计 → 和我讨论。
### d) 加入 MD 方向调研
如果对动力学模拟感兴趣，可以开始 GROMACS 学习。这条路径需要额外学习成本，但 MD 是 V138R 盐桥假说和 F170E 入口静电路径的唯一实证手段。
**第一步**：读 `docs/modeling/P0-md-simulation.md` → 完成 GROMACS lysozyme tutorial（官方入门教程）→ 学习 CHARMM-GUI 膜蛋白体系搭建。
---
## 2. 工作规范
### 结果放哪
| 产出类型 | 存放目录 |
|---------|---------|
| 新突变的对接结果 JSON | `experiments/docking-repro/mutagenesis/` |
| PyMOL 截图 | `experiments/docking-repro/analysis/pymol_top6/output/` |
| 新建的分析脚本 | `experiments/docking-repro/analysis/` |
| 对照实验设计文档 | `docs/modeling/` |
### 怎么记录
跑完一轮之后写一条日志到 `docs/logs/YYYY-MM-DD.md`——说清楚做了什么、结果是什么、有没有异常。日志是跨会话恢复上下文的唯一来源。
### 卡住了怎么办
1. 先查 **REF**（工具版本 → REF-A / 常见坑 → REF-B / 代码目录 → REF-C / SSH → REF-D）
2. 再问 AI（推荐用**两个 AI 交叉验证**——一个给方案，另一个检查方案是否合理）
3. 如果 1+2 解决不了 → 在群里问我，附上你做了什么、卡在哪一步、错误信息是什么
