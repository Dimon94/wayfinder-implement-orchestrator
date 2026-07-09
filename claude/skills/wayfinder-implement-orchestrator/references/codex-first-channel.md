# Codex-First 执行通道

派发任何 hands-on 开发工作前读取本文件。路由规则改编自用户级 `/codex-first`；
调用通道固定为本机安装的 `codex@openai-codex` 插件
（GitHub: openai/codex-plugin-cc）。原则：Codex 打字，Claude 思考与验证。

## 通道判定

默认把 hands-on 工作派给 Codex（`codex-plugin` 通道）：

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
- 对 Codex 产出的 review——永不委托、永不跳过

混合任务：Claude 先定设计、冻结工单，再把 build-out 派给 Codex。
判定启发：dispatch 工单读起来像工作指令 → Codex；写工单时被迫做设计决定 → Claude。

## 调用契约（只用插件能力）

- 程序化调用：Agent tool，`subagent_type: "codex:codex-rescue"`，prompt 为完整工单
  文本加路由 flags。该 subagent 是插件的唯一任务转发面。
- 人工调用：`/codex:rescue`、`/codex:status`、`/codex:result`、`/codex:cancel`、
  `/codex:setup`，供用户和 lead 在 pane 里手动管理后台 job。
- 禁止：手写 `codex exec` 或任何 raw Codex CLI；绕过 subagent 直接调用
  `codex-companion.mjs`；在 Bash tool 中直接调 `node .../codex-companion.mjs`；
  把 review gate 派给 Codex。
- flags：实现工单加 `--write`；只读 exploration 不加 `--write` 并在工单里写明只读。
  首轮显式 `--fresh`，修复轮显式 `--resume`，保证路由确定、不依赖交互确认。
  `--model` / `--effort` 只在 lead 明确指定时传。
- 执行方式：pane worker 默认前台调用并等待结果返回；预计超长的工单可在后台运行
  Agent，完成后读回结果再继续。

## 运行时机制

`CLAUDE_PLUGIN_ROOT` 环境变量由 Claude Code 在以下上下文自动注入：
- `codex:codex-rescue` subagent 内部（Agent tool 调用时）
- `/codex:*` plugin command 执行时
- plugin hook 执行时

该变量在主 conversation 的普通 Bash tool 中**不存在**。这是 Claude Code plugin
架构的设计，不是 bug。

因此：
- ✅ Worker pane 用 `Agent(subagent_type: "codex:codex-rescue")` 派发——变量自动设置
- ✅ 用户或 lead 用 `/codex:status` 查进度——变量自动设置
- ❌ 在 Bash tool 中 `node "$CLAUDE_PLUGIN_ROOT/scripts/..."` ——变量为空，必定失败
- ❌ 在 Bash tool 中 `codex exec ...` ——绕过插件，禁止

### Lead 查询 Codex 状态的正确方式

| 场景 | 正确方式 |
|------|----------|
| 派发任务 | `Agent(subagent_type: "codex:codex-rescue", prompt: 工单)` |
| 查看运行状态 | 提示用户输入 `/codex:status` |
| 获取任务结果 | 提示用户输入 `/codex:result [job-id]` |
| 取消任务 | 提示用户输入 `/codex:cancel [job-id]` |
| 环境检查 | 提示用户输入 `/codex:setup` |

Lead 和 worker 不应尝试在 Bash 中绕路查询 Codex 状态。

## 工单契约

Codex 没有任何本会话上下文。每个工单必须包含：目标、repo/worktree 绝对路径与关键
文件路径、允许编辑范围、禁止范围、非目标、精确验证命令、期望输出形态（改动文件
清单 + 验证输出）。工单质量决定成败。

## 验证（Claude 永远自己做）

- `git status -sb` 加逐行读全量 diff，按外来贡献者 PR 的标准评审。
- 自己运行 focused 验证命令；Codex 的声明只是 advisory。
- 修复轮用 `--resume` 延续上一轮 Codex 任务；连续 2 轮失败后收回 `claude-native`，
  由 pane worker 自己完成。
- commit 由 pane worker 在 review 通过后自己做；push、PR/MR、tracker 写操作仍归 lead。

## 可用性与回退

- 调用失败、Codex 未安装或未登录：提示用户运行 `/codex:setup`；当前 work item 按
  `claude-native` 继续，不要手搓 CLI 替代。
- Subagent 返回空（codex-companion 失败时的行为）：不要重试，不要手搓 CLI，
  标注 `channel fallback: subagent returned empty` 并用 claude-native 继续。
- worker readback 必须带 `执行通道` 行：`codex-plugin <轮数>`、`claude-native` 或
  `channel fallback <原因>`。

### 常见失败模式与排查

| 症状 | 原因 | 解法 |
|------|------|------|
| Bash 中 `$CLAUDE_PLUGIN_ROOT` 为空 | 正常——主 Bash 不注入 | 用 subagent 或 `/codex:*` command |
| Subagent 返回空 | Codex 未登录或 runtime 未启动 | 让用户跑 `/codex:setup` |
| `/codex:status` 无输出 | 没有当前 session 的 job | 正常——还没派发过任务 |
| 连续 2 轮 Codex 产出无法通过验证 | 工单质量问题或 bug 超出 Codex 能力 | 收回 claude-native |
