# Coordinator、Worker 与 Lane 边界

派发 design workers 或进入 implementation 前读取本文件，并同时读取 `frontier-lanes.md`。

## Ownership

coordinator 独占 route、用户问题、integration、remote publication 和 terminal fan-in。
worker 只拥有一个 design question 或一条 execution lane。Codex 自动压缩是每个 task 的
正常续航机制；压缩后从 tracker、Git 和 PR/MR 重建。

## Design Fan-out

- Wayfinder AFK `Research`、可自动执行的 `Task` 和只读 evidence 从 ready frontier 选择
  maximal safe batch，自动创建并行 workers；每个 session 只解决一个判断问题。
  `Research` worker 走 `/research` 工作流；需要写 Markdown artifact 时独占
  `research/<name>` worktree/branch。
- Wayfinder `Prototype`、`Grilling` 和 HITL `Task` child issues：只在用户能进入该
  successor task 反馈时 hand-off；否则当前 owner 停在 `ask-user`，并给出完整 task brief。
- worker terminal 后回报 coordinator；coordinator 验证 final report、重读 map/frontier 并
  立即派发下一批。worker 不打开 descendant threads；resolution 暴露出的新
  decision tickets 仍按 Wayfinder 规则创建并连线。
- Wayfinder complete：当 route classifier 选择 `wayfinder-complete`，当前 owner 报告 map
  已达 Destination 并停止，不派发 spec、implementation ticket split 或 `/implement`。
- Spec synthesis：仅当 route classifier 选择 `needs-spec`，且 seams 已批准时，派一个
  `/to-spec` worker。`needs-implementation-tickets` 或
  `direct-implementation-dispatch` 路线只能在已批准 spec 或「小型化跳过证据」
  已读回时禁止补造 spec；否则 route 无效，回到 `needs-spec`。
- Implementation ticket splitting：当 route classifier 选择
  `needs-implementation-tickets`，或 `needs-spec` 路线已发布 spec 且仍需
  implementation tickets 时派一个 `/to-tickets` worker；如果 split 尚未批准，coordinator
  先问用户再发布。

## AFK Execution Lanes

- 进入 implementation 前冻结 scope、dependency order、acceptance、禁止范围和 local
  execution authority。任一项仍是 `Unknown`，留在 design fan-out。
- ready frontier 的 maximal safe batch 自动建立并行 lanes；所有 lanes 使用 fresh children。
  Coordinator 不亲自执行任何 lane。每条 lane 有独立 worktree/branch。
- Remote CI/CD 或 review-agent fix 先成为 tracker issue 或用户批准的 micro-issue，再由
  当前 owner 继续 `/implement`。
- implementation 期间不为上下文容量主动 hand-off；自动压缩后从 issue、Git diff、checks
  和 commit history 重建。
- 每张票的 tracker readback、commit 和 checks 是 durable checkpoint。direct dependent
  ready 且不与 active lanes 冲突时，lane 直接继续；否则 terminal fan-in。
- 普通实现错误和测试失败由 lane owner 在票面内自行修复。lane blocked 后 coordinator
  继续其他 safe lanes；只有全局 frontier 被同一 blocker 支配时才停止。
- remote publication authority 只在 push、PR/MR 或 remote comment 前检查，不阻塞本地 lanes。
- 有争议的 review-agent comments：如果 verdict 不明显，当前 owner 收集证据，必要时把
  read-only 判断 hand-off 给 successor，然后由 owner 发布 PR/MR rebuttal/adaptation note。

## Coordinator 持有

- Human judgement gates 和 user questions。
- 计算 ready frontier、maximal safe batch 和 active lane conflicts。
- Wayfinder frontier query、selection 和下一步 ownership 决定。
- Integration branch cherry-picks、conflict resolution，以及 PR/MR push/open/update。
- PR/MR comments、review-agent rebuttals，以及 final remote-gate completion。
- 创建 worktree 或需要分支时，只在目标 worktree 目录内创建/切换分支；不要切换
  主目录/source worktree 的分支。

## 应该停止

未解决 product choices、不清晰 route、未批准 ticket splits、缺失 source truth 或无法
验证 acceptance 的 work 不进入 execution lane。重叠 mutable resources 只让相关 work
串行，不阻止其他 ready work 并发。

## Worker Dispatch

ready safe work 自动创建 children。implementation lane 使用
`ISSUE_IMPLEMENT_DISPATCH_PACKET.md`；design/review worker 使用对应 brief。所有 workers
进入 terminal fan-in，不进入 routine progress monitoring。

## Project Ownership 与未注册 Worktree Targeting

派发 worker 前用 `list_projects` 找到源码仓库所属的已保存项目，并把返回值记录为
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
