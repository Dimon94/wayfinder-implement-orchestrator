# Issue Implement Dispatch Packet

Fill this packet for one issue-level `/implement` child thread. Do not send a
partial prompt.

```text
Project:
Parent orchestrator thread:
Parent PRD:
Issue:
Issue title:
Base branch:
Base commit:
Integration branch:
Tracker URL:

Source of truth:
- PRD: <id/url>
- Issue: <id/url>
- Wayfinder map/proof: <path/url>

Route:
- Invoke /implement.
- Implement only this issue.

Allowed scope:
- Touched paths:
- Mutable resources:
- Out of scope:

Read first:
-

Acceptance criteria:
-

Verification commands:
-

Review gate:
- After implementation checks pass and before committing, run `/code-review`
  against `Base commit`.
- If `/code-review` asks for parallel sub-agents, first discover the available
  sub-agent tool. If no sub-agent tool is available in this child, run the same
  Standards and Spec diff review in this thread and record `sub-agent fallback`
  in the final report.
- Fix valid findings before commit. If review cannot be completed or a finding
  needs parent judgement, stop and report `blocked`.

Commit requirement:
- Commit required: yes for file changes, no for read-only blocked reports
- Commit scope: this issue only

Execution rules:
- Use a fresh session and its own worktree/branch.
- Do not create sibling child threads.
- Do not integrate, cherry-pick, push, open the MR, close tracker issues, or
  mark sibling work complete.
- If the issue is blocked or the acceptance criteria are wrong, stop and report
  the blocker instead of widening scope.
- Put the full final report in this child thread's final answer.
- If `send_message_to_thread` is available, send the parent orchestrator thread
  a compact handoff after the final report is ready.
- If parent handoff is unavailable or fails, say so in the final report.

Final report:
Issue:
Status: completed | blocked
Thread:
Worktree:
Branch:
Commit: <hash subject> | none
Parent handoff: sent | unavailable | failed <reason>
Verification:
- <command>: pass | fail | blocked
Review: pass | blocked | sub-agent fallback <summary>
Dirty state: clean | dirty <files>
Touched files:
-
Blockers:
-
Integration recommendation: integrate | retry | revise-issue | blocked

Parent handoff message:
Issue:
Status:
Thread:
Commit:
Verification:
Review:
Dirty state:
Blockers:
Integration recommendation:
```
