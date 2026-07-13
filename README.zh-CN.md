# Wayfinder Implement Orchestrator

[English README](README.md)

一个个人 Codex/Claude skill bundle，用来总控 Matt Pocock skills 主流程里的多 session
开发链路：

```text
/wayfinder discovery -> ready-frontier scheduler -> route classifier
  -> done
  -> /to-spec -> /to-tickets -> AFK execution lanes
  -> /to-tickets -> AFK execution lanes
  -> AFK execution lanes
-> integration -> summary PR/MR
```

它是薄编排器，不替代 `/wayfinder`、`/grilling`、`/domain-modeling`、`/prototype`、
`/research`、`/to-spec`、`/to-tickets`、`/implement` 或 `/code-review`。

## 强依赖

这个 skill 强依赖
[`mattpocock-skills:ask-matt`](https://github.com/mattpocock/skills) framework shape.

它假设目标机器已经安装 Matt Pocock skills 的 engineering flow，并且这些 skills 可以被调用：

- `ask-matt`
- `wayfinder`
- `grilling`
- `domain-modeling`
- `prototype`
- `research`
- `to-spec`
- `to-tickets`
- `implement`
- `code-review`
- `writing-great-skills`

`ask-matt` 定义的是 idea -> ship 主路由；本 skill 只是在这个路由进入多 ticket、
多 session、GitHub PR 或 GitLab MR 汇总时，负责判断当前 map 是已经完成、需要 spec、
只需拆一次 implementation tickets、或已经可以进入 AFK execution，然后编排设计 workers、
execution lanes 和结果收敛。

Codex 和 Claude 都在每轮重算 ready frontier，并自动派发 maximal safe batch。设计问题由
细粒度 AFK workers 并行处理；设计冻结后，每条 execution lane 由一个 owner 在独立
worktree/branch 内串行执行 ticket chain，彼此无冲突的 lanes 则默认并发。

Worker 只上报 terminal completion 或 lane-local blocker。Coordinator 对每份 final report
只读取一次，按依赖顺序集成并立刻重算 frontier；routine progress 不进入主会话。只有
terminal event 缺失、setup 失败或工具超时时才启用 watchdog。

拆票门禁要求对变更面逐面普查（生产侧、消费投影面、旧链对位、旧真相退役、真实首穿、
规模档六面），执行期通过修补票挂图与合同重冻结控制漂移；细节以 skill 的
`references/ticket-split-coverage.md` 为真相源。

## 安装 Codex 版

```bash
git clone https://github.com/Dimon94/wayfinder-implement-orchestrator.git
cd wayfinder-implement-orchestrator
./scripts/install.sh
```

Codex 版默认安装为指向本 checkout 的软链接：

```bash
${CODEX_HOME:-~/.codex}/skills/wayfinder-implement-orchestrator
```

以后更新这个仓库后，重启 Codex 就能读取软链接指向的新版本。

如果你还没安装 Matt Pocock skills，Codex 安装会失败。临时跳过依赖检查：

```bash
./scripts/install.sh --skip-deps-check
```

## 安装 Claude 版

```bash
./scripts/install.sh --target claude
```

会以软链接形式安装（指向本 checkout）：

```text
${CLAUDE_HOME:-~/.claude}/skills/wayfinder-implement-orchestrator
${CLAUDE_HOME:-~/.claude}/agents/wayfinder-*.md
```

以后更新这个仓库后，新开 Claude 会话即可读到软链接指向的新版本。

同时安装 Codex 和 Claude：

```bash
./scripts/install.sh --target all
```

## 使用

在 Codex 里显式调用：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
先跑必要 Wayfinder discovery tickets；每轮都重算 ready frontier，并自动派发 maximal safe
batch。discovery 完成后判断是停止、需要 spec、只需要拆一次 implementation tickets，还是
用 AFK execution lanes 执行已有 tickets。lane 内串行、无冲突 lanes 默认并发，只做
terminal fan-in；最后汇总到一个 summary PR/MR。
```

在 Herdr 管理的 Claude pane 里调用 Claude 版：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
把 ready frontier 中 maximal safe batch 的 discovery、grilling、gate 和 review 判断自动
派成 Herdr panes；设计冻结后调度相互隔离的 AFK execution lanes，按 lane 自动选择
Claude-native 或 Codex-pane runtime。安全 lanes 默认并发，只收敛 terminal reports。
```

## Bundle 格式

这个仓库使用 Codex/Claude 双目标 skill bundle 格式：

```text
skill-bundle.json
skills/wayfinder-implement-orchestrator/SKILL.md
skills/wayfinder-implement-orchestrator/references/*.md
skills/wayfinder-implement-orchestrator/assets/*.md
claude/skills/wayfinder-implement-orchestrator/SKILL.md
claude/skills/wayfinder-implement-orchestrator/references/*.md
claude/skills/wayfinder-implement-orchestrator/assets/*.md
claude/agents/wayfinder-*.md
scripts/install.sh
scripts/validate.py
```

`skill-bundle.json` 是包真相源：声明名称、入口文件、安装目标和外部 skill 依赖。

## 校验

```bash
python3 scripts/validate.py
```

校验脚本会检查：

- Codex 和 Claude `SKILL.md` frontmatter
- `references/` 和 `assets/` 引用路径
- Claude helper agent definitions
- bundle manifest 一致性
- 共享 frontier、lane、terminal fan-in、pane placement 和 authority 不变量
- 不残留显式并发、全局 queue、idle wait 或固定轮询旧规则
- 没有复制 cc-dev 的 PDCA 状态机

## 边界

Codex 版用原生 tasks 自动派发相互独立的设计 workers 和 execution lanes。当前 task 可以
负责一条 lane，其他安全 lanes 在 child tasks 中并发运行。每条 lane 内部串行；某条 lane
blocked 不会停止无关的 ready work。

Claude 版预期在 Herdr 内运行，并按 lane 自动选择 runtime：需要 Claude/MCP 交互的工作走
`claude-native`，边界冻结且可自包含执行的工作走 `codex-pane`。Codex lane 通过
`herdr agent start` 启动，一次只接收一条 lane，而不是全局 queue。Claude Agent Team
只作为单个 pane 内的局部加速器。

两个 runtime 都采用 terminal-only fan-in，不做固定间隔进度轮询。判断、集成和远程发布
留在 coordinator；执行 worker 不 review 自己的输出。本地执行 authority 在编辑前检查，
remote publication authority 只在 push、PR/MR 更新或 remote comment 前要求。通道规则见
`claude/skills/wayfinder-implement-orchestrator/references/codex-first-channel.md`。
Codex 不可用时，受影响 lanes 回退为 `claude-native`，不串行化其他无关 lanes。
