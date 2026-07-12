# 子线程监控

只有在子线程已经派发后才读取本文件。

## 规则

总控线程不要忙轮询子线程，也不要持续积累进度上下文。上下文过长和压缩都会让
父线程变差。使用定时唤醒。

## 设置

- 声称已进入监控前，先发现 `automation_update`。
- 创建 heartbeat 前，对每个 child 做 startup probe：调用一次 `read_thread`，
  确认子线程里有可见派发 prompt、正在执行的工作，或非空 final report。
- 如果 `create_thread` 返回的是 `clientThreadId` 而不是 `threadId`，记录该 pending
  coordinate，并创建 heartbeat 继续发现。recent threads 暂时找不到它只代表 setup
  仍 pending；只有真实 thread ID 出现且通过 startup probe 后，才算已启动子线程。
- 如果一个 `interrupted`、`idle` 或 `completed` 子线程没有可见 prompt、
  模型消息、tool call 或 final report，把它视为未启动。
- 对已解析但未启动的子线程，或已有明确 setup failure 的 pending coordinate，用同一个
  packet 和相同的 `projectId` 创建替代线程，更新 child 坐标，并把旧坐标标为 ignored。
  worktree setup 明确失败时可以降级为 `local` environment；如果替代线程也无法通过
  startup probe，停止并询问用户。
- 用真实 `automation_update` 调用创建 5 分钟 heartbeat：
  `mode: create`, `kind: heartbeat`, `destination: thread`,
  `status: ACTIVE`, target the parent thread, and use a 5 minute recurrence.
- 不要手写 raw automation directives，也不要用父线程反复 `read_thread` 代替
  heartbeat。
- 只包含稳定坐标：child thread IDs、work item IDs、必要时的 integration
  branch、tracker links 和下一门禁。
- 包含派发时的 `进度快照`；每次唤醒只能从真相源重算进度，不沿用旧快照当事实。
- 写入 ignored child thread IDs 和原因，确保 heartbeat 不会把它们当作门禁证据。
- 只有 `automation_update` 成功并返回 automation id 后，才报告监控已启用。
- 如果 automation tools 不可用或调用失败，保留同一组坐标停止，并给出手动 5 分钟
  轮询 checklist。

## Heartbeat Prompt

heartbeat prompt 必须使用中文，并包含：

- child thread IDs 或 pending `clientThreadId` coordinates，以及 work item IDs；
- ignored child thread IDs 和忽略原因；
- 已收到 handoff 但仍处于 settling 的 child IDs；
- 5 分钟 cadence；
- integration branch；
- 派发时的 `进度快照`，以及唤醒时必须从真相源重算的规则；
- 每次唤醒只读取每个 child 一次的规则；
- 不做 full-log summaries 的规则；
- 每个 child 的上下文余量与收线阈值（见「上下文收线与续接」）；
- 只有已验证的 terminal child reports 才能推进门禁的规则；
- child-to-parent handoff 只是唤醒提示，child final report 才是证据源的规则；
- final PR/MR remote-gate 完成后删除 heartbeat 的规则。

## 上下文收线与续接

子线程的聪明区域是已用上下文 ≤ 120K（约窗口 60%）。越过后子线程判断力下降，触发
自动压缩更会丢工作状态，所以宁可收线重派，也不让子线程跑满上下文。收线是父线程
唯一主动打断运行中子线程的情形。

- 每次唤醒读取子线程时顺带估计其上下文消耗：能读到用量指示就用指示，读不到就按
  transcript 规模与已运行轮次粗估。
- 子线程已离开聪明区域且任务尚未接近完成时立即收线：向该子线程发送收线指令，要求
  停止开启新工作，把 handoff 回填到该 work item 的 tracker issue comment——已完成
  并验证的事实、剩余步骤、worktree/branch/commit 坐标、建议的下一步——然后输出以
  `HANDOFF` 开头的 final report 并结束。
- 收到 `HANDOFF` report 后核实 issue 里的回填 comment 存在且四类字段齐全；缺失时向
  同一子线程追问一次，仍缺失则父线程从真相源（commits、child transcript 尾部）补写。
- 续接派发：用同一 packet 和相同的 `projectId` 创建新子线程，prompt 附 handoff
  comment 的 title link 并声明从该 handoff 续接；implementation 子线程复用同一
  worktree 和 branch。旧线程坐标标为 ignored。
- 收线只针对上下文余量；进度慢但余量充足的子线程按原 heartbeat 节奏检查。

## 唤醒检查

每次 reminder：

1. 对 pending `clientThreadId` coordinates，只搜索一次 recent threads。若没有真实 thread，
   记录一行 pending 状态并停止。
2. 每个已解析 child thread 只读一次。
3. 忽略任何已记录为 replaced、工作前 interrupted 或 not started 的 child。
4. 如果父线程 handoff 写着 `Status: completed`，但 `read_thread` 仍显示
   `inProgress`，把该 child 标为 `settling`：不要发纠偏消息、不要替换线程、
   不要判定 blocked。等下一次 heartbeat；如果用户正在等待，可以做一次短 grace
   read。
5. 如果两次 heartbeat 后仍是 settling，询问用户或检查 child transcript 里的证据；
   不要因进度慢打断 child。
6. 如果正在运行且没有 completed handoff，估一眼上下文消耗：仍在聪明区域就记录一行
   状态并停止；已离开聪明区域则按「上下文收线与续接」收线。
7. 如果 blocked，只读足够证据来分类 `valid`、`invalid` 或 `Unknown`，然后询问用户
   或纠正准确的 child thread。
8. 如果 completed，读取 child final report，确认 parent handoff 字段，然后把该
   work item 推进到下一门禁。
9. 不要把完整 child logs 总结进父线程上下文。
10. 当所有 work item 都已推进，且 PR/MR remote gate 完成后，用 `automation_update`
    删除 heartbeat。

如果上下文被压缩，从真相源重建：wayfinder map issue、child issues、spec、tracker
tickets/issues、child final reports、Git commits 和 PR/MR state。不要相信父线程聊天记忆里的状态。
