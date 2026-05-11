#!/bin/bash
# Git commit-msg hook: 自动清除提交信息中的 AI 身份标识（双保险）
# 安装方式: bash .codex/hooks/install.sh
# 此文件本身不是 git hook，是模板，install.sh 会将其安装到 .git/hooks/commit-msg

COMMIT_MSG_FILE="$1"

# 删除 AI 归属行 / 模型字段。用 perl 避免 GNU/BSD sed 标志差异。
perl -i -ne '
print unless
    /Co-authored-by:.*(?:claude|codex|gpt|chatgpt|opus|sonnet|haiku)/i ||
    /Generated\s+(?:with|by)\s+\[?(?:Claude Code|Codex|ChatGPT|GPT(?:[- ][A-Za-z0-9.]+)?|Claude(?:[- ][A-Za-z0-9.]+)?|Opus|Sonnet|Haiku)\]?/i ||
    /(?:AI[- ]?Model|Model|Assistant):.*(?:gpt|chatgpt|claude|opus|sonnet|haiku)/i ||
    /noreply\@anthropic\.com/i ||
    /claude-code\@anthropic/i ||
    /noreply\@openai\.com/i ||
    /codex\@openai/i ||
    /openai.*codex/i
' "$COMMIT_MSG_FILE"

# 清理尾部多余空行
perl -i -0pe 's/\n{3,}$/\n/' "$COMMIT_MSG_FILE" 2>/dev/null || true

exit 0
