# Wayfinder Ticket 子线程派发包

用于派发一个 `/wayfinder` discovery 子线程。不要发送半截 prompt。

```text
项目：
父编排线程：
Wayfinder map：
Ticket slug：
Ticket 类型：Research | Prototype | Task
基线分支：
基线提交：
执行目标：
Source worktree：

路由：
- 使用该 map 和 ticket slug 调用 /wayfinder。
- 只解决这个 ticket。

真相源：
- Map：<path>
- 既有产物：
-

允许范围：
- 这个 slug 对应的 map ticket block
- Artifact paths：
- 禁止范围：

外部可写目标：
- Map ticket block：
- Artifact paths：

执行规则：
- 使用 fresh session。
- 如果 map 仍把 ticket 标为 open，先 claim 这个 ticket 再工作。
- 不要解决 sibling tickets。
- 不要创建后续 sessions。把 `/wayfinder` Next steps 留在 final report；
  父编排线程负责打开下一批 fresh sessions。
- 不要进入 `/implement`。
- 如果 ticket 需要人为判断，停止并报告问题。
- 在 map 里链接 artifacts，不要把完整 artifacts 粘贴进 map。
- 如果 `执行目标` 和 `Source worktree` 不同，只能修改上面列出的外部可写目标；
  其他 source-worktree 路径全部只读。
- 在本子线程 final answer 中输出完整 final report。
- 如果 `send_message_to_thread` 可用，final report 准备好之后，向父编排线程
  发送一个紧凑 handoff。
- 如果无法 handoff 给父线程或 handoff 失败，在 final report 里说明。

Final report：
Ticket：
状态：resolved | blocked
线程：
Worktree：
执行目标：
Source worktree：
分支：
Commit：<hash subject> | none
父线程 handoff：sent | unavailable | failed <reason>
Map 变更：
-
Artifacts：
-
新增或解除阻塞的 tickets：
-
Wayfinder Next steps：
-
阻塞：
-
下一门禁建议：proof | more-discovery | ask-user | blocked

父线程 handoff message：
Ticket：
状态：
线程：
Artifacts：
新增或解除阻塞的 tickets：
阻塞：
下一门禁建议：
```
