# Codex-First 执行通道

派发任何 hands-on 开发工作前读取本文件。原则不变：Codex 打字，Claude 思考与验证。
调用通道是 Herdr：Codex 作为独立 pane worker 运行（`herdr agent start ... -- codex`），
与 Claude pane workers 同级——同一套落点规则、label、agent list 状态和监控。
不使用任何 Claude Code 插件转发 Codex 任务。

## 通道判定

默认把 hands-on 工作派给 Codex（`codex-pane` 通道）：

- 已批准 implementation issue 的实现（spec 已冻结）；重构；机械式迁移
- 有明确复现步骤的 bug fix；测试补写；覆盖率填充
- CI 修复、依赖升级、脚本/工具改动
- 大批量代码阅读式 exploration（原始阅读量远大于答案本身；只读）

留在 Claude（`claude-native` 通道）：

- 设计、API 设计、架构、命名、UX 判断
- 写 spec 本身就是工作的任务（spec、ticket split、dispatch packet 起草；歧义 = 设计）
- 微小改动（约 <20 行、单处明显改动）——委托开销不划算
- 需要会话内工具的任务：MCP、密钥、HITL 用户反馈
- 破坏性/不可逆操作、push、PR/MR、tracker 写操作（本来就归 lead）
- 对 Codex 产出的 review——永不委托给 Codex、永不跳过

混合任务：Claude 先定设计、冻结工单，再把 build-out 派给 Codex。
判定启发：dispatch 工单读起来像工作指令 → Codex；写工单时被迫做设计决定 → Claude。

## 地图级通道确认（实现派发前，一次）

派发本地图第一个 implementation issue 之前，lead 必须把整张地图的通道分配方案交给
用户确认一次：每个 implementation issue 一行——issue title link、拟定通道
（`codex-pane` / `claude-native`）、一句判定依据。用户确认后，该方案对本地图所有
implementation issues 生效，后续派发不再逐票询问。

- 后加入的 issue 符合已确认方案的判定标准时直接沿用，不重新确认。
- 运行期回退（codex pane 起不来、连续 2 轮验证不过收回 `claude-native`）不需要
  重新确认，但必须在 readback 的 `执行通道` 行写明。
- lead 想主动偏离已确认方案（非回退原因改通道）时，必须重新问用户。

## 调用契约（Herdr pane 派发）

- 派发面：lead 按 `herdr-pane-placement.md` 创建 codex pane，与 claude pane 完全同规——
  显式 `--workspace`、`--no-focus`、稳定 label、原子对（创建 + send-text）。
- 启动命令：`codex -s workspace-write -a never`（sandbox 限 worktree 内写、永不弹
  approval，失败直接回给模型）；创建命令的 `--cwd` 指向该 issue 的 worktree。sandbox
  挡住合法验证命令（如需要网络）时，只能由 lead 显式决定升级为
  `codex --dangerously-bypass-approvals-and-sandbox` 重派，不得默认使用。
- 工单投递：`herdr pane send-text <pane_id> '<填好的工单>'`，模板用
  `assets/CODEX_PANE_DISPATCH_PACKET.md`。工单必须自包含。send-text 只把文字录入
  composer，不会提交——之后必须补 `herdr agent send <pane_id> "$(printf '\r')"` 回车
  提交，并用 `herdr agent wait <pane_id> --status working` 确认已开跑。
- 首启信任门：codex 首次启动可能弹 hooks 信任确认（herdr integration 的
  SessionStart hook 等）。lead 不代替用户按 `t`（trust all）；测试/派发时按 esc 跳过，
  提示用户自行 review。
- 命名：codex pane label 带通道后缀，例如 `wf-impl-issue-42-cx`，让 agent list 一眼可辨。
- 修复轮：不新建 pane，直接向同一 codex pane 追加 send-text 修复工单（会话上下文仍在）。
  每轮计数；连续 2 轮验证不过，lead 收回该 issue 改 `claude-native`。
- 禁止：在任何 Claude 会话（lead 或 worker pane）的 Bash 里手搓 `codex exec` 兜底。
  Codex 只以独立 Herdr pane 的形态运行；收回就是收回，由 Claude 自己写。

## 监控与完成检测

- codex pane 的 `idle` / `working` / `blocked` 状态由 Herdr codex integration 上报，
  与 claude pane 同一套 agent list；监控节奏沿用 `child-monitoring.md`。
- 需要阻塞等待时用 `herdr agent wait <target> --status idle --timeout <ms>`；读取产出用
  `herdr agent read <target>`，只读末尾 final report 区域，不做 full-log summaries。
- 前提：`herdr integration status` 里 codex 集成为 current；`codex` 在 pane shell 的
  PATH 上且已登录。

## 工单契约

Codex pane 没有任何本会话上下文。每个工单必须自包含：目标、repo/worktree 绝对路径与
关键文件路径、允许编辑范围、禁止范围、非目标、精确验证命令、期望输出形态（改动文件
清单 + 验证输出）、final report 格式。工单质量决定成败。
工单必须写明硬性约束：不 commit、不 push、不创建/切换分支、不动 worktree 外文件。

## Review 与 commit（Claude 永远自己做）

- codex pane 永不 review 自己的产出。默认由 lead 在该 worktree `git status -sb` 加逐行
  读全量 diff，按外来贡献者 PR 的标准评审；diff 大或并行 issue 多时，派独立 claude
  review pane（用 `GATE_CHILD_DISPATCH_PACKET.md`）承接，结论回 lead。
- 验证命令由 Claude 侧自己运行；Codex 的声明只是 advisory。
- review 通过后由执行 review 的一方在该 worktree commit（范围仅限该 issue）；push、
  PR/MR、tracker 写操作仍归 lead。

## 可用性与回退

- codex pane 起不来（CLI 不在 PATH、未登录、integration 未装）：该 work item 按
  `claude-native` 继续，并提示用户修环境（安装 codex CLI、在 pane 内 `codex login`、
  `herdr integration install codex`）。
- 连续 2 轮 Codex 产出验证不过：收回 `claude-native`，由 claude pane worker 完成。
- readback 必须带 `执行通道` 行：`codex-pane <轮数>`、`claude-native` 或
  `channel fallback <原因>`。

### 常见失败模式与排查

| 症状 | 原因 | 解法 |
|------|------|------|
| pane 显示 command not found: codex | CLI 不在 PATH | 先按 claude-native 继续；用户装好 CLI 后再派 |
| pane 已启动但 agent list 无状态 | Herdr codex integration 未装 | `herdr integration install codex` 后重建 pane |
| codex 要求登录 | 凭证缺失或过期 | 用户在该 pane 内完成 `codex login` |
| 连续 2 轮验证不过 | 工单质量问题或超出 Codex 能力 | 收回 claude-native |
