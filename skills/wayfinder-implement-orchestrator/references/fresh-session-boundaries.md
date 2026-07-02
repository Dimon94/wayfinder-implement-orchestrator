# Fresh Session Boundaries

Read this before dispatching any executable work.

## Fresh By Default

- Wayfinder `Research`, `Prototype`, and automatable `Task` tickets: one fresh
  `/wayfinder` child session per ticket slug.
- Wayfinder follow-up tickets discovered by a child: reread the map, then let
  the parent dispatch the next fresh sessions; children do not open descendants.
- PRD synthesis: use a fresh `/to-prd` session to draft or publish from map
  proof when the seams are already approved; otherwise the child returns the
  seam proposal and the parent asks the user.
- Issue splitting: use a fresh `/to-issues` session to draft or publish from the
  approved PRD; the parent asks the user before publishing if the split is not
  already approved.
- Implementation: one fresh `/implement` child session per tracker issue.
- Integrated review: use a fresh read-only `/code-review` or repo-native review
  child after parent integration when available.
- Remote CI/CD or review-agent fixes: convert each code-changing fix into a
  tracker issue or explicit parent-approved micro-issue, then dispatch a fresh
  `/implement` child.
- Disputed review-agent comments: use a fresh read-only child for evidence
  gathering when the verdict is non-obvious, then the parent posts the MR
  rebuttal/adaptation note.

## Parent-Owned

- Human judgement gates and user questions.
- Deciding which child batch is safe to dispatch.
- `create_thread`, `automation_update`, and child coordinate records.
- Wayfinder frontier selection and next-round dispatch.
- Integration branch cherry-picks, conflict resolution, and MR push/open/update.
- MR comments, review-agent rebuttals, and final remote-gate completion.

## Stop Instead

Do not create a child thread for live user grilling, unresolved product choices,
unclear issue splits, overlapping mutable resources, missing source truth, or
any work item whose acceptance criteria cannot be checked from durable sources.

## Minimal Child Prompt

Use `GATE_CHILD_DISPATCH_PACKET.md` for PRD, issue-splitting, review, and
evidence-gathering children.

## Unregistered Worktree Targeting

If the source map or artifacts live in a worktree that `list_projects` cannot
target, create the child in the nearest registered project. This is not a user
stop by itself.

Record two coordinate sets:

- Execution target: the registered project/worktree used to create the thread.
- External coordinates: absolute map, proof, and artifact paths from the source
  worktree.

External coordinates are read-only unless the packet names a write target. For
discovery tickets, the only allowed external writes are the map ticket block and
listed artifact paths. Report this fallback to the user in one line; do not end
with manual copy-paste instructions when thread tools are available.
