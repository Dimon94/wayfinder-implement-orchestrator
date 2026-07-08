# Herdr Worker 边界

派发任何可执行工作前读取本文件。

## 默认 Worker

- Wayfinder AFK `Research` 和可自动执行的 `Task` child issues：每个 child issue
  一个 Herdr `/wayfinder` worker pane。
- Wayfinder `Prototype`、`Grilling` 和 HITL `Task` child issues：只在用户能进入该
  pane 反馈时派发；否则 lead 停在 `ask-user`，并给出完整 pane prompt。
- Worker 发现的 Wayfinder follow-up tickets：lead 重读 map issue 和 frontier query，
  然后派发下一批 Herdr worker panes；workers 不打开后代 panes。
- Wayfinder complete：当 route classifier 选择 `wayfinder-complete`，lead 报告 map
  已达 Destination 并停止，不派发 PRD、implementation issue split 或 `/implement`。
- PRD synthesis：仅当 route classifier 选择 `needs-prd`，且 seams 已批准时，用 Herdr
  `/to-prd` gate worker 基于 map proof 起草或发布；否则 worker 返回 seam proposal，
  由 lead 问用户。`needs-implementation-issue-split` 或 `direct-implementation-dispatch`
  路线禁止补造 PRD。
- Implementation issue splitting：当 route classifier 选择
  `needs-implementation-issue-split`，或 `needs-prd` 路线已发布 PRD 且仍需
  implementation slices 时，用 Herdr `/to-issues` gate worker 起草或发布；如果 split
  尚未批准，lead 先问用户再发布。
- Implementation：当 route classifier 选择 `direct-implementation-dispatch`，或 issues
  gate 已经发布且读回 ready issues 后，每个 tracker issue 一个 Herdr `/implement`
  worker pane。
- Integrated review：lead 集成后，在可用时使用 Herdr read-only review worker 或
  pane-local Agent Team review helper。
- Remote CI/CD 或 review-agent fixes：把每个需要改代码的 fix 转成 tracker issue，
  或 lead 明确批准的 micro-issue，再派发 Herdr `/implement` worker。
- 有争议的 review-agent comments：如果 verdict 不明显，用 read-only worker 收集
  证据，然后 lead 发布 PR/MR rebuttal/adaptation note。

## 执行通道

Boundaries 决定 work item 跑在哪个 pane；`codex-first-channel.md` 决定该 pane 里
hands-on 工作由谁执行。派发前给每个可执行 work item 标注 `codex-plugin` 或
`claude-native`。

- Implementation worker pane：spec 已冻结的写码工作默认 `codex-plugin`；微小改动、
  需要会话内工具或插件不可用时 `claude-native`。
- Discovery `Research` 的大批量代码阅读：可经 `codex-plugin` 只读工单委托；决策、
  ticket resolution 和 map 写操作永远留在 Claude。
- Grilling、PRD、issue split、review、integration、remote 操作：永远 `claude-native`。

## Lead 持有

- Human judgement gates 和 user questions。
- 判断哪个 worker batch 可以安全派发。
- Herdr pane creation、pane labels、worker coordinate records 和 5 分钟检查节奏。
- Wayfinder frontier query、selection 和下一轮 dispatch。
- Integration branch cherry-picks、conflict resolution，以及 PR/MR push/open/update。
- PR/MR comments、review-agent rebuttals，以及 final remote-gate completion。
- 创建 worktree 或需要分支时，只在目标 worktree 目录内创建/切换分支；不要切换
  主目录/source worktree 的分支。

## 应该停止

不要为 live user grilling、未解决的 product choices、不清晰的 route、未批准的 issue
splits、重叠 mutable resources、缺失 source truth，或任何无法从持久真相源验证验收标准的
work item 创建 Herdr worker pane。

## 最小 Worker Prompt

PRD、issue-splitting、review 和 evidence-gathering workers 使用
`GATE_CHILD_DISPATCH_PACKET.md`。

## 外部坐标

如果 source artifacts 不在 worker pane 的当前 repo/worktree 内，把它们作为外部坐标写入
dispatch packet。map/ticket issue 仍通过 tracker 坐标读写。

记录两组坐标：

- Execution target：Herdr pane label、worker cwd、worktree/path 和 branch。
- External coordinates：tracker map/ticket issue URLs、source worktree 里的 proof 和
  artifact paths。

除非 packet 明确列出 write target，否则 external coordinates 都是只读。对 discovery
tickets，唯一允许的 external writes 是 tracker map/ticket issues 和列出的 artifact
paths。用一行向用户报告这个 fallback；Herdr 可创建 pane 时，不要以手动 copy-paste
instructions 结束。
