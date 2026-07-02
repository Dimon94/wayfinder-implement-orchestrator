# Wayfinder Grilling Dispatch Packet

Fill this packet when a wayfinder map reaches an unblocked `Grilling` ticket
or any discovery ticket that needs live user judgement. Give it to the user as
one copy-paste prompt for a fresh Codex thread.

```text
Project:
Parent orchestrator thread:
Wayfinder map:
Ticket slug:
Base branch:
Base commit:

Route:
- Invoke /wayfinder with the map and this ticket slug.
- Resolve only this ticket.
- Use /grilling and /domain-modeling.
- Ask one question at a time and wait for user feedback.
- Provide your recommended answer with each question.

Source of truth:
- Map: <path>
- Prior artifacts:
-

Allowed scope:
- Map ticket block for this slug
- Domain glossary or ADR files if /domain-modeling needs them
- Out of scope:

Return to parent:
- After the grilling ticket is resolved or blocked, discover `send_message_to_thread`.
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
