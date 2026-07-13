# Codex AFK Execution Lane 工单

用于 self-contained frozen hands-on lane。一个 pane 承接一条 lane，不承接全局 queue；packet
必须自包含。

```text
Lane ID：L<编号>
Coordinator pane：<id>
目标：<一句话>
项目：
Repo/worktree 绝对路径：
分支（已检出，不要切换）：
基线提交：
初始 ticket：<id/title/url>
估时档位：<档位(总分) 上限分钟；来自 ticket body>
可领取 direct dependents：
- <id/title/url — 档位与 prerequisites/冲突条件>
Active lane conflicts：
- <lane/resource> | none

先读：
- <关键路径>
允许编辑范围：
- <路径>
禁止范围：
- <路径>
- worktree 外任何文件
非目标：
- <条目>

执行规则：
- 当前 ticket 执行 /implement、focused checks、review，并创建仅含该票的 checkpoint commit。
- 只有 direct dependent 的全部 prerequisites 已满足且不与 active lanes 冲突时才继续领取；
  否则正常结束 lane，把 dependent 留给 coordinator 重算 frontier。
- 普通实现错误和测试失败在票面内自行修复。
- 合同被推翻、需要用户判断、新 local authority 或安全边界失效时只阻塞本 lane。
- 每个 checkpoint 自检已耗墙钟：超过 2× 档位上限且离完成还远时，停止本 lane 并在
  final report 建议拆分方案（超估熔断）。
- 自动压缩后从本 packet、Git 和 checkpoints 重建，不因上下文增长停止。

每票验收与验证：
- <ticket>：<acceptance>；<commands>

硬性约束：
- 每票本地 checkpoint commit；不 push，不创建/切换 branch，不写 tracker，不开 PR/MR
- 不修改允许范围外文件，不自行做设计决定，不创建 sibling panes

Checkpoint：
Ticket：
状态：completed
Commit：<hash subject>
验证：
下一张：<ticket | terminal>

Lane final report：
Lane ID：
状态：completed | blocked
执行通道：codex-pane
完成 tickets：
每票实际分钟：<#ticket 分钟；#ticket 分钟>
未领取 dependents：
Worktree：
分支：
Commits：
验证：
- <command>: pass | fail
Review：pass | blocked
Dirty state：clean | dirty <files>
发现的隐藏前置：<none | 坐标与建议票名>
阻塞：<none | reason>
集成建议：integrate | retry | revise-ticket | blocked
```

final report 完整后进入 terminal；coordinator 通过
`herdr wait agent-status <pane_id> --status done` fan-in。
