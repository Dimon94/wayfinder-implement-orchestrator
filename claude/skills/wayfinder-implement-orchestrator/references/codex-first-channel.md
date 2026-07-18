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
- 启动 `codex -s danger-full-access -a never`。Codex 需要访问完整开发环境
  （环境配置、测试工具、依赖安装、git 提交、网络请求）才能完成实现与验证。
- 用 `CODEX_PANE_DISPATCH_PACKET.md` 投递完整 lane packet；`send-text` 后提交回车，并确认
  agent 已 working。
- pane 可在 lane 内连续执行 direct dependents，prerequisites 满足且无 active lanes
  冲突时领取。
- 每票创建本地 checkpoint commit。lead 持有 push、branch switch、PR/MR 开启、tracker 写权限。
- Claude pane Bash 中的 `codex exec` 已被 Herdr pane 渠道完全取代。

## Claude-native Lane Contract

- 当前 lead 自有 lane 或独立 Claude X pane 都使用 `ISSUE_IMPLEMENT_DISPATCH_PACKET.md`。
- lane 可使用 Claude 会话工具完成 tracker checkpoint。lead 持有 remote publication 权限。
- 独立 pane 用 `claude --dangerously-skip-permissions`；workers 使用 pane-local tools。

## Terminal Wait

- Claude pane 完整 final report 后发 WAKE。
- Codex pane 用
  `herdr wait agent-status <pane_id> --status done --timeout <ms>` 等 terminal event。
- 等待期间仅读 terminal event。terminal 后只读一次末尾 final report，并进入
  `child-monitoring.md` 的 fan-in。
- Herdr integration/CLI 不可用时该 pane setup 被阻塞；coordinator 可把 lane 改派
  `claude-native`，其他 lanes 正常执行。

## Review and Integration

lane owner 完成 focused review。coordinator 执行最终 integration review（review gate 强制）；
验证每个 checkpoint commit、复跑必要 checks，按 topology 集成。valid finding 可回原 lane 一次；
再失败则拆成新 ready work。lead 持有 push、PR/MR 和 remote comments 权限（remote publication gate）。

## Readback

每个 final report 必须含：lane ID、current/completed tickets、runtime、worktree/branch、commits、
checks、review、dirty state、hidden prerequisites、blocker 与 integration recommendation。
