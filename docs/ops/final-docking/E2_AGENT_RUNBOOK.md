# Docking：E2 执行手册

## 1. 目的

本手册规定一个 docking 批次在 E2 共享服务器上的交付方式：先冻结并校验上传包，再进行资源门禁、唯一运行目录创建、受控执行、终态验证和结果回传。

科学方法、受体与配体身份、搜索空间、参数和成功判据由本次 `WORK_ORDER.md` 定义。本手册只负责把该工作单可靠地执行并形成可复核证据。

## 2. 固定入口与资源边界

| 项目 | 值 |
|---|---|
| SSH 主机 | `e2.tongyuangene.com` |
| SSH 端口 | `40042` |
| SSH 用户 | `dengwei` |
| 用户 HOME | `/ifs1/User/dengwei` |
| 个人工作区 | `/ifs1/User/dengwei/${OWNER_DIR}` |
| 项目根目录 | `/ifs1/User/dengwei/${OWNER_DIR}/${PROJECT_SLUG}` |
| 常规线程数 | `16`；工作单可写明 `32` |
| 单人总线程硬上限 | `128` |
| 长任务会话 | `tmux` |

主机、CPU、内存、GPU、磁盘和配额均以运行前的实时读数为准。共享账号下的进程归属必须能够解释；归属不清即视为资源门禁未通过。

## 3. 上传包合同

本地上传包必须具有以下结构：

```text
UPLOAD_BUNDLE/
├── WORK_ORDER.md
├── inputs/
├── environment/
├── workflow/
│   ├── preflight.sh
│   ├── run.sh
│   └── validate.sh
└── manifest/
    └── upload.sha256
```

合同要求：

- `WORK_ORDER.md` 写明工作单 ID、科学任务、输入身份、环境锁、资源预算、运行参数、预期产物和 validator 通过条件。
- `inputs/` 只含本次工作单的冻结输入；文件名使用 ASCII 字母、数字、点、下划线、连字符和目录分隔符，不含空格。
- `environment/` 保存工具与依赖的锁定信息。环境是否可用由 `workflow/preflight.sh` 只读检查。
- `workflow/preflight.sh`、`run.sh`、`validate.sh` 必须是非交互、重复调用语义明确的 Bash 脚本。
- 三个脚本通过环境变量接收路径和资源，不依赖调用者当前目录：`RUN_ID`、`INPUT_DIR`、`WORK_DIR`、`OUTPUT_DIR`、`EVIDENCE_DIR`、`THREADS`。
- `THREADS` 是本工作单的总线程预算。`run.sh` 必须把 OpenMP、BLAS、JAX/PyTorch、结构预测器和 docking 工具的并行度绑定到该预算，禁止每个子进程各自使用 `THREADS` 导致超额。
- `preflight.sh` 输出工具版本、实际 executable 路径及 SHA256，并在任何依赖、版本或输入不满足时返回非零。
- `run.sh` 只写 `WORK_DIR`、`OUTPUT_DIR` 和 `EVIDENCE_DIR`。
- `validate.sh` 只读检查本次产物；只有全部工作单判据满足时返回 `0`。
- `manifest/upload.sha256` 覆盖 `WORK_ORDER.md`、`inputs/`、`environment/` 和 `workflow/` 下的全部普通文件。
- 上传包不含符号链接、凭据、token、私钥或交互式口令。

环境缺失时，工作单应提供单独审核过、依赖已锁定且幂等的环境构建步骤。环境构建完成后重新制作上传包并从本手册第 4 节开始执行。

## 4. 本地冻结与校验

在同一个本地 Bash 会话中设置变量。占位值必须替换：

```bash
export E2_HOST='e2.tongyuangene.com'
export E2_PORT='40042'
export E2_USER='dengwei'

export OWNER_DIR='replace_with_owner_pinyin'
export PROJECT_SLUG='replace_with_project_slug'
export WORK_ORDER_ID='replace_with_work_order_id'
export BUNDLE_ROOT='/absolute/path/to/UPLOAD_BUNDLE'
export LOCAL_RETURN_ROOT='/absolute/path/to/project/artifacts/e2'

export THREADS='16'
export REQUIRED_RAM_GIB='replace_with_integer'
export EXPECTED_REMOTE_GIB='replace_with_integer'
export REQUIRES_GPU='0'

export RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_${WORK_ORDER_ID}"
export E2_TARGET="${E2_USER}@${E2_HOST}"
export REMOTE_ROOT="/ifs1/User/dengwei/${OWNER_DIR}/${PROJECT_SLUG}"
export REMOTE_INCOMING="${REMOTE_ROOT}/incoming/${RUN_ID}"
export REMOTE_RUN="${REMOTE_ROOT}/runs/${RUN_ID}"
```

