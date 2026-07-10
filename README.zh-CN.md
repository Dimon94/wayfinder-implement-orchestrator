# Wayfinder Implement Orchestrator

[English README](README.md)

一个个人 Codex/Claude skill bundle，用来总控 Matt Pocock skills 主流程里的多 session
开发链路：

```text
/wayfinder discovery -> route classifier
  -> done
  -> /to-spec -> /to-tickets -> /implement workers
  -> /to-tickets -> /implement workers
  -> /implement workers
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
只需拆一次 implementation tickets、或已经可以调度实现，然后编排阶段门禁、worker 派发、
监控和结果收敛。

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

会安装到：

```text
${CLAUDE_HOME:-~/.claude}/skills/wayfinder-implement-orchestrator
${CLAUDE_HOME:-~/.claude}/agents/wayfinder-*.md
```

同时安装 Codex 和 Claude：

```bash
./scripts/install.sh --target all
```

## 使用

在 Codex 里显式调用：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
先跑必要 Wayfinder discovery tickets；discovery 完成后判断是停止、需要 spec、只需要拆一次
implementation tickets，还是已有 implementation tickets 只需要调度 /implement child threads；
最后汇总到一个 summary PR/MR。
```

在 Herdr 管理的 Claude pane 里调用 Claude 版：

```text
使用 $wayfinder-implement-orchestrator 处理 <wayfinder map issue URL>。
把 discovery、grilling、gate、implementation 和 review workers 派发成 Herdr pane workers。
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
- 没有复制 cc-dev 的 PDCA 状态机

## 边界

Codex 版执行编排链路时依赖 Codex thread tools，例如 `create_thread`、`read_thread`、
`send_message_to_thread` 和 `automation_update`。

Claude 版预期在 Herdr 内运行，并派发独立 pane workers：判断型工作用
`claude --dangerously-skip-permissions` pane，spec 已冻结的 hands-on 工作用
`codex -s workspace-write -a never` pane。Claude Agent Team 只作为单个 pane 内的
局部加速器。

Claude 版的 hands-on 开发执行走 Codex-first 通道：spec 已冻结的实现型工作直接派成
独立 Codex CLI pane（`herdr agent start ... -- codex -s workspace-write -a never`），
与 Claude panes
共用同一套落点规则、label、agent list 状态和监控（herdr 的 claude/codex integration
都需已安装，见 `herdr integration status`）。判断、设计、工单、review 和集成留在
Claude；codex pane 永不 review 自己的产出。路由规则见
`claude/skills/wayfinder-implement-orchestrator/references/codex-first-channel.md`。
codex CLI 缺失或未登录时，该 work item 回退为 claude-native 执行并在回报中标注。
