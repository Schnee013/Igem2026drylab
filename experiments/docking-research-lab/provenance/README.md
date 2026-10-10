# 来源 迁移与交付核验

[文件映射](file-map.csv)记录原项目相对路径、交付位置、来源SHA256及字节数。原研究数据、科学脚本和运行记录保留内容；阅读文档的链接适配另见[文档修改记录](documentation-changes.json)。[checksums.sha256](checksums.sha256)记录整理完成时的交付内容。

[复制检查](copy-verification.json)记录初次复制校验；[源快照](source-snapshot.json)记录纳入交付的源文件；[排除清单](excluded-files.json)记录未纳入项。原目录保持原样，交付中的新说明、表格和核验脚本见[新增文件清单](generated-files.json)。

## 只读核验与数据恢复

GitHub目录先运行：

```bash
python3 provenance/verify_delivery.py --mode github
```

取得飞书六个附件后，按[恢复说明](../DATA_DELIVERY.md)运行restore_feishu.py，再运行：

```bash
python3 provenance/verify_delivery.py --mode full
```

完整模式检查文件校验值、两份报告所列来源、122个间接受体依赖、八批输出、阅读链接和语法。默认GitHub模式允许清单中已明确列出的飞书文件尚未恢复；它不等同完整科学来源核验。

原JSON中的历史路径通过file-map.csv映射。checksums.sha256覆盖GitHub与恢复后的飞书内容；verify_research.py保存完整科研文件检查逻辑，由完整模式调用。

发布分工见[PUBLICATION_SCOPE.md](PUBLICATION_SCOPE.md)，来源复制和历史验证记录保留当时的范围与日期。
