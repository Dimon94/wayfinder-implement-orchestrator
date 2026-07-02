# Wayfinder Grilling 会话派发包

当 wayfinder map 走到未阻塞的 `Grilling` ticket，或任何需要实时用户判断的
discovery ticket 时，填写这个 packet。一个 Grilling ticket 对应一个用户运行的
fresh thread，承载完整拷问会话；不要每个问题开一个线程。

```text
项目：
父编排线程：
Wayfinder map：
Ticket slug：
基线分支：
基线提交：
拷问目标：
需要解决的决策分支：
-

路由：
- 使用该 map 和 ticket slug 调用 /wayfinder。
- 只解决这个 ticket。
- 把 /grilling 作为一个连续会话使用；当术语需要钉住时使用 /domain-modeling。
- 一次只问一个问题并等待用户反馈，然后继续问下一个依赖问题，直到这个 ticket
  resolved 或 blocked。
- 每个问题都给出你的推荐答案。
- 不要在第一个回答之后就返回父线程。
- 如果某个问题可以通过探索代码库或已链接 artifacts 回答，就先探索，不要问用户。

真相源：
- Map：<path>
- 既有产物：
-

允许范围：
- 这个 slug 对应的 map ticket block
- 如果 /domain-modeling 需要，可以修改 domain glossary 或 ADR 文件
- 禁止范围：

返回父线程：
- 只有当整个 grilling ticket resolved 或 blocked 后，才发现
  `send_message_to_thread`。
- 如果可用，把下面的紧凑父线程 handoff 发给父编排线程。
- 如果不可用，把紧凑父线程 handoff 放进 final answer，供用户粘贴回父线程。

Final report：
Ticket：
状态：resolved | blocked
线程：
Worktree：
分支：
Commit：<hash subject> | none
父线程 handoff：sent | unavailable | failed <reason>
Map 变更：
-
Docs 变更：
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
Map 变更：
Docs 变更：
新增或解除阻塞的 tickets：
阻塞：
下一门禁建议：
```
