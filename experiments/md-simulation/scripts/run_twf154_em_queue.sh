#!/usr/bin/env bash
# Bounded sequential queue; one worker is 16 CPU threads. Preserve each failure.
set -u
ROOT=$(cd "$1" && pwd)
shift
cd "$ROOT"
for CASE in "$@"; do
  if bash scripts/run_twf154_preheat_case_v3.sh "$ROOT" "$CASE" em_only; then
    printf '%s\t%s\tEM_PASS\n' "$(date -u +%FT%TZ)" "$CASE"
  else
    printf '%s\t%s\tEM_FAILED_REVIEW_REQUIRED\n' "$(date -u +%FT%TZ)" "$CASE"
  fi
done
