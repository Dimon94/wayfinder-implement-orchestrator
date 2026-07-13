# Terminal Fan-in 与 Watchdog

workers 已派发后读取本文件。normal path 只处理 terminal events；不轮询 routine progress。

## Startup Probe

- 每个 child 创建后读取一次，确认 dispatch prompt、工作启动或非空 final report。
- `create_thread` 返回 `clientThreadId` 时记录 pending coordinate；解析到真实 thread ID 并
  通过 startup probe 后才算 started。
- 空、interrupted 或 setup failure child 用同一 packet、相同的 `projectId` 创建一次 replacement；
  旧坐标标 ignored。replacement 仍失败则报告 blocker。
- 每个 child 记录 work item/lane ID、thread ID、`Source owner projectId`、worktree/branch、
  真相源、停止条件和 terminal signal 通道。

## Terminal Signal

- child final report 准备好后用 `send_message_to_thread` 向 coordinator 发送一行
  `TERMINAL: <lane/work-item> completed|blocked <一句原因>`。
- signal 只负责唤醒；final report、Git commits/checks 和 tracker readback 才是证据。
- coordinator 不因 `working`、运行时长或上下文估算读取 child。
- terminal signal 到达后，每个 child 只读一次 final report；验证 status、commits、checks、
  dirty state、touched files 和 blocker。
- completed lane 按 dependency topology 集成后立即重算 ready frontier；blocked lane 只暂停
  自己，并同样触发 frontier 重算。

## Watchdog

watchdog 只处理 terminal signal 丢失、pending setup、worker process 消失或工具 timeout。
它不是固定 cadence。

1. timeout 时对目标 child 做一次 `read_thread` 或 recent-thread lookup。
2. pending `clientThreadId` 仍未解析时保留坐标并等待下一次外部 wake；不扫描其他 children。
3. running child 记录 still running 后停止，不读取 full log、不打断、不重派。
4. terminal 但 signal 丢失时按 Terminal Signal 流程 fan-in。
5. setup failure 时按 Startup Probe replacement 规则处理。

全部 lanes terminal 且 ready frontier 为空后，不再保留 watchdog 状态。上下文压缩后从
map/spec/tickets、child final reports、Git commits 和 PR/MR state 重建，不相信聊天快照。
