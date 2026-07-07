# Wayfinder Implement Orchestrator

[English README](README.md)

一个个人 Codex/Claude skill bundle，用来总控 Matt Pocock skills 主流程里的多 session
开发链路：

```text
/wayfinder discovery -> proof gate -> /to-prd -> /to-issues
-> issue-level /implement workers -> integration -> summary PR/MR
```

它是薄编排器，不替代 `/wayfinder`、`/grilling`、`/domain-modeling`、`/prototype`、
`/to-prd`、`/to-issues`、`/implement` 或 `/code-review`。

## 强依赖

这个 skill 强依赖
[`mattpocock-skills:ask-matt`](https://github.com/mattpocock/skills) framework shape.

它假设目标机器已经安装 Matt Pocock skills 的 engineering flow，并且这些 skills 可以被调用：

- `ask-matt`
- `wayfinder`
- `grilling`
- `domain-modeling`
- `prototype`
- `to-prd`
- `to-issues`
- `implement`
- `code-review`
- `writing-great-skills`

`ask-matt` 定义的是 idea -> ship 主路由；本 skill 只是在这个路由进入多 issue、
多 session、GitHub PR 或 GitLab MR 汇总时，负责阶段门禁、worker 派发、监控和结果收敛。

## 安装 Codex 版

```bash
git clone https://github.com/Dimon94/wayfinder-implement-orchestrator.git
cd wayfinder-implement-orchestrator
./scripts/install.sh
```

默认安装到：

```bash
${CODEX_HOME:-~/.codex}/skills/wayfinder-implement-orchestrator
```

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
先跑 AFK research/task tickets 和 HITL prototype/grilling/task tickets，再进入
PRD/issues，然后并行派发 issue-level /implement child threads，最后汇总到一个
summary PR/MR。
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

Claude 版预期在 Herdr 内运行，并派发独立的
`claude --dangerously-skip-permissions` pane workers。Claude Agent Team 只作为单个 pane
内的局部加速器。
