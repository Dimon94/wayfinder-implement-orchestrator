# Coordinator、Worker 与 Execution Lane 边界

派发 design work 或进入 implementation 前读取本文件，并同时读取 `frontier-lanes.md`。

## Coordinator 持有

- route、human judgement、scope/ticket approval 和 user questions；
- 每轮 ready frontier、maximal safe batch、lane/runtime 选择；
- Herdr pane placement、terminal fan-in、integration 与冲突处理；
- tracker/map 的跨 item 写入，以及所有 remote publication actions；
- 最终 whole-change review、CI/CD 与完成判断。

Coordinator 可以亲自成为一个 execution lane 的 owner，但不能因此阻塞其他 safe lanes。

## Design Workers

- 一个 worker 只回答一个判断问题，只写自己的 ticket/artifact。
- AFK `Research`、evidence 和可自动 `Task` 按 maximal safe batch 自动并发。
- `Prototype`、`Grilling` 和 HITL `Task` 的用户等待只阻塞对应 pane。
- worker 可建议 follow-up，但不创建 descendants、不选择 route、不集成。
- spec、ticket split 和 review 仍是独立 gate workers；它们 terminal 后回 coordinator fan-in。

## AFK Execution Lanes

进入 implementation 前冻结 scope、dependency、acceptance、禁止范围和 local execution
authority。每个 lane 独占一个 worktree/branch，执行一条可串行验证的 ticket 链。

- maximal safe batch 中每张票启动一条 lane；当前 lead 可执行一条，其余自动派 pane。
- runtime 按 lane 特征自动选择：自包含 frozen hands-on work 用 `codex-pane`；需要 MCP、
  tracker writes、HITL 或不可逆操作用 `claude-native`。
- lane 内每票 `/implement`、focused verification、review、checkpoint commit 后，可继续领取
  一个无冲突且 prerequisites 已满足的 direct dependent。
- checkpoint 不等待用户。自动压缩后从 packet、tracker、Git 和 commits 重建。
- blocker 只停止本 lane；其他 lanes 继续。只有 blocker 支配全部剩余 frontier 才全局停下。
- lane 不 push、不开 PR/MR、不写 remote comment；这些动作回 coordinator。

## Authority Boundary

- local execution authority 在创建 worktree、编辑和 commit 前检查。
- remote publication authority 在 push、open/update PR/MR、remote comment 前检查。
- 缺失 remote authority 不阻塞 design workers、本地 execution lanes、checks 或 integration。

## Terminal Boundary

worker 完成或阻塞时输出完整 final report，再发 terminal signal。coordinator 对每条 lane 只读
一次 final report，验证 commits/checks/dirty state，按依赖拓扑集成并立即重算 frontier。
normal path 不读 routine progress；watchdog 只处理 startup failure、丢失 signal 或工具 timeout。

## External Coordinates

packet 记录两组坐标：

- Execution target：lane ID、pane、cwd、worktree、branch、base commit。
- External coordinates：map/ticket URLs、source worktree proofs、artifact paths。

除 packet 明确列出的 write targets 外，external coordinates 都是只读。
