# Wayfinder Ticket Dispatch Packet

Fill this packet for one `/wayfinder` discovery child thread. Do not send a
partial prompt.

```text
Project:
Parent orchestrator thread:
Wayfinder map:
Ticket slug:
Ticket type: Research | Prototype | Task
Base branch:
Base commit:

Route:
- Invoke /wayfinder with the map and this ticket slug.
- Resolve only this ticket.

Source of truth:
- Map: <path>
- Prior artifacts:
-

Allowed scope:
- Map ticket block for this slug
- Artifact paths:
- Out of scope:

Execution rules:
- Use a fresh session.
- Claim the ticket before work if the map still marks it open.
- Do not resolve sibling tickets.
- Do not create follow-up sessions. Leave `/wayfinder` Next steps in the final
  report; the parent orchestrator opens the next fresh sessions.
- Do not enter `/implement`.
- If the ticket requires human judgement, stop and report the question.
- Link artifacts from the map; do not paste full artifacts into the map.
- Put the full final report in this child thread's final answer.
- If `send_message_to_thread` is available, send the parent orchestrator thread
  a compact handoff after the final report is ready.
- If parent handoff is unavailable or fails, say so in the final report.

Final report:
Ticket:
Status: resolved | blocked
Thread:
Worktree:
Branch:
Commit: <hash subject> | none
Parent handoff: sent | unavailable | failed <reason>
Map changes:
-
Artifacts:
-
New or unblocked tickets:
-
Wayfinder Next steps:
-
Blockers:
-
Next gate recommendation: proof | more-discovery | ask-user | blocked

Parent handoff message:
Ticket:
Status:
Thread:
Artifacts:
New or unblocked tickets:
Blockers:
Next gate recommendation:
```
