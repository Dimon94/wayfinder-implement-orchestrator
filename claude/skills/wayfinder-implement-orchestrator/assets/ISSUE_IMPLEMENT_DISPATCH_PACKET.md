# Claude-native AFK Execution Lane 派发包

用于需要 Claude 会话工具、tracker coordination、HITL 或不可逆判断的 lane。不要发送半截 prompt。

```text
Lane ID：L<编号>
Coordinator pane：<id>
父 Scope source：<spec/map URL>
初始 Issue：<id/title/url>
可领取 direct dependents：
- <id/title/url — prerequisites 与冲突条件>
Worktree：
分支：
Base commit：
进度快照：<gate；完成/active/blocked/ready；本 maximal safe batch>

真相源：
- Scope：<URL>
- Issue：<URL>
- Wayfinder proof：<URLs/paths>

执行通道：claude-native
允许范围：
- 可改路径：
- 可变资源：
禁止范围：
先读：
-
验收标准：
-
验证命令：
-

执行规则：
- 对当前 issue 调用 /implement，运行 focused checks 与 review，创建单票 checkpoint commit。
- 只有 direct dependent prerequisites 已满足且不与 active lanes 冲突时才继续领取。
- 不创建 sibling panes，不集成、不 push、不开 PR/MR；remote publication 归 coordinator。
- blocker 或 hidden prerequisite 只停止本 lane，不标记其他 lanes blocked。
- 自动压缩后从 packet、tracker、Git 和 checkpoints 重建。

Review gate：
- 每票提交前基于 Base commit 做 Standards + Spec diff review，修复 valid findings。
- review 需要 coordinator/user judgement 时结束为 blocked。

Lane final report：
Lane ID：
状态：completed | blocked
执行通道：claude-native
Pane：
Worktree：
分支：
完成 Issues：
未领取 dependents：
Commits：
验证：
- <command>: pass | fail | blocked
Review：pass | blocked | helper fallback <summary>
Dirty state：clean | dirty <files>
发现的隐藏前置：<none | 坐标与建议票名>
阻塞：<none | reason>
集成建议：integrate | retry | revise-issue | blocked

Terminal signal：
先输出完整 final report，再运行：
herdr agent send <coordinator-pane-id> 'WAKE: L<编号> done|blocked <一句原因>'
```
