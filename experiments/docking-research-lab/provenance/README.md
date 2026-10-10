# 来源、迁移与交付核验

当前交付入口见[必要数据恢复](../DATA_DELIVERY.md)。[LFS 包清单](lfs-release.json)记录十个包；[恢复映射](lfs-files.csv)记录它们与原研究路径的关系；[普通 Git 校验值](release-git.sha256)记录当前紧凑文件；[payload manifest](payload_manifest.tsv)区分发布与本地历史材料。

在仓库根目录运行：

```bash
python3 experiments/docking-research-lab/provenance/verify_delivery.py --mode github
python3 experiments/docking-research-lab/provenance/restore_lfs.py
python3 experiments/docking-research-lab/provenance/verify_delivery.py --mode full
```

恢复前先按[数据恢复说明](../DATA_DELIVERY.md)获取 LFS。`full` 检查本次发布内容、报告全部来源、间接受体和八批输出；历史材料的阅读链接单列，不冒充已恢复。科学计算未重运行。

[文件映射](file-map.csv)记录原研究路径到交付路径及来源哈希，用于解析报告中的历史路径。[源快照](source-snapshot.json)、[复制检查](copy-verification.json)、[文档修改记录](documentation-changes.json)、[新增文件记录](generated-files.json)、[排除清单](excluded-files.json)保留 PR #18 整理时的范围与日期。

旧 `feishu-archives.json`、`feishu-files.csv`、`checksums.sha256`、`validation-result.json` 与 `commit-files.csv` 是当时的六附件交付快照。`restore_feishu.py` 仅用于持有完整旧附件的历史恢复；`verify_research.py` 保留旧整体校验逻辑，并提供当前交付复用的科学来源检查函数。当前验证入口始终是 `verify_delivery.py`。
