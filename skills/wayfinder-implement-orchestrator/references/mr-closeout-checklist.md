# MR Closeout Checklist

Read this only when all required issue children are terminal or explicitly out
of scope.

## Child Result Audit

- Read each child thread with `read_thread`; do not trust a notification alone.
- Confirm final report fields: issue, status, worktree, branch, commit,
  verification, dirty state, touched files, blockers, recommendation.
- Inspect each commit before integration: `git show --stat --oneline <hash>` and
  a focused diff.
- Reject commits with unrelated files, missing verification, dirty worktree, or
  a blocker hidden as success.

## Integration Audit

- Cherry-pick or otherwise integrate only verified child commits into the
  integration branch.
- After every integrated child, run that issue's focused verification.
- After the batch, run the smallest whole-change check that proves the PRD.
- Run `/code-review` or the repo-native review gate before remote submission.
- If the review skill cannot spawn sub-agents in this session, run the same
  Standards and Spec diff review in-thread and record the fallback in the MR
  evidence.

## Summary MR Body

Include:

- PRD link.
- Implemented issue links.
- Child thread IDs.
- Integrated commits.
- Verification commands and results.
- Blocked or skipped issues with reasons.
- Known residual risk.

Ask before push/open/update if the user did not already authorize remote action.

## Remote Pass Gate

- After opening or updating the MR, read remote CI/CD status from the tracker or
  host API.
- Read MR comments for the automated review Agent verdict.
- Treat `pending`, missing, failed, or ambiguous CI/CD as not complete.
- Treat review-agent requests, failures, or absent verdict as not complete.
- Finish only when CI/CD passes and the review Agent explicitly says the MR can
  pass.

## Review-Agent Mistake

For each blocking review-agent comment:

1. Classify it as `valid`, `invalid`, or `Unknown` from code, tests, artifacts,
   and MR diff evidence.
2. If `valid`, fix or dispatch a follow-up issue before completion.
3. If `Unknown`, ask the user or gather the smallest missing evidence.
4. If `invalid`, reply in the MR with a concise rebuttal and direct evidence.
5. In the MR, leave an adaptation note recording why the review likely fired and
   what future review-agent behavior should change.

Use this comment shape for invalid reviews:

```text
Review-agent rebuttal:
- Comment: <link or quote the claim briefly>
- Verdict: invalid
- Evidence: <file/test/artifact/API result>
- Reason: <why the claim does not apply>

Review-agent adaptation note:
- Likely trigger: <pattern, missing context, stale assumption, or heuristic>
- Desired future behavior: <specific rule the review Agent should learn>
```

Do not mark the MR complete after a rebuttal alone. Completion still requires a
passing review-agent verdict, or explicit user direction to stop with an
unresolved remote-gate risk.
