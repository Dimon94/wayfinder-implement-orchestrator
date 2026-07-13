---
name: wayfinder-implement-orchestrator
description: Orchestrate tracker-backed Wayfinder maps through concurrent design frontiers, AFK execution lanes, terminal fan-in, and one summary PR/MR.
---

# Wayfinder Implement Orchestrator for Claude

只有当用户用 tracker 上的 wayfinder map issue、需要变成 shared map 的松散想法，或已批准的
spec/tickets 集合调用时，才使用本 skill。它只负责编排链路；不替代 `/wayfinder`、
`/to-spec`、`/to-tickets` 或 `/implement`。

## Execution Model

每轮都从持久真相源重算 `ready frontier`，选择没有 dependency 或 mutable-resource 冲突的
`maximal safe batch`。安全并发是默认行为，不需要用户先开启。

- **Design fan-out**：一个判断问题一个 Herdr pane；AFK research/evidence/task 自动并发，
  HITL blocker 只暂停对应 pane。
- **AFK execution lanes**：一个 lane = 一个 AFK owner + 一个 worktree/branch + 一条可串行
  验证的 ticket 链。当前 Claude lead 可亲自执行一条 lane，其余 lanes 自动派发。
- **Terminal fan-in**：lead 只消费 `done` / `blocked` terminal event；每个 final report 只读
  一次，验证后按依赖拓扑集成，并立刻重算 frontier。没有固定节奏轮询。

每条 execution lane 自动选择 runtime：自包含、已冻结、无需 MCP/密钥/HITL/remote write 的
hands-on work 用 `codex-pane`；需要 Claude 会话工具、tracker write、用户判断或不可逆操作的
work 用 `claude-native`。runtime 是 lane-local routing，不需要逐 lane 征求用户同意。

Claude Agent Team 只作为 pane-local accelerator，不拥有全局 lifecycle，不更新 map/spec/
tickets/PR/MR。Codex 只允许 Herdr pane 派发，禁止在 Claude Bash 里手搓 `codex exec`。

如果 `HERDR_ENV=1` 不存在，停止创建 workers，当前 lead 可继续一条安全 lane，并为其余 ready
work 输出完整 manual packets。

## Startup Gates

1. 读取 map issue、repo instructions、tracker operations 和引用 artifacts。识别 Destination、
   Decisions-so-far、Not yet specified、Out of scope、真相源、frontier 和 claim 规则。
2. 加载 `references/gate-state-machine.md`，识别当前 gate、route 和通过证据。
3. 涉及根因、因果、冲突、隐藏假设或不确定影响时，加载
   `references/toc-thinking-processes.md`。
4. 加载 `references/frontier-lanes.md`、`references/fresh-session-boundaries.md` 和
   `references/codex-first-channel.md`。完成标准：ready frontier、maximal safe batch、lane
   坐标、runtime 和 terminal channel 已明确。
5. 进入 tickets gate 或出现执行期漂移时，加载 `references/ticket-split-coverage.md`。
6. 按 work 类型加载 packet：gate/review/evidence 用 `GATE_CHILD_DISPATCH_PACKET.md`；
   discovery 用 `wayfinder-frontier-loop.md` 与 `WAYFINDER_TICKET_DISPATCH_PACKET.md`；
   grilling 用 `WAYFINDER_GRILLING_DISPATCH_PACKET.md`；execution lane 按 runtime 用
   `ISSUE_IMPLEMENT_DISPATCH_PACKET.md` 或 `CODEX_PANE_DISPATCH_PACKET.md`。
7. 创建 pane 前加载 `references/herdr-pane-placement.md`，显式解析 space/tab/pane 落点。
8. workers 运行时加载 `references/child-monitoring.md`，建立 terminal fan-in 与 watchdog。
9. 收尾 summary PR/MR 时加载 `references/remote-closeout-checklist.md`。

## Dispatch Rules

- 创建 pane 前确认 `HERDR_ENV=1`；否则不伪造并发。
- design pane label 为 `#<issue> <摘要>`；execution pane label 为
  `L<lane>(#<issue>) <摘要>`。创建命令显式带目标 workspace/tab 和 `--no-focus`。
- Claude pane 用 `claude --dangerously-skip-permissions`；Codex pane 用
  `codex -s workspace-write -a never`。sandbox escalation 必须由 lead 单独授权。
- create、send-text、pane rename、tab rename 是一个原子组；完成后再创建下一 pane。
- 每轮自动派发 maximal safe batch。重叠 mutable resources 只让相关 work 串行，不把整个
  frontier 降成串行。
- lane blocker 只停本 lane；lead 处理 terminal report 后立即重算并继续其他 ready work。
- workers 不创建 descendants、不集成、不 push、不开 PR/MR。lead 持有 route、用户判断、
  fan-in、integration 和 remote publication authority。

## Worktree Policy

- 每个 execution lane 使用独立 worktree/branch；共享 worktree 同时只允许一个 writer。
- 创建前记录 source worktree branch。用
  `git worktree add -b <lane-branch> <lane-path> <base-ref>` 创建，不切换 source worktree。
- lane path/branch 写入 packet 和坐标记录。推荐 branch `wf/<map-slug>-l<lane>`，path
  `<repo-parent>/<repo>-wf-<map-slug>-l<lane>`。
- design/read-only workers 默认不建 worktree；需要 repo writes 时也遵守一 writer 一 worktree。
- lane terminal 后先验证 clean state 和 commits；集成完成且不再复用时安全移除 worktree。

## Truth and Authority Rules

- 面向用户、worker 和 PR/MR 的自然语言用中文；skill/tool/status/path/hash 保持原样。
- map 是 index，不是 store。discovery details 留在 child resolution 与 artifacts。
- discovery frontier 清空后运行 route classifier，不默认进入 spec。
- Wayfinder child ticket 是 discovery/decision work；implementation ticket 才进入 `/implement`。
- 每次 dispatch 或 terminal event 从 tracker/Git 重算 `进度快照`，不沿用聊天记忆。
- local execution authority 在 worktree 创建、文件修改和本地 commit 前检查。
- remote publication authority 只在 push、open/update PR/MR 或 remote comment 前检查；缺失
  remote authority 不阻塞本地 lanes。
- HITL ticket 只能由真人反馈 resolve。用户判断只阻塞相关 item，不冻结其他 safe work。
- Summary PR/MR 只有 CI/CD 通过且 remote review Agent 明确 can pass 才完成。
- 不调用或复制 cc-dev workflow；本 skill 有自己的 gates。

## AFK Continuation

Claude/Codex 自动压缩是正常续航机制。lane 从 packet、tracker、Git、checks 和 checkpoint
commits 重建，不因上下文增长 hand-off。只有合同被证据推翻、需要用户判断、缺少 local
authority 或安全边界失效时暂停对应 lane。

## Minimal Run

1. 读取 map 与 frontier，自动并发派发 design maximal safe batch。
2. 每个 terminal event 到达时只读一次 final report，更新真相源并重算 frontier。
3. discovery 完成后选择 `wayfinder-complete`、`needs-spec`、
   `needs-implementation-tickets` 或 `direct-implementation-dispatch`。
4. implementation ready 后，为 maximal safe batch 建立独立 lanes；当前 lead 可执行一条，
   其余按 lane 特征自动选择 `claude-native` 或 `codex-pane`。
5. 每条 lane AFK 执行、验证、review、checkpoint；blocked 只停本 lane。
6. terminal fan-in 按拓扑集成并持续重算 frontier；全部清空后运行 whole-change gates。
7. 获得 remote publication authority 后 push/open summary PR/MR，等待 CI/CD 与 review verdict。
