---
name: wayfinder-implement-orchestrator
description: Thin orchestrator for wayfinder discovery through PRD, issues, issue-level implement threads, and one summary MR.
disable-model-invocation: true
---

# Wayfinder Implement Orchestrator

Use this only when the user invokes it with a wayfinder map, a loose idea that
should become a wayfinder map, or an already-approved PRD/issues set. It
coordinates the chain; it does not replace `/wayfinder`, `/to-prd`,
`/to-issues`, or `/implement`.

## Start

1. Read or create the smallest wayfinder map, the repo instructions nearest the
   work, and any referenced research/prototype artifacts. Completion: every
   current source coordinate is known or marked `Unknown`, and every unblocked
   discovery ticket is known.
2. Load `references/gate-state-machine.md`. Completion: the current gate,
   source of truth, and next gate are identified.
3. Load `references/fresh-session-boundaries.md`. Completion: every executable
   work item is classified as fresh child, parent-owned gate, or user stop.
4. If dispatching PRD, issue-splitting, review, or evidence-gathering gate
   children, load `assets/GATE_CHILD_DISPATCH_PACKET.md`. Completion: one gate
   packet can be filled without relying on chat memory.
5. If dispatching discovery tickets, load
   `references/wayfinder-frontier-loop.md` and
   `assets/WAYFINDER_TICKET_DISPATCH_PACKET.md`. Completion: one packet can be
   filled per ticket without relying on chat memory.
6. If the next discovery ticket is `Grilling` or needs live judgement, load
   `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`. Completion: one copy-paste
   prompt lets the user run the grilling in a fresh thread and return the
   result to this parent thread.
7. If dispatching implementation issues, load
   `assets/ISSUE_IMPLEMENT_DISPATCH_PACKET.md`. Completion: one packet can be
   filled per issue without relying on chat memory.
8. If child threads are running, load `references/child-monitoring.md`.
   Completion: each child passed startup probe, then a 5 minute automation
   reminder exists, or missing automation support is reported with manual check
   coordinates.
9. If closing out a summary MR, load
   `references/mr-closeout-checklist.md`. Completion: all child results,
   commits, checks, issue links, CI/CD, and review-agent verdicts are mapped.

## Rules

- Keep one source of truth per gate: wayfinder map for discovery, PRD issue for
  product scope, tracker issues for implementation slices, child thread
  readback plus Git commits for execution, MR for final review.
- Ask the user only at judgement gates: unresolved discovery choice, PRD seam
  approval, issue split approval, ambiguous dispatch batch, failed integration,
  remote action not already authorized, valid review-agent rejection, or
  `Unknown` review-agent rejection.
- A summary MR is not done when opened. It is done only when remote CI/CD passes
  and the remote review Agent comments that the MR can pass.
- If the review Agent is wrong, rebut it in an MR comment with evidence, then
  leave a second note explaining why the review likely happened and what the
  review Agent should learn.
- Do not continuously read child threads. Dispatch, create a 5 minute reminder
  automation, stop the active loop, and inspect child progress only on wake-up
  or child handoff.
- An unblocked discovery frontier is executable work, not a user prompt. Create
  child threads automatically unless a stop condition or missing tool prevents
  dispatch.
- `create_thread` is not enough. Before monitoring, read each child once and
  confirm it has started from the dispatch prompt; empty/interrupted children
  are not dispatched.
- Prefer fresh sessions for bounded execution. The parent owns gates, user
  questions, integration, remote comments, and MR authority.
- Dispatch only issue-level `/implement` work as child Codex threads. One issue
  gets one fresh session. Do not dispatch loose TODOs, layers, workstreams, or
  research/prototype tickets as implementation children.
- If several implementation issues pass the same dispatch batch, create all of
  their child threads before the heartbeat; do not serialize independent issues.
- Use Codex thread tools when available: discover `create_thread`,
  `list_threads`, `read_thread`, `send_message_to_thread`, and
  `automation_update`; if unavailable, stop with manual child-session
  coordinates instead of pretending parallel dispatch happened.
- Do not invoke or copy the cc-dev workflow. Its child-thread mechanics are a
  reference only; this skill has its own gates and no `task.md` contract.

## Minimal Example

User says:

```text
Use $wayfinder-implement-orchestrator with docs/wayfinder/payment-map.md.
Run research/prototype tickets first, then PRD/issues, then parallel
issue-level /implement threads, then one summary MR.
```

Run:

1. Run the wayfinder frontier loop: dispatch open unblocked discovery tickets
   as fresh `/wayfinder` sessions, reread the map after each round, and repeat
   until the map has enough proof for a PRD or needs user judgement.
2. Stop if the map exposes a human product or architecture choice; otherwise
   run the proof gate.
3. Use a fresh PRD synthesis session where it is bounded; stop in the parent
   for the seam approval `/to-prd` requires; publish the PRD.
4. Use a fresh issue-splitting session where it is bounded; stop in the parent
   for issue split approval; publish dependency-ordered issues.
5. Dispatch ready issues in parallel with one filled issue packet per
   `/implement` child thread.
6. Create the 5 minute child-progress reminder; on wake-up, read terminal child
   reports, integrate verified commits, run focused and whole-change checks,
   open or update one summary MR, then wait for CI/CD and review-agent approval.
