# Child Monitoring

Read this only after child threads are dispatched.

## Rule

The orchestrator must not busy-poll child threads or keep accumulating progress
context. Long context and compaction make the parent worse. Use timed wake-ups.

## Setup

- Discover `automation_update` before claiming monitored dispatch.
- Before creating heartbeat, run a startup probe for each child: call
  `read_thread` once and confirm the child has a visible dispatch prompt,
  in-progress work, or a non-empty final report.
- If `create_thread` returns a `pendingWorktreeId` instead of a `threadId`,
  record that pending ID and create a heartbeat for discovery. It is not a
  started child until a real thread ID appears and passes startup probe.
- Treat `interrupted`, `idle`, or `completed` children with no visible prompt,
  model message, tool call, or final report as not started.
- For a not-started child, create one replacement thread from the same packet,
  update child coordinates, and mark the old thread as ignored. If the
  replacement also fails startup probe, stop and ask the user.
- Create a 5 minute heartbeat with an actual `automation_update` call:
  `mode: create`, `kind: heartbeat`, `destination: thread`,
  `status: ACTIVE`, target the parent thread, and use a 5 minute recurrence.
- Do not write raw automation directives by hand or replace the heartbeat with
  repeated parent-thread `read_thread` calls.
- Include only stable coordinates: child thread IDs, work item IDs, integration
  branch when relevant, tracker links, and the next gate.
- Include ignored child thread IDs with the reason so heartbeat never treats
  them as gate evidence.
- Report monitoring as active only after `automation_update` succeeds and
  returns an automation id.
- If automation tools are unavailable or the call fails, stop with the same
  coordinates and a manual 5 minute polling checklist.

## Heartbeat Prompt

The heartbeat prompt must include:

- child thread IDs or pending worktree IDs, plus work item IDs;
- ignored child thread IDs and why they are ignored;
- completed handoff IDs that are still settling;
- the 5 minute cadence;
- the integration branch;
- the rule to read each child once per wake-up;
- the rule to avoid full-log summaries;
- the rule to advance gates only from verified terminal child reports;
- the rule that child-to-parent handoff is only a wake-up hint, and the child
  final report remains the evidence source;
- the rule to delete the heartbeat after final MR remote-gate completion.

## Wake-Up Pass

On each reminder:

1. For pending worktree IDs, search recent threads once. If no thread exists,
   record one-line pending status and stop.
2. Read each resolved child thread once.
3. Ignore any child recorded as replaced, interrupted before work, or not
   started.
4. If a parent handoff says `Status: completed` but `read_thread` still shows
   `inProgress`, mark the child `settling`: do not send it a correction,
   do not replace it, and do not call it blocked. Wait for the next heartbeat
   or one short grace read if the user is actively waiting.
5. If still settling after two heartbeat passes, ask the user or inspect
   evidence from the child transcript; do not interrupt the child.
6. If running without a completed handoff, record a one-line status and stop.
7. If blocked, read only enough evidence to classify `valid`, `invalid`, or
   `Unknown`, then ask or correct the exact child thread.
8. If completed, read the child final report, confirm the parent handoff field,
   and move that work item to the next gate.
9. Do not summarize full child logs into parent context.
10. When every work item is advanced and the MR remote gate is complete, delete
   the heartbeat with `automation_update`.

If context was compacted, rebuild from sources: wayfinder map, PRD, tracker
issues, child final reports, Git commits, and MR state. Do not trust parent chat
memory for state.
