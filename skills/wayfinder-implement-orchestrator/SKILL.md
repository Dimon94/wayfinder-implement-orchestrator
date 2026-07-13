---
name: wayfinder-implement-orchestrator
version: 1.2.0
description: Coordinate Wayfinder maps through route selection, spec/ticket gates, implementation dispatch, integration, and one summary PR/MR.
disable-model-invocation: true
skill_class: user-entry
route_family: main
reads:
  - references/gate-state-machine.md
  - references/ticket-split-coverage.md
  - references/fresh-session-boundaries.md
  - references/wayfinder-frontier-loop.md
  - references/child-monitoring.md
  - references/remote-closeout-checklist.md
  - assets/GATE_CHILD_DISPATCH_PACKET.md
  - assets/WAYFINDER_TICKET_DISPATCH_PACKET.md
  - assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md
  - assets/ISSUE_IMPLEMENT_DISPATCH_PACKET.md
  - references/toc-thinking-processes.md
writes: []
---

# Wayfinder Implement Orchestrator

只有当用户用 tracker 上的 wayfinder map issue、需要变成 shared map 的松散想法，
或已批准的 spec/tickets 集合调用时，才使用本 skill。它只负责编排链路；不替代
`/wayfinder`、`/to-spec`、`/to-tickets` 或 `/implement`。

## 启动

1. 读取或创建最小 wayfinder map issue、离工作最近的 repo instructions、
   `docs/agents/issue-tracker.md` 的 Wayfinding operations，以及任何已引用的
   research/prototype artifacts。完成标准：map issue 坐标、Destination、
   Decisions-so-far、Not yet specified、Out of scope、tracker 表达 child
   issues/blocking/frontier/assignee claim 的方式、每个当前真相源坐标都已知道或标为
   `Unknown`，每个 open、未阻塞且 unassigned 的 discovery child issue 都已知道。
   如果用户给的是松散想法而不是现有 map issue，先按 `/wayfinder` chart-map 流程命名
   Destination 并 breadth-first 探 fog；如果没有 in-scope fog，说明不需要 map，停止并
   问用户要直接进入哪种单 session 路径，不要创建空 map。
   创建或更新 tracker 内容前，同时识别 repo 的 Issue 模板与必填字段；完成
   标准：即将由本链路写入的 Issue 标题、正文、字段文本和评论均已按下方
   `Tracker 中文输出门禁` 准备为中文。
2. 加载 `references/gate-state-machine.md`。完成标准：已识别当前门禁、真相源和
   下一门禁；如果 in-scope Wayfinder child issues 都已 closed，已用 post-discovery route classifier
   选择 `wayfinder-complete`、`needs-spec`、`needs-implementation-tickets` 或
   `direct-implementation-dispatch`，并写出证据。
3. 如果当前 map/gate 涉及根因、因果、冲突、隐藏假设或不确定影响，加载
   `references/toc-thinking-processes.md`。完成标准：当前门禁已有
   TOC 记录，或缺失的 CRT 边、Conflict Cloud 假设、Injection 证据、PRT 障碍、
   NBR 风险被标成 frontier / user stop / `Unknown`。
4. 加载 `references/fresh-session-boundaries.md`。完成标准：每个可执行 work item
   都已分类为 fresh child、parent-owned gate 或 user stop；每个 fresh child 的
   `Source owner projectId` 已解析并写进 dispatch packet，或缺少同仓库项目而成为 user stop。
5. 如果 route 进入 tickets 门禁，或执行期出现修补票、被推翻合同或票面外发现，加载
   `references/ticket-split-coverage.md`。完成标准：变更面普查六面各有票或 map
   边界行；执行期新票已挂图；被推翻合同已有 supersede note 与重冻结前置。
6. 如果要派发 spec、ticket 拆分、review 或 evidence-gathering gate child，加载
   `assets/GATE_CHILD_DISPATCH_PACKET.md`。完成标准：可以不依赖聊天记忆填写一个
   gate packet。
7. 如果要派发 discovery child issues，加载
   `references/wayfinder-frontier-loop.md` 和
   `assets/WAYFINDER_TICKET_DISPATCH_PACKET.md`。完成标准：可以不依赖聊天记忆为每个
   child issue 填写一个 packet。
8. 如果下一个 discovery child issue 是 `wayfinder:grilling` 或需要实时判断，加载
   `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`。完成标准：一个 copy-paste
   prompt 能让用户在 fresh thread 跑完整拷问会话，并把结果带回父线程。
