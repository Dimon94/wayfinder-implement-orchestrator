# AFK Execution Lane 派发包

用于派发一条以 ready issue 开始的 AFK execution lane。不要发送半截 prompt。

```text
项目：
Coordinator task：
Lane ID：
父 Spec/Scope source：<spec id/url | Wayfinder map/source issue id/url>
Initial issue：
Initial issue 标题：
可领取 direct dependents：<ids/urls；仍需在领取时重算 prerequisites/conflicts>
基线分支：
基线提交：
Source owner projectId：
集成分支：
Tracker URL：
进度快照：<当前门禁；implementation 已完成/运行/阻塞/待派发数量；本 batch；下一门禁或 blocker>

真相源：
- Spec：<id/url | none; route skipped spec because scope is already implementation-ready>
- Scope source：<map/source issue id/url and route decision>
- Issue：<id/url>
- Wayfinder proof：<map issue URL, closed ticket links, artifact paths>

路由：
- 调用 /implement。
- 先实现 initial issue。完成 checkpoint 后，只有 direct dependent 的其他 prerequisites 已
  满足且不与 active lanes 冲突时才继续；否则 lane terminal。

允许范围：
- 可改路径：
- 可变资源：
- 禁止范围：

先读：
-

验收标准：
-

验证命令：
-

Review gate：
- 实现检查通过后、提交前，基于 `Base commit` 运行 `/code-review`。
- 如果 `/code-review` 要求并行 sub-agents，先发现当前可用的 sub-agent 工具，优先用
  `spawn_agent`。
- 如果指定 `agent_type`，不要同时做 full-history/context fork。使用 no-context spawn
  或 `fork_context: false`，并把完整 review 包显式传入：base commit、diff/files、
  spec/scope source/ticket、验收标准、禁止范围、验证结果、只读要求和输出格式。
- 如果工具只支持 full-history `fork_thread`，不要指定 `agent_type`；如果无法形成有效
  sub-agent 调用，就在本线程执行同等的 Standards 和 Spec diff review，并在 final
  report 记录 `sub-agent fallback`。
- 提交前修复有效 findings。如果 review 无法完成，或某个 finding 需要父线程
  判断，停止并报告 `blocked`。

提交要求：
- 是否需要 commit：有文件变更则 yes；只读 blocked report 则 no
- Commit 范围：每张 ticket 一个 checkpoint commit

执行规则：
- 使用 fresh session，并使用自己的 worktree/branch。
- 需要分支时，只在本 worktree 目录内创建/切换；不要切换主目录/source worktree 的分支。
- 不要创建 sibling child threads；coordinator 负责全局 frontier。
- 不要集成、cherry-pick、push、打开 PR/MR、关闭 tracker issue，或标记 sibling
  work complete。
- 如果 issue 被阻塞，或验收标准是错的，停止本 lane 并报告 blocker；不要阻止其他 lanes。
- 隐藏前置升级出口：实现证据暴露票面外活跃消费者、被推翻合同或超出本票安全
  边界的爆炸半径时，停止并在 final report 的「发现的隐藏前置」给出新前置票建议
  （消费者/缺口坐标 + 一句建议票名），保持本票原范围。
- lane terminal 时输出完整 final report，并用 `send_message_to_thread` 向 coordinator 发送
  `TERMINAL: <lane-id> completed|blocked <一句原因>`。不发送 routine progress。

Final report：
Lane ID：
Completed issues：
Remaining/blocked issues：
状态：completed | blocked
线程：
Worktree：
分支：
Commit：<hash subject> | none
Terminal signal：sent | unavailable | failed <reason>
验证：
- <command>: pass | fail | blocked
Review：pass | blocked | sub-agent fallback <summary>
Dirty state：clean | dirty <files>
已改文件：
-
发现的隐藏前置：
- <坐标与建议票名> | none
阻塞：
-
集成建议：integrate | retry | revise-issue | blocked

Terminal message：
Lane ID：
状态：
线程：
Commit：
验证：
Review：
Dirty state：
阻塞：
集成建议：
```
