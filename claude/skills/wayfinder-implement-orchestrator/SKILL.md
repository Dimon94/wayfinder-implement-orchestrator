---
name: wayfinder-implement-orchestrator
description: Orchestrate tracker-backed Wayfinder maps through PRD, issues, Herdr pane workers, and one summary PR/MR.
---

# Wayfinder Implement Orchestrator for Claude

只有当用户用 tracker 上的 wayfinder map issue、需要变成 shared map 的松散想法，
或已批准的 PRD/issues 集合调用时，才使用本 skill。它只负责编排链路；不替代
`/wayfinder`、`/to-prd`、`/to-issues` 或 `/implement`。

## Execution Model

**Herdr pane workers are the default.** Discovery、grilling、gate、implementation 和
review work 都派发到 sibling Herdr panes，每个 pane 运行一个独立 `claude` 会话。
Worker panes 必须用 `claude --dangerously-skip-permissions` 启动。模型不强制，使用
当前 Claude 配置。
这样 Herdr 左侧 agent list 能显示 worker 的 `idle` / `working` / `blocked` / `done`，
用户也能直接点进 grilling pane 回答问题。

Claude Agent Team 只作为 **pane-local accelerator**：某个 worker pane 内需要短时并行
research、review 或 competing hypotheses 时，可以在那个 pane 内使用 Agent Team。它不
拥有全局 worker lifecycle，不替代 Herdr panes，也不直接更新 map、PRD、issues 或 PR/MR。

如果 `HERDR_ENV=1` 不存在，停止创建 workers，输出可复制的 manual worker packets，并说明
需要从 Herdr-managed pane 运行。

## Startup Gates

1. 读取或创建最小 wayfinder map issue、最近的 repo instructions、
   `docs/agents/issue-tracker.md` 的 Wayfinding operations，以及已引用 artifacts。
   完成标准：map 坐标、tracker child/blocking/frontier 表达方式、当前真相源坐标、
   open/unblocked/unclaimed discovery frontier 都已知道或标为 `Unknown`。
2. 加载 `references/gate-state-machine.md`。完成标准：当前 gate、真相源和下一 gate 已识别。
3. 当前 gate 涉及根因、因果、冲突、隐藏假设或不确定影响时，加载
   `references/toc-thinking-processes.md`。完成标准：缺失 CRT 边、
   Conflict Cloud 假设、Injection 证据、PRT 障碍或 NBR 风险已记录为 frontier /
   user stop / `Unknown`。
4. 加载 `references/fresh-session-boundaries.md`。完成标准：每个 work item 已分类为
   Herdr pane worker、pane-local Agent Team helper、lead-owned gate 或 user stop。
5. 按即将派发的 work 类型加载 dispatch packet：
   - gate/review/evidence：`assets/GATE_CHILD_DISPATCH_PACKET.md`
   - discovery：`references/wayfinder-frontier-loop.md` 和
     `assets/WAYFINDER_TICKET_DISPATCH_PACKET.md`
   - grilling：`assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`
   - implementation：`assets/ISSUE_IMPLEMENT_DISPATCH_PACKET.md`
6. workers 正在运行时加载 `references/child-monitoring.md`。完成标准：每个 worker 都有
   pane label、任务、真相源、停止条件和回报格式。
7. 收尾 summary PR/MR 时加载 `references/remote-closeout-checklist.md`。完成标准：
   worker results、commits、checks、issue links、CI/CD 和 review-agent verdicts 已映射。

## Pane Dispatch Rules

- 创建 workers 前确认 `HERDR_ENV=1`。缺失时不要假装并行派发。
- 使用 `herdr` CLI 创建 sibling panes，并给每个 pane 稳定 label，例如
  `wf-grill-auth-boundary`、`wf-research-api-shape`、`wf-impl-issue-42`、
  `wf-review-summary-pr`。
- 每个 worker pane 运行独立 Claude 会话，启动命令必须是
  `claude --dangerously-skip-permissions`。模型使用当前 Claude 配置，不在 dispatch
  中强制切换。Prompt 必须包含：map/issue title link、目标 gate、真相源、允许编辑范围、
  禁止动作、完成标准、回报格式、blocked 时要问用户的问题格式。
- 多个独立 work items 要先创建完整 worker set，再监控状态；不要串行化独立 discovery /
  grilling / implementation work。
- Grilling workers 在需要用户回答时必须在自己的 pane 里留下清晰问题，并进入 blocked。
- Implementation workers 一个 tracker issue 一个 worktree 一个 pane。会改文件的 worker
  先产出 plan；lead 批准后才实现。避免多个 panes 编辑同一文件或同一迁移序列。
