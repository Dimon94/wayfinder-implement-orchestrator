# Frontier、Execution Lane 与 Terminal Fan-in

design 派发、implementation dispatch 或任一 lane terminal 后读取本文件。它是 Herdr/Claude
运行时并发调度的真相源。

## Ready Frontier

`ready frontier` 是当前真相源中所有 open、未被 dependency 阻塞、未被 claim、且验收可独立
验证的 work items。每次派发和每次 terminal event 都从 tracker/Git 重算，不沿用聊天快照。

从 ready frontier 选择 `maximal safe batch`：尽可能多地选择 work items，同时保证它们两两
没有以下冲突：同一文件或 migration 序列、同一 lock/external resource、必须串行的 release
ordering、尚未满足的 dependency、同一 tracker item 写权限。缺少冲突证据时只串行相关项，
不把整个 frontier 降成串行。

## Design Fan-out

- AFK research、evidence 和可自动 task：maximal safe batch 自动创建并行 Herdr panes；不需要
  用户先授权“并行”。每个 worker 只回答一个判断问题并写自己的 ticket/artifact。
- HITL prototype、grilling 和 task：各自保留独立 pane；用户判断是该 ticket 的 blocker，
  不阻塞其他 AFK design workers。
- lead 保留 route、用户问题和 fan-in authority。worker 不创建 descendant panes；resolution
  暴露出的新 decision tickets 仍按 Wayfinder 规则创建并连线。

## Execution Lanes

`execution lane` 是一个独立 AFK owner、一个 worktree/branch 和一条可串行验证的 ticket 链。

1. maximal safe batch 中每张 implementation ticket 启动一个 lane；当前 Claude lead 可以亲自
   执行其中一条 lane，其余 lanes 按执行通道创建 Codex 或 Claude panes。
2. lane 内按 dependency order 执行 `/implement`、focused checks、review 和 checkpoint commit。
3. lane 只有在 direct dependent 的其他 prerequisites 已满足、且不会与 active lanes 冲突时，
   才继续领取该 dependent；否则输出 terminal report。
4. 某 lane blocked 只暂停该 lane。lead 立即重算 frontier，继续派发其他 safe work；只有
   blocker 支配全部剩余 work 时才停止全局执行。
5. 每个 lane 使用独立 worktree/branch。共享 worktree 只允许一个 writer。

## Runtime Selection

- self-contained、已冻结、无需 MCP/密钥/HITL/remote writes 的 hands-on lane 使用
  `codex-pane`。
- 需要 Claude 会话工具、tracker writes、用户判断或不可逆操作的 lane 使用 `claude-native`。
- runtime 是 lane-local routing，不需要逐 lane 询问用户；只有 sandbox escalation、未授权
  remote action 或用户判断才停下。

## Terminal Fan-in

- normal path 只消费 terminal notification；不读取 routine progress，不做固定 cadence 轮询。
  Claude WAKE 携带 `done|blocked`，Codex Herdr lifecycle 用 `done`，final report 再区分
  `completed|blocked` outcome。
- Claude pane 用 WAKE，Codex pane 用 `herdr wait agent-status <pane_id> --status done`；signal
  只是唤醒，final report、Git 和 tracker 才是证据。
- lead 对每个 terminal lane 只读取一次 final report，验证 commits/checks/dirty state，按
  dependency topology 集成，然后立即重算 ready frontier；不等待同批全部 lanes 才推进。
- watchdog 只处理丢失 terminal signal、启动失败或超过工具 timeout 的 pane；watchdog 触发时
  做一次状态检查，不建立固定 cadence。
- 全部 lanes terminal 且 frontier 为空后，运行 whole-change review/checks，再进入 remote gate。

## Authority Gates

- local execution authority 在创建 worktree、修改文件和本地 commit 前检查。
- remote publication authority 只在 push、打开/更新 PR/MR 或写 remote comment 前检查；缺失
  remote authority 不阻塞本地 lanes。
