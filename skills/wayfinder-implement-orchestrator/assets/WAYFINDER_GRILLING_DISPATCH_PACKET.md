# Wayfinder Grilling Session Dispatch Packet

Fill this packet when a wayfinder map reaches an unblocked `Grilling` ticket
or any discovery ticket that needs live user judgement. One Grilling ticket gets
one fresh user-run thread for the whole grilling session, not one thread per
question.

```text
Project:
Parent orchestrator thread:
Wayfinder map:
Ticket slug:
Base branch:
Base commit:
Grilling objective:
Decision branches to resolve:
-

Route:
- Invoke /wayfinder with the map and this ticket slug.
- Resolve only this ticket.
- Use /grilling as a continuous session and /domain-modeling when terminology
  needs to be pinned down.
- Ask one question at a time and wait for user feedback, then continue with the
  next dependent question until the ticket is resolved or blocked.
- Provide your recommended answer with each question.
- Do not return to the parent after the first answer.
- If a question can be answered by exploring the codebase or linked artifacts,
  explore instead of asking the user.

Source of truth:
- Map: <path>
- Prior artifacts:
-

Allowed scope:
- Map ticket block for this slug
- Domain glossary or ADR files if /domain-modeling needs them
- Out of scope:

Return to parent:
- Only after the whole grilling ticket is resolved or blocked, discover
  `send_message_to_thread`.
- If available, send the compact parent handoff below to the parent orchestrator thread.
- If unavailable, put the compact parent handoff in the final answer for the user to paste back.

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
Docs changes:
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
Map changes:
Docs changes:
New or unblocked tickets:
Blockers:
Next gate recommendation:
```
