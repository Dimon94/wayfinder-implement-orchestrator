# Fresh Session 边界

派发任何可执行工作前读取本文件。

## 默认 Fresh

- Wayfinder AFK `Research` 和可自动执行的 `Task` child issues：每个 child issue
  一个 fresh `/wayfinder` child session。
- Wayfinder `Prototype`、`Grilling` 和 HITL `Task` child issues：只在用户能进入该
  child session 反馈时派发；否则父线程停在 `ask-user`，并给出完整 session prompt。
- child 发现的 Wayfinder follow-up tickets：父线程重读 map issue 和 frontier query，
  然后派发下一批 fresh sessions；children 不打开后代线程。
- Wayfinder complete：当 route classifier 选择 `wayfinder-complete`，父线程报告 map
  已达 Destination 并停止，不派发 spec、implementation ticket split 或 `/implement`。
- Spec synthesis：仅当 route classifier 选择 `needs-spec`，且 seams 已批准时，用 fresh
  `/to-spec` session 基于 map proof 起草或发布；否则 child 返回 seam proposal，由父线程
  问用户。`needs-implementation-tickets` 或 `direct-implementation-dispatch` 路线禁止补造 spec。
- Implementation ticket splitting：当 route classifier 选择
  `needs-implementation-tickets`，或 `needs-spec` 路线已发布 spec 且仍需
  implementation tickets 时，用 fresh `/to-tickets` session 起草或发布；如果 split 尚未批准，
  父线程先问用户再发布。
- Implementation：当 route classifier 选择 `direct-implementation-dispatch`，或 tickets 门禁已经发布
  且读回 ready tickets 后，每个 tracker implementation ticket/issue 一个 fresh `/implement` child session。
- Integrated review：父线程集成后，在可用时使用 fresh read-only `/code-review`
  或 repo-native review child。
- Remote CI/CD 或 review-agent fixes：把每个需要改代码的 fix 转成 tracker issue，
  或父线程明确批准的 micro-issue，再派发 fresh `/implement` child。
- 有争议的 review-agent comments：如果 verdict 不明显，用 fresh read-only child
  收集证据，然后父线程发布 PR/MR rebuttal/adaptation note。

## 父线程持有

- Human judgement gates 和 user questions。
- 判断哪个 child batch 可以安全派发。
- `create_thread`、`automation_update` 和 child coordinate records。
- Wayfinder frontier query、selection 和下一轮 dispatch。
- Integration branch cherry-picks、conflict resolution，以及 PR/MR push/open/update。
- PR/MR comments、review-agent rebuttals，以及 final remote-gate completion。
- 创建 worktree 或需要分支时，只在目标 worktree 目录内创建/切换分支；不要切换
  主目录/source worktree 的分支。

## 应该停止

不要为 live user grilling、未解决的 product choices、不清晰的 route、未批准的 ticket
splits、重叠 mutable resources、缺失 source truth，或任何无法从持久真相源验证验收标准的
work item 创建 child thread。

## 最小 Child Prompt

Spec、ticket-splitting、review 和 evidence-gathering children 使用
`GATE_CHILD_DISPATCH_PACKET.md`。

## Project Ownership 与未注册 Worktree Targeting

派发前用 `list_projects` 找到源码仓库所属的已保存项目，并把返回值记录为
`Source owner projectId`。如果 source artifacts 位于无法直接 target 的 Git worktree，
使用同一仓库的已保存项目；路径接近但属于另一仓库的 project 不是 owner。

按以下顺序解析 owner：source path 与 project path 精确匹配；source path 位于某个
project path 内时取最长匹配；Git worktree 仍未命中时，对 source 和候选 project 运行
`git rev-parse --path-format=absolute --git-common-dir`，只有 common dir 相同才算同一仓库。

`projectId` 不变量：首次 `create_thread`、worktree-to-local 降级和 replacement 都使用
同一个 `Source owner projectId`。已确认 worktree setup 失败时可以把 environment 从
`worktree` 改成 `local`，项目归属保持不变。没有同一仓库的已保存项目时停止，并请用户
先把源码仓库添加为 Codex project。

创建后第一次 startup probe 同时核对 child `cwd`：它必须等于 owner project path，或位于
该项目创建的 Codex worktree。归属不匹配就是错误派发；停止使用该 child，并按相同
`Source owner projectId` 创建 replacement。

记录两组坐标：

- Execution target：`Source owner projectId` 对应的已注册 project/worktree。
- External coordinates：tracker map/ticket issue URLs、source worktree 里的 proof 和
  artifact paths。

除非 packet 明确列出 write target，否则 external coordinates 都是只读。对 discovery
tickets，唯一允许的 external writes 是 tracker map/ticket issues 和列出的 artifact
paths。用一行向用户报告同仓库 worktree-to-local 降级；当 thread tools 可用时，不要以
手动 copy-paste instructions 结束。
