# Codex Desktop 会话列表消失排查记录

> 事故日期：2026-05-21
> 适用范围：Codex Desktop 项目会话列表只显示当前 thread，但本地历史会话文件仍存在。

## 现象

- Codex Desktop 在 `/Users/roy/Documents/drylab` 项目页只显示当前这一条会话。
- 重启 Codex、`Cmd+Q`、kill 旧进程后仍不恢复。
- `.codex/sessions/` 和 `state_5.sqlite` 中历史会话实际仍存在，不是数据被删除。

## 根因

这次根因是 `model_provider` 名称迁移后，历史会话被前端列表过滤。

- 当前 `/Users/roy/.codex/config.toml` 使用 `model_provider = "openai_http"`。
- 旧会话的 `session_meta.payload.model_provider` 仍是 `openai`。
- Codex Desktop 的 `thread/list` 会按当前 provider 过滤；因此旧 `openai` 会话仍在磁盘上，但不显示在当前 `openai_http` 项目列表里。
- 只改 SQLite 索引不够，因为 Desktop 会从 JSONL session 源重新索引，把旧 provider 再读回来。

`hooks.json` 和 automations 不是这次主因：当时 `config.toml` 中 `[features] hooks = false`，没有证据表明 hook 或 automation 影响 `thread/list`。

## 诊断证据

检查 SQLite provider 分布：

```sh
sqlite3 -header -column /Users/roy/.codex/state_5.sqlite \
'select model_provider, count(*) rows from threads group by model_provider order by rows desc;'
```

检查 drylab 可见线程：

```sh
sqlite3 -header -column /Users/roy/.codex/state_5.sqlite \
'select id, datetime(updated_at,"unixepoch","localtime") updated, model_provider, archived, has_user_event, substr(title,1,60) title
 from threads
 where cwd="/Users/roy/Documents/drylab" and archived=0 and has_user_event=1
 order by updated_at desc limit 15;'
```

检查 JSONL 源文件里的 `session_meta` provider：

```sh
ruby -rjson -e 'counts=Hash.new(0); Dir["/Users/roy/.codex/sessions/**/*.jsonl"].each{|path| File.foreach(path){|line| begin obj=JSON.parse(line); counts[obj.dig("payload","model_provider")] += 1 if obj["type"]=="session_meta"; rescue JSON::ParserError; end }}; counts.sort.each{|k,v| puts "#{k.inspect} #{v}"}'
```

检查 Desktop/app-server 是否实际请求了 `thread/list`：

```sh
sqlite3 -header -column /Users/roy/.codex/logs_2.sqlite \
"select datetime(ts,'unixepoch','localtime') as t, feedback_log_body as body
 from logs
 where target='codex_app_server::message_processor'
 and feedback_log_body like '%thread/list%'
 order by ts desc, ts_nanos desc
 limit 30;"
```

手动 app-server 探针可区分“后端没返回”和“前端没显示”：

```sh
/Applications/Codex.app/Contents/Resources/codex app-server --listen stdio://
```

启动后发送：

```json
{"method":"initialize","id":"diag-init","params":{"clientInfo":{"name":"manual-diagnostic","title":"Manual Diagnostic","version":"0"},"capabilities":{"experimentalApi":false,"requestAttestation":false}}}
{"method":"thread/list","id":"diag-list","params":{"cwd":"/Users/roy/Documents/drylab","limit":20,"archived":false,"sortKey":"updated_at","sortDirection":"desc"}}
```

如果手动 `thread/list` 返回旧会话，但 Desktop UI 仍不显示，问题已从数据索引层转到前端缓存、旧 app-server 进程或 UI 状态。

## 恢复步骤

1. 先备份，不直接改原文件。

   这次备份目录：

   ```text
   /Users/roy/.codex/thread-recovery-backups/provider-source-fix-20260521-0351/
   ```

   备份内容包括：

   - `state_5.sqlite`
   - 候选 session JSONL 文件清单
   - 候选 session JSONL 源文件 tar 包
   - `session_index.jsonl`
   - `.codex-global-state.json`

2. 修 JSONL 源记录。

   只改解析后满足以下条件的 JSON 行：

   - `type == "session_meta"`
   - `payload.model_provider == "openai"`

   将其改为：

   ```json
   "model_provider": "openai_http"
   ```

   不要做盲目全文替换；session 内容中可能也出现字符串 `openai`，那不是索引字段。

3. 修 SQLite 索引。

   将 `/Users/roy/.codex/state_5.sqlite` 的 `threads.model_provider` 从 `openai` 更新为 `openai_http`。

4. 验证。

   - `sqlite integrity_check` 返回 `ok`。
   - JSONL `session_meta` provider 统计只剩 `openai_http`。
   - SQLite `threads` provider 统计只剩 `openai_http`。
   - 手动 app-server 默认 `thread/list` 能返回旧 drylab 会话。

5. 重启 Desktop。

   修复后如果手动 app-server 已返回旧会话，但 UI 仍只显示当前 thread，退出 Codex Desktop，再重新打开。原因通常是 Desktop 正在运行的 app-server 或 Electron 前端仍握着修复前的状态。

## 禁止操作

- 不要删除 `/Users/roy/.codex/sessions/`。
- 不要删除 `/Users/roy/.codex/archived_sessions/`。
- 不要直接删 `/Users/roy/.codex/state_5.sqlite`。
- 不要未备份就清 Electron storage。
- 不要用盲目 `sed` 或全文替换改所有 JSONL 内容。
- 不要把 hook/automation 当成首要原因，除非日志显示它们实际参与了 `thread/list` 或 state 重写。

## 预防

- 改 `/Users/roy/.codex/config.toml` 的 `model_provider` 后，立即检查旧 thread 的 `model_provider` 是否还与当前 provider 匹配。
- 如果只看到当前会话，先查 provider 分布和手动 `thread/list`，不要先做清库或重装。
- 对 Codex state 做任何修复前，先建时间戳备份目录，并记录修复命令和验证输出。
