# Docking 并入现有研究线

按现有文件用途拆分，各分类下的子路径统一以 `final-docking/` 开头。2026-10-10 已完成本地导入、路径适配和验证；[逐文件执行与校验记录](../../../docs/research/local-remote-sync-20261008/docking-import-execution-20261010.json)记录最终身份。源目录保留；本地提交与发布状态回 [INDEX](../../../docs/INDEX.md)。

## 目录

| 内容 | 目标位置 |
|---|---|
| 结构处理、准备、GUI、Vina/ProLIF 及批处理代码 | `src/modeling/docking-repro/final-docking/` |
| 搜索盒配置 | `src/modeling/docking-repro/final-docking/configs/boxes.tsv` |
| 受体序列、预测结构、置信度、拓扑与比对 | `experiments/docking-repro/receptors/final-docking/` |
| 配体及原子映射 | `experiments/docking-repro/ligands/final-docking/` |
| 准备后的受体与配体 | `experiments/docking-repro/prepared/final-docking/` |
| Vina 姿态和得分 | `experiments/docking-repro/results/final-docking/vina/` |
| ProLIF 指纹、CSV、SDF 和汇总结果 | `experiments/docking-repro/results/final-docking/prolif/` |
| 残基对应、数值矩阵与比较分析 | `experiments/docking-repro/analysis/final-docking/` |
| 突变组合建议 | `experiments/docking-repro/mutagenesis/final-docking/` |
| 研究报告 | `docs/modeling/final-docking/` |
| 依赖和安装说明 | `environments/final-docking/` |
| 运行时构建器 | `scripts/final-docking/` |
| E2 使用说明 | `docs/ops/final-docking/` |
| 已有保存记录 | `docs/research/final-docking/` |
| 展示材料 | `docs/presentation/reference-materials/final-docking/` |

旧 review export 放到 `analysis/final-docking/archive/`；预测辅助材料放到 `receptors/final-docking/source-archives/`。35 个可重建的 `receptor.json` 和运行时 wheel 仍按原分类放仓库外，对应位置改为 `/Users/roy/Documents/drylab-payloads/final-docking/`。

现有 P0 Docking 入口只补链接；项目级 Git 规则按需调整，不把独立项目的首页和规则整份复制成第二套入口。全部逐文件去向见[对应表](../../../docs/research/local-remote-sync-20261008/docking-import-path-map-20261009.tsv)。

## 说明写到什么程度

`final-docking/` 已经说明归属，不再为每个文件重复添加“来自独立 Docking”“某日并入”“最终批次”等标签，不在各层 README 复述本次整理决定。

只说明阅读或运行确实需要知道的内容：

- 受体、配体、突变和模型的具体身份；
- 截短范围、残基编号对应、结构对齐及配体电荷状态；
- 输入、程序、结果之间的关联和运行方法；
- 指标定义、统计分母和已有报告的解释限制。

能从路径或文件名看懂的不再重复写。既有原始数据、数值和运行记录不插入整理说明。

## 路径适配

1. 原 `src/` 和四个批处理脚本归到同一个代码子目录。`cif_to_pdb.py` 在 `final-docking/` 内保留原名，不再需要为了避开旧目录同名文件而改名。
2. 批处理原先从项目根找 `inputs/outputs/configs`；拆分后显式配置受体、配体、搜索盒和结果路径。GUI 导入和工具注册一起检查。
3. `run_all_vina.sh` 的默认输出与已保存结果目录不同；统一指向拟定的 Vina 结果目录。
4. 将 5 条 MD 外部引用改为对应的仓库内结构、序列和姿态，逐一核对内容。新旧目标见[路径核验摘要](../../../docs/research/local-remote-sync-20261008/docking-import-summary-20261009.json)。
5. 修正报告、CSV 清单和可执行配置中的路径；保留科学对象的原标识，避免把全长、截短和不同坐标系混为一份输入。

## 执行及检查

本轮按用户指令导入原研究目录；复制前核对全部源文件，并对照远端 `38bbf5ba` 确认目标路径没有冲突。后续提交以实时 main 为基线核对增量；源目录保留。

验证代码入口、既有测试、70 组任务发现、CSV 汇总、残基映射、关键数值和 5 条 MD 引用。输出写入临时目录；数据身份核对不等于重新运行 Vina、ProLIF 或 MD。

对应表覆盖 1,369 个非缓存文件：1,366 个文件的目标位置位于各分类的 `final-docking/` 下，另外 3 项为既有项目入口/规则的合并处理。文件身份来自 10 月 9 日清点；10 月 10 日按用户要求更新路径和说明方式，执行时已重新核对全部来源哈希。

所引：源 Docking 文件、逐文件对应表、路径核验摘要及 [payload policy](../../../docs/ops/payload-tracking-policy.md)。被引：[同步方案](local-remote-sync-20261008.md)、[计划索引](README.md)和 [INDEX](../../../docs/INDEX.md)。