9. 如果要派发 implementation tickets，加载
   `assets/ISSUE_IMPLEMENT_DISPATCH_PACKET.md`。完成标准：可以不依赖聊天记忆为每个
   issue 填写一个 packet。
10. 如果 child threads 正在运行，加载 `references/child-monitoring.md`。完成标准：
   每个 child 都通过 startup probe，然后存在 5 分钟 automation reminder，且每次唤醒
   含上下文余量收线判断；如果缺少 automation 支持，就报告手动检查坐标。
11. 如果要收尾 summary PR/MR，加载 `references/remote-closeout-checklist.md`。完成标准：
   所有 child results、commits、checks、issue links、CI/CD 和 review-agent verdicts
   都已映射。

## 规则

- 所有面向用户、子线程、heartbeat、handoff、Issue 和 PR/MR comment 的自然语言都用中文。
  skill 名、tool 名、状态枚举、路径、分支名、commit hash 和代码字面量保持原样。
- 执行 `Tracker 中文输出门禁`：
  - 本链路及其 child threads 新建或改写的所有 Issue 标题、Issue 正文、自由文本
    字段、进度评论、resolution/closeout comment 和回复必须使用中文；这包括
    map issue、discovery child issue、spec issue 和 implementation ticket。
  - 英文模板栏目名可保留以符合 tracker schema，但栏目下的说明、结论、证据摘要
    和行动项必须用中文。skill/tool 名、标签、状态枚举、API 字段、代码、命令、
    路径、URL、分支名、commit hash 和必须精确匹配的引用保持原样。
  - 英文来源以中文概括并附原始链接；除了证据必需的短引用，不把英文段落直接
    粘贴到 Issue 或评论。
  - 每次调用 tracker 的 create/update/comment/close 操作前检查待发布文本；如果存在
    非例外的英文自然语言，先翻译或改写为中文，不得先发布再补改。
  - dispatch packet 必须显式携带这个门禁；child 返回英文 Issue 草稿或评论草稿时，
    父线程必须在远程写入前转为中文。第三方 bot 或 reviewer 已发布的文本不属于
    本链路的可控输出，但对它的回复仍必须中文。
- 每个门禁只保留一个真相源：discovery 用 `wayfinder:map` issue 和它的 child
  issues，product scope 只在 route 选择 `needs-spec` 时用 spec issue/doc，
  implementation tickets 用 tracker issues，execution 用 child thread readback 加 Git
  commits，final review 用 PR/MR。
- 用 TOC 记录判断复杂门禁：discovery 找缺失 CRT 边和 Conflict Cloud 假设，spec
  写清 what to change / what to change to / how to cause change，tickets 拆成
  Injection / prerequisite / transition step，integration 用 FRT/NBR 查合并负分支。
- Wayfinder map 是 index，不是 store。决策细节留在 resolved child issue 的
  resolution comment 和 linked artifacts；map 的 Decisions-so-far 只追加一行
  title link 加 gist。
- Wayfinder 默认是 planning：discovery tickets 产出 decisions、evidence 和必要
  linked artifacts，不交付 Destination 本身。只有 map 的 Notes 明确授权本轮把
  execution 带进 map 时，才允许 discovery ticket 做超出决策清障的执行。
- Wayfinder map 的 Destination 固定本轮边界；Not yet specified 只放仍然 in-scope
  但还不能成票的 fog，Out of scope 只放已 ruled beyond destination 的 work。
- 术语必须分层：Wayfinder child issue/ticket 是 `wayfinder:research`、
  `wayfinder:prototype`、`wayfinder:grilling` 或 `wayfinder:task`，用于发现和决策；
  implementation ticket 是 `/to-tickets` 或人工发布的交付票，用于 `/implement`。不要把
  closed Wayfinder child issues 当成 implementation tickets。
- Discovery frontier 清空不等于进入 spec。加载 `gate-state-machine.md` 的 route
  classifier，从持久真相源选择一个 route，并且只执行已选 route 的后续门禁。
- Wayfinder ticket mode 必须显式识别：`Research` 是 AFK，`Prototype` 是 HITL，
  `Grilling` 是 HITL，`Task` 可以是 HITL 或 AFK。HITL ticket 只能通过真人反馈
  resolve；agent 可以给推荐答案，但不能把推荐当成用户回答。
- `wayfinder:task` 只做让后续 decision 可判断的前置清障，例如申请访问、搬数据或
  暴露事实；它不能变成实现 Destination 的交付票。
