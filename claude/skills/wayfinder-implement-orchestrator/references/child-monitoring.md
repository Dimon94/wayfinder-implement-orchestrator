# Worker 监控

只有在 Herdr worker panes 已经派发后才读取本文件。

## 规则

Lead pane 不要忙轮询 workers，也不要持续积累进度上下文。上下文过长和压缩都会让
lead 变差。派发后用 Herdr pane 状态做 5 分钟节奏检查。

## 设置

- 声称已进入监控前，确认每个 worker pane 已在 Herdr agent list 中出现、落在派发
  记录的目标 space（workspace）里，并有稳定 label、work item ID、真相源和停止条件。
- 对每个 worker 做 startup probe：打开对应 pane，确认 prompt 已贴入（原子对派发
  应保证这一点）、对应 agent 会话已启动（`claude` 或 `codex`，按通道），或已有非空
  final report。
- 如果 pane 创建失败、pane 为空、进程未启动，或 prompt 不完整（原子对断裂），用
  同一个 packet 重新执行原子对（创建 + send-text），更新 worker 坐标，并把旧 pane
  标为 ignored。如果替代 pane 也无法通过 startup probe，停止并询问用户。
- 记录稳定坐标：space（workspace）label 与 id、pane label、work item ID、
  worktree/path、branch、tracker links、ignored pane labels 和下一 gate。
- 包含派发时的 `进度快照`；每次检查只能从真相源重算进度，不沿用旧快照当事实。
- Herdr pane status 是 worker lifecycle 的真相源。
- 如果 Herdr status 不可读，保留同一组坐标停止，并给出手动 5 分钟检查清单。

## 5 分钟检查清单

每次检查必须使用中文，并包含：

- pane labels、work item IDs 和必要 worktree/branch；
- ignored pane labels 和忽略原因；
- 仍在 settling 的 worker labels；
- 派发时的 `进度快照`，以及检查时必须从真相源重算的规则；
- 每次只打开每个 pane 一次的规则；
- 不做 full-log summaries 的规则；
- 只有已验证的 terminal final reports 才能推进 gate 的规则；
- worker handoff 只是提示，worker final report 才是证据源的规则。

## 唤醒检查

每次 5 分钟检查：

1. 对每个 worker pane 只读取一次当前状态和末尾 final report 区域。
2. 忽略任何已记录为 replaced、启动前失败或 not started 的 pane。
3. 如果 pane 显示 done 但 final report 尚未完整，把该 worker 标为 `settling`：
   不发纠偏消息，不替换 pane，不判定 blocked。等下一次检查；如果用户正在等待，
   可以做一次短 grace read。
4. 如果两次检查后仍是 settling，检查 pane transcript 里的证据或询问用户；不要打断
   仍在运行的 worker。
5. 如果 worker 正在运行且没有 completed final report，记录一行状态并停止。
6. 如果 worker blocked，只读足够证据来分类 `valid`、`invalid` 或 `Unknown`，然后
   由 lead 询问用户或纠正准确的 worker pane。
7. 如果 worker completed，读取 final report，确认 handoff 字段，然后把该 work item
   推进到下一 gate。
8. 不要把完整 worker logs 总结进 lead pane 上下文。

如果上下文被压缩，从真相源重建：wayfinder map issue、child issues、spec、tracker
tickets/issues、worker final reports、Git commits 和 PR/MR state。不要相信 lead pane 聊天记忆里的状态。
