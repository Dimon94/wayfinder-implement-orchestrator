# 门禁状态机

在 `SKILL.md` 第 2 步之后读取本文件。

## 门禁

| Gate | 真相源 | 通过条件 | 何时停下问用户 |
| --- | --- | --- | --- |
| `discovery` | Wayfinder map | 必要 research/prototype tickets 已 resolved，且 linked artifacts 存在 | 任何未解决的 product、architecture、access 或 risk choice |
| `proof` | Map answers 加 linked artifacts | 证据支持 PRD，且没有隐藏假设 | proof 缺失、冲突或 stale |
| `prd` | 已发布 PRD issue/doc | 已捕获用户批准的 seams 和 scope | Seam approval、scope tradeoff 或 tracker failure |
| `issues` | 已发布 tracker issues | 已批准 vertical slices 有真实 issue IDs、read-back bodies 和 dependencies | Split/merge/dependency judgement 或 partial publish |
| `dispatch` | Tracker issues | Ready issues 没有 blocking dependencies 或 mutable-resource conflicts | issue set 模糊、files/resources 重叠、缺少 base branch |
| `collect` | 5 分钟 automation wake-up、child thread readback | 每个 child 报告 status、commit if changed、checks、dirty state、touched files | child blocked/off-scope 或缺少 final report |
| `integrate` | integration branch 上的 Git commits | child commit 已检查、clean、in-scope，且 integration 后 focused checks 通过 | conflict、scope drift、failed check |
| `mr` | Remote MR、CI/CD status、review-agent comments | MR 链接 PRD/issues/child threads/commits/checks/risks，CI/CD 通过，且 review Agent 说 MR can pass | Push/open-MR 权限不清晰、CI/CD 失败、valid/Unknown review rejection，或未解决的 review-Agent mistake |

## 流程

```text
discovery -> proof -> prd -> issues -> dispatch -> collect -> integrate -> mr
```

不要跳过门禁。如果某个门禁无法证明，要么运行最小缺失前置步骤，要么停下来让用户判断。

## Discovery Tickets

Research 和 prototype tickets 属于 `/wayfinder`，不属于 `/implement`。通过
`wayfinder-frontier-loop.md` 执行它们。ticket resolved 后，把 answer 和 artifact
link 更新进 map；不要把完整 artifact 复制进 map。

如果 map 里有未阻塞的 `Research`、`Prototype` 或可自动执行的 `Task` tickets，且表格
没有要求停下问用户，就在同一轮派发这些 tickets。不要以“让用户复制粘贴 child
prompts”结束。

## Implementation Batch

只有当 batch 内每个 issue 都满足以下条件时，才派发 batch：

- 已发布到 tracker；
- 没有 dependency 阻塞，或 prerequisites 已满足；
- 大小适合一个 fresh `/implement` session；
- 在 files、migrations、locks、external resources 或 release ordering 上与 sibling
  独立；
- 足够清晰，acceptance criteria 不需要父线程聊天记忆也能验证。

如果任何条件是 `Unknown`，把该 issue 从 batch 移除，或询问用户。在同一个 dispatch
turn 中为剩余每个 issue 创建一个 `/implement` child，然后用一个 heartbeat 监控整个
batch。

## 上下文预算

派发后，不要让父线程持续推理循环保持打开。使用 `child-monitoring.md` 里的 5 分钟
reminder；每次 wake-up 只读取判断 child 是 still running、blocked，还是 ready for
the next gate 所需的紧凑状态。
