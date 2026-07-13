# Wayfinder Implement Orchestrator

[中文说明](README.zh-CN.md)

A personal Codex/Claude skill bundle for orchestrating the Matt Pocock skills
multi-session delivery flow:

```text
/wayfinder discovery -> ready-frontier scheduler -> route classifier
  -> done
  -> /to-spec -> /to-tickets -> AFK execution lanes
  -> /to-tickets -> AFK execution lanes
  -> AFK execution lanes
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

On both Codex and Claude, each scheduling round recomputes the ready frontier
and automatically dispatches a maximal safe batch. Design questions fan out as
fine-grained AFK workers. Once the design is frozen, implementation runs in AFK
execution lanes: each lane has one owner and one isolated worktree/branch,
executes its ticket chain serially, and runs concurrently with non-conflicting
lanes. Ticket checkpoints are not hand-off points.

Workers report only terminal completion or a lane-local blocker. The
coordinator reads each final report once, integrates in dependency order, and
immediately recomputes the frontier. Routine progress never needs to be copied
into the main task; watchdog checks are reserved for missing terminal events,
setup failures, and tool timeouts.

The ticket-split gate requires a change-surface census across six surfaces
(production side, consumer projections, legacy-chain counterparts, legacy-truth
retirement, real first pass-through, scale tier), and execution-time drift is
controlled through patch-ticket map anchoring and contract re-freezing; the
skill's `references/ticket-split-coverage.md` is the source of truth for the
details.

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

This installs symlinks to this checkout:

```text
${CLAUDE_HOME:-~/.claude}/skills/wayfinder-implement-orchestrator
${CLAUDE_HOME:-~/.claude}/agents/wayfinder-*.md
```

After updating this repo, start a new Claude session to pick up the symlinked
skill and agents.

To install both targets:

```bash
./scripts/install.sh --target all
```

## Use

Invoke the Codex version explicitly:

```text
Use $wayfinder-implement-orchestrator with <wayfinder map issue URL>.
Run the necessary Wayfinder discovery tickets first. At every round, recompute
the ready frontier and automatically dispatch its maximal safe batch. After
discovery, decide whether to stop, synthesize a spec, split implementation
tickets, or execute existing tickets in AFK execution lanes. Keep each lane
serial and isolated, run safe lanes concurrently, use terminal-only fan-in, and
finish with one summary PR/MR.
```

Invoke the Claude version from a Herdr-managed Claude pane:

```text
Use $wayfinder-implement-orchestrator with <wayfinder map issue URL>.
Automatically fan out the maximal safe batch of discovery, grilling, gate, and
review decisions as Herdr panes. Once the design is frozen, schedule isolated
AFK execution lanes; choose the appropriate Claude-native or Codex-pane runtime
per lane, run safe lanes concurrently, and collect terminal reports only.
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
- shared frontier, lane, terminal fan-in, placement, and authority invariants
- no legacy opt-in concurrency, global-queue, idle-wait, or fixed-polling rules
- no copied cc-dev PDCA state machine

## Boundary

The Codex version uses native tasks to dispatch independent design workers and
execution lanes automatically. The current task may own one lane while other
safe lanes run in child tasks. Each lane is serial internally; lane blockers do
not stop unrelated ready work.

The Claude version expects to run inside Herdr. It automatically chooses a
lane-local runtime: `claude-native` for work needing Claude/MCP interaction and
`codex-pane` for self-contained frozen implementation. A Codex lane starts via
`herdr agent start`; it receives one lane rather than the global queue. Claude
Agent Team remains a pane-local accelerator.

Both runtimes use terminal-only fan-in instead of fixed-interval progress
polling. Judgment, integration, and remote publication stay with the
coordinator; execution workers never review their own output. Local execution
authority is checked before edits, while remote publication authority is only
required before pushes, PR/MR changes, or remote comments. Claude channel rules
live in `claude/skills/wayfinder-implement-orchestrator/references/codex-first-channel.md`.
If Codex is unavailable, affected lanes fall back to `claude-native` without
serializing unrelated lanes.
