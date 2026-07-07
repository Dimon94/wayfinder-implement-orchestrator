# Wayfinder Frontier Loop

当 discovery gate 使用 wayfinder map issue 时读取本文件。

## 循环

1. 读取 map issue 的低分辨率 index：Destination、Notes、Decisions-so-far、
   Not yet specified、Out of scope，并读取本 repo 的 Wayfinding operations。
2. 查询 `open`、未被 native blocking 阻塞、且没有 assignee 的 child issues；
   不要从 map 正文推断 open tickets。
3. 自动派发只覆盖 AFK discovery：`Research` 和可自动执行且只为 decision 清障的
   `Task` child issues，使用 `WAYFINDER_TICKET_DISPATCH_PACKET.md`。
   `Prototype`、`Grilling` 和 HITL `Task` 必须有真人参与；没有可参与的用户线程时，
   生成对应 prompt/worker 坐标并停止为 `ask-user`。
4. 派发后使用 `child-monitoring.md`；不要让父线程循环一直开着。
5. wake-up 时读取 child final reports，然后重读 map issue 的 Destination、
   Decisions-so-far、Not yet specified、Out of scope 和 frontier query。
6. 只要还有新的 open、未阻塞且 unassigned 的 discovery child issues，就从第 1 步重复。

## 停止

出现以下情况时停止 frontier loop：

- map issue 已有足够 proof 进入 PRD synthesis，且没有阻塞下一门禁的 in-scope
  Not yet specified fog；
- 下一个 frontier child issue 是 `wayfinder:prototype`、`wayfinder:grilling`、
  HITL `wayfinder:task`，或需要实时用户判断；加载
  `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`，输出一个用于完整 HITL 会话的
  已填写 prompt，然后等待 returned handoff 再继续。不要每个问题创建一个 prompt；
- child 报告 `ask-user`、`blocked` 或 `Unknown`；
- 两个 child sessions 编辑了同一个 child issue，或留下冲突 tracker state。

对非判断类 tickets，copy-paste child prompts 只是 `create_thread` 或 project
targeting 不可用时的 fallback。Codex thread tools 可用时，直接创建 fresh sessions。

父线程负责创建新线程。`/wayfinder` child 可以输出正常的 Next steps block，但不能自己
打开 descendant sessions。
