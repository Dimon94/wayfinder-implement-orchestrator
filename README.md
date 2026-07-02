# Wayfinder Implement Orchestrator

[中文说明](README.zh-CN.md)

A personal Codex skill for orchestrating the Matt Pocock skills multi-session
delivery flow:

```text
/wayfinder discovery -> proof gate -> /to-prd -> /to-issues
-> issue-level /implement child threads -> integration -> summary PR/MR
```

It is a thin orchestrator. It does not replace `/wayfinder`, `/to-prd`,
`/to-issues`, `/implement`, or `/code-review`.

## Hard Dependency

This skill is tightly coupled to the
[`mattpocock-skills:ask-matt`](https://github.com/mattpocock/skills) framework shape.

It assumes the target machine already has the Matt Pocock engineering flow
installed and callable by Codex:

- `ask-matt`
- `wayfinder`
- `to-prd`
- `to-issues`
- `implement`
- `code-review`
- `writing-great-skills`

`ask-matt` defines the idea-to-ship route. This skill only coordinates the part
where that route becomes multiple issues, multiple fresh sessions, and one final
GitHub PR or GitLab MR.

## Install

```bash
git clone https://github.com/Dimon94/wayfinder-implement-orchestrator.git
cd wayfinder-implement-orchestrator
./scripts/install.sh
```

Default install target:

```bash
${CODEX_HOME:-~/.codex}/skills/wayfinder-implement-orchestrator
```

If Matt Pocock skills are not installed yet, the installer fails. To skip the
dependency check:

```bash
./scripts/install.sh --skip-deps-check
```

## Use

Invoke it explicitly in Codex:

```text
Use $wayfinder-implement-orchestrator with <wayfinder map issue URL>.
Run research/prototype/task tickets first, then PRD/issues, then parallel
issue-level /implement child threads, then one summary PR/MR.
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

`skill-bundle.json` is the package truth: name, entrypoint, install target, and
required external skills.

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

This is Codex-oriented. It expects Codex thread tools such as `create_thread`,
`read_thread`, `send_message_to_thread`, and `automation_update` when running
the orchestration path.
