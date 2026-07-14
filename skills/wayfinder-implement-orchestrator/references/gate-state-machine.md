# 门禁状态机

在 `SKILL.md` 第 2 步之后读取本文件。

## 门禁

| Gate | 真相源 | 通过条件 | 何时停下问用户 |
| --- | --- | --- | --- |
| `discovery` | Wayfinder map issue 的 Destination/Decisions-so-far/Not yet specified/Out of scope 和 child issue frontier | 必要 research/prototype/task child issues 已 closed，resolution comments 和必要 linked artifacts 存在；阻塞下一步判断的 in-scope fog 已从 Not yet specified 毕业成票或被解决，越过 Destination 的 work 已进 Out of scope | 任何未解决的 product、architecture、access 或 risk choice |
| `route` | Destination、Notes、closed child issue resolutions、linked artifacts、现有 spec/tickets tracker search/readback | 已选择且记录一个 post-discovery route：`wayfinder-complete`、`needs-spec`、`needs-implementation-tickets` 或 `direct-implementation-dispatch`；未选择的门禁不再执行 | Destination/Notes 与 resolutions 冲突、产物形态不清、现有 spec/tickets 是否复用需要用户判断 |
| `spec` | 已发布 spec issue/doc | 已捕获用户批准的 seams 和 scope；旧 tracker candidate overlap 已记录但未误判为 duplicate | Seam approval、scope tradeoff、精确 duplicate、或 tracker failure |
| `tickets` | 已发布 tracker implementation tickets/issues | 已批准 implementation tickets 有真实 issue IDs、read-back bodies 和 dependencies；duplicate 只按当前 route truth source 判断；变更面普查六面各有票或 map 边界行；每票带估时档位，无 XL 且 L 有不拆理由（`ticket-split-coverage.md`）；仪表盘已生成并打开（`map-dashboard.md`） | Split/merge/dependency judgement、当前 source 下的 duplicate、或 partial publish |
| `dispatch` | Tracker implementation tickets/issues、`frontier-lanes.md` | 已重算 ready frontier，并把 maximal safe batch 自动放入有独立 worktree/branch 的 execution lanes；存量票已补估档位，lane packet 携带档位上限；仪表盘已更新并打开 | ticket set 模糊、冲突无法隔离、缺少 local execution authority 或 base branch |
| `execute` | lane ticket readback、Git 状态、checks 和 review | lane 按依赖串行完成一张 ticket 的 `/implement`、验证、review、checkpoint commit；无冲突 successor 可留在同一 lane | ticket blocked/off-scope、合同被推翻，或票面内诊断与修复耗尽后 checks 仍失败；只停止该 lane |
| `collect` | terminal events、lane final reports | terminal lane 报告 commit、checks、dirty state、touched files；coordinator 只读取一次并立即重算 frontier；`estimate-log.csv` 已按 final report 追加行 | 缺少 terminal report，或 watchdog 发现 setup/signal/tool timeout |
| `integrate` | integration branch、已验证 lane commits | terminal commits 按依赖拓扑检查并集成；frontier 和 lanes 均清空后 whole-change checks 通过 | conflict、scope drift、failed check |
| `remote-review` | GitHub PR 或 GitLab MR、CI/CD status、review-agent comments | 已取得 remote publication authority；PR/MR 链接 spec/tickets/commits/checks/risks/lane reports；CI/CD 通过，且 review Agent 说 PR/MR can pass | Push/open PR/MR 权限不清晰、CI/CD 失败、valid/Unknown review rejection，或未解决的 review-Agent mistake |

## 流程

```text
discovery -> route -> spec -> tickets -> dispatch -> (execute <-> collect)* -> integrate -> remote-review
discovery -> route -> tickets -> dispatch -> (execute <-> collect)* -> integrate -> remote-review
discovery -> route -> dispatch -> (execute <-> collect)* -> integrate -> remote-review
discovery -> route -> done
```

`(execute <-> collect)*` 是动态 scheduler：lane 内按依赖串行，lane 间默认并发。每次 terminal
fan-in 都验证一次结果、按拓扑集成可集成 commit，并立即重算 ready frontier；不等整批结束，
也不按固定时间轮询。

`dispatch -> execute` 是 AFK 边界：进入前，scope、dependency order、acceptance、禁止范围、
local execution authority 和冲突隔离必须已知。remote publication authority 只在进入
`remote-review` 前检查。ticket checkpoint 不回到用户；lane 连续运行到 terminal 或真实停止条件。

不要把未选择的门禁当成必须步骤。只在已选路径内不得跳过门禁；如果某个已选门禁无法
证明，要么运行最小缺失前置步骤，要么停下来让用户判断。

## Post-discovery Route Classifier

只有所有 in-scope Wayfinder child issues 都 closed，且没有 open blocked child issues
仍在等前置条件时，才运行 route classifier。`frontier=0` 只表示“当前没有可拿的未阻塞
票”，不等于 discovery 完成。

route classifier 只决定 Wayfinder map 之外是否还要继续交付。大型 Wayfinder
map 清雾后默认先进入 `/to-spec`，把 linked decision tickets 折叠成一份可实现的
scope truth source；只有通过下方「小型化跳过证据」时才可绕过 spec。

选择 `wayfinder-complete`，当 Destination 已经由 closed Wayfinder child resolutions
满足，且用户没有要求把结果继续交付成 spec、implementation tickets 或代码变更。报告地图
完成并停止。

