# 数据发布范围

GitHub保留文档、脚本、方法定义、解析表格和图表、紧凑验证结果及来源清单。飞书保存可通过附件和校验值恢复的原始输入、结构、pose、运行日志、运行配置副本、预测详情和分析对象。

该划分按目标仓库docs/ops/payload-tracking-policy.md落实。全部8,712个外部文件及用途见[payload manifest](payload_manifest.tsv)，准确恢复路径见[feishu-files.csv](feishu-files.csv)。Git文件以[commit-files.csv](commit-files.csv)为准。

[初步分类](publication-file-classification.csv)和[初步统计](publication-classification-summary.json)保留此前按体积筛选的历史结果；当前发布范围以上述实际清单为准。

两份报告直接引用2,271个不同来源文件，接触metadata进一步引用122个受体JSON。完整来源检查需要恢复全部六个附件；依赖记录见[分析清单](analysis-publication-dependencies.csv)，操作见[数据恢复](../DATA_DELIVERY.md)。

原科研目录和local-full完整副本保留。附件已本地生成，发送状态由实际传输记录确认。
