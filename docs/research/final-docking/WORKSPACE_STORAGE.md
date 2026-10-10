# Docking 工作区与保存方案

核验日期：2026-09-30。用途：决定本机项目是否保存、保存到网盘时选择哪些文件；不是科学结果的重新评估。下列大小按文件字节统计，未包含本地 Git，可能与 du 的磁盘占用略有差异。

## 建议

推荐保存精简档案：约 **187.0 MiB**，包含现有代码、配置、环境定义、结构输入、对接姿态、ProLIF 数值结果、残基映射和突变建议，移除可重建的 receptor.json 与可选原始大文件。若希望重做 ProLIF 时省去 Meeko receptor 预处理，则保存约 **512.5 MiB**，额外保留全部 receptor.json。

AF2 内部 pickle 与 Phyre2 完整任务包已于 2026-09-30 按用户明确要求删除，释放 **2,430,350,870 字节（2.26 GiB）**。删除前逐文件核对大小与 SHA256，记录见 [已删除文件清单](storage-review/2026-09-30-removed-files.tsv)。当前结构、分数、拓扑和五套 c7xmsA 比对继续保留。`.git/` 约 173 MiB，按用户要求不纳入网盘方案。

## 值得保留

| 内容 | 保留原因 |
| --- | --- |
| src、scripts、configs、env | GUI/CLI、Vina 与 ProLIF 批处理、固定 box、环境版本和 AF2 relax 构建器；现有代码与修改不能依赖远端恢复 |
| inputs/ligands | ASCR3/ASCR18 去质子化配体、SDF/PDBQT、原子映射 |
| inputs/receptors | FASTA、AF2/AF3 结构与分数、原始 CIF/full_data、WT/截短/对齐/PDBQT、DeepTMHMM/MEMSAT 拓扑 |
| inputs/receptors/alignments/phyre2-c7xmsA | 五受体 c7xmsA 原始比对 TXT/HTML，保留生物学报告真正使用的 Phyre2 证据 |
| outputs/af3 | 35 个受体模型 × ASCR3/ASCR18，共 70 组 Vina 姿态与日志；所有批次源姿态路径存在 |
| outputs/prolif-batch-full/af3 | 70 组 completed 的 pose SDF、IFP pickle、CSV、运行元数据、batch manifest 与源工作簿 |
| outputs/msa-prolif-evidence-20260826 | 生物学报告、残基映射表、完整配对矩阵、场景脚本及补回项目内的原分析来源 |
| mutants | 突变组合建议工作簿；保留为实验设计线索 |
| archive/receptor-prediction-raw | 小体积 AF2 辅助文件、AF3 A3M/templates 与拓扑图；与当前分析存在来源关系 |
| archive/historical-results、archive/notes | 历史 review export（含原校验记录）与 info_record.pptx；体积小，适合保留背景 |

## 已删除与仍可排除

| 路径/文件 | 原因与影响 |
| --- | --- |
| 已删除：AF2 ColabFold 的 20 个 pickle，约 1.71 GiB | 完整 AF2 内部预测对象；当前结构与分数已在 inputs 保留。删除后不能读取旧运行的全部内部 tensor，需要重新预测才能重建该层 |
| 已删除：Phyre2 完整任务包，约 0.57 GiB | Phyre2 全任务网页、模板与运行日志；当前采用的拓扑和五套 c7xmsA 比对已保存。已不保留旧任务的全部网页、模板和运行日志 |
| outputs/prolif-batch-full 下 35 个 receptor.json，约 325.6 MiB | Meeko 预处理受体序列化对象；可按现有输入和批处理脚本重建。CSV/姿态/元数据和结果分析不随其删除 |
| .git | Git 本地历史/LFS 缓存，不进入网盘档案；本轮未删除 |
| Finder/Python 缓存 | 本轮已清理约 0.27 MiB，见审查记录 |

## 目录结构

```text
docking/
├── INDEX.md                          保存说明入口
├── src/                              GUI、结构处理和分析 CLI
├── scripts/                          Vina、ProLIF、CSV 汇总脚本
├── configs/boxes.tsv                  固定搜索空间
├── env/                              环境定义、安装说明、relax 构建器/小 wheel
├── inputs/
│   ├── ligands/                      配体及原子映射
│   └── receptors/                    FASTA、AF2、AF3、PDBQT、拓扑和 c7xmsA 比对
├── outputs/
│   ├── af3/                          70 组 docking 姿态
│   ├── prolif-batch-full/af3/         IFP、CSV、SDF、元数据、汇总工作簿
│   └── msa-prolif-evidence-20260826/  生物学报告和来源快照
├── mutants/                          突变建议工作簿
├── archive/
│   ├── receptor-prediction-raw/       建议保留的小型预测证据
│   ├── historical-results/           历史结果
│   └── notes/                        旧汇报
└── docs/                             E2 手册、本说明、审查清单
```

## 整理与验证

四个根目录批处理脚本移到 scripts，boxes.tsv 移到 configs；已修正脚本默认项目根目录、ProLIF 子脚本和 box 路径。环境安装说明中的命令也改为实际 env 路径。科学数据路径保持，除可选原始档案归拢；逐文件原哈希确认科学数据字节不变。

从 .codex 可视化目录补回两组 ProLIF 原分析 CSV/报告快照，逐文件哈希一致；五套 c7xmsA 比对补入 inputs。生物学报告的对应来源链接与突变工作簿的临时路径已改指项目内文件。文献链接仍指原论文，未下载论文全文。本方案足以保存本次结果与其现存本地证据，不承诺脱离依赖环境即可完全重算。

验证通过：batch_prolif --dry-run 自动发现 70 jobs／35 models；原 batch manifest 的 70 行均为 completed，源姿态全部存在；merge_prolif_csv 在 /private/tmp 输出 3 种 CSV × 2 种布局，每份覆盖 70 source blocks／35 models；Python AST、bash -n 和 git diff --check 通过。没有启动新的 docking、relax 或 ProLIF 计算。

整理前工作区已有 13 个修改、123 个删除和 39 个未跟踪条目（按 git 的目录折叠视图）。原删除没有恢复或扩大到其他源码；完整旧状态见 [整理前状态](storage-review/2026-09-30-status-before.txt)。当前仓库未配置 Git remote，因此保存当前源码和未跟踪材料有必要；本轮未提交或推送。

## 所引与被引

所引：[逐文件 SHA256 与分类清单](storage-review/2026-09-30-file-inventory.tsv)、[脚本移动记录](storage-review/2026-09-30-moves.tsv)、[来源快照记录](storage-review/2026-09-30-imported-evidence.tsv)、batch_manifest.csv、现有分析报告和输入。当前分类字段 KEEP 为精简方案、OPTIONAL_REGENERABLE 为可重建 receptor.json；OPTIONAL_RAW 仅出现在已删除清单中。

被引：根 INDEX.md 和本次对话。其他引用未穷尽检索。清单是核对身份与选择范围的工具，不是备份；尚未上传网盘。
