# 2026-10-11 双通道校准本地实现

任务于 10 月 10 日开始，按 AGENTS / DOCMAP 核对 origin/main `6ec153d6d331d39b2b95736c9bd46dd5814738c1`；原工作区为干净的 `feature/ode-phase2b-sensitivity`，HEAD `2c5bb816`。通过 fetch 核对后在独立 detached worktree 实现，原分支保持原状。

新增[方法入口](../modeling/P1-dual-channel-calibration.md)、[实验模板与模拟](../../experiments/dual-channel/README.md)、[接口](../../src/modeling/dual_channel/calibration.py)及[测试](../../tests/modeling/test_dual_channel.py)。Eco 阈值、单位和上限由 main 的配置/实现读取。文献交叉核验 Manosalva 2015 Results，保留 C. elegans 也产生 ascr#18 的证据边界。

运行 `python -m unittest tests.modeling.test_dual_channel tests.modeling.test_eco_model -q`：28 tests OK。固定种子模拟成功生成配对 CSV、留出比较及阈值跨越情景；数值权威在 simulation.json。采集模板核对 27 个唯一样本、9 个组合各 3 份、按批次划分 18/9；未填实测数值。

INDEX 新增该活跃入口，状态为模拟接口、等待实测。本轮交付范围为本地探索性原型。

按用户要求收缩任务，复用既有结果在实验 README 中补充一个“读数→密度→Eco”完整例子，保留真实标定待完成的证据状态。
