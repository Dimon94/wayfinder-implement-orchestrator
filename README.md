# Wayfinder Implement Orchestrator

[中文说明](README.zh-CN.md)

A personal Codex/Claude skill bundle for orchestrating the Matt Pocock skills
multi-session delivery flow:

```text
/wayfinder discovery -> route classifier
  -> done
  -> /to-spec -> /to-tickets -> /implement workers
  -> /to-tickets -> /implement workers
  -> /implement workers
-> integration -> summary PR/MR
```

It is a thin orchestrator. It does not replace `/wayfinder`, `/grilling`,
`/domain-modeling`, `/prototype`, `/research`, `/to-spec`, `/to-tickets`, `/implement`, or
`/code-review`.

## Hard Dependency

This skill is tightly coupled to the
[`mattpocock-skills:ask-matt`](https://github.com/mattpocock/skills) framework shape.

It assumes the target machine already has the Matt Pocock engineering flow
installed and callable:

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

`ask-matt` defines the idea-to-ship route. This skill coordinates the point
where a map is complete, needs spec synthesis, needs one implementation ticket
split, or can go straight to implementation scheduling, then carries the work
across multiple sessions and one final GitHub PR or GitLab MR.

## Install Codex

```bash
git clone https://github.com/Dimon94/wayfinder-implement-orchestrator.git
cd wayfinder-implement-orchestrator
./scripts/install.sh
```

Default Codex install target is a symlink to this checkout:

```bash
${CODEX_HOME:-~/.codex}/skills/wayfinder-implement-orchestrator
```

After updating this repo, restart Codex to pick up the symlinked skill.

If Matt Pocock skills are not installed yet, the Codex install fails. To skip
the dependency check:

```bash
./scripts/install.sh --skip-deps-check
```

## Install Claude

```bash
./scripts/install.sh --target claude
```

This installs:

```text
${CLAUDE_HOME:-~/.claude}/skills/wayfinder-implement-orchestrator
${CLAUDE_HOME:-~/.claude}/agents/wayfinder-*.md
```

To install both targets:

```bash
./scripts/install.sh --target all
```

## Use

Invoke the Codex version explicitly:

```text
Use $wayfinder-implement-orchestrator with <wayfinder map issue URL>.
Run the necessary Wayfinder discovery tickets first; after discovery completes,
decide whether to stop, synthesize a spec, split implementation tickets, or
schedule /implement for existing implementation tickets; then finish with one
summary PR/MR.
```

Invoke the Claude version from a Herdr-managed Claude pane:

```text
Use $wayfinder-implement-orchestrator with <wayfinder map issue URL>.
Dispatch discovery, grilling, gate, implementation, and review workers as Herdr
pane workers.
```

## Bundle Format

This repo uses a dual-surface skill bundle format:

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

`skill-bundle.json` is the package truth: name, entrypoints, install targets,
and required external skills.

## Verify

```bash
python3 scripts/validate.py
```

The validator checks:

- Codex and Claude `SKILL.md` frontmatter
- referenced `references/` and `assets/` paths
- Claude helper agent definitions
- bundle manifest consistency
- no copied cc-dev PDCA state machine

## Boundary

The Codex version expects Codex thread tools such as `create_thread`,
`read_thread`, `send_message_to_thread`, and `automation_update`.

The Claude version expects to run inside Herdr and dispatch independent
`claude --dangerously-skip-permissions` pane workers. Claude Agent Team is only
a pane-local accelerator.

The Claude version routes hands-on development execution through a Codex-first
channel: frozen-spec implementation work is delegated to Codex via the locally
installed [`codex@openai-codex` plugin](https://github.com/openai/codex-plugin-cc)
(the `codex:codex-rescue` subagent and `/codex:*` commands), while judgment,
design, review, and integration stay in Claude. Routing rules live in
`claude/skills/wayfinder-implement-orchestrator/references/codex-first-channel.md`.
If the plugin is missing or not authenticated, workers fall back to
claude-native execution and report the fallback.
