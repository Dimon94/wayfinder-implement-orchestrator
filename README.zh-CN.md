# Wayfinder Implement Orchestrator

[English README](README.md)

一个个人 Codex skill，用来总控 Matt Pocock skills 主流程里的多 session 开发链路：

```text
/wayfinder discovery -> proof gate -> /to-prd -> /to-issues
-> issue-level /implement child threads -> integration -> summary MR
```

它是薄编排器，不替代 `/wayfinder`、`/to-prd`、`/to-issues`、`/implement` 或 `/code-review`。

## 强依赖

这个 skill 强依赖
[`mattpocock-skills:ask-matt`](https://github.com/mattpocock/skills) framework shape.

它假设目标机器已经安装 Matt Pocock skills 的 engineering flow，并且这些 skills 可以被 Codex 调用：

- `ask-matt`
- `wayfinder`
- `to-prd`
- `to-issues`
- `implement`
- `code-review`
- `writing-great-skills`

`ask-matt` 定义的是 idea -> ship 主路由；本 skill 只是在这个路由进入多 issue、多 fresh session、MR 汇总时，负责阶段门禁、子线程派发、监控和结果收敛。

## 安装

```bash
git clone https://github.com/Dimon94/wayfinder-implement-orchestrator.git
cd wayfinder-implement-orchestrator
./scripts/install.sh
```

默认安装到：

```bash
${CODEX_HOME:-~/.codex}/skills/wayfinder-implement-orchestrator
```

如果你还没安装 Matt Pocock skills，installer 会失败。临时跳过依赖检查：

```bash
./scripts/install.sh --skip-deps-check
```

## 使用

在 Codex 里显式调用：

```text
Use $wayfinder-implement-orchestrator with docs/decision-maps/my-map.md.
Run research/prototype tickets first, then PRD/issues, then parallel
issue-level /implement child threads, then one summary MR.
```

## Bundle 格式

这个仓库使用最小单 skill bundle 格式：

```text
skill-bundle.json
skills/wayfinder-implement-orchestrator/SKILL.md
skills/wayfinder-implement-orchestrator/references/*.md
skills/wayfinder-implement-orchestrator/assets/*.md
scripts/install.sh
scripts/validate.py
```

`skill-bundle.json` 是包真相源：声明名称、入口文件、安装目标和外部 skill 依赖。

## 校验

```bash
python3 scripts/validate.py
```

校验脚本会检查：

- `SKILL.md` frontmatter
- `references/` 和 `assets/` 引用路径
- bundle manifest 一致性
- 没有复制 cc-dev 的 PDCA 状态机

## 边界

这是 Codex-oriented skill。执行编排链路时，它依赖 Codex thread tools，例如 `create_thread`、`read_thread`、`send_message_to_thread` 和 `automation_update`。
