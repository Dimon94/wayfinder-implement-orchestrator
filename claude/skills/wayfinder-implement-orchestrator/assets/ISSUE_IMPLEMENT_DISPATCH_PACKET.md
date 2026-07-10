# Issue 实现 worker pane 派发包

用于派发一个 issue-level `/implement` claude worker pane（`claude-native` 通道）。
判为 `codex-pane` 通道的 issue 不用本包，改用 `CODEX_PANE_DISPATCH_PACKET.md` 直接
派独立 codex pane。不要发送半截 prompt。

```text
项目：
Lead pane：
父 Spec/Scope source：<spec id/url | Wayfinder map/source issue id/url>
Issue：
Issue 标题：
基线分支：
基线提交：
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
- 只实现这个 issue。

执行通道：
- 通道：claude-native
- 判定依据：<codex-first 规则一行，例如 约 <20 行微小改动 / 需要会话内工具 /
  codex-pane 连续 2 轮失败收回>
- hands-on 写码由本 pane 的 Claude 自己完成；不要在 Bash 里手搓 `codex exec` 转包。
- 若本 issue 是从 codex-pane 收回的，在 readback 标注 `channel fallback <原因>`。

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
- 如果 `/code-review` 要求并行 helpers，优先使用 pane-local Claude Agent Team 的
  `wayfinder-integration-reviewer`，并把完整 review
  包显式传入：base commit、diff/files、spec/scope source/ticket、验收标准、禁止范围、
  验证结果、只读要求和输出格式。
- 如果无法形成有效 helper 调用，就在本 pane 执行同等的 Standards 和 Spec diff
  review，并在 final report 记录 `helper fallback`。
- 提交前修复有效 findings。如果 review 无法完成，或某个 finding 需要 lead
  判断，停止并报告 `blocked`。

提交要求：
- 是否需要 commit：有文件变更则 yes；只读 blocked report 则 no
- Commit 范围：仅限这个 issue

执行规则：
- 使用独立 Herdr worker pane，并使用自己的 worktree/branch。
- 需要分支时，只在本 worktree 目录内创建/切换；不要切换主目录/source worktree 的分支。
- 不要创建 sibling worker panes。
- 不要集成、cherry-pick、push、打开 PR/MR、关闭 tracker issue，或标记 sibling
  work complete。
- 如果 issue 被阻塞，或验收标准是错的，停止并报告 blocker，不要扩大范围。
- 在本 worker pane final answer 中输出完整 final report。
- final report 准备好后，在当前 pane 留下紧凑 handoff，供 lead 收集。

Final report：
Issue：
状态：completed | blocked
Pane：
Worktree：
分支：
Commit：<hash subject> | none
Lead handoff：ready
验证：
- <command>: pass | fail | blocked
执行通道：claude-native | channel fallback <原因>
Review：pass | blocked | helper fallback <summary>
Dirty state：clean | dirty <files>
已改文件：
-
阻塞：
-
集成建议：integrate | retry | revise-issue | blocked

Lead handoff message：
Issue：
状态：
Pane：
Commit：
验证：
执行通道：
Review：
Dirty state：
阻塞：
集成建议：
```
