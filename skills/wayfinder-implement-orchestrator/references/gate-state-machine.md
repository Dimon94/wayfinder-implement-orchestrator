# Gate State Machine

Read this after `SKILL.md` step 2.

## Gates

| Gate | Source of truth | Pass condition | Stop for user |
| --- | --- | --- | --- |
| `discovery` | Wayfinder map | Required research/prototype tickets are resolved and linked artifacts exist | Any unresolved product, architecture, access, or risk choice |
| `proof` | Map answers plus linked artifacts | Evidence supports a PRD without hidden assumptions | Missing, contradictory, or stale proof |
| `prd` | Published PRD issue/doc | User-approved seams and scope are captured | Seam approval, scope tradeoff, or tracker failure |
| `issues` | Published tracker issues | Approved vertical slices have real issue IDs, read-back bodies, and dependencies | Split/merge/dependency judgement or partial publish |
| `dispatch` | Tracker issues | Ready issues have no blocking dependencies or mutable-resource conflicts | Ambiguous issue set, overlapping files/resources, missing base branch |
| `collect` | 5 minute automation wake-up, child thread readback | Each child reports status, commit if changed, checks, dirty state, touched files | Blocked/off-scope child or missing final report |
| `integrate` | Git commits on integration branch | Child commit is inspected, clean, in-scope, and focused checks pass after integration | Conflict, scope drift, failed check |
| `mr` | Remote MR, CI/CD status, review-agent comments | MR links PRD/issues/child threads/commits/checks/risks, CI/CD passes, and the review Agent says the MR can pass | Push/open-MR authority is unclear, CI/CD fails, valid/Unknown review rejection, or unresolved review-Agent mistake |

## Flow

```text
discovery -> proof -> prd -> issues -> dispatch -> collect -> integrate -> mr
```

Do not skip a gate. If a gate cannot be proven, either run the smallest
missing predecessor step or stop for user judgement.

## Discovery Tickets

Research and prototype tickets belong to `/wayfinder`, not `/implement`.
Run them through `wayfinder-frontier-loop.md`. When a ticket resolves, update
the map with the answer and artifact link; do not copy the full artifact into
the map.

If the map has unblocked `Research`, `Prototype`, or automatable `Task` tickets
and no row in the table says to stop for user judgement, dispatch those tickets
in the same turn. Do not end by asking the user to copy-paste child prompts.

## Implementation Batch

Dispatch a batch only when every issue in it is:

- published in the tracker;
- unblocked by dependencies or already satisfied prerequisites;
- sized for one fresh `/implement` session;
- independent from siblings in files, migrations, locks, external resources, or
  release ordering;
- clear enough that acceptance criteria can be verified without parent chat
  memory.

If any condition is `Unknown`, remove that issue from the batch or ask the user.
Create one `/implement` child per remaining issue in the same dispatch turn,
then monitor the whole batch with one heartbeat.

## Context Budget

After dispatch, do not keep a continuous parent-thread reasoning loop open.
Use the 5 minute reminder in `child-monitoring.md`; each wake-up reads only the
compact status needed to decide whether a child is still running, blocked, or
ready for the next gate.
