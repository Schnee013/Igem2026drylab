# 飞书附件与数据恢复

GitHub保存研究说明、脚本、方法定义、解析结果表、图表和来源记录。原始输入、结构、pose、日志和运行副本通过以下六个ZIP交付。附件已本地生成，实际发送由用户完成。

| 文件 | 恢复文件数 | 压缩后MiB |
|---|---:|---:|
| `docking-analysis-objects.zip` | 70 | 0.88 |
| `docking-prepared-receptors.zip` | 176 | 125.64 |
| `docking-source-archives.zip` | 36 | 338.25 |
| `docking-structure-predictions.zip` | 3,698 | 326.66 |
| `docking-supporting-copies.zip` | 34 | 1.11 |
| `docking-runtime-payloads.zip` | 4,698 | 72.66 |

前五包分别保存受体准备数据、结构预测、原始压缩包、序列化分析对象及历史副本；runtime-payloads补充原始结构、对接输出、运行日志、序列输入与逐任务配置副本。全部附件共恢复8,712个文件。

包级SHA256见[附件清单](provenance/feishu-archives.json)，逐文件位置与SHA256见[恢复清单](provenance/feishu-files.csv)，用途与恢复来源见[payload manifest](provenance/payload_manifest.tsv)。README和解析分析表可直接阅读；指向原始结构、日志或输入文件的链接需要先恢复附件。

## 接收者操作

将六个ZIP下载到同一个目录，保持文件名。在本项目根目录运行：

```bash
python3 provenance/verify_delivery.py --mode github
python3 provenance/restore_feishu.py --archives "/实际路径/飞书附件"
python3 provenance/verify_delivery.py --mode full
```

Python需3.9或以上；工具仅使用标准库。恢复器先校验所有包和已有目标文件，再逐文件写入。已有文件哈希相同则跳过；同名内容不同则停止并保留现场。ZIP成员恢复到本项目原相对路径。

完整模式同时核对报告来源哈希、122个间接受体依赖、272组突变输出、文档链接和Python语法。核验不启动科学计算；科学CLI仍保留部分历史路径，重运行前需适配环境和路径。

附件路径已准确列入本目录.gitignore。Git暂存按[七组任务清单](provenance/commit-files.csv)进行，恢复后的数据留在本地。
