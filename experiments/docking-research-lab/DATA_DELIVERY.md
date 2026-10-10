# 必要数据与 Git LFS 恢复

Git 保存研究说明、脚本、方法、解析表格和图表，以及小型序列、参数、预测请求、置信度摘要和必要运行证据。Git LFS 保存支撑 01–08 批突变研究、初始选位和已有 MD 输入关系的必要原始数据。

| LFS 数据 | 内容 | 文件数 | MiB |
|---|---|---:|---:|
| AF3 原始返回 | 02–08 批的 8 个原始 ZIP；05 批分为两包 | 8 | 262.39 |
| 接触分析受体 | 01–08 批的 136 个唯一受体 JSON，保存 Meeko 化学模板、原子及氢坐标 | 1 | 95.26 |
| 正式结构和姿势 | 1,098 个唯一文件：八批受体/pose、初筛接触输入和已有 MD 输入结构 | 1 | 18.52 |
| 合计 | 10 个 LFS 文件 | 10 | 376.17 |

AF3 原始包包含 133 个预测任务（127 个突变体任务和 6 个 WT/基准任务）；不同批次可包含相同突变，不能把任务数解释为独立突变设计数。原始包保留所有预测模型及置信度，实际使用模型以各批模型选择记录为准，包括 W338C 的 model_1。

数据按既有 Docking 线保存：

- `experiments/docking/receptors/final-docking/af3/`：8 个 AF3 原始 ZIP。
- `experiments/docking-repro/prepared/final-docking/core-receptors.zip`：136 个受体对象。
- `experiments/docking-repro/results/final-docking/core-structures.zip`：1,098 个结构和姿势。

[LFS 包清单](provenance/lfs-release.json)记录精确位置、字节数和 SHA256；[恢复映射](provenance/lfs-files.csv)将唯一保存的内容恢复到现有研究脚本引用的原路径。预测文件从原始 AF3 包恢复，重复的交接结构和受体复用相同内容。无需再上传一套展开预测文件或展示副本。

## 获取与恢复

安装 Git LFS 后，在仓库根目录运行以下命令。GitHub 仓库的访问权限仍适用；LFS 不会改变仓库可见性。

```bash
git lfs install --local
git lfs pull --include="experiments/docking/receptors/final-docking/af3/*.zip,experiments/docking-repro/prepared/final-docking/core-receptors.zip,experiments/docking-repro/results/final-docking/core-structures.zip"
python3 experiments/docking-research-lab/provenance/verify_delivery.py --mode github
python3 experiments/docking-research-lab/provenance/restore_lfs.py
python3 experiments/docking-research-lab/provenance/verify_delivery.py --mode full
```

Python 需 3.9 或以上，恢复和验证只使用标准库。恢复器先校验全部 LFS 包及目标路径；已有文件内容相同则跳过，不同则停止并保留原文件。恢复数据继续被忽略，不作为第二份普通 Git 数据提交。

`github` 模式仅核对普通 Git 文件。`full` 模式核对本次发布的 LFS 包、恢复文件、两份报告的全部来源哈希、122 个间接受体依赖和八批共 272 组对接输出，并检查阅读链接。它不重运行 AF3、对接、接触分析或 MD。

## 发布范围

本次不要求原来的六个飞书附件齐全。其他历史预测、SwissDock/其他受体与协议探索、70 个旧 pickle、展示副本和整理备份不进入本次 LFS；原始附件未删除。指向这些材料的历史阅读链接可能需要本地旧附件，验证结果会单列这些链接，不能据此宣称整个历史研究目录已恢复。

详细取舍见[发布范围](provenance/PUBLICATION_SCOPE.md)。[payload manifest](provenance/payload_manifest.tsv)逐项区分普通 Git、LFS 可恢复、仓库已有内容复用和仅在本地的历史材料。旧 `feishu-*` 清单及 `checksums.sha256` 保留为 PR #18 导入快照；当前交付使用 `lfs-release.json`、`lfs-files.csv` 和 `release-git.sha256`。
