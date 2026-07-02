# Gate Child Dispatch Packet

Fill this for one non-implementation gate child: PRD synthesis, issue splitting,
read-only review, or evidence gathering.

```text
Project:
Parent orchestrator thread:
Gate: prd | issues | review | evidence
Route skill: /to-prd | /to-issues | /code-review | none
Base branch:
Base commit:

Source coordinates:
- Wayfinder map:
- PRD:
- Tracker issues:
- Research/prototype artifacts:
- Source worktree:

Target note:
- If Source worktree is not a Codex project target, read its absolute paths as
  read-only proof from the created project thread.

Allowed scope:
- May write/publish:
- Read-only:
- Out of scope:

Stop condition:
- Stop and report if user judgement, missing proof, tracker auth failure,
  conflicting source truth, or code changes are required.

Expected artifact:
- PRD URL/body | issue split proposal/issue URLs | review report | evidence

Tracker publish guard for `prd` and `issues` gates:
- Before creating issues, search/read the tracker for existing children of the
  same PRD or same slice titles. If partial duplicates exist, stop and report
  the existing IDs instead of publishing another set.
- Do not pass Markdown bodies through shell-quoted inline strings. Use a temp
  body file, JSON encoder, or tracker helper file input so backticks,
  checkboxes, `$`, and quotes survive unchanged.
- Publish in dependency order. After each create/update, immediately read back
  the tracker issue and verify title, label, parent reference, dependency text,
  checklist count, and any code literals that were present in the source body.
- If a create/update partially succeeds or readback fails, stop. The final
  report must list every created ID, the failed field, and whether rerun would
  duplicate work.

Execution rules:
- Use a fresh session.
- Do not dispatch child threads.
- Do not enter `/implement`.
- Do not integrate, push, open/update MR, or comment on MR.
- Put the full final report in this child thread's final answer.
- If `send_message_to_thread` is available, send the parent orchestrator thread
  a compact handoff after the final report is ready.
- If parent handoff is unavailable or fails, say so in the final report.

Final report:
Gate:
Status: completed | blocked
Thread:
Artifact:
Parent handoff: sent | unavailable | failed <reason>
Source coordinates used:
-
Verification:
-
Created tracker items for `prd`/`issues` gates:
- <id/url, readback status, dependency state>
Blockers:
-
Next gate recommendation: prd | issues | dispatch | integrate | mr | ask-user | blocked

Parent handoff message:
Gate:
Status:
Thread:
Artifact:
Blockers:
Next gate recommendation:
```