校验变量，任何一条失败都停止：

```bash
set -euo pipefail

case "$OWNER_DIR" in
  replace_*|'') echo 'OWNER_DIR 未设置' >&2; exit 10 ;;
  *[!a-z0-9_-]*) echo 'OWNER_DIR 只能含小写字母、数字、_、-' >&2; exit 10 ;;
esac

case "$PROJECT_SLUG" in
  replace_*|'') echo 'PROJECT_SLUG 未设置' >&2; exit 10 ;;
  *[!a-z0-9_-]*) echo 'PROJECT_SLUG 只能含小写字母、数字、_、-' >&2; exit 10 ;;
esac

case "$WORK_ORDER_ID" in
  replace_*|'') echo 'WORK_ORDER_ID 未设置' >&2; exit 10 ;;
  *[!A-Za-z0-9._-]*) echo 'WORK_ORDER_ID 含不安全字符' >&2; exit 10 ;;
esac

case "$THREADS:$REQUIRED_RAM_GIB:$EXPECTED_REMOTE_GIB:$REQUIRES_GPU" in
  *[!0-9:]*) echo '资源变量必须是非负整数' >&2; exit 10 ;;
esac

test "$THREADS" -ge 1
test "$THREADS" -le 128
test "$REQUIRED_RAM_GIB" -ge 1
test "$EXPECTED_REMOTE_GIB" -ge 1
test "$REQUIRES_GPU" -eq 0 || test "$REQUIRES_GPU" -eq 1

if test "$THREADS" -gt 32; then
  echo '线程数超过常规范围，需要工作单中的专项资源授权' >&2
  exit 11
fi

test -d "$BUNDLE_ROOT"
test -d "$LOCAL_RETURN_ROOT"
test -f "$BUNDLE_ROOT/WORK_ORDER.md"
test -f "$BUNDLE_ROOT/manifest/upload.sha256"
test -x "$BUNDLE_ROOT/workflow/preflight.sh"
test -x "$BUNDLE_ROOT/workflow/run.sh"
test -x "$BUNDLE_ROOT/workflow/validate.sh"

if find "$BUNDLE_ROOT" -type l -print -quit | grep -q .; then
  echo '上传包含符号链接' >&2
  exit 12
fi
```

确认 manifest 路径安全、文件集合完整且内容哈希一致：

```bash
expected_list="$(mktemp)"
manifest_list="$(mktemp)"
trap 'rm -f -- "$expected_list" "$manifest_list"' EXIT

(
  cd "$BUNDLE_ROOT"
  find WORK_ORDER.md inputs environment workflow -type f -print | LC_ALL=C sort \
    >"$expected_list"
  awk 'NF != 2 || length($1) != 64 || $1 !~ /^[0-9A-Fa-f]+$/ { exit 1 }
       { path_value=$2; sub(/^\*/, "", path_value); print path_value }' \
    manifest/upload.sha256 | LC_ALL=C sort >"$manifest_list"
  awk '{ path_value=$2; sub(/^\*/, "", path_value);
         if (path_value ~ /^\// || path_value ~ /(^|\/)\.\.($|\/)/) exit 1 }' \
      manifest/upload.sha256
  cmp "$expected_list" "$manifest_list"
  /usr/bin/shasum -a 256 -c manifest/upload.sha256
)
```

工作单与 manifest 一经通过，本次 `RUN_ID` 对应的上传包即冻结。后续内容变化使用新的 `RUN_ID`。

## 5. 只读资源门禁

先验证 SSH，再读取实时资源。此步骤不会创建远程目录或上传文件。

