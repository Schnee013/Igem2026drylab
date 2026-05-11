#!/bin/bash
# 安装 git hooks 到 .git/hooks/
# 在 drylab 根目录运行: bash .codex/hooks/install.sh

set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_DIR="$REPO_ROOT/.codex/hooks"

install_hook() {
    local name="$1"
    local source="$SOURCE_DIR/$name.sh"
    local target="$HOOKS_DIR/$name"

    if [ ! -f "$source" ]; then
        echo "⚠ 找不到 $source，跳过"
        return
    fi

    cp "$source" "$target"
    chmod +x "$target"
    echo "✓ 已安装: .git/hooks/$name"
}

install_hook "commit-msg"

echo ""
echo "Git hooks 安装完成。提交时会自动过滤 AI 身份标识。"