选择 `needs-spec`，当用户要求继续交付，且没有已批准 spec，又无法证明「小型化
跳过证据」。以下任一条都强制这条路线：

- Destination 是 spec、product/architecture scope、用户可批准方案，或 map 明确说终点是
  spec/决策文档；
- closed child resolutions 是证据、research 或 prototype feedback，还没有统一 what to
  change / what to change to / how to cause change；
- 用户 acceptance、seams、scope tradeoff 或 rollout/risk policy 仍需一个 spec issue/doc 承载；
- 没有已批准 spec，且 implementation tickets 会缺少共同 scope truth source。

选择 `needs-implementation-tickets`，仅当全部成立：

- 用户要求继续交付到代码；
- 已有已批准 spec，或已记录并读回「小型化跳过证据」；
- closed child resolutions 已给出足够实现锚点，例如文件/函数坐标、步骤、验收标准、
  测试锚、禁止范围或依赖事实；
- 不需要再合成 spec 才能解释 scope；
- 还没有可直接调度的 implementation ticket truth source，或仍需把已决项按依赖、
  shared files/resources、批次顺序和验收正文切成 tracker tickets/issues。

选择 `direct-implementation-dispatch`，仅当全部成立：

- 已存在可读回的 implementation tickets/issues；
- 这些 tickets 源自已批准 spec，或已记录并读回「小型化跳过证据」；
- 每个 ready item 都满足 Implementation Batch 条件；
- 依赖、shared files/resources、base branch 和 acceptance criteria 都清楚，不需要
  spec seam approval 或 ticket split approval；
- 没有 in-scope Not yet specified fog 会改变当前 batch。

### 小型化跳过证据

只有 Wayfinder 努力最终被证明已经小到不需要跨 session 合成时，才能跳过
`/to-spec`。route 记录必须同时给出：

- 交付可由一张 implementation ticket 在一次 single worker invocation 内完成；
- 所有 acceptance、scope、seam、risk 和禁止范围可在该 ticket 中自足表达；
- 该 ticket 显式链接每个对实现有影响的 closed decision ticket，不依赖聊天记忆；
- 已读回 ticket body，证明 linked decisions 没有在跳过 spec 时丢失。

任一条无法证明就选择 `needs-spec`；不得只因 Destination 里写了
`implementation-ready` 就跳过 spec。

如果 Destination 写明“不在本图内”的 spec 或合入步骤，不要把它们作为下一门禁。把它们
当作 Out of scope 边界；只有用户重新画 Destination 才进入新路线。

## Discovery Tickets

Research、prototype、grilling 和 task child issues 属于 `/wayfinder`，不属于
`/implement`。它们回答问题或清障，不是 implementation tickets。
通过 `wayfinder-frontier-loop.md` 执行它们。ticket resolved 后，把 answer 写成
resolution comment，close ticket，把 artifact link 留在 ticket，并给 map
Decisions-so-far 追加 title link + gist；不要把完整 answer 或 artifact 复制进 map。
如果 answer 让 Not yet specified 中的 fog 变得可成票，创建/连线 child issues，并从
Not yet specified 删除对应 fog；如果某个 ticket 或 fog 已越过 Destination，close 或删除
它，并在 Out of scope 追加 title link + gist + ruled-out reason，不要写入 Decisions-so-far。

如果 frontier query 返回 open、未阻塞且 unassigned 的 AFK `wayfinder:research` 或
可自动执行的 `wayfinder:task` child issues，且表格没有要求停下问用户，就在同一轮
派发这些 tickets。`wayfinder:prototype`、`wayfinder:grilling` 和 HITL task 必须等
真人反馈后才能 close；没有可参与的用户 task 时，当前 owner 停在 `ask-user`。

## Implementation Batch

只有满足以下条件的 implementation ticket/issue 才能进入 execute：

- 已发布到 tracker，且是 implementation ticket/issue；
- 没有 dependency 阻塞，或 prerequisites 已满足；
- 大小适合一次 issue-level `/implement`；
- 足够清晰，acceptance criteria 不需要聊天记忆也能验证。

每轮重算 ready frontier，并按 `frontier-lanes.md` 选择 maximal safe batch。彼此在 files、
migrations、locks、external resources 和 release ordering 上无冲突的 tickets 自动进入不同
lanes；相关 tickets 在同一 lane 串行。当前 task 可以拥有一条 lane，其余 lanes 使用 fresh
children。某条 lane blocked 时记录 blocker、终止该 lane 并继续其他 ready lanes。

## Tracker 去重

宽关键词搜索只能发现候选，不能单独阻止发布。精确 duplicate 必须同时匹配当前批准
spec/ticket、父子关系或 source 坐标、acceptance/禁止范围和门禁类型。历史迁移项、旧父
spec 下的实现 ticket、低 IID 旧项、closed/stale 项，或只覆盖部分术语的宽 spec，都记录为
candidate overlap；除非用户明确选择复用/更新，否则不要把它们当成当前链路的完成产物。

## 上下文续航

coordinator 和每条 lane 都接受 Codex 自动压缩；压缩后从 map/spec/tickets、Git、lane 坐标和
PR/MR 重建状态。design workers 与 execution lanes 都使用 `child-monitoring.md` 的 terminal
fan-in；只有 terminal event 或 watchdog 条件才读取 child，不做常规进度检查。
