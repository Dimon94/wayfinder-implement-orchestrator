---
name: wayfinder-implement-orchestrator
description: Orchestrate tracker-backed Wayfinder maps after discovery by deciding whether the current map needs spec synthesis, one ticket-splitting pass, or direct ticket-level Herdr implementation scheduling, then coordinate workers and one summary PR/MR.
---

# Wayfinder Implement Orchestrator for Claude

只有当用户用 tracker 上的 wayfinder map issue、需要变成 shared map 的松散想法，
或已批准的 spec/tickets 集合调用时，才使用本 skill。它只负责编排链路；不替代
`/wayfinder`、`/to-spec`、`/to-tickets` 或 `/implement`。

## Execution Model

**Herdr pane workers are the default.** Discovery、grilling、gate、implementation 和
review work 都派发到 sibling Herdr panes，每个 pane 运行一个独立 `claude` 会话。
Worker panes 必须用 `claude --dangerously-skip-permissions` 启动。模型不强制，使用
当前 Claude 配置。
这样 Herdr 左侧 agent list 能显示 worker 的 `idle` / `working` / `blocked` / `done`，
用户也能直接点进 grilling pane 回答问题。

Claude Agent Team 只作为 **pane-local accelerator**：某个 worker pane 内需要短时并行
research、review 或 competing hypotheses 时，可以在那个 pane 内使用 Agent Team。它不
拥有全局 worker lifecycle，不替代 Herdr panes，也不直接更新 map、spec、tickets 或 PR/MR。

开发执行通道按 `references/codex-first-channel.md` 判定：pane 拓扑决定 work item 跑在
哪，通道决定 pane 里 hands-on 写码交给谁。spec 已冻结的实现型工作默认经本机安装的
`codex@openai-codex` 插件（GitHub: openai/codex-plugin-cc）派给 Codex；判断、设计、
工单、review、集成永远留在 Claude。调度 Codex 只允许使用插件能力——
`codex:codex-rescue` subagent 和 `/codex:*` commands——禁止手写 raw Codex CLI。

如果 `HERDR_ENV=1` 不存在，停止创建 workers，输出可复制的 manual worker packets，并说明
需要从 Herdr-managed pane 运行。

## Startup Gates

1. 读取或创建最小 wayfinder map issue、最近的 repo instructions、
   `docs/agents/issue-tracker.md` 的 Wayfinding operations，以及已引用 artifacts。
   完成标准：map 坐标、Destination、Decisions-so-far、Not yet specified、
   Out of scope、tracker child/blocking/frontier/assignee claim 表达方式、当前真相源坐标、
   open、未阻塞且 unassigned 的 discovery frontier 都已知道或标为 `Unknown`。
   如果用户给的是松散想法而不是现有 map issue，先按 `/wayfinder` chart-map 流程命名
   Destination 并 breadth-first 探 fog；如果没有 in-scope fog，说明不需要 map，停止并
   问用户要直接进入哪种单 session 路径，不要创建空 map。
2. 加载 `references/gate-state-machine.md`。完成标准：当前 gate、真相源和下一 gate 已识别；
   如果 in-scope Wayfinder child issues 都已 closed，已用 post-discovery route classifier 选择
   `wayfinder-complete`、`needs-spec`、`needs-implementation-tickets` 或
   `direct-implementation-dispatch`，并写出证据。
3. 当前 gate 涉及根因、因果、冲突、隐藏假设或不确定影响时，加载
   `references/toc-thinking-processes.md`。完成标准：缺失 CRT 边、
   Conflict Cloud 假设、Injection 证据、PRT 障碍或 NBR 风险已记录为 frontier /
   user stop / `Unknown`。
4. 加载 `references/fresh-session-boundaries.md` 和 `references/codex-first-channel.md`。
   完成标准：每个 work item 已分类为 Herdr pane worker、pane-local Agent Team helper、
   lead-owned gate 或 user stop；每个可执行 work item 已标注执行通道 `codex-plugin`
   或 `claude-native`，并记录判定依据。
5. 按即将派发的 work 类型加载 dispatch packet：
   - gate/review/evidence：`assets/GATE_CHILD_DISPATCH_PACKET.md`
   - discovery：`references/wayfinder-frontier-loop.md` 和
     `assets/WAYFINDER_TICKET_DISPATCH_PACKET.md`
   - grilling：`assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`
   - implementation：`assets/ISSUE_IMPLEMENT_DISPATCH_PACKET.md` 和
     `references/codex-first-channel.md`
6. workers 正在运行时加载 `references/child-monitoring.md`。完成标准：每个 worker 都有
   pane label、任务、真相源、停止条件和回报格式。
