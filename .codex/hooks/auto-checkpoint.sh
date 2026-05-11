#!/usr/bin/env bash
# auto-checkpoint.sh — Stop hook (async)
# Codex 停止响应时，如果有较多未提交变更，创建 git stash checkpoint
# 架构：Stop 事件 → 每次响应最多触发一次（而非每次 Edit 都触发）
# 节流：/tmp 时间戳文件，5 分钟冷却
# Rotation：只保留最近 3 个 auto-checkpoint stash

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

# ── 冷却检查（5 分钟内不重复） ──
LOCKFILE="/tmp/codex-auto-checkpoint.last"
NOW=$(date +%s)
if [[ -f "$LOCKFILE" ]]; then
  LAST=$(cat "$LOCKFILE" 2>/dev/null)
  if [[ -n "$LAST" ]] && (( NOW - LAST < 300 )); then
    exit 0
  fi
fi

# ── 变更文件数阈值 ──
TOTAL=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [[ "$TOTAL" -lt 5 ]]; then
  exit 0
fi

# ── 创建 checkpoint（不修改工作区） ──
STASH_SHA=$(git stash create 2>/dev/null)
if [[ -z "$STASH_SHA" ]]; then
  exit 0
fi
git stash store -m "auto-checkpoint: ${TOTAL} files changed" "$STASH_SHA" >/dev/null 2>&1
echo "$NOW" > "$LOCKFILE"
echo "[Auto-checkpoint] 已创建安全检查点（${TOTAL} 个文件变更）"

# ── Rotation：只保留最近 3 个 auto-checkpoint ──
# 从旧到新遍历 stash，删除超出保留数的 auto-checkpoint 条目
AC_INDICES=()
while IFS= read -r line; do
  if [[ "$line" == *"auto-checkpoint:"* ]]; then
    idx=$(echo "$line" | grep -oE 'stash@\{[0-9]+\}' | grep -oE '[0-9]+')
    AC_INDICES+=("$idx")
  fi
done < <(git stash list 2>/dev/null)

KEEP=3
if (( ${#AC_INDICES[@]} > KEEP )); then
  # 从大索引往小删（避免索引偏移）
  for (( i=${#AC_INDICES[@]}-1; i>=KEEP; i-- )); do
    git stash drop "stash@{${AC_INDICES[$i]}}" >/dev/null 2>&1
  done
fi
