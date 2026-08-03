# Git 操作角色与 PR 协作规范

> 本文件只在 drylab 的 Git commit、push、PR review/integration 或 merge 任务中加载。它不根据 clone、checkout、分支名、remote、GitHub 用户名或 git config 推断任何人的权限身份。

## 1. 本次操作角色

每次 commit 和每次 push 前，都必须针对精确仓库、分支和变更范围确认一次本次操作角色：

- **权威维护者 / 集成者**：可依据已验证工作更新受影响的权威路由、状态投影和无后缀规范日志。
- **协作者 / 贡献者**：提交实际工作文件、测试或结果、可复核证据，以及 `YYYY-MM-DD-<contributor>.md` 形式的贡献者日志。

角色是单次操作属性，不是用户的永久身份。不得从当前分支、默认分支、工作区位置、remote 所有者、提交者邮箱或历史操作推断。commit 的角色确认不自动授权 push；一次 push 的确认不覆盖下一次 push。当前用户指令若已明确给出该次操作的角色、目标和范围，可视为该次确认；否则必须暂停并询问。

## 2. Commit 与 push 门

执行 commit 前：

1. 核验 repo root、当前分支、working tree、staged diff 和未暂存变更。
2. 确认本次 commit 的操作角色和精确文件范围，再按 `safe-commit` 逐文件分类与暂存。
3. 协作者角色不得提交 `AGENTS.md`、`docs/INDEX.md`、`docs/DOCMAP.md`、本文件、其他 index/docmap/router 文件或无后缀 `docs/logs/YYYY-MM-DD.md`；发现这些文件时停止，并把建议更新写入 PR 描述或贡献者日志供集成者处理。
4. 权威维护者角色只更新已被本次证据影响的权威文件；INDEX 仍只在项目级状态、优先级、阻塞项或活跃入口改变时更新。

执行 push 前：

1. 重新核验 remote、目标分支、upstream、outgoing commits 和相对目标的完整 diff。
2. 重新确认本次 push 的操作角色、精确 remote/branch 和 commit range；不得沿用 commit 时的角色确认。
3. 协作者角色只向其工作分支推送，不直接向集成目标或受保护分支推送。
4. 权威维护者角色的 push 仍需明确远端写授权；force-push、受保护分支写入和其他历史改写另设单独批准门。

角色、目标或 diff 任一不清楚时停止。不得通过改写命令、切换 remote 或使用环境变量绕过确认。

## 3. PR 内容边界

协作者 PR 可以包含实际工作文件、测试或结果、必要的可复核产物，以及带贡献者后缀的详细日志。贡献者日志只描述该 PR 的过程与证据，不承担跨 PR 的当前项目状态，也不得自行把候选结论提升为项目级 `active`、`done`、`fixed` 或 `verified`。

PR 描述至少列出：目标与范围、changed files 分类、已执行验证、原始结果指针、未验证项、建议集成者更新的权威文件、已知限制、后续工作和贡献者日志路径。

## 4. Review、集成与合并

1. **只读初审**：确认 PR 编号、base/head、作者和 head SHA，读取描述、commits、完整净 diff、checks 与既有 review。查看或审查请求不授权 GitHub 写入。
2. **review 写入**：先报告带文件/行号证据的问题。只有存在阻断问题且用户明确授权时才提交 `REQUEST_CHANGES`；无阻断问题时不制造返工轮次。评论、批准和 request changes 分别是远端写操作。
3. **复审**：修复后重新取得 head SHA，复审完整净 diff、checks 和 review 状态，不沿用旧 head 的结论。
4. **权威集成**：先确认本次操作为权威维护者/集成者角色，再从隔离 clean worktree 最小更新受影响的权威文件。集成修改应与候选工作在同一待合并变更集中交付；若原 PR 分支不可写，改用维护者集成分支或集成 PR。
5. **合并**：在最终 head 上重新验证 checks、review 状态、mergeability 和权威更新；确认合并操作的权威维护者/集成者角色，并取得针对精确 PR/head 的合并授权后才执行。
6. **合并后核验与日志**：核验目标集成分支包含预期 PR 和 commit。需要后续日志写入时，按新的 commit/push 门确认角色；无后缀规范日志只记录 PR、commit、权威更新和验证指针，不复制贡献者日志正文。

inspect、提交 review、commit、push、merge 和合并后日志写入互不授权；每个远端写操作都绑定其精确目标和当时已核验的变更身份。
