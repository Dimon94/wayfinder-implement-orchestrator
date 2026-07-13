# Terminal Fan-in 与 Watchdog

workers 派发后读取本文件。normal path 由 terminal event 驱动，不做固定 cadence 轮询。

## Startup Probe

- 确认每个 pane 出现在 Herdr agent list，且 workspace/tab、label、work item/lane ID、cwd、
  branch、真相源和停止条件与 dispatch record 一致。
- 确认 agent 已启动且完整 packet 已提交。create + send-text 原子组断裂时，用同一 packet
  重建一次，旧 pane 标为 ignored。
- 第二次仍失败时，把该 lane 标为 setup blocked；其他 lanes 继续。
- 记录派发时 `进度快照`，但每次 terminal fan-in 都从 tracker/Git 重算。
- Herdr pane status 是 lifecycle 提示；final report、tracker 和 Git 才是完成证据。

## Terminal Signals

- Claude pane：输出 final report 后发送
  `WAKE: <lane-or-item> done|blocked <一句原因>`。
- Codex pane：lead 启动后台
  `herdr wait agent-status <pane_id> --status done --timeout <ms>`；`done` 是 Herdr lifecycle
  terminal，pane final report 再区分 `completed` 或 `blocked` outcome。
- signal 只用于唤醒，不承载完成证据。ignored/replaced pane 的 signal 直接忽略。

## Fan-in

收到一条 terminal event 时：

1. 只读取该 pane 一次，取得末尾完整 final report；不总结 full logs。
2. 若 report 尚未落盘，允许一次短 grace read；仍缺失则交给 watchdog，不猜测结果。
3. 验证 ticket/lane ID、commit、focused checks、review、dirty state 和 blocker。
4. `completed`：按 dependency topology 集成已验证 commits，更新 tracker/map。
5. `blocked`：只暂停该 lane；记录 blocker/hidden prerequisite，必要时落新票。
6. 立即从真相源重算 ready frontier，自动派发下一 maximal safe batch；不等待原 batch 全部结束。

## Watchdog

watchdog 只在以下异常触发一次状态检查：startup probe 失败、terminal signal 丢失、等待命令或
工具 timeout。它不建立周期性检查，也不读取 working progress。

- running 且无 terminal report：保留 pane，重新建立一次 terminal waiter。
- terminal 但 report 缺失：短 grace read 后标为 invalid terminal，要求原 pane补 report。
- pane 消失或进程失败：保留 worktree/Git 证据，重建 lane 或标 setup blocked。
- blocker 需要用户/authority：只上报受影响 lane；其他 frontier 继续。

上下文压缩后，从 map/spec/tickets、worker final reports、Git commits 和 PR/MR state 重建。