```bash
ssh -p "$E2_PORT" -o BatchMode=yes "$E2_TARGET" \
  'test "$(whoami)" = dengwei && test "$HOME" = /ifs1/User/dengwei && printf "host=%s\nuser=%s\nhome=%s\nutc=%s\n" "$(hostname)" "$(whoami)" "$HOME" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"'
```

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- "$REQUIRES_GPU" <<'REMOTE_PREFLIGHT'
set -euo pipefail
requires_gpu=$1

echo '[cpu]'
printf 'nproc='; nproc
printf 'loadavg='; cat /proc/loadavg
uptime

echo '[memory]'
free -h

echo '[disk]'
df -h /ifs1/User/dengwei
if ! command -v quota >/dev/null 2>&1; then
  echo 'QUOTA_COMMAND_MISSING' >&2
  exit 21
fi
quota -uvs

echo '[shared-account thread snapshot]'
printf 'account_thread_count='
ps -u "$(whoami)" -L -o lwp= | wc -l
ps -u "$(whoami)" -L -o pid=,lwp=,etimes=,pcpu=,pmem=,comm= \
  --sort=-pcpu | sed -n '1,120p'

echo '[active processes]'
ps -eo user,pid,ppid,etimes,%cpu,%mem,args --sort=-%cpu | sed -n '1,50p'

echo '[tmux sessions]'
tmux list-sessions 2>&1 || true

echo '[gpu]'
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
  nvidia-smi --query-compute-apps=pid,process_name,used_memory \
    --format=csv,noheader 2>/dev/null || true
elif test "$requires_gpu" -eq 1; then
  echo 'GPU_REQUIRED_BUT_NVIDIA_SMI_MISSING' >&2
  exit 20
else
  echo 'GPU_NOT_REQUESTED'
fi
REMOTE_PREFLIGHT
```

Agent 根据实时输出作出一次明确门禁结论。通过条件全部满足后才进入第 6 节：

1. `nproc`、load average 和活跃进程显示系统能容纳本次 `THREADS`，且本账号所有已知任务加本次任务不超过 128 线程。
2. `free` 显示可用内存不低于 `REQUIRED_RAM_GIB`，并保留共享服务余量。
3. 用户 quota 与文件系统可用空间都不低于 `EXPECTED_REMOTE_GIB`，并至少为预计上传包、工作区和输出总量留出 2 倍余量。
4. 需要 GPU 时，GPU 状态、显存余量和现有计算进程归属均清楚；资源满足工作单预算。
5. 现有进程和 tmux 会话的归属可解释，没有同名项目或同一工作单正在运行。

任何读数缺失、资源不足、进程归属不清或资源冲突都输出 `BLOCKED_RESOURCE_PREFLIGHT`，附实时命令输出，并在本节停止。Agent 不终止、暂停或调整任何既有进程。

## 6. 创建唯一目录并上传

资源门禁通过后，创建本次唯一目录。已有同名路径属于冲突，命令将直接失败：

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- \
  "$REMOTE_ROOT" "$RUN_ID" <<'REMOTE_CREATE'
set -euo pipefail
remote_root=$1
run_id=$2

case "$remote_root" in
  /ifs1/User/dengwei/?*/*) ;;
  *) echo 'REMOTE_ROOT 越界' >&2; exit 30 ;;
esac
case "$run_id" in
  ''|*[!A-Za-z0-9._-]*) echo 'RUN_ID 不安全' >&2; exit 30 ;;
esac

incoming="$remote_root/incoming/$run_id"
run_root="$remote_root/runs/$run_id"
test ! -e "$incoming"
test ! -e "$run_root"

owner_root=${remote_root%/*}
test -d "$owner_root"
mkdir -p "$remote_root/incoming" "$remote_root/runs"
mkdir "$incoming"
mkdir "$run_root"
mkdir "$run_root/work" "$run_root/outputs" "$run_root/evidence" "$run_root/logs"
chmod 750 "$remote_root" "$remote_root/incoming" "$remote_root/runs" \
  "$incoming" "$run_root" "$run_root"/{work,outputs,evidence,logs}
REMOTE_CREATE
```

上传冻结包：

```bash
rsync -rtv --partial --progress \
  -e "ssh -p ${E2_PORT}" \
  "$BUNDLE_ROOT/" "$E2_TARGET:$REMOTE_INCOMING/"
```

