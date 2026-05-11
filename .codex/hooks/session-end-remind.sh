#!/usr/bin/env bash
# session-end-remind.sh — Stop hook (提示模式，不 block)
# Codex 停止响应前检查未 commit 改动，有则打印提醒
# 30 秒冷却防止 Stop 事件连发时重复提醒

LOCKFILE="/tmp/codex-session-end-remind.last"
NOW=$(date +%s)
if [[ -f "$LOCKFILE" ]]; then
  LAST=$(cat "$LOCKFILE" 2>/dev/null)
  if [[ -n "$LAST" ]] && (( NOW - LAST < 30 )); then
    exit 0
  fi
fi

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

CHANGED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CHANGED" -gt 0 ]]; then
  SUMMARY=$(git diff --stat HEAD 2>/dev/null | tail -1)
  echo "[提醒] 当前有 ${CHANGED} 个未提交的文件变更（${SUMMARY}）。可运行 /commit 提交。"
  echo "$NOW" > "$LOCKFILE"
fi
exit 0