- 每次派发 child batch 前，从当前门禁真相源现算一行 `进度快照`，并填入每个
  child dispatch packet；不要把进度写成 map 节点或长期状态。快照只写已验证事实：
  当前门禁、完成/运行/阻塞数量、正在派发的 batch、下一门禁或 blocker。
- 面向人读的 map/ticket 引用用 issue title link；裸 id/number/url 只作为坐标。
- 只在判断门禁问用户：未解决的 discovery choice、spec seam approval、ticket split
  approval、模糊 dispatch batch、integration 失败、未授权 remote action、有效的
  review-agent rejection，或 `Unknown` review-agent rejection。
- Summary PR/MR 打开不等于完成。只有 remote CI/CD 通过，且远程 review Agent 评论说
  PR/MR can pass，才算完成。
- 如果 review Agent 错了，在 PR/MR 评论里用证据反驳，然后再留一条记录解释为什么
  可能触发该 review，以及 review Agent 应该学习什么。
- 不要持续读取 child threads。派发后创建 5 分钟 reminder automation，停止主动循环，
  只在 wake-up 或 child handoff 时检查进度。
- open、未阻塞且 unassigned 的 discovery frontier 是可执行工作，不是用户 prompt。除非有
  停止条件或缺少工具阻止派发，否则自动创建 child threads。
- Discovery child issue 必须回答一个具体 TOC 缺口：CRT 因果边、Conflict Cloud
  假设、Injection 证据、PRT 障碍或 NBR 风险。Loose topic 先改写成缺口，再派发。
- 创建 worktree 或在某个 worktree 内工作时，不要切换主目录/source worktree 的
  分支。需要新分支时，只在目标 worktree 目录内创建/切换该分支。
- 只有 `create_thread` 不够。进入监控前，读取每个 child 一次，确认它已经从 dispatch
  prompt 启动；空线程或 interrupted 线程不算已派发。
- bounded execution 优先用 fresh sessions。父线程拥有 gates、user questions、
  integration、remote comments 和 PR/MR authority。
- 只把 issue-level `/implement` 工作派发为 child Codex threads。一个 issue 一个
  fresh session。不要把 loose TODOs、layers、workstreams 或 research/prototype
  tickets 当作 implementation children 派发。
- 如果多个 implementation tickets 属于同一可派发 batch，先创建所有 child threads，
  再创建 heartbeat；不要串行化彼此独立的 tickets。
- Codex thread tools 可用时就使用：发现 `create_thread`、
  `list_threads`、`read_thread`、`send_message_to_thread` 和
  `automation_update`；如果不可用，带着手动 child-session 坐标停止，不要假装已经
  并行派发。
- 不要调用或复制 cc-dev workflow。它的 child-thread mechanics 只作参考；本 skill
  有自己的 gates，且没有 `task.md` contract。

## 最小示例

用户说：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
先跑必要 discovery tickets；discovery 完成后判断是需要 spec、只需要拆一次 implementation tickets，
已有 tickets 只需要调度 `/implement`，还是 Wayfinder 已完成应停止；最后汇总到一个
summary PR/MR。
```

执行：

1. 运行 wayfinder frontier loop：先读取 Destination、Decisions-so-far、
   Not yet specified 和 Out of scope，再查询 open、未阻塞且 unassigned 的 discovery child
   issues，派发成 fresh `/wayfinder` sessions；每轮结束重读 map issue 和 frontier；
   重复直到没有可自动 discovery，或需要用户判断。
2. discovery 完成后运行 post-discovery route classifier：`wayfinder-complete` 停止；
   `needs-spec` 才进入 spec；`needs-implementation-tickets` 直接进入 implementation
   ticket split；`direct-implementation-dispatch` 直接进入 dispatch。
3. 如果选择 `needs-spec`，用 fresh `/to-spec` synthesis session；遇到 seam approval
   时回到父线程停止；然后发布 spec，再判断是否需要 tickets。
4. 如果选择 `needs-implementation-tickets`，用 map/spec 的当前真相源做一次
   implementation ticket split；遇到 ticket split approval 时回到父线程停止；然后按
   依赖顺序发布 implementation tickets。
5. 如果选择 `direct-implementation-dispatch` 或 tickets 已发布，对 ready tickets 并行派发，每个
   `/implement` child thread 一个填好的 ticket
   packet。
6. 创建 5 分钟 child-progress reminder；wake-up 时读取 terminal child reports，
   集成已验证 commits，运行 focused 和 whole-change checks，打开或更新一个 summary
   PR/MR，然后等待 CI/CD 和 review-agent approval。
