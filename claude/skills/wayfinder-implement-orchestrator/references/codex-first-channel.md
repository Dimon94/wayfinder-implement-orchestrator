# Execution Lane Runtime Channel

进入 hands-on development 前读取。本文件按 lane 独立选择 runtime。

## Automatic Runtime Selection

使用 `codex-pane`，当 lane 同时满足：

- scope、acceptance、dependencies、允许/禁止范围已冻结；
- work self-contained，可仅凭 repo、ticket packet 和本地 commands 完成；
- 不需要 MCP、密钥、HITL、tracker writes、remote writes 或不可逆操作；
- 可在独立 worktree/branch 内完成并留下 checkpoint commits。

使用 `claude-native`，当 lane 需要 Claude 会话工具、tracker coordination、用户判断、密钥、
不可逆操作，或 packet 仍需动态解释。当前 lead 可直接拥有一条 claude-native lane；更多
claude-native lanes 用独立 Herdr panes。

runtime routing 自动发生，不询问用户。只有 sandbox escalation、新 local authority、remote
publication 或真实 human judgement 才停下。

## Codex Lane Contract

- 按 `herdr-pane-placement.md` 用 `herdr agent start` 创建一个 X pane，label
  `L<id>(#<issue>) <摘要>`，cwd 指向 lane 独立 worktree。
- 启动 `codex -s workspace-write -a never`。需要突破 sandbox 时停止，由 coordinator 决定，
  不默认升级。
- 用 `CODEX_PANE_DISPATCH_PACKET.md` 投递完整 lane packet；`send-text` 后提交回车，并确认
  agent 已 working。
- pane 可在 lane 内连续执行 direct dependents，但只有 prerequisites 满足且不与 active lanes
  冲突时才能领取。
- 每票创建本地 checkpoint commit；不 push、不切换 branch、不开 PR/MR、不写 tracker。
- 禁止在任何 Claude pane 的 Bash 中用 `codex exec` 兜底。

## Claude-native Lane Contract

- 当前 lead 自有 lane 或独立 Claude X pane 都使用 `ISSUE_IMPLEMENT_DISPATCH_PACKET.md`。
- lane 可使用 Claude 会话工具完成 tracker checkpoint，但 remote publication 仍归 coordinator。
- 独立 pane 用 `claude --dangerously-skip-permissions`；不创建 sibling workers。

## Terminal Wait

- Claude pane 完整 final report 后发 WAKE。
- Codex pane 用
  `herdr wait agent-status <pane_id> --status done --timeout <ms>` 等 terminal event。
- 等待期间不读 working progress。terminal 后只读一次末尾 final report，并进入
  `child-monitoring.md` 的 fan-in。
- Herdr integration/CLI 不可用只阻塞该 pane setup；coordinator 可把 lane 改派
  `claude-native`，其他 lanes 不受影响。

## Review and Integration

lane owner 完成 focused review，但不做自己的最终 integration review；review gate 永不跳过。
coordinator 验证每个
checkpoint commit、复跑必要 checks，按 topology 集成。valid finding 可回原 lane 一次；再失败
则拆成新 ready work。push、PR/MR 和 remote comments 永远留在 remote publication gate。

## Readback

每个 final report 必须含：lane ID、current/completed tickets、runtime、worktree/branch、commits、
checks、review、dirty state、hidden prerequisites、blocker 与 integration recommendation。
