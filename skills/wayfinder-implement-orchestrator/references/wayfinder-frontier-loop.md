# Wayfinder Frontier Loop

Read this when the discovery gate uses a wayfinder map.

## Loop

1. Read the whole map.
2. Find `open` tickets whose `Blocked by` entries are all `resolved`.
3. Dispatch only bounded `Research`, `Prototype`, or automatable `Task` tickets
   with `WAYFINDER_TICKET_DISPATCH_PACKET.md`.
4. Use `child-monitoring.md` after dispatch; do not keep the parent loop open.
5. On wake-up, read child final reports, then reread the map from disk.
6. Repeat from step 1 while new unblocked discovery tickets exist.

## Stop

Stop the frontier loop when:

- the map has enough proof for PRD synthesis;
- the next unblocked ticket is `Grilling` or otherwise needs live user
  judgement; load `assets/WAYFINDER_GRILLING_DISPATCH_PACKET.md`, emit one
  filled copy-paste prompt for a fresh user-run thread, then wait for the
  returned handoff before continuing;
- a child reports `ask-user`, `blocked`, or `Unknown`;
- two child sessions edited the same ticket or left conflicting map state.

For non-judgement tickets, copy-paste child prompts are only a fallback when
`create_thread` or project targeting is unavailable. With Codex thread tools
available, create the fresh sessions directly.

The parent owns new thread creation. A `/wayfinder` child may output its normal
Next steps block, but it must not open descendant sessions itself.