在服务器端复核文件集合和 SHA256，并锁定上传包权限：

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- \
  "$REMOTE_INCOMING" "$REMOTE_RUN" <<'REMOTE_VERIFY'
set -euo pipefail
incoming=$1
run_root=$2

test -f "$incoming/manifest/upload.sha256"
if find "$incoming" -type l -print -quit | grep -q .; then
  echo '远程上传包含符号链接' >&2
  exit 31
fi

cd "$incoming"
expected_list="$(mktemp)"
manifest_list="$(mktemp)"
trap 'rm -f -- "$expected_list" "$manifest_list"' EXIT

find WORK_ORDER.md inputs environment workflow -type f -print | LC_ALL=C sort \
  >"$expected_list"
awk 'NF != 2 || length($1) != 64 || $1 !~ /^[0-9A-Fa-f]+$/ { exit 1 }
     { path_value=$2; sub(/^\*/, "", path_value); print path_value }' \
  manifest/upload.sha256 | LC_ALL=C sort >"$manifest_list"
awk '{ path_value=$2; sub(/^\*/, "", path_value);
       if (path_value ~ /^\// || path_value ~ /(^|\/)\.\.($|\/)/) exit 1 }' \
    manifest/upload.sha256
cmp "$expected_list" "$manifest_list"
sha256sum -c manifest/upload.sha256

cp WORK_ORDER.md "$run_root/evidence/WORK_ORDER.md"
cp manifest/upload.sha256 "$run_root/evidence/upload.sha256"

find "$incoming" -type d -exec chmod 750 {} +
find "$incoming" -type f -exec chmod 640 {} +
chmod 750 "$incoming/workflow/preflight.sh" \
  "$incoming/workflow/run.sh" \
  "$incoming/workflow/validate.sh"
REMOTE_VERIFY
```

## 7. 生成运行驱动器

运行驱动器负责顺序执行环境预检、主任务和 validator，并向 `run_state_events.tsv` 追加事件。它不会覆盖已存在的事件文件。

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- "$REMOTE_RUN" <<'REMOTE_DRIVER'
set -euo pipefail
run_root=$1
driver="$run_root/evidence/run_driver.sh"
test ! -e "$driver"

cat >"$driver" <<'DRIVER'
#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

: "${RUN_ID:?}"
: "${INPUT_DIR:?}"
: "${WORK_DIR:?}"
: "${OUTPUT_DIR:?}"
: "${EVIDENCE_DIR:?}"
: "${LOG_DIR:?}"
: "${THREADS:?}"
: "${WORKFLOW_DIR:?}"

events="$EVIDENCE_DIR/run_state_events.tsv"
test ! -e "$events"
printf 'timestamp_utc\tstate\tdetail\n' >"$events"

terminal_recorded=0
on_unexpected_exit() {
  rc=$?
  trap - EXIT
  if test "$rc" -ne 0 && test "$terminal_recorded" -eq 0; then
    printf '%s\tUNEXPECTED_EXIT\texit=%s\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" >>"$events"
  fi
  exit "$rc"
}
trap on_unexpected_exit EXIT

event() {
  printf '%s\t%s\t%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >>"$events"
}

event 'PREFLIGHT_STARTED' "run_id=$RUN_ID"
if "$WORKFLOW_DIR/preflight.sh" \
  >"$LOG_DIR/preflight.stdout.log" \
  2>"$LOG_DIR/preflight.stderr.log"; then
  event 'PREFLIGHT_PASSED' 'exit=0'
else
  rc=$?
  event 'PREFLIGHT_FAILED' "exit=$rc"
  terminal_recorded=1
  exit "$rc"
fi

event 'RUN_STARTED' "threads=$THREADS"
if "$WORKFLOW_DIR/run.sh" \
  >"$LOG_DIR/run.stdout.log" \
  2>"$LOG_DIR/run.stderr.log"; then
  event 'RUN_FINISHED' 'exit=0'
else
  rc=$?
  event 'RUN_FAILED' "exit=$rc"
  terminal_recorded=1
  exit "$rc"
fi

event 'VALIDATION_STARTED' "run_id=$RUN_ID"
if "$WORKFLOW_DIR/validate.sh" \
  >"$LOG_DIR/validate.stdout.log" \
  2>"$LOG_DIR/validate.stderr.log"; then
  event 'VALIDATION_PASSED' 'exit=0'
else
  rc=$?
  event 'VALIDATION_FAILED' "exit=$rc"
  terminal_recorded=1
  exit "$rc"
fi

trap - EXIT
DRIVER

chmod 750 "$driver"
REMOTE_DRIVER
```

说明：这里的 heredoc 只在本次唯一 `REMOTE_RUN` 下创建运行驱动器。所有科学步骤仍来自已校验的 `workflow/` 脚本。

## 8. 启动 tmux 任务

启动前再做一次短资源复核；若状态相对第 5 节发生实质变化，重新执行完整资源门禁。

```bash
ssh -p "$E2_PORT" "$E2_TARGET" \
  'uptime; free -h; ps -eo user,pid,etimes,%cpu,%mem,args --sort=-%cpu | sed -n "1,25p"'
```

启动唯一 tmux 会话：

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- \
  "$REMOTE_INCOMING" "$REMOTE_RUN" "$RUN_ID" "$THREADS" <<'REMOTE_LAUNCH'
set -euo pipefail
incoming=$1
run_root=$2
run_id=$3
threads=$4
session="dock_${run_id}"

if tmux has-session -t "$session" 2>/dev/null; then
  echo '同名 tmux 会话已存在' >&2
  exit 40
fi

printf 'run_id=%s\nthreads=%s\ninput_dir=%s\nrun_root=%s\n' \
  "$run_id" "$threads" "$incoming/inputs" "$run_root" \
  >"$run_root/evidence/run_metadata.env"

printf -v launch_command \
  'env RUN_ID=%q INPUT_DIR=%q WORK_DIR=%q OUTPUT_DIR=%q EVIDENCE_DIR=%q LOG_DIR=%q THREADS=%q WORKFLOW_DIR=%q bash %q' \
  "$run_id" \
  "$incoming/inputs" \
  "$run_root/work" \
  "$run_root/outputs" \
  "$run_root/evidence" \
  "$run_root/logs" \
  "$threads" \
  "$incoming/workflow" \
  "$run_root/evidence/run_driver.sh"

tmux new-session -d -s "$session" "$launch_command"
tmux list-sessions
REMOTE_LAUNCH
```

## 9. 监控与终态判断

查看会话、事件和资源：

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- "$REMOTE_RUN" "$RUN_ID" <<'REMOTE_STATUS'
set -euo pipefail
run_root=$1
run_id=$2
session="dock_${run_id}"

tmux has-session -t "$session" 2>/dev/null && \
  tmux capture-pane -pt "$session" -S -80 || true
tail -n 30 "$run_root/evidence/run_state_events.tsv" 2>/dev/null || true
ps -eo user,pid,ppid,etimes,%cpu,%mem,args --sort=-%cpu | sed -n '1,30p'
free -h
REMOTE_STATUS
```

终态解释：

| 最后一条 state | 结论 | 后续动作 |
|---|---|---|
| `VALIDATION_PASSED` | 计算与 validator 均通过 | 进入第 10 节 |
| `PREFLIGHT_FAILED` | 环境或输入未通过 | 保留证据，停止 |
| `RUN_FAILED` | 主任务非零退出 | 保留证据，停止 |
| `VALIDATION_FAILED` | 产物未满足工作单 | 保留证据，停止 |
| `*_STARTED` 且 tmux 仍存在 | 仍在运行 | 继续监控 |
| `UNEXPECTED_EXIT` | 驱动器在某个显式阶段之外非零退出 | 保留证据，停止 |
| `*_STARTED` 且 tmux 已消失 | 非正常终止 | 保留当前事件/日志，报告异常并停止 |

Agent 只观察本次 `RUN_ID` 的进程和文件。任何既有进程都保持原状。

## 10. 冻结结果并生成回传 manifest

只有终态为 `VALIDATION_PASSED` 才执行：

```bash
ssh -p "$E2_PORT" "$E2_TARGET" bash -s -- "$REMOTE_RUN" <<'REMOTE_FINALIZE'
set -euo pipefail
run_root=$1
events="$run_root/evidence/run_state_events.tsv"
manifest="$run_root/return_manifest.sha256"

test -f "$events"
test "$(tail -n 1 "$events" | cut -f 2)" = 'VALIDATION_PASSED'
test ! -e "$manifest"

cd "$run_root"
find outputs evidence logs -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 -r sha256sum >return_manifest.sha256
test -s return_manifest.sha256
sha256sum -c return_manifest.sha256
REMOTE_FINALIZE
```

manifest 覆盖输出、工作单副本、上传 manifest、运行元数据、驱动器、事件流和日志。`work/` 是运行中间区，不进入回传合同；工作单要求保留的中间文件应由 `run.sh` 放入 `outputs/` 或 `evidence/`。

## 11. 回传与本地复核

本地目标必须是新目录：

```bash
export LOCAL_RUN_RETURN="${LOCAL_RETURN_ROOT}/${RUN_ID}"
test ! -e "$LOCAL_RUN_RETURN"
mkdir -p "$LOCAL_RUN_RETURN"/{outputs,evidence,logs}
```

回传合同内文件：

```bash
rsync -rtv --partial --progress -e "ssh -p ${E2_PORT}" \
  "$E2_TARGET:$REMOTE_RUN/outputs/" "$LOCAL_RUN_RETURN/outputs/"
rsync -rtv --partial --progress -e "ssh -p ${E2_PORT}" \
  "$E2_TARGET:$REMOTE_RUN/evidence/" "$LOCAL_RUN_RETURN/evidence/"
rsync -rtv --partial --progress -e "ssh -p ${E2_PORT}" \
  "$E2_TARGET:$REMOTE_RUN/logs/" "$LOCAL_RUN_RETURN/logs/"
rsync -tv --partial --progress -e "ssh -p ${E2_PORT}" \
  "$E2_TARGET:$REMOTE_RUN/return_manifest.sha256" "$LOCAL_RUN_RETURN/"
```

本地逐文件核验：

```bash
(
  cd "$LOCAL_RUN_RETURN"
  /usr/bin/shasum -a 256 -c return_manifest.sha256
  printf 'verified_utc=%s\nrun_id=%s\nremote=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RUN_ID" "$E2_TARGET:$REMOTE_RUN" \
    >local_transfer_verification.txt
)
```

## 12. 完成条件与保留策略

本次 E2 工作只有在以下条件同时满足时才可报告完成：

1. 上传前与上传后的 `upload.sha256` 均通过。
2. 资源门禁通过，使用量符合工作单和共享服务器边界。
3. 本次运行使用唯一 `RUN_ID`，没有覆盖既有目录或会话。
4. `run_state_events.tsv` 最后一条 state 为 `VALIDATION_PASSED`。
5. `return_manifest.sha256` 在服务器端与本地均逐文件通过。
6. 本地存在 `local_transfer_verification.txt`，可定位远程运行根目录。

回传核验后，`incoming/${RUN_ID}` 与 `runs/${RUN_ID}` 进入保留状态。清理属于单独工作单，必须指向精确 `RUN_ID`、列明待删路径，并在执行前再次核对本地回传 manifest；本手册在结果核验处结束。

## 13. 必须停止的情形

出现下列任一情况，Agent 保留现有证据并报告阻塞，不自行改参数、换输入或重跑：

- 工作单、环境锁、输入 manifest 或 validator 缺失或不一致。
- 上传包含符号链接、凭据、未列入 manifest 的文件或不安全路径。
- SSH 身份、HOME、项目根路径或运行 ID 不符合本手册合同。
- CPU、内存、GPU、磁盘、quota 或进程归属无法明确判定。
- 同名上传目录、运行目录或 tmux 会话已存在。
- 上传后 SHA256 不通过。
- `preflight.sh`、`run.sh` 或 `validate.sh` 返回非零。
- tmux 消失且事件流没有受支持的终态。
- 远端或本地回传 SHA256 不通过。

阻塞报告至少包含：`RUN_ID`、失败阶段、失败命令、退出码、相关日志路径、已创建的精确远程路径，以及恢复执行前需要补齐的事实或授权。
