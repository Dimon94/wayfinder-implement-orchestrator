# Wayfinder Implement Orchestrator

一个个人 Codex skill，用来总控 Matt Pocock skills 主流程里的多 session 开发链路：

```text
/wayfinder discovery -> proof gate -> /to-prd -> /to-issues
-> issue-level /implement child threads -> integration -> summary MR
```

它是薄编排器，不替代 `/wayfinder`、`/to-prd`、`/to-issues`、`/implement` 或 `/code-review`。

## Hard Dependency

This skill is tightly coupled to the
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

## Install

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

## Use

在 Codex 里显式调用：

```text
Use $wayfinder-implement-orchestrator with docs/decision-maps/my-map.md.
Run research/prototype tickets first, then PRD/issues, then parallel
issue-level /implement child threads, then one summary MR.
```

## Bundle Format

This repo uses a minimal single-skill bundle format:

```text
skill-bundle.json
skills/wayfinder-implement-orchestrator/SKILL.md
skills/wayfinder-implement-orchestrator/references/*.md
skills/wayfinder-implement-orchestrator/assets/*.md
scripts/install.sh
scripts/validate.py
```

`skill-bundle.json` is the package truth: name, entrypoint, install target, and required external skills.

## Verify

```bash
python3 scripts/validate.py
```

The validator checks:

- `SKILL.md` frontmatter
- referenced `references/` and `assets/` paths
- bundle manifest consistency
- no copied cc-dev PDCA state machine

## Boundary

This is Codex-oriented. It expects Codex thread tools such as `create_thread`, `read_thread`, `send_message_to_thread`, and `automation_update` when running the orchestration path.