7. 收尾 summary PR/MR 时加载 `references/remote-closeout-checklist.md`。完成标准：
   worker results、commits、checks、issue links、CI/CD 和 review-agent verdicts 已映射。

## Pane Dispatch Rules

- 创建 workers 前确认 `HERDR_ENV=1`。缺失时不要假装并行派发。
- 使用 `herdr` CLI 创建 sibling panes，并给每个 pane 稳定 label，例如
  `wf-grill-auth-boundary`、`wf-research-api-shape`、`wf-impl-issue-42`、
  `wf-review-summary-pr`。
- 每个 worker pane 运行独立 Claude 会话，启动命令必须是
  `claude --dangerously-skip-permissions`。模型使用当前 Claude 配置，不在 dispatch
  中强制切换。Prompt 必须包含：map/issue title link、目标 gate、真相源、允许编辑范围、
  禁止动作、完成标准、回报格式、blocked 时要问用户的问题格式。
- 多个独立 work items 要先创建完整 worker set，再监控状态；不要串行化独立 discovery /
  grilling / implementation work。
- Prototype、Grilling 和 HITL Task workers 在需要用户回答时必须在自己的 pane 里留下
  清晰问题，并进入 blocked。推荐答案只能帮助用户判断，不能替用户确认。
- Implementation workers 一个 tracker issue 一个 worktree 一个 pane。会改文件的 worker
  先产出 plan；lead 批准后才实现。避免多个 panes 编辑同一文件或同一迁移序列。
- Implementation pane 内 hands-on 写码默认走 `codex-plugin` 通道：worker 按
  `references/codex-first-channel.md` 把冻结好的工单经 `codex:codex-rescue` subagent
  派给 Codex；Claude 侧负责工单、diff review、验证和 commit。通道决定与回退情况必须
  写进 dispatch packet 和 worker readback。
- Lead 只拥有 gates、用户判断、scope approval、ticket split approval、integration、
  remote comments、PR/MR authority 和最终完成判断。

## Worktree Policy

- Implementation workers 必须使用独立 git worktree 和独立 branch。创建 worktree 失败时，
  不得创建对应 Herdr pane worker；先把失败原因交回 lead。
- 创建前记录 source worktree 当前 branch 作为 base/ref。Branch 必须通过 worktree 创建流程
  生成，不能在项目主目录/source worktree 里 `git switch` / `git checkout` 到新 branch。
  首选命令形态：
  `git worktree add -b <branch> <worktree-path> <base-ref>`。
- Discovery、grilling、research、spec、ticket-splitting 和 review workers 默认不创建
  worktree；除非它们需要修改 repo 文件，且 lead 明确批准。
- 不允许任何 worker 切换 source worktree 的 branch。需要新 branch 时，只能在该 worker
  的目标 worktree 内创建或切换。
- Worktree path 和 branch name 必须在 dispatch prompt 中写明，并出现在 worker 回报里。
- Worktree 创建完成标准：`git worktree list` 能看到目标 path，目标 path 当前 branch 是
  dispatch 指定 branch，该 branch 名唯一对应一个 tracker issue，且 source worktree 的
  当前 branch 与创建前完全相同。
- Worker 完成且 lead 已集成需要的 commits/artifacts 后，必须关闭 worker branch 和
  worktree：先确认目标 worktree 无未保存变更，再 `git worktree remove <worktree-path>`，
  然后删除本地 branch。使用安全删除优先；如果 branch 删除被拒绝或 cleanup 会丢变更，
  停止并交回 lead。不要在未授权时删除 remote branch。
- Worktree 收尾完成标准：`git worktree list` 不再包含目标 path，`git branch --list
  <branch>` 不再返回该本地 branch，source worktree 当前 branch 仍与派发前相同。
- 推荐命名：branch `wf/<issue-slug>`；path `<repo-parent>/<repo-name>-wf-<issue-slug>`。

## Truth Rules

- 所有面向用户、worker pane、handoff 和 PR/MR comment 的自然语言都用中文。skill 名、
  tool 名、状态枚举、路径、分支名、commit hash 和代码字面量保持原样。
- 每个 gate 只保留一个真相源：discovery 用 `wayfinder:map` issue 和 child issues；
  product scope 只在 route 选择 `needs-spec` 时用 spec issue/doc；implementation tickets 用
  tracker tickets/issues；execution 用 worker readback 加 Git commits；final review 用 PR/MR。
- Wayfinder map 是 index，不是 store。决策细节留在 resolved child issue 的 resolution
  comment 和 linked artifacts；map 的 Decisions-so-far 只追加 title link 加 gist。
