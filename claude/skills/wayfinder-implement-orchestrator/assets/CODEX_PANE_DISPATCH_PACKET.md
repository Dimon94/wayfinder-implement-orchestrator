# Codex pane 工单派发包

用于把一个判为 `codex-pane` 通道的 work item 直接派给独立 codex pane。codex pane 没有
任何本会话上下文，工单必须自包含。不要发送半截工单。

pane 创建与投递按 `references/codex-first-channel.md` 和
`references/herdr-pane-placement.md`：显式 `--workspace`、`--no-focus`、原子对
（创建 + send-text）、label 带 `-cx` 后缀。

```text
工单目标：<一句话说明要交付什么>
项目：
Repo/worktree 绝对路径：
分支（已检出，不要切换）：
基线提交：
Issue：<id/url>
Issue 标题：

先读：
- <关键文件路径>

允许编辑范围：
- <路径/目录>

禁止范围：
- <路径/目录>
- worktree 外的任何文件

非目标：
- <明确不做的事>

实现要求：
- <逐条、可执行、无歧义；设计已冻结，不要重新设计>

验收标准：
-

验证命令（在 worktree 根目录逐条运行）：
-

硬性约束：
- 不要 commit，不要 push，不要创建/切换分支
- 不要修改允许编辑范围以外的文件
- 不要引入新依赖，除非工单明确允许
- 工单有矛盾或缺信息时：停止并在 final report 报 blocked，不要自行做设计决定

Final report（完成或阻塞时输出）：
状态：completed | blocked
已改文件：
- <路径> — <改动一句话>
验证：
- <command>: pass | fail
遗留问题：
- <None 或具体条目>
阻塞：
- <None 或缺什么信息/什么矛盾>
```
