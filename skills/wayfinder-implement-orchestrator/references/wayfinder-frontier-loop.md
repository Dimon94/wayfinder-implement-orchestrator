# Wayfinder Frontier Loop

当 discovery gate 使用 wayfinder map 时读取本文件。

## 循环

1. 读取完整 map。
2. 找到 `open` 且所有 `Blocked by` 都已 `resolved` 的 tickets。
3. 只派发 bounded `Research`、`Prototype` 或可自动执行的 `Task` tickets，使用
   `WAYFINDER_TICKET_DISPATCH_PACKET.md`。
4. 派发后使用 `child-monitoring.md`；不要让父线程循环一直开着。
5. wake-up 时读取 child final reports，然后从磁盘重读 map。
6. 只要还有新的未阻塞 discovery tickets，就从第 1 步重复。

## 停止

出现以下情况时停止 frontier loop：

- map 已有足够 proof 进入 PRD synthesis；
- 下一个未阻塞 ticket 是 `Grilling`，或需要实时用户判断；加载
  `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`，输出一个用于完整用户拷问会话的
  已填写 prompt，然后等待 returned handoff 再继续。不要每个问题创建一个 prompt；
- child 报告 `ask-user`、`blocked` 或 `Unknown`；
- 两个 child sessions 编辑了同一个 ticket，或留下冲突 map state。

对非判断类 tickets，copy-paste child prompts 只是 `create_thread` 或 project
targeting 不可用时的 fallback。Codex thread tools 可用时，直接创建 fresh sessions。

父线程负责创建新线程。`/wayfinder` child 可以输出正常的 Next steps block，但不能自己
打开 descendant sessions。
