# Wayfinder Frontier Loop

当 discovery gate 使用 wayfinder map issue 时读取本文件。

## 循环

1. 读取 map issue 的低分辨率 index：Destination、Notes、Decisions-so-far、
   Not yet specified、Out of scope，并读取本 repo 的 Wayfinding operations。
2. 查询 `open`、未被 native blocking 阻塞、且没有 assignee 的 child issues；
   不要从 map 正文推断 open tickets。
   同时查询 open 但仍被 blocking 阻塞或已 assigned 的 in-scope child issues，用来判断
   discovery 是否真的完成。
3. 自动派发只覆盖 AFK discovery：`Research` 和可自动执行且只为 decision 清障的
   `Task` child issues，使用 `WAYFINDER_TICKET_DISPATCH_PACKET.md`。
   `Prototype`、`Grilling` 和 HITL `Task` 必须有真人参与；没有可参与的用户 pane 时，
   生成对应 prompt/worker 坐标并停止为 `ask-user`。
4. 派发后使用 `child-monitoring.md`；不要让 lead pane 循环一直开着。
5. 5 分钟检查时读取 worker final reports，然后重读 map issue 的 Destination、
   Decisions-so-far、Not yet specified、Out of scope 和 frontier query。
6. 只要还有新的 open、未阻塞且 unassigned 的 discovery child issues，就从第 1 步重复。

## 停止

出现以下情况时停止 frontier loop：

- map issue 没有任何 open in-scope Wayfinder child issues，且没有阻塞 route 判断的
  in-scope Not yet specified fog；停止后进入 `gate-state-machine.md` 的
  post-discovery route classifier，不要在 frontier loop 内默认进入 PRD；
- frontier query 为 0，但仍有 open blocked child issues；这不是 route 条件，停在
  discovery 的 blocked/waiting 状态，列出阻塞票和前置票；
- 下一个 frontier child issue 是 `wayfinder:prototype`、`wayfinder:grilling`、
  HITL `wayfinder:task`，或需要实时用户判断；加载
  `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`，输出一个用于完整 HITL 会话的
  已填写 prompt，然后等待 returned handoff 再继续。不要每个问题创建一个 prompt；
- worker 报告 `ask-user`、`blocked` 或 `Unknown`；
- 两个 worker panes 编辑了同一个 child issue，或留下冲突 tracker state。

对非判断类 tickets，copy-paste worker prompts 只是 `HERDR_ENV` 缺失或 Herdr pane
创建不可用时的 fallback。Herdr 可用时，直接创建 worker panes。

Lead 负责创建 worker panes。`/wayfinder` worker 可以建议后续 frontier，但不能自己打开
descendant panes，也不能建议进入 `/to-prd` 或 `/to-issues`。