- Wayfinder 默认是 planning：discovery tickets 产出 decisions、evidence 和必要
  linked artifacts，不交付 Destination 本身。只有 map 的 Notes 明确授权本轮把
  execution 带进 map 时，才允许 discovery worker 做超出决策清障的执行。
- Wayfinder map 的 Destination 固定本轮边界；Not yet specified 只放仍然 in-scope
  但还不能成票的 fog，Out of scope 只放已 ruled beyond destination 的 work。
- 术语必须分层：Wayfinder child issue/ticket 是 `wayfinder:research`、
  `wayfinder:prototype`、`wayfinder:grilling` 或 `wayfinder:task`，用于发现和决策；
  implementation ticket 是 `/to-tickets` 或人工发布的交付票，用于 `/implement`。不要把
  closed Wayfinder child issues 当成 implementation tickets。
- Discovery frontier 清空不等于进入 spec。加载 `gate-state-machine.md` 的 route
  classifier，从持久真相源选择一个 route，并且只执行已选 route 的后续 gate。
- Wayfinder ticket mode 必须显式识别：`Research` 是 AFK，`Prototype` 是 HITL，
  `Grilling` 是 HITL，`Task` 可以是 HITL 或 AFK。HITL ticket 只能通过真人反馈
  resolve；worker 可以给推荐答案，但不能把推荐当成用户回答。
- `wayfinder:task` 只做让后续 decision 可判断的前置清障，例如申请访问、搬数据或
  暴露事实；它不能变成实现 Destination 的交付票。
- 每次派发 worker batch 前，从当前 gate 真相源现算一行 `进度快照`，并填入每个
  dispatch packet；不要把进度写成 map 节点或长期状态。快照只写已验证事实：
  当前 gate、完成/运行/阻塞数量、正在派发的 batch、下一 gate 或 blocker。
- 面向人读的 map/ticket 引用用 issue title link；裸 id/number/url 只作为坐标。
- Discovery worker 必须回答一个具体 TOC 缺口：CRT 因果边、Conflict Cloud 假设、
  Injection 证据、PRT 障碍或 NBR 风险。Loose topic 先改写成缺口，再派发。
- 只在 gate 判断处问用户：未解决 discovery choice、spec seam approval、ticket split
  approval、模糊 dispatch batch、integration 失败、未授权 remote action、有效的
  review-agent rejection，或 `Unknown` review-agent rejection。
- Summary PR/MR 打开不等于完成。只有 remote CI/CD 通过，且远程 review Agent 评论说
  PR/MR can pass，才算完成。
- 不要调用或复制 cc-dev workflow。本 skill 有自己的 gates，且没有 `task.md` contract。

## Minimal Run

用户说：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
先跑必要 discovery tickets；discovery 完成后判断是需要 spec、只需要拆一次 implementation tickets，
已有 tickets 只需要调度 `/implement` workers，还是 Wayfinder 已完成应停止；最后汇总到
一个 summary PR/MR。
```

执行：

1. 先读取 Destination、Decisions-so-far、Not yet specified 和 Out of scope，再查询
   open、未阻塞且 unassigned 的 discovery child issues，为每个 ready frontier 创建
   Herdr pane worker；每轮结束重读 map issue 和 frontier。
2. discovery 完成后运行 post-discovery route classifier：`wayfinder-complete` 停止；
   `needs-spec` 才进入 spec；`needs-implementation-tickets` 直接进入 implementation
   ticket split；`direct-implementation-dispatch` 直接进入 dispatch。
3. 如果选择 `needs-spec`，创建 `/to-spec` gate pane worker；遇到 seam approval 回到 lead
   停止；然后发布 spec，再判断是否需要 tickets。
4. 如果选择 `needs-implementation-tickets`，用 map/spec 的当前真相源创建
   implementation ticket-splitting gate pane worker；遇到 split approval 回到 lead
   停止；然后按依赖顺序发布 implementation tickets。
5. 如果选择 `direct-implementation-dispatch` 或 tickets 已发布，对 ready implementation tickets 先创建
   独立 worktree 和 branch，再创建 pane workers。
   一个 tracker issue 一个 worktree，一个 tracker issue 一个 pane。
   pane worker 内 hands-on 实现按 `references/codex-first-channel.md` 判通道，默认经
   codex 插件执行。
6. Lead 综合 worker 回报，集成已验证 commits，关闭已集成 worker 的 worktree 和本地
   branch，运行 focused 和 whole-change checks，打开或更新 summary PR/MR，然后等待 CI/CD
   和 review-agent approval。
