# Issue 实现子线程派发包

用于派发一个 issue-level `/implement` 子线程。不要发送半截 prompt。

```text
项目：
父编排线程：
父 PRD：
Issue：
Issue 标题：
基线分支：
基线提交：
集成分支：
Tracker URL：

真相源：
- PRD：<id/url>
- Issue：<id/url>
- Wayfinder map/proof：<path/url>

路由：
- 调用 /implement。
- 只实现这个 issue。

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
- 如果 `/code-review` 要求并行 sub-agents，先发现当前可用的 sub-agent 工具。
  如果本子线程没有 sub-agent 工具，就在本线程执行同等的 Standards 和 Spec
  diff review，并在 final report 记录 `sub-agent fallback`。
- 提交前修复有效 findings。如果 review 无法完成，或某个 finding 需要父线程
  判断，停止并报告 `blocked`。

提交要求：
- 是否需要 commit：有文件变更则 yes；只读 blocked report 则 no
- Commit 范围：仅限这个 issue

执行规则：
- 使用 fresh session，并使用自己的 worktree/branch。
- 不要创建 sibling child threads。
- 不要集成、cherry-pick、push、打开 MR、关闭 tracker issue，或标记 sibling
  work complete。
- 如果 issue 被阻塞，或验收标准是错的，停止并报告 blocker，不要扩大范围。
- 在本子线程 final answer 中输出完整 final report。
- 如果 `send_message_to_thread` 可用，final report 准备好之后，向父编排线程
  发送一个紧凑 handoff。
- 如果无法 handoff 给父线程或 handoff 失败，在 final report 里说明。

Final report：
Issue：
状态：completed | blocked
线程：
Worktree：
分支：
Commit：<hash subject> | none
父线程 handoff：sent | unavailable | failed <reason>
验证：
- <command>: pass | fail | blocked
Review：pass | blocked | sub-agent fallback <summary>
Dirty state：clean | dirty <files>
已改文件：
-
阻塞：
-
集成建议：integrate | retry | revise-issue | blocked

父线程 handoff message：
Issue：
状态：
线程：
Commit：
验证：
Review：
Dirty state：
阻塞：
集成建议：
```
