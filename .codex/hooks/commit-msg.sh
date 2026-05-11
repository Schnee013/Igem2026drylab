#!/bin/bash
# Git commit-msg hook: 自动清除提交信息中的 AI 身份标识（双保险）
# 安装方式: bash .codex/hooks/install.sh
# 此文件本身不是 git hook，是模板，install.sh 会将其安装到 .git/hooks/commit-msg

COMMIT_MSG_FILE="$1"

# 删除 AI 归属行
sed -i '' \
    -e '/Co-Authored-By:.*[Cc]laude/d' \
    -e '/Co-authored-by:.*[Cc]laude/d' \
    -e '/🤖 Generated with/d' \
    -e '/Generated with \[Claude Code\]/d' \
    -e '/noreply@anthropic\.com/d' \
    -e '/claude-code@anthropic/d' \
    "$COMMIT_MSG_FILE"

# 清理尾部多余空行
perl -i -0pe 's/\n{3,}$/\n/' "$COMMIT_MSG_FILE" 2>/dev/null || true

exit 0
