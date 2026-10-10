# 数据交付与使用边界

当前交付由普通 Git 文件与十个必要 LFS 包组成，按[数据恢复说明](../DATA_DELIVERY.md)获取并校验。包级及逐文件校验值分别由 [lfs-release.json](lfs-release.json)、[lfs-files.csv](lfs-files.csv) 与 [release-git.sha256](release-git.sha256)维护。

`full` 验证核对报告来源、间接受体和八批输出，不代表科学计算重新运行。研究脚本仍保留部分历史环境和路径；重新计算前须按各批方法与实际软件环境适配。其他历史路线资料不属于本次数据发布。

[七组整理计划](COMMIT_PLAN.md)仅用于理解 PR #18 的原始组织方式；它不是当前提交指令，也不再要求用户发送六个飞书附件。