- Lead 只拥有 gates、用户判断、scope approval、issue split approval、integration、
  remote comments、PR/MR authority 和最终完成判断。

## Worktree Policy

- Implementation workers 必须使用独立 git worktree 和独立 branch。创建 worktree 失败时，
  不得创建对应 Herdr pane worker；先把失败原因交回 lead。
- 创建前记录 source worktree 当前 branch 作为 base/ref。Branch 必须通过 worktree 创建流程
  生成，不能在项目主目录/source worktree 里 `git switch` / `git checkout` 到新 branch。
  首选命令形态：
  `git worktree add -b <branch> <worktree-path> <base-ref>`。
- Discovery、grilling、research、PRD、issue-splitting 和 review workers 默认不创建
  worktree；除非它们需要修改 repo 文件，且 lead 明确批准。
- 不允许任何 worker 切换 source worktree 的 branch。需要新 branch 时，只能在该 worker
  的目标 worktree 内创建或切换。
- Worktree path 和 branch name 必须在 dispatch prompt 中写明，并出现在 worker 回报里。
- Worktree 创建完成标准：`git worktree list` 能看到目标 path，目标 path 当前 branch 是
  dispatch 指定 branch，该 branch 名唯一对应一个 tracker issue，且 source worktree 的
  当前 branch 与创建前完全相同。
- Worker 完成且 lead 已集成需要的 commits/artifacts 后，必须关闭 worker branch 和
  worktree：先确认目标 worktree 无未保存变更，再 `git worktree remove <worktree-path>`，
  然后删除本地 branch。使用安全删除优先；如果 branch 删除被拒绝或 cleanup 会丢变更，
  停止并交回 lead。不要在未授权时删除 remote branch。
- Worktree 收尾完成标准：`git worktree list` 不再包含目标 path，`git branch --list
  <branch>` 不再返回该本地 branch，source worktree 当前 branch 仍与派发前相同。
- 推荐命名：branch `wf/<issue-slug>`；path `<repo-parent>/<repo-name>-wf-<issue-slug>`。

## Truth Rules

- 所有面向用户、worker pane、handoff 和 PR/MR comment 的自然语言都用中文。skill 名、
  tool 名、状态枚举、路径、分支名、commit hash 和代码字面量保持原样。
- 每个 gate 只保留一个真相源：discovery 用 `wayfinder:map` issue 和 child issues；
  product scope 用 PRD issue；implementation slices 用 tracker issues；execution 用
  worker readback 加 Git commits；final review 用 PR/MR。
- Wayfinder map 是 index，不是 store。决策细节留在 resolved child issue 的 resolution
  comment 和 linked artifacts；map 的 Decisions-so-far 只追加 title link 加 gist。
- 面向人读的 map/ticket 引用用 issue title link；裸 id/number/url 只作为坐标。
- Discovery worker 必须回答一个具体 TOC 缺口：CRT 因果边、Conflict Cloud 假设、
  Injection 证据、PRT 障碍或 NBR 风险。Loose topic 先改写成缺口，再派发。
- 只在 gate 判断处问用户：未解决 discovery choice、PRD seam approval、issue split
  approval、模糊 dispatch batch、integration 失败、未授权 remote action、有效的
  review-agent rejection，或 `Unknown` review-agent rejection。
- Summary PR/MR 打开不等于完成。只有 remote CI/CD 通过，且远程 review Agent 评论说
  PR/MR can pass，才算完成。
- 不要调用或复制 cc-dev workflow。本 skill 有自己的 gates，且没有 `task.md` contract。

## Minimal Run

用户说：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
先跑 research/prototype/task tickets，再进入 PRD/issues，然后并行派发 issue-level
/implement workers，最后汇总到一个 summary PR/MR。
```

执行：

1. 查询 open、未阻塞、未 claimed 的 discovery child issues，为每个 ready frontier
   创建 Herdr pane worker；每轮结束重读 map issue 和 frontier。
2. 如果 map 暴露人为 product 或 architecture choice，停止给 lead/user 判断；否则进入
   proof gate。
3. 边界清晰时创建 PRD gate pane worker；遇到 seam approval 回到 lead 停止；然后发布 PRD。
4. 边界清晰时创建 issue-splitting gate pane worker；遇到 split approval 回到 lead 停止；
   然后按依赖顺序发布 issues。
5. 对 ready implementation issues 先创建独立 worktree 和 branch，再创建 pane workers。
   一个 tracker issue 一个 worktree，一个 tracker issue 一个 pane。
6. Lead 综合 worker 回报，集成已验证 commits，关闭已集成 worker 的 worktree 和本地
   branch，运行 focused 和 whole-change checks，打开或更新 summary PR/MR，然后等待 CI/CD
   和 review-agent approval。
