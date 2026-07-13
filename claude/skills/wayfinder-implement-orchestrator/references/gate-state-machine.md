# 门禁状态机

在 `SKILL.md` 第 2 步之后读取本文件。

## 门禁

| Gate | 真相源 | 通过条件 | 何时停下问用户 |
| --- | --- | --- | --- |
| `discovery` | Wayfinder map issue 的 Destination/Decisions-so-far/Not yet specified/Out of scope 和 child issue frontier | 必要 research/prototype/task child issues 已 closed，resolution comments 和必要 linked artifacts 存在；阻塞下一步判断的 in-scope fog 已从 Not yet specified 毕业成票或被解决，越过 Destination 的 work 已进 Out of scope | 任何未解决的 product、architecture、access 或 risk choice |
| `route` | Destination、Notes、closed child issue resolutions、linked artifacts、现有 spec/tickets tracker search/readback | 已选择且记录一个 post-discovery route：`wayfinder-complete`、`needs-spec`、`needs-implementation-tickets` 或 `direct-implementation-dispatch`；未选择的门禁不再执行 | Destination/Notes 与 resolutions 冲突、产物形态不清、现有 spec/tickets 是否复用需要用户判断 |
| `spec` | 已发布 spec issue/doc | 已捕获用户批准的 seams 和 scope；旧 tracker candidate overlap 已记录但未误判为 duplicate | Seam approval、scope tradeoff、精确 duplicate、或 tracker failure |
| `tickets` | 已发布 tracker implementation tickets/issues | 已批准 implementation tickets 有真实 issue IDs、read-back bodies 和 dependencies；duplicate 只按当前 route truth source 判断；变更面普查六面各有票或 map 边界行（`ticket-split-coverage.md`） | Split/merge/dependency judgement、当前 source 下的 duplicate、或 partial publish |
| `dispatch` | Tracker tickets、`frontier-lanes.md` | ready frontier、maximal safe batch、lane IDs、独立 worktree/branch、runtime 和 local execution authority 已冻结 | ticket set、base、local authority 或冲突边界模糊 |
| `execute` | lane packet、Git、checks 和 review | 每条 lane AFK 完成 ticket checkpoint；只在无冲突且 prerequisites 满足时继续 direct dependent | 本 lane off-scope、合同被推翻、需要用户判断或 checks 耗尽仍失败 |
| `collect` | terminal events、lane final reports | 每条 terminal lane 已被读取一次并验证；blocked 只暂停本 lane | final report 缺失、commit/dirty state 不可信 |
| `integrate` | 已验证 lane commits、integration branch | terminal commits 已按依赖拓扑集成；frontier 为空后 focused/whole-change checks 通过 | conflict、scope drift、failed check |
| `remote-review` | GitHub PR 或 GitLab MR、CI/CD status、review-agent comments | 已获得 remote publication authority；PR/MR 链接 scope/tickets/commits/checks/risks；CI/CD 通过且 review Agent 说 can pass | remote authority 缺失、CI/CD 失败、valid/Unknown review rejection |

## 流程

```text
discovery -> route -> spec -> tickets -> dispatch -> (execute -> collect -> integrate -> dispatch)* -> remote-review
discovery -> route -> tickets -> dispatch -> (execute -> collect -> integrate -> dispatch)* -> remote-review
discovery -> route -> dispatch -> (execute -> collect -> integrate -> dispatch)* -> remote-review
discovery -> route -> done
```

括号内是默认 AFK frontier loop：自动派发 maximal safe batch；每条 lane terminal 后立即
collect/integrate 并重算 frontier，不等待同批全部 lanes。lane blocker 不停止其他 lanes。

不要把未选择的门禁当成必须步骤。只在已选路径内不得跳过门禁；如果某个已选门禁无法
证明，要么运行最小缺失前置步骤，要么停下来让用户判断。

## Post-discovery Route Classifier

只有所有 in-scope Wayfinder child issues 都 closed，且没有 open blocked child issues
仍在等前置条件时，才运行 route classifier。`frontier=0` 只表示“当前没有可拿的未阻塞
票”，不等于 discovery 完成。

route classifier 只决定 Wayfinder map 之外是否还要继续交付：不让 `/wayfinder` 自己
默认进入 `/to-spec` 或 `/to-tickets`。

选择 `wayfinder-complete`，当 Destination 已经由 closed Wayfinder child resolutions
满足，且用户没有要求把结果继续交付成 spec、implementation tickets 或代码变更。报告地图
完成并停止。

选择 `needs-spec`，仅当至少一条成立：

- Destination 是 spec、product/architecture scope、用户可批准方案，或 map 明确说终点是
  spec/决策文档；
- closed child resolutions 是证据、research 或 prototype feedback，还没有统一 what to
  change / what to change to / how to cause change；
- 用户 acceptance、seams、scope tradeoff 或 rollout/risk policy 仍需一个 spec issue/doc 承载；
- 没有已批准 spec，且 implementation tickets 会缺少共同 scope truth source。

选择 `needs-implementation-tickets`，仅当全部成立：

- 用户要求继续交付到代码，且 Destination 或 Notes 明确本图终点是可实现范围、
  implementation-ready decisions、implementation ticket handoff，或直接派给实现者；
- closed child resolutions 已给出足够实现锚点，例如文件/函数坐标、步骤、验收标准、
  测试锚、禁止范围或依赖事实；
- 不需要再合成 spec 才能解释 scope；
- 还没有可直接调度的 implementation ticket truth source，或仍需把已决项按依赖、
  shared files/resources、批次顺序和验收正文切成 tracker tickets/issues。

选择 `direct-implementation-dispatch`，仅当全部成立：

- 已存在可读回的 implementation tickets/issues；
- 每个 ready item 都满足 Implementation Batch 条件；
- 依赖、shared files/resources、base branch 和 acceptance criteria 都清楚，不需要
  spec seam approval 或 ticket split approval；
- 没有 in-scope Not yet specified fog 会改变当前 batch。

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
真人反馈后才能 close；没有可参与的用户 pane 时，lead 停在 `ask-user`。

## Implementation Batch

只有满足以下条件的 implementation ticket/issue 才能进入 execution queue：

- 已发布到 tracker，且是 implementation ticket/issue；
- 没有 dependency 阻塞，或 prerequisites 已满足；
- 大小适合一次 issue-level `/implement`；
- 足够清晰，acceptance criteria 不需要 lead pane 聊天记忆也能验证。

每轮从这些 tickets 重算 ready frontier，并自动选择 maximal safe batch。两两检查 files、
migrations、locks、external resources 和 release ordering；安全 items 各自进入独立 lane，
冲突 items 只在相关 lane 间串行。读取 `frontier-lanes.md` 与 `child-monitoring.md`。

## Tracker 去重

宽关键词搜索只能发现候选，不能单独阻止发布。精确 duplicate 必须同时匹配当前批准
spec/ticket、父子关系或 source 坐标、acceptance/禁止范围和门禁类型。历史迁移项、旧父
spec 下的实现 ticket、低 IID 旧项、closed/stale 项，或只覆盖部分术语的宽 spec，都记录为
candidate overlap；除非用户明确选择复用/更新，否则不要把它们当成当前链路的完成产物。

## 上下文续航

每条 lane 接受自动压缩并继续执行；压缩后从 packet、map/spec/tickets、Git 和 commits
重建。coordinator 只等待 terminal signal；watchdog 仅处理丢失 signal、setup failure 或
工具 timeout，不建立固定检查节奏。
