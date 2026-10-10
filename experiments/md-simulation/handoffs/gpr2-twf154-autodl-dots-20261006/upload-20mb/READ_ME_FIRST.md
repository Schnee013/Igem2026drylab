# 20 MB 限制下的完整材料传输

本目录的 `drylab-md-v3-01-of-05.zip` 至 `drylab-md-v3-05-of-05.zip` 是五个普通 ZIP 附件，每个小于 20,000,000 字节。必须全部收到。它们是 v3-new-access 完整交接包的无损分块，不是五个可单独执行的体系。

旧凭据已作废，旧 `PRIVATE_ACCESS.txt` 已删除；不得尝试或要求重传。用户在完整提示词开头填写新的 SSH 密钥/密码，或指定新私钥附件。未填写时只能先做离线检查。五个分卷都不含新旧凭据；本传输方式不改变六组、100 ns、输入身份或邮件模板。

## 给狼尊的恢复顺序

1. 将五个 ZIP 附件放到同一个工作目录，保留附件名。
2. 从第 1 个 ZIP 提取 `restore_handoff.py` 与 `SPLIT_MANIFEST.json` 到该目录。其余附件不必先解压。
3. 在该目录执行 `python3 restore_handoff.py --parts-dir . --output-dir .`。工具核验每块哈希并恢复 `gpr2-twf154-dots-20261006-v3-new-access.zip`；缺卷或损坏会报错，不能拿部分材料开始 MD。
4. 解压恢复的完整包，在其根目录执行 `python3 compute/scripts/verify_bundle.py --root .`。
5. 校验通过后读取完整包的 `00_START_HERE.md`、`PROMPT.md` 和工作单，并执行用户给出的完整提示词。实际 SSH、持续运行和邮件工具仍须现场核验。

已把五卷都解压为 `.bin` 文件时，恢复工具也能直接读取同一目录中的这些分块。不需要安装分卷解压软件，只需 Python 3 标准库。恢复后原完整 ZIP 的大小和 SHA256 必须与 SPLIT_MANIFEST 一致。

所引：上一级 `archive.json` 对应的完整 v3-new-access 包及 SHA256。被引：上一级交接 README、项目 INDEX 与当天日志。重组必须逐字节恢复该完整包；原 v1/v2 包仅供历史溯源，不再沿用其旧认证指引。
